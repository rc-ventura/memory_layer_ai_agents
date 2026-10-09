"""Conferência da rodada real restaurada: Arrow direto + consistência interna.

Não é auditoria independente semântica. Não interpreta casos, não usa CSVs
legados, não executa notebooks/Jupyter/Athena nem aprova memórias. Exige hash de referência.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import matplotlib
matplotlib.use("Agg")
import pandas as pd
import pyarrow.parquet as pq

import base_pipeline as bp
import mineracao_observada as mo

OUT = mo.HERE / "resultados/conferencia_observada_2026-10-07"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    checks = {}
    report = {"estado": "em_execucao", "verificacoes": checks,
              "gerado_em": datetime.now(timezone.utc).isoformat(),
              "auditoria_semantica_independente": False,
              "memorias_aprovadas": 0}

    def save():
        (OUT / "conferencia.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")

    def check(name, condition):
        checks[name] = bool(condition)
        if not condition:
            report["estado"] = "falhou"
            save()
            raise AssertionError("Conferência falhou: " + name)

    save()
    source = mo.conferir_fonte(bp.TRACE, mo.FONTE_REFERENCIA_SHA256)
    report["fonte"] = source
    # Projeção Arrow direta: não usa leitor/adaptador nem conteúdos de casos em output.
    raw = pq.read_table(bp.TRACE, columns=["cod_idef_exeo", "cod_idef_aget", "papel", "step_pos",
                                           "structured_error", "observation_suspect", "error_message",
                                           "total_tokens", "duration_seconds"]).to_pandas()
    structured = pd.to_numeric(raw.structured_error).eq(1)
    suspect = pd.to_numeric(raw.observation_suspect).eq(1)
    messages = raw.error_message.astype("string").replace("", pd.NA)
    eligible = structured & messages.notna() & messages.str.len().lt(20000)
    tokens = pd.to_numeric(raw.total_tokens)
    duration = pd.to_numeric(raw.duration_seconds)
    A = bp.carregar_mineracao_observada()
    E = A.EU
    check("identidade_fonte", A.manifesto["fonte_id"] == source["sha256"])
    check("chaves_n_unicas_arrow", not raw.duplicated(["cod_idef_exeo", "cod_idef_aget", "papel", "step_pos"]).any())
    check("inventario_arrow", len(A.carga.steps) == len(raw) and len(E) == int(structured.sum())
          and A.resumo["suspeitas_fora_taxonomia"] == int(suspect.sum()))
    check("canais_disjuntos_arrow", not (structured & suspect).any())
    check("sintomas_elegiveis_arrow", A.resumo["sintomas_elegiveis"] == int(eligible.sum()))
    check("tokens_erro_arrow", E.tok_tot.sum(min_count=1) == tokens[structured].sum(min_count=1))
    check("duracao_erro_arrow", abs(E.dur_s.sum() - duration[structured].sum()) < .00001)
    check("custos_ausentes_arrow", int(E.tok_tot.isna().sum()) == int(tokens[structured].isna().sum())
          and int(E.dur_s.isna().sum()) == int(duration[structured].isna().sum()))
    observed = E.situacao_mecanismo.eq("observavel")
    T = A.tabelas["triagem_visivel_observada"]
    check("conservacao_erros", int(observed.sum()) + int((~observed).sum()) == len(E)
          and T.erros_observaveis.sum() == int(observed.sum()))
    check("conservacao_tokens", T.tokens_n_conhecidos.sum() + E.loc[~observed, "tok_tot"].sum() == tokens[structured].sum())
    check("pendencias_sem_unidade", E.loc[~observed, "unidade"].isna().all())
    check("indices_nao_fabricados", E.idx.isna().all())
    check("totais_globais_nao_fabricados", A.carga.execs[["n_steps", "tok_tot", "dur_s", "tem_final"]].isna().all().all())
    check("silenciosas_nao_medidas", T.silenciosas.eq("não medidas").all() and not A.capacidades["silenciosas_completas"])
    # Consistência interna não usa a tabela pronta para decidir a régua novamente.
    exec_counts = E.loc[observed].drop_duplicates(["unidade", "exec_id", "agente"]).groupby("unidade").size()
    month_counts = E.loc[observed].groupby("unidade").mes.nunique()
    kind = T.unidade.map(lambda u: bp.UNI[u][1])
    expected = set(T.loc[kind.isin([bp.FACT, bp.ESTR]) & T.unidade.map(exec_counts).ge(3)
                         & T.unidade.map(month_counts).ge(2), "unidade"])
    candidates = T.loc[T.decisao.eq(mo.CANDIDATO), "unidade"].tolist()
    check("candidatura_recontada_internamente", expected == set(candidates))
    check("destinos_nao_herdados", T.loc[kind.isin([bp.FACT, bp.ESTR]), "destino_proposto"].eq("em aberto").all())
    graph = mo.genealogia(A)
    stages = ["familia", "assinatura", "submecanismo", "unidade", "destino"]
    check("genealogia_sem_lacunas_ocultas", len(graph) == len(E) and not graph[stages].isna().any().any())
    graph_counts = {stage: int(graph[stage].value_counts().sum()) for stage in stages}
    check("genealogia_conserva_cada_coluna", all(n == int(structured.sum()) for n in graph_counts.values()))
    check("genealogia_pendencias_separadas", int(graph.destino.eq("COMPLEMENTAR evidência").sum()) == int((~observed).sum()))
    dest = mo.gravar(A, perfis=candidates)
    report["rodada"] = dest.name
    report["rodada_id"] = A.manifesto["rodada_id"]
    report["resumo"] = A.resumo
    report["genealogia_contagens_colunas"] = graph_counts
    report["candidatas"] = candidates
    report["tokens_candidatas"] = int(T.loc[T.decisao.eq(mo.CANDIDATO), "tokens_n_conhecidos"].sum())
    profiles = []
    for u in candidates:
        cases = mo.ler_artefato(dest, f"perfis/{u}/casos.csv", fonte_id=source["sha256"], rodada_id=A.manifesto["rodada_id"])
        sample = mo.ler_artefato(dest, f"perfis/{u}/amostra_investigacao.csv", fonte_id=source["sha256"], rodada_id=A.manifesto["rodada_id"])
        row = T[T.unidade.eq(u)].iloc[0]
        check("perfil_populacao_" + u, len(cases) == int(row.erros_observaveis)
              and len(cases[["exec_id", "agente"]].drop_duplicates()) == int(row.execucoes)
              and cases.mes.nunique() == int(row.meses) and cases.step_ref.is_unique)
        check("amostra_localizacao_" + u, len(sample) == min(30, len(cases)) and sample.step_ref.is_unique
              and set(sample.step_ref) <= set(cases.step_ref)
              and cases.idx.isna().all() and cases.step_pos.notna().all())
        profiles.append({"unidade": u, "erros": len(cases), "casos_amostra": len(sample),
                         "codigo_integral_sql_na_amostra": int(sample.code_estado.eq("sem_corte_sql").sum()),
                         "codigo_limitado_ou_ausente_na_amostra": int((~sample.code_estado.eq("sem_corte_sql")).sum())})
    pd.DataFrame(profiles).to_csv(OUT / "perfis_agregados.csv", index=False)
    # Consolidação em Python (antes nas células do consolidacao_unidades.ipynb): conserva o que a triagem conta.
    C = A.tabelas
    check("consolidacao_limitrofes", set(C["consolidacao_limitrofes"].unidade) == set(candidates))
    check("consolidacao_componentes", int(C["consolidacao_componentes_limites"].componentes.sum())
          == len(A.mecanismos.episodios.episodios))
    check("consolidacao_unidade_papel_mes", int(C["consolidacao_unidade_papel_mes"].erros.sum()) == int(observed.sum()))
    check("consolidacao_pendencias", int(C["consolidacao_pendencias"].erros.sum()) == int((~observed).sum()))
    check("consolidacao_global_papel", len(C["consolidacao_global_papel"]) == len(A.tabelas["triagem_por_papel"]))
    report["consolidacao_python"] = {k: len(v) for k, v in C.items() if k.startswith("consolidacao_")}
    final_manifest = json.loads((dest / "manifesto.json").read_text(encoding="utf-8"))
    check("hashes_todos_artefatos", all(mo.sha256(dest / name) == value for name, value in final_manifest["artefatos"].items()))
    check("fonte_inalterada_ao_final", mo.sha256(bp.TRACE) == source["sha256"])
    report["estado"] = "rodada_real_conferida_tecnicamente_sem_aprovacao_semantica"
    save()
    print(json.dumps({"estado": report["estado"], "rodada": dest.name, "verificacoes": len(checks),
                      "candidatas": len(candidates), "perfis": len(profiles),
                      "fonte_inalterada": checks["fonte_inalterada_ao_final"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
