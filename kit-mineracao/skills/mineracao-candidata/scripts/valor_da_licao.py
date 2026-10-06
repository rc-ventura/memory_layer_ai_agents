"""O painel das lições candidatas: a FREQUÊNCIA (vale um notebook?), a CONFIANÇA (a regra está certa?) e a SITUAÇÃO de
cada uma — a fila de trabalho da mineração de candidatas. As regras estão no procedimento da análise
(`docs/*procedimento-mineracao-candidatas*.md`, "A regra de criação de um notebook específico").

    python valor_da_licao.py <pasta-da-analise> [<unidade>]

Frequência (lê pipeline/resultados/candidatos_memoria.csv e execucoes.csv):
  Pareto    a lição está entre as que, juntas, chegam a 80% das ocorrências das candidatas (inclusive a que cruza)
  presença  a lição aparece na maior parte dos meses da base
Confiança (lê a tabela do funil do procedimento e pipeline/resultados/mineracao/<u>/confianca.json, que o
concordancia.py e o testar_regra.py gravam com --registrar):
  confirmada    a lição tem notebook específico no funil; ou todos os registros passam (kappa ≥ 0,6 entre os leitores;
                regras com concordância ≥ 90% e "pega a mais" ≤ 10%)
  falhou        algum registro abaixo dos limiares (inclusive numa partição nova)
  não avaliada  sem confianca.json
Situação: pronta para notebook · prioridade de investigação · importante e mal entendida · certa, mas rara · baixa
prioridade (e "notebook" para quem já tem). Com <unidade>, sai com 0 se ela tem frequência e 1 se não.
Só contagens; só biblioteca padrão.
"""

import csv, glob, json, os, re, sys

PARETO, KAPPA, CONCORDANCIA, A_MAIS = 0.80, 0.6, 0.90, 0.10


def funil(pasta):
    docs = glob.glob(os.path.join(pasta, "docs", "*procedimento-mineracao-candidatas*.md"))
    if not docs:
        return {}
    txt = open(docs[0], encoding="utf-8").read()
    bloco = txt.split("<!-- funil", 1)[-1].split("<!-- /funil -->", 1)[0]
    return {m.group(1): m.group(2) for m in re.finditer(r"^\|\s*`([UHXC]_\w+)`\s*\|\s*`([^`]+)`", bloco, re.M)}


def confianca(pasta, u, parte):
    if parte.startswith("notebook:"):
        return "confirmada (notebook)"
    arq = os.path.join(pasta, "pipeline", "resultados", "mineracao", u, "confianca.json")
    if not os.path.exists(arq):
        return "não avaliada"
    d = json.load(open(arq, encoding="utf-8"))
    ok = all(r["kappa"] >= KAPPA for r in d.get("leitores", [])) and \
         all(r["concordancia"] >= CONCORDANCIA and r["pega_a_mais"] <= A_MAIS for r in d.get("regras", []))
    tem = d.get("leitores") and d.get("regras")
    return "confirmada" if ok and tem else ("falhou" if not ok else "não avaliada")


def situacao(freq, conf):
    if conf == "confirmada (notebook)":
        return "notebook"
    if freq != "não":
        return {"confirmada": "pronta para notebook", "falhou": "importante e mal entendida"}.get(conf, "prioridade de investigação")
    return "certa, mas rara" if conf == "confirmada" else "baixa prioridade"


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    pasta = os.path.abspath(sys.argv[1])
    res = os.path.join(pasta, "pipeline", "resultados")
    cand = [r for r in csv.DictReader(open(os.path.join(res, "candidatos_memoria.csv"), encoding="utf-8"))
            if r.get("decisão") == "candidato"]
    meses_base = len({r["mes"] for r in csv.DictReader(open(os.path.join(res, "execucoes.csv"), encoding="utf-8"))})
    partes = funil(pasta)
    cand.sort(key=lambda r: -int(r["ocorrências"]))
    total, acum, antes = sum(int(r["ocorrências"]) for r in cand), 0, 0.0
    freq_de = {}
    print(f"{'unidade':<22} {'ocorr.':>6} {'acum.':>5} {'meses':>7}  {'frequência':<17} {'confiança':<22} situação")
    for r in cand:
        u = r["unidade"]
        acum += int(r["ocorrências"])
        pareto, presenca = antes < PARETO, int(r["meses"]) > meses_base / 2
        freq = " + ".join(n for n, v in (("Pareto", pareto), ("presença", presenca)) if v) or "não"
        conf = confianca(pasta, u, partes.get(u, ""))
        freq_de[u] = freq
        print(f"{u:<22} {r['ocorrências']:>6} {acum / total:>5.0%} {r['meses']:>3}/{meses_base:<3}  {freq:<17} {conf:<22} "
              f"{situacao(freq, conf)}")
        antes = acum / total
    print(f"\n{len(cand)} candidatas · {total} ocorrências · {meses_base} meses na base")
    if len(sys.argv) > 2:
        u = sys.argv[2]
        print(f"{u}: frequência {freq_de.get(u, '?')}")
        sys.exit(0 if freq_de.get(u, "não") != "não" else 1)


if __name__ == "__main__":
    main()
