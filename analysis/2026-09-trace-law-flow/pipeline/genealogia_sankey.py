"""Gera a figura da genealogia completa dos erros: família → assinatura → mecanismo → unidade → destino.

O último estágio é o DESTINO nomeado — o artefato que nasce de cada unidade:
`MEM <título>` para candidatas a memória, `HARNESS <título>` para correções de
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

**Cor = onde o erro termina** (a decisão da triagem, `COR_DECISAO` em paleta.py —
a mesma linguagem do gráfico 9.3): memória factual, memória de estratégia,
não-memória, revisar, fora. Cada fita e cada fatia de nó leva a cor da decisão
dos erros que passam por ela; um nó que reúne erros de destinos diferentes é
desenhado em fatias, uma por decisão, e as fitas saem da fatia da sua decisão.
Família, assinatura e mecanismo são identificados pelo nome escrito, não pela
cor. Até 24/09/2026 a cor era a da família de origem, herdada para a direita;
um agregado cinza ("outros mecanismos") passava o cinza a tudo que saía dele,
inclusive a uma memória candidata. Uso:

    python3 genealogia_sankey.py

Reaproveitamento por outra análise: `ordenar_colunas`, `calcular_ys`,
`centralizar`, `dividir`, `ribbon_path` e o corpo de desenho de `render_png`
não sabem o que é "família" nem "erro" — só consomem `(tot, arestas, comp)`
genéricos (arestas com uma coluna de categoria de cor) e desenham um Sankey de N
colunas com o piso de altura mínima acima.
É o motor reaproveitável se uma análise futura precisar da mesma figura
legível. `preparar_dados`, `KEEP_SIG`/`KEEP_MEC`/`CURTO_MEM` e o resto do
módulo são específicos desta classificação (`base_pipeline.py`) e não
generalizam. Ainda não foi extraído para um módulo à parte por só ter um
chamador até agora — quando aparecer o segundo, o candidato natural é
`analysis/` (ao lado de `schema-e-taxonomia-de-erros.md`), que também não é
amarrado a um trace específico.
"""

import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path

from base_pipeline import carregar_base, triagem, UNI, CATEGORIAS_DECISAO, categoria_decisao
from paleta import COR_DECISAO

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTADOS = os.path.join(HERE, "resultados")
ASSETS = os.path.join(HERE, "..", "assets")

# nós mantidos explícitos na figura: os maiores + os protagonistas da
# narrativa (divide "Could not index"; funde dict_iterado/modulo_sem_import;
# aresta cruzada nome_nunca_definido). O resto vira "outras/outros".
KEEP_SIG = {
    "String não fechada (relatório longo em literal)",
    "Falha ao indexar o retorno (Could not index)",
    "Sintaxe inválida",
    "Argumento posicional onde só cabe nomeado",
    "Resposta sem bloco de código (harness)",
    "Tipo diferente do esperado",
    "Função ou import bloqueado pelo sandbox",
    "Objeto sem o atributo esperado",
    "Variável não definida",
    "Módulo usado sem import",
}
KEEP_MEC = {
    "texto_em_literal",
    "dict_indexado_por_posicao",
    "tipo_real_do_retorno",
    "argumento_posicional",
    "harness_bloco_code",
    "texto_solto_no_codigo",
    "next_sobre_gerador",
    "inventario_sandbox",
    "campo_inexistente_no_retorno",
    "dict_iterado_como_lista",
    "modulo_sem_import",
    "nome_nunca_definido",
}
OUTROS_SIG, OUTROS_MEC = "outras assinaturas", "outros mecanismos"

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
    "Protocolo do harness": "Protocolo do harness",
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
    "H_infra_llm": "retry/backoff LLM",
    "H_bloco_code": "gatilho bloco de código",
}

STAGES = ["familia", "sig_disp", "mec_disp", "unidade", "destino"]
TITULOS = {"familia": "família", "sig_disp": "assinatura", "mec_disp": "mecanismo",
           "unidade": "unidade", "destino": "destino"}
PARES = list(zip(STAGES, STAGES[1:]))

# ordem das fatias dentro de cada nó (de cima para baixo) = ordem das categorias de decisão
ORDEM_CAT = CATEGORIAS_DECISAO


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
        if d == "não-memória":
            return f"HARNESS {nome}"
        if d.startswith("revisar"):
            return f"REVISAR {nome}"
        return f"FORA {d.split(': ', 1)[1]}"

    EU["destino"] = EU["unidade"].map(destino)
    EU["cat"] = [categoria_decisao(tri_idx.loc[u, "decisão"], UNI[u][1]) for u in EU["unidade"]]
    EU["sig_disp"] = EU["assinatura"].map(lambda s: s if s in KEEP_SIG else OUTROS_SIG)
    EU["mec_disp"] = EU["submecanismo"].map(lambda s: s if s in KEEP_MEC else OUTROS_MEC)
    return EU, tri


def montar_grafo(EU):
    tot = {c: EU[c].value_counts() for c in STAGES}

    def fluxo(a, b):
        return EU.groupby([a, b, "cat"], sort=False).size().reset_index(name="n")

    arestas = {par: fluxo(*par) for par in PARES}
    comp = {c: EU.groupby([c, "cat"]).size() for c in STAGES}   # quantos erros de cada decisão em cada nó
    return tot, arestas, comp


def ordenar_colunas(tot, arestas):
    """Ordem vertical de cada coluna: 1ª coluna por valor desc.; as demais por
    baricentro das arestas de entrada (média da posição das origens, ponderada
    pelo n da aresta) — mesmo princípio do d3-sankey, reduz cruzamento visual."""
    ordem = {STAGES[0]: list(tot[STAGES[0]].sort_values(ascending=False).index)}
    for a, b in PARES:
        pos_a = {n: i for i, n in enumerate(ordem[a])}
        pesos = {}
        for _, r in arestas[(a, b)].iterrows():
            pesos.setdefault(r[b], []).append((pos_a[r[a]], r["n"]))
        bary = {n: sum(p * w for p, w in ws) / sum(w for _, w in ws) for n, ws in pesos.items()}
        ordem[b] = sorted(tot[b].index, key=lambda n: bary.get(n, 0))
    return ordem


def calcular_ys(tot, ordem, min_h, pad, scale):
    ys = {}
    for col in STAGES:
        y = 0.0
        extents = {}
        for nome in ordem[col]:
            h = max(int(tot[col][nome]) * scale, min_h)
            extents[nome] = (y, y + h, h)
            y += h + pad
        ys[col] = extents
    return ys


def centralizar(ys):
    totais = {col: max(y1 for _, y1, _ in ex.values()) for col, ex in ys.items()}
    maior = max(totais.values())
    for col in STAGES:
        off = (maior - totais[col]) / 2
        ys[col] = {n: (y0 + off, y1 + off, h) for n, (y0, y1, h) in ys[col].items()}
    return ys, maior


def fatias(col, comp, ys, ordem):
    """(y0, y1) de cada categoria dentro de cada nó da coluna, na ordem ORDEM_CAT, proporcional à contagem."""
    saida = {}
    for nome in ordem[col]:
        y0, _, h = ys[col][nome]
        cont = comp[col].loc[nome]
        total, cur, d = cont.sum(), y0, {}
        for c in ORDEM_CAT:
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


def rotulo(col, nome, tot):
    base = NOME_CURTO.get(nome, nome)
    return f"{base} · {int(tot[col][nome])}"


def render_png(EU, out_path):
    tot, arestas, comp = montar_grafo(EU)
    ordem = ordenar_colunas(tot, arestas)

    maior_valor = max(int(v) for col in STAGES for v in tot[col].values)
    MIN_H, PAD = 0.16, 0.12
    scale = 3.4 / maior_valor
    ys = calcular_ys(tot, ordem, MIN_H, PAD, scale)
    ys, altura_dados = centralizar(ys)

    fat = {col: fatias(col, comp, ys, ordem) for col in STAGES}

    X_STEP, NODE_W = 3.6, 0.22
    X = {col: i * X_STEP for i, col in enumerate(STAGES)}

    fig_w, fig_h = 21.5, altura_dados + 1.6
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    for a, b in PARES:
        g = arestas[(a, b)]
        saida = dividir(a, b, g, fat[a], ordem)
        entrada = dividir(b, a, g, fat[b], ordem)
        for (nome_a, nome_b, c), (y0s, y1s) in saida.items():
            y0t, y1t = entrada[(nome_b, nome_a, c)]
            path = ribbon_path(X[a] + NODE_W, y0s, y1s, X[b], y0t, y1t)
            ax.add_patch(mpatches.PathPatch(path, facecolor=COR_DECISAO[c],
                                             edgecolor="none", alpha=0.42, zorder=1))

    for col in STAGES:
        for nome, (y0, y1, h) in ys[col].items():
            for c, (c0, c1) in fat[col][nome].items():   # o nó em fatias, uma por decisão
                ax.add_patch(mpatches.Rectangle((X[col], c0), NODE_W, c1 - c0, facecolor=COR_DECISAO[c],
                                                 edgecolor="white", linewidth=0.7, zorder=2))
            texto = rotulo(col, nome, tot)
            ax.text(X[col] + NODE_W + 0.08, (y0 + y1) / 2, texto, va="center", ha="left",
                    fontsize=8.3, zorder=3,
                    bbox=dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="none", alpha=0.75))
        ax.text(X[col] + NODE_W / 2, -0.45, TITULOS[col], ha="center", va="bottom",
                fontsize=11, fontweight="bold", color="#333333")

    ax.set_xlim(-0.2, X[STAGES[-1]] + NODE_W + 3.6)
    ax.set_ylim(-0.7, altura_dados + 0.3)
    ax.invert_yaxis()
    ax.axis("off")
    ax.set_title(f"Genealogia dos {len(EU)} erros: família → assinatura → mecanismo → unidade → destino  ·  "
                 "cor = onde o erro termina", fontsize=13, fontweight="bold", pad=14, loc="left")
    presentes = [c for c in ORDEM_CAT if (EU["cat"] == c).any()]
    ax.legend(handles=[mpatches.Patch(color=COR_DECISAO[c], label=c) for c in presentes],
              loc="upper right", bbox_to_anchor=(1.0, 1.02), ncol=len(presentes), fontsize=9.5, frameon=False)
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
