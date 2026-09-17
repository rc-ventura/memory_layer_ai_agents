# -*- coding: utf-8 -*-
"""
Ferramenta de triangulação: parte de um achado agregado (uma assinatura de erro,
uma família) e mostra o(s) caso(s) concreto(s) no trace cru que o sustentam.

Uso:
    python drill_down.py tutorial
        -> passo a passo guiado (pra quem tá usando o script pela 1ª vez, sem
           saber ainda o que quer procurar). Os outros comandos abaixo são a
           referência rápida; o tutorial explica o "por quê" de cada um.

    python drill_down.py amostra [n]
        -> lista n execuções/papéis quaisquer (default 10), sem filtro nenhum —
           use isto quando só quiser ver uma execução crua qualquer pra conferir
           com os próprios olhos, sem partir de um achado específico.

    python drill_down.py listar "Falha ao indexar o retorno (Could not index)"
        -> lista exec_id/role/mes candidatos pra essa assinatura (mensagem de erro/sintoma —
           pra buscar por MECANISMO, que é mais específico, use `mecanismo` abaixo)

    python drill_down.py planos [n]
        -> lista exec_id/role/mes das execuções que têm PlanningStep (o módulo de
           plano nativo do smolagents, ligado por `planning_interval` — hoje só em
           RespostaBacen e CalculoTrabalhista; ver 04-roadmap.md item 10)

    python drill_down.py mecanismo "Retorno pode chegar como string" [n]
        -> lista exec_id/role/mes/step dos erros atribuídos a esse MECANISMO (a unidade
           de memória da §9 do notebook), não a uma mensagem de erro. Lê
           resultados/erros_mecanismo.csv, gerado pelo notebook — rode o notebook antes.
           Nome errado imprime a lista de mecanismos disponíveis.

    python drill_down.py ferramenta validar_quebra_sigilo
        -> como o system prompt DECLARA essa ferramenta, no trace inteiro: cada variante
           do bloco `def ferramenta(...)` (assinatura, descrição, formato de retorno), com
           em quantos steps, execuções, meses e papéis ela aparece. Serve para conferir
           o que o prompt diz que a ferramenta devolve contra o que ela devolve de verdade
           (notebook §11.3; 03-procedimento-validacao.md §1.8). O bloco é documentação da
           ferramenta, não dado de caso — mas conferir antes de colar em documento.

    python drill_down.py evidencia [<análise>]
        -> completa as pastas resultados/evidencia/<análise>/ que a §11 do notebook grava
           (casos.csv, derivados/*.csv, leia-me.md): para cada caso de casos.csv, escreve
           crus/<exec_id>.json — a linha inteira do trace, sem alteração, só txt_etap_memo
           desserializado — e derivados/<exec>_<role>_idx<n>.json — a visão do caso para
           leitura humana, em que cada trecho é cópia do cru com o caminho onde ele está
           (conferido contra o cru ao gravar). Sem <análise>, todas as pastas.
           Ex.: python drill_down.py evidencia 11.4_conserto
           O cru é a fonte; a visão só espelha. Texto cru, com PII: resultados/ é
           git-ignored — não versionar. Ver 03-procedimento-validacao.md §1.8.

    python drill_down.py evidencia <exec_id> <role> <idx> <ferramenta>
        -> o mesmo para um caso qualquer, fora das análises: resultados/evidencia/avulso/.
           `idx` é a coluna `idx` do notebook (posição do ActionStep no papel, a partir de 0).

    python drill_down.py caso <exec_id> <role>
        -> imprime a trajetória inteira daquele papel naquela execução, na ordem
           em que aconteceu: PlanningStep (plano) quando existir, e pra cada
           ActionStep o thought, código, observação e erro — o material bruto por
           trás de qualquer número do relatório. Saída em texto formatado, campos
           longos truncados (pensada pra leitura rápida em auditoria).

    python drill_down.py caso <exec_id> <role> --json
        -> mesma trajetória, mas em JSON puro, sem truncar nada — cada step é o
           dict original completo (token_usage inteiro, tool_calls,
           model_input_messages, action_output, is_final_answer incluídos).
           Redirecionável: `python drill_down.py caso <exec_id> <role> --json >
           caso.json`. Mesma ressalva de PII: o arquivo gerado não deve ser
           commitado nem sair do ambiente local.

Requer o trace cru (85cb11b5-....csv.xz) em `../data/` (a pasta canônica é
`analysis/2026-09-trace-law-flow/data/`; resolvido pelo caminho do próprio
script, não pelo diretório corrente — corrigido 16/09/2026, auditoria M2).
Nunca commitar a saída deste script — ela reproduz nomes de clientes e
números de processo em claro.
"""
import sys, os, json, re, random
import pandas as pd

TRACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                      "85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz")

def classify(m):
    # Nomes sincronizados com classify() do notebook (§2) — renomeados 15/09/2026 (grupo 1:
    # os 4 nomes antigos afirmavam uma causa só parcialmente verdadeira; ver 01-racionais.md §7).
    if 'Could not index' in m: return 'Falha ao indexar o retorno (Could not index)'
    if 'does not support multiple positional' in m: return 'Argumento posicional onde só cabe nomeado'
    if 'unterminated' in m: return 'String não fechada (relatório longo em literal)'
    if 'regex pattern' in m: return 'Resposta sem bloco de código [INATIVO desde dez/2025]'
    if 'IndentationError' in m: return 'Indentação inválida'
    if 'leading zeros' in m: return 'Data DD/MM interpolada como número'
    if 'forgot a comma' in m or 'never closed' in m or 'invalid decimal' in m: return 'Texto do documento colado em literal'
    if 'SyntaxError' in m: return 'Sintaxe inválida'
    if 'is not defined' in m:
        v = re.search(r'variable `(\w+)`', m)
        if v and v.group(1) in {'json','pd','np','re','os','math','datetime'}: return 'Módulo usado sem import'
        return 'Variável não definida'
    if 'has no attribute' in m: return 'Objeto sem o atributo esperado'
    if 'not allowed' in m or 'explicitly allowed' in m or 'is not permitted' in m: return 'Função ou import bloqueado pelo sandbox'
    if 'ModuleNotFound' in m: return 'Módulo ausente no sandbox'
    if 'Forbidden' in m: return 'Operação proibida'
    if 'AgentGenerationError' in m or 'internally hosted' in m: return 'Falha do LLM interno'
    if 'Error code: 422' in m or 'UnprocessableEntity' in m: return 'HTTP 422'
    if 'JSONDecode' in m: return 'Retorno não era JSON'
    if 'KeyError' in m: return 'Campo ausente no retorno'
    if 'TypeError' in m: return 'Tipo diferente do esperado'
    if 'ValueError' in m: return 'Formato/valor inválido'
    if 'IndexError' in m: return 'Retorno vazio indexado'
    return 'Erro não classificado'

def tutorial():
    """Passo a passo guiado, pra quem tá usando o script pela 1ª vez sem saber
    ainda o que quer procurar. Os comandos aqui já são os reais — copia e roda."""
    print(f"""
{'='*78}
TUTORIAL — drill_down.py, passo a passo
{'='*78}

Passo 1 — encontre um caso aleatório
  python drill_down.py amostra 5

  Saída: 5 linhas tipo `exec_id=... role=... data=... N ActionStep`.
  Escolha qualquer uma. (Se quiser especificamente um caso que tenha
  PlanningStep — o achado de 14/09 — use `python drill_down.py planos 5` no
  lugar deste passo; funciona igual dali em diante.)

Passo 2 — pegue o exec_id
  Copie o valor depois de `exec_id=` da linha que você escolheu.

Passo 3 — escolha a role
  A linha já trouxe uma role junto (mais simples, usa essa). Mas como uma
  execução tem VÁRIOS papéis (a esteira é multiagente), se quiser ver a lista
  completa de quem participou daquele exec_id, chute uma role errada de
  propósito:
    python drill_down.py caso <exec_id> x
  Ele não vai achar "x" e vai responder "Papéis disponíveis: [...]" — aí você
  escolhe de verdade.

Passo 4 — rode em JSON, salvando em arquivo
  python drill_down.py caso <exec_id> <role> --json > caso.json

Passo 5 — abra o caso.json
  No editor, ou no terminal:
    python -m json.tool caso.json | less

Passo 6 — o que olhar dentro do JSON
  Estrutura: {{"exec_id", "role", "status", "data", "steps": [...]}}.
  Pra cada item de `steps`, olhe o campo `__class__`:
    "PlanningStep" -> tem o campo `plan` (o achado de 14/09)
    "ActionStep"   -> tem `model_output` (thought), `code_action` (o que ele
                      rodou), `observations` (o que voltou), `error` (se
                      quebrou), `model_input_messages` (o prompt cru enviado
                      ao LLM), `tool_calls`, `token_usage`, `is_final_answer`

Passo 7 — quer ver outro papel da mesma execução?
  Repete o passo 4 trocando só a role (o exec_id continua o mesmo), salvando
  num arquivo diferente:
    python drill_down.py caso <exec_id> managerAgent --json > caso_manager.json

Passo 8 — depois de olhar, apaga
  caso*.json tem PII em claro (nome de cliente, nº de processo). Já está no
  .gitignore desta pasta, mas mesmo assim: `rm caso*.json` quando terminar —
  não é pra ficar solto no disco além do necessário.
{'='*78}
""")

def bloco_da_ferramenta(prompt, fn):
    # Sincronizada com a célula 11.0 do notebook: do `def fn(` até o próximo `def ` do prompt.
    m = re.search(r"def\s+" + re.escape(fn) + r"\s*\(", prompt)
    if not m:
        return ""
    fim = re.search(r"\ndef\s+\w+\s*\(", prompt[m.end():])
    return prompt[m.start(): m.end() + fim.start()] if fim else prompt[m.start():]

def system_prompt(st):
    # Mesma extração da §1 do notebook: a PRIMEIRA mensagem do contexto, onde as ferramentas são declaradas.
    mim = st.get("model_input_messages")
    if not mim:
        return ""
    m0 = mim[0] if isinstance(mim[0], dict) else {}
    c = m0.get("content")
    return c[0].get("text", "") if isinstance(c, list) and c and isinstance(c[0], dict) else str(c or "")

def texto_msg(m):
    c = m.get("content")
    if isinstance(c, list):
        return "".join(x.get("text", "") for x in c if isinstance(x, dict))
    return str(c or "")

def load():
    return pd.read_csv(TRACE, dtype=str)

def amostra(n=10):
    """Sem filtro: qualquer (exec_id, role) com pelo menos um ActionStep, pra olhar
    uma execução crua qualquer sem partir de um achado específico."""
    df = load()
    sub = df[df["txt_etap_memo"].notna()]
    found = []
    for _, r in sub.iterrows():
        try: memo = json.loads(r["txt_etap_memo"])
        except Exception: continue
        for role, steps in memo.items():
            if not isinstance(steps, list): continue
            n_action = sum(1 for s in steps if isinstance(s, dict) and s.get("__class__") == "ActionStep")
            if n_action > 0:
                found.append((r["cod_idef_exeo"], role, r["anomesdia"], n_action))
    random.shuffle(found)
    print(f"{len(found)} pares (exec_id, role) com ActionStep no trace inteiro. Amostra aleatória de {min(n,len(found))}:\n")
    for eid, role, dt, n_action in found[:n]:
        print(f"  exec_id={eid}  role={role}  data={dt}  {n_action} ActionStep")
    print(f"\nPara ver o caso completo:\n  python drill_down.py caso <exec_id> <role>")

def listar(assinatura, n=8):
    df = load()
    sub = df[df["txt_etap_memo"].notna()]
    found = []
    for _, r in sub.iterrows():
        try: memo = json.loads(r["txt_etap_memo"])
        except Exception: continue
        for role, steps in memo.items():
            if not isinstance(steps, list): continue
            for st in steps:
                if not isinstance(st, dict): continue
                e = st.get("error") or {}
                if not e: continue
                if classify(str(e.get("message", ""))) == assinatura:
                    found.append((r["cod_idef_exeo"], role, r["anomesdia"], st.get("step_number")))
    print(f"'{assinatura}': {len(found)} ocorrências. Amostra de {min(n,len(found))}:\n")
    for eid, role, dt, step in found[:n]:
        print(f"  exec_id={eid}  role={role}  data={dt}  step={step}")
    print(f"\nPara ver o caso completo:\n  python drill_down.py caso <exec_id> <role>")

def planos(n=20):
    """Lista execuções/papéis que têm PlanningStep — o módulo de plano nativo do
    smolagents (planning_interval), hoje descartado pelo caso()/classify() antigos.
    Ver 04-roadmap.md item 10."""
    df = load()
    sub = df[df["txt_etap_memo"].notna()]
    found = []
    for _, r in sub.iterrows():
        try: memo = json.loads(r["txt_etap_memo"])
        except Exception: continue
        for role, steps in memo.items():
            if not isinstance(steps, list): continue
            n_plan = sum(1 for s in steps if isinstance(s, dict) and s.get("__class__") == "PlanningStep")
            if n_plan > 0:
                found.append((r["cod_idef_exeo"], role, r["anomesdia"], n_plan))
    print(f"{len(found)} pares (exec_id, role) com PlanningStep. Amostra de {min(n,len(found))}:\n")
    for eid, role, dt, n_plan in found[:n]:
        print(f"  exec_id={eid}  role={role}  data={dt}  {n_plan} PlanningStep")
    print(f"\nPara ver o caso completo (o plano aparece inline na trajetória):\n  python drill_down.py caso <exec_id> <role>")

def mecanismo(nome, n=8):
    """Lista casos de um mecanismo de erro (unidade de memória da §9 do notebook), não de uma
    mensagem. Usa resultados/erros_mecanismo.csv, exportado pelo notebook."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados", "erros_mecanismo.csv")
    if not os.path.exists(p):
        print("resultados/erros_mecanismo.csv não existe — rode o notebook inteiro antes."); return
    m = pd.read_csv(p, dtype=str)
    sub = m[m["unidade_nome"] == nome]
    if sub.empty:
        print(f"mecanismo '{nome}' não encontrado. Disponíveis:")
        for u, c in m["unidade_nome"].value_counts().items():
            print(f"  {c:4d}  {u}")
        return
    print(f"'{nome}': {len(sub)} erros em {sub['exec_id'].nunique()} execuções. Amostra de {min(n, len(sub))}:\n")
    for r in sub.head(n).itertuples():
        apos = "  (logo após outro erro)" if r.seguidor == "True" else ""
        print(f"  exec_id={r.exec_id}  role={r.role}  data={r.mes}  step={r.step}  mensagem='{r.assinatura}'{apos}")
    print(f"\nPara ver o caso completo:\n  python drill_down.py caso <exec_id> <role>")

def ferramenta(nome):
    """Variantes do bloco `def nome(...)` no system prompt (a PRIMEIRA mensagem do contexto de cada ActionStep —
    mesma extração da §1 do notebook), no trace inteiro, com steps/execuções/meses/papéis de cada uma."""
    df = load()
    variantes = {}
    for _, r in df[df["txt_etap_memo"].notna()].iterrows():
        try: memo = json.loads(r["txt_etap_memo"])
        except Exception: continue
        for role, steps in memo.items():
            if not isinstance(steps, list): continue
            for st in steps:
                if not isinstance(st, dict) or st.get("__class__") != "ActionStep": continue
                b = bloco_da_ferramenta(system_prompt(st), nome)
                if not b: continue
                v = variantes.setdefault(b, {"steps": 0, "execs": set(), "meses": set(), "papeis": set()})
                v["steps"] += 1; v["execs"].add(r["cod_idef_exeo"]); v["meses"].add(r["anomesdia"][:6]); v["papeis"].add(role)
    if not variantes:
        print(f"nenhum system prompt declara `def {nome}(...)`."); return
    todos = set().union(*(v["execs"] for v in variantes.values()))
    print(f"`{nome}`: {len(variantes)} variante(s) do bloco, em {sum(v['steps'] for v in variantes.values())} steps de "
          f"{len(todos)} execuções.\n")
    for i, (b, v) in enumerate(sorted(variantes.items(), key=lambda kv: -kv[1]["steps"]), 1):
        meses = sorted(v["meses"])
        print(f"{'='*100}\nvariante {i}: {v['steps']} steps · {len(v['execs'])} execuções · {len(meses)} meses "
              f"({meses[0]}..{meses[-1]}) · papéis: {', '.join(sorted(v['papeis']))}\n{'='*100}")
        print(b.rstrip() + "\n")

PASTA_EVIDENCIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados", "evidencia")

def vazio_se_nan(v):
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)

def resolver(obj, caminho):
    for k in caminho:
        obj = obj[k]
    return obj

def gravar_cru(pasta, r, linha):
    """A linha inteira do trace, sem alteração: só `txt_etap_memo` é desserializado (json.loads), para dar pra ler e
    apontar caminhos dentro dele."""
    out = {"_origem": {"arquivo": "data/85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz", "linha_de_dados": int(linha),
                       "nota": "cópia literal da linha do trace; só txt_etap_memo foi desserializado (json.loads), "
                               "sem nenhuma outra alteração"}}
    for col, v in r.items():
        if pd.isna(v):
            out[col] = None
        elif col == "txt_etap_memo":
            out[col] = json.loads(v)
        else:
            out[col] = v
    os.makedirs(os.path.join(pasta, "crus"), exist_ok=True)
    with open(os.path.join(pasta, "crus", f"{r['cod_idef_exeo']}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return out

def visao_do_caso(analise, caso, cru):
    """Visão derivada de UM caso. Cada trecho é cópia de uma parte do cru e diz onde ela está (`cru`: o caminho dentro
    de crus/<exec_id>.json; `caracteres`: o recorte, quando é pedaço de um texto). Campos calculados dizem a regra."""
    import ast
    exec_id, role, idx = caso["exec_id"], caso["role"], int(caso["idx"])
    ferramenta = vazio_se_nan(caso.get("ferramenta"))
    lista = cru["txt_etap_memo"][role]
    pos = [i for i, s in enumerate(lista) if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
    trechos = []

    def trecho(o_que, caminho, **extra):
        trechos.append({"o_que": o_que, "cru": caminho, **extra})

    p = pos[idx]
    st = lista[p]
    base = ["txt_etap_memo", role, p]
    cam_sys = base + ["model_input_messages", 0, "content", 0, "text"]
    try:
        sysp = resolver(cru, cam_sys)
    except (KeyError, IndexError, TypeError):
        sysp = ""
    if ferramenta and sysp:
        bloco = bloco_da_ferramenta(sysp, ferramenta)
        if bloco:
            ini = sysp.index(bloco)
            trecho(f"bloco em que `{ferramenta}` é declarada no system prompt enviado ao agente neste step", cam_sys,
                   caracteres=[ini, ini + len(bloco)], texto=bloco)
            for m in re.finditer(r"[^\n]*" + re.escape(ferramenta) + r"[^\n]*", sysp):
                if ini <= m.start() < ini + len(bloco):
                    continue
                trecho(f"outra linha do system prompt que cita `{ferramenta}`", cam_sys,
                       caracteres=[m.start(), m.end()], texto=m.group(0))
        else:
            trecho(f"`{ferramenta}` não está declarada no system prompt deste step", cam_sys, texto=None)
    # o step em que a ferramenta foi chamada por último, se foi antes do step do erro
    if ferramenta:
        chamadas = [j for j in range(idx) if re.search(r"\b" + re.escape(ferramenta) + r"\s*\(", lista[pos[j]].get("code_action") or "")]
        if chamadas:
            j = chamadas[-1]
            for campo in ("code_action", "observations"):
                trecho(f"step idx {j}: {campo} (última chamada de `{ferramenta}` antes do erro)",
                       ["txt_etap_memo", role, pos[j], campo], texto=lista[pos[j]].get(campo))
    for campo in ("model_output", "code_action", "observations"):
        trecho(f"step do erro (idx {idx}): {campo}", base + [campo], texto=st.get(campo))
    trecho(f"step do erro (idx {idx}): mensagem de erro", base + ["error", "message"], texto=(st.get("error") or {}).get("message"))
    if idx + 1 < len(pos):
        p2 = pos[idx + 1]
        st2 = lista[p2]
        msgs = st2.get("model_input_messages") or []
        ult = max((i for i, m in enumerate(msgs) if m.get("role") == "assistant"), default=None)
        if ult is not None:
            trecho(f"o que o agente leu antes do step seguinte (mensagens depois da sua última resposta)",
                   ["txt_etap_memo", role, p2, "model_input_messages"], mensagens=[ult, len(msgs)],
                   texto=[{"role": m.get("role"), "texto": texto_msg(m)} for m in msgs[ult:]])
        for campo in ("model_output", "code_action"):
            trecho(f"step seguinte (idx {idx + 1}): {campo}", ["txt_etap_memo", role, p2, campo], texto=st2.get(campo))
        trecho(f"step seguinte (idx {idx + 1}): mensagem de erro", ["txt_etap_memo", role, p2, "error", "message"],
               texto=(st2.get("error") or {}).get("message"))

    # conferência: cada trecho tem de ser igual ao cru no caminho indicado
    ok = 0
    for t in trechos:
        try:
            v = resolver(cru, t["cru"])
        except (KeyError, IndexError, TypeError):
            v = None
        if "caracteres" in t:
            v = v[t["caracteres"][0]: t["caracteres"][1]] if isinstance(v, str) else None
        elif "mensagens" in t:
            v = [{"role": m.get("role"), "texto": texto_msg(m)} for m in v[t["mensagens"][0]: t["mensagens"][1]]]
        if t["texto"] is None or v == t["texto"]:
            ok += 1
        else:
            raise AssertionError(f"trecho diverge do cru: {t['o_que']} em {t['cru']}")

    # calculados — não são texto do trace
    msg = (st.get("error") or {}).get("message") or ""
    pedida = re.findall(r"KeyError: ('(?:[^'\\]|\\.)*'|-?\d+)", msg)
    mi = re.search(r"Could not index (.*) with '(.*?)': ", msg, re.S)
    chaves_obj = []
    if mi:
        try:
            o = ast.literal_eval(mi.group(1))
            chaves_obj = sorted(o) if isinstance(o, dict) else []
        except Exception:
            chaves_obj = sorted(set(re.findall(r"'(\w+)':", mi.group(1))))
    procurar = [k for k in vazio_se_nan(caso.get("chaves")).split(";") if k] or chaves_obj

    def onde(s):
        msgs = (s or {}).get("model_input_messages") or []
        return [{"chave": k,
                 "declarada_como_chave_no_system_prompt": bool(re.search(r"['\"]" + re.escape(k) + r"['\"]\s*:", texto_msg(msgs[0]) if msgs else "")),
                 "mensagens_depois_do_system_prompt": [{"mensagem": i, "role": m.get("role")}
                                                       for i, m in enumerate(msgs) if i > 0 and f"'{k}'" in texto_msg(m)]}
                for k in procurar]

    seguinte = lista[pos[idx + 1]] if idx + 1 < len(pos) else None
    calculados = {
        "chave_pedida_pelo_agente": {"valor": [ast.literal_eval(x) for x in pedida[-1:]], "regra": "último `KeyError: <chave>` da mensagem de erro"},
        "chaves_de_topo_do_objeto_na_mensagem": {"valor": chaves_obj, "regra": "ast.literal_eval do objeto em `Could not index <objeto> with`"},
        "onde_as_chaves_aparecem_no_contexto": {
            "regra": "presença literal de 'chave' em cada mensagem do contexto (model_input_messages) — antes: contexto do step do erro; depois: do step seguinte",
            "antes_do_erro": onde(st), "depois_do_erro": onde(seguinte) if seguinte else None},
    }
    colunas = {k: (None if isinstance(v, float) and pd.isna(v) else v.item() if hasattr(v, "item") else v) for k, v in caso.items()}
    return {
        "_leia": "Visão derivada de UM caso, para leitura humana. Cada trecho é cópia de uma parte do cru: `cru` é o caminho "
                 "dentro do arquivo cru, `caracteres` o recorte de um texto, `mensagens` o intervalo de mensagens. Os trechos "
                 f"foram conferidos contra o cru ao gravar ({ok}/{len(trechos)} iguais). `calculados` não é texto do trace. "
                 "Em dúvida, vale o cru.",
        "analise": analise, "arquivo_cru": f"crus/{exec_id}.json",
        "caso_segundo_o_notebook": {"nota": "colunas de casos.csv, calculadas pelo notebook", **colunas},
        "posicao_no_cru": {"papel": role, "idx_actionstep": idx, "indice_na_lista_do_papel": p, "step_number": st.get("step_number")},
        "trechos_do_cru": trechos,
        "calculados": calculados,
    }, ok, len(trechos)

def evidencia(analise=None):
    """Completa as pastas de evidência a partir do casos.csv que o notebook gravou: crus/<exec_id>.json (a linha inteira
    do trace) e derivados/<exec>_<role>_idx<n>.json (a visão de cada caso, conferida contra o cru). Sem argumento, todas
    as pastas que têm casos.csv."""
    pastas = sorted(d for d in os.listdir(PASTA_EVIDENCIA) if os.path.exists(os.path.join(PASTA_EVIDENCIA, d, "casos.csv"))) \
        if analise is None else [analise]
    if not pastas or not os.path.exists(os.path.join(PASTA_EVIDENCIA, pastas[0], "casos.csv")):
        print(f"nenhum casos.csv em {PASTA_EVIDENCIA}/{analise or '*'} — rode a §11 do notebook antes."); return
    casos = {d: pd.read_csv(os.path.join(PASTA_EVIDENCIA, d, "casos.csv"), dtype={"exec_id": str, "role": str}) for d in pastas}
    ids = set().union(*(set(c["exec_id"]) for c in casos.values()))
    df = load()
    linhas = {r["cod_idef_exeo"]: (i, r) for i, r in df[df["cod_idef_exeo"].isin(ids)].iterrows()}
    for d in pastas:
        pasta = os.path.join(PASTA_EVIDENCIA, d)
        os.makedirs(os.path.join(pasta, "crus"), exist_ok=True)
        crus, ok_tot, n_tot = {}, 0, 0
        for _, caso in casos[d].iterrows():
            eid = caso["exec_id"]
            if eid not in crus:
                i, r = linhas[eid]
                crus[eid] = gravar_cru(pasta, r, i)
            visao, ok, n = visao_do_caso(d, caso.to_dict(), crus[eid])
            ok_tot, n_tot = ok_tot + ok, n_tot + n
            os.makedirs(os.path.join(pasta, "derivados"), exist_ok=True)
            with open(os.path.join(pasta, "derivados", f"{eid[:8]}_{caso['role']}_idx{int(caso['idx'])}.json"), "w", encoding="utf-8") as f:
                json.dump(visao, f, ensure_ascii=False, indent=2)
        tam = sum(os.path.getsize(os.path.join(pasta, "crus", x)) for x in os.listdir(os.path.join(pasta, "crus")))
        print(f"{d}: {len(casos[d])} casos · {len(crus)} crus ({tam / 1e6:.1f} MB) · trechos conferidos contra o cru: {ok_tot}/{n_tot}")

def evidencia_avulsa(exec_id, role, idx, ferramenta):
    """Um caso qualquer, fora das análises do notebook: grava em resultados/evidencia/avulso/."""
    pasta = os.path.join(PASTA_EVIDENCIA, "avulso")
    df = load()
    sel = df[df["cod_idef_exeo"] == exec_id]
    if sel.empty:
        print(f"exec_id {exec_id} não encontrado (use o exec_id inteiro)."); return
    i, r = sel.index[0], sel.iloc[0]
    cru = gravar_cru(pasta, r, i)
    caso = {"exec_id": exec_id, "role": role, "idx": idx, "ferramenta": ferramenta, "motivo": "avulso"}
    visao, ok, n = visao_do_caso("avulso", caso, cru)
    os.makedirs(os.path.join(pasta, "derivados"), exist_ok=True)
    arq = os.path.join(pasta, "derivados", f"{exec_id[:8]}_{role}_idx{idx}.json")
    with open(arq, "w", encoding="utf-8") as f:
        json.dump(visao, f, ensure_ascii=False, indent=2)
    print(f"gravado: {os.path.relpath(arq)} e crus/{exec_id}.json · trechos conferidos contra o cru: {ok}/{n}")

def caso(exec_id, role, as_json=False):
    df = load()
    row = df[df["cod_idef_exeo"] == exec_id]
    if row.empty:
        print(f"exec_id {exec_id} não encontrado."); return
    r = row.iloc[0]
    memo = json.loads(r["txt_etap_memo"])
    all_steps = memo.get(role, [])
    # Inclui PlanningStep junto com ActionStep, na ordem original em que aparecem —
    # antes só ActionStep entrava aqui, e todo PlanningStep (o plano nativo do
    # smolagents, ligado por planning_interval) era descartado em silêncio.
    steps = [s for s in all_steps if isinstance(s, dict) and s.get("__class__") in ("ActionStep", "PlanningStep")]
    if not steps:
        print(f"papel '{role}' não tem ActionStep/PlanningStep nesta execução. Papéis disponíveis: {list(memo.keys())}")
        return

    if as_json:
        # Estrutura crua completa, sem truncar nenhum campo — inclusive os que a
        # versão formatada abaixo não mostra (token_usage inteiro, tool_calls,
        # model_input_messages, action_output, is_final_answer). Saída é um único
        # objeto JSON válido, pronta pra `> arquivo.json` ou outra ferramenta.
        # Mesma ressalva de sempre: contém PII em claro, só terminal local.
        out = {
            "exec_id": exec_id,
            "role": role,
            "status": r["cod_idef_stat_exeo_aget"],
            "data": r["anomesdia"],
            "steps": steps,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
        return

    n_plan = sum(1 for s in steps if s.get("__class__") == "PlanningStep")
    n_action = len(steps) - n_plan
    print(f"{'='*100}\nexec_id={exec_id}  role={role}  status={r['cod_idef_stat_exeo_aget']}  "
          f"data={r['anomesdia']}  {len(steps)} steps ({n_action} ActionStep + {n_plan} PlanningStep)\n{'='*100}\n")
    for st in steps:
        tu = st.get("token_usage") or {}
        if st.get("__class__") == "PlanningStep":
            plan = str(st.get("plan") or "")[:800]
            print(f"--- PLANNING STEP (tokens={tu.get('total_tokens','?')}) ---")
            print(f"\n[PLANO]\n{plan}\n")
            continue
        e = st.get("error") or {}
        print(f"--- STEP {st.get('step_number')} "
              f"({'ERRO' if e else 'ok'}  tokens={tu.get('total_tokens','?')}) ---")
        thought = str(st.get("model_output") or "")[:500]
        print(f"\n[THOUGHT]\n{thought}")
        code = str(st.get("code_action") or "")[:500]
        print(f"\n[CÓDIGO]\n{code}")
        if e:
            print(f"\n[ERRO] {classify(str(e.get('message','')))}")
            print(str(e.get("message", ""))[:600])
        obs = str(st.get("observations") or "")[:400]
        print(f"\n[OBSERVAÇÃO]\n{obs}")
        print()
    print(f"{'='*100}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "tutorial":
        tutorial()
    elif cmd == "amostra":
        amostra(int(sys.argv[2]) if len(sys.argv) > 2 else 10)
    elif cmd == "listar":
        listar(sys.argv[2])
    elif cmd == "planos":
        planos(int(sys.argv[2]) if len(sys.argv) > 2 else 20)
    elif cmd == "mecanismo":
        mecanismo(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
    elif cmd == "ferramenta":
        ferramenta(sys.argv[2])
    elif cmd == "evidencia":
        if len(sys.argv) >= 6:
            evidencia_avulsa(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])
        else:
            evidencia(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "caso":
        args = [a for a in sys.argv[2:] if a != "--json"]
        as_json = "--json" in sys.argv[2:]
        caso(args[0], args[1], as_json=as_json)
    else:
        print(__doc__)
