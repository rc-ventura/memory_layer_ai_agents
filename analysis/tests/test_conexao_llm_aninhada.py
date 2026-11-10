"""Ajuste 35: a conexão perdida numa chamada a outro agente/LLM feita de dentro do código (`APIConnectionError`,
`APIStatusError`; na base 3, a linha que falhou chama `orquestrador_*`) sai do resíduo ("Sintoma não reconhecido") para
`H_infra_llm`, pelo submecanismo `conexao_llm_aninhada`, nos dois pipelines e na auditoria nº 6.

A regra é a última do `classify()` e do `submecanismo()`: só alcança o que nenhuma outra regra reconhece. Um erro que
outra regra já pega (o `APITimeoutError` no timeout, o `AgentGenerationError` na infra_llm, o "Could not index") não muda.

Fixtures sintéticas, nunca IDs ou conteúdo de clientes.
"""
import ast
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_adaptador_trace import janela  # noqa: E402
from test_integracao_carga_base3 import BP, RAW1  # noqa: E402
from test_sintomas_base3 import state  # noqa: E402

AUD6 = Path(__file__).resolve().parents[1] / "2026-09-trace-law-flow" / "audit" / "scripts" / "audit_recompute6.py"


def auditoria6():
    """As regras da auditoria nº 6 sem rodar o script (ele lê o trace e os CSVs ao ser importado): só as funções, as
    constantes e os imports da biblioteca padrão."""
    arvore = ast.parse(AUD6.read_text(encoding="utf-8"))
    nomes = {"MODS", "PT_STOP", "SUB2UNI"}
    corpo = [n for n in arvore.body
             if isinstance(n, ast.FunctionDef)
             or (isinstance(n, ast.Import))
             or (isinstance(n, ast.Assign) and any(getattr(t, "id", None) in nomes for t in n.targets))]
    ns = {}
    exec(compile(ast.Module(body=corpo, type_ignores=[]), str(AUD6), "exec"), ns)
    return ns


def falhou(linha, erro):
    return f"Code execution failed at line '{linha}' due to: {erro}"


CONEXAO = falhou("r = orquestrador_eletronico(tarefa=t)", "APIConnectionError: Connection error.")
CONEXAO_URL = falhou("r = orquestrador_papel(tarefa=t)",
                     "APIConnectionError: Connection error. For troubleshooting, consult: https://exemplo.invalid/x")
STATUS = falhou("r = orquestrador_papel(tarefa=t)", "APIStatusError: <html><body>502 Bad Gateway</body></html>")
# outras regras pegam antes: não podem mudar
TIMEOUT_API = falhou("r = orquestrador_papel(tarefa=t)", "APITimeoutError: Request timed out.")
GERACAO = "AgentGenerationError: Error in generating model output: APIConnectionError: Connection error."
INDEXA = falhou("x = r['campo']", "InterpreterError: Could not index {'a': 1} with 'campo': KeyError: 'campo' "
                "(depois de um APIConnectionError)")
# o nome tem de estar inteiro (borda de palavra)
PREFIXADO = falhou("r = f()", "RuntimeError: MyAPIConnectionErrorX happened")


class TestAjuste35(unittest.TestCase):
    def test_submecanismo_nas_duas_bases(self):
        esperado = {CONEXAO: "conexao_llm_aninhada", CONEXAO_URL: "conexao_llm_aninhada",
                    STATUS: "conexao_llm_aninhada", TIMEOUT_API: "timeout_ferramenta", GERACAO: "infra_llm",
                    INDEXA: "campo_inexistente_no_retorno", PREFIXADO: "causa_sem_regra"}
        for pipeline in (BP, RAW1):
            for msg, sub in esperado.items():
                self.assertEqual(pipeline.submecanismo(msg), sub, msg)

    def test_sintoma_nas_duas_bases(self):
        for pipeline in (BP, RAW1):
            for msg in (CONEXAO, CONEXAO_URL, STATUS):
                self.assertEqual(pipeline.classify(msg),
                                 ("Infra / LLM upstream", "Conexão perdida na chamada aninhada ao LLM"), msg)
            self.assertEqual(pipeline.classify(TIMEOUT_API)[1], "Ferramenta excedeu o timeout")
            self.assertEqual(pipeline.classify(PREFIXADO)[0], "Sintoma não reconhecido")

    def test_unidade(self):
        for pipeline in (BP, RAW1):
            self.assertEqual(pipeline.SUB2UNI["conexao_llm_aninhada"], "H_infra_llm")
            self.assertIn("APIConnectionError", pipeline.UNI["H_infra_llm"][2])

    def test_observado_na_base3(self):
        def um(msg):
            return BP.analisar_mecanismos_observaveis(state(janela(error_message=msg, error_code_action=""))).EU.iloc[0]
        for msg in (CONEXAO, STATUS):
            r = um(msg)
            self.assertEqual((r.unidade, r.situacao_mecanismo), ("H_infra_llm", "observavel"), msg)
        self.assertEqual(um(PREFIXADO).unidade, "X_sintoma_nao_reconhecido")

    def test_auditoria6_reescreve_a_regra(self):
        a = auditoria6()
        for msg in (CONEXAO, CONEXAO_URL, STATUS):
            self.assertEqual(a["submecanismo_spec"](msg), "conexao_llm_aninhada", msg)
            self.assertEqual(a["classify_sig_local"](msg), "conexao_llm", msg)
        self.assertEqual(a["submecanismo_spec"](PREFIXADO), "causa_sem_regra")
        self.assertEqual(a["classify_sig_local"](TIMEOUT_API), "timeout")
        self.assertEqual(a["SUB2UNI"]["conexao_llm_aninhada"], "H_infra_llm")


if __name__ == "__main__":
    unittest.main()
