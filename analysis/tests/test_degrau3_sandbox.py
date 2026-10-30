"""degrau3_sandbox.py (base 3): as regras contadas do degrau 3 e os casos mascarados (dossiê do sandbox §2h, 30).
Sintético. O mascaramento é o que decide o que sai da máquina da base: os testes cobrem os buracos já vistos."""
import csv
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import tempfile
import unittest

import pyarrow as pa
import pyarrow.parquet as pq

RAIZ = Path(__file__).resolve().parents[2]
VAL = RAIZ / "analysis/2026-10-trace-law-flow-third/pipeline/validacao"
sys.path.insert(0, str(VAL))
spec = spec_from_file_location("degrau3_sandbox", VAL / "degrau3_sandbox.py")
d3 = module_from_spec(spec)
spec.loader.exec_module(d3)


def falha(linha, motivo):
    return f"Code execution failed at line '{linha}' due to: InterpreterError: {motivo}"


class TestMascarar(unittest.TestCase):
    def test_aspas_comentario_numero(self):
        t = d3.mascarar('x = obter("João da Silva", 12345)  # cliente Maria\ny = f"valor {x}"')
        self.assertNotIn("João", t)
        self.assertNotIn("Maria", t)
        self.assertNotIn("12345", t)
        self.assertIn('obter("<texto>", <n>)', t)

    def test_aspas_triplas_fechadas_e_abertas(self):
        fechada = d3.mascarar('r = f"""\n| Item | Valor |\n**EJ2025** documento\n"""\nprint(r)')
        self.assertNotIn("EJ2025", fechada)
        self.assertIn("print(r)", fechada)
        aberta = d3.mascarar('r = f"""\n| Item | Valor |\n**EJ2025** documento')   # o trecho termina dentro do texto
        self.assertNotIn("EJ2025", aberta)
        self.assertNotIn("Item", aberta)

    def test_linha_de_texto_corrido_e_omitida(self):
        linhas = d3.linhas_seguras("a = 1\n| Nome | Valor |\nesta e uma frase longa de texto que vazou aqui")
        self.assertEqual(linhas[0], "a = <n>")
        self.assertTrue(all(l.startswith("<linha omitida") for l in linhas[1:]))

    def test_assinatura_guarda_o_nome_da_funcao_barrada(self):
        msg = falha("print(repr(x))", "Forbidden function evaluation: 'repr' is not among the allowed")
        self.assertIn("evaluation: repr is", d3.assinatura(msg))
        self.assertEqual(d3.assinatura(""), "(sem erro)")
        self.assertNotIn("Cliente", d3.assinatura("due to: KeyError: 'Cliente Fulano'"))


class TestRegras(unittest.TestCase):
    def test_instrucao_de_varias_linhas(self):
        msg = falha('r = f"""\nRelatório {datetime.now()}\n"""', "The variable `datetime` is not defined.")
        self.assertIn("datetime.now", d3.instrucao_que_falhou(msg))
        self.assertEqual(d3.linha_que_falhou(msg), 'r = f"""')

    def test_outros_nomes_sem_import(self):
        """A linha do JoogleAnalytics usa `pd` e `json`: o `json` sem import conta; importado no passo anterior ou antes
        da linha que falhou, não; o nome da própria memória não entra."""
        linha_ja = "df = pd.DataFrame(json.loads(run_query(query=q)))"
        msg = falha(linha_ja, "The variable `pd` is not defined.")
        sem = {"error_message": msg, "error_code_action": f"q = 'x'\n{linha_ja}", "prev_code_action": "q = 1"}
        self.assertEqual(d3.outros_nomes(sem, "pd"), ["json · sem import antes da falha"])
        anterior = {**sem, "prev_code_action": "import json\nq = 1"}
        self.assertEqual(d3.outros_nomes(anterior, "pd"), ["json · importado antes"])
        no_passo = {**sem, "error_code_action": f"import json\n{linha_ja}"}
        self.assertEqual(d3.outros_nomes(no_passo, "pd"), ["json · importado antes"])
        depois = {**sem, "error_code_action": f"{linha_ja}\nimport json"}      # depois da linha que falhou: não rodou
        self.assertEqual(d3.outros_nomes(depois, "pd"), ["json · sem import antes da falha"])
        so_json = {**sem, "error_message": falha("d = json.loads(t)", "The variable `json` is not defined.")}
        self.assertEqual(d3.outros_nomes(so_json, "json"), [])

    def test_uso_introspeccao_da_f(self):
        self.assertEqual(d3.uso_introspeccao("if 'x' not in globals():", "globals"), "verificação de existência (in)")
        self.assertEqual(d3.uso_introspeccao("u = globals().get('u', None)", "globals"), "leitura com valor padrão (.get)")
        self.assertEqual(d3.uso_introspeccao("lista = eval(obs)", "eval"), "eval(...)")
        self.assertEqual(d3.uso_introspeccao("if not has_var('x'):", "globals"),
                         "o nome não aparece na instrução (função auxiliar?)")
        self.assertEqual(d3.uso_introspeccao("print(vars(obj))", "vars"), "outro uso")

    def test_lugar_na_linha(self):
        self.assertEqual(d3.lugar_na_linha("print(repr(x))"), "dentro de print(...)")
        self.assertEqual(d3.lugar_na_linha("t = type(x).__name__"), "numa atribuição")
        self.assertEqual(d3.lugar_na_linha("if dir(x):"), "numa condição")
        self.assertEqual(d3.lugar_na_linha("return repr(x)"), "num return")


class TestContarECasos(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.p = Path(self.d.name)
        linhas = [
            # C.JoogleAnalytics: pd sem import → importa e dá outro erro
            {"cod_idef_exeo": "e1", "cod_idef_aget": 1, "papel": "J", "step_pos": 2, "mes_execucao": "2026-05",
             "error_message": falha("t = pd.DataFrame(d)", "The variable `pd` is not defined."),
             "error_code_action": "d = f()\nt = pd.DataFrame(d)", "prev_code_action": "d = f()", "prev_error_type": "",
             "next_code_action": "import pandas as pd\nt = pd.DataFrame(d)\nt['x']", "next_error_type": "E",
             "next_error_message": falha("t['x']", "KeyError: 'Valor do cliente'")},
            # E: repr dentro de print
            {"cod_idef_exeo": "e2", "cod_idef_aget": 1, "papel": "P", "step_pos": 3, "mes_execucao": "2026-06",
             "error_message": falha("print(repr(x))", "Forbidden function evaluation: 'repr' is not among the allowed"),
             "error_code_action": "x = g('Fulano de Tal')\nprint(repr(x))", "prev_code_action": "", "prev_error_type": "",
             "next_code_action": "print(type(x))", "next_error_type": "", "next_error_message": ""},
            # F: verificação de existência com globals → o passo seguinte volta a chamar e erra
            {"cod_idef_exeo": "e3", "cod_idef_aget": 1, "papel": "Q", "step_pos": 4, "mes_execucao": "2026-07",
             "error_message": falha("if 'x' not in globals():", "Forbidden function evaluation: 'globals' is not among"),
             "error_code_action": "if 'x' not in globals():\n    x = f()", "prev_code_action": "", "prev_error_type": "",
             "next_code_action": "x = globals().get('x')", "next_error_type": "E",
             "next_error_message": falha("x = globals().get('x')", "Forbidden function evaluation: 'globals'")},
        ]
        self.fonte = self.p / "fonte.parquet"
        pq.write_table(pa.Table.from_pylist(linhas), self.fonte)
        self.min = self.p / "min"
        self.min.mkdir()
        with open(self.min / "erros_lidos.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["exec_id", "agente", "role", "step_pos", "mes", "tipo", "nome", "memoria_id"])
            w.writeheader()
            w.writerow({"exec_id": "e1", "agente": 1, "role": "J", "step_pos": 2, "mes": "2026-05",
                        "tipo": "modulo_sem_import", "nome": "pd", "memoria_id": "U_sandbox.C.JoogleAnalytics"})
            w.writerow({"exec_id": "e2", "agente": 1, "role": "P", "step_pos": 3, "mes": "2026-06",
                        "tipo": "funcao_proibida", "nome": "repr", "memoria_id": "U_sandbox.E"})
            w.writerow({"exec_id": "e3", "agente": 1, "role": "Q", "step_pos": 4, "mes": "2026-07",
                        "tipo": "funcao_proibida", "nome": "globals", "memoria_id": "U_sandbox.F"})

    def tearDown(self):
        self.d.cleanup()

    def test_contar(self):
        pop = d3.ler_populacao(self.min, d3.MEMORIAS)
        med = d3.contar(pop, d3.ler_fonte(self.fonte, {d3.chave(r) for r in pop}))
        j = med["U_sandbox.C.JoogleAnalytics"]
        self.assertEqual(j["depois"], {"importa · com erro": 1})
        self.assertEqual(j["uso"], {"o nome aparece na instrução que falhou": 1})
        self.assertEqual(j["outros_nomes"], {"nenhum outro nome do inventário": 1})
        self.assertEqual(list(j["erro_seguinte"]), ['InterpreterError: KeyError: "<texto>"'])     # o valor do cliente mascarado
        self.assertEqual(med["U_sandbox.E"]["por_nome_e_lugar"], {("repr", "dentro de print(...)"): 1})
        f = med["U_sandbox.F"]
        self.assertEqual(f["por_nome_e_uso"], {("globals", "verificação de existência (in)"): 1})
        self.assertEqual((f["por_papel"], f["depois"]), ({"Q": 1}, {"com erro · volta a chamar o nome": 1}))

    def test_casos_mascarados_e_bloqueio(self):
        amostra = self.p / "casos.csv"
        with open(amostra, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["exec_id", "agente", "role", "idx", "mes"])
            w.writeheader()
            w.writerow({"exec_id": "e2", "agente": 1, "role": "P", "idx": 3, "mes": "2026-06"})
        pop = d3.ler_populacao(self.min, ("U_sandbox.E",))
        texto = d3.casos("U_sandbox.E", amostra, d3.ler_fonte(self.fonte, {("e2", "1", "P", "3")}), 10, pop)
        self.assertNotIn("Fulano", texto)
        self.assertIn(">> print(repr(x))", texto)
        self.assertEqual(d3.main(["casos", "U_sandbox.E", "--fonte", str(self.fonte), "--mineracao", str(self.min),
                                  "--amostra", str(amostra)]), 0)
        original = d3._padroes_pii
        d3._padroes_pii = lambda: {"teste": r"print"}     # um padrão que acha algo: não imprime
        try:
            self.assertEqual(d3.main(["casos", "U_sandbox.E", "--fonte", str(self.fonte), "--mineracao",
                                      str(self.min), "--amostra", str(amostra)]), 1)
        finally:
            d3._padroes_pii = original


if __name__ == "__main__":
    unittest.main()
