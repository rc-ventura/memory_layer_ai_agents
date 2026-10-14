"""Relatório único de uma rodada: o painel (os erros) e as taxas (o denominador do pedido A) num só documento.

As duas lógicas continuam separadas — o painel lê só a rodada; as taxas leem a rodada, a fonte e as contagens, e só
saem se a junção conferir —, e esta função as gera e consolida em `<rodada>/relatorio/relatorio.md`, com as figuras
copiadas ao lado (a pasta se lê sozinha). Se as taxas não saírem, a parte 2 diz por quê, em vez de sumir.

Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/executar.py relatorio [--rodada <pasta>] [--contagens <parquet>] [--fonte <parquet>]
"""
import argparse
from pathlib import Path
import re
import shutil
import sys

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

from execucao import painel, taxas


def _corpo(md):
    """O documento sem o título (primeira linha `# `) e com cada cabeçalho um nível abaixo."""
    linhas = md.splitlines()
    if linhas and linhas[0].startswith("# "):
        linhas = linhas[1:]
    return [("#" + l) if re.match(r"^#{1,5} ", l) else l for l in linhas]


def gerar(pasta, contagens=None, fonte=None):
    pasta = Path(pasta)
    dir_painel = painel.gerar(pasta)
    try:
        dir_taxas, motivo = taxas.gerar(pasta, contagens, fonte), None
    except taxas.TravaTaxas as e:
        dir_taxas, motivo = None, str(e)
    saida = pasta / "relatorio"
    if saida.exists():
        shutil.rmtree(saida)
    saida.mkdir()
    for d in [dir_painel, dir_taxas]:
        for png in (d.glob("*.png") if d else []):
            shutil.copy2(png, saida / png.name)
    md = [f"# Relatório — base 3, rodada `{pasta.name}`", "",
          "Dois geradores, um documento: a **parte 1** sai só da rodada (`execucao/painel.py`, hashes dos CSVs "
          "conferidos com o manifesto); a **parte 2** junta a rodada, a fonte e as contagens do pedido A "
          "(`execucao/taxas.py`, só depois de a junção conferir). Gerado por `execucao/relatorio.py`.", "",
          "# Parte 1 · Os erros: cobertura, triagem e leituras", ""]
    md += _corpo((dir_painel / "painel.md").read_text(encoding="utf-8"))
    md += ["", "# Parte 2 · Taxas e custo (denominador do pedido A)", ""]
    if dir_taxas:
        md += _corpo((dir_taxas / "taxas.md").read_text(encoding="utf-8"))
    else:
        md += [f"**Não gerada:** {motivo}.", "",
               "Sem a junção conferida, nenhuma taxa é calculada: confira as contagens com "
               "`validacao/conferir_contagens.py` e rode de novo.", ""]
    (saida / "relatorio.md").write_text("\n".join(md), encoding="utf-8")
    return saida, motivo


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rodada", type=Path)
    p.add_argument("--contagens", type=Path)
    p.add_argument("--fonte", type=Path)
    args = p.parse_args(argv)
    saida, motivo = gerar(painel._rodada(args.rodada), args.contagens, args.fonte)
    print("Relatório:", saida / "relatorio.md")
    if motivo:
        print("Parte 2 (taxas) não gerada:", motivo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
