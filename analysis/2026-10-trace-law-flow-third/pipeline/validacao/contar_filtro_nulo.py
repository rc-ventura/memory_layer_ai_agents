"""Contagens para checar se o filtro de tamanho da query v1 cortou execuções sem resposta/estado final.

No SQL, `length(txt_vrvl_locl) + length(txt_rspa_fina) + length(txt_etap_memo) < 30000000` é NULL quando um dos
três textos é NULL, e a linha sai da base. Se nenhuma execução da base 3 tem has_persisted_response = 0 (ou
has_final_locals = 0), é sinal de que as sem resposta/estado foram cortadas. Na base 1, vazio=NULL deixaria 100/1000.

Imprime só contagens — nada de identificador ou texto. Uso, de qualquer pasta:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_filtro_nulo.py [--fonte <parquet>]
"""
import argparse
from pathlib import Path
import sys

import pyarrow.parquet as pq

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
import base_pipeline as bp


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fonte", type=Path, default=Path(bp.TRACE))
    args = p.parse_args(argv)
    cols = ["cod_idef_exeo", "cod_idef_aget", "has_persisted_response", "has_final_locals"]
    df = pq.read_table(args.fonte, columns=cols).to_pandas()
    e = df.drop_duplicates(["cod_idef_exeo", "cod_idef_aget"])
    print("linhas:", len(df), "| execucoes (exec+agente):", len(e))
    for c in ["has_persisted_response", "has_final_locals"]:
        print(c, "por execucao:", {str(k): int(v) for k, v in e[c].value_counts(dropna=False).items()})
    ambos = int(((e.has_persisted_response == 0) & (e.has_final_locals == 0)).sum())
    print("execucoes com os dois = 0:", ambos)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
