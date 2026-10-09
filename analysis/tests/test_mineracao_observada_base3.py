"""Fixtures sintéticas: recorrência sem censo, proveniência e publicação fechada."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

import matplotlib
matplotlib.use("Agg")
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_sintomas_base3 import state
from test_adaptador_trace import janela, pair
from test_integracao_carga_base3 import BP
sys.path.insert(0, str(Path(BP.__file__).parent))
import mineracao_observada as mo


def recorrentes(message="Could not index: string indices must be integers"):
    return [janela(cod_idef_exeo=f"exec-sintetica-{i}", error_message=message,
                   dat_hor_inio_exeo=f"2026-{7 + i % 2:02d}-01 10:00:00",
                   dat_hor_encm_exeo=f"2026-{7 + i % 2:02d}-01 10:01:00", mes_execucao=f"2026-{7 + i % 2:02d}")
            for i in range(3)]


class TestTriagemObservada(unittest.TestCase):
    def test_candidatura_sem_censo_sem_sucesso_sem_silenciosas(self):
        with patch.object(mo.bp, "carregar_base", side_effect=AssertionError("raw")), \
                patch.object(mo.bp, "medir_sucesso", side_effect=AssertionError("sucesso")), \
                patch.object(mo.bp, "falhas_silenciosas", side_effect=AssertionError("silenciosas")):
            a = mo.analisar(state(*recorrentes()))
        t = a.tabelas["triagem_visivel_observada"].iloc[0]
        self.assertEqual(t.decisao, mo.CANDIDATO)
        self.assertEqual(t.execucoes, 3)
        self.assertEqual(t.meses, 2)
        self.assertEqual(t.silenciosas, "não medidas")
        self.assertFalse(a.capacidades["taxas_globais"])
        self.assertTrue(a.carga.steps.idx.isna().all())

    def test_nao_inventa_recorrencia_faltante(self):
        a = mo.analisar(state(janela()))
        self.assertEqual(a.tabelas["triagem_visivel_observada"].decisao.iloc[0], mo.SEM_RECORRENCIA)

    def test_sensibilidade_mais_estrita(self):
        a = mo.analisar(state(*recorrentes()))
        self.assertEqual(a.tabelas["triagem_sensibilidade"].decisao.iloc[0], mo.SEM_RECORRENCIA)

    def test_nao_herda_harness_base2(self):
        a = mo.analisar(state(*recorrentes("Could not index: KeyError: 'campo_sintetico'")))
        self.assertEqual(a.tabelas["triagem_visivel_observada"].destino_proposto.iloc[0], "em aberto")

    def test_plataforma_e_residuo_nao_candidatos(self):
        for message in ["No code block found", "mensagem sintetica desconhecida"]:
            a = mo.analisar(state(*recorrentes(message)))
            self.assertFalse(a.tabelas["triagem_visivel_observada"].decisao.eq(mo.CANDIDATO).any())

    def test_pendencias_preservadas_no_custo_e_genealogia(self):
        rows = recorrentes() + [janela(cod_idef_exeo="exec-pendente", error_message="x" * 20000, total_tokens="100")]
        a = mo.analisar(state(*rows))
        graph = mo.genealogia(a)
        self.assertEqual(len(graph), 4)
        self.assertFalse(graph[["familia", "assinatura", "submecanismo", "unidade", "destino"]].isna().any().any())
        self.assertEqual(graph.destino.eq("COMPLEMENTAR evidência").sum(), 1)
        self.assertEqual(a.tabelas["cobertura_mecanismos"].tokens_n_conhecidos.sum(), 136)
        self.assertEqual(a.tabelas["triagem_visivel_observada"].tokens_n_conhecidos.sum(), 36)

    def test_suspeita_nao_entra_em_unidade(self):
        suspect = janela(cod_idef_exeo="exec-suspeita", structured_error="0", observation_suspect="1",
                         error_source="OBSERVATION_SUSPECT", error_type=None, error_message=None)
        a = mo.analisar(state(*recorrentes(), suspect))
        self.assertEqual(len(a.EU), 3)
        self.assertEqual(a.resumo["suspeitas_fora_taxonomia"], 1)

    def test_sem_erro_estruturado_nao_fabrica_tabela(self):
        row = janela(structured_error="0", observation_suspect="1", error_source="OBSERVATION_SUSPECT",
                     error_type=None, error_message=None)
        a = mo.analisar(state(row))
        self.assertTrue(a.tabelas["triagem_visivel_observada"].empty)

    def test_mesma_cascata_nao_reconstruida_por_subconjunto(self):
        first, second = pair(error_message="x" * 20000)
        a = mo.analisar(state(first, second))
        self.assertEqual(a.EU.episodio_estruturado_ref.nunique(), 1)
        self.assertEqual(a.tabelas["triagem_visivel_observada"].ocorrencias_condicionais.sum(), 1)
        self.assertEqual(a.tabelas["triagem_visivel_observada"].erros_limites_abertos.sum(), 1)

    def test_custo_ausente_nao_zero_nem_percentual(self):
        a = mo.analisar(state(*[dict(r, total_tokens=None) for r in recorrentes()]))
        t = a.tabelas["triagem_visivel_observada"].iloc[0]
        self.assertTrue(pd.isna(t.tokens_n_conhecidos))
        self.assertEqual(t.tokens_n_ausentes, 3)
        self.assertTrue(pd.isna(t.pct_tokens_todos_estruturados))

    def test_mecanismos_de_outra_fonte_rejeitados(self):
        a = mo.analisar(state(*recorrentes()))
        a.EU.attrs["fonte_carga_id"] = "outra-fonte"
        with self.assertRaises(mo.bp.AnaliseNaoIntegrada):
            mo.triagem_observada(a.carga, a.mecanismos)

    def test_custo_adulterado_rejeitado(self):
        a = mo.analisar(state(*recorrentes()))
        a.EU.loc[a.EU.index[0], "tok_tot"] = 999
        with self.assertRaises(mo.bp.AnaliseNaoIntegrada):
            mo.triagem_observada(a.carga, a.mecanismos)

    def test_nao_muta_carga(self):
        b = state(*recorrentes())
        before = b.steps.copy(deep=True)
        mo.analisar(b)
        pd.testing.assert_frame_equal(before, b.steps)
        self.assertIsNone(b.EU)

    def test_identidade_execucao_inclui_agente(self):
        rows = recorrentes()
        rows[1]["cod_idef_exeo"] = rows[0]["cod_idef_exeo"]
        rows[1]["cod_idef_aget"] = "2"
        # Metadados não devem variar dentro da identidade legada; aqui há dois agentes.
        a = mo.analisar(state(*rows))
        self.assertEqual(a.tabelas["triagem_visivel_observada"].execucoes.iloc[0], 3)

    def test_sem_limiar_invalido(self):
        a = mo.analisar(state(janela()))
        with self.assertRaises(ValueError):
            mo.triagem_observada(a.carga, a.mecanismos, 0, 2)


class TestPerfil(unittest.TestCase):
    def test_desconhecido_nao_vira_primeira_chamada_ou_ultimo_step(self):
        a = mo.analisar(state(*recorrentes()))
        p = mo.perfil_unidade(a, "U_tipo_retorno")
        cases = p["casos"]
        self.assertEqual(len(cases), p["perfil"].erros_observaveis.iloc[0])
        self.assertTrue(cases.antes.eq("desconhecido").all())
        self.assertTrue(cases.depois.eq("desconhecido").all())
        self.assertTrue(cases[["idx", "modelo", "versao_prompt", "mesma_chamada", "sucesso_semantico"]].isna().all().all())
        self.assertTrue(cases.step_pos.notna().all())

    def test_vizinho_sem_sinal_nao_sucesso(self):
        rows = [dict(r, next_step_number="2", next_error_like="0", next_is_final_answer="false") for r in recorrentes()]
        a = mo.analisar(state(*rows))
        cases = mo.perfil_unidade(a, "U_tipo_retorno")["casos"]
        self.assertTrue(cases.depois.str.contains("não sucesso").all())
        self.assertTrue(cases.proximo_final_observado.eq(False).all())

    def test_nao_minera_unidade_fora_da_triagem(self):
        a = mo.analisar(state(janela()))
        with self.assertRaises(mo.bp.AnaliseNaoIntegrada):
            mo.perfil_unidade(a, "U_contrato_dict")

    def test_amostra_e_rodada_reprodutiveis(self):
        a, b = mo.analisar(state(*recorrentes())), mo.analisar(state(*recorrentes()))
        self.assertEqual(a.manifesto["rodada_id"], b.manifesto["rodada_id"])
        pd.testing.assert_frame_equal(mo.perfil_unidade(a, "U_tipo_retorno")["amostra_investigacao"],
                                      mo.perfil_unidade(b, "U_tipo_retorno")["amostra_investigacao"])


class TestProveniencia(unittest.TestCase):
    def test_io_caminho_longo_sem_renomear_artefato(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / ("a" * 80) / ("b" * 80) / ("c" * 80) / "amostra_investigacao.csv"
            extended = mo.caminho_io(path)
            extended.parent.mkdir(parents=True)
            try:
                extended.write_text("fixture\n1\n", encoding="utf-8")
                self.assertEqual(extended.name, path.name)
                self.assertEqual(mo.sha256(path), mo.sha256(extended))
                dotted = path.parent / ".." / path.parent.name / path.name
                self.assertEqual(mo.sha256(dotted), mo.sha256(path))
            finally:
                # tempfile/shutil também sofrem o limite ao limpar a fixture.
                extended.unlink(missing_ok=True)
                extended.parent.rmdir()

    def test_inventario_hash_nao_data_modificacao(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            current, old = root / "third/pipeline", root / "second/pipeline"
            for p in [current, old]:
                (p / "resultados").mkdir(parents=True)
                (p / "resultados/a.csv").write_text('valor\n"linha\ncom quebra"\n', encoding="utf-8")
            table = mo.inventariar(current, old)
            self.assertEqual(table.registros.iloc[0], 1)
            self.assertEqual(table.estado.iloc[0], "legado_igual_second")

    def test_parquet_invalido_bloqueia_sem_reparo(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "invalido.parquet"
            path.write_bytes(b"nao e parquet")
            with self.assertRaises(mo.bp.AnaliseNaoIntegrada):
                mo.conferir_fonte(path)
            self.assertEqual(path.read_bytes(), b"nao e parquet")

    def test_snapshot_divergente_bloqueia(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "fonte.parquet"
            path.write_bytes(b"fixture")
            with self.assertRaisesRegex(mo.bp.AnaliseNaoIntegrada, "referência"):
                mo.conferir_fonte(path, "0" * 64)

    def test_saida_canonica_proibida(self):
        a = mo.analisar(state(*recorrentes()))
        with self.assertRaises(ValueError):
            mo.gravar(a, mo.HERE / "resultados")

    def test_manifest_rejeita_csv_antigo(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            m = {"contrato": mo.CONTRATO, "base": "base2", "fonte_id": "fixture", "rodada_id": "rodada"}
            (root / "manifesto.json").write_text(json.dumps(m), encoding="utf-8")
            with self.assertRaises(mo.bp.AnaliseNaoIntegrada):
                mo.ler_artefato(root, "candidatos_memoria.csv", fonte_id="fixture", rodada_id="rodada")

    def test_publicacao_sintetica_com_graficos_manifest_e_perfis(self):
        with tempfile.TemporaryDirectory() as d:
            here = Path(d) / "pipeline"
            with patch.object(mo, "HERE", here), patch.object(mo, "versoes_codigo", return_value={"fixture": "hash"}):
                a = mo.analisar(state(*recorrentes()))
                dest = mo.gravar(a, perfis=["U_tipo_retorno"])
                table = mo.ler_artefato(dest, "triagem_visivel_observada.csv", fonte_id=a.carga.fonte["id"],
                                        rodada_id=a.manifesto["rodada_id"])
                self.assertEqual(table.erros_observaveis.sum(), 3)
                manifest = json.loads((dest / "manifesto.json").read_text(encoding="utf-8"))
                self.assertFalse(manifest["aprovacao_memorias"])
                self.assertIn("genealogia_observada.png", manifest["artefatos"])
                self.assertIn("perfis/U_tipo_retorno/casos.csv", manifest["artefatos"])
                (dest / "triagem_visivel_observada.csv").write_text("adulterado", encoding="utf-8")
                with self.assertRaises(mo.bp.AnaliseNaoIntegrada):
                    mo.ler_artefato(dest, "triagem_visivel_observada.csv", fonte_id=a.carga.fonte["id"],
                                    rodada_id=a.manifesto["rodada_id"])


class TestPainel(unittest.TestCase):
    def test_painel_so_contagens_e_recusa_csv_alterado(self):
        sys.path.insert(0, str(mo.HERE))
        from execucao import painel
        with tempfile.TemporaryDirectory() as d:
            here = Path(d) / "pipeline"
            with patch.object(mo, "HERE", here), patch.object(mo, "versoes_codigo", return_value={"fixture": "hash"}):
                a = mo.analisar(state(*recorrentes()))
                dest = mo.gravar(a)
            saida = painel.gerar(dest)
            md = (saida / "painel.md").read_text(encoding="utf-8")
            self.assertIn("U_tipo_retorno", md)
            self.assertNotIn("exec-sintetica", md)
            self.assertTrue((saida / "cobertura.png").is_file())
            for nome in ["destinos.png", "frequencia_custo.png", "concentracao_papel.png", "papeis_candidatas.png",
                         "linha_do_tempo.png"]:
                self.assertTrue((saida / nome).is_file(), nome)
            self.assertIn("**Limitação:**", md)
            (dest / "triagem_visivel_observada.csv").write_text("adulterado", encoding="utf-8")
            with self.assertRaises(SystemExit):
                painel.gerar(dest)


class TestConsolidacaoPython(unittest.TestCase):
    """O que os notebooks consolidacao_unidades/mineracao_generica mostravam, agora tabelas da rodada."""

    def test_consolidacao_conserva_triagem_e_cobertura(self):
        a = mo.analisar(state(*recorrentes(), janela(cod_idef_exeo="exec-pendente", error_message="x" * 20000)))
        c = a.tabelas
        self.assertEqual(c["consolidacao_limitrofes"].unidade.tolist(), ["U_tipo_retorno"])
        self.assertFalse(c["consolidacao_limitrofes"].candidata_5_3.iloc[0])
        self.assertEqual(c["consolidacao_unidade_papel_mes"].erros.sum(), 3)
        self.assertEqual(c["consolidacao_pendencias"].erros.sum(), 1)
        self.assertEqual(c["consolidacao_componentes_limites"].componentes.sum(), len(a.mecanismos.episodios.episodios))
        self.assertTrue(c["consolidacao_global_papel"].candidata_global.all())

    def test_perfil_traz_final_do_vizinho_sem_notebook(self):
        a = mo.analisar(state(*recorrentes()))
        p = mo.perfil_unidade(a, "U_tipo_retorno")
        self.assertEqual(p["proximo_final"].erros.sum(), 3)
        self.assertNotIn("consolidacao_unidades.ipynb", " ".join(mo.versoes_codigo()))


if __name__ == "__main__":
    unittest.main()
