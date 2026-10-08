"""Entrada única, roteamento sem mineração acidental e scripts movidos."""
from contextlib import redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

PIPELINE = Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third/pipeline"
sys.path.insert(0, str(PIPELINE))
import executar
from execucao import executar_observada
from validacao import conferir_rodada_observada, validar_observada


class TestEntradaUnica(unittest.TestCase):
    def test_sem_comando_so_ajuda(self):
        with redirect_stdout(io.StringIO()) as output, patch.object(executar_observada, "main") as run:
            self.assertEqual(executar.main([]), 0)
        run.assert_not_called()
        self.assertIn("analisar", output.getvalue())

    def test_analisar_preserva_opcoes_de_fonte_e_perfil(self):
        with patch.object(executar_observada, "main", return_value=0) as run:
            self.assertEqual(executar.main(["analisar", "--fonte", "fixture.parquet", "--perfil", "U_tipo_retorno"]), 0)
        run.assert_called_once_with(["--fonte", "fixture.parquet", "--perfil", "U_tipo_retorno"])

    def test_inventariar_nao_e_analise_real(self):
        with patch.object(executar_observada, "main", return_value=0) as run:
            self.assertEqual(executar.main(["inventariar"]), 0)
        run.assert_called_once_with(["--inventario-only"])

    def test_validar_roteia_so_para_sinteticos(self):
        with patch.object(validar_observada, "main", return_value=0) as validate, \
                patch.object(conferir_rodada_observada, "main") as real:
            self.assertEqual(executar.main(["validar"]), 0)
        validate.assert_called_once_with()
        real.assert_not_called()

    def test_conferir_roteia_para_conferencia_real(self):
        with patch.object(conferir_rodada_observada, "main", return_value=0) as real:
            self.assertEqual(executar.main(["conferir"]), 0)
        real.assert_called_once_with()

    def test_scripts_relocalizados_resolvem_pipeline(self):
        self.assertEqual(executar_observada.PIPELINE, PIPELINE)
        self.assertEqual(validar_observada.PIPELINE, PIPELINE)
        self.assertEqual(conferir_rodada_observada.PIPELINE, PIPELINE)

    def test_entrada_funciona_fora_da_raiz(self):
        result = subprocess.run([sys.executable, str(PIPELINE / "executar.py"), "--help"],
                                cwd=PIPELINE.parent, capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("inventariar", result.stdout)

    def test_historico_nao_acionado_por_entrada_atual(self):
        self.assertFalse((PIPELINE / "validar_base3.py").exists())
        self.assertTrue((PIPELINE / "validacao/historico/validar_base3.py").is_file())
        # A entrada atual não lê resultados de rodadas antigas (apagáveis): referência fica no código.
        for name in ["validar_observada.py", "conferir_rodada_observada.py"]:
            source = (PIPELINE / "validacao" / name).read_text(encoding="utf-8")
            self.assertNotIn("resultados/etapa7", source)
            self.assertNotIn("validacao_fechamento", source)


if __name__ == "__main__":
    unittest.main()
