"""Primitivas genéricas para análises de trace de CodeAgent (formato smolagents).

Nada aqui conhece a esteira jurídica, a taxonomia de erros ou uma base específica: só consome
registros por step (dicts com `exec_id`, `role`, `idx`, `code`, `sysprompt`) e texto. O que é
hipótese de uma análise (`classify()`, `submecanismo()`, `SUB2UNI`, `carregar_base()`) continua
no `base_pipeline.py` da pasta datada — é copiado, não importado, quando uma base nova chega.

Uso a partir de `<análise>/pipeline/`:

    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    from base_utils import agrupar_por_execucao, inventario_ferramentas, ...
"""

import ast
import re
from collections import defaultdict

DEF_FERRAMENTA = re.compile(r"def\s+(\w+)\s*\(")


def agrupar_por_execucao(registros):
    """(exec_id, role) -> lista de registros em ordem de `idx`."""
    seqs = defaultdict(list)
    for r in registros:
        seqs[(r["exec_id"], r["role"])].append(r)
    for seq in seqs.values():
        seq.sort(key=lambda x: x["idx"])
    return seqs


def inventario_ferramentas(registros):
    """Nomes que algum system prompt declara como `def nome(...)` — o inventário autorizado.

    Extrair do prompt, não das chamadas observadas: a lista observada mistura ferramenta declarada
    com função auxiliar que o próprio agente define e reutiliza."""
    inv = set()
    for r in registros:
        inv.update(DEF_FERRAMENTA.findall(r.get("sysprompt") or ""))
    return inv


def parse_codigo(code):
    """AST do `code_action`, ou None se não parseia."""
    try:
        return ast.parse(code or "")
    except Exception:
        return None


def chamadas_diretas(tree):
    """Todo `ast.Call` cujo alvo é um nome simples (`f(...)`, não `obj.f(...)`)."""
    if tree is None:
        return []
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]


def nomes_lidos(tree):
    """Nomes lidos (contexto Load) no código — o que o código efetivamente usa."""
    if tree is None:
        return set()
    return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def atribuicoes_de_chamada(tree):
    """(nome_da_função, [alvos]) para cada `alvo = f(...)` com alvo nome simples."""
    if tree is None:
        return []
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name):
            out.append((n.value.func.id, [t.id for t in n.targets if isinstance(t, ast.Name)]))
    return out


def assinatura_chamada(node):
    """Forma normalizada de uma chamada — duas chamadas idênticas têm a mesma assinatura."""
    return ast.dump(node)


def entidades(texto, padroes):
    """[(tipo, valor)] para cada casamento de `padroes` ({tipo: regex}) em `texto`.

    Os padrões são do chamador (ex.: CNJ/CPF/CNPJ/data/valor na esteira jurídica); a função não
    sabe o que é uma entidade do domínio."""
    texto = texto or ""
    return [(tipo, m.group(0)) for tipo, rx in padroes.items() for m in re.finditer(rx, texto)]


def entidades_sem_suporte(texto, referencia, padroes):
    """Entidades de `texto` que não aparecem literalmente em `referencia` — candidatas a valor
    inventado. Valor calculado pelo próprio código também cai aqui: triagem, não veredito."""
    referencia = referencia or ""
    return [(t, v) for t, v in entidades(texto, padroes) if v not in referencia]
