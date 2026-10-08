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
FIGURAS = [("genealogia_observada.png", "Genealogia: família → assinatura → mecanismo → unidade → destino"),
           ("unidades_observadas.png", "Tokens dos erros por unidade"),
           ("papel_unidade.png", "Erros por papel × unidade")]
MOTIVO = {
    "regra_por_mensagem_elegivel": "regra pela mensagem (inteira)",
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


def figura_cobertura(cob, destino):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from paleta import BASE, BLUE, INK2
    c = cob.assign(motivo=cob.motivo_evidencia.map(lambda m: MOTIVO.get(m, m))).sort_values("erros")
    fig, ax = plt.subplots(figsize=(11, max(3, 0.45 * len(c) + 1)))
    cores = [BLUE if s == "observavel" else BASE for s in c.situacao_mecanismo]
    ax.barh(c.motivo, c.erros, color=cores)
    for i, v in enumerate(c.erros):
        ax.text(v, i, " " + _n(v), va="center", fontsize=9, color=INK2)
    obs = int(cob.loc[cob.situacao_mecanismo.eq("observavel"), "erros"].sum())
    fig.suptitle(f"Cobertura das regras: {_n(obs)} de {_n(cob.erros.sum())} erros estruturados caem numa unidade (azul)\n"
                 "os demais ficam pendentes por falta de dado (cinza)", x=0.01, ha="left", fontsize=11)
    ax.set_xlabel("erros estruturados")
    for lado in ["top", "right"]:
        ax.spines[lado].set_visible(False)
    fig.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def gerar(pasta):
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
        ("Caem numa unidade (observáveis)", f"{_n(r['mecanismos_observaveis'])} ({_n(100 * r['mecanismos_observaveis'] / total_err)}%)"),
        ("Pendentes por falta de dado", f"{_n(r['pendentes'])} ({_n(100 * r['pendentes'] / total_err)}%)"),
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

    figura_cobertura(cob, saida / "cobertura.png")
    figuras = [("cobertura.png", "Cobertura das regras: observável × pendente, por motivo")]
    for nome, titulo in FIGURAS:
        if (pasta / nome).exists():
            shutil.copy2(pasta / nome, saida / nome)
            figuras.append((nome, titulo))

    md = [f"# Painel — base 3, rodada `{pasta.name}`", "",
          f"Fonte: SHA-256 `{m.get('fonte_sha256')}` · contrato `{m.get('contrato_fonte')}` · estado `{m.get('estado')}`.",
          "Gerado por `execucao/painel.py` a partir dos CSVs da rodada (hashes conferidos com o manifesto). "
          "Só contagens; candidata = recorrente o suficiente para minerar, não memória aprovada; sem taxas "
          "(a extração não traz os passos sem erro).", "",
          "## Resumo", "", _tabela(resumo, "ld"), "",
          "## Cobertura das regras", "", _tabela(cobertura, "llddd"), "",
          "![cobertura](cobertura.png)", "",
          "## Triagem", "", _tabela(triagem, "llldddddd"), "",
          "Execuções se sobrepõem entre unidades: não somar a coluna.", ""]
    for nome, titulo in figuras[1:]:
        md += [f"## {titulo}", "", f"![{titulo}]({nome})", ""]
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
