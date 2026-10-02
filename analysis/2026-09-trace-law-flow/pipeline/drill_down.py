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
           (notebook mineracao_unidades_n2_n10.ipynb §11.3; 03-procedimento-validacao.md §1.8). O bloco é documentação da
           ferramenta, não dado de caso — mas conferir antes de colar em documento.

    python drill_down.py evidencia [<análise>]
        -> completa as pastas resultados/evidencia/<análise>/ que a §11 do notebook mineracao_unidades_n2_n10.ipynb grava
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

    python drill_down.py relogios
        -> resultados/evidencia/A3_relogios/: para cada execução, as três datas de fontes
           independentes — `anomesdia`, `dat_hor_inio_exeo` e o `timing` dos steps (gravado
           pelo runtime) — mais o cruzamento mês da partição × mês real e os crus de uma
           regra de escolha escrita. Sustenta que `anomesdia` não é a data da execução.
           Imprime só contagens. Leia o leia-me.md da pasta.

    python drill_down.py residuo
        -> resultados/evidencia/A5_residuo/: todos os erros que nenhuma regra de causa reconheceu
           (unidades X_), com a classe de cada um e a frase da exceção mascarada, mais os crus.
           Lê resultados/erros_mecanismo.csv — rode o notebook antes. Imprime só contagens.

    python drill_down.py padrao ["<trecho do padrão>"]
        -> os casos de um padrão de erro do resíduo (exec_id/role/idx/mês), para o passo 1 do
           procedimento de revisão (03-procedimento-validacao.md, Frente 3). Sem argumento, lista
           os padrões com erros, execuções e meses. Lê resultados/erros_mecanismo.csv.

    python drill_down.py tempo [<role>] [--mecanismo=a,b]
        -> quem gastou os 30 s? Para cada erro de tempo do interpretador (timeout_interpretador, codigo_lento,
           resultado_bruto_na_resposta):
           tamanhos em jogo, estrutura do código do step (laços, chamadas), o que ia para o final_answer e o que o
           agente fez depois no papel; por papel, os final_answer que deram certo, para comparar. Para cada laço,
           a linha e o que se repete a cada volta × o que roda uma vez (ferramenta dentro de laço?). Só números e
           nomes — sem texto de caso nem exec_id. `--mecanismo=` troca os mecanismos (para testar em outra base).
           Lê resultados/erros_mecanismo.csv. Ver pipeline-entre-bases.md, Etapa 5b.

    python drill_down.py protocolo
        -> "resposta sem bloco de código" (H_bloco_code): por mês e papel (erros, por 1k steps, gatilho), o que o LLM
           escreveu no lugar do bloco (só a forma), recuperação e cascata. Só contagens; os casos com exec_id vão para
           resultados/evidencia/protocolo/casos.csv. [7]: as versões do system prompt por papel (hash), com meses,
           erros e o modo (JSON estruturado × texto com <code>); [8]: o modelo que respondeu (raw.model) e a versão
           do agente (cod_vers_aget), com meses, steps e erros; [9]: o M1 — o texto escrito no lugar do bloco
           reaparece na resposta final entregue depois (antecipou) ou veio da observação anterior (sobreposicao(),
           M1_LIMIAR). Ver pipeline-entre-bases.md, Ajuste 10b; 10-racionais-protocolo-harness.md §4 M1.

    python drill_down.py protocolo --prompt <versão>
        -> grava o texto daquela versão do system prompt em resultados/evidencia/protocolo/ para ler na máquina.

    python drill_down.py protocolo --casos <papel> [<versão>] [<quantos>]
        -> um arquivo por erro do papel (e da versão, se dada; padrão 3 erros, alternando as formas) com, na ordem: o
           system prompt exato do step, a observação anterior, o que o modelo escreveu no lugar do código, o erro, o
           step seguinte e a resposta final. Rode `protocolo` antes. Caso em claro: ler na máquina.

    python drill_down.py silenciosas [<ferramenta>]
        -> falhas silenciosas de ferramenta: "Error calling tool '<nome>'" na observação com error: null (o step conta
           como ok, mas a ferramenta falhou). [1] por ferramenta: steps, falhas com exceção, silenciosas, papéis,
           meses; [2] o 1º erro do mesmo papel depois de cada falha; [3] quanto dos erros de contrato de retorno
           (U_tipo_retorno, U_contrato_dict, U_campo_inexistente) vem logo depois de uma falha silenciosa; [4] papéis
           que entregaram final_answer depois da falha sem chamada bem-sucedida (candidato a sucesso falso). Só
           números e nomes; casos em resultados/evidencia/silenciosas/casos.csv. Função: falhas_silenciosas().

    python drill_down.py silenciosas --motivos [<ferramenta>]
        -> os motivos das falhas de ferramenta, por ferramenta, mascarados (o que está entre aspas e depois de '=' vira
           <v>, dígito vira 9, 60 caracteres): sobra o texto que o dev da ferramenta escreveu. Pode ser fotografado.

    python drill_down.py silenciosas --forma <ferramenta>
        -> em cada falha silenciosa da ferramenta, como o 1º argumento foi passado — json.dumps, str(...), dict ou
           string montados à mão, variável devolvida por outra ferramenta — só a contagem por tipo, sem conteúdo.
           Decide o dono do json_invalido (agente × ferramenta). Abre o str(...) e separa o literal colado de um
           retorno impresso (mesmo critério do repr_colado: ≥2 chaves já impressas antes no papel) do montado à mão.

    python drill_down.py critico [<papel>]
        -> os erros críticos (o papel esgotou os passos): uma linha por execução morta — papel, mês, idx do crítico,
           steps, erros antes, primeira unidade, unidades no caminho —, se a execução tem "resposta sem bloco de
           código" (quantos e em que idx) e a trajetória do papel step a step, só o tipo (ok ou unidade do erro),
           com repetições agrupadas. Só números e nomes — sem texto de caso nem exec_id; pode ser fotografada.
           Lê resultados/criticos.csv (ou recalcula com caminho_dos_criticos) e resultados/erros_mecanismo.csv.
           Ver 12-procedimento-protocolo-harness.md e o item 39 do roadmap.

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
import sys, os, json, re, random, ast
from collections import Counter
import pandas as pd

from base_pipeline import TRACE, classify as _bp_classify

def classify(m):
    # Assinatura do par (família, assinatura) que base_pipeline.classify retorna —
    # mesma classificação dos notebooks, sem cópia local (antes sincronizada à mão).
    return _bp_classify(m)[1]

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
                found.append((r["cod_idef_exeo"], role, r["dat_hor_inio_exeo"][:10], n_action))
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
                    found.append((r["cod_idef_exeo"], role, r["dat_hor_inio_exeo"][:10], st.get("step_number")))
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
                found.append((r["cod_idef_exeo"], role, r["dat_hor_inio_exeo"][:10], n_plan))
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
                v["steps"] += 1; v["execs"].add(r["cod_idef_exeo"]); v["meses"].add(r["dat_hor_inio_exeo"][:7]); v["papeis"].add(role)
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
    """Completa as pastas de evidência a partir do casos.csv que o notebook de mineração gravou: crus/<exec_id>.json (a linha inteira
    do trace) e derivados/<exec>_<role>_idx<n>.json (a visão de cada caso, conferida contra o cru). Sem argumento, todas
    as pastas que têm casos.csv."""
    def por_step(d):  # só as pastas da §11 da mineração; A3_relogios e A5_residuo têm comando próprio
        arq = os.path.join(PASTA_EVIDENCIA, d, "casos.csv")
        return d.startswith("11.") and os.path.exists(arq) and {"role", "idx"} <= set(pd.read_csv(arq, nrows=0).columns)
    pastas = sorted(d for d in os.listdir(PASTA_EVIDENCIA) if por_step(d)) if analise is None else [analise]
    if not pastas or not os.path.exists(os.path.join(PASTA_EVIDENCIA, pastas[0], "casos.csv")):
        print(f"nenhum casos.csv em {PASTA_EVIDENCIA}/{analise or '*'} — rode a §11 do notebook mineracao_unidades_n2_n10.ipynb antes."); return
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
    """Um caso qualquer, fora das análises do notebook de mineração: grava em resultados/evidencia/avulso/."""
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

def _timing(memo_txt):
    """Menor start_time e maior end_time (epoch, gravados pelo runtime do agente) entre todos os steps do JSON."""
    if pd.isna(memo_txt):
        return None, None
    try:
        memo = json.loads(memo_txt)
    except Exception:
        return None, None
    ini, fim = [], []
    for passos in memo.values():
        if not isinstance(passos, list):
            continue
        for st in passos:
            tm = (st.get("timing") or {}) if isinstance(st, dict) else {}
            if isinstance(tm.get("start_time"), (int, float)): ini.append(tm["start_time"])
            if isinstance(tm.get("end_time"), (int, float)): fim.append(tm["end_time"])
    return (min(ini) if ini else None), (max(fim) if fim else None)

def relogios():
    """Evidência do Ajuste 3: três relógios por execução, de fontes independentes — `anomesdia` (coluna),
    `dat_hor_inio_exeo` (coluna) e `timing` dos steps (gravado pelo runtime dentro de txt_etap_memo). Não usa o
    código de classificação; só o `h_bloco_code.csv` lê resultados/erros_mecanismo.csv (rode o notebook antes).
    Grava resultados/evidencia/A3_relogios/ e imprime só contagens."""
    pasta = os.path.join(PASTA_EVIDENCIA, "A3_relogios")
    os.makedirs(os.path.join(pasta, "derivados"), exist_ok=True)
    df = load()
    tm = df["txt_etap_memo"].map(_timing)
    R = pd.DataFrame({
        "exec_id": df["cod_idef_exeo"], "linha_de_dados": df.index,
        "anomesdia": df["anomesdia"], "dat_hor_inio_exeo": df["dat_hor_inio_exeo"],
        "timing_min": pd.to_datetime([t[0] for t in tm], unit="s"),
        "timing_max": pd.to_datetime([t[1] for t in tm], unit="s"),
    })
    part = pd.to_datetime(R["anomesdia"], format="%Y%m%d")
    ini = pd.to_datetime(R["dat_hor_inio_exeo"])
    R["delta_dias"] = ((part - ini).dt.total_seconds() / 86400).round(2)          # partição − início
    R["delta_coluna_timing_h"] = ((ini - R["timing_min"]).dt.total_seconds() / 3600).round(3)
    R["mes_particao"] = part.dt.to_period("M").astype(str)
    R["mes_exec"] = ini.dt.to_period("M").astype(str)
    R["mes_timing"] = R["timing_min"].dt.to_period("M").astype(str).where(R["timing_min"].notna())
    R.drop(columns="linha_de_dados").to_csv(os.path.join(pasta, "derivados", "relogios.csv"), index=False)
    X = pd.crosstab(R["mes_particao"], R["mes_exec"])
    X.to_csv(os.path.join(pasta, "derivados", "cruzamento.csv"))

    H = None
    arq_mec = os.path.join(os.path.dirname(PASTA_EVIDENCIA), "erros_mecanismo.csv")
    if os.path.exists(arq_mec):
        M = pd.read_csv(arq_mec, dtype={"exec_id": str})
        H = (M[M["unidade"] == "H_bloco_code"][["exec_id", "role", "idx"]]
             .merge(R[["exec_id", "anomesdia", "dat_hor_inio_exeo", "mes_particao", "mes_exec"]], on="exec_id", how="left")
             .sort_values(["dat_hor_inio_exeo", "exec_id", "idx"]))
        H.to_csv(os.path.join(pasta, "derivados", "h_bloco_code.csv"), index=False)

    # regra de escolha dos crus (escrita antes de olhar os casos; empate → ordem de exec_id)
    Ro = R.sort_values("exec_id")
    casos = [(r, "maior defasagem partição − início (top 3)") for _, r in
             R.sort_values(["delta_dias", "exec_id"], ascending=[False, True]).head(3).iterrows()]
    for p, g in Ro.groupby("mes_particao"):
        g = g[g["delta_dias"] > 30]
        if len(g):
            casos.append((g.iloc[0], f"partição {p}: 1ª execução (ordem exec_id) com defasagem > 30 dias"))
    ctrl = Ro[Ro["delta_dias"] < 1]
    if len(ctrl):
        casos.append((ctrl.iloc[0], "controle: 1ª execução (ordem exec_id) com defasagem < 1 dia"))
    if H is not None:
        h10 = H[H["mes_exec"] == "2025-10"].sort_values("exec_id")
        if len(h10):
            casos.append((R[R["exec_id"] == h10.iloc[0]["exec_id"]].iloc[0],
                          "H_bloco_code: 1ª execução (ordem exec_id) com início em out/2025"))
    vistos, linhas_casos = set(), []
    for r, motivo in casos:
        linhas_casos.append({"exec_id": r["exec_id"], "motivo": motivo, "anomesdia": r["anomesdia"],
                             "dat_hor_inio_exeo": r["dat_hor_inio_exeo"], "timing_min": r["timing_min"],
                             "delta_dias": r["delta_dias"]})
        if r["exec_id"] not in vistos:
            vistos.add(r["exec_id"])
            gravar_cru(pasta, df.loc[r["linha_de_dados"]], r["linha_de_dados"])
    pd.DataFrame(linhas_casos).to_csv(os.path.join(pasta, "casos.csv"), index=False)

    com_t = R["timing_min"].notna()
    # dois recortes: as 1.000 linhas, e as execuções com memória (as que o pipeline analisa — steps, erros, triagem)
    recortes = [("todas as linhas", R), ("com memória (base das análises)", R[com_t])]
    fatos = [f"linhas: {len(R)} · com memória (timing nos steps): {int(com_t.sum())} · "
             f"exec_id repetido: {int(R['exec_id'].duplicated().sum())}"]
    for nome, s in recortes:
        igual = s["mes_particao"].eq(s["mes_exec"])
        fatos.append(f"{nome}: mês da partição = mês real em {int(igual.sum())}/{len(s)} ({igual.mean():.1%}) · "
                     f"defasagem partição − início: mediana {s['delta_dias'].median():.1f} d, "
                     f"p75 {s['delta_dias'].quantile(.75):.1f} d, máx {s['delta_dias'].max():.1f} d")
    fatos += [
        f"início DEPOIS da partição: {int((R['delta_dias'] < 0).sum())}",
        f"dat_hor_inio_exeo × timing_min: mesmo mês {(R.loc[com_t, 'mes_exec'] == R.loc[com_t, 'mes_timing']).mean():.1%} · "
        f"|diferença| máx {R.loc[com_t, 'delta_coluna_timing_h'].abs().max():.2f} h",
        f"valores distintos de anomesdia: {R['anomesdia'].nunique()} ({', '.join(sorted(R['anomesdia'].unique()))})",
        f"meses reais sem nenhuma partição do mesmo mês: {', '.join(sorted(set(R['mes_exec']) - set(R['mes_particao']))) or 'nenhum'}",
    ]
    if H is not None:
        fatos.append(f"H_bloco_code: {len(H)} erros · por mês real: " + ", ".join(f"{k} {v}" for k, v in H["mes_exec"].value_counts().sort_index().items())
                     + " · por partição: " + ", ".join(f"{k} {v}" for k, v in H["mes_particao"].value_counts().sort_index().items()))
    with open(os.path.join(pasta, "leia-me.md"), "w", encoding="utf-8") as f:
        f.write(LEIA_ME_RELOGIOS.format(n_casos=len(linhas_casos), n_crus=len(vistos),
                                        fatos="\n".join(f"- {x}" for x in fatos)))
    print("A3_relogios:"); print("\n".join("  " + x for x in fatos))
    print(f"  casos: {len(linhas_casos)} · crus gravados: {len(vistos)}")

LEIA_ME_RELOGIOS = """# A3_relogios — Ajuste 3 (mês de partição × mês real da execução)

**O que esta pasta sustenta.** Que `anomesdia` (de onde o pipeline deriva `mes`) **não** é a data da execução, e que
`dat_hor_inio_exeo` é. A prova compara três relógios de fontes independentes para cada execução:

1. `anomesdia`: coluna da tabela (semântica não documentada; hipótese: data de corte da democratização da base);
2. `dat_hor_inio_exeo`: coluna da tabela, "data/hora de início" (`05-schema.md`);
3. `timing.start_time` / `end_time` de cada step: gravados **pelo runtime do agente** dentro de `txt_etap_memo`.

Se (2) e (3) concordam e (1) diverge, então (1) não data a execução. Nenhum código de classificação do pipeline
entra nisso, só leitura de colunas e de um campo do JSON. A única exceção é `h_bloco_code.csv`, que usa a
atribuição de unidade exportada pelo notebook (`resultados/erros_mecanismo.csv`).

**Números (recalculados a cada geração):**

{fatos}

**Regra de escolha dos {n_casos} casos ({n_crus} crus),** escrita antes de olhar os casos; empate → ordem de `exec_id`:
- as 3 execuções de maior defasagem partição − início;
- em cada partição, a 1ª execução com defasagem > 30 dias;
- 1 controle: a 1ª execução com defasagem < 1 dia;
- a 1ª execução `H_bloco_code` com início em out/2025.

**Arquivos.**

- `crus/<exec_id>.json`: **a fonte**, a linha inteira do trace sem alteração (`txt_etap_memo` só desserializado).
- `casos.csv`: os casos escolhidos, com o motivo e as três datas.
- `derivados/relogios.csv`: as 1.000 execuções, uma por linha: as três datas, `delta_dias` (partição − início),
  `delta_coluna_timing_h`, `mes_particao`, `mes_exec`, `mes_timing`. Só ids e datas.
- `derivados/cruzamento.csv`: execuções por mês da partição (linhas) × mês real (colunas).
- `derivados/h_bloco_code.csv`: os erros `H_bloco_code` com as datas da execução.

**Conferir sem confiar no pipeline:** abrir um `crus/<exec_id>.json`, ler `anomesdia` e `dat_hor_inio_exeo`, pegar
o `timing.start_time` de qualquer step em `txt_etap_memo` e converter o epoch (`date -u -r <epoch>` no macOS). As
duas últimas datas batem; a primeira vem semanas ou meses depois.

**O que esta pasta NÃO prova:** o que `anomesdia` é exatamente. Isso só quem mantém a tabela confirma
(pergunta aberta: `05-schema.md` §Aberto).

**Gerar** (em `pipeline/`): `uv run python drill_down.py relogios`

> Os crus têm nome de cliente, número de processo e texto de documento. Pasta git-ignored — não versionar.
"""

CLASSE_RESIDUO = {
    "codigo_mal_escrito": "Código Python mal escrito",
    "causa_sem_regra": "Erro conhecido, causa sem regra",
    "sintoma_nao_reconhecido": "Erro que a taxonomia não conhece",
}

from base_pipeline import mascarar, padrao_residuo, linha_rejeitada  # a mesma impressão digital que a triagem usa

def residuo():
    """Evidência do resíduo da taxonomia: todos os erros das unidades X_ (causa não identificada / sintoma não
    reconhecido), com a classe de cada um e a frase da exceção mascarada. Lê resultados/erros_mecanismo.csv (rode o
    notebook antes). Grava resultados/evidencia/A5_residuo/ e imprime só contagens."""
    pasta = os.path.join(PASTA_EVIDENCIA, "A5_residuo")
    os.makedirs(os.path.join(pasta, "derivados"), exist_ok=True)
    M = pd.read_csv(os.path.join(os.path.dirname(PASTA_EVIDENCIA), "erros_mecanismo.csv"), dtype={"exec_id": str})
    X = M[M["unidade"].str.startswith("X_")].copy()
    df = load()
    linha = {r["cod_idef_exeo"]: (i, r) for i, r in df[df["cod_idef_exeo"].isin(set(X["exec_id"]))].iterrows()}
    msgs = {}
    for eid, (i, r) in linha.items():
        memo = json.loads(r["txt_etap_memo"])
        for role, passos in memo.items():
            if not isinstance(passos, list): continue
            acts = [st for st in passos if isinstance(st, dict) and st.get("__class__") == "ActionStep"]
            for k, st in enumerate(acts):
                e = st.get("error") or {}
                if e: msgs[(eid, role, k)] = (e.get("type"), str(e.get("message") or ""))
    linhas = []
    for _, c in X.sort_values(["submecanismo", "exec_id", "idx"]).iterrows():
        tipo, m = msgs.get((c["exec_id"], c["role"], int(c["idx"])), (None, ""))
        exc = re.findall(r"(\b\w+(?:Error|Exception)\b):\s*([^\n]{0,90})", m)
        if exc and c["submecanismo"] != "codigo_mal_escrito":
            classe_exc, frase = exc[-1]
        else:  # erro de parsing: só a classe, sem frase (a mensagem traz o código rejeitado)
            classe_exc, frase = (re.findall(r"\b\w+(?:Error|Exception)\b", m) or ["?"])[-1], ""
        linhas.append({"exec_id": c["exec_id"], "role": c["role"], "idx": int(c["idx"]), "mes": c["mes"],
                       "unidade": c["unidade"], "submecanismo": c["submecanismo"],
                       "classe": CLASSE_RESIDUO.get(c["submecanismo"], c["submecanismo"]),
                       "assinatura": c["assinatura"], "error_type": tipo, "excecao": classe_exc,
                       "frase_mascarada": mascarar(frase),
                       "padrao": padrao_residuo(m, c["submecanismo"], tipo),
                       # estrutura da mensagem, só verdadeiro/falso: o formato que linha_rejeitada() espera existe?
                       "tem_due_to": bool(re.search(r"due to: \w+", m)),
                       "tem_linha_error": any(l.strip().startswith("Error:") for l in m.splitlines()),
                       "linha_rejeitada_ok": linha_rejeitada(m) != ""})
    casos = pd.DataFrame(linhas)
    casos.to_csv(os.path.join(pasta, "casos.csv"), index=False)
    casos.drop(columns=["frase_mascarada"]).to_csv(os.path.join(pasta, "derivados", "residuo.csv"), index=False)
    for eid in casos["exec_id"].unique():
        i, r = linha[eid]
        gravar_cru(pasta, r, i)
    cont = casos.groupby(["unidade", "classe"]).size()
    with open(os.path.join(pasta, "leia-me.md"), "w", encoding="utf-8") as f:
        f.write(LEIA_ME_RESIDUO.format(n=len(casos), n_crus=casos["exec_id"].nunique(),
                                       contagem="\n".join(f"- {u} · {c}: {n}" for (u, c), n in cont.items())))
    print(f"A5_residuo: {len(casos)} erros · {casos['exec_id'].nunique()} crus")
    for (u, c), n in cont.items(): print(f"  {u} · {c}: {n}")
    # contagens por padrão × error.type × estrutura da mensagem — só nomes de classe e verdadeiro/falso, sem texto de
    # caso: o bloco que pode sair da máquina para a conferência do resíduo (plano do resíduo da base 2, Etapa 1)
    est = (casos.groupby(["unidade", "padrao", "error_type", "tem_due_to", "tem_linha_error", "linha_rejeitada_ok"],
                         dropna=False)
           .agg(erros=("exec_id", "size"), execucoes=("exec_id", "nunique"), meses=("mes", "nunique"),
                papeis=("role", "nunique"))
           .reset_index().sort_values(["unidade", "erros"], ascending=[True, False]))
    print("\nestrutura por padrão (due_to · linha Error: · linha rejeitada extraída):")
    for _, r in est.iterrows():
        print(f"  {r['unidade']:26s} {r['erros']:3d} err · {r['execucoes']:3d} exec · {r['meses']:2d} m · "
              f"{r['papeis']:2d} pap · type={r['error_type']} · due_to={r['tem_due_to']:d} "
              f"error={r['tem_linha_error']:d} rejeitada={r['linha_rejeitada_ok']:d} · {str(r['padrao'])[:70]}")

LEIA_ME_RESIDUO = """# A5_residuo — o resíduo da taxonomia

**O que esta pasta sustenta.** A leitura dos erros que nenhuma regra de causa reconheceu (`01-racionais.md` §7, "Os
dois baldes de resíduo"; casos em `03-procedimento-validacao.md` §1.13): de qual classe é cada um e o que a
mensagem de exceção diz.

**Regra de escolha dos {n} casos ({n_crus} crus):** todos os erros das unidades `X_causa_nao_identificada` e
`X_sintoma_nao_reconhecido` — sem amostra.

**Contagem:**

{contagem}

**As classes:**
- **Código Python mal escrito** (`codigo_mal_escrito`): erro de sintaxe ou indentação em código de verdade, não
  texto colado no código.
- **Erro conhecido, causa sem regra** (`causa_sem_regra`): o sintoma tem nome no `classify()`, mas nenhuma regra do
  `submecanismo()` diz o que o agente fez de errado.
- **Erro que a taxonomia não conhece** (`sintoma_nao_reconhecido`): nem o sintoma nem a causa são reconhecidos.

**Arquivos.**
- `crus/<exec_id>.json`: **a fonte**, a linha inteira do trace sem alteração (`txt_etap_memo` só desserializado).
- `casos.csv`: um erro por linha, com a classe, o `error.type`, a classe da exceção, a frase da exceção mascarada
  (texto entre aspas → `<q>`, entre crases → `<id>`, números → `<n>`) e o **padrão** (`padrao_residuo()` do
  `base_pipeline.py`) — a chave com que a triagem conta a recorrência do resíduo. Três colunas verdadeiro/falso dizem
  se a mensagem tem o formato que `linha_rejeitada()` espera: `tem_due_to` (trecho `due to: <Classe>`),
  `tem_linha_error` (uma linha começando com `Error:`) e `linha_rejeitada_ok` (a linha de código rejeitada foi
  extraída). Sintaxe com `linha_rejeitada_ok` falso cai em "Código Python mal escrito" por falta de formato, não por
  diagnóstico.
- `derivados/residuo.csv`: o mesmo, sem a frase — com `exec_id`/`role`/`idx` para voltar ao cru.

**Conferir no cru:** `txt_etap_memo` → papel → o `idx`-ésimo `ActionStep` da lista → `error.message`. Ou
`uv run python drill_down.py caso <exec_id> <role>`.

**Gerar** (em `pipeline/`, depois do notebook): `uv run python drill_down.py residuo`

> Os crus têm nome de cliente, número de processo e texto de documento. Pasta git-ignored — não versionar.
"""

def padrao(trecho=None):
    """Os casos de um padrão de erro do resíduo (passo 1 do procedimento de revisão, 03-procedimento-validacao.md,
    Frente 3). Sem argumento: lista os padrões com contagem. Com argumento: o padrão que contém o trecho (sem
    diferença de maiúsculas); se mais de um contém, lista os candidatos para escolher. Lê
    resultados/erros_mecanismo.csv — rode o notebook antes. Só ids e datas: o padrão já vem mascarado."""
    M = pd.read_csv(os.path.join(os.path.dirname(PASTA_EVIDENCIA), "erros_mecanismo.csv"), dtype={"exec_id": str})
    if "padrao" not in M.columns:
        print("erros_mecanismo.csv sem a coluna `padrao` — rode o notebook de novo (versão de 23/09/2026 em diante)."); return
    R = M[M["padrao"].notna()]
    cont = R.groupby(["unidade", "padrao"]).agg(erros=("exec_id", "size"), execucoes=("exec_id", "nunique"),
                                                meses=("mes", "nunique")).sort_values(["execucoes", "erros"], ascending=False)
    if not trecho:
        print(f"{len(cont)} padrões de resíduo (unidade · erros · execuções · meses):\n")
        for (u, pd_), c in cont.iterrows():
            print(f"  {u:27s} {c['erros']:3d} err · {c['execucoes']:3d} exec · {c['meses']:2d} meses · {pd_}")
        print('\nUm padrão:  python drill_down.py padrao "<trecho do padrão>"'); return
    hits = sorted({p_ for p_ in R["padrao"] if trecho.lower() in p_.lower()})
    if trecho in hits:  # o padrão exato (ex.: "SyntaxError", "?") vale mesmo que outros padrões o contenham
        hits = [trecho]
    if not hits:
        print(f"nenhum padrão contém '{trecho}'. Sem argumento, a lista completa."); return
    if len(hits) > 1:
        print(f"{len(hits)} padrões contêm '{trecho}' — use um trecho mais específico:")
        for h in hits: print("  " + h)
        return
    C = R[R["padrao"] == hits[0]].sort_values(["mes", "exec_id", "idx"])
    print(f"padrão: {hits[0]}\n{len(C)} erros · {C['exec_id'].nunique()} execuções · {C['mes'].nunique()} meses\n")
    for _, c in C.iterrows():
        print(f"  exec_id={c['exec_id']}  role={c['role']}  idx={c['idx']}  mes={c['mes']}  unidade={c['unidade']}")
    print("\nLer um caso no cru:  python drill_down.py caso <exec_id> <role>")

MECANISMOS_TEMPO = ["timeout_interpretador", "codigo_lento", "resultado_bruto_na_resposta"]

def _nome_chamada(f):
    if isinstance(f, ast.Name): return f.id
    if isinstance(f, ast.Attribute):
        return (_nome_chamada(f.value) + "." if isinstance(f.value, (ast.Name, ast.Attribute)) else ".") + f.attr
    return "?"

def _aninhamento(n, d=0):
    laco = isinstance(n, (ast.For, ast.While, ast.comprehension))
    return max([d + laco] + [_aninhamento(c, d + laco) for c in ast.iter_child_nodes(n)])

def _chamadas(nos):
    return Counter(_nome_chamada(c.func) for n in nos for c in ast.walk(n) if isinstance(c, ast.Call))

def _lacos(t):
    """Cada laço do bloco: (linha, tipo, chamadas que se repetem a cada volta, chamadas do cabeçalho — rodam uma vez).
    for: o corpo repete, o `in <expr>` roda uma vez; while: condição e corpo repetem; compreensão: o elemento e os
    `if` repetem, o primeiro `in <expr>` roda uma vez."""
    out = []
    for n in ast.walk(t):
        if isinstance(n, ast.For):
            out.append((n.lineno, "for", _chamadas(n.body + n.orelse), _chamadas([n.iter])))
        elif isinstance(n, ast.While):
            out.append((n.lineno, "while", _chamadas([n.test] + n.body + n.orelse), Counter()))
        elif isinstance(n, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            elt = [n.key, n.value] if isinstance(n, ast.DictComp) else [n.elt]
            g0, resto = n.generators[0], n.generators[1:]
            dentro = elt + list(g0.ifs) + [x for g in resto for x in [g.iter, *g.ifs]]
            out.append((n.lineno, "compreensão", _chamadas(dentro), _chamadas([g0.iter])))
    return sorted(out, key=lambda x: x[0])

def tempo(papel=None, mecanismos=None):
    """Quem gastou os 30 s? Para cada erro de tempo do interpretador (`timeout_interpretador`, `codigo_lento`):
    os tamanhos em jogo, a estrutura do código do step, o que ia para o final_answer e o que o agente fez depois no
    mesmo papel; e, por papel, os final_answer que deram certo, para comparar. Só números e nomes (de variáveis e de
    funções) — nenhum texto de caso, nenhum exec_id: a saída pode sair da máquina. Lê resultados/erros_mecanismo.csv
    — rode o notebook antes. Plano da Etapa 5b (pipeline-entre-bases.md)."""
    M = pd.read_csv(os.path.join(os.path.dirname(PASTA_EVIDENCIA), "erros_mecanismo.csv"), dtype={"exec_id": str})
    F = M[M["submecanismo"].isin(mecanismos or MECANISMOS_TEMPO)]
    if papel:
        F = F[F["role"] == papel]
    if F.empty:
        print(f"nenhum erro de {', '.join(mecanismos or MECANISMOS_TEMPO)}" + (f" no papel {papel}" if papel else "") + "."); return
    df = load().drop_duplicates("cod_idef_exeo").set_index("cod_idef_exeo")

    def passos(r, role):
        if not isinstance(r["txt_etap_memo"], str) or role not in r["txt_etap_memo"]: return []
        return [s for s in json.loads(r["txt_etap_memo"]).get(role, []) if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
    def dur(s): return (s.get("timing") or {}).get("duration") or 0
    def ent(s): return len(str(s.get("action_output") or ""))

    for role in sorted(F["role"].unique()):
        # a régua: os final_answer que deram certo neste papel, na base inteira
        tam, tmp = [], []
        for _, r in df.iterrows():
            for s in passos(r, role):
                if s.get("is_final_answer") and not s.get("error"):
                    tam.append(ent(s)); tmp.append(dur(s))
        T, D = pd.Series(tam, dtype=float), pd.Series(tmp, dtype=float)
        print(f"{'='*100}\n{role}: final_answer que deram certo = {len(T)}")
        if len(T):
            print(f"  texto entregue (caracteres): mediana={T.median():,.0f}  p90={T.quantile(.9):,.0f}  máx={T.max():,.0f}  "
                  f"| >= 25 mil: {int((T >= 25000).sum())}")
            print(f"  duração do step (s, inclui o LLM): mediana={D.median():.1f}  p90={D.quantile(.9):.1f}  máx={D.max():.1f}")
        C = F[F["role"] == role].sort_values(["mes", "exec_id", "idx"])
        for k, (_, c) in enumerate(C.iterrows(), 1):
            r = df.loc[c["exec_id"]]; acts = passos(r, role); i = int(c["idx"])
            st = acts[i]; code = str(st.get("code_action") or "")
            obs = [len(str(s.get("observations") or "")) for s in acts[:i]]
            try: loc = (json.loads(r["txt_vrvl_locl"]) or {}).get(role) or {}
            except Exception: loc = {}
            top = sorted(((n, len(str(v))) for n, v in loc.items()), key=lambda x: -x[1])[:3]
            print(f"\n  caso {k} · idx={i} · {c['submecanismo']} · mês {c['mes']} · step {dur(st):.1f}s")
            print(f"    tamanhos: maior observação anterior={max(obs or [0]):,}  soma={sum(obs):,}  "
                  f"| maiores variáveis (estado final): {top}")
            try:
                t = ast.parse(code)
            except SyntaxError:
                print(f"    código: {len(code):,} caracteres · não parseia"); t = None
            if t is not None:
                chamadas = Counter(_nome_chamada(n.func) for n in ast.walk(t) if isinstance(n, ast.Call))
                lacos = sum(isinstance(n, (ast.For, ast.While, ast.comprehension)) for n in ast.walk(t))
                mais = sum(isinstance(n, ast.AugAssign) for n in ast.walk(t))
                print(f"    código: {len(code):,} caracteres · laços={lacos} aninhamento={_aninhamento(t)} '+='={mais} "
                      f"· chamadas: {dict(chamadas.most_common(8))}")
                # o que se repete em cada laço (Etapa 5b: ferramenta dentro de laço × uma chamada só)
                for lin, tipo, dentro, cab in _lacos(t):
                    print(f"    laço na linha {lin} ({tipo}): repete a cada volta {dict(dentro) or '{}'} "
                          f"· roda uma vez no cabeçalho {dict(cab) or '{}'}")
                # a palavra for/while fora de um laço de verdade (comentário, texto): só os números das linhas
                linhas_laco = {lin for lin, *_ in _lacos(t)}
                so_palavra = [k for k, l in enumerate(code.splitlines(), 1)
                              if re.search(r"\b(for|while)\b", l) and k not in linhas_laco]
                if so_palavra:
                    print(f"    'for'/'while' como palavra, sem ser laço (comentário ou texto), nas linhas: {so_palavra}")
                fixo, nomes = 0, []
                for n in ast.walk(t):
                    if isinstance(n, ast.Call) and _nome_chamada(n.func) == "final_answer":
                        for a in list(n.args) + [kw.value for kw in n.keywords]:
                            for x in ast.walk(a):
                                if isinstance(x, ast.Constant) and isinstance(x.value, str): fixo += len(x.value)
                                if isinstance(x, ast.Name): nomes.append((x.id, len(str(loc.get(x.id, "")))))
                if "final_answer" in chamadas:
                    print(f"    para o final_answer: texto fixo={fixo:,} caracteres · variáveis passadas (estado final): {nomes}")
            for j in range(i + 1, len(acts)):
                s = acts[j]
                print(f"    depois idx={j}: {'ERRO' if s.get('error') else 'ok'}  final={bool(s.get('is_final_answer'))}  "
                      f"entregue={ent(s):,} caracteres  step {dur(s):.1f}s")
            if i + 1 >= len(acts):
                print("    depois: nenhum step (o papel terminou aqui)")
    print(f"{'='*100}\nLimites: a duração do step inclui o LLM pensando; o tamanho das variáveis é o do fim da execução.")

def _forma_da_resposta(mo):
    """O que o LLM escreveu no lugar do bloco de código — só pela forma, sem ler o conteúdo. O `</code>` do fim é
    ignorado: é a sequência de parada, e o próprio harness a acrescenta de volta à resposta."""
    mo = re.sub(r"\s*</code>\s*$", "", mo).strip()
    if len(mo) < 20:
        return "vazio"
    if re.search(r"```(py|python)?\s*\n", mo):
        return "bloco em ``` em vez de <code>"
    if mo[0] in "{[":
        return "resposta em dict/JSON (sem código)"
    return "frase ou texto (sem código)"

_MARCA_FORMATO = re.compile(r"<code>|</code>|```|<end_code>|Thought:|final_answer\(")

def _variante_prompt(sysp):
    """Versão do FORMATO que o system prompt ensina: hash só das linhas que citam as marcas de código (<code>, ```,
    <end_code>, Thought:, final_answer( ), com dígitos mascarados. O prompt inteiro muda a cada execução; as linhas de
    formato, não — na base 1 são 1 ou 2 versões por papel. Só o identificador sai na tela; o texto, com --prompt."""
    import hashlib
    if not sysp:
        return "(sem prompt)"
    linhas = [re.sub(r"\d", "0", l.strip()) for l in sysp.splitlines() if _MARCA_FORMATO.search(l)]
    return hashlib.md5("\n".join(linhas).encode("utf-8")).hexdigest()[:8]

def _modelo_do_step(s):
    """O modelo que respondeu o step: `model_output_message.raw.model`, gravado pela API do provedor."""
    raw = (s.get("model_output_message") or {}).get("raw") if isinstance(s.get("model_output_message"), dict) else None
    return str(raw.get("model")) if isinstance(raw, dict) and raw.get("model") else "(não registrado)"

def _modo_prompt(sysp):
    """Em que modo do CodeAgent (smolagents) o system prompt põe o agente — só pela presença de marcas, sem texto.
    JSON estruturado: o modelo responde {"thought": …, "code": …} e o harness lê o JSON (não há regex de <code>, então
    o erro "regex pattern" não acontece). Texto com <code>: o modelo escreve Thought + <code>…</code> e o harness procura
    o bloco com a regex — o único modo em que o erro existe. (Os ```python do prompt só mostram as ferramentas.)"""
    if re.search(r'\{"thought":', sysp):
        return "JSON estruturado"
    if "<code>" in sysp and "</code>" in sysp:
        return "texto com <code>"
    return "outro"

from base_pipeline import UNIDADES_CONTRATO  # a mesma lista do notebook falhas_silenciosas.ipynb


def silenciosas(ferramenta=None, janela=3, motivos=False, forma=False):
    """Falhas silenciosas de ferramenta: a ferramenta falha, o wrapper devolve "Error calling tool '<nome>'" como
    STRING, o step fica com error: null, e o pipeline o conta como ok. Só números e nomes, sem exec_id. Os casos vão
    para resultados/evidencia/silenciosas/casos.csv (git-ignored). Mesma função do notebook: falhas_silenciosas()
    (base_pipeline.py). Origem: 11-relatorio-protocolo-harness.md §2.5; roadmap item 26.
    `motivos=True` (--motivos): só a lista dos motivos por ferramenta, mascarados (mascarar_motivo), com a contagem —
    para escrever as regras de motivo olhando as duas bases (S2b)."""
    from base_pipeline import (carregar_trace, falhas_silenciosas, mascarar_motivo, GRUPOS_FALHA_REAL, DONO_DO_GRUPO,
                               formas_das_falhas, erro_depois_da_falha, contrato_precedido, sucesso_falso_candidato)
    df = carregar_trace()
    F = falhas_silenciosas(df)
    if ferramenta:
        F = F[F["ferramenta"] == ferramenta]
    if F.empty:
        print("nenhuma chamada ou falha de ferramenta encontrada."); return
    sil = F[F["falha"] == "silenciosa"]
    if forma:
        # --forma <ferramenta>: como o 1º argumento foi passado em cada falha silenciosa dela, só contagem por tipo
        if not ferramenta:
            print("uso: python drill_down.py silenciosas --forma <ferramenta>"); return
        cont = Counter(zip(sil["grupo"], formas_das_falhas(df, sil)))
        print(f"{'='*100}\n{ferramenta} — falhas silenciosas: {len(sil)} · como o 1º argumento foi passado "
              f"(só o tipo, sem conteúdo)\n{'='*100}")
        for (grp, f), n in cont.most_common():
            print(f"  {n:>4} · {grp:<19} · {f}")
        return
    if motivos:
        fal = F[F["falha"].notna()].copy()
        fal["motivo_m"] = fal["motivo"].map(mascarar_motivo)
        print(f"{'='*100}\nMotivos das falhas de ferramenta (mascarados: <v> = valor do caso, 9 = dígito)"
              f"{' · ' + ferramenta if ferramenta else ''}\n{'='*100}")
        for t, g in fal.groupby("ferramenta"):
            print(f"\n{t}  ({len(g)} falhas: {(g['falha'] == 'silenciosa').sum()} silenciosas, "
                  f"{(g['falha'] == 'excecao').sum()} com exceção)")
            for (mot, tipo, grp), n in g.groupby(["motivo_m", "falha", "grupo"]).size().sort_values(ascending=False).items():
                print(f"  {n:>4} · {'silenc.' if tipo == 'silenciosa' else 'exceção'} · {grp:<19} · {mot or '(vazio)'}")
        return
    print(f"{'='*100}\nFalhas silenciosas de ferramenta — 'Error calling tool' com error: null"
          f"{' · ' + ferramenta if ferramenta else ''}\n{'='*100}")
    # uma linha de F = um par step × ferramenta: um step que chama duas ferramentas conta duas vezes (ressalva C da
    # auditoria de 02/10 — o notebook §13.1 conta steps distintos)
    n_steps = F[["exec_id", "role", "idx"]].drop_duplicates().shape[0]
    print(f"chamadas de ferramenta (step × ferramenta, chamada ou falha): {len(F):,} em {n_steps:,} steps · falhas com exceção: "
          f"{(F['falha'] == 'excecao').sum():,} · **falhas silenciosas: {len(sil):,}** em "
          f"{sil['exec_id'].nunique()} execuções, {sil['mes'].nunique()} meses")

    print("\n[1] por ferramenta (ordenado pelas silenciosas):  steps · com exceção · silenciosas · % silenciosa · papéis · meses")
    g = F.groupby("ferramenta")
    tab = pd.DataFrame({"steps": g.size(),
                        "excecao": g["falha"].apply(lambda s: (s == "excecao").sum()),
                        "silenciosa": g["falha"].apply(lambda s: (s == "silenciosa").sum())})
    tab = tab[(tab["excecao"] + tab["silenciosa"]) > 0].sort_values("silenciosa", ascending=False)
    for t, row in tab.iterrows():
        s = sil[sil["ferramenta"] == t]
        print(f"  {t:<40} {row['steps']:>6} · {row['excecao']:>3} · {row['silenciosa']:>4} · "
              f"{row['silenciosa'] / row['steps']:>5.0%} · {', '.join(sorted(s['role'].unique())) or '—'} · "
              f"{', '.join(sorted(s['mes'].unique())) or '—'}")

    # [1b] o motivo, por grupo (motivo_da_falha, S2b): quem é o dono da falha
    DONO = DONO_DO_GRUPO
    fal = F[F["falha"].notna()]
    print("\n[1b] por grupo do motivo:  silenciosas · com exceção · ferramentas principais · dono")
    for grp in DONO:
        gg = fal[fal["grupo"] == grp]
        if gg.empty:
            continue
        top = ", ".join(f"{t} {n}" for t, n in gg["ferramenta"].value_counts().head(3).items())
        print(f"  {grp:<20} {(gg['falha'] == 'silenciosa').sum():>4} · {(gg['falha'] == 'excecao').sum():>3} · "
              f"{top} · {DONO[grp]}")

    arq_mec = os.path.join(os.path.dirname(PASTA_EVIDENCIA), "erros_mecanismo.csv")
    if os.path.exists(arq_mec) and len(sil):
        M = pd.read_csv(arq_mec, dtype={"exec_id": str})
        M["idx"] = M["idx"].astype(int)
        # [2] o primeiro erro do mesmo papel depois de cada falha silenciosa, até `janela` steps adiante
        print(f"\n[2] o que veio depois de cada falha silenciosa (1º erro do mesmo papel em até {janela} steps):")
        for u, n in Counter(erro_depois_da_falha(sil, M, janela)).most_common(10):
            print(f"  {u:<40} {n:>4}")
        # [3] quanto dos erros de contrato de retorno vem logo depois de uma falha silenciosa
        print(f"\n[3] erros de contrato de retorno precedidos por falha silenciosa no mesmo papel (até {janela} steps antes):")
        for u, (n_err, n_prec) in contrato_precedido(sil, M, janela).items():
            print(f"  {u:<24} {n_err:>4} erros · {n_prec:>4} precedidos ({(n_prec / n_err) if n_err else 0:.0%})")
    elif not os.path.exists(arq_mec):
        print(f"\n[2]/[3] precisam de {os.path.relpath(arq_mec)} — rode o notebook antes.")

    # [4] candidato a sucesso falso: o papel entregou final_answer depois da falha, sem chamada bem-sucedida da mesma
    # ferramenta entre a falha e o final
    # Só as falhas reais (GRUPOS_FALHA_REAL): responder "não encontrei" depois de uma busca vazia, ou "assunto não
    # parametrizado", é a resposta certa, não sucesso falso.
    real = sil[sil["grupo"].isin(GRUPOS_FALHA_REAL)]
    if len(real):
        cand = Counter(real.loc[sucesso_falso_candidato(F, sil), "grupo"])
        print(f"\n[4] falhas reais ({len(real)} de {len(sil)}; fora sem_resultado e fora_da_cobertura): o papel entregou "
              f"final_answer depois, sem chamada sem falha da mesma ferramenta no meio: {sum(cand.values())} "
              f"({', '.join(f'{g} {n}' for g, n in cand.most_common())}) — candidato a sucesso falso, conferir no caso")

    pasta = os.path.join(PASTA_EVIDENCIA, "silenciosas")
    os.makedirs(pasta, exist_ok=True)
    sil.to_csv(os.path.join(pasta, "casos.csv"), index=False)
    print(f"\nCasos (com exec_id): {os.path.relpath(os.path.join(pasta, 'casos.csv'))} — não sai da máquina.")


def critico(papel=None):
    """Fila dos erros críticos (limite de passos) com a ligação ao "resposta sem bloco de código" e a trajetória do
    papel por tipo de erro — para achar o passo crítico (o primeiro erro da cascata) sem abrir o texto do caso.
    Mesmo cálculo do notebook: `caminho_dos_criticos()` (base_pipeline.py). Saída sem exec_id."""
    from base_pipeline import caminho_dos_criticos
    pasta = os.path.dirname(PASTA_EVIDENCIA)
    arq_mec = os.path.join(pasta, "erros_mecanismo.csv")
    if not os.path.exists(arq_mec):
        print(f"falta {os.path.relpath(arq_mec)} — rode o notebook antes."); return
    M = pd.read_csv(arq_mec, dtype={"exec_id": str})
    arq_crit = os.path.join(pasta, "criticos.csv")
    C = pd.read_csv(arq_crit, dtype={"exec_id": str}) if os.path.exists(arq_crit) else caminho_dos_criticos(M)
    fonte = "criticos.csv" if os.path.exists(arq_crit) else "recalculado de erros_mecanismo.csv"
    if papel:
        C = C[C["role"] == papel]
    print(f"{'='*100}\nErros críticos (limite de passos){' do papel ' + papel if papel else ''}: {len(C)} "
          f"execução(ões) · fonte: {fonte}\n{'='*100}")
    if C.empty:
        print("nenhum erro crítico."); return
    for k, (_, c) in enumerate(C.iterrows(), 1):
        g = M[(M["exec_id"] == c["exec_id"]) & (M["role"] == c["role"])].sort_values("idx")
        i_crit = int(c["idx do erro crítico"])
        n = c.get("steps no papel")
        n = int(n) if pd.notna(n) else i_crit + 1
        prot = g[g["submecanismo"] == "harness_bloco_code"]
        print(f"\n[{k}] {c['role']} · {c['mes']} · {n} steps no papel · erro crítico no idx {i_crit} · "
              f"{int(c['erros antes'])} erros antes")
        print(f"    primeira unidade: {c['primeira unidade'] or '—'}")
        print(f"    unidades no caminho: {c['unidades no caminho'] or '—'}")
        print(f"    'resposta sem bloco de código' nesta execução: {'sim' if len(prot) else 'não'}"
              + (f" — {len(prot)} erro(s), idx {sorted(prot['idx'].astype(int))}" if len(prot) else ""))
        # trajetória: um rótulo por idx (ok ou a unidade do erro), repetições seguidas agrupadas
        por_idx = g.drop_duplicates("idx").set_index("idx")["unidade"].to_dict()
        rot = [por_idx.get(i, "ok") for i in range(n)]
        print(f"    trajetória (idx: tipo; ×N = repetido em sequência):")
        i = 0
        while i < n:
            j = i
            while j + 1 < n and rot[j + 1] == rot[i]:
                j += 1
            faixa = f"{i}" if i == j else f"{i}–{j}"
            print(f"      {faixa:>7}: {rot[i]}{f'  ×{j - i + 1}' if j > i else ''}")
            i = j + 1
        nomes = g.drop_duplicates("unidade").set_index("unidade")["assinatura"].to_dict()
        print("    legenda (unidade → assinatura): "
              + "; ".join(f"{u} → {a}" for u, a in nomes.items()))
    print(f"\nPasso crítico: o primeiro erro da trajetória que inicia a cascata (ver 'primeira unidade'). Leitura do "
          f"caso, se precisar: `caso <exec_id> <papel>` — o exec_id está em "
          f"{os.path.relpath(arq_crit if os.path.exists(arq_crit) else arq_mec)}, não sai da máquina.")


def protocolo_casos(papel, versao=None, n=3):
    """Um arquivo de texto por erro de "resposta sem bloco de código" do papel (e da versão do prompt, se dada), para
    ler prompt, erro e recuperação juntos: o system prompt exato do step, a observação que o agente acabara de ver, o
    que ele escreveu no lugar do código, o erro, o step seguinte e a resposta final. Escolhe até `n` erros, alternando
    entre as formas (frase, markdown, dict, ...). Lê resultados/evidencia/protocolo/casos.csv — rode `protocolo` antes.
    Os arquivos têm o caso em claro: ficam em resultados/ (git-ignored), para ler na máquina."""
    pasta = os.path.join(PASTA_EVIDENCIA, "protocolo")
    arq_casos = os.path.join(pasta, "casos.csv")
    if not os.path.exists(arq_casos):
        print("rode antes: python drill_down.py protocolo"); return
    C = pd.read_csv(arq_casos, dtype={"exec_id": str})
    sel = C[C["role"] == papel]
    if versao:
        sel = sel[sel["variante_prompt"] == versao]
    if sel.empty:
        print(f"nenhum erro para papel={papel}" + (f", versão={versao}" if versao else "") +
              f". Papéis com erro: {sorted(C['role'].unique())}"); return
    print(f"{papel}" + (f" · versão {versao}" if versao else "") + f": {len(sel)} erros. Por versão e forma:")
    print("  " + sel.groupby(["variante_prompt", "forma"]).size().to_string().replace("\n", "\n  "))
    # até n casos, alternando as formas (um de cada forma antes de repetir), em ordem de mês/execução
    sel = sel.sort_values(["mes", "exec_id", "idx"])
    grupos = [g for _, g in sel.groupby("forma")]
    escolha, k = [], 0
    while len(escolha) < min(n, len(sel)):
        for g in grupos:
            if k < len(g) and len(escolha) < n:
                escolha.append(g.iloc[k])
        k += 1
    df = load().drop_duplicates("cod_idef_exeo").set_index("cod_idef_exeo")
    for j, c in enumerate(escolha, 1):
        acts = [st for st in json.loads(df.loc[c["exec_id"], "txt_etap_memo"])[papel]
                if isinstance(st, dict) and st.get("__class__") == "ActionStep"]
        i = int(c["idx"]); st = acts[i]; seg = acts[i + 1] if i + 1 < len(acts) else {}
        fins = [a for a in acts[i + 1:] if a.get("is_final_answer") and not a.get("error")]
        partes = [
            f"papel {papel} · versão do prompt {c['variante_prompt']} · modo {_modo_prompt(system_prompt(st))} · "
            f"modelo {_modelo_do_step(st)} · mês {c['mes']} · idx {i} · exec_id {c['exec_id']}",
            ("1. SYSTEM PROMPT (exato, deste step)", system_prompt(st)),
            ("2. O QUE ELE TINHA ACABADO DE VER (observação do step anterior)",
             str(acts[i - 1].get("observations") or "") if i > 0 else "(primeiro step do papel)"),
            ("3. O QUE O MODELO ESCREVEU NO LUGAR DO CÓDIGO (model_output do step do erro)", str(st.get("model_output") or "")),
            ("4. ERRO DO HARNESS", str((st.get("error") or {}).get("message") or "")),
            ("5. STEP SEGUINTE — o que escreveu", str(seg.get("model_output") or "(não há)")),
            ("5b. STEP SEGUINTE — código executado", str(seg.get("code_action") or "(não há)")),
            ("6. RESPOSTA FINAL ENTREGUE PELO PAPEL", str(fins[0].get("action_output") or "") if fins else "(nenhuma)"),
        ]
        arq = os.path.join(pasta, f"erro_{papel}_{c['variante_prompt']}_{j}.txt")
        with open(arq, "w", encoding="utf-8") as fh:
            fh.write(partes[0] + "\n")
            for titulo, texto in partes[1:]:
                fh.write(f"\n{'=' * 100}\n===== {titulo}\n{'=' * 100}\n{texto}\n")
        print(f"  gravado: {os.path.relpath(arq)} · forma {c['forma']} · {int(c['chars']):,} caracteres")
    print("Os arquivos têm o caso em claro: ler aqui, não copiar para fora.")

def protocolo(prompt=None):
    """"Resposta sem bloco de código" (H_bloco_code): o harness não achou o bloco <code>…</code> na resposta do LLM.
    Incidente ou crônico? Um papel ou todos? O que o LLM escreveu no lugar (só a forma)? O agente se recuperou? O que
    vem depois na cascata? Só contagens — nenhum texto de caso, nenhum exec_id na tela. Os casos, com exec_id, vão para
    resultados/evidencia/protocolo/casos.csv (git-ignored), para escolher o que ler com `evidencia`. Lê
    resultados/erros_mecanismo.csv e execucoes.csv — rode o notebook antes. Ajuste 10b (pipeline-entre-bases.md)."""
    from base_pipeline import sobreposicao, M1_LIMIAR
    res = os.path.dirname(PASTA_EVIDENCIA)
    M = pd.read_csv(os.path.join(res, "erros_mecanismo.csv"), dtype={"exec_id": str})
    X = pd.read_csv(os.path.join(res, "execucoes.csv"), dtype={"exec_id": str}).set_index("exec_id")
    unid = {(r.exec_id, r.role, int(r.idx)): r.unidade for r in M.itertuples()}
    df = load().drop_duplicates("cod_idef_exeo")
    passos, casos = Counter(), []
    variantes = {}   # (role, variante) -> {"meses": Counter, "steps", "erros", "modo", "chars", "texto"}
    por_modelo = {}  # (role, eixo, valor) -> {"meses": Counter, "steps", "erros"}; eixo = modelo | versão do agente
    for _, r in df.iterrows():
        eid = r["cod_idef_exeo"]
        if not isinstance(r["txt_etap_memo"], str) or eid not in X.index:
            continue
        mes = X.loc[eid, "mes"]
        for role, lst in json.loads(r["txt_etap_memo"]).items():
            if not isinstance(lst, list): continue
            acts = [s for s in lst if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
            passos[(mes, role)] += len(acts)
            for i, s in enumerate(acts):
                sp = system_prompt(s)
                v = variantes.setdefault((role, _variante_prompt(sp)), {"meses": Counter(), "steps": 0, "erros": 0,
                                                                      "modo": _modo_prompt(sp), "chars": len(sp),
                                                                      "texto": sp})
                v["meses"][mes] += 1; v["steps"] += 1
                erro_aqui = "regex pattern" in str((s.get("error") or {}).get("message") or "")
                for eixo, valor in (("modelo", _modelo_do_step(s)), ("versão do agente", str(r.get("cod_vers_aget")))):
                    pm = por_modelo.setdefault((role, eixo, valor), {"meses": Counter(), "steps": 0, "erros": 0})
                    pm["meses"][mes] += 1; pm["steps"] += 1; pm["erros"] += erro_aqui
                if not erro_aqui:
                    continue
                v["erros"] += 1
                mo = str(s.get("model_output") or "")
                depois = [unid.get((eid, role, j)) for j in range(i + 1, len(acts))]
                cascata = []
                for u in depois:          # erros seguidos logo depois, até o primeiro step sem erro
                    if u is None: break
                    cascata.append(u)
                # [9] M1: o texto escrito no lugar do bloco reaparece na resposta final entregue depois (o 1º
                # final_answer do papel) ou veio da observação anterior? (sobreposicao(), base_pipeline.py)
                fin = next((a for a in acts[i + 1:] if a.get("is_final_answer")), None)
                antecipou = sobreposicao(mo, str(fin.get("action_output") or "")) if fin else 0.0
                copia = sobreposicao(mo, str(acts[i - 1].get("observations") or "")) if i > 0 else 0.0
                casos.append({"exec_id": eid, "role": role, "idx": i, "mes": mes, "variante_prompt": _variante_prompt(sp),
                              "forma": _forma_da_resposta(mo), "chars": len(mo),
                              "tok_out": (s.get("token_usage") or {}).get("output_tokens") or 0,
                              "comeca_markdown": bool(re.match(r"\s*(#|\||- |\*\*)", mo)),
                              "cita_final_answer": "final_answer" in mo,
                              "papel_entregou_depois": any(a.get("is_final_answer") and not a.get("error") for a in acts[i + 1:]),
                              "execucao_com_resposta": bool(X.loc[eid, "tem_final"]),
                              "proximo": cascata[0] if cascata else "(step sem erro)",
                              "cascata_depois": len(cascata),
                              "repetiu_logo_depois": bool(cascata) and cascata[0] == "H_bloco_code",
                              "sobreposicao_final": round(antecipou, 3), "sobreposicao_obs_anterior": round(copia, 3)})
    C = pd.DataFrame(casos)
    pasta = os.path.join(PASTA_EVIDENCIA, "protocolo")
    os.makedirs(pasta, exist_ok=True)
    if prompt:   # grava o texto de uma versão do system prompt, para ler na máquina (não sai dela)
        achou = [(r, v) for (r, vid), v in variantes.items() if vid == prompt]
        if not achou:
            print(f"versão {prompt} não encontrada. Rode `protocolo` sem argumento para ver as versões."); return
        for r, v in achou:
            arq = os.path.join(pasta, f"prompt_{r}_{prompt}.txt")
            with open(arq, "w", encoding="utf-8") as fh:
                fh.write(v["texto"])
            print(f"gravado: {os.path.relpath(arq)} ({v['chars']:,} caracteres) — texto do prompt: ler aqui, não copiar para fora.")
        return
    if C.empty:
        print("nenhum erro 'resposta sem bloco de código' nesta base."); return
    C.sort_values(["mes", "role", "exec_id", "idx"]).to_csv(os.path.join(pasta, "casos.csv"), index=False)
    P = pd.Series(passos)
    tot_steps = int(P.sum())
    print(f"{'='*100}\nResposta sem bloco de código (H_bloco_code): {len(C)} erros · {C['exec_id'].nunique()} execuções · "
          f"{C['role'].nunique()} papéis · {len(C) / tot_steps * 1000:.2f} por 1k steps ({tot_steps:,} steps)")
    print("gatilho de reabertura (base 1): >= 2 casos num mês, ou > 1 por 1k steps")
    por_mes = P.groupby(level=0).sum()
    print("\n[1] por mês (mês da execução):  erros · steps · por 1k steps · execuções · papéis")
    for mes, n_st in por_mes.items():
        c = C[C["mes"] == mes]
        marca = "  ← gatilho" if len(c) >= 2 or (n_st and len(c) / n_st * 1000 > 1) else ""
        print(f"  {mes}  {len(c):4d} · {n_st:7,} · {len(c) / n_st * 1000 if n_st else 0:6.2f} · {c['exec_id'].nunique():4d} · "
              f"{c['role'].nunique():2d}{marca}")
    por_papel = P.groupby(level=1).sum()
    print("\n[2] por papel:  erros · steps · por 1k steps · meses com erro")
    for role in C["role"].value_counts().index:
        c = C[C["role"] == role]; n_st = int(por_papel.get(role, 0))
        print(f"  {role:24s} {len(c):4d} · {n_st:7,} · {len(c) / n_st * 1000 if n_st else 0:6.2f} · {c['mes'].nunique():2d}")
    print("\n[3] mês × papel (erros):")
    print("  " + pd.crosstab(C["mes"], C["role"]).to_string().replace("\n", "\n  "))
    print("\n[4] o que o LLM escreveu no lugar do bloco (só a forma):")
    for k, n in C["forma"].value_counts().items():
        print(f"  {n:4d}  {k}")
    print(f"  começa como markdown (#, |, -, **): {int(C['comeca_markdown'].sum())} · cita final_answer: "
          f"{int(C['cita_final_answer'].sum())} · tamanho mediano {C['chars'].median():,.0f} caracteres · tokens de saída: "
          f"mediana {C['tok_out'].median():,.0f}, máx {C['tok_out'].max():,}")
    print("\n[5] recuperação:")
    print(f"  o papel ainda entregou final_answer depois: {int(C['papel_entregou_depois'].sum())}/{len(C)} · "
          f"execução terminou com resposta: {int(C['execucao_com_resposta'].sum())}/{len(C)}")
    print("\n[6] cascata — o que vem logo depois:")
    for k, n in C["proximo"].value_counts().items():
        print(f"  {n:4d}  {k}")
    print(f"  repetiu o mesmo erro logo depois: {int(C['repetiu_logo_depois'].sum())} · erros seguidos depois: "
          f"total {int(C['cascata_depois'].sum())}, máx {int(C['cascata_depois'].max())}")
    print("\n[7] versões do formato no system prompt, nos papéis com o erro (hash das linhas de formato) — o MODO do agente:")
    print("  papel · versão · modo · meses (steps) · steps · erros · por 1k")
    for (role, vid), v in sorted(variantes.items(), key=lambda x: (x[0][0], min(x[1]["meses"]))):
        if role not in set(C["role"]): continue
        meses = ", ".join(f"{m} ({n})" for m, n in sorted(v["meses"].items()))
        print(f"  {role:20s} {vid} · {v['modo']:16s} · {meses} · {v['steps']:5d} · {v['erros']:3d} · "
              f"{v['erros'] / v['steps'] * 1000:6.1f}")
    print("  ler o texto de uma versão:  python drill_down.py protocolo --prompt <versão>")
    for eixo in ("modelo", "versão do agente"):
        print(f"\n[8] {eixo} que respondeu, nos papéis com o erro:  papel · {eixo} · meses (steps) · steps · erros · por 1k")
        for (role, ex, valor), v in sorted(por_modelo.items(), key=lambda x: (x[0][0], min(x[1]["meses"]))):
            if ex != eixo or role not in set(C["role"]): continue
            meses = ", ".join(f"{m} ({n})" for m, n in sorted(v["meses"].items()))
            print(f"  {role:20s} {valor:40s} · {meses} · {v['steps']:5d} · {v['erros']:3d} · {v['erros'] / v['steps'] * 1000:6.1f}")
    print(f"\n[9] M1 — resposta final fora do envelope (trechos de 5 palavras do que o modelo escreveu; limiar {M1_LIMIAR:.0%}):")
    print("  papel · erros · antecipou a resposta final entregue depois · mediana da sobreposição · copiou da observação anterior")
    for role in C["role"].value_counts().index:
        c = C[C["role"] == role]
        print(f"  {role:24s} {len(c):4d} · {int((c['sobreposicao_final'] >= M1_LIMIAR).sum()):3d}/{len(c)} · "
              f"{c['sobreposicao_final'].median():4.0%} · {int((c['sobreposicao_obs_anterior'] >= M1_LIMIAR).sum()):3d}/{len(c)}")
    print("  falso negativo conhecido: o LLM reescreve ao reembrulhar (10-racionais-protocolo-harness.md §4 M1)")
    print(f"\nCasos (com exec_id, para `evidencia`): {os.path.relpath(os.path.join(pasta, 'casos.csv'))} — não sai da máquina.")
    print(f"{'='*100}")

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
            "data": r["dat_hor_inio_exeo"],
            "lote_anomesdia": r["anomesdia"],
            "steps": steps,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
        return

    n_plan = sum(1 for s in steps if s.get("__class__") == "PlanningStep")
    n_action = len(steps) - n_plan
    print(f"{'='*100}\nexec_id={exec_id}  role={role}  status={r['cod_idef_stat_exeo_aget']}  "
          f"data={r['dat_hor_inio_exeo'][:19]} (lote {r['anomesdia']})  {len(steps)} steps ({n_action} ActionStep + {n_plan} PlanningStep)\n{'='*100}\n")
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
    elif cmd == "relogios":
        relogios()
    elif cmd == "residuo":
        residuo()
    elif cmd == "padrao":
        padrao(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "silenciosas":
        args = [a for a in sys.argv[2:] if a not in ("--motivos", "--forma")]
        silenciosas(args[0] if args else None, motivos="--motivos" in sys.argv[2:], forma="--forma" in sys.argv[2:])
    elif cmd == "critico":
        critico(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "protocolo" and "--casos" in sys.argv:
        resto = sys.argv[sys.argv.index("--casos") + 1:]
        if not resto:
            print("uso: python drill_down.py protocolo --casos <papel> [<versão>] [<quantos>]"); sys.exit(1)
        ver = next((a for a in resto[1:] if re.fullmatch(r"[0-9a-f]{8}", a)), None)
        qtd = next((int(a) for a in resto[1:] if a.isdigit() and not re.fullmatch(r"[0-9a-f]{8}", a)), 3)
        protocolo_casos(resto[0], ver, qtd)
    elif cmd == "protocolo":
        pr = [a.split("=", 1)[1] if "=" in a else None for a in sys.argv[2:] if a.startswith("--prompt")]
        if pr and pr[0] is None and len(sys.argv) > 3:
            pr = [sys.argv[sys.argv.index("--prompt") + 1]]
        protocolo(pr[0] if pr else None)
    elif cmd == "tempo":
        args = [a for a in sys.argv[2:] if not a.startswith("--mecanismo=")]
        mec = [a.split("=", 1)[1].split(",") for a in sys.argv[2:] if a.startswith("--mecanismo=")]
        tempo(args[0] if args else None, mec[0] if mec else None)
    elif cmd == "caso":
        args = [a for a in sys.argv[2:] if a != "--json"]
        as_json = "--json" in sys.argv[2:]
        caso(args[0], args[1], as_json=as_json)
    else:
        print(__doc__)
