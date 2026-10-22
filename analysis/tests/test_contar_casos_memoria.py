"""O contador de casos por memória e da evidência de "uma causa só" nas bases 1 e 2 (contar_casos_memoria_base2.py;
dossiê do sandbox §2h, 24). Sintético."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "analysis/2026-09-trace-law-flow-second/scripts"))
spec = spec_from_file_location("contar_casos_memoria_base2",
                               RAIZ / "analysis/2026-09-trace-law-flow-second/scripts/contar_casos_memoria_base2.py")
cc = module_from_spec(spec)
spec.loader.exec_module(cc)

NAO_DEF = "Code execution failed due to: InterpreterError: The variable `{}` is not defined."
PROIBIDA = "Code execution failed due to: InterpreterError: Forbidden function evaluation: '{}' is not among the allowed"


def nomes(**kw):
    return {"importar": [], "usar": [], "nao_importar": [], "nao_usar": [], **kw}


C = {"id": "U_x.C", "scope": {"role": None}, "nomes": nomes(importar=["json", "pandas"])}
CP = {"id": "U_x.C.Q", "scope": {"role": "Q"}, "nomes": nomes(importar=["pandas"])}
E = {"id": "U_x.E", "scope": {"role": None}, "nomes": nomes(nao_usar=["repr", "dir"])}


def passo(exec_id, idx, err="", code="x = 1", role="P", mes="2026-07"):
    return {"exec_id": exec_id, "agente": 1, "role": role, "idx": idx, "mes": mes, "code": code, "err_msg": err}


class TestContarCasos(unittest.TestCase):
    def setUp(self):
        self.S = pd.DataFrame([
            passo("e1", 0, NAO_DEF.format("json")), passo("e1", 1, code="import json"),          # esqueceu e corrigiu
            passo("e2", 0, code="import json"), passo("e2", 1, NAO_DEF.format("json")),           # importou antes: outra causa
            passo("e3", 0, NAO_DEF.format("pd"), role="Q"), passo("e3", 1, PROIBIDA.format("open"), role="Q"),
            passo("e4", 0, PROIBIDA.format("repr")), passo("e4", 1, PROIBIDA.format("dir")),
            passo("e5", 0, NAO_DEF.format("resultado")),                                           # não é módulo da lista
        ])

    def test_populacao_pelos_nomes_e_papel(self):
        out, casos = cc.medir(self.S, [C, CP, E])
        self.assertEqual((out["U_x.C"]["erros"], out["U_x.C"]["execucoes"]), (3, 3))
        self.assertEqual(out["U_x.C"]["por_nome"], {"json": 2, "pd": 1})
        self.assertEqual(out["U_x.C.Q"]["erros"], 1)                     # só o papel Q
        self.assertEqual(out["U_x.E"]["por_nome"], {"dir": 1, "repr": 1})  # `open` não está na memória
        self.assertEqual(casos["U_x.C.Q"], [("e3", "2026-07", 0, "Q")])

    def test_importado_antes_e_passo_seguinte(self):
        out, _ = cc.medir(self.S, [C, E])
        self.assertEqual(out["U_x.C"]["importado_antes_sem_erro"], 1)    # só o e2
        self.assertEqual(out["U_x.C"]["passo_seguinte"], {"sem_erro": 1, "com_erro": 1, "sem_passo": 1})
        self.assertNotIn("importado_antes_sem_erro", out["U_x.E"])
        self.assertEqual(out["U_x.E"]["passo_seguinte"], {"sem_erro": 0, "com_erro": 1, "sem_passo": 1})

    def test_importados(self):
        self.assertEqual(cc.importados("import pandas as pd, os.path\nfrom json.decoder import x"),
                         {"pandas", "os", "json"})


if __name__ == "__main__":
    unittest.main()
