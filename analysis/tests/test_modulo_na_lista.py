"""contar_modulo_na_lista_base2.py: o módulo na lista autorizada do prompt, por papel e versão. Sintético."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

RAIZ = Path(__file__).resolve().parents[2]
_spec = spec_from_file_location("contar_modulo_na_lista_base2",
                                RAIZ / "analysis/2026-09-trace-law-flow-second/scripts/contar_modulo_na_lista_base2.py")
cm = module_from_spec(_spec)
_spec.loader.exec_module(cm)


def frase(*mods):
    return "You can use imports in your code, but only from the following list of modules: [" + \
           ", ".join(f"'{m}'" for m in mods) + "]"


class TestModuloNaLista(unittest.TestCase):
    def test_modulos(self):
        self.assertEqual(cm.modulos(frase("json", "re")), {"json", "re"})
        self.assertEqual(cm.modulos(frase()), set())
        self.assertIsNone(cm.modulos("prompt sem a frase"))

    def test_contar(self):
        linhas = [{"role": "A", "versao": "v1", "execucoes": 4, "meses": ["2026-05"], "prompt": frase("json", "re")},
                  {"role": "A", "versao": "v2", "execucoes": 7, "meses": ["2026-07", "2026-08"], "prompt": frase("re")},
                  {"role": "B", "versao": "v3", "execucoes": 2, "meses": ["2026-06"], "prompt": "sem a frase"}]
        T = {r["papel"]: r for r in cm.contar(linhas, "json")}
        self.assertEqual((T["A"]["versoes_com"], T["A"]["versoes_sem"], T["A"]["execucoes_sem"]), (1, 1, 7))
        self.assertEqual(T["A"]["meses_sem"], ["2026-07", "2026-08"])
        self.assertEqual((T["B"]["versoes_sem_lista"], T["B"]["versoes_sem"]), (1, 0))


_spec2 = spec_from_file_location("contar_modulo_sem_import_base2",
                                 RAIZ / "analysis/2026-09-trace-law-flow-second/scripts/contar_modulo_sem_import_base2.py")
ms = module_from_spec(_spec2)
_spec2.loader.exec_module(ms)


class TestModuloSemImport(unittest.TestCase):
    def test_medir(self):
        import pandas as pd
        nao_def = "x due to: InterpreterError: The variable `json` is not defined."
        S = pd.DataFrame([  # (exec, papel, idx, prompt, erro)
            ("e1", "A", 0, frase("json", "re"), ""), ("e1", "A", 1, "", nao_def),
            ("e2", "A", 0, frase("re"), nao_def), ("e2", "A", 1, "", nao_def),
            ("e3", "A", 0, frase("re"), ""),
            ("e4", "B", 0, "sem a frase", ""),
        ], columns=["exec_id", "role", "idx", "sysprompt", "err_msg"]).assign(agente=1)
        T = ms.medir(S, "json")
        self.assertEqual(T["A"]["na lista"], {"execucoes": 1, "com_erro": 1, "erros": 1})
        self.assertEqual(T["A"]["fora da lista"], {"execucoes": 2, "com_erro": 1, "erros": 2})
        self.assertEqual(T["B"]["sem a frase"]["execucoes"], 1)
        self.assertEqual(T["(total)"]["fora da lista"]["erros"], 2)
        self.assertEqual(list(T)[-1], "(total)")


if __name__ == "__main__":
    unittest.main()
