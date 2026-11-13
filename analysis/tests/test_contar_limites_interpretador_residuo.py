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


def falha(linha, erro):
    """A mensagem do interpretador com o tipo verdadeiro do erro (`due to: KeyError: ...`)."""
    return f"Code execution failed at line '{linha}' due to: {erro}"
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


class TestDepois(unittest.TestCase):
    def test_desfecho(self):
        d = M.desfecho
        self.assertEqual(d("NoneType", None, None, None), "sem_passo")
        self.assertEqual(d("NoneType", 4, "x = {**a}", msg("x = {**a}", NONE)), "mesmo_limite")
        self.assertEqual(d("NoneType", 4, "x = dict(a)\nx.update(b)", None), "trocou_ok")
        self.assertEqual(d("NoneType", 4, "x = dict(a)", falha("x = dict(a)", "KeyError: 'k'")), "trocou_outro_erro")
        self.assertEqual(d("NoneType", 4, "if c:\n    x = {**a}\nelse:\n    x = 1", None), "usa_ok")
        self.assertEqual(d("NamedExpr", 4, "y = (", "SyntaxError"), "nao_lido_outro_erro")
        self.assertEqual(d("unpack", 4, "for k, v in d.items():\n    pass", None), "nao_lido_ok")
        # global: a função definida antes e chamada de novo não traz a palavra, mas a mensagem é a mesma
        self.assertEqual(d("Global", 4, "soma(5)", msg("soma(5)", "Global is not supported.")), "mesmo_limite")
        self.assertEqual(d("Global", 4, "total = soma(total, 5)", None), "trocou_ok")

    def test_sinais_verificacao(self):
        s = M.sinais_verificacao
        instruida = ("def ensure_peticao():\n    global peticao\n    if peticao is None:\n"
                     "        peticao = buscar_peticao(id=1)\n    return peticao")
        r = s("p = ensure_peticao()", instruida)                   # o def no passo anterior, a chamada no que falhou
        self.assertEqual((r["onde_def_global"], r["uso_global"], r["nome_de_estado"]),
                         ("anterior", "verifica_e_guarda_chamada", True))
        r = s("total = 0\ndef soma(v):\n    global total\n    total += v\nsoma(5)", None)
        self.assertEqual((r["onde_def_global"], r["uso_global"], r["nome_de_estado"]), ("passo", "outro_uso", False))
        r = s("def f():\n    global x\n    x = g()\nf()", None)
        self.assertEqual(r["uso_global"], "so_guarda_chamada")
        r = s("y = 1", None)
        self.assertEqual((r["onde_def_global"], r["uso_global"]), ("nao_visto", "def_nao_visto"))
        self.assertEqual(s("y = (", None)["uso_global"], "codigo_nao_parseia")
        r = s("try:\n    x\nexcept NameError:\n    raise\nok = 'x' in globals()", None)
        self.assertTrue(r["raise_em_except_nameerror"] and r["except_nameerror"] and r["introspeccao"])
        self.assertFalse(s("try:\n    x\nexcept KeyError:\n    raise", None)["raise_em_except_nameerror"])

    def test_tipo_erro(self):
        self.assertEqual(M.tipo_erro(falha("x[0]", "KeyError: 'k'")), "KeyError")
        self.assertEqual(M.tipo_erro("TypeError: unsupported operand"), "TypeError")
        self.assertEqual(M.tipo_erro(None), "")
        self.assertEqual(M.tipo_erro("algo estranho"), "outro")

    def test_fonte_e_versoes(self):
        import pyarrow as pa
        import pyarrow.parquet as pq
        base = dict(agente="1", unidade="X_sintoma_nao_reconhecido", tok_tot=10)
        casos = [
            dict(base, exec_id="e1", role="P1", idx=2, mes="2026-07", mensagem=msg("x = {**a}", NONE)),
            dict(base, exec_id="e2", role="P1", idx=3, mes="2026-07", mensagem=msg("if (n := 1):\n    pass",
                                                                                  "NamedExpr is not supported.")),
            dict(base, exec_id="e9", role="P1", idx=1, mes="2026-07", mensagem=msg("global t", "Global is not supported.")),
        ]
        fonte = {
            "cod_idef_exeo": ["e1", "e2", "e0", "e0"], "cod_idef_aget": ["1", "1", "1", "1"],
            "papel": ["P1", "P1", "P1", "P2"], "step_pos": [2, 3, 1, 1],
            "cod_vers_aget": ["vB", "vB", "vA", None], "mes_execucao": ["2026-07", "2026-07", "2026-04", "2026-05"],
            "next_step_number": [3, 4, 2, None], "next_code_action": ["x = dict(a)", "n = 1\nif n:\n    pass", "y", None],
            "next_error_message": [None, falha("z", "KeyError: 'k'"), None, None],
            "next2_step_number": [4, None, None, None], "next2_code_action": ["print(x)", None, None, None],
            "next2_error_message": [None, None, None, None],
        }
        with tempfile.TemporaryDirectory() as tmp:
            pq.write_table(pa.table(fonte), Path(tmp) / "fonte.parquet")
            pd.DataFrame(casos).to_csv(Path(tmp) / "casos.csv", index=False)
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(M.main(["--casos", str(Path(tmp) / "casos.csv"),
                                         "--fonte", str(Path(tmp) / "fonte.parquet")]), 0)
            texto = out.getvalue()
            self.assertIn("1 erros sem linha na fonte", texto)          # o e9 não está na fonte
            self.assertIn("passo seguinte: {'trocou_ok': 1}", texto)    # o {**a} do e1
            self.assertIn("{'trocou_outro_erro': 1}", texto)            # o := do e2
            self.assertIn("o outro erro do passo seguinte: {'KeyError': 1}", texto)
            self.assertIn("P1: v1 2026-04→2026-04 (1 passos; 0 do grupo) · v2 2026-07→2026-07 (2 passos; 2 do grupo)",
                          texto)
            self.assertNotIn("vB", texto)                               # o código da versão não sai
            g = pd.read_csv(Path(tmp) / "casos_limites_interpretador.csv")
            self.assertEqual(g.depois_next.tolist(), ["trocou_ok", "trocou_outro_erro", "sem_passo"])
            self.assertEqual(g.versao.fillna("").tolist(), ["v2", "v2", ""])
            self.assertNotIn("versao_bruta", g.columns)


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
