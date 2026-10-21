"""contar_modulo_sem_import_papel.py (base 3): a linha do tempo e o import que roda no papel. Sintético."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

RAIZ = Path(__file__).resolve().parents[2]
_spec = spec_from_file_location("contar_modulo_sem_import_papel", RAIZ /
                                "analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_modulo_sem_import_papel.py")
cm = module_from_spec(_spec)
_spec.loader.exec_module(cm)

NAO_DEF = "Code execution failed at line 'd = json.loads(s)' due to: InterpreterError: The variable `json` is not defined."
OUTRO = "Code execution failed at line 'x = d[0]' due to: InterpreterError: Could not index"


def linha(ex, mes, msg, codigo="", nxt="", nxt_erro=""):
    return {"cod_idef_exeo": ex, "papel": "R", "mes_execucao": mes, "structured_error": 1, "error_type": "E",
            "error_message": msg, "error_code_action": codigo, "next_code_action": nxt, "next_error_type": nxt_erro,
            "next_error_message": ""}


class TestModuloSemImportPapel(unittest.TestCase):
    def test_importa(self):
        self.assertTrue(cm.importa("import json\nx = 1", "json"))
        self.assertTrue(cm.importa("from json import loads", "json"))
        self.assertFalse(cm.importa("d = json.loads(s)  # import json", "json"))

    def test_medir(self):
        L = [linha("e1", "2026-05", NAO_DEF, nxt="import json\nd = json.loads(s)"),
             linha("e2", "2026-05", NAO_DEF, nxt="d = 1"),
             linha("e3", "2026-04", OUTRO, codigo="import json\nd = json.loads(s)\nx = d[0]")]
        tempo, B = cm.medir(L, "R", "json")
        T = {t["mes"]: t for t in tempo}
        self.assertEqual((T["2026-05"]["execucoes_com_o_erro"], T["2026-05"]["erros"]), (2, 2))
        self.assertEqual(T["2026-04"]["execucoes_com_erro"], 1)
        self.assertEqual(B["depois: importa e o passo roda sem erro"], 1)
        self.assertEqual(B["depois: o passo seguinte não importa"], 1)
        self.assertEqual((B["import_rodou_antes_da_falha"], B["import_rodou · 2026-04"]), (1, 1))


if __name__ == "__main__":
    unittest.main()
