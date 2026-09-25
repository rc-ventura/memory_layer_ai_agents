# -*- coding: utf-8 -*-
"""AUDITORIA INDEPENDENTE 2026-09-16 (fase 6) — nível MECANISMO / TRIAGEM / UNIDADES.

Audita o que a auditoria de 08/09 ainda não cobria (foi criado em 15/09):
  a) submecanismo() por erro — reimplementado DO ZERO a partir da especificação em
     prosa em docs/01-racionais.md §7 Passo 2 (não copiada do notebook), comparada
     erro a erro contra pipeline/resultados/erros_mecanismo.csv;
  b) a regra de cascata (erros consecutivos do mesmo papel na mesma execução)
     e o agregado 498 erros → 437 ocorrências;
  c) a tabela de unidades (14 linhas: ocorrências, erros, execuções, meses, papéis,
     tokens) vs. docs/02-relatorio-achados.md §6 e o CSV candidatos_memoria.csv;
  d) a cobertura 447/498 (90%) e 92% dos tokens;
  e) a tabela papel × mecanismo (§2.2 e §7 do racionais, Passo 5);
  f) as ressalvas documentadas: concentração de "Explicação solta" em dez/2025
     (26/33 erros, 92% tokens, 7 das 12 ocorrências logo após erro de protocolo,
     4 ocorrências próprias abr–jun), e a regra oficial dos steps não parseáveis
     no §3.3 (tokens/chamada por papel e agregada 22.280; mediana/exec 12.192);
  g) a quarta régua do achado central: 58 (13,5%) por mecanismo vs. 51 por mensagem.

Independência: csv.DictReader + json + ast puros; o submecanismo_spec abaixo foi
escrito a partir da PROSA do racional, não do código do notebook.
Saída não commitável: pode conter PII (audit_out*.txt é git-ignored).
"""
import csv, json, lzma, re, sys, ast, builtins, os
from collections import Counter, defaultdict

# mês da execução = dat_hor_inio_exeo (AAAAMM), não anomesdia — anomesdia é a data de corte do lote
# (ver 03-procedimento-validacao.md, 'três relógios'; troca feita em 23/09/2026)
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
# Caminhos canônicos corrigidos 16/09/2026 (auditoria M2): relativos a este script, não a um
# home de usuário fixo.
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRACE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data",
                      "85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz")
EM_CSV = f"{BASE}/pipeline/resultados/erros_mecanismo.csv"
CAND_CSV = f"{BASE}/pipeline/resultados/candidatos_memoria.csv"

# ---------------------------------------------------------------- spec (prosa)
PT_STOP = {"de","da","do","das","dos","a","o","as","os","e","é","que","para","com","não","nao",
           "em","no","na","nos","nas","um","uma","se","por","ao","aos","ou","mais","seu","sua",
           "pelo","pela","este","esta","isso","deve","vou","foi","como","sem","antes","apenas",
           "somente","nenhum","nenhuma"}
MODS = {"json","pd","np","re","os","math","datetime"}

def linha_rejeitada(m, code=""):
    mm = re.search(r"due to: \w+\s*\n(.*?)\n\s*Error:", m, re.S)
    if mm:
        return re.sub(r"\s*\^\s*$", "", mm.group(1).split("\n")[0]).strip()
    # formato novo ("... on line N due to: SyntaxError: <motivo>", sem o código): a linha N do code_action
    n = re.search(r"on line (\d+) due to: \w+", m)
    linhas = (code or "").splitlines()
    return linhas[int(n.group(1)) - 1].strip() if n and 0 < int(n.group(1)) <= len(linhas) else ""

def abre_string(l):
    # "abre uma string": final_answer("..., x = """..., chave de dict entre aspas, task=...
    return re.match(r"^(final_answer\s*\(|\w+\s*\+?=\s*\(?\s*[frbuFRBU]*(\"\"\"|'''|\"|')"
                    r"|[\"'][^\"']*[\"']\s*:|\w+\(\s*task\s*=)", l) is not None

def e_texto_pt(s):
    # markdown no início OU crase OU >=15% stopwords
    if re.match(r"^(\||#|\*\*|- |\d+[.)]\s)", s) or "`" in s: return True
    toks = re.findall(r"[A-Za-zÀ-ÿ]+", s.lower())
    return len(toks) >= 3 and sum(t in PT_STOP for t in toks)/len(toks) >= 0.15

def retorno_colado(l, m, code, obs_ant):
    # retorno de ferramenta impresso e colado inteiro: a linha tem >= 2 chaves distintas com valor texto
    # ("chave": "..."), >= 2 delas já apareceram como chave impressa numa observação anterior do papel, e a
    # instrução onde a linha está não é um final_answer( (lá é relatório em literal)
    chaves = {a for a in re.findall(r"[\"']([^\"'\n]{1,60})[\"']\s*:\s*[\"']", l)}
    if len(chaves) < 2: return False
    if sum(1 for a in chaves if re.search("[\"']" + re.escape(a) + "[\"']\\s*:", obs_ant)) < 2: return False
    n = re.search(r"on line (\d+)", m); linhas = (code or "").splitlines()
    if n and 0 < int(n.group(1)) <= len(linhas):
        j = int(n.group(1)) - 1
        while j > 0 and (not linhas[j].strip() or linhas[j][0] in " \t'\")]}"): j -= 1
        if linhas[j].lstrip().startswith("final_answer("): return False
    return True

def submecanismo_spec(m, code="", obs_ant=""):
    # Escrito a partir do §7 Passo 2 dos racionais (prosa), mesma ordem descrita lá.
    if "regex pattern" in m: return "harness_bloco_code"
    if "AgentGenerationError" in m or "internally hosted" in m or "Error code: 422" in m or "UnprocessableEntity" in m:
        return "infra_llm"
    if "Code parsing failed" in m or "SyntaxError" in m or "IndentationError" in m:
        l = linha_rejeitada(m, code)
        if re.search(r"truncad", l, re.I): return "repr_colado"
        if retorno_colado(l, m, code, obs_ant): return "repr_colado"
        if "unterminated" in m or "forgot a comma" in m or "never closed" in m or abre_string(l):
            return "texto_em_literal"
        if e_texto_pt(l): return "texto_solto_no_codigo"
        return "codigo_mal_escrito"
    if "does not support multiple positional" in m: return "argumento_posicional"
    if "Could not index" in m:
        if "string indices must be integers" in m: return "tipo_real_do_retorno"
        if re.search(r"KeyError: \d+\s*$", m) or "unhashable type: 'slice'" in m: return "dict_indexado_por_posicao"
        if "KeyError: '" in m or "are in the [columns]" in m: return "campo_inexistente_no_retorno"
        return "causa_sem_regra"
    if "Object hashDocumento has no attribute" in m: return "dict_iterado_como_lista"
    if ("JSON object must be str" in m or "JSONDecode" in m or "multiply sequence by non-int" in m
            or "could not convert string to float" in m or "has no attribute" in m):
        return "tipo_real_do_retorno"
    if "object is not an iterator" in m: return "next_sobre_gerador"
    v = re.search(r"variable `(\w+)` is not defined", m)
    if v and v.group(1) in MODS: return "modulo_sem_import"
    f = re.search(r"Forbidden function evaluation: '(\w+)'", m)
    if f and not hasattr(builtins, f.group(1)): return "nome_nao_definido"
    if f or "Import of" in m or "ModuleNotFound" in m or "Forbidden" in m: return "inventario_sandbox"
    if v: return "nome_nao_definido"
    return "causa_sem_regra"

SUB2UNI = {
    "dict_indexado_por_posicao":"U_contrato_dict", "dict_iterado_como_lista":"U_contrato_dict",
    "campo_inexistente_no_retorno":"U_campo_inexistente", "tipo_real_do_retorno":"U_tipo_retorno",
    "texto_em_literal":"U_texto_literal", "texto_solto_no_codigo":"U_texto_solto",
    "argumento_posicional":"U_arg_nomeado", "inventario_sandbox":"U_sandbox", "modulo_sem_import":"U_sandbox",
    "next_sobre_gerador":"U_next_gerador", "nome_de_step_que_falhou":"U_estado_perdido",
    "nome_nunca_definido":"U_nome_inventado", "repr_colado":"U_repr_colado",
    "infra_llm":"H_infra_llm", "harness_bloco_code":"H_bloco_code",
    "codigo_mal_escrito":"X_causa_nao_identificada", "causa_sem_regra":"X_causa_nao_identificada",
    "sintoma_nao_reconhecido":"X_sintoma_nao_reconhecido",
}
UNI_NOME = dict()
for row in csv.DictReader(open(EM_CSV, encoding="utf-8")):
    UNI_NOME[row["unidade"]] = row["unidade_nome"]

# ------------------------------------------------- passe 1: trace cru → erros
errors = []   # dict(eid, role, idx, em, mes, tok, ctx_next quer computar separado)
INV = set()
per_role_tok = Counter(); per_role_calls = Counter()
per_exec_calls = Counter(); per_exec_tok = Counter()
exec_month = {}
traj = defaultdict(list)

with lzma.open(TRACE, 'rt', encoding='utf-8') as f:
    rdr = csv.DictReader(f)
    for r in rdr:
        memo_raw = r.get("txt_etap_memo")
        if not memo_raw: continue
        try: memo = json.loads(memo_raw)
        except Exception: continue
        eid = r["cod_idef_exeo"]; mes = r["dat_hor_inio_exeo"][:7].replace("-", "")
        exec_month[eid] = mes
        for role, stps in memo.items():
            if not isinstance(stps, list): continue
            acts = [s for s in stps if isinstance(s, dict) and s.get("__class__")=="ActionStep"]
            obs_ant = ""
            for i, st in enumerate(acts):
                tu = st.get("token_usage") or {}
                tt = tu.get("total_tokens") or 0
                code = st.get("code_action") or ""
                # §3.3 regra oficial: tokens sempre no numerador; 0 chamadas se não parseia
                mim = st.get("model_input_messages")
                sysp = ""
                if mim:
                    m0 = mim[0] if isinstance(mim[0], dict) else {}
                    c = m0.get("content")
                    sysp = c[0].get("text","") if isinstance(c, list) and c and isinstance(c[0], dict) else str(c or "")
                for nome in re.findall(r"def\s+(\w+)\s*\(", sysp): INV.add(nome)
                nomes = None  # computed lazily below needs full INV — so do calls in passe 2
                traj[(eid,role)].append(dict(i=i, err=bool(st.get("error")), em=str((st.get("error") or {}).get("message") or ""),
                                             mes=mes, tok=tt, code=code, sysp=sysp))
                e = st.get("error")
                if e:
                    errors.append(dict(eid=eid, role=role, idx=i, em=str(e.get("message") or ""), mes=mes, tok=tt,
                                       code=code, obs_ant=obs_ant))
                obs_ant += str(st.get("observations") or "")

# --------------------------------------------- comparação erro-a-erro com o CSV
csv_rows = list(csv.DictReader(open(EM_CSV, encoding="utf-8")))
def classify_sig_local(m):
    if 'Could not index' in m: return 'ret_dict'
    if 'does not support multiple positional' in m: return 'arg_pos'
    if 'unterminated' in m: return 'unterm'
    if 'regex pattern' in m: return 'sem_bloco'
    if 'IndentationError' in m: return 'indent'
    if 'leading zeros' in m: return 'data'
    if 'forgot a comma' in m or 'never closed' in m or 'invalid decimal' in m: return 'colado'
    if 'SyntaxError' in m: return 'sintaxe'
    if 'is not defined' in m:
        v = re.search(r'variable `(\w+)`', m)
        if v and v.group(1) in MODS: return 'sem_import'
        return 'var_nao_def'
    if 'has no attribute' in m: return 'sem_atributo'
    if 'not allowed' in m or 'explicitly allowed' in m or 'is not permitted' in m: return 'bloqueado'
    if 'ModuleNotFound' in m: return 'mod_ausente'
    if 'Forbidden' in m: return 'proibido'
    if 'AgentGenerationError' in m or 'internally hosted' in m: return 'falha_llm'
    if 'Error code: 422' in m or 'UnprocessableEntity' in m: return 'http422'
    if 'JSONDecode' in m: return 'nao_json'
    if 'KeyError' in m: return 'campo_ausente'
    if 'TypeError' in m: return 'tipo'
    if 'ValueError' in m: return 'valor'
    if 'IndexError' in m: return 'ret_vazio'
    return 'NC'

csv_map = {(r["exec_id"], r["role"], int(r["idx"])): r for r in csv_rows}
mine_map = {}
diffs = []
for e in errors:
    sub = submecanismo_spec(e["em"], e["code"], e["obs_ant"])
    # split nome_nao_definido por seguidor (precisa do step anterior — do traj)
    if sub == "nome_nao_definido":
        seq = traj[(e["eid"], e["role"])]
        prev = next((s for s in seq if s["i"] == e["idx"]-1), None)
        if prev is not None and prev["err"]:
            sub = "nome_de_step_que_falhou"
        else:
            sub = "nome_nunca_definido"
    # causa sem regra + sintoma que a classificação local também não reconhece = erro desconhecido (01 §7)
    if sub == "causa_sem_regra" and classify_sig_local(e["em"]) == "NC":
        sub = "sintoma_nao_reconhecido"
    uni = SUB2UNI[sub]
    mine_map[(e["eid"], e["role"], e["idx"])] = (sub, uni)
    cr = csv_map.get((e["eid"], e["role"], e["idx"]))
    if cr is None:
        diffs.append((e["eid"], e["role"], e["idx"], "FALTA no CSV", sub))
    elif cr["submecanismo"] != sub or cr["unidade"] != uni:
        diffs.append((e["eid"], e["role"], e["idx"], f"csv={cr['submecanismo']}/{cr['unidade']}",
                      f"spec={sub}/{uni}"))

print(f"A. erros no trace: {len(errors)} · linhas no erros_mecanismo.csv: {len(csv_rows)} · chaves em comum: {len(set(mine_map) & set(csv_map))}")
print(f"   divergências submecanismo/unidade (spec prosa vs. CSV): {len(diffs)}")
for d in diffs[:20]: print("   ", d)

# ---------------------------------------------------- cascata / ocorrência
rows = []
for e in errors:
    sub, uni = mine_map[(e["eid"], e["role"], e["idx"])]
    seq = traj[(e["eid"], e["role"])]
    prev = next((s for s in seq if s["i"] == e["idx"]-1), None)
    seguidor = bool(prev and prev["err"])
    rows.append(dict(**e, sub=sub, uni=uni, seguidor=seguidor))

# cascata id: cresce a cada erro NÃO-seguidor dentro de (eid,role)
casc = {}
cid = 0
by_key = defaultdict(list)
for row in rows: by_key[(row["eid"],row["role"])].append(row)
for k2, rr in by_key.items():
    for row in sorted(rr, key=lambda x: x["idx"]):
        if not row["seguidor"]: cid += 1
        casc[id(row)] = cid
        row["cascata"] = cid
        row["ocorrencia"] = f'{cid}|{row["uni"]}'
n_oc = len({r["ocorrencia"] for r in rows})
print(f"B. cascatas={len({r['cascata'] for r in rows})} · ocorrências (cascata×unidade)={n_oc} (esp. 437) · seguidores={sum(1 for r in rows if r['seguidor'])}")

# ------------------------------------------ agregado por unidade vs. relatório/CSV
agg = defaultdict(lambda: dict(oc=set(), err=0, ex=set(), me=set(), pa=set(), tok=0))
for r in rows:
    a = agg[r["uni"]]
    a["oc"].add(r["ocorrencia"]); a["err"] += 1; a["ex"].add(r["eid"]); a["me"].add(r["mes"]); a["pa"].add(r["role"]); a["tok"] += r["tok"]
cand_csv = {row["unidade"]: row for row in csv.DictReader(open(CAND_CSV, encoding="utf-8"))}
print("C. unidade: minhas contagens vs. candidatos_memoria.csv (ocorr/erros/execs/meses/papéis/tokens)")
tot_cand_err = 0; tot_cand_tok = 0; tot_tok_err = sum(r["tok"] for r in rows)
for u in sorted(agg, key=lambda x: -agg[x]["tok"]):
    a = agg[u]; c = cand_csv.get(u, {})
    mine = (len(a["oc"]), a["err"], len(a["ex"]), len(a["me"]), len(a["pa"]), a["tok"])
    csvv = (int(c.get("ocorrências",-1)), int(c.get("erros",-1)), int(c.get("execuções",-1)),
            int(c.get("meses",-1)), int(c.get("papéis",-1)), int(c.get("tokens",-1)))
    ok = "OK" if mine == csvv else f"<< DIVERGE csv={csvv}"
    if c.get("decisão") == "candidato": tot_cand_err += a["err"]; tot_cand_tok += a["tok"]
    print(f"   {u:22s} {UNI_NOME.get(u,'')[:44]:46s} oc={mine[0]:3d} err={mine[1]:3d} ex={mine[2]:3d} me={mine[3]} pa={mine[4]} tok={mine[5]:>9,} {ok}")
print(f"   cobertura candidatas: {tot_cand_err}/498 = {tot_cand_err/498:.1%} (esp. 447/89,8%) · tokens {tot_cand_tok/tot_tok_err:.1%} (esp. 92%)")

# ------------------------------------------------------ tabela papel × mecanismo
print("D. papel × unidade (% dos erros DO papel, papéis com ≥5 erros):")
role_tot = Counter(r["role"] for r in rows)
role_uni = defaultdict(Counter)
for r in rows: role_uni[r["role"]][UNI_NOME[r["uni"]]] += 1
for role in ["CadastroTrabalhista","CalculoCivel","managerAgent","ConversationAgent","RespostaBacen"]:
    c = role_uni[role]; t = sum(c.values())
    top = ", ".join(f"{n}={v} ({v/t:.0%})" for n,v in c.most_common(3))
    print(f"   {role:20s} n={t}: {top}")

# ---------------- ressalva "Explicação solta" (dez/2025, após protocolo, abr–jun)
ru = [r for r in rows if r["uni"]=="U_texto_solto"]
dz = [r for r in ru if r["mes"]=="202512"]
tok_dz = sum(r["tok"] for r in dz); tok_ru = sum(r["tok"] for r in ru)
oc_ru = sorted({(r["cascata"], r["eid"], r["role"], r["mes"]) for r in ru})
# ocorrência "logo após protocolo": a cascata começa imediatamente depois de erro H_bloco_code
oc_after = 0
seen_oc = set()
for r in sorted(ru, key=lambda x: (x["eid"], x["role"], x["idx"])):
    key = (r["cascata"], r["eid"], r["role"])
    if key in seen_oc: continue
    seen_oc.add(key)
    seq = traj[(r["eid"], r["role"])]
    prev = next((s for s in seq if s["i"] == r["idx"]-1), None)
    if prev and prev["err"] and submecanismo_spec(prev["em"])=="harness_bloco_code":
        oc_after += 1
oc_meses = defaultdict(set)
for r in ru:
    for rr in ru:
        if rr["ocorrencia"]==r["ocorrencia"]:
            oc_meses[r["ocorrencia"]].add(rr["mes"])
own = sum(1 for oc, mm in oc_meses.items() if mm and not ("2025-12" in mm and len(mm)==1))
# ^ "ocorrências próprias fora de dez"?
own_mes = defaultdict(list)
for oc, mm in oc_meses.items(): own_mes[len(mm)].append(oc)
print(f"E. 'Explicação solta': {len(dz)}/{len(ru)} erros em dez/2025 ({tok_dz/tok_ru:.0%} dos tokens) (esp. 26/33, 92%)")
print(f"   ocorrências={len(seen_oc)} (esp. 12) · logo após erros de protocolo: {oc_after} (esp. 7)")
mesq = Counter()
seen=set()
for r in sorted(ru, key=lambda x:(x["eid"],x["role"],x["idx"])):
    key=(r["cascata"],r["eid"],r["role"])
    if key in seen: continue
    seen.add(key); mesq[r["mes"]] += 1
print(f"   ocorrências por mês: {dict(sorted(mesq.items()))} (esp. abr–jun somando 4 próprias)")

# ---------------------------------------------- §3.3 tokens/chamada (regra oficial)
import statistics as stt
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
                if not isinstance(st, dict) or st.get("__class__")!="ActionStep": continue
                tt = (st.get("token_usage") or {}).get("total_tokens") or 0
                code = st.get("code_action") or ""
                per_role_tok[role] += tt
                per_exec_tok[eid] += tt
                try:
                    tree = ast.parse(code)
                    nc = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call)
                             and isinstance(n.func, ast.Name) and n.func.id in INV)
                except Exception:
                    nc = 0
                per_role_calls[role] += nc
                per_exec_calls[eid] += nc
tt_ = sum(per_role_tok.values()); cc_ = sum(per_role_calls.values())
rats = [per_exec_tok[e]/per_exec_calls[e] for e in per_exec_tok if per_exec_calls.get(e,0)>0]
print("F. tokens/chamada (regra oficial inclusiva):")
for role in ["CalculoCivel","CalculoTrabalhista","ConversationAgent","managerAgent"]:
    t,c = per_role_tok[role], per_role_calls[role]
    print(f"   {role:20s} {t/c:10,.0f} (esp. {dict(CalculoCivel=141673, CalculoTrabalhista=50624, ConversationAgent=27988, managerAgent=18775)[role]:,})")
print(f"   agregada={tt_/cc_:,.0f} (esp. 22.280) · mediana/exec={stt.median(rats):,.0f} (esp. 12.192)")
print(f"   ferramentas declaradas (união): {len(INV)} (esp. 90)")

# -------------------------------------- quarta régua: reincidência por mecanismo
# Precisa do model_input_messages do step seguinte — passe dedicado, mantendo só
# (eid, role, idx, err, em, uni, ctx_next).
checked=reached=repeated=same_mec_r=0
same_sig_r=0
traj2 = defaultdict(list)
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
            acts = [s for s in stps if isinstance(s, dict) and s.get("__class__")=="ActionStep"]
            for i, st in enumerate(acts):
                em = str((st.get("error") or {}).get("message") or "")
                mim = st.get("model_input_messages")
                ctx = json.dumps(mim, ensure_ascii=False) if mim else ""
                traj2[(eid,role)].append((i, bool(st.get("error")), em, ctx))
for (eid,role),seq0 in traj2.items():
    seq = sorted(seq0)
    for j in range(len(seq)-1):
        i0,e0,em0,_ = seq[j]; i1,e1,em1,ctx1 = seq[j+1]
        if not e0: continue
        checked += 1
        core = re.sub(r"\s+"," ", em0)[:45]
        if core and core in re.sub(r"\s+"," ", ctx1):
            reached += 1
            if e1:
                repeated += 1
                if classify_sig_local(em0) == classify_sig_local(em1): same_sig_r += 1
                u0 = SUB2UNI.get(submecanismo_spec(em0))
                # seguidor relevante p/ split do nome_nao_definido
                if submecanismo_spec(em0) == "nome_nao_definido":
                    prev = None
                    for s in seq:
                        if s[0] == i0-1: prev = s
                    if prev and prev[1]: u0 = "U_estado_perdido"
                u1 = SUB2UNI.get(submecanismo_spec(em1))
                if submecanismo_spec(em1) in ("nome_nao_definido",):
                    prev = None
                    for s in seq:
                        if s[0] == i1-1: prev = s
                    if prev and prev[1]: u1 = "U_estado_perdido"
                if u0 == u1: same_mec_r += 1
print(f"G. régua mecanismo: checked={checked} · reached={reached} ({reached/checked:.1%}) · repetiram={repeated} ({repeated/reached:.1%}) · mesma msg={same_sig_r} ({same_sig_r/reached:.1%}) (esp. 51/11,9%) · mesmo mecanismo={same_mec_r} ({same_mec_r/reached:.1%}) (esp. 58/13,5%)")
