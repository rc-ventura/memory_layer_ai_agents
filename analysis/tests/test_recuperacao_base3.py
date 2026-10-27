"""A recuperação depois do erro por trajetória (execução × agente × papel) da base 3 — `execucao/recuperacao.py`.

Fixtures sintéticas: uma trajetória por categoria, com os vizinhos como a query os traz (texto, como no parquet). O
teste com resposta conhecida na base 1 (trace completo) é o `validacao/conferir_recuperacao_base1.py`.
"""
from pathlib import Path
import sys
import tempfile
import unittest

import matplotlib
matplotlib.use("Agg")
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third" / "pipeline"))
from execucao import recuperacao as rec
import execucao.figuras_taxas as ft


def erro(exec_id, pos, numero, seguinte=None, seguinte_erra=False, anterior_erra=False, agente="1", papel="Agent",
         msg="Could not index", suspeita_depois=False):
    """Uma linha da v2 com erro estruturado; `seguinte` = o step_number do ActionStep seguinte (None = não há)."""
    return dict(cod_idef_exeo=exec_id, cod_idef_aget=agente, papel=papel, structured_error="1", observation_suspect="0",
                step_pos=str(pos), step_number=str(numero), error_message=msg,
                next_step_number=None if seguinte is None else float(seguinte),
                next_error_type="AgentExecutionError" if seguinte_erra else None,
                next_error_like=float(seguinte_erra or suspeita_depois) if seguinte is not None else None,
                prev_error_type="AgentExecutionError" if anterior_erra else None, execution_has_final_step="1")


def fonte():
    return pd.DataFrame([
        erro("um", 2, 1, seguinte=2),                                                     # um erro, depois nada
        erro("cascata", 2, 1, seguinte=2, seguinte_erra=True),                            # dois seguidos
        erro("cascata", 3, 2, seguinte=3, anterior_erra=True),
        erro("recaida", 2, 1, seguinte=2),                                                # erra, passa, erra de novo
        erro("recaida", 5, 4, seguinte=5),
        erro("fim", 4, 3),                                                                # o último passo errou
        erro("limite", 9, 8, seguinte=9, msg="AgentMaxStepsError: Reached max steps."),   # esgotou os passos
        erro("fora_do_censo", 2, 1, seguinte=2, seguinte_erra=True),                      # o seguinte errou e não está
        erro("dois_agentes", 2, 1, seguinte=2, agente="1"),                               # a query mistura os dois
        erro("dois_agentes", 2, 1, seguinte=2, agente="2"),
        erro("nova_chamada", 4, 3, seguinte=1, seguinte_erra=True),                       # o número recomeça
        erro("nova_chamada", 6, 1, seguinte=2, anterior_erra=True),
        erro("dois_papeis", 2, 1, seguinte=2, seguinte_erra=True, papel="A"),             # cascata em A,
        erro("dois_papeis", 3, 2, seguinte=3, anterior_erra=True, papel="A"),
        erro("dois_papeis", 7, 6, papel="B"),                                             # B termina no erro
    ])


def contagens(f):
    erros = f.groupby(rec.CHAVE).size().rename("qtd_erros_estruturados").reset_index()
    sem = pd.DataFrame([dict(cod_idef_exeo=f"sem-{i}", cod_idef_aget="1", papel="Agent", qtd_erros_estruturados=0)
                        for i in range(5)])
    c = pd.concat([erros, sem], ignore_index=True)
    c["qtd_actionsteps"] = 10.0
    return c


class TestTrajetorias(unittest.TestCase):
    def setUp(self):
        self.t = rec.trajetorias(fonte())

    def linha(self, exec_id, papel="Agent"):
        return self.t[self.t.cod_idef_exeo.eq(exec_id) & self.t.papel.eq(papel)].iloc[0]

    def cat(self, exec_id, papel="Agent"):
        return self.linha(exec_id, papel).categoria

    def test_uma_categoria_por_caso(self):
        self.assertEqual(self.cat("um"), "um_erro")
        self.assertEqual(self.cat("cascata"), "cascata")
        self.assertEqual(self.cat("recaida"), "recaida")
        self.assertEqual(self.cat("fim"), "terminou_no_erro")
        self.assertEqual(self.cat("limite"), "limite_de_passos")
        self.assertEqual(self.cat("dois_papeis", "A"), "cascata")
        self.assertEqual(self.cat("dois_papeis", "B"), "terminou_no_erro")

    def test_sequencias_pelos_vizinhos_nao_pela_numeracao(self):
        """O step_number recomeça numa nova chamada (3 → 1): ainda é cascata, porque o seguinte errou e é o próximo."""
        self.assertEqual(self.cat("nova_chamada"), "cascata")
        self.assertEqual(self.linha("recaida").sequencias, 2)
        self.assertEqual(self.linha("cascata").sequencias, 1)

    def test_indeterminado_contado_com_o_motivo(self):
        self.assertEqual(self.cat("fora_do_censo"), "indeterminado")
        self.assertIn("fora do censo", self.linha("fora_do_censo").motivo_indeterminado)
        d = rec.trajetorias(fonte())
        dois = d[d.cod_idef_exeo.eq("dois_agentes")]
        self.assertEqual(len(dois), 2)
        self.assertTrue(dois.categoria.eq("indeterminado").all())
        self.assertTrue(dois.motivo_indeterminado.str.contains("mais de um agente").all())

    def test_vizinhos_que_nao_conferem(self):
        """O primeiro diz que o seguinte errou, mas o próximo erro diz que o anterior não errou."""
        f = pd.DataFrame([erro("x", 2, 1, seguinte=2, seguinte_erra=True), erro("x", 3, 2, seguinte=3)])
        t = rec.trajetorias(f).iloc[0]
        self.assertEqual(t.categoria, "indeterminado")
        self.assertEqual(t.motivo_indeterminado, "os vizinhos de dois erros não conferem")

    def test_suspeita_nao_entra_na_conta(self):
        f = fonte()
        f = pd.concat([f, pd.DataFrame([dict(erro("um", 3, 2, seguinte=3), structured_error="0", observation_suspect="1",
                                             error_message=None)])], ignore_index=True)
        self.assertEqual(rec.trajetorias(f).set_index("cod_idef_exeo").loc["um"].erros, 1)


class TestTabelas(unittest.TestCase):
    def setUp(self):
        self.f = fonte()
        self.pop, self.papel, self.motivos, self.extra = rec.tabelas(self.f, contagens(self.f))

    def test_execucao_o_pior_papel_manda(self):
        ex = self.pop[self.pop.nivel.eq("execuções")].set_index("categoria").n
        self.assertEqual(ex["sem_erro"], 5)
        self.assertEqual(ex["recuperou"], 4)        # um, cascata, recaida, nova_chamada
        self.assertEqual(ex["nao_recuperou"], 3)    # fim, limite, dois_papeis (B terminou no erro)
        self.assertEqual(ex["indeterminado"], 3)    # fora_do_censo e os dois agentes
        self.assertEqual(int(ex.sum()), 15)

    def test_papeis_somam_e_sem_identificador(self):
        pa = self.pop[self.pop.nivel.eq("papéis com erro")]
        self.assertEqual(int(pa.n.sum()), int(pa.total.iloc[0]))
        self.assertEqual(int(self.papel.com_erro.sum()), int(pa.total.iloc[0]))
        for tab in [self.pop, self.papel, self.motivos]:
            self.assertFalse(tab.astype(str).apply(lambda c: c.str.contains("cascata_|dois_agentes|fora_do_censo")).any().any())
            self.assertNotIn("cod_idef_exeo", tab.columns)
        self.assertEqual(self.extra["erros_em_cascata"], 3)   # um em cascata, um em nova_chamada, um em dois_papeis A

    def test_figuras(self):
        with tempfile.TemporaryDirectory() as t:
            titulo, _, ler, limite = ft.recuperacao_populacao(self.pop, self.extra, Path(t) / "p.png")
            self.assertTrue((Path(t) / "p.png").is_file())
            self.assertIn("por trajetória, não por erro", ler)
            self.assertIn("não sucesso", limite)
            titulo, _, ler, _ = ft.recuperacao_papel(self.papel, Path(t) / "q.png")
            self.assertTrue((Path(t) / "q.png").is_file())


if __name__ == "__main__":
    unittest.main()
