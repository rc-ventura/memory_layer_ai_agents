"""As duas figuras que separam os eixos da genealogia (decisão de 22/10): o sintoma, de um lado; a decisão, do outro.

A genealogia de cinco colunas (família → assinatura → mecanismo → unidade → destino) desenha uma corrente única, e o
método tem dois eixos paralelos: o sintoma (o que o sistema reclamou) descreve e não decide; o mecanismo (o que o
agente fez de errado) decide. Aqui saem duas figuras, as duas lidas só do `genealogia_arestas.csv` da rodada (nenhuma
rodada nova, nenhuma fonte):

- `censo_sintomas`: família e assinatura, em barras — como cada assinatura pertence a uma só família (N:1) não há
  cruzamento, e um Sankey nada diria a mais;
- `genealogia_decisao`: mecanismo → unidade · destino, no mesmo Sankey da genealogia (as peças de
  `genealogia_sankey`), pintado pelo destino e não pela família. O desenho mora aqui, e não em `render_png`, porque o
  `genealogia_sankey.py` entra no hash de código da rodada (`versoes_codigo`): mexer nele deixaria a rodada de 21/10
  "desatualizada" para a mineração.

Cada função desenha uma figura e devolve (título, pergunta, como ler, limitação), o contrato do `figuras_painel.py`.
"""
import math
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
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


def _fatias(col, comp, ys, ordem, ordem_cat):
    """O `fatias` do genealogia_sankey, com a ordem das categorias de quem chama (o dele usa a das famílias)."""
    saida = {}
    for nome in ordem[col]:
        y0, _, h = ys[col][nome]
        cont = comp[col].loc[nome]
        total, cur, d = cont.sum(), y0, {}
        for c in ordem_cat + [k for k in cont.index if k not in ordem_cat]:
            n = int(cont.get(c, 0))
            if n:
                d[c] = (cur, cur + n / total * h)
                cur += n / total * h
        saida[nome] = d
    return saida


def _sankey_decisao(gs, EU, out_path, paleta, ordem_cat, titulo):
    """As duas colunas, mecanismo e "decisão · lição": o corpo do `render_png`, com a cor e a ordem pelo destino."""
    EU = EU.assign(unidade=[f"{d} ({u})" if not str(d).startswith("COMPLEMENTAR") else f"pendente: {d.lower()}"
                            for u, d in zip(EU["unidade"], EU["destino"])])
    stages = ["submecanismo", "unidade"]
    tot, arestas, comp = gs.montar_grafo(EU, stages)
    ordem = gs.ordenar_colunas(tot, arestas, stages)
    maior = max(int(v) for col in stages for v in tot[col].values)
    MIN_H, PAD, PAD_PEQ, ALTURA_ROTULO, NODE_W = 0.16, 0.12, 0.2, 0.25, 0.22
    scale = 3.4 / maior
    ys, altura = gs.centralizar(gs.calcular_ys(tot, ordem, MIN_H, PAD, scale, PAD_PEQ, stages))
    fat = {col: _fatias(col, comp, ys, ordem, ordem_cat) for col in stages}
    X = {"submecanismo": 0.0, "unidade": 4.9}   # o mecanismo tem rótulo longo
    fig, ax = plt.subplots(figsize=(23, altura + 1.6))
    a, b = stages
    saida = gs.dividir(a, b, arestas[(a, b)], fat[a], ordem)
    entrada = gs.dividir(b, a, arestas[(a, b)], fat[b], ordem)
    for (nome_a, nome_b, c), (y0s, y1s) in saida.items():
        y0t, y1t = entrada[(nome_b, nome_a, c)]
        ax.add_patch(mpatches.PathPatch(gs.ribbon_path(X[a] + NODE_W, y0s, y1s, X[b], y0t, y1t),
                                         facecolor=cor(paleta, c), edgecolor="none", alpha=0.42, zorder=1))
    for col in stages:
        nomes = ordem[col]
        centros = [(ys[col][n][0] + ys[col][n][1]) / 2 for n in nomes]
        for nome, centro, y_rot in zip(nomes, centros, gs.afastar(centros, ALTURA_ROTULO)):
            for c, (c0, c1) in fat[col][nome].items():
                ax.add_patch(mpatches.Rectangle((X[col], c0), NODE_W, c1 - c0, facecolor=cor(paleta, c),
                                                 edgecolor="white", linewidth=0.7, zorder=2))
            x_rot = X[col] + NODE_W + 0.08
            if abs(y_rot - centro) > 0.02:   # rótulo afastado do vizinho: um traço o liga ao nó
                x_rot += 0.25
                ax.plot([X[col] + NODE_W, x_rot - 0.02], [centro, y_rot], color="#52514e", lw=0.6, zorder=3)
            ax.text(x_rot, y_rot, gs.rotulo(col, nome, tot), va="center", ha="left", fontsize=8.3, zorder=4,
                    bbox=dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="white", linewidth=1.2))
        ax.text(X[col] + NODE_W / 2, -0.45, "mecanismo" if col == "submecanismo" else "decisão · lição (unidade)",
                ha="center", va="bottom", fontsize=11, fontweight="bold", color="#333333")
    ax.set_xlim(-0.2, X["unidade"] + NODE_W + 5.6)
    ax.set_ylim(-0.7, altura + 0.6)
    ax.invert_yaxis()
    ax.axis("off")
    ax.text(0, altura + 0.25, f"Largura das fitas e altura dos nós = número de erros (não tokens), mas só acima de ≈ "
            f"{_n(round(0.16 / scale, -1))} erros: um nó menor é desenhado com a altura mínima, para o rótulo caber.",
            fontsize=9, color="#52514e", va="top")
    ax.set_title(titulo, fontsize=13, fontweight="bold", pad=14, loc="left")
    presentes = [c for c in ordem_cat if (EU["cat"] == c).any()]
    ax.legend(handles=[mpatches.Patch(color=cor(paleta, c), label=c) for c in presentes], loc="upper center",
              bbox_to_anchor=(0.5, -0.01), ncol=math.ceil(len(presentes) / 2), fontsize=9.5, frameon=False)
    fig.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    fig.savefig(out_path, dpi=170)
    plt.close(fig)


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
    _sankey_decisao(gs, EU, destino, paleta, ordem,
                    f"Da causa à decisão: {_n(total)} erros em {n_mec} causas e {n_uni} lições; "
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
