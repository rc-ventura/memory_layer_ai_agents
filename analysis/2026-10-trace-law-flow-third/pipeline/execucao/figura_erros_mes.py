"""O painel de erros por mês × taxa: erros absolutos por mês (barras) e taxa de erro por passo (linha), os dois do
mesmo `taxas/taxas_por_mes.csv` da rodada. Mostra que o erro absoluto cresce e que a taxa oscila com o mix de papéis.

Era a função `painel_duplo` do `gerar_apresentacao.py` (removido com o esqueleto da apresentação); o desenho é o mesmo.
Lê o CSV só se o hash bater com o `taxas/manifesto_taxas.json`, como as outras figuras da rodada. Fica fora do hash
de código da rodada (`versoes_codigo`) e não é um comando do `executar.py`.

Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/execucao/figura_erros_mes.py [--rodada <pasta>] [--saida <arquivo.png>]
Grava em `<rodada>/taxas/painel_erros_taxa_mes.png`.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

from execucao.painel import _n, _rodada, _sha256

CSV = "taxas_por_mes.csv"
MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()
AZUL, OURO, OURO_ESCURO, TINTA = "#336fb2", "#db9d41", "#8a5a12", "#1c2d3e"


def _rotulo_mes(v):
    m = re.match(r"(\d{4})-?(\d{2})", str(v).strip())
    return f"{MESES[int(m[2]) - 1]}/{m[1][2:]}" if m else str(v)


def serie_mensal(rodada):
    """A série mensal da rodada, só se o hash do CSV bater com o manifesto das taxas."""
    pasta = Path(rodada) / "taxas"
    manifesto = pasta / "manifesto_taxas.json"
    if not manifesto.is_file() or not (pasta / CSV).is_file():
        raise SystemExit(f"{pasta}: sem {CSV} ou sem manifesto_taxas.json — rode antes: executar.py taxas")
    esperado = json.loads(manifesto.read_text(encoding="utf-8"))["artefatos"].get(CSV)
    if esperado is None or _sha256(pasta / CSV) != esperado:
        raise SystemExit(f"{CSV}: ausente do manifesto ou alterado depois da rodada — figura não gerada.")
    return pd.read_csv(pasta / CSV).sort_values("mes")


def painel_duplo(m, destino):
    rot = [_rotulo_mes(v) for v in m.mes]
    x = range(len(m))
    fig, a1 = plt.subplots(figsize=(10, 4.3))
    a1.bar(x, m.erros, color=AZUL, width=0.62)
    for i, v in enumerate(m.erros):
        a1.text(i, v, _n(v), ha="center", va="bottom", fontsize=8.5, color=TINTA)
    a1.set_ylabel("erros no mês (barras)", color=AZUL)
    a1.set_ylim(0, m.erros.max() * 1.18)
    a1.set_xticks(list(x), rot)
    a2 = a1.twinx()
    a2.plot(list(x), 100 * m.taxa, marker="o", color=OURO, linewidth=2)
    for i, v in enumerate(m.taxa):
        a2.annotate(f"{_n(100 * v, 1)}%", (i, 100 * v), xytext=(0, 8), textcoords="offset points", ha="center",
                    fontsize=8.5, color=OURO_ESCURO)
    a2.set_ylabel("taxa de erro por passo (linha)", color=OURO_ESCURO)
    a2.set_ylim(0, 100 * m.taxa.max() * 1.35)
    for a in (a1, a2):
        a.spines["top"].set_visible(False)
    a1.set_title("O erro absoluto cresce; a taxa oscila com o mix de papéis", fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(destino, dpi=200)
    plt.close(fig)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rodada", type=Path)
    p.add_argument("--saida", type=Path, help="arquivo .png (padrão: <rodada>/taxas/painel_erros_taxa_mes.png)")
    args = p.parse_args(argv)
    rodada = _rodada(args.rodada)
    destino = args.saida or rodada / "taxas" / "painel_erros_taxa_mes.png"
    painel_duplo(serie_mensal(rodada), destino)
    print("Painel erros × taxa por mês:", destino)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
