"""Concordância entre dois leitores (o investigador e o segundo leitor) — o número sai daqui, não do LLM.

    python concordancia.py <leitura1.csv> <leitura2.csv> [--rotulo <coluna>] [--coluna-idx idx]
                           [--lado-a-lado <tabela.md> [--mostrar <coluna> ...]] [--nula <categoria>]
                           [--registrar <confianca.json> --local <amostra | partição <id>>]

Casa as duas leituras por (exec_id, role, idx).
--rotulo       a coluna de categoria a comparar: imprime casos em comum, concordância simples e kappa de Cohen, e a
               tabela das discordâncias por par de categorias (só contagens).
--lado-a-lado  grava uma tabela Markdown com cada caso em comum e o que cada leitor disse: a coluna --rotulo (com ✓ ou
               ✗) e as colunas --mostrar (por exemplo, a lição escrita com as próprias palavras, `licao_livre`). É o
               material da decisão do pesquisador; tem `exec_id`, então fica no ambiente — a versão que sai passa
               pelo versao_para_sair.py. Sem --rotulo, só grava a tabela (a leitura aberta, que não se mede).
--nula         a categoria "não há uma lição única" do roteiro: registra a fração de casos que cada leitor pôs nela
               (o painel usa a maior das duas).
Só biblioteca padrão.
"""

import argparse, csv
from collections import Counter


def registrar(arq, chave, item):
    """Acrescenta `item` à lista `chave` do confianca.json da lição (cria se não existir). É de onde o painel
    (valor_da_licao.py) lê a confiança — por script, sem ninguém transcrever número."""
    import datetime, json, os
    d = json.load(open(arq, encoding="utf-8")) if os.path.exists(arq) else {}
    d.setdefault(chave, []).append({**item, "data": datetime.date.today().isoformat()})
    with open(arq, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)


def ler(arq, col_idx):
    with open(arq, encoding="utf-8", newline="") as fh:
        return {(r["exec_id"], r["role"], r[col_idx]): r for r in csv.DictReader(fh)}


def celula(v):
    return (v or "").replace("|", "/").replace("\n", " ").strip()


def lado_a_lado(arq, A, B, comuns, rotulo, mostrar):
    cab = ["exec_id", "papel", "idx"]
    if rotulo:
        cab += [f"{rotulo}: leitor 1", f"{rotulo}: leitor 2", ""]
    for c in mostrar:
        cab += [f"{c}: leitor 1", f"{c}: leitor 2"]
    linhas = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    # discordâncias primeiro: é onde o pesquisador precisa olhar
    ordem = sorted(comuns, key=lambda k: (bool(rotulo) and A[k][rotulo] == B[k][rotulo], k[1], k[0]))
    for k in ordem:
        a, b = A[k], B[k]
        cel = [f"`{k[0]}`", k[1], k[2]]
        if rotulo:
            cel += [celula(a[rotulo]), celula(b[rotulo]), "✓" if a[rotulo] == b[rotulo] else "✗"]
        for c in mostrar:
            cel += [celula(a.get(c)), celula(b.get(c))]
        linhas.append("| " + " | ".join(cel) + " |")
    with open(arq, "w", encoding="utf-8") as fh:
        fh.write("\n".join(linhas) + "\n")
    print(f"lado a lado: {len(comuns)} casos → {arq}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("--rotulo")
    ap.add_argument("--coluna-idx", default="idx")
    ap.add_argument("--lado-a-lado"); ap.add_argument("--mostrar", nargs="*", default=[])
    ap.add_argument("--nula")
    ap.add_argument("--registrar"); ap.add_argument("--local", default="amostra")
    x = ap.parse_args()
    if not x.rotulo and not x.lado_a_lado:
        ap.error("informe --rotulo, --lado-a-lado ou os dois")
    A, B = ler(x.a, x.coluna_idx), ler(x.b, x.coluna_idx)
    comuns = sorted(set(A) & set(B))
    if not comuns:
        print("nenhum caso em comum"); return
    if x.lado_a_lado:
        lado_a_lado(x.lado_a_lado, A, B, comuns, x.rotulo, x.mostrar)
    if not x.rotulo:
        return
    ra, rb = {k: A[k][x.rotulo] for k in comuns}, {k: B[k][x.rotulo] for k in comuns}
    iguais = sum(ra[k] == rb[k] for k in comuns)
    po = iguais / len(comuns)
    ca, cb = Counter(ra.values()), Counter(rb.values())
    pe = sum(ca[c] * cb[c] for c in set(ca) | set(cb)) / len(comuns) ** 2
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    print(f"casos em comum: {len(comuns)} · concordam: {iguais} ({po:.0%}) · kappa: {kappa:.2f}")
    nula = None
    if x.nula:
        nula = round(max(ca[x.nula], cb[x.nula]) / len(comuns), 3)
        print(f"  '{x.nula}': leitor 1 {ca[x.nula]} · leitor 2 {cb[x.nula]} (maior fração {nula:.0%})")
    if x.registrar:
        item = {"rotulo": x.rotulo, "local": x.local, "casos": len(comuns),
                "concordancia": round(po, 3), "kappa": round(kappa, 3)}
        if nula is not None:
            item["nula"] = nula
        registrar(x.registrar, "leitores", item)
    for (va, vb), n in Counter((ra[k], rb[k]) for k in comuns if ra[k] != rb[k]).most_common():
        print(f"  discordância  {va}  ×  {vb}: {n}")


if __name__ == "__main__":
    main()
