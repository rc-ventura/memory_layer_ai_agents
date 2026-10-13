"""Ajuste 17: a assinatura `try/except NameError` na linha que falhou decide antes da posição do passo anterior.

Fixtures sintéticas, nunca IDs ou conteúdo de clientes. As mensagens seguem o formato do interpretador do sandbox
("Code execution failed at line '...' due to: InterpreterError: The variable `x` is not defined.").
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_adaptador_trace import janela, set_slot
from test_integracao_carga_base3 import BP, RAW1
from test_mecanismos_episodios_base3 import rows_chain
from test_sintomas_base3 import state


def falha(linha, nome="x"):
    return f"Code execution failed at line '{linha}' due to: InterpreterError: The variable `{nome}` is not defined."


ASSINATURA = falha("try:\n    x\nexcept NameError:\n    x = ferramenta()")
TUPLA = falha("try:\n    x\nexcept (NameError, KeyError):\n    x = 1")
TRY_SEM_NAMEERROR = falha("try:\n    x\nexcept Exception:\n    pass")
COMUM = falha("print(x)")
MODULO = falha("try:\n    json\nexcept NameError:\n    import json", nome="json")


class TestMecanismo(unittest.TestCase):
    def test_as_duas_bases_classificam_igual(self):
        esperado = {ASSINATURA: "verificacao_try_nameerror", TUPLA: "verificacao_try_nameerror",
                    TRY_SEM_NAMEERROR: "nome_nao_definido", COMUM: "nome_nao_definido", MODULO: "modulo_sem_import"}
        for pipeline in (BP, RAW1):
            for msg, mec in esperado.items():
                self.assertEqual(pipeline.submecanismo(msg), mec, msg)

    def test_unidade_e_destino(self):
        for pipeline in (BP, RAW1):
            self.assertEqual(pipeline.SUB2UNI["verificacao_try_nameerror"], "U_verificacao_try_nameerror")
            self.assertIn("U_verificacao_try_nameerror", pipeline.UNI)
            self.assertEqual(pipeline.destino_mineracao("U_verificacao_try_nameerror", "base2"), "harness")
            self.assertEqual(pipeline.destino_mineracao("U_verificacao_try_nameerror", "base3"), "harness")
            self.assertEqual(pipeline.destino_mineracao("U_verificacao_try_nameerror", "base1"), "em aberto")


class TestObservado(unittest.TestCase):
    def analyze(self, *rows):
        return BP.analisar_mecanismos_observaveis(state(*rows))

    def test_primeiro_passo_com_assinatura_deixa_de_ser_pendente(self):
        r = self.analyze(janela(error_message=ASSINATURA)).EU.iloc[0]
        self.assertEqual(r.submecanismo, "verificacao_try_nameerror")
        self.assertEqual(r.situacao_mecanismo, "observavel")
        self.assertEqual(r.unidade, "U_verificacao_try_nameerror")

    def test_primeiro_passo_sem_assinatura_continua_pendente(self):
        self.assertTrue(self.analyze(janela(error_message=COMUM)).EU.unidade.isna().all())

    def test_assinatura_vence_a_posicao(self):
        # depois de um passo com erro: sem a assinatura seria estado perdido
        r = rows_chain()
        r[1]["error_message"] = ASSINATURA
        set_slot(r[0], "next", r[1])
        self.assertEqual(self.analyze(*r).EU.iloc[1].unidade, "U_verificacao_try_nameerror")
        r = rows_chain()
        r[1]["error_message"] = COMUM
        set_slot(r[0], "next", r[1])
        self.assertEqual(self.analyze(*r).EU.iloc[1].submecanismo, "nome_de_step_que_falhou")


if __name__ == "__main__":
    unittest.main()
