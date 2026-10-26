"""A genealogia em duas figuras (decisão do Rafael, 23/10): o sintoma de um lado, a decisão do outro — e o recorte
de uma unidade para o estudo de caso.

A genealogia de cinco colunas da rodada (família → assinatura → mecanismo → unidade → destino) junta duas análises
diferentes. Medido nas arestas (`genealogia_arestas.csv`, ensaio da base 1 de 20/10), cada passagem tem uma forma:

- **família → assinatura é uma árvore** (cada assinatura tem uma família só): não há cruzamento a desenhar, e o censo
  vai em barras — `censo_sintomas`;
- **assinatura → mecanismo diverge e converge** (11 de 21 assinaturas se abrem em mais de uma causa; 10 de 21 causas
  recebem mais de uma assinatura): é a única passagem com cruzamento e o que o método mostra — a mesma mensagem com
  causas diferentes, a mesma causa com mensagens diferentes;
- **mecanismo → unidade só converge**, por construção (o dicionário causa → unidade do `base_pipeline`);
- **unidade → destino segue reto** (uma decisão por unidade): as duas viram uma coluna, "decisão · lição" (D4, 16/10).

Por isso a genealogia da decisão é assinatura → mecanismo → unidade · destino, pintada pela família do erro
(a cor do censo; o destino está escrito na última coluna) — `genealogia_decisao`. Com `unidade=`, ela recorta uma unidade: como cada causa vai para uma unidade só, pegar a
unidade puxa exatamente as suas causas e as assinaturas que chegam nelas, e os fluxos somam os erros dela.

Tudo lido só do `genealogia_arestas.csv` da rodada (o hash conferido com o manifesto): nenhuma rodada nova. O desenho
mora aqui, e não no `genealogia_sankey.py`, porque aquele entra no hash de código da rodada (`versoes_codigo`).
Cada função devolve (título, pergunta, como ler, limitação), o contrato do `figuras_painel.py`.

Uso, da raiz (as duas figuras da rodada, ou o recorte de uma unidade):
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/execucao/figuras_genealogia.py [--rodada <pasta>] [--unidade U_sandbox]
Não é um comando do `executar.py` porque ele também entra no hash de código: mexer nele faria a mineração específica
recusar a rodada atual.
"""
import argparse
import math
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import genealogia_sankey as gs
from paleta import COR_ERRO, GRID, INK, INK2, MUTED, cor
from execucao.figuras_painel import DESTINO, SIGNIFICADO_DESTINO, _limpar, _n, _pct, _salvar

PENDENTE = "pendente"
ARESTAS = "genealogia_arestas.csv"
STAGES = ["assinatura", "submecanismo", "unidade"]
TITULO_COLUNA = {"assinatura": "assinatura (o sintoma)", "submecanismo": "mecanismo (a causa)",
                 "unidade": "decisão · lição (unidade)"}


class GenealogiaInvalida(RuntimeError):
    """As arestas não têm a forma que o recorte supõe (uma causa em mais de uma unidade, unidade inexistente)."""


def _etapa(ar, nome):
    return ar[ar.etapa.eq(nome)].groupby(["origem", "destino"], as_index=False).erros.sum()


def _classe_destino(d):
    for chave, rotulo, _ in DESTINO:
        if str(d).startswith(chave):
            return rotulo
    return PENDENTE   # o erro sem mecanismo por falta de dado ("COMPLEMENTAR evidência")


def caminhos(ar, unidade=None):
    """Uma linha por (assinatura, mecanismo, família do erro) com a unidade, o destino e os erros. Confere que cada causa vai para
    uma unidade só (é o que deixa o recorte exato) e, com `unidade`, recorta."""
    am = (ar[ar.etapa.eq("assinatura->submecanismo")].groupby(["origem", "destino", "categoria"], as_index=False).erros.sum()
          .rename(columns={"origem": "assinatura", "destino": "submecanismo", "categoria": "familia"}))
    mu = _etapa(ar, "submecanismo->unidade")
    dup = mu.groupby("origem").destino.nunique()
    if dup.gt(1).any():
        raise GenealogiaInvalida("causa em mais de uma unidade: " + ", ".join(dup[dup.gt(1)].index))
    ud = _etapa(ar, "unidade->destino")
    if ud.groupby("origem").destino.nunique().gt(1).any():
        raise GenealogiaInvalida("unidade com mais de um destino")
    c = am.assign(unidade=am.submecanismo.map(dict(zip(mu.origem, mu.destino))))
    c["destino"] = c.unidade.map(dict(zip(ud.origem, ud.destino)))
    if c.unidade.isna().any() or c.destino.isna().any():
        raise GenealogiaInvalida("aresta assinatura → mecanismo sem unidade ou sem destino")
    if unidade is not None:
        if unidade not in set(c.unidade):
            raise GenealogiaInvalida(f"unidade {unidade} não está na rodada; há: " + ", ".join(sorted(set(c.unidade))))
        c = c[c.unidade.eq(unidade)]
    return c.reset_index(drop=True)


def censo_sintomas(ar, destino):
    """1 · O que o sistema reclama: erros por família e, dentro dela, por assinatura (barras: é uma árvore)."""
    bruto = ar[ar.etapa.eq("familia->assinatura")]
    # a categoria de cor das arestas separa o resíduo da família (o mesmo sintoma cai em duas cores): no censo, uma
    # assinatura é uma barra só, e a cor é a da categoria dominante da família
    cor_da_familia = bruto.groupby(["origem", "categoria"]).erros.sum().reset_index().sort_values(
        "erros", ascending=False).drop_duplicates("origem").set_index("origem").categoria
    e = _etapa(ar, "familia->assinatura")
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
            ax.text(0, i, f"{fam} · {_n(n)} {'erro' if n == 1 else 'erros'} ({_pct(100 * n / total, 1)})", ha="left",
                    va="center", fontsize=10, fontweight="bold", color=cor(COR_ERRO, cat))
        else:
            ax.barh(i, n, color=cor(COR_ERRO, cat), height=0.72)
            ax.text(-0.01 * por_familia.max(), i, ass, ha="right", va="center", fontsize=8.5, color=INK)
            ax.text(n + 0.006 * por_familia.max(), i, f"{_n(n)} · {_pct(100 * n / total, 1)}", ha="left", va="center",
                    fontsize=8, color=MUTED)
    ax.set_ylim(len(linhas) - 0.4, -0.8)
    ax.set_xlim(0, por_familia.max() * 1.12)
    ax.set_yticks([])
    ax.set_xlabel("erros estruturados")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: _n(v)))
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    _limpar(ax)
    ax.spines["left"].set_visible(False)
    ax.set_title(f"O que o sistema reclama: {len(por_familia)} famílias e {e.destino.nunique()} assinaturas; a maior, "
                 f"{por_familia.index[0]}, tem {_pct(100 * por_familia.iloc[0] / total, 0)} dos {_n(total)} erros",
                 loc="left", fontsize=11)
    fig.subplots_adjust(left=0.36)
    _salvar(fig, destino)
    return ("O sintoma: o que o sistema reclama (família e assinatura)",
            "De que tipo é a reclamação do sistema, e qual é exatamente?",
            "Uma barra por assinatura (o sintoma fino: o que a mensagem do erro estruturado diz), agrupadas na sua família "
            "(o grupo grosso do sintoma); a cor é a da família. Cada assinatura pertence a uma só família, então não há "
            "cruzamento a desenhar: é um censo. O comprimento da barra é o número de erros estruturados, com a fatia do "
            "total ao lado. O sintoma só descreve: a causa de cada erro (o mecanismo) e a decisão estão na genealogia da "
            "decisão, a figura seguinte.",
            "A assinatura vem só do texto da mensagem; o mesmo sintoma esconde causas diferentes, e é o mecanismo que as "
            "separa. Os erros sem texto suficiente na extração aparecem como evidência insuficiente.")


def _desenhar(EU, destino, titulo, paleta, ordem_cat):
    """O Sankey de três colunas com as peças do `genealogia_sankey` (posição, fatias, fitas, rótulos sem colisão),
    pintado pela família do erro (a mesma cor do censo e da genealogia de cinco colunas)."""
    tot, arestas, comp = gs.montar_grafo(EU, STAGES)
    ordem = gs.ordenar_colunas(tot, arestas, STAGES)
    maior = max(int(v) for col in STAGES for v in tot[col].values)
    MIN_H, PAD, PAD_PEQ, ALTURA_ROTULO, NODE_W = 0.16, 0.12, 0.2, 0.25, 0.22
    scale = 3.4 / maior
    ys, altura = gs.centralizar(gs.calcular_ys(tot, ordem, MIN_H, PAD, scale, PAD_PEQ, STAGES))
    fat = {}
    for col in STAGES:   # as fatias de cada nó, na ordem da paleta das famílias
        fat[col] = {}
        for nome in ordem[col]:
            y0, _, h = ys[col][nome]
            cont = comp[col].loc[nome]
            cur, d = y0, {}
            for c in ordem_cat + [k for k in cont.index if k not in ordem_cat]:
                if int(cont.get(c, 0)):
                    d[c] = (cur, cur + cont[c] / cont.sum() * h)
                    cur = d[c][1]
            fat[col][nome] = d
    X = {"assinatura": 0.0, "submecanismo": 4.4, "unidade": 9.3}   # o mecanismo tem rótulo longo
    fig, ax = plt.subplots(figsize=(24, max(altura + 1.6, 4.5)))
    for a, b in zip(STAGES, STAGES[1:]):
        saida = gs.dividir(a, b, arestas[(a, b)], fat[a], ordem)
        entrada = gs.dividir(b, a, arestas[(a, b)], fat[b], ordem)
        for (nome_a, nome_b, c), (y0s, y1s) in saida.items():
            y0t, y1t = entrada[(nome_b, nome_a, c)]
            ax.add_patch(mpatches.PathPatch(gs.ribbon_path(X[a] + NODE_W, y0s, y1s, X[b], y0t, y1t),
                                             facecolor=cor(paleta, c), edgecolor="none", alpha=0.42, zorder=1))
    for col in STAGES:
        nomes = ordem[col]
        centros = [(ys[col][n][0] + ys[col][n][1]) / 2 for n in nomes]
        for nome, centro, y_rot in zip(nomes, centros, gs.afastar(centros, ALTURA_ROTULO)):
            for c, (c0, c1) in fat[col][nome].items():
                ax.add_patch(mpatches.Rectangle((X[col], c0), NODE_W, c1 - c0, facecolor=cor(paleta, c),
                                                 edgecolor="white", linewidth=0.7, zorder=2))
            x_rot = X[col] + NODE_W + 0.08
            if abs(y_rot - centro) > 0.02:   # rótulo afastado do vizinho: um traço o liga ao nó
                x_rot += 0.25
                ax.plot([X[col] + NODE_W, x_rot - 0.02], [centro, y_rot], color=INK2, lw=0.6, zorder=3)
            ax.text(x_rot, y_rot, gs.rotulo(col, nome, tot), va="center", ha="left", fontsize=8.3, zorder=4,
                    bbox=dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="white", linewidth=1.2))
        ax.text(X[col] + NODE_W / 2, -0.45, TITULO_COLUNA[col], ha="center", va="bottom", fontsize=11,
                fontweight="bold", color="#333333")
    ax.set_xlim(-0.2, X["unidade"] + NODE_W + 6.2)
    ax.set_ylim(-0.7, altura + 0.6)
    ax.invert_yaxis()
    ax.axis("off")
    ax.text(0, altura + 0.25, f"Largura das fitas e altura dos nós = número de erros (não tokens), mas só acima de ≈ "
            f"{_n(max(round(MIN_H / scale, -1), 1))} erros: um nó menor é desenhado com a altura mínima, para o rótulo "
            "caber.", fontsize=9, color=INK2, va="top")
    ax.set_title(titulo, fontsize=13, fontweight="bold", pad=14, loc="left")
    presentes = [c for c in ordem_cat if EU.cat.eq(c).any()]
    ax.legend(handles=[mpatches.Patch(color=cor(paleta, c), label=c) for c in presentes], loc="upper center",
              bbox_to_anchor=(0.5, -0.01), ncol=max(math.ceil(len(presentes) / 2), 1), fontsize=9.5, frameon=False)
    fig.tight_layout()
    fig.savefig(destino, dpi=170)
    plt.close(fig)


def genealogia_decisao(ar, destino, unidade=None):
    """2 · Do sintoma à decisão: assinatura → mecanismo → unidade · destino, pintado pela família do erro (a cor do
    censo). Com `unidade`, o recorte de uma unidade (o estudo de caso)."""
    c = caminhos(ar, unidade)
    c["unidade"] = [f"{d} ({u})" if not str(d).startswith("COMPLEMENTAR") else f"pendente: {str(d).lower()}"
                    for u, d in zip(c.unidade, c.destino)]
    c["classe_destino"] = c.destino.map(_classe_destino)
    c["cat"] = c.familia
    EU = c.loc[c.index.repeat(c.erros), STAGES + ["cat"]].reset_index(drop=True)
    paleta = COR_ERRO
    ordem_cat = list(COR_ERRO)
    total, n_ass, n_mec = len(EU), EU.assinatura.nunique(), EU.submecanismo.nunique()
    abre = c.groupby("assinatura").submecanismo.nunique().gt(1).sum()
    junta = c.groupby("submecanismo").assinatura.nunique().gt(1).sum()
    if unidade is None:
        cand = int(c.erros[c.classe_destino.eq("candidata a memória")].sum())
        titulo = (f"Do sintoma à decisão: {_n(total)} erros, {n_ass} assinaturas, {n_mec} causas e "
                  f"{EU.unidade.nunique()} lições; {_pct(100 * cand / total, 0)} vão para candidata a memória  ·  "
                  "cor = família do erro")
    else:
        titulo = (f"{unidade}: {_n(total)} erros, que chegam por {n_ass} "
                  f"{'assinatura' if n_ass == 1 else 'assinaturas'} e {n_mec} {'causa' if n_mec == 1 else 'causas'}  ·  "
                  f"destino: {c.classe_destino.iloc[0]}  ·  cor = família do erro")
    _desenhar(EU, destino, titulo, paleta, ordem_cat)
    ler = ("Três colunas, e cada uma soma os erros estruturados " + ("de todas as unidades" if unidade is None
                                                                      else f"da unidade {unidade}") +
           ": a assinatura (o sintoma: o que a mensagem diz), o mecanismo (a causa: o que o agente fez de errado) e a "
           "decisão com a lição (a unidade). Entre a assinatura e o mecanismo as fitas se abrem e se juntam — a mesma "
           "mensagem com causas diferentes, a mesma causa com mensagens diferentes" +
           (f" ({abre} {'assinatura se abre' if abre == 1 else 'assinaturas se abrem'} em mais de uma causa; {junta} "
            f"{'causa recebe' if junta == 1 else 'causas recebem'} mais de uma assinatura)" if unidade is None else "") +
           "; do mecanismo para a lição as fitas só se juntam (cada causa vai para uma lição só); a lição tem um destino "
           "só. A largura das fitas e a altura dos nós são o número de erros (não tokens). Cor = a família do erro, a mesma "
           "do censo de família e assinatura: a fita mantém a cor do começo ao fim, então se vê de que família vem o "
           "que termina em cada decisão (roxo = nenhuma regra reconheceu a causa). O destino está escrito na última "
           "coluna: " + SIGNIFICADO_DESTINO + ".")
    limite = ("O destino escrito na última coluna é o da triagem desta rodada (candidata não é memória aprovada) e muda "
              "quando uma investigação muda a classificação. A cor não diz o destino, só a família do erro. Abaixo do limiar escrito na figura o nó tem a altura mínima, para o rótulo caber. "
              "A figura conta erros; a triagem decide sobre ocorrências (a cascata conta uma vez).")
    if unidade is not None:
        limite += (" O recorte mostra só os erros desta unidade: uma assinatura que também leva a outras unidades "
                   "aparece aqui só com a parte que chega nesta (a figura inteira mostra o resto).")
    nome = "Do sintoma à decisão" + (f": {unidade}" if unidade else ": assinatura → mecanismo → unidade · destino")
    return (nome, "Que mensagens chegam a cada causa, e que causas formam cada lição e o seu destino?" if unidade is None
            else f"Por que mensagens e por que causas os erros chegam a {unidade}?", ler, limite)


def gerar(pasta, unidade=None, saida=None):
    """As duas figuras da rodada (em `<rodada>/genealogia/`) ou, com `unidade`, só o recorte dela; um `.md` com o
    "como ler" ao lado de cada figura, para colar no relatório do estudo de caso."""
    from execucao.painel import ler
    import json
    pasta = Path(pasta)
    m = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
    ar = ler(pasta, m, ARESTAS)
    saida = Path(saida) if saida else pasta / "genealogia"
    saida.mkdir(parents=True, exist_ok=True)
    figuras = ([(f"genealogia_decisao_{unidade}.png", lambda d: genealogia_decisao(ar, d, unidade))] if unidade else
               [("censo_sintomas.png", lambda d: censo_sintomas(ar, d)),
                ("genealogia_decisao.png", lambda d: genealogia_decisao(ar, d))])
    md = [f"# Genealogia — base 3, rodada `{pasta.name}`" + (f", recorte `{unidade}`" if unidade else ""), "",
          f"Gerado por `execucao/figuras_genealogia.py` a partir do `{ARESTAS}` da rodada (hash conferido com o "
          "manifesto). Só contagens.", ""]
    for nome, desenhar in figuras:
        titulo, pergunta, ler_como, limite = desenhar(saida / nome)
        md += [f"## {titulo}", "", f"**Pergunta:** {pergunta}", "", f"![{titulo}]({nome})", "",
               f"**Como ler:** {ler_como}", "", f"**Limitação:** {limite}", ""]
    arq = saida / (f"genealogia_{unidade}.md" if unidade else "genealogia.md")
    arq.write_text("\n".join(md), encoding="utf-8")
    return arq


def main(argv=None):
    from execucao.painel import _rodada
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rodada", type=Path)
    p.add_argument("--unidade", help="recorta a genealogia da decisão numa unidade (ex.: U_sandbox)")
    p.add_argument("--saida", type=Path, help="pasta das figuras (padrão: <rodada>/genealogia/)")
    args = p.parse_args(argv)
    try:
        arq = gerar(_rodada(args.rodada), args.unidade, args.saida)
    except GenealogiaInvalida as e:
        print(f"GENEALOGIA NÃO GERADA: {e}")
        return 1
    print("Genealogia:", arq)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
