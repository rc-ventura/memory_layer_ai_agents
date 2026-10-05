"""Auditoria independente da família "Protocolo do harness" (o erro "resposta sem bloco de código").

Recalcula do zero, a partir da prosa do 10-racionais-protocolo-harness.md e do 12-procedimento-protocolo-harness.md, as
medidas que o `drill_down.py protocolo` imprime ([1]–[9]) e grava nas tabelas de resultados/evidencia/protocolo/.
Independência: csv + json + re + hashlib; não importa o base_pipeline nem o drill_down. Só a abertura do arquivo vem de
fora (analysis/leitor_trace.py), e o próximo erro da cascata vem do erros_mecanismo.csv (--em), como no audit_recompute9.

    python audit_recompute10.py                                         # base 1, contra os números do 11 §1
    python audit_recompute10.py --base <base> --trace <arquivo> --em <erros_mecanismo.csv> --json <medidas.json>

Base sem números embutidos: tudo "a conferir"; com --json, grava as medidas para o encontro com as tabelas da
mineração (kit de mineração, skill mineracao-protocolo).
"""
import argparse, csv, hashlib, json, os, re, sys
from collections import Counter, defaultdict

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, ".."))
from leitor_trace import abrir_trace   # só a abertura do arquivo (CSV ou parquet, plano §4.10)

ap = argparse.ArgumentParser()
ap.add_argument("--base", default="base1")
ap.add_argument("--trace", default=os.path.join(RAIZ, "data", "85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz"))
ap.add_argument("--em", default=os.path.join(RAIZ, "pipeline", "resultados", "erros_mecanismo.csv"))
ap.add_argument("--json")
args = ap.parse_args()

# ------------------------------------------------------------------ o publicado (11 §1.1 e §1.2), por base
ESPERADO = {
    "base1": dict(erros=33, por_mes={"2025-10": 24, "2025-11": 1, "2025-12": 7, "2026-02": 1},
                  formas={"frase ou texto (sem código)": 31, "bloco em ``` em vez de <code>": 2},
                  papel_entregou_depois=33, execucao_com_resposta=33,
                  proximo={"(step sem erro)": 25, "U_texto_solto": 7, "U_estado_perdido": 1},
                  versoes={"82de8f07": (130, 21), "2f96aa69": (83, 3), "b0f37eea": (193, 9)}),
}.get(args.base, {})
DIVERG = []


def confere(rotulo, meu, esp):
    if esp is None:
        print(f"   {rotulo}: {meu} (a conferir — sem número publicado para {args.base})")
    elif meu == esp:
        print(f"   {rotulo}: {meu} OK")
    else:
        print(f"   {rotulo}: {meu} << DIVERGE (publicado {esp})"); DIVERG.append(rotulo)


# ------------------------------------------------------------------ as definições, da prosa dos docs 10 e 12
MARCAS_DE_FORMATO = re.compile(r"<code>|</code>|```|<end_code>|Thought:|final_answer\(")


def prompt_de_sistema(st):
    """A primeira mensagem do contexto do step: é onde o formato e as ferramentas são declarados."""
    mim = st.get("model_input_messages") or []
    if not mim or not isinstance(mim[0], dict): return ""
    c = mim[0].get("content")
    return c[0].get("text", "") if isinstance(c, list) and c and isinstance(c[0], dict) else str(c or "")


def versao_do_formato(sp):
    """12 Passo 2.1: a versão é o hash das linhas do prompt que citam as marcas de código, com dígitos mascarados."""
    if not sp: return "(sem prompt)"
    linhas = [re.sub(r"\d", "0", l.strip()) for l in sp.splitlines() if MARCAS_DE_FORMATO.search(l)]
    return hashlib.md5("\n".join(linhas).encode("utf-8")).hexdigest()[:8]


def modo(sp):
    """10 §2: JSON estruturado ({"thought": …}) × texto com <code>…</code> (o único modo em que o erro existe)."""
    if re.search(r'\{"thought":', sp): return "JSON estruturado"
    if "<code>" in sp and "</code>" in sp: return "texto com <code>"
    return "outro"


def modelo(st):
    m = st.get("model_output_message")
    raw = m.get("raw") if isinstance(m, dict) else None
    return str(raw.get("model")) if isinstance(raw, dict) and raw.get("model") else "(não registrado)"


def forma(texto):
    """12 Passo 4, pergunta A, só pela forma: o </code> final é a sequência de parada e não conta."""
    t = re.sub(r"\s*</code>\s*$", "", texto).strip()
    if len(t) < 20: return "vazio"
    if re.search(r"```(py|python)?\s*\n", t): return "bloco em ``` em vez de <code>"
    if t[0] in "{[": return "resposta em dict/JSON (sem código)"
    return "frase ou texto (sem código)"


def sobreposicao(texto, outro, n=5):
    """10 §4 M1: a fração dos trechos de 5 palavras do texto que reaparecem no outro."""
    def trechos(t):
        w = re.findall(r"\w+", str(t or "").lower())
        return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}
    a = trechos(texto)
    return len(a & trechos(outro)) / len(a) if a else 0.0


LIMIAR_M1 = 0.5

# ------------------------------------------------------------------ leitura do cru
unidade_do_erro = {}
for e in csv.DictReader(open(args.em, encoding="utf-8")):
    unidade_do_erro[(e["exec_id"], e["role"], int(e["idx"]))] = e["unidade"]

passos = Counter()                       # (mes, papel) -> steps
versoes = defaultdict(lambda: [0, 0])    # (papel, versão) -> [steps, erros]
modos = {}
modelos = defaultdict(lambda: [0, 0])    # (papel, eixo, valor) -> [steps, erros]
erros, vistos = [], set()
with abrir_trace(args.trace) as linhas:
    for r in linhas:
        eid = r["cod_idef_exeo"]
        if eid in vistos or not r.get("txt_etap_memo"): continue
        vistos.add(eid)
        try: memo = json.loads(r["txt_etap_memo"])
        except Exception: continue
        papeis = {p: l for p, l in memo.items() if isinstance(l, list)}
        acoes = {p: [s for s in l if isinstance(s, dict) and s.get("__class__") == "ActionStep"] for p, l in papeis.items()}
        if not any(acoes.values()): continue          # execução sem nenhum ActionStep não entra na contagem
        mes = r["dat_hor_inio_exeo"][:7]
        tem_final = any(s.get("is_final_answer") for a in acoes.values() for s in a)
        versao_agente = r.get("cod_vers_aget") or "nan"   # nulo como o pandas o escreve
        for papel, lst in papeis.items():
            acts = acoes[papel]
            chamada, ch = [], 0
            for s in lst:
                if isinstance(s, dict) and s.get("__class__") == "TaskStep": ch += 1
                elif isinstance(s, dict) and s.get("__class__") == "ActionStep": chamada.append(ch)
            passos[(mes, papel)] += len(acts)
            for i, s in enumerate(acts):
                sp = prompt_de_sistema(s)
                v = versao_do_formato(sp)
                modos[(papel, v)] = modo(sp)
                eh_erro = "regex pattern" in str((s.get("error") or {}).get("message") or "")
                versoes[(papel, v)][0] += 1; versoes[(papel, v)][1] += eh_erro
                for eixo, valor in (("modelo", modelo(s)), ("versão do agente", versao_agente)):
                    modelos[(papel, eixo, valor)][0] += 1; modelos[(papel, eixo, valor)][1] += eh_erro
                if not eh_erro: continue
                texto = str(s.get("model_output") or "")
                seguintes = [unidade_do_erro.get((eid, papel, j)) for j in range(i + 1, len(acts))]
                cascata = []
                for u in seguintes:
                    if u is None: break
                    cascata.append(u)
                final = next((a for a in acts[i + 1:] if a.get("is_final_answer")), None)
                erros.append(dict(
                    mes=mes, papel=papel, eid=eid, forma=forma(texto),
                    papel_entregou_depois=any(a.get("is_final_answer") and not a.get("error") for a in acts[i + 1:]),
                    execucao_com_resposta=tem_final, proximo=cascata[0] if cascata else "(step sem erro)",
                    antecipou=(sobreposicao(texto, str(final.get("action_output") or "")) if final else 0.0) >= LIMIAR_M1,
                    copiou=(sobreposicao(texto, str(acts[i - 1].get("observations") or "")) if i > 0 else 0.0) >= LIMIAR_M1,
                    chamada=chamada[i], chamadas_do_papel=ch))

# ------------------------------------------------------------------ as medidas
print(f"[{args.base}] execuções lidas: {len(vistos)} · steps: {sum(passos.values())} · erros 'resposta sem bloco de código': {len(erros)}")
papeis_com_erro = {e["papel"] for e in erros}
por_mes, por_papel = Counter(e["mes"] for e in erros), Counter(e["papel"] for e in erros)
steps_mes, steps_papel = Counter(), Counter()
for (m, p), n in passos.items(): steps_mes[m] += n; steps_papel[p] += n
print("A. contagem ([1], [2]):")
confere("erros", len(erros), ESPERADO.get("erros"))
confere("execuções com o erro", len({e["eid"] for e in erros}), None)
confere("papéis com o erro", len(papeis_com_erro), None)
confere("erros por mês", dict(sorted(por_mes.items())), ESPERADO.get("por_mes"))
print("B. forma, recuperação e cascata ([4], [5], [6]):")
confere("forma", dict(Counter(e["forma"] for e in erros).most_common()), ESPERADO.get("formas"))
confere("o papel entregou final_answer depois", sum(e["papel_entregou_depois"] for e in erros), ESPERADO.get("papel_entregou_depois"))
confere("a execução terminou com resposta", sum(e["execucao_com_resposta"] for e in erros), ESPERADO.get("execucao_com_resposta"))
confere("o que vem logo depois", dict(Counter(e["proximo"] for e in erros).most_common()), ESPERADO.get("proximo"))
print("C. a camada ([7] versões do formato, [8] modelos):")
por_versao = defaultdict(lambda: [0, 0])
for (p, v), (st, er) in versoes.items():
    if p in papeis_com_erro: por_versao[v][0] += st; por_versao[v][1] += er
for v, esp in (ESPERADO.get("versoes") or {}).items():
    confere(f"versão {v} (steps, erros)", tuple(por_versao.get(v, (0, 0))), esp)
print(f"   versões nos papéis com o erro: {len(por_versao)} · modelos nos papéis com o erro: "
      f"{len({k[2] for k in modelos if k[0] in papeis_com_erro and k[1] == 'modelo'})}")
print("D. M1 e fronteira de chamada ([9]):")
print(f"   antecipou a resposta final: {sum(e['antecipou'] for e in erros)}/{len(erros)} · copiou da observação anterior: "
      f"{sum(e['copiou'] for e in erros)}/{len(erros)} · erros numa chamada > 1: {sum(e['chamada'] > 1 for e in erros)} · "
      f"erros em papel com mais de uma chamada: {sum(e['chamadas_do_papel'] > 1 for e in erros)}")

if args.json:
    with open(args.json, "w", encoding="utf-8") as fh:
        json.dump({
            "base": args.base, "erros": len(erros), "execucoes": len({e["eid"] for e in erros}),
            "papeis": len(papeis_com_erro), "steps": sum(passos.values()),
            "steps_por_mes": dict(sorted(steps_mes.items())), "steps_por_papel": dict(sorted(steps_papel.items())),
            "erros_por_mes": dict(sorted(por_mes.items())), "erros_por_papel": dict(sorted(por_papel.items())),
            "formas": dict(sorted(Counter(e["forma"] for e in erros).items())),
            "papel_entregou_depois": sum(e["papel_entregou_depois"] for e in erros),
            "execucao_com_resposta": sum(e["execucao_com_resposta"] for e in erros),
            "proximo": dict(sorted(Counter(e["proximo"] for e in erros).items())),
            "versoes": {f"{p}|{v}": [modos[(p, v)], st, er] for (p, v), (st, er) in sorted(versoes.items())},
            "modelos": {f"{p}|{x}|{val}": [st, er] for (p, x, val), (st, er) in sorted(modelos.items())},
            "m1_antecipou_por_papel": dict(sorted(Counter(e["papel"] for e in erros if e["antecipou"]).items())),
            "m1_copiou_por_papel": dict(sorted(Counter(e["papel"] for e in erros if e["copiou"]).items())),
            "erros_em_chamada_maior_que_1": sum(e["chamada"] > 1 for e in erros),
            "erros_em_papel_com_varias_chamadas": sum(e["chamadas_do_papel"] > 1 for e in erros),
        }, fh, ensure_ascii=False, indent=2)

print(f"\nDIVERGÊNCIAS: {len(DIVERG)}" + (f" → {DIVERG}" if DIVERG else ""))
