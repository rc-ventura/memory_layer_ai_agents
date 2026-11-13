"""Ajuste 36: a ferramenta que sai do próprio contrato de retorno ou de erro sai do resíduo ("Sintoma não reconhecido")
para `H_contrato_ferramenta`, por três submecanismos, nos dois pipelines e na auditoria nº 6:
  - `retorno_fora_do_contrato`: "Invalid structured content returned by tool <nome>" (devolveu `None` onde o esquema
    dela exige objeto);
  - `erro_interno_ferramenta`: `RecoverableToolError` com um Traceback dentro (o erro interno vazou);
  - `ausencia_como_excecao`: `RecoverableToolError` dizendo que nenhum dado foi encontrado (a ausência virou exceção).

As regras são as últimas do `classify()` e do `submecanismo()`: só alcançam o que nenhuma outra reconhece. Um erro que
outra regra já pega não muda; um `RecoverableToolError` com outra mensagem continua no resíduo.

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

FORA = falhou("r = enterprise_web_search(q=q)",
              "RuntimeError: Invalid structured content returned by tool enterprise_web_search: None is not of type "
              "'object'")
TRACE = falhou("d = get_infos_pasta(p=p)",
               "RecoverableToolError: Ocorreu um erro ao buscar as informações da pasta. Detalhes do erro: Traceback "
               "(most recent call last):\n  File \"x.py\", line 1, in f\nRuntimeError: falhou")
AUSENTE = falhou("d = get_docs(p=p)",
                 "RecoverableToolError: Nenhum documento do tipo inicial encontrado para o processo 123")
# Traceback e ausência juntos: conta como erro interno
AMBOS = falhou("d = get_docs(p=p)",
               "RecoverableToolError: Nenhum documento encontrado. Detalhes do erro: Traceback (most recent call last)")
# outro RecoverableToolError: nenhuma das três causas — continua no resíduo
OUTRO = falhou("d = get_docs(p=p)", "RecoverableToolError: Serviço em manutenção")
# outra regra pega antes: não pode mudar
TIMEOUT = falhou("r = enterprise_web_search(q=q)", "TimeoutError: a ferramenta excedeu o timeout de 600 s")

ESPERADO = {FORA: "retorno_fora_do_contrato", TRACE: "erro_interno_ferramenta", AUSENTE: "ausencia_como_excecao",
            AMBOS: "erro_interno_ferramenta", OUTRO: "causa_sem_regra"}


class TestAjuste36(unittest.TestCase):
    def test_submecanismo_nas_duas_bases(self):
        for pipeline in (BP, RAW1):
            for msg, sub in ESPERADO.items():
                self.assertEqual(pipeline.submecanismo(msg), sub, msg)
            self.assertNotIn(pipeline.submecanismo(TIMEOUT), set(ESPERADO.values()))

    def test_sintoma_nas_duas_bases(self):
        for pipeline in (BP, RAW1):
            self.assertEqual(pipeline.classify(FORA),
                             ("Infra / ferramenta", "Ferramenta devolveu conteúdo fora do próprio esquema"))
            self.assertEqual(pipeline.classify(TRACE),
                             ("Infra / ferramenta", "Erro interno da ferramenta vazou como Traceback"))
            self.assertEqual(pipeline.classify(AUSENTE),
                             ("Infra / ferramenta", "Ausência de dado sinalizada como exceção"))
            self.assertEqual(pipeline.classify(TIMEOUT)[1], "Ferramenta excedeu o timeout")
            self.assertEqual(pipeline.classify(OUTRO)[0], "Sintoma não reconhecido")

    def test_unidade(self):
        for pipeline in (BP, RAW1):
            for sub in ("retorno_fora_do_contrato", "erro_interno_ferramenta", "ausencia_como_excecao"):
                self.assertEqual(pipeline.SUB2UNI[sub], "H_contrato_ferramenta")
            nome, tipo, texto = pipeline.UNI["H_contrato_ferramenta"]
            self.assertEqual(tipo, pipeline.NAO)
            self.assertIn("Ajuste 36", texto)

    def test_observado_na_base3(self):
        def um(msg):
            return BP.analisar_mecanismos_observaveis(state(janela(error_message=msg, error_code_action=""))).EU.iloc[0]
        for msg in (FORA, TRACE, AUSENTE):
            r = um(msg)
            self.assertEqual((r.unidade, r.situacao_mecanismo), ("H_contrato_ferramenta", "observavel"), msg)
        self.assertEqual(um(OUTRO).unidade, "X_sintoma_nao_reconhecido")

    def test_auditoria6_reescreve_a_regra(self):
        a = auditoria6()
        for msg, sub in ESPERADO.items():
            self.assertEqual(a["submecanismo_spec"](msg), sub, msg)
        self.assertEqual(a["classify_sig_local"](FORA), "ferramenta_fora_esquema")
        self.assertEqual(a["classify_sig_local"](TRACE), "ferramenta_traceback")
        self.assertEqual(a["classify_sig_local"](AUSENTE), "ferramenta_ausencia")
        self.assertEqual(a["classify_sig_local"](OUTRO), "NC")
        self.assertEqual(a["SUB2UNI"]["ausencia_como_excecao"], "H_contrato_ferramenta")


if __name__ == "__main__":
    unittest.main()
