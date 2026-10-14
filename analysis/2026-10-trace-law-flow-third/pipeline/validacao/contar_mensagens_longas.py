"""Por que as mensagens que a v1 cortava foram quase todas para o retorno-string e nenhuma para o retorno-dict (roadmap b3 #34).

Na v2 (sem corte), as mensagens com mais de 20.000 caracteres são exatamente as que a v1 cortava. Cada uma passa pela regra
real (`classify` e `submecanismo` do `base_pipeline`) e é comparada com as mensagens curtas. A regra do retorno-dict casa
`KeyError: <número>` no FIM da mensagem; a do retorno-string, `string indices must be integers` em qualquer posição.
O que o smolagents escreve é `Could not index <valor> with '<chave>': <Tipo>: <texto>`: o valor entra por inteiro, então a
mensagem é longa quando o valor indexado é longo. Aqui se vê como o valor começa (`{`, `[` ou texto) e COMO a mensagem
termina — só categorias e contagens, nenhum texto de caso. Resultado de 14/10 (roadmap #34, fechado): 848 das 854 longas
com "Could not index" começam com `{`, e 849 terminam no erro de string — JSON chegando como texto, não dict. Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_mensagens_longas.py [--fonte <v2.parquet>]
"""
import argparse
from pathlib import Path
import re
import sys

import pandas as pd
import pyarrow.parquet as pq

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
import base_pipeline as bp

CORTE_V1 = 20_000
FIM = [  # (rótulo, regex no fim da mensagem) — a primeira que casa
    # Python 3.11+: "string indices must be integers, not 'str'" — o sufixo entra no fim
    ("string indices must be integers", re.compile(r"string indices must be integers(, not '\w+')?\s*$")),
    ("KeyError: <número>", re.compile(r"KeyError: \d+\s*$")),
    ("KeyError: '<campo>'", re.compile(r"KeyError: '[^']*'\s*$")),
    ("list indices must be integers", re.compile(r"list indices must be integers[^\n]*$")),
    ("unhashable type: 'slice'", re.compile(r"unhashable type: 'slice'\s*$")),
]
_VALOR = re.compile(r"Could not index (.)", re.S)


def fim(m):
    for rotulo, rx in FIM:
        if rx.search(m):
            return rotulo
    return "outro fim"


def valor(m):
    v = _VALOR.search(m)
    if not v:
        return "sem 'Could not index'"
    # O smolagents imprime str(valor): um dict e um JSON em texto começam os dois com "{". Quem decide se era string é o
    # erro do Python ("string indices must be integers" só sai de str), não o primeiro caractere.
    return {"{": "começa com { (dict ou JSON em texto)", "[": "começa com [ (lista ou JSON em texto)"}.get(
        v.group(1), "texto (outro)")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fonte", type=Path, default=Path(bp.TRACE))
    args = p.parse_args(argv)
    df = pq.read_table(args.fonte, columns=["structured_error", "error_message", "papel"]).to_pandas()
    df = df[pd.to_numeric(df.structured_error).eq(1)].copy()
    df["m"] = df.error_message.fillna("")
    df["comprimento"] = df.m.str.len()
    df["longa"] = df.comprimento > CORTE_V1
    print(f"erros estruturados: {len(df)} | mensagens longas (> {CORTE_V1}): {int(df.longa.sum())} | "
          f"exatamente {CORTE_V1}: {int((df.comprimento == CORTE_V1).sum())}")
    q = df.loc[df.longa, "comprimento"].quantile([.5, .9, .99]).astype(int).to_dict()
    print("comprimento das longas — mediana/p90/p99/máx:", q[.5], q[.9], q[.99], int(df.comprimento.max()))
    df["assinatura"] = df.m.map(lambda m: bp.classify(m)[1])
    df["mecanismo"] = df.m.map(bp.submecanismo)   # argumentos padrão: exato para "Could not index", ver o docstring
    for nome, sub in (("LONGAS", df[df.longa]), ("CURTAS", df[~df.longa])):
        print(f"\n== {nome}: {len(sub)}")
        print("assinatura:", sub.assinatura.value_counts().head(8).to_dict())
        print("mecanismo (regra real):", sub.mecanismo.value_counts().head(10).to_dict())
        ci = sub[sub.m.str.contains("Could not index", regex=False)].copy()
        print(f"-- 'Could not index': {len(ci)}")
        if len(ci):
            ci["valor"] = ci.m.map(valor)
            ci["fim"] = ci.m.map(fim)
            print(pd.crosstab(ci.valor, ci.fim).to_string())
            print("mecanismo × fim:\n" + pd.crosstab(ci.mecanismo, ci.fim).to_string())
            print("papéis (5 com mais):", ci.papel.value_counts().head(5).to_dict())
        # a regra do dict falha quando o fim não é "KeyError: <número>" mesmo havendo o texto antes?
        ancora = sub.m.str.contains(r"KeyError: \d+", regex=True) & ~sub.m.str.contains(r"KeyError: \d+\s*$", regex=True)
        print("tem 'KeyError: <número>' mas NÃO no fim (regra do dict não casa):", int(ancora.sum()))
        print("tem 'string indices must be integers' E 'KeyError' juntos:",
              int((sub.m.str.contains("string indices must be integers") & sub.m.str.contains("KeyError")).sum()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
