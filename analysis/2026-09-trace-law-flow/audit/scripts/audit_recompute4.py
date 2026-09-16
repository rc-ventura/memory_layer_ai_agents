# -*- coding: utf-8 -*-
"""AUDITORIA fase 4 — réplica exata do §3.3, ferramentas posicionais, CSVs derivados,
integridade do notebook (imagens/ordem/erros)."""
import csv, json, lzma, re, sys, ast
from collections import Counter, defaultdict
from statistics import median

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
import os
# Caminhos canônicos corrigidos 16/09/2026 (auditoria M1+M2): BASE é a pasta
# analysis/2026-09-trace-law-flow/ (2 níveis acima de audit/scripts/), não a raiz do repo —
# o REPO antigo (raiz) apontava pra analysis/2026-09-trace-law-flow/resultados/, a cópia
# obsoleta de 08/09 que a auditoria de 16/09 achou (M1) e que foi removida. Os CSVs derivados
# vivem em pipeline/resultados/, a única pasta que o notebook de fato escreve.
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data",
                      "85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz")

# 1) colunas via pandas (notebook diz 12)
import pandas as pd
hdr = pd.read_csv(TRACE, dtype=str, nrows=2)
print(f"1. pandas vê {hdr.shape[1]} colunas: {list(hdr.columns)}")

# 2) réplica EXATA da célula 19 (tokens só contam se o código parsear, no agregado por papel;
#    no nível de execução, tokens sempre contam e calls=0 se não parsear)
INV = set()
per_role = defaultdict(lambda: [0, 0])
per_role_excl = defaultdict(lambda: [0, 0])   # regra pré-15/09/2026: descarta o step que não parseia
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
                # REGRA OFICIAL desde 15/09/2026 (docs/01-racionais.md §3.3, Ressalva 2): o step entra sempre no
                # numerador — os tokens são custo real do papel — e contribui zero ao denominador quando o código
                # não parseia. Até 15/09 esta réplica seguia a célula antiga, que descartava o step do agregado
                # POR PAPEL mas mantinha os tokens dele no agregado POR EXECUÇÃO; era essa inconsistência que
                # fazia 21.420 e 12.192 baterem ao mesmo tempo. `per_role_excl` preserva a regra antiga para que
                # as duas fiquem impressas lado a lado, em vez de a divergência sumir do registro.
                try:
                    nc = sum(1 for n in ast.walk(ast.parse(code))
                             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in INV)
                    parseou = True
                except Exception:
                    nc, parseou = 0, False
                per_role[role][0] += tt; per_role[role][1] += nc
                per_exec[eid][0] += nc; per_exec[eid][1] += tt
                if parseou:
                    per_role_excl[role][0] += tt; per_role_excl[role][1] += nc
tt_ = sum(v[0] for v in per_role.values()); cc_ = sum(v[1] for v in per_role.values())
rats = [t/c for c, t in per_exec.values() if c > 0]
te_ = sum(v[0] for v in per_role_excl.values()); ce_ = sum(v[1] for v in per_role_excl.values())
print(f"2. réplica-exata §3.3 → razão agregada: {tt_/cc_:,.0f} (notebook 22.280) · mediana/exec: {median(rats):,.0f} (notebook 12.192)")
print(f"   regra antiga, pré-15/09 (descarta step sem parse) → razão agregada: {te_/ce_:,.0f} (era 21.420)")
print(f"   ferramentas distintas citadas em msgs 'positional': {len(pos_tools)} (relatório diz 12) → {sorted(pos_tools)}")

# 3) CSVs derivados — pipeline/resultados/, não a cópia obsoleta que existiu na raiz da análise
#    até 16/09/2026 (M1: 4 dos 5 arquivos em comum divergiam; erros_mecanismo.csv e
#    triagem_assinaturas.csv nem existiam lá — sinal de que estava desatualizada, não só duplicada)
for nome in ["erros_classificados", "execucoes", "payoff_assinaturas", "reincidencia", "candidatos_memoria"]:
    p = f"{BASE}/pipeline/resultados/{nome}.csv"
    with open(p) as fh: n = sum(1 for _ in fh)
    print(f"3. pipeline/resultados/{nome}.csv: {n-1} linhas de dados")

# 4) integridade do notebook: imagens embutidas por célula, ordem de execução, erros
nb = json.load(open(f"{BASE}/pipeline/analise_trace_esteira_juridica.ipynb"))
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
