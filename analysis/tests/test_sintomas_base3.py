"""Sintomas/custos: elegibilidade, denominadores e regressão sintética."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_adaptador_trace import janela, census, typed_text
from test_integracao_carga_base3 import BP, RAW1, RAW2, raw_row
from adaptador_trace import adaptar


def state(*rows):
    return BP._estado_estrutural(adaptar(pd.DataFrame(rows), fonte_id="sintomas-fixture"))


class TestSintomas(unittest.TestCase):
    def test_reusa_regra_existente_exata(self):
        b = state(janela())
        e = BP.analisar_sintomas(b).E.iloc[0]
        self.assertEqual((e.familia, e.assinatura), RAW1.classify(b.steps.err_msg.iloc[0]))
        self.assertEqual((e.familia, e.assinatura), RAW2.classify(b.steps.err_msg.iloc[0]))

    def test_cortado_nem_invoca_classificador(self):
        r = janela(error_message="TypeError " + "x" * (20000 - len("TypeError ")))
        with patch.object(BP, "classify", side_effect=AssertionError("não classificar fragmento")):
            a = BP.analisar_sintomas(state(r))
        self.assertEqual(a.resumo["mensagem_limitada"], 1)
        self.assertTrue(a.E.familia.isna().all())
        self.assertTrue(a.E.assinatura.isna().all())
        self.assertTrue(a.tabelas["typeerror"].empty)

    def test_suspeita_fora_taxonomia_sem_recomputar_regex(self):
        r = janela(structured_error="0", observation_suspect="1", error_source="OBSERVATION_SUSPECT",
                   error_type=None, error_message=None)
        a = BP.analisar_sintomas(state(r))
        self.assertEqual(len(a.E), 0)
        self.assertEqual(a.resumo["suspeitas_fora_taxonomia"], 1)

    def test_ausencia_de_mensagem_nao_vira_residuo(self):
        a = BP.analisar_sintomas(state(janela(error_message=None)))
        self.assertEqual(a.resumo["mensagem_indisponivel"], 1)
        self.assertEqual(a.resumo["sintomas_nao_reconhecidos_elegiveis"], 0)
        self.assertTrue(a.E.familia.isna().all())

    def test_mensagem_integral_desconhecida_continua_residuo(self):
        a = BP.analisar_sintomas(state(janela(error_message="fixture diferente sem categoria")))
        self.assertEqual(a.resumo["sintomas_nao_reconhecidos_elegiveis"], 1)
        self.assertEqual(a.E.familia.iloc[0], "Sintoma não reconhecido")

    def test_custos_cortados_continuam_total_e_nao_assinatura(self):
        a = BP.analisar_sintomas(state(janela(), janela(step_pos="3", step_number="2", total_tokens="100",
                                                        error_message="x" * 20000)))
        t = a.tabelas["custos_por_situacao"]
        self.assertEqual(t.tokens_n_conhecidos.sum(), 112)
        self.assertEqual(a.tabelas["custos_assinaturas"].tokens_n_conhecidos.sum(), 12)
        self.assertEqual(len(a.E), 2)
        self.assertEqual(len(a.Ee), 1)

    def test_percentual_explica_os_dois_denominadores(self):
        a = BP.analisar_sintomas(state(janela(), janela(step_pos="3", error_message="x" * 20000)))
        self.assertEqual(float(a.tabelas["familias"].pct_erros_elegiveis.iloc[0]), 100)
        self.assertEqual(float(a.tabelas["familias"].pct_erros_estruturados.iloc[0]), 50)

    def test_custo_ausente_sem_zero_ou_percentual_falso(self):
        a = BP.analisar_sintomas(state(janela(total_tokens=None, duration_seconds=None)))
        t = a.tabelas["custos_por_situacao"].iloc[0]
        self.assertTrue(pd.isna(t.tokens_n_conhecidos))
        self.assertTrue(pd.isna(t.pct_tokens_universo_tabela))
        self.assertEqual(t.tokens_n_ausentes, 1)
        self.assertEqual(t.dur_s_n_ausente, 1)

    def test_custo_parcial_tem_soma_conhecida_e_n_ausentes(self):
        a = BP.analisar_sintomas(state(janela(), janela(step_pos="3", total_tokens=None)))
        t = a.tabelas["custos_assinaturas"].iloc[0]
        self.assertEqual(t.tokens_n_conhecidos, 12)
        self.assertEqual(t.tokens_n_ausentes, 1)
        self.assertTrue(pd.isna(t.pct_tokens_universo_tabela))

    def test_custos_nao_somam_vizinhos(self):
        a = BP.analisar_sintomas(state(janela(next_step_number="2", next_error_like="0", next_total_tokens="999")))
        self.assertEqual(a.tabelas["custos_assinaturas"].tokens_n_conhecidos.iloc[0], 12)

    def test_sem_sinal_A_nao_e_erro_estruturado(self):
        a = BP.analisar_sintomas(state(janela(structured_error="0", observation_suspect="0",
                                              error_source=None, error_type=None, error_message=None)))
        self.assertTrue(a.E.empty)
        self.assertTrue(a.tabelas["custos_assinaturas"].empty)

    def test_nao_muta_carga_e_nunca_chama_mecanismos(self):
        b = state(janela())
        before = b.steps.copy(deep=True)
        with patch.object(BP, "montar_unidades", side_effect=AssertionError("não chamar")), \
                patch.object(BP, "medir_sucesso", side_effect=AssertionError("não chamar")):
            a = BP.analisar_sintomas(b)
        pd.testing.assert_frame_equal(b.steps, before)
        self.assertIsNone(b.E)
        self.assertIsNone(a.EU)
        self.assertIsNone(a.S)
        with self.assertRaises(BP.AnaliseNaoIntegrada):
            BP.montar_unidades(a.E)

    def test_typeerror_mesmas_regras(self):
        messages = ["TypeError: unexpected keyword argument", "TypeError: required positional argument",
                    "TypeError: not subscriptable", "TypeError: fixture other"]
        rows = [janela(step_pos=str(i + 2), step_number=str(i + 1), error_message=m) for i, m in enumerate(messages)]
        table = BP.analisar_sintomas(state(*rows)).tabelas["typeerror"]
        self.assertEqual(len(table), 4)
        self.assertEqual(table.erros.sum(), 4)

    def test_B_flag_real_corte_suspende_sintoma(self):
        r = census(structured_error="1", error_like="1", error_source="STRUCTURED_ERROR", error_type="AgentExecutionError")
        typed_text(r, "error_message", "TypeError " + "x" * 20000, 20000)
        a = BP.analisar_sintomas(state(r))
        self.assertEqual(a.resumo["mensagem_limitada"], 1)

    def test_B_tamanho_exato_sem_corte_e_elegivel(self):
        r = census(structured_error="1", error_like="1", error_source="STRUCTURED_ERROR", error_type="AgentExecutionError")
        typed_text(r, "error_message", "TypeError " + "x" * (20000 - len("TypeError ")), 20000)
        a = BP.analisar_sintomas(state(r))
        self.assertEqual(a.resumo["sintomas_elegiveis"], 1)

    def test_guardas_comparativos_mantidas(self):
        b = state(janela())
        a = BP.analisar_sintomas(b)
        self.assertEqual(a.cobertura["comparativos_globais"], "bloqueados_ate_complemento_validado")
        self.assertTrue(b.execs.tok_tot.isna().all())
        with self.assertRaises(BP.AnaliseNaoIntegrada):
            BP.exigir_analise_integrada(b)

    def test_proveniencia_perdida_nao_habilita_caminho_raw(self):
        steps = state(janela()).steps.copy()
        steps.attrs.clear()
        with self.assertRaises(BP.AnaliseNaoIntegrada):
            BP.classificar_sintomas_elegiveis(steps)

    def test_quadro_papel_inclui_erros_nao_classificaveis(self):
        a = BP.analisar_sintomas(state(janela(), janela(step_pos="3", error_message=None)))
        self.assertEqual(a.tabelas["papeis"].erros.sum(), 2)
        self.assertEqual(a.tabelas["familias"].erros.sum(), 1)

    def test_erro_estruturado_vazio_trata_sem_grafico_falso(self):
        a = BP.analisar_sintomas(state(janela(structured_error="0", observation_suspect="1",
                                              error_source="OBSERVATION_SUSPECT", error_type=None, error_message=None)))
        self.assertEqual(a.resumo["erros_estruturados"], 0)
        self.assertEqual(a.resumo["sintomas_elegiveis"], 0)
        self.assertTrue(a.tabelas["familias"].empty)


if __name__ == "__main__":
    unittest.main()
