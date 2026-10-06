"""O painel das lições candidatas: a FREQUÊNCIA (vale um notebook?), a CONFIANÇA (o padrão existe? a lição está
escrita de um jeito que duas pessoas aplicam igual?), a SITUAÇÃO de cada uma e a DECISÃO do pesquisador nas situações
que pedem uma. As regras estão no procedimento da análise (`docs/*procedimento-mineracao-candidatas*.md`, "A regra de
criação de um notebook específico" e "O gate do pesquisador").

    python valor_da_licao.py <pasta-da-analise> [<unidade>]

Frequência (lê pipeline/resultados/candidatos_memoria.csv e execucoes.csv):
  Pareto    a lição está entre as que, juntas, chegam a 80% das ocorrências das candidatas (inclusive a que cruza)
  presença  a lição aparece na maior parte dos meses da base
Confiança (lê a tabela do funil do procedimento e pipeline/resultados/mineracao/<u>/confianca.json, que o
concordancia.py e o testar_regra.py gravam com --registrar; vale a última medida de cada pergunta e de cada regra):
  confirmada              regras com concordância ≥ 90% e "pega a mais" ≤ 10%, e os leitores com kappa ≥ 0,6
  redação em aberto       as regras passam (o padrão existe), mas os leitores discordam (kappa < 0,6)
  várias causas           um dos leitores pôs metade ou mais dos casos em "não há uma lição única"
  padrão não confirmado   alguma regra abaixo dos limiares
  poucos casos            a leitura dos dois leitores tem menos de 20 casos (ou menos que a população, se ela é menor)
  não avaliada            sem confianca.json, sem leitura dupla ou sem regra contada
Situação: notebook · pronta para notebook · lição existe, redação em aberto · várias causas: investigar a fundo ·
importante e mal entendida · prioridade de investigação · certa, mas rara: monitorar · baixa prioridade.
Decisão (lê pipeline/resultados/mineracao/<u>/decisoes.json, gravado pelo registrar_decisao.py): nas situações com
gate, "aguardando" até o pesquisador decidir para a situação atual.
Com <unidade>, imprime as opções do gate e sai com 0 se a lição tem frequência e 1 se não.
Só contagens; só biblioteca padrão.
"""

import csv, glob, json, os, re, sys

PARETO, KAPPA, CONCORDANCIA, A_MAIS, MIN_LEITURA, NULA = 0.80, 0.6, 0.90, 0.10, 20, 0.5

# as situações que param e pedem a decisão do pesquisador, com as opções que o relatório leva
GATE = {
    "pronta para notebook": ["propor o notebook (/propor-notebook)", "esperar a próxima partição"],
    "lição existe, redação em aberto": ["aprovar a lição de um dos leitores", "escrever uma lição geral que cubra as duas",
                                        "investigar mais a fundo (várias causas; dividir a lição)"],
    "várias causas: investigar a fundo": ["dividir a lição por causa", "investigar mais a fundo"],
    "certa, mas rara: monitorar": ["monitorar (reconferir a cada partição nova)", "descartar"],
}


def funil(pasta):
    docs = glob.glob(os.path.join(pasta, "docs", "*procedimento-mineracao-candidatas*.md"))
    if not docs:
        return {}
    txt = open(docs[0], encoding="utf-8").read()
    bloco = txt.split("<!-- funil", 1)[-1].split("<!-- /funil -->", 1)[0]
    return {m.group(1): m.group(2) for m in re.finditer(r"^\|\s*`([UHXC]_\w+)`\s*\|\s*`([^`]+)`", bloco, re.M)}


def populacao(pasta, u):
    arq = os.path.join(pasta, "pipeline", "resultados", "mineracao", u, "casos.csv")
    if not os.path.exists(arq):
        return None
    with open(arq, encoding="utf-8", newline="") as fh:
        return sum(1 for _ in csv.DictReader(fh))


def confianca(pasta, u, parte):
    if parte.startswith("notebook:"):
        return "confirmada (notebook)"
    arq = os.path.join(pasta, "pipeline", "resultados", "mineracao", u, "confianca.json")
    if not os.path.exists(arq):
        return "não avaliada"
    d = json.load(open(arq, encoding="utf-8"))
    # vale a ÚLTIMA medida de cada pergunta (rótulo, local) e de cada regra (rótulo, alvo, local): as versões de regra
    # testadas antes, inclusive as que falharam, ficam no histórico do arquivo, mas não decidem
    ultimos = lambda lst, chave: list({chave(r): r for r in lst}.values())
    leit = ultimos(d.get("leitores", []), lambda r: (r["rotulo"], r.get("local")))
    regr = ultimos(d.get("regras", []), lambda r: (r["rotulo"], r["alvo"], r.get("local")))
    if not leit:
        return "não avaliada"
    if any(r.get("nula", 0) >= NULA for r in leit):
        return "várias causas"
    pop = populacao(pasta, u)
    minimo = min(MIN_LEITURA, pop) if pop else MIN_LEITURA
    if any(r["casos"] < minimo for r in leit):
        return "poucos casos"
    if not regr:
        return "não avaliada"
    if not all(r["concordancia"] >= CONCORDANCIA and r["pega_a_mais"] <= A_MAIS for r in regr):
        return "padrão não confirmado"
    if not all(r["kappa"] >= KAPPA for r in leit):
        return "redação em aberto"
    return "confirmada"


def situacao(freq, conf):
    if conf == "confirmada (notebook)":
        return "notebook"
    if freq != "não":
        return {"confirmada": "pronta para notebook",
                "redação em aberto": "lição existe, redação em aberto",
                "várias causas": "várias causas: investigar a fundo",
                "padrão não confirmado": "importante e mal entendida"}.get(conf, "prioridade de investigação")
    return "certa, mas rara: monitorar" if conf == "confirmada" else "baixa prioridade"


def decisao(pasta, u, sit):
    if sit not in GATE:
        return "—"
    arq = os.path.join(pasta, "pipeline", "resultados", "mineracao", u, "decisoes.json")
    if os.path.exists(arq):
        for r in reversed(json.load(open(arq, encoding="utf-8"))):
            if r.get("situacao") == sit:
                return f"{r['opcao']} ({r['data']})"
    return "aguardando"


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
    linha_de = {}
    print(f"{'unidade':<20} {'ocorr.':>6} {'acum.':>5} {'meses':>7}  {'frequência':<17} {'confiança':<22} "
          f"{'situação':<34} decisão")
    for r in cand:
        u = r["unidade"]
        acum += int(r["ocorrências"])
        pareto, presenca = antes < PARETO, int(r["meses"]) > meses_base / 2
        freq = " + ".join(n for n, v in (("Pareto", pareto), ("presença", presenca)) if v) or "não"
        conf = confianca(pasta, u, partes.get(u, ""))
        sit = situacao(freq, conf)
        dec = decisao(pasta, u, sit)
        linha_de[u] = (freq, conf, sit, dec)
        print(f"{u:<20} {r['ocorrências']:>6} {acum / total:>5.0%} {r['meses']:>3}/{meses_base:<3}  {freq:<17} "
              f"{conf:<22} {sit:<34} {dec}")
        antes = acum / total
    print(f"\n{len(cand)} candidatas · {total} ocorrências · {meses_base} meses na base")
    if len(sys.argv) > 2:
        u = sys.argv[2]
        freq, conf, sit, dec = linha_de.get(u, ("não", "?", "?", "—"))
        print(f"{u}: frequência {freq} · confiança {conf} · situação {sit} · decisão {dec}")
        if sit in GATE:
            print("  opções do gate: " + " · ".join(GATE[sit]))
        sys.exit(0 if freq != "não" else 1)


if __name__ == "__main__":
    main()
