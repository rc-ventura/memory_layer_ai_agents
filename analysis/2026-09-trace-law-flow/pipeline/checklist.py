# -*- coding: utf-8 -*-
"""checklist.py — verificações de intake antes de rodar a análise numa base nova.

Operacionaliza os itens não-mecânicos do "Intake checklist — a new trace base"
(analysis/README.md). Roda antes de qualquer notebook:

  §0 formato     — CSV ou parquet; no parquet, o tipo de cada coluna, nulos, texto vazio que virou nulo e colunas
                   aninhadas (o leitor as serializa com json.dumps); para se alguma memória não parsear
  §1 schema      — as colunas que base_pipeline.py lê por nome existem? quais extras vieram?
  §2 cobertura   — linhas, linhas com memória, linhas com >=1 erro (o que o LIKE do SQL pegaria);
  §3 JSON        — quantas memórias parseiam vs. quebram (o except de explodir_memoria engole
                   quebradas em silêncio);
  §4 error.type  — censo regex no cru (o que o DISTINCT no banco vê) × censo via parse (o que
                   o pipeline vê), com flag de divergência;
  §5 contexto    — período das execuções (dat_hor_inio_exeo) × lotes de corte (anomesdia), com o cruzamento;
                   agentes/versões, papéis presentes no JSON.

Uso (rodar de dentro de pipeline/):  python checklist.py [outra-base.csv|.parquet]
Lê sempre o TRACE de base_pipeline.py — nada hardcoded aqui —, com o leitor único ler_trace() (CSV ou parquet).
Com um argumento, adiciona §6: sobreposição de execuções (cod_idef_exeo) com a outra base —
o outro arquivo pode ser um CSV ou parquet completo, ou uma lista de IDs em coluna única.
"""
import json, os, re, sys
from collections import Counter
import pandas as pd
from base_pipeline import TRACE, ler_trace

# dat_hor_inio_exeo é requerida desde 23/09/2026: é dela que base_pipeline.py tira o `mes` (quando a execução
# rodou). anomesdia continua requerida, mas só como proveniência (o lote de corte) — não data a execução.
REQUERIDAS = ["txt_etap_memo", "cod_idef_exeo", "cod_idef_aget",
              "cod_idef_stat_exeo_aget", "dat_hor_inio_exeo", "anomesdia"]
VALIOSAS = ["txt_vrvl_locl", "txt_rspa_fina",
            "dat_hor_encm_exeo", "cod_vers_aget", "cod_idef_cvsa_asnc"]

df = ler_trace(TRACE)
FORMATO = df.attrs.get("formato", {})

print("=" * 66)
print(f"CHECKLIST — {os.path.basename(TRACE)}")
print("=" * 66)

# -- §0 formato -------------------------------------------------------------------
print(f"\n§0 FORMATO — {FORMATO.get('formato', '?')}\n")
if FORMATO.get("formato") == "parquet":
    print(f"  linhas: {FORMATO['linhas']}   grupos de linhas: {FORMATO['grupos_de_linhas']}\n")
    print(f"  {'coluna':<26} {'tipo no parquet':<34} {'nulos':>8} {'vazio→nulo':>11}")
    for c, r in FORMATO["colunas"].items():
        print(f"  {c:<26} {r['tipo'][:34]:<34} {r['nulos']:>8} {r['vazios_para_nulo']:>11}"
              + ("   <-- aninhada" if r["aninhada"] else ""))
    aninhadas = [c for c, r in FORMATO["colunas"].items() if r["aninhada"]]
    if aninhadas:
        print(f"\n  !! aninhada(s): {', '.join(aninhadas)} — serializadas com json.dumps. Num struct, chave ausente na")
        print("     origem vira null (o arrow completa as chaves): conferir contra uma linha crua antes de seguir")
    fusos = [c for c, r in FORMATO["colunas"].items() if "tz=" in r["tipo"]]
    if fusos:
        print(f"  !! com fuso: {', '.join(fusos)} — o leitor entrega a hora local desse fuso, sem o sufixo")
    if any(r["vazios_para_nulo"] for r in FORMATO["colunas"].values()):
        print("  vazio→nulo: texto vazio no nível da coluna virou nulo, como o pd.read_csv faria com o CSV")
else:
    print("  CSV: texto em tudo; vazio e nulo são a mesma coisa no arquivo")

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
if quebrados and FORMATO.get("formato") == "parquet":
    print("  !! PARAR: no parquet, memória que não parseia é sinal de conversão errada do arquivo — conferir o")
    print("     tipo da coluna no §0 e uma linha crua antes de rodar qualquer notebook")

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
exec_m = part_m = None
if "dat_hor_inio_exeo" in df.columns:
    exec_m = pd.to_datetime(df["dat_hor_inio_exeo"], errors="coerce").dt.to_period("M")
    print(f"  execuções (dat_hor_inio_exeo): {exec_m.min()} a {exec_m.max()}  ({exec_m.nunique()} meses reais)"
          + (f"  !! {int(exec_m.isna().sum())} sem data" if exec_m.isna().any() else ""))
if "anomesdia" in df.columns:
    part_m = pd.to_datetime(df["anomesdia"].str.replace("-", "", regex=False), format="%Y%m%d", errors="coerce").dt.to_period("M")
    print(f"  lotes de corte (anomesdia):    {part_m.min()} a {part_m.max()}  ({part_m.nunique()} lotes)"
          "  — proveniência, não data de execução")
if exec_m is not None and part_m is not None:
    igual = (exec_m == part_m).mean()
    print(f"  lote = mês real em {igual:.0%} das linhas. Execuções por lote (linhas) × mês real (colunas):\n")
    print("\n".join("    " + l for l in pd.crosstab(part_m, exec_m).to_string().splitlines()))
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
    outro = ler_trace(outro_path)
    col = "cod_idef_exeo" if "cod_idef_exeo" in outro.columns else outro.columns[0]
    atual, outros = set(df["cod_idef_exeo"].dropna()), set(outro[col].dropna())
    inter = atual & outros
    print("\n§6 SOBREPOSIÇÃO —", os.path.basename(outro_path), "\n")
    print(f"  exec_ids nesta base:   {len(atual)}")
    print(f"  exec_ids na outra:     {len(outros)}")
    print(f"  sobrepostos:           {len(inter)}   ({len(inter)/max(len(outros),1):.0%} da outra base)")
    if inter:
        print("  → mesmas execuções nas duas bases: dedup obrigatório numa análise conjunta;")
        print("    como réplica, reportar a sobreposição no relatório.")
    else:
        print("  → extrações disjuntas: réplica independente.")
print()

if quebrados and FORMATO.get("formato") == "parquet":
    sys.exit(1)   # o intake não passa: ver o §3
