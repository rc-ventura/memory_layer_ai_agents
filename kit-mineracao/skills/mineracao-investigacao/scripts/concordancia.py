"""Concordância entre dois leitores (o investigador e o segundo leitor) — o número sai daqui, não do LLM.

    python concordancia.py <leitura1.csv> <leitura2.csv> --rotulo <coluna> [--coluna-idx idx]

Casa as duas leituras por (exec_id, role, idx) e imprime: casos em comum, concordância simples e kappa de Cohen, e a
tabela das discordâncias por par de categorias (só contagens). Só biblioteca padrão.
"""

import argparse, csv
from collections import Counter


def ler(arq, col_idx, rotulo):
    with open(arq, encoding="utf-8", newline="") as fh:
        return {(r["exec_id"], r["role"], r[col_idx]): r[rotulo] for r in csv.DictReader(fh)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("--rotulo", required=True)
    ap.add_argument("--coluna-idx", default="idx")
    x = ap.parse_args()
    A, B = ler(x.a, x.coluna_idx, x.rotulo), ler(x.b, x.coluna_idx, x.rotulo)
    comuns = sorted(set(A) & set(B))
    if not comuns:
        print("nenhum caso em comum"); return
    iguais = sum(A[k] == B[k] for k in comuns)
    po = iguais / len(comuns)
    ca, cb = Counter(A[k] for k in comuns), Counter(B[k] for k in comuns)
    pe = sum(ca[c] * cb[c] for c in set(ca) | set(cb)) / len(comuns) ** 2
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    print(f"casos em comum: {len(comuns)} · concordam: {iguais} ({po:.0%}) · kappa: {kappa:.2f}")
    for (ra, rb), n in Counter((A[k], B[k]) for k in comuns if A[k] != B[k]).most_common():
        print(f"  discordância  {ra}  ×  {rb}: {n}")


if __name__ == "__main__":
    main()
