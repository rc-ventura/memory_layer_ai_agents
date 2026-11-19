"""O contador do grupo "nome de ferramenta usado como variável" do resíduo da base 3 (`validacao/
contar_nome_ferramenta_residuo.py`): o nome, a forma da linha e a repetição. Fixtures sintéticas."""
from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

import pandas as pd

ARQ = (Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third" / "pipeline" / "validacao"
       / "contar_nome_ferramenta_residuo.py")
spec = importlib.util.spec_from_file_location("contar_nome_ferramenta_residuo", ARQ)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def msg(linha, nome):
    return (f"Code execution failed at line '{linha}' due to: InterpreterError: Cannot assign to name '{nome}': "
            "doing this would erase the existing tool!")


class TestForma(unittest.TestCase):
    def test_formas(self):
        casos = {
            "resultado_com_o_nome": msg("busca = busca(q='x')", "busca"),
            "outro_valor": msg("busca = []", "busca"),
            "alvo_multiplo": msg("a, busca = f()", "busca"),
            "laco": msg("for i, busca in enumerate(xs):", "busca"),
            "funcao": msg("def busca(q):", "busca"),
            "outra": msg("print(busca)", "busca"),
            "sem_linha": "InterpreterError: Cannot assign to name 'busca': doing this would erase the existing tool!",
        }
        for esperado, m in casos.items():
            self.assertEqual(M.forma(m, "busca"), esperado, m)
        # comparação não é atribuição
        self.assertEqual(M.forma(msg("busca == 1", "busca"), "busca"), "outra")
        # o nome tem de estar inteiro
        self.assertEqual(M.forma(msg("buscas = 1", "busca"), "busca"), "outra")


class TestContar(unittest.TestCase):
    def test_grupo_repeticao_e_saida(self):
        linhas = [
            dict(exec_id="e1", agente="A", role="P1", idx=1, mes="2026-05", unidade="X_sintoma_nao_reconhecido",
                 tok_tot=10, mensagem=msg("busca = busca(q=1)", "busca")),
            dict(exec_id="e1", agente="A", role="P1", idx=2, mes="2026-05", unidade="X_sintoma_nao_reconhecido",
                 tok_tot=10, mensagem=msg("busca = busca(q=2)", "busca")),
            dict(exec_id="e2", agente="A", role="P2", idx=1, mes="2026-06", unidade="X_sintoma_nao_reconhecido",
                 tok_tot=5, mensagem=msg("docs = []", "docs")),
            dict(exec_id="e3", agente="A", role="P2", idx=1, mes="2026-06", unidade="X_sintoma_nao_reconhecido",
                 tok_tot=5, mensagem="KeyError: 'x'"),
        ]
        G = M.contar(pd.DataFrame(linhas))
        self.assertEqual(len(G), 3)
        self.assertEqual(G.nome.value_counts().to_dict(), {"busca": 2, "docs": 1})
        r = M.repeticao(G)
        self.assertEqual((r["execuções-papel com o erro"], r["com o erro 2+ vezes"], r["2+ vezes com o mesmo nome"]),
                         (2, 1, 1))
        with tempfile.TemporaryDirectory() as tmp:
            casos = Path(tmp) / "casos.csv"
            pd.DataFrame(linhas).to_csv(casos, index=False)
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(M.main(["--casos", str(casos)]), 0)
            self.assertIn("3 erros · 2 execuções · 2 meses", out.getvalue())
            self.assertNotIn("busca = busca", out.getvalue())   # nada de código na saída
            gravado = pd.read_csv(Path(tmp) / "casos_nome_ferramenta.csv")
            self.assertNotIn("mensagem", gravado.columns)
            self.assertEqual(len(gravado), 3)


if __name__ == "__main__":
    unittest.main()
