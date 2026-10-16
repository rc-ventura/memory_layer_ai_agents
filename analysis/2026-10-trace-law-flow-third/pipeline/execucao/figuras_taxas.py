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
from execucao.figuras_painel import (SEM_UNIDADE, _limpar, _milhar, _n, _pct, _salvar, _tok as tok, papel as nome_papel,
                                     refs_tamanho, rotular, unidade)

MIN_N = 20         # abaixo disso, o mês ou o papel aparece em cinza: amostra pequena para uma taxa
MIN_PASSOS = 1000  # mês do sistema com menos passos: cinza e fora da escala de cor na taxa por unidade e mês (D2, 16/10)
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
    for ax, rot, val, nota in [
            (a1, ["execuções", "execuções com pelo menos um erro"], [n, com_erro],
             f"{_n(erros / com_erro, 2) if com_erro else '—'} erros por execução com erro"),
            (a2, ["passos (ActionSteps)", "passos com erro"], [asteps, erros],
             f"{_n(asteps / n, 2)} passos por execução")]:
        ax.barh(rot[::-1], val[::-1], color=[ORANGE, BASE])
        for i, v in enumerate(val[::-1]):
            ax.text(v, i, " " + _n(v) + (f" ({_p(v, val[0])})" if v != val[0] else ""), va="center", fontsize=9,
                    color=INK2)
        ax.set_xlim(0, val[0] * 1.35)
        _milhar(ax, "x")
        ax.text(0, -0.32, nota, transform=ax.transAxes, fontsize=9, color=INK2)
        _limpar(ax)
    a1.set_title("Execuções (execução + agente)", loc="left", fontsize=10)
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
            "subconjunto da de cima e o percentual é sobre ela. Uma execução com erro pode ter vários: por isso os dois "
            "percentuais são diferentes (as linhas embaixo dão a ligação).",
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
    refs = refs_tamanho(float(p.tokens_total.max()))
    ax.legend(handles=[plt.scatter([], [], s=v * escala, color=BLUE, alpha=0.6, edgecolor="white") for v in refs],
              labels=[tok(v) for v in refs], title="tamanho = gasto total do papel", loc="upper right", frameon=False,
              fontsize=8, title_fontsize=8, labelspacing=1.5, borderpad=1)
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
            f"legenda dá a escala. Rótulo em todo papel com pelo menos {MIN_N} execuções. A linha pontilhada é a taxa "
            "global do sistema (ponderada pelo volume, puxada pelos papéis grandes), não a média dos papéis. Acima do "
            f"dobro da taxa global: {lista}.",
            f"Pontos cinza: menos de {MIN_N} execuções do papel. A taxa é a do período inteiro (esconde o mês) e conta todos "
            "os erros do papel, de qualquer destino.")


def custo_execucao(execs, custo_papel, destino):
    """4 · A execução típica com erro × sem erro: k× os tokens e j× os passos (medianas normalizadas)."""
    g = execs[execs.actionsteps.gt(0)].assign(com=lambda d: d.erros.gt(0))
    med = g.groupby("com")[["tokens_total", "actionsteps"]].median()
    n = g.com.value_counts()
    if not {True, False} <= set(med.index):
        raise ValueError("custo por execução: falta o grupo com ou sem erro")
    k = med.loc[True] / med.loc[False]
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.2))
    for ax, col, rot, unid in [(axes[0], "tokens_total", "tokens por execução", "tokens"),
                               (axes[1], "actionsteps", "passos por execução", "passos")]:
        ax.barh(["sem erro", "com erro"], [1, k[col]], color=[BLUE, ORANGE])
        for i, grupo in enumerate([False, True]):
            v = 1 if not grupo else k[col]
            ax.text(v, i, f"  {_n(v, 1)}× · mediana {_n(med.loc[grupo, col])} {unid} (n = {_n(n[grupo])})", va="center",
                    fontsize=8.5, color=INK2)
        ax.set_xlim(0, max(k[col], 1) * 2.1)
        ax.set_xlabel("× a execução típica sem erro")
        ax.set_title(rot, loc="left", fontsize=10)
        _limpar(ax)
    fig.suptitle(f"A execução típica com erro usa {_n(k['tokens_total'], 1)}× os tokens e {_n(k['actionsteps'], 1)}× os "
                 "passos da típica sem erro", x=0.01, ha="left", fontsize=11)
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
    return ("Custo de uma execução com erro × sem erro",
            "Quanto mais tokens e mais passos usa uma execução que teve erro?",
            "Duas barras por painel, normalizadas: a execução sem erro vale 1×. A estatística é a mediana — a execução do "
            "meio: metade custa menos, metade custa mais (robusta à cauda longa: poucas execuções levam boa parte do "
            "gasto). Execução = execução + agente, somando os papéis." + dentro,
            "Não é causa: uma execução longa tem mais chance de errar e custa mais de qualquer jeito. Só os passos (o "
            "planejamento não entra). \"Sem erro\" inclui as execuções só com suspeita. A média e o p90 estão no CSV.")


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
        ax.annotate(f"{q}% mais caras = {_n(100 * v)}% do gasto\ndessas, {_n(100 * e)}% têm erro", (q, 100 * v),
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
            "mais concentrado. Nos dois pontos marcados, a % das execuções que têm pelo menos um erro estruturado. É uma "
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
    ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=8, loc="upper left")
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
                 loc="left", fontsize=11)
    _salvar(fig, destino)
    return ("Evolução mensal do custo por execução",
            "O custo por execução cai sozinho, sem memória — e anda junto com a taxa de erro?",
            "Barras: a mediana dos tokens por execução no mês (a execução do meio), com o número de execuções. Linha "
            "laranja, no eixo da direita: a taxa de erro do mesmo mês (o gráfico de taxa por mês), para ver o par. A média "
            "por mês está em `taxas_por_mes.csv`.",
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
    a1.set_yticks(y, [f"{nome_papel(i)}\n{_n(r.erros)} passos com erro" for i, r in p.iterrows()], fontsize=8)
    a1.invert_yaxis()
    for yy, (_, r) in zip(y, p.iterrows()):
        a2.text(1.02, yy, f"com erro: {_mil(r.e_err + r.s_err)} ({'+' if r.excesso >= 0 else '−'}"
                f"{_mil(abs((r.e_err + r.s_err) - (r.e_ok + r.s_ok)))})\nexcesso: {'−' if r.excesso < 0 else ''}{tok(abs(r.excesso))}",
                transform=a2.get_yaxis_transform(), va="center", fontsize=7.5, color=INK2)
    a1.legend(frameon=False, fontsize=8, loc="lower right")
    minimo = p.entrada_err.min()
    fig.suptitle(f"Em todos os {len(p)} papéis com mais tokens em erro, pelo menos {_n(100 * minimo)}% dos tokens do "
                 "passo com erro são de entrada", x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    # composição: quanto da diferença global de fatia de saída é dentro dos papéis e quanto é mistura
    w = q.tokens_erro / q.tokens_erro.sum()
    dentro = float((w * (q.saida_erro - q.saida_total)).sum())
    total = total_erro[1] - total_erro[0]
    err_ps = papel.tokens_erro.sum() / papel.erros.sum()
    ok_ps = (papel.tokens_total.sum() - papel.tokens_erro.sum()) / (papel.actionsteps.sum() - papel.erros.sum())
    return ("Tokens de entrada × saída por passo",
            "Quanto um passo com erro gasta a mais que o passo típico do mesmo papel, e onde — na entrada ou na saída?",
            "Entrada = o que o modelo lê no passo (prompt, histórico, retorno das ferramentas); saída = o que ele escreve "
            "(raciocínio e código). Para cada papel (os de mais tokens em erro), a média de tokens por passo: azul = os "
            "passos sem erro do papel, laranja = os passos com erro. À direita, duas medidas: o gasto do passo com erro "
            "(tudo o que ele gastou; o passo é descartado) com a diferença sobre o passo sem erro, e o excesso no papel "
            "(essa diferença × os passos com erro). No sistema: passo com erro "
            f"{_mil(err_ps)}, passo sem erro {_mil(ok_ps)} ({_n(err_ps / ok_ps, 1)}×), excesso ≈ "
            f"{tok((err_ps - ok_ps) * papel.erros.sum())}. A fatia de saída sobe de {_pct(100 * total_erro[0])} (todos os "
            f"passos) a {_pct(100 * total_erro[1])} (passos com erro), mas dentro dos papéis a diferença é "
            f"{_n(100 * dentro, 1)} ponto(s); os outros {_n(100 * (total - dentro), 1)} vêm da mistura (os erros se "
            "concentram em papéis que escrevem mais).",
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
        ax.set_xticks(range(n_c), [f"{_mes(m)}\n{_n(d)} passos" if pd.notna(d) else _mes(m)
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
    picos = taxa.iloc[:-1]
    for i, (u, r) in enumerate(picos.iterrows()):
        if r.max() > 0:
            mm = r.idxmax()
            axes[1].text(n_c - 0.4, i, f" pico {_n(r.max(), 2)}% ({_mes(mm)})", va="center", fontsize=7, color=INK2,
                         clip_on=False)
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
            "o denominador (passos do mês). Uma régua de cor só por painel, em escala log, com a barra de cores: células "
            "de mesma cor têm o mesmo valor. À direita, o pico de cada linha. A linha do total soma a coluna; na taxa, é "
            f"a taxa total do mês (a do gráfico de taxa por mês). Exemplo: {exemplo}. Onde a contagem sobe e a taxa não, "
            f"foi volume. Um mês com menos de {_n(MIN_PASSOS)} passos no sistema mostra os números, mas fica cinza e fora "
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
        f"\norçamento de injeção: ≈ {_n(fx['candidata'] / asteps)} tokens por passo\n"
        "hipótese: teto, sem o custo de injetar a memória")
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


def _painel_prioridade(ax, p, col, sist, sem, maior, rot_valor, cobertura):
    """Um painel do gráfico de prioridade: x = `col` ÷ gasto total do papel, y = `col` (log); papéis até `cobertura`
    do total da coluna, o resto num ponto; o fator sobre a referência no rótulo; em laranja, quem mais muda de posição
    entre os dois painéis (marcado de fora, em `p.destaque`)."""
    p = p[p[col].gt(0)].sort_values(col, ascending=False)
    acum = p[col].cumsum() / p[col].sum()
    k = max(int((acum < cobertura).sum()) + 1, min(3, len(p)))
    sel, resto = p.head(k), p.iloc[k:]
    pct = sel[col] / sel.tokens_total
    ax.scatter(100 * pct, sel[col], s=60, color=[ORANGE if d else BLUE for d in sel.destaque], zorder=3)
    xs, ys, textos = (100 * pct).tolist(), sel[col].tolist(), []
    for i, r in sel.iterrows():
        ref, nome_ref = (sist, "o sistema") if i == maior else (sem, f"sem o {nome_papel(maior)}")
        textos.append(f"{nome_papel(i)}: {_pct(100 * r[col] / r.tokens_total)} de {tok(r.tokens_total)} = {tok(r[col])}"
                      f" · {_n(r[col] / r.tokens_total / ref, 1)}× {nome_ref}")
    if len(resto):
        rp = resto[col].sum() / resto.tokens_total.sum()
        ax.scatter([100 * rp], [resto[col].sum()], s=60, color=BASE, zorder=3)
        xs.append(100 * rp)
        ys.append(resto[col].sum())
        textos.append(f"demais {len(resto)} papéis: {_pct(100 * rp)} de {tok(resto.tokens_total.sum())}")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: tok(v)))
    for v, r, ls in [(sist, f"referência: sistema todo {_pct(100 * sist)}", "--"),
                     (sem, f"referência: sem o {nome_papel(maior)} {_pct(100 * sem)}", ":")]:
        ax.axvline(100 * v, color=MUTED, linestyle=ls, linewidth=1, label=r)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.set_xlim(0, 100 * max(pct.max(), sist) * 1.3)
    ax.set_ylim(min(ys) / 2.5, max(ys) * 2.5)
    rotular(ax, xs, ys, textos, raios=[4] * len(xs), fontsize=7)
    ax.set_xlabel(f"% do gasto total do papel {rot_valor}")
    ax.grid(color=GRID, lw=0.6, zorder=0)
    _limpar(ax)
    return sel


def prioridade(papel, upt, tri, destino, cobertura=0.95):
    """10 · A prioridade em dois critérios, um por painel (decisão D3 de 16/10): para reduzir erros (todos os tokens em
    passos com erro) e para memória (o teto: só os tokens das candidatas)."""
    papel = papel.copy()
    criterios = [("tokens_erro", "que foi para passos com erro", "Para reduzir erros: todos os tokens em passos com erro")]
    if upt is not None:
        cand = set(tri.loc[tri.decisao.eq("candidato observado"), "unidade"])
        papel["teto"] = (upt[upt.unidade.isin(cand)].groupby("role").tokens_n_conhecidos.sum()
                         .reindex(papel.index).fillna(0))
    p = papel[papel.tokens_erro.gt(0)].copy()
    if p.execucoes.ge(MIN_N).any():   # base pequena: todos os papéis com erro
        p = p[p.execucoes.ge(MIN_N)]
    if upt is not None:
        criterios.append(("teto", "que foi para erros das candidatas (teto)",
                          "Para memória: só os tokens das candidatas (o teto de economia, hipótese)"))
    # quem mais muda de posição entre os dois critérios (ou entre % e absoluto, se só há um)
    if len(criterios) == 2:
        r1, r2 = p.tokens_erro.rank(ascending=False, method="first"), p.teto.rank(ascending=False, method="first")
    else:
        r1 = p.tokens_erro.rank(ascending=False, method="first")
        r2 = (p.tokens_erro / p.tokens_total).rank(ascending=False, method="first")
    mov = (r1 - r2).abs().sort_values(ascending=False)
    p["destaque"] = p.index.isin(mov[mov.gt(0)].head(3).index)
    fig, axes = plt.subplots(1, len(criterios), figsize=(12.5 * len(criterios) / 1.5 + 2, 7), squeeze=False)
    lideres = []
    for ax, (col, rot_valor, titulo) in zip(axes[0], criterios):
        tot_col, tot = papel[col].sum(), papel.tokens_total.sum()
        sist = tot_col / tot
        maior = p[col].idxmax()
        sem = (tot_col - p[col][maior]) / (tot - p.tokens_total[maior])
        sel = _painel_prioridade(ax, p, col, sist, sem, maior, rot_valor, cobertura)
        ax.set_title(titulo, loc="left", fontsize=10)
        lideres.append((col, sel[col].idxmax()))
    axes[0][0].set_ylabel("tokens (escala log)")
    if len(lideres) == 2:
        a, b = lideres[0][1], lideres[1][1]
        titulo = (f"Prioridade: {nome_papel(a)} lidera nos dois critérios — para reduzir erros e para memória" if a == b else
                  f"Prioridade: {nome_papel(a)} lidera para reduzir erros; {nome_papel(b)}, para memória")
    else:
        titulo = f"Prioridade para reduzir erros: {nome_papel(lideres[0][1])} lidera em tokens em erro"
    fig.suptitle(titulo, x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    movem = ", ".join(f"{nome_papel(i)} ({int(r1[i])}.º → {int(r2[i])}.º)" for i in mov[mov.gt(0)].head(3).index)
    return ("Prioridade: para reduzir erros e para memória",
            "Onde começar — o papel que mais gasta em erros é o mesmo em que uma memória economizaria mais?",
            "Um painel por critério. À esquerda, para reduzir erros: todos os tokens gastos em passos com erro, de "
            "qualquer destino. À direita, para memória: só os tokens dos erros das candidatas (o teto de economia: se uma "
            "memória evitasse todos eles; hipótese, sem o custo de injetar a memória). Em cada painel, um ponto por papel "
            f"(os que somam {_n(100 * cobertura)}% do critério; o resto num ponto só): à direita, os que perdem uma fatia "
            "maior do próprio gasto total (todos os tokens dos seus passos); acima, os que gastam mais tokens. O rótulo dá "
            "a conta (fatia × gasto) e o fator sobre a referência — o papel que mais gasta é comparado com o sistema todo; "
            "os demais, com o sistema sem ele. As linhas são referências, não metas. Em laranja, os que mais mudam de "
            f"posição entre os dois critérios: {movem or 'nenhum'}.",
            f"Só papéis com pelo menos {MIN_N} execuções. Tokens do passo com erro, não da recuperação. A composição do "
            "gasto de cada papel por destino está no gráfico anterior.")
