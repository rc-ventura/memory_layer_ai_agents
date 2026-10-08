"""A query v1 da base 3 (ICTI_crossmemory_query_mineracao_erros) reescrita em Python, para um trace completo.

Serve para testar o modo observado com resposta conhecida: a base 1 (trace completo, aqui) passa pela mesma
extração que gerou a base 3 (na máquina 2), e o resultado é comparado com o pipeline clássico da base 1
(`comparar_base1.py`). Não é usado na análise da base 3 — lá a extração é a própria query no Athena.

Segue a query CTE a CTE, com a semântica do Trino onde ela importa:
- source_raw: período, memória não vazia, filtro de tamanho; deduplicação por (execução, agente);
- base/roles: `TRY(CAST(JSON_PARSE(...) AS MAP(VARCHAR, ARRAY(JSON))))` — um papel que não seja lista derruba o
  trace inteiro; papel em branco vira `<SEM_PAPEL>`;
- raw_steps: `UNNEST ... WITH ORDINALITY` (step_pos 1-based, conta todas as classes de step);
  `JSON_EXTRACT_SCALAR` devolve NULL para objeto/lista (o `action_output` dict some, como no Athena);
- classified/flags: erro estruturado = `error.type` preenchido; suspeita = regex nas observações;
- step_context: LAG/LEAD sobre os ActionSteps, `PARTITION BY execução, papel` (sem o agente), antes do filtro;
- errors_only + SELECT final: cortes por SUBSTR, `recovery_signal`, custos com COALESCE 0.

O filtro de tamanho soma três textos; no SQL, um NULL em qualquer um deles torna a soma NULL e exclui a linha.
No CSV da base 1 não dá para separar NULL de texto vazio, então `nulo_exclui` decide: True reproduz o SQL ao pé da
letra (tudo vazio vira NULL), False trata vazio como comprimento 0. O comparador roda as duas e reporta.
"""
from __future__ import annotations

import json
import re

import pandas as pd

COLUNAS_V1 = None  # preenchida no import (ordem do adaptador_trace.COLUNAS_JANELAS)

SUSPEITA = re.compile(r"(?i)input validation error|code execution failed|interpretererror|agentexecutionerror"
                      r"|validationerror|traceback \(most recent call last\)")
INICIO, FIM = 20250801, 20260930
LIMITE_TAMANHO = 30_000_000
CORTES = {  # coluna final -> (coluna de origem, tamanho)
    "error_message": 20000, "tool_calls": 12000, "error_model_output": 12000, "error_code_action": 12000,
    "error_observations": 20000, "error_action_output": 12000,
    "prev_model_output": 8000, "prev_code_action": 8000, "prev_observations": 12000,
    "next_model_output": 12000, "next_code_action": 12000, "next_observations": 16000, "next_error_message": 20000,
    "next2_model_output": 12000, "next2_code_action": 12000, "next2_observations": 16000, "next2_error_message": 20000,
}


def _vazio(v):
    return v is None or (isinstance(v, float) and pd.isna(v)) or (isinstance(v, str) and v.strip() == "")


def _escalar(v):
    """JSON_EXTRACT_SCALAR: texto do escalar; NULL para null, objeto e lista."""
    if v is None or isinstance(v, (dict, list)):
        return None
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return v
    return json.dumps(v)


def _int(v):
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _float(v):
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _bool(v):
    return {"true": True, "false": False}.get(v) if v is not None else None


def _texto(df, col):
    return df[col] if col in df else pd.Series(None, index=df.index, dtype=object)


def selecionar_snapshots(df, nulo_exclui=True):
    """source_raw + rn = 1. Devolve (snapshots, contagens)."""
    anomes = pd.to_numeric(_texto(df, "anomesdia").astype(str).str.replace("-", "", regex=False), errors="coerce")
    memo = _texto(df, "txt_etap_memo")
    ok = anomes.between(INICIO, FIM) & memo.notna() & memo.fillna("").str.strip().ne("")
    textos = [_texto(df, c) for c in ["txt_vrvl_locl", "txt_rspa_fina", "txt_etap_memo"]]
    if nulo_exclui:
        nulo = textos[0].isna() | textos[1].isna() | textos[2].isna()
        tamanho = sum(t.fillna("").str.len() for t in textos)
        ok &= ~nulo & tamanho.lt(LIMITE_TAMANHO)
    else:
        ok &= sum(t.fillna("").str.len() for t in textos).lt(LIMITE_TAMANHO)
    s = df[ok].copy()
    s["_anomes"] = anomes[ok]
    s["_encm"] = ~s["dat_hor_encm_exeo"].map(_vazio)
    s["_len"] = s["txt_etap_memo"].str.len()
    s = s.sort_values(["cod_idef_exeo", "cod_idef_aget", "_anomes", "_encm", "_len"],
                      ascending=[True, True, False, False, False], kind="mergesort")
    snap = s.drop_duplicates(["cod_idef_exeo", "cod_idef_aget"], keep="first")
    return snap, {"registros": len(df), "elegiveis": int(ok.sum()), "snapshots": len(snap),
                  "excluidos_por_filtro": int((~ok).sum()), "duplicados_descartados": len(s) - len(snap)}


def explodir_action_steps(snap):
    """base → roles → raw_steps → action_steps. Devolve (ActionSteps, traces invalidos)."""
    linhas, invalidos = [], 0
    for _, r in snap.iterrows():
        try:
            memo = json.loads(r["txt_etap_memo"])
            if not isinstance(memo, dict) or any(not isinstance(v, list) for v in memo.values()):
                raise ValueError
        except ValueError:
            invalidos += 1  # TRY(CAST(...)) devolve NULL e o trace inteiro some no CROSS JOIN
            continue
        comum = {c: r[c] for c in ["cod_idef_exeo", "cod_idef_aget", "cod_idef_stat_exeo_aget", "cod_idef_cvsa_asnc",
                                   "dat_hor_inio_exeo", "dat_hor_encm_exeo", "cod_vers_aget"]}
        comum["anomesdia"] = int(r["_anomes"])
        comum["has_final_locals"] = int(not _vazio(r.get("txt_vrvl_locl")))
        comum["has_persisted_response"] = int(not _vazio(r.get("txt_rspa_fina")))
        for papel, steps in memo.items():
            papel = papel if papel.strip() else "<SEM_PAPEL>"
            for pos, st in enumerate(steps, start=1):
                st = st if isinstance(st, dict) else {}
                if _escalar(st.get("__class__")) != "ActionStep":
                    continue
                err = st.get("error") if isinstance(st.get("error"), dict) else {}
                tu = st.get("token_usage") if isinstance(st.get("token_usage"), dict) else {}
                tm = st.get("timing") if isinstance(st.get("timing"), dict) else {}
                tc = st.get("tool_calls")
                tc0 = tc[0] if isinstance(tc, list) and tc and isinstance(tc[0], dict) else {}
                fn = tc0.get("function") if isinstance(tc0.get("function"), dict) else {}
                linhas.append({**comum, "papel": papel, "step_pos": pos,
                               "step_number": _int(_escalar(st.get("step_number"))),
                               "model_output": _escalar(st.get("model_output")),
                               "code_action": _escalar(st.get("code_action")),
                               "observations": _escalar(st.get("observations")),
                               "action_output": _escalar(st.get("action_output")),
                               "error_type": _escalar(err.get("type")),
                               "error_message": _escalar(err.get("message")),
                               "is_final_answer": _bool(_escalar(st.get("is_final_answer"))),
                               "input_tokens": _int(_escalar(tu.get("input_tokens"))),
                               "output_tokens": _int(_escalar(tu.get("output_tokens"))),
                               "total_tokens": _int(_escalar(tu.get("total_tokens"))),
                               "duration_seconds": _float(_escalar(tm.get("duration"))),
                               "tool_name": _escalar(fn.get("name")),
                               "tool_calls": None if tc is None else json.dumps(tc, ensure_ascii=False, separators=(",", ":"))})
    return pd.DataFrame(linhas), invalidos


def contexto(a):
    """classified → flags → step_context (LAG/LEAD antes do filtro, sem o agente na partição)."""
    a = a.sort_values(["cod_idef_exeo", "papel", "step_pos"], kind="mergesort").reset_index(drop=True)
    a["structured_error"] = a.error_type.notna().astype(int)
    a["observation_suspect"] = (a.error_type.isna()
                                & a.observations.fillna("").map(lambda s: bool(SUSPEITA.search(s)))).astype(int)
    a["error_like"] = (a.structured_error.eq(1) | a.observation_suspect.eq(1)).astype(int)
    g = a.groupby(["cod_idef_exeo", "papel"], sort=False)
    for c in ["step_number", "model_output", "code_action", "observations", "error_type", "error_like"]:
        a["prev_" + c] = g[c].shift(1)
    vizinho = ["step_number", "model_output", "code_action", "observations", "error_type", "error_like",
               "is_final_answer", "error_message", "tool_name", "input_tokens", "output_tokens", "total_tokens",
               "duration_seconds"]
    for k, pref in [(1, "next_"), (2, "next2_")]:
        for c in vizinho:
            a[pref + c] = g[c].shift(-k)
    a["execution_has_final_step"] = g["is_final_answer"].transform(lambda s: int(s.eq(True).any()))
    # idx = ordinal do ActionStep no papel (a chave do pipeline clássico); não sai no parquet v1
    a["_idx"] = g.cumcount()
    return a


def _recovery(r):
    def eq(v, x):
        return v is not None and not pd.isna(v) and v == x
    if pd.isna(r.next_step_number):
        return "NO_NEXT_ACTION"
    if eq(r.next_error_like, 0) and eq(r.next_is_final_answer, True):
        return "RECOVERED_TO_FINAL_NEXT_ACTION"
    if eq(r.next_error_like, 1) and eq(r.next2_error_like, 0) and eq(r.next2_is_final_answer, True):
        return "RECOVERED_TO_FINAL_WITHIN_2_ACTIONS"
    if eq(r.next_error_like, 0):
        return "POSSIBLE_RECOVERY_NEXT_ACTION"
    if eq(r.next_error_like, 1) and eq(r.next2_error_like, 0):
        return "POSSIBLE_RECOVERY_WITHIN_2_ACTIONS"
    if eq(r.next_error_like, 1) and eq(r.next2_error_like, 1):
        return "ERROR_CASCADE"
    return "UNKNOWN"


def selecionar_erros(a):
    """errors_only + SELECT final, nas 69 colunas e na ordem do parquet da base 3."""
    e = a[a.structured_error.eq(1) | a.observation_suspect.eq(1)].copy()
    e["mes_execucao"] = e.dat_hor_inio_exeo.str[:7]
    e["error_source"] = e.structured_error.map({1: "STRUCTURED_ERROR", 0: "OBSERVATION_SUSPECT"})
    e = e.rename(columns={"model_output": "error_model_output", "code_action": "error_code_action",
                          "observations": "error_observations", "action_output": "error_action_output"})
    for c, n in CORTES.items():
        e[c] = e[c].where(e[c].isna(), e[c].astype(object).map(lambda s: s[:n] if isinstance(s, str) else s))
    z = lambda c: pd.to_numeric(e[c], errors="coerce").fillna(0)
    e["recovery_signal"] = [_recovery(r) for r in e.itertuples()]
    e["tokens_error_plus_next_action"] = (z("total_tokens") + z("next_total_tokens")).astype("int64")
    e["seconds_error_plus_next_action"] = z("duration_seconds") + z("next_duration_seconds")
    e["tokens_error_plus_next_2_actions"] = (z("total_tokens") + z("next_total_tokens") + z("next2_total_tokens")).astype("int64")
    e["seconds_error_plus_next_2_actions"] = z("duration_seconds") + z("next_duration_seconds") + z("next2_duration_seconds")
    e["num_actions_after_error_observed"] = [0 if pd.isna(n1) else 1 if pd.isna(n2) else 2
                                             for n1, n2 in zip(e.next_step_number, e.next2_step_number)]
    e["has_full_2_action_window"] = e.next2_step_number.notna().astype(int)
    e = e.sort_values(["cod_idef_exeo", "papel", "step_pos"], kind="mergesort")
    mapa = e[["cod_idef_exeo", "cod_idef_aget", "papel", "step_pos", "_idx"]].rename(columns={"_idx": "idx"})
    return e[list(COLUNAS_V1)].reset_index(drop=True), mapa.reset_index(drop=True)


def tipar(e):
    """Tipos como no parquet real: inteiros de n em int64, vizinhos numéricos em double, flag final em bool."""
    e = e.copy()
    for c in ["cod_idef_aget", "cod_idef_stat_exeo_aget", "cod_vers_aget", "step_pos", "step_number",
              "input_tokens", "output_tokens", "total_tokens", "structured_error", "observation_suspect",
              "has_final_locals", "has_persisted_response", "execution_has_final_step", "anomesdia"]:
        e[c] = pd.to_numeric(e[c], errors="coerce").astype("Int64")
    for c in [c for c in e if c.startswith(("prev_", "next_", "next2_"))
              and c.endswith(("step_number", "error_like", "tokens", "seconds"))] + ["duration_seconds"]:
        e[c] = pd.to_numeric(e[c], errors="coerce").astype("float64")
    for c in ["next_is_final_answer", "next2_is_final_answer"]:
        e[c] = e[c].astype("boolean")
    for c in ["cod_idef_exeo", "cod_idef_cvsa_asnc", "dat_hor_inio_exeo", "dat_hor_encm_exeo", "mes_execucao"]:
        e[c] = e[c].astype("string")
    return e


def porta_v1(df_raw, nulo_exclui=True):
    """Trace completo (texto, como o leitor_trace entrega) → (parquet v1 tipado, mapa step_pos→idx, contagens)."""
    snap, cont = selecionar_snapshots(df_raw, nulo_exclui)
    a, invalidos = explodir_action_steps(snap)
    cont.update(traces_invalidos=invalidos, action_steps=len(a))
    if a.empty:
        return pd.DataFrame(columns=list(COLUNAS_V1)), pd.DataFrame(), cont
    e, mapa = selecionar_erros(contexto(a))
    cont.update(linhas=len(e), estruturados=int(e.structured_error.sum()), suspeitas=int(e.observation_suspect.sum()))
    return tipar(e), mapa, cont


def _colunas():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from adaptador_trace import COLUNAS_JANELAS
    return COLUNAS_JANELAS


COLUNAS_V1 = _colunas()
