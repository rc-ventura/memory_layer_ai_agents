"""A evidência do Ajuste 37 (`validacao/contar_regra_nome_ferramenta_prompt.py`): a regra do framework no prompt de
sistema, os `def` dos nomes do grupo e a atribuição `final_answer =`. Fixtures sintéticas."""
import importlib.util
import json
from pathlib import Path
import unittest

ARQ = (Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third" / "pipeline" / "validacao"
       / "contar_regra_nome_ferramenta_prompt.py")
spec = importlib.util.spec_from_file_location("contar_regra_nome_ferramenta_prompt", ARQ)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

REGRA = "7. Don't name any new variable with the same name as a tool: for instance don't name a variable 'final_answer'."


def passo(prompt):
    return {"__class__": "ActionStep", "model_input_messages": [{"content": [{"text": prompt}]}]}


class TestMedir(unittest.TestCase):
    def test_conta_por_papel(self):
        memos = [
            json.dumps({"A": [passo(f"def final_answer(answer): ...\nRules:\n{REGRA}\n")],
                        "B": [{"__class__": "PlanningStep"}, passo("def resposta_final(x): ...\nfinal_answer = 1\n")]}),
            json.dumps({"A": [passo(f"def final_answer(answer): ...\n{REGRA.replace('7.', '5.')}\n"), passo("outro")]}),
            "não é json",
            json.dumps({"C": [{"__class__": "ActionStep"}]}),   # sem prompt: não conta
        ]
        por, frases = M.medir(memos)
        self.assertEqual(set(por), {"A", "B"})
        self.assertEqual((por["A"]["execuções"], por["A"]["regra"], por["A"]["def final_answer"]), (2, 2, 2))
        self.assertEqual((por["B"]["regra"], por["B"]["def resposta_final"], por["B"]["atribui final_answer"]), (0, 1, 1))
        # o número da regra sai da frase: as duas versões contam como uma
        self.assertEqual(len(frases), 1)
        self.assertEqual(list(frases.values()), [2])


if __name__ == "__main__":
    unittest.main()
