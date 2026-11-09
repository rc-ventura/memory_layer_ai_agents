"""Auditoria independente da tabela do resíduo na base 3 (procedimento do resíduo, base 1 `docs/19`; racional `18`).

    python audit_residuo_base3.py --casos <pipeline/resultados/mineracao/residuo/casos.csv> --fonte <parquet>
        --json <arquivo>

Uma segunda implementação, escrita a partir do racional (`18-racionais-residuo.md` §2 e §3), **sem importar o
pipeline nem o `especificas/residuo.py`**. Ela lê o parquet cru com o pyarrow e reescreve à parte:
  - a máscara (aspas → `<q>`, crases → `<id>`, números → `<n>`);
  - a impressão digital de cada erro (o padrão): a classe da exceção mais a frase mascarada; na sintaxe, o motivo do
    parser sem a posição; sem nome de exceção, "sem nome de exceção: <tipo>", que nunca conta como recorrente;
  - a régua de recorrência da triagem da base 3: ≥3 execuções (execução = execução × agente) e ≥2 meses, por erro.
Grava as medidas por padrão num JSON. O encontro com a tabela da mineração é o `comparar_auditoria.py` da skill
`mineracao-residuo`.

**O que vem do pipeline, e só isso:** a população (a chave execução × agente × papel × posição de cada erro do
resíduo) e a classe de cada um (`submecanismo`), lidas do `casos.csv`. Reescrever as regras de causa que decidem quem
cai no resíduo não é o objeto desta auditoria: o que ela confere é o padrão, a contagem e a recorrência. A mensagem, o
mês, o tipo do erro e os tokens vêm do parquet, pela chave, e não do `casos.csv`. "Re-rodar não é verificar": nada aqui
vem do `base_pipeline.py`.

Imprime só contagens. Saída 1 se uma chave da população não estiver na fonte, ou estiver mais de uma vez.
"""
import argparse
from collections import defaultdict
import csv
import json
import re
import sys

import pyarrow.parquet as pq

COLUNAS = ["cod_idef_exeo", "cod_idef_aget", "papel", "step_pos", "mes_execucao", "error_type", "error_message",
           "total_tokens"]
SEM_NOME = "sem nome de exceção"
MIN_EXECUCOES, MIN_MESES = 3, 2


def mascara(frase):
    frase = re.sub(r"'[^']*'|\"[^\"]*\"", "<q>", frase)
    frase = re.sub(r"`[^`]*`", "<id>", frase)
    return re.sub(r"\d+", "<n>", frase).strip()


def impressao_digital(msg, classe_causa, tipo):
    """O padrão de um erro do resíduo (racional §2)."""
    if classe_causa == "codigo_mal_escrito":
        nomes = re.findall(r"due to: (\w+Error)", msg) or re.findall(r"\b(\w+Error)\b", msg)
        nome = nomes[-1] if nomes else "?"
        error = [l.strip()[len("Error:"):] for l in msg.splitlines() if l.strip().startswith("Error:")]
        if error:
            motivo = mascara(error[-1])
        else:
            na_linha = re.search(r"due to: \w+Error: ([^\n]*)", msg)
            motivo = mascara(na_linha.group(1)) if na_linha else ""
        motivo = re.sub(r"\s+on line <n>", "", re.sub(r"\s*\(<unknown>, line <n>\)", "", motivo))
        return f"{nome}: {motivo}".rstrip(": ")
    pares = re.findall(r"(\b\w+(?:Error|Exception)\b):\s*([^\n]{0,90})", msg)
    if pares:
        return f"{pares[-1][0]}: {mascara(pares[-1][1])}"
    nomes = re.findall(r"\b\w+(?:Error|Exception)\b", msg)
    return nomes[-1] if nomes else f"{SEM_NOME}: {tipo or '?'}"


def ler_populacao(caminho):
    with open(caminho, encoding="utf-8", newline="") as fh:
        return [{"chave": (r["exec_id"], str(r["agente"]), r["role"], str(int(float(r["idx"])))),
                 "unidade": r["unidade"], "classe": r["submecanismo"]} for r in csv.DictReader(fh)]


def ler_fonte(caminho, chaves):
    t = pq.read_table(caminho, columns=COLUNAS).to_pylist()
    achadas = defaultdict(list)
    for r in t:
        k = (str(r["cod_idef_exeo"]), str(r["cod_idef_aget"]), str(r["papel"]),
             str(int(r["step_pos"])) if r["step_pos"] is not None else "")
        if k in chaves:
            achadas[k].append(r)
    return achadas


def medir(populacao, achadas):
    grupos = defaultdict(lambda: {"erros": 0, "execucoes": set(), "meses": set(), "papeis": set(), "tokens": 0,
                                  "tokens_ausentes": 0})
    for p in populacao:
        r = achadas[p["chave"]][0]
        padrao = impressao_digital(str(r["error_message"] or ""), p["classe"], r["error_type"])
        g = grupos[(p["unidade"], p["classe"], padrao)]
        g["erros"] += 1
        g["execucoes"].add(p["chave"][:2])
        g["meses"].add(r["mes_execucao"])
        g["papeis"].add(p["chave"][2])
        if r["total_tokens"] is None:
            g["tokens_ausentes"] += 1
        else:
            g["tokens"] += int(r["total_tokens"])
    padroes = []
    for (u, classe, padrao), g in sorted(grupos.items()):
        identificada = not padrao.startswith(SEM_NOME)
        padroes.append({"unidade": u, "submecanismo": classe, "padrao": padrao, "erros": g["erros"],
                        "execucoes": len(g["execucoes"]), "meses": len(g["meses"]), "papeis": len(g["papeis"]),
                        "tokens": g["tokens"], "tokens_ausentes": g["tokens_ausentes"],
                        "chave": "identificada" if identificada else SEM_NOME,
                        "passa_na_recorrencia": identificada and len(g["execucoes"]) >= MIN_EXECUCOES
                        and len(g["meses"]) >= MIN_MESES})
    por_balde = defaultdict(int)
    for p in populacao:
        por_balde[p["unidade"]] += 1
    return {"populacao": len(populacao), "por_balde": dict(sorted(por_balde.items())), "padroes": padroes,
            "padroes_que_passam": sum(p["passa_na_recorrencia"] for p in padroes),
            "regua": {"min_execucoes": MIN_EXECUCOES, "min_meses": MIN_MESES, "execucao": "execução × agente",
                      "contagem": "por erro"}}


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--casos", required=True)
    ap.add_argument("--fonte", required=True)
    ap.add_argument("--json", required=True)
    a = ap.parse_args(argv)
    pop = ler_populacao(a.casos)
    chaves = {p["chave"] for p in pop}
    achadas = ler_fonte(a.fonte, chaves)
    faltam = [k for k in chaves if len(achadas.get(k, [])) != 1]
    if faltam or len(chaves) != len(pop):
        print(f"FALHA: {len(faltam)} chave(s) da população sem exatamente uma linha na fonte; "
              f"{len(pop) - len(chaves)} chave(s) repetida(s) na população")
        return 1
    med = medir(pop, achadas)
    with open(a.json, "w", encoding="utf-8") as fh:
        json.dump(med, fh, ensure_ascii=False, indent=2)
    print(f"auditoria do resíduo: {med['populacao']} erros · {len(med['padroes'])} padrões · "
          f"{med['padroes_que_passam']} passam · chaves na fonte {len(chaves)}/{len(chaves)} → {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
