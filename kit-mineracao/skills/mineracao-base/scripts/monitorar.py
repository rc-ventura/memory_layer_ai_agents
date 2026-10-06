"""O monitoramento: confere, numa base ou partição nova, cada lição ou sinal que o pesquisador decidiu monitorar, e
dispara alerta pelos gatilhos registrados. Roda no passo 0 de toda mineração, antes de qualquer outra coisa.

    python monitorar.py <pasta-da-analise> [--desde AAAA-MM] [--ate AAAA-MM] [--item <id>]

Lê `<pasta-da-analise>/monitoramento.json` (versionado: só decisões, contagens e regras, nenhum dado de caso). Para
cada item:
  - a população é uma tabela derivada desta base (`populacao`, relativa a pipeline/resultados/), filtrada (`filtro`,
    como o --onde do amostrar.py). Se a tabela não existe, diz o comando que a gera (`gerar`) e sai com 2;
  - conta erros (linhas), execuções e meses;
  - se o item tem `sub` (as regras contadas que separam as sub-lições), conta cada uma pelo testar_regra.py da skill
    mineracao-investigacao, e quantos erros nenhuma regra pega;
  - compara com a `linha_de_base` (a base onde a decisão foi tomada) e confere os `gatilhos`:
      regua           a população passa na régua da triagem (execuções ≥ n e meses ≥ m)
      frequencia      a unidade está no Pareto das ocorrências das candidatas (80%) ou aparece na maior parte dos meses
      cresce          erros ≥ fator × os da linha de base
      sub_muda        a fração de alguma sub-lição mudou mais que `delta` (absoluto) em relação à linha de base
                      (só com `min_erros` ou mais, padrão 10: com poucos erros, a proporção não diz nada)
      sem_regra       a fração de erros que nenhuma regra de `sub` pega passou de `fracao` (algo novo; também com
                      `min_erros` ou mais)
      some            nenhum erro (num sinal de harness: o conserto pode ter entrado; confirmar)
      aparece_desde   algum erro a partir do mês `mes` (num sinal dado como consertado: voltou)
Na própria base da linha de base, sem recorte, não há o que comparar: o item só é contado (é a conferência de que a
linha de base reproduz). --desde/--ate recortam os meses (`coluna_mes`) — para simular uma partição nova numa base
que já existe.
Sai com 1 se algum gatilho disparou (pare a rodada e leve o alerta ao pesquisador), 2 se faltou uma tabela, 0 se
nada disparou. Imprime só contagens e nomes. Só biblioteca padrão.
"""

import argparse, csv, json, os, re, subprocess, sys, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from amostrar import aplicar_onde   # o mesmo filtro da amostra, da evidência e das regras

TESTAR_REGRA = os.path.join(AQUI, "..", "..", "mineracao-investigacao", "scripts", "testar_regra.py")
PARETO = 0.80


def ler_csv(arq):
    with open(arq, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def recortar(linhas, col, desde, ate):
    return [r for r in linhas if (not desde or r.get(col, "") >= desde) and (not ate or r.get(col, "") <= ate)]


def contar_sub(pasta, linhas, sub):
    """{nome: n} pelas regras contadas, mais '(nenhuma regra)'. Usa o testar_regra.py (a mesma contagem da
    investigação), numa população temporária já filtrada."""
    if not linhas:
        return {s["nome"]: 0 for s in sub} | {"(nenhuma regra)": 0}
    with tempfile.TemporaryDirectory() as tmp:
        pop = os.path.join(tmp, "pop.csv")
        with open(pop, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(linhas[0].keys())); w.writeheader(); w.writerows(linhas)
        casou_algum, n = {}, {}
        for i, s in enumerate(sub):
            saida = os.path.join(tmp, f"r{i}.csv")
            cmd = [sys.executable, TESTAR_REGRA, pasta, "--populacao", pop, "--saida", saida]
            cmd += ["--regex", s["regex"], "--campo-passo", s["campo_passo"]] if "regex" in s else ["--condicao", s["condicao"]]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode:
                sys.exit(f"testar_regra falhou na sub-lição {s['nome']!r}:\n{r.stderr[-800:]}")
            res = ler_csv(saida)
            n[s["nome"]] = sum(x["casou"] == "True" for x in res)
            for x in res:
                k = (x["exec_id"], x["role"], x.get("idx"))
                casou_algum[k] = casou_algum.get(k, False) or x["casou"] == "True"
        n["(nenhuma regra)"] = sum(not v for v in casou_algum.values())
    return n


def frequencia(res, unidade):
    """Pareto + presença da unidade nesta base, como o painel das candidatas (só para unidade da triagem)."""
    arq = os.path.join(res, "candidatos_memoria.csv")
    if not os.path.exists(arq):
        return None
    cand = sorted((r for r in ler_csv(arq) if r.get("decisão") == "candidato"), key=lambda r: -int(r["ocorrências"]))
    meses_base = len({r["mes"] for r in ler_csv(os.path.join(res, "execucoes.csv"))})
    total, acum, antes = sum(int(r["ocorrências"]) for r in cand), 0, 0.0
    for r in cand:
        acum += int(r["ocorrências"])
        if r["unidade"] == unidade:
            f = [n for n, v in (("Pareto", antes < PARETO), ("presença", int(r["meses"]) > meses_base / 2)) if v]
            return " + ".join(f) or "não"
        antes = acum / total
    return "não é candidata nesta base"


def base_id(pasta):
    """O BASE_ID do base_pipeline.py, lido como texto (sem importar o pipeline)."""
    arq = os.path.join(pasta, "pipeline", "base_pipeline.py")
    m = re.search(r"^BASE_ID\s*=\s*[\"']([^\"']+)", open(arq, encoding="utf-8").read(), re.M) if os.path.exists(arq) else None
    return m.group(1) if m else None


def conferir(pasta, item, desde, ate):
    res = os.path.join(pasta, "pipeline", "resultados")
    arq = os.path.join(res, item["populacao"])
    if not os.path.exists(arq):
        print(f"  FALTA a tabela {item['populacao']}: gere com `{item.get('gerar', '?')}`")
        return None
    col = item.get("coluna_mes", "mes")
    linhas = recortar(aplicar_onde(ler_csv(arq), item.get("filtro", [])), col, desde, ate)
    erros, execs, meses = len(linhas), len({r["exec_id"] for r in linhas}), sorted({r[col] for r in linhas})
    base = item.get("linha_de_base", {})
    print(f"  agora: {erros} erros · {execs} execuções · {len(meses)} meses"
          f"{' (' + ', '.join(meses) + ')' if 0 < len(meses) <= 6 else ''}  |  linha de base ({base.get('base', '?')}): "
          f"{base.get('erros', '?')} erros · {base.get('execucoes', '?')} execuções · {base.get('meses', '?')} meses")
    sub = contar_sub(pasta, linhas, item["sub"]) if item.get("sub") else None
    if sub is not None:
        bsub = base.get("sub", {})
        print("  sub-lições: " + " · ".join(f"{k} {v}" + (f" (antes {bsub[k]})" if k in bsub else "")
                                             for k, v in sub.items()))
    alertas = []
    if base.get("base") == base_id(pasta) and not (desde or ate):
        iguais = (erros, execs, len(meses)) == (base.get("erros"), base.get("execucoes"), base.get("meses")) and \
                 all(sub[k] == v for k, v in base.get("sub", {}).items()) if sub is not None else \
                 (erros, execs, len(meses)) == (base.get("erros"), base.get("execucoes"), base.get("meses"))
        print(f"  {'ok' if iguais else 'DIVERGE'}      esta é a base da linha de base: "
              f"{'a contagem reproduz' if iguais else 'a contagem NÃO reproduz a linha de base'}")
        return [] if iguais else ["a linha de base não reproduz nesta base (o código ou a tabela mudou?)"]
    for g in item.get("gatilhos", []):
        t = g["tipo"]
        if t == "regua" and execs >= g.get("execucoes", 3) and len(meses) >= g.get("meses", 2):
            alertas.append(f"passa na régua da triagem ({execs} execuções ≥ {g.get('execucoes', 3)}, "
                           f"{len(meses)} meses ≥ {g.get('meses', 2)})")
        elif t == "frequencia" and not (desde or ate):
            f = frequencia(res, item.get("unidade", item["id"]))
            if f and f not in ("não", "não é candidata nesta base"):
                alertas.append(f"tem frequência nesta base ({f})")
        elif t == "cresce" and base.get("erros") and erros >= g.get("fator", 3) * base["erros"]:
            alertas.append(f"cresceu: {erros} erros ≥ {g.get('fator', 3)} × {base['erros']}")
        elif t == "sub_muda" and sub and erros >= g.get("min_erros", 10) and base.get("sub") and base.get("erros"):
            for k, v in base["sub"].items():
                if k in sub and abs(sub[k] / erros - v / base["erros"]) > g.get("delta", 0.3):
                    alertas.append(f"a sub-lição '{k}' mudou de peso: {v / base['erros']:.0%} → {sub[k] / erros:.0%}")
        elif t == "sem_regra" and sub and erros >= g.get("min_erros", 10) and sub["(nenhuma regra)"] / erros > g.get("fracao", 0.2):
            alertas.append(f"{sub['(nenhuma regra)']} de {erros} erros sem nenhuma regra ({sub['(nenhuma regra)'] / erros:.0%} "
                           f"> {g.get('fracao', 0.2):.0%}): algo novo")
        elif t == "some" and erros == 0:
            alertas.append("sumiu: nenhum erro (o conserto pode ter entrado; confirmar)")
        elif t == "aparece_desde":
            depois = [r for r in linhas if r.get(col, "") >= g["mes"]]
            if depois:
                alertas.append(f"voltou: {len(depois)} erros a partir de {g['mes']}")
    for a in alertas:
        print(f"  ALERTA  {a}")
    if not alertas:
        print("  ok      nenhum gatilho disparou")
    return alertas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta"); ap.add_argument("--desde"); ap.add_argument("--ate"); ap.add_argument("--item")
    x = ap.parse_args()
    pasta = os.path.abspath(x.pasta)
    arq = os.path.join(pasta, "monitoramento.json")
    if not os.path.exists(arq):
        print("sem monitoramento.json: nada monitorado nesta análise"); return
    itens = json.load(open(arq, encoding="utf-8"))["itens"]
    if x.item:
        itens = [i for i in itens if i["id"] == x.item]
    recorte = f" · meses {x.desde or '…'} a {x.ate or '…'}" if (x.desde or x.ate) else ""
    print(f"monitoramento: {len(itens)} item(ns){recorte}")
    falta, disparou = False, 0
    for it in itens:
        print(f"\n{it['id']} — {it['o_que']} [{it['tipo']}; decidido em {it['decidido_em']}: {it['decisao']}]")
        r = conferir(pasta, it, x.desde, x.ate)
        falta |= r is None
        disparou += bool(r)
    print(f"\n{disparou} item(ns) com alerta" + (" · faltam tabelas" if falta else ""))
    sys.exit(2 if falta else (1 if disparou else 0))


if __name__ == "__main__":
    main()
