"""Figuras das taxas da base 3 (roadmap b3 #32): erros e custo sobre o denominador do pedido A.

Cada função recebe tabelas já conferidas pelo `taxas.py` (a junção fonte × contagens passou), desenha uma figura e
devolve (título, pergunta, como ler, limitação) — o mesmo contrato do `figuras_painel.py`. Títulos com número saem
dos dados. Só contagens, nomes de papel, de unidade e meses: nenhum identificador de execução nem texto de caso.
Grupo 1 (só as contagens): funil, taxa por mês, papel, custo por execução, concentração, custo mensal, entrada ×
saída. Grupo 2 (contagens × rodada): taxa por unidade e mês, orçamento do papel por destino, prioridade por critério.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import base_pipeline as bp
from paleta import BASE, BLUE, GRID, INK, INK2, MUTED, ORANGE, RESIDUO
from execucao.figuras_painel import _limpar, _n, _salvar

MIN_N = 20   # abaixo disso, o mês ou o papel aparece em cinza: amostra pequena para uma taxa


def _pct(a, b, casas=1):
    return _n(100 * a / b, casas) + "%" if b else "—"


def funil(execs, destino):
    """O tamanho do problema: execuções e ActionSteps, com e sem erro."""
    n, com_as, com_erro = len(execs), int(execs.actionsteps.gt(0).sum()), int(execs.erros.gt(0).sum())
    asteps, erros = int(execs.actionsteps.sum()), int(execs.erros.sum())
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 3.2))
    for ax, rot, val in [(a1, ["execuções", "com ActionStep", "com erro estruturado"], [n, com_as, com_erro]),
                         (a2, ["ActionSteps", "com erro estruturado"], [asteps, erros])]:
        ax.barh(rot[::-1], val[::-1], color=[ORANGE] + [BLUE] * (len(val) - 1))
        for i, v in enumerate(val[::-1]):
            ax.text(v, i, " " + _n(v) + (f" ({_pct(v, val[0])})" if v != val[0] else ""), va="center", fontsize=9, color=INK2)
        ax.set_xlim(0, val[0] * 1.3)
        _limpar(ax)
    a1.set_title("Execuções (execução + agente)", loc="left", fontsize=10)
    a2.set_title("ActionSteps", loc="left", fontsize=10)
    fig.suptitle(f"{_pct(com_erro, n)} das execuções e {_pct(erros, asteps)} dos ActionSteps têm erro estruturado",
                 x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    return ("O tamanho do problema: execuções e ActionSteps com erro",
            "Quanto do trabalho do sistema esbarra num erro estruturado?",
            "Dois painéis com escalas próprias: à esquerda as execuções, à direita os ActionSteps. Cada barra é um "
            "subconjunto da anterior; o percentual é sobre a primeira.",
            "Erro estruturado é o que levantou exceção; as suspeitas da query e as falhas silenciosas não entram. "
            "Execuções sem nenhum ActionStep (papéis que só delegam) contam no total.")


def taxa_mes(mes, destino):
    """Agosto teve mais execuções ou mais erro por passo? A taxa por mês, com e sem o sinal de harness."""
    m = mes.sort_index()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True, gridspec_kw={"height_ratios": [1, 1.4]})
    x = np.arange(len(m))
    a1.bar(x, m.actionsteps, color=[BASE if e < MIN_N else BLUE for e in m.execucoes])
    for i, v in enumerate(m.actionsteps):
        a1.text(i, v, _n(v), ha="center", va="bottom", fontsize=7, color=INK2)
    a1.set_ylabel("ActionSteps")
    a2.plot(x, 100 * m.taxa, marker="o", color=ORANGE, label="erros estruturados ÷ ActionSteps")
    a2.plot(x, 100 * m.taxa_sem_harness, marker="o", color=BLUE, linestyle="--", label="sem o sinal de harness")
    for i, v in enumerate(m.taxa):
        a2.text(i, 100 * v, f" {_n(100 * v, 1)}%", fontsize=7, color=INK2, va="bottom")
    a2.set_ylabel("% dos ActionSteps")
    a2.set_xticks(x, m.index, rotation=45, ha="right")
    a1.legend(*a2.get_legend_handles_labels(), frameon=False, fontsize=8, loc="upper left")   # o topo-esquerdo do volume é vazio
    for ax in (a1, a2):
        _limpar(ax)
    pico = m.taxa.idxmax()
    fig.suptitle(f"Taxa de erro por mês: o pico é {pico} ({_n(100 * m.taxa[pico], 1)}%); "
                 f"o mês com mais ActionSteps é {m.actionsteps.idxmax()}", x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    return ("Taxa de erro por mês",
            "Um mês com mais erros teve mais execuções ou mais erro por passo?",
            "Em cima, o volume (ActionSteps); embaixo, a taxa. Se a barra sobe e a taxa não, foi volume; se a taxa sobe, "
            "o sistema errou mais por passo. A linha tracejada tira os erros das unidades de sinal de harness (o "
            "`try/except NameError`): a distância entre as duas linhas é o que o prompt explica.",
            f"Mês de início da execução. Barras cinza: menos de {MIN_N} execuções no mês.")


def papel_volume(papel, destino, rotulos=10):
    """Um papel erra mais ou só roda mais? Volume × taxa."""
    p = papel[papel.actionsteps.gt(0)]
    fig, ax = plt.subplots(figsize=(11, 6))
    tam = 30 + 600 * p.tokens_total / p.tokens_total.max()
    ax.scatter(p.actionsteps, 100 * p.taxa, s=tam, color=[BASE if e < MIN_N else BLUE for e in p.execucoes],
               alpha=0.75, edgecolor="white")
    media = p.erros.sum() / p.actionsteps.sum()
    ax.axhline(100 * media, color=MUTED, linestyle=":", linewidth=1)
    ax.text(p.actionsteps.min(), 100 * media, f" média {_n(100 * media, 1)}%", fontsize=8, color=MUTED, va="bottom")
    for nome, r in p.sort_values("erros", ascending=False).head(rotulos).iterrows():
        ax.annotate(nome, (r.actionsteps, 100 * r.taxa), fontsize=8, xytext=(4, 3), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_xlabel("ActionSteps do papel (escala log)")
    ax.set_ylabel("% dos ActionSteps com erro estruturado")
    _limpar(ax)
    acima = p[(p.taxa > 2 * media) & (p.execucoes >= MIN_N)].sort_values("erros", ascending=False)
    extra = f": {', '.join(acima.index[:3])}" if len(acima) else ""
    ax.set_title(f"Volume × taxa por papel · {len(acima)} papéis com mais do dobro da taxa média{extra}",
                 loc="left", fontsize=11)
    _salvar(fig, destino)
    return ("Papel: volume × taxa",
            "Um papel aparece com muitos erros porque erra mais por passo ou porque roda mais?",
            "Cada ponto é um papel; à direita, os que rodam mais; acima, os que erram mais por passo; o tamanho é o "
            "gasto total em tokens. Rótulo nos 10 papéis com mais erros. Acima da linha pontilhada, taxa acima da média.",
            f"Pontos cinza: menos de {MIN_N} execuções do papel. A taxa mistura todas as unidades do papel, inclusive "
            "o sinal de harness e a não-memória.")


def custo_execucao(execs, destino):
    """O preço de uma execução com erro, em tokens e em passos."""
    g = execs[execs.actionsteps.gt(0)].assign(grupo=lambda d: np.where(d.erros.gt(0), "com erro", "sem erro"))
    ordem = ["sem erro", "com erro"]
    med = g.groupby("grupo")[["tokens_total", "actionsteps"]].median().reindex(ordem).fillna(0)
    p90 = g.groupby("grupo")[["tokens_total", "actionsteps"]].quantile(0.9).reindex(ordem).fillna(0)
    n = g.grupo.value_counts().reindex(ordem).fillna(0)
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.4))
    for ax, col, rot in [(axes[0], "tokens_total", "tokens por execução"), (axes[1], "actionsteps", "ActionSteps por execução")]:
        ax.barh(ordem, med.loc[ordem, col], color=[BLUE, ORANGE])
        ax.scatter(p90.loc[ordem, col], ordem, marker="|", s=300, color=INK, label="p90")
        for i, gname in enumerate(ordem):
            ax.text(max(med.loc[gname, col], p90.loc[gname, col]), i, f"  mediana {_n(med.loc[gname, col])} · p90 {_n(p90.loc[gname, col])} "
                    f"(n={_n(n[gname])})", va="center", fontsize=8, color=INK2)
        ax.set_title(rot, loc="left", fontsize=10)
        ax.set_xlim(0, max(p90[col].max(), 1) * 2.4)
        _limpar(ax)
    sem = med.loc["sem erro", "tokens_total"]
    razao = _n(med.loc["com erro", "tokens_total"] / sem, 1) + "×" if sem else "—"
    fig.suptitle(f"Uma execução com erro custa {razao} a mediana de uma sem erro", x=0.01, ha="left", fontsize=11)
    _salvar(fig, destino)
    return ("Custo de uma execução com erro × sem erro",
            "Quanto mais caro fica uma execução quando ela tem erro?",
            "Dois painéis com escalas próprias; a barra é a mediana e o traço, o percentil 90. Execução = execução + "
            "agente, somando os papéis.",
            "Não é causa: execuções longas têm mais chance de errar e custam mais de qualquer jeito. Só ActionSteps "
            "(o planejamento não entra). Execuções sem ActionStep ficam de fora.")


def concentracao(execs, destino):
    """O custo é dominado por poucas execuções caras? Curva de Lorenz."""
    t = np.sort(execs.tokens_total.fillna(0).to_numpy())[::-1]
    acum = np.cumsum(t) / t.sum()
    x = np.arange(1, len(t) + 1) / len(t)
    top10, top1 = acum[max(int(0.10 * len(t)) - 1, 0)], acum[max(int(0.01 * len(t)) - 1, 0)]
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(100 * x, 100 * acum, color=BLUE)
    ax.plot([0, 100], [0, 100], color=MUTED, linestyle="--", linewidth=1)
    for q, v in [(1, top1), (10, top10)]:
        ax.scatter([q], [100 * v], color=ORANGE, zorder=3)
        ax.annotate(f"{q}% mais caras = {_n(100 * v)}% do gasto", (q, 100 * v), xytext=(8, -12),
                    textcoords="offset points", fontsize=9)
    ax.set_xlabel("% das execuções, da mais cara para a mais barata")
    ax.set_ylabel("% do gasto total em tokens")
    _limpar(ax)
    ax.set_title(f"Concentração de custo: as 10% execuções mais caras levam {_n(100 * top10)}% dos tokens",
                 loc="left", fontsize=11)
    _salvar(fig, destino)
    return ("Concentração de custo (curva de Lorenz)",
            "O gasto total é dominado por uma cauda de execuções caras?",
            "Cada ponto: as N% execuções mais caras e a fatia do gasto que elas levam. A diagonal tracejada é o custo "
            "igual para todas; quanto mais a curva sobe cedo, mais concentrado.",
            "Tokens dos ActionSteps de todas as execuções, com ou sem erro.")


def custo_mensal(execs, destino):
    """O custo por execução cai sozinho, sem memória? Mediana por mês."""
    g = execs[execs.actionsteps.gt(0)].groupby("mes")
    med, n = g.tokens_total.median(), g.size()
    fig, ax = plt.subplots(figsize=(12, 3.8))
    x = np.arange(len(med))
    ax.bar(x, med, color=[BASE if v < MIN_N else BLUE for v in n])
    for i, (v, k) in enumerate(zip(med, n)):
        ax.text(i, v, f"{_n(v)}\nn={_n(k)}", ha="center", va="bottom", fontsize=7, color=INK2)
    ax.set_xticks(x, med.index, rotation=45, ha="right")
    ax.set_ylim(0, med.max() * 1.2)
    ax.set_ylabel("tokens por execução (mediana)")
    _limpar(ax)
    ok = med[n >= MIN_N] if (n >= MIN_N).any() else med
    ax.set_title(f"Custo mediano por execução, por mês: de {_n(ok.iloc[0])} ({ok.index[0]}) a {_n(ok.iloc[-1])} "
                 f"({ok.index[-1]})", loc="left", fontsize=11)
    _salvar(fig, destino)
    return ("Evolução mensal do custo por execução",
            "O custo por execução está caindo sozinho, sem nenhum mecanismo de memória?",
            "Mediana dos tokens por execução no mês; o n é o número de execuções.",
            f"Barras cinza: menos de {MIN_N} execuções. Mudança de mix de papéis muda a mediana sem mudar a eficiência "
            "de nenhum deles.")


def entrada_saida(papel, total_erro, destino, topo=10):
    """O custo do erro é contexto acumulado? A fatia de saída nos passos com erro × em todos."""
    p = papel.sort_values("tokens_total", ascending=False).head(topo)
    fig, ax = plt.subplots(figsize=(11, 0.45 * len(p) + 2.2))
    y = np.arange(len(p))
    ax.barh(y - 0.2, 100 * p.saida_total, height=0.4, color=BLUE, label="em todos os ActionSteps do papel")
    ax.barh(y + 0.2, 100 * p.saida_erro, height=0.4, color=ORANGE, label="nos ActionSteps com erro estruturado")
    ax.set_yticks(y, p.index)
    ax.invert_yaxis()
    ax.set_xlabel("% dos tokens que são de saída")
    ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=4)
    _limpar(ax)
    t, e = total_erro
    ax.set_title(f"Saída no total: {_n(100 * t, 1)}% · nos passos com erro: {_n(100 * e, 1)}% "
                 f"({topo} papéis com mais tokens)", loc="left", fontsize=11)
    _salvar(fig, destino)
    return ("Tokens de entrada × saída",
            "O custo de um erro vem do contexto acumulado (entrada) ou do que o agente gera (saída)?",
            "Para cada papel, a fatia de tokens de saída em todos os passos (azul) e só nos passos com erro "
            "(laranja). Laranja maior: o passo que falha gera mais do que o passo típico do papel.",
            "Passos com erro vêm da fonte (a v2); todos os passos, das contagens. Por unidade, a conta é a do #13.")


def taxa_unidade_mes(upm, tri, mes, destino):
    """O padrão é estável, novo ou terminou — agora em taxa, não em contagem."""
    ordem = tri.sort_values("erros_observaveis", ascending=False).unidade.tolist()
    piv = upm.pivot_table(index="unidade", columns="mes", values="erros", aggfunc="sum", fill_value=0)
    piv = piv.reindex([u for u in ordem if u in piv.index])
    den = mes.actionsteps.reindex(piv.columns)
    taxa = 1000 * piv.div(den, axis=1)
    fig, ax = plt.subplots(figsize=(12, 0.42 * len(taxa) + 1.8))
    ax.imshow(taxa.to_numpy() / taxa.to_numpy().max(axis=1, keepdims=True).clip(min=1e-9), aspect="auto", cmap="Blues")
    for i in range(taxa.shape[0]):
        for j in range(taxa.shape[1]):
            v = taxa.iat[i, j]
            if v > 0:
                ax.text(j, i, _n(v, 1), ha="center", va="center", fontsize=7,
                        color="white" if v / max(taxa.iloc[i].max(), 1e-9) > 0.6 else INK)
    ax.set_xticks(range(taxa.shape[1]), taxa.columns, rotation=45, ha="right")
    ax.set_yticks(range(taxa.shape[0]), taxa.index)
    ax.set_title("Erros por 1.000 ActionSteps do mês, por unidade (cor relativa ao pico de cada linha)",
                 loc="left", fontsize=11)
    _salvar(fig, destino)
    return ("Taxa por unidade e mês",
            "A unidade cresce porque o sistema rodou mais, ou porque o erro ficou mais frequente por passo?",
            "Mesmo desenho do gráfico de contagem por mês, mas cada célula é erros da unidade por 1.000 ActionSteps "
            "do mês. Comparar com a contagem: onde a contagem sobe e a taxa não, foi volume.",
            "O denominador é o mês inteiro (todos os papéis), não só os papéis onde a unidade aparece. Só erros "
            "observáveis (os pendentes não têm unidade).")


def orcamento_papel(papel, tpp, tri, destino, topo=12):
    """Quanto do gasto de cada papel vai para passos com erro, e para que destino."""
    dec = tri.set_index("unidade").decisao
    t = tpp.assign(destino=tpp.unidade.map(dec)).copy()
    grupos = [("candidato observado", "candidata a memória", BLUE), (bp.SINAL_HARNESS, "sinal de harness", ORANGE),
              ("não-memória", "harness / infra", INK2)]
    p = papel.sort_values("tokens_total", ascending=False).head(topo).copy()
    fig, ax = plt.subplots(figsize=(12, 0.45 * len(p) + 2.2))
    esquerda = np.zeros(len(p))
    nos_grupos = np.zeros(len(p))
    for chave, rot, cor in grupos:
        v = t[t.destino.eq(chave)].groupby("role").tokens_n_conhecidos.sum().reindex(p.index).fillna(0).to_numpy()
        ax.barh(p.index, 100 * v / p.tokens_total, left=esquerda, color=cor, label=rot)
        esquerda += 100 * v / p.tokens_total.to_numpy()
        nos_grupos += v
    # o que sobra dos tokens de erro do papel (da fonte): resíduo, crítico, sem recorrência e pendentes (sem unidade)
    resto = (p.tokens_erro.to_numpy() - nos_grupos).clip(min=0)
    ax.barh(p.index, 100 * resto / p.tokens_total, left=esquerda, color=RESIDUO, label="resíduo, crítico ou pendente")
    for i, (tot, er) in enumerate(zip(p.tokens_total, p.tokens_erro)):
        ax.text(100 * er / tot, i, f"  {_n(100 * er / tot, 1)}% de {_n(tot / 1e6, 1)} mi", va="center", fontsize=8,
                color=INK2)
    ax.invert_yaxis()
    ax.set_xlabel("% dos tokens do papel gastos em ActionSteps com erro estruturado")
    ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=4)
    _limpar(ax)
    pior = (p.tokens_erro / p.tokens_total).idxmax()
    ax.set_title(f"Fatia do orçamento de cada papel em erros · maior: {pior} "
                 f"({_n(100 * p.tokens_erro[pior] / p.tokens_total[pior], 1)}%)", loc="left", fontsize=11)
    _salvar(fig, destino)
    return ("Fatia do orçamento de cada papel gasta em erros",
            "Em que papel o erro pesa mais no próprio orçamento — e é erro de memória, de harness ou de infra?",
            f"Os {topo} papéis com mais tokens; cada barra é a fatia dos tokens do papel gasta em passos com erro, "
            "dividida pelo destino da unidade. O rótulo dá a fatia total e o gasto do papel.",
            "É o custo do passo que falhou, não o da recuperação; tokens de erro não são economia garantida. O "
            "destino é o da triagem global da unidade.")


def prioridade(papel, destino, topo=10):
    """A prioridade muda conforme o critério: % do próprio orçamento × volume absoluto."""
    p = papel[papel.execucoes.ge(MIN_N)].copy()
    p["pct"] = p.tokens_erro / p.tokens_total
    sel = p.sort_values("tokens_erro", ascending=False).head(topo)
    r_abs = sel.tokens_erro.rank(ascending=False, method="first")
    r_pct = sel.pct.rank(ascending=False, method="first")
    fig, ax = plt.subplots(figsize=(9, 0.5 * len(sel) + 1.8))
    for nome in sel.index:
        destaque = r_abs[nome] == 1 or r_pct[nome] == 1
        ax.plot([0, 1], [r_pct[nome], r_abs[nome]], color=ORANGE if destaque else BASE, linewidth=2 if destaque else 1)
        ax.text(-0.02, r_pct[nome], f"{nome} {_n(100 * sel.pct[nome], 1)}%", ha="right", va="center", fontsize=8)
        ax.text(1.02, r_abs[nome], f"{nome} {_n(sel.tokens_erro[nome] / 1e6, 1)} mi", ha="left", va="center", fontsize=8)
    ax.set_xlim(-0.6, 1.6)
    ax.invert_yaxis()
    ax.set_xticks([0, 1], ["% do próprio orçamento em erros", "tokens em erros (absoluto)"])
    ax.set_yticks([])
    for lado in ["top", "right", "left"]:
        ax.spines[lado].set_visible(False)
    ax.set_title(f"A prioridade muda conforme o critério ({topo} papéis com mais tokens em erros)", loc="left", fontsize=11)
    _salvar(fig, destino)
    return ("A prioridade muda conforme o critério",
            "O papel que mais desperdiça em números absolutos é o mesmo que mais desperdiça do próprio orçamento?",
            "Cada linha liga a posição do papel nos dois rankings; linhas que cruzam mostram a reordenação. Em "
            "laranja, o primeiro de cada ranking.",
            f"Só papéis com pelo menos {MIN_N} execuções. Tokens do passo com erro, não da recuperação.")
