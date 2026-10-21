"""Bases 1 e 2 (trace completo, com prompt): quando o prompt NÃO lista um módulo, o interpretador barra o import dele?

Pergunta (dossiê do sandbox na base 3, `propostas/U_sandbox/dossie_base3.md`, §2h, 16–17): no smolagents, a lista de
imports autorizados do prompt e a do interpretador saem da mesma configuração (`authorized_imports`). Na base 3, o
interpretador do RoteadorCivel deixa importar `json`, e o prompt do mesmo papel e período (bases 1 e 2) não o lista. Se,
na MESMA execução, o prompt não lista o módulo e o import dele roda, a plataforma monta o prompt e o interpretador por
caminhos diferentes; se o import é barrado ("Import of <módulo> is not allowed"), os dois acompanham, e a diferença da
base 3 é de configuração.

Por papel e por "o módulo está na lista do prompt da execução" (sim / não): execuções, passos com `import <módulo>`, os
que rodaram e os barrados. Não grava nada. Só contagens e nomes de papel. Uso, da raiz:
    uv run python analysis/2026-09-trace-law-flow-second/scripts/contar_import_vs_lista_base2.py --trace <trace> [--modulo json]
Com `--listar <papel>`: os exec_id, mês e idx dos passos com `import <módulo>` em execuções cujo prompt NÃO lista o
módulo — para abrir o caso inteiro com `drill_down.py caso <exec_id> <papel>` (na pasta pipeline/ da base; o caso tem
texto cru: fica na máquina da base).
"""
import argparse
from pathlib import Path
import re
import sys

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from contar_modulo_na_lista_base2 import modulos  # noqa: E402


def medir(S, modulo):
    """S: um ActionStep por linha (exec_id, agente, role, idx, sysprompt, code, err_msg). Uma linha por papel × lista."""
    m = re.escape(modulo)
    imp = re.compile(rf"(?m)^\s*(?:import\s+{m}\b|from\s+{m}(?:\.\w+)*\s+import\b)")
    barrado = re.compile(rf"Import (?:of|from) {m}\b[\w.]* is not allowed")
    chave = ["exec_id", "agente", "role"]
    prim = S[S.idx.eq(0)].drop_duplicates(chave)
    lista = {k: (None if ms is None else modulo in ms) for k, ms in
             zip(prim[chave].itertuples(index=False, name=None), map(modulos, prim.sysprompt.fillna("")))}
    S = S.assign(na_lista=[lista.get(k) for k in S[chave].itertuples(index=False, name=None)])
    saida = []
    for (papel, na), G in S[S.na_lista.notna()].groupby(["role", "na_lista"], sort=True):
        com = G[G.code.fillna("").str.contains(imp)]
        bar = int(com.err_msg.fillna("").str.contains(barrado).sum())
        saida.append({"papel": papel, "na_lista": bool(na), "execucoes": int(G[chave].drop_duplicates().shape[0]),
                      "passos_com_import": len(com), "rodou": len(com) - bar, "barrado": bar})
    return saida


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trace", required=True, type=Path, help="o arquivo do trace cru (CSV ou parquet)")
    p.add_argument("--modulo", default="json")
    p.add_argument("--listar", metavar="PAPEL", help="lista exec_id/mês/idx dos imports fora da lista nesse papel")
    a = p.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    from contar_primeiro_passo_nome_base2 import bp, explodir   # o leitor do trace (importa o pipeline da base 1)
    bp.TRACE = str(a.trace)
    S = explodir(bp.carregar_trace())
    T = medir(S, a.modulo)
    if a.listar:
        import re as _re
        m = _re.escape(a.modulo)
        imp = _re.compile(rf"(?m)^\s*(?:import\s+{m}\b|from\s+{m}(?:\.\w+)*\s+import\b)")
        chave = ["exec_id", "agente", "role"]
        prim = S[S.idx.eq(0)].drop_duplicates(chave)
        fora = {k for k, ms in zip(prim[chave].itertuples(index=False, name=None), map(modulos, prim.sysprompt.fillna("")))
                if ms is not None and a.modulo not in ms}
        L = S[S.role.eq(a.listar) & S.code.fillna("").str.contains(imp)]
        L = L[[k in fora for k in L[chave].itertuples(index=False, name=None)]]
        print(f"`import {a.modulo}` no {a.listar}, em execuções cujo prompt não lista `{a.modulo}`: {len(L)} passos")
        for r in L.sort_values(["mes", "exec_id", "idx"]).itertuples(index=False):
            print(f"  exec_id={r.exec_id}  mês={r.mes}  idx={r.idx}  erro={'sim' if str(r.err_msg or '') else 'não'}")
        print(f"\nPara ver o caso inteiro (na pasta pipeline/ da base): python drill_down.py caso <exec_id> {a.listar}")
        return 0
    print(f"`import {a.modulo}` × `{a.modulo}` na lista do prompt da execução (só os grupos com algum import)")
    print(f"{'papel':22} {'na lista':>8} {'execuções':>10} {'passos c/ import':>17} {'rodou':>6} {'barrado':>8}")
    for r in T:
        if r["passos_com_import"]:
            print(f"{r['papel']:22} {'sim' if r['na_lista'] else 'não':>8} {r['execucoes']:>10} {r['passos_com_import']:>17} "
                  f"{r['rodou']:>6} {r['barrado']:>8}")
    tot = lambda na, k: sum(r[k] for r in T if r["na_lista"] is na)
    print(f"{'(total) fora da lista':31} {tot(False, 'execucoes'):>10} {tot(False, 'passos_com_import'):>17} "
          f"{tot(False, 'rodou'):>6} {tot(False, 'barrado'):>8}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
