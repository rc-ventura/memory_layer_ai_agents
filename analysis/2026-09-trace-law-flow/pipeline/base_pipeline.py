"""Base compartilhada das análises do trace cru da esteira jurídica.

Carrega o trace, explode a working memory em steps e classifica os erros por
causa-raiz — a espinha computacional que qualquer análise desta pasta consome.
Os notebooks importam daqui em vez de recopiar células de setup:

    from base_pipeline import *
    B = carregar_base()            # B.df, B.steps, B.RAW, B.execs, B.E, B.EU, B.S

Cada builder também pode ser chamado isolado (`carregar_trace`, `explodir_memoria`,
`classificar_erros`, `montar_unidades`, `medir_sucesso`) quando a análise só precisa
de parte do estado. A lógica é a mesma das células de §§1–3 do notebook de análise
genérica — mudança aqui muda os dois notebooks.
"""

import json, re, ast, builtins, unicodedata, os
import pandas as pd, numpy as np
from collections import Counter, defaultdict
from types import SimpleNamespace

__all__ = ["TRACE", "carregar_trace", "explodir_memoria", "classify", "classificar_erros",
           "linha_rejeitada", "e_texto", "submecanismo", "SUB2UNI", "FACT", "ESTR", "NAO", "SEM",
           "UNI", "montar_unidades", "MIN_EXECS", "MIN_MESES", "triagem",
           "DEGENERADO", "medir_sucesso", "carregar_base"]

TRACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                     "85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz")


def carregar_trace():
    df = pd.read_csv(TRACE, dtype=str)
    df["mes"] = pd.to_datetime(df["anomesdia"], format="%Y%m%d").dt.to_period("M").astype(str)
    return df


def explodir_memoria(df):
    rows, raw = [], []
    for _, r in df[df["txt_etap_memo"].notna()].iterrows():
        try: memo = json.loads(r["txt_etap_memo"])
        except Exception: continue
        for role, steps in memo.items():
            if not isinstance(steps, list): continue
            acts = [s for s in steps if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
            for i, st in enumerate(acts):
                tu, tm = st.get("token_usage") or {}, st.get("timing") or {}
                err = st.get("error") or {}
                rec = {"exec_id": r["cod_idef_exeo"], "agente": r["cod_idef_aget"], "mes": r["mes"],
                       "status": r["cod_idef_stat_exeo_aget"], "role": role,
                       "idx": i, "n_steps_role": len(acts), "step": st.get("step_number"),
                       "dur_s": tm.get("duration"), "tok_in": tu.get("input_tokens") or 0,
                       "tok_out": tu.get("output_tokens") or 0, "tok_tot": tu.get("total_tokens") or 0,
                       "err_type": err.get("type"), "err_msg": str(err.get("message") or ""),
                       "is_final": bool(st.get("is_final_answer"))}
                rows.append(rec)
                mim = st.get("model_input_messages")
                # system prompt = PRIMEIRA mensagem apenas. É onde as ferramentas são declaradas.
                # Ler o contexto inteiro contaminaria com as funções que o próprio agente define
                # ao longo da conversa (ver procedimento-validacao.md §1.6).
                sysp = ""
                if mim:
                    m0 = mim[0] if isinstance(mim[0], dict) else {}
                    c = m0.get("content")
                    sysp = c[0].get("text", "") if isinstance(c, list) and c and isinstance(c[0], dict) else str(c or "")
                raw.append({**rec, "code": st.get("code_action") or "",
                            "thought": str(st.get("model_output") or ""),
                            "sysprompt": sysp,
                            "ctx": json.dumps(mim, ensure_ascii=False) if mim else "",
                            # o payload de verdade, só nos steps finais (o resto não interessa e pesa memória) — usado pela §11.9 do notebook mineracao_unidades_n2_n10.ipynb
                            "out": st.get("action_output") if st.get("is_final_answer") else None})
    steps = pd.DataFrame(rows)
    RAW = raw   # com code/thought/ctx — usado nos detectores silenciosos

    execs = (steps.groupby("exec_id").agg(agente=("agente","first"), mes=("mes","first"),
             n_steps=("step","size"), n_err=("err_type", lambda s: s.notna().sum()),
             tok_tot=("tok_tot","sum"), dur_s=("dur_s","sum"), tem_final=("is_final","any")).reset_index())
    execs["com_erro"] = execs["n_err"] > 0
    return steps, RAW, execs


def classify(m):
    if 'Could not index' in m:      return ('Contrato de retorno da ferramenta','Falha ao indexar o retorno (Could not index)')
    if 'does not support multiple positional' in m: return ('Convenção de chamada de ferramenta','Argumento posicional onde só cabe nomeado')
    if 'unterminated' in m:         return ('Geração de código','String não fechada (relatório longo em literal)')
    if 'regex pattern' in m:        return ('Protocolo do harness','Resposta sem bloco de código [INATIVO desde dez/2025]')
    if 'IndentationError' in m:     return ('Geração de código','Indentação inválida')
    if 'leading zeros' in m:        return ('Geração de código','Data DD/MM interpolada como número')
    if 'forgot a comma' in m or 'never closed' in m or 'invalid decimal' in m:
                                    return ('Geração de código','Texto do documento colado em literal')
    if 'SyntaxError' in m:          return ('Geração de código','Sintaxe inválida')
    if 'is not defined' in m:
        v = re.search(r'variable `(\w+)`', m)
        if v and v.group(1) in {'json','pd','np','re','os','math','datetime'}:
            return ('Ambiente & sandbox','Módulo usado sem import')
        return ('Suposição sobre estado','Variável não definida')
    if 'has no attribute' in m:     return ('Contrato de retorno da ferramenta','Objeto sem o atributo esperado')
    if 'not allowed' in m or 'explicitly allowed' in m or 'is not permitted' in m:
                                    return ('Ambiente & sandbox','Função ou import bloqueado pelo sandbox')
    if 'ModuleNotFound' in m:       return ('Ambiente & sandbox','Módulo ausente no sandbox')
    if 'Forbidden' in m:            return ('Ambiente & sandbox','Operação proibida')
    if 'AgentGenerationError' in m or 'internally hosted' in m: return ('Infra / LLM upstream','Falha do LLM interno')
    if 'Error code: 422' in m or 'UnprocessableEntity' in m:   return ('Infra / LLM upstream','HTTP 422')
    if 'JSONDecode' in m:           return ('Contrato de retorno da ferramenta','Retorno não era JSON')
    if 'KeyError' in m:             return ('Contrato de retorno da ferramenta','Campo ausente no retorno')
    if 'TypeError' in m:            return ('Contrato de retorno da ferramenta','Tipo diferente do esperado')
    if 'ValueError' in m:           return ('Suposição sobre dados','Formato/valor inválido')
    if 'IndexError' in m:           return ('Contrato de retorno da ferramenta','Retorno vazio indexado')
    return ('Não classificado', 'Erro não classificado')


def classificar_erros(steps):
    E = steps[steps["err_type"].notna()].copy()
    E[["familia","assinatura"]] = E["err_msg"].apply(lambda m: pd.Series(classify(m)))
    return E


# Do sintoma ao mecanismo: submecanismo determinístico por erro, cascata e ocorrência
PT_STOP = {"de", "da", "do", "das", "dos", "a", "o", "as", "os", "e", "é", "que", "para", "com", "não", "nao",
           "em", "no", "na", "nos", "nas", "um", "uma", "se", "por", "ao", "aos", "ou", "mais", "seu", "sua",
           "pelo", "pela", "este", "esta", "isso", "deve", "vou", "foi", "como", "sem", "antes", "apenas",
           "somente", "nenhum", "nenhuma"}
LITERAL_INICIO = re.compile(r"^(final_answer\s*\(|\w+\s*\+?=\s*\(?\s*[frbuFRBU]*(\"\"\"|'''|\"|')"
                            r"|[\"'][^\"']*[\"']\s*:|\w+\(\s*task\s*=)")
MODULOS = {"json", "pd", "np", "re", "os", "math", "datetime"}


def linha_rejeitada(m):
    mm = re.search(r"due to: \w+\s*\n(.*?)\n\s*Error:", m, re.S)
    return re.sub(r"\s*\^\s*$", "", mm.group(1).split("\n")[0]).strip() if mm else ""


def e_texto(s):
    if re.match(r"^(\||#|\*\*|- |\d+[.)]\s)", s) or "`" in s:
        return True
    toks = re.findall(r"[A-Za-zÀ-ÿ]+", s.lower())
    return len(toks) >= 3 and sum(t in PT_STOP for t in toks) / len(toks) >= 0.15


def submecanismo(m):
    if "regex pattern" in m:
        return "harness_bloco_code"
    if "AgentGenerationError" in m or "internally hosted" in m or "Error code: 422" in m or "UnprocessableEntity" in m:
        return "infra_llm"
    if "Code parsing failed" in m or "SyntaxError" in m or "IndentationError" in m:
        l = linha_rejeitada(m)
        if re.search(r"truncad", l, re.I):
            return "repr_colado"
        if "unterminated" in m or "forgot a comma" in m or "never closed" in m or LITERAL_INICIO.match(l):
            return "texto_em_literal"
        if e_texto(l):
            return "texto_solto_no_codigo"
        return "pontual"
    if "does not support multiple positional" in m:
        return "argumento_posicional"
    if "Could not index" in m:
        if "string indices must be integers" in m:
            return "tipo_real_do_retorno"
        if re.search(r"KeyError: \d+\s*$", m) or "unhashable type: 'slice'" in m:
            return "dict_indexado_por_posicao"
        if "KeyError: '" in m or "are in the [columns]" in m:
            return "campo_inexistente_no_retorno"
        return "pontual"
    if "Object hashDocumento has no attribute" in m:
        return "dict_iterado_como_lista"
    if ("JSON object must be str" in m or "JSONDecode" in m or "multiply sequence by non-int" in m
            or "could not convert string to float" in m or "has no attribute" in m):
        return "tipo_real_do_retorno"
    if "object is not an iterator" in m:
        return "next_sobre_gerador"
    v = re.search(r"variable `(\w+)` is not defined", m)
    if v and v.group(1) in MODULOS:
        return "modulo_sem_import"
    f = re.search(r"Forbidden function evaluation: '(\w+)'", m)
    if f and not hasattr(builtins, f.group(1)):
        return "nome_nao_definido"
    if f or "Import of" in m or "ModuleNotFound" in m or "Forbidden" in m:
        return "inventario_sandbox"
    if v:
        return "nome_nao_definido"
    return "pontual"


SUB2UNI = {
    "dict_indexado_por_posicao": "U_contrato_dict", "dict_iterado_como_lista": "U_contrato_dict",
    "campo_inexistente_no_retorno": "U_campo_inexistente",
    "tipo_real_do_retorno": "U_tipo_retorno",
    "texto_em_literal": "U_texto_literal",
    "texto_solto_no_codigo": "U_texto_solto",
    "argumento_posicional": "U_arg_nomeado",
    "inventario_sandbox": "U_sandbox", "modulo_sem_import": "U_sandbox",
    "next_sobre_gerador": "U_next_gerador",
    "nome_de_step_que_falhou": "U_estado_perdido",
    "nome_nunca_definido": "U_nome_inventado",
    "repr_colado": "U_repr_colado",
    "infra_llm": "H_infra_llm",
    "harness_bloco_code": "H_bloco_code",
    "pontual": "X_pontual",
}
FACT, ESTR, NAO, SEM = "factual · ambiente", "experiencial · estratégia", "não-memória · harness/infra", "—"
UNI = {
    "U_contrato_dict": ("Retorno das ferramentas de documento é dict", FACT,
                        "Ferramentas de documento retornam {'result': [[...]]}: acessar r['result'][0] e iterar a lista interna; nunca r[0], nunca iterar o dict."),
    "U_campo_inexistente": ("Campo inexistente no retorno estruturado", FACT,
                            "Acessar só chaves observadas no retorno (ex.: o verificador de sigilo devolve vazamento_sigilo/justificativa — não existe quebra_sigilo); na dúvida, inspecionar r.keys()."),
    "U_tipo_retorno": ("Retorno pode chegar como string", ESTR,
                       "Antes de indexar por chave, fazer conta ou json.loads, checar se o retorno é str (JSON serializado ou texto de erro da ferramenta)."),
    "U_texto_literal": ("Texto longo nunca dentro de literal de string", ESTR,
                        "Montar relatório/documento em variáveis ou lista de partes e só então chamar final_answer; não colar markdown, tabela ou texto de documento entre aspas."),
    "U_texto_solto": ("Explicação nunca solta no bloco de código", ESTR,
                      "O bloco de código contém só Python; justificativa e texto ao usuário vão no pensamento ou dentro de final_answer(...)."),
    "U_arg_nomeado": ("Ferramentas só aceitam argumento nomeado", FACT,
                      "Chamar sempre f(arg=valor); nenhuma das ferramentas observadas aceita posicional."),
    "U_sandbox": ("Inventário do sandbox", FACT,
                  "repr/eval/globals/dir e imports fora da lista (ex.: ast) são proibidos; json/datetime exigem import explícito; openpyxl ausente — usar envia_excel_para_usuario."),
    "U_next_gerador": ("next() sobre expressão geradora falha no sandbox", FACT,
                       "Usar list comprehension com [0] (ou for + break) em vez de next(x for x in ...)."),
    "U_estado_perdido": ("Após step com erro, o que ele definiria não existe", ESTR,
                         "Se a observação anterior traz exceção, redefinir variáveis e funções auxiliares daquele step antes de usá-las."),
    "U_nome_inventado": ("Nome usado sem ter sido definido", ESTR,
                         "Usar só variáveis e funções definidas no próprio código; 'Observation' é rótulo do harness, não variável."),
    "U_repr_colado": ("Não colar retorno impresso de volta no código", ESTR,
                      "Referenciar a variável que guardou o retorno em vez de colar o print truncado dentro do código."),
    "H_infra_llm": ("Falha do LLM upstream — política de retry", NAO,
                    "AgentGenerationError/422: retry com backoff e circuit breaker por subagente."),
    "H_bloco_code": ("Protocolo do harness [INATIVO]", NAO,
                     "≥2 casos num mês, ou taxa > 1/1k steps, reabre o candidato (limiar = teto do IC95% do regime pós-incidente dez/2025)."),
    "X_pontual": ("Erros pontuais sem conteúdo único", SEM, "—"),
}


def montar_unidades(E):
    EU = E.copy().sort_values(["exec_id", "role", "idx"])
    EU["seguidor"] = EU.groupby(["exec_id", "role"])["idx"].shift().eq(EU["idx"] - 1)
    EU["cascata"] = (~EU["seguidor"]).cumsum()
    EU["submecanismo"] = EU["err_msg"].apply(submecanismo)
    sel = EU["submecanismo"].eq("nome_nao_definido")
    EU.loc[sel, "submecanismo"] = np.where(EU.loc[sel, "seguidor"], "nome_de_step_que_falhou", "nome_nunca_definido")
    EU["unidade"] = EU["submecanismo"].map(SUB2UNI)
    EU["ocorrencia"] = EU["cascata"].astype(str) + "|" + EU["unidade"]
    return EU


MIN_EXECS, MIN_MESES = 3, 2


def triagem(EU, min_execs=MIN_EXECS, min_meses=MIN_MESES):
    tri = []
    for u, g in EU.groupby("unidade"):
        nome, tipo, conteudo = UNI[u]
        o = g.drop_duplicates("ocorrencia")
        execs_u, meses_u = o["exec_id"].nunique(), o["mes"].nunique()
        if tipo == NAO:
            decisao = "não-memória"
        elif tipo == SEM:
            decisao = "fora: sem conteúdo único"
        elif execs_u < min_execs or meses_u < min_meses:
            decisao = "fora: sem recorrência"
        else:
            decisao = "candidato"
        tri.append({"unidade": u, "nome": nome, "tipo": tipo, "decisão": decisao,
                    "ocorrências": len(o), "erros": len(g), "reincidências na cascata": len(g) - len(o),
                    "execuções": execs_u, "meses": meses_u, "papéis": o["role"].nunique(),
                    "tokens": int(g["tok_tot"].sum()),
                    "% ocorr. após outro erro": round(o["seguidor"].mean() * 100),
                    "assinaturas de origem": " + ".join(g["assinatura"].value_counts().index),
                    "conteúdo proposto": conteudo})
    ordem = {"candidato": 0, "não-memória": 1, "fora: sem recorrência": 2, "fora: sem conteúdo único": 3}
    t = pd.DataFrame(tri)
    return t.assign(_o=t["decisão"].map(ordem)).sort_values(["_o", "tokens"], ascending=[True, False]).drop(columns="_o")


DEGENERADO = re.compile(r"n[ãa]o encontrad[oa] na base|informa[çc][ãa]o insuficiente", re.I)


def medir_sucesso(df):
    linhas = []
    for _, r in df[df["txt_etap_memo"].notna()].iterrows():
        try: memo = json.loads(r["txt_etap_memo"])
        except Exception: continue
        outcome_txt, outcome_end, mgr_txt, mgr_end = None, -1, None, -1
        errs, tok_soma = [], 0
        for role, passos in memo.items():
            if not isinstance(passos, list): continue
            for st in passos:
                if not isinstance(st, dict) or st.get("__class__") != "ActionStep": continue
                tok_soma += (st.get("token_usage") or {}).get("total_tokens") or 0
                e = st.get("error") or {}
                if e: errs.append(str(e.get("message", "")))
                if st.get("is_final_answer"):
                    end = (st.get("timing") or {}).get("end_time") or 0
                    txt = str(st.get("action_output") or "")
                    if role == "managerAgent" and end > mgr_end: mgr_txt, mgr_end = txt, end
                    if end > outcome_end: outcome_txt, outcome_end = txt, end
        final_txt = mgr_txt if mgr_txt is not None else outcome_txt
        if final_txt is None: continue
        degenerado = bool(DEGENERADO.search(final_txt)) or len(final_txt.strip()) < 15
        linhas.append({"exec_id": r["cod_idef_exeo"], "sucesso": not degenerado,
                        "com_erro": len(errs) > 0,
                        "assinaturas": [classify(m)[1] for m in errs], "tok_tot": tok_soma})

    S = pd.DataFrame(linhas)
    return S


def carregar_base():
    df = carregar_trace()
    steps, RAW, execs = explodir_memoria(df)
    E = classificar_erros(steps)
    EU = montar_unidades(E)
    S = medir_sucesso(df)
    return SimpleNamespace(df=df, steps=steps, RAW=RAW, execs=execs, E=E, EU=EU, S=S)
