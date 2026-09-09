# -*- coding: utf-8 -*-
"""AUDITORIA fase 2 — contexto, candidatos, detectores, pendências da fase 1.
Independente do notebook (csv + json + ast, sem pandas)."""
import csv, json, lzma, re, sys, ast
from collections import Counter, defaultdict

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

header = None
traj = defaultdict(list)
exec_tok = Counter(); exec_err = Counter()
dur_err_sum = 0.0
err_rows = []
CASE = "2a407143-c37d-687f-4b4a-45f8dc413734"
posicional_msgs = []

with lzma.open(TRACE, 'rt', encoding='utf-8') as f:
    rdr = csv.DictReader(f)
    header = rdr.fieldnames
    for r in rdr:
        memo_raw = r.get("txt_etap_memo")
        if not memo_raw: continue
        try: memo = json.loads(memo_raw)
        except Exception: continue
        eid = r["cod_idef_exeo"]; mes = r["anomesdia"][:6]
        for role, stps in memo.items():
            if not isinstance(stps, list): continue
            acts = [s for s in stps if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
            for i, st in enumerate(acts):
                tu = st.get("token_usage") or {}; tt = tu.get("total_tokens") or 0
                e = st.get("error") or {}; em = str(e.get("message") or "")
                mim = st.get("model_input_messages")
                sysp = ""
                if mim:
                    m0 = mim[0] if isinstance(mim[0], dict) else {}
                    c = m0.get("content")
                    sysp = c[0].get("text","") if isinstance(c, list) and c and isinstance(c[0], dict) else str(c or "")
                traj[(eid, role)].append({
                    "idx": i, "err": bool(e), "em": em, "sig": classify_sig(em) if e else None,
                    "tok": tt, "dur": (st.get("timing") or {}).get("duration") or 0,
                    "end": (st.get("timing") or {}).get("end_time") or 0,
                    "is_final": bool(st.get("is_final_answer")),
                    "aout": str(st.get("action_output") or "") if st.get("is_final_answer") else None,
                    "code": st.get("code_action") or "",
                    "sysp": sysp,
                    "ctx": json.dumps(mim, ensure_ascii=False) if mim else "",
                })
                exec_tok[eid] += tt
                if e:
                    exec_err[eid] += 1; dur_err_sum += traj[(eid, role)][-1]["dur"]
                    err_rows.append((classify_sig(em), eid, role, mes, tt))
                    if 'does not support multiple positional' in em and len(posicional_msgs) < 3:
                        posicional_msgs.append(em[:200])

for k in traj: traj[k].sort(key=lambda x: x["idx"])

print(f"A. header ({len(header)} campos): {header}")
print(f"B. latência de steps com erro: {dur_err_sum/60:,.1f} min (esperado 159)")

sem_final = [k for k, seq in traj.items() if not any(s["is_final"] for s in seq)]
print(f"C. trajetórias sem final_answer: {len(sem_final)} → {[(k[0][:8], k[1], sum(1 for s in traj[k] if s['err'])) for k in sem_final]}")

checked = reached = repeated = same = 0
maxrun, maxrun_key = 0, None
for k, seq in traj.items():
    run = 1
    for j in range(len(seq)-1):
        s0, s1 = seq[j], seq[j+1]
        if s0["err"]:
            checked += 1
            core = re.sub(r"\s+", " ", s0["em"])[:45]
            if core and core in re.sub(r"\s+", " ", s1["ctx"]):
                reached += 1
                if s1["err"]:
                    repeated += 1
                    if s0["sig"] == s1["sig"]: same += 1
        if s0["err"] and s1["err"] and s0["sig"] == s1["sig"]:
            run += 1
            if run > maxrun: maxrun, maxrun_key = run, k
        else:
            run = 1
print(f"D. erro→contexto k+1: {reached}/{checked} = {reached/checked:.1%} (esperado 430/498 = 86,3%)")
print(f"   repetiram: {repeated} ({repeated/reached:.1%}) · mesma causa: {same} ({same/reached:.1%})  (esperado 76/17,7% · 51/11,9%)")
print(f"   recorde global de repetições consecutivas mesma-causa: {maxrun} em {maxrun_key[0]} / {maxrun_key[1]} (relatório cita 10 em 2a407143…/managerAgent)")
seq_case = traj.get((CASE, "managerAgent"))
if seq_case:
    run = best = 1
    for j in range(len(seq_case)-1):
        if seq_case[j]["err"] and seq_case[j+1]["err"] and seq_case[j]["sig"] == seq_case[j+1]["sig"]:
            run += 1; best = max(best, run)
        else: run = 1
    print(f"   caso citado: maior sequência = {best} · erros totais = {sum(1 for s in seq_case if s['err'])} · steps = {len(seq_case)}")

DEG = re.compile(r"n[ãa]o encontrad[oa] na base|informa[çc][ãa]o insuficiente", re.I)
by_exec = defaultdict(list)
for (eid, role), seq in traj.items():
    for s in seq: by_exec[eid].append((role, s))
n_total = n_suc = n_suc_err = n_fallback = 0
for eid, items in by_exec.items():
    mgr_txt, mgr_end, out_txt, out_end = None, -1, None, -1
    for role, s in items:
        if s["is_final"]:
            if s["end"] > out_end: out_txt, out_end = s["aout"], s["end"]
            if role == "managerAgent" and s["end"] > mgr_end: mgr_txt, mgr_end = s["aout"], s["end"]
    final_txt = mgr_txt if mgr_txt is not None else out_txt
    if mgr_txt is None and final_txt is not None: n_fallback += 1
    if final_txt is None: continue
    n_total += 1
    deg = bool(DEG.search(final_txt)) or len(final_txt.strip()) < 15
    if not deg:
        n_suc += 1
        if exec_err.get(eid, 0) > 0: n_suc_err += 1
print(f"E. execs com final_answer: {n_total} · sem final do managerAgent (fallback): {n_fallback}")
print(f"   conteúdo: {n_suc} ({n_suc/n_total:.1%}) · com erro: {n_suc_err} ({n_suc_err/n_suc:.1%})  (esperado 840 · 834/99,3% · 310/37,2%)")

agg = defaultdict(lambda: [0, set(), set(), 0])
for sig, eid, role, mes, tok in err_rows:
    a = agg[sig]; a[0] += 1; a[1].add(eid); a[2].add(mes); a[3] += tok
for sig, esp in [("Retorno é dict","136/119ex/7m/4.687.425 tok"), ("String não fechada","159/125/8/3.572.698"),
                 ("Argumento posicional","35/22/6/364.543"), ("Import não autorizado","11/11/6/907.471 (CSV); relatório diz 19/1,06M"),
                 ("Variável inexistente","8/7/4/299.222"), ("Falha LLM interno","6/6/3/23.249 (CSV); relatório diz 7/0,12M")]:
    a = agg[sig]
    print(f"F. {sig:24s} erros={a[0]} execs={len(a[1])} meses={len(a[2])} tok={a[3]:,}   [esperado: {esp}]")
for nome, grupo in [("sandbox", ('Import não autorizado','Módulo sem import','Módulo ausente','Operação proibida')),
                    ("infra", ('Falha LLM interno','HTTP 422'))]:
    er = sum(agg[s][0] for s in grupo); ex = len(set().union(*(agg[s][1] for s in grupo)))
    me = len(set().union(*(agg[s][2] for s in grupo))); tk = sum(agg[s][3] for s in grupo)
    print(f"   combo {nome}: erros={er} execs={ex} meses={me} tok={tk:,}")

INV = set(); call_count = Counter()
ignored = total_assign = rac_n = 0
for seq in traj.values():
    for s in seq:
        for nome in re.findall(r"def\s+(\w+)\s*\(", s["sysp"] or ""):
            INV.add(nome)
for seq in traj.values():
    trees = []
    for s in seq:
        try: trees.append(ast.parse(s["code"]))
        except Exception: trees.append(None)
    later = [{n.id for n in ast.walk(t) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)} if t else set() for t in trees]
    seen_traj = Counter()
    for i, (s, t) in enumerate(zip(seq, trees)):
        if t is None: continue
        fut = set().union(*later[i:]) if later[i:] else set()
        for n in ast.walk(t):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                if n.func.id in INV:
                    call_count[n.func.id] += 1
                    if not s["err"]:
                        try: seen_traj[(n.func.id, ast.dump(n))] += 1
                        except Exception: pass
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name):
                if n.value.func.id in INV and n.value.func.id != "final_answer":
                    total_assign += 1
                    tg = [x.id for x in n.targets if isinstance(x, ast.Name)]
                    if tg and not any(x in fut for x in tg): ignored += 1
    for key, c in seen_traj.items():
        if c > 1 and key[0] != "final_answer":
            rac_n += c - 1
print(f"G. ferramentas declaradas: {len(INV)} (esperado 90) · distintas chamadas no código: {sum(1 for v in call_count if v in INV)}")
print(f"   answer_question_using_documents: {call_count.get('answer_question_using_documents',0)} (esperado 821) · get_available_documents: {call_count.get('get_available_documents',0)} (esperado 730)")

execs_fin = defaultdict(bool); execs_tool = Counter()
for (eid, role), seq in traj.items():
    for s in seq:
        try: t = ast.parse(s["code"])
        except Exception: continue
        for n in ast.walk(t):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                if n.func.id == "final_answer": execs_fin[eid] = True
                elif n.func.id in INV: execs_tool[eid] += 1
tool_skip = sum(1 for e in execs_fin if execs_fin[e] and execs_tool.get(e, 0) == 0)
print(f"H. Result-Ignore: {ignored}/{total_assign} ({ignored/total_assign:.1%})  (esperado 103/3.053 = 3,4%)")
print(f"   RAC conservador: {rac_n} (esperado 125)")
print(f"   Tool-Skip provisório: {tool_skip} de {len(execs_fin)} execs com final_answer (esperado 10 de 840)")

top_exec = max(exec_tok.values())
print(f"I. exec mais cara: {top_exec:,} tokens (relatório fala 5,9M)")

print("J. amostra de msgs 'does not support multiple positional' (para origem do '12 ferramentas'):")
for m in posicional_msgs: print("   |", m.replace(chr(10), " ")[:160])
