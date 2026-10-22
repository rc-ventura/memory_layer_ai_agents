"""drill_down.py da base 3: a tabela de casos de uma memória, a janela de um erro e a evidência no contrato do kit
(dossiê do sandbox §2h, 26). Sintético."""
import csv
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import tempfile
import unittest

import pyarrow as pa
import pyarrow.parquet as pq

RAIZ = Path(__file__).resolve().parents[2]
spec = spec_from_file_location("drill_down_base3", RAIZ / "analysis/2026-10-trace-law-flow-third/pipeline/drill_down.py")
dd = module_from_spec(spec)
spec.loader.exec_module(dd)


def linha(ex, papel, pos, codigo, prox=""):
    return {"cod_idef_exeo": ex, "papel": papel, "step_pos": pos, "mes_execucao": "2026-07", "step_number": pos - 1,
            "error_code_action": codigo, "error_type": "AgentExecutionError",
            "error_message": "Forbidden function evaluation: 'repr'", "prev_code_action": "x = f()",
            "next_code_action": prox, "next_error_type": "", "next_is_final_answer": False}


class TestDrillDownBase3(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.p = Path(self.d.name)
        self.fonte = self.p / "fonte.parquet"
        pq.write_table(pa.Table.from_pylist([linha("e1", "P", 3, "print(repr(x))", "print(type(x))"),
                                             linha("e1", "P", 5, "print(dir(x))"),
                                             linha("e2", "Q", 2, "repr(y)")]), self.fonte)
        self.res = self.p / "resultados"
        (self.res / "mineracao" / "U_x").mkdir(parents=True)
        with open(self.res / "mineracao" / "U_x" / "erros_lidos.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["exec_id", "agente", "role", "step_pos", "step_ref", "mes", "memoria_id"])
            w.writeheader()
            w.writerow({"exec_id": "e1", "agente": 1, "role": "P", "step_pos": 3, "step_ref": "r1", "mes": "2026-07",
                        "memoria_id": "U_x.E"})
            w.writerow({"exec_id": "e2", "agente": 1, "role": "Q", "step_pos": 2, "step_ref": "r2", "mes": "2026-07",
                        "memoria_id": "U_x.C"})
        self.antes = dd.RESULTADOS
        dd.RESULTADOS = self.res

    def tearDown(self):
        dd.RESULTADOS = self.antes
        self.d.cleanup()

    def test_linhas_e_janela(self):
        self.assertEqual([r["step_pos"] for r in dd.linhas("e1", "P", caminho=self.fonte)], [3, 5])
        r = dd.linhas("e1", "P", "3", caminho=self.fonte)
        self.assertEqual(len(r), 1)
        txt = dd.janela(r[0])
        self.assertIn("código (`error_code_action`): print(repr(x))", txt)
        self.assertIn("**passo seguinte (n+1)**", txt)
        self.assertIn("código (`next_code_action`): print(type(x))", txt)

    def test_tabela_e_evidencia(self):
        dd.tabela("U_x.E", "mineracao/U_x/erros_lidos.csv")
        casos = self.res / "mineracao" / "U_x" / "casos_U_x.E.csv"
        with open(casos, encoding="utf-8") as fh:
            linhas = list(csv.DictReader(fh))
        self.assertEqual([(r["exec_id"], r["role"], r["idx"]) for r in linhas], [("e1", "P", "3")])
        pasta = self.res / "evidencia" / "t"
        pasta.mkdir(parents=True)
        (pasta / "casos.csv").write_text(casos.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertEqual(dd.evidencia("t", self.fonte), 0)
        cru = json.loads((pasta / "crus" / "e1__P__3.json").read_text(encoding="utf-8"))
        self.assertEqual(cru["error_code_action"], "print(repr(x))")
        self.assertTrue((pasta / "derivados" / "e1__P__3.md").exists())

    def test_fonte_pela_variavel_de_ambiente(self):
        os.environ["DRILL_DOWN_FONTE"] = str(self.fonte)
        try:
            self.assertEqual(dd.fonte(), self.fonte)
        finally:
            del os.environ["DRILL_DOWN_FONTE"]


if __name__ == "__main__":
    unittest.main()
