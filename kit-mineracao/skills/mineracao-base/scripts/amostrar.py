"""Escolhe os casos que o investigador vai ler — por regra fixa, nunca por escolha do LLM.

    python amostrar.py <casos.csv> --saida <amostra.csv> [--onde coluna=valor ...] [--por coluna,...]
                       [--regra procedimento|primeiro-por-mes|semente] [--n 10] [--semente 20261005]

Regras (a de `procedimento` é a das pastas de evidência):
  procedimento      todos, se forem até --n; senão o 1º de cada mês (ordem mes, exec_id, idx)
  primeiro-por-mes  o 1º de cada mês, sempre
  semente           --n casos sorteados com random.Random(--semente) — para o segundo leitor e para amostras grandes
`--por` aplica a regra dentro de cada grupo (ex.: --por ferramenta). `--onde` filtra antes (pode repetir).

Grava a amostra (as colunas da entrada + `regra_amostra`) e imprime só contagens — nenhum identificador.
Só biblioteca padrão.
"""

import argparse, csv, random, sys
from collections import defaultdict

ORDEM = ("mes", "exec_id", "idx")


def chave_ordem(r):
    return tuple(int(r[c]) if c == "idx" and r.get(c, "").isdigit() else r.get(c, "") for c in ORDEM)


def amostrar(linhas, regra, n, semente):
    linhas = sorted(linhas, key=chave_ordem)
    if regra == "semente":
        return random.Random(semente).sample(linhas, min(n, len(linhas))), f"semente {semente}, n={n}"
    if regra == "procedimento" and len(linhas) <= n:
        return linhas, f"todos (até {n})"
    if linhas and "mes" not in linhas[0]:
        sys.exit("a entrada não tem a coluna `mes`: use --regra semente (ou junte o mês antes)")
    vistos, out = set(), []
    for r in linhas:
        if r["mes"] not in vistos:
            vistos.add(r["mes"]); out.append(r)
    return out, "1º de cada mês (mes, exec_id, idx)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada"); ap.add_argument("--saida", required=True)
    ap.add_argument("--onde", action="append", default=[]); ap.add_argument("--por", default="")
    ap.add_argument("--regra", default="procedimento", choices=["procedimento", "primeiro-por-mes", "semente"])
    ap.add_argument("--n", type=int, default=10); ap.add_argument("--semente", type=int, default=20261005)
    a = ap.parse_args()

    with open(a.entrada, encoding="utf-8", newline="") as fh:
        linhas = list(csv.DictReader(fh))
    for cond in a.onde:
        col, val = cond.split("=", 1)
        linhas = [r for r in linhas if r.get(col) == val]
    grupos = defaultdict(list)
    por = [c for c in a.por.split(",") if c]
    for r in linhas:
        grupos[tuple(r.get(c, "") for c in por)].append(r)

    amostra = []
    for g in sorted(grupos):
        escolhidos, rotulo = amostrar(grupos[g], a.regra, a.n, a.semente)
        amostra += [{**r, "regra_amostra": rotulo} for r in escolhidos]
        if por:
            print(f"  grupo {'/'.join(g)}: {len(grupos[g])} → {len(escolhidos)} ({rotulo})")
    if not amostra:
        sys.exit("nenhum caso depois dos filtros")
    with open(a.saida, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(amostra[0])); w.writeheader(); w.writerows(amostra)
    print(f"população (depois dos filtros): {len(linhas)} · amostra: {len(amostra)} · regra: {a.regra} → {a.saida}")


if __name__ == "__main__":
    main()
