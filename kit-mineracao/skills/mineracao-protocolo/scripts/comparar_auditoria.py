"""O encontro das duas implementações da mineração do protocolo do harness: as tabelas que o `drill_down.py protocolo`
grava × as medidas que a auditoria independente recalculou direto do trace. Não compara com relatório nenhum.

    python comparar_auditoria.py <pasta-da-analise> <medidas.json>

Lê de pipeline/resultados/evidencia/protocolo/: casos.csv (um erro por linha), passos.csv (steps por mês e papel),
versoes.csv (versões do formato do prompt) e modelos.csv (modelo e versão do agente). Imprime medida por medida
(tabelas · auditoria · OK/DIVERGE) e as conferências internas; sai com 1 se algo diverge. Só contagens; só biblioteca
padrão.
"""

import csv, json, os, sys
from collections import Counter, defaultdict

LIMIAR_M1 = 0.5


def ler(pasta, nome):
    return list(csv.DictReader(open(os.path.join(pasta, nome), encoding="utf-8")))


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    ev = os.path.join(os.path.abspath(sys.argv[1]), "pipeline", "resultados", "evidencia", "protocolo")
    aud = json.load(open(sys.argv[2], encoding="utf-8"))
    C, P, V, M = (ler(ev, n) for n in ("casos.csv", "passos.csv", "versoes.csv", "modelos.csv"))

    steps_mes, steps_papel = Counter(), Counter()
    for r in P:
        steps_mes[r["mes"]] += int(r["steps"]); steps_papel[r["role"]] += int(r["steps"])
    sim = lambda v: v == "True"
    tabelas = {
        "erros": len(C), "execucoes": len({r["exec_id"] for r in C}), "papeis": len({r["role"] for r in C}),
        "steps": sum(steps_mes.values()),
        "steps_por_mes": dict(sorted(steps_mes.items())), "steps_por_papel": dict(sorted(steps_papel.items())),
        "erros_por_mes": dict(sorted(Counter(r["mes"] for r in C).items())),
        "erros_por_papel": dict(sorted(Counter(r["role"] for r in C).items())),
        "formas": dict(sorted(Counter(r["forma"] for r in C).items())),
        "papel_entregou_depois": sum(sim(r["papel_entregou_depois"]) for r in C),
        "execucao_com_resposta": sum(sim(r["execucao_com_resposta"]) for r in C),
        "proximo": dict(sorted(Counter(r["proximo"] for r in C).items())),
        "versoes": {f"{r['role']}|{r['versao']}": [r["modo"], int(r["steps"]), int(r["erros"])] for r in V},
        "modelos": {f"{r['role']}|{r['eixo']}|{r['valor']}": [int(r["steps"]), int(r["erros"])] for r in M},
        "m1_antecipou_por_papel": dict(sorted(Counter(r["role"] for r in C if float(r["sobreposicao_final"]) >= LIMIAR_M1).items())),
        "m1_copiou_por_papel": dict(sorted(Counter(r["role"] for r in C if float(r["sobreposicao_obs_anterior"]) >= LIMIAR_M1).items())),
        "erros_em_chamada_maior_que_1": sum(int(r["chamada"]) > 1 for r in C),
        "erros_em_papel_com_varias_chamadas": sum(int(r["chamadas_do_papel"]) > 1 for r in C),
        "sinal_resto_por_papel": dict(sorted(Counter(r["role"] for r in C if r.get("sinal_resto") == "True").items())),
        "depois_da_ferramenta_final_por_papel": dict(sorted(Counter(r["role"] for r in C if r.get("anterior_ferramenta_final") == "True").items())),
        "regra_ferramenta_final_por_papel": dict(sorted(Counter(r["role"] for r in C if r.get("regra_ferramenta_final") == "True").items())),
    }

    diverge = 0
    print(f"{'medida':<40} {'resultado'}")
    for k in sorted(set(tabelas) | (set(aud) - {"base"})):
        a, b = tabelas.get(k), aud.get(k)
        if isinstance(a, dict) or isinstance(b, dict):
            a, b = a or {}, b or {}
            dif = sorted(c for c in set(a) | set(b) if a.get(c) != b.get(c))
            diverge += bool(dif)
            print(f"{k:<40} {len(set(a) | set(b))} chaves · " + ("OK" if not dif else f"DIVERGE em {len(dif)}: " +
                  "; ".join(f"{c}: tabelas {a.get(c)} × auditoria {b.get(c)}" for c in dif[:5])))
        else:
            diverge += a != b
            print(f"{k:<40} tabelas {a} · auditoria {b}  {'OK' if a == b else 'DIVERGE'}")

    print("\nconferências internas (valem em qualquer base):")
    internas = [
        ("soma por papel = soma por mês = total", sum(Counter(r['role'] for r in C).values()) == sum(Counter(r['mes'] for r in C).values()) == len(C)),
        ("todo erro tem forma", all(r["forma"] for r in C)),
        ("o que vem depois soma o total", sum(Counter(r["proximo"] for r in C).values()) == len(C)),
        ("erros nas versões do formato = total", sum(int(r["erros"]) for r in V) == len(C)),
        ("erros por modelo = total", sum(int(r["erros"]) for r in M if r["eixo"] == "modelo") == len(C)),
    ]
    for rot, ok in internas:
        diverge += not ok
        print(f"  {'OK  ' if ok else 'FALHA'}  {rot}")
    print(f"\nauditoria × tabelas: {'tudo igual' if not diverge else f'{diverge} divergência(s) — parar'}")
    sys.exit(1 if diverge else 0)


if __name__ == "__main__":
    main()
