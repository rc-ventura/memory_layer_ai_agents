"""Ajuste 38: Python válido que o interpretador não implementa (`{**x}` num dicionário, `:=`, `global`, `nonlocal`,
`raise` sozinho; "InterpreterError: <Nó> is not supported." e "Re-raise is not supported without an active exception")
sai do resíduo ("Sintoma não reconhecido") para o inventário do sandbox (`U_sandbox`, submecanismo
`sintaxe_nao_suportada`), nos dois pipelines e na auditoria nº 6.

A regra é a última do `classify()` e do `submecanismo()`: só alcança o que nenhuma outra reconhece. Ficam no resíduo o
"Cannot unpack non-tuple value" (falha também no Python normal) e um "is not supported" de biblioteca (sem o prefixo do
interpretador). O Ajuste 37 não muda, e o que o inventário já pegava (função barrada) continua igual.

Fixtures sintéticas, nunca IDs ou conteúdo de clientes.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_adaptador_trace import janela  # noqa: E402
from test_conexao_llm_aninhada import auditoria6, falhou  # noqa: E402
from test_integracao_carga_base3 import BP, RAW1  # noqa: E402
from test_sintomas_base3 import state  # noqa: E402

DICT = falhou("d = {**a, 'k': 1}", "InterpreterError: NoneType is not supported.")
WALRUS = falhou("if (n := len(xs)) > 1:\n    r = n", "InterpreterError: NamedExpr is not supported.")
GLOBAL = falhou("soma(5)", "InterpreterError: Global is not supported.")
NONLOCAL = falhou("r = conta()", "InterpreterError: Nonlocal is not supported.")
# a linha que falhou é a chamada da função que tem o `raise` (como no caso da base 3); uma linha com `except KeyError`
# cairia antes na regra do KeyError, que olha a mensagem inteira
RERAISE = falhou("repassa()", "InterpreterError: Re-raise is not supported without an active exception")
NOVOS = (DICT, WALRUS, GLOBAL, NONLOCAL, RERAISE)
# ficam no resíduo
UNPACK = falhou("for k, v in d:\n    pass", "InterpreterError: Cannot unpack non-tuple value")
BIBLIOTECA = falhou("df.loc[x] = 1", "ValueError: Setting with a non-unique index is not supported.")
# outras regras pegam antes: não podem mudar
FERRAMENTA = falhou("final_answer = {'a': 1}",
                    "InterpreterError: Cannot assign to name 'final_answer': doing this would erase the existing tool!")
BARRADA = falhou("r = 'x' in globals()", "InterpreterError: Forbidden function evaluation: 'globals' is not among the "
                                         "explicitly allowed tools or defined/imported in the preceding code")


class TestAjuste38(unittest.TestCase):
    def test_submecanismo_nas_duas_bases(self):
        for pipeline in (BP, RAW1):
            for msg in NOVOS:
                self.assertEqual(pipeline.submecanismo(msg), "sintaxe_nao_suportada", msg)
            for msg in (UNPACK, BIBLIOTECA):
                self.assertEqual(pipeline.submecanismo(msg), "causa_sem_regra", msg)
            self.assertEqual(pipeline.submecanismo(FERRAMENTA), "nome_de_ferramenta_atribuido")
            self.assertNotEqual(pipeline.submecanismo(BARRADA), "sintaxe_nao_suportada")

    def test_sintoma_nas_duas_bases(self):
        for pipeline in (BP, RAW1):
            for msg in NOVOS:
                self.assertEqual(pipeline.classify(msg),
                                 ("Ambiente & sandbox", "Sintaxe que o interpretador não implementa"), msg)
            self.assertEqual(pipeline.classify(UNPACK)[0], "Sintoma não reconhecido")
            self.assertNotEqual(pipeline.classify(BIBLIOTECA)[1], "Sintaxe que o interpretador não implementa")
            self.assertEqual(pipeline.classify(FERRAMENTA)[1], "Nome de ferramenta usado como variável")
            self.assertNotEqual(pipeline.classify(BARRADA)[1], "Sintaxe que o interpretador não implementa")

    def test_unidade_e_memoria(self):
        for pipeline in (BP, RAW1):
            self.assertEqual(pipeline.SUB2UNI["sintaxe_nao_suportada"], "U_sandbox")
            nome, tipo, texto = pipeline.UNI["U_sandbox"]
            self.assertEqual((nome, tipo), ("Inventário do sandbox", pipeline.FACT))
            for trecho in ("repr/eval/globals/dir", "d = dict(a)", "nunca dict(a, **b)", "raise e"):
                self.assertIn(trecho, texto)

    def test_observado_na_base3(self):
        def um(msg):
            return BP.analisar_mecanismos_observaveis(state(janela(error_message=msg, error_code_action=""))).EU.iloc[0]
        for msg in NOVOS:
            r = um(msg)
            self.assertEqual((r.unidade, r.situacao_mecanismo), ("U_sandbox", "observavel"), msg)
        self.assertEqual(um(UNPACK).unidade, "X_sintoma_nao_reconhecido")

    def test_auditoria6_reescreve_a_regra(self):
        a = auditoria6()
        for msg in NOVOS:
            self.assertEqual(a["submecanismo_spec"](msg), "sintaxe_nao_suportada", msg)
            self.assertEqual(a["classify_sig_local"](msg), "sintaxe_nao_suportada", msg)
        self.assertEqual(a["submecanismo_spec"](UNPACK), "causa_sem_regra")
        self.assertEqual(a["classify_sig_local"](UNPACK), "NC")
        self.assertEqual(a["SUB2UNI"]["sintaxe_nao_suportada"], "U_sandbox")


if __name__ == "__main__":
    unittest.main()
