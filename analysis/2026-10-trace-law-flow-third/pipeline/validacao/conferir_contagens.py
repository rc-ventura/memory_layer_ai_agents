"""Junção da v2 (erros) com as contagens (pedido A), e da v2 com a v1 se for passada (roadmap b3 #26).

Contagens: chave (execução, agente, papel) única? Toda chave da v2 existe lá, com o mesmo número de erros e de
suspeitas? Os tokens dos passos com erro cabem nos tokens do papel? E a taxa por mês, que o pedido A destrava.
v1 × v2: mesmas linhas (execução, agente, papel, step_pos) e mesmo error_type? A mensagem da v1 é o começo da da v2?

Imprime só contagens e rótulos de categoria (mês, status) — nada de identificador ou texto. Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/conferir_contagens.py \\
        --v2 <base_erros_minerados_full_v2.parquet> --contagens <base_contagens.parquet> [--v1 <parquet da v1>]
"""
import argparse
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

CHAVE = ["cod_idef_exeo", "cod_idef_aget", "papel"]
LINHA = CHAVE + ["step_pos"]


def _contagens(v2, cont):
    print(f"contagens: {len(cont)} linhas | chaves duplicadas: {int(cont.duplicated(CHAVE).sum())} | "
          f"linhas com qtd nula: {int(cont.qtd_actionsteps.isna().sum())} | com 0 ActionSteps: "
          f"{int((cont.qtd_actionsteps == 0).sum())}")
    print("status_memoria:", cont.status_memoria.value_counts(dropna=False).to_dict())
    for nome, df in (("v2", v2), ("contagens", cont)):
        ag = df.groupby("cod_idef_exeo").cod_idef_aget.nunique()
        print(f"{nome}: execuções com mais de um agente: {int((ag > 1).sum())} de {len(ag)}")
    g = v2.groupby(CHAVE).agg(erros=("structured_error", "sum"), suspeitas=("observation_suspect", "sum"),
                              tokens_erro=("total_tokens", "sum")).reset_index()
    j = g.merge(cont, on=CHAVE, how="left", indicator=True)
    sem_par = int((j._merge == "left_only").sum())
    com = j[j._merge == "both"]
    print(f"chaves da v2: {len(g)} | sem par nas contagens: {sem_par} | erros diferentes: "
          f"{int((com.erros != com.qtd_erros_estruturados).sum())} | suspeitas diferentes: "
          f"{int((com.suspeitas != com.qtd_suspeitas_observadas).sum())} | tokens dos erros > tokens do papel: "
          f"{int((com.tokens_erro > com.tokens_total).sum())}")
    erro = v2[v2.structured_error == 1]
    print(f"global: {int(cont.qtd_erros_estruturados.sum())} erros em {int(cont.qtd_actionsteps.sum())} ActionSteps "
          f"({cont.qtd_erros_estruturados.sum() / cont.qtd_actionsteps.sum():.2%}) | tokens dos erros estruturados "
          f"{int(erro.total_tokens.sum())} de {int(cont.tokens_total.sum())} ({erro.total_tokens.sum() / cont.tokens_total.sum():.2%})")
    print(f"tokens por ActionStep: todos {cont.tokens_total.sum() / cont.qtd_actionsteps.sum():.0f} | com erro "
          f"estruturado {erro.total_tokens.mean():.0f} | saída/total: todos "
          f"{cont.tokens_saida.sum() / cont.tokens_total.sum():.2%}, com erro {erro.output_tokens.sum() / erro.total_tokens.sum():.2%}")
    m = cont.groupby("mes_execucao").agg(linhas=("papel", "size"), actionsteps=("qtd_actionsteps", "sum"),
                                         erros=("qtd_erros_estruturados", "sum"), tokens=("tokens_total", "sum"))
    m["execucoes"] = cont.drop_duplicates(["cod_idef_exeo", "cod_idef_aget"]).groupby("mes_execucao").size()
    m["erro_por_actionstep"] = (m.erros / m.actionsteps).round(4)
    m["actionsteps_por_execucao"] = (m.actionsteps / m.execucoes).round(2)
    print("por mês:\n" + m.astype({"actionsteps": int, "erros": int, "tokens": int}).to_string())


def _v1_v2(v1, v2):
    a = v1.set_index(LINHA)
    b = v2.set_index(LINHA)
    print(f"v1 × v2: linhas {len(v1)} × {len(v2)} | chaves duplicadas v1 {int(a.index.duplicated().sum())}, "
          f"v2 {int(b.index.duplicated().sum())} | só na v1: {len(a.index.difference(b.index))} | só na v2: "
          f"{len(b.index.difference(a.index))}")
    c = a.join(b[["error_type", "error_message", "total_tokens"]], how="inner", rsuffix="_v2")
    print(f"error_type diferente: {int((c.error_type.fillna('') != c.error_type_v2.fillna('')).sum())} | "
          f"total_tokens diferente: {int((c.total_tokens != c.total_tokens_v2).sum())}")
    m1, m2 = c.error_message.fillna(""), c.error_message_v2.fillna("")
    prefixo = pd.Series([y.startswith(x) for x, y in zip(m1, m2)], index=c.index)
    cortadas = m1.str.len() == 20_000
    print(f"mensagem da v1 é o começo da da v2: {int(prefixo.sum())} de {len(c)} | v1 no corte de 20.000: "
          f"{int(cortadas.sum())}, das quais mais longas na v2: {int((cortadas & (m2.str.len() > 20_000)).sum())}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--v2", type=Path, required=True)
    p.add_argument("--contagens", type=Path, required=True)
    p.add_argument("--v1", type=Path)
    args = p.parse_args(argv)
    cols = LINHA + ["structured_error", "observation_suspect", "total_tokens", "output_tokens"]
    v2 = pq.read_table(args.v2, columns=cols + ["error_type", "error_message"]).to_pandas()
    _contagens(v2, pq.read_table(args.contagens).to_pandas())
    if args.v1:
        v1 = pq.read_table(args.v1, columns=LINHA + ["error_type", "error_message", "total_tokens"]).to_pandas()
        _v1_v2(v1, v2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
