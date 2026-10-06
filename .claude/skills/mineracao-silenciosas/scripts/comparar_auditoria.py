"""O encontro das duas implementações: as tabelas da mineração das falhas silenciosas × as medidas que a auditoria
independente recalculou direto do trace. Não compara com relatório nenhum: numa base nova, as duas chegarem no mesmo
número é a verificação.

    python comparar_auditoria.py <pasta-da-analise> <medidas.json>

Lê, da pasta da análise:
  pipeline/resultados/evidencia/silenciosas/casos.csv        (uma linha por falha silenciosa — `drill_down.py silenciosas`)
  pipeline/resultados/evidencia/silenciosas/ocorrencias.csv  (a saída do notebook para a consolidação)
  pipeline/base_pipeline.py                                  (só a tupla GRUPOS_FALHA_REAL, lida pela AST)
e o JSON gravado por `audit_recompute9.py --json`. Imprime medida por medida (tabelas · auditoria · OK/DIVERGE) e as
conferências internas; sai com 1 se algo diverge. Só contagens; só biblioteca padrão.
"""

import ast, csv, json, os, sys
from collections import Counter


def grupos_reais(base_pipeline):
    arv = ast.parse(open(base_pipeline, encoding="utf-8").read())
    return set(next(ast.literal_eval(n.value) for n in arv.body if isinstance(n, ast.Assign)
                    and any(getattr(t, "id", "") == "GRUPOS_FALHA_REAL" for t in n.targets)))


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    pasta, aud = os.path.abspath(sys.argv[1]), json.load(open(sys.argv[2], encoding="utf-8"))
    ev = os.path.join(pasta, "pipeline", "resultados", "evidencia", "silenciosas")
    casos = [r for r in csv.DictReader(open(os.path.join(ev, "casos.csv"), encoding="utf-8"))
             if r.get("falha", "silenciosa") == "silenciosa"]
    ocorr = list(csv.DictReader(open(os.path.join(ev, "ocorrencias.csv"), encoding="utf-8")))
    reais = grupos_reais(os.path.join(pasta, "pipeline", "base_pipeline.py"))

    g = Counter(r["grupo"] for r in casos)
    cand = Counter(r["grupo"] for r in casos if r["grupo"] in reais and r["sucesso_falso_candidato"] == "True")
    tot = Counter(r["grupo"] for r in casos if r["grupo"] in reais)
    unid = Counter(r["unidade"] for r in ocorr if r.get("unidade") and r.get("canal", "silencioso") == "silencioso")
    tabelas = {
        "silenciosas": len(casos),
        "steps_silenciosos": len({(r["exec_id"], r["role"], r["idx"]) for r in casos}),
        "execucoes": len({r["exec_id"] for r in casos}),
        "meses": len({r["mes"] for r in casos}),
        "papeis": len({r["role"] for r in casos}),
        "ferramentas": len({r["ferramenta"] for r in casos}),
        **{f"grupo {k}": v for k, v in g.items()},
        "falhas_reais": sum(tot.values()),
        **{f"sucesso falso {k} (candidatos/reais)": [cand.get(k, 0), tot[k]] for k in tot},
        "sucesso falso total (candidatos/reais)": [sum(cand.values()), sum(tot.values())],
        **{f"steps silenciosos da unidade {u}": unid.get(u, 0) for u in aud.get("steps_silenciosos_por_unidade", {})},
    }
    auditoria = {k: aud[k] for k in ("silenciosas", "steps_silenciosos", "execucoes", "meses", "papeis", "ferramentas",
                                     "falhas_reais")}
    auditoria.update({f"grupo {k}": v for k, v in aud["grupos"].items()})
    auditoria.update({f"sucesso falso {k} (candidatos/reais)": v for k, v in aud["sucesso_falso"]["por_grupo"].items()})
    auditoria["sucesso falso total (candidatos/reais)"] = aud["sucesso_falso"]["total"]
    auditoria.update({f"steps silenciosos da unidade {u}": v for u, v in aud.get("steps_silenciosos_por_unidade", {}).items()})

    diverge = 0
    print(f"{'medida':<52} {'tabelas':>12} {'auditoria':>12}")
    for k in sorted(set(tabelas) | set(auditoria)):
        a, b = tabelas.get(k, 0), auditoria.get(k, 0)
        ok = a == b
        diverge += not ok
        print(f"{k:<52} {str(a):>12} {str(b):>12}  {'OK' if ok else 'DIVERGE'}")

    print("\nconferências internas (valem em qualquer base):")
    internas = [("soma dos grupos = silenciosas (tabelas)", sum(g.values()) == len(casos)),
                ("silenciosas que caíram no balde visível = 0 (auditoria)", aud["silenciosas_no_visivel"] == 0)]
    for rot, ok in internas:
        diverge += not ok
        print(f"  {'OK  ' if ok else 'FALHA'}  {rot}")
    print(f"\nauditoria × tabelas: {'tudo igual' if not diverge else f'{diverge} divergência(s) — parar'}")
    sys.exit(1 if diverge else 0)


if __name__ == "__main__":
    main()
