"""conferir_versao: o hash ignora o que copiar e colar muda (BOM, CRLF, espaços no fim, linhas vazias no fim) e a camada
da base (TRACE, BASE_ID), mas pega qualquer mudança de código."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import tempfile
import unittest

RAIZ = Path(__file__).resolve().parents[2]
_spec = spec_from_file_location("conferir_versao", RAIZ / ".claude/skills/mineracao-base/scripts/conferir_versao.py")
cv = module_from_spec(_spec)
_spec.loader.exec_module(cv)

ORIGINAL = 'import os\nTRACE = "a.csv"\nBASE_ID = "base1"\n\ndef f(x):\n    return x + 1\n'


class TestAssinatura(unittest.TestCase):
    def h(self, conteudo, nome="base_pipeline.py"):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / nome
            p.write_bytes(conteudo)
            return cv.assinatura(str(p))

    def test_copiar_e_colar_nao_muda(self):
        h0 = self.h(ORIGINAL.encode())
        sujo = "\ufeff" + ORIGINAL.replace("\n", "  \r\n") + "\r\n\r\n"
        self.assertEqual(self.h(sujo.encode("utf-8")), h0)

    def test_camada_da_base_nao_muda(self):
        h0 = self.h(ORIGINAL.encode())
        outro = ORIGINAL.replace('"a.csv"', '"b.csv"').replace('"base1"', '"base2"')
        self.assertEqual(self.h(outro.encode()), h0)

    def test_mudanca_de_codigo_muda(self):
        h0 = self.h(ORIGINAL.encode())
        self.assertNotEqual(self.h(ORIGINAL.replace("x + 1", "x + 2").encode()), h0)
        self.assertNotEqual(self.h(ORIGINAL.replace("    return", "\treturn").encode()), h0)

    def test_repositorio_bate_com_o_manifesto(self):
        esperado = __import__("json").loads((RAIZ / ".claude/skills/mineracao-base/manifesto.json").read_text())["arquivos"]
        for rel, h in esperado.items():
            self.assertEqual(cv.assinatura(str(RAIZ / "analysis/2026-09-trace-law-flow" / rel)), h, rel)


if __name__ == "__main__":
    unittest.main()
