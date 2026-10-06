"""O encontro da parte genérica da mineração de uma candidata com a auditoria independente do balde visível.

    python comparar_auditoria.py <pasta-da-analise> <unidade> <medidas.json>

Lê pipeline/resultados/mineracao/<unidade>/casos.csv (a população da lição que o notebook genérico grava) e o JSON do
`audit_recompute6.py --json --unidade <unidade>`, que recalcula a lição direto do trace sem usar o pipeline. Compara,
no balde visível: erros, ocorrências, execuções, meses, papéis e erros por papel. As conferências internas: o perfil
soma o que o casos.csv tem, e as ocorrências totais = visíveis + silenciosas. Sai com 1 se algo diverge. Só contagens.
"""

import csv, json, os, sys
from collections import Counter


def main():
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(2)
    pasta, u, arq = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3]
    base = os.path.join(pasta, "pipeline", "resultados", "mineracao", u)
    casos = list(csv.DictReader(open(os.path.join(base, "casos.csv"), encoding="utf-8")))
    perfil = {r["medida"]: r["valor"] for r in csv.DictReader(open(os.path.join(base, "perfil.csv"), encoding="utf-8"))}
    aud = (json.load(open(arq, encoding="utf-8")).get("unidades") or {}).get(u)
    if aud is None:
        sys.exit(f"a auditoria não tem a unidade {u} (rode audit_recompute6.py --json … --unidade {u})")
    V = [r for r in casos if r["canal"] == "visível"]
    tabelas = {"erros": len(V), "ocorrencias_visiveis": len({r["ocorrencia"] for r in V}),
               "execucoes_visiveis": len({r["exec_id"] for r in V}), "meses_visiveis": len({r["mes"] for r in V}),
               "papeis_visiveis": len({r["role"] for r in V}),
               "erros_por_papel": dict(sorted(Counter(r["role"] for r in V).items()))}
    diverge = 0
    print(f"lição {u} — balde visível: tabelas da mineração × auditoria independente")
    for k in tabelas:
        a, b = tabelas[k], aud.get(k)
        diverge += a != b
        print(f"  {k:<22} tabelas {a} · auditoria {b}  {'OK' if a == b else 'DIVERGE'}")
    S = [r for r in casos if r["canal"] == "silencioso"]
    internas = [
        ("perfil: erros = linhas visíveis do casos.csv", int(perfil["erros"]) == len(V)),
        ("perfil: ocorrências = visíveis + silenciosas", int(perfil["ocorrencias"]) ==
         len({r["ocorrencia"] for r in V}) + len({r["ocorrencia"] for r in S})),
        ("perfil: execuções = execuções do casos.csv (os dois canais)", int(perfil["execucoes"]) == len({r["exec_id"] for r in casos})),
    ]
    print("\nconferências internas:")
    for rot, ok in internas:
        diverge += not ok
        print(f"  {'OK  ' if ok else 'FALHA'}  {rot}")
    print(f"\nauditoria × tabelas: {'tudo igual' if not diverge else f'{diverge} divergência(s) — parar'}")
    sys.exit(1 if diverge else 0)


if __name__ == "__main__":
    main()
