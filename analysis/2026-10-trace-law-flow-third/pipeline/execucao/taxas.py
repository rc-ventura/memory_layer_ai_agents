"""Taxas e custo de uma rodada observada, com o denominador do pedido A (roadmap b3 #32).

Junta três fontes, cada uma conferida antes de qualquer conta:
- a rodada (`resultados/observada_<id>/`): os CSVs lidos com o hash conferido contra o manifesto (o `ler` do painel);
- a fonte da rodada (a v2): o arquivo tem de ter o SHA-256 que o manifesto registra; dele saem erros e tokens por chave;
- as contagens (`base_contagens.parquet`, o pedido A): uma linha por execução, agente e papel, com o total de
  ActionSteps e de tokens de todas as execuções, com ou sem erro.
A junção é uma trava: chave duplicada nas contagens, chave da fonte ausente nelas, erros ou suspeitas diferentes por
chave, tokens dos erros acima dos do papel, ou somas diferentes das do manifesto — nada é gerado e o motivo sai na
mensagem. Escreve `<rodada>/taxas/`: `taxas.md`, as figuras `taxas_*.png`, as tabelas e `manifesto_taxas.json` (com os
hashes da rodada, da fonte e das contagens). Só contagens, nomes de papel, de unidade e meses — nenhum identificador
de execução nem texto de caso.

Uso, da raiz:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/executar.py taxas [--rodada <pasta>] [--contagens <parquet>] [--fonte <parquet>]
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import base_pipeline as bp
from execucao.painel import _n, _rodada, _sha256, _tabela, ler

CONTAGENS = PIPELINE.parent / "data" / "base_contagens.parquet"
CHAVE = ["cod_idef_exeo", "cod_idef_aget", "papel"]
COLUNAS_FONTE = CHAVE + ["structured_error", "observation_suspect", "total_tokens", "output_tokens"]


class TravaTaxas(RuntimeError):
    """A junção fonte × contagens não confere: nenhuma taxa sai."""


def _chave(df):
    out = df.copy()
    for c in CHAVE:
        out[c] = out[c].astype(str)
    return out


def _num(df, cols):
    for c in cols:
        df[c] = pd.to_numeric(df[c])
    return df


def conferir_juncao(fonte, cont, resumo):
    """As verificações da junção (nome → bool). Levanta TravaTaxas, com a lista das que falharam, se alguma falhar."""
    g = fonte.assign(tok_erro=fonte.total_tokens.where(fonte.structured_error.eq(1), 0)).groupby(CHAVE).agg(
        erros=("structured_error", "sum"), suspeitas=("observation_suspect", "sum"), tok_erro=("tok_erro", "sum"))
    c = cont.set_index(CHAVE)
    junto = g.join(c[["qtd_erros_estruturados", "qtd_suspeitas_observadas", "tokens_total"]], how="left")
    v = {
        "chaves_unicas_nas_contagens": not cont.duplicated(CHAVE).any(),
        "toda_chave_da_fonte_nas_contagens": bool(junto.qtd_erros_estruturados.notna().all()),
        "erros_iguais_por_chave": bool(junto.erros.eq(junto.qtd_erros_estruturados).all()),
        "suspeitas_iguais_por_chave": bool(junto.suspeitas.eq(junto.qtd_suspeitas_observadas).all()),
        "tokens_dos_erros_dentro_do_papel": bool(junto.tok_erro.le(junto.tokens_total).all()),
        "erros_somam_o_manifesto": int(cont.qtd_erros_estruturados.sum()) == int(resumo["erros_estruturados"]),
        "suspeitas_somam_o_manifesto": int(cont.qtd_suspeitas_observadas.sum())
                                       == int(resumo.get("suspeitas_fora_taxonomia", -1)),
    }
    falhas = [k for k, ok in v.items() if not ok]
    if falhas:
        raise TravaTaxas("junção fonte × contagens não confere: " + ", ".join(falhas))
    return v


def carregar(pasta, contagens, fonte):
    pasta = Path(pasta)
    m = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
    if m.get("estado") != "concluida_tecnicamente_sem_aprovacao_semantica":
        raise TravaTaxas("rodada não concluída")
    fonte, contagens = Path(fonte or bp.TRACE), Path(contagens or CONTAGENS)
    for nome, arq in [("fonte", fonte), ("contagens", contagens)]:
        if not arq.is_file():
            raise TravaTaxas(f"{nome} não encontrada: {arq.name}")
    sha_fonte = _sha256(fonte)
    if m.get("fonte_sha256") and sha_fonte != m["fonte_sha256"]:
        raise TravaTaxas("a fonte não é a da rodada (SHA-256 diferente do manifesto)")
    f = _num(_chave(pq.read_table(fonte, columns=COLUNAS_FONTE).to_pandas()),
             ["structured_error", "observation_suspect", "total_tokens", "output_tokens"])
    c = _num(_chave(pq.read_table(contagens).to_pandas()),
             ["qtd_actionsteps", "tokens_entrada", "tokens_saida", "tokens_total", "qtd_erros_estruturados",
              "qtd_suspeitas_observadas"])
    return m, f, c, sha_fonte, _sha256(contagens)


def tabelas(f, c):
    """Execução, mês e papel, com o denominador; nada de identificador sai daqui (as tabelas gravadas não têm chave).

    A taxa é a de TODOS os erros estruturados (decisão de 15/10, "erro é erro"): nenhuma separação por destino aqui."""
    sem = c.qtd_actionsteps.isna()
    ok = c[~sem]
    execs = ok.groupby(["cod_idef_exeo", "cod_idef_aget"]).agg(
        actionsteps=("qtd_actionsteps", "sum"), erros=("qtd_erros_estruturados", "sum"),
        suspeitas=("qtd_suspeitas_observadas", "sum"), tokens_total=("tokens_total", "sum"),
        mes=("mes_execucao", "first")).reset_index(drop=True)
    mes = ok.groupby("mes_execucao").agg(actionsteps=("qtd_actionsteps", "sum"), erros=("qtd_erros_estruturados", "sum"),
                                          tokens_total=("tokens_total", "sum"))
    mes["execucoes"] = execs.groupby("mes").size()
    mes.index.name = "mes"
    mes["taxa"] = mes.erros / mes.actionsteps
    com_passo = execs[execs.actionsteps.gt(0)].groupby("mes").tokens_total
    mes["mediana_tokens_execucao"], mes["media_tokens_execucao"] = com_passo.median(), com_passo.mean()
    papel = ok.groupby("papel").agg(execucoes=("cod_idef_exeo", "size"), actionsteps=("qtd_actionsteps", "sum"),
                                    erros=("qtd_erros_estruturados", "sum"), tokens_total=("tokens_total", "sum"),
                                    tokens_saida=("tokens_saida", "sum"))
    e = f[f.structured_error.eq(1)]
    pe = e.groupby("papel").agg(tokens_erro=("total_tokens", "sum"), saida_erro_tok=("output_tokens", "sum"))
    papel = papel.join(pe, how="left").fillna({"tokens_erro": 0, "saida_erro_tok": 0})
    papel["taxa"] = papel.erros / papel.actionsteps.where(papel.actionsteps.gt(0))
    papel["saida_total"] = papel.tokens_saida / papel.tokens_total.where(papel.tokens_total.gt(0))
    papel["saida_erro"] = papel.saida_erro_tok / papel.tokens_erro.where(papel.tokens_erro.gt(0))
    total_erro = (ok.tokens_saida.sum() / ok.tokens_total.sum(), e.output_tokens.sum() / e.total_tokens.sum())
    # custo por papel: cada linha (execução, agente, papel) com passo, com × sem erro — mediana, média e p90
    lin = ok[ok.qtd_actionsteps.gt(0)].assign(grupo=lambda d: d.qtd_erros_estruturados.gt(0).map({True: "com_erro",
                                                                                                    False: "sem_erro"}))
    custo_papel = lin.groupby(["papel", "grupo"]).agg(
        n=("tokens_total", "size"), mediana_tokens=("tokens_total", "median"), media_tokens=("tokens_total", "mean"),
        p90_tokens=("tokens_total", lambda x: x.quantile(0.9)), mediana_passos=("qtd_actionsteps", "median"),
        media_passos=("qtd_actionsteps", "mean")).unstack("grupo")
    custo_papel.columns = [f"{a}_{b}" for a, b in custo_papel.columns]
    extra = {"linhas_zero_passos": int(ok.qtd_actionsteps.eq(0).sum())}
    return execs, mes, papel, total_erro, int(sem.sum()), custo_papel.reset_index(), extra


def gerar(pasta, contagens=None, fonte=None):
    import execucao.figuras_taxas as ft
    pasta = Path(pasta)
    m, f, c, sha_fonte, sha_cont = carregar(pasta, contagens, fonte)
    verif = conferir_juncao(f, c, m["resumo"])
    tri = ler(pasta, m, "triagem_visivel_observada.csv")
    opc = lambda nome: ler(pasta, m, nome) if nome in m["artefatos"] else None
    upm, ppm = opc("consolidacao_unidade_papel_mes.csv"), opc("consolidacao_pendencias_papel_mes.csv")
    upt = opc("consolidacao_unidade_papel_tokens.csv")
    execs, mes, papel, total_erro, sem_contagem, custo_papel, extra = tabelas(f, c)
    saida = pasta / "taxas"
    saida.mkdir(exist_ok=True)
    graficos = [("taxas_funil.png", lambda d: ft.funil(execs, extra, d)),
                ("taxas_mes.png", lambda d: ft.taxa_mes(mes, d)),
                ("taxas_papel.png", lambda d: ft.papel_volume(papel, d)),
                ("taxas_custo_execucao.png", lambda d: ft.custo_execucao(execs, custo_papel, d)),
                ("taxas_concentracao.png", lambda d: ft.concentracao(execs, d)),
                ("taxas_custo_mensal.png", lambda d: ft.custo_mensal(execs, mes, d)),
                ("taxas_entrada_saida.png", lambda d: ft.entrada_saida(papel, total_erro, d))]
    pulados = []
    if upm is not None:
        graficos.append(("taxas_unidade_mes.png", lambda d: ft.taxa_unidade_mes(upm, ppm, tri, mes, d)))
    else:
        pulados.append("Erros e taxa por unidade e mês: a rodada não tem `consolidacao_unidade_papel_mes.csv`.")
    if upt is not None:
        graficos.append(("taxas_orcamento_papel.png", lambda d: ft.orcamento_papel(papel, upt, tri, d)))
    else:
        pulados.append("Gasto de cada papel por destino: a rodada não tem `consolidacao_unidade_papel_tokens.csv` "
                       "(tabela de 15/10; rode `executar.py analisar` de novo).")
    graficos.append(("taxas_prioridade.png", lambda d: ft.prioridade(papel, upt, tri, d)))

    asteps, erros = int(execs.actionsteps.sum()), int(execs.erros.sum())
    tok_tot, tok_err = float(papel.tokens_total.sum()), float(papel.tokens_erro.sum())
    com_erro = int(execs.erros.gt(0).sum())
    resumo = pd.DataFrame([
        ("Execuções (execução + agente)", _n(len(execs))),
        ("… com pelo menos um erro estruturado", f"{_n(com_erro)} ({_n(100 * com_erro / len(execs), 1)}%)"),
        ("ActionSteps (passos)", _n(asteps)),
        ("Passos com erro estruturado", f"{_n(erros)} ({_n(100 * erros / asteps, 1)}%)"),
        ("Tokens em todos os passos", ft.tok(tok_tot)),
        ("… nos passos com erro estruturado", f"{ft.tok(tok_err)} ({_n(100 * tok_err / tok_tot, 1)}%)"),
        ("Saída ÷ total: todos os passos · passos com erro", f"{_n(100 * total_erro[0], 1)}% · {_n(100 * total_erro[1], 1)}%"),
        ("Linhas das contagens sem quantidade (fora das contas)", _n(sem_contagem)),
    ], columns=["Medida", "Valor"])
    md = ["# Taxas e custo — base 3, rodada `" + pasta.name + "`", "",
          f"Fonte: SHA-256 `{sha_fonte}` · contagens (pedido A): SHA-256 `{sha_cont}`.",
          "Gerado por `execucao/taxas.py`. **Junção conferida** antes de qualquer conta: "
          + ", ".join(f"`{k}`" for k in verif) + f" — {len(verif)} de {len(verif)}. Só contagens; nenhum "
          "identificador de execução. Nos gráficos de volume, taxa e custo, erro é erro (todos os erros estruturados, "
          "sem separar destino); só o gráfico do gasto de cada papel separa por destino.", "",
          "## Resumo", "", _tabela(resumo, "ld"), "", "# Leituras com denominador", ""]
    artefatos = {}
    for nome, desenhar in graficos:
        titulo, pergunta, ler_como, limite = desenhar(saida / nome)
        artefatos[nome] = _sha256(saida / nome)
        md += [f"## {titulo}", "", f"**Pergunta:** {pergunta}", "", f"![{titulo}]({nome})", "",
               f"**Como ler:** {ler_como}", "", f"**Limitação:** {limite}", ""]
    if pulados:
        md += ["## Gráficos não gerados nesta rodada", ""] + [f"- {x}" for x in pulados] + [""]
    mes.reset_index().to_csv(saida / "taxas_por_mes.csv", index=False)
    papel.reset_index().to_csv(saida / "taxas_por_papel.csv", index=False)
    custo_papel.to_csv(saida / "taxas_custo_por_papel.csv", index=False)
    (saida / "taxas.md").write_text("\n".join(md), encoding="utf-8")
    for nome in ["taxas_por_mes.csv", "taxas_por_papel.csv", "taxas_custo_por_papel.csv", "taxas.md"]:
        artefatos[nome] = _sha256(saida / nome)
    (saida / "manifesto_taxas.json").write_text(json.dumps({
        "rodada": pasta.name, "rodada_id": m.get("rodada_id"), "fonte_sha256": sha_fonte, "contagens_sha256": sha_cont,
        "verificacoes_juncao": verif, "linhas_sem_contagem": sem_contagem, "tokens_total_sistema": tok_tot,
        "artefatos": artefatos, "gerado_em": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return saida


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rodada", type=Path)
    p.add_argument("--contagens", type=Path, help=f"padrão: {CONTAGENS.name} em data/")
    p.add_argument("--fonte", type=Path, help="padrão: a fonte padrão do pipeline (a v2)")
    args = p.parse_args(argv)
    try:
        saida = gerar(_rodada(args.rodada), args.contagens, args.fonte)
    except TravaTaxas as e:
        print(f"TAXAS NÃO GERADAS: {e}")
        return 1
    print("Taxas:", saida / "taxas.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
