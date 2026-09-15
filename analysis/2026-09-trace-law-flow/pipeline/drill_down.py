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

    python drill_down.py listar "Retorno é dict, agente indexa como lista"
        -> lista exec_id/role/mes candidatos pra essa assinatura

    python drill_down.py planos [n]
        -> lista exec_id/role/mes das execuções que têm PlanningStep (o módulo de
           plano nativo do smolagents, ligado por `planning_interval` — hoje só em
           RespostaBacen e CalculoTrabalhista; ver 04-roadmap.md item 10)

    python drill_down.py mecanismo "Retorno pode chegar como string" [n]
        -> lista exec_id/role/mes/step dos erros atribuídos a esse MECANISMO (a unidade
           de memória da §9 do notebook), não a uma mensagem de erro. Lê
           resultados/erros_mecanismo.csv, gerado pelo notebook — rode o notebook antes.
           Nome errado imprime a lista de mecanismos disponíveis.

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

Requer o trace cru (85cb11b5-....csv.xz) na raiz do repo. Nunca commitar a saída
deste script — ela reproduz nomes de clientes e números de processo em claro.
"""
import sys, os, json, re, random
import pandas as pd

TRACE = "../../../85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz"

def classify(m):
    if 'Could not index' in m: return 'Retorno é dict, agente indexa como lista'
    if 'does not support multiple positional' in m: return 'Argumento posicional onde só cabe nomeado'
    if 'unterminated' in m: return 'String não fechada (relatório longo em literal)'
    if 'regex pattern' in m: return 'Resposta sem bloco de código [INATIVO desde dez/2025]'
    if 'IndentationError' in m: return 'Indentação inválida'
    if 'leading zeros' in m: return 'Data DD/MM interpolada como número'
    if 'forgot a comma' in m or 'never closed' in m or 'invalid decimal' in m: return 'Texto do documento colado em literal'
    if 'SyntaxError' in m: return 'Sintaxe inválida (prosa vazando no código)'
    if 'is not defined' in m:
        v = re.search(r'variable `(\w+)`', m)
        if v and v.group(1) in {'json','pd','np','re','os','math','datetime'}: return 'Módulo usado sem import'
        return 'Variável inexistente (estado perdido)'
    if 'has no attribute' in m: return 'Objeto sem o atributo esperado'
    if 'not allowed' in m or 'explicitly allowed' in m or 'is not permitted' in m: return 'Import/ferramenta não autorizado'
    if 'ModuleNotFound' in m: return 'Módulo ausente no sandbox'
    if 'Forbidden' in m: return 'Operação proibida'
    if 'AgentGenerationError' in m or 'internally hosted' in m: return 'Falha do LLM interno'
    if 'Error code: 422' in m or 'UnprocessableEntity' in m: return 'HTTP 422'
    if 'JSONDecode' in m: return 'Retorno não era JSON'
    if 'KeyError' in m: return 'Campo ausente no retorno'
    if 'TypeError' in m: return 'Tipo diferente do esperado'
    if 'ValueError' in m: return 'Formato/valor inválido'
    if 'IndexError' in m: return 'Retorno vazio indexado'
    return 'Não classificado'

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
    elif cmd == "caso":
        args = [a for a in sys.argv[2:] if a != "--json"]
        as_json = "--json" in sys.argv[2:]
        caso(args[0], args[1], as_json=as_json)
    else:
        print(__doc__)
