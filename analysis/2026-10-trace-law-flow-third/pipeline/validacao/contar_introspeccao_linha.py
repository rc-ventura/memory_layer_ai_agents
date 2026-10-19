"""Base 3: a introspecção proibida (`globals`, `locals`…) é uma verificação de existência? E o lado a lado com o
`try/except NameError`, por papel e mês.

Hipótese (dossiê do inventário do sandbox, `propostas/U_sandbox/dossie_base3.md`, parte A): a instrução do prompt do
ContestacaoCivel "VERIFIQUE se a variável de saída já está preenchida em memória; se já estiver, PULE a chamada" (vista
no prompt de julho, base 1) é cumprida com `'x' in globals()` em julho e com `try/except NameError` em agosto, quando o
prompt passou a mandar o `try/except` (§7.9). Se vale, (1) a linha que falhou nos erros de `globals` é uma verificação
de existência e (2) os dois erros se substituem no tempo, no mesmo papel.

  A. os erros de introspecção por papel × mês × função × uso da linha que falhou ('verificação de existência':
     `in globals()`, `globals().get(`, `globals()[`; ou 'outro uso');
  B. lado a lado por papel × mês: introspecção como verificação, introspecção em outro uso, `try/except NameError`.

Lê o parquet cru com o pyarrow (não usa o pipeline). Não grava nada. Imprime só contagens, nomes de papel e meses.
Uso, da raiz, na máquina da base:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_introspeccao_linha.py --fonte <parquet>
"""
import argparse
import re
import sys

import pandas as pd
import pyarrow.parquet as pq

INTROSPECCAO = ("globals", "locals", "vars", "dir")
RE_PROIBIDA = re.compile(r"Forbidden function evaluation: '(\w+)'")
LINHA_FALHA = re.compile(r"failed at line '(.*?)' due to", re.S)
VERIFICA = re.compile(r"\bin\s+(?:globals|locals|vars)\s*\(\s*\)|(?:globals|locals|vars)\s*\(\s*\)\s*(?:\.get\s*\(|\[)")
TRY_NAMEERROR = re.compile(r"except\s+\(?[^)\n:]*\bNameError\b")


def classificar(msg):
    """('introspecção', função, uso) | ('try/except NameError', None, None) | None."""
    msg = str(msg or "")
    linha = LINHA_FALHA.search(msg)
    linha = linha.group(1) if linha else ""
    f = RE_PROIBIDA.search(msg)
    if f and f.group(1) in INTROSPECCAO:
        return "introspecção", f.group(1), ("verificação de existência" if VERIFICA.search(linha) else "outro uso")
    if "is not defined" in msg and TRY_NAMEERROR.search(linha):
        return "try/except NameError", None, None
    return None


def medir(linhas):
    """linhas: dicts com papel, mes_execucao, structured_error, error_type, error_message. Devolve as tabelas A e B."""
    regs = []
    for r in linhas:
        if not (r.get("structured_error") == 1 and str(r.get("error_type") or "").strip()):
            continue
        c = classificar(r.get("error_message"))
        if c:
            regs.append({"papel": r["papel"], "mes": r["mes_execucao"], "erro": c[0], "funcao": c[1], "uso": c[2]})
    R = pd.DataFrame(regs, columns=["papel", "mes", "erro", "funcao", "uso"])
    I = R[R.erro.eq("introspecção")]
    A = I.groupby(["papel", "mes", "funcao", "uso"]).size().rename("erros").reset_index()
    R["coluna"] = R.erro.where(R.erro.ne("introspecção"), "introspecção · " + R.uso.fillna(""))
    B = R.pivot_table(index=["papel", "mes"], columns="coluna", values="erro", aggfunc="size", fill_value=0).reset_index()
    B.columns.name = None
    return {"A": A, "B": B}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fonte", required=True, help="o parquet da base 3 (a v2, em data/)")
    a = p.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    cols = ["papel", "mes_execucao", "structured_error", "error_type", "error_message"]
    T = medir(pq.read_table(a.fonte, columns=cols).to_pylist())
    pd.set_option("display.width", 200)
    print("A · erros de introspecção: papel × mês × função × uso da linha que falhou")
    print(T["A"].to_string(index=False) if len(T["A"]) else "  nenhum")
    print("\nB · lado a lado por papel × mês (introspecção como verificação, em outro uso, e try/except NameError)")
    print(T["B"].to_string(index=False) if len(T["B"]) else "  nenhum")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
