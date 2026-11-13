"""Custo do passo com erro e volumetria de uma unidade (fase 1 dos POCs): o que a primeira volumetria não mediu.

Dois usos, com a mesma rodada da base 3 (as tabelas `perfis/<unidade>/casos.csv`, uma linha por erro, com `tok_tot`
e `dur_s` do passo que errou):
1. `--erros-lidos` + `--casos-sandbox`: para cada memória do sandbox × papel, os tokens e a duração do PASSO COM ERRO
   (mediana, p90) e quantos erros têm esses valores. É o `s` da conta de compensação.
2. `--casos-unidade` + `--nome`: para outra unidade (por exemplo, o retorno que chega como texto), a incidência por papel e
   mês (execuções distintas com a unidade ÷ execuções do papel) e o mesmo custo do passo com erro.
Só sai contagem, nome de memória, de unidade, de papel e mês, tokens e segundos: nenhum identificador de execução, nenhum
texto de caso. Fica fora do hash do código da rodada.

Uso, da raiz (os caminhos exatos estão em `pocs/prompt-maquina-2-custo-do-erro.md`):
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_custo_passo.py --casos-sandbox <casos.csv> --erros-lidos <erros_lidos.csv>
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/execucao/volumetria_custo_passo.py --casos-unidade <casos.csv> --nome <U_...>
"""
import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import volumetria_memorias as vm   # noqa: E402


def resumo_custo(g):
    """Mediana e p90 de tokens e de segundos do passo com erro; `n_sem_valor` conta os erros sem o dado."""
    tok, dur = pd.to_numeric(g.tok_tot, errors="coerce"), pd.to_numeric(g.dur_s, errors="coerce")
    return pd.Series({"erros": len(g), "execucoes": g.exec_id.nunique(),
                      "tokens_passo_mediana": tok.median(), "tokens_passo_p90": tok.quantile(0.9),
                      "segundos_passo_mediana": dur.median(), "segundos_passo_p90": dur.quantile(0.9),
                      "erros_sem_tokens": int(tok.isna().sum()), "erros_sem_duracao": int(dur.isna().sum())})


def custo_por_memoria(erros_lidos, casos):
    """memória × papel → custo do passo com erro. Une as duas tabelas pelo `step_ref` (a mesma chave da mineração)."""
    e = erros_lidos[erros_lidos.memoria_id.notna()][["memoria_id", "role", "step_ref", "exec_id"]]
    c = casos[["step_ref", "tok_tot", "dur_s"]].drop_duplicates("step_ref")
    j = e.merge(c, on="step_ref", how="left")
    sem = int((~e.step_ref.isin(c.step_ref)).sum())   # erros cujo step_ref não está nos casos
    out = j.groupby(["memoria_id", "role"]).apply(resumo_custo, include_groups=False).reset_index()
    return out.sort_values(["memoria_id", "erros"], ascending=[True, False]).reset_index(drop=True), sem


def volumetria_unidade(casos, cont, nome):
    """Incidência da unidade por papel e mês, com o custo do passo com erro (casos: perfis/<unidade>/casos.csv)."""
    k = casos.copy()
    k["mes"] = k.mes.astype(str).str[:7]
    den = vm.execucoes_por_papel_mes(cont)
    mapa, avisos = vm.casar_papeis(k.role, set(den.papel))
    k["papel"] = k.role.map(mapa)
    sem_par = k.papel.isna()
    if sem_par.any():
        avisos.append(f"{int(sem_par.sum())} erros sem papel nas contagens saem da incidência")
    k = k[~sem_par]
    por_mes = (k.groupby(["papel", "mes"]).agg(erros=("step_ref", "size"), execucoes_com_a_unidade=("exec_id", "nunique"),
                                                  tokens_passo_mediana=("tok_tot", "median"),
                                                  segundos_passo_mediana=("dur_s", "median")).reset_index())
    por_mes = por_mes.merge(den, on=["papel", "mes"], how="left")
    por_mes["incidencia"] = por_mes.execucoes_com_a_unidade / por_mes.execucoes_do_papel
    por_mes.insert(0, "unidade", nome)
    ultimos = set(sorted(den.mes.unique())[-2:])
    linhas = []
    for papel, g in por_mes.groupby("papel"):
        dp = den[den.papel.eq(papel)]
        rec = g[g.mes.isin(ultimos)]
        den_rec = dp[dp.mes.isin(ultimos)].execucoes_do_papel.sum()
        p_rec = rec.execucoes_com_a_unidade.sum() / den_rec if den_rec else float("nan")
        kk = k[k.papel.eq(papel)]
        linhas.append({"unidade": nome, "papel": papel, "erros_total": int(g.erros.sum()),
                       "execucoes_com_a_unidade_total": int(g.execucoes_com_a_unidade.sum()),
                       "execucoes_do_papel_total": int(dp.execucoes_do_papel.sum()),
                       "incidencia_total": g.execucoes_com_a_unidade.sum() / dp.execucoes_do_papel.sum(),
                       "ultimos_meses": ",".join(sorted(ultimos)),
                       "execucoes_com_a_unidade_ultimos_2_meses": int(rec.execucoes_com_a_unidade.sum()),
                       "execucoes_do_papel_ultimos_2_meses": int(den_rec),
                       "incidencia_ultimos_2_meses": p_rec,
                       "execucoes_para_ver_1_vez_95": vm.execucoes_para_ver(p_rec) if p_rec == p_rec else None,
                       "erros_por_execucao": g.erros.sum() / g.execucoes_com_a_unidade.sum(),
                       "tokens_passo_mediana": float(pd.to_numeric(kk.tok_tot, errors="coerce").median()),
                       "segundos_passo_mediana": float(pd.to_numeric(kk.dur_s, errors="coerce").median()),
                       "mediana_tokens_execucao_papel": float(dp.mediana_tokens.median()),
                       "mediana_passos_execucao_papel": float(dp.mediana_passos.median())})
    resumo = pd.DataFrame(linhas).sort_values("erros_total", ascending=False).reset_index(drop=True)
    return por_mes, resumo, avisos


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--casos-sandbox", type=Path)
    ap.add_argument("--erros-lidos", type=Path, default=vm.ERROS_LIDOS)
    ap.add_argument("--casos-unidade", type=Path)
    ap.add_argument("--nome", default="unidade")
    ap.add_argument("--contagens", type=Path, default=vm.CONTAGENS)
    a = ap.parse_args(argv)
    if not a.casos_sandbox and not a.casos_unidade:
        raise SystemExit("passe --casos-sandbox (com --erros-lidos) e/ou --casos-unidade (com --nome)")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    pd.set_option("display.max_rows", 300)
    if a.casos_sandbox:
        for nome, arq in [("casos do sandbox", a.casos_sandbox), ("erros_lidos", a.erros_lidos)]:
            if not arq.is_file():
                raise SystemExit(f"não achei {nome}: {arq}")
        out, sem = custo_por_memoria(pd.read_csv(a.erros_lidos, dtype={"exec_id": str, "step_ref": str}),
                                     pd.read_csv(a.casos_sandbox, dtype={"exec_id": str, "step_ref": str}))
        saida = a.casos_sandbox.parent / "custo_do_erro_por_memoria.csv"
        out.to_csv(saida, index=False)
        print(f"escrito: {saida.name} em {saida.parent}")
        if sem:
            print(f"AVISO: {sem} erros sem tokens/duração (a chave step_ref não achou o caso)")
        print(out.round(1).to_string(index=False))
    if a.casos_unidade:
        for nome, arq in [("casos da unidade", a.casos_unidade), ("contagens", a.contagens)]:
            if not arq.is_file():
                raise SystemExit(f"não achei {nome}: {arq}")
        por_mes, resumo, avisos = volumetria_unidade(pd.read_csv(a.casos_unidade, dtype={"exec_id": str, "step_ref": str}),
                                                      pd.read_parquet(a.contagens), a.nome)
        saida = a.casos_unidade.parent
        por_mes.to_csv(saida / f"volumetria_unidade_{a.nome}_por_mes.csv", index=False)
        resumo.to_csv(saida / f"volumetria_unidade_{a.nome}_resumo.csv", index=False)
        print(f"escrito: volumetria_unidade_{a.nome}_resumo.csv e _por_mes.csv em {saida}")
        for av in avisos:
            print("AVISO:", av)
        print(resumo.round(4).to_string(index=False))
        print("\npor mês (os 3 papéis com mais erros):")
        top = set(resumo.papel.head(3))
        print(por_mes[por_mes.papel.isin(top)].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
