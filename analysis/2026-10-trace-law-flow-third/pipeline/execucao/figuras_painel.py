"""Figuras do painel da base 3, todas calculadas dos CSVs de uma rodada (nada escrito à mão).

Cada função recebe tabelas já lidas (com hash conferido pelo painel.py), desenha uma figura e devolve
(título, pergunta, como ler, limitação) para a seção do painel.md. Títulos com número saem dos dados.
Só contagens, nomes de unidade, de papel e de motivo — nenhum identificador de execução nem texto de caso.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import base_pipeline as bp
from paleta import BASE, BLUE, COR_ERRO, GRID, INK, INK2, MUTED, ORANGE, RESIDUO, cor

DESTINO = [("candidato observado", "candidata a memória", BLUE),
           ("não-memória", "harness / infra (não-memória)", INK2),
           ("investigar — crítico", "crítico (limite de passos)", INK),
           ("revisar", "resíduo (revisar a taxonomia)", RESIDUO),
           ("recorrência não demonstrada", "sem recorrência demonstrada", MUTED),
           ("pendente", "pendente (falta dado na extração)", "#b58a32")]


def _n(v, casas=0):
    s = f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _limpar(ax):
    for lado in ["top", "right"]:
        ax.spines[lado].set_visible(False)


def _cor_unidade(u, familia):
    return cor(COR_ERRO, bp.categoria_do_erro(familia, u))


def _salvar(fig, destino):
    fig.tight_layout()
    fig.savefig(destino, dpi=150, bbox_inches="tight")
    plt.close(fig)


def destinos(tri, cob, destino):
    """1 · Para onde vão os erros e os tokens."""
    linhas = []
    for chave, rotulo, c in DESTINO:
        if chave == "pendente":
            g = cob[cob.situacao_mecanismo.eq("pendente")]
            e, t = g.erros.sum(), g.tokens_n_conhecidos.sum()
        else:
            g = tri[tri.decisao.str.startswith(chave)]
            e, t = g.erros_observaveis.sum(), g.tokens_n_conhecidos.sum()
        linhas.append((rotulo, c, float(e), float(t)))
    tot_e, tot_t = sum(l[2] for l in linhas), sum(l[3] for l in linhas)
    fig, ax = plt.subplots(figsize=(12, 3.6))
    for y, (idx, total, nome) in [(1, (3, tot_t, "tokens")), (0, (2, tot_e, "erros"))]:
        esq = 0.0
        for rot, c, e, t in linhas:
            v = (t if idx == 3 else e) / total * 100
            ax.barh(y, v, left=esq, color=c, edgecolor="white")
            if v >= 4:
                ax.text(esq + v / 2, y, f"{_n(v)}%", ha="center", va="center", color="white", fontsize=9)
            esq += v
    ax.set_yticks([0, 1], [f"erros ({_n(tot_e)})", f"tokens ({_n(tot_t / 1e6, 1)} mi)"])
    ax.set_xlim(0, 100)
    ax.set_xlabel("% do total")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in DESTINO],
              labels=[r for _, r, _ in DESTINO], ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.35),
              frameon=False, fontsize=9)
    cand = linhas[0]
    ax.set_title(f"Para onde vão os erros: {_n(cand[2] / tot_e * 100)}% dos erros e {_n(cand[3] / tot_t * 100)}% "
                 "dos tokens estão em candidatas a memória", loc="left", fontsize=11)
    _limpar(ax)
    _salvar(fig, destino)
    return ("Para onde vão os erros e os tokens",
            "Qual parte do problema é memória, qual é harness e qual a extração não deixa ver?",
            "Duas barras de 100%: em cima os tokens, embaixo os erros, divididos pelo destino da triagem. "
            "A diferença entre as duas barras mostra onde cada erro é mais caro ou mais barato que a média.",
            "Tokens são só os do passo com erro (sem a recuperação). Candidata é recorrência, não memória aprovada.")


def frequencia_custo(tri, destino):
    """2 · Frequência × custo por erro."""
    t = tri[tri.erros_observaveis.gt(0)].copy()
    t["tok_erro"] = t.tokens_n_conhecidos / t.erros_observaveis
    fig, ax = plt.subplots(figsize=(12, 7))
    escala = 1200 / t.execucoes.max()
    for r in t.itertuples():
        ax.scatter(r.erros_observaveis, r.tok_erro / 1e3, s=max(r.execucoes * escala, 15),
                   color=_cor_unidade(r.unidade, r.familia_dominante), alpha=0.75, edgecolor="white")
        ax.annotate(r.unidade, (r.erros_observaveis, r.tok_erro / 1e3), fontsize=8, color=INK2,
                    xytext=(6, 4), textcoords="offset points")
    media = t.tokens_n_conhecidos.sum() / t.erros_observaveis.sum() / 1e3
    ax.set_xscale("log")
    ax.axhline(media, color=MUTED, ls=":", lw=1)
    ax.text(0.01, media, f" média {_n(media, 1)} mil tokens/erro", va="bottom", fontsize=8, color=MUTED,
            transform=ax.get_yaxis_transform())
    ax.set_xlabel("erros observáveis (escala log)")
    ax.set_ylabel("tokens por erro (mil)")
    ax.grid(color=GRID, lw=0.6)
    topo = t.sort_values("tokens_n_conhecidos", ascending=False).iloc[0]
    ax.set_title(f"Frequência × custo por erro · tamanho = execuções · a maior em tokens ({topo.unidade}) custa "
                 f"{_n(topo.tok_erro / 1e3, 1)} mil tokens por erro", loc="left", fontsize=11)
    _limpar(ax)
    _salvar(fig, destino)
    return ("Frequência × custo por erro",
            "Uma unidade pesa em tokens porque é frequente ou porque cada erro é caro?",
            "Mais à direita = mais erros; mais alto = cada erro custa mais tokens. O token de um passo é quase todo "
            "contexto acumulado: alto quer dizer que o erro acontece tarde ou num papel de contexto grande.",
            "Custo é do passo com erro. O peso da entrada no total é hipótese até a conta de tokens de entrada × saída.")


def concentracao_papel(tri, tpp, destino, topo=3):
    """3 · Em quantos papéis mora cada candidata."""
    cand = tri.loc[tri.decisao.eq("candidato observado"), "unidade"].tolist()
    g = tpp[tpp.unidade.isin(cand)]
    tons = ["#1f4e8c", "#4a83c4", "#9cc0e6"]
    fig, ax = plt.subplots(figsize=(12, 0.55 * len(cand) + 1.5))
    for y, u in enumerate(reversed(cand)):
        p = g[g.unidade.eq(u)].sort_values("erros_observaveis", ascending=False)
        tot = p.erros_observaveis.sum()
        esq = 0.0
        for i, r in enumerate(p.head(topo).itertuples()):
            v = r.erros_observaveis / tot * 100
            ax.barh(y, v, left=esq, color=tons[i], edgecolor="white")
            rot = f"{r.role} {_n(v)}%"
            if v >= 0.75 * len(rot):
                ax.text(esq + v / 2, y, rot, ha="center", va="center", color="white", fontsize=8)
            elif v >= 6:
                ax.text(esq + v / 2, y, f"{_n(v)}%", ha="center", va="center", color="white", fontsize=8)
            esq += v
        resto = 100 - esq
        if resto > 0:
            ax.barh(y, resto, left=esq, color=BASE, edgecolor="white")
            if resto >= 12:
                ax.text(esq + resto / 2, y, f"demais {len(p) - topo}", ha="center", va="center",
                        fontsize=8, color=INK2)
        ax.text(101, y, f"{len(p)} {'papel' if len(p) == 1 else 'papéis'} · {_n(tot)} erros", va="center",
                fontsize=8, color=INK2)
    ax.set_yticks(range(len(cand)), list(reversed(cand)))
    ax.set_xlim(0, 125)
    ax.set_xticks(range(0, 101, 25))
    ax.set_xlabel("% dos erros da candidata")
    ax.set_title(f"Em quantos papéis mora cada candidata: os {topo} papéis com mais erros (azul; o nome aparece quando "
                 "cabe) e o resto (cinza)",
                 loc="left", fontsize=11)
    _limpar(ax)
    _salvar(fig, destino)
    return ("Concentração de cada candidata por papel",
            "A lição vale para todos os agentes ou para um papel específico?",
            "Uma barra por candidata. Barra quase toda num azul só = o erro mora num papel: aponta para o prompt ou "
            "as ferramentas desse papel. Barra dividida = o erro é geral.",
            "Contagem, não taxa: um papel que roda mais erra mais em número absoluto. Separar exige o denominador "
            "por papel.")


def papeis_candidatas(tri, tpp, destino, topo=12):
    """4 · Quais papéis concentram os erros das candidatas."""
    cand = tri.loc[tri.decisao.eq("candidato observado"), ["unidade", "familia_dominante"]]
    g = tpp[tpp.unidade.isin(cand.unidade)]
    piv = g.pivot_table(index="role", columns="unidade", values="erros_observaveis", aggfunc="sum", fill_value=0)
    ordem = piv.sum(axis=1).sort_values(ascending=False)
    demais = piv.loc[ordem.index[topo:]].sum()
    piv = piv.loc[ordem.index[:topo]]
    if len(ordem) > topo:
        piv.loc[f"demais {len(ordem) - topo} {'papel' if len(ordem) - topo == 1 else 'papéis'}"] = demais
    piv = piv.iloc[::-1]
    paleta_u = ["#2a78d6", "#eb6834", "#1baf7a", "#e87ba4", "#008300", "#e34948", "#9a6ee0", "#b58a32",
                "#4ab3c8", "#52514e", "#c9a227", "#7a4a2a"]
    cores_u = {u: paleta_u[i % len(paleta_u)] for i, u in enumerate(cand.unidade)}
    fig, ax = plt.subplots(figsize=(12, 0.5 * len(piv) + 2))
    esq = pd.Series(0.0, index=piv.index)
    for u in piv.columns:
        ax.barh(piv.index, piv[u], left=esq, color=cores_u.get(u, BASE), edgecolor="white", label=u)
        esq += piv[u]
    for y, v in enumerate(esq):
        ax.text(v, y, f" {_n(v)}", va="center", fontsize=8, color=INK2)
    total = g.erros_observaveis.sum()
    dois = ordem.head(2)
    ax.set_title(f"Erros das candidatas por papel: os 2 papéis com mais erros ({', '.join(dois.index)}) têm "
                 f"{_n(dois.sum() / total * 100)}% dos {_n(total)}", loc="left", fontsize=11)
    ax.set_xlabel("erros observáveis das candidatas")
    ax.legend(ncol=5, fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    _limpar(ax)
    _salvar(fig, destino)
    return ("Quais papéis concentram os erros das candidatas",
            "O problema está espalhado pela esteira ou em poucos papéis?",
            "Uma barra por papel, dividida pela candidata (uma cor por candidata). Os papéis do topo são onde uma "
            "intervenção (prompt, ferramenta, memória do papel) alcança mais erros.",
            "Contagem, não taxa. Sem o total de passos por papel, um papel grande parece pior do que é.")


def linha_do_tempo(tri, upm, destino):
    """5 · Erros por unidade e mês."""
    ordem = tri.sort_values("erros_observaveis", ascending=False).unidade.tolist()
    piv = upm.pivot_table(index="unidade", columns="mes", values="erros", aggfunc="sum", fill_value=0)
    piv = piv.reindex([u for u in ordem if u in piv.index])
    fig, ax = plt.subplots(figsize=(12, 0.42 * len(piv) + 1.8))
    ax.imshow(piv.to_numpy() / piv.to_numpy().max(axis=1, keepdims=True).clip(min=1), aspect="auto", cmap="Blues")
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.iat[i, j]
            if v:
                ax.text(j, i, _n(v), ha="center", va="center", fontsize=7,
                        color="white" if v / max(piv.iloc[i].max(), 1) > 0.6 else INK)
    ax.set_xticks(range(piv.shape[1]), piv.columns, rotation=45, ha="right")
    ax.set_yticks(range(piv.shape[0]), piv.index)
    meses = piv.gt(0).sum(axis=1)
    pontuais = meses[meses.le(2)].index.tolist()
    extra = f" · em até 2 meses: {', '.join(pontuais)}" if pontuais else ""
    ax.set_title(f"Erros por unidade e mês (cor relativa ao pico de cada linha){extra}", loc="left", fontsize=11)
    _salvar(fig, destino)
    return ("Erros por unidade e mês",
            "O padrão é estável, novo, terminou ou foi um incidente?",
            "Uma linha por unidade, um mês por coluna; a cor é relativa ao maior mês da própria linha. Linha "
            "preenchida = recorrente (\"ainda relevante\"); uma coluna só = surto ou incidente.",
            "Mês de início da execução. Mês com poucos erros pode ser mês com poucas execuções: sem denominador "
            "mensal não dá para separar.")


ROTULO_DEPOIS = [("sem sinal do produtor observado – não sucesso", "sem erro no passo seguinte", "#1baf7a"),
                 ("erro estruturado vinculado", "novo erro (cascata)", ORANGE),
                 ("erro estruturado observado; unidade desconhecida", "novo erro, vínculo não confirmado", "#f2a37f"),
                 ("suspeita observada", "suspeita", "#e87ba4"),
                 ("desconhecido", "sem passo seguinte na janela", BASE)]


def depois_do_erro(perfis, destino):
    """6 · O que vem depois do erro, por candidata (perfis da rodada)."""
    us = list(perfis)
    fig, ax = plt.subplots(figsize=(12, 0.55 * len(us) + 2))
    for y, u in enumerate(reversed(us)):
        d = perfis[u]["depois"].set_index("depois").erros
        tot = d.sum()
        esq = 0.0
        for chave, _, c in ROTULO_DEPOIS:
            v = d.get(chave, 0) / tot * 100
            ax.barh(y, v, left=esq, color=c, edgecolor="white")
            if v >= 7:
                ax.text(esq + v / 2, y, f"{_n(v)}%", ha="center", va="center", fontsize=8, color="white")
            esq += v
        pf = perfis[u]["proximo_final"]
        fin = pf.loc[pf.proximo_final_observado.astype(str).str.lower().eq("true"), "erros"].sum()
        ax.text(101, y, f"seguinte é final: {_n(fin / tot * 100)}%", va="center", fontsize=8, color=INK2)
    ax.set_yticks(range(len(us)), list(reversed(us)))
    ax.set_xlim(0, 125)
    ax.set_xticks(range(0, 101, 25))
    ax.set_xlabel("% dos erros da candidata")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in ROTULO_DEPOIS],
              labels=[r for _, r, _ in ROTULO_DEPOIS], ncol=3, fontsize=8, frameon=False,
              loc="upper center", bbox_to_anchor=(0.5, -0.12))
    ax.set_title("O que vem no passo seguinte ao erro, por candidata", loc="left", fontsize=11)
    _limpar(ax)
    _salvar(fig, destino)
    return ("O que vem depois do erro",
            "O agente se corrige no passo seguinte ou entra em cascata?",
            "Verde = o passo seguinte não tem erro; laranja = o passo seguinte também erra. Muito laranja = o agente "
            "não aprende com a mensagem de erro, e é onde a memória tem mais valor.",
            "\"Sem erro no passo seguinte\" não é sucesso (pode ser outro problema sem erro estruturado). Só a janela "
            "de um passo; o fim da execução não está no arquivo.")


def pendentes(ppm, destino, topo=12):
    """8 · Onde estão os pendentes: por papel e por mês, divididos pelo motivo."""
    from execucao.painel import MOTIVO
    p = ppm.assign(motivo=ppm.motivo_evidencia.map(lambda m: MOTIVO.get(m, m)))
    motivos = p.groupby("motivo").erros.sum().sort_values(ascending=False).index.tolist()
    cores = dict(zip(motivos, ["#b58a32", "#d8b56a", MUTED, BASE, "#6f6a5c", GRID, "#3d3a33"] * 3))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 0.45 * topo + 2.5), gridspec_kw={"width_ratios": [1.2, 1]})
    por_papel = p.pivot_table(index="role", columns="motivo", values="erros", aggfunc="sum", fill_value=0)
    ordem = por_papel.sum(axis=1).sort_values(ascending=False).index
    por_papel = por_papel.loc[ordem[:topo]].iloc[::-1]
    esq = pd.Series(0.0, index=por_papel.index)
    for m in motivos:
        if m in por_papel:
            a1.barh(por_papel.index, por_papel[m], left=esq, color=cores[m], label=m, edgecolor="white")
            esq += por_papel[m]
    a1.set_title(f"Pendentes por papel ({topo} com mais)", loc="left", fontsize=10)
    por_mes = p.pivot_table(index="mes", columns="motivo", values="erros", aggfunc="sum", fill_value=0).sort_index()
    base = pd.Series(0.0, index=por_mes.index)
    for m in motivos:
        if m in por_mes:
            a2.bar(por_mes.index, por_mes[m], bottom=base, color=cores[m], edgecolor="white")
            base += por_mes[m]
    a2.set_title("Pendentes por mês", loc="left", fontsize=10)
    from matplotlib.ticker import MaxNLocator
    a2.yaxis.set_major_locator(MaxNLocator(integer=True))
    a2.tick_params(axis="x", rotation=45)
    a1.legend(fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.9, -0.1), ncol=2)
    total = p.erros.sum()
    topo_papel = p.groupby("role").erros.sum().sort_values(ascending=False)
    fig.suptitle(f"Onde estão os {_n(total)} pendentes: o papel com mais ({topo_papel.index[0]}) tem "
                 f"{_n(topo_papel.iloc[0] / total * 100)}%", x=0.01, ha="left", fontsize=11)
    for a in (a1, a2):
        _limpar(a)
    _salvar(fig, destino)
    return ("Onde estão os pendentes",
            "Os erros que a extração não deixa classificar estão espalhados ou concentrados?",
            "À esquerda por papel, à direita por mês, cada barra dividida pelo motivo da pendência. Concentrado num "
            "papel aponta para o prompt ou o harness desse papel; espalhado aponta para o agente.",
            "Pendente não é resíduo: a regra existe, faltou o dado. A causa só sai da investigação (roadmap #1).")
