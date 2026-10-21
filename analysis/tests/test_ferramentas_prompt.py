"""O teste da parte B do sandbox: a ferramenta que o prompt manda usar está declarada (os `def`)? Sintético."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
ARQ = RAIZ / "analysis/2026-09-trace-law-flow-second/scripts/contar_ferramentas_prompt_base2.py"
sys.path.insert(0, str(ARQ.parent))
spec = spec_from_file_location("contar_ferramentas_prompt_base2", ARQ)
m = module_from_spec(spec)
spec.loader.exec_module(m)

SEM = "def get_docs(pasta: string) -> object:\n    pass\nIf you need the raw text, use `get_document_text`.\nYou can use imports in your code, but only from the following list of modules: ['json']"
COM = SEM + "\ndef get_document_text(h: string) -> string:\n    pass\n"


class TestFerramentasPrompt(unittest.TestCase):
    def test_ferramentas_e_importado(self):
        self.assertEqual(m.ferramentas(SEM)[0], ["get_docs"])
        self.assertIn("get_document_text", m.ferramentas(COM)[0])
        self.assertEqual(m.importado("x due to: InterpreterError: Import of get_document_text is not allowed."), "get_document_text")
        self.assertEqual(m.importado("x due to: ModuleNotFoundError: No module named 'tools'"), "tools")
        self.assertIsNone(m.importado("x due to: InterpreterError: Import of ast is not allowed."))   # parte D

    def test_medir(self):
        imp = "Code execution failed at line 'import get_document_text' due to: InterpreterError: Import of get_document_text is not allowed."
        S = pd.DataFrame([
            {"exec_id": "e1", "agente": 1, "role": "OBFCivel", "idx": 0, "mes": "2026-07", "err_type": "InterpreterError", "err_msg": imp, "sysprompt": SEM},
            {"exec_id": "e2", "agente": 1, "role": "OBFCivel", "idx": 0, "mes": "2026-08", "err_type": "InterpreterError", "err_msg": imp, "sysprompt": COM},
        ])
        T = m.medir(S)
        A = T["A"].set_index("versao")
        self.assertEqual(len(A), 2)
        self.assertEqual(sorted(A.declara_get_document_text.tolist()), [False, True])
        self.assertTrue(A.menciona_get_document_text.all())
        B = T["B"].set_index("declarada_na_versao").erros.to_dict()
        self.assertEqual(B, {False: 1, True: 1})
        self.assertEqual(int(T["C"].com_lista_de_imports.iloc[0]), 2)


if __name__ == "__main__":
    unittest.main()
