# -*- coding: utf-8 -*-
"""AUDITORIA fase 4 — réplica exata do §3.3, ferramentas posicionais, CSVs derivados,
integridade do notebook (imagens/ordem/erros)."""
import csv, json, lzma, re, sys, ast
from collections import Counter, defaultdict
from statistics import median

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
REPO = "/Users/rafaelventura/ICT-ITAU/memory_layer_ai_agents"
TRACE = f"{REPO}/85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz"

# 1) colunas via pandas (notebook diz 12)
import pandas as pd
hdr = pd.read_csv(TRACE, dtype=str, nrows=2)
print(f"1. pandas vê {hdr.shape[1]} colunas: {list(hdr.columns)}")

# 2) réplica EXATA da célula 19 (tokens só contam se o código parsear, no agregado por papel;
#    no nível de execução, tokens sempre contam e calls=0 se não parsear)
INV = set()
per_role = defaultdict(lambda: [0, 0])
per_exec = defaultdict(lambda: [0, 0])
pos_tools = Counter()
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
                code = st.get("code_action") or ""
                em = str((st.get("error") or {}).get("message") or "")
                mt = re.search(r"tool (\w+) does not support multiple positional", em)
                if mt: pos_tools[mt.group(1)] += 1
                try:
                    nc = sum(1 for n in ast.walk(ast.parse(code))
                             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in INV)
                except Exception:
                    per_exec[eid][0] += 0
                    per_exec[eid][1] += tt
                    continue
                per_role[role][0] += tt; per_role[role][1] += nc
                per_exec[eid][0] += nc; per_exec[eid][1] += tt
tt_ = sum(v[0] for v in per_role.values()); cc_ = sum(v[1] for v in per_role.values())
rats = [t/c for c, t in per_exec.values() if c > 0]
print(f"2. réplica-exata §3.3 → razão agregada: {tt_/cc_:,.0f} (notebook 21.420) · mediana/exec: {median(rats):,.0f} (notebook 12.192)")
print(f"   ferramentas distintas citadas em msgs 'positional': {len(pos_tools)} (relatório diz 12) → {sorted(pos_tools)}")

# 3) CSVs derivados
for nome in ["erros_classificados", "execucoes", "payoff_assinaturas", "reincidencia", "candidatos_memoria"]:
    p = f"{REPO}/analysis/2026-09-trace-law-flow/resultados/{nome}.csv"
    with open(p) as fh: n = sum(1 for _ in fh)
    print(f"3. resultados/{nome}.csv: {n-1} linhas de dados")

# 4) integridade do notebook: imagens embutidas por célula, ordem de execução, erros
nb = json.load(open(f"{REPO}/analysis/2026-09-trace-law-flow/pipeline/analise_trace_esteira_juridica.ipynb"))
execseq = []
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] != "code": continue
    kinds = []
    for o in c.get("outputs", []):
        t = o.get("output_type")
        if t in ("display_data", "execute_result"):
            kinds.append("/".join(o.get("data", {}).keys()))
        else: kinds.append(t)
    execseq.append((i, c.get("execution_count"), kinds))
print("4. células de código: idx, execution_count, tipos de output")
for i, ec, kinds in execseq:
    print(f"   cell {i:02d}  exec#{ec}  {kinds}")
