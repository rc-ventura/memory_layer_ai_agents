"""Parte específica do inventário do sandbox (`U_sandbox`): a regra que lê o nome recusado na mensagem de erro.

Implementa o racional pré-registrado (`propostas/U_sandbox/racional.md`, passos 4, 5, 6 e 8). Não roda sozinho: o
`minerar.py` chama as funções abaixo na ordem dos passos (procedimento 06). Determinístico, sem LLM.

Interface que o `minerar.py` espera de todo script específico:
    LIMIAR_COBERTURA                      o limiar do passo 5 (o do racional)
    medir(casos, mensagens) -> tabelas    passo 4: as tabelas da lição; `casos` é o casos.csv do perfil da rodada,
                                          `mensagens` um DataFrame (step_ref, mensagem, estado)
    confianca(tabelas) -> dict            passo 5: {"medida", "valor", "limiar", "passa", ...}
    destino(tabelas) -> dict              passo 6: os números para a decisão memória × harness
    para_encontro(tabelas) -> dict        passo 7: as medidas no formato da auditoria independente
    memoria(perfil, tabelas, conf, dest, ids, encontro) -> dict   passo 8: os campos do esquema da memória;
                                          `encontro` é a lista do passo 7 (medida, mineração, auditoria, igual)
"""
import re

import pandas as pd

LIMIAR_COBERTURA = 0.95
REGRAS = [  # (tipo, padrão no último trecho da mensagem) — racional, passo 4, na ordem
    ("funcao_proibida", r"Forbidden function evaluation: '([^']+)'"),
    ("import_bloqueado", r"Import (?:of|from) ([\w.]+) is not allowed"),
    ("modulo_ausente", r"No module named '([^']+)'"),
    ("atributo_dunder", r"Forbidden access to dunder attribute: (\w+)"),
    ("modulo_sem_import", r"The variable `(\w+)` is not defined"),
]
AUTORIZADOS = re.compile(r"Authorized imports are: \[([^\]]*)\]")
ESTADOS_INTEGROS = {"sem_corte_sql"}  # o texto inteiro; "possivelmente_cortado" (v1, no teto) não conta


def ultimo_trecho(msg):
    return msg.rsplit("due to:", 1)[-1]


def extrair(msg):
    """(tipo, nome) da mensagem; ("sem_nome", primeira palavra do trecho) se nenhuma regra casa."""
    trecho = ultimo_trecho(msg)
    for tipo, rx in REGRAS:
        x = re.search(rx, trecho)
        if x:
            return tipo, x.group(1)
    t = trecho.strip()
    return "sem_nome", (t.split(":")[0].split()[0] if t else "")


def lista_autorizada(msg):
    a = AUTORIZADOS.search(ultimo_trecho(msg))
    if not a:
        return None
    return ", ".join(sorted(x.strip().strip("'\"") for x in a.group(1).split(",") if x.strip()))


def medir(casos, mensagens):
    m = casos.merge(mensagens, on="step_ref", how="left")
    lidos = []
    for r in m.itertuples(index=False):
        msg = r.mensagem if isinstance(r.mensagem, str) else ""
        integra = isinstance(r.estado, str) and r.estado in ESTADOS_INTEGROS
        tipo, nome = extrair(msg) if (msg and integra) else ("sem_nome", f"mensagem {r.estado}")
        lidos.append({"exec_id": r.exec_id, "agente": r.agente, "role": r.role, "step_pos": int(r.step_pos),
                      "step_ref": r.step_ref, "mes": r.mes, "tipo": tipo, "nome": nome,
                      "lista_autorizada": lista_autorizada(msg) if msg else None})
    L = pd.DataFrame(lidos, columns=["exec_id", "agente", "role", "step_pos", "step_ref", "mes", "tipo", "nome",
                                     "lista_autorizada"])
    N = L[L.tipo.ne("sem_nome")]
    inv = (N.groupby(["tipo", "nome"]).agg(erros=("step_ref", "size"), execucoes=("exec_id", "nunique"),
                                           papeis=("role", "nunique"), meses=("mes", "nunique"))
           .reset_index().sort_values(["erros", "tipo", "nome"], ascending=[False, True, True]))
    por_papel = N.groupby(["tipo", "nome", "role"]).size().rename("erros").reset_index()
    por_mes = N.groupby(["tipo", "nome", "mes"]).size().rename("erros").reset_index()
    A = L[L.lista_autorizada.notna()]
    listas = (A.groupby("lista_autorizada").agg(erros=("step_ref", "size"),
                                                 papeis=("role", lambda s: ", ".join(sorted(set(s)))),
                                                 meses=("mes", lambda s: ", ".join(sorted(set(s)))))
              .reset_index())
    return {"erros_lidos": L, "inventario": inv, "inventario_papel": por_papel, "inventario_mes": por_mes,
            "imports_autorizados": listas}


def confianca(t):
    L = t["erros_lidos"]
    com = int(L.tipo.ne("sem_nome").sum())
    valor = com / len(L) if len(L) else 0.0
    sem = L[L.tipo.eq("sem_nome")].nome.value_counts().to_dict()
    return {"medida": "cobertura", "com_nome": com, "erros": len(L), "valor": round(valor, 4),
            "limiar": LIMIAR_COBERTURA, "passa": bool(len(L)) and valor >= LIMIAR_COBERTURA,
            "sem_nome_por_tipo": {str(k): int(v) for k, v in sorted(sem.items())}}


def destino(t):
    L, listas = t["erros_lidos"], t["imports_autorizados"]
    N = L[L.tipo.ne("sem_nome")].sort_values(["exec_id", "agente", "role", "step_pos"])
    rep = N.duplicated(["exec_id", "role", "tipo", "nome"], keep="first")
    return {"listas_autorizadas_distintas": int(len(listas)),
            "lista_unica_em_todos_papeis_e_meses": bool(len(listas) == 1),
            "erros_que_repetem_o_nome_na_mesma_execucao_e_papel": int(rep.sum()),
            "execucoes_com_repeticao": int(N[rep].exec_id.nunique())}


def para_encontro(t):
    L = t["erros_lidos"]
    inv = t["inventario"]
    return {
        "populacao": {"erros": len(L), "execucoes": int(L.exec_id.nunique()), "papeis": int(L.role.nunique()),
                      "meses": int(L.mes.nunique()),
                      "erros_por_papel": {str(k): int(v) for k, v in sorted(L.role.value_counts().items())},
                      "chaves": sorted([str(r.exec_id), str(r.agente), str(r.role), int(r.step_pos)]
                                       for r in L.itertuples(index=False))},
        "cobertura": {"com_nome": int(L.tipo.ne("sem_nome").sum()), "erros": len(L)},
        "inventario": {f"{r.tipo}|{r.nome}": {"erros": int(r.erros), "execucoes": int(r.execucoes),
                                              "papeis": int(r.papeis), "meses": int(r.meses)}
                       for r in inv.sort_values(["tipo", "nome"]).itertuples(index=False)},
        "listas_autorizadas": {r.lista_autorizada: int(r.erros) for r in
                               t["imports_autorizados"].sort_values("lista_autorizada").itertuples(index=False)},
    }


def _nomes(inv, tipo):
    return ", ".join(inv.loc[inv.tipo.eq(tipo), "nome"])


def memoria(perfil, t, conf, dest, ids, encontro):
    L, inv, listas = t["erros_lidos"], t["inventario"], t["imports_autorizados"]
    primeiros = L.sort_values(["role", "mes", "step_ref"]).drop_duplicates("role").head(10)
    location = {"total_erros": int(perfil["erros_observaveis"]),
                "casos": [{"exec_id": str(r.exec_id), "role": r.role, "mes": r.mes, "step_ref": r.step_ref,
                           "fonte_id": ids["fonte_id"], "rodada_id": ids["rodada_id"]}
                          for r in primeiros.itertuples(index=False)]}
    tipos_top = L[L.tipo.ne("sem_nome")].tipo.value_counts().index[:3]
    ev = []
    for tp in tipos_top:
        r = L[L.tipo.eq(tp)].sort_values(["role", "mes", "step_ref"]).iloc[0]
        ev.append({"exec_id": str(r.exec_id), "role": r.role, "mes": r.mes, "step_ref": r.step_ref,
                   "tipo": tp, "nome": r.nome})
    partes = [("Não chame", "funcao_proibida"), ("Não importe", "import_bloqueado"),
              ("Importe antes de usar", "modulo_sem_import"), ("Não existe no ambiente", "modulo_ausente"),
              ("Não acesse", "atributo_dunder")]
    guia = [f"{rot}: {_nomes(inv, tp)}" for rot, tp in partes if _nomes(inv, tp)]
    if len(listas) == 1:
        guia.append(f"Imports autorizados: {listas.lista_autorizada.iloc[0]}")
    elif len(listas) > 1:
        for r in listas.itertuples(index=False):
            guia.append(f"Imports autorizados (papéis {r.papeis}): {r.lista_autorizada}")
    cont = L[L.tipo.ne("sem_nome")].tipo.value_counts()
    desc = (f"{len(L)} erros em {L.role.nunique()} papéis: o interpretador do sandbox recusou o código — "
            + ", ".join(f"{k} {int(v)}" for k, v in cont.items()) + ".")
    return {
        "category": "Inventário do sandbox (factual · ambiente)",
        "scope": {"role": None, "tool": None},
        "location": location,
        "evidence": ev,
        "description": desc,
        "correction_guidance": "; ".join(guia) + ".",
        "occurrences": {"erros": int(perfil["erros_observaveis"]),
                        "ocorrencias": int(perfil["ocorrencias_condicionais"]),
                        "execucoes": int(perfil["execucoes"]), "meses": sorted(L.mes.unique().tolist())},
        # racional, passo 8: derived-and-checked se a cobertura passa e o encontro fecha
        "status": "derived-and-checked" if conf["passa"] and encontro and all(e["igual"] for e in encontro) else "parcial",
        "validation": {"cobertura": conf,
                       "encontro": {"medidas": len(encontro), "diferentes": sum(not e["igual"] for e in encontro),
                                    "com_a": "audit/scripts/audit_candidata_base3.py"},
                       "listas_autorizadas": [{"lista": r.lista_autorizada, "erros": int(r.erros), "papeis": r.papeis,
                                               "meses": r.meses} for r in listas.itertuples(index=False)],
                       "destino_numeros": dest, "destino": "em aberto"},
        "impact": None,
    }
