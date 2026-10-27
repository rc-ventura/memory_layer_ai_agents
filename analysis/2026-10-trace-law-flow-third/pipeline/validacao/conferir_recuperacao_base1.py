"""Teste com resposta conhecida da recuperação por trajetória (`execucao/recuperacao.py`), na base 1 (trace completo).

A verdade sai do trace inteiro: a posição de cada ActionStep no papel, com e sem erro, dá as sequências de erros e se o
último passo do papel errou. A reconstrução sai só do que a base 3 tem: as linhas com erro da porta da query v1 (as
mesmas colunas e vizinhos do Athena). Pergunta: as duas dão a mesma categoria em toda trajetória?

Também mede por que a numeração não serve de posição (`step_number` × posição do ActionStep no papel) e grava as
contagens da base 1 no formato do pedido A, para rodar `executar.py relatorio` na rodada de ensaio
(`validacao/rodada_base1.py`). Imprime só contagens.

Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/conferir_recuperacao_base1.py \\
        [--contagens-saida <parquet>]
"""
import argparse
from pathlib import Path
import sys

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
ANALYSIS = PIPELINE.parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(ANALYSIS))
from leitor_trace import ler_trace
from execucao.recuperacao import CHAVE, trajetorias
from validacao.comparar_base1 import base1
from validacao.porta_query_v1 import contexto, explodir_action_steps, selecionar_erros, selecionar_snapshots, tipar

SAIDA = PIPELINE / "resultados" / "ensaio_base1" / "contagens_base1.parquet"


def verdade(a):
    """A categoria de cada trajetória pelo trace completo (posição de todo ActionStep), sem os vizinhos da query."""
    a = a.sort_values(CHAVE + ["step_pos"]).copy()
    a["ordinal"] = a.groupby(CHAVE).cumcount() + 1
    n = a.groupby(CHAVE).size().rename("n")
    e = a[a.structured_error.eq(1)].join(n, on=CHAVE)
    linhas = []
    for k, g in e.groupby(CHAVE):
        pos = g.ordinal.tolist()
        seq = 1 + sum(1 for x, y in zip(pos, pos[1:]) if y != x + 1)
        limite = g.error_message.fillna("").str.contains("Reached max steps|AgentMaxStepsError").any()
        cat = ("limite_de_passos" if limite else "terminou_no_erro" if pos[-1] == g.n.iloc[0]
               else "um_erro" if len(pos) == 1 else "cascata" if seq == 1 else "recaida")
        linhas.append((*k, len(pos), seq, cat))
    return pd.DataFrame(linhas, columns=CHAVE + ["erros", "sequencias", "categoria"])


def numeracao(a):
    a = a.sort_values(CHAVE + ["step_pos"]).copy()
    a["ordinal"] = a.groupby(CHAVE).cumcount() + 1
    g = a.groupby(CHAVE)
    reinicia = g.step_number.diff().le(0)
    print(f"numeração: {len(a)} ActionSteps em {g.ngroups} papéis | step_number ≠ posição no papel: "
          f"{int(a.step_number.ne(a.ordinal).sum())} ({a.step_number.ne(a.ordinal).mean():.1%}) | papéis em que o "
          f"step_number recomeça (nova chamada): {int(reinicia.groupby([a[c] for c in CHAVE]).any().sum())} | "
          f"maior step_number = nº de ActionSteps do papel: {int(g.step_number.max().eq(g.size()).sum())} de {g.ngroups}")


def contagens(a, snap):
    """As contagens do pedido A para a base 1: uma linha por execução, agente e papel, com todos os ActionSteps."""
    mes = snap.set_index(["cod_idef_exeo", "cod_idef_aget"]).dat_hor_inio_exeo.astype(str).str[:7]
    c = a.groupby(CHAVE).agg(qtd_actionsteps=("step_pos", "size"), tokens_entrada=("input_tokens", "sum"),
                             tokens_saida=("output_tokens", "sum"), tokens_total=("total_tokens", "sum"),
                             qtd_erros_estruturados=("structured_error", "sum"),
                             qtd_suspeitas_observadas=("observation_suspect", "sum")).reset_index()
    c["mes_execucao"] = [mes.get((e, g)) for e, g in zip(c.cod_idef_exeo, c.cod_idef_aget)]
    c["status_memoria"] = "OK"
    for k in CHAVE:
        c[k] = c[k].astype(str)
    return c.astype({x: "float64" for x in ["qtd_actionsteps", "tokens_entrada", "tokens_saida", "tokens_total",
                                             "qtd_erros_estruturados", "qtd_suspeitas_observadas"]})


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--contagens-saida", type=Path, default=SAIDA)
    args = p.parse_args(argv)
    antes = set(sys.modules)
    trace = base1().TRACE
    pasta_b1 = str(Path(trace).resolve().parent.parent / "pipeline")   # como no rodada_base1: tira a pipeline da base 1
    sys.path[:] = [x for x in sys.path if Path(x).resolve() != Path(pasta_b1).resolve()]
    for nome in set(sys.modules) - antes:
        if (getattr(sys.modules[nome], "__file__", "") or "").startswith(pasta_b1):
            del sys.modules[nome]
    snap, _ = selecionar_snapshots(ler_trace(trace), False)   # o mesmo corte da rodada de ensaio (rodada_base1)
    a, _ = explodir_action_steps(snap)
    a = contexto(a)
    numeracao(a)
    v1, _ = selecionar_erros(a)
    v1 = tipar(v1)
    for k in CHAVE:
        v1[k] = v1[k].astype(str)
        a[k] = a[k].astype(str)
    certo = verdade(a)
    rec = trajetorias(v1)
    j = certo.merge(rec, on=CHAVE, how="outer", suffixes=("_verdade", "_base3"), indicator=True)
    print(f"trajetórias com erro: verdade {len(certo)} | reconstruídas {len(rec)} | só numa das duas: "
          f"{int(j._merge.ne('both').sum())}")
    both = j[j._merge.eq("both")]
    print("verdade × reconstrução (linhas = verdade):")
    print(pd.crosstab(both.categoria_verdade, both.categoria_base3).to_string())
    iguais = both.categoria_verdade.eq(both.categoria_base3)
    print(f"mesma categoria: {int(iguais.sum())} de {len(both)} | mesmo nº de erros: "
          f"{int(both.erros_verdade.eq(both.erros_base3).sum())} | mesmo nº de sequências: "
          f"{int(both.sequencias_verdade.eq(both.sequencias_base3).sum())}")
    print("indeterminadas por motivo:", rec.motivo_indeterminado.value_counts().to_dict())
    c = contagens(a, snap)
    args.contagens_saida.parent.mkdir(parents=True, exist_ok=True)
    c.to_parquet(args.contagens_saida, index=False)
    print(f"contagens da base 1: {len(c)} linhas em {args.contagens_saida.name}")
    return 0 if iguais.all() and j._merge.eq("both").all() else 1


if __name__ == "__main__":
    raise SystemExit(main())
