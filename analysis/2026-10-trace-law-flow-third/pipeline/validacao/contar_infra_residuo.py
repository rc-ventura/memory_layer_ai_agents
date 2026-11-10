"""Base 3: o grupo "infra / LLM" do resíduo (b3 #5) — quem falhou, por regra, antes de ler casos.

O resíduo da rodada `13b0d026242de2dc` (Ajuste 34) tem, no balde "sintoma não reconhecido", exceções de rede, de API,
de política de conteúdo do LLM e de ferramenta que nenhuma regra conhece: `APIConnectionError`, `APIStatusError`,
`BadRequestError` (política de conteúdo), `RecoverableToolError` e `RuntimeError: Invalid structured content returned by
tool …`. A hipótese (procedimento do resíduo, passo 4, pergunta R2): a falha é da plataforma (a rede, a API, o modelo,
a ferramenta), não do agente, e o destino é uma unidade de não-memória — estendendo a `H_infra_llm` (hoje só
`AgentGenerationError`, "internally hosted" e 422) ou a `H_timeout_ferramenta`, ou criando outra.

Duas medidas respondem boa parte disso sem ler caso:
  - **o tipo do erro do passo** (`err_type`): `AgentGenerationError` = falhou a geração do modelo; `AgentExecutionError`
    = falhou a execução do código que o agente escreveu (a falha veio de dentro de uma chamada);
  - **a função chamada na linha que falhou** (`Code execution failed at line '<linha>' due to: …`): o nome da ferramenta
    (ou função) que levantou a exceção. "sem linha" = a mensagem não traz a linha (falha fora da execução do código).

Para cada grupo da hipótese: erros, execuções, meses, papéis e tokens; e, cruzados, o tipo do erro × a função. Grava
`casos_infra.csv` (os erros do grupo, com as colunas `grupo` e `funcao_na_linha`) na pasta do `casos.csv`, para o
`montar_evidencia.py --de mineracao/residuo/<pasta>/casos_infra.csv --onde grupo=<g>` montar a amostra com os crus.

Não muda nada no pipeline e fica fora do hash da rodada. Imprime só contagens, nomes de papel, tipos de erro, nomes de
função e meses: nada de mensagem nem de identificador. Uso, da raiz, no ambiente da base:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_infra_residuo.py
        --casos <pipeline/resultados/mineracao/residuo/<pasta>/casos.csv>
"""
import argparse
from pathlib import Path
import re
import sys

import pandas as pd

# os grupos da hipótese, em ordem: o primeiro que casa a mensagem vale
GRUPOS = [
    ("rede_api", re.compile(r"\bAPI(?:Connection|Status|Timeout)Error\b")),
    ("politica_llm", re.compile(r"\bBadRequestError\b|ContentPolicyViolation")),
    ("ferramenta_recuperavel", re.compile(r"\bRecoverableToolError\b")),
    ("ferramenta_conteudo", re.compile(r"Invalid structured content returned by tool")),
]
LINHA = re.compile(r"failed at line '(.*?)' due to", re.S)
CHAMADA = re.compile(r"([A-Za-z_][\w.]*)\s*\(")


def grupo(msg):
    for nome, rx in GRUPOS:
        if rx.search(msg):
            return nome
    return None


def funcao_na_linha(msg):
    """A primeira função chamada na linha que falhou (sem `print`), ou "sem linha"."""
    m = LINHA.search(msg)
    if not m:
        return "sem linha"
    nomes = [n for n in CHAMADA.findall(m.group(1)) if n.split(".")[-1] not in {"print", "str", "len", "int", "float"}]
    return nomes[0] if nomes else "linha sem chamada"


def contar(C):
    C = C.copy()
    C["mensagem"] = C["mensagem"].fillna("").astype(str)
    C["grupo"] = [grupo(m) for m in C.mensagem]
    G = C[C.grupo.notna()].copy()
    G["funcao_na_linha"] = [funcao_na_linha(m) for m in G.mensagem]
    return G


def _resumo(g):
    return (f"{len(g)} erros · {len(g[['exec_id', 'agente']].drop_duplicates())} execuções · {g.mes.nunique()} meses · "
            f"{g.role.nunique()} papéis · {int(g.tok_tot.fillna(0).sum()):,} tokens".replace(",", "."))


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--casos", required=True)
    a = p.parse_args(argv)
    C = pd.read_csv(a.casos, dtype={"exec_id": str, "agente": str})
    if "mensagem" not in C.columns:
        print("casos.csv sem a coluna `mensagem`: rode o `especificas/residuo.py` desta versão")
        return 1
    G = contar(C)
    print(f"resíduo: {len(C)} erros · no grupo infra / LLM: {_resumo(G)}")
    print(f"  por balde: {G.unidade.value_counts().to_dict()}")
    for nome, _ in GRUPOS:
        g = G[G.grupo.eq(nome)]
        if g.empty:
            print(f"\n== {nome}: 0 erros")
            continue
        print(f"\n== {nome}: {_resumo(g)}")
        print(f"  papéis: {g.role.value_counts().to_dict()}")
        print(f"  meses: {g.mes.value_counts().sort_index().to_dict()}")
        print("  tipo do erro × função na linha que falhou:")
        for (t, f), n in g.groupby(["err_type", "funcao_na_linha"]).size().sort_values(ascending=False).items():
            print(f"    {n:4d}  {t} · {f}")
    destino = Path(a.casos).parent / "casos_infra.csv"
    G.drop(columns=["mensagem"]).to_csv(destino, index=False)
    print(f"\n→ {destino} ({len(G)} erros; sem a coluna mensagem)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
