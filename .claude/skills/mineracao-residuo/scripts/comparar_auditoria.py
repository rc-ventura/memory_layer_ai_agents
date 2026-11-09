"""O encontro das duas implementações da mineração do resíduo: a tabela de padrões que a mineração gravou × as medidas
que a auditoria independente recalculou direto da fonte. Não compara com relatório nenhum.

    python comparar_auditoria.py <pasta-da-analise> <medidas.json> [--tabelas <pasta>]

Lê de <pasta-da-analise>/pipeline/resultados/mineracao/residuo/ (ou de --tabelas): residuo_padroes.csv (um padrão
por linha) e casos.csv (um erro por linha). Compara padrão por padrão (erros, execuções, meses, papéis, tokens, chave,
passa na recorrência), os padrões que só um dos dois tem e os totais por balde. Roda as conferências internas: a soma
dos padrões = as linhas do casos.csv; erros por balde iguais nas duas tabelas; todo caso tem padrão. Imprime medida por
medida e sai com 1 se algo diverge ou falha. Só contagens e padrões mascarados; só biblioteca padrão.
"""

import argparse, csv, json, os, sys
from collections import Counter

MEDIDAS = ["erros", "execucoes", "meses", "papeis", "tokens", "tokens_ausentes", "chave", "passa_na_recorrencia"]


def _num(v):
    if v in ("", None):
        return 0
    if v in ("True", "False"):
        return v == "True"
    try:
        f = float(v)
        return int(f) if f == int(f) else f
    except ValueError:
        return v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pasta"); ap.add_argument("medidas"); ap.add_argument("--tabelas")
    a = ap.parse_args()
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    pasta = a.tabelas or os.path.join(os.path.abspath(a.pasta), "pipeline", "resultados", "mineracao", "residuo")
    with open(os.path.join(pasta, "residuo_padroes.csv"), encoding="utf-8", newline="") as fh:
        P = list(csv.DictReader(fh))
    with open(os.path.join(pasta, "casos.csv"), encoding="utf-8", newline="") as fh:
        C = list(csv.DictReader(fh))
    with open(a.medidas, encoding="utf-8") as fh:
        aud = json.load(fh)

    falhas = 0
    chave = lambda r: (r["unidade"], r["submecanismo"], r["padrao"])
    tab = {chave(r): {m: _num(r[m]) for m in MEDIDAS} for r in P}
    med = {chave(r): {m: r[m] for m in MEDIDAS} for r in aud["padroes"]}

    print("== padrão por padrão (tabela · auditoria) ==")
    for k in sorted(set(tab) | set(med)):
        rotulo = f"{k[0]} · {k[1]} · {k[2]}"
        if k not in tab or k not in med:
            falhas += 1
            print(f"  DIVERGE  {rotulo}: só na {'auditoria' if k not in tab else 'tabela'}")
            continue
        dif = [f"{m} {tab[k][m]} × {med[k][m]}" for m in MEDIDAS if tab[k][m] != med[k][m]]
        falhas += bool(dif)
        print(f"  {'DIVERGE' if dif else 'OK     '}  {rotulo}" + (f": {'; '.join(dif)}" if dif else
                                                                  f" ({tab[k]['erros']} erros)"))

    print("== totais ==")
    balde_tab = dict(sorted(Counter(r["unidade"] for r in C).items()))
    for nome, x, y in [("erros do resíduo", len(C), aud["populacao"]), ("por balde", balde_tab, aud["por_balde"]),
                       ("padrões", len(P), len(aud["padroes"])),
                       ("padrões que passam", sum(_num(r["passa_na_recorrencia"]) for r in P), aud["padroes_que_passam"])]:
        ok = x == y
        falhas += not ok
        print(f"  {'OK     ' if ok else 'DIVERGE'}  {nome}: {x} · {y}")

    print("== conferências internas ==")
    soma = sum(int(r["erros"]) for r in P)
    balde_pad = {}
    for r in P:
        balde_pad[r["unidade"]] = balde_pad.get(r["unidade"], 0) + int(r["erros"])
    for nome, ok in [(f"soma dos padrões ({soma}) = linhas do casos.csv ({len(C)})", soma == len(C)),
                     ("erros por balde: padrões = casos", dict(sorted(balde_pad.items())) == balde_tab),
                     ("todo caso tem padrão", all(r["padrao"] for r in C))]:
        falhas += not ok
        print(f"  {'OK   ' if ok else 'FALHA'}  {nome}")

    print(f"\n{'0 divergências: verificado' if not falhas else f'{falhas} divergência(s) ou falha(s): pare e registre'}")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
