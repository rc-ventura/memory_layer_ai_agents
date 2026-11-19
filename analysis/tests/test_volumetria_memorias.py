"""Volumetria das memórias por papel e mês: fixtures sintéticas, a conta à mão."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

import pandas as pd

ARQ = (Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third" / "pipeline" / "execucao"
       / "volumetria_memorias.py")
spec = spec_from_file_location("volumetria_memorias", ARQ)
vm = module_from_spec(spec)
spec.loader.exec_module(vm)


def cont():
    linhas = []
    # PapelA: jun 10 execuções, jul 20; PapelB: jul 4; uma linha sem passos (não conta)
    for i in range(10):
        linhas.append(dict(cod_idef_exeo=f"a-jun-{i}", papel="PapelA", mes_execucao="2026-06", qtd_actionsteps=4.0,
                           tokens_total=100.0))
    for i in range(20):
        linhas.append(dict(cod_idef_exeo=f"a-jul-{i}", papel="PapelA", mes_execucao="2026-07", qtd_actionsteps=6.0,
                           tokens_total=300.0))
    for i in range(4):
        linhas.append(dict(cod_idef_exeo=f"b-jul-{i}", papel="PapelB", mes_execucao="2026-07", qtd_actionsteps=2.0,
                           tokens_total=50.0))
    linhas.append(dict(cod_idef_exeo="sem", papel="PapelA", mes_execucao="2026-07", qtd_actionsteps=None,
                       tokens_total=None))
    return pd.DataFrame(linhas)


def erros():
    def e(exec_id, step, role, mes, mem):
        return dict(exec_id=exec_id, step_ref=step, role=role, mes=mes, memoria_id=mem)
    return pd.DataFrame([
        e("a-jun-0", "s1", "PapelA", "2026-06", "U.C"),
        e("a-jun-0", "s2", "PapelA", "2026-06", "U.C"),      # mesma execução, 2 erros: conta 1 execução
        e("a-jul-1", "s3", "PapelA", "2026-07", "U.C"),
        e("a-jul-2", "s4", "PapelA", "2026-07", "U.C"),
        e("b-jul-0", "s5", "PapelB", "2026-07", "U.C"),
        e("a-jul-3", "s6", "PapelA", "2026-07", None),        # sem memória: fora
        e("x-1", "s7", "Fantasma", "2026-07", "U.C"),         # papel sem contagens: fora, com aviso
    ])


class TestVolumetria(unittest.TestCase):
    def test_incidencia_por_mes(self):
        por_mes, _, _ = vm.contar(erros(), cont())
        a = por_mes[(por_mes.papel == "PapelA") & (por_mes.mes == "2026-06")].iloc[0]
        self.assertEqual((a.erros, a.execucoes_com_erro, a.execucoes_do_papel), (2, 1, 10))
        self.assertAlmostEqual(a.incidencia, 0.1)
        j = por_mes[(por_mes.papel == "PapelA") & (por_mes.mes == "2026-07")].iloc[0]
        self.assertEqual((j.execucoes_com_erro, j.execucoes_do_papel), (2, 20))

    def test_linha_sem_passos_nao_conta_como_execucao(self):
        den = vm.execucoes_por_papel_mes(cont())
        self.assertEqual(int(den[(den.papel == "PapelA") & (den.mes == "2026-07")].execucoes_do_papel.iloc[0]), 20)

    def test_resumo_e_ultimos_meses(self):
        _, resumo, _ = vm.contar(erros(), cont())
        a = resumo[resumo.papel == "PapelA"].iloc[0]
        self.assertEqual((a.execucoes_com_erro_total, a.execucoes_do_papel_total), (3, 30))
        self.assertEqual(a.ultimos_meses, "2026-06,2026-07")        # só há dois meses nas contagens
        self.assertAlmostEqual(a.incidencia_ultimos_2_meses, 0.1)
        self.assertEqual(a.execucoes_para_ver_1_vez_95, 29)          # ln(0,05)/ln(0,9) = 28,4 → 29

    def test_papel_sem_contagens_gera_aviso_e_sai(self):
        por_mes, resumo, avisos = vm.contar(erros(), cont())
        self.assertNotIn("Fantasma", set(por_mes.papel))
        self.assertTrue(any("Fantasma" in a for a in avisos))

    def test_nome_cortado_casa_pelo_final(self):
        mapa, avisos = vm.casar_papeis(["ontestacaoCivel"], {"ContestacaoCivel", "Outro"})
        self.assertEqual(mapa["ontestacaoCivel"], "ContestacaoCivel")
        self.assertTrue(avisos)

    def test_execucoes_para_ver(self):
        self.assertEqual(vm.execucoes_para_ver(0.5), 5)
        self.assertEqual(vm.execucoes_para_ver(0.01), 299)
        self.assertIsNone(vm.execucoes_para_ver(0))

    def test_saida_nao_tem_identificador(self):
        por_mes, resumo, _ = vm.contar(erros(), cont())
        for df in (por_mes, resumo):
            self.assertFalse({"exec_id", "step_ref", "cod_idef_exeo"} & set(df.columns))


if __name__ == "__main__":
    unittest.main()
