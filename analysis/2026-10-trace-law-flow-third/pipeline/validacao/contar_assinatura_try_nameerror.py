"""A assinatura `try/except NameError` na mensagem de erro: a base 3 tem evidência própria da causa do primeiro passo?

Na base 2 (trace inteiro, relatório da base 3 §7.9), o erro de nome no primeiro passo do ContestacaoCivel vem de uma
instrução do system prompt: verificar se a variável existe com `try: nome` / `except NameError: nome = ...`. O
interpretador do sandbox levanta `InterpreterError` para o nome inexistente, que o `except NameError` não captura
(reproduzido no smolagents 1.26.0). A base 3 não tem o prompt, mas a mensagem de erro traz a linha que falhou
("Code execution failed at line 'try: ... except NameError: ...' due to: InterpreterError: The variable `x` is not
defined"). Este script conta essa assinatura:

  1. nos erros de nome não definido pendentes por "predecessor não identificado" (os 5.818 do primeiro passo);
  2. em TODOS os erros de nome não definido, pela situação atual (unidade ou motivo da pendência) — mostra se parte do
     "estado perdido" ou do "nome inventado" é o mesmo padrão;
  3. por papel e mês.

"Duvidoso" = a linha que falhou começa com `try:` mas não traz `except NameError` (outra forma de verificação, ou a
mensagem cortada). Não muda regra nem grava nada. Imprime só contagens, nomes de papel e de unidade, e meses. Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_assinatura_try_nameerror.py [--fonte <parquet>]
"""
import argparse
from pathlib import Path
import re
import sys

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE.parents[1]))
import base_pipeline as bp

MOTIVO_PRIMEIRO_PASSO = "predecessor_nao_identificado_sql"
LINHA = re.compile(r"failed at line '(.*?)' due to", re.S)


def assinatura(msg):
    """'try/except NameError', 'duvidoso' (linha começa com try: sem except NameError) ou 'não'."""
    m = str(msg)
    linha = LINHA.search(m)
    trecho = linha.group(1) if linha else ""
    if re.search(r"except\s+\(?[^)\n:]*\bNameError\b", trecho):
        return "try/except NameError"
    if trecho.lstrip().startswith("try:"):
        return "duvidoso"
    return "não"


def situacao(r):
    if r.situacao_mecanismo == "pendente":
        return "pendente: " + str(r.motivo_evidencia)
    return str(r.unidade)


def contar(carga):
    EU = bp.analisar_mecanismos_observaveis(carga).EU
    N = EU[[bp.submecanismo(m) == "nome_nao_definido" for m in EU.err_msg]].copy()
    N["assinatura"] = N.err_msg.map(assinatura)
    N["situacao"] = [situacao(r) for r in N.itertuples()]
    return EU, N


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fonte", type=Path, default=Path(bp.TRACE))
    args = p.parse_args(argv)
    EU, N = contar(bp.carregar_carga(args.fonte))
    print("erros estruturados:", len(EU), "| de nome não definido:", len(N))
    print("assinatura em todos os erros de nome:", N.assinatura.value_counts().to_dict())

    P = N[N.motivo_evidencia.eq(MOTIVO_PRIMEIRO_PASSO)]
    print("\n1 · os pendentes do primeiro passo:", len(P), "| assinatura:", P.assinatura.value_counts().to_dict())

    print("\n2 · todos os erros de nome, pela situação atual × assinatura:")
    print(pd.crosstab(N.situacao, N.assinatura, margins=True, margins_name="total").to_string())

    print("\n3 · com a assinatura, por papel × mês (os 15 maiores):")
    A = N[N.assinatura.eq("try/except NameError")]
    print(A.groupby(["role", "mes"]).size().rename("erros").reset_index()
          .sort_values("erros", ascending=False).head(15).to_string(index=False) if len(A) else "  nenhum")

    outros = EU[~EU.index.isin(N.index) & EU.err_msg.astype(str).str.contains("except NameError", regex=False)]
    print("\nerros que não são de nome não definido, mas cuja mensagem traz 'except NameError':", len(outros),
          "| por tipo:", outros.err_type.value_counts().head(5).to_dict())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
