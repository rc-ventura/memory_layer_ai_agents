"""Teste com resposta conhecida: a base 1 pela query v1 (porta_query_v1) × o pipeline clássico da base 1.

Roda aqui, onde está o trace da base 1. Imprime só contagens e nomes de unidade/motivo — nenhum texto de caso.
Pergunta: o que o modo observado (mineracao_observada) faz com erros cuja resposta já sabemos?
  1. a extração reproduz a população (ActionSteps, erros estruturados)?
  2. cada erro cai na mesma unidade, fica pendente (e por quê) ou muda de unidade?
  3. a triagem (candidata / não) muda?

Uso, da raiz: uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/comparar_base1.py [--nulo-sql]
"""
import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import tempfile

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
ANALYSIS = PIPELINE.parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(ANALYSIS))
import matplotlib
matplotlib.use("Agg")
import base_pipeline as bp3
import mineracao_observada as mo
from leitor_trace import ler_trace
from validacao.porta_query_v1 import porta_v1

BASE1 = ANALYSIS / "2026-09-trace-law-flow" / "pipeline" / "base_pipeline.py"


def base1():
    spec = spec_from_file_location("base1_classico", BASE1)
    m = module_from_spec(spec)
    sys.path.insert(0, str(BASE1.parent))
    spec.loader.exec_module(m)
    return m


def comparar(nulo_exclui=False):
    b1 = base1()
    raw = ler_trace(b1.TRACE)
    v1, mapa, cont = porta_v1(raw, nulo_exclui)
    B = b1.carregar_base()
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "base1_formato_v1.parquet"
        v1.to_parquet(path, index=False)
        A = mo.analisar(bp3.carregar_carga(path))
    out = {"extracao": cont, "classico": {"action_steps": len(B.steps), "erros_estruturados": len(B.E)}}

    # cada erro observado ← idx do clássico (exec, papel, idx)
    E = A.EU.drop(columns=["idx"]).merge(mapa.rename(columns={"cod_idef_exeo": "exec_id", "papel": "role"})
                   .astype({"exec_id": str, "step_pos": "int64"})[["exec_id", "role", "step_pos", "idx"]],
                   left_on=["exec_id", "role", "step_pos"], right_on=["exec_id", "role", "step_pos"], how="left")
    C = B.EU[["exec_id", "role", "idx", "unidade", "submecanismo"]].astype({"exec_id": str, "idx": "int64"})
    E["idx"] = E["idx"].astype("int64")
    J = E.merge(C, on=["exec_id", "role", "idx"], how="left", suffixes=("", "_classico"))
    out["juncao"] = {"erros_observados": len(E), "com_par_no_classico": int(J.unidade_classico.notna().sum())}

    obs = J.situacao_mecanismo.eq("observavel")
    J["resultado"] = "pendente"
    J.loc[obs & J.unidade.eq(J.unidade_classico), "resultado"] = "mesma unidade"
    J.loc[obs & J.unidade.ne(J.unidade_classico), "resultado"] = "unidade diferente"
    out["por_resultado"] = J.resultado.value_counts().to_dict()
    pend = J[J.resultado.eq("pendente")]
    out["pendentes_por_motivo_e_unidade_classica"] = (
        pend.groupby(["motivo_evidencia", "unidade_classico"]).size().rename("erros").reset_index()
        .sort_values("erros", ascending=False).to_dict("records"))
    dif = J[J.resultado.eq("unidade diferente")]
    out["unidades_diferentes"] = (dif.groupby(["unidade_classico", "unidade"]).size().rename("erros").reset_index()
                                  .to_dict("records"))

    # triagem: clássico (sem silenciosas, como o modo observado) × observado
    T1 = b1.triagem(B.EU).set_index("unidade")
    T3 = A.tabelas["triagem_visivel_observada"].set_index("unidade")
    linhas = []
    for u in sorted(set(T1.index) | set(T3.index)):
        linhas.append({"unidade": u,
                       "classico_decisao": T1["decisão"].get(u), "classico_erros": int(T1["erros"].get(u, 0)) if "erros" in T1 else None,
                       "observado_decisao": T3["decisao"].get(u), "observado_erros": int(T3["erros_observaveis"].get(u, 0))})
    out["triagem"] = linhas
    return out, J


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--nulo-sql", action="store_true", help="filtro de tamanho com NULL excluindo, como no SQL")
    args = p.parse_args(argv)
    out, _ = comparar(args.nulo_sql)
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
