"""Mecanismos/episódios: fixtures, nunca IDs ou conteúdo de clientes."""
from pathlib import Path
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_adaptador_trace import janela, census, typed_text, set_slot
from test_integracao_carga_base3 import BP, RAW1
from test_sintomas_base3 import state
from episodios_trace import construir_episodios_observados


def rows_chain(count=2, suspect_at=None):
    rows = [janela(step_number=str(i + 2), step_pos=str(2 * i + 3)) for i in range(count)]
    if suspect_at is not None:
        rows[suspect_at].update(error_type=None, structured_error="0", observation_suspect="1",
                                error_source="OBSERVATION_SUSPECT", error_message=None)
    rows[0].update(prev_step_number="1", prev_error_like="0", prev_code_action="data = {}")
    rows[-1].update(next_step_number=str(count + 2), next_error_like="0", next_is_final_answer="true",
                    next_code_action="final_answer('fixture')")
    for a, b in zip(rows, rows[1:]):
        set_slot(a, "next", b)
        set_slot(b, "prev", a)
    return rows


class TestEpisodios(unittest.TestCase):
    def test_duas_definicoes_custos_nao_devem_ser_somados(self):
        b = state(*rows_chain(3))
        a = construir_episodios_observados(b)
        for kind in ["estruturado", "misto"]:
            eps = a.episodios[a.episodios.definicao.eq(kind)]
            self.assertEqual(len(eps), 1)
            self.assertEqual(eps.n_ancoras.iloc[0], 3)
            self.assertEqual(eps.tokens_n_conhecidos.sum(), 36)
        self.assertEqual(len(a.membros), 6)

    def test_suspeita_interrompe_estruturada_mas_nao_mista(self):
        a = construir_episodios_observados(state(*rows_chain(3, suspect_at=1)))
        self.assertEqual(len(a.episodios[a.episodios.definicao.eq("estruturado")]), 2)
        self.assertEqual(len(a.episodios[a.episodios.definicao.eq("misto")]), 1)

    def test_mesmo_ID_sem_vinculos_nao_faz_cascata(self):
        r = [janela(), janela(step_pos="5", step_number="4")]
        a = construir_episodios_observados(state(*r))
        self.assertEqual(len(a.episodios[a.episodios.definicao.eq("misto")]), 2)

    def test_gap_step_pos_nao_e_gap_ActionStep(self):
        a = construir_episodios_observados(state(*rows_chain(2)))
        self.assertEqual(a.episodios.n_ancoras.max(), 2)

    def test_numero_reinicia_suspende_ligacao_e_limites(self):
        r = rows_chain(2)
        r[1]["step_number"] = "1"
        set_slot(r[0], "next", r[1])
        a = construir_episodios_observados(state(*r))
        mix = a.episodios[a.episodios.definicao.eq("misto")]
        self.assertEqual(len(mix), 2)
        self.assertTrue(mix.inicio.str.contains("suspenso").any())
        self.assertTrue(mix.fim.str.contains("suspenso").any())
        self.assertFalse(mix.componente_fechada_na_definicao.any())

    def test_null_proximo_nao_prova_fim_global(self):
        a = construir_episodios_observados(state(janela()))
        self.assertEqual(set(a.episodios.fim), {"aberto_nao_identificado_sql"})
        self.assertFalse(a.episodios.componente_fechada_na_definicao.any())

    def test_limites_identificados_e_final_nao_e_sucesso(self):
        a = construir_episodios_observados(state(*rows_chain()))
        self.assertTrue(a.episodios.componente_fechada_na_definicao.all())
        self.assertTrue(a.episodios.proximo_sem_sinal_observado.all())
        self.assertNotIn("recuperado", a.episodios)
        self.assertEqual(set(a.episodios.chamada), {"nao_observavel"})

    def test_custo_missing_nao_zero(self):
        a = construir_episodios_observados(state(janela(total_tokens=None)))
        self.assertTrue(a.episodios.tokens_n_conhecidos.isna().all())
        self.assertTrue(a.episodios.tokens_n_ausentes.eq(1).all())

    def test_agentes_nao_unidos(self):
        r = rows_chain()
        r[1]["cod_idef_aget"] = "2"
        a = construir_episodios_observados(state(*r))
        self.assertEqual(a.episodios.n_ancoras.max(), 1)
        self.assertFalse(a.episodios.componente_fechada_na_definicao.any())

    def test_censo_conta_chamadas_sem_provar_namespace(self):
        r = [census(structured_error="1", error_like="1", error_source="STRUCTURED_ERROR", error_type="AgentExecutionError",
                    n_actions_role="2", n_task_steps_role="2", n_raw_steps_role="4"),
             census(step_pos="4", action_idx="1", chamada_id="2", n_actions_role="2", n_task_steps_role="2", n_raw_steps_role="4",
                    structured_error="1", error_like="1", error_source="STRUCTURED_ERROR", error_type="AgentExecutionError")]
        a = construir_episodios_observados(state(*r))
        self.assertEqual(a.episodios.n_ancoras.max(), 2)
        self.assertEqual(set(a.episodios.chamada), {"multiplos_contadores_taskstep"})

    def test_referencias_estaveis_ao_reordenar(self):
        r = rows_chain(3)
        a = construir_episodios_observados(state(*r))
        b = construir_episodios_observados(state(*reversed(r)))
        self.assertEqual(set(a.episodios.episodio_ref), set(b.episodios.episodio_ref))


class TestMecanismos(unittest.TestCase):
    def analyze(self, *rows):
        return BP.analisar_mecanismos_observaveis(state(*rows))

    def test_regra_por_mensagem_reaproveitada(self):
        a = self.analyze(janela())
        r = a.EU.iloc[0]
        self.assertEqual(r.submecanismo, RAW1.submecanismo(r.err_msg))
        self.assertEqual(r.unidade, "U_contrato_dict")

    def test_mensagem_limitada_nao_vira_residuo(self):
        a = self.analyze(janela(error_message="Could not index " + "x" * (20000 - len("Could not index "))))
        self.assertEqual(a.EU.situacao_mecanismo.iloc[0], "pendente")
        self.assertTrue(a.EU.unidade.isna().all())

    def test_fallback_mensagem_integral_residuo(self):
        a = self.analyze(janela(error_message="fixture sem regra"))
        self.assertEqual(a.EU.unidade.iloc[0], "X_sintoma_nao_reconhecido")

    def test_timeout_sem_prompt_nao_codigo_lento(self):
        a = self.analyze(janela(error_message="exceeded the maximum execution time", error_code_action="final_answer('fixture')"))
        self.assertTrue(a.EU.unidade.isna().all())
        self.assertIn("prompt", a.EU.motivo_evidencia.iloc[0])

    def test_precedencia_harness_antes_de_parsing(self):
        a = self.analyze(janela(error_message="regex pattern SyntaxError fixture"))
        self.assertEqual(a.EU.submecanismo.iloc[0], "harness_bloco_code")

    def test_nome_predecessor_estruturado_reproduz_proxy(self):
        r = rows_chain()
        r[1]["error_message"] = "variable `x` is not defined"
        set_slot(r[0], "next", r[1])
        a = self.analyze(*r)
        self.assertEqual(a.EU.iloc[1].submecanismo, "nome_de_step_que_falhou")
        self.assertIn("proxy", a.EU.iloc[1].motivo_evidencia)

    def test_nome_predecessor_suspeito_nao_estruturado(self):
        r = rows_chain(2, suspect_at=0)
        r[1]["error_message"] = "variable `x` is not defined"
        set_slot(r[0], "next", r[1])
        a = self.analyze(*r)
        self.assertEqual(a.EU.submecanismo.iloc[0], "nome_nunca_definido")

    def test_nome_sem_predecessor_pendente(self):
        a = self.analyze(janela(error_message="variable `x` is not defined"))
        self.assertTrue(a.EU.unidade.isna().all())

    def test_nome_reset_pendente(self):
        r = rows_chain()
        r[1].update(error_message="variable `x` is not defined", step_number="1")
        set_slot(r[0], "next", r[1])
        a = self.analyze(*r)
        self.assertTrue(pd.isna(a.EU.iloc[1].submecanismo))

    def test_modulo_sem_import_independe_predecessor(self):
        a = self.analyze(janela(error_message="variable `json` is not defined"))
        self.assertEqual(a.EU.submecanismo.iloc[0], "modulo_sem_import")

    def test_parsing_novo_sem_codigo_integral_pendente(self):
        a = self.analyze(janela(error_message="Code parsing failed on line 1 due to: SyntaxError: invalid syntax",
                                error_code_action="x" * 12000))
        self.assertTrue(a.EU.unidade.isna().all())

    def test_parsing_novo_codigo_integral_texto_solto(self):
        a = self.analyze(janela(error_message="Code parsing failed on line 1 due to: SyntaxError: invalid syntax",
                                error_code_action="# fixture de texto livre"))
        self.assertEqual(a.EU.submecanismo.iloc[0], "texto_solto_no_codigo")

    def test_parsing_antigo_linha_na_mensagem_sem_codigo(self):
        # TRANSCRIÇÃO: o fim desta mensagem saiu cortado na foto (depois de "Error: un"); completado.
        a = self.analyze(janela(error_message="Code parsing failed on line 1 due to: SyntaxError\nhello = 'unterminated\nError: unterminated string literal",
                                error_code_action=None))
        self.assertEqual(a.EU.submecanismo.iloc[0], "texto_em_literal")

    def test_parsing_repr_colado_negativo_em_historico_incompleto_pendente(self):
        code = "data = {'a': 'text', 'b': 'text'}"
        a = self.analyze(janela(error_message="Code parsing failed on line 1 due to: SyntaxError: invalid syntax",
                                error_code_action=code, prev_step_number="0", prev_error_like="0", prev_observations="fixture"))
        self.assertTrue(a.EU.unidade.isna().all())

    def test_parsing_repr_colado_evidencia_positiva(self):
        code = "data = {'a': 'text', 'b': 'text'}"
        a = self.analyze(janela(error_message="Code parsing failed on line 1 due to: SyntaxError: invalid syntax",
                                error_code_action=code, prev_step_number="0", prev_error_like="0",
                                prev_observations="{'a': 'return', 'b': 'return'}"))
        self.assertEqual(a.EU.submecanismo.iloc[0], "repr_colado")

    def test_final_answer_nao_precisa_excluir_historico_repr(self):
        code = "final_answer({'a': 'text', 'b': 'text'})"
        # TRANSCRIÇÃO: a linha abaixo saiu cortada à direita na foto (depois de "error_code_acti"); completada.
        a = self.analyze(janela(error_message="Code parsing failed on line 1 due to: SyntaxError: invalid syntax", error_code_action=code))
        self.assertEqual(a.EU.submecanismo.iloc[0], RAW1.submecanismo(a.EU.err_msg.iloc[0], code, 0, True))

    def test_suspeitas_sem_mecanismo_na_taxonomia(self):
        a = self.analyze(*rows_chain(2, suspect_at=0))
        self.assertEqual(len(a.EU), 1)
        self.assertEqual(a.episodios.episodios[a.episodios.episodios.definicao.eq("misto")].n_ancoras.sum(), 2)

    def test_contagem_custos_pendencias_conservados(self):
        a = self.analyze(janela(), janela(step_pos="3", error_message="exceeded the maximum execution time"))
        self.assertEqual(a.tabelas["cobertura_mecanismos"].tokens_n_conhecidos.sum(), 24)
        self.assertEqual(a.tabelas["mecanismos"].tokens_n_conhecidos.sum(), 12)
        self.assertEqual(a.tabelas["cobertura_mecanismos"].erros.sum(), 2)

    def test_nao_habilita_triagem_legada(self):
        a = self.analyze(janela())
        self.assertNotIn("ocorrencia", a.EU)
        self.assertNotIn("cascata", a.EU)
        self.assertEqual(a.cobertura["triagem"], "bloqueada")
        with self.assertRaises(BP.AnaliseNaoIntegrada):
            BP.montar_unidades(a.EU)

    def test_carga_vazia_sem_inventar_unidades(self):
        # TRANSCRIÇÃO: linha cortada à direita na foto (depois de "error_type=None, error"); completada.
        b = state(janela(structured_error="0", observation_suspect="1", error_source="OBSERVATION_SUSPECT", error_type=None, error_message=None))
        a = BP.analisar_mecanismos_observaveis(b)
        self.assertTrue(a.EU.empty)
        self.assertEqual(a.resumo["pendentes"], 0)


if __name__ == "__main__":
    unittest.main()
