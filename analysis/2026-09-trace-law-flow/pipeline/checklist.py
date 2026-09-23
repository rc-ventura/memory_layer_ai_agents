# -*- coding: utf-8 -*-
"""checklist.py — verificações de intake antes de rodar a análise numa base nova.

Operacionaliza os itens não-mecânicos do "Intake checklist — a new trace base"
(analysis/README.md). Roda antes de qualquer notebook:

  §1 schema      — as colunas que base_pipeline.py lê por nome existem? quais extras vieram?
  §2 cobertura   — linhas, linhas com memória, linhas com >=1 erro (o que o LIKE do SQL pegaria);
  §3 JSON        — quantas memórias parseiam vs. quebram (o except de explodir_memoria engole
                   quebradas em silêncio);
  §4 error.type  — censo regex no cru (o que o DISTINCT no banco vê) × censo via parse (o que
                   o pipeline vê), com flag de divergência;
  §5 contexto    — período (anomesdia), agentes/versões, papéis presentes no JSON.

Uso (rodar de dentro de pipeline/):  python checklist.py [outra-base.csv]
Lê sempre o TRACE de base_pipeline.py — nada hardcoded aqui.
Com um argumento, adiciona §6: sobreposição de execuções (cod_idef_exeo) com a outra base —
o outro arquivo pode ser um CSV completo ou uma lista de IDs em coluna única.
"""
import json, re, sys
from collections import Counter
import pandas as pd
from base_pipeline import TRACE

REQUERIDAS = ["txt_etap_memo", "cod_idef_exeo", "cod_idef_aget",
              "cod_idef_stat_exeo_aget", "anomesdia"]
VALIOSAS = ["txt_vrvl_locl", "txt_rspa_fina", "dat_hor_inio_exeo",
            "dat_hor_encm_exeo", "cod_vers_aget", "cod_idef_cvsa_asnc"]

df = pd.read_csv(TRACE, dtype=str)

print("=" * 66)
print(f"CHECKLIST — {TRACE.split('/')[-1]}")
print("=" * 66)

# -- §1 schema -----------------------------------------------------------------
print("\n§1 SCHEMA — colunas\n")
faltam = [c for c in REQUERIDAS if c not in df.columns]
for c in REQUERIDAS:
    print(f"  {'ok ' if c in df.columns else 'FALTA'}  {c}")
extras = [c for c in df.columns if c not in REQUERIDAS]
print(f"\n  extras ({len(extras)}): {', '.join(extras)}")
for c in VALIOSAS:
    if c in extras:
        print(f"    + {c} — evidência disponível")
if faltam:
    print(f"\n  !! {len(faltam)} requerida(s) ausente(s) — ajustar carregar_trace() antes de seguir")

# -- §2 cobertura ---------------------------------------------------------------
memos = df["txt_etap_memo"].dropna() if "txt_etap_memo" in df.columns else pd.Series(dtype=str)
com_erro = int(memos.str.contains(r'"error":\s*\{', regex=True).sum())
print("\n§2 COBERTURA\n")
print(f"  linhas totais:            {len(df)}")
print(f"  com txt_etap_memo:        {len(memos)}")
print(f"  com >=1 erro (LIKE cru):  {com_erro}   ({com_erro/max(len(memos),1):.1%} das c/ memória)")

# -- §3+§4 um parse só: saúde do JSON, censo parseado e papéis --------------------
raw = Counter(t for m in memos for t in re.findall(r'"error":\s*\{\s*"type":\s*"([^"]+)"', m))
parsed, papeis = Counter(), Counter()
parse_ok = quebrados = 0
for m in memos:
    try:
        d = json.loads(m)
    except Exception:
        quebrados += 1
        continue
    parse_ok += 1
    for role, steps in d.items():
        if not isinstance(steps, list):
            continue
        papeis[role] += 1
        for s in steps:
            e = (s or {}).get("error") or {}
            if e.get("type"):
                parsed[e["type"]] += 1

print("\n§3 JSON — memórias que parseiam\n")
print(f"  parse ok:  {parse_ok}")
print(f"  quebradas: {quebrados}   (>0 = execuções descartadas em silêncio pelo pipeline)")

print("\n§4 CENSO error.type — regex (cru) × parse (pipeline)\n")
print(f"  {'error.type':<30} {'regex':>8} {'parse':>8}")
for t in sorted(set(raw) | set(parsed)):
    flag = "   <-- divergência" if raw[t] != parsed[t] else ""
    print(f"  {t:<30} {raw[t]:>8} {parsed[t]:>8}{flag}")
print(f"\n  total de erros:           regex={sum(raw.values())}   parse={sum(parsed.values())}")
novos = [t for t in raw if t not in ("AgentExecutionError", "AgentParsingError")]
if novos:
    print(f"  !! tipo(s) fora da dupla conhecida: {novos} — investigar antes de classificar")

# -- §5 contexto ------------------------------------------------------------------
print("\n§5 CONTEXTO\n")
if "anomesdia" in df.columns:
    meses = pd.to_datetime(df["anomesdia"], format="%Y%m%d", errors="coerce").dt.to_period("M")
    print(f"  período (anomesdia):      {meses.min()} a {meses.max()}  ({meses.nunique()} meses)")
if "cod_idef_aget" in df.columns:
    vc = df["cod_idef_aget"].value_counts()
    print(f"  agentes (cod_idef_aget):  {df['cod_idef_aget'].nunique()} — "
          + ", ".join(f"{k}({v})" for k, v in vc.head(6).items()))
if "cod_vers_aget" in df.columns:
    vc = df["cod_vers_aget"].value_counts()
    print(f"  versões (cod_vers_aget):  {df['cod_vers_aget'].nunique()} — "
          + ", ".join(f"{k}({v})" for k, v in vc.head(6).items()))
print(f"  papéis no JSON:           {len(papeis)} — "
      + ", ".join(f"{k}({v} execs)" for k, v in papeis.most_common(8)))

# -- §6 sobreposição com outra base (opcional, via argumento) ---------------------
if len(sys.argv) > 1 and "cod_idef_exeo" in df.columns:
    outro_path = sys.argv[1]
    outro = pd.read_csv(outro_path, dtype=str)
    col = "cod_idef_exeo" if "cod_idef_exeo" in outro.columns else outro.columns[0]
    atual, outros = set(df["cod_idef_exeo"].dropna()), set(outro[col].dropna())
    inter = atual & outros
    print("\n§6 SOBREPOSIÇÃO —", outro_path.split("/")[-1], "\n")
    print(f"  exec_ids nesta base:   {len(atual)}")
    print(f"  exec_ids na outra:     {len(outros)}")
    print(f"  sobrepostos:           {len(inter)}   ({len(inter)/max(len(outros),1):.0%} da outra base)")
    if inter:
        print("  → mesmas execuções nas duas bases: dedup obrigatório numa análise conjunta;")
        print("    como réplica, reportar a sobreposição no relatório.")
    else:
        print("  → extrações disjuntas: réplica independente.")
print()
