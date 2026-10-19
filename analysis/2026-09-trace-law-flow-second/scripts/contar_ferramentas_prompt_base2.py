"""Base 2 (trace completo; roda também na base 1): o prompt dos papéis das partes B, C e D do inventário do sandbox.

Hipótese (dossiê do sandbox na base 3, `propostas/U_sandbox/dossie_base3.md`, §2e): a parte B ("ferramenta importada
como módulo", 212 erros na base 3, 167 deles `get_document_text` no OBFCivel) vem do prompt — o prompt do OBFCivel
manda "use `get_document_text` …", mas `get_document_text` não está entre as ferramentas declaradas (os `def` do
prompt); o agente tenta importá-la e o sandbox barra. Visto na base 1 (11 execuções, uma versão do prompt). Se vale na
base 2, B é sinal de harness, não memória (a memória "chame-as direto, sem import" mandaria chamar uma função que não
existe).

  A. por papel × versão das ferramentas declaradas (hash dos nomes dos `def` do prompt): execuções, meses, as
     ferramentas declaradas, e se o prompt menciona / declara `get_document_text` e `python_interpreter`;
  B. os erros de import de ferramenta (a parte B: `Import of`/`No module named` com um nome de ferramenta ou do
     framework) por papel × versão — e se o nome importado é uma ferramenta declarada naquela versão;
  C. as pistas das partes C e D no prompt, por papel: a frase da lista de imports autorizados; `pd.`/`pandas`
     descrito no retorno de uma ferramenta.

Usa o leitor do `contar_primeiro_passo_nome_base2.py`. Não grava nada. Imprime só contagens, nomes de papel, meses,
hashes e nomes de ferramenta. Uso, da raiz, na máquina da base 2:
    uv run python analysis/2026-09-trace-law-flow-second/scripts/contar_ferramentas_prompt_base2.py --trace <trace da base 2>
"""
import argparse
import hashlib
from pathlib import Path
import re
import sys

import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from contar_primeiro_passo_nome_base2 import bp, explodir  # noqa: E402

DEF = re.compile(r"^def (\w+)\(", re.M)
# a regra da parte B (racional do sandbox, emenda 4): o framework, os nomes de ferramenta genéricos, ou get_*
FERRAMENTA = re.compile(r"^(?:smolagents|mcp|mcp_client|tools|tool_usage|tool_functions|python_interpreter|get_\w*)$")
IMPORT = re.compile(r"Import (?:of|from) ([\w.]+) is not allowed|No module named '([^']+)'")
LISTA = re.compile(r"You can use imports in your code, but only from the following list of modules")
PANDAS_NO_RETORNO = re.compile(r"pd\.\w+\(|pandas DataFrame|pandas dataframe")
VIGIADAS = ("get_document_text", "python_interpreter")


def ferramentas(prompt):
    """Os nomes das ferramentas declaradas no prompt (os `def`) e o hash da lista (a versão)."""
    defs = sorted(set(DEF.findall(str(prompt or ""))))
    return defs, (hashlib.sha256(",".join(defs).encode("utf-8")).hexdigest()[:10] if defs else "(nenhuma)")


def importado(msg):
    """O nome da ferramenta que o agente tentou importar (parte B), ou None."""
    m = IMPORT.search(str(msg or "").rsplit("due to:", 1)[-1])
    if not m:
        return None
    nome = m.group(1) or m.group(2)
    return nome if FERRAMENTA.match(nome.split(".")[0]) else None


def medir(S):
    """S: um ActionStep por linha (exec_id, agente, role, idx, mes, err_type, err_msg, sysprompt)."""
    prim = S[S.idx.eq(0)][["exec_id", "agente", "role", "mes", "sysprompt"]].copy()
    fv = [ferramentas(p) for p in prim.sysprompt]
    prim["versao"] = [v for _, v in fv]
    prim["declaradas"] = [", ".join(d) for d, _ in fv]
    for n in VIGIADAS:
        prim[f"menciona_{n}"] = prim.sysprompt.fillna("").str.contains(n, regex=False)
        prim[f"declara_{n}"] = [n in d for d, _ in fv]
    A = (prim.groupby(["role", "versao", "declaradas"] + [f"{k}_{n}" for n in VIGIADAS for k in ("menciona", "declara")])
         .agg(execucoes=("exec_id", "size"), meses=("mes", lambda s: ", ".join(sorted(set(s)))))
         .reset_index().sort_values(["role", "execucoes"], ascending=[True, False]))
    E = S[S.err_type.notna()].assign(nome=lambda d: d.err_msg.map(importado))
    E = E[E.nome.notna()].merge(prim[["exec_id", "agente", "role", "versao", "declaradas"]],
                                on=["exec_id", "agente", "role"], how="left")
    E["declarada_na_versao"] = [str(n).split(".")[0] in str(d).split(", ") for n, d in zip(E.nome, E.declaradas)]
    B = (E.groupby(["role", "versao", "nome", "declarada_na_versao"], dropna=False).size().rename("erros")
         .reset_index().sort_values(["role", "erros"], ascending=[True, False]))
    C = (prim.assign(lista_de_imports=prim.sysprompt.fillna("").str.contains(LISTA),
                     pandas_no_retorno=prim.sysprompt.fillna("").str.contains(PANDAS_NO_RETORNO))
         .groupby("role").agg(execucoes=("exec_id", "size"), com_lista_de_imports=("lista_de_imports", "sum"),
                              com_pandas_no_retorno=("pandas_no_retorno", "sum")).reset_index())
    return {"A": A, "B": B, "C": C}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trace", required=True, type=Path, help="o arquivo do trace cru (CSV ou parquet)")
    p.add_argument("--papel", help="só este papel na tabela A (ex.: OBFCivel)")
    a = p.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    bp.TRACE = str(a.trace)
    T = medir(explodir(bp.carregar_trace()))
    pd.set_option("display.width", 220)
    pd.set_option("display.max_colwidth", 160)
    A = T["A"] if not a.papel else T["A"][T["A"].role.eq(a.papel)]
    print("A · papel × versão das ferramentas declaradas (os `def` do prompt): menciona/declara get_document_text e python_interpreter")
    for r in A.itertuples(index=False):
        print(f"  {r.role} · versão {r.versao} · {r.execucoes} execuções · meses {r.meses}")
        print(f"     menciona/declara get_document_text: {r.menciona_get_document_text}/{r.declara_get_document_text} · "
              f"python_interpreter: {r.menciona_python_interpreter}/{r.declara_python_interpreter}")
        print(f"     declaradas: {r.declaradas}")
    print("\nB · erros de import de ferramenta (parte B) por papel × versão: o nome importado é ferramenta declarada na versão?")
    print(T["B"].to_string(index=False) if len(T["B"]) else "  nenhum")
    print("\nC · pistas das partes C e D no prompt (primeiro passo), por papel")
    print(T["C"].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
