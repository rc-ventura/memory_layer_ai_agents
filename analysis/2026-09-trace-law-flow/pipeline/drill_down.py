# -*- coding: utf-8 -*-
"""
Ferramenta de triangulação: parte de um achado agregado (uma assinatura de erro,
uma família) e mostra o(s) caso(s) concreto(s) no trace cru que o sustentam.

Uso:
    python drill_down.py listar "Retorno é dict, agente indexa como lista"
        -> lista exec_id/role/mes candidatos pra essa assinatura

    python drill_down.py caso <exec_id> <role>
        -> imprime a trajetória inteira daquele papel naquela execução:
           thought, código, observação e erro de cada step, na ordem em que
           aconteceram — o material bruto por trás de qualquer número do relatório.

Requer o trace cru (85cb11b5-....csv.xz) na raiz do repo. Nunca commitar a saída
deste script — ela reproduz nomes de clientes e números de processo em claro.
"""
import sys, json, re
import pandas as pd

TRACE = "../../../85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz"

def classify(m):
    if 'Could not index' in m: return 'Retorno é dict, agente indexa como lista'
    if 'does not support multiple positional' in m: return 'Argumento posicional onde só cabe nomeado'
    if 'unterminated' in m: return 'String não fechada (relatório longo em literal)'
    if 'regex pattern' in m: return 'Resposta sem bloco de código [RESOLVIDO]'
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

def load():
    return pd.read_csv(TRACE, dtype=str)

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

def caso(exec_id, role):
    df = load()
    row = df[df["cod_idef_exeo"] == exec_id]
    if row.empty:
        print(f"exec_id {exec_id} não encontrado."); return
    r = row.iloc[0]
    memo = json.loads(r["txt_etap_memo"])
    steps = [s for s in memo.get(role, []) if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
    if not steps:
        print(f"papel '{role}' não tem ActionStep nesta execução. Papéis disponíveis: {list(memo.keys())}")
        return
    print(f"{'='*100}\nexec_id={exec_id}  role={role}  status={r['cod_idef_stat_exeo_aget']}  "
          f"data={r['anomesdia']}  {len(steps)} steps\n{'='*100}\n")
    for st in steps:
        e = st.get("error") or {}
        tu = st.get("token_usage") or {}
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
    if cmd == "listar":
        listar(sys.argv[2])
    elif cmd == "caso":
        caso(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
