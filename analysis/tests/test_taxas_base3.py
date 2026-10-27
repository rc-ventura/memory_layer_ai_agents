"""Taxas e relatório único da base 3 (roadmap b3 #32): a junção é trava, o relatório consolida e explica o que falta.

Fixtures sintéticas: uma rodada de 3 erros (a mesma dos testes da mineração), a fonte com as mesmas linhas e contagens
montadas delas, com execuções sem erro e uma linha `JSON_INVALIDO` sem quantidade.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import matplotlib
matplotlib.use("Agg")
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_sintomas_base3 import state
from test_mineracao_observada_base3 import recorrentes
import mineracao_observada as mo

sys.path.insert(0, str(mo.HERE))
from execucao import relatorio, taxas


def contagens(rows):
    linhas = [dict(cod_idef_exeo=r["cod_idef_exeo"], cod_idef_aget=r["cod_idef_aget"], papel=r["papel"],
                   mes_execucao=r["mes_execucao"], status_memoria="OK", qtd_actionsteps=5.0, tokens_entrada=80.0,
                   tokens_saida=20.0, tokens_total=100.0, qtd_erros_estruturados=1.0, qtd_suspeitas_observadas=0.0)
              for r in rows]
    for i in range(4):
        linhas.append(dict(cod_idef_exeo=f"exec-sem-erro-{i}", cod_idef_aget="1", papel="Agent", mes_execucao="2026-07",
                           status_memoria="OK", qtd_actionsteps=3.0, tokens_entrada=50.0, tokens_saida=10.0,
                           tokens_total=60.0, qtd_erros_estruturados=0.0, qtd_suspeitas_observadas=0.0))
    linhas.append(dict(cod_idef_exeo="exec-json-invalido", cod_idef_aget="1", papel="Agent", mes_execucao="2026-08",
                       status_memoria="JSON_INVALIDO", qtd_actionsteps=None, tokens_entrada=None, tokens_saida=None,
                       tokens_total=None, qtd_erros_estruturados=None, qtd_suspeitas_observadas=None))
    return pd.DataFrame(linhas)


class TestTaxas(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        rows = recorrentes()
        with patch.object(mo, "HERE", d / "pipeline"), patch.object(mo, "versoes_codigo", return_value={"fixture": "hash"}):
            self.rodada = mo.gravar(mo.analisar(state(*rows)))
        self.fonte = d / "fonte.parquet"
        pd.DataFrame(rows).to_parquet(self.fonte)
        self.cont = d / "contagens.parquet"
        self.cont_df = contagens(rows)
        self.cont_df.to_parquet(self.cont)

    def tearDown(self):
        self.tmp.cleanup()

    def test_juncao_confere_e_gera_sem_identificador(self):
        saida = taxas.gerar(self.rodada, self.cont, self.fonte)
        man = json.loads((saida / "manifesto_taxas.json").read_text(encoding="utf-8"))
        self.assertTrue(all(man["verificacoes_juncao"].values()))
        self.assertEqual(man["linhas_sem_contagem"], 1)
        self.assertEqual(len(list(saida.glob("taxas_*.png"))), 14)   # 12 + os dois da recuperação
        textos = [(saida / n).read_text(encoding="utf-8") for n in ["taxas.md", "taxas_por_mes.csv", "taxas_por_papel.csv",
                                                                  "taxas_por_papel_mes.csv"]]
        self.assertFalse(any("exec-" in t for t in textos))
        md = textos[0]
        self.assertIn("ActionSteps", md)
        self.assertIn("3 (11,1%)", md)   # 3 erros em 27 ActionSteps (3×5 + 4×3; a linha sem quantidade fica fora)

    def test_papel_por_mes_soma_e_desenha(self):
        """Erros e passos por papel e mês somam o total; o gráfico dá a fatia dos erros e a dos passos de cada papel."""
        import execucao.figuras_taxas as ft
        pm = taxas.papel_por_mes(self.cont_df.assign(**{c: pd.to_numeric(self.cont_df[c]) for c in
                                                        ["qtd_actionsteps", "qtd_erros_estruturados"]}))
        self.assertEqual(int(pm.erros.sum()), 3)
        self.assertEqual(int(pm.actionsteps.sum()), 27)   # a linha sem quantidade fica fora
        self.assertEqual(int(pm.execucoes.sum()), 7)      # 3 com erro + 4 sem erro; a sem quantidade fica fora
        with tempfile.TemporaryDirectory() as t:
            titulo, _, ler, limite = ft.papel_mes(pm, Path(t) / "x.png")
            self.assertTrue((Path(t) / "x.png").is_file())
        self.assertIn("dos erros", titulo + ler)
        self.assertIn("linear", ler)

    def test_papel_entrada_acha_o_primeiro_mes(self):
        """O primeiro mês de cada papel é o primeiro com execução; a figura diz quantos papéis entram depois."""
        import execucao.figuras_taxas as ft
        pm = pd.DataFrame({"papel": ["A", "A", "B", "C"], "mes": ["2026-01", "2026-02", "2026-02", "2026-03"],
                           "execucoes": [5, 7, 2, 1], "actionsteps": [20, 30, 8, 3], "erros": [1, 2, 0, 0]})
        with tempfile.TemporaryDirectory() as t:
            titulo, _, ler, limite = ft.papel_entrada(pm, Path(t) / "x.png")
            self.assertTrue((Path(t) / "x.png").is_file())
        self.assertIn("fev/26", ler)           # o maior salto de execuções (5 → 9) é em fevereiro, quando entra o B
        self.assertIn("B", ler)
        self.assertIn("não os tem", limite)    # a base 3 não traz modelo nem prompt

    def test_custo_execucao_em_valores_reais(self):
        """O gráfico do custo mostra a mediana em unidades reais (tokens e passos inteiros), com a razão ao lado."""
        import execucao.figuras_taxas as ft
        saida = taxas.gerar(self.rodada, self.cont, self.fonte)
        md = (saida / "taxas.md").read_text(encoding="utf-8")
        # com erro: 100 tokens e 5 passos (a mediana); sem erro: 60 tokens e 3 passos
        self.assertIn("1,7× em tokens (100 ÷ 60) e 1,7× em passos (5 ÷ 3)", md)
        self.assertIn("diferença de 2 passo(s)", md)
        self.assertNotIn("× a execução típica sem erro", md)   # o eixo normalizado saiu
        execs = pd.DataFrame({"tokens_total": [100.0, 100.0, 60.0, 60.0, 60.0], "actionsteps": [5.0, 5.0, 3.0, 3.0, 4.0],
                              "erros": [1, 2, 0, 0, 0]})
        cp = pd.DataFrame({"papel": ["Agent"], "n_com_erro": [2], "n_sem_erro": [3], "mediana_tokens_com_erro": [100.0],
                           "mediana_tokens_sem_erro": [60.0]})
        titulo, *_ = ft.custo_execucao(execs, cp, Path(self.tmp.name) / "custo.png")
        self.assertIn("Custo", titulo)
        self.assertTrue((Path(self.tmp.name) / "custo.png").stat().st_size > 0)
        execs["erros"] = 0
        with self.assertRaisesRegex(ValueError, "falta o grupo"):
            ft.custo_execucao(execs, cp, Path(self.tmp.name) / "custo2.png")

    def test_erro_diferente_por_chave_trava(self):
        c = self.cont_df.copy()
        c.loc[0, "qtd_erros_estruturados"] = 2.0
        c.loc[3, "qtd_erros_estruturados"] = -1.0   # a soma continua igual: só a conferência por chave pega
        c.to_parquet(self.cont)
        with self.assertRaisesRegex(taxas.TravaTaxas, "erros_iguais_por_chave"):
            taxas.gerar(self.rodada, self.cont, self.fonte)
        self.assertFalse((self.rodada / "taxas" / "taxas.md").exists())

    def test_soma_diferente_do_manifesto_trava(self):
        c = self.cont_df.copy()
        c.loc[3, "qtd_erros_estruturados"] = 1.0   # erro numa chave que a fonte não tem
        c.to_parquet(self.cont)
        with self.assertRaisesRegex(taxas.TravaTaxas, "erros_somam_o_manifesto"):
            taxas.gerar(self.rodada, self.cont, self.fonte)

    def test_relatorio_consolida_e_explica_o_que_falta(self):
        saida, motivo = relatorio.gerar(self.rodada, self.cont, self.fonte)
        md = (saida / "relatorio.md").read_text(encoding="utf-8")
        self.assertIsNone(motivo)
        self.assertIn("# Parte 1", md)
        self.assertIn("# Parte 2", md)
        self.assertIn("## Taxa de erro por mês", md.replace("### ", "## "))
        self.assertTrue((saida / "taxas_funil.png").exists() and (saida / "cobertura.png").exists())
        saida, motivo = relatorio.gerar(self.rodada, Path(self.tmp.name) / "nao_existe.parquet", self.fonte)
        md = (saida / "relatorio.md").read_text(encoding="utf-8")
        self.assertIn("não encontrada", motivo)
        self.assertIn("**Não gerada:**", md)
        self.assertIn("# Parte 1", md)


if __name__ == "__main__":
    unittest.main()
