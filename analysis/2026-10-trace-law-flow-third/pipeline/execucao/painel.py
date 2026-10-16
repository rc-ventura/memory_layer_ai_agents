"""Painel de uma rodada observada: um MD com as tabelas e as figuras, gerado só dos arquivos da rodada.

Lê `resultados/observada_<id>/` (a mais recente, ou --rodada), confere o hash de cada CSV contra o manifesto e
escreve `<rodada>/painel/` com `painel.md`, as figuras da rodada copiadas e uma figura nova de cobertura.
Todo número e todo texto com número sai dos CSVs — nada escrito à mão. Só contagens, nomes de unidade e motivos:
nenhum identificador de execução nem texto de caso, então o painel pode sair da máquina 2.

Uso, da raiz:  uv run python analysis/2026-10-trace-law-flow-third/pipeline/executar.py painel [--rodada <pasta>]
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import pandas as pd

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import base_pipeline as bp

RESULTADOS = PIPELINE / "resultados"
MOTIVO = {
    "regra_por_mensagem_elegivel": "mensagem de erro inteira basta",
    "sinais_suficientes_para_regra_de_parsing": "sinais suficientes para a regra de código mal formado",
    "proxy_predecessor_estruturado_nao_prova_namespace": "nome não definido com o erro anterior visível na janela",
    "linha_rejeitada_na_mensagem_ou_codigo": "linha rejeitada visível na mensagem ou no código",
    "predecessor_nao_identificado_sql": "nome não definido sem passo anterior identificado",
    "mensagem_limitada_ou_ausente": "mensagem cortada (20.000 caracteres) ou ausente",
    "timeout_requer_prompt_declarado_e_codigo": "timeout sem o prompt e o código que a regra precisa",
    "linha_rejeitada_requer_codigo_integral": "linha rejeitada sem o código inteiro",
    "historico_incompleto_para_excluir_repr_colado": "histórico insuficiente para separar retorno colado",
    "predecessor_numero_ou_chamada_ambiguo": "numeração ambígua do passo anterior",
    "predecessor_com_vinculo_suspenso": "vínculo com o passo anterior suspenso",
    "predecessor_estruturado_sem_ligacao": "passo anterior com erro, sem vínculo confirmado",
    "predecessor_nao_observavel": "passo anterior fora da janela",
    "linha_rejeitada_nao_observavel": "linha rejeitada não observável",
    "repr_colado_exige_destino_no_codigo_integral": "retorno colado exige o código inteiro",
    "destino_final_answer_nao_observavel": "destino da resposta final não observável",
}


def _sha256(path):
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def _rodada(arg):
    if arg:
        return Path(arg)
    manifestos = sorted(RESULTADOS.glob("observada_*/manifesto.json"), key=lambda m: m.stat().st_mtime)
    if not manifestos:
        raise SystemExit("Nenhuma rodada em resultados/ — rode antes: executar.py analisar")
    return manifestos[-1].parent


def ler(pasta, manifesto, nome):
    """CSV da rodada, só se o hash bater com o manifesto (o painel nunca lê um arquivo alterado)."""
    esperado = manifesto["artefatos"].get(nome)
    if esperado is None or _sha256(pasta / nome) != esperado:
        raise SystemExit(f"{nome}: ausente do manifesto ou alterado depois da rodada — painel não gerado.")
    return pd.read_csv(pasta / nome)


def _n(v, casas=0):
    if pd.isna(v):
        return "—"
    s = f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _tabela(df, alinhar):
    cab = "| " + " | ".join(df.columns) + " |"
    sep = "|" + "|".join("---:" if a == "d" else "---" for a in alinhar) + "|"
    linhas = ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join([cab, sep] + linhas)


def figura_cobertura(cob, tri, destino):
    """1 · Cobertura das regras: em quantos erros a regra tem a evidência para decidir (observável) e, desses, quantos
    caem numa unidade reconhecida (o resto é resíduo); os pendentes, por motivo."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    from paleta import BLUE, INK2, MUTED
    from execucao.figuras_painel import _pct
    tot_e, tot_t = float(cob.erros.sum()), float(cob.tokens_n_conhecidos.sum())
    c = cob.assign(motivo=cob.motivo_evidencia.map(lambda m: MOTIVO.get(m, m))).sort_values("erros")
    fig, ax = plt.subplots(figsize=(12, max(3.5, 0.45 * len(c) + 2)))
    ax.barh(c.motivo, c.erros, color=[BLUE if s == "observavel" else MUTED for s in c.situacao_mecanismo])
    for i, (v, t) in enumerate(zip(c.erros, c.tokens_n_conhecidos)):
        ax.text(v, i, f" {_n(v)} ({_pct(100 * v / tot_e)}) · {_n(t / 1e6, 1)} mi tokens", va="center", fontsize=8.5,
                color=INK2)
    ax.set_xlim(0, c.erros.max() * 1.4)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: _n(v)))
    grupos = {}
    for s in ["observavel", "pendente"]:
        g = cob[cob.situacao_mecanismo.eq(s)]
        grupos[s] = (float(g.erros.sum()), float(g.tokens_n_conhecidos.sum()))
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color=MUTED)],
              labels=[f"{nome}: {_n(e)} {'erro' if e == 1 else 'erros'} ({_pct(100 * e / tot_e)}) · {_n(t / 1e6, 1)} mi tokens ({_pct(100 * t / tot_t)})"
                      for nome, (e, t) in [("a regra tem a evidência para decidir", grupos["observavel"]),
                                           ("pendente (faltou dado na extração)", grupos["pendente"])]],
              loc="lower right", frameon=False, fontsize=9)
    obs = grupos["observavel"][0]
    res = float(tri.loc[tri.unidade.str.startswith("X_"), "erros_observaveis"].sum())
    fig.suptitle(f"Cobertura das regras: a regra tem a evidência para decidir em {_n(obs)} de {_n(tot_e)} erros "
                 f"({_pct(100 * obs / tot_e)})\n{_n(obs - res)} ({_pct(100 * (obs - res) / tot_e)}) caem numa unidade "
                 f"reconhecida; {_n(res)} são resíduo (nenhuma regra reconheceu a causa)", x=0.01, ha="left", fontsize=11)
    ax.set_xlabel("erros estruturados")
    for lado in ["top", "right"]:
        ax.spines[lado].set_visible(False)
    fig.tight_layout()
    fig.savefig(destino, dpi=150, bbox_inches="tight")
    plt.close(fig)


def gerar(pasta, gasto_total=None):
    """`gasto_total`: os tokens de todos os ActionSteps do sistema (das contagens, pelo relatório único); sem ele, o
    gráfico de destinos fica só com a base dos tokens dos erros."""
    pasta = Path(pasta)
    m = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
    if m.get("estado") != "concluida_tecnicamente_sem_aprovacao_semantica":
        raise SystemExit("Rodada não concluída — painel não gerado.")
    tri = ler(pasta, m, "triagem_visivel_observada.csv")
    sens = ler(pasta, m, "triagem_sensibilidade.csv")
    cob = ler(pasta, m, "cobertura_mecanismos.csv")
    r = m["resumo"]
    saida = pasta / "painel"
    saida.mkdir(exist_ok=True)

    total_err, total_tok = int(cob.erros.sum()), float(cob.tokens_n_conhecidos.sum())
    obs = cob.situacao_mecanismo.eq("observavel")
    cand = tri[tri.decisao.eq("candidato observado")]
    firmes = set(sens.loc[sens.decisao.eq("candidato observado"), "unidade"])
    residuo = tri[tri.unidade.str.startswith("X_")]

    resumo = pd.DataFrame([
        ("Erros estruturados", _n(r["erros_estruturados"])),
        ("Suspeitas da query (fora da taxonomia)", _n(r.get("suspeitas_fora_taxonomia"))),
        ("A regra tem a evidência para decidir (observáveis)", f"{_n(r['mecanismos_observaveis'])} ({_n(100 * r['mecanismos_observaveis'] / total_err, 1)}%)"),
        ("… caem numa unidade reconhecida (sem o resíduo)", f"{_n(r['mecanismos_observaveis'] - residuo.erros_observaveis.sum())} "
                                                           f"({_n(100 * (r['mecanismos_observaveis'] - residuo.erros_observaveis.sum()) / total_err, 1)}%)"),
        ("Pendentes por falta de dado", f"{_n(r['pendentes'])} ({_n(100 * r['pendentes'] / total_err, 1)}%)"),
        ("Unidades observáveis", _n(r["unidades_observaveis"])),
        ("Candidatas a memória (≥3 execuções, ≥2 meses)", _n(len(cand))),
        ("… que passam também na régua estrita (≥5, ≥3)", _n(len(firmes & set(cand.unidade)))),
        ("Tokens em todos os erros estruturados", f"{_n(total_tok / 1e6, 1)} mi"),
        ("Tokens dos erros das candidatas", f"{_n(cand.tokens_n_conhecidos.sum() / 1e6, 1)} mi "
                                            f"({_n(100 * cand.tokens_n_conhecidos.sum() / total_tok)}%)"),
        ("Resíduo (causa ou sintoma não reconhecidos)", f"{_n(residuo.erros_observaveis.sum())} "
                                                       f"({_n(100 * residuo.erros_observaveis.sum() / total_err, 1)}% dos erros)"),
    ], columns=["Medida", "Valor"])

    c = cob.sort_values(["situacao_mecanismo", "erros"], ascending=[True, False])
    cobertura = pd.DataFrame({
        "Situação": c.situacao_mecanismo.map({"observavel": "observável", "pendente": "pendente"}),
        "Motivo": c.motivo_evidencia.map(lambda x: MOTIVO.get(x, x)),
        "Erros": c.erros.map(_n),
        "% dos erros": (100 * c.erros / total_err).map(lambda v: _n(v, 1)),
        "Tokens (mi)": (c.tokens_n_conhecidos / 1e6).map(lambda v: _n(v, 1))})

    t = tri.copy()
    triagem = pd.DataFrame({
        "Unidade": "`" + t.unidade + "`",
        "Lição": t.unidade.map(lambda u: bp.UNI[u][0]),
        "Decisão": [d + (" (régua estrita: não)" if d == "candidato observado" and u not in firmes else "")
                    for d, u in zip(t.decisao, t.unidade)],
        "Erros": t.erros_observaveis.map(_n), "Execuções": t.execucoes.map(_n), "Meses": t.meses.map(_n),
        "Papéis": t.papeis.map(_n), "Tokens (mi)": (t.tokens_n_conhecidos / 1e6).map(lambda v: _n(v, 1)),
        "% tokens": (100 * t.tokens_n_conhecidos / total_tok).map(lambda v: _n(v, 1))})

    figura_cobertura(cob, tri, saida / "cobertura.png")

    md = [f"# Painel — base 3, rodada `{pasta.name}`", "",
          f"Fonte: SHA-256 `{m.get('fonte_sha256')}` · contrato `{m.get('contrato_fonte')}` · estado `{m.get('estado')}`.",
          "Gerado por `execucao/painel.py` a partir dos CSVs da rodada (hashes conferidos com o manifesto). "
          "Só contagens; candidata = recorrente o suficiente para minerar, não memória aprovada. Sem taxas aqui: "
          "elas precisam das contagens do pedido A e saem em `taxas/` e no relatório único (`executar.py relatorio`).", "",
          "## Resumo", "", _tabela(resumo, "ld"), "",
          "## Cobertura das regras", "", _tabela(cobertura, "llddd"), "",
          "![cobertura](cobertura.png)", "",
          "## Triagem", "", _tabela(triagem, "llldddddd"), "",
          "Execuções se sobrepõem entre unidades: não somar a coluna.", ""]

    # Gráficos de leitura: cada um responde a uma pergunta; os que dependem de tabela ausente são pulados com o motivo.
    # Ordem e conteúdo: auditoria da parte 1 (roadmap b3 #40). Cortados por "um insight por gráfico": os papéis das
    # candidatas (o total por papel foi para a margem do papel × unidade) e a contagem por unidade e mês (virou o painel
    # esquerdo da taxa por unidade e mês, na parte 2).
    import execucao.figuras_painel as fp
    tpp = ler(pasta, m, "triagem_por_papel.csv")
    graficos, pulados = [], []
    if (pasta / "genealogia_observada.png").exists() and "genealogia_observada.png" in m["artefatos"]:
        shutil.copy2(pasta / "genealogia_observada.png", saida / "genealogia_observada.png")
        graficos.append(("genealogia_observada.png", lambda d: fp.genealogia()))
    graficos.append(("unidades_observadas.png", lambda d: fp.tokens_unidade(tri, cob, d)))
    upt = (ler(pasta, m, "consolidacao_unidade_papel_tokens.csv")
           if "consolidacao_unidade_papel_tokens.csv" in m["artefatos"] else None)
    if upt is not None:
        graficos.append(("papel_unidade.png", lambda d: fp.papel_unidade(upt, tpp, tri, d)))
    else:
        pulados.append("Erros por papel × unidade e concentração por papel: a rodada não tem "
                       "`consolidacao_unidade_papel_tokens.csv` (tabela de 15/10; rode `executar.py analisar` de novo).")
    graficos += [("destinos.png", lambda d: fp.destinos(tri, cob, d, gasto_total)),
                 ("unidades_destino_tipo.png", lambda d: fp.unidades_destino_tipo(tri, d)),
                 ("frequencia_custo.png", lambda d: fp.frequencia_custo(tri, d))]
    if upt is not None:
        graficos.append(("concentracao_papel.png", lambda d: fp.concentracao_papel(upt, tri, d)))
    if "consolidacao_depois_unidade.csv" in m["artefatos"]:
        dep = ler(pasta, m, "consolidacao_depois_unidade.csv")
    else:   # rodada de antes de 16/10: só as candidatas, pelos perfis
        perfis = {u: ler(pasta, m, f"perfis/{u}/casos.csv")[["depois", "proximo_final_observado"]]
                  for u in cand.unidade if f"perfis/{u}/casos.csv" in m["artefatos"]}
        dep = fp.depois_de_perfis(perfis) if perfis else None
    if dep is not None and len(dep):
        graficos.append(("depois_do_erro.png", lambda d: fp.depois_do_erro(dep, tri, d)))
    else:
        pulados.append("O que vem depois do erro: a rodada não tem `consolidacao_depois_unidade.csv` nem perfis.")
    if "consolidacao_pendencias_papel_mes.csv" in m["artefatos"]:
        ppm = ler(pasta, m, "consolidacao_pendencias_papel_mes.csv")
        meses = (ler(pasta, m, "consolidacao_unidade_papel_mes.csv").mes.unique().tolist()
                 if "consolidacao_unidade_papel_mes.csv" in m["artefatos"] else [])
        if len(ppm):
            graficos.append(("pendentes.png", lambda d: fp.pendentes(ppm, meses, total_err, total_tok, d)))
    else:
        pulados.append("Onde estão os pendentes: a rodada não tem `consolidacao_pendencias_papel_mes.csv` "
                       "(gerado a partir de 09/10; rode `executar.py analisar` de novo).")
    md += ["# Leituras", ""]
    for nome, desenhar in graficos:
        titulo, pergunta, ler_como, limite = desenhar(saida / nome)
        md += [f"## {titulo}", "", f"**Pergunta:** {pergunta}", "", f"![{titulo}]({nome})", "",
               f"**Como ler:** {ler_como}", "", f"**Limitação:** {limite}", ""]
    if dep is not None and dep.depois.eq("erro estruturado vinculado").any():
        v = dep[dep.depois.eq("erro estruturado vinculado")]
        tot_u = dep.groupby("unidade").erros.sum()
        tr = v.groupby(["unidade", "unidade_seguinte"]).erros.sum().sort_values(ascending=False).head(15).reset_index()
        if len(tr):
            md += ["## As transições mais frequentes (o erro seguinte, com vínculo confirmado)", "",
                   "Sequência, não causa. A matriz inteira: `consolidacao_depois_unidade.csv`.", "",
                   _tabela(pd.DataFrame({"Erro": tr.unidade, "Erro seguinte": tr.unidade_seguinte,
                                         "Erros": tr.erros.map(_n),
                                         "% dos erros da unidade": (100 * tr.erros / tr.unidade.map(tot_u)).map(lambda x: _n(x, 1))}),
                           "lldd"), ""]
    if pulados:
        md += ["## Gráficos não gerados nesta rodada", ""] + [f"- {x}" for x in pulados] + [""]
    (saida / "painel.md").write_text("\n".join(md), encoding="utf-8")
    return saida


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rodada", type=Path)
    args = p.parse_args(argv)
    saida = gerar(_rodada(args.rodada))
    print("Painel:", saida / "painel.md")
    print("Arquivos:", ", ".join(sorted(f.name for f in saida.iterdir())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
