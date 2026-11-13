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

Com `--fonte <parquet da base>` (junto do `--casos`): **o que o agente faz depois do erro**, para separar "não conhecia
o ambiente" de "errou mesmo sabendo". Em cada erro do grupo, o passo seguinte e o seguinte a ele (`next_*` e `next2_*`
da fonte, ligados pela chave execução, agente, papel e posição do passo) recebem um desfecho: sem passo; o mesmo
limite de novo; trocou a construção (ok ou com outro erro); ainda usa a construção (ok ou com outro erro); não lido (o
unpack, ou o código não parseia). Mais o tipo do outro erro, tirado da mensagem. E a **versão do agente** por papel, na
fonte inteira, com rótulos v1, v2… em ordem do 1º mês (o código da versão não sai): os picos de julho (`:=` no
RoteadorCivel, `global` no ontestacaoCivel) coincidem com uma versão nova? E **a instrução de verificação**: o `global`
e o `raise` sozinho do ContestacaoCivel seriam um terceiro jeito de cumprir "VERIFIQUE se a variável de saída já está
preenchida; se já estiver, PULE a chamada" (como o `'x' in globals()` e o `try/except NameError`, que são da unidade da
verificação de existência, destino harness)? No código do passo que falhou e do anterior (`sinais_verificacao`): onde
está a função com `global`, se ela testa a variável global e a preenche com o retorno de uma chamada, se o nome dela é
de verificação ou estado, e se o código usa `globals()` ou `except NameError`; com um controle nos outros limites.

Grava `casos_limites_interpretador.csv` (os erros do grupo, com `limite`, `forma` e `construtos`, sem a mensagem) na
pasta do `casos.csv`, para o `montar_evidencia.py --de mineracao/residuo/<pasta>/casos_limites_interpretador.csv
--onde forma=<f>` montar a amostra com os crus.

Não muda nada no pipeline e fica fora do hash da rodada. Imprime só contagens, nomes de papel, os limites, as formas e
os meses: nada de mensagem, de código nem de identificador. Uso, da raiz, no ambiente da base:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_limites_interpretador_residuo.py
        --casos <pipeline/resultados/mineracao/residuo/<pasta>/casos.csv> [--fonte <parquet da base>]
        [--trace <trace com prompt>]
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


# O que o agente faz depois do erro (com --fonte): a construção recusada de cada limite, procurada na árvore do código
# do passo seguinte. O unpack não tem construção própria (é erro de código comum): só o erro conta.
ALVO = {"NoneType": "dict_com_estrela", "NamedExpr": "walrus", "Global": "global", "Nonlocal": "nonlocal",
        "Re-raise": "raise_sozinho", "unpack": None}
DESFECHOS = ["sem_passo", "mesmo_limite", "trocou_ok", "trocou_outro_erro", "usa_ok", "usa_outro_erro",
             "nao_lido_ok", "nao_lido_outro_erro"]
PASSOS = ("next", "next2")
CHAVE_FONTE = ["cod_idef_exeo", "cod_idef_aget", "papel", "step_pos"]
COLUNAS_FONTE = CHAVE_FONTE + ["cod_vers_aget", "mes_execucao", "error_code_action", "prev_code_action"] + [
    f"{p}_{c}" for p in PASSOS for c in ("step_number", "code_action", "error_message")]

# O `global` e o `raise` sozinho são a instrução de verificação do prompt? (dossiê do inventário do sandbox, parte A: o
# ContestacaoCivel recebe "VERIFIQUE se a variável de saída já está preenchida em memória; se já estiver, PULE a
# chamada" e a cumpre com `'x' in globals()` em julho e `try/except NameError` em agosto, as duas barradas; a unidade é a
# verificação de existência, destino harness.) Os sinais, no código do passo que falhou e no do passo anterior (a
# função com o `global` pode ter sido definida antes; a linha que falhou é a da chamada):
INTROSPECCAO = re.compile(r"\b(?:globals|locals|vars)\s*\(")
EXCEPT_NAMEERROR = re.compile(r"except\s+\(?[^)\n:]*\bNameError\b")
NOME_DE_ESTADO = re.compile(r"(?i)has_|exist|defin|ensure|check|verif|preench|filled|^ja_|cache|get_or|garant|^set_|"
                            r"salva|guarda|estado|memo|state|store|^is_")
USOS_GLOBAL = ["verifica_e_guarda_chamada", "so_guarda_chamada", "so_verifica", "outro_uso", "def_nao_visto",
               "codigo_nao_parseia"]


def _defs_com_global(t):
    """As funções do código que declaram `global`, com os nomes declarados."""
    for f in ast.walk(t):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
            nomes = {n for g in ast.walk(f) if isinstance(g, ast.Global) for n in g.names}
            if nomes:
                yield f, nomes


def _verifica(f, nomes):
    """A função testa uma das variáveis globais (`if x is None`, `if not x`, `'x' in globals()`…)?"""
    for n in ast.walk(f):
        if isinstance(n, (ast.If, ast.IfExp, ast.While)):
            for m in ast.walk(n.test):
                if (isinstance(m, ast.Name) and m.id in nomes) or (isinstance(m, ast.Constant) and m.value in nomes):
                    return True
    return False


def _guarda_chamada(f, nomes):
    """A função guarda numa variável global o retorno de uma chamada (`x = ferramenta(...)`)?"""
    for n in ast.walk(f):
        alvos = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, (ast.AnnAssign, ast.AugAssign)) else []
        if any(isinstance(a, ast.Name) and a.id in nomes for a in alvos) and isinstance(getattr(n, "value", None), ast.Call):
            return True
    return False


def _raise_em_except_nameerror(t):
    """Um `raise` sozinho dentro de um `except` que pega NameError?"""
    for h in ast.walk(t):
        if isinstance(h, ast.ExceptHandler) and h.type is not None and any(
                isinstance(m, ast.Name) and m.id == "NameError" for m in ast.walk(h.type)):
            if any(isinstance(r, ast.Raise) and r.exc is None for r in ast.walk(h)):
                return True
    return False


def sinais_verificacao(codigo, anterior):
    """Os sinais da instrução de verificação no código do passo que falhou e no do anterior:
      onde_def_global  passo / anterior / nao_visto (nenhuma função com `global` nos dois) / nao_parseia;
      uso_global       verifica_e_guarda_chamada (testa a variável global e a preenche com o retorno de uma chamada: o
                       que a instrução pede), so_guarda_chamada, so_verifica, outro_uso, def_nao_visto,
                       codigo_nao_parseia;
      nome_de_estado   o nome da função com `global` é de verificação ou estado (`has_`, `exist`, `ensure`, `cache`…);
      introspeccao     `globals()`/`locals()`/`vars()` no código; except_nameerror  `except NameError` no código;
      raise_em_except_nameerror  `raise` sozinho dentro de um `except NameError`."""
    s = {"onde_def_global": "nao_visto", "uso_global": "def_nao_visto", "nome_de_estado": False,
         "introspeccao": False, "except_nameerror": False, "raise_em_except_nameerror": False}
    algum_parseia = False
    for onde, c in (("passo", codigo), ("anterior", anterior)):
        if _vazio(c):
            continue
        c = str(c)
        s["introspeccao"] |= bool(INTROSPECCAO.search(c))
        s["except_nameerror"] |= bool(EXCEPT_NAMEERROR.search(c))
        t = arvore(c)
        if t is None:
            continue
        algum_parseia = True
        s["raise_em_except_nameerror"] |= _raise_em_except_nameerror(t)
        defs = list(_defs_com_global(t))
        if defs and s["onde_def_global"] == "nao_visto":
            s["onde_def_global"] = onde
            v = any(_verifica(f, n) for f, n in defs)
            g = any(_guarda_chamada(f, n) for f, n in defs)
            s["uso_global"] = ("verifica_e_guarda_chamada" if v and g else "so_guarda_chamada" if g else
                               "so_verifica" if v else "outro_uso")
            s["nome_de_estado"] = any(NOME_DE_ESTADO.search(f.name) for f, _ in defs)
    if not algum_parseia and s["onde_def_global"] == "nao_visto":
        s["onde_def_global"], s["uso_global"] = "nao_parseia", "codigo_nao_parseia"
    return s


def _vazio(v):
    return v is None or (isinstance(v, float) and v != v) or (isinstance(v, str) and not v.strip())


def desfecho(lim, passo, codigo, erro):
    """O que aconteceu num passo depois do erro (ver DESFECHOS):
      sem_passo          o papel não teve esse passo (a execução acabou ou o papel parou);
      mesmo_limite       o passo falhou com a mesma mensagem (para o `global`, pega também a função definida antes
                         e chamada de novo, que não traz a palavra no código do passo);
      trocou_* / usa_*   o código do passo não tem / ainda tem a construção recusada; `ok` sem erro, `outro_erro` com
                         outro erro;
      nao_lido_*         sem construção para procurar (unpack) ou o código não parseia: só o erro conta."""
    if _vazio(passo):
        return "sem_passo"
    erro = "" if _vazio(erro) else str(erro)
    if erro and limite(erro) == lim:
        return "mesmo_limite"
    fim = "outro_erro" if erro else "ok"
    t = arvore(str(codigo)) if ALVO.get(lim) and not _vazio(codigo) else None
    if t is None:
        return f"nao_lido_{fim}"
    return f"{'usa' if ALVO[lim] in construtos(t) else 'trocou'}_{fim}"


def tipo_erro(msg):
    """O tipo do erro pela mensagem (o `next_error_type` só diz AgentExecutionError); '' se não houve erro."""
    if _vazio(msg):
        return ""
    m = re.search(r"due to: (\w+)", str(msg)) or re.match(r"\s*(\w+(?:Error|Exception))\b", str(msg))
    if not m:
        return "outro"
    lim = limite(str(msg)) if m.group(1) == "InterpreterError" else None   # outro limite do grupo: diz qual
    return f"InterpreterError ({lim})" if lim else m.group(1)


def _chave_casos(r):
    return (str(r["exec_id"]), str(r["agente"]), str(r["role"]), int(float(r["idx"])))


def ler_fonte(fonte):
    """A fonte só nas colunas usadas (pyarrow), como DataFrame."""
    import pyarrow.parquet as pq
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from mineracao_observada import caminho_io
    caminho = caminho_io(fonte)
    nomes = set(pq.read_schema(caminho).names)
    return pq.read_table(caminho, columns=[c for c in COLUNAS_FONTE if c in nomes]).to_pandas()


def depois(G, F):
    """Junta à população do grupo o que veio depois (desfecho e tipo do erro, nos passos `next` e `next2`) e a versão
    do agente. Devolve (G com as colunas novas, quantos erros não acharam linha na fonte)."""
    por = {}
    for r in F.to_dict("records"):
        por.setdefault((str(r["cod_idef_exeo"]), str(r["cod_idef_aget"]), str(r["papel"]), int(float(r["step_pos"]))), r)
    G = G.copy()
    linhas = [por.get(_chave_casos(r)) for _, r in G.iterrows()]
    for p in PASSOS:
        G[f"depois_{p}"] = [desfecho(lim, *(None, None, None) if l is None else
                                     (l.get(f"{p}_step_number"), l.get(f"{p}_code_action"), l.get(f"{p}_error_message")))
                            for lim, l in zip(G.limite, linhas)]
        G[f"erro_{p}"] = ["" if l is None else tipo_erro(l.get(f"{p}_error_message")) for l in linhas]
    G["versao_bruta"] = [None if l is None or _vazio(l.get("cod_vers_aget")) else str(l.get("cod_vers_aget"))
                         for l in linhas]
    sv = [sinais_verificacao(*(None, None) if l is None else (l.get("error_code_action"), l.get("prev_code_action")))
          for l in linhas]
    for k in sv[0] if sv else []:
        G[k] = [x[k] for x in sv]
    return G, sum(l is None for l in linhas)


def versoes(F, papeis):
    """Por papel, as versões do agente na fonte inteira, em ordem do 1º mês, com rótulos v1, v2… (o código da versão
    não sai): {papel: [(rótulo, versão bruta, 1º mês, último mês, passos)]}."""
    if "cod_vers_aget" not in F.columns or "mes_execucao" not in F.columns:
        return {}
    F = F[F.papel.isin(papeis)].copy()
    F["v"] = F.cod_vers_aget.map(lambda v: "sem versão" if _vazio(v) else str(v))
    out = {}
    for papel, g in F.groupby("papel"):
        t = g.groupby("v").mes_execucao.agg(["min", "max", "size"]).sort_values(["min", "max"])
        reais = iter(range(1, len(t) + 1))
        out[papel] = [(v if v == "sem versão" else f"v{next(reais)}", v, str(r["min"]), str(r["max"]), int(r["size"]))
                      for v, r in t.iterrows()]
    return out


def _imprimir_depois(G, faltam, V):
    print(f"\no que veio depois (fonte; {faltam} erros sem linha na fonte):")
    for lim, _ in LIMITES:
        g = G[G.limite == lim]
        if g.empty:
            continue
        print(f"  {lim} ({len(g)}):")
        for p in PASSOS:
            d = g[f"depois_{p}"].value_counts().reindex(DESFECHOS, fill_value=0)
            print(f"    passo {'seguinte' if p == 'next' else 'depois dele'}: {d[d > 0].to_dict()}")
        outros = g.loc[g.depois_next.str.endswith("outro_erro"), "erro_next"].value_counts()
        if len(outros):
            print(f"    o outro erro do passo seguinte: {outros.head(8).to_dict()}")
    print("\na instrução de verificação? (código do passo que falhou e do anterior; ver sinais_verificacao):")
    for lim in ("Global", "Re-raise", "Nonlocal"):
        for papel, g in G[G.limite == lim].groupby("role"):
            print(f"  {lim} · {papel} ({len(g)}): onde está o def com global "
                  f"{g.onde_def_global.value_counts().to_dict()} · uso "
                  f"{g.uso_global.value_counts().reindex(USOS_GLOBAL, fill_value=0).loc[lambda x: x > 0].to_dict()} · "
                  f"nome de verificação/estado {int(g.nome_de_estado.sum())} · globals()/locals()/vars() "
                  f"{int(g.introspeccao.sum())} · except NameError {int(g.except_nameerror.sum())} · "
                  f"raise sozinho em except NameError {int(g.raise_em_except_nameerror.sum())}")
    print("  controle, todos os limites (papel: erros · com globals()/locals()/vars() · com except NameError):")
    for (lim, papel), g in G.groupby(["limite", "role"]):
        print(f"    {lim} · {papel}: {len(g)} · {int(g.introspeccao.sum())} · {int(g.except_nameerror.sum())}")
    if V:
        print("\nversão do agente por papel (na fonte inteira; rótulo em ordem do 1º mês, o código não sai):")
        rot = {(p, v): r for p, vs in V.items() for r, v, *_ in vs}
        for papel, vs in V.items():
            g = G[G.role == papel]
            erros = Counter(rot.get((papel, v or "sem versão"), "?") for v in g.versao_bruta)
            print(f"  {papel}: " + " · ".join(f"{r} {a}→{b} ({n} passos; {erros.get(r, 0)} do grupo)"
                                             for r, _, a, b, n in vs))


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
    p.add_argument("--fonte", help="o parquet da base (com --casos): o que veio depois do erro e a versão do agente")
    a = p.parse_args(argv)
    if not a.casos and not a.trace:
        p.error("passe --casos, --trace ou os dois")
    if a.fonte and not a.casos:
        p.error("--fonte precisa do --casos")
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
            if a.fonte:
                F = ler_fonte(a.fonte)
                G, faltam = depois(G, F)
                V = versoes(F, set(G.role))
                _imprimir_depois(G, faltam, V)
                rot = {(p, v): r for p, vs in V.items() for r, v, *_ in vs}
                G["versao"] = [rot.get((p, v or "sem versão"), "") for p, v in zip(G.role, G.versao_bruta)]
                G = G.drop(columns=["versao_bruta"])
            destino = Path(a.casos).parent / "casos_limites_interpretador.csv"
            G.drop(columns=["mensagem"]).to_csv(destino, index=False)
            print(f"\n→ {destino} ({len(G)} erros; sem a coluna mensagem)")
    if a.trace:
        _prompt(a.trace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
