"""Os dois testes da hipótese da introspecção (dossiê do sandbox, parte A): a linha que falhou e a versão do prompt.
Sintético."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]


def carregar(nome, arq):
    sys.path.insert(0, str(arq.parent))
    spec = spec_from_file_location(nome, arq)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


b3 = carregar("contar_introspeccao_linha", RAIZ / "analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_introspeccao_linha.py")
b2 = carregar("contar_introspeccao_prompt_base2", RAIZ / "analysis/2026-09-trace-law-flow-second/scripts/contar_introspeccao_prompt_base2.py")

VERIF = "Code execution failed at line 'if 'peticao' in globals():' due to: InterpreterError: Forbidden function evaluation: 'globals' is not among the explicitly allowed tools"
OUTRO = "Code execution failed at line 'print(globals())' due to: InterpreterError: Forbidden function evaluation: 'globals' is not among"
TRY = "Code execution failed at line 'try:\n    peticao\nexcept NameError:\n    peticao = None' due to: InterpreterError: The variable `peticao` is not defined."


class TestLinha(unittest.TestCase):
    def test_classificar(self):
        self.assertEqual(b3.classificar(VERIF), ("introspecção", "globals", "verificação de existência"))
        self.assertEqual(b3.classificar(OUTRO), ("introspecção", "globals", "outro uso"))
        self.assertEqual(b3.classificar(TRY), ("try/except NameError", None, None))
        self.assertIsNone(b3.classificar("due to: InterpreterError: Forbidden function evaluation: 'repr' is not"))

    def test_usos(self):
        self.assertEqual(b3.uso_da_linha("if 'x' not in globals():"), "verificação de existência")
        self.assertEqual(b3.uso_da_linha("v = globals().get('x')"), "verificação de existência")
        self.assertEqual(b3.uso_da_linha("globals()['x'] = 1"), "atribuição dinâmica")
        self.assertEqual(b3.uso_da_linha("globals().update(d)"), "atribuição dinâmica")
        self.assertEqual(b3.uso_da_linha("y = globals()['x']"), "leitura por nome")
        self.assertEqual(b3.uso_da_linha("if globals()['x'] == 1:"), "leitura por nome")
        self.assertEqual(b3.uso_da_linha("print(dir(obj))"), "outro uso")

    def test_lado_a_lado(self):
        linhas = [{"papel": "P", "mes_execucao": m, "structured_error": 1, "error_type": "InterpreterError", "error_message": t}
                  for m, t in (("2026-07", VERIF), ("2026-07", VERIF), ("2026-08", TRY), ("2026-08", OUTRO))]
        B = b3.medir(linhas)["B"].set_index("mes")
        self.assertEqual(int(B.loc["2026-07", "introspecção · verificação de existência"]), 2)
        self.assertEqual(int(B.loc["2026-08", "try/except NameError"]), 1)


class TestPrompt(unittest.TestCase):
    def test_trecho_da_instrucao(self):
        julho = "texto\n- Antes de chamar qualquer tool, VERIFIQUE se a variável de saída correspondente já\nestá preenchida em memória. Se já estiver, PULE a chamada.\nfim"
        agosto = julho + "\nNão use globals() nem locals(); use try/except NameError."
        hj, tj = b2.trecho(julho)
        ha, ta = b2.trecho(agosto)
        self.assertTrue(tj["instrucao_verificar"]) and self.assertFalse(tj["NameError"])
        self.assertEqual((ta["NameError"], ta["globals()"]), (True, True))
        self.assertNotEqual(hj, ha)
        self.assertEqual(b2.trecho("nada aqui")[0], "(nenhuma)")

    def test_como_verificou(self):
        self.assertEqual(b2.como_verificou("if 'x' not in globals():\n    x = f()"), "introspecção (globals/locals/vars)")
        self.assertEqual(b2.como_verificou("try:\n    x\nexcept NameError:\n    x = f()"), "try/except NameError")
        self.assertEqual(b2.como_verificou("try:\n    x\nexcept Exception:\n    x = f()"), "try/except de outro tipo")
        self.assertEqual(b2.como_verificou("x = f()\nprint(x)"), "não verificou")

    def test_medir(self):
        S = pd.DataFrame([
            {"exec_id": "e1", "agente": 1, "role": "C", "idx": 0, "mes": "2026-07", "err_type": "InterpreterError", "err_msg": VERIF,
             "sysprompt": "VERIFIQUE se a variável x já está preenchida em memória", "code": "if 'x' in globals(): pass"},
            {"exec_id": "e2", "agente": 1, "role": "C", "idx": 0, "mes": "2026-07", "err_type": None, "err_msg": "",
             "sysprompt": "VERIFIQUE se a variável x já está preenchida em memória", "code": "x = f()"},
        ])
        C = b2.medir(S)["C"]
        self.assertEqual((int(C.execucoes.sum()), int(C.com_introspeccao.sum()), int(C.com_nenhum.sum())), (2, 1, 1))
        E = b2.medir(S)["E"].set_index("como_verificou")
        self.assertEqual(int(E.loc["não verificou", "execucoes"]), 1)


if __name__ == "__main__":
    unittest.main()
