"""Conferência independente da lição U_sandbox (validador-de-script), escrita só a partir do `racional.md`.

Não importa o pipeline, o script da lição, o `minerar.py` nem a auditoria da candidata. Lê o parquet cru pelo
`analysis/leitor_trace.py` (abrir o arquivo não é lógica auditada) e o `casos.csv` do perfil da rodada com `csv`.
Grava as medidas num JSON (contagens, nomes de papel, mês, módulo e função, exec_id e step_ref; nenhum texto de caso).

Revalidação 7 (20/10): a emenda 7 (o import de uma ferramenta citada e não declarada pelo prompt, hoje só
`get_document_text`, sai da população), a emenda 8 (no papel cujo prompt manda verificar, hoje só o ContestacaoCivel,
que chega ao trace como `ontestacaoCivel`, toda verificação de existência com globals/locals/vars sai da população) e a
emenda 9 (C dividida em global e por papel, B com o texto novo, E sem globals/locals/vars/eval e com o complemento
curto, a parte F, e `validation.nomes` em todas as partes).

Revalidação 6 (19/10): a emenda 5 (a emenda 3 vale também para `eval`, pela função escrita pelo agente, com a chamada
fora de globals/locals/vars/eval) e a emenda 6 (E com destino memória e o complemento fixo da guidance de E).

Revalidação 5 (19/10): a tabela "O arquivo final de cada parte" (complemento da emenda 4): category, scope,
location, evidence, description, correction_guidance, occurrences e impact de cada memória, com o desempate por
erros e, no empate, a alfabética.

Revalidação 4 (19/10): a emenda 3 (a introspecção que verifica uma variável sai da população, pela linha que falhou e
pelo código do passo) e a emenda 4 (uma memória por parte C/B/D/E: os erros, o escopo, o destino, `location`,
`evidence` e os nomes da `correction_guidance` de cada memória, e o catálogo esperado), lidas só do racional.

    uv run python analysis/2026-10-trace-law-flow-third/propostas/U_sandbox/conferencia_independente.py \
        --fonte <parquet> --casos <rodada>/perfis/U_sandbox/casos.csv --perfil <rodada>/perfis/U_sandbox/perfil.csv \
        --json <arquivo>
"""

import argparse, builtins, collections, csv, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(AQUI, "..", "..", "..")))  # analysis/
from leitor_trace import linhas_do_trace  # noqa: E402

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

# ------------------------------------------------------------------ passo 1 (prosa do racional, para a auditoria)
EMBUTIDAS = set(dir(builtins))
MODULOS_VARIAVEL = {"json", "pd", "np", "re", "os", "math", "datetime"}
RE_FFE = re.compile(r"Forbidden function evaluation: '([^']+)'")
RE_IMPORT = re.compile(r"Import of|Import from|ModuleNotFound")
RE_FORBIDDEN = re.compile(r"Forbidden")
RE_VARIAVEL = re.compile(r"The variable `([^`]+)` is not defined")
# os sinais que o pipeline decide antes (o racional os nomeia; o padrão literal é a leitura deste validador)
SINAIS_ANTES = {
    # emenda 2 do racional (fd93e93): os três sinais que faltavam, com os padrões literais que o racional dá
    "bloco_de_codigo": re.compile(r"regex pattern"),
    "falha_llm": re.compile(r"AgentGenerationError|internally hosted|Error code: 422|UnprocessableEntity"),
    "timeout_ferramenta": re.compile(r"excedeu o timeout|TimeoutError"),
    "sintaxe": re.compile(r"SyntaxError|invalid syntax|Error in code parsing"),
    "could_not_index": re.compile(r"Could not index"),
    "has_no_attribute": re.compile(r"has no attribute"),
    "jsondecode": re.compile(r"JSONDecode"),
    "argumento_posicional": re.compile(r"positional argument"),
    "nao_iterador": re.compile(r"object is not an iterator"),
    "limite_passos": re.compile(r"[Mm]ax(imum)?[ _-]?(number of )?steps|Reached max"),
    "tempo_interpretador": re.compile(r"[Tt]ime ?out|timed out|execution time"),
}


# emenda 3 (19/10, Ajuste 21): sai da população a introspecção que verifica uma variável e guarda a criação dela
INTROSPECCAO = {"globals", "locals", "vars"}
RE_LINHA = re.compile(r"at line '(.*)' due to:", re.S)


def nomes_verificados(linha):
    """Os nomes que a linha verifica: direto (in/not in globals(), globals().get) ou por f('x') com x criado na linha."""
    intro = r"(?:globals|locals|vars)\(\)"
    diretos = set(re.findall(r"""['"]([A-Za-z_]\w*)['"]\s+(?:not\s+)?in\s+""" + intro, linha))
    diretos |= set(re.findall(intro + r"""\.get\(\s*['"]([A-Za-z_]\w*)['"]""", linha))
    criados = set(re.findall(r"(?<![=!<>\w.])([A-Za-z_]\w*)\s*=(?!=)", linha))
    por_funcao = {x for x in re.findall(r"""(?<![.\w])[A-Za-z_]\w*\(\s*['"]([A-Za-z_]\w*)['"]\s*\)""", linha)
                  if x in criados}
    return diretos | por_funcao


def recebe_chamada(nome, texto, excluidas=INTROSPECCAO):
    """`nome = f(...)` com f fora de `excluidas` (globals/locals/vars; na emenda 5, também eval), no texto."""
    for f in re.findall(r"(?<![\w.])" + re.escape(nome) + r"\s*=(?!=)[^\n]*?(?<![\w.])([A-Za-z_][\w.]*)\s*\(", texto):
        if f.split(".")[-1] not in excluidas:
            return True
    return False


# emenda 5 (19/10, Ajuste 23): a emenda 3 vale também para `eval`, só pelo braço da função escrita pelo agente
EXCLUIDAS_EVAL = INTROSPECCAO | {"eval"}


def nomes_por_funcao_do_agente(linha):
    """f('x') com f uma função escrita pelo agente (não embutida) e x criado na mesma linha."""
    criados = set(re.findall(r"(?<![=!<>\w.])([A-Za-z_]\w*)\s*=(?!=)", linha))
    return {x for f, x in re.findall(r"""(?<![.\w])([A-Za-z_]\w*)\(\s*['"]([A-Za-z_]\w*)['"]\s*\)""", linha)
            if x in criados and f not in EMBUTIDAS}


def verificacao_existencia(msg, codigo):
    m = RE_FFE.search(trecho_final(msg))
    if not m or m.group(1) not in INTROSPECCAO | {"eval"}:
        return False
    lm = RE_LINHA.search(msg)
    if not lm:
        return False
    linha = lm.group(1)
    if m.group(1) == "eval":
        return any(recebe_chamada(x, codigo or "", EXCLUIDAS_EVAL) or recebe_chamada(x, linha, EXCLUIDAS_EVAL)
                   for x in nomes_por_funcao_do_agente(linha))
    return any(recebe_chamada(x, codigo or "") or recebe_chamada(x, linha) for x in nomes_verificados(linha))


def trecho_final(msg):
    return msg.rsplit("due to:", 1)[-1] if "due to:" in msg else msg


# emenda 7 (20/10, Ajuste 26): o import de uma ferramenta que o prompt cita e não declara (hoje só get_document_text)
CITADAS_NAO_DECLARADAS = {"get_document_text"}
RE_IMPORT_NOME = [re.compile(r"Import of (\S+?) is not allowed"), re.compile(r"Import from (\S+?) is not allowed"),
                  re.compile(r"No module named '([^']+)'")]


def ferramenta_nao_declarada(msg):
    t = trecho_final(msg)
    for rx in RE_IMPORT_NOME:
        for x in rx.findall(t):
            if x.strip("'\"`").split(".")[0] in CITADAS_NAO_DECLARADAS:
                return True
    return False


# emenda 8 (20/10, Ajuste 27): no papel cujo prompt manda verificar, toda verificação com globals/locals/vars
PAPEIS_QUE_VERIFICAM = {"ContestacaoCivel", "ontestacaoCivel"}  # o racional: chega ao trace como `ontestacaoCivel`
RE_VERIF_PAPEL = re.compile(r"\bin\s+(?:globals|locals|vars)\(\)|(?<![\w.])(?:globals|locals|vars)\(\)\.get\(")


def verificacao_papel_instruido(msg, papel):
    if papel not in PAPEIS_QUE_VERIFICAM:
        return False
    m = RE_FFE.search(trecho_final(msg))
    if not m or m.group(1) not in INTROSPECCAO:
        return False
    lm = RE_LINHA.search(msg)
    return bool(lm and RE_VERIF_PAPEL.search(lm.group(1)))


def criterio_sandbox(msg):
    """Qual braço do passo 1 a mensagem satisfaz (ou None)."""
    m = RE_FFE.search(msg)
    if m and m.group(1) in EMBUTIDAS:
        return "funcao_embutida"
    if RE_IMPORT.search(msg):
        return "import_modulenotfound"
    # "Forbidden (qualquer outro)": outro Forbidden que não a avaliação de função
    if RE_FORBIDDEN.search(RE_FFE.sub("", msg)):
        return "forbidden_outro"
    v = RE_VARIAVEL.search(msg)
    if v and v.group(1) in MODULOS_VARIAVEL:
        return "variavel_modulo"
    return None


# ------------------------------------------------------------------ passo 4 (a regra específica)
REGRAS = [
    ("funcao_proibida", re.compile(r"Forbidden function evaluation: '([^']+)'")),
    ("import_bloqueado", re.compile(r"Import (?:of|from) (\S+?) is not allowed")),
    ("modulo_ausente", re.compile(r"No module named '([^']+)'")),
    ("atributo_dunder", re.compile(r"Forbidden access to dunder attribute: (\S+)")),
    ("modulo_sem_import", re.compile(r"The variable `([^`]+)` is not defined")),
]
RE_AUTORIZADOS = re.compile(r"Authorized imports are: \[([^\]]*)\]")
ROTULOS = [  # a ordem da correction_guidance no racional
    ("Não chame", "funcao_proibida"),
    ("não importe", "import_bloqueado"),
    ("importe antes de usar", "modulo_sem_import"),
    ("não existe no ambiente", "modulo_ausente"),
    ("não acesse", "atributo_dunder"),
]


def nome_recusado(msg, integro):
    if not integro:
        return "sem_nome", None
    t = trecho_final(msg)
    for tipo, rx in REGRAS:
        m = rx.search(t)
        if m:
            return tipo, m.group(1).strip().rstrip(".,;:").strip("'\"`")
    return "sem_nome", None


# emenda 4 (19/10): as partes C/B/D/E; emenda 9 (20/10): C dividida (C global e Cp por papel) e a parte F
B_FRAMEWORK = {"smolagents", "mcp", "mcp_client"}
B_NOMES = {"tools", "tool_usage", "tool_functions", "python_interpreter"}
FRAMEWORK_9 = B_FRAMEWORK | B_NOMES  # emenda 9: os nomes do framework, pela raiz
APELIDOS = {"pd": "pandas", "np": "numpy"}  # emenda 9: o módulo de um modulo_sem_import
F_FUNCOES = {"globals", "locals", "vars", "eval"}  # emenda 9: saem de E para F


def modulo_de(nome):
    return APELIDOS.get(nome, nome)


def molde_import(nome):
    m = modulo_de(nome)
    return f"import {m} as {nome}" if m != nome else f"import {m}"


def parte_do_erro(tipo, nome, modulos_c_global=None):
    if tipo == "modulo_sem_import":
        if modulos_c_global is None or modulo_de(nome) in modulos_c_global:
            return "C"
        return "Cp"
    if tipo == "funcao_proibida" and nome in F_FUNCOES:
        return "F"
    if tipo in ("funcao_proibida", "atributo_dunder"):
        return "E"
    if tipo in ("import_bloqueado", "modulo_ausente"):
        n = nome or ""
        topo = n.split(".")[0]  # leitura deste validador: o framework pelo pacote de topo
        if topo in B_FRAMEWORK or n in B_NOMES or n.startswith("get_"):
            return "B"
        return "D"
    return None


def lista_autorizada(msg):
    m = RE_AUTORIZADOS.search(msg)
    if not m:
        return None
    nomes = re.findall(r"'([^']+)'", m.group(1)) or [x.strip().strip("'\"") for x in m.group(1).split(",") if x.strip()]
    return tuple(sorted(nomes))


# ------------------------------------------------------------------ revalidação 5: a tabela "O arquivo final de cada parte"
# emenda 9: o complemento perde "; para ler JSON, use json.loads"
COMPLEMENTO_E = "Para inspecionar um valor, use print(type(x)) e print(str(x)[:n])."
ROTULO_PARTE = {"C": "módulo usado sem import", "Cp": "módulo usado sem import, por papel",
                "B": "ferramenta importada como módulo", "D": "import fora da lista autorizada",
                "E": "funções e atributos proibidos", "F": "introspecção fora da verificação instruída"}
GLOBAIS = ("C", "E", "F")
DESTINO = {"C": "memória", "Cp": "memória", "B": "memória", "D": "memória", "E": "memória", "F": "em aberto"}


def por_erros(contagem):
    """Em toda lista de nomes: por erros, e no empate a alfabética."""
    return [nm for nm, _ in sorted(contagem.items(), key=lambda x: (-x[1], x[0]))]


def lista_do_papel(papel, erros_com_lista):
    """A lista do papel no mês mais recente em que aparece; empate no mês: a com mais erros, depois a alfabética."""
    do_papel = [e for e in erros_com_lista if e["papel"] == papel and e["lista"] is not None]
    if not do_papel:
        return None, None, 0
    mes_max = max(e["mes"] for e in do_papel)
    c = collections.Counter(e["lista"] for e in do_papel if e["mes"] == mes_max)
    escolhida = sorted(c.items(), key=lambda x: (-x[1], x[0]))[0][0]
    return list(escolhida), mes_max, len(c)


def memoria_da_parte(mid, v, erros, a):
    pt = v[0]["parte"]
    papel = mid.split(".", 2)[2] if pt in ("B", "D", "Cp") else None
    rot = ROTULO_PARTE[pt]
    o_ppm = sorted(v, key=lambda e: (e["papel"], e["mes"], e["step_ref"]))
    if pt in GLOBAIS:
        loc, vis = [], set()
        for e in o_ppm:
            if e["papel"] not in vis:
                vis.add(e["papel"])
                loc.append(e)
        loc = loc[:10]
    else:
        loc = sorted(v, key=lambda e: (e["mes"], e["step_ref"]))[:10]
    cont_nome = collections.Counter(e["nome"] for e in v)
    tres = por_erros(cont_nome)[:3]
    ev = [next(x for x in o_ppm if x["nome"] == nm) for nm in tres]
    papeis = len({e["papel"] for e in v})
    desc_nomes = ", ".join(f"{nm} {cont_nome[nm]}" for nm in por_erros(cont_nome))
    # o molde do racional (emenda 4, ef36e2c): termina com ponto final
    descricao = {k: f"{len(v)} erros em {papeis} {pal}, parte {pt} do inventário do sandbox ({rot}): {desc_nomes}."
                 for k, pal in (("literal", "papel(éis)"), ("concordancia", "papel" if papeis == 1 else "papéis"))}
    def nomes(tipos):
        return por_erros(collections.Counter(e["nome"] for e in v if e["tipo"] in tipos))
    lista = mes_lista = None
    n_listas_mes = 0
    lista_so_parte = None
    vnomes = {"importar": [], "nao_importar": [], "nao_usar": [], "usar": []}
    cont_mod = collections.Counter(modulo_de(e["nome"]) for e in v if e["tipo"] == "modulo_sem_import")
    apelido_de = {modulo_de(e["nome"]): e["nome"] for e in v if e["tipo"] == "modulo_sem_import"}
    if pt == "C":
        mods = por_erros(cont_mod)
        guia = "Importe antes de usar: " + ", ".join(molde_import(apelido_de[m]) for m in mods) + "."
        vnomes["importar"] = mods
    elif pt == "Cp":
        lista, mes_lista, n_listas_mes = lista_do_papel(papel, erros)
        mods = por_erros(cont_mod)
        sim = [m for m in mods if lista is None or m in lista]
        nao = [m for m in mods if lista is not None and m not in lista]
        pedacos = []
        if sim:
            pedacos.append("Importe antes de usar: " + ", ".join(molde_import(apelido_de[m]) for m in sim))
        if nao:
            pedacos.append("Não está na lista autorizada deste papel: " + ", ".join(nao))
        guia = "; ".join(pedacos) + "."
        vnomes["importar"], vnomes["nao_importar"] = sim, nao
    elif pt == "B":
        todos = nomes({"import_bloqueado", "modulo_ausente"})
        fw = [nm for nm in todos if nm.split(".")[0] in FRAMEWORK_9]
        guia = ("As ferramentas são só as funções declaradas no prompt: chame-as direto, sem import. "
                f"Não importe: {', '.join(todos)}.")
        if fw:
            guia += f" {', '.join(fw)}: são do framework, e o seu código já roda no interpretador."
        vnomes["nao_importar"] = por_erros(collections.Counter(e["nome"].split(".")[0] for e in v))
    elif pt == "F":
        guia = "Não chame: " + ", ".join(nomes({"funcao_proibida"})) + "."
        vnomes["nao_usar"] = nomes({"funcao_proibida"})
    elif pt == "D":
        lista, mes_lista, n_listas_mes = lista_do_papel(papel, erros)
        lista_so_parte = lista_do_papel(papel, v)[0]
        pedacos = []
        if nomes({"import_bloqueado"}):
            pedacos.append("Não importe: " + ", ".join(nomes({"import_bloqueado"})))
        if nomes({"modulo_ausente"}):
            pedacos.append("Não existe no ambiente: " + ", ".join(nomes({"modulo_ausente"})))
        if lista:
            pedacos.append("imports autorizados neste papel: " + ", ".join(lista))
        guia = "; ".join(pedacos) + "."
        vnomes["nao_importar"] = por_erros(cont_nome)
    else:
        pedacos = []
        if nomes({"funcao_proibida"}):
            pedacos.append("Não chame: " + ", ".join(nomes({"funcao_proibida"})))
        if nomes({"atributo_dunder"}):
            pedacos.append("Não acesse: " + ", ".join(nomes({"atributo_dunder"})))
        # emenda 6: o complemento fixo depois de "Não chame: …; Não acesse: …."
        guia = "; ".join(pedacos) + ". " + COMPLEMENTO_E
        # "em toda lista de nomes, a ordem é por erros, e no empate a alfabética": nao_usar é uma lista só
        vnomes["nao_usar"] = nomes({"funcao_proibida", "atributo_dunder"})
        vnomes["usar"] = ["print", "type", "str"]
    grupos = collections.defaultdict(int)
    for e in v:
        grupos[(e["exec_id"], e["papel"], e["nome"])] += 1
    listas_parte = sorted({e["lista"] for e in v if e["lista"] is not None})
    return {
        "parte": pt, "rotulo": rot, "papel_escopo": papel,
        # emenda 4: C e E "global"; B e D "uma memória por papel"; emenda 9: Cp por papel, F global
        "escopo": "global" if pt in GLOBAIS else "papel",
        "destino": DESTINO[pt],  # emenda 6: E memória; emenda 9: Cp memória, F em aberto
        "validation_nomes": vnomes,
        # "onde cada destino foi decidido": um destino "em aberto" não foi decidido (como E na revalidação 5)
        "destino_decidido_presente": DESTINO[pt] != "em aberto",
        "erros": len(v), "execucoes": len({e["exec_id"] for e in v}), "meses_lista": sorted({e["mes"] for e in v}),
        "meses": len({e["mes"] for e in v}), "papeis": papeis, "erros_por_tipo": dict(collections.Counter(e["tipo"] for e in v)),
        "category": f"Inventário do sandbox · {rot} (factual · ambiente)",
        "scope": {"role": papel, "tool": None},
        "location": [{"step_ref": e["step_ref"], "role": e["papel"], "mes": e["mes"]} for e in loc],
        "location_total_erros": len(v),
        "evidence": [{"step_ref": e["step_ref"], "tipo": e["tipo"], "nome": e["nome"]} for e in ev],
        "description": descricao,
        "correction_guidance": guia,
        "lista_D": {"lista": lista, "mes": mes_lista, "listas_no_mes": n_listas_mes,
                    "igual_se_so_erros_da_parte": lista_so_parte == lista} if pt == "D" else None,
        "lista_Cp": {"lista": lista, "mes": mes_lista, "listas_no_mes": n_listas_mes} if pt == "Cp" else None,
        "occurrences": {"erros": len(v), "ocorrencias": len(v), "execucoes": len({e["exec_id"] for e in v}),
                        "meses": sorted({e["mes"] for e in v})},
        "listas_autorizadas_da_parte": [list(L) for L in listas_parte],
        "repeticoes_do_nome_na_parte": sum(n - 1 for n in grupos.values() if n > 1),
        "impact": None,
        "chaves": sorted([e["exec_id"], e["step_ref"]] for e in v),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonte", required=True)
    ap.add_argument("--casos", required=True)
    ap.add_argument("--perfil", required=True)
    ap.add_argument("--json", required=True)
    a = ap.parse_args()

    # ---- a população na rodada (casos.csv do perfil; os pendentes não entram)
    casos = list(csv.DictReader(open(a.casos, encoding="utf-8", newline="")))
    casos = [c for c in casos if c.get("unidade", "U_sandbox") == "U_sandbox"]
    chave_rodada = {(c["exec_id"], c["agente"], c["role"], c["step_pos"]): c for c in casos}
    assert len(chave_rodada) == len(casos), "chave (exec_id, agente, papel, step_pos) não é única na rodada"

    # ---- a população na fonte crua (prosa do passo 1)
    colunas = ["cod_idef_exeo", "cod_idef_aget", "papel", "step_pos", "mes_execucao", "structured_error",
               "error_type", "error_message", "error_code_action"]
    fonte, excluidos_por_sinal, linhas, estruturados = {}, collections.Counter(), 0, 0
    chaves_fonte = collections.Counter()  # (exec, agente, papel, step_pos): a chave precisa do papel
    msgs_rodada = {}
    for r in linhas_do_trace(a.fonte, colunas=colunas):
        linhas += 1
        k = (r["cod_idef_exeo"], r["cod_idef_aget"], r["papel"], r["step_pos"])
        chaves_fonte[k] += 1
        if k in chave_rodada:
            msgs_rodada[k] = r
        if not r["error_type"]:
            continue
        estruturados += 1
        msg = r["error_message"] or ""
        braco = criterio_sandbox(msg)
        if not braco:
            continue
        sinais = [n for n, rx in SINAIS_ANTES.items() if rx.search(msg)]
        if not sinais and verificacao_existencia(msg, r["error_code_action"]):
            sinais = ["verificacao_existencia_emenda3"]
        if not sinais and ferramenta_nao_declarada(msg):
            sinais = ["ferramenta_nao_declarada_emenda7"]
        if not sinais and verificacao_papel_instruido(msg, r["papel"]):
            sinais = ["verificacao_papel_instruido_emenda8"]
        if sinais:
            for n in sinais:
                excluidos_por_sinal[n] += 1
            continue
        fonte[k] = (r, braco)

    so_rodada = sorted(set(chave_rodada) - set(fonte))
    so_fonte = sorted(set(fonte) - set(chave_rodada))

    # ---- passo 4 sobre a população da rodada, com a mensagem da fonte crua
    erros = []
    for k, c in sorted(chave_rodada.items()):
        r = msgs_rodada.get(k)
        msg = (r or {}).get("error_message", "") or ""
        integro = c.get("err_msg_estado", "sem_corte_sql") == "sem_corte_sql"
        tipo, nome = nome_recusado(msg, integro)
        primeira = (trecho_final(msg).strip().split() or [""])[0] if tipo == "sem_nome" else None
        erros.append({
            "exec_id": c["exec_id"], "agente": c["agente"], "step_ref": c["step_ref"], "step_pos": int(c["step_pos"]),
            "papel": (r or {}).get("papel") or c["role"], "papel_rodada": c["role"],
            "mes": (r or {}).get("mes_execucao") or c["mes"], "mes_rodada": c["mes"],
            "tipo": tipo, "nome": nome, "sem_nome_primeira_palavra": primeira,
            "lista": lista_autorizada(msg), "code_estado": c.get("code_estado"),
            "err_msg_estado": c.get("err_msg_estado"), "msg_na_fonte": r is not None,
        })

    n = len(erros)
    com_nome = sum(1 for e in erros if e["tipo"] != "sem_nome")
    cobertura = com_nome / n if n else 0.0
    # variante: se o "estado" fosse o do código (code_estado), não o da mensagem
    com_nome_var_code = sum(1 for e in erros if e["tipo"] != "sem_nome" and e["code_estado"] in (None, "sem_corte_sql"))

    # ---- inventário
    inv = collections.defaultdict(list)
    for e in erros:
        inv[(e["tipo"], e["nome"] or "")].append(e)
    inventario = sorted(([t, nm, len(v), len({x["exec_id"] for x in v}), len({x["papel"] for x in v}),
                          len({x["mes"] for x in v})] for (t, nm), v in inv.items()), key=lambda x: (-x[2], x[0], x[1]))
    inv_papel = sorted(collections.Counter((e["nome"] or "", e["papel"]) for e in erros).items())
    inv_mes = sorted(collections.Counter((e["nome"] or "", e["mes"]) for e in erros).items())

    listas = collections.defaultdict(list)
    for e in erros:
        if e["lista"] is not None:
            listas[e["lista"]].append(e)
    listas_out = [{"lista": list(L), "erros": len(v), "papeis": sorted({x["papel"] for x in v}),
                   "meses": sorted({x["mes"] for x in v})} for L, v in sorted(listas.items())]

    # ---- passo 6
    grupos = collections.defaultdict(list)
    for e in erros:
        if e["nome"]:
            grupos[(e["exec_id"], e["papel"], e["nome"])].append(e["step_pos"])
    repet = {k: len(v) - 1 for k, v in grupos.items() if len(v) > 1}
    papeis_todos = sorted({e["papel"] for e in erros})
    meses_todos = sorted({e["mes"] for e in erros})

    # ---- passo 8 (o que é determinado pelo racional)
    ordem = sorted(erros, key=lambda e: (e["papel"], e["mes"], e["step_ref"]))
    location, vistos = [], set()
    for e in ordem:
        if e["papel"] not in vistos:
            vistos.add(e["papel"])
            location.append({"exec_id": e["exec_id"], "step_ref": e["step_ref"], "papel": e["papel"]})
    location = location[:10]
    por_tipo = collections.Counter(e["tipo"] for e in erros if e["tipo"] != "sem_nome")
    tres = [t for t, _ in sorted(por_tipo.items(), key=lambda x: (-x[1], x[0]))[:3]]
    evidence = []
    for t in tres:
        e = next(x for x in ordem if x["tipo"] == t)
        evidence.append({"exec_id": e["exec_id"], "step_ref": e["step_ref"], "tipo": t, "nome": e["nome"]})
    nomes_por_tipo = {}
    for rot, t in ROTULOS:
        c = collections.Counter(e["nome"] for e in erros if e["tipo"] == t)
        nomes_por_tipo[rot] = [nm for nm, _ in sorted(c.items(), key=lambda x: (-x[1], x[0]))]
        nomes_por_tipo[rot + " (contagens)"] = dict(c)

    # ---- emenda 4 (19/10): uma memória por parte; a parte sai do tipo e do nome do passo 4
    # emenda 9: C (global) = os módulos que estão em todas as listas autorizadas distintas; sem lista vista, todos
    if listas:
        modulos_c_global = set.intersection(*(set(L) for L in listas))
    else:
        modulos_c_global = None
    partes = collections.defaultdict(list)
    for e in erros:
        pt = parte_do_erro(e["tipo"], e["nome"], modulos_c_global)
        e["parte"] = pt
        if pt in GLOBAIS:
            mid = f"U_sandbox.{pt}"
        elif pt == "Cp":
            mid = f"U_sandbox.C.{e['papel']}"
        elif pt in ("B", "D"):
            mid = f"U_sandbox.{pt}.{e['papel']}"
        else:
            mid = None
        e["memoria"] = mid
        if mid:
            partes[mid].append(e)
    memorias = {}
    for mid, v in sorted(partes.items()):
        memorias[mid] = memoria_da_parte(mid, v, erros, a)
    sem_parte = sum(1 for e in erros if e["memoria"] is None)
    catalogo_esperado = sorted(m for m, d in memorias.items() if d["destino"] == "memória")

    perfil = next(csv.DictReader(open(a.perfil, encoding="utf-8", newline="")))

    out = {
        "fonte": {"linhas": linhas, "erros_estruturados_tipo_preenchido": estruturados,
                  "chaves_repetidas_com_papel": sum(1 for v in chaves_fonte.values() if v > 1)},
        "passo1": {
            "populacao_rodada": len(chave_rodada),
            "populacao_fonte_prosa": len(fonte),
            "so_na_rodada": [list(k) for k in so_rodada],
            "so_na_fonte": [list(k) for k in so_fonte],
            "braco_na_fonte": dict(collections.Counter(b for _, b in fonte.values())),
            "excluidos_por_sinal_antes": dict(excluidos_por_sinal),
            "execucoes": len({e["exec_id"] for e in erros}),
            "papeis": len(papeis_todos), "papeis_lista": papeis_todos,
            "meses": len(meses_todos), "meses_lista": meses_todos,
            "papel_igual_rodada": all(e["papel"] == e["papel_rodada"] for e in erros),
            "mes_igual_rodada": all(e["mes"] == e["mes_rodada"] for e in erros),
            "mensagem_achada_na_fonte": sum(e["msg_na_fonte"] for e in erros),
            "err_msg_estado": dict(collections.Counter(e["err_msg_estado"] for e in erros)),
            "code_estado": dict(collections.Counter(e["code_estado"] for e in erros)),
        },
        "passo4": {
            "erros_por_tipo": dict(collections.Counter(e["tipo"] for e in erros)),
            "inventario": [{"tipo": t, "nome": nm, "erros": ne, "execucoes": nx, "papeis": np_, "meses": nmes}
                           for t, nm, ne, nx, np_, nmes in inventario],
            "nome_x_papel": [{"nome": k[0], "papel": k[1], "erros": v} for k, v in inv_papel],
            "nome_x_mes": [{"nome": k[0], "mes": k[1], "erros": v} for k, v in inv_mes],
            "listas_autorizadas": listas_out,
            "linhas": [{k: e[k] for k in ("exec_id", "step_ref", "papel", "mes", "tipo", "nome")} for e in erros],
        },
        "passo5": {
            "com_nome": com_nome, "populacao": n, "cobertura": cobertura, "limiar": 0.95,
            "passa": cobertura >= 0.95,
            "sem_nome_por_primeira_palavra": dict(collections.Counter(
                e["sem_nome_primeira_palavra"] for e in erros if e["tipo"] == "sem_nome")),
            "variante_estado_do_codigo": {"com_nome": com_nome_var_code,
                                          "cobertura": com_nome_var_code / n if n else 0.0},
        },
        "passo6": {
            "listas_distintas": len(listas),
            "lista_unica_em_todos_papeis_e_meses": len(listas) == 1,
            "papeis_com_lista": sorted({p for v in listas.values() for p in (x["papel"] for x in v)}),
            "erros_com_lista": sum(len(v) for v in listas.values()),
            "grupos_exec_papel_nome": len(grupos),
            "grupos_com_repeticao": len(repet),
            "erros_repetidos_depois_do_primeiro": sum(repet.values()),
        },
        "passo8": {
            "location": location, "evidence": evidence,
            "correction_guidance_nomes": nomes_por_tipo,
            "occurrences_perfil": {k: perfil[k] for k in ("erros_observaveis", "ocorrencias_condicionais",
                                                          "execucoes", "meses", "papeis")},
        },
        "emenda4_partes": {
            "erros_por_parte": dict(collections.Counter(e["parte"] for e in erros)),
            "erros_sem_parte": sem_parte,
            "modulos_c_global": sorted(modulos_c_global) if modulos_c_global is not None else None,
            "memorias": memorias,
            "catalogo_esperado_se_derived_and_checked": catalogo_esperado,
        },
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
    with open(a.json, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"populacao_rodada": n, "populacao_fonte": len(fonte), "cobertura": round(cobertura, 4),
                      "listas": len(listas), "repetidos": sum(repet.values())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
