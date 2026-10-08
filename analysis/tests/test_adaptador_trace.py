"""Fixtures sintéticas; nenhum dado de cliente nos testes versionados."""
from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adaptador_trace import (
    CENSO, JANELAS, TRACE_COMPLETO, COLUNAS_CENSO, COLUNAS_JANELAS,
    ErroContrato, adaptar, carregar_fonte, detectar_contrato,
)


def janela(**changes):
    r = dict.fromkeys(COLUNAS_JANELAS)
    r.update(cod_idef_exeo="exec-sintetica", cod_idef_aget="1", papel="Agent",
             cod_idef_stat_exeo_aget="3", cod_idef_cvsa_asnc="fluxo-sintetico", cod_vers_aget="2",
             dat_hor_inio_exeo="2026-08-01 10:00:00", dat_hor_encm_exeo="2026-08-01 10:01:00",
             mes_execucao="2026-08", anomesdia="20260930", has_final_locals="1", has_persisted_response="1",
             execution_has_final_step="1", error_source="STRUCTURED_ERROR", structured_error="1", observation_suspect="0",
             step_number="1", step_pos="2", error_type="AgentExecutionError", error_message="Could not index: KeyError: 0",
             error_code_action="x = data[0]", error_model_output="Diagnostico sintetico", error_observations="retorno sintetico",
             tool_calls="[]", input_tokens="10", output_tokens="2", total_tokens="12", duration_seconds="0.5",
             recovery_signal="UNKNOWN", num_actions_after_error_observed="0", has_full_2_action_window="0")
    r.update(changes)
    return r


def set_slot(r, prefix, target):
    for field in ["step_number", "error_type", "error_message", "tool_name", "input_tokens", "output_tokens", "total_tokens", "duration_seconds"]:
        key = prefix + "_" + field
        if key in r:
            r[key] = target[field]
    for name, field in [("code_action", "error_code_action"), ("model_output", "error_model_output"), ("observations", "error_observations")]:
        r[prefix + "_" + name] = target[field]
    r[prefix + "_error_like"] = "1"
    if prefix + "_is_final_answer" in r:
        r[prefix + "_is_final_answer"] = "false"


def pair(**changes_second):
    a, b = janela(), janela(step_number="2", step_pos="3", **changes_second)
    set_slot(a, "next", b)
    set_slot(b, "prev", a)
    return a, b


def census(**changes):
    r = dict.fromkeys(COLUNAS_CENSO)
    r.update(extraction_contract=CENSO, cod_idef_exeo="exec-sintetica", cod_idef_aget="1",
             papel_original="Agent", papel="Agent", cod_idef_stat_exeo_aget="3", cod_idef_cvsa_asnc="fluxo-sintetico",
             cod_vers_aget="2", dat_hor_inio_exeo="2026-08-01 10:00:00", dat_hor_encm_exeo="2026-08-01 10:01:00",
             mes_execucao="2026-08", anomesdia="20260930", source_trace_sha256="a" * 64, source_trace_length="100",
             has_final_locals="1", has_persisted_response="1", step_pos="2", step_number="1", action_idx="0",
             n_actions_role="1", chamada_id="1", n_task_steps_role="1", n_planning_steps_role="0", n_raw_steps_role="2",
             is_final_answer="false", role_has_final_step="0", n_actions_final_flag_unknown="0",
             structured_error="0", observation_suspect="0", error_like="0", error_source="NO_ERROR_SIGNAL",
             input_tokens="10", output_tokens="2", total_tokens="12", duration_seconds="0.5",
             action_output_kind="ABSENT_OR_SQL_NULL")
    r.update(changes)
    return r


def typed_text(r, field, value, cap):
    stem = field.removesuffix("_fragment") if field.endswith("_fragment") else field
    r[field] = None if value is None else value[:cap]
    r[stem + "_length"] = None if value is None else str(len(value))
    r[stem + "_truncated"] = None if value is None else str(len(value) > cap).lower()


def adapt(*rows):
    return adaptar(pd.DataFrame(rows), fonte_id="fonte-sintetica")


class TestSchema(unittest.TestCase):
    def test_detecta_janelas(self):
        self.assertEqual(detectar_contrato(COLUNAS_JANELAS), JANELAS)

    def test_detecta_censo(self):
        self.assertEqual(detectar_contrato(COLUNAS_CENSO), CENSO)

    def test_raw_preservado_sem_reimplementar(self):
        df = pd.DataFrame([dict(txt_etap_memo="{}")])
        self.assertEqual(detectar_contrato(df), TRACE_COMPLETO)
        with self.assertRaisesRegex(ErroContrato, "caminho existente"):
            adaptar(df, fonte_id="sintetica")

    def test_schema_misto_rejeitado(self):
        with self.assertRaises(ErroContrato):
            detectar_contrato(set(COLUNAS_JANELAS) | set(COLUNAS_CENSO))

    def test_schema_incompleto_rejeitado(self):
        df = pd.DataFrame([janela()]).drop(columns="error_observations")
        with self.assertRaisesRegex(ErroContrato, "incompleto"):
            adaptar(df, fonte_id="sintetica")

    def test_sem_fonte_rejeitado(self):
        with self.assertRaises(ErroContrato):
            adaptar(pd.DataFrame([janela()]), fonte_id="")


class TestNormalizacao(unittest.TestCase):
    def test_nao_muta_dataframe(self):
        df = pd.DataFrame([janela()])
        before = df.copy(deep=True)
        b = adaptar(df, fonte_id="sintetica")
        pd.testing.assert_frame_equal(df, before)
        self.assertEqual(b.steps.iloc[0].tok_tot, 12)

    def test_nulos_nao_sao_zero_contexto_ou_idx(self):
        b = adapt(janela(total_tokens=None, input_tokens=None, duration_seconds=None))
        r = b.steps.iloc[0]
        for c in ["tok_tot", "tok_in", "dur_s", "idx", "n_steps_role", "chamada_id", "is_final", "ctx", "sysprompt"]:
            self.assertTrue(pd.isna(r[c]), c)
        self.assertEqual(r.ctx_estado, "nao_exportado")

    def test_false_textual_nao_e_true(self):
        a = janela(next_step_number="2", next_error_like="0", next_is_final_answer="false")
        b = adapt(a)
        r = b.slots[b.slots.offset.eq(1)].iloc[0]
        self.assertFalse(r.is_final)
        self.assertFalse(r.error_like)

    def test_mes_real_distinto_da_particao(self):
        b = adapt(janela())
        self.assertEqual(b.steps.mes.iloc[0], "2026-08")
        self.assertEqual(b.steps.mes_particao.iloc[0], "2026-09")
        self.assertEqual(int(b.steps.particao_fonte.iloc[0]), 20260930)

    def test_booleano_invalido_rejeitado(self):
        with self.assertRaises(ErroContrato):
            adapt(janela(structured_error="yes"))

    def test_numero_fracionario_rejeitado(self):
        with self.assertRaises(ErroContrato):
            adapt(janela(step_pos="2.5"))

    def test_chave_nula_rejeitada(self):
        with self.assertRaises(ErroContrato):
            adapt(janela(cod_idef_exeo=None))

    def test_duplicidade_rejeitada_sem_descartar(self):
        with self.assertRaisesRegex(ErroContrato, "duplicada"):
            adapt(janela(), janela())

    def test_tipo_indicador_incompativel(self):
        with self.assertRaises(ErroContrato):
            adapt(janela(structured_error="0"))

    def test_suspeita_nao_vira_estruturado(self):
        b = adapt(janela(structured_error="0", observation_suspect="1", error_type=None,
                         error_source="OBSERVATION_SUSPECT", error_message=None))
        self.assertEqual(b.resumo()["estruturados"], 0)
        self.assertEqual(b.resumo()["suspeitas"], 1)

    def test_complemento_A_com_origem_nula(self):
        b = adapt(janela(structured_error="0", observation_suspect="0", error_type=None,
                         error_source=None, error_message=None))
        self.assertEqual(b.resumo()["sem_sinal"], 1)
        self.assertTrue(pd.isna(b.origem.error_source.iloc[0]))

    def test_snapshot_metadados_mistos_rejeitado(self):
        a, b = pair()
        b["cod_vers_aget"] = "3"
        with self.assertRaisesRegex(ErroContrato, "snapshots"):
            adapt(a, b)

    def test_custo_negativo_rejeitado(self):
        with self.assertRaises(ErroContrato):
            adapt(janela(total_tokens="-1"))

    def test_inteiro_grande_preservado_sem_float(self):
        b = adapt(janela(total_tokens="9007199254740993"))
        self.assertEqual(int(b.steps.tok_tot.iloc[0]), 9007199254740993)

    def test_inteiro_fora_int64_rejeitado(self):
        with self.assertRaises(ErroContrato):
            adapt(janela(total_tokens="9223372036854775808"))

    def test_referencias_estaveis_independem_ordem(self):
        a, b = pair()
        x, y = adapt(a, b), adapt(b, a)
        self.assertEqual(set(x.steps.step_ref), set(y.steps.step_ref))
        self.assertEqual(x.vinculos.origem_ref.to_list(), y.vinculos.origem_ref.to_list())


class TestTexto(unittest.TestCase):
    def test_legado_limite_e_possibilidade_nao_corte_certo(self):
        b = adapt(janela(error_code_action="x" * 12000))
        self.assertEqual(b.steps.code_estado.iloc[0], "possivelmente_cortado")
        self.assertEqual(len(b.steps.code.iloc[0]), 12000)

    def test_limite_excedido_rejeitado(self):
        with self.assertRaises(ErroContrato):
            adapt(janela(error_code_action="x" * 12001))

    def test_censo_distingue_corte_e_exato(self):
        for length, state in [(12000, "sem_corte_sql"), (12001, "cortado")]:
            r = census()
            typed_text(r, "code_action", "x" * length, 12000)
            self.assertEqual(adapt(r).steps.code_estado.iloc[0], state)

    def test_flag_corte_falsa_inconsistente(self):
        r = census()
        typed_text(r, "code_action", "x" * 12001, 12000)
        r["code_action_truncated"] = "false"
        with self.assertRaises(ErroContrato):
            adapt(r)

    def test_json_fragmento_preservado_nao_reparado(self):
        r = census()
        full = '[{"text":"' + "x" * 13000 + '"}]'
        typed_text(r, "tool_calls_json_fragment", full, 12000)
        b = adapt(r)
        self.assertEqual(b.steps.tool_calls.iloc[0], full[:12000])
        self.assertEqual(b.steps.tool_calls_estado.iloc[0], "cortado")

    def test_objeto_action_output_nao_confundido_com_scalar(self):
        r = census(action_output_kind="OBJECT")
        typed_text(r, "action_output_json_fragment", '{"answer":1}', 12000)
        b = adapt(r)
        self.assertTrue(pd.isna(b.steps.out.iloc[0]))
        self.assertEqual(b.steps.out_json.iloc[0], '{"answer":1}')

    def test_vazio_B_com_comprimento_zero(self):
        r = census()
        typed_text(r, "code_action", "", 12000)
        self.assertEqual(adapt(r).steps.code_estado.iloc[0], "vazio_na_origem")


class TestVinculos(unittest.TestCase):
    def test_par_reciproco_candidato_nao_episodio(self):
        b = adapt(*pair())
        self.assertEqual(b.vinculos.estado.to_list(), ["compativel_candidato"])
        self.assertTrue(b.vinculos.mesma_chamada.isna().all())
        self.assertNotIn("cascata", b.steps)

    def test_gap_pos_original_nao_interrompe_actionstep(self):
        a, b = pair()
        b["step_pos"] = "5"
        self.assertEqual(adapt(a, b).vinculos.estado.iloc[0], "compativel_candidato")

    def test_numero_reinicia_fica_ambiguo(self):
        a, b = pair()
        b["step_number"] = "1"
        set_slot(a, "next", b)
        self.assertEqual(adapt(a, b).vinculos.estado.iloc[0], "ambiguo")

    def test_predecessor_suspeito_nao_e_erro_estruturado(self):
        a, b = pair()
        a.update(structured_error="0", observation_suspect="1", error_type=None,
                 error_source="OBSERVATION_SUSPECT", error_message=None)
        set_slot(b, "prev", a)
        x = adapt(a, b)
        self.assertEqual(x.vinculos.estado.iloc[0], "compativel_candidato")
        self.assertEqual(x.resumo()["estruturados"], 1)

    def test_prefixo_SQL_explicado(self):
        a, b = pair()
        a["error_code_action"] = "x" * 10000
        b["prev_code_action"] = "x" * 8000
        self.assertEqual(adapt(a, b).vinculos.prefixos_explicados.iloc[0], 1)

    def test_prefixo_arbitrario_rejeitado(self):
        a, b = pair()
        b["prev_code_action"] = a["error_code_action"][:2]
        self.assertEqual(adapt(a, b).vinculos.estado.iloc[0], "conflito")

    def test_conflito_nao_unido(self):
        a, b = pair()
        a["next_code_action"] = "other_code()"
        self.assertEqual(adapt(a, b).vinculos.estado.iloc[0], "conflito")

    def test_nulo_vs_conteudo_conflito_nao_igual(self):
        a, b = pair()
        a["next_code_action"] = None
        self.assertEqual(adapt(a, b).vinculos.estado.iloc[0], "conflito")

    def test_sem_reciprocidade_nao_unir(self):
        a, b = pair()
        b["prev_error_like"] = "0"
        b["prev_error_type"] = None
        self.assertTrue(adapt(a, b).vinculos.empty)

    def test_numero_ausente_no_vizinho_nao_e_ausencia(self):
        a = janela(next_step_number=None, next_error_like="0", next_code_action="answer()")
        b = adapt(a)
        self.assertEqual(b.slots[b.slots.offset.eq(1)].presenca.iloc[0], "numero_ausente_com_campos")

    def test_colisao_agente_suspende_janelas_legadas(self):
        a, b = pair()
        c = janela(cod_idef_aget="2")
        self.assertEqual(adapt(a, b, c).vinculos.estado.iloc[0], "ambiguo")

    def test_slots_sobrepostos_nao_entram_em_steps(self):
        b = adapt(*pair())
        self.assertEqual(len(b.steps), 2)
        self.assertEqual(len(b.slots), 6)
        self.assertEqual(b.steps.tok_tot.sum(), 24)


class TestCenso(unittest.TestCase):
    def test_censo_minimo_sem_inventar_populacao_global(self):
        b = adapt(census())
        self.assertEqual(b.steps.idx.iloc[0], 0)
        self.assertEqual(b.cobertura["populacao_global"], "condicionada_manifesto_externo")

    def test_ordem_censo_independente_step_number(self):
        a = census(n_actions_role="2", n_raw_steps_role="4", n_task_steps_role="2")
        b = census(step_pos="4", action_idx="1", chamada_id="2", n_actions_role="2",
                   n_raw_steps_role="4", n_task_steps_role="2")
        x = adapt(a, b)
        self.assertEqual(x.vinculos.estado.iloc[0], "ordem_censo")
        self.assertFalse(x.vinculos.mesma_chamada.iloc[0])

    def test_censo_grupo_incompleto_rejeitado(self):
        with self.assertRaisesRegex(ErroContrato, "incompleto"):
            adapt(census(n_actions_role="2"))

    def test_idx_repetido_rejeitado(self):
        a, b = census(n_actions_role="2", n_raw_steps_role="3"), census(step_pos="3", n_actions_role="2", n_raw_steps_role="3")
        with self.assertRaises(ErroContrato):
            adapt(a, b)

    def test_flag_final_nula_nao_false(self):
        b = adapt(census(is_final_answer=None, n_actions_final_flag_unknown="1"))
        self.assertTrue(pd.isna(b.steps.is_final.iloc[0]))

    def test_censo_origem_errorlike_inconsistente(self):
        with self.assertRaises(ErroContrato):
            adapt(census(error_like="1"))

    def test_versao_contrato_incorreta(self):
        with self.assertRaises(ErroContrato):
            adapt(census(extraction_contract="outra_versao"))

    def test_agentes_ou_papeis_originais_distintos_nao_unidos(self):
        a, b = census(), census(cod_idef_aget="2")
        self.assertTrue(adapt(a, b).vinculos.empty)
        c = census(papel_original=" Agent ")
        self.assertTrue(adapt(a, c).vinculos.empty)

    def test_sha_do_trace_invalido(self):
        with self.assertRaises(ErroContrato):
            adapt(census(source_trace_sha256=None))


class TestLeitor(unittest.TestCase):
    def test_contratos_vazios_nao_inventam_observacoes(self):
        for columns in [COLUNAS_JANELAS, COLUNAS_CENSO]:
            b = adaptar(pd.DataFrame(columns=columns), fonte_id="sintetica-vazia")
            self.assertEqual(b.resumo()["registros_n"], 0)
            self.assertTrue(b.vinculos.empty)

    def test_schema_tem_colunas_originais_esperadas(self):
        self.assertEqual(len(COLUNAS_JANELAS), 69)
        self.assertEqual(len(COLUNAS_CENSO), 61)
        self.assertEqual(len(set(COLUNAS_CENSO)), 61)

    def test_leitura_parquet_reusa_contrato_booleano(self):
        r = census()
        r["is_final_answer"] = False
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sintetico.parquet"
            pq.write_table(pa.Table.from_pandas(pd.DataFrame([r])), path)
            b = carregar_fonte(path)
            self.assertFalse(b.steps.is_final.iloc[0])
            self.assertEqual(b.fonte["formato"]["formato"], "parquet")
            self.assertEqual(len(b.fonte["sha256"]), 64)

    def test_leitura_csv_sintetica(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sintetico.csv"
            pd.DataFrame([janela()]).to_csv(path, index=False)
            self.assertEqual(carregar_fonte(path).resumo()["registros_n"], 1)


if __name__ == "__main__":
    unittest.main()
