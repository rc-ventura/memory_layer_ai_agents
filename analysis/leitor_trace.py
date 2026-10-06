"""Leitor único do trace cru — CSV (puro, .xz, .gz) ou um único arquivo parquet (plano-atual §4.10).

Fica fora do `base_pipeline.py` de propósito: os `audit_recompute*` não podem importar o pipeline (a lógica deles é
independente), mas abrir o arquivo não é lógica auditada — os dois lados leem por aqui. Não sabe nada da esteira
jurídica nem da taxonomia: só entrega texto.

O contrato é o que o código já espera do CSV, nos dois formatos:

    ler_trace(caminho, colunas=None)     -> DataFrame igual a pd.read_csv(caminho, dtype=str): texto em tudo,
                                            nulo = NaN (o pipeline, o drill_down.py, o checklist.py)
    linhas_do_trace(caminho, colunas=None) -> um dict por linha igual ao csv.DictReader: texto em tudo, nulo = ""
                                            (os audit_recompute*), em lotes — não carrega o arquivo inteiro
    abrir_trace(caminho)                 -> o mesmo, com `.fieldnames` e `with`, no lugar do csv.DictReader

No parquet, a normalização é explícita, coluna a coluna:
  - texto fica texto; número e booleano viram o texto do valor (`1`, não `1.0`);
  - data e hora viram `AAAA-MM-DD HH:MM:SS[.ffffff]` (zeros finais da fração cortados, como no CSV da base 1); com
    fuso, a hora local do fuso da coluna, sem o sufixo — o checklist mostra o fuso;
  - coluna aninhada (struct/list/map) vira JSON com `json.dumps` — nunca `str()`, que daria a representação do
    Python e faria o `json.loads` do pipeline pular a execução em silêncio;
  - texto vazio no nível da coluna vira nulo, como o `pd.read_csv` faz (vazio dentro do JSON não é tocado).
O que a normalização fez fica em `df.attrs["formato"]` — o `checklist.py` imprime.
"""

import csv, datetime, decimal, gzip, json, lzma, os, sys

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

LOTE = 10_000   # linhas por lote no parquet (iter_batches) — limita a memória na escala de ~1M


def formato_do_trace(caminho):
    """'parquet', 'xz', 'gz' ou 'csv' — pelo conteúdo (bytes mágicos), não pela extensão."""
    if os.path.isdir(caminho):
        raise ValueError(f"{caminho} é uma pasta; o leitor espera um único arquivo (parquet ou CSV)")
    with open(caminho, "rb") as fh:
        cab = fh.read(6)
    if cab.startswith(b"PAR1"): return "parquet"
    if cab.startswith(b"\xfd7zXZ"): return "xz"
    if cab.startswith(b"\x1f\x8b"): return "gz"
    return "csv"


def trace_da_linha_de_comando(padrao):
    """`--trace <arquivo>` na linha de comando, ou o padrão do script (convenção do audit_recompute9)."""
    if "--trace" in sys.argv[1:-1]:
        return sys.argv[sys.argv.index("--trace") + 1]
    return padrao


# ---------------------------------------------------------------- normalização do parquet

def _json_padrao(v):
    if isinstance(v, (datetime.datetime, datetime.date, datetime.time)):
        return v.isoformat(sep=" ") if isinstance(v, datetime.datetime) else v.isoformat()
    if isinstance(v, decimal.Decimal): return str(v)
    if isinstance(v, (bytes, bytearray)): return v.decode("utf-8")
    raise TypeError(f"valor aninhado sem forma JSON: {type(v).__name__}")


def _mapas_como_dict(v, tipo):
    """`as_py()` devolve map como lista de pares; em JSON ele é objeto."""
    import pyarrow as pa
    if v is None: return None
    if pa.types.is_map(tipo):
        return {k: _mapas_como_dict(x, tipo.item_type) for k, x in v}
    if pa.types.is_struct(tipo):
        return {f.name: _mapas_como_dict(v.get(f.name), f.type) for f in tipo}
    if pa.types.is_list(tipo) or pa.types.is_large_list(tipo) or pa.types.is_fixed_size_list(tipo):
        return [_mapas_como_dict(x, tipo.value_type) for x in v]
    return v


def _aninhado(tipo):
    import pyarrow as pa
    return pa.types.is_nested(tipo)


def _como_texto(col):
    """Uma coluna arrow (Array ou ChunkedArray) -> coluna de texto arrow, conforme o contrato do módulo."""
    import pyarrow as pa, pyarrow.compute as pc
    tipo = col.type
    if pa.types.is_dictionary(tipo):
        col, tipo = pc.cast(col, tipo.value_type), tipo.value_type
    if pa.types.is_null(tipo):
        return pa.nulls(len(col), pa.large_string())
    if pa.types.is_string(tipo) or pa.types.is_large_string(tipo):
        return col
    if pa.types.is_string_view(tipo) or pa.types.is_binary(tipo) or pa.types.is_large_binary(tipo) \
            or pa.types.is_binary_view(tipo):
        return pc.cast(col, pa.large_string())          # binário que não é UTF-8 falha aqui, alto — não em silêncio
    if pa.types.is_timestamp(tipo):
        txt = pc.strftime(col, format="%Y-%m-%d %H:%M:%S")   # %S já traz a fração na unidade da coluna
        return pc.replace_substring_regex(txt, pattern=r"(\.\d*?[1-9])0+$|\.0+$", replacement=r"\1")
    if pa.types.is_date(tipo):
        return pc.strftime(col, format="%Y-%m-%d")
    if _aninhado(tipo):
        return pa.array([None if v is None else json.dumps(_mapas_como_dict(v, tipo), default=_json_padrao)
                         for v in col.to_pylist()], pa.large_string())
    return pc.cast(col, pa.large_string())             # inteiro, real, booleano, decimal, hora


def _normalizar(tabela, relatorio=None):
    """Tabela/RecordBatch arrow -> {coluna: texto arrow}, com vazio -> nulo; acumula o relatório se pedido."""
    import pyarrow.compute as pc
    cols = {}
    for nome, col in zip(tabela.schema.names, tabela.columns):
        txt = _como_texto(col)
        vazio = pc.equal(txt, "")
        n_vazios = pc.sum(vazio).as_py() or 0
        if n_vazios:
            txt = pc.if_else(vazio, None, txt)
        cols[nome] = txt
        if relatorio is not None:
            tipo = col.type
            r = relatorio.setdefault(nome, {"tipo": str(tipo), "aninhada": _aninhado(tipo),
                                            "nulos": 0, "vazios_para_nulo": 0})
            r["nulos"] += col.null_count
            r["vazios_para_nulo"] += n_vazios
    return cols


# ---------------------------------------------------------------- leitura

def ler_trace(caminho, colunas=None):
    """DataFrame com o contrato de `pd.read_csv(caminho, dtype=str)`, de CSV ou parquet. `colunas` lê só essas."""
    import pandas as pd
    fmt = formato_do_trace(caminho)
    if fmt != "parquet":
        df = pd.read_csv(caminho, dtype=str, usecols=colunas,
                         compression={"xz": "xz", "gz": "gzip", "csv": None}[fmt])
        df.attrs["formato"] = {"formato": fmt}
        return df
    import pyarrow.parquet as pq
    arq = pq.ParquetFile(caminho)
    ordem = [c for c in arq.schema_arrow.names if colunas is None or c in colunas]
    faltam = [c for c in (colunas or []) if c not in ordem]
    if faltam:
        raise ValueError(f"colunas ausentes no parquet: {faltam}")
    relatorio = {}
    partes = [_normalizar(lote, relatorio) for lote in arq.iter_batches(batch_size=LOTE, columns=ordem)]
    df = pd.DataFrame({c: pd.Series([v for p in partes for v in p[c].to_pylist()], dtype=str) for c in ordem}) \
        if partes else pd.DataFrame({c: pd.Series([], dtype=str) for c in ordem})
    df.attrs["formato"] = {"formato": "parquet", "linhas": arq.metadata.num_rows,
                           "grupos_de_linhas": arq.metadata.num_row_groups, "colunas": relatorio}
    return df


def _abrir_csv(caminho, fmt):
    if fmt == "xz": return lzma.open(caminho, "rt", encoding="utf-8", newline="")
    if fmt == "gz": return gzip.open(caminho, "rt", encoding="utf-8", newline="")
    return open(caminho, "r", encoding="utf-8", newline="")


def linhas_do_trace(caminho, colunas=None):
    """Um dict por linha, com o contrato do `csv.DictReader` (texto; nulo = ""), de CSV ou parquet, em lotes."""
    fmt = formato_do_trace(caminho)
    if fmt != "parquet":
        with _abrir_csv(caminho, fmt) as fh:
            for r in csv.DictReader(fh):
                yield r if colunas is None else {c: r[c] for c in colunas}
        return
    import pyarrow.parquet as pq
    arq = pq.ParquetFile(caminho)
    for lote in arq.iter_batches(batch_size=LOTE, columns=colunas):
        cols = {c: t.to_pylist() for c, t in _normalizar(lote).items()}
        nomes = list(cols)
        for i in range(lote.num_rows):
            yield {c: ("" if cols[c][i] is None else cols[c][i]) for c in nomes}


def colunas_do_trace(caminho):
    """Os nomes das colunas, na ordem do arquivo, sem ler os dados."""
    fmt = formato_do_trace(caminho)
    if fmt == "parquet":
        import pyarrow.parquet as pq
        return list(pq.ParquetFile(caminho).schema_arrow.names)
    with _abrir_csv(caminho, fmt) as fh:
        return next(csv.reader(fh))


class abrir_trace:
    """Troca direta do `with lzma.open(...) as f: rdr = csv.DictReader(f)` dos audit_recompute*: `.fieldnames`,
    iterável, usável com `with` — só a abertura do arquivo muda, a lógica de quem lê não."""

    def __init__(self, caminho, colunas=None):
        self.fieldnames = list(colunas) if colunas else colunas_do_trace(caminho)
        self._linhas = linhas_do_trace(caminho, colunas)

    def __iter__(self):
        return self._linhas

    def __next__(self):
        return next(self._linhas)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._linhas.close()
