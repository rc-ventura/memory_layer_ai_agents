"""Dos erros de nome não definido pendentes por "predecessor não identificado", quantos são o primeiro passo?

A regra marca como `predecessor_nao_identificado_sql` dois casos diferentes, que o leitor do parquet já separa na
coluna `presenca` do vizinho n-1:
  - `nao_identificado_por_sql`: nenhuma coluna prev_* preenchida → não há ActionStep anterior no papel (primeiro passo);
  - `numero_ausente_com_campos`: prev_step_number vazio, mas outras prev_* preenchidas → o anterior existe, sem número.
Este script conta os dois casos (e, no segundo, se o anterior teve erro estruturado). Decide se o pedido à query
precisa trazer a posição do passo no papel. Não muda regra nem grava nada em resultados.

Na base 1 (parquet simulado pela porta da query) o primeiro caso foi exatamente o primeiro ActionStep: 50 de 50, e
nenhum erro que não é o primeiro caiu nele. Na base 3 a proporção entre os dois casos não foi medida: é o que este
script mede.

Imprime só contagens, nomes de papel e meses — nenhum identificador de execução nem texto de caso. Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_predecessor_pendentes.py [--fonte <parquet>]
"""
import argparse
from pathlib import Path
import sys

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE.parents[1]))
import base_pipeline as bp
from episodios_trace import contexto_local

MOTIVO = "predecessor_nao_identificado_sql"


def contar(carga):
    A = bp.analisar_mecanismos_observaveis(carga)
    EU = A.EU
    out = {"erros_estruturados": len(EU),
           "pendencias_por_motivo": EU.loc[EU.situacao_mecanismo.eq("pendente"), "motivo_evidencia"].value_counts().to_dict()}
    P = EU[EU.motivo_evidencia.eq(MOTIVO)].copy()
    out["pendentes_deste_motivo"] = len(P)
    if P.empty:
        return out, P
    ctx = contexto_local(carga)
    P["presenca_n_menos_1"] = [ctx[(ref, -1)]["presenca"] for ref in P.step_ref]
    P["anterior_com_erro"] = [pd.notna(ctx[(ref, -1)].get("err_type")) for ref in P.step_ref]
    P["step_do_erro"] = P.step_ref.map(carga.steps.set_index("step_ref")["step"])
    P["step_pos_do_erro"] = P.step_ref.map(carga.steps.set_index("step_ref")["step_pos"])
    P["primeiro_pelo_numero"] = P.step_do_erro.eq(1) & P.step_pos_do_erro.le(3)
    out["por_presenca"] = P.presenca_n_menos_1.value_counts().to_dict()
    com_campos = P[P.presenca_n_menos_1.eq("numero_ausente_com_campos")]
    out["numero_ausente_com_campos__anterior_teve_erro"] = com_campos.anterior_com_erro.value_counts().to_dict()
    sem = P[P.presenca_n_menos_1.eq("nao_identificado_por_sql")]
    out["nao_identificado__e_o_primeiro_pelo_numero(step=1 e step_pos<=3)"] = sem.primeiro_pelo_numero.value_counts().to_dict()
    out["nao_identificado__step_nulo"] = int(sem.step_do_erro.isna().sum())
    out["nao_identificado__step_pos_mais_frequentes"] = sem.step_pos_do_erro.value_counts().head(6).to_dict()
    return out, P


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fonte", type=Path, default=Path(bp.TRACE))
    args = p.parse_args(argv)
    out, P = contar(bp.carregar_carga(args.fonte))
    for k, v in out.items():
        print(f"{k}: {v}")
    if not P.empty:
        print("\npor papel (os 8 maiores) × situação do anterior:")
        print(P.groupby(["role", "presenca_n_menos_1"]).size().rename("erros").reset_index()
              .sort_values("erros", ascending=False).head(8).to_string(index=False))
        if "mes" in P:
            print("\npor mês × situação do anterior:")
            print(P.groupby(["mes", "presenca_n_menos_1"]).size().rename("erros").reset_index().to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
