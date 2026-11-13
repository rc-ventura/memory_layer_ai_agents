"""Custo do passo com erro e volumetria de uma unidade: fixtures sintéticas, a conta à mão."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

import pandas as pd

PASTA = Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third" / "pipeline" / "execucao"
sys.path.insert(0, str(PASTA))
spec = spec_from_file_location("volumetria_custo_passo", PASTA / "volumetria_custo_passo.py")
vc = module_from_spec(spec)
spec.loader.exec_module(vc)


def cont():
    linhas = [dict(cod_idef_exeo=f"a-{m}-{i}", papel="PapelA", mes_execucao=m, qtd_actionsteps=4.0, tokens_total=100.0)
              for m, n in (("2026-07", 10), ("2026-08", 20)) for i in range(n)]
    return pd.DataFrame(linhas)


def casos():
    def c(exec_id, step, mes, tok, dur):
        return dict(exec_id=exec_id, step_ref=step, role="PapelA", mes=mes, tok_tot=tok, dur_s=dur)
    return pd.DataFrame([c("a-2026-07-0", "s1", "2026-07", 1000.0, 10.0), c("a-2026-07-0", "s2", "2026-07", 3000.0, 30.0),
                         c("a-2026-08-1", "s3", "2026-08", 2000.0, 20.0), c("a-2026-08-2", "s4", "2026-08", None, None)])


def erros():
    return pd.DataFrame([dict(memoria_id="M1", role="PapelA", step_ref=s, exec_id=e)
                         for s, e in (("s1", "a-2026-07-0"), ("s2", "a-2026-07-0"), ("s3", "a-2026-08-1"),
                                      ("s4", "a-2026-08-2"))])


class TestCustoPasso(unittest.TestCase):
    def test_custo_por_memoria(self):
        out, sem = vc.custo_por_memoria(erros(), casos())
        r = out.iloc[0]
        self.assertEqual((r.erros, r.execucoes), (4, 3))
        self.assertEqual(r.tokens_passo_mediana, 2000.0)          # mediana de 1000, 3000, 2000 (o None não entra)
        self.assertEqual(r.erros_sem_tokens, 1)
        self.assertEqual(r.segundos_passo_mediana, 20.0)

    def test_volumetria_unidade(self):
        por_mes, resumo, avisos = vc.volumetria_unidade(casos(), cont(), "U_x")
        r = resumo.iloc[0]
        self.assertEqual((r.erros_total, r.execucoes_com_a_unidade_total, r.execucoes_do_papel_total), (4, 3, 30))
        self.assertAlmostEqual(r.incidencia_total, 0.1)
        self.assertAlmostEqual(r.erros_por_execucao, 4 / 3)
        jul = por_mes[por_mes.mes == "2026-07"].iloc[0]
        self.assertEqual((jul.erros, jul.execucoes_com_a_unidade, jul.execucoes_do_papel), (2, 1, 10))

    def test_por_rodada_qualquer_unidade(self):
        tri = pd.DataFrame([
            dict(role="PapelA", unidade="U_x", erros_observaveis=4, execucoes=3, tokens_n_conhecidos=6000.0,
                 tokens_n_ausentes=1, dur_s_n_conhecida=60.0, dur_s_n_ausente=1),
            dict(role="PapelA", unidade="U_y", erros_observaveis=2, execucoes=2, tokens_n_conhecidos=500.0,
                 tokens_n_ausentes=0, dur_s_n_conhecida=8.0, dur_s_n_ausente=0)])
        out, avisos = vc.volumetria_por_rodada(tri, cont(), ["U_x"])
        self.assertEqual(list(out.unidade), ["U_x"])
        r = out.iloc[0]
        self.assertAlmostEqual(r.incidencia_total, 3 / 30)               # 3 execuções ÷ 30 do papel
        self.assertAlmostEqual(r.tokens_passo_media, 6000 / 3)           # 4 erros − 1 sem o dado
        self.assertAlmostEqual(r.erros_por_execucao, 4 / 3)
        self.assertEqual(len(vc.volumetria_por_rodada(tri, cont())[0]), 2)   # sem filtro: todas as unidades
        self.assertFalse({"exec_id", "step_ref", "role"} & set(out.columns))

    def test_saida_sem_identificador(self):
        por_mes, resumo, _ = vc.volumetria_unidade(casos(), cont(), "U_x")
        out, _ = vc.custo_por_memoria(erros(), casos())
        for df in (por_mes, resumo, out):
            self.assertFalse({"exec_id", "step_ref", "cod_idef_exeo"} & set(df.columns))


if __name__ == "__main__":
    unittest.main()
