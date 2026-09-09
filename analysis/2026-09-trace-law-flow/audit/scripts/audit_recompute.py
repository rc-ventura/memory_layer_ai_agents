# -*- coding: utf-8 -*-
"""AUDITORIA INDEPENDENTE — recomputa os números-chave do relatório direto do
trace cru, com csv.DictReader + json + statistics (sem pandas, sem reutilizar
código do notebook). Roda da pasta analysis/2026-09-trace-law-flow/.

Não commitar a saída: pode conter PII do payload.
"""
import csv, json, lzma, re, statistics, sys
from collections import Counter, defaultdict

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

TRACE = "/Users/rafaelventura/ICT-ITAU/memory_layer_ai_agents/85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz"

def classify_sig(m):
    # reimplementação independente da classify() do notebook (mesmas regras,
    # reescrita do zero a partir da leitura da tabela do relatório)
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

n_rows = 0
n_memo = 0
steps_total = 0
errs = []                       # (exec_id, role, idx, sig, tok_tot, dur, mes)
exec_stats = {}                 # exec_id -> dict(tok, n_err, n_steps, mes)
traj = defaultdict(list)        # (exec_id, role) -> [(idx, err_bool, err_msg)]
traj_final = defaultdict(bool)  # (exec_id, role) -> is_final any
traj_last_err = 0
tokens_total = 0
role_steps = Counter(); role_errs = Counter()
tokens_err = 0
final_answer_txt = {}

with lzma.open(TRACE, 'rt', encoding='utf-8') as f:
    rdr = csv.DictReader(f)
    cols = rdr.fieldnames
    for r in rdr:
        n_rows += 1
        memo_raw = r.get("txt_etap_memo")
        if not memo_raw:
            continue
        try:
            memo = json.loads(memo_raw)
        except Exception:
            continue
        n_memo += 1
        eid = r["cod_idef_exeo"]
        mes = r["anomesdia"][:6]
        for role, stps in memo.items():
            if not isinstance(stps, list): continue
            acts = [s for s in stps if isinstance(s, dict) and s.get("__class__") == "ActionStep"]
            for i, st in enumerate(acts):
                steps_total += 1
                tu = st.get("token_usage") or {}
                tt = tu.get("total_tokens") or 0
                e = st.get("error") or {}
                em = str(e.get("message") or "")
                tokens_total += tt
                role_steps[role] += 1
                ex = exec_stats.setdefault(eid, dict(tok=0, n_err=0, mes=mes))
                ex["tok"] += tt
                if e:
                    sig = classify_sig(em)
                    errs.append((eid, role, i, sig, tt, (st.get("timing") or {}).get("duration"), mes))
                    ex["n_err"] += 1
                    role_errs[role] += 1
                    tokens_err += tt
                traj[(eid, role)].append((i, bool(e), em))
                if st.get("is_final_answer"):
                    traj_final[(eid, role)] = True
                    txt = str(st.get("action_output") or "")
                    if role == "managerAgent" and txt:
                        final_answer_txt[eid] = txt

print(f"1. linhas no CSV: {n_rows} (esperado 1000) · colunas: {len(cols)}")
print(f"2. execuções com memória: {n_memo} (esperado 840)")
print(f"3. ActionSteps: {steps_total} (esperado 5.781)")
print(f"4. steps com erro: {len(errs)} ({len(errs)/steps_total:.1%}) (esperado 498, 8,6%)")
n_exec_err = sum(1 for v in exec_stats.values() if v["n_err"] > 0)
print(f"5. execuções com ≥1 erro: {n_exec_err} ({n_exec_err/len(exec_stats):.1%}) (esperado 313, 37,3%)")
print(f"6. tokens totais: {tokens_total:,} (esperado 142.613.752)")
print(f"   tokens em steps com erro: {tokens_err:,} ({tokens_err/tokens_total:.1%}) (esperado ~13,95M, 9,8%)")

# famílias dominantes
sig_c = Counter(e[3] for e in errs)
for nome, esperado in [("String não fechada",159), ("Retorno é dict",136),
                       ("Argumento posicional",35), ("Sem bloco de código",33),
                       ("Sintaxe inválida",39), ("Texto colado em literal",20)]:
    print(f"7. assinatura '{nome}': {sig_c.get(nome,0)} (esperado {esperado})")
print(f"   não classificados: {sig_c.get('NÃO CLASSIFICADO',0)} (esperado 1)")

# 0 de 1550 trajetórias terminam em erro
n_traj = len(traj)
terminam_erro = 0
for k, seq in traj.items():
    seq.sort()
    if seq and seq[-1][1]: terminam_erro += 1
print(f"8. trajetórias: {n_traj} (esperado 1.550) · terminam em erro: {terminam_erro} (esperado 0)")
chegam = sum(1 for k, v in traj_final.items() if v)
print(f"   trajetórias que chegam a final_answer: {chegam} de {n_traj}")

# custo por execução com/sem erro (medianas)
tok_com = [v["tok"] for v in exec_stats.values() if v["n_err"] > 0]
tok_sem = [v["tok"] for v in exec_stats.values() if v["n_err"] == 0]
print(f"9. mediana tokens exec COM erro: {statistics.median(tok_com):,.0f} (esperado ~146 mil)")
print(f"   mediana tokens exec SEM erro: {statistics.median(tok_sem):,.0f} (esperado ~48 mil)")

# propagação
ee = en = ne = nn = 0
for k, seq in traj.items():
    seq.sort()
    for j in range(len(seq)-1):
        a, b = seq[j][1], seq[j+1][1]
        if a and b: ee += 1
        elif a: en += 1
        elif b: ne += 1
        else: nn += 1
print(f"10. P(err k+1|err k)={ee/(ee+en):.1%} · P(err k+1|ok k)={ne/(ne+nn):.1%} · razão {ee/(ee+en)/(ne/(ne+nn)):.1f}× (esperado 17,7%/9,7%/1,8×)")

# 86,3% / 17,7% / 11,9% — checagem de contexto exige o campo model_input_messages,
# que este script não carrega; medida separada no audit_contexto.py se preciso.
checked = sum(1 for seq in traj.values() for j in range(len(seq)-1) if sorted(seq)[j][1])
print(f"11. steps com erro seguidos de outro step: {checked} (esperado 498)")

# Pareto
toks = sorted((v["tok"] for v in exec_stats.values()), reverse=True)
tot = sum(toks)
for pct, esp in [(1,"16,8%"), (5,"41,9%"), (10,"54,6%")]:
    k = max(1, round(len(toks)*pct/100))
    print(f"12. top {pct}% ({k} execs) concentra {sum(toks[:k])/tot:.1%} (esperado {esp})")

# por papel (taxa de erro)
print("13. taxa de erro por papel (steps >= 30):")
for role in ["CadastroTrabalhista","CalculoCivel","RespostaBacen","RoteadorCivel","ConversationAgent","managerAgent","WorkflowManager"]:
    s, e = role_steps.get(role,0), role_errs.get(role,0)
    print(f"    {role:22s} {e:4d}/{s:5d} = {e/s:.1%}")

# sucesso por conteúdo
DEG = re.compile(r"n[ãa]o encontrad[oa] na base|informa[çc][ãa]o insuficiente", re.I)
n_fa = len(final_answer_txt)
deg = [eid for eid, t in final_answer_txt.items() if DEG.search(t) or len(t.strip()) < 15]
suc = set(final_answer_txt) - set(deg)
suc_err = sum(1 for eid in suc if exec_stats.get(eid,{}).get("n_err",0) > 0)
print(f"14. execs com final_answer: {n_fa} (esperado 840) · degeneradas: {len(deg)} (esperado 6)")
print(f"    conteúdo: {len(suc)} ({len(suc)/n_fa:.1%}) · com erro: {suc_err} ({suc_err/len(suc):.1%}) (esperado 834/99,3% · 310/37,2%)")

# evolução mensal
pm = defaultdict(list)
for v in exec_stats.values(): pm[v["mes"]].append(v["tok"])
print("15. mediana tokens/execução por mês:")
for m in sorted(pm):
    print(f"    {m}: n={len(pm[m]):3d} mediana={statistics.median(pm[m]):,.0f}")

# reincidência
rec_m = defaultdict(set); rec_e = defaultdict(set)
for eid, role, i, sig, tt, dur, mes in errs:
    rec_m[sig].add(mes); rec_e[sig].add(eid)
print(f"16. 'String não fechada': {len(rec_e['String não fechada'])} execs / {len(rec_m['String não fechada'])} meses (esperado 125/8)")
print(f"    'Retorno é dict':     {len(rec_e['Retorno é dict'])} execs / {len(rec_m['Retorno é dict'])} meses (esperado 119/7)")
