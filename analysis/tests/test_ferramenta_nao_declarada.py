"""Ajuste 26: o import de uma ferramenta que o prompt cita e não declara (`get_document_text`) sai do inventário do
sandbox para `U_ferramenta_nao_declarada` (sinal de harness), nos dois pipelines e na auditoria do sandbox (emenda 7 do
racional). Os nomes do framework (`python_interpreter`, `tools`…) e os imports fora da lista ficam no sandbox.

Fixtures sintéticas, nunca IDs ou conteúdo de clientes. As mensagens seguem o formato do interpretador do sandbox
("Code execution failed at line '...' due to: InterpreterError: Import of x is not allowed. Authorized imports are: [...]").
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_adaptador_trace import janela
from test_integracao_carga_base3 import BP, RAW1
from test_mineracao_candidata_base3 import aud
from test_sintomas_base3 import state


def barrado(linha, nome):
    return (f"Code execution failed at line '{linha}' due to: InterpreterError: Import of {nome} is not allowed. "
            "Authorized imports are: ['json', 're']")


DE = barrado("import get_document_text", "get_document_text")
FROM = barrado("from get_document_text import get_document_text", "get_document_text").replace("Import of", "Import from")
SEM_MODULO = "Code execution failed at line 'import get_document_text.x' due to: ModuleNotFoundError: No module named 'get_document_text'"
FRAMEWORK = barrado("import python_interpreter", "python_interpreter")
OUTRO_GET = barrado("import get_docs", "get_docs")
FORA_DA_LISTA = barrado("import ast", "ast")
# o nome aparece na linha de código, mas o import barrado é outro: decide o último trecho da mensagem
SO_NA_LINHA = barrado("import ast  # depois get_document_text", "ast")


class TestAjuste26(unittest.TestCase):
    def test_as_duas_bases_classificam_igual(self):
        esperado = {DE: "ferramenta_nao_declarada", FROM: "ferramenta_nao_declarada",
                    SEM_MODULO: "ferramenta_nao_declarada", FRAMEWORK: "inventario_sandbox",
                    OUTRO_GET: "inventario_sandbox", FORA_DA_LISTA: "inventario_sandbox",
                    SO_NA_LINHA: "inventario_sandbox"}
        for pipeline in (BP, RAW1):
            for msg, sub in esperado.items():
                self.assertEqual(pipeline.submecanismo(msg), sub, msg)

    def test_unidade_e_destino(self):
        for pipeline in (BP, RAW1):
            self.assertEqual(pipeline.SUB2UNI["ferramenta_nao_declarada"], "U_ferramenta_nao_declarada")
            self.assertIn("U_ferramenta_nao_declarada", pipeline.UNI)
            for base in ("base1", "base2", "base3"):
                self.assertEqual(pipeline.destino_mineracao("U_ferramenta_nao_declarada", base), "harness")

    def test_observado(self):
        def um(msg):
            return BP.analisar_mecanismos_observaveis(state(janela(error_message=msg, error_code_action=""))).EU.iloc[0]
        self.assertEqual(um(DE).unidade, "U_ferramenta_nao_declarada")
        self.assertEqual(um(FRAMEWORK).unidade, "U_sandbox")

    def test_auditoria_tira_da_populacao(self):
        self.assertFalse(aud.populacao_sandbox(DE))
        self.assertFalse(aud.populacao_sandbox(SEM_MODULO))
        self.assertTrue(aud.populacao_sandbox(FRAMEWORK))
        self.assertTrue(aud.populacao_sandbox(SO_NA_LINHA))

    def test_auditoria_e_pipeline_dizem_o_mesmo(self):
        # a auditoria reescreve a regra da prosa (emenda 7), sem importar o pipeline: as duas listas são a mesma
        self.assertEqual(set(BP.FERRAMENTAS_NAO_DECLARADAS), aud.NAO_DECLARADAS)
        self.assertEqual(set(RAW1.FERRAMENTAS_NAO_DECLARADAS), aud.NAO_DECLARADAS)


if __name__ == "__main__":
    unittest.main()
