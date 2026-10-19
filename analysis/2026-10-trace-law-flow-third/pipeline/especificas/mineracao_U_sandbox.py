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
    memorias(perfil, tabelas, conf, dest, ids, encontro) -> list  passo 8: uma memória por parte da lição
                                          ({id, parte, memoria}, com os campos do esquema); `encontro` é a lista do
                                          passo 7 (medida, mineração, auditoria, igual)
    TABELAS                               as tabelas que `medir` devolve e o passo 4 grava

Emenda 4 do racional (19/10, decisão do Rafael): a lição tem quatro partes, cada uma com escopo e destino próprios
(`PARTES`); a parte de cada erro sai do tipo e do nome (`parte_de`).
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
TABELAS = ["erros_lidos", "inventario", "inventario_papel", "inventario_mes", "imports_autorizados", "partes"]

# emenda 4 (19/10): as partes da lição (racional, passo 8; decisoes.md, 19/10) — rótulo, escopo, destino
PARTES = {"C": ("módulo usado sem import", "global", "memória"),
          "B": ("ferramenta importada como módulo", "papel", "memória"),
          "D": ("import fora da lista autorizada", "papel", "memória"),
          "E": ("funções e atributos proibidos", "global", "em aberto")}   # em investigação: vem do prompt? (dossiê, §2c)
# o import de uma ferramenta: o framework e os nomes que o agente dá às ferramentas (racional, emenda 4)
FERRAMENTAS = {"smolagents", "mcp", "mcp_client", "tools", "tool_usage", "tool_functions", "python_interpreter"}


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


def parte_de(tipo, nome):
    """A parte da lição (C, B, D, E) pelo tipo e pelo nome; None para o sem_nome."""
    if tipo == "modulo_sem_import":
        return "C"
    if tipo in ("funcao_proibida", "atributo_dunder"):
        return "E"
    if tipo in ("import_bloqueado", "modulo_ausente"):
        raiz = str(nome).split(".")[0]
        return "B" if raiz in FERRAMENTAS or raiz.startswith("get_") else "D"
    return None


def memoria_id(parte, papel):
    """U_sandbox.C (parte global) ou U_sandbox.B.<papel> (parte por papel); None sem parte."""
    if not isinstance(parte, str):   # None (ou NaN, numa coluna do pandas)
        return None
    return f"U_sandbox.{parte}" + (f".{papel}" if PARTES[parte][1] == "papel" else "")


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
    L["parte"] = [parte_de(t, n) for t, n in zip(L.tipo, L.nome)]
    L["memoria_id"] = [memoria_id(p, r) for p, r in zip(L.parte, L.role)]
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
    P = L[L.parte.notna()]
    partes = (P.groupby(["memoria_id", "parte"]).agg(erros=("step_ref", "size"), execucoes=("exec_id", "nunique"),
                                                     papeis=("role", "nunique"), meses=("mes", "nunique"))
              .reset_index().sort_values(["parte", "erros"], ascending=[True, False]))
    return {"erros_lidos": L, "inventario": inv, "inventario_papel": por_papel, "inventario_mes": por_mes,
            "imports_autorizados": listas, "partes": partes}


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
    # racional, passo 6: o mesmo nome na mesma execução e papel (o tipo não entra: `json` sem import e depois
    # `json` bloqueado é o mesmo nome repetido)
    rep = N.duplicated(["exec_id", "role", "nome"], keep="first")
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
        "partes": {r.memoria_id: int(r.erros) for r in t["partes"].sort_values("memoria_id").itertuples(index=False)},
    }


def _lista_do_papel(L, papel):
    """A lista autorizada do papel: a do mês mais recente em que aparece (empate: a mais frequente)."""
    A = L[L.role.eq(papel) & L.lista_autorizada.notna()]
    if A.empty:
        return None
    ult = A[A.mes.eq(A.mes.max())]
    return ult.lista_autorizada.value_counts().sort_index().sort_values(ascending=False, kind="stable").index[0]


def _guia(parte, P, L, papel):
    """A correction_guidance da parte, montada da tabela, sem texto livre (racional, passo 8, emenda 4)."""
    nomes = lambda tipos: ", ".join(P[P.tipo.isin(tipos)].nome.value_counts().index)
    if parte == "C":
        return f"Importe antes de usar: {nomes(['modulo_sem_import'])}."
    if parte == "B":
        return ("As ferramentas já estão no escopo como funções: chame-as direto, sem import. "
                f"Não importe: {nomes(['import_bloqueado', 'modulo_ausente'])}.")
    if parte == "D":
        g = [f"{rot}: {nomes([tp])}" for rot, tp in (("Não importe", "import_bloqueado"),
                                                       ("Não existe no ambiente", "modulo_ausente")) if nomes([tp])]
        lista = _lista_do_papel(L, papel)
        return "; ".join(g + ([f"imports autorizados neste papel: {lista}"] if lista else [])) + "."
    g = [f"{rot}: {nomes([tp])}" for rot, tp in (("Não chame", "funcao_proibida"), ("Não acesse", "atributo_dunder"))
         if nomes([tp])]
    return "; ".join(g) + "."


def memorias(perfil, t, conf, dest, ids, encontro):
    """Uma memória por parte (emenda 4): C e E globais; B e D, uma por papel."""
    L = t["erros_lidos"]
    fecha = bool(conf["passa"] and encontro and all(e["igual"] for e in encontro))
    saida = []
    for r in t["partes"].sort_values(["parte", "memoria_id"]).itertuples(index=False):
        P = L[L.memoria_id.eq(r.memoria_id)]
        rotulo, escopo, destino_parte = PARTES[r.parte]
        papel = P.role.iloc[0] if escopo == "papel" else None
        if escopo == "papel":
            casos = P.sort_values(["mes", "step_ref"]).head(10)
        else:
            casos = P.sort_values(["role", "mes", "step_ref"]).drop_duplicates("role").head(10)
        location = {"total_erros": int(len(P)),
                    "casos": [{"exec_id": str(c.exec_id), "role": c.role, "mes": c.mes, "step_ref": c.step_ref,
                               "fonte_id": ids["fonte_id"], "rodada_id": ids["rodada_id"]}
                              for c in casos.itertuples(index=False)]}
        ev = []
        for nome in P.nome.value_counts().index[:3]:
            c = P[P.nome.eq(nome)].sort_values(["role", "mes", "step_ref"]).iloc[0]
            ev.append({"exec_id": str(c.exec_id), "role": c.role, "mes": c.mes, "step_ref": c.step_ref,
                       "tipo": c.tipo, "nome": c.nome})
        cont = P.nome.value_counts()
        desc = (f"{len(P)} erros em {P.role.nunique()} papel(éis), parte {r.parte} do inventário do sandbox ({rotulo}): "
                + ", ".join(f"{k} {int(v)}" for k, v in cont.items()) + ".")
        rep = P.sort_values(["exec_id", "agente", "role", "step_pos"]).duplicated(["exec_id", "role", "nome"], keep="first")
        A = P[P.lista_autorizada.notna()]
        mem = {
            "category": f"Inventário do sandbox · {rotulo} (factual · ambiente)",
            "scope": {"role": papel, "tool": None},
            "location": location,
            "evidence": ev,
            "description": desc,
            "correction_guidance": _guia(r.parte, P, L, papel),
            # na parte, ocorrências = erros (a ocorrência condicional é da unidade inteira, no perfil da rodada)
            "occurrences": {"erros": int(len(P)), "ocorrencias": int(len(P)), "execucoes": int(P.exec_id.nunique()),
                            "meses": sorted(P.mes.unique().tolist())},
            # racional, passo 8: derived-and-checked se a cobertura passa e o encontro (que inclui as partes) fecha
            "status": "derived-and-checked" if fecha else "parcial",
            "validation": {"parte": {"codigo": r.parte, "rotulo": rotulo, "escopo": escopo},
                           "cobertura": conf,
                           "encontro": {"medidas": len(encontro), "diferentes": sum(not e["igual"] for e in encontro),
                                        "com_a": "audit/scripts/audit_candidata_base3.py"},
                           "listas_autorizadas": [{"lista": k, "erros": int(v)} for k, v in
                                                  sorted(A.lista_autorizada.value_counts().items())],
                           "destino_numeros": {**dest, "erros_que_repetem_o_nome_na_parte": int(rep.sum())},
                           "destino": destino_parte,
                           "destino_decidido_em": "decisoes.md, 19/10" if destino_parte != "em aberto" else None},
            "impact": None,
        }
        saida.append({"id": r.memoria_id, "parte": r.parte, "memoria": mem})
    return saida
