"""As duas figuras que separam os eixos da genealogia (decisão de 22/10): o sintoma, de um lado; a decisão, do outro.

A genealogia de cinco colunas (família → assinatura → mecanismo → unidade → destino) desenha uma corrente única, e o
método tem dois eixos paralelos: o sintoma (o que o sistema reclamou) descreve e não decide; o mecanismo (o que o
agente fez de errado) decide. Aqui saem duas figuras, as duas lidas só do `genealogia_arestas.csv` da rodada (nenhuma
rodada nova, nenhuma fonte):

- `censo_sintomas`: família e assinatura, em barras — como cada assinatura pertence a uma só família (N:1) não há
  cruzamento, e um Sankey nada diria a mais;
- `genealogia_decisao`: mecanismo → unidade · destino, no mesmo Sankey da genealogia (`genealogia_sankey.render_png`,
  a partir do mecanismo), pintado pelo destino e não pela família.

Cada função desenha uma figura e devolve (título, pergunta, como ler, limitação), o contrato do `figuras_painel.py`.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

from paleta import COR_ERRO, INK, MUTED, cor
from execucao.figuras_painel import DESTINO, _limpar, _n, _pct, _salvar

PENDENTE = "pendente"


def _etapa(ar, nome):
    return ar[ar.etapa.eq(nome)]


def censo_sintomas(ar, destino):
    """1 · O que o sistema reclama: erros por família e, dentro dela, por assinatura."""
    bruto = _etapa(ar, "familia->assinatura")
    # a categoria de cor das arestas separa o resíduo da família (o mesmo sintoma cai em duas cores): no censo, uma
    # assinatura é uma barra só, e a cor é a da categoria dominante da família
    cor_da_familia = bruto.groupby(["origem", "categoria"]).erros.sum().reset_index().sort_values(
        "erros", ascending=False).drop_duplicates("origem").set_index("origem").categoria
    e = bruto.groupby(["origem", "destino"], as_index=False).erros.sum()
    total = int(e.erros.sum())
    por_familia = e.groupby("origem").erros.sum().sort_values(ascending=False)
    linhas = []   # (família, assinatura, erros, categoria): o cabeçalho da família tem assinatura None
    for fam, n in por_familia.items():
        sub = e[e.origem.eq(fam)].sort_values("erros", ascending=False)
        linhas.append((fam, None, int(n), cor_da_familia[fam]))
        linhas += [(fam, r.destino, int(r.erros), cor_da_familia[fam]) for r in sub.itertuples()]
    fig, ax = plt.subplots(figsize=(13, 0.27 * len(linhas) + 1.8))
    for i, (fam, ass, n, cat) in enumerate(linhas):
        if ass is None:
            ax.text(0, i, f"{fam} · {_n(n)} {'erro' if n == 1 else 'erros'} ({_pct(100 * n / total, 1)})", ha="left", va="center", fontsize=10,
                    fontweight="bold", color=cor(COR_ERRO, cat))
        else:
            ax.barh(i, n, color=cor(COR_ERRO, cat), height=0.72)
            ax.text(-0.01 * por_familia.max(), i, ass, ha="right", va="center", fontsize=8.5, color=INK)
            ax.text(n + 0.006 * por_familia.max(), i, f"{_n(n)} · {_pct(100 * n / total, 1)}", ha="left", va="center",
                    fontsize=8, color=MUTED)
    ax.set_ylim(len(linhas) - 0.4, -0.8)
    ax.set_xlim(0, por_familia.max() * 1.12)
    ax.set_yticks([])
    ax.set_xlabel("erros estruturados")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: _n(v)))
    ax.grid(axis="x", color="#e1e0d9", lw=0.6)
    ax.set_axisbelow(True)
    _limpar(ax)
    ax.spines["left"].set_visible(False)
    maior = por_familia.index[0]
    n_ass = int(e.destino.nunique())
    ax.set_title(f"O que o sistema reclama: {len(por_familia)} famílias e {n_ass} assinaturas; a maior, {maior}, tem "
                 f"{_pct(100 * por_familia.iloc[0] / total, 0)} dos {_n(total)} erros", loc="left", fontsize=11)
    fig.subplots_adjust(left=0.36)
    _salvar(fig, destino)
    return ("O sintoma: o que o sistema reclama (família e assinatura)",
            "De que tipo é a reclamação do sistema, e qual é exatamente?",
            "Uma barra por assinatura (o sintoma fino: o que a mensagem de erro diz), agrupadas na sua família (o grupo "
            "grosso do sintoma); a cor é a da família. Cada assinatura pertence a uma só família, então não há cruzamento "
            "a desenhar: é um censo. O comprimento da barra é o número de erros estruturados, com a fatia do total ao lado. "
            "O sintoma só descreve — a causa de cada erro (o mecanismo) e a lição (a unidade) estão na figura da decisão.",
            "A assinatura vem só do texto da mensagem; o mesmo sintoma esconde causas diferentes, e é o mecanismo que as "
            "separa. Os erros sem texto suficiente na extração aparecem como evidência insuficiente.")


def _classe_destino(d):
    for chave, rotulo, _ in DESTINO:
        if str(d).startswith(chave):
            return rotulo
    return PENDENTE   # o erro sem mecanismo por falta de dado ("COMPLEMENTAR evidência")


def genealogia_decisao(ar, destino):
    """2 · Da causa à decisão: mecanismo → unidade · destino, pintado pelo destino."""
    import genealogia_sankey as gs
    a = _etapa(ar, "submecanismo->unidade").groupby(["origem", "destino"], as_index=False).erros.sum()
    a = a.rename(columns={"origem": "submecanismo", "destino": "unidade"})
    b = _etapa(ar, "unidade->destino").drop_duplicates("origem").set_index("origem").destino
    a["destino"] = a.unidade.map(b)
    a["cat"] = a.destino.map(_classe_destino)
    EU = a.loc[a.index.repeat(a.erros)].drop(columns="erros").reset_index(drop=True)
    paleta = {rotulo: c for _, rotulo, c in DESTINO}
    paleta[PENDENTE] = paleta.get(PENDENTE, "#b58a32")
    ordem = [rotulo for _, rotulo, _ in DESTINO]
    total, cand = len(EU), int(EU.cat.eq("candidata a memória").sum())
    n_mec, n_uni = EU.submecanismo.nunique(), EU.unidade.nunique()
    gs.render_png(EU, destino, inicio=2, paleta=paleta, ordem_cat=ordem, nomes_cat={},
                  titulo=f"Da causa à decisão: {_n(total)} erros em {n_mec} causas e {n_uni} lições; "
                         f"{_pct(100 * cand / total, 0)} vai para candidata a memória  ·  cor = destino")
    return ("A decisão: da causa à lição e ao destino",
            "Que causas formam cada lição, e para onde cada lição vai?",
            "Duas colunas, e cada uma soma todos os erros estruturados: à esquerda a causa (o mecanismo, o que o agente "
            "fez de errado), à direita a decisão e a lição (a unidade). Várias causas podem fechar na mesma lição (N:1) e "
            "cada lição tem um só destino. A largura das fitas e a altura dos nós são o número de erros (não tokens). A "
            "cor é o destino da triagem: candidata a memória, sinal de harness (erro do agente com conserto no prompt ou "
            "no ambiente), harness / infra, resíduo (falta regra), crítico, pendente (falta dado na extração). A "
            "classificação do sintoma não entra: está no censo de família e assinatura.",
            "O destino é o da triagem desta rodada (candidata não é memória aprovada) e muda quando uma investigação muda "
            "a classificação. Abaixo do limiar escrito na figura o nó tem a altura mínima, para o rótulo caber. A figura "
            "conta erros; a triagem decide sobre ocorrências (a cascata conta uma vez).")
