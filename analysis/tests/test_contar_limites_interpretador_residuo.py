"""O contador do grupo "limites do interpretador" do resíduo da base 3 (`validacao/
contar_limites_interpretador_residuo.py`): o limite, a forma da linha, os construtos e a repetição. Fixtures
sintéticas."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

ARQ = (Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third" / "pipeline" / "validacao"
       / "contar_limites_interpretador_residuo.py")
spec = importlib.util.spec_from_file_location("contar_limites_interpretador_residuo", ARQ)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def msg(linha, erro):
    return f"Code execution failed at line '{linha}' due to: InterpreterError: {erro}"


NONE = "NoneType is not supported."
DICT_MULTILINHA = ("regs = [\n    {\n        'a': d['a'],\n        **{m['k']: m['v'] for m in d['m']}\n    }\n"
                   "    for d in docs\n]")


class TestClassificar(unittest.TestCase):
    def test_formas(self):
        casos = {
            ("NoneType", "dict_com_estrela"): msg(DICT_MULTILINHA, NONE),
            ("NoneType", "kwonly_sem_padrao"): msg("def f(*, a):\n    return a", NONE),
            ("NoneType", "outra"): msg("x = 1", NONE),
            ("NoneType", "nao_parseia_com_estrela"): msg("y = {**a, 'b': (", NONE),
            ("NoneType", "nao_parseia"): msg("y = (", NONE),
            ("NoneType", "sem_linha"): "InterpreterError: NoneType is not supported.",
            ("NamedExpr", "em_if"): msg("if (m := f(x)):\n    print(m)", "NamedExpr is not supported."),
            ("NamedExpr", "em_while"): msg("while (c := ler()):\n    pass", "NamedExpr is not supported."),
            ("NamedExpr", "em_compreensao"): msg("ys = [y for x in xs if (y := f(x))]",
                                                 "NamedExpr is not supported."),
            ("Global", "so_a_declaracao"): msg("global total", "Global is not supported."),
            ("Global", "em_funcao"): msg("def g():\n    global total\n    total += 1", "Global is not supported."),
            ("Nonlocal", "em_funcao"): msg("def g():\n    def h():\n        nonlocal n\n    h()",
                                           "Nonlocal is not supported."),
            ("unpack", "atribuicao"): msg("a, b = f()", "Cannot unpack non-tuple value"),
            ("unpack", "laco"): msg("for k, v in d:\n    pass", "Cannot unpack non-tuple value"),
            ("Re-raise", "raise_sozinho"): msg("raise", "Re-raise is not supported without an active exception"),
        }
        for (lim, forma), m in casos.items():
            self.assertEqual(M.classificar(m)[:2], (lim, forma), m)
        self.assertEqual(M.classificar("KeyError: 'x'"), (None, None, []))

    def test_construtos(self):
        _, _, cs = M.classificar(msg(DICT_MULTILINHA, NONE))
        self.assertEqual(cs, ["dict_com_estrela", "compreensao"])
        _, _, cs = M.classificar(msg("r = {**a} if (n := len(a)) else f'{n}'", NONE))
        self.assertEqual(cs, ["dict_com_estrela", "walrus", "fstring"])
        # chamada com ** não é dicionário com estrela
        self.assertEqual(M.classificar(msg("f(**kw)", NONE))[1:], ("outra", []))

    def test_estrela_no_texto(self):
        rx = M.ESTRELA_NO_DICT
        for sim in ("{**a", "{ 'a': 1, **b", DICT_MULTILINHA):
            self.assertTrue(rx.search(sim), sim)
        # a potência num exemplo do framework e o **kw de uma chamada dentro do dicionário não contam
        for nao in ('{"code": "idade = 88 ** 0.36"', "{'a': f(x, **kw)}"):
            self.assertFalse(rx.search(nao), nao)


class TestContar(unittest.TestCase):
    def test_grupo_repeticao_e_saida(self):
        base = dict(agente="A", unidade="X_sintoma_nao_reconhecido", tok_tot=10)
        linhas = [
            dict(base, exec_id="e1", role="P1", idx=1, mes="2026-05", mensagem=msg("x = {**a}", NONE)),
            dict(base, exec_id="e1", role="P1", idx=2, mes="2026-05", mensagem=msg("x = {**b}", NONE)),
            dict(base, exec_id="e2", role="P2", idx=1, mes="2026-06", mensagem=msg("global t", "Global is not supported.")),
            dict(base, exec_id="e3", role="P2", idx=1, mes="2026-06", mensagem="KeyError: 'x'"),
        ]
        G = M.contar(pd.DataFrame(linhas))
        self.assertEqual(G.limite.value_counts().to_dict(), {"NoneType": 2, "Global": 1})
        r = M.repeticao(G)
        self.assertEqual((r["execuções-papel-limite"], r["2+ vezes"], r["máximo de vezes"]), (2, 1, 2))
        with tempfile.TemporaryDirectory() as tmp:
            casos = Path(tmp) / "casos.csv"
            pd.DataFrame(linhas).to_csv(casos, index=False)
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(M.main(["--casos", str(casos)]), 0)
            self.assertIn("limites do interpretador: 3 erros · 2 execuções · 2 meses", out.getvalue())
            self.assertIn("'dict_com_estrela': 2", out.getvalue())
            self.assertNotIn("{**a}", out.getvalue())   # nada de código na saída
            gravado = pd.read_csv(Path(tmp) / "casos_limites_interpretador.csv")
            self.assertNotIn("mensagem", gravado.columns)
            self.assertEqual(len(gravado), 3)


class TestPrompt(unittest.TestCase):
    def test_cita_e_exemplo(self):
        def memo(texto):
            return json.dumps({"P1": [{"__class__": "ActionStep",
                                       "model_input_messages": [{"content": [{"text": texto}]}]}]})
        avisa = "Rules:\n1. Don't use the walrus operator.\n```py\nd = {**a, 'b': 1}\n```"
        neutro = "Rules:\n1. Use a visão global do caso.\n<code>x = 1</code>"
        por = M.medir_prompt([memo(avisa), memo(neutro), "não é json"])
        c = por["P1"]
        self.assertEqual(c["execuções"], 2)
        self.assertEqual(c["cita walrus (:= ou a palavra)"], 1)
        self.assertEqual(c["cita global x"], 0)      # "global" em português não conta
        self.assertEqual(c["exemplo usa dict_com_estrela"], 1)
        self.assertEqual(c["exemplo usa walrus"], 0)


if __name__ == "__main__":
    unittest.main()
