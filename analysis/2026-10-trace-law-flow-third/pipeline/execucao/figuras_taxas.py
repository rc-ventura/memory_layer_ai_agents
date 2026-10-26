"""Figuras das taxas da base 3 (parte 2 do relatório; roadmap b3 #32): erros e custo sobre o denominador do pedido A.

Cada função recebe tabelas já conferidas pelo `taxas.py` (a junção fonte × contagens passou), desenha uma figura e
devolve (título, pergunta, como ler, limitação) — o mesmo contrato do `figuras_painel.py`. Títulos com número saem
dos dados. Só contagens, nomes de papel, de unidade e meses: nenhum identificador de execução nem texto de caso.

Regras da auditoria dos gráficos (roadmap b3 #36; decisões de 15/10 em `analysis/decisoes.md`): nos gráficos de
volume, taxa e custo, **erro é erro** (todos os erros estruturados, sem linha, marca ou cor por destino); só o gasto de
cada papel separa por destino. A base de toda taxa está escrita no eixo e no "Como ler"; "gasto total do papel" =
todos os tokens dos passos do papel, com ou sem erro (antes chamado "orçamento"); acima de 1.000 mi, em bilhões.
"""
import matplotlib
matplotlib.use("Agg")
from matplotlib.colors import LogNorm
from matplotlib.ticker import FuncFormatter, MaxNLocator
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import base_pipeline as bp
from paleta import BASE, BLUE, GRID, INK, INK2, MUTED, ORANGE, RESIDUO
from execucao.recuperacao import CATEGORIAS
from execucao.figuras_painel import (SEM_UNIDADE, _limpar, _milhar, _n, _pct, _salvar, _tok as tok, papel as nome_papel,
                                     refs_tamanho, rotular, unidade)

MIN_N = 20         # abaixo disso, o mês ou o papel aparece em cinza: amostra pequena para uma taxa
MIN_PASSOS = 1000  # mês do sistema com menos passos: cinza e fora da escala de cor na taxa por unidade e mês (D2, 16/10)
MIN_PASSOS_PAPEL_MES = 100  # papel com menos passos no mês: cinza e fora da escala de cor na taxa por papel e mês
MES_PT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def _p(a, b, casas=1):
    return _pct(100 * a / b, casas) if b else "—"


def _mes(m):
    """'2026-01' → 'jan/26'."""
    try:
        a, mm = str(m).split("-")[:2]
        return f"{MES_PT[int(mm) - 1]}/{a[2:]}"
    except (ValueError, IndexError):
        return str(m)


def _mil(v):
    return f"{_n(v / 1e3, 1)} mil"


def funil(execs, extra, destino):
    """1 · O tamanho do problema: execuções e passos, com e sem erro."""
    n, com_erro = len(execs), int(execs.erros.gt(0).sum())
    asteps, erros = int(execs.actionsteps.sum()), int(execs.erros.sum())
    com_susp = int((execs.erros.gt(0) | execs.suspeitas.gt(0)).sum())
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 3.4))
    for ax, rot, val in [(a1, ["execuções", "com erro"], [n, com_erro]), (a2, ["passos", "com erro"], [asteps, erros])]:
        ax.barh(rot[::-1], val[::-1], color=[ORANGE, BLUE])
        for i, v in enumerate(val[::-1]):
            ax.text(v, i, " " + _n(v) + (f" ({_p(v, val[0])})" if v != val[0] else ""), va="center", fontsize=9,
                    color=INK2)
        ax.set_xlim(0, val[0] * 1.35)
        ax.xaxis.set_major_locator(MaxNLocator(4))
        _milhar(ax, "x")
        _limpar(ax)
    a1.set_title("Execuções", loc="left", fontsize=10)
    a2.set_title("Passos", loc="left", fontsize=10)
    fig.suptitle(f"{_p(com_erro, n)} das execuções têm pelo menos um erro · {_p(erros, asteps)} dos passos são erro",
                 x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    if execs.actionsteps.gt(0).all():
        passos = ("Toda execução tem ao menos um passo" + (
            f" (as {_n(extra['linhas_zero_passos'])} linhas das contagens com 0 passos são papéis dentro de execuções que "
            "têm outros papéis com passos)" if extra.get("linhas_zero_passos") else "") + ". ")
    else:
        passos = f"{_n(int(execs.actionsteps.eq(0).sum()))} execuções sem nenhum passo contam no total. "
    return ("O tamanho do problema: execuções e passos com erro",
            "Quanto do trabalho do sistema esbarra num erro estruturado?",
            "À esquerda as execuções, à direita os passos (ActionSteps), cada painel na sua escala; a barra de baixo é um "
            "subconjunto da de cima e o percentual é sobre ela. Uma execução com erro pode ter vários — "
            f"{_n(erros / com_erro, 2) if com_erro else '—'} erros por execução com erro, e {_n(asteps / n, 2)} passos por "
            "execução —, por isso os dois percentuais são diferentes.",
            "Execução = execução + agente, somando os papéis. " + passos + "Erro estruturado = levantou exceção; as "
            "suspeitas da query e as falhas silenciosas não entram. Com as suspeitas, "
            f"{_p(com_susp, n)} das execuções ({_n(com_susp)}) têm erro ou suspeita.")


def taxa_mes(mes, destino):
    """2 · A taxa de erro por mês (todos os erros: sem separar o sinal de harness)."""
    m = mes.sort_index()
    ok = m[m.execucoes.ge(MIN_N)] if m.execucoes.ge(MIN_N).any() else m
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 6.2), sharex=True, gridspec_kw={"height_ratios": [1, 1.4]})
    x = np.arange(len(m))
    a1.bar(x, m.actionsteps, color=[BASE if e < MIN_N else BLUE for e in m.execucoes])
    for i, v in enumerate(m.actionsteps):
        a1.text(i, v, _n(v), ha="center", va="bottom", fontsize=7, color=INK2)
    a1.set_ylabel("passos no mês")
    a1.set_ylim(0, m.actionsteps.max() * 1.18)
    _milhar(a1, "y")
    a2.plot(x, 100 * m.taxa, marker="o", color=ORANGE)
    for i, v in enumerate(m.taxa):
        a2.annotate(_pct(100 * v), (i, 100 * v), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=8,
                    color=INK2, bbox=dict(boxstyle="round,pad=0.1", facecolor="white", edgecolor="none"))
    a2.set_ylim(0, 100 * m.taxa.max() * 1.3)
    a2.set_ylabel("erros a cada 100 passos (%)")
    a2.set_xticks(x, [_mes(i) for i in m.index], rotation=45, ha="right")
    for ax in (a1, a2):
        _limpar(ax)
    mx = ok.taxa.max()
    picos = [i for i in ok.index if ok.taxa[i] >= mx - 0.0005]
    depois = ok[ok.index > picos[-1]]
    rot_pico = f"{_pct(100 * mx)} ({' e '.join(_mes(i) for i in picos)})"
    if len(depois) >= 2:
        mn, ult = depois.taxa.idxmin(), ok.index[-1]
        if ult != mn and ok.taxa[ult] >= 2 * ok.taxa[mn]:
            titulo = (f"A taxa de erro não cai de forma sustentada: {rot_pico} → {_pct(100 * ok.taxa[mn])} ({_mes(mn)}) "
                      f"→ {_pct(100 * ok.taxa[ult])} ({_mes(ult)})")
        else:
            titulo = f"Taxa de erro por mês: pico de {rot_pico}; {_pct(100 * ok.taxa[ult])} em {_mes(ult)}"
    else:
        titulo = f"Taxa de erro por mês: pico de {rot_pico}"
    fig.suptitle(titulo, x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    pequenos = [f"{_mes(i)} tem só {_n(v)} passos" for i, v in m.actionsteps.items() if v < MIN_PASSOS]
    aviso = (" O painel de cima mostra o tamanho de cada mês: " + "; ".join(pequenos) + " — a taxa de um mês assim muda "
             "muito com poucas execuções (os erros vêm em sequência dentro da mesma execução)." if pequenos else "")
    return ("Taxa de erro por mês",
            "Um mês com mais erros teve mais execuções ou mais erro por passo?",
            "Em cima, o volume (passos no mês); embaixo, a taxa: erros estruturados a cada 100 passos do mês (%), de "
            "qualquer destino — erro é erro. Se a barra sobe e a taxa não, foi volume; se a taxa sobe, o sistema errou "
            "mais por passo." + aviso,
            f"Mês de início da execução. Barras cinza: menos de {MIN_N} execuções no mês. A taxa mistura papéis: a queda "
            "ou a subida pode ser outro conjunto de papéis rodando (a taxa por papel e mês é o roadmap b3 #37). Os erros "
            "vêm em sequência dentro da mesma execução, então meses com poucos passos oscilam mais do que uma conta "
            "binomial sugere.")


def papel_volume(papel, destino):
    """3 · Um papel erra mais ou só roda mais? Volume × taxa."""
    p = papel[papel.actionsteps.gt(0)].copy()
    p.index = [nome_papel(i) for i in p.index]
    fig, ax = plt.subplots(figsize=(12, 6.8))
    escala = 900 / p.tokens_total.max()
    tam = (p.tokens_total * escala).clip(lower=15)
    ax.scatter(p.actionsteps, 100 * p.taxa, s=tam, color=[BASE if e < MIN_N else BLUE for e in p.execucoes],
               alpha=0.75, edgecolor="white", zorder=2)
    glob = p.erros.sum() / p.actionsteps.sum()
    ax.axhline(100 * glob, color=MUTED, linestyle=":", linewidth=1)
    ax.text(0.005, 100 * glob, f" taxa global {_pct(100 * glob)}", fontsize=8, color=MUTED, va="bottom", ha="left",
            transform=ax.get_yaxis_transform())
    ax.set_xscale("log")
    _milhar(ax, "x")
    ax.set_xlabel("passos do papel (escala log)")
    ax.set_ylabel("erros a cada 100 passos do papel (%)")
    ax.grid(color=GRID, lw=0.6, zorder=0)
    ax.set_ylim(0, 100 * p.taxa.max() * 1.15)
    grandes = p[p.execucoes.ge(MIN_N)] if p.execucoes.ge(MIN_N).any() else p   # base pequena: todos
    rot = grandes.sort_values("tokens_total", ascending=False)
    rotular(ax, rot.actionsteps.tolist(), (100 * rot.taxa).tolist(),
            [f"{i} {_pct(100 * r.taxa)}" for i, r in rot.iterrows()],
            raios=(np.sqrt(tam[rot.index]) / 2).tolist(), fontsize=7.5)
    mx = float(p.tokens_total.max())
    refs = [v for v in [1e9, 1e8, 1e7] if v <= mx] or refs_tamanho(mx)
    leg = ax.legend(handles=[plt.scatter([], [], s=max(v * escala, 15), color=BLUE, alpha=0.6, edgecolor="white")
                             for v in refs], labels=[tok(v) for v in refs], title="tamanho = gasto total\ndo papel em tokens",
                    loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False, fontsize=8, title_fontsize=8,
                    labelspacing=2.0, borderpad=1)
    leg._legend_box.sep = 12
    _limpar(ax)
    alto, vol = grandes.taxa.idxmax(), grandes.actionsteps.idxmax()
    if alto != vol:
        titulo = (f"Quem erra mais por passo não é quem roda mais: {alto} erra em {_pct(100 * grandes.taxa[alto])} de "
                  f"{_n(grandes.actionsteps[alto])} passos; {vol}, em {_pct(100 * grandes.taxa[vol])} de "
                  f"{_n(grandes.actionsteps[vol])}")
    else:
        titulo = f"{alto} roda mais e erra mais por passo: {_pct(100 * grandes.taxa[alto])} de {_n(grandes.actionsteps[alto])}"
    ax.set_title(titulo, loc="left", fontsize=11)
    _salvar(fig, destino)
    acima = grandes[grandes.taxa > 2 * glob].sort_values("taxa", ascending=False)
    lista = ", ".join(f"{i} ({_pct(100 * r.taxa)})" for i, r in acima.iterrows()) or "nenhum"
    return ("Papel: volume × taxa",
            "Um papel aparece com muitos erros porque erra mais por passo ou porque roda mais?",
            "Cada ponto é um papel: à direita, os que rodam mais; acima, os que erram mais por passo (erros a cada 100 "
            "passos do papel). O tamanho é o gasto total do papel em tokens, em todos os seus passos (com ou sem erro); a "
            "área da bolha é proporcional ao gasto e a legenda dá três referências (uma bolha entre a de 100 mi e a de 1 bi "
            f"gasta algumas centenas de milhões). Rótulo em todo papel com pelo menos {MIN_N} execuções. A linha pontilhada é a taxa "
            "global do sistema (ponderada pelo volume, puxada pelos papéis grandes), não a média dos papéis. Acima do "
            f"dobro da taxa global: {lista}.",
            f"Pontos cinza: menos de {MIN_N} execuções do papel. A taxa é a do período inteiro (esconde o mês) e conta todos "
            "os erros do papel, de qualquer destino.")


def papel_mes(pm, destino, topo=8, execucoes=None):
    """3b · Erros por papel e mês: a contagem (esquerda) e a taxa do próprio papel (direita) — o papel fixo (roadmap #37).

    Cada linha traz, no rótulo, a fatia dos erros e a fatia dos passos do papel: concentrado de verdade é o papel que
    tem mais erro do que passo, e a taxa do período. Entram os `topo` papéis com mais erros e, se `execucoes` (por papel)
    vier, também os que erram mais de 2× a taxa global em pelo menos MIN_N execuções, mesmo com poucos erros (o que erra
    muito por passo e roda pouco não pode sumir em "demais"). Escala de cor linear (não log)."""
    d = pm.assign(papel=pm.papel.map(nome_papel))
    er = d.pivot_table(index="papel", columns="mes", values="erros", aggfunc="sum", fill_value=0)
    pa = d.pivot_table(index="papel", columns="mes", values="actionsteps", aggfunc="sum", fill_value=0)
    meses = sorted(er.columns)
    er, pa = er.reindex(columns=meses, fill_value=0), pa.reindex(er.index).reindex(columns=meses, fill_value=0)
    ordem = er.sum(axis=1).sort_values(ascending=False).index.tolist()
    er_t, pa_t = er.sum().sum(), pa.sum().sum()
    taxa_p = er.sum(axis=1) / pa.sum(axis=1).where(pa.sum(axis=1).gt(0))
    alto = []
    if execucoes is not None:
        ex = execucoes.rename(index=nome_papel)
        alto = [n for n in ordem[topo:] if ex.get(n, 0) >= MIN_N and taxa_p[n] > 2 * er_t / pa_t]
    fica = [n for n in ordem if n in ordem[:topo] or n in alto]
    resto = [n for n in ordem if n not in fica]
    linhas = er.loc[fica].copy(), pa.loc[fica].copy()
    nomes = list(fica)
    if resto:
        linhas[0].loc[f"demais {len(resto)} papéis"] = er.loc[resto].sum()
        linhas[1].loc[f"demais {len(resto)} papéis"] = pa.loc[resto].sum()
        nomes.append(f"demais {len(resto)} papéis")
    ce, cp = linhas
    ce.loc["todos os papéis"], cp.loc["todos os papéis"] = er.sum(), pa.sum()
    nomes.append("todos os papéis")
    taxa = 100 * ce / cp.where(cp.gt(0))
    pouco = (cp < MIN_PASSOS_PAPEL_MES).to_numpy()
    n_l, n_c = ce.shape
    rotulos = [n if i == n_l - 1 else
               f"{n}\n{_p(ce.loc[n].sum(), er_t, 0)} dos erros · {_p(cp.loc[n].sum(), pa_t, 0)} dos passos\n"
               f"taxa no período: {_p(ce.loc[n].sum(), cp.loc[n].sum(), 1)} de {_n(cp.loc[n].sum())} passos"
               for i, n in enumerate(nomes)]
    fig, axes = plt.subplots(1, 2, figsize=(20, 0.78 * n_l + 3.4), sharey=True)
    for ax, tab, casas, rot in [(axes[0], ce, 0, "erros (contagem)"),
                                (axes[1], taxa, 1, "% dos passos do próprio papel no mês")]:
        dados = tab.to_numpy().astype(float)
        cor = dados.copy()
        cor[-1, :] = np.nan                              # a linha do total não entra na cor
        if casas:
            cor[pouco] = np.nan                          # nem os papéis com poucos passos no mês (taxa instável)
        corpo = cor[~np.isnan(cor)]
        norm = plt.Normalize(vmin=0, vmax=float(corpo.max())) if len(corpo) and corpo.max() > 0 else None
        im = ax.imshow(np.where(np.isnan(cor), np.nan, cor), aspect="auto", cmap="Blues", interpolation="nearest",
                       norm=norm)
        for i in range(n_l):
            for j in range(n_c):
                v = dados[i, j]
                if np.isnan(v) or (not casas and v <= 0):
                    continue
                escuro = not np.isnan(cor[i, j]) and norm is not None and norm(cor[i, j]) > 0.6
                ax.text(j, i, _n(v, casas), ha="center", va="center", fontsize=8,
                        color="white" if escuro else (MUTED if (casas and pouco[i, j]) else INK),
                        fontweight="bold" if i == n_l - 1 else "normal")
        ax.axhline(n_l - 1.5, color=INK2, lw=0.8)
        ax.set_xticks(range(n_c), [_mes(m) for m in meses], fontsize=8)
        ax.set_title(rot, loc="left", fontsize=10)
        cb = fig.colorbar(im, ax=ax, orientation="horizontal", location="bottom", fraction=0.04, pad=0.08, aspect=60)
        cb.ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _, c=casas: _n(v, c)))
        cb.ax.tick_params(labelsize=7)
        cb.set_label(rot + " (escala linear)", fontsize=8)
    axes[0].set_yticks(range(n_l), rotulos, fontsize=8)
    cima = [n for n in fica[:2]]
    fe = ce.loc[cima].to_numpy().sum() / er_t
    fp = cp.loc[cima].to_numpy().sum() / pa_t
    fig.suptitle(f"Erros por papel e mês: {' e '.join(cima)} têm {_pct(100 * fe, 0)} dos erros, em {_pct(100 * fp, 0)} dos "
                 f"passos. À direita, a taxa de cada papel no mês (sem cor, número cinza: menos de {_n(MIN_PASSOS_PAPEL_MES)} "
                 "passos do papel no mês)", x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    corpo_t = taxa.loc[fica].where(~pd.DataFrame(pouco, index=taxa.index, columns=taxa.columns).loc[fica])
    if corpo_t.stack().dropna().empty:         # base pequena: nenhuma célula com passos suficientes, vale qualquer uma
        corpo_t = taxa.loc[fica]
    p_ex, m_ex = corpo_t.stack().dropna().idxmax()
    exemplo = (f"{_mes(m_ex)}, {p_ex}: {_n(ce.loc[p_ex, m_ex])} erros ÷ {_n(cp.loc[p_ex, m_ex])} passos do papel = "
               f"{_n(taxa.loc[p_ex, m_ex], 1)}%")
    sobre = [n for n in fica if ce.loc[n].sum() / er_t > 1.5 * cp.loc[n].sum() / pa_t]
    sub = [n for n in fica if ce.loc[n].sum() / er_t < 0.5 * cp.loc[n].sum() / pa_t]
    return ("Erros e taxa por papel e mês",
            "Os erros se concentram em poucos papéis e meses porque o papel erra mais por passo, ou só porque roda mais?",
            "Mesmas linhas e meses nos dois painéis. À esquerda, a contagem de erros por papel e mês; à direita, a taxa do "
            "próprio papel: erros do papel no mês ÷ passos do papel no mês — o papel fixo, que separa \"o papel errou "
            "mais\" de \"entrou um papel que erra mais\". Em cada linha, o rótulo traz a fatia dos erros e a fatia dos "
            "passos: um papel com mais erros do que passos é concentrado de verdade; com menos, só roda muito. A "
            "régua de cor é linear (não logarítmica) em cada painel: a célula com o dobro da cor tem o dobro do valor. "
            f"Exemplo: {exemplo}. Onde a contagem sobe e a taxa não, foi volume. Erros muito acima do peso em passos: "
            f"{', '.join(sobre) or 'nenhum'}; muito abaixo: {', '.join(sub) or 'nenhum'}. A última linha soma todos os papéis "
            "e, na taxa, é a taxa do sistema no mês (a do gráfico de taxa por mês).",
            "Conta todos os erros estruturados da rodada (erro é erro, de qualquer destino); o mapa papel × unidade conta só "
            f"os observáveis, por isso os totais por papel diferem um pouco. Papel com menos de {_n(MIN_PASSOS_PAPEL_MES)} "
            "passos no mês mostra o número em cinza, sem cor e fora da régua. A taxa por papel mistura prompts: se o prompt "
            "do papel mudou no meio do período, o gráfico não separa isso do agente. Associação, não causa.")


def papel_entrada(pm, destino):
    """3c · Em que mês cada papel aparece, e quanto pesa nos passos do mês (o mix) — roadmap #37, visão de contagem."""
    d = pm.assign(papel=pm.papel.map(nome_papel))
    ex = d.pivot_table(index="papel", columns="mes", values="execucoes", aggfunc="sum", fill_value=0)
    pa = d.pivot_table(index="papel", columns="mes", values="actionsteps", aggfunc="sum", fill_value=0)
    meses = sorted(ex.columns)
    ex, pa = ex.reindex(columns=meses, fill_value=0), pa.reindex(ex.index).reindex(columns=meses, fill_value=0)
    primeiro = {p: next(m for m in meses if ex.loc[p, m] > 0) for p in ex.index if ex.loc[p].sum() > 0}
    ordem = sorted(primeiro, key=lambda p: (meses.index(primeiro[p]), -ex.loc[p].sum()))
    ex, pa = ex.loc[ordem], pa.loc[ordem]
    parte = 100 * pa / pa.sum().where(pa.sum().gt(0))     # % dos passos do mês: cada coluna soma 100
    n_l, n_c = ex.shape
    fig, axes = plt.subplots(1, 2, figsize=(20, 0.5 * n_l + 3.4), sharey=True)
    for ax, tab, casas, rot, log in [(axes[0], ex, 0, "execuções do papel no mês (contagem)", True),
                                     (axes[1], parte, 0, "% dos passos do mês (cada coluna soma 100%)", False)]:
        dados = tab.to_numpy().astype(float)
        cor = np.where(dados > 0, dados, np.nan)
        pos = cor[~np.isnan(cor)]
        norm = (LogNorm(vmin=pos.min(), vmax=pos.max()) if log and len(pos) and pos.max() > pos.min()
                else plt.Normalize(vmin=0, vmax=float(pos.max())) if len(pos) else None)
        im = ax.imshow(cor, aspect="auto", cmap="Blues", interpolation="nearest", norm=norm)
        for i in range(n_l):
            for j in range(n_c):
                v = dados[i, j]
                if np.isnan(v) or v <= 0:
                    continue
                txt = "<1" if (not log and v < 0.5) else _n(v, casas)
                escuro = norm is not None and norm(v) > 0.65
                ax.text(j, i, txt, ha="center", va="center", fontsize=8, color="white" if escuro else INK)
        for i, p in enumerate(ordem):                   # o mês em que o papel aparece pela primeira vez
            ax.add_patch(plt.Rectangle((meses.index(primeiro[p]) - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=ORANGE, lw=2.2))
        ax.set_xticks(range(n_c), [_mes(m) for m in meses], fontsize=8)
        ax.set_title(rot, loc="left", fontsize=10)
        cb = fig.colorbar(im, ax=ax, orientation="horizontal", location="bottom", fraction=0.04, pad=0.08, aspect=60)
        cb.ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _, c=casas: _n(v, c)))
        cb.ax.tick_params(labelsize=7)
        cb.set_label(rot.split(" (")[0] + (" (escala log)" if log else " (escala linear)"), fontsize=8)
    axes[0].set_yticks(range(n_l), [f"{p}\nprimeira vez em {_mes(primeiro[p])} · {_n(ex.loc[p].sum())} execuções"
                                   for p in ordem], fontsize=8)
    desde = [p for p in ordem if primeiro[p] == meses[0]]
    depois = [p for p in ordem if primeiro[p] != meses[0]]
    fig.suptitle(f"Quando cada papel aparece: {len(desde)} dos {len(ordem)} papéis já rodam em {_mes(meses[0])}"
                 + (f"; os outros {len(depois)} entram entre {_mes(primeiro[depois[0]])} e {_mes(primeiro[depois[-1]])}"
                    if depois else "") + ". Moldura laranja = primeiro mês do papel", x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    tot_mes = ex.sum()
    saltos = tot_mes.pct_change().replace([np.inf, -np.inf], np.nan)
    m_salto = saltos.idxmax() if saltos.notna().any() else meses[-1]
    novos = [p for p in depois if primeiro[p] == m_salto]
    return ("Quando cada papel aparece e o mix do mês",
            "Em que mês cada papel entra, e o mix de papéis muda de um mês para o outro?",
            "Uma linha por papel, na ordem do mês em que aparece pela primeira vez (moldura laranja), e os mesmos meses "
            "nos dois painéis. À esquerda, as execuções do papel no mês (escala log: o 1 aparece, não some ao lado dos "
            "milhares). À direita, a participação do papel nos passos do mês: cada coluna soma 100%, então a coluna é "
            "o mix daquele mês e dá para ver o papel entrar e tomar espaço dos outros. Execução = execução + agente, "
            f"com passos registrados. O maior salto de execuções entre dois meses seguidos foi em {_mes(m_salto)}"
            + (f" (entram nele: {', '.join(novos)})" if novos else "") + ".",
            "O primeiro mês é o primeiro com execução na base, não o da entrada em produção: papel que já aparece no "
            f"primeiro mês da base ({_mes(meses[0])}) pode ser mais antigo, e os meses do começo da base têm poucas "
            "execuções, então a data de entrada de um papel raro pode estar atrasada. Não traz modelo nem prompt (a base 3 "
            "não os tem): uma mudança de modelo ou de prompt no mesmo papel não aparece aqui.")


def custo_execucao(execs, custo_papel, destino):
    """4 · A execução típica com erro × sem erro, em valores reais: tokens e passos (medianas), a razão ao lado."""
    g = execs[execs.actionsteps.gt(0)].assign(com=lambda d: d.erros.gt(0))
    grupos = g.groupby("com")[["tokens_total", "actionsteps"]]
    med, media = grupos.median(), grupos.mean()
    n = g.com.value_counts()
    if not {True, False} <= set(med.index):
        raise ValueError("custo por execução: falta o grupo com ou sem erro")
    k = med.loc[True] / med.loc[False]

    def q(v):   # inteiro quando é inteiro (a mediana de passos costuma ser), senão uma casa
        return _n(v) if abs(v - round(v)) < 1e-9 else _n(v, 1)

    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
    paineis = [(axes[0], "tokens_total", "tokens por execução", lambda v: f"{_n(v)} tokens"),
               (axes[1], "actionsteps", "passos por execução", lambda v: f"{q(v)} passos")]
    for ax, col, rot, fmt in paineis:
        vals = [med.loc[False, col], med.loc[True, col]]
        ax.barh(["sem erro", "com erro"], vals, color=[BLUE, ORANGE])
        for i, grupo in enumerate([False, True]):
            razao = f"{_n(k[col], 1)}× a execução sem erro" if grupo else "execução típica sem erro"
            ax.text(vals[i], i, f"  {fmt(vals[i])}\n  {razao} · n = {_n(n[grupo])}\n  média: {fmt(media.loc[grupo, col])}",
                    va="center", fontsize=9, color=INK2, linespacing=1.45)
        ax.set_xlim(0, max(vals) * 2.3)
        ax.set_title(rot, loc="left", fontsize=10)
        if col == "tokens_total":
            ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: _n(v / 1e3)))
            ax.set_xlabel("tokens por execução (em milhares)")
        else:
            ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
            ax.set_xlabel("passos (ActionSteps) por execução")
        _limpar(ax)
    fig.suptitle(f"A execução típica com erro usa {_n(k['tokens_total'], 1)} vezes os tokens e {q(med.loc[True, 'actionsteps'])} "
                 f"passos, contra {q(med.loc[False, 'actionsteps'])}, da típica sem erro", x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    cp = custo_papel.set_index("papel")
    ok = cp[(cp.n_com_erro >= MIN_N) & (cp.n_sem_erro >= MIN_N)]
    dentro = ""
    if len(ok):
        r = (ok.mediana_tokens_com_erro / ok.mediana_tokens_sem_erro).sort_values()
        w = ok.n_com_erro.reindex(r.index)
        pond = r[w.cumsum() >= w.sum() / 2].iloc[0]
        dentro = (f" Dentro do mesmo papel (os {len(ok)} papéis com pelo menos {MIN_N} execuções em cada grupo), a razão "
                  f"de tokens vai de {_n(r.iloc[0], 1)}× a {_n(r.iloc[-1], 1)}× (mediana ponderada pelas execuções com "
                  f"erro: {_n(pond, 1)}×); a diferença para os {_n(k['tokens_total'], 1)}× do sistema é a mistura de papéis "
                  "(a execução com erro é mais frequente nos papéis caros). Por papel, em `taxas_custo_por_papel.csv`.")
    pc, ps = med.loc[True, "actionsteps"], med.loc[False, "actionsteps"]
    return ("Custo de uma execução com erro × sem erro",
            "Quanto mais tokens e mais passos usa uma execução que teve erro?",
            "Duas barras por painel, nos valores reais (o tamanho da barra é o que a execução gasta; nada normalizado). "
            "A barra é a mediana — a execução do meio de cada grupo: metade gasta menos, metade gasta mais (robusta à "
            "cauda longa: poucas execuções levam boa parte do gasto); a média de cada grupo vem escrita abaixo. A razão "
            "ao lado da barra laranja é a mediana com erro ÷ a mediana sem erro: "
            f"{_n(k['tokens_total'], 1)}× em tokens ({_n(med.loc[True, 'tokens_total'])} ÷ "
            f"{_n(med.loc[False, 'tokens_total'])}) e {_n(k['actionsteps'], 1)}× em passos ({q(pc)} ÷ {q(ps)}). Os passos "
            f"são contados inteiros: a razão dos passos é a de dois números inteiros, e mede uma diferença de {q(pc - ps)} "
            f"passo(s). n = execuções de cada grupo ({_n(n[True])} com erro, {_n(n[False])} sem). Execução = execução + "
            "agente, somando os papéis." + dentro,
            "Não é causa: uma execução longa tem mais chance de errar e custa mais de qualquer jeito. Só os passos (o "
            "planejamento não entra). \"Sem erro\" inclui as execuções só com suspeita. A média e o p90 por papel estão "
            "no CSV.")


def concentracao(execs, destino):
    """5 · O custo é dominado por poucas execuções caras? Curva de concentração (Lorenz invertida)."""
    d = execs.assign(t=execs.tokens_total.fillna(0)).sort_values("t", ascending=False)
    t, err = d.t.to_numpy(), d.erros.gt(0).to_numpy()
    acum = np.concatenate([[0], np.cumsum(t) / t.sum()])
    x = np.arange(len(t) + 1) / len(t)
    fig, ax = plt.subplots(figsize=(8, 6.4))
    ax.plot(100 * x, 100 * acum, color=BLUE)
    ax.plot([0, 100], [0, 100], color=MUTED, linestyle="--", linewidth=1)
    tops = {}
    for q, xt in [(1, 14), (10, 30)]:
        kq = max(int(q / 100 * len(t)), 1)
        v, e = acum[kq], err[:kq].mean()
        tops[q] = (v, e)
        yc = 100 * np.interp(xt / 100, x, acum)
        ax.scatter([q], [100 * v], color=ORANGE, zorder=3)
        ax.annotate(f"{q}% mais caras = {_n(100 * v)}% do gasto\n{_n(100 * e)}% dessas execuções tiveram erro\n"
                    f"(no total: {_n(100 * err.mean())}%)", (q, 100 * v),
                    xytext=(xt, yc - 12), fontsize=9, va="center",
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 102)
    ax.set_xlabel("% das execuções, da mais cara para a mais barata")
    ax.set_ylabel("% do gasto total em tokens")
    _limpar(ax)
    ax.set_title(f"Concentração de custo: as 10% mais caras das execuções levam {_n(100 * tops[10][0])}% dos tokens",
                 loc="left", fontsize=11)
    _salvar(fig, destino)
    return ("Concentração de custo",
            "O gasto total é dominado por uma cauda de execuções caras — e essas execuções têm erro?",
            "A curva soma o gasto da execução mais cara para a mais barata: cada ponto diz que as N% execuções mais caras "
            "levam tal fatia do gasto. A diagonal tracejada é o custo igual para todas; quanto mais a curva sobe cedo, "
            "mais concentrado. Nos dois pontos marcados, a % daquelas execuções (contagem, não tokens) que tiveram pelo "
            "menos um erro estruturado, comparada com a % no sistema todo: as execuções caras têm erro com mais "
            "frequência. É uma "
            "curva de concentração (uma Lorenz invertida: por somar da mais cara, fica acima da diagonal); a análise da "
            "base 1 a chama de Lorenz.",
            "Execução = execução + agente, somando os papéis; só os tokens dos passos (o planejamento não entra), com ou "
            "sem erro.")


def custo_mensal(execs, mes, destino):
    """6 · O custo por execução e a taxa de erro, mês a mês."""
    g = execs[execs.actionsteps.gt(0)].groupby("mes")
    med, n = g.tokens_total.median(), g.size()
    fig, ax = plt.subplots(figsize=(12, 4.2))
    x = np.arange(len(med))
    ax.bar(x, med, color=[BASE if v < MIN_N else BLUE for v in n], label="tokens por execução (mediana)")
    for i, (v, k) in enumerate(zip(med, n)):
        ax.text(i, v, f"{_n(v)}\nn = {_n(k)}", ha="center", va="bottom", fontsize=7, color=INK2)
    ax.set_xticks(x, [_mes(i) for i in med.index], rotation=45, ha="right")
    ax.set_ylim(0, med.max() * 1.25)
    ax.set_ylabel("tokens por execução (mediana)")
    _milhar(ax, "y")
    a2 = ax.twinx()
    taxa = 100 * mes.taxa.reindex(med.index)
    a2.plot(x, taxa, color=ORANGE, marker="o", label="erros a cada 100 passos (%)")
    a2.set_ylim(0, taxa.max() * 2.2)   # a linha fica embaixo e não cobre os rótulos das barras
    a2.set_ylabel("erros a cada 100 passos (%)", color=ORANGE)
    a2.spines["top"].set_visible(False)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = a2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=8, loc="lower left", bbox_to_anchor=(0.0, 1.06), ncol=2)
    ax.spines["top"].set_visible(False)
    ok = med[n >= MIN_N] if (n >= MIN_N).any() else med
    pico = ok.idxmax()
    depois = ok[ok.index > pico]
    partes = [f"pico de {_n(ok[pico])} em {_mes(pico)}"]
    if len(depois):
        mn = depois.idxmin()
        partes.append(f"{_n(ok[mn])} em {_mes(mn)}")
        if ok.index[-1] != mn:
            partes.append(f"{_n(ok.iloc[-1])} em {_mes(ok.index[-1])}")
    ax.set_title("Custo mediano por execução: " + ", ".join(partes[:-1]) + (" e " if len(partes) > 1 else "") + partes[-1],
                 loc="left", fontsize=11, pad=30)
    _salvar(fig, destino)
    k = n >= MIN_N
    r = float(np.corrcoef(med[k], taxa[k])[0, 1]) if k.sum() >= 3 else float("nan")
    par = ("poucos meses para medir" if np.isnan(r) else
           f"{'o custo da execução típica e a taxa de erro andam juntos' if r >= 0.5 else 'custo e taxa de erro não andam juntos'} "
           f"(correlação de {_n(r, 2)} nos {int(k.sum())} meses com pelo menos {MIN_N} execuções; n pequeno: sugere, não prova)")
    return ("Evolução mensal do custo por execução",
            "O custo por execução cai sozinho, sem memória — e anda junto com a taxa de erro?",
            "Barras: a mediana dos tokens por execução no mês (a execução do meio), com o número de execuções. Linha "
            "laranja, no eixo da direita: a taxa de erro do mesmo mês (o gráfico de taxa por mês). O que este gráfico "
            f"acrescenta é o par: {par}. Duas leituras possíveis, as duas hipóteses: o erro encarece a execução, ou uma "
            "causa comum (a mistura de papéis de cada mês) mexe nos dois; separar é o gráfico por papel e mês (roadmap b3 "
            "#37). "
            "A média por mês está em `taxas_por_mes.csv`.",
            f"Barras cinza: menos de {MIN_N} execuções. Uma mudança na mistura de papéis muda a mediana sem mudar a "
            "eficiência de nenhum deles (roadmap b3 #37). O que cai aqui é o custo por execução, não o gasto total do mês.")


def entrada_saida(papel, total_erro, destino, topo=10):
    """7 · Quanto um passo com erro gasta a mais que o passo típico do mesmo papel, e onde (entrada ou saída)."""
    q = papel[papel.erros.gt(0) & papel.actionsteps.gt(papel.erros)].copy()
    q["e_err"] = (q.tokens_erro - q.saida_erro_tok) / q.erros
    q["s_err"] = q.saida_erro_tok / q.erros
    n_ok = q.actionsteps - q.erros
    q["e_ok"] = ((q.tokens_total - q.tokens_saida) - (q.tokens_erro - q.saida_erro_tok)) / n_ok
    q["s_ok"] = (q.tokens_saida - q.saida_erro_tok) / n_ok
    q["excesso"] = ((q.e_err + q.s_err) - (q.e_ok + q.s_ok)) * q.erros
    q["entrada_err"] = (q.tokens_erro - q.saida_erro_tok) / q.tokens_erro
    p = q.sort_values("tokens_erro", ascending=False).head(topo)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 0.62 * len(p) + 2.4), sharey=True,
                                 gridspec_kw={"width_ratios": [1.3, 1]})
    y = np.arange(len(p))
    for ax, ok_col, err_col, tit in [(a1, "e_ok", "e_err", "entrada (o que o modelo lê) — tokens por passo"),
                                     (a2, "s_ok", "s_err", "saída (o que o modelo escreve) — tokens por passo")]:
        ax.barh(y - 0.2, p[ok_col], height=0.4, color=BLUE, label="passo sem erro do papel")
        ax.barh(y + 0.2, p[err_col], height=0.4, color=ORANGE, label="passo com erro")
        for yy, a, b in zip(y, p[ok_col], p[err_col]):
            ax.text(a, yy - 0.2, " " + _mil(a), va="center", fontsize=7, color=INK2)
            ax.text(b, yy + 0.2, " " + _mil(b), va="center", fontsize=7, color=INK2)
        ax.set_xlim(0, max(p[ok_col].max(), p[err_col].max()) * 1.3)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: _mil(v)))
        ax.set_title(tit, loc="left", fontsize=10)
        _limpar(ax)
    a1.set_yticks(y, [nome_papel(i) for i in p.index], fontsize=8.5)
    a1.invert_yaxis()
    a1.legend(frameon=False, fontsize=8, loc="lower right")
    # o achado: dentro do mesmo papel, o passo com erro custa quase o mesmo que o sem erro? (soma do excesso de cada
    # papel × o excesso que a média do sistema sugere)
    err_ps = papel.tokens_erro.sum() / papel.erros.sum()
    ok_ps = (papel.tokens_total.sum() - papel.tokens_erro.sum()) / (papel.actionsteps.sum() - papel.erros.sum())
    excesso_sistema = (err_ps - ok_ps) * papel.erros.sum()
    excesso_dentro = float(q.excesso.sum())
    if abs(excesso_dentro) < 0.25 * abs(excesso_sistema):
        titulo = (f"Dentro do mesmo papel, o passo com erro custa quase o mesmo que o passo sem erro: os "
                  f"{_n(err_ps / ok_ps, 1)}× do sistema ({_mil(err_ps)} × {_mil(ok_ps)} por passo) vêm da mistura de papéis")
    else:
        titulo = (f"Dentro do mesmo papel, os passos com erro gastam {tok(abs(excesso_dentro))} "
                  f"{'a mais' if excesso_dentro > 0 else 'a menos'} que gastariam passos sem erro")
    fig.suptitle(titulo, x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    w = q.tokens_erro / q.tokens_erro.sum()
    dentro = float((w * (q.saida_erro - q.saida_total)).sum())
    total = total_erro[1] - total_erro[0]
    minimo = p.entrada_err.min()
    return ("Tokens de entrada × saída por passo",
            "Um passo com erro gasta mais que o passo sem erro do mesmo papel — e onde, na entrada ou na saída?",
            "Entrada = o que o modelo lê no passo (prompt, histórico, retorno das ferramentas); saída = o que ele escreve "
            "(raciocínio e código). Para cada papel (os de mais tokens em erro), a média de tokens por passo: azul = os "
            "passos sem erro do papel, laranja = os passos com erro. Barras parecidas = o passo com erro custa o mesmo "
            "que um passo comum: o gasto do erro vem de quantos passos falham (cada um é descartado), não de passos mais "
            f"caros. No sistema, o passo com erro custa {_mil(err_ps)} e o sem erro {_mil(ok_ps)} ({_n(err_ps / ok_ps, 1)}×), "
            f"o que sugeriria {tok(excesso_sistema)} a mais; somando papel a papel, a diferença é "
            f"{'+' if excesso_dentro >= 0 else '−'}{tok(abs(excesso_dentro))}: o resto é mistura (os erros se concentram "
            "nos papéis de passo caro). Um passo com erro mais barato que o comum costuma ser erro cedo na trajetória, com "
            f"pouco contexto (hipótese). Em todos os {len(p)} papéis, pelo menos {_n(100 * minimo)}% dos tokens do passo "
            f"com erro são de entrada. A fatia de saída sobe de {_pct(100 * total_erro[0])} (todos os passos) a "
            f"{_pct(100 * total_erro[1])} (passos com erro), mas dentro dos papéis a diferença é {_n(100 * dentro, 1)} "
            f"ponto(s); os outros {_n(100 * (total - dentro), 1)} vêm da mistura. Passos com erro por papel: "
            + "; ".join(f"{nome_papel(i)} {_n(r.erros)}" for i, r in p.iterrows()) + ".",
            "Média por passo (as contagens dão somas, não a distribuição); não inclui os passos de recuperação depois do "
            "erro (cascata). Hipóteses, não medidas: que a entrada alta seja contexto acumulado (falta a entrada por "
            "posição do passo, roadmap b3 #13); que a saída maior no passo com erro venha de erros que geram texto "
            "(resposta sem bloco de código, texto solto, texto longo em literal).")


def taxa_unidade_mes(upm, ppm, tri, mes, destino):
    """8 · Erros por unidade e mês: a contagem (esquerda) e a taxa por 1.000 passos do mês (direita)."""
    ordem = tri.sort_values("erros_observaveis", ascending=False).unidade.tolist()
    meses = sorted(set(mes.index) | set(upm.mes))
    piv = upm.pivot_table(index="unidade", columns="mes", values="erros", aggfunc="sum", fill_value=0)
    piv = piv.reindex([u for u in ordem if u in piv.index]).reindex(columns=meses, fill_value=0)
    if ppm is not None and len(ppm):
        piv.loc[SEM_UNIDADE] = ppm.groupby("mes").erros.sum().reindex(meses, fill_value=0)
    piv.loc["total do mês"] = piv.sum()
    den = mes.actionsteps.reindex(meses)
    taxa = 100 * piv.div(den, axis=1)   # % dos passos do sistema no mês (D2, 16/10: uma unidade só no relatório)
    poucos = den.lt(MIN_PASSOS).to_numpy()
    n_l, n_c = piv.shape
    fig, axes = plt.subplots(1, 2, figsize=(22, 0.42 * n_l + 3.2), sharey=True)
    for ax, tab, casas, rot in [(axes[0], piv, 0, "erros (contagem)"),
                                (axes[1], taxa, 2, "% dos passos do sistema no mês")]:
        dados = tab.to_numpy().astype(float)
        cor = dados.copy()
        cor[-1, :] = np.nan                  # a linha do total não entra na cor
        cor[:, poucos] = np.nan              # nem os meses com poucos passos
        cor[cor <= 0] = np.nan
        pos = cor[~np.isnan(cor)]
        norm = LogNorm(vmin=pos.min(), vmax=pos.max()) if len(pos) and pos.max() > pos.min() else None
        im = ax.imshow(cor, aspect="auto", cmap="Blues", interpolation="nearest", norm=norm)
        for i in range(n_l):
            for j in range(n_c):
                v = dados[i, j]
                if v > 0:
                    txt = f"<{_n(0.01, 2)}" if casas and v < 0.005 else _n(v, casas)
                    escuro = not np.isnan(cor[i, j]) and norm is not None and norm(cor[i, j]) > 0.65
                    ax.text(j, i, txt, ha="center", va="center", fontsize=7,
                            color="white" if escuro else (MUTED if poucos[j] else INK),
                            fontweight="bold" if i == n_l - 1 else "normal")
        ax.axhline(n_l - 1.5, color=INK2, lw=0.8)
        ax.set_xticks(range(n_c), [f"{_mes(m)}\n{_n(d)}" if pd.notna(d) else _mes(m)
                                   for m, d in zip(meses, den)], fontsize=7.5)
        for lab, pq in zip(ax.get_xticklabels(), poucos):
            if pq:
                lab.set_color(MUTED)
        ax.set_title(rot, loc="left", fontsize=10)
        cb = fig.colorbar(im, ax=ax, orientation="horizontal", location="bottom", fraction=0.025, pad=0.07, aspect=60)
        cb.ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _, c=casas: _n(v, c)))
        cb.ax.tick_params(labelsize=7)
        cb.set_label(rot + " (escala log)", fontsize=8)
    axes[0].set_yticks(range(n_l), [unidade(u) if u != "total do mês" else "total do mês" for u in piv.index], fontsize=7.5)
    ult = meses[-1]
    fig.suptitle(f"Erros por unidade e mês — à esquerda a contagem, à direita a taxa: % dos passos do sistema no mês "
                 f"(todos os papéis). Cinza: mês com menos de {_n(MIN_PASSOS)} passos no sistema (fora da escala de cor)",
                 x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    corpo = taxa.iloc[:-1].drop(index=[SEM_UNIDADE], errors="ignore")
    if (~poucos).any():
        corpo = corpo.drop(columns=[m for m, pq in zip(meses, poucos) if pq])
    u_ex, m_ex = corpo.stack().idxmax()
    exemplo = (f"{_mes(m_ex)}, {unidade(u_ex)}: {_n(piv.loc[u_ex, m_ex])} erros ÷ {_n(den[m_ex])} passos do sistema = "
               f"{_n(taxa.loc[u_ex, m_ex], 2)}%")
    return ("Erros e taxa por unidade e mês",
            "A unidade cresce porque o sistema rodou mais, ou porque o erro ficou mais frequente por passo?",
            "Mesmas linhas e meses nos dois painéis: à esquerda a contagem de erros, à direita a taxa — os erros da "
            "unidade como % de todos os passos do sistema no mês (a mesma unidade da taxa por mês). Embaixo de cada mês, "
            "o número de passos do sistema no mês (o denominador). Uma régua de cor só por painel, em escala log, com a "
            "barra de cores: células de mesma cor têm o mesmo valor. A linha do total soma a coluna; na taxa, é a taxa "
            f"total do mês (a do gráfico de taxa por mês) e serve de régua: a unidade com {_n(taxa.loc[u_ex, m_ex], 2)}% "
            f"em {_mes(m_ex)} é {_n(100 * taxa.loc[u_ex, m_ex] / taxa.loc['total do mês', m_ex])}% de todos os erros "
            f"daquele mês. Exemplo: {exemplo}. Onde a contagem sobe e a taxa não, foi volume: o sistema rodou mais, o erro "
            f"não ficou mais frequente. Um mês com menos de {_n(MIN_PASSOS)} passos no sistema mostra os números, mas fica cinza e fora "
            "da régua de cor: poucos erros nele viram uma taxa alta e pintariam o pico da linha.",
            "O denominador é o mês inteiro (todos os papéis), não só os papéis onde a unidade aparece: uma unidade que cai "
            "pode ser um papel que rodou menos (a taxa por papel é o roadmap b3 #37). Meses com poucos passos têm taxa "
            "instável e ficam fora da cor.")


FAIXAS = [("candidata", "candidata a memória (teto de economia)", BLUE),
          ("sinal", "sinal de harness (conserto no prompt)", ORANGE),
          ("infra", "harness / infra", INK2),
          ("resto", "resíduo, crítico, sem recorrência ou pendente", RESIDUO)]


def _faixa(decisao):
    if decisao == "candidato observado":
        return "candidata"
    if decisao == bp.SINAL_HARNESS:
        return "sinal"
    if decisao == "não-memória":
        return "infra"
    return "resto"


def orcamento_papel(papel, upt, tri, destino, topo=12):
    """9 · A fatia do gasto total de cada papel que foi para passos com erro, por destino (o único gráfico de taxas com
    destino); o teto de economia por memória (hipótese) na faixa das candidatas."""
    dec = tri.set_index("unidade").decisao
    t = upt.assign(faixa=[("resto" if u == SEM_UNIDADE else _faixa(dec.get(u))) for u in upt.unidade])
    por = t.pivot_table(index="role", columns="faixa", values="tokens_n_conhecidos", aggfunc="sum", fill_value=0)
    por = por.reindex(columns=[k for k, _, _ in FAIXAS], fill_value=0).reindex(papel.index, fill_value=0)
    dif = (por.sum(axis=1) - papel.tokens_erro).abs()
    p = papel.sort_values("tokens_total", ascending=False).head(topo)
    fig, ax = plt.subplots(figsize=(13, 0.5 * len(p) + 3.2))
    esq = np.zeros(len(p))
    for k, rot, c in FAIXAS:
        v = 100 * por.loc[p.index, k].to_numpy() / p.tokens_total.to_numpy()
        ax.barh(range(len(p)), v, left=esq, color=c, label=rot, edgecolor="white", linewidth=0.5)
        esq += v
    for i, (nome, r) in enumerate(p.iterrows()):
        teto = por.loc[nome, "candidata"]
        ax.text(100 * r.tokens_erro / r.tokens_total, i,
                f"  {_pct(100 * r.tokens_erro / r.tokens_total)} de {tok(r.tokens_total)} · teto {tok(teto)} "
                f"({_pct(100 * teto / r.tokens_total)})", va="center", fontsize=7.5, color=INK2)
    sist = papel.tokens_erro.sum() / papel.tokens_total.sum()
    maior = papel.tokens_erro.idxmax()
    sem = (papel.tokens_erro.sum() - papel.tokens_erro[maior]) / (papel.tokens_total.sum() - papel.tokens_total[maior])
    for v, rot, ls in [(sist, f"referência: sistema todo {_pct(100 * sist)}", "--"),
                       (sem, f"referência: sem o {nome_papel(maior)} {_pct(100 * sem)}", ":")]:
        ax.axvline(100 * v, color=MUTED, linestyle=ls, linewidth=1, label=rot)
    ax.set_yticks(range(len(p)), [nome_papel(i) for i in p.index], fontsize=8)
    ax.set_ylim(len(p) - 0.4, -0.6)
    ax.set_xlim(0, 100 * (p.tokens_erro / p.tokens_total).max() * 1.6)
    ax.set_xlabel("% do gasto total do papel que foi para passos com erro")
    ax.legend(frameon=True, facecolor="white", edgecolor=GRID, fontsize=8, loc="lower right")
    tot = papel.tokens_total.sum()
    asteps = papel.actionsteps.sum()
    fx = {k: por[k].sum() for k, _, _ in FAIXAS}
    quadro = ("Sistema todo (gasto total " + tok(tot) + "):\n" + "\n".join(
        f"{rot.split(' (')[0]}: {tok(fx[k])} = {_pct(100 * fx[k] / tot)}" for k, rot, _ in FAIXAS) +
        f"\npara empatar, a memória pode custar até ≈ {_n(fx['candidata'] / asteps)} tokens por passo\n"
        "(teto = hipótese: supõe evitar todos esses erros, sem o custo de injetar a memória)")
    ax.text(0.99, 0.32, quadro, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color=INK2,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=GRID))
    _limpar(ax)
    pior = (p.tokens_erro / p.tokens_total).idxmax()
    ax.set_title(f"Fatia do gasto total de cada papel que foi para passos com erro, por destino · maior: "
                 f"{nome_papel(pior)} ({_pct(100 * p.tokens_erro[pior] / p.tokens_total[pior])})", loc="left", fontsize=11)
    _salvar(fig, destino)
    return ("Fatia do gasto de cada papel gasta em erros, por destino",
            "Em que papel o erro pesa mais no próprio gasto — e é erro de memória, de harness ou de infra?",
            f"Os {topo} papéis com maior gasto total (todos os tokens dos seus passos, com ou sem erro). Cada barra é a "
            "fatia desse gasto que foi para passos com erro, dividida pelo destino da unidade de cada erro (os pendentes "
            "entram na faixa roxa). O rótulo dá a fatia, o gasto do papel e o teto de economia por memória (os tokens das "
            "candidatas): se uma memória evitasse todos esses erros, o limite seria esse. As linhas verticais são "
            "referências, não metas: a fatia do sistema todo e a do sistema sem o papel que mais gasta em erro. O quadro "
            "dá os totais do sistema e o orçamento de injeção (o teto das candidatas dividido por todos os passos: quanto "
            "a memória poderia custar por passo para empatar).",
            "Hipótese: teto, sem o custo de injetar a memória (que aumenta a entrada de todos os passos); candidata é "
            "recorrência, não memória aprovada; é o custo do passo que falhou, não o da recuperação. O destino é o da "
            f"triagem global da unidade. Conferência: soma das faixas × tokens de erro da fonte, diferença máxima "
            f"{_n(dif.max())} tokens.")


def prioridade(papel, upt, tri, destino, cobertura=0.95):
    """10 · Prioridade em tokens absolutos, um painel só (redesenhado em 16/10: os dois painéis de pontos ficaram ilegíveis).
    A barra inteira é o que o papel gastou em passos com erro ("para reduzir erros"); a parte azul, o que é de candidatas a
    memória ("para memória", o teto). O gráfico anterior dá a fatia de cada papel sobre o próprio gasto; este, o volume."""
    papel = papel.copy()
    cand = set(tri.loc[tri.decisao.eq("candidato observado"), "unidade"]) if upt is not None else set()
    papel["teto"] = (upt[upt.unidade.isin(cand)].groupby("role").tokens_n_conhecidos.sum().reindex(papel.index).fillna(0)
                     if upt is not None else 0.0)
    p = papel[papel.tokens_erro.gt(0)].sort_values("tokens_erro", ascending=False)
    acum = p.tokens_erro.cumsum() / p.tokens_erro.sum()
    k = max(int((acum < cobertura).sum()) + 1, min(3, len(p)))
    sel, resto = p.head(k), p.iloc[k:]
    linhas = [(nome_papel(i), r.tokens_erro, r.teto) for i, r in sel.iterrows()]
    if len(resto):
        linhas.append((f"demais {len(resto)} papéis", resto.tokens_erro.sum(), resto.teto.sum()))
    tot_err, tot_teto = papel.tokens_erro.sum(), papel.teto.sum()
    fig, ax = plt.subplots(figsize=(12, 0.55 * len(linhas) + 2))
    y = np.arange(len(linhas))
    ax.barh(y, [l[1] / 1e6 for l in linhas], color=BASE, label="tokens em passos com erro (todos os destinos)")
    if upt is not None:
        ax.barh(y, [l[2] / 1e6 for l in linhas], color=BLUE, height=0.5, label="… dos quais de candidatas a memória (teto)")
    for yy, (nome, e, t) in zip(y, linhas):
        ax.text(e / 1e6, yy, f"  {tok(e)} ({_n(100 * e / tot_err)}% dos erros)"
                + (f" · candidatas {tok(t)}" if upt is not None else ""), va="center", fontsize=8.5, color=INK2)
    ax.set_yticks(y, [l[0] for l in linhas], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, max(l[1] for l in linhas) / 1e6 * 1.45)
    ax.set_xlabel("milhões de tokens")
    ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    _limpar(ax)
    lider_e = linhas[0][0]
    lider_t = max(linhas, key=lambda l: l[2])[0] if upt is not None else lider_e
    titulo = (f"Prioridade: o {lider_e} tem {_n(100 * linhas[0][1] / tot_err)}% dos tokens em erro"
              + (f" e o maior teto para memória ({tok(max(l[2] for l in linhas))})" if lider_t == lider_e and upt is not None
                 else (f"; o maior teto para memória é do {lider_t}" if upt is not None else "")))
    ax.set_title(titulo, loc="left", fontsize=11)
    _salvar(fig, destino)
    return ("Prioridade: onde está o volume",
            "Em que papel reduzir erros economiza mais tokens — e quanto disso uma memória alcançaria?",
            f"Os papéis que somam {_n(100 * cobertura)}% dos tokens gastos em passos com erro, do maior para o menor (o resto "
            "numa linha). A barra cinza inteira é o que o papel gastou em passos com erro, de qualquer destino: é a "
            "prioridade para reduzir erros. A barra azul por dentro é a parte desses tokens que vem de candidatas a memória "
            f"— o teto de economia por memória (hipótese: se uma memória evitasse todos esses erros). No sistema: "
            f"{tok(tot_err)} em erros, {tok(tot_teto)} de candidatas. A diferença entre cinza e azul é o que se resolve "
            "fora da memória (prompt, harness, infra) ou ainda não tem destino (resíduo, pendentes). O gráfico anterior "
            "mostra a mesma coisa como fatia do gasto de cada papel; este mostra o volume, que é o que decide onde começar.",
            "Tokens do passo com erro, não da recuperação. O teto não desconta o custo de injetar a memória e supõe evitar "
            "todos os erros das candidatas.")


_CLARAS = {"#b7e4c7", "#e0dfd8", "#c3c2b7", "#52b788"}   # segmentos em que o % vai em tinta escura


def _barra_empilhada(ax, y, partes, total, altura=0.7):
    """Uma barra 100% em `y`: `partes` = [(n, cor)]; o % escrito no segmento quando cabe (≥ 4%)."""
    esq = 0.0
    for n, cr in partes:
        v = 100 * n / total if total else 0
        ax.barh(y, v, left=esq, color=cr, edgecolor="white", height=altura)
        if v >= 4:
            ax.text(esq + v / 2, y, _pct(v, 0), ha="center", va="center", fontsize=8,
                    color=INK if cr in _CLARAS else "white")
        esq += v


def recuperacao_populacao(pop, extra, destino):
    """11 · A recuperação depois do erro, na população: os papéis com erro (censo dos erros da base 3). A barra das
    execuções saiu (Rafael, 26/10, foto IMG_6065): repetia o funil; o número de execuções com erro fica no título."""
    ex, pa = pop[pop.nivel.eq("execuções")].set_index("categoria"), pop[pop.nivel.eq("papéis com erro")].set_index("categoria")
    n_ex, n_pa = int(ex.total.iloc[0]), int(pa.total.iloc[0])
    fig, ax = plt.subplots(figsize=(13, 2.9))
    _barra_empilhada(ax, 0, [(pa.n.get(k, 0), c) for k, _, c in CATEGORIAS], n_pa)
    ax.set_yticks([0], [f"papéis com erro\n{_n(n_pa)}"], fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 25))
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in CATEGORIAS],
              labels=[r for _, r, _ in CATEGORIAS], ncol=2, fontsize=8, frameon=False, loc="lower left",
              bbox_to_anchor=(0, 1.0))
    _limpar(ax)
    ax.set_xlabel("% dos papéis com erro (cada papel numa execução conta uma vez)")
    com_erro = n_ex - int(ex.n.get("sem_erro", 0))
    verde = sum(int(pa.n.get(k, 0)) for k in ["um_erro", "cascata", "recaida"])
    de_novo = int(pa.n.get("cascata", 0) + pa.n.get("recaida", 0))
    nao = int(pa.n.get("terminou_no_erro", 0) + pa.n.get("limite_de_passos", 0))
    ax.set_title(f"Dos {_n(n_pa)} papéis que erraram (em {_n(com_erro)} execuções), {_p(pa.n.get('um_erro', 0), n_pa)} "
                 f"erraram uma vez só, {_p(de_novo, n_pa)} erraram de novo e depois seguiram sem erro, {_p(nao, n_pa)} "
                 "não se recuperaram", loc="left", fontsize=11, pad=48)
    _salvar(fig, destino)
    indet = int(pa.n.get("indeterminado", 0))
    return ("A recuperação depois do erro: os papéis com erro",
            "Quando o sistema erra, o agente se recupera, erra de novo ou termina no erro?",
            "A conta é por trajetória, não por erro: cada papel numa execução conta uma vez, do primeiro erro até o fim do "
            f"papel. Só os papéis com erro ({_n(n_pa)}, em {_n(com_erro)} das {_n(n_ex)} execuções; a fração das execuções "
            "com erro está no funil), pelo que aconteceu — um erro só e depois nenhum; uma "
            "cascata (errou de novo no passo seguinte) e depois nenhum; uma recaída (passou um passo sem erro e errou de "
            "novo mais adiante) e depois nenhum; o último passo do papel com erro; o limite de passos; e indeterminado "
            f"(os vizinhos de dois erros não conferem). Seguiram sem erro até o fim (os três verdes): "
            f"{_p(verde, n_pa)} dos papéis com erro. Dos {_n(extra['erros'])} erros, {_n(extra['erros_em_cascata'])} "
            "vêm logo depois de outro erro do mesmo papel. Os números por papel e os motivos dos indeterminados estão nas "
            "tabelas `recuperacao_*.csv`.",
            "\"Seguiu sem erro até o fim\" é sinal de recuperação, não sucesso: a qualidade da resposta não está na base e "
            "uma falha silenciosa não é erro estruturado (a suspeita da query pega pouco). A base 3 tem todos os erros de "
            "cada papel, por isso o \"até o fim\" vale; o número de passos depois do último erro não é medido (a posição "
            f"de cada passo no papel não está na base). Indeterminados: {_n(indet)} papéis. Sequência entre dois erros não "
            "prova que um causou o outro.")


def recuperacao_papel(por_papel, destino, topo=12):
    """12 · A mesma recuperação, um papel por barra (os papéis com mais trajetórias com erro; o resto numa barra)."""
    cats = [k for k, _, _ in CATEGORIAS]
    p = por_papel.copy()
    corte = topo if len(p) > topo + 1 else len(p)   # um papel só a mais vai pelo nome, não como "demais 1 papéis"
    sel, resto = p.head(corte), p.iloc[corte:]
    linhas = [(nome_papel(r.papel), r) for _, r in sel.iterrows()]
    if len(resto):
        soma = resto[cats + ["com_erro", "execucoes"]].sum()
        linhas.append((f"demais {len(resto)} papéis", soma))
    fig, ax = plt.subplots(figsize=(14, 0.6 * len(linhas) + 2.4))
    for y, (nome, r) in enumerate(linhas):
        _barra_empilhada(ax, y, [(r[k], c) for k, _, c in CATEGORIAS], r.com_erro, altura=0.75)
        ax.text(101, y, f"{_n(r.com_erro)} de {_n(r.execucoes)} {'execução' if r.execucoes == 1 else 'execuções'} do "
                f"papel com erro ({_p(r.com_erro, r.execucoes)})",
                va="center", fontsize=8, color=INK2)
    ax.set_yticks(range(len(linhas)), [n for n, _ in linhas], fontsize=8.5)
    for lab, (_, r) in zip(ax.get_yticklabels(), linhas):
        if r.com_erro < MIN_N:
            lab.set_color(MUTED)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks(range(0, 101, 25))
    ax.set_xlabel("% dos papéis com erro (cada papel numa execução conta uma vez)")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in CATEGORIAS], labels=[r for _, r, _ in CATEGORIAS],
              ncol=2, fontsize=8, frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0))
    _limpar(ax)
    g = sel[sel.com_erro.ge(MIN_N)] if sel.com_erro.ge(MIN_N).any() else sel
    de_novo = (g.cascata + g.recaida + g.terminou_no_erro + g.limite_de_passos) / g.com_erro
    pior, melhor = de_novo.idxmax(), de_novo.idxmin()
    ax.set_title(f"Quem mais erra de novo ou termina no erro é o {nome_papel(g.papel[pior])} "
                 f"({_pct(100 * de_novo[pior], 0)} dos papéis com erro); o que menos, o {nome_papel(g.papel[melhor])} "
                 f"({_pct(100 * de_novo[melhor], 0)})", loc="left", fontsize=11, pad=48)
    _salvar(fig, destino)
    return ("A recuperação depois do erro, por papel",
            "Em que papel o agente se recupera de um erro, e em que papel ele erra de novo ou termina no erro?",
            f"Uma barra por papel, os {topo} com mais trajetórias com erro (o resto numa barra), cada uma somando 100% dos "
            "papéis com erro dele, nas mesmas categorias do gráfico anterior. À direita, quantas execuções do papel "
            "tiveram erro, sobre todas as execuções dele (o denominador das contagens). O título compara os papéis com "
            f"pelo menos {MIN_N} trajetórias com erro pela soma de cascata, recaída, terminou no erro e limite de passos. "
            "Muito verde-escuro = o papel erra uma vez e segue; muito verde-claro ou vermelho = o erro desse papel puxa "
            "outros. Hipótese, não testada: o papel com mais cascata é onde a mensagem de erro menos ajuda o agente a se "
            "corrigir.",
            f"Nome em cinza: menos de {MIN_N} trajetórias com erro (porcentagem instável). As mesmas limitações do gráfico "
            "anterior: sinal de recuperação, não sucesso; só erros estruturados.")
