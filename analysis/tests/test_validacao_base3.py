"""Recomputação direta: fixtures sem conteúdo ou identificadores de clientes."""
import importlib.util
from pathlib import Path
import sys
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_mecanismos_episodios_base3 import rows_chain

PIPELINE = Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third/pipeline"
spec = importlib.util.spec_from_file_location("validacao_base3_test", PIPELINE / "validacao/historico/validar_base3.py")
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


def typed_rows():
    frame = pd.DataFrame(rows_chain())
    for name in ["step_pos", "step_number", "total_tokens", "input_tokens", "output_tokens"]:
        frame[name] = pd.to_numeric(frame[name]).astype("int64")
    for prefix in ["prev", "next", "next2"]:
        for suffix in ["step_number", "total_tokens", "input_tokens", "output_tokens", "duration_seconds"]:
            name = prefix + "_" + suffix
            if name in frame:
                frame[name] = pd.to_numeric(frame[name]).astype("float64")
    return frame


class TestRecomputacao(unittest.TestCase):
    def test_inteiro_n_e_double_slot_nao_sao_conflito(self):
        self.assertEqual(validation.reciprocal_links(typed_rows()), {(0, 1): "compativel_candidato"})

    def test_diferenca_numerica_real_e_conflito(self):
        frame = typed_rows()
        frame.loc[0, "next_total_tokens"] += 1
        self.assertEqual(validation.reciprocal_links(frame), {(0, 1): "conflito"})

    def test_custo_ausente_nao_igual_custo_conhecido(self):
        frame = typed_rows()
        frame.loc[0, "next_total_tokens"] = float("nan")
        self.assertEqual(validation.reciprocal_links(frame), {(0, 1): "conflito"})

    def test_numero_nao_crescente_continua_ambiguo(self):
        frame = typed_rows()
        frame.loc[1, "step_number"] = 1
        frame.loc[0, "next_step_number"] = 1.0
        self.assertEqual(validation.reciprocal_links(frame), {(0, 1): "ambiguo"})

    def test_numero_ausente_continua_ambiguo(self):
        frame = typed_rows()
        frame["step_number"] = frame.step_number.astype("float64")
        frame.loc[1, "step_number"] = float("nan")
        frame.loc[0, "next_step_number"] = float("nan")
        self.assertEqual(validation.reciprocal_links(frame), {(0, 1): "ambiguo"})


if __name__ == "__main__":
    unittest.main()
