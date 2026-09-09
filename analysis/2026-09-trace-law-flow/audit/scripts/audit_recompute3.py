# -*- coding: utf-8 -*-
"""AUDITORIA fase 3 — durações, razões in/out, eficiência, desperdício, papel×assinatura."""
import csv, json, lzma, re, sys, ast
from collections import Counter, defaultdict
from statistics import median

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
TRACE = "/Users/rafaelventura/ICT-ITAU/memory_layer_ai_agents/85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz"

def classify_sig(m):
    if 'Could not index' in m: return 'Retorno é dict'
    if 'does not support multiple positional' in m: return 'Argumento posicional'
    if 'unterminated' in m: return 'String não fechada'
    if 'regex pattern' in m: return 'Sem bloco de código'
    if 'IndentationError' in m: return 'Indentação inválida'
    if 'leading zeros' in m: return 'Data DD/MM'
    if 'forgot a comma' in m or 'never closed' in m or 'invalid decimal' in m: return 'Texto colado em literal'
    if 'SyntaxError' in m: return 'Sintaxe inválida'
    if 'is not defined' in m:
        v = re.search(r'variable `(\w+)`', m)
        if v and v.group(1) in {'json','pd','np','re','os','math','datetime'}: return 'Módulo sem import'
        return 'Variável inexistente'
    if 'has no attribute' in m: return 'Sem atributo'
    if 'not allowed' in m or 'explicitly allowed' in m or 'is not permitted' in m: return 'Import não autorizado'
    if 'ModuleNotFound' in m: return 'Módulo ausente'
    if 'Forbidden' in m: return 'Operação proibida'
    if 'AgentGenerationError' in m or 'internally hosted' in m: return 'Falha LLM interno'
    if 'Error code: 422' in m or 'UnprocessableEntity' in m: return 'HTTP 422'
    if 'JSONDecode' in m: return 'Retorno não era JSON'
    if 'KeyError' in m: return 'Campo ausente'
    if 'TypeError' in m: return 'Tipo diferente'
    if 'ValueError' in m: return 'Formato/valor inválido'
    if 'IndexError' in m: return 'Retorno vazio indexado'
    return 'NÃO CLASSIFICADO'

# checagem do header vs nº de campos (pandas diz 12 colunas; csv.DictReader achou 11 nomes)
with lzma.open(TRACE, 'rt', encoding='utf-8') as f:
    first = f.readline()
    second = f.readline(10_000_000)
print(f"A1. campos no header: {len(next(csv.reader([first])))} · campos na 1ª linha de dados: {len(next(csv.reader([second])))}")

ok_ratios, err_by_sig = [], defaultdict(lambda: {"dur": [], "ratio": [], "tok": 0, "exec": set(), "mes": set(), "roles": Counter()})
role_tok = Counter(); role_tok_err = Counter(); role_calls = Counter(); role_tok_all = Counter()
errors_role_sig = defaultdict(Counter)
exec_calls = defaultdict(lambda: [0, 0])   # eid -> [calls, tok]
INV = set()

with lzma.open(TRACE, 'rt', encoding='utf-8') as f:
    rdr = csv.DictReader(f)
    for r in rdr:
        memo_raw = r.get("txt_etap_memo")
        if not memo_raw: continue
        try: memo = json.loads(memo_raw)
        except Exception: continue
        eid = r["cod_idef_exeo"]; mes = r["anomesdia"][:6]
        for role, stps in memo.items():
            if not isinstance(stps, list): continue
            acts = [s for s in stps if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
            for st in acts:
                tu = st.get("token_usage") or {}
                ti, to, tt = tu.get("input_tokens") or 0, tu.get("output_tokens") or 0, tu.get("total_tokens") or 0
                e = st.get("error") or {}
                role_tok_all[role] += tt
                exec_calls[eid][1] += tt
                if e:
                    sig = classify_sig(str(e.get("message") or ""))
                    d = err_by_sig[sig]
                    d["dur"].append((st.get("timing") or {}).get("duration"))
                    d["tok"] += tt; d["exec"].add(eid); d["mes"].add(mes); d["roles"][role] += 1
                    errors_role_sig[role][sig] += 1
                    role_tok_err[role] += tt
                    if to > 0: d["ratio"].append(ti / to)
                elif to > 0:
                    ok_ratios.append(ti / to)

print(f"A2. mediana in/out steps OK: {median(ok_ratios):.1f} (esperado 33,5)")
print("A3. duração mediana + razão in/out por assinatura:")
for sig, esp in [("String não fechada","15,3s n=159 ratio 17,5"), ("Sintaxe inválida","RELAT DIZ 11,5s n=64 (CSV diz n=39!)"),
                 ("Sem bloco de código","15,6s n=33"), ("Retorno é dict","7,7s n=136 ratio 58,9"),
                 ("Texto colado em literal","15,6s n=20"), ("Falha LLM interno","v1 dizia 115,2s n=6"),
                 ("Módulo sem import","v1 dizia 65s n=6")]:
    d = err_by_sig.get(sig)
    if not d: print(f"    {sig:24s} AUSENTE"); continue
    dur = [x for x in d["dur"] if x is not None]
    r = f"ratio_med={median(d['ratio']):.1f}" if d["ratio"] else "ratio n/a"
    print(f"    {sig:24s} mediana={median(dur):6.1f}s  n={len(dur):3d}  {r}   [{esp}]")
fl = sorted(x for x in err_by_sig["Falha LLM interno"]["dur"] if x is not None)
mi = sorted(x for x in err_by_sig["Módulo sem import"]["dur"] if x is not None)
print(f"    Falha LLM interno brutos: {fl}")
print(f"    Módulo sem import brutos: {mi}")

print("A4. papel × assinatura (% dos erros DO papel; n≥5):")
for role, esp in [("CadastroTrabalhista","94% arg posicional n=18"), ("CalculoCivel","76% retorno-dict n=17"),
                  ("RespostaBacen","62% retorno-dict n=24"), ("managerAgent","56% string-não-fechada n=180"),
                  ("ConversationAgent","45% dict + 24% string n=224, sem dominante")]:
    c = errors_role_sig.get(role, Counter()); tot = sum(c.values())
    top = c.most_common(2)
    txt = ", ".join(f"{s}={n} ({n/tot:.0%})" for s, n in top)
    print(f"    {role:22s} n={tot}: {txt}   [{esp}]")

print("A5. desperdício por papel (tok_total ≥ 50k):")
for role in sorted(role_tok_all, key=lambda x: -role_tok_err.get(x, 0))[:6]:
    t, e = role_tok_all[role], role_tok_err.get(role, 0)
    print(f"    {role:22s} total={t/1e6:5.1f}M erro={e/1e6:5.2f}M ({e/t*100:.1f}%)")

# tokens/chamada por papel — precisa AST; reusa s abordagem documentada (sysprompt[0] por step)
INV = set()
per_role = defaultdict(lambda: [0, 0])
with lzma.open(TRACE, 'rt', encoding='utf-8') as f:
    rdr = csv.DictReader(f)
    for r in rdr:
        memo_raw = r.get("txt_etap_memo")
        if not memo_raw: continue
        try: memo = json.loads(memo_raw)
        except Exception: continue
        eid = r["cod_idef_exeo"]
        for role, stps in memo.items():
            if not isinstance(stps, list): continue
            for st in stps:
                if not isinstance(st, dict) or st.get("__class__") != "ActionStep": continue
                mim = st.get("model_input_messages")
                sysp = ""
                if mim:
                    m0 = mim[0] if isinstance(mim[0], dict) else {}
                    c = m0.get("content")
                    sysp = c[0].get("text","") if isinstance(c, list) and c and isinstance(c[0], dict) else str(c or "")
                for nome in re.findall(r"def\s+(\w+)\s*\(", sysp): INV.add(nome)
                tt = (st.get("token_usage") or {}).get("total_tokens") or 0
                per_role[role][0] += tt
                try: tree = ast.parse(st.get("code_action") or "")
                except Exception: continue
                # NB: a célula 19 do notebook NÃO exclui final_answer — réplica idêntica
                nc = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in INV)
                per_role[role][1] += nc
                exec_calls[eid][0] += nc
print("A6. tokens por chamada de ferramenta declarada:")
vals = []
for role, (tk, ca) in per_role.items():
    if ca > 0:
        vals.append((role, tk, ca))
        print(f"    {role:22s} {tk/ca:10,.0f} tok/chamada  ({tk:,} tok / {ca:,} chamadas)")
tot_t = sum(v[1] for v in vals); tot_c = sum(v[2] for v in vals)
ratios = [tk/ca for tk, ca in exec_calls.values() if ca > 0]
print(f"    razão agregada: {tot_t/tot_c:,.0f} (esperado 21.420) · mediana por exec: {median(ratios):,.0f} (esperado 12.192)")
