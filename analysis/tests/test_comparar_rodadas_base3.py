"""comparar_rodadas (b3 #42): rodadas sintéticas, sem conteúdo nem identificadores reais."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

PIPELINE = Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third/pipeline"
sys.path.insert(0, str(PIPELINE))
import mineracao_observada as mo
from validacao import comparar_rodadas as cr

RESUMO = {"erros_estruturados": 5, "pendentes": 1, "tokens_estruturados_conhecidos": 50, "papeis": {"a": 3, "b": 2}}
TABELAS = {
    "triagem_visivel_observada.csv": "unidade,erros_observaveis,tokens_n_conhecidos\nU_x,3,30\nU_y,1,10\n",
    "consolidacao_unidade_papel_tokens.csv": ("unidade,role,erros,tokens_n_conhecidos,tokens_n_ausentes\n"
                                              "U_x,a,2,20,0\nU_x,b,1,10,0\nU_y,a,1,10,0\n"
                                              f"{mo.SEM_UNIDADE},b,1,10,0\n"),
    "consolidacao_depois_unidade.csv": "unidade,depois,erros\nU_x,recupera,3\nU_y,final,1\nsem,final,1\n",
    "genealogia_arestas.csv": ("etapa,origem,destino,categoria,erros\n"
                               "familia->unidade,F1,U_x,c,3\nfamilia->unidade,F2,U_y,c,2\n"
                               "unidade->destino,U_x,memoria,c,3\nunidade->destino,U_y,harness,c,2\n"),
    "perfis/U_x/casos.csv": "rodada_id,erros\nRODADA,3\n",
}


def rodada(pasta, rodada_id, tabelas=None, resumo=None, figura=b"png"):
    pasta.mkdir(parents=True)
    artefatos = {}
    for nome, texto in {**TABELAS, **(tabelas or {})}.items():
        if texto is None:
            continue
        (pasta / nome).parent.mkdir(parents=True, exist_ok=True)
        (pasta / nome).write_text(texto.replace("RODADA", rodada_id), encoding="utf-8")
        artefatos[nome] = hashlib.sha256((pasta / nome).read_bytes()).hexdigest()
    (pasta / "genealogia_observada.png").write_bytes(figura)
    artefatos["genealogia_observada.png"] = hashlib.sha256(figura).hexdigest()
    m = {"estado": cr.CONCLUIDA, "rodada_id": rodada_id, "contrato": "c", "base": "base3", "fonte_id": "f" * 64,
         "extracao": "v2", "codigo": {"m.py": rodada_id}, "resumo": resumo or RESUMO, "artefatos": artefatos}
    (pasta / "manifesto.json").write_text(json.dumps(m), encoding="utf-8")
    return pasta


class TestCompararRodadas(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.antes = rodada(self.tmp / "a", "a" * 64)

    def comparar(self, depois):
        with redirect_stdout(io.StringIO()) as out:
            falhas = cr.comparar(self.antes, depois)
        return falhas, out.getvalue()

    def test_rotulo_sem_unidade_e_o_do_pipeline(self):
        self.assertEqual(cr.SEM_UNIDADE, mo.SEM_UNIDADE)

    def test_mesmos_numeros_fecha_com_rodada_id_e_figura_diferentes(self):
        falhas, out = self.comparar(rodada(self.tmp / "b", "b" * 64, figura=b"outra"))
        self.assertEqual(falhas, [])
        self.assertIn("difere só em rodada_id", out)
        self.assertIn("figura diferente", out)

    def test_coluna_nova_nao_e_numero_mudado(self):
        t = {"triagem_visivel_observada.csv": "unidade,erros_observaveis,tokens_n_conhecidos,finalidade\n"
                                              "U_x,3,30,candidatura\nU_y,1,10,candidatura\n"}
        falhas, out = self.comparar(rodada(self.tmp / "b", "b" * 64, t))
        self.assertEqual(falhas, [])
        self.assertIn("só colunas novas", out)

    def test_so_a_ordem_das_linhas(self):
        t = {"triagem_visivel_observada.csv": "unidade,erros_observaveis,tokens_n_conhecidos\nU_y,1,10\nU_x,3,30\n"}
        falhas, out = self.comparar(rodada(self.tmp / "b", "b" * 64, t))
        self.assertEqual(falhas, [])
        self.assertIn("só a ordem das linhas", out)

    def test_numero_mudado_nao_fecha(self):
        t = {"perfis/U_x/casos.csv": "rodada_id,erros\nRODADA,4\n"}
        falhas, _ = self.comparar(rodada(self.tmp / "b", "b" * 64, t))
        self.assertTrue(any("perfis/U_x/casos.csv: conteúdo diferente" in f for f in falhas))

    def test_resumo_diferente_nao_fecha(self):
        falhas, _ = self.comparar(rodada(self.tmp / "b", "b" * 64, resumo={**RESUMO, "papeis": {"a": 4, "b": 1}}))
        self.assertIn("resumo: papeis.a", falhas)

    def test_tabela_removida_nao_fecha(self):
        falhas, _ = self.comparar(rodada(self.tmp / "b", "b" * 64, {"perfis/U_x/casos.csv": None}))
        self.assertIn("tabela removida: perfis/U_x/casos.csv", falhas)

    def test_artefato_alterado_nao_fecha_nem_e_lido_mas_o_resto_e_comparado(self):
        depois = rodada(self.tmp / "b", "b" * 64)
        (depois / "perfis/U_x/casos.csv").write_text("rodada_id,erros\nX,9\n", encoding="utf-8")
        falhas, out = self.comparar(depois)
        self.assertEqual(falhas, ["b: perfis/U_x/casos.csv alterado depois da rodada"])
        self.assertIn("conteúdo diferente)", out)
        self.assertIn("igual (hash)", out)
        self.assertNotIn("perfis/*/casos.csv", out)

    def test_artefato_ausente_e_dito_ausente(self):
        (self.antes / "perfis/U_x/casos.csv").unlink()
        falhas, _ = self.comparar(rodada(self.tmp / "b", "b" * 64))
        self.assertEqual(falhas, ["a: perfis/U_x/casos.csv ausente depois da rodada"])

    def test_pista_de_editor_so_o_fim_de_linha(self):
        depois = rodada(self.tmp / "b", "b" * 64)
        p = depois / "perfis/U_x/casos.csv"
        p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
        _, out = self.comparar(depois)
        self.assertIn("só o fim de linha", out)

    def test_tabela_usada_na_conferencia_alterada_pula_a_conferencia(self):
        depois = rodada(self.tmp / "b", "b" * 64)
        (depois / "triagem_visivel_observada.csv").write_text("unidade\n", encoding="utf-8")
        falhas, out = self.comparar(depois)
        self.assertIn("não conferidas: triagem_visivel_observada.csv", out)
        self.assertEqual(len(falhas), 1)

    def test_fonte_diferente_para(self):
        depois = rodada(self.tmp / "b", "b" * 64)
        m = json.loads((depois / "manifesto.json").read_text(encoding="utf-8"))
        (depois / "manifesto.json").write_text(json.dumps({**m, "fonte_id": "0" * 64}), encoding="utf-8")
        with self.assertRaises(SystemExit), redirect_stdout(io.StringIO()):
            cr.comparar(self.antes, depois)

    def test_genealogia_com_outra_forma_e_os_mesmos_erros_fecha(self):
        g = ("etapa,origem,destino,categoria,erros\nfamilia->licao,F1,U_x · memoria,c,3\n"
             "familia->licao,F2,U_y · harness,c,2\n")
        falhas, out = self.comparar(rodada(self.tmp / "b", "b" * 64, {"genealogia_arestas.csv": g}))
        self.assertEqual(falhas, [])
        self.assertIn("erros conservados", out)

    def test_genealogia_que_perde_erro_nao_fecha(self):
        g = ("etapa,origem,destino,categoria,erros\nfamilia->unidade,F1,U_x,c,3\nfamilia->unidade,F2,U_y,c,1\n"
             "unidade->destino,U_x,memoria,c,3\nunidade->destino,U_y,harness,c,1\n")
        falhas, _ = self.comparar(rodada(self.tmp / "b", "b" * 64, {"genealogia_arestas.csv": g}))
        self.assertTrue(any(f.startswith("genealogia:") for f in falhas))

    def test_tabela_nova_que_nao_soma_a_triagem_nao_fecha(self):
        t = {"consolidacao_unidade_papel_tokens.csv": ("unidade,role,erros,tokens_n_conhecidos,tokens_n_ausentes\n"
                                                       "U_x,a,2,20,0\nU_y,a,2,10,0\n"
                                                       f"{mo.SEM_UNIDADE},b,1,10,0\n")}
        falhas, _ = self.comparar(rodada(self.tmp / "b", "b" * 64, t))
        self.assertTrue(any("por unidade = triagem" in f for f in falhas))

    def test_o_que_vem_depois_que_nao_soma_os_erros_nao_fecha(self):
        t = {"consolidacao_depois_unidade.csv": "unidade,depois,erros\nU_x,recupera,3\n"}
        falhas, _ = self.comparar(rodada(self.tmp / "b", "b" * 64, t))
        self.assertTrue(any("o que vem depois" in f for f in falhas))

    def test_por_papel_contra_a_fonte(self):
        import pandas as pd
        fonte = self.tmp / "fonte.parquet"
        pd.DataFrame({"papel": ["a", "a", "a", "b", "b", "b"], "structured_error": [1, 1, 1, 1, 1, 0],
                      "total_tokens": [10, 10, 10, 10, 10, 99]}).to_parquet(fonte, index=False)
        depois = rodada(self.tmp / "b", "b" * 64)
        upt = pd.read_csv(depois / "consolidacao_unidade_papel_tokens.csv")
        checks = cr._por_papel_na_fonte(upt, {}, fonte)
        self.assertTrue(all(ok for ok, _ in checks.values()), checks)
        upt.loc[0, "tokens_n_conhecidos"] += 1
        self.assertFalse(cr._por_papel_na_fonte(upt, {}, fonte)["por papel = fonte (tokens)"][0])

    def test_perfis_numa_linha_por_tabela(self):
        itens = [("perfis/U_x/casos.csv", "d"), ("perfis/U_y/casos.csv", "d"), ("triagem.csv", "")]
        self.assertEqual(cr._juntar_perfis(itens), [("perfis/*/casos.csv (2 unidades)", "d"), ("triagem.csv", "")])


if __name__ == "__main__":
    unittest.main()
