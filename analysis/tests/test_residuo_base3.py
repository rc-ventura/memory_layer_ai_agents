"""Mineração do resíduo na base 3: a tabela de padrões (`especificas/residuo.py`), a auditoria independente
(`audit_residuo_base3.py`) e o encontro (`comparar_auditoria.py` da skill). Sintético: mensagens montadas aqui, nenhum
caso real."""
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import matplotlib
matplotlib.use("Agg")
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_adaptador_trace import janela  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
B3 = RAIZ / "analysis/2026-10-trace-law-flow-third"
sys.path.insert(0, str(B3 / "pipeline"))
import base_pipeline as bp  # noqa: E402
import mineracao_observada as mo  # noqa: E402


def carregar(nome, arq):
    spec = spec_from_file_location(nome, arq)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


res = carregar("residuo_base3_test", B3 / "pipeline/especificas/residuo.py")
aud = carregar("audit_residuo_base3_test", B3 / "audit/scripts/audit_residuo_base3.py")
ENCONTRO = RAIZ / ".claude/skills/mineracao-residuo/scripts/comparar_auditoria.py"

# mensagens do resíduo: (classe da causa, mensagem, err_type)
MENSAGENS = [
    ("causa_sem_regra", "Code execution failed due to: TypeError: '<' not supported between instances of 'str' and 'int'", "AgentExecutionError"),
    ("causa_sem_regra", "ValueError: dictionary update sequence element #0 has length 3; 2 is required", "AgentExecutionError"),
    ("codigo_mal_escrito", "Code parsing failed on line 4 due to: SyntaxError\nx = f(a]\n      ^\nError: closing parenthesis ']' does not match opening parenthesis '(' (<unknown>, line 4)", "AgentParsingError"),
    ("codigo_mal_escrito", "Code parsing failed due to: SyntaxError: invalid syntax on line 12", "AgentParsingError"),
    ("codigo_mal_escrito", "Code parsing failed due to: IndentationError", "AgentParsingError"),
    ("sintoma_nao_reconhecido", "InterpreterError: NoneType is not supported.", "AgentExecutionError"),
    ("sintoma_nao_reconhecido", "a execução parou sem dizer por quê", "AgentMaxStepsError"),
    ("sintoma_nao_reconhecido", "falhou com MinhaException no meio do texto", "AgentExecutionError"),
]


def linhas_residuo(padroes):
    """Um DataFrame no formato do resíduo de `EU`: (exec_id, agente, role, mes, padrao)."""
    return pd.DataFrame([{"exec_id": e, "agente": ag, "role": r, "mes": m, "unidade": "X_causa_nao_identificada",
                          "submecanismo": "causa_sem_regra", "padrao": p, "tok_tot": 10,
                          "situacao_mecanismo": "observavel"} for e, ag, r, m, p in padroes])


class TestImpressaoDigital(unittest.TestCase):
    def test_auditoria_reescreve_o_mesmo_padrao(self):
        # a auditoria não importa o pipeline: as duas implementações têm de dar o mesmo padrão
        for classe, msg, tipo in MENSAGENS:
            self.assertEqual(aud.impressao_digital(msg, classe, tipo), bp.padrao_residuo(msg, classe, tipo), msg)

    def test_sintaxe_sem_posicao_e_sem_nome(self):
        self.assertEqual(aud.impressao_digital(MENSAGENS[2][1], "codigo_mal_escrito", "AgentParsingError"),
                         "SyntaxError: closing parenthesis <q> does not match opening parenthesis <q>")
        self.assertEqual(aud.impressao_digital(MENSAGENS[3][1], "codigo_mal_escrito", "AgentParsingError"),
                         "SyntaxError: invalid syntax")
        self.assertTrue(aud.impressao_digital(MENSAGENS[6][1], "sintoma_nao_reconhecido", "AgentMaxStepsError")
                        .startswith(aud.SEM_NOME))


class TestTabelaPadroes(unittest.TestCase):
    def test_regua_por_erro_execucao_e_agente(self):
        R = linhas_residuo([("e1", 1, "A", "2026-01", "TypeError: x"), ("e2", 1, "A", "2026-02", "TypeError: x"),
                            ("e3", 1, "B", "2026-02", "TypeError: x"),
                            ("e1", 1, "A", "2026-01", "ValueError: y"), ("e1", 2, "A", "2026-01", "ValueError: y"),
                            ("e4", 1, "A", "2026-01", "ValueError: y")])
        P = res.tabela_padroes(R).set_index("padrao")
        self.assertTrue(P.loc["TypeError: x", "passa_na_recorrencia"])
        # (e1, agente 1) e (e1, agente 2) são duas execuções na régua da base 3
        self.assertEqual(P.loc["ValueError: y", "execucoes"], 3)
        self.assertEqual(P.loc["ValueError: y", "meses"], 1)
        self.assertFalse(P.loc["ValueError: y", "passa_na_recorrencia"])

    def test_sem_impressao_digital_nunca_passa(self):
        sem = f"{bp.SEM_NOME}: AgentMaxStepsError"
        R = linhas_residuo([(f"e{i}", 1, "A", f"2026-0{1 + i % 3}", sem) for i in range(6)])
        P = res.tabela_padroes(R)
        self.assertEqual(P.chave.iloc[0], bp.SEM_NOME)
        self.assertFalse(P.passa_na_recorrencia.iloc[0])


def fixture_rows():
    rows = []
    for i in range(4):   # um padrão que recorre: 4 execuções, 2 meses
        rows.append(janela(cod_idef_exeo=f"exec-res-{i}", error_message="FalhaSinteticaException: algo sintetico deu errado no passo 42",
                           mes_execucao=f"2026-0{7 + i % 2}", dat_hor_inio_exeo=f"2026-0{7 + i % 2}-01 10:00:00",
                           dat_hor_encm_exeo=f"2026-0{7 + i % 2}-01 10:01:00"))
    rows.append(janela(cod_idef_exeo="exec-res-9", error_message="OutraSinteticaException: nada a ver"))
    rows.append(janela(cod_idef_exeo="exec-res-10"))  # fora do resíduo (Could not index)
    return rows


class TestPontaAPonta(unittest.TestCase):
    """Fonte sintética → análise observada → tabela do resíduo → auditoria → encontro."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.fonte = cls.dir / "fonte.parquet"
        pd.DataFrame(fixture_rows()).to_parquet(cls.fonte, index=False)
        cls.a = mo.analisar(bp.carregar_carga(cls.fonte, "v2"))
        cls.R = res.residuo(cls.a.EU)
        cls.P = res.tabela_padroes(cls.R)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_residuo_e_conferencias(self):
        self.assertEqual(len(self.R), 5)
        self.assertEqual(int(self.P.erros.sum()), 5)
        self.assertEqual(int(self.P.passa_na_recorrencia.sum()), 1)
        feito = res.conferir(self.R, self.P, self.a.tabelas["triagem_visivel_observada"])
        self.assertEqual(len(feito), 2)

    def test_conferencia_para_se_a_triagem_diverge(self):
        T = self.a.tabelas["triagem_visivel_observada"].copy()
        T.loc[T.unidade.str.startswith("X_"), "decisao"] = bp.REVISAR_BAIXA
        with self.assertRaises(res.Parada):
            res.conferir(self.R, self.P, T)

    def test_auditoria_e_encontro(self):
        pasta = self.dir / "tabelas"
        pasta.mkdir(exist_ok=True)
        self.P.to_csv(pasta / "residuo_padroes.csv", index=False)
        res.tabela_casos(self.R).to_csv(pasta / "casos.csv", index=False)
        medidas = self.dir / "aud.json"
        self.assertEqual(aud.main(["--casos", str(pasta / "casos.csv"), "--fonte", str(self.fonte),
                                   "--json", str(medidas)]), 0)
        self.assertEqual(json.loads(medidas.read_text(encoding="utf-8"))["populacao"], 5)
        r = subprocess.run([sys.executable, str(ENCONTRO), str(B3), str(medidas), "--tabelas", str(pasta)],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout)
        # uma divergência plantada faz o encontro sair com 1
        P2 = self.P.copy()
        P2.loc[0, "execucoes"] = P2.loc[0, "execucoes"] + 1
        P2.to_csv(pasta / "residuo_padroes.csv", index=False)
        r = subprocess.run([sys.executable, str(ENCONTRO), str(B3), str(medidas), "--tabelas", str(pasta)],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 1, r.stdout)


class TestMascaraAjuste34(unittest.TestCase):
    """Ajuste 34: o endereço de memória (`0x…`) vira `<id>`, e a frase é mascarada inteira antes do corte de 90."""

    SUB, TIPO = "sintoma_nao_reconhecido", "AgentExecutionError"
    LONGA = ("LayoutError: Flowable <Table@0x{h} {r} rows x 3 cols(tallest row 1)> with cell(0,0) containing "
             "'{q}' too large on page")
    VARIANTES = [("7F3B2D1E", 3, "x"), ("7FA8BC", 12, "yy"), ("7FEAAAD0", 120, "z"), ("7F00", 7, "w")]

    def padrao(self, msg):
        return bp.padrao_residuo(msg, self.SUB, self.TIPO)

    def test_mesmo_erro_um_padrao(self):
        # endereços e números de tamanhos diferentes: antes do Ajuste 34, quatro padrões; agora, um
        padroes = {self.padrao(self.LONGA.format(h=h, r=r, q=q)) for h, r, q in self.VARIANTES}
        self.assertEqual(len(padroes), 1)
        p = padroes.pop()
        self.assertIn("Table@<id>", p)
        self.assertLessEqual(len(p), len("LayoutError: ") + 90)

    def test_corte_nao_deixa_aspas_sem_mascara(self):
        msg = "ValueError: " + "x" * 80 + " 'texto do caso que nao pode aparecer no padrao'"
        self.assertNotIn("texto do caso", self.padrao(msg))

    def test_auditoria_e_pipeline_iguais(self):
        msgs = [self.LONGA.format(h=h, r=r, q=q) for h, r, q in self.VARIANTES]
        msgs += ["UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8c in position 3: invalid start byte",
                 'KeyError: "None of [Index([\'a\', \'b\'], dtype=\'object\')] are in the [columns]"']
        for m in msgs:
            self.assertEqual(aud.impressao_digital(m, self.SUB, self.TIPO), self.padrao(m), m)

    def test_simulacao_depois_do_ajuste_nao_muda_nada(self):
        # o simular_mascara_hex.py foi a evidência do Ajuste 34; com a regra no pipeline, A e B não mudam mais nada
        sim = carregar("simular_mascara_hex_test", B3 / "pipeline/validacao/simular_mascara_hex.py")
        L = [(f"f{i}", f"2026-0{2 + i % 3}", self.LONGA.format(h=h, r=r, q=q))
             for i, (h, r, q) in enumerate(self.VARIANTES)]
        C = pd.DataFrame([{"exec_id": e, "agente": "1", "role": "A", "idx": 1, "mes": m, "unidade": "X_sintoma_nao_reconhecido",
                           "submecanismo": self.SUB, "err_type": self.TIPO, "mensagem": msg, "tok_tot": 10,
                           "padrao": self.padrao(msg)} for e, m, msg in L])
        for cortar in (False, True):
            r = sim.simular(C, cortar_depois=cortar)
            self.assertEqual(r["mudam"], 0)
            self.assertEqual(len(r["depois"]), 1)
            self.assertTrue(r["depois"].passa_na_recorrencia.iloc[0])


if __name__ == "__main__":
    unittest.main()
