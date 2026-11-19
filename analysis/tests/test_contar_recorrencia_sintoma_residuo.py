"""`validacao/contar_recorrencia_sintoma_residuo.py` (base 3): os grupos do que sobrou do balde "sintoma não
reconhecido" e a régua de recorrência (≥ 3 execuções e ≥ 2 meses). Fixtures sintéticas."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

import pandas as pd

ARQ = (Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third" / "pipeline" / "validacao"
       / "contar_recorrencia_sintoma_residuo.py")
spec = importlib.util.spec_from_file_location("recorrencia_sintoma", ARQ)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

SEM = "sem nome de exceção: AgentExecutionError"


def caso(i, msg, padrao, mes="2026-07", role="P1", unidade=M.BALDE, execucao=None):
    return {"exec_id": execucao or f"e{i}", "agente": "1", "role": role, "mes": mes, "unidade": unidade,
            "padrao": padrao, "tok_tot": 10, "mensagem": msg}


def casos():
    L = []
    # pdf: 4 execuções em 2 meses → passa
    for i, mes in enumerate(["2026-05", "2026-05", "2026-07", "2026-07"]):
        L.append(caso(f"pdf{i}", "LayoutError: Flowable <Table> too large", "LayoutError: Flowable <Table>", mes))
    # decodificar: 3 execuções, 1 mês só → não passa (mês)
    for i in range(3):
        L.append(caso(f"dec{i}", "UnicodeDecodeError: 'x' codec can't decode", "UnicodeDecodeError: codec", "2026-08"))
    # etapa: 2 execuções, 2 meses → não passa (execuções); uma delas com NameError no nome
    L.append(caso("et0", "NameError: pass' due to: RuntimeError: Pipeline já concluído (resposta_json existe)",
                  "NameError: pass'", "2026-05"))
    L.append(caso("et1", "RuntimeError: Etapa 3 já foi executada; reutilize as variáveis", "RuntimeError: Etapa", "2026-07"))
    # dado/conta: três padrões diferentes, somados passam, nenhum sozinho
    L.append(caso("dt0", "AttributeError: Can only use .str accessor with string values!", "AttributeError: .str", "2026-05"))
    L.append(caso("dt1", "ZeroDivisionError: division by zero", "ZeroDivisionError: division", "2026-07"))
    L.append(caso("dt2", "DateParseError: Unknown datetime string format", "DateParseError: Unknown", "2026-07"))
    # sem nome: a chave sem impressão digital nunca passa sozinha
    for i in range(3):
        L.append(caso(f"sn{i}", "AgentExecutionError", SEM, ["2026-05", "2026-07", "2026-08"][i]))
    # recusa do LLM, que entra só para a conta fechar
    L.append(caso("rl0", "BadRequestError: litellm.ContentPolicyViolationError", "BadRequestError: litellm", "2026-05"))
    # um erro que nenhuma regra casa
    L.append(caso("ou0", "KeyboardInterrupt: parou", "KeyboardInterrupt: parou", "2026-05"))
    # outro balde: não entra
    L.append(caso("fora", "LayoutError: x", "LayoutError: x", unidade="X_causa_nao_identificada"))
    return pd.DataFrame(L)


class TestGrupos(unittest.TestCase):
    def test_cada_mensagem_cai_no_seu_grupo(self):
        casos_ = {"pdf0": "pdf_layout", "dec0": "decodificar_barra", "et0": "etapa_ja_executada",
                  "et1": "etapa_ja_executada", "dt0": "dado_tipo_ou_conta", "dt1": "dado_tipo_ou_conta",
                  "dt2": "dado_tipo_ou_conta", "sn0": "sem_nome", "rl0": "recusa_llm", "ou0": "outro"}
        S = M.contar(casos())
        got = dict(zip(S.exec_id, S.grupo))                       # `caso()` põe um "e" na frente do identificador
        for k, g in casos_.items():
            self.assertEqual(got["e" + k], g, k)

    def test_so_o_balde_do_sintoma(self):
        S = M.contar(casos())
        self.assertNotIn("efora", set(S.exec_id))
        self.assertTrue(S.unidade.eq(M.BALDE).all())

    def test_nao_e_trocado_pelo_primeiro_que_casa_mais_amplo(self):
        # uma mensagem com "Pipeline já concluído" e `NameError` é a trava da etapa, não "outro"
        g = M.grupo("NameError: pass' due to: RuntimeError: Pipeline já concluído", "NameError: pass'")
        self.assertEqual(g, "etapa_ja_executada")


class TestRegua(unittest.TestCase):
    def setUp(self):
        self.T = M.tabela(M.contar(casos())).set_index("grupo")

    def test_passa_so_com_execucoes_e_meses(self):
        self.assertTrue(self.T.loc["pdf_layout", "passa"])
        self.assertFalse(self.T.loc["decodificar_barra", "passa"])      # 3 execuções, 1 mês
        self.assertFalse(self.T.loc["etapa_ja_executada", "passa"])     # 2 execuções
        self.assertIn("1 mês", self.T.loc["decodificar_barra", "motivo"])
        self.assertIn("2 execuções", self.T.loc["etapa_ja_executada", "motivo"])
        self.assertEqual(self.T.loc["pdf_layout", "motivo"], "passa a régua")

    def test_somado_passa_mas_nenhum_padrao_sozinho(self):
        r = self.T.loc["dado_tipo_ou_conta"]
        self.assertTrue(r.passa)                                        # 3 execuções, 2 meses somados
        self.assertEqual((r.padroes, r.padroes_que_passam), (3, 0))

    def test_sem_nome_passa_a_regua_do_grupo_mas_nao_como_padrao(self):
        r = self.T.loc["sem_nome"]
        self.assertTrue(r.passa)                                        # 3 execuções, 3 meses
        self.assertEqual(r.padroes_que_passam, 0)                       # a chave sem impressão digital não passa

    def test_padrao_identificado_que_passa(self):
        # o padrão do PDF é um só e passa sozinho (4 execuções, 2 meses)
        self.assertEqual((self.T.loc["pdf_layout", "padroes"], self.T.loc["pdf_layout", "padroes_que_passam"]), (1, 1))

    def test_a_soma_dos_grupos_e_o_balde(self):
        S = M.contar(casos())
        self.assertEqual(int(self.T.erros.sum()), len(S))


class TestLinhaDeComando(unittest.TestCase):
    def test_grava_a_tabela_sem_mensagem_e_sai_com_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            arq = Path(tmp) / "casos.csv"
            casos().to_csv(arq, index=False)
            self.assertEqual(M.main(["--casos", str(arq)]), 0)
            T = pd.read_csv(Path(tmp) / "recorrencia_sintoma.csv")
            self.assertEqual(list(T.columns), M.COLUNAS)
            self.assertNotIn("mensagem", T.columns)
            self.assertIn("pdf_layout", set(T.grupo))

    def test_sem_a_coluna_mensagem_para_com_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            arq = Path(tmp) / "casos.csv"
            casos().drop(columns=["mensagem"]).to_csv(arq, index=False)
            self.assertEqual(M.main(["--casos", str(arq)]), 1)

    def test_sem_erro_do_balde_para_com_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            arq = Path(tmp) / "casos.csv"
            c = casos()
            c[c.unidade.eq(M.BALDE)].assign(unidade="X_causa_nao_identificada").to_csv(arq, index=False)
            self.assertEqual(M.main(["--casos", str(arq)]), 1)


if __name__ == "__main__":
    unittest.main()
