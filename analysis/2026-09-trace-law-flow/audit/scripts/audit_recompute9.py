# -*- coding: utf-8 -*-
"""AUDITORIA INDEPENDENTE 2026-10-02 (fase 9) — o BALDE INVISÍVEL (falhas silenciosas de ferramenta).

Por que existe: a auditoria de 02/10 (PR #29) conferiu os números do balde invisível REEXECUTANDO as mesmas funções
do notebook (`falhas_silenciosas`, `motivo_da_falha`, [2]–[4], `forma_argumento`) — isso prova reprodutibilidade, não
correção. Este script reimplementa as medidas a partir da PROSA de docs/13-racionais-falhas-silenciosas.md (§2–§5) e
do Ajuste 11 (pipeline-entre-bases.md), com csv + lzma + json + re puros: sem pandas, sem importar base_pipeline.
A única coisa lida do código é a TABELA `MOTIVO_REGRAS` (é a especificação dos grupos, não a lógica), por `ast`, do
fonte do base_pipeline.py — a aplicação (normalização, ordem, 1ª que casa) é reimplementada aqui.

Confere, contra os números publicados (docs/14-relatorio-falhas-silenciosas.md):
  A) o funil: falhas com exceção × silenciosas, por par step×ferramenta e por step; execuções, meses, papéis,
     ferramentas; silenciosas ∩ erros_mecanismo.csv (a tabela do balde VISÍVEL) = 0 — cruzamento entre tabelas;
  B) os grupos do motivo e as falhas reais; disparos por regra × a anotação de base (b1/b2) de cada regra;
  C) [2] o 1º erro com exceção do mesmo papel em até 3 steps; [3] contrato de retorno precedido;
  D) [4] candidato a sucesso falso, com a regra do Ajuste 11 (final no próprio step ou depois, na mesma chamada);
     e as sondas que motivaram o ajuste (pela regra antiga);
  E) a forma do 1º argumento do busca_obf nas falhas json_invalido (gesto colado do repr_colado);
  F) sondas para a consolidação (plano 4.2b) e de robustez: json_invalido em sequência, execuções em comum com o
     U_repr_colado visível, falha sem a ferramenta chamada no step (eco), papel "null", linhas duplicadas;
  G) a consolidação (Ajuste 12, 04/10): a U_repr_colado nos dois canais — visível pelas cascatas do
     erros_mecanismo.csv, silencioso pela regra do doc 13 §5 (JSON inválido, qualquer ferramenta, argumento colado de um
     retorno impresso), ocorrência = cascata × unidade nos dois; recorrência contada sobre a união.

Uso (de dentro de audit/scripts/ ou de qualquer lugar):
    python audit_recompute9.py                       # base 1, caminhos do repo
    python audit_recompute9.py --base base2 --trace <arquivo .csv, .csv.xz ou .parquet> --em <erros_mecanismo.csv> --fonte <base_pipeline.py>
Saída: só contagens, nomes de papel e de ferramenta — nenhum exec_id, nenhum texto de caso. Pode ser fotografada na
máquina 2. Gravar em audit/scripts/audit_out9.txt (git-ignored).
"""
import argparse, ast, csv, gzip, json, lzma, os, re, sys, unicodedata
from collections import Counter, defaultdict

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
try: sys.stdout.reconfigure(encoding="utf-8")   # terminal do Windows (máquina 2): sem isso, "×"/"∩" derrubam o print
except Exception: pass


# O trace da base 1 é .csv.xz; o da base 2 é .csv puro; o da base 3, parquet. O leitor decide pelo conteúdo (bytes
# mágicos), não pela extensão — só a abertura do arquivo vem de fora (plano §4.10).
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from leitor_trace import abrir_trace
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))          # analysis/2026-09-trace-law-flow
ap = argparse.ArgumentParser()
ap.add_argument("--base", default="base1", choices=["base1", "base2"])
ap.add_argument("--trace", default=os.path.join(RAIZ, "data", "85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz"))
ap.add_argument("--em", default=os.path.join(RAIZ, "pipeline", "resultados", "erros_mecanismo.csv"))
ap.add_argument("--fonte", default=os.path.join(RAIZ, "pipeline", "base_pipeline.py"))
args = ap.parse_args()

# ------------------------------------------------------------------ o publicado (doc 14), por base
# None = não publicado para a base (só o notebook dá lá) → imprime "a conferir", não conta como divergência.
ESPERADO = {
    "base1": dict(excecao=9, silenciosas=120, steps_sil=119, execs=90, meses=10, papeis=13, ferramentas=22,
                  pares=3573, steps_ferr=3373,
                  grupos=dict(sem_resultado=43, fora_da_cobertura=2, argumento_do_agente=41, plataforma=19,
                              json_invalido=6, nao_reconhecido=9), reais=75,
                  depois={"(nenhum erro)": 107, "U_tipo_retorno": 4, "H_bloco_code": 2, "U_campo_inexistente": 0,
                          "outros": 7},
                  contrato={"U_tipo_retorno": (47, 4), "U_contrato_dict": (96, 1), "U_campo_inexistente": (10, 0)},
                  # [4] depois do Ajuste 11 (02/10): 53 → 54 (nao_reconhecido 7 → 8)
                  sucesso={"argumento_do_agente": (30, 41), "plataforma": (16, 19), "json_invalido": (0, 6),
                           "nao_reconhecido": (8, 9)}, sucesso_total=(54, 75),
                  forma_colado=(6, 6),
                  # consolidação (Ajuste 12): visível 6 + silencioso 6, sem execução em comum
                  consolidado=dict(ocorrencias=12, execucoes=12, meses=4, papeis=2)),
    # pares/steps_ferr: o cabeçalho do `drill_down.py silenciosas` na máquina 2 (foto de 02/10)
    # steps_sil, papeis e o [4] novo: a 1ª rodada deste script na máquina 2 (02/10), agora publicados no doc 14
    "base2": dict(excecao=20, silenciosas=134, steps_sil=134, execs=124, meses=7, papeis=10, ferramentas=18,
                  pares=8232, steps_ferr=2771,
                  grupos=dict(sem_resultado=8, fora_da_cobertura=10, argumento_do_agente=6, plataforma=22,
                              json_invalido=86, nao_reconhecido=2), reais=116,
                  depois={"(nenhum erro)": 122, "U_tipo_retorno": 3, "H_bloco_code": 3, "U_campo_inexistente": 3,
                          "outros": 3},
                  contrato={"U_tipo_retorno": (79, 5), "U_contrato_dict": (0, 0), "U_campo_inexistente": (38, 3)},
                  # [4] depois do Ajuste 11 (02/10): 20 → 24 (plataforma 16 → 17, json_invalido 0 → 3)
                  sucesso={"argumento_do_agente": (2, 6), "plataforma": (17, 22), "json_invalido": (3, 86),
                           "nao_reconhecido": (2, 2)}, sucesso_total=(24, 116), sucesso_antes=(20, 116),
                  forma_colado=(86, 86),
                  # consolidação (Ajuste 12): visível 18 (triagem da máquina 2, 02/10) + silencioso 86, 0 em comum;
                  # meses 4 (o silencioso tem mai/2026, o visível começa em jun) e papéis 1 — rodada 2 (05/10)
                  consolidado=dict(ocorrencias=104, execucoes=104, meses=4, papeis=1)),
}[args.base]
DIVERG = []


def confere(rotulo, meu, esp):
    if esp is None:
        print(f"   {rotulo}: {meu} (a conferir — não publicado para {args.base})")
    elif meu == esp:
        print(f"   {rotulo}: {meu} OK")
    else:
        print(f"   {rotulo}: {meu} << DIVERGE (publicado {esp})"); DIVERG.append(rotulo)


# ------------------------------------------------------------------ a tabela de regras (spec), lida por ast
arv = ast.parse(open(args.fonte, encoding="utf-8").read())
REGRAS = next(ast.literal_eval(n.value) for n in arv.body if isinstance(n, ast.Assign)
              and any(getattr(t, "id", "") == "MOTIVO_REGRAS" for t in n.targets))
REAIS = {"argumento_do_agente", "plataforma", "json_invalido", "nao_reconhecido"}   # doc 13 §3, "é falha real?"
CONTRATO = ["U_tipo_retorno", "U_contrato_dict", "U_campo_inexistente"]              # doc 13 §4 [3]
disparos = Counter()


def grupo_do_motivo(motivo):
    # doc 13 §3: palavras-chave na ordem, a 1ª que casa decide; sem acento, minúsculo; senão nao_reconhecido
    t = unicodedata.normalize("NFKD", motivo).encode("ascii", "ignore").decode().lower().strip()
    for k, (g, padrao, _) in enumerate(REGRAS):
        if re.search(padrao, t):
            disparos[k] += 1
            return g
    return "nao_reconhecido"


def prompt_de_sistema(st):
    mim = st.get("model_input_messages") or []
    if not mim or not isinstance(mim[0], dict): return ""
    c = mim[0].get("content")
    return c[0].get("text", "") if isinstance(c, list) and c and isinstance(c[0], dict) else str(c or "")


# ------------------------------------------------------------------ leitura do cru
ERRO_FERR = re.compile(r"Error calling tool '(\w+)'")
pares = []          # um por (step, ferramenta) chamada ou que falhou
passos = {}         # (eid, role) -> lista de dicts por ActionStep (i, chamada, final, err, code, obs)
linhas_trace, eids_vistos, dup = 0, set(), 0
papel_null = 0
with abrir_trace(args.trace) as fh:
    for r in fh:
        linhas_trace += 1
        eid = r["cod_idef_exeo"]
        if not r.get("txt_etap_memo"): continue
        if eid in eids_vistos: dup += 1; continue        # uma execução conta uma vez
        eids_vistos.add(eid)
        try: memo = json.loads(r["txt_etap_memo"])
        except Exception: continue
        mes = r["dat_hor_inio_exeo"][:7]
        if "null" in memo: papel_null += 1
        for role, lst in memo.items():
            if not isinstance(lst, list): continue
            seq, chamada = [], 0
            for st in lst:
                if not isinstance(st, dict): continue
                if st.get("__class__") == "TaskStep": chamada += 1; continue
                if st.get("__class__") != "ActionStep": continue
                i = len(seq)
                err = st.get("error") or {}
                code = str(st.get("code_action") or "")
                obs = str(st.get("observations") or "")
                texto = obs + " " + str(st.get("action_output") or "") + " " + str(err.get("message") or "")
                declaradas = set(re.findall(r"def\s+(\w+)\s*\(", prompt_de_sistema(st))) - {"final_answer"}
                chamadas = {t for t in declaradas if re.search(rf"\b{t}\s*\(", code)}
                falhou = set(ERRO_FERR.findall(texto))
                seq.append(dict(i=i, chamada=chamada, final=bool(st.get("is_final_answer")), err=bool(err),
                                code=code, obs=obs))
                for t in chamadas | falhou:
                    motivo = ""
                    if t in falhou:
                        m = re.search(r"Error calling tool '" + re.escape(t) + r"':?\s*([^\n]*)", texto)
                        motivo = m.group(1) if m else ""
                    pares.append(dict(eid=eid, role=role, i=i, chamada=chamada, mes=mes, ferr=t, chamou=t in chamadas,
                                      canal=(("excecao" if err else "silenciosa") if t in falhou else None),
                                      motivo=motivo, grupo=grupo_do_motivo(motivo) if t in falhou else None))
            passos[(eid, role)] = seq

sil = [p for p in pares if p["canal"] == "silenciosa"]
exc = [p for p in pares if p["canal"] == "excecao"]
print(f"[{args.base}] linhas do trace: {linhas_trace} · execuções com memória: {len(eids_vistos)} · "
      f"linhas repetidas de execução (ignoradas): {dup}")

# ------------------------------------------------------------------ A. funil
print("A. funil (doc 13 §2):")
confere("pares step×ferramenta (chamada ou falha)", len(pares), ESPERADO["pares"])
confere("steps com ferramenta", len({(p["eid"], p["role"], p["i"]) for p in pares}), ESPERADO["steps_ferr"])
confere("falhas com exceção", len(exc), ESPERADO["excecao"])
confere("falhas silenciosas", len(sil), ESPERADO["silenciosas"])
confere("steps com falha silenciosa", len({(p["eid"], p["role"], p["i"]) for p in sil}), ESPERADO["steps_sil"])
confere("execuções", len({p["eid"] for p in sil}), ESPERADO["execs"])
confere("meses", len({p["mes"] for p in sil}), ESPERADO["meses"])
confere("papéis", len({p["role"] for p in sil}), ESPERADO["papeis"])
confere("ferramentas", len({p["ferr"] for p in sil}), ESPERADO["ferramentas"])
print(f"   % silenciosas entre as falhas de ferramenta: {len(sil) / max(1, len(sil) + len(exc)):.0%}")
EM = list(csv.DictReader(open(args.em, encoding="utf-8")))
chave_visivel = {(e["exec_id"], e["role"], int(e["idx"])) for e in EM}
confere("silenciosas no balde visível (erros_mecanismo.csv)",
        sum((p["eid"], p["role"], p["i"]) in chave_visivel for p in sil), 0)

# ------------------------------------------------------------------ B. grupos
print("B. grupos do motivo (doc 13 §3):")
g = Counter(p["grupo"] for p in sil)
for grp, n_esp in ESPERADO["grupos"].items():
    confere(f"{grp:<20}", g.get(grp, 0), n_esp)
confere("falhas reais", sum(g[x] for x in REAIS), ESPERADO["reais"])
confere("soma dos grupos = silenciosas", sum(g.values()), len(sil))
print("   disparos por regra (todas as falhas, com e sem exceção) × anotação de base:")
for k, (grp, padrao, origem) in enumerate(REGRAS):
    n = disparos.get(k, 0)
    nota = ""
    if n and args.base == "base1" and "b1" not in origem.split(): nota = "  ← regra anotada só b2 dispara na base 1"
    if n and args.base == "base2" and "b2" not in origem.split(): nota = "  ← regra anotada só b1 dispara na base 2"
    if not n and args.base.replace("base", "b") in origem.split(): nota = f"  ← anotada {origem}, não dispara aqui"
    print(f"     {k:2d} {grp:<20} {origem:<6} {n:4d}  {padrao[:48]}{nota}")

# ------------------------------------------------------------------ C. [2] e [3]
print("C. [2] o que vem depois · [3] contrato precedido (doc 13 §4, janela 3):")
erros_do_papel = defaultdict(list)
for e in EM: erros_do_papel[(e["exec_id"], e["role"])].append((int(e["idx"]), e["unidade"]))
for v in erros_do_papel.values(): v.sort()
depois = Counter()
for p in sil:
    prox = next((u for j, u in erros_do_papel.get((p["eid"], p["role"]), []) if p["i"] < j <= p["i"] + 3), None)
    depois[prox or "(nenhum erro)"] += 1
listados = [k for k in ESPERADO["depois"] if k != "outros"]
for k in listados:
    confere(f"[2] {k:<22}", depois.get(k, 0), ESPERADO["depois"][k])
confere("[2] outros", sum(n for k, n in depois.items() if k not in listados), ESPERADO["depois"]["outros"])
sil_por_papel = defaultdict(list)
for p in sil: sil_por_papel[(p["eid"], p["role"])].append(p["i"])
for u in CONTRATO:
    E = [e for e in EM if e["unidade"] == u]
    prec = sum(1 for e in E if any(int(e["idx"]) - 3 <= i < int(e["idx"])
                                   for i in sil_por_papel.get((e["exec_id"], e["role"]), [])))
    confere(f"[3] {u:<22} (erros, precedidos)", (len(E), prec), ESPERADO["contrato"][u])

# ------------------------------------------------------------------ D. [4] sucesso falso candidato
print("D. [4] candidato a sucesso falso (doc 13 §4 + Ajuste 11):")
ok_chamada = defaultdict(list)   # (eid, role, ferr) -> idx de chamadas sem falha
for p in pares:
    if p["chamou"] and p["canal"] is None: ok_chamada[(p["eid"], p["role"], p["ferr"])].append(p["i"])


def final_novo(p):
    # o 1º final_answer a partir do próprio step, na mesma chamada do papel
    return next((s["i"] for s in passos[(p["eid"], p["role"])] if s["final"] and s["i"] >= p["i"]
                 and s["chamada"] == p["chamada"]), None)


def final_antigo(p):
    # a regra de antes do Ajuste 11: o 1º final estritamente depois, em qualquer chamada
    return next((s["i"] for s in passos[(p["eid"], p["role"])] if s["final"] and s["i"] > p["i"]), None)


def candidato(p, f):
    return f is not None and not any(p["i"] < j <= f for j in ok_chamada[(p["eid"], p["role"], p["ferr"])])


reais = [p for p in sil if p["grupo"] in REAIS]
cand = Counter(p["grupo"] for p in reais if candidato(p, final_novo(p)))
tot = Counter(p["grupo"] for p in reais)
if ESPERADO["sucesso"] is not None:
    for grp, esp in ESPERADO["sucesso"].items():
        confere(f"[4] {grp:<20}", (cand.get(grp, 0), tot.get(grp, 0)), esp)
    confere("[4] total", (sum(cand.values()), len(reais)), ESPERADO["sucesso_total"])
else:
    for grp in sorted(tot):
        print(f"   [4] {grp:<20}: {cand.get(grp, 0)}/{tot[grp]} (número novo, depois do Ajuste 11)")
    print(f"   [4] total: {sum(cand.values())}/{len(reais)} (publicado antes do Ajuste 11: "
          f"{ESPERADO['sucesso_antes'][0]}/{ESPERADO['sucesso_antes'][1]})")
cand_ant = Counter(p["grupo"] for p in reais if candidato(p, final_antigo(p)))
no_final = sum(1 for p in reais if any(s["final"] for s in passos[(p["eid"], p["role"])] if s["i"] == p["i"]))
atravessa = sum(1 for p in reais if final_antigo(p) is not None and
                next(s for s in passos[(p["eid"], p["role"])] if s["i"] == final_antigo(p))["chamada"] != p["chamada"])
print(f"   pela regra antiga: {sum(cand_ant.values())}/{len(reais)} {dict(sorted(cand_ant.items()))}")
print(f"   sondas: falha real no próprio step do final_answer = {no_final} · final antigo em outra chamada = "
      f"{atravessa} · falha real sem final na chamada = {sum(1 for p in reais if final_novo(p) is None)}")

# ------------------------------------------------------------------ E. forma do busca_obf
print("E. busca_obf, json_invalido — forma do 1º argumento (doc 13 §5):")


def primeiro_argumento(code, ferr):
    m = re.search(rf"\b{ferr}\s*\(", code)
    if not m: return None
    k, prof, ini = m.end(), 1, m.end()
    while k < len(code) and prof:        # até o fecha-parêntese do mesmo nível (aspas não são tratadas: só a forma)
        prof += {"(": 1, ")": -1}.get(code[k], 0); k += 1
    a = code[ini:k - 1].strip()
    return re.sub(r"^\w+\s*=(?!=)\s*", "", a)


def colado(lit, obs_ant):
    chaves = set(re.findall(r"[\"']([^\"'\n]{1,60})[\"']\s*:\s*[\"']", lit))
    vistas = [c for c in chaves if re.search(r"[\"']" + re.escape(c) + r"[\"']\s*:", obs_ant)]
    return len(chaves) >= 2 and len(vistas) >= 2


formas = Counter()
ji = [p for p in sil if p["grupo"] == "json_invalido" and p["ferr"] == "busca_obf"]
for p in ji:
    seq = passos[(p["eid"], p["role"])]
    a = primeiro_argumento(seq[p["i"]]["code"], "busca_obf")
    obs_ant = "".join(s["obs"] for s in seq[:p["i"]])
    if a is None: formas["sem chamada visível"] += 1
    elif a.startswith("json.dumps"): formas["json.dumps"] += 1
    elif a.startswith("str(") and a[4:].lstrip()[:1] in "{[":
        formas["str(literal colado)" if colado(a, obs_ant) else "str(literal montado)"] += 1
    elif a[:1] in "{[": formas["literal colado" if colado(a, obs_ant) else "literal montado"] += 1
    elif re.match(r"[fFrR]?[\"']", a): formas["string colada" if colado(a, obs_ant) else "string montada"] += 1
    else: formas["variável/outro"] += 1
print(f"   {dict(formas)}")
n_col = sum(n for f, n in formas.items() if "colad" in f)
confere("gesto colado / falhas json_invalido do busca_obf", (n_col, len(ji)), ESPERADO["forma_colado"])

# ------------------------------------------------------------------ F. sondas para a 4.2b e de robustez
print("F. sondas (consolidação 4.2b e robustez):")
jall = sorted((p["eid"], p["role"], p["i"]) for p in sil if p["grupo"] == "json_invalido")
seqs = sum(1 for k, x in enumerate(jall) if k == 0 or not (x[:2] == jall[k - 1][:2] and x[2] == jall[k - 1][2] + 1))
print(f"   json_invalido: {len(jall)} falhas em {seqs} sequências (steps consecutivos do mesmo papel fundidos) · "
      f"{len({x[0] for x in jall})} execuções")
rc = [e for e in EM if e["unidade"] == "U_repr_colado"]
print(f"   U_repr_colado visível: {len(rc)} erros em {len({e['exec_id'] for e in rc})} execuções · execuções em comum "
      f"com o json_invalido silencioso: {len({e['exec_id'] for e in rc} & {x[0] for x in jall})}")
eco = [p for p in sil if not p["chamou"]]
print(f"   falha silenciosa sem a ferramenta chamada no step (possível eco de print): {len(eco)} "
      f"{dict(Counter(p['grupo'] for p in eco))}")
sil_seq = sorted({(p["eid"], p["role"], p["i"]) for p in sil})
casc = sum(1 for k, x in enumerate(sil_seq) if k == 0 or not (x[:2] == sil_seq[k - 1][:2] and x[2] == sil_seq[k - 1][2] + 1))
print(f"   todas as silenciosas: {len(sil_seq)} steps em {casc} sequências · execuções com papel 'null': {papel_null} "
      f"(falhas nele: {sum(p['role'] == 'null' for p in sil)})")
multi = sum(1 for seq in passos.values() if seq and max(s["chamada"] for s in seq) > 1)
print(f"   papéis com mais de uma chamada (TaskStep) na mesma execução: {multi} de {len(passos)}")

# ------------------------------------------------------------------ G. consolidação (Ajuste 12)
print("G. consolidação — U_repr_colado nos dois canais (doc 13 §2 e §5; Ajuste 12):")


def colado_no_step(p):
    """JSON inválido com o 1º argumento colado de um retorno impresso: dict/lista literal (dentro de str() ou não) ou
    string literal, com ≥2 chaves já impressas numa observação anterior do papel (o critério do repr_colado)."""
    seq = passos[(p["eid"], p["role"])]
    a = primeiro_argumento(seq[p["i"]]["code"], p["ferr"])
    if a is None: return False
    obs_ant = "".join(s["obs"] for s in seq[:p["i"]])
    if a.startswith("str(") and a[4:].lstrip()[:1] in "{[": return colado(a, obs_ant)
    if a[:1] in "{[" or re.match(r"[fFrR]?[\"']", a): return colado(a, obs_ant)
    return False


passos_sil = sorted({(p["eid"], p["role"], p["i"]) for p in sil})
casc_de, n = {}, 0
for k, x in enumerate(passos_sil):
    if k == 0 or not (x[:2] == passos_sil[k - 1][:2] and x[2] == passos_sil[k - 1][2] + 1): n += 1
    casc_de[x] = n
s_rc = {(p["eid"], p["role"], p["i"]): p["mes"] for p in sil if p["grupo"] == "json_invalido" and colado_no_step(p)}
oc_s = {casc_de[k] for k in s_rc}
v_rc = [e for e in EM if e["unidade"] == "U_repr_colado"]
oc_v = {e["cascata"] for e in v_rc}
execs = {e["exec_id"] for e in v_rc} | {k[0] for k in s_rc}
meses = {e["mes"] for e in v_rc} | set(s_rc.values())
papeis = {e["role"] for e in v_rc} | {k[1] for k in s_rc}
print(f"   visível: {len(v_rc)} erros em {len(oc_v)} ocorrências · silencioso: {len(s_rc)} steps em {len(oc_s)} "
      f"ocorrências · execuções em comum: {len({e['exec_id'] for e in v_rc} & {k[0] for k in s_rc})}")
esp = ESPERADO["consolidado"]
confere("U_repr_colado consolidada — ocorrências", len(oc_v) + len(oc_s), esp["ocorrencias"])
confere("U_repr_colado consolidada — execuções", len(execs), esp["execucoes"])
confere("U_repr_colado consolidada — meses", len(meses), esp["meses"])
confere("U_repr_colado consolidada — papéis", len(papeis), esp["papeis"])

print(f"\nDIVERGÊNCIAS: {len(DIVERG)}" + (f" → {DIVERG}" if DIVERG else ""))
