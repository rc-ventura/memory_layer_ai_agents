"""Schema e agregados de um parquet novo, sem dado de linha (roadmap b3 #26).

Para os dois parquets que chegaram em 14/10 (denominadores e query v2): quais colunas, de que tipo, quantas
linhas, e por coluna só agregados — nulos, mínimo, máximo e soma nas numéricas; nulos, maior comprimento e quantos
atingem esse maior comprimento nas de texto (é o que mostra o novo corte da mensagem e se ele ainda trunca).
Nunca imprime valor de célula, identificador ou texto: só nomes de colunas e contagens, que podem sair da máquina 2.

Uso, de qualquer pasta, um arquivo por vez:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/inspecionar_parquet.py <parquet>
"""
import argparse
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

CHAVE = ["cod_idef_exeo", "cod_idef_aget"]
CORTES_CONHECIDOS = (20_000,)   # o corte da mensagem na v1 (limitação 1)


def _agregar_texto(pf, col):
    nulos = total = maior = no_maior = 0
    nos_cortes = {c: 0 for c in CORTES_CONHECIDOS}
    for lote in pf.iter_batches(columns=[col], batch_size=5_000):
        arr = lote.column(0)
        if not (pa.types.is_string(arr.type) or pa.types.is_large_string(arr.type)):
            arr = arr.cast(pa.large_string())
        total += len(arr)
        nulos += arr.null_count
        comp = pc.utf8_length(arr)
        m = pc.max(comp).as_py()
        if m is None:
            continue
        if m > maior:
            maior, no_maior = m, 0
        if m == maior:
            no_maior += pc.sum(pc.equal(comp, maior).cast(pa.int64())).as_py() or 0
        for c in CORTES_CONHECIDOS:
            nos_cortes[c] += pc.sum(pc.equal(comp, c).cast(pa.int64())).as_py() or 0
    return (f"texto | nulos {nulos} | maior comprimento {maior} (em {no_maior} linhas) | "
            + " | ".join(f"== {c}: {n}" for c, n in nos_cortes.items()))


def _agregar_numerica(pf, col):
    nulos = soma = 0
    mini = maxi = None
    for lote in pf.iter_batches(columns=[col], batch_size=50_000):
        arr = lote.column(0)
        nulos += arr.null_count
        if arr.null_count == len(arr):
            continue
        lo, hi, s = pc.min(arr).as_py(), pc.max(arr).as_py(), pc.sum(arr).as_py()
        mini = lo if mini is None else min(mini, lo)
        maxi = hi if maxi is None else max(maxi, hi)
        soma += s
    return f"numerica | nulos {nulos} | min {mini} | max {maxi} | soma {soma}"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("parquet", type=Path)
    args = p.parse_args(argv)
    pf = pq.ParquetFile(args.parquet)
    schema = pf.schema_arrow
    print(f"arquivo: {args.parquet.name} | linhas: {pf.metadata.num_rows} | colunas: {len(schema)} "
          f"| grupos de linhas: {pf.metadata.num_row_groups}")
    for campo in schema:
        t = campo.type
        if pa.types.is_string(t) or pa.types.is_large_string(t):
            resumo = _agregar_texto(pf, campo.name)
        elif pa.types.is_integer(t) or pa.types.is_floating(t) or pa.types.is_boolean(t) or pa.types.is_decimal(t):
            resumo = _agregar_numerica(pf, campo.name) if not pa.types.is_boolean(t) else "booleana"
        elif pa.types.is_timestamp(t) or pa.types.is_date(t):
            resumo = "data/hora"
        else:
            resumo = "aninhada ou outro tipo"
        print(f"  {campo.name} [{t}] -> {resumo}")
    if all(c in schema.names for c in CHAVE):
        df = pq.read_table(args.parquet, columns=CHAVE).to_pandas()
        print(f"execucoes distintas: {df.cod_idef_exeo.nunique()} | exec+agente distintos: "
              f"{len(df.drop_duplicates(CHAVE))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
