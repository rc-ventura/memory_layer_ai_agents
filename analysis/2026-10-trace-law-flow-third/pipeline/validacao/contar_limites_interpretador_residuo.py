"""Base 3: o grupo "limites do interpretador" do resíduo (b3 #5) — que construto, de que forma e quem, antes de ler
casos.

Na rodada `2db46d963c549710` (Ajuste 37), 49 erros do balde "sintoma não reconhecido" são o interpretador do agente
(smolagents) recusando uma construção de Python que ele não implementa:
    NoneType is not supported.                              (21)
    NamedExpr is not supported.                             (13)  o operador `:=`
    Global is not supported.                                (11)  `global x`
    Cannot unpack non-tuple value                           (2)
    Nonlocal is not supported.                              (1)   `nonlocal x`
    Re-raise is not supported without an active exception   (1)   `raise` sozinho fora de um `except`
A hipótese (procedimento do resíduo, passo 4, perguntas R2 e R3): a falha é do agente, que escreveu Python válido que
este interpretador não roda, e o destino é uma lição de fato do ambiente (o que o sandbox não roda, com a alternativa).
Ao contrário do grupo 1 (Ajuste 37), o prompt padrão do framework não avisa sobre essas construções; o `--trace` confere
isso num trace com prompt (base 1 aqui, base 2 no ambiente da base).

O `NoneType` é o que menos se entende pela mensagem: o interpretador recebeu um nó vazio (`None`) onde esperava uma
expressão. A hipótese é o `**` dentro de um dicionário literal (`{**a, 'k': v}`): o Python guarda a chave desse item
como `None`. O único caso da base 1 tem essa forma.

As medidas, por regra, sem ler caso (a linha que falhou, `Code execution failed at line '<linha>'`, é lida pela árvore
sintática do Python, `ast`, nunca impressa):
  - **o limite** (qual das seis mensagens);
  - **a forma**, por limite:
      NoneType   dict_com_estrela (`{**x}`), kwonly_sem_padrao (`def f(*, a)`), yield_sem_valor, outra;
      NamedExpr  em_if, em_while, em_compreensao, outra;
      Global / Nonlocal   so_a_declaracao (a linha é só `global x`), em_funcao (dentro de um `def`), outra;
      unpack     atribuicao (`a, b = ...`), laco (`for a, b in ...`), outra;
      Re-raise   raise_sozinho, outra;
    e, para todos: nao_parseia (a linha não é Python inteiro; se tiver `{**`, `nao_parseia_com_estrela`), sem_linha;
  - **os construtos na linha** (pode haver mais de um): dict_com_estrela, walrus, global, nonlocal, raise_sozinho,
    kwonly_sem_padrao, yield_sem_valor, lambda, compreensao, fstring, def;
  - **a repetição:** quantas execuções-papel têm o mesmo limite mais de uma vez (o agente repete depois de ver a
    mensagem?);
  - erros, execuções, meses, papéis e tokens; e papel × limite.

Com `--trace <trace com prompt>`: por papel, quantos prompts citam cada construção (`:=`/walrus, `global`, `nonlocal`,
`{**`, "not supported") e quantos a usam nos exemplos de código (o prompt induziria o erro). Só contagens.

Grava `casos_limites_interpretador.csv` (os erros do grupo, com `limite`, `forma` e `construtos`, sem a mensagem) na
pasta do `casos.csv`, para o `montar_evidencia.py --de mineracao/residuo/<pasta>/casos_limites_interpretador.csv
--onde forma=<f>` montar a amostra com os crus.

Não muda nada no pipeline e fica fora do hash da rodada. Imprime só contagens, nomes de papel, os limites, as formas e
os meses: nada de mensagem, de código nem de identificador. Uso, da raiz, no ambiente da base:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_limites_interpretador_residuo.py
        --casos <pipeline/resultados/mineracao/residuo/<pasta>/casos.csv> [--trace <trace com prompt>]
"""
import argparse
import ast
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys
import textwrap

import pandas as pd

RAIZ = Path(__file__).resolve().parents[4]

LIMITES = [
    ("NoneType", re.compile(r"\bNoneType is not supported\.")),
    ("NamedExpr", re.compile(r"\bNamedExpr is not supported\.")),
    ("Global", re.compile(r"\bGlobal is not supported\.")),
    ("Nonlocal", re.compile(r"\bNonlocal is not supported\.")),
    ("unpack", re.compile(r"Cannot unpack non-tuple value")),
    ("Re-raise", re.compile(r"Re-raise is not supported without an active exception")),
]
LINHA = re.compile(r"failed at line '(.*?)' due to", re.S)
FORMAS = {
    "NoneType": ["dict_com_estrela", "kwonly_sem_padrao", "yield_sem_valor", "outra"],
    "NamedExpr": ["em_if", "em_while", "em_compreensao", "outra"],
    "Global": ["so_a_declaracao", "em_funcao", "outra"],
    "Nonlocal": ["so_a_declaracao", "em_funcao", "outra"],
    "unpack": ["atribuicao", "laco", "outra"],
    "Re-raise": ["raise_sozinho", "outra"],
}
COMUNS = ["nao_parseia_com_estrela", "nao_parseia", "sem_linha"]
CONSTRUTOS = ["dict_com_estrela", "walrus", "global", "nonlocal", "raise_sozinho", "kwonly_sem_padrao",
              "yield_sem_valor", "lambda", "compreensao", "fstring", "def"]
# `{**x` ou `{..., **x` (sem parêntese entre a chave e a vírgula): o `**` de desempacotar, não a potência (`88 ** 2`)
# nem o `**kw` de uma chamada dentro do dicionário. Só serve para a linha que não parseia e para o texto do prompt.
ESTRELA_NO_DICT = re.compile(r"\{\s*\*\*\s*[A-Za-z_{(\[]|\{[^{}()]*,\s*\*\*\s*[A-Za-z_{(\[]")
COMPREENSOES = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def limite(msg):
    for nome, rx in LIMITES:
        if rx.search(msg):
            return nome
    return None


def arvore(linha):
    """A árvore da linha que falhou, ou None se ela não é Python inteiro (cortada, por exemplo)."""
    try:
        return ast.parse(textwrap.dedent(linha))
    except (SyntaxError, ValueError):
        return None


def construtos(t):
    """Os construtos presentes na árvore (ver o docstring do módulo), na ordem de CONSTRUTOS."""
    achou = set()
    for n in ast.walk(t):
        if isinstance(n, ast.Dict) and any(k is None for k in n.keys):
            achou.add("dict_com_estrela")
        elif isinstance(n, ast.NamedExpr):
            achou.add("walrus")
        elif isinstance(n, ast.Global):
            achou.add("global")
        elif isinstance(n, ast.Nonlocal):
            achou.add("nonlocal")
        elif isinstance(n, ast.Raise) and n.exc is None:
            achou.add("raise_sozinho")
        elif isinstance(n, ast.arguments) and any(d is None for d in n.kw_defaults):
            achou.add("kwonly_sem_padrao")
        elif isinstance(n, (ast.Yield, ast.YieldFrom)) and n.value is None:
            achou.add("yield_sem_valor")
        elif isinstance(n, ast.Lambda):
            achou.add("lambda")
        elif isinstance(n, COMPREENSOES):
            achou.add("compreensao")
        elif isinstance(n, ast.JoinedStr):
            achou.add("fstring")
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            achou.add("def")
    return [c for c in CONSTRUTOS if c in achou]


def _dentro(t, alvo, de):
    """Algum nó do tipo `alvo` está dentro de um nó do tipo `de`?"""
    return any(isinstance(m, alvo) for n in ast.walk(t) if isinstance(n, de) for m in ast.walk(n) if m is not n)


def _forma(lim, t, cs):
    if lim == "NoneType":
        for f in ("dict_com_estrela", "kwonly_sem_padrao", "yield_sem_valor"):
            if f in cs:
                return f
        return "outra"
    if lim == "NamedExpr":
        if _dentro(t, ast.NamedExpr, COMPREENSOES):
            return "em_compreensao"
        if any(isinstance(n, ast.If) and any(isinstance(m, ast.NamedExpr) for m in ast.walk(n.test))
               for n in ast.walk(t)):
            return "em_if"
        if any(isinstance(n, ast.While) and any(isinstance(m, ast.NamedExpr) for m in ast.walk(n.test))
               for n in ast.walk(t)):
            return "em_while"
        return "outra"
    if lim in ("Global", "Nonlocal"):
        tipo = ast.Global if lim == "Global" else ast.Nonlocal
        if len(t.body) == 1 and isinstance(t.body[0], tipo):
            return "so_a_declaracao"
        return "em_funcao" if _dentro(t, tipo, (ast.FunctionDef, ast.AsyncFunctionDef)) else "outra"
    if lim == "unpack":
        if any(isinstance(n, (ast.For, ast.comprehension)) and isinstance(n.target, (ast.Tuple, ast.List))
               for n in ast.walk(t)):
            return "laco"
        if any(isinstance(n, ast.Assign) and any(isinstance(a, (ast.Tuple, ast.List)) for a in n.targets)
               for n in ast.walk(t)):
            return "atribuicao"
        return "outra"
    return "raise_sozinho" if "raise_sozinho" in cs else "outra"


def classificar(msg):
    """(limite, forma, construtos) de uma mensagem; limite None se ela não é do grupo."""
    lim = limite(msg)
    if lim is None:
        return None, None, []
    m = LINHA.search(msg)
    if not m:
        return lim, "sem_linha", []
    t = arvore(m.group(1))
    if t is None:
        return lim, "nao_parseia_com_estrela" if ESTRELA_NO_DICT.search(m.group(1)) else "nao_parseia", []
    cs = construtos(t)
    return lim, _forma(lim, t, cs), cs


def contar(C):
    C = C.copy()
    C["mensagem"] = C["mensagem"].fillna("").astype(str)
    trios = [classificar(m) for m in C.mensagem]
    C["limite"] = [x[0] for x in trios]
    C["forma"] = [x[1] for x in trios]
    C["construtos"] = ["+".join(x[2]) for x in trios]
    return C[C.limite.notna()].copy()


def repeticao(G):
    """Por (execução, papel, limite): quantas vezes o mesmo limite aparece."""
    por = G.groupby(["exec_id", "agente", "role", "limite"]).size()
    return {"execuções-papel-limite": len(por), "1 vez": int((por == 1).sum()), "2+ vezes": int((por >= 2).sum()),
            "máximo de vezes": int(por.max()) if len(por) else 0}


TERMOS = {
    "walrus (:= ou a palavra)": re.compile(r":=|walrus", re.I),
    "global x": re.compile(r"^\s*global\s+[A-Za-z_]\w*\s*$", re.M),
    "nonlocal": re.compile(r"\bnonlocal\b"),
    "{** no texto": ESTRELA_NO_DICT,
    "'not supported'": re.compile(r"not supported", re.I),
}
BLOCO = re.compile(r"```(?:py|python)?\s*\n(.*?)```|<code>(.*?)</code>", re.S)


def medir_prompt(memos):
    """memos: os `txt_etap_memo` (JSON). Por papel: execuções com prompt, prompts que citam cada termo, e prompts cujos
    exemplos de código (blocos ``` ou <code>) usam cada construto."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from contar_regra_nome_ferramenta_prompt import prompt_do_papel
    por = defaultdict(Counter)
    for txt in memos:
        try:
            memo = json.loads(txt)
        except (TypeError, ValueError):
            continue
        for papel, steps in memo.items():
            p = prompt_do_papel(steps) if isinstance(steps, list) else ""
            if not p:
                continue
            c = por[papel]
            c["execuções"] += 1
            for nome, rx in TERMOS.items():
                c[f"cita {nome}"] += bool(rx.search(p))
            usados = set()
            for b in BLOCO.finditer(p):
                t = arvore(b.group(1) or b.group(2) or "")
                if t is not None:
                    usados.update(construtos(t))
            for k in ("dict_com_estrela", "walrus", "global", "nonlocal", "raise_sozinho"):
                c[f"exemplo usa {k}"] += k in usados
    return por


def _resumo(g):
    return (f"{len(g)} erros · {len(g[['exec_id', 'agente']].drop_duplicates())} execuções · {g.mes.nunique()} meses · "
            f"{g.role.nunique()} papéis · {int(g.tok_tot.fillna(0).sum()):,} tokens".replace(",", "."))


def _prompt(trace):
    sys.path.insert(0, str(RAIZ / "analysis"))
    from leitor_trace import ler_trace
    por = medir_prompt(ler_trace(trace)["txt_etap_memo"])
    cols = [f"cita {n}" for n in TERMOS] + [f"exemplo usa {k}" for k in
                                            ("dict_com_estrela", "walrus", "global", "nonlocal", "raise_sozinho")]
    print(f"\no prompt ({sum(c['execuções'] for c in por.values())} execuções-papel com prompt):")
    print("  papel | execuções | " + " | ".join(cols))
    for papel, c in sorted(por.items(), key=lambda kv: -kv[1]["execuções"]):
        print(f"  {papel} | {c['execuções']} | " + " | ".join(str(c[k]) for k in cols))


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--casos")
    p.add_argument("--trace")
    a = p.parse_args(argv)
    if not a.casos and not a.trace:
        p.error("passe --casos, --trace ou os dois")
    if a.casos:
        C = pd.read_csv(a.casos, dtype={"exec_id": str, "agente": str})
        if "mensagem" not in C.columns:
            print("casos.csv sem a coluna `mensagem`: rode o `especificas/residuo.py` desta versão")
            return 1
        G = contar(C)
        print(f"resíduo: {len(C)} erros · limites do interpretador: {_resumo(G)}")
        if not G.empty:
            print(f"  por balde: {G.unidade.value_counts().to_dict()}")
            print(f"  meses: {G.mes.value_counts().sort_index().to_dict()}")
            print(f"  papéis: {G.role.value_counts().to_dict()}")
            print(f"  repetição: {repeticao(G)}")
            for lim, _ in LIMITES:
                g = G[G.limite == lim]
                if g.empty:
                    continue
                print(f"\n  {lim}: {_resumo(g)}")
                print(f"    forma: {g.forma.value_counts().reindex(FORMAS[lim] + COMUNS, fill_value=0).to_dict()}")
                cs = Counter(c for s in g.construtos for c in s.split("+") if c)
                print(f"    construtos na linha: {dict(cs.most_common())}")
                print(f"    papéis: {g.role.value_counts().to_dict()}")
                print(f"    meses: {g.mes.value_counts().sort_index().to_dict()}")
            destino = Path(a.casos).parent / "casos_limites_interpretador.csv"
            G.drop(columns=["mensagem"]).to_csv(destino, index=False)
            print(f"\n→ {destino} ({len(G)} erros; sem a coluna mensagem)")
    if a.trace:
        _prompt(a.trace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
