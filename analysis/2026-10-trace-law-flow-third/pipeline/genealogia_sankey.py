"""Gera a figura da genealogia completa dos erros: família → assinatura → mecanismo → unidade → destino.

O último estágio é o DESTINO nomeado — o artefato que nasce de cada unidade:
`MEM <título>` para candidatas a memória, `SINAL-HARNESS <título>` para o erro do
agente cujo conserto a mineração pôs no ambiente, `HARNESS <título>` para correções de
infra, `REVISAR <título>` para o resíduo (falta regra de causa — trabalho de
taxonomia), `FORA <motivo>` para descartes (o prefixo carrega a decisão da triagem,
o título é a lição real de `UNI` em base_pipeline.py — a mesma que já
alimenta `candidatos_memoria.csv`). É 1:1 com `unidade`: nenhuma fusão nova
acontece aqui, só o rótulo humano da lição substitui o id técnico.

Computa as arestas reais (contagem de ERROS por nó e por aresta — não ocorrências;
a triagem continua sendo decidida sobre ocorrências) a partir do base_pipeline
e emite:

1. `assets/09-genealogia-sankey.png`, a figura embutida no doc 09 (§1.1);
2. `pipeline/resultados/genealogia_arestas.csv` com as arestas CRUS
   (granularidade total, nomes originais) — a figura agrega as caudas para
   legibilidade, o CSV não.

Por que PNG e não mais o `sankey-beta` do mermaid: o parser do mermaid não
aceita configurar altura por nó nem espaçamento entre rótulos — com ~50 nós
(5 estágios × até 14 nós) as legendas colidiam. A figura aqui reserva uma
altura mínima por nó (piso de legibilidade, não proporcional ao valor para
os nós minúsculos) e ordena cada coluna por baricentro das arestas de entrada
(o mesmo princípio do d3-sankey) para reduzir cruzamento visual. Cada estágio
soma o total de erros classificados — a figura é uma decomposição de fluxo
completa.

**Árvore de roteamento, sem agregados:** todas as assinaturas e todos os
mecanismos aparecem com o nome, para seguir cada bucket de erro até o mecanismo,
a lição e o destino. **Cor = a família do erro, carregada de ponta a ponta** (a
língua de cor comum das figuras, `COR_ERRO` em paleta.py via
`base_pipeline.categoria_do_erro`): cada fita leva a cor da família dos erros
que passam por ela; roxo = resíduo (nenhuma regra reconheceu a causa); cinzas =
plataforma (harness/infra); preto = erro crítico (Ajuste 10). Um nó que reúne categorias diferentes é desenhado em
fatias, e as fitas saem da fatia da sua categoria. Até 24/09/2026 a cor era
herdada do nó anterior e um agregado cinza ("outros mecanismos") passava o cinza
a tudo que saía dele, inclusive a uma memória candidata. Uso:

    python3 genealogia_sankey.py

Reaproveitamento por outra análise: `ordenar_colunas`, `calcular_ys`,
`centralizar`, `dividir`, `ribbon_path` e o corpo de desenho de `render_png`
não sabem o que é "família" nem "erro" — só consomem `(tot, arestas, comp)`
genéricos (arestas com uma coluna de categoria de cor) e desenham um Sankey de N
colunas com o piso de altura mínima acima.
É o motor reaproveitável se uma análise futura precisar da mesma figura
legível. `preparar_dados`, `NOME_CURTO`/`CURTO_MEM` e o resto do
módulo são específicos desta classificação (`base_pipeline.py`) e não
generalizam. Ainda não foi extraído para um módulo à parte por só ter um
chamador até agora — quando aparecer o segundo, o candidato natural é
`analysis/` (ao lado de `schema-e-taxonomia-de-erros.md`), que também não é
amarrado a um trace específico.
"""

import math
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path

from base_pipeline import carregar_base, triagem, UNI, categoria_do_erro, SINAL_HARNESS, INVESTIGAR_CRITICO
from paleta import COR_ERRO, NOME_ERRO, cor

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTADOS = os.path.join(HERE, "resultados")
ASSETS = os.path.join(HERE, "..", "assets")

NOME_CURTO = {
    "Falha ao indexar o retorno (Could not index)": "Could not index",
    "String não fechada (relatório longo em literal)": "String não fechada",
    "Resposta sem bloco de código (harness)": "Sem bloco de código (harness)",
    "Função ou import bloqueado pelo sandbox": "Função bloqueada",
    "Argumento posicional onde só cabe nomeado": "Arg. posicional",
    "Tipo diferente do esperado": "Tipo diferente",
    "Objeto sem o atributo esperado": "Objeto sem atributo",
    "Variável não definida": "Variável não definida",
    "Módulo usado sem import": "Módulo sem import",
    "Contrato de retorno da ferramenta": "Contrato de retorno",
    "Convenção de chamada de ferramenta": "Convenção de chamada",
    "Ambiente & sandbox": "Ambiente & sandbox",
    "Infra / LLM upstream": "Infra / LLM upstream",
    "Infra / ferramenta": "Infra / ferramenta",
    "Ferramenta excedeu o timeout": "Timeout de ferramenta",
    "Bloco de código excedeu o tempo do interpretador": "Tempo do interpretador",
    "Limite de passos atingido": "Limite de passos",
    "Protocolo do harness": "Protocolo do harness",
    "Erro crítico": "Erro crítico",
    "Suposição sobre estado": "Suposição sobre estado",
    "Suposição sobre dados": "Suposição sobre dados",
}

# rótulo curto do destino final de cada unidade (o nome da memória/correção
# que o erro deve produzir — não o id técnico da unidade). Unidades fora
# deste dicionário caem no nome completo de UNI[u][0] (mais raras: só as
# unidades "fora" — X_causa_nao_identificada, X_sintoma_nao_reconhecido, U_repr_colado — não
# têm entrada aqui).
CURTO_MEM = {
    "U_contrato_dict": "retorno é dict",
    "U_campo_inexistente": "campo inexistente",
    "U_tipo_retorno": "retorno pode ser str",
    "U_texto_literal": "texto fora de literal",
    "U_texto_solto": "nada solto no código",
    "U_arg_nomeado": "só arg. nomeado",
    "U_sandbox": "inventário do sandbox",
    "U_next_gerador": "next() proibido",
    "U_estado_perdido": "redefinir após erro",
    "U_nome_inventado": "não inventar nomes",
    "U_verificacao_existencia": "corrigir a verificação no prompt",
    "U_ferramenta_nao_declarada": "declarar a ferramenta no prompt",
    "H_infra_llm": "retry/backoff LLM",
    "H_timeout_ferramenta": "timeout de ferramenta",
    "U_codigo_lento": "nada de laço pesado no bloco",
    "U_resultado_bruto": "extrair, não entregar o bruto",
    "C_limite_passos": "limite de passos",
    "H_bloco_code": "gatilho bloco de código",
}

STAGES = ["familia", "assinatura", "submecanismo", "unidade", "destino"]
TITULOS = {"familia": "família", "assinatura": "assinatura", "submecanismo": "mecanismo",
           "unidade": "unidade", "destino": "destino"}
PARES = list(zip(STAGES, STAGES[1:]))

# ordem das fatias dentro de cada nó (de cima para baixo) = ordem das categorias de decisão
ORDEM_CAT = list(COR_ERRO)   # famílias do agente, plataforma, resíduo — a ordem da paleta


def preparar_dados():
    B = carregar_base()
    EU = B.EU.copy()
    tri = triagem(EU)
    tri_idx = tri.set_index("unidade")

    def destino(u):
        d = tri_idx.loc[u, "decisão"]
        nome = CURTO_MEM.get(u, UNI[u][0])
        if d == "candidato":
            return f"MEM {nome}"
        if d == SINAL_HARNESS:   # erro do agente; a mineração decidiu que o conserto é no ambiente (Ajuste 5)
            return f"SINAL-HARNESS {nome}"
        if d == INVESTIGAR_CRITICO:   # o agente não se recuperou: investigar o caminho (Ajuste 8)
            return f"CRÍTICO {nome}"
        if d == "não-memória":
            return f"HARNESS {nome}"
        if d.startswith("revisar"):
            return f"REVISAR {nome}"
        return f"FORA {d.split(': ', 1)[1]}"

    EU["destino"] = EU["unidade"].map(destino)
    EU["cat"] = [categoria_do_erro(f, u) for f, u in zip(EU["familia"], EU["unidade"])]
    return EU, tri


def montar_grafo(EU, stages=STAGES):
    pares = list(zip(stages, stages[1:]))
    tot = {c: EU[c].value_counts() for c in stages}

    def fluxo(a, b):
        return EU.groupby([a, b, "cat"], sort=False).size().reset_index(name="n")

    arestas = {par: fluxo(*par) for par in pares}
    comp = {c: EU.groupby([c, "cat"]).size() for c in stages}   # quantos erros de cada decisão em cada nó
    return tot, arestas, comp


def ordenar_colunas(tot, arestas, stages=STAGES):
    """Ordem vertical de cada coluna: 1ª coluna por valor desc.; as demais por
    baricentro das arestas de entrada (média da posição das origens, ponderada
    pelo n da aresta) — mesmo princípio do d3-sankey, reduz cruzamento visual."""
    ordem = {stages[0]: list(tot[stages[0]].sort_values(ascending=False).index)}
    for a, b in zip(stages, stages[1:]):
        pos_a = {n: i for i, n in enumerate(ordem[a])}
        pesos = {}
        for _, r in arestas[(a, b)].iterrows():
            pesos.setdefault(r[b], []).append((pos_a[r[a]], r["n"]))
        bary = {n: sum(p * w for p, w in ws) / sum(w for _, w in ws) for n, ws in pesos.items()}
        ordem[b] = sorted(tot[b].index, key=lambda n: bary.get(n, 0))
    return ordem


def calcular_ys(tot, ordem, min_h, pad, scale, pad_pequeno=None, stages=STAGES):
    """Posição de cada nó; um nó inflado até a altura mínima ganha `pad_pequeno` de folga (o rótulo dele tem a altura
    do próprio nó e encostaria no vizinho)."""
    pad_pequeno = pad if pad_pequeno is None else pad_pequeno
    ys = {}
    for col in stages:
        y = 0.0
        extents = {}
        for nome in ordem[col]:
            h = max(int(tot[col][nome]) * scale, min_h)
            extents[nome] = (y, y + h, h)
            y += h + (pad_pequeno if h <= min_h else pad)
        ys[col] = extents
    return ys


def centralizar(ys):  # as colunas são as chaves de ys
    totais = {col: max(y1 for _, y1, _ in ex.values()) for col, ex in ys.items()}
    maior = max(totais.values())
    for col in ys:
        off = (maior - totais[col]) / 2
        ys[col] = {n: (y0 + off, y1 + off, h) for n, (y0, y1, h) in ys[col].items()}
    return ys, maior


def fatias(col, comp, ys, ordem, ordem_cat=None):
    """(y0, y1) de cada categoria dentro de cada nó da coluna, na ordem ORDEM_CAT, proporcional à contagem."""
    ordem_cat = ORDEM_CAT if ordem_cat is None else ordem_cat
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


def dividir(col_ref, col_outro, arestas_df, fat, ordem):
    """Onde cada fita encosta no nó de col_ref: dentro da fatia da sua categoria e, dentro dela, na ordem dos nós
    de col_outro (é o que evita cruzamento à toa). Chave: (nó de col_ref, nó de col_outro, categoria)."""
    pos_outro = {n: i for i, n in enumerate(ordem[col_outro])}
    segs = {}
    for (nome, c), sub in arestas_df.groupby([col_ref, "cat"], sort=False):
        a0, a1 = fat[nome][c]
        sub = sub.assign(_ord=sub[col_outro].map(pos_outro)).sort_values("_ord")
        total_n, cur = sub["n"].sum(), a0
        for _, r in sub.iterrows():
            seg_h = r["n"] / total_n * (a1 - a0)
            segs[(nome, r[col_outro], c)] = (cur, cur + seg_h)
            cur += seg_h
    return segs


def ribbon_path(x0, y0a, y0b, x1, y1a, y1b):
    xm = (x0 + x1) / 2
    verts = [(x0, y0a), (xm, y0a), (xm, y1a), (x1, y1a),
             (x1, y1b), (xm, y1b), (xm, y0b), (x0, y0b), (x0, y0a)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    return Path(verts, codes)


def _n(v):
    return f"{int(v):,}".replace(",", ".")


def rotulo(col, nome, tot):
    """Nome curto e o número de erros em pt-BR; no mecanismo, o nome legível com o identificador entre parênteses."""
    base = NOME_CURTO.get(nome, nome)
    if col == "submecanismo" and nome in NOME_ERRO:
        base = f"{NOME_ERRO[nome]} ({nome})"
    return f"{base} · {_n(tot[col][nome])}"


def afastar(centros, altura):
    """Posições dos rótulos de uma coluna (na ordem dos nós) sem sobreposição: rótulos que encostam formam um grupo,
    espaçado de `altura` e centrado na média dos seus nós; repete até nenhum grupo encostar no seguinte."""
    grupos = [[c] for c in centros]
    while True:
        topo = [sum(g) / len(g) - (len(g) - 1) * altura / 2 for g in grupos]
        for i in range(len(grupos) - 1):
            if topo[i + 1] - (topo[i] + (len(grupos[i]) - 1) * altura) < altura:
                grupos[i:i + 2] = [grupos[i] + grupos[i + 1]]
                break
        else:
            return [t + k * altura for t, g in zip(topo, grupos) for k in range(len(g))]


def render_png(EU, out_path, titulo=None, juntar_destino=True, inicio=0, paleta=None, ordem_cat=None, nomes_cat=None):
    """`juntar_destino` (decisão D4 de 16/10): unidade e destino são 1 para 1 — a figura desenha uma coluna só,
    "decisão · lição (unidade)"; as arestas gravadas (`montar_grafo` com as 5 colunas) não mudam.

    `inicio`: primeira coluna desenhada (2 = a partir do mecanismo: a figura da decisão, sem o sintoma). `paleta`,
    `ordem_cat` e `nomes_cat`: a cor, a ordem e o nome curto de cada categoria da coluna `cat` (padrão: a família do
    erro); a figura da decisão pinta pelo destino."""
    paleta = COR_ERRO if paleta is None else paleta
    ordem_cat = ORDEM_CAT if ordem_cat is None else ordem_cat
    nomes_cat = NOME_CURTO if nomes_cat is None else nomes_cat
    stages = STAGES[inicio:]
    if juntar_destino:
        EU = EU.assign(unidade=[f"{d} ({u})" if not str(d).startswith("COMPLEMENTAR") else f"pendente: {d.lower()}"
                                for u, d in zip(EU["unidade"], EU["destino"])])
        stages = stages[:-1]
    pares = list(zip(stages, stages[1:]))
    tot, arestas, comp = montar_grafo(EU, stages)
    ordem = ordenar_colunas(tot, arestas, stages)

    maior_valor = max(int(v) for col in stages for v in tot[col].values)
    MIN_H, PAD, PAD_PEQ, ALTURA_ROTULO = 0.16, 0.12, 0.2, 0.25
    scale = 3.4 / maior_valor
    limiar = MIN_H / scale   # abaixo disso, a altura do nó é o piso, não o volume
    ys = calcular_ys(tot, ordem, MIN_H, PAD, scale, PAD_PEQ, stages)
    ys, altura_dados = centralizar(ys)

    fat = {col: fatias(col, comp, ys, ordem, ordem_cat) for col in stages}

    NODE_W = 0.22
    GAP = {"familia": 3.6, "assinatura": 3.6, "submecanismo": 4.9, "unidade": 3.6}   # o mecanismo tem rótulo longo
    X, x = {}, 0.0
    for col in stages:
        X[col] = x
        x += GAP.get(col, 0)

    fig_w, fig_h = 23, altura_dados + 1.6
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    for a, b in pares:
        g = arestas[(a, b)]
        saida = dividir(a, b, g, fat[a], ordem)
        entrada = dividir(b, a, g, fat[b], ordem)
        for (nome_a, nome_b, c), (y0s, y1s) in saida.items():
            y0t, y1t = entrada[(nome_b, nome_a, c)]
            path = ribbon_path(X[a] + NODE_W, y0s, y1s, X[b], y0t, y1t)
            ax.add_patch(mpatches.PathPatch(path, facecolor=cor(paleta, c),
                                             edgecolor="none", alpha=0.42, zorder=1))

    for col in stages:
        nomes = ordem[col]
        centros = [(ys[col][n][0] + ys[col][n][1]) / 2 for n in nomes]
        for nome, centro, y_rot in zip(nomes, centros, afastar(centros, ALTURA_ROTULO)):
            for c, (c0, c1) in fat[col][nome].items():   # o nó em fatias, uma por categoria de erro
                ax.add_patch(mpatches.Rectangle((X[col], c0), NODE_W, c1 - c0, facecolor=cor(paleta, c),
                                                 edgecolor="white", linewidth=0.7, zorder=2))
            x_rot = X[col] + NODE_W + 0.08
            if abs(y_rot - centro) > 0.02:   # rótulo afastado do vizinho: um traço o liga ao nó
                x_rot += 0.25
                ax.plot([X[col] + NODE_W, x_rot - 0.02], [centro, y_rot], color="#52514e", lw=0.6, zorder=3)
            ax.text(x_rot, y_rot, rotulo(col, nome, tot), va="center", ha="left", fontsize=8.3, zorder=4,
                    bbox=dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="white", linewidth=1.2))
        ax.text(X[col] + NODE_W / 2, -0.45, "unidade · destino" if juntar_destino and col == "unidade" else TITULOS[col], ha="center", va="bottom",
                fontsize=11, fontweight="bold", color="#333333")

    ax.set_xlim(-0.2, X[stages[-1]] + NODE_W + 5.6)   # a última coluna leva "decisão · lição (unidade)"
    ax.set_ylim(-0.7, altura_dados + 0.6)
    ax.invert_yaxis()
    ax.axis("off")
    ax.text(0, altura_dados + 0.25, f"Largura das fitas e altura dos nós = número de erros (não tokens), mas só "
            f"acima de ≈ {_n(round(limiar, -1))} erros: um nó menor é desenhado com a altura mínima, para o rótulo caber.",
            fontsize=9, color="#52514e", va="top")
    ax.set_title(titulo or f"Genealogia dos {_n(len(EU))} erros: família → assinatura → mecanismo → unidade → destino  ·  "
                 "cor = família do erro (roxo = resíduo, cinza = plataforma, preto = erro crítico)", fontsize=13, fontweight="bold",
                 pad=14, loc="left")
    presentes = [c for c in ordem_cat if (EU["cat"] == c).any()]
    ax.legend(handles=[mpatches.Patch(color=cor(paleta, c), label=nomes_cat.get(c, c)) for c in presentes],
              loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=math.ceil(len(presentes) / 2), fontsize=9.5,
              frameon=False)
    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=170)
    plt.close(fig)


def main():
    EU, tri = preparar_dados()

    # CSV cru: granularidade total (não agregada), nomes originais
    etapas_raw = [("familia", "assinatura"), ("assinatura", "submecanismo"),
                  ("submecanismo", "unidade"), ("unidade", "destino")]
    csv_rows = []
    for a, b in etapas_raw:
        for (o, d), n in EU.groupby([a, b]).size().items():
            csv_rows.append({"etapa": f"{a}->{b}", "origem": o, "destino": d, "erros": int(n)})
    os.makedirs(RESULTADOS, exist_ok=True)
    pd.DataFrame(csv_rows).to_csv(os.path.join(RESULTADOS, "genealogia_arestas.csv"), index=False)

    out_png = os.path.join(ASSETS, "09-genealogia-sankey.png")
    render_png(EU, out_png)
    print(f"figura: {os.path.relpath(out_png, HERE)}")
    print(f"csv: {os.path.relpath(os.path.join(RESULTADOS, 'genealogia_arestas.csv'), HERE)}")
    for a, b in PARES:
        soma = EU.groupby([a, b]).size().sum()
        print(f"# {a} -> {b}: {soma}")


if __name__ == "__main__":
    main()
