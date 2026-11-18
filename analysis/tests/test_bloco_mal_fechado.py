"""Ajuste 40: um erro de sintaxe com a tag do bloco (`<code>` ou `</code>`) escrita no código vai para `H_bloco_code`
(submecanismo `bloco_mal_fechado`, harness). O agente abriu um bloco sem fechar e abriu outro; o harness pega cada trecho de
um `<code>` até o `</code>` seguinte, e o trecho aberto leva ao interpretador a narração e a tag. A regra vem antes do texto em literal
e do texto solto (que pegavam a linha do meio do bloco colado) e depois do retorno colado. Fora do erro de sintaxe, a tag
não decide nada. Fixtures sintéticas.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_adaptador_trace import janela  # noqa: E402
from test_conexao_llm_aninhada import auditoria6, falhou  # noqa: E402
from test_integracao_carga_base3 import BP, RAW1  # noqa: E402
from test_sintomas_base3 import state  # noqa: E402
from test_texto_numa_conta import trace_row  # noqa: E402


def parsing_antigo(linha, motivo="invalid syntax"):
    """O formato antigo (base 1): a mensagem traz a linha rejeitada."""
    return f"Code parsing failed on line 1 due to: SyntaxError\n{linha}\n ^\nError: {motivo}"


PROSA = "Agora vou somar os valores da causa"                    # texto solto, sem a tag
SOLTO = parsing_antigo(PROSA)
LITERAL = parsing_antigo("relatorio = '''Parte 1", "unterminated triple-quoted string literal")
MAL_ESCRITO = parsing_antigo("x = = 1")
TRUNCADO = parsing_antigo("{'a': 'b', ... (truncado)")
COLADO = f"{PROSA}\n</code>\n<code>\ntotal = 1 + 2\n"           # o bloco mal fechado: prosa e a tag do segundo bloco
NOVO = "Code parsing failed on line 1 due to: SyntaxError: invalid syntax"   # formato novo (base 3): sem a linha


class TestRegra(unittest.TestCase):
    def test_a_tag_no_codigo_vai_para_o_harness(self):
        for pipeline in (BP, RAW1):
            for msg in (SOLTO, LITERAL, MAL_ESCRITO):
                self.assertEqual(pipeline.submecanismo(msg, tag_do_bloco=True), "bloco_mal_fechado", msg)
            self.assertEqual(pipeline.SUB2UNI["bloco_mal_fechado"], "H_bloco_code")

    def test_sem_a_tag_nada_muda(self):
        for pipeline in (BP, RAW1):
            self.assertEqual(pipeline.submecanismo(SOLTO), "texto_solto_no_codigo")
            self.assertEqual(pipeline.submecanismo(LITERAL), "texto_em_literal")
            self.assertEqual(pipeline.submecanismo(MAL_ESCRITO), "codigo_mal_escrito")

    def test_o_retorno_colado_vem_antes(self):
        for pipeline in (BP, RAW1):
            self.assertEqual(pipeline.submecanismo(TRUNCADO, tag_do_bloco=True), "repr_colado")

    def test_o_sinal_so_existe_no_erro_de_sintaxe(self):
        for pipeline in (BP, RAW1):
            f = pipeline.bloco_mal_fechado
            self.assertTrue(f(SOLTO, COLADO))
            self.assertTrue(f(NOVO, "x = 1\n<code>\ny = 2"))
            self.assertTrue(f("IndentationError: unexpected indent", "</code>"))
            self.assertFalse(f(SOLTO, "total = 1 + 2"))
            self.assertFalse(f(SOLTO, None))
            # outro erro com a tag no código: a tag não decide
            self.assertFalse(f(falhou("x = y", "InterpreterError: The variable `y` is not defined."), COLADO))


class TestPontaAPontaBase1(unittest.TestCase):
    def unidade(self, passos):
        steps, _, _ = RAW1.explodir_memoria(trace_row(passos))
        return RAW1.montar_unidades(RAW1.classificar_erros(steps)).unidade.tolist()

    def test_com_e_sem_a_tag(self):
        self.assertEqual(self.unidade([(COLADO, SOLTO)]), ["H_bloco_code"])
        self.assertEqual(self.unidade([(f"{PROSA}\ntotal = 1 + 2\n", SOLTO)]), ["U_texto_solto"])


class TestBase3(unittest.TestCase):
    def um(self, codigo):
        return BP.analisar_mecanismos_observaveis(
            state(janela(error_message=NOVO, error_code_action=codigo))).EU.iloc[0]

    def test_com_e_sem_a_tag(self):
        r = self.um(COLADO)
        self.assertEqual((r.submecanismo, r.unidade, r.situacao_mecanismo),
                         ("bloco_mal_fechado", "H_bloco_code", "observavel"))
        self.assertEqual(self.um("x = = 1\n</code>").unidade, "H_bloco_code")
        r = self.um(f"{PROSA}\ntotal = 1 + 2\n")
        self.assertEqual((r.submecanismo, r.unidade), ("texto_solto_no_codigo", "U_texto_solto"))


class TestAuditoria6(unittest.TestCase):
    def test_reescreve_a_regra(self):
        a = auditoria6()
        self.assertEqual(a["submecanismo_spec"](SOLTO, code=COLADO), "bloco_mal_fechado")
        self.assertEqual(a["submecanismo_spec"](MAL_ESCRITO, code="x = = 1\n<code>"), "bloco_mal_fechado")
        self.assertEqual(a["submecanismo_spec"](SOLTO, code=f"{PROSA}\n"), "texto_solto_no_codigo")
        self.assertEqual(a["submecanismo_spec"](TRUNCADO, code=COLADO), "repr_colado")
        self.assertEqual(a["SUB2UNI"]["bloco_mal_fechado"], "H_bloco_code")


if __name__ == "__main__":
    unittest.main()
