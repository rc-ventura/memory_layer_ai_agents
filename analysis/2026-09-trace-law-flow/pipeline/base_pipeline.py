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
           "linha_do_codigo", "PAR_CHAVE_TEXTO", "sinais_de_parsing", "linha_rejeitada", "e_texto", "submecanismo", "SUB2UNI", "FACT", "ESTR", "NAO", "SEM",
           "UNI", "montar_unidades", "MIN_EXECS", "MIN_MESES", "triagem", "mascarar", "padrao_residuo",
           "residuo_por_padrao", "REVISAR_PRIORIDADE", "REVISAR_BAIXA", "ALARME_COBERTURA",
           "BASE_ID", "DESTINO_MINERACAO", "SINAL_HARNESS", "destino_mineracao", "CRIT", "INVESTIGAR_CRITICO",
           "caminho_dos_criticos", "FALHA_FERRAMENTA", "falhas_silenciosas", "mascarar_motivo", "MOTIVO_REGRAS",
           "GRUPOS_FALHA_REAL", "motivo_da_falha", "DONO_DO_GRUPO", "UNIDADES_CONTRATO", "forma_argumento",
           "formas_das_falhas", "erro_depois_da_falha", "contrato_precedido", "sucesso_falso_candidato","chama_ferramenta_declarada", "final_answer_sem_laco", "tem_laco", "SEM_NOME",
           "categoria_do_erro", "triagem_por_papel",
           "DEGENERADO", "medir_sucesso", "carregar_base"]

TRACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                     "85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz")
# qual base é esta: "base1" aqui, "base2" na pasta -second, "base3" na -third. Junto com o TRACE, é o que se ajusta ao
# copiar o pipeline para uma base nova — a decisão da mineração (DESTINO_MINERACAO) só vale na base em que foi tomada.
BASE_ID = "base1"


def carregar_trace():
    df = pd.read_csv(TRACE, dtype=str)
    # `mes` = mês em que a execução RODOU (dat_hor_inio_exeo). `anomesdia` não serve para isso: é a data de corte
    # do lote (1 valor por mês, sempre posterior ao início — mediana 46 dias, até 230), e só bate com o mês real
    # em 36% das execuções com memória. Evidência: `drill_down.py relogios`; método: 03-procedimento-validacao.md.
    df["mes_exec"] = pd.to_datetime(df["dat_hor_inio_exeo"]).dt.to_period("M").astype(str)
    df["mes_particao"] = pd.to_datetime(df["anomesdia"], format="%Y%m%d").dt.to_period("M").astype(str)
    df["mes"] = df["mes_exec"]
    return df


def explodir_memoria(df):
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
                      "dentro do código."),
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
# mineração foi feita (a nº10 da base 2 não herda o "harness" da base 1 — pipeline-entre-bases.md, Ajuste 7).
DESTINO_MINERACAO = {
    "U_contrato_dict": {"destino": "memória", "base": "base1"},
    "U_campo_inexistente": {"destino": "harness", "base": "base1"},
}
SINAL_HARNESS = "sinal de harness"


def destino_mineracao(u, base_id=None):
    """O destino que a mineração decidiu para a unidade NESTA base (memória / harness), ou "em aberto" se ela não foi
    minerada aqui."""
    d = DESTINO_MINERACAO.get(u)
    return d["destino"] if d and d["base"] == (base_id or BASE_ID) else "em aberto"


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


FALHA_FERRAMENTA = re.compile(r"Error calling tool '(\w+)'")


def falhas_silenciosas(df):
    """Uma linha por (step, ferramenta) em que uma ferramenta declarada foi chamada ou falhou. É uma medida, não uma
    regra de classificação. `falha`:
      - "excecao": o step tem erro e a ferramenta aparece em `Error calling tool '<nome>'`;
      - "silenciosa": a mesma mensagem está na observação (ou no action_output), mas o step tem `error: null`. A
        ferramenta falhou, o wrapper devolveu o erro como STRING e o Python seguiu. Para o pipeline, o step foi "ok";
      - None: chamada sem falha visível.
    `idx` é o mesmo de explodir_memoria (posição entre os ActionSteps do papel), para cruzar com erros_mecanismo.csv.
    `idx_final_depois`: o primeiro step do papel com is_final_answer depois deste (ou None).
    Origem: 11-relatorio-protocolo-harness.md §2.5 (a calculadora do CalculoCivel, base 2) e o item 26 do roadmap.
    Limite: só a forma "Error calling tool"; validações e resultados vazios ou errados não entram."""
    linhas = []
    for _, r in df[df["txt_etap_memo"].notna()].iterrows():
        try: memo = json.loads(r["txt_etap_memo"])
        except Exception: continue
        for role, steps in memo.items():
            if not isinstance(steps, list): continue
            acts = [s for s in steps if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
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
                prox_final = next((f for f in finais if f > i), None)
                for t in sorted(chamadas | falhou):
                    # o motivo: o texto da ferramenta depois de "Error calling tool '<nome>':" (1ª linha). Pode conter
                    # valores do caso (filtros) — mascarar_motivo() antes de mostrar.
                    m = re.search(rf"Error calling tool '{t}':?\s*([^\n]*)", texto) if t in falhou else None
                    linhas.append({"exec_id": r["cod_idef_exeo"], "role": role, "idx": i, "mes": r["mes"],
                                   "ferramenta": t, "chamou": t in chamadas,
                                   "falha": ("excecao" if err else "silenciosa") if t in falhou else None,
                                   "motivo": m.group(1)[:300] if m else "",
                                   "grupo": motivo_da_falha(m.group(1)) if m else None,
                                   "idx_final_depois": prox_final})
    return pd.DataFrame(linhas, columns=["exec_id", "role", "idx", "mes", "ferramenta", "chamou", "falha", "motivo",
                                         "grupo", "idx_final_depois"])


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
    ("plataforma", r"^'default'$", "b2"),
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
    """[4] para cada falha REAL de `sil` (GRUPOS_FALHA_REAL): o papel entregou final_answer depois sem nenhuma chamada
    sem falha da mesma ferramenta no meio? Série booleana só sobre as falhas reais. É teto: conferir no caso."""
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


def triagem(EU, min_execs=MIN_EXECS, min_meses=MIN_MESES):
    # resíduo: recorrência contada por PADRÃO de erro, não pela unidade (que junta erros diferentes por construção)
    passa = residuo_por_padrao(EU, min_execs, min_meses).groupby("unidade")["passa na recorrência"].any()
    # execuções mortas (limite de passos) em que cada unidade aparece no caminho — o peso de gravidade (Ajuste 8)
    crit = caminho_dos_criticos(EU)
    mortas = Counter(u for c in crit["unidades no caminho"] for u in c.split(" + ") if u)
    fracao_desconhecida = (EU["unidade"] == "X_sintoma_nao_reconhecido").mean()
    tri = []
    for u, g in EU.groupby("unidade"):
        nome, tipo, conteudo = UNI[u]
        o = g.drop_duplicates("ocorrencia")
        execs_u, meses_u = o["exec_id"].nunique(), o["mes"].nunique()
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
                    "ocorrências": len(o), "erros": len(g), "reincidências na cascata": len(g) - len(o),
                    "execuções mortas com esta unidade no caminho": mortas.get(u, 0),
                    "execuções": execs_u, "meses": meses_u, "papéis": o["role"].nunique(),
                    "tokens": int(g["tok_tot"].sum()),
                    "% ocorr. após outro erro": round(o["seguidor"].mean() * 100),
                    "assinaturas de origem": " + ".join(g["assinatura"].value_counts().index),
                    "conteúdo proposto": conteudo})
    ordem = {"candidato": 0, SINAL_HARNESS: 1, INVESTIGAR_CRITICO: 2, "não-memória": 3, REVISAR_PRIORIDADE: 4,
             REVISAR_BAIXA: 5, "fora: sem recorrência": 6}
    t = pd.DataFrame(tri)
    return t.assign(_o=t["decisão"].map(ordem)).sort_values(["_o", "tokens"], ascending=[True, False]).drop(columns="_o")


def triagem_por_papel(EU, min_execs=MIN_EXECS, min_meses=MIN_MESES):
    """A mesma régua do triagem(), aplicada dentro de cada papel — a candidatura scoped da §9.4. Só unidades
    elegíveis a memória (tipo factual/estratégia): plataforma (não-memória) e resíduo (X_) ficam fora por
    decisão de desenho. Uma linha por (role, unidade) com erros no papel; a decisão é "candidato" quando a
    unidade se repete naquele papel (>= min_execs execuções e >= min_meses meses, sobre ocorrências
    deduplicadas da cascata, como a global). Unidade ausente no papel simplesmente não gera linha. Unidade cujo
    destino da mineração é harness também fica fora: o conserto é no ambiente, não há memória por papel a escrever."""
    tri = []
    for (role, u), g in EU.groupby(["role", "unidade"]):
        nome, tipo, _ = UNI[u]
        if tipo not in (FACT, ESTR) or destino_mineracao(u) == "harness":
            continue
        o = g.drop_duplicates("ocorrencia")
        execs, meses = o["exec_id"].nunique(), o["mes"].nunique()
        tri.append({"role": role, "unidade": u, "nome": nome, "tipo": tipo,
                    "decisão": "candidato" if (execs >= min_execs and meses >= min_meses) else "fora no papel",
                    "ocorrências": len(o), "erros": len(g), "execuções": execs, "meses": meses,
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
