"""Os dois testes da parte E do sandbox (funções e atributos proibidos): o uso da linha que falhou e o prompt. Sintético."""
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


b3 = carregar("contar_proibidas_linha", RAIZ / "analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_proibidas_linha.py")
b2 = carregar("contar_proibidas_prompt_base2", RAIZ / "analysis/2026-09-trace-law-flow-second/scripts/contar_proibidas_prompt_base2.py")


def msg(linha, fim):
    return f"Code execution failed at line '{linha}' due to: InterpreterError: {fim}"


DUNDER = "Forbidden access to dunder attribute: __name__"
EXCECAO_COD = "for s in secoes:\n    try:\n        r = gerar(s)\n    except Exception as e:\n        falhas.append(type(e).__name__)\n"


class TestUso(unittest.TestCase):
    def test_dunder(self):
        self.assertEqual(b3.uso_proibida("__name__", "falhas.append(type(e).__name__)", EXCECAO_COD), "nome do tipo da exceção")
        self.assertEqual(b3.uso_proibida("__name__", "print(type(x).__name__)"), "nome do tipo")
        self.assertEqual(b3.uso_proibida("__name__", "n = f.__name__"), "nome de função/objeto")
        self.assertEqual(b3.uso_proibida("__name__", "if __name__ == '__main__':"), "bloco __main__")

    def test_funcoes(self):
        self.assertEqual(b3.uso_proibida("repr", "print('x', repr(res)[:80])"), "depuração (print)")
        self.assertEqual(b3.uso_proibida("eval", "docs = eval(texto)"), "converter texto (eval)")
        self.assertEqual(b3.uso_proibida("exec", "exec(codigo)"), "código dinâmico")
        self.assertEqual(b3.uso_proibida("open", "f = open('a.txt')"), "abrir arquivo")
        self.assertEqual(b3.uso_proibida("globals", "if 'x' in globals():"), "introspecção · verificação de existência")
        self.assertEqual(b3.uso_proibida("represent", "y = represent(x)"), "outro uso")

    def test_funcao_auxiliar(self):
        cod = "def mostrar(v):\n    return repr(v)[:50]\n\nprint(mostrar(r))\n"
        self.assertEqual(b3.uso_proibida("repr", "print(mostrar(r))", cod), "função auxiliar")
        self.assertEqual(b3.uso_proibida("repr", "print(outra(r))", cod), "outro uso")

    def test_em_except(self):
        self.assertTrue(b3.em_except("falhas.append(type(e).__name__)", EXCECAO_COD))
        self.assertFalse(b3.em_except("r = gerar(s)", EXCECAO_COD))

    def test_mascarar(self):
        self.assertEqual(b3.mascarar("x = docs_260200198489['a']"), "x = docs_#['…']")

    def test_medir(self):
        base = {"structured_error": 1, "error_type": "InterpreterError"}
        linhas = [
            {**base, "papel": "ContestacaoCivel", "mes_execucao": "2026-08",
             "error_message": msg("falhas.append(type(e).__name__)", DUNDER), "error_code_action": EXCECAO_COD},
            {**base, "papel": "ContestacaoCivel", "mes_execucao": "2026-08",
             "error_message": msg("if 'x' not in globals():\n    x = ferramenta()", "Forbidden function evaluation: 'globals' is not among"),
             "error_code_action": "if 'x' not in globals():\n    x = ferramenta()"},           # verifica e cria: sai (Ajuste 21)
            {**base, "papel": "OBFCivel", "mes_execucao": "2026-07", "error_message": msg("print(repr(r))", "Forbidden function evaluation: 'repr' is not among"),
             "error_code_action": "print(repr(r))"},
            {**base, "papel": "OBFCivel", "mes_execucao": "2026-07", "error_message": msg("import ast", "Import of ast is not allowed."),
             "error_code_action": "import ast"},                                             # parte D, não E
        ]
        T = b3.medir(linhas)
        self.assertEqual(T["total"], 2)
        D = T["D"].set_index(["grupo", "nome"])
        self.assertEqual(int(D.loc[("ContestacaoCivel", "__name__"), "no_except"]), 1)
        self.assertEqual(set(T["B"].uso), {"nome do tipo da exceção", "depuração (print)"})


class TestPromptBase2(unittest.TestCase):
    def test_medir(self):
        p_cc = "Gere cada seção.\nSe falhar, registre em secoes_com_falha com type(e).__name__.\nOutra linha."
        p_out = "Responda ao usuário."
        S = pd.DataFrame([
            {"exec_id": "e1", "agente": "a", "role": "ContestacaoCivel", "idx": 0, "mes": "2026-08", "err_type": "InterpreterError",
             "err_msg": msg("falhas.append(type(e).__name__)", DUNDER), "code": EXCECAO_COD, "sysprompt": p_cc},
            {"exec_id": "e2", "agente": "a", "role": "ContestacaoCivel", "idx": 0, "mes": "2026-08", "err_type": None,
             "err_msg": "", "code": "", "sysprompt": p_cc},
            {"exec_id": "e3", "agente": "a", "role": "ConversationAgent", "idx": 0, "mes": "2026-08", "err_type": "InterpreterError",
             "err_msg": msg("print(repr(r))", "Forbidden function evaluation: 'repr' is not among"), "code": "print(repr(r))", "sysprompt": p_out},
        ])
        T = b2.medir(S)
        self.assertEqual(T["total"], 2)
        C = T["C"].set_index("role")
        self.assertEqual(int(C.loc["ContestacaoCivel", "execucoes"]), 2)
        self.assertEqual(int(C.loc["ContestacaoCivel", "com_erro_parte_e"]), 1)
        self.assertTrue(bool(C.loc["ContestacaoCivel", "menciona___name__"]))
        self.assertEqual(T["D"].iloc[0].execucoes, 2)
        E = T["E"].set_index(["grupo", "nome"])
        self.assertEqual(int(E.loc[("ContestacaoCivel", "__name__"), "nome_escrito_no_prompt"]), 1)
        self.assertEqual(int(E.loc[("outros", "repr"), "nome_escrito_no_prompt"]), 0)


if __name__ == "__main__":
    unittest.main()
