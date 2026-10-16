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
        self.assertEqual(len(list(saida.glob("taxas_*.png"))), 10)
        textos = [(saida / n).read_text(encoding="utf-8") for n in ["taxas.md", "taxas_por_mes.csv", "taxas_por_papel.csv"]]
        self.assertFalse(any("exec-" in t for t in textos))
        md = textos[0]
        self.assertIn("ActionSteps", md)
        self.assertIn("3 (11,1%)", md)   # 3 erros em 27 ActionSteps (3×5 + 4×3; a linha sem quantidade fica fora)

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
