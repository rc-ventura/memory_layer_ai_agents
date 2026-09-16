# -*- coding: utf-8 -*-
"""AUDITORIA INDEPENDENTE 2026-09-16 (fase 5) — re-verificação do nível BASE
(assinatura/erro/execução) APÓS as mudanças de 15/09/2026, direto do trace cru.

Independência: csv.DictReader + json + statistics puros, sem pandas, sem reutilizar
código do notebook. A classify_sig abaixo é reescrita do zero (nomes curtos meus).

Objeto: os números-manchete de docs/02-relatorio-achados.md (TL;DR, §2, §3, §3.1,
§3.4, §3.5, §3.6, §4) e de docs/01-racionais.md (§3, §4, §5).

Não commitar a saída: pode conter PII do payload (audit_out*.txt é git-ignored).
"""
import csv, json, lzma, re, statistics, sys
from collections import Counter, defaultdict

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
import os
# Caminho canônico corrigido 16/09/2026 (auditoria M2): ../../data/ a partir deste script.
TRACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data",
                      "85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz")

def classify_sig(m):
    # Reimplementação independente (mesma lógica de prioridades, reescrita).
    if 'Could not index' in m: return 'A_ret_dict'
    if 'does not support multiple positional' in m: return 'B_arg_pos'
    if 'unterminated' in m: return 'C_unterm'
    if 'regex pattern' in m: return 'D_sem_bloco'
    if 'IndentationError' in m: return 'E_indent'
    if 'leading zeros' in m: return 'F_data'
    if 'forgot a comma' in m or 'never closed' in m or 'invalid decimal' in m: return 'G_colado'
    if 'SyntaxError' in m: return 'H_sintaxe'
    if 'is not defined' in m:
        v = re.search(r'variable `(\w+)`', m)
        if v and v.group(1) in {'json','pd','np','re','os','math','datetime'}: return 'I_sem_import'
        return 'J_var_nao_def'
    if 'has no attribute' in m: return 'K_sem_atributo'
    if 'not allowed' in m or 'explicitly allowed' in m or 'is not permitted' in m: return 'L_bloqueado'
    if 'ModuleNotFound' in m: return 'M_mod_ausente'
    if 'Forbidden' in m: return 'N_proibido'
    if 'AgentGenerationError' in m or 'internally hosted' in m: return 'O_falha_llm'
    if 'Error code: 422' in m or 'UnprocessableEntity' in m: return 'P_http422'
    if 'JSONDecode' in m: return 'Q_nao_json'
    if 'KeyError' in m: return 'R_campo_ausente'
    if 'TypeError' in m: return 'S_tipo'
    if 'ValueError' in m: return 'T_valor'
    if 'IndexError' in m: return 'U_ret_vazio'
    return 'Z_NAO_CLASSIFICADO'

n_rows = 0
n_memo = 0
steps_total = 0
tokens_total = 0
tokens_err = 0
dur_err_sum = 0.0
err_lat_err_ids = set()
exec_stats = {}
traj = defaultdict(list)          # (eid, role) -> [step dicts]
sig_c = Counter()
role_steps = Counter()
role_errs = Counter()
exec_month = {}
month_tok = defaultdict(list)
mesme_por_ass = defaultdict(set)
execme_por_ass = defaultdict(set)
pos_tools = Counter()
nonparse = {"n": 0, "err": 0, "tok": 0}
max_tok_exec = ("", 0)

with lzma.open(TRACE, 'rt', encoding='utf-8') as f:
    rdr = csv.DictReader(f)
    for r in rdr:
        n_rows += 1
        memo_raw = r.get("txt_etap_memo")
        if not memo_raw: continue
        try: memo = json.loads(memo_raw)
        except Exception: continue
        n_memo += 1
        eid = r["cod_idef_exeo"]
        mes = r["anomesdia"][:6]
        exec_month[eid] = mes
        for role, stps in memo.items():
            if not isinstance(stps, list): continue
            acts = [s for s in stps if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
            for i, st in enumerate(acts):
                steps_total += 1
                tu = st.get("token_usage") or {}
                tt = tu.get("total_tokens") or 0
                tokens_total += tt
                e = st.get("error") or {}
                em = str(e.get("message") or "")
                ex = exec_stats.setdefault(eid, dict(tok=0, n_err=0))
                ex["tok"] += tt
                if ex["tok"] > max_tok_exec[1]: max_tok_exec = (eid, ex["tok"])
                role_steps[role] += 1
                month_tok[mes]  # touch
                code = st.get("code_action") or ""
                parseou = True
                try: compile(code, "<c>", "exec")
                except Exception: parseou = False
                if not parseou:
                    nonparse["n"] += 1; nonparse["tok"] += tt
                    if e: nonparse["err"] += 1
                if e:
                    sig = classify_sig(em)
                    sig_c[sig] += 1
                    tokens_err += tt
                    dur_err_sum += (st.get("timing") or {}).get("duration") or 0
                    ex["n_err"] += 1
                    role_errs[role] += 1
                    mesme_por_ass[sig].add(mes)
                    execme_por_ass[sig].add(eid)
                    mt = re.search(r"tool (\w+) does not support multiple positional", em)
                    if mt: pos_tools[mt.group(1)] += 1
                mim = st.get("model_input_messages")
                ctx = json.dumps(mim, ensure_ascii=False) if mim else ""
                aout = ""
                end = (st.get("timing") or {}).get("end_time") or ""
                if st.get("is_final_answer"):
                    aout = str(st.get("action_output") or "")
                traj[(eid, role)].append(dict(i=i, err=bool(e), em=em, sig=classify_sig(em) if e else None,
                                              ctx=ctx, aout=aout, end=end, isF=bool(st.get("is_final_answer"))))

for eid, v in exec_stats.items():
    month_tok[exec_month[eid]].append(v["tok"])

print(f"1. linhas CSV={n_rows} (esp. 1000) · execs c/ memória={n_memo} (esp. 840)")
print(f"2. ActionSteps={steps_total} (esp. 5.781) · erros={sum(sig_c.values())} ({sum(sig_c.values())/steps_total:.1%}) (esp. 498, 8,6%)")
n_exec_err = sum(1 for v in exec_stats.values() if v["n_err"] > 0)
print(f"3. execs com erro: {n_exec_err} ({n_exec_err/len(exec_stats):.1%}) (esp. 313, 37,3%)")
print(f"4. tokens={tokens_total:,} (esp. 142.613.752) · em erro={tokens_err:,} ({tokens_err/tokens_total:.1%}) (esp. 13.946.017, 9,8%)")
print(f"   latência em steps com erro: {dur_err_sum/60:,.1f} min (esp. 159)")
print(f"   exec mais cara: {max_tok_exec[1]:,} (esp. 5.908.703)")
print("5. assinaturas:")
for s, esp in [('C_unterm',159), ('A_ret_dict',136), ('H_sintaxe',39), ('B_arg_pos',35),
               ('D_sem_bloco',33), ('S_tipo',22), ('G_colado',20), ('L_bloqueado',11),
               ('J_var_nao_def',8), ('K_sem_atributo',8), ('I_sem_import',6), ('O_falha_llm',6),
               ('F_data',5), ('Z_NAO_CLASSIFICADO',1)]:
    st = "OK" if sig_c.get(s,0)==esp else "<< DIVERGE"
    print(f"   {s:20s} {sig_c.get(s,0):4d} (esp. {esp}) {st}")

n_traj = len(traj)
def traj_termina_erro(seq):
    seq = sorted(seq, key=lambda s: s["i"])
    return bool(seq) and bool(seq[-1]["err"])
term_err = sum(1 for seq in traj.values() if traj_termina_erro(seq))
n_final = sum(1 for seq in traj.values() if any(s["isF"] for s in seq))
print(f"6. trajetórias={n_traj} (esp. 1.550) · terminam em erro={term_err} (esp. 0) · chegam a final_answer={n_final} (esp. 1.549)")

tok_com = [v["tok"] for v in exec_stats.values() if v["n_err"] > 0]
tok_sem = [v["tok"] for v in exec_stats.values() if v["n_err"] == 0]
st_com = [len([1 for s in seq if True]) for seq in traj.values()]
# steps per execution com/sem erro (mediana)
steps_exec = defaultdict(int)
for (eid, role), seq in traj.items(): steps_exec[eid] += len(seq)
sp_com = [steps_exec[e] for e,v in exec_stats.items() if v["n_err"]>0]
sp_sem = [steps_exec[e] for e,v in exec_stats.items() if v["n_err"]==0]
print(f"7. mediana tok exec COM erro: {statistics.median(tok_com):,.0f} (esp. 146.306) · SEM: {statistics.median(tok_sem):,.0f} (esp. 47.884)")
print(f"   mediana steps COM erro: {statistics.median(sp_com):.0f} (esp. 7) · SEM: {statistics.median(sp_sem):.0f} (esp. 5)")

ee=en=ne=nn=0
for seq0 in traj.values():
    seq = sorted(seq0, key=lambda s: s["i"])
    for j in range(len(seq)-1):
        a,b = seq[j]["err"], seq[j+1]["err"]
        if a and b: ee+=1
        elif a: en+=1
        elif b: ne+=1
        else: nn+=1
print(f"8. P(err k+1|err k)={ee/(ee+en):.1%} · P(err k+1|ok k)={ne/(ne+nn):.1%} · razão {ee/(ee+en)/(ne/(ne+nn)):.1f}× (esp. 17,7%/9,7%/1,8×)")

# resultado central: contexto + repetição (prefixo 45), classify independente
checked=reached=repeated=same=0
for seq0 in traj.values():
    seq = sorted(seq0, key=lambda s: s["i"])
    for j in range(len(seq)-1):
        s0,s1 = seq[j], seq[j+1]
        if not s0["err"]: continue
        checked += 1
        core = re.sub(r"\s+"," ", s0["em"])[:45]
        if core and core in re.sub(r"\s+"," ", s1["ctx"]):
            reached += 1
            if s1["err"]:
                repeated += 1
                if classify_sig(s0["em"]) == classify_sig(s1["em"]): same += 1
print(f"9. erro seguido de step={checked} (esp. 498) · contexto={reached} ({reached/checked:.1%}) (esp. 430/86,3%)")
print(f"   repetiram={repeated} ({repeated/reached:.1%}) (esp. 76/17,7%) · mesma assinatura={same} ({same/reached:.1%}) (esp. 51/11,9%)")

toks = sorted((v["tok"] for v in exec_stats.values()), reverse=True)
tot = sum(toks)
for pct,esp in [(1,'16,8%'),(5,'41,9%'),(10,'54,6%'),(20,'69,1%'),(50,'89,8%')]:
    k = max(1, round(len(toks)*pct/100))
    print(f"10. top {pct}% ({k} execs): {sum(toks[:k])/tot:.1%} (esp. {esp})")

print("11. taxa de erro por papel:")
for role in ["CadastroTrabalhista","CalculoCivel","RespostaBacen","RoteadorCivel","ConversationAgent","managerAgent","WorkflowManager"]:
    s,e = role_steps[role], role_errs[role]
    print(f"    {role:20s} {e:3d}/{s:4d} = {e/s:.1%}")

# sucesso por conteúdo — com a MESMA seleção documentada (final do managerAgent,
# fallback = último is_final por end_time entre TODOS os papéis) e 2 frases exatas
DEG = re.compile(r"n[ãa]o encontrad[oa] na base|informa[çc][ãa]o insuficiente", re.I)
by_exec = defaultdict(list)
for (eid,role),seq in traj.items():
    for s in seq: by_exec[eid].append((role,s))
n_tot=n_suc=n_suc_err=n_fb=0
for eid,(items) in by_exec.items():
    mgr, mgr_end, any_t, any_end = None, "", None, ""
    for role,s in items:
        if not s["isF"]: continue
        if str(s["end"]) >= str(any_end): any_t, any_end = s["aout"], s["end"]
        if role=="managerAgent" and str(s["end"]) >= str(mgr_end): mgr, mgr_end = s["aout"], s["end"]
    txt = mgr if mgr is not None else any_t
    if mgr is None and txt is not None: n_fb += 1
    if txt is None: continue
    n_tot += 1
    if not (DEG.search(txt) or len(txt.strip()) < 15):
        n_suc += 1
        if exec_stats[eid]["n_err"] > 0: n_suc_err += 1
print(f"12. execs c/ resolução: {n_tot} (esp. 840) · fallback={n_fb} (esp. 134)")
print(f"    conteúdo={n_suc} ({n_suc/n_tot:.1%}) (esp. 834/99,3%) · com erro={n_suc_err} ({n_suc_err/n_suc:.1%}) (esp. 310/37,2%)")

print("13. mediana tokens/execução por mês:")
for m in sorted(month_tok):
    v = month_tok[m]
    print(f"    {m}: n={len(v):3d} mediana={statistics.median(v):,.0f}")

print("14. reincidência entre execuções (por assinatura):")
print(f"    String não fechada: {len(execme_por_ass['C_unterm'])} exec / {len(mesme_por_ass['C_unterm'])} meses (esp. 125/8)")
print(f"    Retorno é dict:     {len(execme_por_ass['A_ret_dict'])} exec / {len(mesme_por_ass['A_ret_dict'])} meses (esp. 119/7)")

print(f"15. steps não parseáveis: {nonparse['n']} (esp. 224) · com erro: {nonparse['err']} (esp. 224 = 100%) · tokens: {nonparse['tok']:,} (esp. ~5,50M)")
print(f"16. ferramentas distintas em msgs 'positional': {len(pos_tools)} (esp. 12)")
