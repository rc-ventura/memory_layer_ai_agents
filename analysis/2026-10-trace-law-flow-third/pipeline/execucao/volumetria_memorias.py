"""Volumetria das memórias por papel e mês: quantas execuções do papel tiveram o erro de cada memória (fase 1 dos POCs).

Junta duas tabelas que já existem na máquina da base:
- `resultados/mineracao/U_sandbox/erros_lidos.csv`: uma linha por erro, com a memória (`memoria_id`), o papel e o mês;
- `data/base_contagens.parquet` (o pedido A): uma linha por execução, agente e papel, com ou sem erro.
Para cada memória × papel × mês: as execuções distintas com o erro ÷ as execuções do papel no mês (a incidência).
Só sai contagem, nome de memória, nome de papel e mês: nenhum identificador de execução, nenhum texto de caso.
Fica fora do hash do código da rodada (não altera nenhum arquivo de `versoes_codigo`).

Uso, da raiz (sem argumentos; os dois caminhos acima são os padrões):
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_memorias.py
Escreve `volumetria_memorias_por_mes.csv` e `volumetria_memorias_resumo.csv` ao lado do `erros_lidos.csv` e imprime o resumo.
"""
import argparse
from math import ceil, log
from pathlib import Path

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
ERROS_LIDOS = PIPELINE / "resultados" / "mineracao" / "U_sandbox" / "erros_lidos.csv"
CONTAGENS = PIPELINE.parent / "data" / "base_contagens.parquet"


def execucoes_por_papel_mes(cont):
    """Execuções do papel em cada mês, com a mediana de tokens e de passos (só as linhas com passos lidos)."""
    ok = cont[cont.qtd_actionsteps.notna()].rename(columns={"mes_execucao": "mes"})
    ok = ok.assign(mes=ok.mes.astype(str).str[:7])
    return (ok.groupby(["papel", "mes"]).agg(execucoes_do_papel=("cod_idef_exeo", "size"),
                                              mediana_tokens=("tokens_total", "median"),
                                              mediana_passos=("qtd_actionsteps", "median")).reset_index())


def casar_papeis(papeis_erro, papeis_cont):
    """papel dos erros → papel das contagens. O nome cortado (`ontestacaoCivel`) casa pelo final do nome; sem par: None."""
    mapa, avisos = {}, []
    for p in sorted(set(papeis_erro)):
        if p in papeis_cont:
            mapa[p] = p
            continue
        achados = [q for q in papeis_cont if q.endswith(p) and len(q) > len(p)]
        if len(achados) == 1:
            mapa[p] = achados[0]
            avisos.append(f"papel casado pelo nome cortado: {p} -> {achados[0]}")
        else:
            mapa[p] = None
            avisos.append(f"papel dos erros SEM correspondente nas contagens: {p}")
    return mapa, avisos


def execucoes_para_ver(p, confianca=0.95):
    """Quantas execuções para ver o erro ao menos uma vez com a confiança dada (0 < p < 1)."""
    return ceil(log(1 - confianca) / log(1 - p)) if 0 < p < 1 else None


def contar(erros, cont):
    """(por_mes, resumo, avisos). `erros`: erros_lidos; `cont`: base_contagens."""
    e = erros[erros.memoria_id.notna()].copy()
    e["mes"] = e.mes.astype(str).str[:7]
    den = execucoes_por_papel_mes(cont)
    mapa, avisos = casar_papeis(e.role, set(den.papel))
    e["papel"] = e.role.map(mapa)
    sem_par = e.papel.isna()
    if sem_par.any():
        avisos.append(f"{int(sem_par.sum())} erros ficaram sem papel nas contagens e saem da incidência")
    por_mes = (e[~sem_par].groupby(["memoria_id", "papel", "mes"])
               .agg(erros=("step_ref", "size"), execucoes_com_erro=("exec_id", "nunique")).reset_index())
    por_mes = por_mes.merge(den, on=["papel", "mes"], how="left")
    por_mes["incidencia"] = por_mes.execucoes_com_erro / por_mes.execucoes_do_papel
    meses = sorted(den.mes.unique())
    ultimos = set(meses[-2:])
    linhas = []
    for (mem, papel), g in por_mes.groupby(["memoria_id", "papel"]):
        rec = g[g.mes.isin(ultimos)]
        den_papel = den[den.papel.eq(papel)]
        den_rec = den_papel[den_papel.mes.isin(ultimos)].execucoes_do_papel.sum()
        p_rec = rec.execucoes_com_erro.sum() / den_rec if den_rec else float("nan")
        linhas.append({"memoria_id": mem, "papel": papel, "meses_com_erro": int(g.mes.nunique()),
                       "execucoes_com_erro_total": int(g.execucoes_com_erro.sum()),
                       "execucoes_do_papel_total": int(den_papel.execucoes_do_papel.sum()),
                       "incidencia_total": g.execucoes_com_erro.sum() / den_papel.execucoes_do_papel.sum(),
                       "ultimos_meses": ",".join(sorted(ultimos)),
                       "execucoes_com_erro_ultimos_2_meses": int(rec.execucoes_com_erro.sum()),
                       "execucoes_do_papel_ultimos_2_meses": int(den_rec),
                       "incidencia_ultimos_2_meses": p_rec,
                       "execucoes_para_ver_1_vez_95": execucoes_para_ver(p_rec) if p_rec == p_rec else None,
                       "mediana_tokens_papel": float(den_papel.mediana_tokens.median()),
                       "mediana_passos_papel": float(den_papel.mediana_passos.median())})
    resumo = pd.DataFrame(linhas).sort_values(["memoria_id", "execucoes_com_erro_total"], ascending=[True, False])
    return por_mes, resumo.reset_index(drop=True), avisos


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--erros-lidos", type=Path, default=ERROS_LIDOS)
    ap.add_argument("--contagens", type=Path, default=CONTAGENS)
    a = ap.parse_args(argv)
    for nome, arq in [("erros_lidos", a.erros_lidos), ("contagens", a.contagens)]:
        if not arq.is_file():
            raise SystemExit(f"não achei {nome}: {arq}")
    erros = pd.read_csv(a.erros_lidos, dtype={"exec_id": str, "step_ref": str})
    cont = pd.read_parquet(a.contagens)
    por_mes, resumo, avisos = contar(erros, cont)
    saida = a.erros_lidos.parent
    por_mes.to_csv(saida / "volumetria_memorias_por_mes.csv", index=False)
    resumo.to_csv(saida / "volumetria_memorias_resumo.csv", index=False)
    print(f"erros_lidos: {a.erros_lidos.name} ({len(erros)} linhas) · contagens: {a.contagens.name} ({len(cont)} linhas)")
    print(f"escrito em: {saida}")
    for av in avisos:
        print("AVISO:", av)
    with pd.option_context("display.width", 250, "display.max_columns", 30, "display.max_rows", 200):
        print(resumo.round(4).to_string(index=False))
        print("\npor mês:")
        print(por_mes.round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
