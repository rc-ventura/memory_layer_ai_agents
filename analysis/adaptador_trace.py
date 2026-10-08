"""Núcleo estrutural de fontes de steps; não classifica erros nem cria memória.

Etapa 4: janelas da extração legada e censo compacto v2. Os consumidores ainda
não estão integrados. Texto ausente/cortado não equivale a ausência no trace.
`steps` contém apenas n; `slots` não deve ser somado como novas ações.
Nenhuma função imprime IDs/payloads ou escreve arquivos de dados.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
import hashlib
import json
import math
from typing import Iterable

import pandas as pd

try:
    from .leitor_trace import colunas_do_trace, ler_trace
except ImportError:
    from leitor_trace import colunas_do_trace, ler_trace

JANELAS = "janelas_legadas"
CENSO = "censo_actionsteps_v2_proposta"
TRACE_COMPLETO = "trace_completo"

COLUNAS_JANELAS = tuple("""
cod_idef_exeo cod_idef_aget papel cod_idef_stat_exeo_aget cod_idef_cvsa_asnc
cod_vers_aget dat_hor_inio_exeo dat_hor_encm_exeo mes_execucao has_final_locals
has_persisted_response execution_has_final_step error_source structured_error
observation_suspect step_number step_pos error_type error_message tool_name tool_calls
error_model_output error_code_action error_observations error_action_output
input_tokens output_tokens total_tokens duration_seconds
prev_step_number prev_model_output prev_code_action prev_observations prev_error_type prev_error_like
next_step_number next_model_output next_code_action next_observations next_error_type next_error_like
next_is_final_answer next_error_message next_tool_name next_input_tokens next_output_tokens next_total_tokens next_duration_seconds
next2_step_number next2_model_output next2_code_action next2_observations next2_error_type next2_error_like
next2_is_final_answer next2_error_message next2_tool_name next2_input_tokens next2_output_tokens next2_total_tokens next2_duration_seconds
recovery_signal tokens_error_plus_next_action seconds_error_plus_next_action
tokens_error_plus_next_2_actions seconds_error_plus_next_2_actions num_actions_after_error_observed has_full_2_action_window anomesdia
""".split())
COLUNAS_CENSO = tuple("""
extraction_contract cod_idef_exeo cod_idef_aget papel_original papel cod_idef_stat_exeo_aget
cod_idef_cvsa_asnc cod_vers_aget dat_hor_inio_exeo dat_hor_encm_exeo mes_execucao
source_trace_sha256 source_trace_length has_final_locals has_persisted_response
step_pos step_number action_idx n_actions_role chamada_id n_task_steps_role
n_planning_steps_role n_raw_steps_role is_final_answer role_has_final_step n_actions_final_flag_unknown
structured_error observation_suspect error_like error_source error_type
error_message error_message_length error_message_truncated tool_name
tool_calls_json_fragment tool_calls_json_length tool_calls_json_truncated
model_output model_output_length model_output_truncated code_action code_action_length code_action_truncated
observations observations_length observations_truncated
action_output_scalar action_output_scalar_length action_output_scalar_truncated
action_output_json_fragment action_output_json_length action_output_json_truncated action_output_kind
input_tokens output_tokens total_tokens duration_seconds step_start_time step_end_time anomesdia
""".split())

# Nome interno -> campo/cap de n em cada contrato. Não altera texto nem completa sufixos.
TEXTOS_JANELAS = {
    "err_msg": ("error_message", 20000), "code": ("error_code_action", 12000),
    "thought": ("error_model_output", 12000), "observations": ("error_observations", 20000),
    "out": ("error_action_output", 12000), "tool_calls": ("tool_calls", 12000),
}
TEXTOS_CENSO = {
    "err_msg": ("error_message", 20000), "code": ("code_action", 12000),
    "thought": ("model_output", 12000), "observations": ("observations", 20000),
    "out": ("action_output_scalar", 12000), "tool_calls": ("tool_calls_json_fragment", 12000),
    "out_json": ("action_output_json_fragment", 12000),
}
LIMITES_SLOT = {
    "prev": {"thought": 8000, "code": 8000, "observations": 12000},
    "next": {"thought": 12000, "code": 12000, "observations": 16000, "err_msg": 20000},
    "next2": {"thought": 12000, "code": 12000, "observations": 16000, "err_msg": 20000},
}
TEXTO_DTYPE = pd.StringDtype(storage="python")


class ErroContrato(ValueError):
    """Mensagem sem valores de caso; detalhe pertence ao intake privado."""


@dataclass
class BaseEstrutural:
    contrato: str
    fonte: dict
    origem: pd.DataFrame
    steps: pd.DataFrame
    slots: pd.DataFrame
    vinculos: pd.DataFrame
    cobertura: dict

    def resumo(self) -> dict:
        """Só contagens/estados, apropriado para diagnóstico sem payloads."""
        return {
            "contrato": self.contrato, "registros_n": len(self.steps),
            "execucoes_representadas": int(self.steps.exec_id.nunique()),
            "estruturados": int(self.steps.structured_error.sum()),
            "suspeitas": int(self.steps.observation_suspect.sum()),
            "sem_sinal": int((~self.steps.error_like).sum()),
            "slots": len(self.slots),
            "vinculos_por_estado": self.vinculos.estado.value_counts().to_dict(),
            "cobertura": dict(self.cobertura),
        }


def detectar_contrato(colunas: Iterable[str] | pd.DataFrame) -> str:
    """Detecta a família do schema, sem afirmar que a população é completa."""
    cols = set(colunas.columns if isinstance(colunas, pd.DataFrame) else colunas)
    markers = [
        TRACE_COMPLETO if "txt_etap_memo" in cols else None,
        JANELAS if {"error_code_action", "prev_step_number", "next_step_number"} <= cols else None,
        CENSO if {"extraction_contract", "action_idx", "papel_original"} <= cols else None,
    ]
    hits = [x for x in markers if x]
    if len(hits) != 1:
        raise ErroContrato("Schema desconhecido ou mistura ambígua de contratos.")
    return hits[0]


def _text(series: pd.Series) -> pd.Series:
    return series.astype(TEXTO_DTYPE).replace("", pd.NA)


def _number(series: pd.Series, field: str, integer: bool = False) -> pd.Series:
    source = series.replace("", pd.NA)
    if integer:
        values = []
        for value in source:
            if pd.isna(value):
                values.append(pd.NA)
                continue
            try:
                exact = Decimal(str(value))
            except InvalidOperation:
                raise ErroContrato(f"Campo numérico inválido: {field}.") from None
            if not exact.is_finite():
                raise ErroContrato(f"Campo numérico inválido: {field}.")
            if exact != exact.to_integral_value():
                raise ErroContrato(f"Campo inteiro fracionário: {field}.")
            values.append(int(exact))
        try:
            return pd.Series(values, index=series.index, dtype="Int64")
        except (TypeError, ValueError, OverflowError):
            raise ErroContrato(f"Campo fora do domínio numérico: {field}.") from None
    nums = pd.to_numeric(source, errors="coerce")
    bad = source.notna() & nums.isna()
    if bad.any() or any(not math.isfinite(float(v)) for v in nums.dropna()):
        raise ErroContrato(f"Campo numérico inválido: {field}.")
    try:
        return nums.astype("Float64")
    except (TypeError, ValueError, OverflowError):
        raise ErroContrato(f"Campo fora do domínio numérico: {field}.") from None


def _boolean(series: pd.Series, field: str) -> pd.Series:
    s = _text(series).str.lower()
    values = {"true": True, "false": False, "1": True, "0": False, "1.0": True, "0.0": False}
    if (s.notna() & ~s.isin(values)).any():
        raise ErroContrato(f"Indicador fora do domínio booleano: {field}.")
    return s.map(values).astype("boolean")


def _required_values(frame: pd.DataFrame, names: list[str]) -> None:
    if frame[names].isna().any().any():
        raise ErroContrato("Chave ou indicador obrigatório contém nulos.")


def _ref(fonte_id: str, parts: list) -> str:
    raw = json.dumps(parts, ensure_ascii=False, separators=(",", ":"))
    return fonte_id + ":" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _estado_texto(frame: pd.DataFrame, field: str, cap: int, census: bool) -> pd.Series:
    s = _text(frame[field])
    lengths = s.str.len()
    if lengths.gt(cap).any():
        raise ErroContrato(f"Texto excede limite do contrato: {field}.")
    result = pd.Series("ausente_na_projecao", index=frame.index, dtype=TEXTO_DTYPE)
    result.loc[s.notna() & lengths.lt(cap)] = "sem_corte_sql"
    result.loc[s.notna() & lengths.eq(cap)] = "possivelmente_cortado"
    if census:
        stem = field.removesuffix("_fragment") if field.endswith("_fragment") else field
        declared = _number(frame[stem + "_length"], stem + "_length", True)
        flag = _boolean(frame[stem + "_truncated"], stem + "_truncated")
        # Vazio vira nulo pelo leitor, porém comprimento original zero é conhecido.
        empty = s.isna() & declared.eq(0).fillna(False) & flag.eq(False).fillna(False)
        absent = s.isna() & declared.isna() & flag.isna()
        seen = s.notna() & declared.notna() & flag.notna()
        valid_seen = seen & declared.ge(0) & lengths.eq(declared.clip(upper=cap)) & flag.eq(declared.gt(cap))
        if (~(empty | absent | valid_seen.fillna(False))).any():
            raise ErroContrato(f"Comprimento/flag de corte incompatível: {field}.")
        result.loc[empty] = "vazio_na_origem"
        result.loc[seen & flag.eq(False)] = "sem_corte_sql"
        result.loc[seen & flag.eq(True)] = "cortado"
    return result


def _unavailable(index: pd.Index, dtype: str = "Int64") -> pd.Series:
    return pd.Series(pd.NA, index=index, dtype=dtype)


def adaptar(df: pd.DataFrame, *, fonte_id: str) -> BaseEstrutural:
    """Normaliza a fonte sem mutation. Exige ID de fonte para referências estáveis.

    Não aceita trace completo neste núcleo: preservar o caminho existente.
    Censo B precisa satisfazer índices e contagens declarados dentro dos grupos;
    ausência de grupos inteiros só será detectada com manifest externo.
    """
    if not isinstance(fonte_id, str) or not fonte_id.strip():
        raise ErroContrato("Identificação da fonte obrigatória.")
    mode = detectar_contrato(df)
    if mode == TRACE_COMPLETO:
        raise ErroContrato("Trace completo: use o caminho existente; este núcleo não o substitui.")
    required = COLUNAS_JANELAS if mode == JANELAS else COLUNAS_CENSO
    if set(required) - set(df.columns):
        raise ErroContrato("Schema incompleto para o contrato detectado.")
    origin = df.copy(deep=True).reset_index(drop=True)
    if mode == CENSO and not _text(origin.extraction_contract).eq(CENSO).fillna(False).all():
        raise ErroContrato("Versão do censo não corresponde ao contrato suportado.")
    idx = origin.index
    identity_role = "papel" if mode == JANELAS else "papel_original"
    steps = pd.DataFrame(index=idx)
    for dest, src in [("exec_id", "cod_idef_exeo"), ("role", identity_role), ("role_rotulo", "papel"),
                      ("err_type", "error_type"), ("error_source", "error_source"), ("tool_name", "tool_name")]:
        steps[dest] = _text(origin[src])
    for dest, src in [("agente", "cod_idef_aget"), ("step_pos", "step_pos"), ("step", "step_number"),
                      ("versao_agente", "cod_vers_aget"), ("status", "cod_idef_stat_exeo_aget"),
                      ("particao_fonte", "anomesdia")]:
        steps[dest] = _number(origin[src], src, True)
    partition = pd.to_datetime(steps.particao_fonte.astype(TEXTO_DTYPE), format="%Y%m%d", errors="coerce")
    if (steps.particao_fonte.notna() & partition.isna()).any():
        raise ErroContrato("Partição preenchida não representa AAAAMMDD válido.")
    steps["mes_particao"] = partition.dt.to_period("M").astype(TEXTO_DTYPE).where(partition.notna(), pd.NA)
    for c in ["structured_error", "observation_suspect"]:
        steps[c] = _boolean(origin[c], c)
    _required_values(steps, ["exec_id", "agente", "role", "step_pos", "structured_error", "observation_suspect"])
    if steps.duplicated(["exec_id", "agente", "role", "step_pos"]).any():
        raise ErroContrato("Chave duplicada; nenhuma linha será descartada automaticamente.")
    if steps.step_pos.lt(1).any() or steps.step.dropna().lt(0).any():
        raise ErroContrato("Posição original deve ser 1-based; step_number não pode ser negativo.")
    group = ["cod_idef_exeo", "cod_idef_aget"]
    metadata = ["dat_hor_inio_exeo", "dat_hor_encm_exeo", "cod_vers_aget", "anomesdia", "cod_idef_stat_exeo_aget"]
    if origin.groupby(group, dropna=False)[metadata].nunique(dropna=False).gt(1).any().any():
        raise ErroContrato("Metadados de execução/agente variam; possível mistura de snapshots.")
    steps["error_like"] = steps.structured_error | steps.observation_suspect
    if (steps.structured_error & steps.observation_suspect).any():
        raise ErroContrato("Fontes de erro sobrepostas no mesmo n.")
    if not steps.structured_error.eq(steps.err_type.notna()).all():
        raise ErroContrato("Indicador estruturado e presença de tipo discordam.")
    expected = pd.Series("NO_ERROR_SIGNAL", index=idx, dtype=TEXTO_DTYPE)
    expected.loc[steps.structured_error] = "STRUCTURED_ERROR"
    expected.loc[steps.observation_suspect] = "OBSERVATION_SUSPECT"
    # A legada exporta error_source NULL no complemento sem sinal.
    source_matches = steps.error_source.eq(expected).fillna(False)
    if mode == JANELAS:
        source_matches |= ~steps.error_like & steps.error_source.isna()
    if not source_matches.all():
        raise ErroContrato("Origem e indicadores discordam; não reclassificar a fonte.")
    steps["mes"] = _text(origin.mes_execucao)
    date = pd.to_datetime(origin.dat_hor_inio_exeo, format="mixed", errors="coerce")
    if date.isna().any() or not date.dt.to_period("M").astype(str).eq(steps.mes).all():
        raise ErroContrato("Data de início ou mês real incompatível.")
    for dest, src in [("tok_in", "input_tokens"), ("tok_out", "output_tokens"), ("tok_tot", "total_tokens")]:
        steps[dest] = _number(origin[src], src, True)
    steps["dur_s"] = _number(origin.duration_seconds, "duration_seconds")
    if steps[["tok_in", "tok_out", "tok_tot", "dur_s"]].lt(0).any().any():
        raise ErroContrato("Custo negativo no n.")
    text_map = TEXTOS_JANELAS if mode == JANELAS else TEXTOS_CENSO
    for dest, (src, cap) in text_map.items():
        steps[dest] = _text(origin[src])
        steps[dest + "_estado"] = _estado_texto(origin, src, cap, mode == CENSO)
    for dest in ["sysprompt", "ctx"]:
        steps[dest] = _unavailable(idx, TEXTO_DTYPE)
        steps[dest + "_estado"] = pd.Series("nao_exportado", index=idx, dtype=TEXTO_DTYPE)
    steps["linha_fonte"] = pd.Series(range(len(steps)), dtype="Int64")
    steps["step_ref"] = pd.Series(
        [_ref(fonte_id, [str(e), int(a), str(r), int(p)])
         for e, a, r, p in steps[["exec_id", "agente", "role", "step_pos"]].itertuples(index=False, name=None)],
        index=idx, dtype=TEXTO_DTYPE,
    )
    if mode == JANELAS:
        for c in ["idx", "n_steps_role", "chamada_id"]:
            steps[c] = _unavailable(idx)
        steps["is_final"] = _unavailable(idx, "boolean")
        steps["indice_tipo"] = "posicao_original_sem_ordinal_actionstep"
        steps["tem_final_no_papel"] = _boolean(origin.execution_has_final_step, "execution_has_final_step")
        steps["recovery_signal_produtor"] = _text(origin.recovery_signal)
        slots = _slots_janelas(origin, steps)
        links = _vinculos_janelas(steps, slots)
        coverage = {"populacao_global": "nao_observavel", "idx_global": "nao_observavel",
                    "fronteira_chamada": "nao_observavel", "texto_integral": "parcial",
                    "vinculos": "candidatos_conferir_trace", "contexto_modelo": "nao_observavel"}
    else:
        steps["idx"] = _number(origin.action_idx, "action_idx", True)
        steps["n_steps_role"] = _number(origin.n_actions_role, "n_actions_role", True)
        steps["chamada_id"] = _number(origin.chamada_id, "chamada_id", True)
        steps["is_final"] = _boolean(origin.is_final_answer, "is_final_answer")
        steps["tem_final_no_papel"] = _boolean(origin.role_has_final_step, "role_has_final_step")
        steps["indice_tipo"] = "ordinal_actionstep_0_based_declarado"
        _validar_censo(origin, steps)
        slots = pd.DataFrame(columns=["origem_ref", "offset", "slot_ref", "presenca"])
        links = _vinculos_censo(steps)
        coverage = {"populacao_global": "condicionada_manifesto_externo", "idx_global": "consistente_no_arquivo",
                    "fronteira_chamada": "contador_taskstep_nao_prova_namespace", "texto_integral": "parcial",
                    "vinculos": "ordem_declarada_censo", "contexto_modelo": "nao_observavel"}
    return BaseEstrutural(mode, {"id": fonte_id, "colunas": list(origin.columns),
                                 "formato": dict(df.attrs.get("formato", {}))}, origin, steps, slots, links, coverage)


def _slots_janelas(origin: pd.DataFrame, steps: pd.DataFrame) -> pd.DataFrame:
    parts = []
    mapping = {"step": "step_number", "err_type": "error_type", "error_like": "error_like",
               "is_final": "is_final_answer", "err_msg": "error_message", "tool_name": "tool_name",
               "code": "code_action", "thought": "model_output", "observations": "observations",
               "tok_in": "input_tokens", "tok_out": "output_tokens", "tok_tot": "total_tokens", "dur_s": "duration_seconds"}
    for prefix, offset in [("prev", -1), ("next", 1), ("next2", 2)]:
        s = pd.DataFrame(index=origin.index)
        s["origem_ref"] = steps.step_ref
        s["linha_fonte"] = steps.linha_fonte
        s["offset"] = offset
        s["slot_ref"] = steps.step_ref + ":slot:" + str(offset)
        for name, suffix in mapping.items():
            field = prefix + "_" + suffix
            if field not in origin:
                dtype = "boolean" if name in {"error_like", "is_final"} else ("Float64" if name == "dur_s" else "Int64" if name in {"step", "tok_in", "tok_out", "tok_tot"} else TEXTO_DTYPE)
                s[name] = _unavailable(origin.index, dtype)
            elif name in {"error_like", "is_final"}:
                s[name] = _boolean(origin[field], field)
            elif name in {"step", "tok_in", "tok_out", "tok_tot", "dur_s"}:
                s[name] = _number(origin[field], field, name != "dur_s")
            else:
                s[name] = _text(origin[field])
            if name in {"code", "thought", "observations", "err_msg"}:
                s[name + "_estado"] = _estado_texto(origin, field, LIMITES_SLOT[prefix][name], False) \
                    if field in origin else pd.Series("nao_exportado", index=origin.index, dtype=TEXTO_DTYPE)
        has_number = s.step.notna()
        fields = [c for c in origin if c.startswith(prefix + "_") and c != prefix + "_step_number"]
        has_other = origin[fields].notna().any(axis=1)
        s["presenca"] = "nao_identificado_por_sql"
        s.loc[has_number, "presenca"] = "identificado_por_numero"
        s.loc[~has_number & has_other, "presenca"] = "numero_ausente_com_campos"
        if (has_number & s.error_like.isna()).any():
            raise ErroContrato("Vizinho numerado sem indicador error_like.")
        if (s.err_type.notna() & s.error_like.eq(False)).any():
            raise ErroContrato("Tipo de erro presente com vizinho declarado sem sinal.")
        if s[["tok_in", "tok_out", "tok_tot", "dur_s"]].lt(0).any().any():
            raise ErroContrato("Custo negativo em slot.")
        parts.append(s)
    return pd.concat(parts, ignore_index=True)


def _missing(v) -> bool:
    return bool(pd.isna(v))


def _compare_slot(slot: dict, anchor: dict, prefix: str) -> tuple[list[str], int, int]:
    conflicts, support, prefixes = [], 0, 0
    for field in ["step", "err_type", "tool_name", "tok_in", "tok_out", "tok_tot", "dur_s"]:
        if prefix == "prev" and field not in {"step", "err_type"}:
            continue
        a, b = slot[field], anchor[field]
        if _missing(a) != _missing(b):
            conflicts.append(field)
        elif not _missing(a):
            equal = math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-6) if field == "dur_s" else a == b
            if not equal:
                conflicts.append(field)
    for field in LIMITES_SLOT[prefix]:
        a, b = slot[field], anchor[field]
        if _missing(a) != _missing(b):
            conflicts.append(field)
        elif not _missing(a):
            if a == b:
                support += bool(a)
            elif len(a) == LIMITES_SLOT[prefix][field] and b.startswith(a):
                support += 1
                prefixes += 1
            else:
                conflicts.append(field)
    return conflicts, support, prefixes


LINK_COLUMNS = ["origem_ref", "alvo_ref", "linha_origem", "linha_alvo", "offset", "estado",
                "motivo", "apoios_textuais", "prefixos_explicados", "numero_nao_crescente", "mesma_chamada"]


def _vinculos_janelas(steps: pd.DataFrame, slots: pd.DataFrame) -> pd.DataFrame:
    source = steps.to_dict("records")
    slot_records = {(int(r["linha_fonte"]), int(r["offset"])): r for r in slots.to_dict("records")}
    links = []
    # O SQL legado omite agente na partição: qualquer colisão observada suspende
    # os vínculos desses IDs/papéis. Ausência de colisão no subset não prova global.
    collisions = steps.groupby(["exec_id", "role"], dropna=False).agente.nunique().gt(1)
    collision_keys = set(collisions[collisions].index)
    for (exec_id, agent, role), g in steps.sort_values(["exec_id", "agente", "role", "step_pos"]).groupby(
            ["exec_id", "agente", "role"], sort=False, dropna=False):
        ids = g.linha_fonte.astype(int).to_list()
        for i, j in zip(ids, ids[1:]):
            a, b = source[i], source[j]
            fwd, back = slot_records[(i, 1)], slot_records[(j, -1)]
            if fwd["error_like"] is not True or back["error_like"] is not True:
                continue
            conflicts1, supports1, caps1 = _compare_slot(fwd, b, "next")
            conflicts2, supports2, caps2 = _compare_slot(back, a, "prev")
            errors = ["next:" + v for v in conflicts1] + ["prev:" + v for v in conflicts2]
            no_number = _missing(fwd["step"]) or _missing(back["step"]) or _missing(a["step"]) or _missing(b["step"])
            nonincreasing = not _missing(a["step"]) and not _missing(b["step"]) and b["step"] <= a["step"]
            if (exec_id, role) in collision_keys:
                state, reason = "ambiguo", "particao_legada_pode_misturar_agentes"
            elif errors:
                state, reason = "conflito", ";".join(errors)
            elif no_number:
                state, reason = "ambiguo", "numeração_ausente"
            elif not supports1 + supports2:
                state, reason = "ambiguo", "sem_apoio_textual"
            elif nonincreasing:
                state, reason = "ambiguo", "numero_nao_crescente_conferir_chamada"
            else:
                state, reason = "compativel_candidato", "reciproco_com_prefixos_sql" if caps1 + caps2 else "reciproco_igual"
            links.append(dict(origem_ref=a["step_ref"], alvo_ref=b["step_ref"], linha_origem=i, linha_alvo=j,
                              offset=1, estado=state, motivo=reason, apoios_textuais=supports1 + supports2,
                              prefixos_explicados=caps1 + caps2, numero_nao_crescente=bool(nonincreasing),
                              mesma_chamada=pd.NA))
    return pd.DataFrame(links, columns=LINK_COLUMNS)


def _validar_censo(origin: pd.DataFrame, steps: pd.DataFrame) -> None:
    _required_values(steps, ["idx", "n_steps_role", "chamada_id"])
    declared = _boolean(origin.error_like, "error_like")
    if declared.isna().any() or not declared.eq(steps.error_like).all():
        raise ErroContrato("error_like declarado e fontes discordam.")
    if steps.chamada_id.lt(0).any():
        raise ErroContrato("Contador TaskStep negativo.")
    hashes = _text(origin.source_trace_sha256)
    if hashes.isna().any() or not hashes.str.fullmatch(r"[0-9a-fA-F]{64}").all():
        raise ErroContrato("Identificação do trace original inválida no censo.")
    for _, g in steps.sort_values(["exec_id", "agente", "role", "step_pos"]).groupby(
            ["exec_id", "agente", "role"], sort=False, dropna=False):
        if g.idx.to_list() != list(range(len(g))) or not g.n_steps_role.eq(len(g)).all():
            raise ErroContrato("Censo incompleto ou ordinais incompatíveis no grupo.")
        if g.chamada_id.diff().dropna().lt(0).any():
            raise ErroContrato("Contador TaskStep retrocede na ordem original.")
        ix = g.index
        raw = origin.loc[ix]
        if hashes.loc[ix].nunique() != 1:
            raise ErroContrato("Censo mistura snapshots no papel.")
        for field in ["n_task_steps_role", "n_planning_steps_role", "n_raw_steps_role", "n_actions_final_flag_unknown"]:
            v = _number(raw[field], field, True)
            if v.isna().any() or v.nunique() != 1 or v.lt(0).any():
                raise ErroContrato(f"Contagem inconsistente no grupo: {field}.")
        tasks = int(_number(raw.n_task_steps_role, "n_task_steps_role", True).iloc[0])
        planning = int(_number(raw.n_planning_steps_role, "n_planning_steps_role", True).iloc[0])
        total = int(_number(raw.n_raw_steps_role, "n_raw_steps_role", True).iloc[0])
        unknown = int(_number(raw.n_actions_final_flag_unknown, "n_actions_final_flag_unknown", True).iloc[0])
        if (g.chamada_id.gt(tasks).any() or total < len(g) + tasks + planning
                or total < int(g.step_pos.max()) or unknown != int(g.is_final.isna().sum())):
            raise ErroContrato("Contagens de classes/chamada/final inconsistentes.")
        has_final = _boolean(raw.role_has_final_step, "role_has_final_step")
        if has_final.isna().any() or not has_final.eq(bool(g.is_final.fillna(False).any())).all():
            raise ErroContrato("Flag final agregada incompatível com flags de n.")


def _vinculos_censo(steps: pd.DataFrame) -> pd.DataFrame:
    links = []
    for _, g in steps.sort_values(["exec_id", "agente", "role", "step_pos"]).groupby(
            ["exec_id", "agente", "role"], sort=False, dropna=False):
        records = g.to_dict("records")
        for a, b in zip(records, records[1:]):
            links.append(dict(origem_ref=a["step_ref"], alvo_ref=b["step_ref"], linha_origem=int(a["linha_fonte"]),
                              linha_alvo=int(b["linha_fonte"]), offset=1, estado="ordem_censo",
                              motivo="contagens_ordinais_consistentes_no_arquivo", apoios_textuais=0,
                              prefixos_explicados=0, numero_nao_crescente=(not _missing(a["step"]) and
                              not _missing(b["step"]) and b["step"] <= a["step"]),
                              mesma_chamada=bool(a["chamada_id"] == b["chamada_id"])))
    return pd.DataFrame(links, columns=LINK_COLUMNS)


def carregar_fonte(caminho: str | Path) -> BaseEstrutural:
    """Reusa o leitor existente; fingerprint do arquivo ancora as referências."""
    path = Path(caminho)
    cols = colunas_do_trace(path)
    detectar_contrato(cols)
    initial = path.stat()
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    result = adaptar(ler_trace(path), fonte_id=h.hexdigest())
    final = path.stat()
    if (initial.st_size, initial.st_mtime_ns) != (final.st_size, final.st_mtime_ns):
        raise ErroContrato("Fonte mudou durante a leitura.")
    result.fonte.update(sha256=h.hexdigest(), tamanho_bytes=initial.st_size)
    return result
