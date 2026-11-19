"""Ajuste 39: um texto entrou numa conta, num round ou num formato de número ("unsupported operand type(s) for +: 'int'
and 'str'", "type str doesn't define __round__ method", "Unknown format code 'f' for object of type 'str'"…) sai do
resíduo ("causa não identificada"):
  - para `H_contrato_ferramenta` (submecanismo `tipo_de_retorno_descumprido`, harness) quando a variável da linha que
    falhou foi atribuída pela chamada de uma ferramenta que o system prompt declara devolver número (assinatura ou
    `Returns:`) — a ferramenta entregou texto onde prometeu número;
  - para `U_tipo_retorno` (submecanismo `tipo_real_do_retorno`, memória) em todo o resto: o contrato diz texto, não diz
    nada, ou o valor não veio de ferramenta.
Sem o prompt (base 3), o contrato vem de `CONTRATOS_DE_RETORNO_CONHECIDOS` (lido no prompt da base 2: as duas ferramentas
de correção monetária declaram `Returns: float`); o stub no prompt, quando existe, vale mais que a lista.

A regra é a última do `submecanismo()`: só alcança o que nenhuma outra reconhece. Só operadores de conta com um número do
outro lado: o `'function' | 'str'` (o único caso da base 1) fica no resíduo. Fixtures sintéticas.
"""
import json
from pathlib import Path
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_adaptador_trace import janela  # noqa: E402
from test_conexao_llm_aninhada import auditoria6, falhou  # noqa: E402
from test_integracao_carga_base3 import BP, RAW1  # noqa: E402
from test_sintomas_base3 import state  # noqa: E402

SOMA = falhou("total = valor + 100", "TypeError: unsupported operand type(s) for +: 'str' and 'int'")
SOMA_INVERSA = falhou("total = 100 + valor", "TypeError: unsupported operand type(s) for +: 'int' and 'str'")
SOMA_IN_PLACE = falhou("total += valor", "TypeError: unsupported operand type(s) for +=: 'float' and 'str'")
CONCAT = falhou("t = valor + 1", 'TypeError: can only concatenate str (not "int") to str')
ROUND = falhou("r = round(valor, 2)", "TypeError: type str doesn't define __round__ method")
FORMATO = falhou("s = f'{valor:.2f}'", "ValueError: Unknown format code 'f' for object of type 'str'")
MATH = falhou("r = math.floor(valor)", "TypeError: must be real number, not str")
NOVOS = (SOMA, SOMA_INVERSA, SOMA_IN_PLACE, CONCAT, ROUND, FORMATO, MATH)
# ficam no resíduo: não é conta com número
PIPE = falhou("t = f | 'x'", "TypeError: unsupported operand type(s) for |: 'function' and 'str'")
NONE = falhou("t = a + b", "TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'")
LISTA = falhou("t = a + b", "TypeError: unsupported operand type(s) for +: 'list' and 'str'")
# outra regra pega antes: não muda
JA_TIPO = falhou("x = float(v)", "ValueError: could not convert string to float: 'R$ 1,00'")


def stub(nome, assinatura, returns):
    linha = f"        Returns:\n            {returns}: o resultado\n" if returns else ""
    return (f"def {nome}(x: string) -> {assinatura}:\n    \"\"\"\n        Ferramenta de exemplo.\n\n        Args:\n"
            f"            x (str): entrada\n{linha}    \"\"\"\n")


SYSP = ("You are an expert assistant.\n"
        + stub("calcular_numero", "object", "float")
        + stub("calcular_texto", "object", "str")
        + stub("calcular_sem_retorno", "object", None)
        + stub("calcular_assinatura", "number", None))


class TestRegra(unittest.TestCase):
    def test_mensagens_de_texto_numa_conta_vao_para_a_memoria(self):
        for pipeline in (BP, RAW1):
            for msg in NOVOS:
                self.assertEqual(pipeline.submecanismo(msg), "tipo_real_do_retorno", msg)
                self.assertEqual(pipeline.SUB2UNI[pipeline.submecanismo(msg)], "U_tipo_retorno")

    def test_o_que_nao_e_conta_com_numero_fica_no_residuo(self):
        for pipeline in (BP, RAW1):
            for msg in (PIPE, NONE, LISTA):
                self.assertEqual(pipeline.submecanismo(msg), "causa_sem_regra", msg)

    def test_a_regra_antiga_do_tipo_de_retorno_nao_muda(self):
        for pipeline in (BP, RAW1):
            self.assertEqual(pipeline.submecanismo(JA_TIPO), "tipo_real_do_retorno")
            self.assertEqual(pipeline.submecanismo(JA_TIPO, retorno_numero=True), "tipo_real_do_retorno")

    def test_contrato_descumprido_vai_para_harness(self):
        for pipeline in (BP, RAW1):
            self.assertEqual(pipeline.submecanismo(SOMA, retorno_numero=True), "tipo_de_retorno_descumprido")
            self.assertEqual(pipeline.SUB2UNI["tipo_de_retorno_descumprido"], "H_contrato_ferramenta")
            self.assertEqual(pipeline.submecanismo(PIPE, retorno_numero=True), "causa_sem_regra")


class TestContratoNoPrompt(unittest.TestCase):
    def test_tipo_de_retorno_declarado(self):
        for pipeline in (BP, RAW1):
            self.assertEqual(pipeline.tipo_de_retorno_declarado("calcular_numero", SYSP), ("object", "float"))
            self.assertEqual(pipeline.tipo_de_retorno_declarado("calcular_texto", SYSP), ("object", "str"))
            self.assertEqual(pipeline.tipo_de_retorno_declarado("calcular_sem_retorno", SYSP), ("object", None))
            self.assertEqual(pipeline.tipo_de_retorno_declarado("calcular_assinatura", SYSP), ("number", None))
            self.assertIsNone(pipeline.tipo_de_retorno_declarado("nao_existe", SYSP))

    def test_retorno_numero_declarado(self):
        for pipeline in (BP, RAW1):
            f = pipeline.retorno_numero_declarado
            # a variável veio de uma ferramenta que promete número (no Returns, ou na assinatura): harness
            self.assertTrue(f(SOMA, ["valor = calcular_numero(x)", "total = valor + 100"], SYSP))
            self.assertTrue(f(ROUND, ["valor = calcular_assinatura(x)"], SYSP))
            # a ferramenta promete texto, não diz nada, ou o valor não veio de ferramenta: memória
            self.assertFalse(f(SOMA, ["valor = calcular_texto(x)"], SYSP))
            self.assertFalse(f(SOMA, ["valor = calcular_sem_retorno(x)"], SYSP))
            self.assertFalse(f(SOMA, ["valor = '1500,00'"], SYSP))
            self.assertFalse(f(SOMA, ["outra = calcular_numero(x)"], SYSP))   # não é a variável da linha
            self.assertFalse(f(SOMA, ["if valor == calcular_numero(x): pass"], SYSP))   # comparação, não atribuição
            # sem o prompt (base 3): só o contrato registrado; e sem texto numa conta, nunca harness
            self.assertFalse(f(SOMA, ["valor = calcular_numero(x)"], ""))
            self.assertTrue(f(SOMA, ["valor = calcular_correcao_monetaria(x)"], ""))
            self.assertTrue(f(ROUND, ["valor = indice_correcao_monetaria(x)"], ""))
            self.assertFalse(f(JA_TIPO, ["v = calcular_numero(x)"], SYSP))
            # o stub no prompt vale mais que o registro
            sysp_str = SYSP + stub("calcular_correcao_monetaria", "object", "str")
            self.assertFalse(f(SOMA, ["valor = calcular_correcao_monetaria(x)"], sysp_str))


def trace_row(passos):
    """Uma execução da base 1 com um papel: `passos` = [(código, mensagem de erro ou None)]; o system prompt é SYSP."""
    acts = [{"__class__": "ActionStep", "step_number": i + 1, "code_action": c,
             "error": {"type": "AgentExecutionError", "message": e} if e else None, "is_final_answer": False,
             "model_input_messages": [{"role": "system", "content": [{"type": "text", "text": SYSP}]}],
             "token_usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}, "timing": {"duration": 0.1}}
            for i, (c, e) in enumerate(passos)]
    return pd.DataFrame([dict(cod_idef_exeo="fixture-exec", cod_idef_aget="1", cod_idef_stat_exeo_aget="3",
                              mes="2026-08", mes_particao="202608", txt_etap_memo=json.dumps({"CalculoX": acts}))])


class TestPontaAPontaBase1(unittest.TestCase):
    def unidade(self, passos):
        steps, _, _ = RAW1.explodir_memoria(trace_row(passos))
        return RAW1.montar_unidades(RAW1.classificar_erros(steps)).unidade.tolist()

    def test_a_ferramenta_atribuida_num_passo_anterior(self):
        self.assertEqual(self.unidade([("valor = calcular_numero(x)\nprint(valor)", None),
                                       ("total = valor + 100", SOMA)]), ["H_contrato_ferramenta"])
        self.assertEqual(self.unidade([("valor = calcular_texto(x)\nprint(valor)", None),
                                       ("total = valor + 100", SOMA)]), ["U_tipo_retorno"])

    def test_no_mesmo_passo(self):
        self.assertEqual(self.unidade([("valor = calcular_numero(x)\ntotal = valor + 100", SOMA)]),
                         ["H_contrato_ferramenta"])


class TestBase3SemPrompt(unittest.TestCase):
    def um(self, msg, codigo, anterior=None):
        extra = dict(prev_step_number="1", prev_code_action=anterior, prev_error_like="0", step_number="2") if anterior else {}
        return BP.analisar_mecanismos_observaveis(
            state(janela(error_message=msg, error_code_action=codigo, **extra))).EU.iloc[0]

    def test_ferramenta_sem_contrato_registrado_vai_para_a_memoria(self):
        for msg in NOVOS:
            r = self.um(msg, "valor = calcular_numero(x)\ntotal = valor + 100")
            self.assertEqual((r.unidade, r.situacao_mecanismo), ("U_tipo_retorno", "observavel"), msg)
        self.assertEqual(self.um(PIPE, "").unidade, "X_causa_nao_identificada")

    def test_contrato_registrado_vai_para_harness(self):
        r = self.um(SOMA, "valor = calcular_correcao_monetaria(x)\ntotal = valor + 100")
        self.assertEqual((r.unidade, r.situacao_mecanismo), ("H_contrato_ferramenta", "observavel"))
        # a atribuição no passo anterior
        r = self.um(SOMA, "total = valor + 100", anterior="valor = indice_correcao_monetaria(x)\nprint(valor)")
        self.assertEqual(r.unidade, "H_contrato_ferramenta")
        # o valor não veio da ferramenta registrada
        self.assertEqual(self.um(SOMA, "valor = '1500,00'\ntotal = valor + 100").unidade, "U_tipo_retorno")


class TestAuditoria6(unittest.TestCase):
    def test_reescreve_as_duas_saidas(self):
        a = auditoria6()
        for msg in NOVOS:
            self.assertEqual(a["submecanismo_spec"](msg), "tipo_real_do_retorno", msg)
        for msg in (PIPE, NONE, LISTA):
            self.assertEqual(a["submecanismo_spec"](msg), "causa_sem_regra", msg)
        self.assertEqual(a["submecanismo_spec"](SOMA, sysp=SYSP, codigos=["valor = calcular_numero(x)"]),
                         "tipo_de_retorno_descumprido")
        self.assertEqual(a["submecanismo_spec"](SOMA, sysp=SYSP, codigos=["valor = calcular_texto(x)"]),
                         "tipo_real_do_retorno")
        self.assertEqual(a["submecanismo_spec"](SOMA, codigos=["valor = calcular_correcao_monetaria(x)"]),
                         "tipo_de_retorno_descumprido")
        self.assertEqual(a["SUB2UNI"]["tipo_de_retorno_descumprido"], "H_contrato_ferramenta")


if __name__ == "__main__":
    unittest.main()
