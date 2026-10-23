"""O "depois do erro" da população e por destino (a visão do sistema; a por unidade já existia)."""
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
from execucao import figuras_painel as fp


class TestDepoisPopulacao(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        with patch.object(mo, "HERE", d / "pipeline"), patch.object(mo, "versoes_codigo", return_value={"fixture": "hash"}):
            self.rodada = mo.gravar(mo.analisar(state(*recorrentes())))
        self.dep = pd.read_csv(self.rodada / "consolidacao_depois_unidade.csv")
        self.tri = pd.read_csv(self.rodada / "triagem_visivel_observada.csv")

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_figura_sai_da_rodada_e_diz_que_nao_e_sucesso(self):
        titulo, pergunta, ler, limite = fp.depois_populacao(self.dep, self.tri, Path(self.tmp.name) / "x.png")
        self.assertTrue((Path(self.tmp.name) / "x.png").is_file())
        self.assertIn("Cada barra soma 100%", ler)
        self.assertIn("não o sucesso", limite)
        self.assertIn("por papel", limite)   # a limitação diz o que falta para a visão por papel

    def test_as_fatias_do_titulo(self):
        """20 erros seguidos de outro erro, 30 em que o seguinte é a resposta final, 50 que seguem sem erro."""
        sem = "sem sinal do produtor observado – não sucesso"
        dep = pd.DataFrame({"unidade": ["A", "A", "A"],
                            "depois": ["erro estruturado vinculado", sem, sem],
                            "proximo_final_observado": [False, True, False],
                            "unidade_seguinte": ["A", None, None], "erros": [20, 30, 50]})
        tri = pd.DataFrame({"unidade": ["A"], "decisao": ["candidato observado"]})
        titulo, _, ler, _ = fp.depois_populacao(dep, tri, Path(self.tmp.name) / "y.png")
        self.assertIn("recuperação aparente: 80,0% dos erros (30,0% com a resposta final no passo seguinte); novo erro: 20,0%", ler)

    def test_grupo_decisao(self):
        self.assertEqual(fp._grupo_decisao("candidato observado"), "candidata a memória")
        self.assertEqual(fp._grupo_decisao("não-memória"), "harness / infra")
        self.assertEqual(fp._grupo_decisao(float("nan")), "pendente")


if __name__ == "__main__":
    unittest.main()
