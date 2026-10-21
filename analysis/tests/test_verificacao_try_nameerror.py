"""Ajuste 17: a assinatura `try/except NameError` na linha que falhou decide antes da posição do passo anterior.
Ajuste 21: a unidade passa a `U_verificacao_existencia`, que recebe também a introspecção que verifica e cria a variável.

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
            self.assertEqual(pipeline.SUB2UNI["verificacao_try_nameerror"], "U_verificacao_existencia")
            self.assertNotIn("U_verificacao_try_nameerror", pipeline.UNI)
            self.assertIn("U_verificacao_existencia", pipeline.UNI)
            for base in ("base1", "base2", "base3"):
                self.assertEqual(pipeline.destino_mineracao("U_verificacao_existencia", base), "harness")


class TestObservado(unittest.TestCase):
    def analyze(self, *rows):
        return BP.analisar_mecanismos_observaveis(state(*rows))

    def test_primeiro_passo_com_assinatura_deixa_de_ser_pendente(self):
        r = self.analyze(janela(error_message=ASSINATURA)).EU.iloc[0]
        self.assertEqual(r.submecanismo, "verificacao_try_nameerror")
        self.assertEqual(r.situacao_mecanismo, "observavel")
        self.assertEqual(r.unidade, "U_verificacao_existencia")

    def test_primeiro_passo_sem_assinatura_continua_pendente(self):
        self.assertTrue(self.analyze(janela(error_message=COMUM)).EU.unidade.isna().all())

    def test_assinatura_vence_a_posicao(self):
        # depois de um passo com erro: sem a assinatura seria estado perdido
        r = rows_chain()
        r[1]["error_message"] = ASSINATURA
        set_slot(r[0], "next", r[1])
        self.assertEqual(self.analyze(*r).EU.iloc[1].unidade, "U_verificacao_existencia")
        r = rows_chain()
        r[1]["error_message"] = COMUM
        set_slot(r[0], "next", r[1])
        self.assertEqual(self.analyze(*r).EU.iloc[1].submecanismo, "nome_de_step_que_falhou")


def proibida(linha, funcao="globals"):
    return (f"Code execution failed at line '{linha}' due to: InterpreterError: Forbidden function evaluation: "
            f"'{funcao}' is not among the explicitly allowed tools or defined/imported in the preceding code")


DIRETA = proibida("if 'peticao' not in globals():")
AUXILIAR = proibida("if not has_var('peticao'): peticao = get_peticao(numero=n)")
LEITURA_PADRAO = proibida("ctx = globals().get('ctx', 'padrao')")
OUTRO = proibida("print(dir(obj))", "dir")
CODIGO_CRIA = "if 'peticao' not in globals():\n    peticao = get_peticao(numero=n)\n"
CODIGO_PADRAO = "if 'peticao' not in globals():\n    peticao = 'padrao'\n"


class TestAjuste21(unittest.TestCase):
    def test_regra_nas_duas_bases(self):
        for pipeline in (BP, RAW1):
            v = pipeline.verificacao_por_introspeccao
            self.assertTrue(v(DIRETA, CODIGO_CRIA))         # verifica e cria por uma chamada: instruída
            self.assertTrue(v(AUXILIAR))                     # a função auxiliar, com a criação na própria linha
            self.assertFalse(v(DIRETA, CODIGO_PADRAO))       # cria com um literal: espontânea
            self.assertFalse(v(LEITURA_PADRAO, LEITURA_PADRAO))
            self.assertFalse(v(OUTRO))
            self.assertEqual(pipeline.submecanismo(DIRETA, verifica_e_cria=True), "verificacao_introspeccao")
            self.assertEqual(pipeline.submecanismo(DIRETA), "inventario_sandbox")
            self.assertEqual(pipeline.submecanismo(OUTRO, verifica_e_cria=True), "inventario_sandbox")
            self.assertEqual(pipeline.SUB2UNI["verificacao_introspeccao"], "U_verificacao_existencia")

    def test_observado(self):
        def um(msg, code):
            return BP.analisar_mecanismos_observaveis(state(janela(error_message=msg, error_code_action=code))).EU.iloc[0]
        r = um(DIRETA, CODIGO_CRIA)
        self.assertEqual((r.submecanismo, r.unidade), ("verificacao_introspeccao", "U_verificacao_existencia"))
        self.assertEqual(um(AUXILIAR, "").unidade, "U_verificacao_existencia")
        self.assertEqual(um(DIRETA, CODIGO_PADRAO).unidade, "U_sandbox")
        self.assertEqual(um(LEITURA_PADRAO, LEITURA_PADRAO).unidade, "U_sandbox")


EVAL_AUX = proibida("if not _exists('peticao'): peticao = get_peticao(numero=n)", "eval")
EVAL_TEXTO = proibida("docs = eval(texto)", "eval")


class TestAjuste23(unittest.TestCase):
    def test_eval_por_funcao_auxiliar(self):
        for pipeline in (BP, RAW1):
            v = pipeline.verificacao_por_introspeccao
            self.assertTrue(v(EVAL_AUX))                     # verifica e cria por uma chamada: instruída
            self.assertFalse(v(EVAL_TEXTO, "docs = eval(texto)"))   # converte texto: fica no sandbox
            self.assertEqual(pipeline.submecanismo(EVAL_AUX, verifica_e_cria=True), "verificacao_introspeccao")
            self.assertEqual(pipeline.submecanismo(EVAL_TEXTO, verifica_e_cria=False), "inventario_sandbox")

    def test_observado(self):
        def um(msg, code):
            return BP.analisar_mecanismos_observaveis(state(janela(error_message=msg, error_code_action=code))).EU.iloc[0]
        self.assertEqual(um(EVAL_AUX, "").unidade, "U_verificacao_existencia")
        self.assertEqual(um(EVAL_TEXTO, "docs = eval(texto)").unidade, "U_sandbox")


def proibida(linha, funcao="globals"):
    return (f"Code execution failed at line '{linha}' due to: InterpreterError: Forbidden function evaluation: "
            f"'{funcao}' is not among the explicitly allowed tools or defined/imported in the preceding code")


PAPEL = "ontestacaoCivel"   # o ContestacaoCivel, como chega ao trace
VALOR_FIXO = proibida("if 'id_processo' not in globals(): id_processo = 'x'")
LEITURA = proibida("u = globals().get('u', 'p')")
SEM_NOME = proibida("missing = [v for v in obrigatorias if v not in globals()]")
LOCALS = proibida("if 'a' not in locals():", "locals")
SO_DIR = proibida("print(dir(obj))", "dir")
NAO_VERIFICA = proibida("print(globals())")


class TestAjuste27(unittest.TestCase):
    def test_pelo_papel(self):
        for pipeline in (BP, RAW1):
            v = pipeline.verificacao_no_papel_da_instrucao
            for msg in (VALOR_FIXO, LEITURA, SEM_NOME, LOCALS):
                self.assertTrue(v(msg, PAPEL), msg)              # as quatro formas, no papel da instrução
                self.assertFalse(v(msg, "CalculoTrabalhista"))  # nos outros papéis, não
            self.assertFalse(v(SO_DIR, PAPEL))                   # dir não verifica existência
            self.assertFalse(v(NAO_VERIFICA, PAPEL))             # globals() sem verificar
            self.assertEqual(pipeline.submecanismo(VALOR_FIXO, verifica_e_cria=v(VALOR_FIXO, PAPEL)),
                             "verificacao_introspeccao")
            self.assertEqual(pipeline.submecanismo(VALOR_FIXO, verifica_e_cria=v(VALOR_FIXO, "Outro")),
                             "inventario_sandbox")

    def test_observado(self):
        def um(msg, papel):
            return BP.analisar_mecanismos_observaveis(state(janela(error_message=msg, error_code_action="",
                                                                   papel=papel))).EU.iloc[0]
        self.assertEqual(um(VALOR_FIXO, PAPEL).unidade, "U_verificacao_existencia")
        self.assertEqual(um(SEM_NOME, PAPEL).unidade, "U_verificacao_existencia")
        # fora do papel, sem o código do passo, a regra (b) não decide: pendente (o papel decide sem o código)
        fora = um(VALOR_FIXO, "CalculoTrabalhista")
        self.assertEqual(fora.situacao_mecanismo, "pendente")
        self.assertEqual(um(VALOR_FIXO, PAPEL).situacao_mecanismo, "observavel")

    def test_auditoria(self):
        from test_mineracao_candidata_base3 import aud
        self.assertFalse(aud.populacao_sandbox(VALOR_FIXO, "", PAPEL))
        self.assertFalse(aud.populacao_sandbox(SEM_NOME, "", PAPEL))
        self.assertTrue(aud.populacao_sandbox(VALOR_FIXO, "", "CalculoTrabalhista"))
        self.assertTrue(aud.populacao_sandbox(SO_DIR, "", PAPEL))
        self.assertEqual(set(BP.PAPEIS_COM_INSTRUCAO_DE_VERIFICAR), aud.PAPEIS_QUE_VERIFICAM)
        self.assertEqual(set(RAW1.PAPEIS_COM_INSTRUCAO_DE_VERIFICAR), aud.PAPEIS_QUE_VERIFICAM)


if __name__ == "__main__":
    unittest.main()
