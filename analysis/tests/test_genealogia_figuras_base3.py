"""A genealogia em duas figuras e o recorte por unidade (`execucao/figuras_genealogia.py`, decisão de 23/10).

Fixture sintética de arestas no formato do `genealogia_arestas.csv`: uma assinatura que se abre em duas causas de
unidades diferentes, uma causa que recebe duas assinaturas, duas causas que fecham na mesma unidade.
"""
from pathlib import Path
import sys
import tempfile
import unittest

import matplotlib
matplotlib.use("Agg")
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third" / "pipeline"))
from execucao import figuras_genealogia as fg


def arestas():
    linhas = [
        ("familia->assinatura", "Contrato de retorno da ferramenta", "Could not index", 10),
        ("familia->assinatura", "Ambiente & sandbox", "Função bloqueada", 6),
        ("familia->assinatura", "Ambiente & sandbox", "Módulo sem import", 3),
        ("assinatura->submecanismo", "Could not index", "tipo_real_do_retorno", 7),        # a mesma mensagem,
        ("assinatura->submecanismo", "Could not index", "campo_inexistente_no_retorno", 3),  # duas causas
        ("assinatura->submecanismo", "Função bloqueada", "inventario_sandbox", 4),
        ("assinatura->submecanismo", "Função bloqueada", "nome_nunca_definido", 2),
        ("assinatura->submecanismo", "Módulo sem import", "modulo_sem_import", 2),
        ("assinatura->submecanismo", "Módulo sem import", "inventario_sandbox", 1),        # a mesma causa, duas mensagens
        ("submecanismo->unidade", "tipo_real_do_retorno", "U_tipo_retorno", 7),
        ("submecanismo->unidade", "campo_inexistente_no_retorno", "U_campo_inexistente", 3),
        ("submecanismo->unidade", "inventario_sandbox", "U_sandbox", 5),                   # duas causas,
        ("submecanismo->unidade", "modulo_sem_import", "U_sandbox", 2),                    # uma unidade
        ("submecanismo->unidade", "nome_nunca_definido", "U_nome_inventado", 2),
        ("unidade->destino", "U_tipo_retorno", "candidato observado · Retorno pode chegar como string", 7),
        ("unidade->destino", "U_campo_inexistente", "candidato observado · Campo inexistente", 3),
        ("unidade->destino", "U_sandbox", "candidato observado · Inventário do sandbox", 7),
        ("unidade->destino", "U_nome_inventado", "não-memória · Nome inventado", 2),
    ]
    return pd.DataFrame([dict(etapa=e, origem=o, destino=d, categoria="Geração de código", erros=n)
                         for e, o, d, n in linhas])


class TestCaminhos(unittest.TestCase):
    def test_todos_os_erros_e_o_recorte_soma_a_unidade(self):
        c = fg.caminhos(arestas())
        self.assertEqual(int(c.erros.sum()), 19)
        s = fg.caminhos(arestas(), "U_sandbox")
        self.assertEqual(int(s.erros.sum()), 7)
        self.assertEqual(set(s.submecanismo), {"inventario_sandbox", "modulo_sem_import"})
        # a assinatura que também vai para outra unidade entra só com a parte que chega aqui
        self.assertEqual(int(s[s.assinatura.eq("Função bloqueada")].erros.sum()), 4)

    def test_recusa_causa_em_duas_unidades(self):
        ar = pd.concat([arestas(), pd.DataFrame([dict(etapa="submecanismo->unidade", origem="inventario_sandbox",
                                                      destino="U_outra", categoria="x", erros=1)])])
        with self.assertRaises(fg.GenealogiaInvalida):
            fg.caminhos(ar)

    def test_recusa_unidade_inexistente(self):
        with self.assertRaisesRegex(fg.GenealogiaInvalida, "U_sandbox"):
            fg.caminhos(arestas(), "U_nada")


class TestFiguras(unittest.TestCase):
    def test_censo_e_decisao_e_recorte(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            titulo, _, ler, _ = fg.censo_sintomas(arestas(), t / "censo.png")
            self.assertTrue((t / "censo.png").is_file())
            self.assertIn("não há cruzamento", ler)
            titulo, _, ler, _ = fg.genealogia_decisao(arestas(), t / "dec.png")
            self.assertTrue((t / "dec.png").is_file())
            self.assertIn("3 assinaturas se abrem em mais de uma causa; 1 causa recebe mais de uma assinatura", ler)
            titulo, pergunta, ler, limite = fg.genealogia_decisao(arestas(), t / "sb.png", "U_sandbox")
            self.assertTrue((t / "sb.png").is_file())
            self.assertIn("U_sandbox", titulo)
            self.assertIn("da unidade U_sandbox", ler)
            self.assertIn("só os erros desta unidade", limite)


if __name__ == "__main__":
    unittest.main()
