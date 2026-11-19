"""Ajuste 37: a atribuição a um nome de ferramenta, que o interpretador barra ("Cannot assign to name '<nome>': doing
this would erase the existing tool"), sai do resíduo ("Sintoma não reconhecido") para `U_nome_ferramenta_como_variavel`
(submecanismo `nome_de_ferramenta_atribuido`), nos dois pipelines e na auditoria nº 6. Vale para ferramenta declarada
(`final_answer = {...}`, `x = x(...)`) e para função embutida do interpretador (`exp = ...`).

A regra é a última do `classify()` e do `submecanismo()`: só alcança o que nenhuma outra reconhece. Um erro que outra
regra já pega não muda; uma mensagem parecida, sem a proteção da ferramenta, continua no resíduo.

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


def protegido(linha, nome):
    return falhou(linha, f"InterpreterError: Cannot assign to name '{nome}': doing this would erase the existing tool!")


DICT = protegido("final_answer = {'campo': 1}", "final_answer")
PROPRIO = protegido("calculo_x = calculo_x(valor=v)", "calculo_x")
EMBUTIDA = protegido("exp = 2", "exp")
# parecida, sem a proteção da ferramenta: continua no resíduo
PARECIDA = falhou("x = 1", "InterpreterError: Cannot assign to name 'x': something else")
# outra regra pega antes: não pode mudar
TIMEOUT = falhou("r = enterprise_web_search(q=q)", "TimeoutError: a ferramenta excedeu o timeout de 600 s")

NOVOS = (DICT, PROPRIO, EMBUTIDA)


class TestAjuste37(unittest.TestCase):
    def test_submecanismo_nas_duas_bases(self):
        for pipeline in (BP, RAW1):
            for msg in NOVOS:
                self.assertEqual(pipeline.submecanismo(msg), "nome_de_ferramenta_atribuido", msg)
            self.assertEqual(pipeline.submecanismo(PARECIDA), "causa_sem_regra")
            self.assertNotEqual(pipeline.submecanismo(TIMEOUT), "nome_de_ferramenta_atribuido")

    def test_sintoma_nas_duas_bases(self):
        for pipeline in (BP, RAW1):
            for msg in NOVOS:
                self.assertEqual(pipeline.classify(msg), ("Ambiente & sandbox", "Nome de ferramenta usado como variável"))
            self.assertEqual(pipeline.classify(PARECIDA)[0], "Sintoma não reconhecido")
            self.assertEqual(pipeline.classify(TIMEOUT)[1], "Ferramenta excedeu o timeout")

    def test_unidade(self):
        for pipeline in (BP, RAW1):
            self.assertEqual(pipeline.SUB2UNI["nome_de_ferramenta_atribuido"], "U_nome_ferramenta_como_variavel")
            nome, tipo, texto = pipeline.UNI["U_nome_ferramenta_como_variavel"]
            self.assertEqual(tipo, pipeline.FACT)
            self.assertIn("Ajuste 37", texto)

    def test_observado_na_base3(self):
        def um(msg):
            return BP.analisar_mecanismos_observaveis(state(janela(error_message=msg, error_code_action=""))).EU.iloc[0]
        for msg in NOVOS:
            r = um(msg)
            self.assertEqual((r.unidade, r.situacao_mecanismo), ("U_nome_ferramenta_como_variavel", "observavel"), msg)
        self.assertEqual(um(PARECIDA).unidade, "X_sintoma_nao_reconhecido")

    def test_auditoria6_reescreve_a_regra(self):
        a = auditoria6()
        for msg in NOVOS:
            self.assertEqual(a["submecanismo_spec"](msg), "nome_de_ferramenta_atribuido", msg)
            self.assertEqual(a["classify_sig_local"](msg), "nome_ferramenta_variavel", msg)
        self.assertEqual(a["submecanismo_spec"](PARECIDA), "causa_sem_regra")
        self.assertEqual(a["classify_sig_local"](PARECIDA), "NC")
        self.assertEqual(a["SUB2UNI"]["nome_de_ferramenta_atribuido"], "U_nome_ferramenta_como_variavel")


if __name__ == "__main__":
    unittest.main()
