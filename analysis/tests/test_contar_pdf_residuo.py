"""`validacao/contar_pdf_residuo.py` (base 3): o que o agente muda no passo seguinte ao `LayoutError` do PDF. Fixtures
sintéticas: o que mudou (por regra, em ordem), as medidas e a linha de comando."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

import pandas as pd

ARQ = (Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third" / "pipeline" / "validacao"
       / "contar_pdf_residuo.py")
spec = importlib.util.spec_from_file_location("contar_pdf", ARQ)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

FERR = "orquestrador_papel"
LONGO = "x" * 400
FALHOU = f"{FERR}(titulo='t', tabela='{LONGO}')\nprint('ok')\n"


class TestMudanca(unittest.TestCase):
    def test_sem_passo(self):
        q, m = P.mudanca(FALHOU, None, FERR)
        self.assertEqual(q, "sem_passo")
        self.assertEqual(m["chars_seguinte"], 0)
        self.assertEqual(P.mudanca(FALHOU, float("nan"), FERR)[0], "sem_passo")

    def test_nao_parseia_so_conta_caracteres(self):
        q, m = P.mudanca(FALHOU, f"{FERR}(", FERR)
        self.assertEqual(q, "nao_parseia")
        self.assertEqual(m["chars_seguinte"], len(f"{FERR}("))
        self.assertIsNone(m["chamadas_seguinte"])

    def test_outra_ferramenta(self):
        self.assertEqual(P.mudanca(FALHOU, "outra_ferramenta(1)\n", FERR)[0], "outra_ferramenta")

    def test_dividiu_em_varias_chamadas(self):
        seguinte = f"{FERR}(titulo='a', tabela='{LONGO[:200]}')\n{FERR}(titulo='b', tabela='{LONGO[200:]}')\n"
        q, m = P.mudanca(FALHOU, seguinte, FERR)
        self.assertEqual((q, m["chamadas_falhou"], m["chamadas_seguinte"]), ("dividiu", 1, 2))

    def test_encurtou_pelo_menos_20_por_cento(self):
        q, m = P.mudanca(FALHOU, f"{FERR}(titulo='t', tabela='{LONGO[:100]}')\n", FERR)
        self.assertEqual(q, "encurtou")
        self.assertEqual((m["literal_falhou"], m["literal_seguinte"]), (400, 100))
        # 15% menor não é encurtar
        quase = f"{FERR}(titulo='t', tabela='{LONGO[:340]}')\nprint('ok')\n"
        self.assertEqual(P.mudanca(FALHOU, quase, FERR)[0], "outra_mudanca")

    def test_outra_mudanca(self):
        outro = FALHOU.replace("titulo='t'", "titulo='u'")
        self.assertEqual(P.mudanca(FALHOU, outro, FERR)[0], "outra_mudanca")

    def test_o_nome_da_ferramenta_vale_com_ponto(self):
        self.assertEqual(P.chamadas(P._arvore(f"mod.{FERR}(1)\n{FERR}(2)"), FERR), 2)

    def test_precedencia_dividiu_antes_de_encurtou(self):
        # mais chamadas e mais curto: vale "dividiu" (vem antes na ordem)
        seguinte = f"{FERR}('a')\n{FERR}('b')\n"
        self.assertEqual(P.mudanca(FALHOU, seguinte, FERR)[0], "dividiu")


def fonte(codigos):
    """A fonte sintética: um passo por erro, com o código que falhou e o do passo seguinte."""
    return pd.DataFrame([{"cod_idef_exeo": f"e{i}", "cod_idef_aget": "1", "papel": "P1", "step_pos": 1,
                          "cod_vers_aget": "v", "mes_execucao": "2026-03", "error_code_action": f,
                          "prev_code_action": None, "next_step_number": None if s is None else 2,
                          "next_code_action": s, "next_error_message": None, "next2_step_number": None,
                          "next2_code_action": None, "next2_error_message": None}
                         for i, (f, s) in enumerate(codigos)])


def casos(n, ferr=FERR):
    msg = f"Code execution failed at line '{ferr}(titulo=t)' due to: LayoutError: Flowable too large"
    return pd.DataFrame([{"exec_id": f"e{i}", "agente": "1", "role": "P1", "idx": 1, "mes": "2026-03",
                          "unidade": "X_sintoma_nao_reconhecido", "padrao": "LayoutError: Flowable", "tok_tot": 10,
                          "mensagem": msg} for i in range(n)])


class TestMedir(unittest.TestCase):
    def test_uma_linha_por_erro_com_a_ferramenta_e_o_que_mudou(self):
        cod = [(FALHOU, f"{FERR}('a')\n{FERR}('b')\n"), (FALHOU, None), (FALHOU, "outra(1)\n")]
        T, faltam = P.medir(casos(3), fonte(cod))
        self.assertEqual(faltam, 0)
        self.assertEqual(list(T.columns), P.COLUNAS)
        self.assertEqual(list(T.mudanca), ["dividiu", "sem_passo", "outra_ferramenta"])
        self.assertEqual(set(T.ferramenta), {FERR})

    def test_erro_sem_linha_na_fonte(self):
        T, faltam = P.medir(casos(2), fonte([(FALHOU, "x = 1\n")]))
        self.assertEqual(faltam, 1)
        self.assertEqual(T.mudanca.iloc[1], "sem_passo")


class TestLinhaDeComando(unittest.TestCase):
    def test_grava_so_numeros_e_sai_com_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = Path(tmp) / "casos.csv"
            f = Path(tmp) / "fonte.parquet"
            casos(2).to_csv(c, index=False)
            fonte([(FALHOU, f"{FERR}('a')\n{FERR}('b')\n"), (FALHOU, f"{FERR}(tabela='{LONGO[:50]}')\n")]).to_parquet(f)
            self.assertEqual(P.main(["--casos", str(c), "--fonte", str(f)]), 0)
            T = pd.read_csv(Path(tmp) / "pdf_medidas.csv")
            self.assertEqual(list(T.columns), P.COLUNAS)
            self.assertEqual(sorted(T.mudanca), ["dividiu", "encurtou"])
            self.assertFalse({"exec_id", "mensagem", "step_ref"} & set(T.columns))

    def test_sem_erro_do_grupo_para_com_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = Path(tmp) / "casos.csv"
            f = Path(tmp) / "fonte.parquet"
            outro = casos(1)
            outro["mensagem"] = "ValueError: x"
            outro.to_csv(c, index=False)
            fonte([(FALHOU, None)]).to_parquet(f)
            self.assertEqual(P.main(["--casos", str(c), "--fonte", str(f)]), 1)

    def test_sem_a_coluna_mensagem_para_com_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = Path(tmp) / "casos.csv"
            casos(1).drop(columns=["mensagem"]).to_csv(c, index=False)
            self.assertEqual(P.main(["--casos", str(c), "--fonte", str(Path(tmp) / "x.parquet")]), 1)


if __name__ == "__main__":
    unittest.main()
