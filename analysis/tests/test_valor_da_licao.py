"""valor_da_licao (Ajuste 20): a parte específica nova é script; notebook continua como legado da base 1."""
import importlib.util
from pathlib import Path
import unittest

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "valor_da_licao", RAIZ / ".claude/skills/mineracao-candidata/scripts/valor_da_licao.py")
vl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vl)


class TestValorDaLicao(unittest.TestCase):
    def test_parte_especifica_existente(self):
        for tipo in ("script", "notebook"):
            conf = vl.confianca("/nao/existe", "U_x", f"{tipo}:mineracao_U_x")
            self.assertEqual(conf, f"confirmada ({tipo})")
            self.assertEqual(vl.situacao("Pareto", conf), tipo)

    def test_pronta_para_script_tem_gate_com_a_skill_nova(self):
        self.assertEqual(vl.situacao("Pareto", "confirmada"), "pronta para script")
        self.assertIn("propor o script (/propor-script)", vl.GATE["pronta para script"])
        self.assertNotIn("pronta para notebook", vl.GATE)


if __name__ == "__main__":
    unittest.main()
