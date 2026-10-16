"""Figuras do painel da base 3 (parte 1 do relatório), todas calculadas dos CSVs de uma rodada (nada escrito à mão).

Cada função recebe tabelas já lidas (com hash conferido pelo painel.py), desenha uma figura e devolve
(título, pergunta, como ler, limitação) para a seção do painel.md. Títulos com número saem dos dados.
Só contagens, nomes de unidade, de papel e de motivo — nenhum identificador de execução nem texto de caso.

Regras da auditoria dos gráficos (roadmap b3 #40; decisões de 15/10 em `analysis/decisoes.md`):
- **erro é erro** nos gráficos por unidade (tokens, frequência × custo, papel × unidade, concentração): todas as
  unidades, cor da **família** com legenda, nenhuma cor, marca ou texto de destino; o destino mora só nos gráficos de
  destino (`destinos` e `unidades_destino_tipo`);
- **um insight por gráfico**: os papéis das candidatas e a contagem por unidade e mês saíram (o total por papel foi
  para a margem do papel × unidade; a contagem por mês, para o painel esquerdo da taxa por unidade e mês, na parte 2);
- números em pt-BR, nome da lição com o identificador entre parênteses, hipótese escrita como hipótese.
"""
import math

import matplotlib
matplotlib.use("Agg")
from matplotlib.colors import LogNorm
from matplotlib.ticker import FuncFormatter, LogLocator
from matplotlib.transforms import Bbox
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import base_pipeline as bp
from paleta import BASE, BLUE, COR_ERRO, GRID, INK, INK2, MUTED, ORANGE, RESIDUO, cor

SEM_UNIDADE = "sem unidade (pendente)"   # = mineracao_observada.SEM_UNIDADE (sem importar o módulo da rodada)

# Cores e nomes de destino: só nos gráficos de destino. Cinzas e azuis não se repetem entre faixas (a auditoria
# achou harness/infra, sem recorrência e crítico confundidos).
DESTINO = [("candidato observado", "candidata a memória", BLUE),
           (bp.SINAL_HARNESS, "sinal de harness", ORANGE),
           ("não-memória", "harness / infra (não vira memória)", INK2),
           ("investigar — crítico", "crítico (limite de passos)", "#7a4a2a"),
           ("revisar", "resíduo (nenhuma regra reconheceu a causa)", RESIDUO),
           ("recorrência não demonstrada", "poucas execuções ou meses (sem recorrência)", "#1baf7a"),
           ("pendente", "pendente (faltou dado na extração)", "#b58a32")]

# Mapa de exibição do nome do papel (decidido em 15/10): só o rótulo; a chave da junção e os hashes não mudam.
# "ontestacaoCivel" é o ContestacaoCivel com o C cortado pelo regex que gera o nome na origem.
NOME_PAPEL = {"ontestacaoCivel": "ContestacaoCivel"}

# Cores por papel (gráfico de concentração): vivas, uma por papel, sem relação com as famílias.
CORES_PAPEL = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]


def _n(v, casas=0):
    s = f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(v, casas=1):
    """Percentual com "<0,1%" no lugar de um zero que não é zero."""
    if v > 0 and round(v, casas) == 0:
        return f"<{_n(10 ** -casas, casas)}%"
    return f"{_n(v, casas)}%"


def _tok(v):
    """Tokens em mi; acima de 1.000 mi, em bi."""
    return f"{_n(v / 1e9, 2)} bi" if v >= 1e9 else f"{_n(v / 1e6, 1)} mi"


def papel(nome):
    return NOME_PAPEL.get(nome, nome)


def unidade(u, quebra=False):
    """Nome da lição com o identificador entre parênteses."""
    if u == SEM_UNIDADE:
        return "Sem unidade: pendente (falta dado)"
    nome = bp.UNI[u][0] if u in bp.UNI else u
    return f"{nome}\n({u})" if quebra else f"{nome} ({u})"


def refs_tamanho(maximo):
    """Três referências redondas (1 algarismo) para a legenda de tamanho: o máximo, a metade e um décimo."""
    def redondo(v):
        if v <= 0:
            return 0
        e = 10 ** math.floor(math.log10(v))
        return round(v / e) * e
    return sorted({redondo(maximo), redondo(maximo / 2), redondo(maximo / 10)} - {0}, reverse=True)


def _milhar(ax, eixo="x"):
    f = FuncFormatter(lambda v, _: _n(v))
    (ax.xaxis if eixo == "x" else ax.yaxis).set_major_formatter(f)


def _limpar(ax):
    for lado in ["top", "right"]:
        ax.spines[lado].set_visible(False)


def _cor_unidade(u, familia):
    return cor(COR_ERRO, bp.categoria_do_erro(familia, u))


def _legenda_familias(ax, unidades_familias, **kw):
    cats = []
    for u, f in unidades_familias:
        c = bp.categoria_do_erro(f, u)
        if c not in cats:
            cats.append(c)
    ordem = [c for c in COR_ERRO if c in cats] + [c for c in cats if c not in COR_ERRO]
    return ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=cor(COR_ERRO, c)) for c in ordem],
                     labels=ordem, title="cor = família do erro", frameon=False, fontsize=8, title_fontsize=8, **kw)


def _salvar(fig, destino):
    fig.tight_layout()
    fig.savefig(destino, dpi=150, bbox_inches="tight")
    plt.close(fig)


def rotular(ax, xs, ys, textos, raios=None, fontsize=8, cores=None):
    """Rótulos que não se sobrepõem nem cobrem as bolhas: para cada ponto, na ordem dada (o mais importante primeiro),
    tenta posições em volta dele, cada vez mais longe, e fica com a primeira livre; longe do ponto, um traço o liga.
    `raios` em pontos tipográficos (o raio da bolha); `xs`, `ys` em coordenadas dos dados."""
    fig = ax.figure
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    px = fig.dpi / 72
    raios = raios if raios is not None else [3] * len(xs)
    cores = cores if cores is not None else [INK2] * len(xs)
    caixa = ax.get_window_extent(r)
    ocupados = []
    for x, y, rp in zip(xs, ys, raios):
        cx, cy = ax.transData.transform((x, y))
        ocupados.append(Bbox.from_bounds(cx - rp * px * 0.8, cy - rp * px * 0.8, 1.6 * rp * px, 1.6 * rp * px))
    direcoes = [(1, 0.4), (1, -0.6), (-1, 0.4), (-1, -0.6), (0, 1), (0, -1.2), (1, 1), (-1, 1), (1, -1.3), (-1, -1.3)]
    for x, y, t, rp, c in zip(xs, ys, textos, raios, cores):
        colocado = None
        for dist in [rp + 3, rp + 12, rp + 24, rp + 40, rp + 60]:
            for dx, dy in direcoes:
                ox, oy = dx * dist, dy * dist
                ann = ax.annotate(t, (x, y), xytext=(ox, oy), textcoords="offset points", fontsize=fontsize, color=c,
                                  ha="left" if dx > 0 else ("right" if dx < 0 else "center"), va="center",
                                  arrowprops=(dict(arrowstyle="-", color=MUTED, lw=0.5, shrinkA=0, shrinkB=rp * 0.8)
                                              if dist > rp + 10 else None))
                bb = ann.get_window_extent(r).expanded(1.04, 1.2)
                dentro = (bb.x0 >= caixa.x0 - 40 and bb.x1 <= caixa.x1 + 140 and bb.y0 >= caixa.y0 and bb.y1 <= caixa.y1 + 20)
                if dentro and not any(bb.overlaps(o) for o in ocupados):
                    colocado = bb
                    break
                ann.remove()
            if colocado:
                break
        if colocado is None:   # sem lugar livre: fica no primeiro, o menos ruim
            ann = ax.annotate(t, (x, y), xytext=(rp + 3, 0), textcoords="offset points", fontsize=fontsize, color=c,
                              va="center")
            colocado = ann.get_window_extent(r)
        ocupados.append(colocado)


# ---------------------------------------------------------------------------------------------------------------------

def genealogia():
    """2 · A genealogia é desenhada na rodada (genealogia_sankey.py); aqui, só o texto da leitura."""
    return ("Genealogia: família → assinatura → mecanismo → unidade · destino",
            "Por que caminho cada erro chega ao seu destino — e onde os caminhos se juntam?",
            "Quatro colunas; cada uma soma todos os erros estruturados. A largura de cada fita e a altura de cada nó são o "
            "número de erros (não tokens). A cor é a família do erro, carregada de ponta a ponta (legenda embaixo): roxo = "
            "resíduo (nenhuma regra reconheceu a causa), cinzas = plataforma (harness/infra), preto = erro crítico, "
            "dourado = evidência insuficiente (pendente). Na coluna do mecanismo, o nome legível vem com o identificador "
            "entre parênteses. A última coluna junta unidade e destino, que são 1 para 1 (decisão de 16/10): \"decisão · lição "
            "(unidade)\"; o arquivo de arestas da rodada continua com as cinco colunas.",
            "Abaixo do limiar escrito na figura, o nó tem a altura mínima (para o rótulo caber) e a espessura deixa de ser "
            "volume. O destino é o da triagem desta rodada: muda quando uma investigação muda a classificação.")


def tokens_unidade(tri, cob, destino):
    """3 · Tokens dos erros por unidade — todas as unidades observáveis, cor por família, sem destino."""
    t = tri[tri.erros_observaveis.gt(0)].sort_values("tokens_n_conhecidos").reset_index(drop=True)
    obs = cob[cob.situacao_mecanismo.eq("observavel")]
    pend = cob[cob.situacao_mecanismo.eq("pendente")]
    total_tok = float(cob.tokens_n_conhecidos.sum())
    fig, ax = plt.subplots(figsize=(13, 0.42 * len(t) + 2))
    v = t.tokens_n_conhecidos.astype(float) / 1e6
    ax.barh(range(len(t)), v, color=[_cor_unidade(u, f) for u, f in zip(t.unidade, t.familia_dominante)])
    for i, (val, tok) in enumerate(zip(v, t.tokens_n_conhecidos)):
        ax.text(val, i, f"  {_n(val, 1)} mi · {_pct(100 * tok / total_tok)}", va="center", fontsize=8, color=INK2)
    ax.set_yticks(range(len(t)), [unidade(u) for u in t.unidade], fontsize=8)
    ax.set_xlim(0, v.max() * 1.25)
    ax.set_xlabel("Tokens dos passos com erro (milhões)")
    _legenda_familias(ax, zip(t.unidade, t.familia_dominante), loc="lower right")
    ax.set_title(f"Tokens dos erros por unidade: {_n(obs.erros.sum())} erros observáveis "
                 f"({_n(obs.tokens_n_conhecidos.sum() / 1e6, 1)} mi tokens); {_n(pend.erros.sum())} pendentes "
                 f"({_n(pend.tokens_n_conhecidos.sum() / 1e6, 1)} mi) ficam fora", loc="left", fontsize=11)
    _limpar(ax)
    _salvar(fig, destino)
    ausentes = int(tri.tokens_n_ausentes.sum())
    return ("Tokens dos erros por unidade",
            "Em que unidade de erro está o gasto dos passos que falharam?",
            "Uma barra por unidade, da que mais gasta para a que menos; o rótulo dá os milhões de tokens e a % sobre os "
            f"tokens de todos os erros estruturados ({_n(total_tok / 1e6, 1)} mi). A cor é a família do erro (legenda). "
            "O número é o dos tokens do passo que errou, não da recuperação depois dele: é o teto do que evitar o erro "
            "pouparia (hipótese), não economia medida. O destino de cada unidade está no gráfico de destinos.",
            f"Erros sem token conhecido não entram na soma: {_n(ausentes)} nesta rodada. Os pendentes não têm unidade "
            "(ver a cobertura).")


def papel_unidade(upt, tpp, tri, destino):
    """4 · Erros por papel × unidade — todas as unidades, com os totais nas margens."""
    u = upt[upt.unidade.ne(SEM_UNIDADE)].assign(role=lambda d: d.role.map(papel))
    piv = u.pivot_table(index="role", columns="unidade", values="erros", aggfunc="sum", fill_value=0)
    piv = piv.loc[piv.sum(axis=1).sort_values(ascending=False).index,
                  piv.sum(axis=0).sort_values(ascending=False).index]
    cand = tpp.assign(role=tpp.role.map(papel)).set_index(["role", "unidade"]).decisao.eq("candidato observado")
    n_l, n_c = piv.shape
    fig, ax = plt.subplots(figsize=(max(13, 0.75 * n_c + 4), 0.38 * n_l + 4.5))
    dados = piv.to_numpy().astype(float)
    im = ax.imshow(np.where(dados > 0, dados, np.nan), aspect="auto", cmap="Blues", interpolation="nearest",
                   norm=LogNorm(vmin=1, vmax=max(dados.max(), 2)))
    for i in range(n_l):
        for j in range(n_c):
            v = dados[i, j]
            if v:
                estrela = "*" if cand.get((piv.index[i], piv.columns[j]), False) else ""
                ax.text(j, i, _n(v) + estrela, ha="center", va="center", fontsize=7,
                        color="white" if v > dados.max() ** 0.6 else INK)
    # margens: total por papel à direita, total por unidade embaixo
    for i, v in enumerate(piv.sum(axis=1)):
        ax.text(n_c - 0.3, i, f"{_n(v)}", ha="left", va="center", fontsize=8, color=INK, fontweight="bold")
    for j, v in enumerate(piv.sum(axis=0)):
        ax.text(j, n_l - 0.3, f"{_n(v)}", ha="center", va="top", fontsize=7.5, color=INK, fontweight="bold", rotation=90)
    ax.text(n_c - 0.3, -0.9, "total do\npapel", ha="left", va="bottom", fontsize=8, color=INK2)
    ax.set_xticks(range(n_c), [unidade(c) for c in piv.columns], rotation=40, ha="right", fontsize=7.5)
    ax.xaxis.tick_top()
    plt.setp(ax.get_xticklabels(), rotation=40, ha="left")
    ax.set_yticks(range(n_l), piv.index, fontsize=8)
    ax.set_xlim(-0.5, n_c + 0.9)
    ax.set_ylim(n_l + 1.2, -0.5)
    ax.text(-0.5, n_l + 1.0, "total da unidade ↑", fontsize=8, color=INK2, va="bottom")
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cb.set_label("erros na célula (escala log)", fontsize=8)
    cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: _n(v)))
    for lado in ["top", "right", "bottom", "left"]:
        ax.spines[lado].set_visible(False)
    tot = piv.to_numpy().sum()
    dois = piv.sum(axis=1).head(2)
    fig.suptitle(f"Erros por papel × unidade: {_n(tot)} erros observáveis em {n_l} papéis e {n_c} unidades; "
                 f"{' e '.join(dois.index)} têm {_n(100 * dois.sum() / tot)}%\n* = a unidade recorre nesse papel "
                 "(≥ 3 execuções e ≥ 2 meses no papel)", x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    return ("Erros por papel × unidade",
            "Onde, na esteira, cada unidade de erro acontece?",
            "Uma linha por papel, uma coluna por unidade (todas as unidades observáveis, ordenadas por erros); a célula é o "
            "número de erros e a cor segue a barra de cores, em escala log (sem ela, poucas células grandes apagam as "
            "outras). À direita, o total do papel; embaixo, o total da unidade. O asterisco marca a célula em que a "
            "unidade é recorrente dentro do próprio papel (só as unidades de memória têm essa conta).",
            "Contagem, não taxa: um papel que roda mais erra mais em número. A taxa por papel está na parte 2 (papel: "
            "volume × taxa); a parcela de cada papel em cada unidade, no gráfico de concentração.")


def destinos(tri, cob, destino, gasto_total=None):
    """5 · Para onde vão os erros e os tokens (gráfico de destino: aqui a cor é o destino)."""
    linhas = []
    for chave, rotulo, c in DESTINO:
        if chave == "pendente":
            g = cob[cob.situacao_mecanismo.eq("pendente")]
            e, t, us = g.erros.sum(), g.tokens_n_conhecidos.sum(), []
        else:
            g = tri[tri.decisao.str.startswith(chave)]
            e, t, us = g.erros_observaveis.sum(), g.tokens_n_conhecidos.sum(), g.unidade.tolist()
        linhas.append((rotulo, c, float(e), float(t), us))
    tot_e, tot_t = sum(l[2] for l in linhas), sum(l[3] for l in linhas)
    # Toda decisão da triagem precisa de uma faixa: sem isto, uma decisão nova some da figura em silêncio
    # (aconteceu com o "sinal de harness" do Ajuste 17). As barras têm de somar todos os erros estruturados.
    sem_faixa = sorted(set(tri.decisao) - {d for d in tri.decisao for k, _, _ in DESTINO if d.startswith(k)})
    if sem_faixa or tot_e != float(cob.erros.sum()):
        raise ValueError(f"figura de destinos incompleta: decisões sem faixa {sem_faixa}; "
                         f"{tot_e:.0f} erros na figura × {float(cob.erros.sum()):.0f} na cobertura")
    fig, ax = plt.subplots(figsize=(12, 4.6))
    for y, (idx, total) in [(1, (2, tot_e)), (0, (3, tot_t))]:   # erros em cima, como no título
        esq = 0.0
        for rot, c, e, t, _ in linhas:
            v = (e if idx == 2 else t) / total * 100
            ax.barh(y, v, left=esq, color=c, edgecolor="white")
            if v >= 4:
                ax.text(esq + v / 2, y, f"{_n(v)}%", ha="center", va="center", color="white", fontsize=9)
            esq += v
    ax.set_yticks([1, 0], [f"erros\n({_n(tot_e)})", f"tokens dos erros\n({_tok(tot_t)})"])
    ax.set_xlim(0, 100)
    ax.set_xlabel("% de cada barra")
    linhas_leg = [l for l in linhas if l[2] > 0]   # destino sem erro nesta rodada não entra na legenda
    rotulos = []
    for rot, c, e, t, us in linhas_leg:
        extra = f" — {', '.join(us)}" if rot.startswith("sinal de harness") and us else ""
        rotulos.append(f"{rot}{extra}: {_n(e)} erros · {_tok(t)}")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, c, _, _, _ in linhas_leg], labels=rotulos, ncol=2,
              loc="upper center", bbox_to_anchor=(0.5, -0.22), frameon=False, fontsize=8)
    cand = linhas[0]
    base = (f" ({_n(100 * cand[3] / gasto_total, 1)}% do gasto total do sistema, {_tok(gasto_total)})"
            if gasto_total else "")
    ax.set_title(f"Para onde vão os erros: candidatas a memória têm {_n(cand[2] / tot_e * 100)}% dos erros e "
                 f"{_n(cand[3] / tot_t * 100)}% dos tokens dos erros{base}", loc="left", fontsize=11)
    _limpar(ax)
    _salvar(fig, destino)
    por_erro = "; ".join(f"{rot.split(' (')[0]} {_n(t / e / 1e3, 1)} mil" for rot, _, e, t, _ in linhas if e >= 100)
    return ("Para onde vão os erros e os tokens",
            "Qual parte do problema é memória, qual é harness e qual a extração não deixa ver?",
            "Duas barras de 100%: em cima os erros, embaixo os tokens dos passos com erro, divididas pelo destino da "
            "triagem (a legenda dá os absolutos de cada faixa). Uma faixa mais larga embaixo que em cima = erros mais caros "
            f"que a média. Tokens por erro (destinos com pelo menos 100 erros): {por_erro}; média "
            f"{_n(tot_t / tot_e / 1e3, 1)} mil.",
            "A base dos % de baixo são os tokens dos passos com erro, não o gasto do sistema"
            + ("" if gasto_total else " (a fatia sobre o gasto total está na parte 2)")
            + ". Tokens só do passo com erro (sem a recuperação). Candidata = recorrente o bastante para minerar, não "
              "memória aprovada; o teto de economia é hipótese, sem o custo de injetar a memória.")


def unidades_destino_tipo(tri, destino):
    """12 · Unidades por destino e tipo de memória (o gráfico de roteamento, §14.6/8.5 da base 1)."""
    grupos = [(k, r) for k, r, _ in DESTINO if k != "pendente"]
    t = tri[tri.erros_observaveis.gt(0)].copy()
    t["grupo"] = [next((r for k, r in grupos if d.startswith(k)), d) for d in t.decisao]
    ordem_g = [r for _, r in grupos if (t.grupo == r).any()]
    linhas, ys, y = [], [], 0
    for g in ordem_g:
        sub = t[t.grupo.eq(g)].sort_values("tokens_n_conhecidos", ascending=False)
        linhas.append(("grupo", g, None))
        ys.append(y)
        y += 1
        for r in sub.itertuples():
            linhas.append(("unidade", r, None))
            ys.append(y)
            y += 1
        y += 0.4
    fig, ax = plt.subplots(figsize=(13, 0.36 * y + 1.8))
    vmax = float(t.tokens_n_conhecidos.max()) / 1e6
    for (tipo, r, _), yy in zip(linhas, ys):
        if tipo == "grupo":
            ax.text(-0.01, yy, r, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=9,
                    fontweight="bold", color=INK)
            continue
        v = float(r.tokens_n_conhecidos) / 1e6
        ax.barh(yy, v, color=_cor_unidade(r.unidade, r.familia_dominante), height=0.7)
        tipo_mem = bp.UNI[r.unidade][1] if r.unidade in bp.UNI else "—"
        ax.text(v + vmax * 0.01, yy, f"{_n(v, 1)} mi · {_n(r.erros_observaveis)} {'erro' if r.erros_observaveis == 1 else 'erros'} · "
                f"{_n(r.ocorrencias_condicionais)} ocorrências · tipo: {tipo_mem}", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks([yy for (tipo, _, _), yy in zip(linhas, ys) if tipo == "unidade"],
                  [unidade(r.unidade) for tipo, r, _ in linhas if tipo == "unidade"], fontsize=8)
    ax.set_ylim(y, -1)
    ax.set_xlim(0, vmax * 1.9)
    ax.set_xlabel("Tokens dos passos com erro (milhões)")
    _legenda_familias(ax, zip(t.unidade, t.familia_dominante), loc="lower right")
    cand = t[t.decisao.eq("candidato observado")]
    tipos = cand.unidade.map(lambda u: bp.UNI[u][1]).value_counts()
    resumo = " e ".join(f"{_n(n)} {tp}" for tp, n in tipos.items())
    ax.set_title(f"Unidades por destino e tipo de memória: {_n(len(cand))} candidatas ({resumo})", loc="left",
                 fontsize=11)
    _limpar(ax)
    _salvar(fig, destino)
    return ("Unidades por destino e tipo de memória",
            "Para onde vai cada unidade, e que tipo de memória a lição seria?",
            "Uma barra por unidade, agrupada pela decisão da triagem (candidata a memória, sinal de harness, harness/infra, "
            "crítico, resíduo, sem recorrência) e ordenada por tokens dentro do grupo. A cor é a família do erro; o rótulo "
            "dá tokens, erros, ocorrências (sequências de erros da mesma unidade na execução) e o tipo da memória na régua "
            "de Hu et al. 2025 (§4): factual · ambiente, ou experiencial · estratégia.",
            "O tipo é o da lição (catálogo do pipeline), não medido no trace. Candidata é recorrência, não memória "
            "aprovada; o destino muda quando uma investigação muda a classificação.")


def frequencia_custo(tri, destino):
    """6 · Frequência × custo por erro; o tamanho é o total de tokens da unidade."""
    t = tri[tri.erros_observaveis.gt(0)].copy()
    t["tok_erro"] = t.tokens_n_conhecidos / t.erros_observaveis / 1e3
    media = t.tokens_n_conhecidos.sum() / t.erros_observaveis.sum() / 1e3
    fig, ax = plt.subplots(figsize=(12.5, 7))
    escala = 1500 / t.tokens_n_conhecidos.max()
    tam = (t.tokens_n_conhecidos * escala).clip(lower=20)
    vals = t.tok_erro.sort_values(ascending=False)
    teto = None
    if len(vals) > 1 and vals.iloc[0] > 1.5 * vals.iloc[1]:   # um ponto fora estica o eixo: corta e marca
        teto = vals.iloc[1] * 1.3
    y = t.tok_erro.clip(upper=teto) if teto else t.tok_erro
    ax.scatter(t.erros_observaveis, y, s=tam, color=[_cor_unidade(u, f) for u, f in zip(t.unidade, t.familia_dominante)],
               alpha=0.75, edgecolor="white", zorder=2)
    ax.set_xscale("log")
    ax.xaxis.set_major_locator(LogLocator(base=10))
    _milhar(ax, "x")
    ax.axhline(media, color=MUTED, ls=":", lw=1)
    ax.text(0.995, media, f"média {_n(media, 1)} mil tokens por erro ", va="bottom", ha="right", fontsize=8, color=MUTED,
            transform=ax.get_yaxis_transform())
    ax.set_xlabel("erros observáveis da unidade (escala log)")
    ax.set_ylabel("tokens por erro (mil)")
    ax.grid(color=GRID, lw=0.6, zorder=0)
    ax.set_ylim(0, (teto or t.tok_erro.max()) * 1.12)
    ax.set_xlim(t.erros_observaveis.min() / 2, t.erros_observaveis.max() * 3)
    ordem = t.assign(y=y).sort_values("tokens_n_conhecidos", ascending=False)
    textos = [(unidade(r.unidade) + (f" ▲ {_n(r.tok_erro, 1)} mil (fora da escala)" if teto and r.tok_erro > teto else ""))
              for r in ordem.itertuples()]
    rotular(ax, ordem.erros_observaveis.tolist(), ordem.y.tolist(), textos,
            raios=(np.sqrt(ordem.tokens_n_conhecidos * escala).clip(lower=np.sqrt(20)) / 2).tolist(), fontsize=7.5)
    refs = refs_tamanho(float(t.tokens_n_conhecidos.max()))
    leg1 = ax.legend(handles=[plt.scatter([], [], s=v * escala, color=BASE, edgecolor="white") for v in refs],
                     labels=[_tok(v) for v in refs], title="tamanho = tokens da unidade", loc="upper right",
                     frameon=False, fontsize=8, title_fontsize=8, labelspacing=1.6, borderpad=1)
    ax.add_artist(leg1)
    _legenda_familias(ax, zip(t.unidade, t.familia_dominante), loc="upper left")
    grandes = t[t.erros_observaveis.ge(1000)]
    caros = grandes[grandes.tok_erro.ge(1.5 * media)].sort_values("tok_erro", ascending=False)
    if len(caros):
        msg = (f"entre as unidades com ≥ 1.000 erros, só {', '.join(caros.unidade)} custa bem mais que a média por erro "
               f"({_n(caros.tok_erro.iloc[0], 1)} mil × {_n(media, 1)} mil)")
    else:
        msg = f"nenhuma unidade com ≥ 1.000 erros custa 1,5× a média por erro ({_n(media, 1)} mil)"
    ax.set_title(f"Frequência × custo por erro, nos {_n(t.erros_observaveis.sum())} erros observáveis: {msg}",
                 loc="left", fontsize=11)
    _limpar(ax)
    _salvar(fig, destino)
    return ("Frequência × custo por erro",
            "Uma unidade pesa em tokens porque é frequente ou porque cada erro é caro?",
            "Mais à direita = mais erros; mais alto = cada erro custa mais tokens; o tamanho da bolha é o total de tokens "
            "da unidade (erros × custo por erro), o que ela pesa no gasto. A linha pontilhada é a média dos erros "
            "observáveis (sem os pendentes). Uma unidade muito acima das outras é desenhada no teto do eixo, com o valor "
            "no rótulo. A cor é a família do erro. Hipótese, não testada: um custo alto por erro vem de o erro acontecer "
            "tarde na trajetória ou num papel de contexto grande.",
            "Custo do passo com erro, sem a recuperação. Na parte 2, a entrada domina os tokens dos passos com erro em "
            "todos os papéis (gráfico de entrada × saída); se ela cresce com a posição do passo ainda não foi medido.")


def concentracao_papel(upt, tri, destino, cores=len(CORES_PAPEL)):
    """7 · Em quantos papéis cai cada unidade — todas as unidades, uma cor por papel."""
    u = upt[upt.unidade.ne(SEM_UNIDADE)].assign(role=lambda d: d.role.map(papel))
    ordem_u = u.groupby("unidade").erros.sum().sort_values(ascending=False).index.tolist()
    papeis_cor = u.groupby("role").erros.sum().sort_values(ascending=False).index[:cores].tolist()
    cor_p = dict(zip(papeis_cor, CORES_PAPEL))
    fig, ax = plt.subplots(figsize=(13, 0.5 * len(ordem_u) + 2.4))
    um_papel = 0
    for y, un in enumerate(ordem_u):
        p = u[u.unidade.eq(un)].sort_values("erros", ascending=False)
        tot = p.erros.sum()
        esq = 0.0
        for r in p[p.role.isin(papeis_cor)].itertuples():
            v = r.erros / tot * 100
            ax.barh(y, v, left=esq, color=cor_p[r.role], edgecolor="white")
            rot = f"{r.role} {_n(v)}%"
            if v >= 1.25 * len(rot):
                ax.text(esq + v / 2, y, rot, ha="center", va="center", color="white", fontsize=7.5)
            elif v >= 5:
                ax.text(esq + v / 2, y, f"{_n(v)}%", ha="center", va="center", color="white", fontsize=7.5)
            esq += v
        resto = p[~p.role.isin(papeis_cor)]
        if len(resto):
            v = 100 - esq
            ax.barh(y, v, left=esq, color=BASE, edgecolor="white")
            if v >= 14:
                ax.text(esq + v / 2, y, f"demais {len(resto)} · {_n(v)}%", ha="center", va="center", fontsize=7.5,
                        color=INK2)
        acum = (p.erros.cumsum() / tot).to_numpy()
        k90 = int(np.argmax(acum >= 0.9)) + 1
        um_papel += k90 == 1
        ax.text(101, y, f"{_n(tot)} {'erro' if tot == 1 else 'erros'} · {len(p)} {'papel' if len(p) == 1 else 'papéis'} · "
                f"90% em {k90}", va="center", fontsize=8, color=INK2)
    ax.set_yticks(range(len(ordem_u)), [unidade(x) for x in ordem_u], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 132)
    ax.set_xticks(range(0, 101, 25))
    ax.set_xlabel("% dos erros da unidade (linhas ordenadas por erros)")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=cor_p[p]) for p in papeis_cor] +
              [plt.Rectangle((0, 0), 1, 1, color=BASE)], labels=papeis_cor + ["demais papéis"], ncol=4, fontsize=8,
              frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.04 - 0.6 / (0.5 * len(ordem_u) + 2.4)))
    ax.set_title(f"Em quantos papéis cai cada unidade: em {um_papel} das {len(ordem_u)} unidades, um papel só tem "
                 "90% dos erros", loc="left", fontsize=11)
    _limpar(ax)
    _salvar(fig, destino)
    return ("Concentração de cada unidade por papel",
            "A lição vale para todos os agentes ou para um papel específico?",
            f"Uma barra por unidade (todas, ordenadas por erros), dividida pelos papéis em que o erro aconteceu; os "
            f"{len(papeis_cor)} papéis com mais erros têm cor própria (legenda), os outros ficam em cinza. À direita, quantos "
            "papéis a unidade tem e em quantos estão 90% dos erros. Barra quase toda de uma cor = o erro cai num papel "
            "só, o que aponta para o prompt ou as ferramentas desse papel (hipótese a conferir caso a caso).",
            "Contagem, não taxa: um papel que roda mais erra mais em número. O peso de cada papel em passos está na parte 2 "
            "(papel: volume × taxa); a taxa por papel e mês é o roadmap b3 #37.")


ROTULO_DEPOIS = [("final", "o seguinte é a resposta final", "#1b4332"),
                 ("sem sinal do produtor observado – não sucesso", "segue sem erro", "#74c69d"),
                 ("erro estruturado vinculado", "novo erro da mesma cascata", "#9d0208"),
                 ("erro estruturado observado; unidade desconhecida", "novo erro, vínculo não confirmado", "#e8a0a0"),
                 ("suspeita observada", "suspeita da query", "#e9c46a"),
                 ("desconhecido", "sem passo seguinte na janela", "#d9d9d9")]
MIN_BASE_DEPOIS = 100   # abaixo disso, a linha fica em cinza: poucos erros para comparar porcentagens


def depois_do_erro(dep, tri, destino):
    """10 · O que vem depois do erro, de TODAS as unidades (decisão D5 de 16/10), com a resposta final separada do
    "segue sem erro" e, à direita, quanto da cascata repete a mesma unidade (a matriz de transição, decisão B+1)."""
    t = tri.set_index("unidade")
    d = dep.copy()
    verde = ROTULO_DEPOIS[1][0]
    d["cat"] = d.depois.where(~(d.depois.eq(verde) & d.proximo_final_observado.astype(str).eq("True")), "final")
    tot_u = d.groupby("unidade").erros.sum().sort_values(ascending=False)
    us = tot_u.index.tolist()
    fig, ax = plt.subplots(figsize=(13.5, 0.62 * len(us) + 2.6))
    for y, u in enumerate(us):
        g = d[d.unidade.eq(u)]
        cats = g.groupby("cat").erros.sum()
        tot = tot_u[u]
        esq = 0.0
        for chave, _, cr in ROTULO_DEPOIS:
            v = cats.get(chave, 0) / tot * 100
            ax.barh(y, v, left=esq, color=cr, edgecolor="white")
            if v >= 4:
                ax.text(esq + v / 2, y, f"{_n(v)}%", ha="center", va="center", fontsize=7.5,
                        color=INK if cr in ("#74c69d", "#e8a0a0", "#e9c46a", "#d9d9d9") else "white")
            esq += v
        casc = (cats.get(ROTULO_DEPOIS[2][0], 0) + cats.get(ROTULO_DEPOIS[3][0], 0)) / tot * 100
        vinc = g[g.depois.eq(ROTULO_DEPOIS[2][0])].groupby("unidade_seguinte").erros.sum()
        txt = f"novo erro: {_n(casc)}%"
        if vinc.sum():
            txt += f" · a mesma unidade: {_n(100 * vinc.get(u, 0) / tot)}%"
            outras = vinc.drop(u, errors="ignore").sort_values(ascending=False)
            if len(outras) and outras.iloc[0] > 0:
                txt += f" · outra mais comum: {outras.index[0]} ({_n(100 * outras.iloc[0] / tot)}%)"
        ax.text(101, y, txt, va="center", fontsize=7.5, color=INK2)
    rot = []
    for u in us:
        base = f"{_n(tot_u[u])} {'erro' if tot_u[u] == 1 else 'erros'}"
        if u in t.index:
            base += f" · {_n(t.loc[u, 'execucoes'])} execuções · {_n(t.loc[u, 'ocorrencias_condicionais'])} ocorrências"
        rot.append(f"{unidade(u)}\n{base}")
    ax.set_yticks(range(len(us)), rot, fontsize=7.5)
    for lab, u in zip(ax.get_yticklabels(), us):
        if tot_u[u] < MIN_BASE_DEPOIS:
            lab.set_color(MUTED)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 25))
    ax.set_xlabel("% dos erros da unidade, pelo que acontece no passo seguinte")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in ROTULO_DEPOIS],
              labels=[r for _, r, _ in ROTULO_DEPOIS], ncol=3, fontsize=8, frameon=False,
              loc="lower left", bbox_to_anchor=(0, 1.0))
    ax.set_title("O que vem no passo seguinte ao erro, por unidade (todas)", loc="left", fontsize=11, pad=42)
    for lado in ["top", "right"]:
        ax.spines[lado].set_visible(False)
    _salvar(fig, destino)
    return ("O que vem depois do erro",
            "O agente se corrige no passo seguinte, entrega a resposta ou entra em cascata — e, quando erra de novo, "
            "repete o mesmo erro ou cai em outro?",
            "Uma barra por unidade (todas, inclusive sinal de harness, harness/infra, resíduo e os pendentes), somando 100% "
            "dos erros dela. Verde-escuro: o passo seguinte é a resposta final; verde-claro: é outro passo de trabalho, sem "
            "erro; vermelho-escuro e rosa: o passo seguinte também erra (a cascata é a soma dos dois, escrita à direita). "
            "À direita também: quanto dos erros é seguido por um erro da **mesma** unidade (o agente repete o erro) e qual "
            "**outra** unidade vem com mais frequência (o agente conserta e esbarra no próximo) — só quando o vínculo entre "
            "os dois erros está confirmado. Cada linha traz o tamanho da base: erros, execuções e ocorrências "
            f"(sequências de erros da mesma unidade na execução); menos de {MIN_BASE_DEPOIS} erros, nome em cinza. "
            "Hipótese, não testada: muita repetição da mesma unidade = o agente não aprende com a mensagem de erro.",
            "\"Segue sem erro\" e \"resposta final\" não são sucesso: a qualidade da resposta não está no arquivo. Só o "
            "passo seguinte (a janela vai até dois). A sequência entre dois erros não prova que um causou o outro. A "
            "matriz inteira (unidade → unidade seguinte) está em `consolidacao_depois_unidade.csv`.")


def depois_de_perfis(perfis):
    """Rodadas antigas (sem `consolidacao_depois_unidade.csv`): a mesma tabela, só das candidatas, a partir dos perfis."""
    linhas = [c.assign(unidade=u) for u, c in perfis.items()]
    d = pd.concat(linhas, ignore_index=True)
    d["proximo_final_observado"] = d.proximo_final_observado.astype(str).str.capitalize()
    d["unidade_seguinte"] = "não medida (rodada antiga)"
    return d.groupby(["unidade", "depois", "proximo_final_observado", "unidade_seguinte"]).size().rename("erros").reset_index()


MOTIVO_RESOLVE = {
    "timeout_requer_prompt_declarado_e_codigo": "pedido B: ferramentas declaradas no prompt",
    "historico_incompleto_para_excluir_repr_colado": "pedido B: histórico",
    "predecessor_numero_ou_chamada_ambiguo": "pedido B: numeração",
    "predecessor_nao_identificado_sql": "ainda sem pedido definido",
}
CORES_MOTIVO = ["#b58a32", "#2a9d8f", "#e76f51", "#6d597a", "#264653", "#8ab17d", "#bc6c25"]


def pendentes(ppm, meses, total_erros, total_tokens, destino, topo=12):
    """11 · Onde estão os pendentes: por papel e por mês, divididos pelo motivo."""
    from execucao.painel import MOTIVO
    p = ppm.assign(motivo=ppm.motivo_evidencia.map(lambda m: MOTIVO.get(m, m)), role=ppm.role.map(papel))
    por_motivo = p.groupby(["motivo_evidencia", "motivo"]).agg(erros=("erros", "sum"),
                                                              tok=("tokens_n_conhecidos", "sum")).reset_index()
    por_motivo = por_motivo.sort_values("erros", ascending=False)
    motivos = por_motivo.motivo.tolist()
    cores = dict(zip(motivos, CORES_MOTIVO * 3))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 0.45 * (topo + 1) + 3), gridspec_kw={"width_ratios": [1.2, 1]})
    por_papel = p.pivot_table(index="role", columns="motivo", values="erros", aggfunc="sum", fill_value=0)
    ordem = por_papel.sum(axis=1).sort_values(ascending=False).index
    demais = por_papel.loc[ordem[topo:]].sum()
    por_papel = por_papel.loc[ordem[:topo]]
    if len(ordem) > topo:
        por_papel.loc[f"demais {len(ordem) - topo} papéis"] = demais
    por_papel = por_papel.iloc[::-1]
    esq = pd.Series(0.0, index=por_papel.index)
    for m in motivos:
        if m in por_papel:
            a1.barh(por_papel.index, por_papel[m], left=esq, color=cores[m], edgecolor="white")
            esq += por_papel[m]
    for i, v in enumerate(esq):
        a1.text(v, i, f" {_n(v)}", va="center", fontsize=8, color=INK2)
    a1.set_title(f"Por papel ({topo} com mais)", loc="left", fontsize=10)
    from matplotlib.ticker import MaxNLocator
    a1.xaxis.set_major_locator(MaxNLocator(integer=True))
    a2.yaxis.set_major_locator(MaxNLocator(integer=True))
    _milhar(a1, "x")
    por_mes = (p.pivot_table(index="mes", columns="motivo", values="erros", aggfunc="sum", fill_value=0)
               .reindex(sorted(set(meses) | set(p.mes)), fill_value=0))
    base = pd.Series(0.0, index=por_mes.index)
    x = np.arange(len(por_mes))
    for m in motivos:
        if m in por_mes:
            a2.bar(x, por_mes[m], bottom=base, color=cores[m], edgecolor="white")
            base += por_mes[m]
    for i, v in enumerate(base):
        if v:
            a2.text(i, v, _n(v), ha="center", va="bottom", fontsize=8, color=INK2)
    a2.set_xticks(x, por_mes.index, rotation=45, ha="right")
    a2.set_title("Por mês", loc="left", fontsize=10)
    _milhar(a2, "y")
    total = p.erros.sum()
    rot_leg = [f"{r.motivo} — {_n(r.erros)} ({_pct(100 * r.erros / total_erros)} dos erros · {_tok(r.tok)}) → "
               f"{MOTIVO_RESOLVE.get(r.motivo_evidencia, 'a definir')}" for r in por_motivo.itertuples()]
    fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=cores[m]) for m in motivos], labels=rot_leg, ncol=1,
               fontsize=8, frameon=False, loc="upper left", bbox_to_anchor=(0.01, 0.0))
    top_p = p.groupby("role").erros.sum().sort_values(ascending=False)
    top_m = p.groupby("mes").erros.sum().sort_values(ascending=False)
    cel = p.groupby(["role", "mes"]).erros.sum().sort_values(ascending=False)
    fig.suptitle(f"Onde estão os {_n(total)} pendentes ({_pct(100 * total / total_erros)} dos erros, "
                 f"{_pct(100 * p.tokens_n_conhecidos.sum() / total_tokens)} dos tokens dos erros): "
                 f"{_n(100 * top_p.iloc[0] / total)}% no {top_p.index[0]}, {_n(100 * top_m.iloc[0] / total)}% em "
                 f"{top_m.index[0]}; a célula {cel.index[0][0]} × {cel.index[0][1]} tem {_n(100 * cel.iloc[0] / total)}%",
                 x=0.01, ha="left", fontsize=11)
    for a in (a1, a2):
        _limpar(a)
    _salvar(fig, destino)
    return ("Onde estão os pendentes",
            "Os erros que a extração não deixa classificar estão espalhados ou concentrados — e o que falta para "
            "classificá-los?",
            "À esquerda por papel, à direita por mês (os mesmos meses dos outros gráficos), cada barra dividida pelo motivo "
            "da pendência. A legenda dá o peso de cada motivo e o que o resolve. O título dá o papel, o mês e a célula "
            "papel × mês com mais pendentes.",
            "Pendente é lacuna de dado (a regra existe, faltou o dado), não resíduo. A concentração mostra onde falta dado, "
            "não a causa: pode vir de como as execuções do papel são montadas (ex.: erro no primeiro passo não tem passo "
            "anterior).")
