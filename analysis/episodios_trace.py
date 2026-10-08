"""Componentes observadas de problemas; não taxonomia, triagem ou causalidade.

Separa consecutivos estruturados e consecutivos error_like. No modo janela,
usa somente vínculos candidatos compatíveis, marcados como tal. Não inventa
ActionStep ordinal nem same-call. Limites desconhecidos não são fins/inícios
provados. Não soma custos de slots ou deduplica vizinhos por texto.
"""
from dataclasses import dataclass
import hashlib

import pandas as pd

try:
    from .adaptador_trace import CENSO, JANELAS, ErroContrato
except ImportError:
    from adaptador_trace import CENSO, JANELAS, ErroContrato


@dataclass
class EpisodiosObservados:
    membros: pd.DataFrame
    episodios: pd.DataFrame
    cobertura: dict


def _known(value):
    return not pd.isna(value)


def _problem(record, definition):
    if definition == "estruturado":
        return _known(record["err_type"])
    v = record["error_like"]
    return bool(v) if _known(v) else None


def contexto_local(carga):
    """(step_ref, offset) -> slot/step normalizado, independente do idx legado."""
    if carga.contrato == JANELAS:
        return {(r["origem_ref"], int(r["offset"])): r for r in carga.slots.to_dict("records")}
    if carga.contrato != CENSO:
        raise ErroContrato("Episódios estruturais requerem janelas/censo, não substituem o caminho raw.")
    ctx = {}
    for _, g in carga.steps.sort_values(["exec_id", "agente", "role", "step_pos"]).groupby(
            ["exec_id", "agente", "role"], sort=False, dropna=False):
        seq = g.to_dict("records")
        for i, r in enumerate(seq):
            for offset in [-1, 1, 2]:
                j = i + offset
                ctx[(r["step_ref"], offset)] = {**seq[j], "presenca": "ordem_censo"} if 0 <= j < len(seq) \
                    else {"presenca": "limite_censo", "step_ref": None, "err_type": pd.NA, "error_like": pd.NA,
                          "is_final": pd.NA, "code": pd.NA, "observations": pd.NA, "step": pd.NA}
    return ctx


def _boundary(slot, definition, blocked=False):
    if blocked:
        return "aberto_vinculo_suspenso"
    if slot is None:
        return "aberto_contexto_ausente"
    if slot["presenca"] == "limite_censo":
        return "limite_censo"
    if slot["presenca"] not in {"identificado_por_numero", "ordem_censo"}:
        return "aberto_nao_identificado_sql"
    p = _problem(slot, definition)
    if p is None:
        return "aberto_indicador_ausente"
    return "aberto_problema_sem_vinculo" if p else "vizinho_fora_definicao"


def construir_episodios_observados(carga):
    """Um membro por n por definição. Componentes são condicionadas à extração.

    `componente_fechada_na_definicao` trata limites no papel, não confirma chamada
    contínua, recuperação semântica ou completa independência dos episódios.
    """
    if carga.contrato not in {JANELAS, CENSO}:
        raise ErroContrato("Contrato não suportado para episódios observados.")
    steps = carga.steps
    refs = steps.set_index("step_ref", drop=False).to_dict("index")
    indexed = steps.set_index("step_ref", drop=False)
    ctx = contexto_local(carga)
    good = set()
    suspended = set()
    for r in carga.vinculos.to_dict("records"):
        key = (r["origem_ref"], r["alvo_ref"])
        if r["estado"] in {"compativel_candidato", "ordem_censo"}:
            good.add(key)
        else:
            suspended.add(key)
    blocked_in = {b for a, b in suspended}
    blocked_out = {a for a, b in suspended}
    collisions = steps.groupby(["exec_id", "role"], dropna=False).agente.nunique()
    collision_keys = set(collisions[collisions.gt(1)].index) if carga.contrato == JANELAS else set()
    members, episodes = [], []
    for definition, field in [("estruturado", "structured_error"), ("misto", "error_like")]:
        sel = steps[steps[field].eq(True)]
        for (eid, agent, role), g in sel.sort_values(["exec_id", "agente", "role", "step_pos"]).groupby(
                ["exec_id", "agente", "role"], sort=False, dropna=False):
            components, active = [], []
            for ref in g.step_ref:
                if active and (active[-1], ref) not in good:
                    components.append(active)
                    active = []
                active.append(ref)
            if active:
                components.append(active)
            for component in components:
                first, last = refs[component[0]], refs[component[-1]]
                ep_ref = "ep:" + definition + ":" + hashlib.sha256(component[0].encode("utf-8")).hexdigest()
                collision = (eid, role) in collision_keys
                start = _boundary(ctx.get((component[0], -1)), definition,
                                  component[0] in blocked_in or collision)
                end = _boundary(ctx.get((component[-1], 1)), definition,
                                component[-1] in blocked_out or collision)
                closed = start in {"vizinho_fora_definicao", "limite_censo"} and end in {"vizinho_fora_definicao", "limite_censo"}
                known_call = carga.contrato == CENSO
                calls = {int(refs[r]["chamada_id"]) for r in component} if known_call else set()
                call_state = ("multiplos_contadores_taskstep" if len(calls) > 1 else "um_contador_taskstep") if known_call else "nao_observavel"
                next_slot = ctx.get((component[-1], 1))
                next_clean = (next_slot is not None and next_slot["presenca"] in {"identificado_por_numero", "ordem_censo"}
                              and _problem(next_slot, "misto") is False)
                # Registra sinal do próximo step apenas; não afirma corretude/mesma chamada.
                final_next = next_slot.get("is_final", pd.NA) if next_slot is not None else pd.NA
                frame = indexed.loc[component]
                episodes.append(dict(
                    episodio_ref=ep_ref, definicao=definition, exec_id=eid, agente=agent, role=role,
                    mes=first["mes"], n_ancoras=len(component), n_estruturados=int(frame.structured_error.sum()),
                    n_suspeitas=int(frame.observation_suspect.sum()), inicio=start, fim=end,
                    componente_fechada_na_definicao=closed, chamada=call_state,
                    situacao_vinculos="candidato_sem_trace" if carga.contrato == JANELAS else "ordem_censo_no_arquivo",
                    primeiro_step_pos=int(first["step_pos"]), ultimo_step_pos=int(last["step_pos"]),
                    tokens_n_conhecidos=frame.tok_tot.sum(min_count=1), tokens_n_ausentes=int(frame.tok_tot.isna().sum()),
                    dur_s_n_conhecida=frame.dur_s.sum(min_count=1), dur_s_n_ausente=int(frame.dur_s.isna().sum()),
                    proximo_sem_sinal_observado=next_clean,
                    proximo_is_final_observado=final_next,
                ))
                for order, ref in enumerate(component):
                    members.append(dict(step_ref=ref, episodio_ref=ep_ref, definicao=definition,
                                        ordem_local=order, inicio=start, fim=end,
                                        componente_fechada_na_definicao=closed, chamada=call_state))
    mcols = ["step_ref", "episodio_ref", "definicao", "ordem_local", "inicio", "fim", "componente_fechada_na_definicao", "chamada"]
    ecols = ["episodio_ref", "definicao", "exec_id", "agente", "role", "mes", "n_ancoras", "n_estruturados", "n_suspeitas",
             "inicio", "fim", "componente_fechada_na_definicao", "chamada", "situacao_vinculos", "primeiro_step_pos", "ultimo_step_pos",
             "tokens_n_conhecidos", "tokens_n_ausentes", "dur_s_n_conhecida", "dur_s_n_ausente",
             "proximo_sem_sinal_observado", "proximo_is_final_observado"]
    return EpisodiosObservados(pd.DataFrame(members, columns=mcols), pd.DataFrame(episodes, columns=ecols),
                               {"continuidade": "condicionada_vinculos_e_limites",
                                "recuperacao_semantica": "nao_medida", "triagem": "nao_habilitada"})
