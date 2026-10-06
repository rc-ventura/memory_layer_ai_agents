"""O cenário de cobertura do protocolo do harness: os papéis ordenados por número de erros, com a cobertura acumulada.
Até onde ir é decisão do pesquisador; o script só dá a tabela.

    python cobertura.py <pasta-da-analise>

Lê pipeline/resultados/evidencia/protocolo/casos.csv. Imprime, por papel: erros, % do total, % acumulado, meses com
erro e erros fora da primeira chamada do papel. Só contagens; só biblioteca padrão.
"""

import csv, os, sys
from collections import Counter, defaultdict


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    arq = os.path.join(os.path.abspath(sys.argv[1]), "pipeline", "resultados", "evidencia", "protocolo", "casos.csv")
    C = list(csv.DictReader(open(arq, encoding="utf-8")))
    if not C:
        print("nenhum erro da família nesta base"); return
    n = Counter(r["role"] for r in C)
    meses, fora = defaultdict(set), Counter()
    for r in C:
        meses[r["role"]].add(r["mes"])
        fora[r["role"]] += int(r.get("chamada") or 1) > 1
    total, acum = len(C), 0
    print(f"{'papel':<28} {'erros':>6} {'%':>6} {'acum.':>7} {'meses':>6} {'fora da 1ª chamada':>19}")
    for papel, k in n.most_common():
        acum += k
        print(f"{papel:<28} {k:>6} {k / total:>6.0%} {acum / total:>7.0%} {len(meses[papel]):>6} {fora[papel]:>19}")
    print(f"\ntotal: {total} erros em {len(n)} papéis")


if __name__ == "__main__":
    main()
