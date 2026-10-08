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

import json, re, ast, builtins, unicodedata, os, sys
import pandas as pd, numpy as np
from collections import Counter, defaultdict
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from leitor_trace import ler_trace   # analysis/leitor_trace.py — CSV (.csv/.xz/.gz) ou um único parquet (plano §4.10)
from leitor_trace import colunas_do_trace
from adaptador_trace import adaptar, carregar_fonte, detectar_contrato, TRACE_COMPLETO, CENSO
from episodios_trace import construir_episodios_observados, contexto_local

# Texto do pandas guardado em Python, não em arrow. Com o pyarrow instalado (para o parquet), o pandas 3 passaria a guardar
# todo `dtype=str` em arrow, e as regex de `.str.contains/extract/replace` rodariam no RE2 do arrow, não no `re`: `\s`
# deixa de casar o espaço não separável, lookahead não compila. O código foi escrito e auditado com o `re` do Python.
pd.set_option("mode.string_storage", "python")

__all__ = ["TRACE", "ler_trace", "carregar_trace", "explodir_memoria", "classify", "classificar_erros",
           "linha_do_codigo", "PAR_CHAVE_TEXTO", "sinais_de_parsing", "linha_rejeitada", "e_texto", "submecanismo", "SUB2UNI", "FACT", "ESTR", "NAO", "SEM",
           "UNI", "montar_unidades", "MIN_EXECS", "MIN_MESES", "triagem", "mascarar", "padrao_residuo",
           "residuo_por_padrao", "REVISAR_PRIORIDADE", "REVISAR_BAIXA", "ALARME_COBERTURA",
           "BASE_ID", "DESTINO_MINERACAO", "SINAL_HARNESS", "destino_mineracao", "CRIT", "INVESTIGAR_CRITICO",
           "caminho_dos_criticos", "sobreposicao", "M1_LIMIAR", "RESTO_LIMIAR", "FERRAMENTA_FINAL", "FALHA_FERRAMENTA", "falhas_silenciosas", "mascarar_motivo", "MOTIVO_REGRAS",
           "GRUPOS_FALHA_REAL", "motivo_da_falha", "DONO_DO_GRUPO", "UNIDADES_CONTRATO", "forma_argumento",
           "formas_das_falhas", "erro_depois_da_falha", "contrato_precedido", "sucesso_falso_candidato",
           "REGRAS_INVISIVEL", "unidade_silenciosa", "ocorrencias_visiveis", "ocorrencias_silenciosas","chama_ferramenta_declarada", "final_answer_sem_laco", "tem_laco", "SEM_NOME",
           "categoria_do_erro", "triagem_por_papel",
           "DEGENERADO", "medir_sucesso", "carregar_base", "carregar_carga",
           "exigir_analise_integrada", "AnaliseNaoIntegrada", "TRACE_COMPLETO",
           "analisar_sintomas", "classificar_sintomas_elegiveis", "analisar_mecanismos_observaveis",
           "carregar_mineracao_observada"]

TRACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                     "base_erros_minerados_full.parquet")
# qual base é esta: "base1" aqui, "base2" na pasta -second, "base3" na -third. Junto com o TRACE, é o que se ajusta ao
# copiar o pipeline para uma base nova — a decisão da mineração (DESTINO_MINERACAO) só vale na base em que foi tomada.
BASE_ID = "base3"


class AnaliseNaoIntegrada(RuntimeError):
    """Carga disponível, mas consumidor analítico ainda não adaptado nesta etapa."""


def exigir_analise_integrada(objeto, etapa="análise"):
    """Bloqueia regras antigas em dados parciais; não altera a taxonomia.

    Steps/df adaptados carregam um marcador nos attrs. Não inferir que o
    conteúdo é trace completo apenas porque os nomes internos foram mapeados.
    """
    contrato = getattr(objeto, "contrato", None)
    if isinstance(objeto, pd.DataFrame):
        contrato = objeto.attrs.get("contrato_carga")
        if contrato is None and {"error_source", "step_pos", "papel"} <= set(objeto.columns):
            contrato = detectar_contrato(objeto)
    if contrato is not None and contrato != TRACE_COMPLETO:
        raise AnaliseNaoIntegrada(
            f"Carga estrutural integrada ({contrato}); {etapa} ainda não integrada. "
            "Nesta etapa execute somente a carga e seu resumo. Não usar idx, "
            "contexto, totais ou regras de trace completo como se estivessem disponíveis."
        )


def _identificar_df(estrutura):
    """Somente metadados pequenos nos attrs: não guardar payload/estado global."""
    df = estrutura.origem.copy()
    df.attrs["contrato_carga"] = estrutura.contrato
    df.attrs["fonte_carga_id"] = estrutura.fonte["id"]
    return df


def carregar_trace(caminho=None):
    caminho = TRACE if caminho is None else caminho
    contrato = detectar_contrato(colunas_do_trace(caminho))
    if contrato != TRACE_COMPLETO:
        return _identificar_df(carregar_fonte(caminho))
    df = ler_trace(caminho)
    # `mes` = mês em que a execução RODOU (dat_hor_inio_exeo). `anomesdia` não serve para isso: é a data de corte
    # do lote (1 valor por mês, sempre posterior ao início — mediana 46 dias, até 230), e só bate com o mês real
    # em 36% das execuções com memória. Evidência: `drill_down.py relogios`; método: 03-procedimento-validacao.md.
    df["mes_exec"] = pd.to_datetime(df["dat_hor_inio_exeo"]).dt.to_period("M").astype(str)
    # anomesdia é AAAAMMDD no CSV; num parquet com a coluna tipada como data, o leitor entrega AAAA-MM-DD
    df["mes_particao"] = pd.to_datetime(df["anomesdia"].str.replace("-", "", regex=False), format="%Y%m%d").dt.to_period("M").astype(str)
    df["mes"] = df["mes_exec"]
    return df


def _execucoes_observadas(steps):
    """Custos apenas de n, nunca das janelas; nenhuma população total implícita."""
    group = steps.groupby(["exec_id", "agente"], dropna=False, sort=False)
    out = group.agg(
        mes=("mes", "first"), mes_particao=("mes_particao", "first"),
        n_steps_observados=("step_ref", "size"),
        n_erros_estruturados_observados=("structured_error", "sum"),
        n_suspeitas_observadas=("observation_suspect", "sum"),
        n_custos_tokens_ausentes=("tok_tot", lambda s: int(s.isna().sum())),
        n_custos_duracao_ausentes=("dur_s", lambda s: int(s.isna().sum())),
        tok_n_observados=("tok_tot", lambda s: s.sum(min_count=1)),
        dur_n_observados=("dur_s", lambda s: s.sum(min_count=1)),
    ).reset_index()
    # Colunas legadas explicitamente desconhecidas: evita chamar soma parcial de
    # orçamento total, ou identificar ausência de flag final como fracasso.
    for field, dtype in [("n_steps", "Int64"), ("tok_tot", "Int64"), ("dur_s", "Float64"), ("tem_final", "boolean")]:
        out[field] = pd.Series(pd.NA, index=out.index, dtype=dtype)
    return out


def _estado_estrutural(estrutura):
    df = _identificar_df(estrutura)
    steps = estrutura.steps.copy()
    steps.attrs["contrato_carga"] = estrutura.contrato
    steps.attrs["fonte_carga_id"] = estrutura.fonte["id"]
    execs = _execucoes_observadas(steps)
    execs.attrs.update(steps.attrs)
    return SimpleNamespace(
        df=df, steps=steps, RAW=steps.to_dict("records"), execs=execs,
        E=None, EU=None, S=None, estrutura=estrutura, contrato=estrutura.contrato,
        fonte=estrutura.fonte, slots=estrutura.slots, vinculos=estrutura.vinculos,
        cobertura={**estrutura.cobertura, "classificacao": "ainda_nao_integrada",
                   "episodios": "ainda_nao_integrados", "comparativos_globais": "bloqueados_ate_complemento_validado"},
        resumo=estrutura.resumo(), status_analise="somente_carga",
    )


def carregar_carga(caminho=None):
    """Fachada de carga sem executar classificadores ou medir sucesso.

    Não busca/concatena automaticamente complemento A ou censo B. União e
    validação de snapshot/população pertencem a uma etapa posterior aprovada.
    """
    caminho = TRACE if caminho is None else caminho
    contrato = detectar_contrato(colunas_do_trace(caminho))
    if contrato != TRACE_COMPLETO:
        carga = _estado_estrutural(carregar_fonte(caminho))
        carga.fonte["caminho_local"] = os.path.abspath(caminho)
        return carga
    df = carregar_trace(caminho)
    steps, RAW, execs = explodir_memoria(df)
    return SimpleNamespace(
        df=df, steps=steps, RAW=RAW, execs=execs, E=None, EU=None, S=None,
        estrutura=None, contrato=TRACE_COMPLETO, fonte={"formato": df.attrs.get("formato", {})},
        slots=None, vinculos=None, cobertura={"classificacao": "caminho_existente_trace_completo"},
        resumo={"contrato": TRACE_COMPLETO, "registros_fonte": len(df), "registros_n": len(steps),
                "execucoes_representadas": len(execs)}, status_analise="somente_carga",
    )


def explodir_memoria(df):
    if detectar_contrato(df) != TRACE_COMPLETO:
        fonte_id = df.attrs.get("fonte_carga_id")
        if not fonte_id:
            raise AnaliseNaoIntegrada("Use carregar_trace() ou carregar_carga() para identificar a fonte antes de adaptar.")
        carga = _estado_estrutural(adaptar(df, fonte_id=fonte_id))
        return carga.steps, carga.RAW, carga.execs
    rows, raw = [], []
    for _, r in df[df["txt_etap_memo"].notna()].iterrows():
        try: memo = json.loads(r["txt_etap_memo"])
        except Exception: continue
        for role, steps in memo.items():
            if not isinstance(steps, list): continue
            acts = [s for s in steps if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
            obs_ant = ""   # observações dos steps anteriores deste papel — só para sinais_de_parsing(), não sai daqui
            for i, st in enumerate(acts):
                tu, tm = st.get("token_usage") or {}, st.get("timing") or {}
                err = st.get("error") or {}
                mim = st.get("model_input_messages")
                # system prompt = PRIMEIRA mensagem apenas. É onde as ferramentas são declaradas.
                # Ler o contexto inteiro contaminaria com as funções que o próprio agente define
                # ao longo da conversa (ver procedimento-validacao.md §1.6).
                sysp = ""
                if mim:
                    m0 = mim[0] if isinstance(mim[0], dict) else {}
                    c = m0.get("content")
                    sysp = c[0].get("text", "") if isinstance(c, list) and c and isinstance(c[0], dict) else str(c or "")
                rec = {"exec_id": r["cod_idef_exeo"], "agente": r["cod_idef_aget"], "mes": r["mes"],
                       "mes_particao": r["mes_particao"], "status": r["cod_idef_stat_exeo_aget"], "role": role,
                       "idx": i, "n_steps_role": len(acts), "step": st.get("step_number"),
                       "dur_s": tm.get("duration"), "tok_in": tu.get("input_tokens") or 0,
                       "tok_out": tu.get("output_tokens") or 0, "tok_tot": tu.get("total_tokens") or 0,
                       "err_type": err.get("type"), "err_msg": str(err.get("message") or ""),
                       **sinais_de_parsing(str(err.get("message") or ""), st.get("code_action"), obs_ant),
                       "chama_ferramenta": chama_ferramenta_declarada(str(err.get("message") or ""),
                                                                      st.get("code_action"), sysp),
                       "final_answer_sem_laco": final_answer_sem_laco(str(err.get("message") or ""),
                                                                      st.get("code_action")),
                       "is_final": bool(st.get("is_final_answer"))}
                rows.append(rec)
                obs_ant += str(st.get("observations") or "")
                raw.append({**rec, "code": st.get("code_action") or "",
                            "thought": str(st.get("model_output") or ""),
                            "sysprompt": sysp,
                            "ctx": json.dumps(mim, ensure_ascii=False) if mim else "",
                            # o payload de verdade, só nos steps finais (o resto não interessa e pesa memória) — usado pela §11.9 do notebook mineracao_unidades_n2_n10.ipynb
                            "out": st.get("action_output") if st.get("is_final_answer") else None})
    steps = pd.DataFrame(rows)
    RAW = raw   # com code/thought/ctx — usado nos detectores silenciosos

    execs = (steps.groupby("exec_id").agg(agente=("agente","first"), mes=("mes","first"), mes_particao=("mes_particao","first"),
             n_steps=("step","size"), n_err=("err_type", lambda s: s.notna().sum()),
             tok_tot=("tok_tot","sum"), dur_s=("dur_s","sum"), tem_final=("is_final","any")).reset_index())
    execs["com_erro"] = execs["n_err"] > 0
    return steps, RAW, execs


def classify(m):
    # limite de tempo do wrapper de ferramentas da esteira (mensagem em português): falha da plataforma, não do agente
    if 'excedeu o timeout' in m or 'TimeoutError' in m: return ('Infra / ferramenta','Ferramenta excedeu o timeout')
    # limite de tempo do sandbox para o bloco inteiro (30 s): o sintoma é do sandbox; a causa (ferramenta lenta ×
    # código lento do agente) se separa no submecanismo()
    if 'exceeded the maximum execution time' in m:
        return ('Ambiente & sandbox','Bloco de código excedeu o tempo do interpretador')
    # o agente esgotou os passos sem resposta: desfecho de uma cascata, não causa (Ajuste 8); família própria, não
    # protocolo do harness (Ajuste 10)
    if 'Reached max steps' in m or 'AgentMaxStepsError' in m:
        return ('Erro crítico','Limite de passos atingido')
    if 'Could not index' in m:      return ('Contrato de retorno da ferramenta','Falha ao indexar o retorno (Could not index)')
    if 'does not support multiple positional' in m: return ('Convenção de chamada de ferramenta','Argumento posicional onde só cabe nomeado')
    if 'unterminated' in m:         return ('Geração de código','String não fechada (relatório longo em literal)')
    if 'regex pattern' in m:        return ('Protocolo do harness','Resposta sem bloco de código (harness)')
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
    return ('Sintoma não reconhecido', 'Sintoma não reconhecido')  # nenhuma regra de sintoma casou: erro novo para a taxonomia


def classificar_erros(steps):
    exigir_analise_integrada(steps, "classificação dos erros")
    E = steps[steps["err_type"].notna()].copy()
    E[["familia","assinatura"]] = E["err_msg"].apply(lambda m: pd.Series(classify(m)))
    return E


def classificar_sintomas_elegiveis(steps):
    """Reusa classify SOMENTE na projeção integral elegível; não cria mecanismos.

    Conservar todos os erros estruturados em E, mesmo quando não classificáveis.
    Falta de evidência textual é status de cobertura, não resíduo da taxonomia.
    Não usa observações, pensamento ou tipo como substituto da mensagem.
    """
    if steps.attrs.get("contrato_carga") is None and "err_msg_estado" in steps:
        raise AnaliseNaoIntegrada("Steps estruturais sem proveniência de carga; não tratar como trace completo.")
    if steps.attrs.get("contrato_carga") is None or steps.attrs["contrato_carga"] == TRACE_COMPLETO:
        exigir_analise_integrada(steps, "sintomas")
        E = classificar_erros(steps)
        E["classificacao_sintoma"] = "classificado"
        E["sintoma_elegivel"] = True
        return E
    requeridas = {"structured_error", "err_type", "err_msg", "err_msg_estado", "step_ref"}
    if not requeridas <= set(steps.columns):
        raise AnaliseNaoIntegrada("Sintomas requerem steps normalizados e disponibilidade da mensagem.")
    E = steps[steps.structured_error.eq(True)].copy()
    if E.err_type.isna().any() or E.step_ref.duplicated().any():
        raise AnaliseNaoIntegrada("Tipo ou unicidade de erros estruturados incompatível.")
    elegiveis = E.err_msg.notna() & E.err_msg_estado.eq("sem_corte_sql")
    E["familia"] = pd.Series(pd.NA, index=E.index, dtype=pd.StringDtype(storage="python"))
    E["assinatura"] = pd.Series(pd.NA, index=E.index, dtype=pd.StringDtype(storage="python"))
    E["classificacao_sintoma"] = "mensagem_indisponivel"
    E.loc[E.err_msg_estado.isin(["possivelmente_cortado", "cortado"]), "classificacao_sintoma"] = "mensagem_limitada"
    E.loc[elegiveis, "classificacao_sintoma"] = "classificado"
    E["sintoma_elegivel"] = elegiveis
    # A primeira regra que casa define o sintoma; texto limitado não é preenchido.
    for index, message in E.loc[elegiveis, "err_msg"].items():
        E.loc[index, ["familia", "assinatura"]] = classify(message)
    E.attrs["analise_integrada"] = "sintomas_elegiveis_sem_mecanismos"
    return E


def _resumo_grupos_erros(E, chaves):
    """Somas dos custos conhecidos, com n de custos ausentes; não imputa zeros."""
    out = E.groupby(chaves, dropna=False, sort=True).agg(
        erros=("err_type", "size"), execucoes=("exec_id", "nunique"),
        tokens_n_conhecidos=("tok_tot", lambda s: s.sum(min_count=1)),
        tokens_n_ausentes=("tok_tot", lambda s: int(s.isna().sum())),
        dur_s_n_conhecida=("dur_s", lambda s: s.sum(min_count=1)),
        dur_s_n_ausente=("dur_s", lambda s: int(s.isna().sum())),
        mediana_tokens_n=("tok_tot", "median"), mediana_dur_s_n=("dur_s", "median"),
    ).reset_index()
    # Percentuais de custo só quando não há nenhum custo desconhecido no universo.
    denom = E.tok_tot.sum(min_count=1)
    out["pct_tokens_universo_tabela"] = pd.Series(pd.NA, index=out.index, dtype="Float64")
    if E.tok_tot.notna().all() and pd.notna(denom) and denom > 0:
        out["pct_tokens_universo_tabela"] = out.tokens_n_conhecidos.div(denom).mul(100).astype("Float64")
    return out


def analisar_sintomas(carga):
    """Análise explicitamente parcial: sintomas elegíveis + custos de todos erros.

    O objeto de carga não é mutado. Não chama montar_unidades/medir_sucesso nem
    habilita comparativos globais, até mesmo com uma fixture de censo B.
    """
    E = classificar_sintomas_elegiveis(carga.steps)
    Ee = E[E.sintoma_elegivel].copy()
    tabelas = {
        "cobertura_sintomas": _resumo_grupos_erros(E, ["classificacao_sintoma"]),
        "familias": _resumo_grupos_erros(Ee, ["familia"]),
        "assinaturas": _resumo_grupos_erros(Ee, ["familia", "assinatura"]),
        "papeis": _resumo_grupos_erros(E, ["role", "classificacao_sintoma"]),
        "duracoes_assinaturas": _resumo_grupos_erros(Ee, ["assinatura"]),
        "custos_assinaturas": _resumo_grupos_erros(Ee, ["familia", "assinatura"]),
        "custos_por_situacao": _resumo_grupos_erros(E, ["classificacao_sintoma"]),
    }
    for name in ["familias", "assinaturas"]:
        table = tabelas[name]
        table["pct_erros_elegiveis"] = table.erros.div(len(Ee)).mul(100) if len(Ee) else pd.NA
        table["pct_erros_estruturados"] = table.erros.div(len(E)).mul(100) if len(E) else pd.NA
    cats = []
    for message in Ee.loc[Ee.err_msg.str.contains("TypeError", na=False), "err_msg"]:
        if "unexpected keyword argument" in message:
            cats.append("IAN – argumento nomeado inexistente")
        elif "required positional argument" in message:
            cats.append("IAV – argumento obrigatório omitido")
        elif "not subscriptable" in message or "not iterable" in message:
            cats.append("Contrato de retorno (não indexável)")
        else:
            cats.append("Outro TypeError")
    tabelas["typeerror"] = pd.Series(cats, dtype="str").value_counts().rename_axis("categoria").reset_index(name="erros")
    resumo = {
        "contrato": carga.contrato, "erros_estruturados": len(E), "sintomas_elegiveis": len(Ee),
        "mensagem_limitada": int(E.classificacao_sintoma.eq("mensagem_limitada").sum()),
        "mensagem_indisponivel": int(E.classificacao_sintoma.eq("mensagem_indisponivel").sum()),
        "sintomas_nao_reconhecidos_elegiveis": int(Ee.familia.eq("Sintoma não reconhecido").sum()),
        "suspeitas_fora_taxonomia": int(carga.steps["observation_suspect"].sum()) if "observation_suspect" in carga.steps else None,
        "tokens_erro_ausentes": int(E.tok_tot.isna().sum()),
        "duracao_erro_ausente": int(E.dur_s.isna().sum()),
        "universo_custos": "n de todos os erros estruturados observados; não orçamento da população",
        "universo_sintomas": "mensagens elegíveis sem corte SQL; não prova de mecanismo/causa",
    }
    return SimpleNamespace(E=E, Ee=Ee, tabelas=tabelas, resumo=resumo,
                           EU=None, S=None, cobertura={**carga.cobertura,
                           "sintomas": "integrados_por_elegibilidade",
                           "custos_erros": "integrados_com_missing_explicito",
                           "mecanismos": "ainda_nao_integrados"})


# Do sintoma ao mecanismo: submecanismo determinístico por erro, cascata e ocorrência
PT_STOP = {"de", "da", "do", "das", "dos", "a", "o", "as", "os", "e", "é", "que", "para", "com", "não", "nao",
           "em", "no", "na", "nos", "nas", "um", "uma", "se", "por", "ao", "aos", "ou", "mais", "seu", "sua",
           "pelo", "pela", "este", "esta", "isso", "deve", "vou", "foi", "como", "sem", "antes", "apenas",
           "somente", "nenhum", "nenhuma"}
LITERAL_INICIO = re.compile(r"^(final_answer\s*\(|\w+\s*\+?=\s*\(?\s*[frbuFRBU]*(\"\"\"|'''|\"|')"
                            r"|[\"'][^\"']*[\"']\s*:|\w+\(\s*task\s*=)")
MODULOS = {"json", "pd", "np", "re", "os", "math", "datetime"}


def linha_do_codigo(m, code):
    """A linha N do code_action, quando a mensagem de parsing é do formato novo (`... on line N due to: SyntaxError:
    <motivo>`, numa linha só e sem o código — RoteadorCivel desde jun/2026, nas duas bases). No formato antigo a
    mensagem já traz a linha e isto devolve "". Conferido na base 1: nos 222 erros do formato antigo, a linha N do
    code_action é a linha que a mensagem traz em 221 (a exceção é uma f-string de várias linhas, em que o parser
    aponta o início e N o fim)."""
    n = re.search(r"on line (\d+) due to: \w+", m)
    if not n or not code or re.search(r"due to: \w+\s*\n(.*?)\n\s*Error:", m, re.S):
        return ""
    linhas = str(code).splitlines()
    k = int(n.group(1)) - 1
    return linhas[k].strip() if 0 <= k < len(linhas) else ""


# par "chave": "texto" — valor é texto fixo, não expressão: o formato de um retorno de ferramenta impresso
PAR_CHAVE_TEXTO = re.compile(r"[\"']([^\"'\n]{1,60})[\"']\s*:\s*[\"']")


def sinais_de_parsing(m, code, obs_ant):
    """Os sinais que o submecanismo() precisa num erro de parsing e que a mensagem sozinha não dá — só números e a
    linha, nunca o texto das observações:
    - `linha_codigo_erro`: a linha rejeitada no formato novo (`linha_do_codigo`);
    - `chaves_vistas_antes`: quantas chaves distintas dos pares "chave": "texto" da linha rejeitada já apareceram
      impressas como chave ('chave':) numa observação anterior do mesmo papel — o retorno colado vem de lá;
    - `em_final_answer`: a instrução que contém a linha rejeitada começa com final_answer( — ali o texto é o
      relatório final (texto_em_literal), não um retorno colado como entrada de código."""
    vazio = {"linha_codigo_erro": "", "chaves_vistas_antes": 0, "em_final_answer": False}
    if not ("Code parsing failed" in m or "SyntaxError" in m or "IndentationError" in m):
        return vazio
    lc = linha_do_codigo(m, code)
    chaves = set(PAR_CHAVE_TEXTO.findall(linha_rejeitada(m, lc)))
    vistas = sum(bool(re.search(r"[\"']" + re.escape(ch) + r"[\"']\s*:", obs_ant)) for ch in chaves)
    em_fa = False
    n = re.search(r"on line (\d+)", m)
    linhas = str(code or "").splitlines()
    if n and 0 < int(n.group(1)) <= len(linhas):
        j = int(n.group(1)) - 1   # sobe até o início da instrução: linha de continuação, vazia ou que abre com aspas/fecha
        while j > 0 and (linhas[j][:1] in (" ", "\t") or not linhas[j].strip() or linhas[j][:1] in "'\")]}"):
            j -= 1
        em_fa = linhas[j].lstrip().startswith("final_answer(")
    return {"linha_codigo_erro": lc, "chaves_vistas_antes": vistas, "em_final_answer": em_fa}


def chama_ferramenta_declarada(m, code, sysp):
    """Só no tempo esgotado do interpretador ("exceeded the maximum execution time"): o bloco chamou alguma ferramenta
    declarada no system prompt do step (`def nome(`), fora o final_answer? Se sim, o tempo foi gasto na ferramenta
    (plataforma); se não, no próprio código do agente. Aproximação declarada: se os dois foram lentos, conta como
    ferramenta (pipeline-entre-bases.md, Ajuste 8)."""
    if "exceeded the maximum execution time" not in m:
        return False
    declaradas = set(re.findall(r"def\s+(\w+)\s*\(", sysp or "")) - {"final_answer"}
    return bool(declaradas & set(re.findall(r"\b(\w+)\s*\(", str(code or ""))))


def final_answer_sem_laco(m, code):
    """Só no tempo esgotado do interpretador: o bloco chama o final_answer e não tem laço (for/while/compreensão)? Sem
    laço, cada linha roda uma vez e o Python do agente não gasta 30 s; se nenhuma outra ferramenta foi chamada, o tempo
    foi no final_answer — na base 2, o resultado bruto da busca entregue inteiro (pipeline-entre-bases.md, Ajuste 9)."""
    if "exceeded the maximum execution time" not in m:
        return False
    code = str(code or "")
    return "final_answer" in set(re.findall(r"\b(\w+)\s*\(", code)) and not tem_laco(code)


def tem_laco(code):
    """O bloco tem laço (for/while, inclusive em compreensão)? Bloco que não parseia: procura a palavra."""
    try:
        return any(isinstance(n, (ast.For, ast.While, ast.comprehension)) for n in ast.walk(ast.parse(code)))
    except SyntaxError:
        return bool(re.search(r"^\s*(for|while)\b|\bfor\s+\w+.*?\s+in\s", code, re.M))


def linha_rejeitada(m, linha_codigo=""):
    """A linha de código que o parser rejeitou: a que a mensagem traz (formato antigo) ou, no formato novo, a linha N
    do code_action (`linha_do_codigo`, coluna `linha_codigo_erro`)."""
    mm = re.search(r"due to: \w+\s*\n(.*?)\n\s*Error:", m, re.S)
    return re.sub(r"\s*\^\s*$", "", mm.group(1).split("\n")[0]).strip() if mm else (linha_codigo or "")


def e_texto(s):
    if re.match(r"^(\||#|\*\*|- |\d+[.)]\s)", s) or "`" in s:
        return True
    toks = re.findall(r"[A-Za-zÀ-ÿ]+", s.lower())
    return len(toks) >= 3 and sum(t in PT_STOP for t in toks) / len(toks) >= 0.15


def submecanismo(m, linha_codigo="", chaves_vistas_antes=0, em_final_answer=False, chama_ferramenta=False,
                 fa_sem_laco=False):
    if "regex pattern" in m:
        return "harness_bloco_code"
    if "AgentGenerationError" in m or "internally hosted" in m or "Error code: 422" in m or "UnprocessableEntity" in m:
        return "infra_llm"
    if "excedeu o timeout" in m or "TimeoutError" in m:
        return "timeout_ferramenta"   # pipeline-entre-bases.md, Ajuste 4
    # tempo do interpretador esgotado: numa chamada de ferramenta → plataforma; só no final_answer, sem laço → o
    # resultado bruto entregue na resposta (Ajuste 9); no código do agente → lição dele
    if "exceeded the maximum execution time" in m:
        if chama_ferramenta:
            return "timeout_interpretador"
        return "resultado_bruto_na_resposta" if fa_sem_laco else "codigo_lento"
    if "Reached max steps" in m or "AgentMaxStepsError" in m:
        return "limite_de_passos"   # desfecho: a execução morreu; a causa está nos erros anteriores (Ajuste 8)
    if "Code parsing failed" in m or "SyntaxError" in m or "IndentationError" in m:
        l = linha_rejeitada(m, linha_codigo)
        if re.search(r"truncad", l, re.I):
            return "repr_colado"
        # retorno impresso colado inteiro (sem "truncado"): >= 2 pares "chave": "texto", >= 2 dessas chaves já
        # impressas numa observação anterior, fora do final_answer. Antes das palavras-chave da mensagem, que o
        # mandavam para texto_em_literal (base 1) ou texto_solto (base 2) — evidência A6_repr_colado
        if (len(set(PAR_CHAVE_TEXTO.findall(l))) >= 2 and chaves_vistas_antes >= 2 and not em_final_answer):
            return "repr_colado"
        if "unterminated" in m or "forgot a comma" in m or "never closed" in m or LITERAL_INICIO.match(l):
            return "texto_em_literal"
        if e_texto(l):
            return "texto_solto_no_codigo"
        return "codigo_mal_escrito"   # sintaxe/indentação em código de verdade, não texto colado
    if "does not support multiple positional" in m:
        return "argumento_posicional"
    # nome de argumento que a assinatura da ferramenta não tem (ex.: final_answer(..., docs=...)) — a mesma lição
    # da chamada posicional: usar a assinatura declarada (pipeline-entre-bases.md, Ajuste 3)
    if re.search(r"\.forward\(\) got an unexpected keyword argument", m):
        return "argumento_inexistente"
    if "Could not index" in m:
        if "string indices must be integers" in m:
            return "tipo_real_do_retorno"
        if re.search(r"KeyError: \d+\s*$", m) or "unhashable type: 'slice'" in m:
            return "dict_indexado_por_posicao"
        if "KeyError: '" in m or "are in the [columns]" in m:
            return "campo_inexistente_no_retorno"
        return "causa_sem_regra"
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
    if f or "Import of" in m or "Import from" in m or "ModuleNotFound" in m or "Forbidden" in m:
        return "inventario_sandbox"
    if v:
        return "nome_nao_definido"
    return "causa_sem_regra"   # nenhuma regra de causa casou; montar_unidades separa o que nem o sintoma reconhece


SUB2UNI = {
    "dict_indexado_por_posicao": "U_contrato_dict", "dict_iterado_como_lista": "U_contrato_dict",
    "campo_inexistente_no_retorno": "U_campo_inexistente",
    "tipo_real_do_retorno": "U_tipo_retorno",
    "texto_em_literal": "U_texto_literal",
    "texto_solto_no_codigo": "U_texto_solto",
    "argumento_posicional": "U_arg_nomeado", "argumento_inexistente": "U_arg_nomeado",
    "inventario_sandbox": "U_sandbox", "modulo_sem_import": "U_sandbox",
    "next_sobre_gerador": "U_next_gerador",
    "nome_de_step_que_falhou": "U_estado_perdido",
    "nome_nunca_definido": "U_nome_inventado",
    "repr_colado": "U_repr_colado",
    "infra_llm": "H_infra_llm", "timeout_ferramenta": "H_timeout_ferramenta",
    "timeout_interpretador": "H_timeout_ferramenta", "codigo_lento": "U_codigo_lento",
    "resultado_bruto_na_resposta": "U_resultado_bruto",
    "limite_de_passos": "C_limite_passos",
    "harness_bloco_code": "H_bloco_code",
    "codigo_mal_escrito": "X_causa_nao_identificada", "causa_sem_regra": "X_causa_nao_identificada",
    "sintoma_nao_reconhecido": "X_sintoma_nao_reconhecido",
}
FACT, ESTR, NAO, SEM = "factual · ambiente", "experiencial · estratégia", "não-memória · harness/infra", "—"
# erro crítico: o agente não se recuperou (a execução esgotou os passos). Não é lição, nem plataforma, nem resíduo:
# todo caso vai para investigação — o passo crítico está nos erros anteriores (Ajuste 8)
CRIT = "erro crítico · não se recuperou"
INVESTIGAR_CRITICO = "investigar — crítico"
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
                      "Chamar as ferramentas com argumentos nomeados e só com os nomes da assinatura declarada: "
                      "f(arg=valor); nenhuma aceita posicional, e o final_answer só recebe a resposta."),
    "U_sandbox": ("Inventário do sandbox", FACT,
                  "repr/eval/globals/dir e imports fora da lista (ex.: ast) são proibidos; json/datetime exigem import explícito; openpyxl ausente — usar envia_excel_para_usuario."),
    "U_next_gerador": ("next() sobre expressão geradora falha no sandbox", FACT,
                       "Usar list comprehension com [0] (ou for + break) em vez de next(x for x in ...)."),
    "U_estado_perdido": ("Após step com erro, o que ele definiria não existe", ESTR,
                         "Se a observação anterior traz exceção, redefinir variáveis e funções auxiliares daquele step antes de usá-las."),
    "U_nome_inventado": ("Nome usado sem ter sido definido", ESTR,
                         "Usar só variáveis e funções definidas no próprio código; 'Observation' é rótulo do harness, não variável."),
    "U_repr_colado": ("Não colar retorno impresso de volta no código", ESTR,
                      "Referenciar a variável que guardou o retorno em vez de colar o print dele (truncado ou inteiro) "
                      "dentro do código; se a ferramenta pede JSON, converter a variável com json.dumps(...), nunca "
                      "com str(...)."),
    "H_infra_llm": ("Falha do LLM upstream — política de retry", NAO,
                    "AgentGenerationError/422: retry com backoff e circuit breaker por subagente."),
    # tipo=NAO reflete só a base 1 (o incidente de out/2025 morre a partir de mar/2026 NESTA base).
    # Gatilho de reabertura (≥2 casos/mês ou taxa > 1/1k steps) foi acionado na base 2 — ver diário
    # de campo 22/09/2026 e `04-roadmap.md` §Monitoramento. Reclassificar (tipo/decisão) quando a
    # base 2 for formalmente integrada ao pipeline; até então, tratar como candidato reaberto, não
    # como resolvido.
    "H_timeout_ferramenta": ("Ferramenta excedeu o timeout — correção na plataforma", NAO,
                             "Ferramenta mais longa que o limite de tempo: o do wrapper de ferramentas da esteira (600 s / "
                             "1800 s por ferramenta) ou o do interpretador, que corta o bloco inteiro em 30 s ou 180 s, "
                             "conforme o agente e a época (base 2) — limites "
                             "desencontrados. Revisar os limites das ferramentas longas ou torná-las assíncronas; o agente já "
                             "segue o fallback do prompt. Gatilho: >= 2 casos num mês ou > 1/1k steps — acionado na base 2."),
    "U_codigo_lento": ("Não rodar laço pesado dentro do bloco de código", ESTR,
                       "O interpretador corta o bloco inteiro (30 s ou 180 s): não percorrer dados longos em laço num só "
                       "bloco; filtrar antes e dividir o trabalho em steps. Sem caso observado — os 3 da base 2 eram "
                       "resultado bruto na resposta final (Ajuste 9)."),
    "U_resultado_bruto": ("Não entregar o resultado bruto de uma ferramenta na resposta final", ESTR,
                          "O final_answer não aguenta o retorno inteiro de uma busca no tempo do interpretador (base 2: "
                          "~27 a ~63 mil caracteres estouraram; os que passaram tinham até ~3 mil). Extrair no código o "
                          "trecho que responde — procurar no texto o que a pergunta pede — e entregar a conclusão com esse "
                          "trecho; não resumir às cegas pelo que ficou visível na observação."),
    "C_limite_passos": ("Limite de passos atingido — o agente não se recuperou", CRIT,
                        "Desfecho, não causa: a execução esgotou os passos sem resposta. Investigar cada caso — o passo "
                        "crítico está nos erros anteriores do papel (resultados/criticos.csv)."),
    "H_bloco_code": ("Protocolo do harness", NAO,
                     "≥2 casos num mês, ou taxa > 1/1k steps, reabre o candidato (limiar = teto do IC95% do regime pós-incidente, a partir de mar/2026: ≤0,99/1k). REABERTO em 22/09/2026 (base 2) — ver diário de campo."),
    # os dois baldes de resíduo (01-racionais.md §7, "Os dois baldes de resíduo"): nunca viram memória; a triagem os
    # põe em "revisar", com prioridade se algum padrão de erro recorre — o que medem é onde as regras não alcançam
    "X_causa_nao_identificada": ("Causa não identificada", SEM, "— (revisar: escrever regra de causa)"),
    "X_sintoma_nao_reconhecido": ("Sintoma não reconhecido", SEM, "— (revisar: escrever regra de sintoma e de causa)"),
}


def montar_unidades(E):
    exigir_analise_integrada(E, "mecanismos, cascatas e unidades")
    EU = E.copy().sort_values(["exec_id", "role", "idx"])
    EU["seguidor"] = EU.groupby(["exec_id", "role"])["idx"].shift().eq(EU["idx"] - 1)
    EU["cascata"] = (~EU["seguidor"]).cumsum()
    col = lambda c, v: EU[c] if c in EU else pd.Series(v, index=EU.index)
    EU["submecanismo"] = [submecanismo(m, l, int(k), bool(fa), bool(cf), bool(fsl)) for m, l, k, fa, cf, fsl in
                          zip(EU["err_msg"], col("linha_codigo_erro", "").fillna(""),
                              col("chaves_vistas_antes", 0).fillna(0), col("em_final_answer", False).fillna(False),
                              col("chama_ferramenta", False).fillna(False),
                              col("final_answer_sem_laco", False).fillna(False))]
    sel = EU["submecanismo"].eq("nome_nao_definido")
    EU.loc[sel, "submecanismo"] = np.where(EU.loc[sel, "seguidor"], "nome_de_step_que_falhou", "nome_nunca_definido")
    # causa sem regra E sintoma não reconhecido pelo classify() = erro que a taxonomia não conhece
    sel = EU["submecanismo"].eq("causa_sem_regra") & EU["familia"].eq("Sintoma não reconhecido")
    EU.loc[sel, "submecanismo"] = "sintoma_nao_reconhecido"
    sem_casa = set(EU["submecanismo"].unique()) - set(SUB2UNI)
    assert not sem_casa, f"mecanismo sem casa em SUB2UNI: {sorted(sem_casa)}"
    EU["unidade"] = EU["submecanismo"].map(SUB2UNI)
    assert EU["unidade"].notna().all(), "erro com unidade NaN após o map SUB2UNI"
    EU["ocorrencia"] = EU["cascata"].astype(str) + "|" + EU["unidade"]
    res = EU["unidade"].str.startswith("X_")
    EU["padrao"] = None
    EU.loc[res, "padrao"] = [padrao_residuo(m, sm, t) for m, sm, t in
                             zip(EU.loc[res, "err_msg"], EU.loc[res, "submecanismo"], col("err_type", None)[res])]
    return EU


def _mecanismo_com_evidencia(r, carga, ctx, incoming, byref):
    """Avalia insumos da regra existente; pendência não inventa novo mecanismo.

    Retorna mecanismo ou NULL, situação, razão. Em parsing, uma ausência num
    prefixo/histórico incompleto nunca substitui o teste anterior de repr_colado.
    """
    if not bool(r["sintoma_elegivel"]):
        return None, "pendente", "mensagem_limitada_ou_ausente"
    m = r["err_msg"]
    ref = r["step_ref"]
    code = r["code"] if pd.notna(r["code"]) else None
    full_code = code is not None and r["code_estado"] == "sem_corte_sql"
    # Preview não decide unidade: serve para reconhecer qual ramo exige sinais.
    preview = submecanismo(m)
    if preview in {"harness_bloco_code", "infra_llm", "timeout_ferramenta", "limite_de_passos"}:
        return preview, "observavel", "regra_por_mensagem_elegivel"
    if preview in {"codigo_lento", "timeout_interpretador", "resultado_bruto_na_resposta"}:
        return None, "pendente", "timeout_requer_prompt_declarado_e_codigo"
    if preview == "nome_nao_definido":
        prev = ctx.get((ref, -1))
        edge = incoming.get(ref)
        if edge is not None and edge["estado"] not in {"compativel_candidato", "ordem_censo"}:
            return None, "pendente", "predecessor_com_vinculo_suspenso"
        if prev is None:
            return None, "pendente", "predecessor_nao_observavel"
        if prev["presenca"] == "limite_censo":
            preceding = False
        elif prev["presenca"] in {"identificado_por_numero", "ordem_censo"}:
            if carga.contrato != CENSO:
                if pd.isna(prev["step"]) or pd.isna(r["step"]) or prev["step"] >= r["step"]:
                    return None, "pendente", "predecessor_numero_ou_chamada_ambiguo"
            preceding = pd.notna(prev["err_type"])
            if preceding and (edge is None or edge["origem_ref"] not in byref):
                return None, "pendente", "predecessor_estruturado_sem_ligacao"
        else:
            return None, "pendente", "predecessor_nao_identificado_sql"
        return ("nome_de_step_que_falhou" if preceding else "nome_nunca_definido"), "observavel", "proxy_predecessor_estruturado_nao_prova_namespace"
    if "Code parsing failed" in m or "SyntaxError" in m or "IndentationError" in m:
        old_line = linha_rejeitada(m)
        if old_line:
            lc = ""
        elif full_code:
            lc = linha_do_codigo(m, code)
        else:
            return None, "pendente", "linha_rejeitada_requer_codigo_integral"
        line = linha_rejeitada(m, lc)
        if not line:
            return None, "pendente", "linha_rejeitada_nao_observavel"
        # Primeira regra de parsing independe de histórico e demais sinais.
        if re.search(r"truncad", line, re.I):
            return submecanismo(m, lc), "observavel", "linha_rejeitada_na_mensagem_ou_codigo"
        keys = set(PAR_CHAVE_TEXTO.findall(line))
        observed = ""
        prev = ctx.get((ref, -1))
        if prev is not None and prev.get("presenca") in {"identificado_por_numero", "ordem_censo"}:
            val = prev.get("observations")
            if pd.notna(val):
                observed = str(val)
        # Somente observações de predecessores vinculados; não inventa passos
        # limpos não exportados nem usa n/+1 (informação futura) como anterior.
        visited = {ref}
        cursor = ref
        while cursor in incoming and incoming[cursor]["estado"] in {"compativel_candidato", "ordem_censo"}:
            edge = incoming[cursor]
            predecessor = edge["origem_ref"]
            if predecessor in visited:
                break
            visited.add(predecessor)
            if predecessor not in byref:
                break
            p = byref[predecessor]
            if pd.notna(p["observations"]):
                observed += "\n" + p["observations"]
            cursor = predecessor
        if len(keys) >= 2:
            if not full_code:
                return None, "pendente", "repr_colado_exige_destino_no_codigo_integral"
            signs = sinais_de_parsing(m, code, observed)
            if not re.search(r"on line (\d+)", m):
                return None, "pendente", "destino_final_answer_nao_observavel"
            line_num = int(re.search(r"on line (\d+)", m).group(1))
            if line_num < 1 or line_num > len(code.splitlines()):
                return None, "pendente", "destino_final_answer_nao_observavel"
            if signs["chaves_vistas_antes"] < 2 and not signs["em_final_answer"]:
                return None, "pendente", "historico_incompleto_para_excluir_repr_colado"
        else:
            # Com <2 chaves, regra do histórico não pode casar: fa/observações
            # não alteram o ramo de parsing; usar o mesmo classificador.
            signs = {"chaves_vistas_antes": 0, "em_final_answer": False}
        return submecanismo(m, lc, signs["chaves_vistas_antes"], signs["em_final_answer"]), "observavel", "sinais_suficientes_para_regra_de_parsing"
    return preview, "observavel", "regra_por_mensagem_elegivel"


def analisar_mecanismos_observaveis(carga, sintomas=None):
    """Reusa regras com cobertura; componentes não habilitam triagem final.

    EU mantém todos estruturados; NULL em pendências não é resíduo. Referências
    de componente/ocorrência observada têm índice_tipo explícito, não idx legado.
    """
    if carga.contrato == TRACE_COMPLETO:
        raise AnaliseNaoIntegrada("Para trace completo use montar_unidades do caminho existente.")
    A = analisar_sintomas(carga) if sintomas is None else sintomas
    if set(A.E.step_ref) != set(carga.steps.loc[carga.steps.structured_error, "step_ref"]):
        raise AnaliseNaoIntegrada("Sintomas e carga não correspondem à mesma população.")
    episodes = construir_episodios_observados(carga)
    ctx = contexto_local(carga)
    incoming = {r["alvo_ref"]: r for r in carga.vinculos.to_dict("records")}
    byref = carga.steps.set_index("step_ref", drop=False).to_dict("index")
    EU = A.E.copy()
    result = [_mecanismo_com_evidencia(r, carga, ctx, incoming, byref) for r in EU.to_dict("records")]
    EU["submecanismo"] = pd.Series([r[0] for r in result], index=EU.index, dtype=pd.StringDtype(storage="python"))
    EU["situacao_mecanismo"] = pd.Series([r[1] for r in result], index=EU.index, dtype=pd.StringDtype(storage="python"))
    EU["motivo_evidencia"] = pd.Series([r[2] for r in result], index=EU.index, dtype=pd.StringDtype(storage="python"))
    # Mesma separação do resíduo em montar_unidades; pendências não entram.
    sel = EU.submecanismo.eq("causa_sem_regra") & EU.familia.eq("Sintoma não reconhecido")
    EU.loc[sel, "submecanismo"] = "sintoma_nao_reconhecido"
    EU["unidade"] = EU.submecanismo.map(SUB2UNI).astype(pd.StringDtype(storage="python"))
    if EU.loc[EU.situacao_mecanismo.eq("observavel"), "unidade"].isna().any():
        raise AnaliseNaoIntegrada("Mecanismo da regra não tem unidade no catálogo existente.")
    membership = episodes.membros[episodes.membros.definicao.eq("estruturado")].set_index("step_ref")
    EU["episodio_estruturado_ref"] = EU.step_ref.map(membership.episodio_ref).astype(pd.StringDtype(storage="python"))
    EU["limites_componente_fechados"] = EU.step_ref.map(membership.componente_fechada_na_definicao).astype("boolean")
    EU["ocorrencia_observada"] = EU.episodio_estruturado_ref + "|" + EU.unidade
    EU["padrao"] = pd.Series(pd.NA, index=EU.index, dtype=pd.StringDtype(storage="python"))
    residual = EU.unidade.str.startswith("X_", na=False)
    for index, r in EU[residual].iterrows():
        EU.loc[index, "padrao"] = padrao_residuo(r.err_msg, r.submecanismo, r.err_type)
    EU.attrs.update(A.E.attrs)
    EU.attrs["analise_integrada"] = "mecanismos_observaveis_sem_triagem"
    obs = EU[EU.situacao_mecanismo.eq("observavel")].copy()
    tables = {
        "cobertura_mecanismos": _resumo_grupos_erros(EU, ["situacao_mecanismo", "motivo_evidencia"]),
        "mecanismos": _resumo_grupos_erros(obs, ["submecanismo", "unidade"]),
        "mecanismos_por_papel": _resumo_grupos_erros(obs, ["role", "unidade"]),
        "custos_mecanismos": _resumo_grupos_erros(obs, ["submecanismo", "unidade"]),
    }
    eps = episodes.episodios
    summary = {"erros_estruturados": len(EU), "mecanismos_observaveis": len(obs), "pendentes": len(EU) - len(obs),
               "pendencias_por_motivo": EU.loc[EU.situacao_mecanismo.eq("pendente"), "motivo_evidencia"].value_counts().to_dict(),
               "componentes_por_definicao": eps.definicao.value_counts().to_dict(),
               "componentes_fechados_por_definicao": eps.loc[eps.componente_fechada_na_definicao.eq(True), "definicao"].value_counts().to_dict(),
               "maior_componente_por_definicao": eps.groupby("definicao").n_ancoras.max().to_dict(),
               "observacao": "proxies determinísticos e componentes candidatos; não causalidade, recuperação ou memória aprovada"}
    return SimpleNamespace(EU=EU, EU_observavel=obs, episodios=episodes, tabelas=tables, resumo=summary,
                           cobertura={**A.cobertura, "mecanismos": "por_regra_com_pendencias",
                                      "episodios": "componentes_observadas_condicionadas", "triagem": "bloqueada"})


def mascarar(frase):
    """Texto entre aspas → <q>, entre crases → <id>, números → <n>. Sobra só o texto padrão da exceção do Python."""
    frase = re.sub(r"'[^']*'|\"[^\"]*\"", "<q>", frase)
    frase = re.sub(r"`[^`]*`", "<id>", frase)
    return re.sub(r"\d+", "<n>", frase).strip()


SEM_NOME = "sem nome de exceção"


def padrao_residuo(m, sub, err_type=None):
    """A impressão digital de um erro do resíduo, para contar recorrência por erro e não pelo balde inteiro:
    classe da exceção + frase mascarada. Na sintaxe, a frase é o motivo do parser (linha `Error:`), sem a posição —
    só a classe juntaria códigos quebrados de jeitos diferentes. Aproximação declarada: pode juntar erros que diferem
    só dentro das aspas, ou separar o mesmo erro se a frase fora das aspas variar (01-racionais.md §7 Passo 5)."""
    if sub == "codigo_mal_escrito":
        classe = (re.findall(r"due to: (\w+Error)", m) or re.findall(r"\b(\w+Error)\b", m) or ["?"])[-1]
        linhas = [l.strip() for l in m.splitlines() if l.strip().startswith("Error:")]
        inline = re.search(r"due to: \w+Error: ([^\n]*)", m)  # formato novo: o motivo vem na linha do `due to:`
        motivo = mascarar(linhas[-1][len("Error:"):]) if linhas else (mascarar(inline.group(1)) if inline else "")
        motivo = re.sub(r"\s*\(<unknown>, line <n>\)", "", motivo)
        motivo = re.sub(r"\s+on line <n>", "", motivo)
        return f"{classe}: {motivo}".rstrip(": ")
    k = re.findall(r"(\b\w+(?:Error|Exception)\b):\s*([^\n]{0,90})", m)
    if k:
        return f"{k[-1][0]}: {mascarar(k[-1][1])}"
    classe = re.findall(r"\b\w+(?:Error|Exception)\b", m)
    # sem nome de exceção na mensagem: a chave diz o tipo do erro e NÃO conta como padrão recorrente — juntaria erros
    # diferentes (na base 2, o antigo "?" juntava tempo do interpretador e limite de passos — Ajuste 8)
    return classe[-1] if classe else f"{SEM_NOME}: {err_type or '?'}"


MIN_EXECS, MIN_MESES = 3, 2
REVISAR_PRIORIDADE, REVISAR_BAIXA = "revisar — prioridade", "revisar — baixa prioridade"
# alarme de cobertura: se o "Sintoma não reconhecido" passar desta fração de TODOS os erros da base, a taxonomia não
# cobre a base e o balde sobe para prioridade mesmo sem padrão recorrente (03-procedimento-validacao.md, Frente 3)
ALARME_COBERTURA = 0.05

# decisão da mineração (Frente 3, procedimento de candidata), tomada DEPOIS da triagem com regra pré-registrada:
# `validation.destino` de cada unidade minerada. Unidade fora daqui = destino em aberto (ainda não minerada).
# "harness" = erro do agente cujo conserto certo é no ambiente (contrato do prompt, validação no harness) — a saída
# "sinal de harness" do mecanismo, distinta da não-memória operacional (onde a plataforma falhou).
# Fonte: 07-relatorio-mineracao-unidades-n2-n10.md §6.1–6.2; pipeline-entre-bases.md, Ajuste 5.
# As bases são independentes: cada uma é triada e minerada por conta própria, e a decisão só vale na base em que a
# mineração foi feita (a nº10 da base 2 não herda o "harness" da base 1 — pipeline-entre-bases.md, Ajuste 7). Quando a
# mesma decisão é tomada noutra base, com evidência dela, a base entra em `bases` (Ajuste 13, 05/10: o "campo
# inexistente" da base 2 — 38/38 com a chave pedida no system prompt, 31 delas `quebra_sigilo` contra o retorno
# `vazamento_sigilo` do `validar_quebra_sigilo`; `investigacao_achados.py` seção C, rodada 2 da máquina 2).
DESTINO_MINERACAO = {
    "U_contrato_dict": {"destino": "memória", "bases": ("base1",)},
    "U_campo_inexistente": {"destino": "harness", "bases": ("base1", "base2")},
}
SINAL_HARNESS = "sinal de harness"


def destino_mineracao(u, base_id=None):
    """O destino que a mineração decidiu para a unidade NESTA base (memória / harness), ou "em aberto" se ela não foi
    minerada aqui."""
    d = DESTINO_MINERACAO.get(u)
    return d["destino"] if d and (base_id or BASE_ID) in d["bases"] else "em aberto"


def residuo_por_padrao(EU, min_execs=MIN_EXECS, min_meses=MIN_MESES):
    """Uma linha por padrão de resíduo: erros, execuções e meses (sobre ocorrências, como a triagem) e se passa no
    mesmo teste de recorrência das candidatas. É a lista de trabalho para escrever regra nova."""
    R = EU[EU["unidade"].str.startswith("X_")]
    o = R.drop_duplicates("ocorrencia")
    chave = ["unidade", "submecanismo", "padrao"]
    t = (o.groupby(chave).agg(ocorrências=("ocorrencia", "size"), execuções=("exec_id", "nunique"),
                               meses=("mes", "nunique"), papéis=("role", "nunique"))
         .join(R.groupby(chave).size().rename("erros")).reset_index())
    t["chave"] = np.where(t["padrao"].astype(str).str.startswith(SEM_NOME), SEM_NOME, "identificada")
    t["passa na recorrência"] = ((t["execuções"] >= min_execs) & (t["meses"] >= min_meses)
                                 & (t["chave"] == "identificada"))
    return t.sort_values(["passa na recorrência", "execuções", "erros"], ascending=False).reset_index(drop=True)


def caminho_dos_criticos(EU):
    """A fila de investigação dos erros críticos: uma linha por execução em que o papel esgotou os passos, com as
    unidades dos erros ANTERIORES do mesmo papel — o caminho até a morte. `primeira unidade` é o primeiro erro do
    caminho, ponto de partida para achar o passo crítico (causa-raiz, no sentido do AgentDebug)."""
    linhas = []
    for (eid, role), g in EU.groupby(["exec_id", "role"]):
        crit = g[g["submecanismo"] == "limite_de_passos"]
        if crit.empty:
            continue
        i_crit = int(crit["idx"].min())
        antes = g[g["idx"] < i_crit].sort_values("idx")
        linhas.append({"exec_id": eid, "role": role, "mes": crit["mes"].iloc[0], "idx do erro crítico": i_crit,
                       "steps no papel": int(crit["n_steps_role"].iloc[0]) if "n_steps_role" in crit else None,
                       "erros antes": len(antes),
                       "primeira unidade": antes["unidade"].iloc[0] if len(antes) else "",
                       "unidades no caminho": " + ".join(antes["unidade"].value_counts().index)})
    return pd.DataFrame(linhas, columns=["exec_id", "role", "mes", "idx do erro crítico", "steps no papel", "erros antes",
                                         "primeira unidade", "unidades no caminho"])


# M1 da família Protocolo do harness (10-racionais-protocolo-harness.md §4): a resposta final escrita fora do envelope
# <code> e reembrulhada depois em final_answer. A medida (30/09) era avulsa; virou função em 02/10 (ressalva D da
# auditoria de 02/10). O limiar não foi registrado em 30/09: 0,5 é o reconstruído — reproduz as 4 linhas publicadas
# da base 1 (qualquer valor em (0,479; 0,523] reproduz; 1 caso de cada lado da margem). Falso negativo conhecido: o LLM que reescreve ao reembrulhar.
M1_LIMIAR = 0.5
# Sinal de resto (M4, 10 §4; Ajuste 15, 05/10): o texto entregue por token de saída, comparado com o NORMAL DO PRÓPRIO
# PAPEL NA MESMA EXECUÇÃO (a mediana dos steps sem erro), e não com um valor fixo. Modelo de raciocínio gasta tokens que
# não viram texto em todo step (o4-mini, base 1: 0,66–0,97 caractere por token nos steps bons); o limiar fixo marcava
# todos. Abaixo de 1/4 do normal, o texto é tratado como resto. Base 1: os erros ficam em 0,11–0,12 (2 do RespostaBacen)
# ou ≥ 0,77; base 2 (fatos de 10 §4 M4): 0,03–0,18.
RESTO_LIMIAR = 0.25
# Ferramenta que se apresenta como resposta final (M2, 10 §4; Ajuste 16, 05/10): reconhecida pelo NOME declarado no
# system prompt (`def <nome>(`), fora o próprio final_answer. Pela descrição não serve: na base 1 pegava 5 ferramentas
# que só citam a resposta final (WorkflowManager, validadores, get_final_answer_schema...).
FERRAMENTA_FINAL = re.compile(r"resposta_?final|final_?response", re.I)


def sobreposicao(texto, outro, n=5):
    """Fração dos trechos de `n` palavras de `texto` que reaparecem em `outro` (0 se `texto` tem menos de `n`
    palavras). Palavra = sequência alfanumérica, em minúsculo. Usada no `drill_down.py protocolo` [9]: o que o modelo escreveu no lugar do
    bloco × a resposta final entregue depois (antecipou?) e × a observação anterior (copiou da ferramenta?)."""
    def trechos(t):
        w = re.findall(r"\w+", str(t or "").lower())
        return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}
    a = trechos(texto)
    return len(a & trechos(outro)) / len(a) if a else 0.0


FALHA_FERRAMENTA = re.compile(r"Error calling tool '(\w+)'")


def falhas_silenciosas(df):
    """Uma linha por (step, ferramenta) em que uma ferramenta declarada foi chamada ou falhou. É uma medida, não uma
    regra de classificação. `falha`:
      - "excecao": o step tem erro e a ferramenta aparece em `Error calling tool '<nome>'`;
      - "silenciosa": a mesma mensagem está na observação (ou no action_output), mas o step tem `error: null`. A
        ferramenta falhou, o wrapper devolveu o erro como STRING e o Python seguiu. Para o pipeline, o step foi "ok";
      - None: chamada sem falha visível.
    `idx` é o mesmo de explodir_memoria (posição entre os ActionSteps do papel), para cruzar com erros_mecanismo.csv.
    `chamada`: quantos TaskStep vêm antes do step na lista do papel (o papel pode ser chamado várias vezes na mesma
    execução; o `idx` conta as chamadas juntas — plano S4).
    `idx_final_depois`: o primeiro step do papel com is_final_answer a partir deste (o próprio step, se ele for o final)
    e na mesma chamada, ou None. Ajuste 11 (02/10): antes era o 1º final estritamente depois, em qualquer chamada — a
    falha no próprio step do final_answer ficava fora do [4], e um final de outra chamada entrava.
    Origem: 11-relatorio-protocolo-harness.md §2.5 (a calculadora do CalculoCivel, base 2) e o item 26 do roadmap.
    Limite: só a forma "Error calling tool"; validações e resultados vazios ou errados não entram."""
    linhas = []
    for _, r in df[df["txt_etap_memo"].notna()].iterrows():
        try: memo = json.loads(r["txt_etap_memo"])
        except Exception: continue
        for role, steps in memo.items():
            if not isinstance(steps, list): continue
            acts, chamada_de, n_task = [], [], 0
            for s in steps:
                if not isinstance(s, dict): continue
                if s.get("__class__") == "TaskStep": n_task += 1
                elif s.get("__class__") == "ActionStep": acts.append(s); chamada_de.append(n_task)
            finais = [i for i, s in enumerate(acts) if s.get("is_final_answer")]
            for i, st in enumerate(acts):
                mim = st.get("model_input_messages")
                sysp = ""
                if mim:
                    m0 = mim[0] if isinstance(mim[0], dict) else {}
                    c = m0.get("content")
                    sysp = c[0].get("text", "") if isinstance(c, list) and c and isinstance(c[0], dict) else str(c or "")
                declaradas = set(re.findall(r"def\s+(\w+)\s*\(", sysp)) - {"final_answer"}
                code = str(st.get("code_action") or "")
                chamadas = declaradas & set(re.findall(r"\b(\w+)\s*\(", code))
                err = st.get("error") or {}
                obs = str(st.get("observations") or "") + " " + str(st.get("action_output") or "")
                texto = obs + " " + str(err.get("message") or "")
                falhou = set(FALHA_FERRAMENTA.findall(texto))
                prox_final = next((f for f in finais if f >= i and chamada_de[f] == chamada_de[i]), None)
                for t in sorted(chamadas | falhou):
                    # o motivo: o texto da ferramenta depois de "Error calling tool '<nome>':" (1ª linha). Pode conter
                    # valores do caso (filtros) — mascarar_motivo() antes de mostrar.
                    m = re.search(rf"Error calling tool '{t}':?\s*([^\n]*)", texto) if t in falhou else None
                    linhas.append({"exec_id": r["cod_idef_exeo"], "role": role, "idx": i, "chamada": chamada_de[i],
                                   "mes": r["mes"],
                                   "ferramenta": t, "chamou": t in chamadas,
                                   "falha": ("excecao" if err else "silenciosa") if t in falhou else None,
                                   "motivo": m.group(1)[:300] if m else "",
                                   "grupo": motivo_da_falha(m.group(1)) if m else None,
                                   "idx_final_depois": prox_final})
    return pd.DataFrame(linhas, columns=["exec_id", "role", "idx", "chamada", "mes", "ferramenta", "chamou", "falha",
                                         "motivo", "grupo", "idx_final_depois"])


# Grupos do motivo de uma falha de ferramenta (S2b, 01/10). Regras por palavra-chave, na ordem; a 1ª que casar
# decide. Cada uma anota a base de onde veio (b1/b2) — as mensagens são escritas pelo dev de cada ferramenta, e uma base
# nova traz ferramentas novas: o que não casar cai em "nao_reconhecido" e é lido como cobertura, como o resíduo.
# Evidência: `drill_down.py silenciosas --motivos` nas duas bases (11-relatorio-protocolo-harness.md §2.5; ledger).
MOTIVO_REGRAS = [
    ("json_invalido", r"expecting property name enclosed in double quotes", "b1 b2"),
    ("json_invalido", r"expecting .{0,8}delimiter", "b2"),
    ("sem_resultado", r"nao foram encontrados", "b1"),
    ("sem_resultado", r"no text of initial complaints found", "b1 b2"),
    ("sem_resultado", r"\bnot found\b", "b1"),
    ("sem_resultado", r"nao foi possivel recuperar", "b1 b2"),
    ("fora_da_cobertura", r"assunto nao previsto", "b1 b2"),
    ("fora_da_cobertura", r"coeficiente nao encontrado", "b2"),
    ("fora_da_cobertura", r"outside available range|no data available", "b1"),
    ("argumento_do_agente", r"necessario passar", "b1"),
    ("argumento_do_agente", r"invalid key=value", "b1"),
    ("argumento_do_agente", r"same amount of documents|maximum amount of documents", "b1"),
    ("argumento_do_agente", r"formato de arquivo nao suportado|file format cannot be determined", "b1"),
    ("argumento_do_agente", r"deve passar versao", "b1"),
    ("argumento_do_agente", r"deve ser anterior ou igual|data_inicial/data_final invalida|indice deve ser", "b1 b2"),
    ("argumento_do_agente", r"validation error for call", "b2"),
    ("argumento_do_agente", r"deve ser um numero", "b2"),
    ("argumento_do_agente", r"query falhou", "b1 b2"),
    ("argumento_do_agente", r"could not convert", "b2"),
    ("argumento_do_agente", r"must be a dict with", "b1"),
    ("argumento_do_agente", r"doesn't exist, use tool", "b1"),
    ("plataforma", r"internally hosted model failed", "b1 b2"),
    ("plataforma", r"litellm|apierror", "b1"),
    ("plataforma", r"failed to fetch", "b1 b2"),
    ("plataforma", r"wrong credentials", "b2"),
    ("plataforma", r"ongoing worker", "b1"),
    ("plataforma", r"object has no attribute|too many values to unpack", "b1 b2"),
    ("plataforma", r"structured_content must be", "b1 b2"),
    ("plataforma", r"^'default'$", "b1 b2"),   # b1 desde 02/10: 2 na base 1 (CalculoCivel, a mesma calculadora; audit_recompute9)
]
GRUPOS_FALHA_REAL = ("argumento_do_agente", "plataforma", "json_invalido", "nao_reconhecido")


def motivo_da_falha(motivo):
    """Grupo do motivo de uma falha de ferramenta (texto depois de "Error calling tool '<nome>':"): sem_resultado,
    fora_da_cobertura, argumento_do_agente, plataforma, json_invalido ou nao_reconhecido. Sem acento, minúsculo."""
    s = unicodedata.normalize("NFKD", str(motivo or "")).encode("ascii", "ignore").decode().lower().strip()
    for grupo, padrao, _ in MOTIVO_REGRAS:
        if re.search(padrao, s):
            return grupo
    return "nao_reconhecido"


def mascarar_motivo(s, n=60):
    """O motivo de uma falha de ferramenta sem dado de caso: o que está entre aspas e o valor depois de '=' viram <v>,
    dígitos viram 9, corta em `n` caracteres. Sobra o texto que o dev da ferramenta escreveu."""
    s = re.sub(r"'[^']*'|\"[^\"]*\"", "<v>", str(s))
    s = re.sub(r"=\s*[^\s,;)]+", "=<v>", s)
    return re.sub(r"\d", "9", s).strip()[:n]


# O balde invisível (notebook falhas_silenciosas.ipynb; docs 13–15). As medidas abaixo são as mesmas do
# `drill_down.py silenciosas` — o notebook e o comando chamam estas funções, para os números não divergirem.

# Quem é o dono da falha, por grupo do motivo. Rótulo GENÉRICO: o json_invalido fica "a conferir" mesmo depois de
# conferido numa base — em outra, o dono pode ser a ferramenta; quem decide em cada base é forma_argumento()
# (decisão do Rafael, 01/10; ledger Etapa 10c).
DONO_DO_GRUPO = {"sem_resultado": "ninguém — não é falha",
                 "fora_da_cobertura": "negócio — pedido fora do que a ferramenta cobre",
                 "argumento_do_agente": "agente — candidato a memória que a taxonomia não vê",
                 "plataforma": "plataforma / ferramenta", "json_invalido": "a conferir: agente ou ferramenta",
                 "nao_reconhecido": "cobertura — sem regra de motivo"}
UNIDADES_CONTRATO = ["U_tipo_retorno", "U_contrato_dict", "U_campo_inexistente"]


def _variavel(a, codes):
    """`a` começa com um nome de variável → de onde ela veio: a ferramenta cuja chamada a atribuiu, ou o agente."""
    v = re.match(r"(\w+)\s*[,)]", a)
    if not v:
        return None
    origem = next((t for c in codes for t in re.findall(rf"\b{v.group(1)}\s*=\s*(\w+)\s*\(", c)), None)
    return f"variável devolvida por {origem}(...)" if origem else "variável montada pelo agente"


def _colado(a, obs_ant):
    """O literal em `a` é um retorno impresso colado? Mesmo critério do repr_colado no submecanismo(): ≥2 pares
    "chave": "texto" e ≥2 dessas chaves já impressas como chave numa observação anterior do mesmo papel."""
    chaves = set(PAR_CHAVE_TEXTO.findall(a))
    vistas = sum(bool(re.search(r"[\"']" + re.escape(ch) + r"[\"']\s*:", obs_ant)) for ch in chaves)
    return len(chaves) >= 2 and vistas >= 2


def forma_argumento(ferramenta, codes, obs_ant=""):
    """Como o 1º argumento de `ferramenta` foi passado no último código de `codes` (os steps do papel até a falha) —
    só o tipo, sem conteúdo. Para decidir o dono do json_invalido: str(dict) com aspas simples / dict ou string montados
    à mão → agente; json.dumps ou a variável que outra ferramenta devolveu → a ferramenta. `obs_ant` (as observações dos
    steps anteriores do papel) separa o literal colado de um retorno impresso — o gesto do repr_colado — do montado.
    Base 1: 6/6 e base 2: 86/86 das falhas do busca_obf são o gesto colado (ledger Etapa 10c, "Achado (01/10)")."""
    m = re.search(rf"\b{ferramenta}\s*\((.{{0,600}})", codes[-1], re.S)
    if not m:
        return "sem chamada visível no código"
    a = re.sub(r"^\s*\w+\s*=(?!=)\s*", "", m.group(1)).lstrip()   # tira o "nome_do_argumento="
    if a.startswith("json.dumps"):
        return "json.dumps(...)"
    if a.startswith("str("):
        dentro = a[4:].lstrip()
        if dentro[:1] in "{[":
            return ("str(dict/lista colado de um retorno impresso) — gesto do repr_colado" if _colado(dentro, obs_ant)
                    else "str(dict/lista literal montado pelo agente)")
        v = _variavel(dentro, codes)
        return f"str({v})" if v else "str(...) — outro"
    if a[:1] in "{[":
        return ("dict/lista colado de um retorno impresso — gesto do repr_colado" if _colado(a, obs_ant)
                else "dict/lista literal montado pelo agente")
    if re.match(r"[fFrR]?[\"']", a):
        return ("string literal colada de um retorno impresso — gesto do repr_colado" if _colado(a, obs_ant)
                else "string literal montada pelo agente")
    return _variavel(a, codes) or "outro"


def formas_das_falhas(df, sil):
    """forma_argumento() de cada falha de `sil` (linhas de falhas_silenciosas()), na mesma ordem. Lê o código e as
    observações do papel até o step da falha — só o tipo sai daqui."""
    D = df.set_index("cod_idef_exeo")
    out = []
    for _, s in sil.iterrows():
        acts = [x for x in json.loads(D.loc[s["exec_id"], "txt_etap_memo"])[s["role"]]
                if isinstance(x, dict) and x.get("__class__") == "ActionStep"]
        ate = acts[: int(s["idx"]) + 1]
        out.append(forma_argumento(s["ferramenta"], [str(x.get("code_action") or "") for x in ate],
                                   "".join(str(x.get("observations") or "") for x in ate[:-1])))
    return pd.Series(out, index=sil.index, dtype=object)


def erro_depois_da_falha(sil, EU, janela=3):
    """[2] a unidade do 1º erro do mesmo papel em até `janela` steps depois de cada falha de `sil`, ou
    "(nenhum erro)". `EU`: erros com exec_id, role, idx, unidade (montar_unidades() ou erros_mecanismo.csv)."""
    out = []
    for _, s in sil.iterrows():
        e = EU[(EU["exec_id"] == s["exec_id"]) & (EU["role"] == s["role"]) & (EU["idx"] > s["idx"])
               & (EU["idx"] <= s["idx"] + janela)].sort_values("idx")
        out.append(e["unidade"].iloc[0] if len(e) else "(nenhum erro)")
    return pd.Series(out, index=sil.index, dtype=object)


def contrato_precedido(sil, EU, janela=3):
    """[3] por unidade de contrato de retorno: (erros, quantos têm uma falha silenciosa no mesmo papel até `janela`
    steps antes). Mede se essas memórias nascem de falha silenciosa (não nascem: 91–94%, duas bases)."""
    chaves = set(zip(sil["exec_id"], sil["role"]))
    res = {}
    for u in UNIDADES_CONTRATO:
        E = EU[EU["unidade"] == u]
        n_prec = sum(1 for _, e in E.iterrows() if (e["exec_id"], e["role"]) in chaves and
                     ((sil["exec_id"] == e["exec_id"]) & (sil["role"] == e["role"]) & (sil["idx"] < e["idx"])
                      & (sil["idx"] >= e["idx"] - janela)).any())
        res[u] = (len(E), n_prec)
    return res


def sucesso_falso_candidato(F, sil):
    """[4] para cada falha REAL de `sil` (GRUPOS_FALHA_REAL): o papel entregou final_answer — no próprio step da falha
    ou depois, na mesma chamada (`idx_final_depois`, Ajuste 11) — sem nenhuma chamada sem falha da mesma ferramenta no
    meio? Série booleana só sobre as falhas reais. É teto: conferir no caso."""
    real = sil[sil["grupo"].isin(GRUPOS_FALHA_REAL)]
    ok = F[F["chamou"] & F["falha"].isna()]
    out = []
    for _, s in real.iterrows():
        if pd.isna(s["idx_final_depois"]):
            out.append(False); continue
        depois_ok = ok[(ok["exec_id"] == s["exec_id"]) & (ok["role"] == s["role"]) & (ok["ferramenta"] == s["ferramenta"])
                       & (ok["idx"] > s["idx"]) & (ok["idx"] <= s["idx_final_depois"])]
        out.append(depois_ok.empty)
    return pd.Series(out, index=real.index, dtype=bool)


# A consolidação (Ajuste 12, 04/10; plano 4.2b). Os dois baldes entregam OCORRÊNCIAS no mesmo formato — exec_id, role,
# idx, mes, unidade, ocorrencia, canal — e a triagem conta a recorrência sobre a união (nunca somando totais: a mesma
# execução pode ter a unidade nos dois canais). Ocorrência, nos dois canais, é a mesma régua (decisão do Rafael, 02/10):
# cascata (steps consecutivos do mesmo papel com falha/erro) × unidade.

# A regra do balde invisível para o catálogo: (grupo do motivo, marca na forma do argumento, unidade). Sem nome de
# ferramenta. O que não casa fica sem unidade — a fila de trabalho do balde invisível, como o resíduo do visível.
# Evidência da única regra: o json_invalido do busca_obf é o gesto do repr_colado nas duas bases (6/6, 86/86) —
# ledger Etapa 10c, "Achado (01/10)"; doc 13 §5.
REGRAS_INVISIVEL = [
    ("json_invalido", "gesto do repr_colado", "U_repr_colado"),
]


def unidade_silenciosa(grupo, forma):
    """A unidade do catálogo de uma falha silenciosa (REGRAS_INVISIVEL), ou None."""
    for g, marca, u in REGRAS_INVISIVEL:
        if grupo == g and marca in str(forma or ""):
            return u
    return None


def ocorrencias_visiveis(EU):
    """As ocorrências do balde visível no formato comum: uma linha por erro, com a `ocorrencia` de montar_unidades()
    (cascata × unidade)."""
    return EU[["exec_id", "role", "idx", "mes", "unidade", "ocorrencia"]].assign(canal="visível")


def ocorrencias_silenciosas(sil, formas):
    """As ocorrências do balde invisível no formato comum. `sil`: as falhas silenciosas (linhas de falhas_silenciosas()
    com falha == "silenciosa"); `formas`: formas_das_falhas(df, sil), na mesma ordem. Uma linha por step com falha (dois
    motivos no mesmo step viram uma linha por unidade). A cascata é a do visível: steps consecutivos do mesmo papel com
    falha silenciosa; `ocorrencia` = cascata × unidade. `unidade` None = sem regra (fica fora da triagem)."""
    S = sil.assign(forma=list(formas))
    S["unidade"] = [unidade_silenciosa(g, f) for g, f in zip(S["grupo"], S["forma"])]
    passos = S.drop_duplicates(["exec_id", "role", "idx"]).sort_values(["exec_id", "role", "idx"])
    seguidor = (passos["exec_id"].eq(passos["exec_id"].shift()) & passos["role"].eq(passos["role"].shift())
                & passos["idx"].eq(passos["idx"].shift() + 1))
    cascata = dict(zip(zip(passos["exec_id"], passos["role"], passos["idx"]), (~seguidor).cumsum()))
    S = S.drop_duplicates(["exec_id", "role", "idx", "unidade"]).copy()
    S["cascata"] = [cascata[k] for k in zip(S["exec_id"], S["role"], S["idx"])]
    S["ocorrencia"] = "s" + S["cascata"].astype(str) + "|" + S["unidade"].fillna("—")
    return (S[["exec_id", "role", "idx", "mes", "unidade", "ocorrencia", "ferramenta", "grupo", "forma"]]
            .assign(canal="silencioso").sort_values(["exec_id", "role", "idx"]).reset_index(drop=True))


def triagem(EU, min_execs=MIN_EXECS, min_meses=MIN_MESES, silenciosas=None):
    # resíduo: recorrência contada por PADRÃO de erro, não pela unidade (que junta erros diferentes por construção)
    passa = residuo_por_padrao(EU, min_execs, min_meses).groupby("unidade")["passa na recorrência"].any()
    # execuções mortas (limite de passos) em que cada unidade aparece no caminho — o peso de gravidade (Ajuste 8)
    crit = caminho_dos_criticos(EU)
    mortas = Counter(u for c in crit["unidades no caminho"] for u in c.split(" + ") if u)
    fracao_desconhecida = (EU["unidade"] == "X_sintoma_nao_reconhecido").mean()
    # `silenciosas` (Ajuste 12): ocorrências do balde invisível (ocorrencias_silenciosas()). Com elas, ocorrências,
    # execuções, meses e papéis contam a UNIÃO dos dois canais; erros, tokens, cascata e "% após outro erro" continuam
    # do visível (o custo das silenciosas é retrabalho, medido no notebook delas). Sem elas, a saída é a de sempre.
    S = None if silenciosas is None else silenciosas[silenciosas["unidade"].notna()]
    grupos = list(EU.groupby("unidade"))
    if S is not None:
        grupos += [(u, EU.iloc[0:0]) for u in sorted(set(S["unidade"]) - set(EU["unidade"]))]
    tri = []
    for u, g in grupos:
        nome, tipo, conteudo = UNI[u]
        o = g.drop_duplicates("ocorrencia")
        s_u = S[S["unidade"] == u].drop_duplicates("ocorrencia") if S is not None else EU.iloc[0:0]
        execs_u = len(set(o["exec_id"]) | set(s_u["exec_id"]))
        meses_u = len(set(o["mes"]) | set(s_u["mes"]))
        if tipo == NAO:
            decisao = "não-memória"
        elif tipo == CRIT:  # o agente não se recuperou: todo caso vai para investigação, sem limite mínimo
            decisao = INVESTIGAR_CRITICO
        elif tipo == SEM:  # resíduo: nunca candidato (falta a regra de causa); a fila de trabalho da taxonomia
            alarme = u == "X_sintoma_nao_reconhecido" and fracao_desconhecida > ALARME_COBERTURA
            decisao = REVISAR_PRIORIDADE if (passa.get(u, False) or alarme) else REVISAR_BAIXA
            motivo = ("padrão recorrente" if passa.get(u, False) else "") + \
                     (" + " if passa.get(u, False) and alarme else "") + \
                     (f"alarme de cobertura ({fracao_desconhecida:.1%} dos erros)" if alarme else "") or \
                     "nenhum padrão recorrente"
        elif execs_u < min_execs or meses_u < min_meses:
            decisao = "fora: sem recorrência"
        else:
            # passou nas três perguntas; se a mineração já decidiu que o conserto é no ambiente, é sinal de harness
            decisao = SINAL_HARNESS if destino_mineracao(u) == "harness" else "candidato"
        tri.append({"unidade": u, "nome": nome, "tipo": tipo, "decisão": decisao,
                    "destino (mineração)": destino_mineracao(u) if tipo in (FACT, ESTR) else "",
                    "motivo (resíduo)": motivo if tipo == SEM else "",
                    "ocorrências": len(o) + len(s_u),
                    **({"ocorrências visíveis": len(o), "ocorrências silenciosas": len(s_u)} if S is not None else {}),
                    "erros": len(g), "reincidências na cascata": len(g) - len(o),
                    "execuções mortas com esta unidade no caminho": mortas.get(u, 0),
                    "execuções": execs_u, "meses": meses_u,
                    "papéis": len(set(o["role"]) | set(s_u["role"])),
                    "tokens": int(g["tok_tot"].sum()),
                    "% ocorr. após outro erro": round(o["seguidor"].mean() * 100) if len(o) else None,
                    "assinaturas de origem": " + ".join(g["assinatura"].value_counts().index),
                    "conteúdo proposto": conteudo})
    ordem = {"candidato": 0, SINAL_HARNESS: 1, INVESTIGAR_CRITICO: 2, "não-memória": 3, REVISAR_PRIORIDADE: 4,
             REVISAR_BAIXA: 5, "fora: sem recorrência": 6}
    t = pd.DataFrame(tri)
    return t.assign(_o=t["decisão"].map(ordem)).sort_values(["_o", "tokens"], ascending=[True, False]).drop(columns="_o")


def triagem_por_papel(EU, min_execs=MIN_EXECS, min_meses=MIN_MESES, silenciosas=None):
    """A mesma régua do triagem(), aplicada dentro de cada papel — a candidatura scoped da §9.4. Só unidades
    elegíveis a memória (tipo factual/estratégia): plataforma (não-memória) e resíduo (X_) ficam fora por
    decisão de desenho. Uma linha por (role, unidade) com erros no papel; a decisão é "candidato" quando a
    unidade se repete naquele papel (>= min_execs execuções e >= min_meses meses, sobre ocorrências
    deduplicadas da cascata, como a global). Unidade ausente no papel simplesmente não gera linha. Unidade cujo
    destino da mineração é harness também fica fora: o conserto é no ambiente, não há memória por papel a escrever.
    `silenciosas` (4.2c): as ocorrências do balde invisível, como na triagem() — ocorrências, execuções e meses do papel
    contam a união dos dois canais; erros e tokens continuam do visível. Sem elas, a saída é a de sempre."""
    S = None if silenciosas is None else silenciosas[silenciosas["unidade"].notna()]
    grupos = list(EU.groupby(["role", "unidade"]))
    if S is not None:
        ja = {k for k, _ in grupos}
        grupos += [(k, EU.iloc[0:0]) for k in sorted(set(zip(S["role"], S["unidade"])) - ja)]
    tri = []
    for (role, u), g in grupos:
        nome, tipo, _ = UNI[u]
        if tipo not in (FACT, ESTR) or destino_mineracao(u) == "harness":
            continue
        o = g.drop_duplicates("ocorrencia")
        s_u = (S[(S["role"] == role) & (S["unidade"] == u)].drop_duplicates("ocorrencia") if S is not None
               else EU.iloc[0:0])
        execs = len(set(o["exec_id"]) | set(s_u["exec_id"]))
        meses = len(set(o["mes"]) | set(s_u["mes"]))
        tri.append({"role": role, "unidade": u, "nome": nome, "tipo": tipo,
                    "decisão": "candidato" if (execs >= min_execs and meses >= min_meses) else "fora no papel",
                    "ocorrências": len(o) + len(s_u),
                    **({"ocorrências visíveis": len(o), "ocorrências silenciosas": len(s_u)} if S is not None else {}),
                    "erros": len(g), "execuções": execs, "meses": meses,
                    "tokens": int(g["tok_tot"].sum())})
    t = pd.DataFrame(tri)
    return t.sort_values(["role", "decisão", "tokens"], ascending=[True, True, False]).reset_index(drop=True)


def categoria_do_erro(familia, unidade):
    """A categoria de cor de um erro — a mesma em todas as figuras (paleta.COR_ERRO): "Resíduo" quando nenhuma regra
    de causa o reconheceu (unidades X_); senão a família do erro. As famílias de plataforma (harness/infra) ficam com
    o nome da família e ganham cinzas na paleta."""
    return "Resíduo" if unidade.startswith("X_") else familia


DEGENERADO = re.compile(r"n[ãa]o encontrad[oa] na base|informa[çc][ãa]o insuficiente", re.I)


def medir_sucesso(df):
    exigir_analise_integrada(df, "sucesso por conteúdo")
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


def carregar_mineracao_observada(caminho=None):
    """Fachada explícita sem habilitar carregar_base/sucesso/consumidores raw."""
    from mineracao_observada import analisar
    return analisar(carregar_carga(caminho))


def carregar_base(*, apenas_carga=False, caminho=None):
    if apenas_carga:
        return carregar_carga(caminho)
    caminho = TRACE if caminho is None else caminho
    contrato = detectar_contrato(colunas_do_trace(caminho))
    if contrato != TRACE_COMPLETO:
        exigir_analise_integrada(SimpleNamespace(contrato=contrato), "análise completa via carregar_base()")
    df = carregar_trace(caminho)
    steps, RAW, execs = explodir_memoria(df)
    E = classificar_erros(steps)
    EU = montar_unidades(E)
    S = medir_sucesso(df)
    return SimpleNamespace(df=df, steps=steps, RAW=RAW, execs=execs, E=E, EU=EU, S=S)
