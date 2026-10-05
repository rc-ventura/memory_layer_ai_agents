"""Monta a evidência de UM achado: escolhe os casos por regra fixa, grava o trace cru de cada um e escreve o bloco de
evidência pronto para entrar no relatório. Nenhuma afirmação de relatório fica sem isto.

    python montar_evidencia.py <pasta-da-analise> --nome <mineracao>_<achado>_<BASE_ID>
        --de <tabela, relativa a pipeline/resultados/> [--onde coluna=valor ...] [--por coluna,...]
        [--regra procedimento|primeiro-por-mes|semente] [--n 10] [--semente 20261005]
        --afirmacao "<o que o achado diz, em uma frase>" --reproduzir "<comando>" [--reproduzir "<outro>"]

Grava em pipeline/resultados/evidencia/<nome>/:
  casos.csv     os casos escolhidos (a evidência derivada, com a regra de escolha em `regra_amostra`)
  crus/         a linha inteira do trace de cada execução (via `drill_down.py evidencia <nome>`), conferida
  derivados/    a visão de cada caso, cada trecho com o caminho no cru
  origem.json   de onde veio: tabela, filtros, regra, tamanhos, afirmação, comandos
  bloco.md      o bloco de evidência para o relatório — com os exec_id completos e o recorte de cada caso
Imprime só contagens e o caminho do bloco: os identificadores vão para os arquivos, não para a tela.
O bloco tem identificador de execução: o relatório que o recebe fica no ambiente do trace (`resultados/` é
git-ignored). Para sair, use `versao_para_sair.py`.
"""

import argparse, csv, datetime, json, os, subprocess, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from amostrar import amostrar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta"); ap.add_argument("--nome", required=True); ap.add_argument("--de", required=True)
    ap.add_argument("--onde", action="append", default=[]); ap.add_argument("--por", default="")
    ap.add_argument("--regra", default="procedimento", choices=["procedimento", "primeiro-por-mes", "semente"])
    ap.add_argument("--n", type=int, default=10); ap.add_argument("--semente", type=int, default=20261005)
    ap.add_argument("--afirmacao", required=True); ap.add_argument("--reproduzir", action="append", required=True)
    a = ap.parse_args()

    pipeline = os.path.join(os.path.abspath(a.pasta), "pipeline")
    origem = os.path.join(pipeline, "resultados", a.de)
    destino = os.path.join(pipeline, "resultados", "evidencia", a.nome)
    os.makedirs(destino, exist_ok=True)

    with open(origem, encoding="utf-8", newline="") as fh:
        linhas = list(csv.DictReader(fh))
    for cond in a.onde:
        col, val = cond.split("=", 1)
        linhas = [r for r in linhas if r.get(col) == val]
    if not linhas:
        sys.exit("nenhuma linha depois dos filtros — sem evidência para montar")
    grupos = defaultdict(list)
    por = [c for c in a.por.split(",") if c]
    for r in linhas:
        grupos[tuple(r.get(c, "") for c in por)].append(r)
    casos, regras = [], set()
    for g in sorted(grupos):
        escolhidos, rotulo = amostrar(grupos[g], a.regra, a.n, a.semente)
        regras.add(rotulo)
        casos += [{**r, "regra_amostra": rotulo} for r in escolhidos]
    with open(os.path.join(destino, "casos.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(casos[0])); w.writeheader(); w.writerows(casos)

    r = subprocess.run([sys.executable, "drill_down.py", "evidencia", a.nome], cwd=pipeline,
                       capture_output=True, text=True, encoding="utf-8")
    conferencia = (r.stdout.strip().splitlines() or ["(sem saída)"])[-1]
    if r.returncode != 0:
        conferencia = "FALHOU: " + ((r.stderr.strip().splitlines() or ["?"])[-1])

    filtro = " e ".join(f"`{c}`" for c in a.onde) or "sem filtro"
    info = dict(nome=a.nome, de=a.de, onde=a.onde, por=por, regra=a.regra, n=a.n, semente=a.semente,
                populacao=len(linhas), casos=len(casos), regra_aplicada=sorted(regras), afirmacao=a.afirmacao,
                reproduzir=a.reproduzir, conferencia_dos_crus=conferencia, data=datetime.date.today().isoformat())
    with open(os.path.join(destino, "origem.json"), "w", encoding="utf-8") as fh:
        json.dump(info, fh, ensure_ascii=False, indent=2)

    rel = f"resultados/evidencia/{a.nome}"
    tem = lambda c: c in casos[0]
    cab = ["#", "exec_id", "papel", "idx"] + [c for c in ("mes", "ferramenta", "grupo", "unidade") if tem(c)] + ["recorte do trace"]
    bloco = [f"#### Evidência · `{a.nome}`", "",
             f"- **Afirmação:** {a.afirmacao}",
             "- **Reproduzir** (de dentro de `pipeline/`): " + " · ".join(f"`{c}`" for c in a.reproduzir),
             f"- **Derivada:** `resultados/{a.de}`, {filtro} → {len(linhas)} linha(s); {len(casos)} escolhida(s) pela regra "
             f"*{'; '.join(sorted(regras))}*" + (f" dentro de cada `{a.por}`" if por else "") + f" → `{rel}/casos.csv`",
             f"- **Crua:** `{rel}/crus/<exec_id>.json` (a linha inteira do trace) e `{rel}/derivados/` (a visão de cada "
             f"caso, com o caminho no cru) — {conferencia}", "",
             "| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    for i, c in enumerate(casos, 1):
        vals = [str(i), f"`{c['exec_id']}`", c["role"], c["idx"]] + [c.get(k, "") for k in cab[4:-1]]
        vals.append(f"`uv run python drill_down.py caso {c['exec_id']} {c['role']}`")
        bloco.append("| " + " | ".join(vals) + " |")
    with open(os.path.join(destino, "bloco.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(bloco) + "\n")

    print(f"evidência `{a.nome}`: população {len(linhas)} · casos {len(casos)} · {conferencia}")
    print(f"bloco para o relatório: pipeline/{rel}/bloco.md")
    sys.exit(1 if r.returncode != 0 else 0)


if __name__ == "__main__":
    main()
