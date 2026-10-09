"""Mineração do canal estruturado observado, sem censo nem sucesso implícito.

Reutiliza a taxonomia da pasta. Não chama o caminho raw, não lê CSV legado e
não promove memórias. Localizadores/casos e manifestações ficam em resultados.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

import base_pipeline as bp
from episodios_trace import contexto_local

HERE = Path(__file__).resolve().parent
CONTRATO = "mineracao_erros_observados_v1"
CANDIDATO = "candidato observado"
SEM_RECORRENCIA = "recorrência não demonstrada"
CHAVE_EXEC = ["exec_id", "agente"]
# Snapshot conferido da base 3 (docs 01 e 04). Fica no código, e não num resultado de rodada antiga, para a
# validação não depender de arquivos privados que podem ser apagados. Outra exportação = nova coorte, novo hash.
FONTE_REFERENCIA_SHA256 = "7604f77df9fe6127bd7fb9db18337b558b1f2587b0a99621c087b0cf3c2873f1"
CAPACIDADES = {
    "triagem_visivel": True, "perfil_candidata": True,
    "taxas_globais": False, "orcamento_global": False,
    "silenciosas_completas": False, "sucesso_semantico": False,
    "memoria_aprovada": False, "skills_legadas": False,
}


def caminho_io(path):
    """I/O Windows longo sem mudar localizador/nome lógico do artefato."""
    path = Path(os.path.abspath(path))
    text = str(path)
    if os.name == "nt" and not text.startswith("\\\\?\\"):
        text = "\\\\?\\UNC\\" + text[2:] if text.startswith("\\\\") else "\\\\?\\" + text
    return Path(text)


def sha256(path):
    with caminho_io(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def hash_codigo(path):
    path = Path(path)
    if path.suffix != ".ipynb":
        return sha256(path)
    notebook = json.loads(path.read_text(encoding="utf-8"))
    cells = [{"tipo": c["cell_type"], "source": "".join(c["source"]) if isinstance(c["source"], list) else c["source"]}
             for c in notebook["cells"]]
    # Outputs/metadados de execução não mudam a versão do consumidor.
    return hashlib.sha256(json.dumps(cells, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def versoes_codigo():
    paths = [HERE / "base_pipeline.py", HERE / "mineracao_observada.py",
             HERE / "genealogia_sankey.py", HERE / "paleta.py", HERE / "executar.py",
             HERE / "execucao" / "__init__.py", HERE / "execucao" / "executar_observada.py",
             HERE / "validacao" / "__init__.py",
             HERE / "validacao" / "validar_observada.py", HERE / "validacao" / "conferir_rodada_observada.py",
             HERE.parent.parent / "adaptador_trace.py",
             HERE.parent.parent / "episodios_trace.py", HERE.parent.parent / "leitor_trace.py",
             HERE.parent.parent / "esquema-memoria.json"]
    return {p.relative_to(HERE.parent.parent).as_posix(): hash_codigo(p) for p in paths}


def _json(value):
    """Serialização estável para hashes do contrato, sem payloads de casos."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)


def _validar(carga, mecanismos):
    source = carga.fonte.get("id")
    E = mecanismos.EU
    expected = carga.steps.loc[carga.steps.structured_error, "step_ref"]
    if (not source or E.attrs.get("fonte_carga_id") != source
            or not E.step_ref.is_unique or set(E.step_ref) != set(expected)
            or not E.structured_error.eq(True).all()):
        raise bp.AnaliseNaoIntegrada("Mecanismos sem proveniência/população da carga.")
    columns = ["exec_id", "agente", "role", "step_pos", "mes", "tok_tot", "dur_s"]
    original = carga.steps.set_index("step_ref").loc[E.step_ref, columns]
    if not original.equals(E.set_index("step_ref")[columns]):
        raise bp.AnaliseNaoIntegrada("Identidade/custos dos mecanismos diferem da carga.")
    observed = E.situacao_mecanismo.eq("observavel")
    if (not E.situacao_mecanismo.isin(["observavel", "pendente"]).all()
            or E.loc[observed, "unidade"].isna().any()
            or E.loc[~observed, "unidade"].notna().any()
            or E.loc[observed, "ocorrencia_observada"].isna().any()
            or not set(E.loc[observed, "unidade"]) <= set(bp.UNI)):
        raise bp.AnaliseNaoIntegrada("Unidades/ocorrências inconsistentes com a elegibilidade.")


def _decisao(u, g, min_execs, min_meses):
    tipo = bp.UNI[u][1]
    if tipo == bp.NAO:
        return "não-memória"
    if tipo == bp.CRIT:
        return bp.INVESTIGAR_CRITICO
    if tipo == bp.SEM:
        # Não dispara alarme histórico com universo de elegibilidade diferente.
        recurrent = any(len(p[CHAVE_EXEC].drop_duplicates()) >= min_execs
                        and p.mes.nunique() >= min_meses
                        for pattern, p in g.groupby("padrao", dropna=False)
                        if pd.notna(pattern) and not str(pattern).startswith(bp.SEM_NOME))
        return bp.REVISAR_PRIORIDADE if recurrent else bp.REVISAR_BAIXA
    if len(g[CHAVE_EXEC].drop_duplicates()) < min_execs or g.mes.nunique() < min_meses:
        return SEM_RECORRENCIA
    return bp.SINAL_HARNESS if bp.destino_mineracao(u) == "harness" else CANDIDATO


def triagem_observada(carga, mecanismos, min_execs=bp.MIN_EXECS, min_meses=bp.MIN_MESES, por_papel=False):
    """Mesma régua de recorrência; componentes são condicionais, nunca cascatas exatas.

    Execuções/meses são evidências observadas de recorrência, não taxas de risco.
    Componentes vêm de TODOS os problemas, antes de selecionar os classificáveis.
    """
    _validar(carga, mecanismos)
    if min_execs < 1 or min_meses < 1:
        raise ValueError("Limiares de recorrência devem ser positivos.")
    E = mecanismos.EU
    observed = E[E.situacao_mecanismo.eq("observavel")]
    keys = ["role", "unidade"] if por_papel else ["unidade"]
    rows = []
    for key, g in observed.groupby(keys, sort=True):
        u = key[-1] if isinstance(key, tuple) else key
        name, kind, _ = bp.UNI[u]
        if por_papel and kind not in (bp.FACT, bp.ESTR):
            continue
        closed = g[g.limites_componente_fechados.eq(True)]
        row = {
            "unidade": u, "nome": name, "tipo": kind,
            "decisao": _decisao(u, g, min_execs, min_meses),
            "destino_proposto": bp.destino_mineracao(u) if kind in (bp.FACT, bp.ESTR) else "não se aplica",
            "erros_observaveis": len(g), "execucoes": len(g[CHAVE_EXEC].drop_duplicates()),
            "meses": g.mes.nunique(), "papeis": g.role.nunique(),
            "ocorrencias_condicionais": g.ocorrencia_observada.nunique(),
            "ocorrencias_limites_fechados": closed.ocorrencia_observada.nunique(),
            "erros_limites_abertos": int((~g.limites_componente_fechados.fillna(False)).sum()),
            "tokens_n_conhecidos": g.tok_tot.sum(min_count=1),
            "tokens_n_ausentes": int(g.tok_tot.isna().sum()),
            "dur_s_n_conhecida": g.dur_s.sum(min_count=1),
            "dur_s_n_ausente": int(g.dur_s.isna().sum()),
            "familia_dominante": g.familia.value_counts().index[0],
            "silenciosas": "não medidas", "situacao": "triagem parcial; não memória aprovada",
        }
        if por_papel:
            row["role"] = key[0]
        rows.append(row)
    columns = ["unidade", "nome", "tipo", "decisao", "destino_proposto", "erros_observaveis",
               "execucoes", "meses", "papeis", "ocorrencias_condicionais", "ocorrencias_limites_fechados",
               "erros_limites_abertos", "tokens_n_conhecidos", "tokens_n_ausentes", "dur_s_n_conhecida",
               "dur_s_n_ausente", "familia_dominante", "silenciosas", "situacao"]
    if por_papel:
        columns = ["role"] + columns
    table = pd.DataFrame(rows, columns=columns).sort_values(
        ["decisao", "tokens_n_conhecidos", "unidade"], ascending=[True, False, True], na_position="last")
    denom = E.tok_tot.sum(min_count=1)
    table["pct_tokens_todos_estruturados"] = pd.Series(pd.NA, index=table.index, dtype="Float64")
    if E.tok_tot.notna().all() and pd.notna(denom) and denom > 0:
        table["pct_tokens_todos_estruturados"] = table.tokens_n_conhecidos.div(denom).mul(100)
    return table.reset_index(drop=True)


def analisar(carga=None):
    carga = bp.carregar_carga() if carga is None else carga
    if carga.contrato == bp.TRACE_COMPLETO:
        raise bp.AnaliseNaoIntegrada("Use o caminho raw existente para traces completos.")
    sintomas = bp.analisar_sintomas(carga)
    mecanismos = bp.analisar_mecanismos_observaveis(carga, sintomas)
    _validar(carga, mecanismos)
    tables = {**sintomas.tabelas, **mecanismos.tabelas}
    tables["triagem_visivel_observada"] = triagem_observada(carga, mecanismos)
    tables["triagem_sensibilidade"] = triagem_observada(carga, mecanismos, 5, 3)
    tables["triagem_por_papel"] = triagem_observada(carga, mecanismos, por_papel=True)
    tables["triagem_por_papel_sensibilidade"] = triagem_observada(carga, mecanismos, 5, 3, True)
    tables.update(consolidacao(tables, mecanismos))
    E = mecanismos.EU
    candidates = tables["triagem_visivel_observada"].decisao.eq(CANDIDATO)
    summary = {**sintomas.resumo, **mecanismos.resumo,
               "unidades_observaveis": int(E.unidade.nunique()),
               "candidatas_observadas": int(candidates.sum()),
               "tokens_estruturados_conhecidos": None if E.tok_tot.notna().sum() == 0 else int(E.tok_tot.sum()),
               "silenciosas": "não medidas", "aprovacao_memorias": "não realizada"}
    capabilities = {**CAPACIDADES, "indice_actionstep": carga.contrato != "janelas_legadas"}
    code = versoes_codigo()
    fingerprint = {"contrato": CONTRATO, "base": bp.BASE_ID,
                   "fonte_id": carga.fonte["id"], "codigo": code}
    run = hashlib.sha256(_json(fingerprint).encode("utf-8")).hexdigest()
    manifest = {**fingerprint, "rodada_id": run, "fonte_sha256": carga.fonte.get("sha256"),
                "contrato_fonte": carga.contrato, "capacidades": capabilities,
                "populacao": "n de erros estruturados exportados; não censo de ações",
                "snapshot": "não comprovado por manifest produtor",
                "silenciosas": "não medidas", "continuidade": "componentes condicionais; não causa/mesma chamada",
                "resumo": summary, "aprovacao_memorias": False}
    return SimpleNamespace(carga=carga, sintomas=sintomas, mecanismos=mecanismos, EU=E,
                           tabelas=tables, resumo=summary, capacidades=capabilities, manifesto=manifest)


def consolidacao(tabelas, mecanismos):
    """Quadros da consolidação (antes no consolidacao_unidades.ipynb), derivados das tabelas já calculadas.

    Não decide nada de novo: só cruza a triagem com a sensibilidade, abre os limites das componentes, a
    unidade por papel × mês e a fila de complementação. Contagens, não taxas; silenciosas não medidas.
    """
    T, TS = tabelas["triagem_visivel_observada"], tabelas["triagem_sensibilidade"]
    TP, TPS = tabelas["triagem_por_papel"], tabelas["triagem_por_papel_sensibilidade"]
    firmes = set(TS.loc[TS.decisao.eq(CANDIDATO), "unidade"])
    lim = T.loc[T.decisao.eq(CANDIDATO), ["unidade", "execucoes", "meses"]].copy()
    lim["candidata_5_3"] = lim.unidade.isin(firmes)
    eps = mecanismos.episodios.episodios
    comp = eps.groupby(["definicao", "inicio", "fim"], dropna=False).size().reset_index(name="componentes")
    obs = mecanismos.EU[mecanismos.EU.situacao_mecanismo.eq("observavel")]
    upm = obs.groupby(["unidade", "role", "mes"]).agg(
        erros=("step_ref", "size"), ocorrencias_condicionais=("ocorrencia_observada", "nunique")).reset_index()
    cob = tabelas["cobertura_mecanismos"]
    pend = cob[cob.situacao_mecanismo.eq("pendente")].reset_index(drop=True)
    gp = TP[["role", "unidade", "decisao"]].copy()
    gp["candidata_global"] = gp.unidade.isin(set(T.loc[T.decisao.eq(CANDIDATO), "unidade"]))
    estrito = TPS.set_index(["role", "unidade"]).decisao
    gp["candidata_papel_5_3"] = [estrito.get((r, u)) == CANDIDATO for r, u in zip(gp.role, gp.unidade)]
    pend_pm = (mecanismos.EU[~mecanismos.EU.situacao_mecanismo.eq("observavel")]
               .groupby(["motivo_evidencia", "role", "mes"], dropna=False)
               .agg(erros=("step_ref", "size"), tokens_n_conhecidos=("tok_tot", lambda s: s.sum(min_count=1)))
               .reset_index())
    return {"consolidacao_limitrofes": lim.reset_index(drop=True),
            "consolidacao_pendencias_papel_mes": pend_pm,
            "consolidacao_componentes_limites": comp,
            "consolidacao_unidade_papel_mes": upm,
            "consolidacao_pendencias": pend,
            "consolidacao_global_papel": gp.reset_index(drop=True)}


def genealogia(analise):
    """Conserva todos os erros em todas as colunas, incluindo pendências distintas de X_."""
    _validar(analise.carga, analise.mecanismos)
    E = analise.EU.copy()
    T = analise.tabelas["triagem_visivel_observada"].set_index("unidade")
    observed = E.situacao_mecanismo.eq("observavel")
    E["familia"] = E.familia.fillna("Evidência textual insuficiente")
    E["assinatura"] = E.assinatura.fillna("Mensagem limitada/ausente – pendente")
    E["submecanismo"] = E.submecanismo.fillna("Mecanismo pendente – falta de evidência")
    E["unidade"] = E.unidade.fillna("Unidade pendente – não resíduo")
    E["destino"] = "COMPLEMENTAR evidência"
    E.loc[observed, "destino"] = [T.loc[u, "decisao"] + " · " + bp.UNI[u][0]
                                  for u in E.loc[observed, "unidade"]]
    E["cat"] = "Evidência insuficiente"
    E.loc[observed, "cat"] = [bp.categoria_do_erro(f, u)
                              for f, u in zip(E.loc[observed, "familia"], E.loc[observed, "unidade"])]
    return E


def _vizinho(slot, lookup, incoming, ref, offset):
    if slot is None or slot.get("presenca") not in {"identificado_por_numero", "ordem_censo"}:
        return "desconhecido"
    if pd.notna(slot.get("err_type")):
        edge = incoming.get(ref) if offset == -1 else lookup.get(ref)
        return "erro estruturado vinculado" if edge else "erro estruturado observado; unidade desconhecida"
    flag = slot.get("error_like")
    if pd.isna(flag):
        return "desconhecido"
    return "suspeita observada" if flag else "sem sinal do produtor observado – não sucesso"


def perfil_unidade(analise, unidade):
    """G1–G6 com localização real e NULL preservado; nunca lê ocorrências legadas."""
    _validar(analise.carga, analise.mecanismos)
    T = analise.tabelas["triagem_visivel_observada"]
    target = T[T.unidade.eq(unidade)]
    if target.empty or target.decisao.iloc[0] != CANDIDATO:
        raise bp.AnaliseNaoIntegrada("A unidade não passou na triagem observada desta rodada.")
    g = analise.EU[analise.EU.unidade.eq(unidade)].copy()
    ctx = contexto_local(analise.carga)
    links = analise.carga.vinculos
    good = links[links.estado.isin(["compativel_candidato", "ordem_censo"])]
    out = dict(zip(good.origem_ref, good.alvo_ref))
    inc = dict(zip(good.alvo_ref, good.origem_ref))
    cases = g[["exec_id", "agente", "role", "step_ref", "step_pos", "idx", "indice_tipo", "mes",
               "versao_agente", "particao_fonte", "unidade", "submecanismo", "assinatura", "tool_name",
               "ocorrencia_observada", "limites_componente_fechados", "motivo_evidencia",
               "tok_tot", "dur_s", "code_estado", "err_msg_estado"]].copy()
    cases["fonte_id"] = analise.carga.fonte["id"]
    cases["rodada_id"] = analise.manifesto["rodada_id"]
    cases["antes"] = [_vizinho(ctx.get((r, -1)), out, inc, r, -1) for r in g.step_ref]
    cases["depois"] = [_vizinho(ctx.get((r, 1)), out, inc, r, 1) for r in g.step_ref]
    cases["proximo_final_observado"] = pd.array([
        ctx.get((r, 1), {}).get("is_final", pd.NA)
        if ctx.get((r, 1), {}).get("presenca") in {"identificado_por_numero", "ordem_censo"}
        else pd.NA for r in g.step_ref], dtype="boolean")
    cases["mesma_chamada"] = pd.NA
    cases["sucesso_semantico"] = pd.NA
    cases["modelo"] = pd.NA
    cases["versao_prompt"] = pd.NA
    tables = {"perfil": target.copy(), "casos": cases,
              "antes": cases.antes.value_counts().rename_axis("antes").reset_index(name="erros"),
              "depois": cases.depois.value_counts().rename_axis("depois").reset_index(name="erros")}
    subs, stability = [], []
    for dim in ["submecanismo", "assinatura", "role", "tool_name"]:
        for value, part in cases.groupby(dim, dropna=False, sort=True):
            subs.append({"dimensao": dim, "valor": value, "erros": len(part),
                         "ocorrencias_condicionais": part.ocorrencia_observada.nunique(),
                         "execucoes": len(part[CHAVE_EXEC].drop_duplicates()), "meses": part.mes.nunique()})
    for dim in ["mes", "versao_agente"]:
        for value, part in cases.groupby(dim, dropna=False, sort=True):
            stability.append({"dimensao": dim, "valor": value, "erros": len(part),
                              "execucoes": len(part[CHAVE_EXEC].drop_duplicates())})
    tables["proximo_final"] = (cases.proximo_final_observado.value_counts(dropna=False)
                               .rename_axis("proximo_final_observado").reset_index(name="erros"))
    tables["sub_unidades"] = pd.DataFrame(subs)
    tables["estabilidade"] = pd.DataFrame(stability)
    # Amostra determinística estratificada por papel: não é amostra probabilística.
    ordered = cases.sort_values(["role", "mes", "exec_id", "agente", "step_pos"])
    ordered = ordered.assign(ordem_no_papel=ordered.groupby("role").cumcount())
    tables["amostra_investigacao"] = ordered.sort_values(["ordem_no_papel", "role"]).head(30)
    return tables


def inventariar(pipeline=HERE, second=None):
    """Hashes e contagens, não mtime nem conteúdos. Não certifica artefato sem manifesto."""
    pipeline = Path(pipeline)
    second = (pipeline.parent.parent / "2026-09-trace-law-flow-second" / "pipeline"
              if second is None else Path(second))
    paths = list((pipeline / "resultados").glob("*.csv")) + list((pipeline.parent / "assets").glob("*"))
    rows = []
    for path in sorted(p for p in paths if p.is_file()):
        rel = path.relative_to(pipeline.parent)
        peer = second.parent / rel
        same = peer.is_file() and sha256(path) == sha256(peer)
        count = None
        if path.suffix == ".csv":
            # csv.reader conta registros com quebras de linha entre aspas corretamente.
            import csv
            with path.open(encoding="utf-8-sig", newline="") as stream:
                count = max(sum(1 for _ in csv.reader(stream)) - 1, 0)
        rows.append({"arquivo": rel.as_posix(), "sha256": sha256(path), "registros": count,
                     "igual_second": same, "estado": "legado_igual_second" if same else "não_certificado_sem_manifesto"})
    for path in sorted(pipeline.glob("*.ipynb")):
        nb = json.loads(path.read_text(encoding="utf-8"))
        outputs = sum(bool(c.get("outputs")) for c in nb["cells"] if c["cell_type"] == "code")
        rows.append({"arquivo": path.relative_to(pipeline.parent).as_posix(), "sha256": sha256(path),
                     "celulas_com_outputs": outputs, "estado": "outputs_não_certificam_fonte_atual"})
    # Colunas fixas: sem legados na pasta (limpeza de 07/10), o inventário vem vazio, mas com o mesmo esquema.
    return pd.DataFrame(rows, columns=["arquivo", "sha256", "registros", "igual_second", "estado", "celulas_com_outputs"])


def conferir_fonte(path, referencia=None):
    """Falha fechada em arquivo inválido ou divergência; nunca repara fonte."""
    import pyarrow.parquet as pq
    source = {"sha256": sha256(path), "tamanho_bytes": Path(path).stat().st_size}
    if referencia is not None and source["sha256"] != referencia:
        raise bp.AnaliseNaoIntegrada("Fonte diferente da referência; validar nova coorte explicitamente.")
    try:
        metadata = pq.read_metadata(path)
    except (OSError, ValueError) as exc:
        raise bp.AnaliseNaoIntegrada("Fonte não abre como Parquet íntegro; restauração/intake necessários.") from exc
    source.update(registros=metadata.num_rows, colunas=metadata.num_columns)
    return source


def gravar(analise, saida=None, perfis=()):
    """Publica somente em rodada privada, com hash de cada artefato e estado final."""
    _validar(analise.carga, analise.mecanismos)
    if analise.manifesto["codigo"] != versoes_codigo():
        raise bp.AnaliseNaoIntegrada("Código mudou após a análise; recompute a rodada.")
    root = (HERE / "resultados").resolve()
    dest = root / ("observada_" + analise.manifesto["rodada_id"][:16]) if saida is None else Path(saida).resolve()
    if dest == root or not dest.is_relative_to(root):
        raise ValueError("Saída deve ser uma subpasta privada de resultados, nunca a raiz canônica.")
    dest = caminho_io(dest)
    dest.mkdir(parents=True, exist_ok=True)
    manifest_path = dest / "manifesto.json"
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous.get("rodada_id") != analise.manifesto["rodada_id"]:
            raise bp.AnaliseNaoIntegrada("Pasta pertence a outra rodada; não sobrescrever.")
    source = analise.carga.fonte.get("sha256")
    source_path = analise.carga.fonte.get("caminho_local")
    if source and (not source_path or sha256(source_path) != source):
        raise bp.AnaliseNaoIntegrada("Fonte mudou após a carga; publicação suspensa.")
    manifest = {**analise.manifesto, "estado": "em_execucao", "artefatos": {},
                "gerado_em": datetime.now(timezone.utc).isoformat()}
    manifest_path.write_text(_json(manifest), encoding="utf-8")

    def save(name, table):
        path = dest / name
        path.parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(path, index=False)
        manifest["artefatos"][name] = sha256(path)

    for name, table in analise.tabelas.items():
        save(name + ".csv", table)
    save("inventario_legados.csv", inventariar())
    graph = genealogia(analise)
    from genealogia_sankey import montar_grafo, render_png
    _, edges, _ = montar_grafo(graph)
    edge_rows = [{"etapa": a + "->" + b, "origem": r[a], "destino": r[b], "categoria": r["cat"], "erros": int(r["n"])}
                 for (a, b), table in edges.items() for _, r in table.iterrows()]
    save("genealogia_arestas.csv", pd.DataFrame(edge_rows, columns=["etapa", "origem", "destino", "categoria", "erros"]))
    for name, figure in [("unidades_observadas.png", grafico_unidades(analise)),
                         ("papel_unidade.png", grafico_papeis(analise))]:
        figure.savefig(dest / name, dpi=150, bbox_inches="tight")
        import matplotlib.pyplot as plt
        plt.close(figure)
        manifest["artefatos"][name] = sha256(dest / name)
    if len(graph):
        render_png(graph, dest / "genealogia_observada.png",
                   titulo=f"{bp.BASE_ID} · {len(graph):,} erros estruturados · triagem observada, não memórias aprovadas")
        manifest["artefatos"]["genealogia_observada.png"] = sha256(dest / "genealogia_observada.png")
    for u in perfis:
        for name, table in perfil_unidade(analise, u).items():
            save(f"perfis/{u}/{name}.csv", table)
    if source and sha256(source_path) != source:
        raise bp.AnaliseNaoIntegrada("Fonte mudou durante a publicação; rodada não concluída.")
    manifest["estado"] = "concluida_tecnicamente_sem_aprovacao_semantica"
    manifest_path.write_text(_json(manifest), encoding="utf-8")
    return dest


def ler_artefato(pasta, nome, *, fonte_id, rodada_id):
    """Consumidores não aceitam pasta/base antiga nem tabela alterada após geração."""
    dest = caminho_io(pasta)
    manifest = json.loads((dest / "manifesto.json").read_text(encoding="utf-8"))
    if (manifest.get("contrato") != CONTRATO or manifest.get("base") != bp.BASE_ID
            or manifest.get("fonte_id") != fonte_id or manifest.get("rodada_id") != rodada_id
            or manifest.get("codigo") != versoes_codigo()
            or manifest.get("estado") != "concluida_tecnicamente_sem_aprovacao_semantica"):
        raise bp.AnaliseNaoIntegrada("Artefato sem contrato/rodada/fonte/código compatíveis.")
    if nome not in manifest["artefatos"] or not (dest / nome).resolve().is_relative_to(dest.resolve()):
        raise bp.AnaliseNaoIntegrada("Artefato fora do manifesto.")
    if sha256(dest / nome) != manifest["artefatos"][nome]:
        raise bp.AnaliseNaoIntegrada("Artefato mudou após a geração.")
    return pd.read_csv(dest / nome, dtype={"exec_id": str, "fonte_id": str, "rodada_id": str, "step_ref": str})


def grafico_unidades(analise):
    import matplotlib.pyplot as plt
    from paleta import COR_ERRO, cor
    T = analise.tabelas["triagem_visivel_observada"].sort_values("tokens_n_conhecidos")
    fig, ax = plt.subplots(figsize=(12, max(4, len(T) * .5)))
    if len(T):
        values = T.tokens_n_conhecidos.astype(float).div(1e6)
        ax.barh(range(len(T)), values, color=[cor(COR_ERRO, bp.categoria_do_erro(f, u))
                                              for f, u in zip(T.familia_dominante, T.unidade)])
        ax.set_yticks(range(len(T)), [f"{u} · {d}" for u, d in zip(T.unidade, T.decisao)])
    else:
        ax.text(.5, .5, "Nenhuma unidade observável", ha="center", transform=ax.transAxes)
    ax.set_title(f"{bp.BASE_ID} · unidades observadas / {len(analise.EU):,} erros estruturados\n"
                 "Somente custos conhecidos de n; pendências na cobertura, silenciosas não medidas")
    ax.set_xlabel("Milhões de tokens conhecidos em erros atribuídos – não orçamento/economia")
    fig.tight_layout()
    return fig


def grafico_papeis(analise):
    import matplotlib.pyplot as plt
    T = analise.tabelas["triagem_por_papel"]
    fig, ax = plt.subplots(figsize=(12, 7))
    if len(T):
        table = T.pivot(index="role", columns="unidade", values="erros_observaveis")
        ax.imshow(table.fillna(0).to_numpy(), aspect="auto", cmap="Blues")
        ax.set_xticks(range(len(table.columns)), table.columns, rotation=35, ha="right")
        ax.set_yticks(range(len(table.index)), table.index)
        decisions = T.set_index(["role", "unidade"]).decisao
        for i, role in enumerate(table.index):
            for j, u in enumerate(table.columns):
                value = table.loc[role, u]
                if pd.notna(value):
                    mark = "*" if decisions.loc[(role, u)] == CANDIDATO else ""
                    ax.text(j, i, f"{int(value)}{mark}", ha="center", va="center", fontsize=8,
                            bbox={"facecolor": "white", "alpha": .7, "edgecolor": "none"})
    else:
        ax.text(.5, .5, "Nenhuma unidade elegível a memória observável", ha="center", transform=ax.transAxes)
    ax.set_title(f"{bp.BASE_ID} · erros observáveis por papel × unidade\n* recorrência ≥3 execuções e ≥2 meses; não taxa de falha")
    fig.tight_layout()
    return fig
