"""Integração da carga estrutural no pipeline da third; fixtures sintéticas."""
# TRANSCRIÇÃO: as linhas 1–29 (cabeçalho) não vieram nas fotos; reconstruídas pelo uso no resto do
# arquivo e no test_mineracao_observada_base3. Neste repositório não existe a pasta -second: o RAW2
# cai no pipeline da base 1, e a comparação "duas cópias" vira uma só. Conferir contra a máquina 2.
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

ANALYSIS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYSIS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from adaptador_trace import CENSO, JANELAS, TRACE_COMPLETO
from test_adaptador_trace import census, janela


def module(folder, name):
    path = ANALYSIS / folder / "pipeline" / "base_pipeline.py"
    if not path.is_file():
        return None
    sys.path.insert(0, str(path.parent))
    spec = spec_from_file_location(name, path)
    loaded = module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


BP = module("2026-10-trace-law-flow-third", "base3_integracao_test")
RAW1 = module("2026-09-trace-law-flow", "base1_regressao_test")
RAW2 = module("2026-09-trace-law-flow-second", "base2_regressao_test") or RAW1


def raw_row():
    memo = {"Agent": [
        {"__class__": "TaskStep", "task": "fixture"},
        {"__class__": "ActionStep", "step_number": 1, "code_action": "x = data[0]",
         "error": {"type": "AgentExecutionError", "message": "Could not index: KeyError: 0"},
         "is_final_answer": False, "token_usage": {"input_tokens": 10, "output_tokens": 2, "total_tokens": 12},
         "timing": {"duration": 0.5}},
        {"__class__": "PlanningStep", "plan": "fixture"},
        {"__class__": "ActionStep", "step_number": 2, "code_action": "final_answer('fixture final longo')",
         "error": None, "is_final_answer": True, "action_output": "fixture final longo",
         "token_usage": {"input_tokens": 3, "output_tokens": 2, "total_tokens": 5},
         "timing": {"duration": 1.0, "end_time": 100}},
    ]}
    return dict(cod_idef_exeo="fixture-exec", cod_idef_aget="1", cod_idef_stat_exeo_aget="3",
                dat_hor_inio_exeo="2026-08-01 10:00:00", anomesdia="20260930", txt_etap_memo=json.dumps(memo))


class TestIntegracao(unittest.TestCase):
    def use_csv(self, row, callback):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fixture.csv"
            pd.DataFrame([row]).to_csv(path, index=False)
            return callback(path)

    def test_carregar_base_somente_carga_nunca_chama_classificadores(self):
        def run(path):
            with patch.object(BP, "classificar_erros", side_effect=AssertionError("não chamar")), \
                    patch.object(BP, "montar_unidades", side_effect=AssertionError("não chamar")), \
                    patch.object(BP, "medir_sucesso", side_effect=AssertionError("não chamar")):
                return BP.carregar_base(apenas_carga=True, caminho=path)
        b = self.use_csv(janela(), run)
        self.assertEqual(b.contrato, JANELAS)
        self.assertIsNone(b.E)
        self.assertIsNone(b.EU)
        self.assertIsNone(b.S)
        self.assertEqual(b.status_analise, "somente_carga")

    def test_carga_tem_fonte_slots_e_limites(self):
        b = self.use_csv(janela(), BP.carregar_carga)
        self.assertEqual(len(b.fonte["sha256"]), 64)
        self.assertEqual(len(b.slots), 3)
        self.assertTrue(b.steps.idx.isna().all())
        self.assertTrue(b.steps.ctx.isna().all())

    def test_builder_explodir_memoria_trabalha_com_carregar_trace(self):
        def run(path):
            df = BP.carregar_trace(path)
            self.assertNotIn("txt_etap_memo", df.columns)
            return BP.explodir_memoria(df)
        steps, raw, execs = self.use_csv(janela(), run)
        self.assertEqual(len(steps), 1)
        self.assertEqual(len(raw), 1)
        self.assertEqual(len(execs), 1)
        self.assertEqual(steps.attrs["contrato_carga"], JANELAS)

    def test_dataframe_sem_proveniencia_nao_e_adaptado_silenciosamente(self):
        with self.assertRaises(BP.AnaliseNaoIntegrada):
            BP.explodir_memoria(pd.DataFrame([janela()]))

    def test_analise_completa_sem_integracao_falha_com_mensagem(self):
        def run(path):
            with self.assertRaisesRegex(BP.AnaliseNaoIntegrada, "ainda não integrada"):
                BP.carregar_base(caminho=path)
        self.use_csv(janela(), run)

    def test_gate_normalizado_impede_classificacao_direta(self):
        b = self.use_csv(janela(), BP.carregar_carga)
        for callback, value in [(BP.classificar_erros, b.steps), (BP.montar_unidades, b.steps), (BP.medir_sucesso, b.df)]:
            with self.assertRaises(BP.AnaliseNaoIntegrada):
                callback(value)

    def test_gate_notebook_impede_uso_de_censo_sem_consumidor(self):
        b = self.use_csv(census(), BP.carregar_carga)
        self.assertEqual(b.contrato, CENSO)
        self.assertEqual(b.steps.idx.iloc[0], 0)
        self.assertIsNone(b.EU)
        with self.assertRaises(BP.AnaliseNaoIntegrada):
            BP.exigir_analise_integrada(b, "notebook")

    def test_sem_exigencia_do_censo_B(self):
        b = self.use_csv(janela(), BP.carregar_carga)
        self.assertEqual(b.contrato, JANELAS)
        self.assertEqual(b.cobertura["comparativos_globais"], "bloqueados_ate_complemento_validado")

    def test_A_isolada_nao_habilita_comparativos_ou_orcamento(self):
        b = self.use_csv(janela(structured_error="0", observation_suspect="0", error_source=None,
                                error_type=None, error_message=None), BP.carregar_carga)
        self.assertEqual(b.resumo["sem_sinal"], 1)
        self.assertTrue(b.execs.tok_tot.isna().all())
        self.assertTrue(b.execs.n_steps.isna().all())

    def test_custo_observado_nao_e_total_execucao(self):
        b = self.use_csv(janela(), BP.carregar_carga)
        self.assertEqual(int(b.execs.tok_n_observados.iloc[0]), 12)
        self.assertTrue(pd.isna(b.execs.tok_tot.iloc[0]))
        self.assertTrue(pd.isna(b.execs.tem_final.iloc[0]))

    def test_custo_ausente_nao_zero(self):
        b = self.use_csv(janela(total_tokens=None, duration_seconds=None), BP.carregar_carga)
        self.assertTrue(pd.isna(b.execs.tok_n_observados.iloc[0]))
        self.assertEqual(int(b.execs.n_custos_tokens_ausentes.iloc[0]), 1)

    def test_RAW_so_n_nao_vizinhos(self):
        b = self.use_csv(janela(next_step_number="2", next_error_like="0", next_is_final_answer="false",
                                next_total_tokens="30"), BP.carregar_carga)
        self.assertEqual(len(b.RAW), 1)
        self.assertEqual(int(b.execs.tok_n_observados.iloc[0]), 12)

    def test_mes_execucao_preservado_distinto_lote(self):
        b = self.use_csv(janela(), BP.carregar_carga)
        self.assertEqual(b.execs.mes.iloc[0], "2026-08")
        self.assertEqual(b.execs.mes_particao.iloc[0], "2026-09")


class TestRegressaoRaw(unittest.TestCase):
    def test_carga_raw_apenas_carga_nao_classifica(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw_fixture.csv"
            pd.DataFrame([raw_row()]).to_csv(path, index=False)
            b = BP.carregar_base(apenas_carga=True, caminho=path)
        self.assertEqual(b.contrato, TRACE_COMPLETO)
        self.assertEqual(len(b.steps), 2)
        self.assertIsNone(b.E)

    def test_mes_e_explosao_raw_iguais_as_duas_copias(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw_fixture.csv"
            pd.DataFrame([raw_row()]).to_csv(path, index=False)
            actual_df = BP.carregar_trace(path)
            actual = BP.explodir_memoria(actual_df)
            for other in [RAW1, RAW2]:
                with patch.object(other, "TRACE", str(path)):
                    expected_df = other.carregar_trace()
                pd.testing.assert_frame_equal(actual_df, expected_df)
                expected = other.explodir_memoria(expected_df)
                pd.testing.assert_frame_equal(actual[0], expected[0])
                self.assertEqual(actual[1], expected[1])
                pd.testing.assert_frame_equal(actual[2], expected[2])

    def test_carregar_base_raw_completo_mantem_resultados(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw_fixture.csv"
            pd.DataFrame([raw_row()]).to_csv(path, index=False)
            actual = BP.carregar_base(caminho=path)
            for other in [RAW1, RAW2]:
                with patch.object(other, "TRACE", str(path)):
                    expected = other.carregar_base()
                for name in ["steps", "execs", "E", "EU", "S"]:
                    pd.testing.assert_frame_equal(getattr(actual, name), getattr(expected, name))

    def test_gate_permite_raw_sem_mudar_classificador(self):
        BP.exigir_analise_integrada(pd.DataFrame([raw_row()]))
        self.assertEqual(BP.classify("Could not index: KeyError: 0"), RAW1.classify("Could not index: KeyError: 0"))


if __name__ == "__main__":
    unittest.main()
