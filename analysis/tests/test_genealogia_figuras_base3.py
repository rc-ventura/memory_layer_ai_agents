"""As duas figuras que separam os eixos da genealogia (decisão de 22/10): o censo do sintoma e a decisão.

Lidas só do `genealogia_arestas.csv` da rodada; a rodada é a sintética dos testes da mineração.
"""
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
from execucao import figuras_genealogia as fg


class TestFigurasGenealogia(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        with patch.object(mo, "HERE", d / "pipeline"), patch.object(mo, "versoes_codigo", return_value={"fixture": "hash"}):
            rodada = mo.gravar(mo.analisar(state(*recorrentes())))
        self.ar = pd.read_csv(rodada / "genealogia_arestas.csv")

    def tearDown(self):
        self.tmp.cleanup()

    def test_censo_uma_barra_por_assinatura(self):
        titulo, pergunta, ler, limite = fg.censo_sintomas(self.ar, Path(self.tmp.name) / "censo.png")
        self.assertTrue((Path(self.tmp.name) / "censo.png").is_file())
        self.assertIn("sintoma", titulo.lower())
        self.assertIn("só descreve", ler)

    def test_decisao_soma_os_erros_e_nao_traz_a_familia(self):
        titulo, pergunta, ler, limite = fg.genealogia_decisao(self.ar, Path(self.tmp.name) / "decisao.png")
        self.assertTrue((Path(self.tmp.name) / "decisao.png").is_file())
        self.assertIn("cor é o destino", ler)
        self.assertIn("não entra", ler)          # a classificação do sintoma fica no censo
        # a figura lê as duas etapas da decisão; cada uma soma o mesmo total de erros
        for etapa in ["submecanismo->unidade", "unidade->destino"]:
            self.assertEqual(int(self.ar[self.ar.etapa.eq(etapa)].erros.sum()), int(self.ar[self.ar.etapa.eq("familia->assinatura")].erros.sum()))


if __name__ == "__main__":
    unittest.main()
