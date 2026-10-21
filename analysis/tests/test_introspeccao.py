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

    def test_regra_b(self):
        vi = b3.verificacao_instruida
        # os formatos da base 3 (foto IMG_5898) e da base 1
        self.assertEqual(vi("if not has_var('peticao_json'): peticao_json = get_peticao_inicial(numero_pasta=p)", ""), "instruída")
        self.assertEqual(vi("peticao_json_str = ensure('peticao_json_str', lambda: get_peticao_inicial(numero_pasta=p))", ""), "instruída")
        self.assertEqual(vi("if 'peticao' not in globals():", "if 'peticao' not in globals():\n    peticao = get_doc(x)"), "instruída")
        self.assertEqual(vi("user_context = globals().get('user_context', 'padrão')", "user_context = globals().get('user_context', 'padrão')"), "espontânea")
        self.assertEqual(vi("if 'x' not in globals():", "if 'x' not in globals():\n    x = 'padrão'"), "espontânea")
        self.assertIsNone(vi("globals_dict = globals()", ""))
        self.assertIsNone(vi("print(dir(obj))", ""))

    def test_forma_espontanea(self):
        fe = b3.forma_espontanea
        # as formas da base 3 (fotos IMG_5922–IMG_5923, mascaradas) e da base 1
        self.assertEqual(fe("if 'id_processo' not in globals(): id_processo = 'x'", ""), "cria com valor fixo")
        self.assertEqual(fe("if 'id_processo' not in globals() or not id_processo: id_processo = 'x'", ""), "cria com valor fixo")
        self.assertEqual(fe("if 'a' not in locals():", "if 'a' not in locals():\n    a = None"), "cria com valor fixo")
        self.assertEqual(fe("user_context = globals().get('user_context', 'p')", ""), "leitura com valor padrão")
        self.assertEqual(fe("missing = [v for v in required_vars if v not in globals()]", ""), "sem nome entre aspas")
        self.assertEqual(fe("if 'x' in globals():", "if 'x' in globals():\n    print(x)"), "verifica e não cria")
        # argumento nomeado não é criar a variável
        self.assertEqual(fe("if 'p' in globals():", "if 'p' in globals():\n    r = f(p=p)"), "verifica e não cria")
        # nem numa chamada de várias linhas (a forma da base 1, ConversationAgent)
        self.assertEqual(fe("u = globals().get('u', 'p')", "u = globals().get('u', 'p')\nr = f(\n    u=u,\n)"),
                         "leitura com valor padrão")
        # a instruída (regra b) não entra; o que não verifica também não
        self.assertIsNone(fe("if 'p' not in globals():", "if 'p' not in globals():\n    p = get_doc(n)"))
        self.assertIsNone(fe("print(globals())", ""))

    def test_parte_e(self):
        def erro(linha):
            return (f"Code execution failed at line '{linha}' due to: InterpreterError: Forbidden function evaluation: "
                    "'globals' is not among the explicitly allowed tools")
        linhas = [{"papel": p, "mes_execucao": "2026-07", "structured_error": 1, "error_type": "InterpreterError",
                   "error_message": erro(l), "error_code_action": ""}
                  for p, l in (("P", "if 'x' not in globals(): x = 'a'"), ("P", "if 'y' not in globals(): y = 1"),
                               ("Q", "u = globals().get('u', 'p')"), ("Q", "print(globals())"))]
        E = b3.medir(linhas)["E"].set_index("papel")
        self.assertEqual(int(E.loc["P", "cria com valor fixo"]), 2)
        self.assertEqual(int(E.loc["Q", "leitura com valor padrão"]), 1)
        self.assertEqual(int(E.loc["Q", "total"]), 1)   # o print(globals()) não é verificação

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
        F = b2.medir(S)["F"].set_index("role")
        self.assertEqual((int(F.loc["C", "prompt_com_instrucao"]), int(F.loc["C", "verificaram_no_primeiro_passo"])), (2, 1))
        E = b2.medir(S)["E"].set_index("como_verificou")
        self.assertEqual(int(E.loc["não verificou", "execucoes"]), 1)


if __name__ == "__main__":
    unittest.main()
