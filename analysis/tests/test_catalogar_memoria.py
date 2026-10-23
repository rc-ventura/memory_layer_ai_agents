"""O catálogo das memórias fechadas (analysis/registros/memorias.json) e o catalogar_memoria.py do kit. Sintético."""
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import tempfile
import unittest

RAIZ = Path(__file__).resolve().parents[2]
spec = spec_from_file_location("catalogar_memoria", RAIZ / ".claude/skills/mineracao-candidata/scripts/catalogar_memoria.py")
cm = module_from_spec(spec)
spec.loader.exec_module(cm)


def doc(ident, destino="memória", status="derived-and-checked"):
    return {"esquema": "0.3", "unidade": "U_x", "id": ident, "parte": "C", "base": "base3", "gerado_em": "2026-10-19",
            "parte_especifica": "script:mineracao_U_x",
            "memoria": {"category": "c", "scope": {"role": None, "tool": None}, "description": "d",
                        "correction_guidance": "g", "status": status,
                        "location": {"total_erros": 2, "casos": [{"rodada_id": "r" * 64, "fonte_id": "f" * 64}]},
                        "occurrences": {"erros": 2, "execucoes": 2, "meses": ["2026-07"]},
                        "validation": {"destino": destino, "destino_decidido_em": "decisoes.md, 19/10"}}}


class TestCatalogo(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.p = Path(self.d.name)

    def tearDown(self):
        self.d.cleanup()

    def gravar(self, nome, obj):
        (self.p / nome).write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
        return self.p / nome

    def test_so_a_fechada_entra(self):
        arqs = [self.gravar("a.json", doc("U_x.C")), self.gravar("b.json", doc("U_x.E", destino="em aberto")),
                self.gravar("c.json", doc("U_x.H", destino="harness")), self.gravar("d.json", doc("U_x.P", status="parcial"))]
        entradas, fora = cm.montar(arqs)
        self.assertEqual([e["id"] for e in entradas], ["U_x.C"])
        self.assertEqual(len(fora), 3)
        self.assertIn("monitoramento.json", fora[1])
        e = entradas[0]
        self.assertNotIn("location", e)
        self.assertNotIn("evidence", e)
        self.assertEqual(e["rodada_id"], "r" * 64)
        self.assertEqual(len(e["arquivo"]["sha256_16"]), 16)

    def test_hash_ignora_bom_e_crlf(self):
        a = self.p / "a.json"; b = self.p / "b.json"
        a.write_bytes(b'{"x": 1}\n'); b.write_bytes(b'\xef\xbb\xbf{"x": 1}\r\n')
        self.assertEqual(cm._sha16(a), cm._sha16(b))

    def test_registrar_troca_a_mesma_e_confere(self):
        reg = {"o_que_e": "x", "itens": []}
        e1, _ = cm.entrada(doc("U_x.C"), self.gravar("a.json", doc("U_x.C")))
        reg, _ = cm.registrar(reg, [e1], hoje="2026-10-19")
        reg, _ = cm.registrar(reg, [{**e1, "description": "nova"}], hoje="2026-10-20")
        self.assertEqual(len(reg["itens"]), 1)
        self.assertEqual(reg["itens"][0]["description"], "nova")
        self.assertEqual(cm.conferir(reg), [])
        reg["itens"].append(dict(reg["itens"][0]))
        self.assertTrue(any("repetido" in x for x in cm.conferir(reg)))

    def test_cli_registrar(self):
        reg = self.gravar("memorias.json", {"o_que_e": "x", "itens": []})
        cat = self.p / "cat.json"
        self.assertEqual(cm.main([str(self.gravar("a.json", doc("U_x.C"))), "--saida", str(cat)]), 0)
        self.assertEqual(cm.main(["--registrar", str(cat), "--registro", str(reg)]), 0)
        self.assertEqual(cm.main(["--conferir", "--registro", str(reg)]), 0)
        self.assertEqual([e["id"] for e in json.loads(reg.read_text(encoding="utf-8"))["itens"]], ["U_x.C"])

    def test_monitorada_rara_e_reforco(self):
        mon = {"itens": [{"id": "a", "gatilhos": [{"tipo": "regua", "execucoes": 3, "meses": 2}]}]}
        e1, _ = cm.entrada(doc("U_x.C"), self.gravar("a.json", doc("U_x.C")))
        e2, _ = cm.entrada(doc("U_x.D"), self.gravar("b.json", doc("U_x.D")))
        reg, _ = cm.registrar({"itens": []}, [e1, e2], hoje="2026-10-20")
        cm.monitorar(reg, ["U_x.C"], "rara", "2 erros, 1 mês", mon, decidido_em="2026-10-21")
        cm.monitorar(reg, ["U_x.D"], "reforço", "repete o prompt", mon)
        m = {e["id"]: e["monitorada"] for e in reg["itens"]}
        self.assertEqual(m["U_x.C"]["gatilhos"], [{"tipo": "regua", "execucoes": 3, "meses": 2}])
        self.assertEqual(m["U_x.D"]["gatilhos"], [{"tipo": "cresce", "fator": 3}])
        self.assertEqual((m["U_x.C"]["linha_de_base"]["erros"], m["U_x.C"]["decidido_em"]), (2, "2026-10-21"))
        self.assertEqual(cm.conferir(reg), [])
        # mineração nova: a marcação fica, a conferência do degrau 2 sai, o alarme dispara
        reg["itens"][0]["degrau"] = 2
        novo_c = {**e1, "occurrences": {"erros": 5, "execucoes": 4, "meses": ["2026-08", "2026-09"]}}
        novo_d = {**e2, "occurrences": {"erros": 5, "execucoes": 5, "meses": ["2026-08"]}}
        reg, alarmes = cm.registrar(reg, [novo_c, novo_d], hoje="2026-11-01")
        por = {e["id"]: e for e in reg["itens"]}
        self.assertEqual(por["U_x.C"]["monitorada"]["tipo"], "rara")
        self.assertNotIn("degrau", por["U_x.C"])
        self.assertEqual(len(alarmes), 1)
        self.assertIn("U_x.C (rara): passa na régua", alarmes[0])   # a D: 5 < 3 × 2, não cresceu
        reg, alarmes = cm.registrar(reg, [{**novo_d, "occurrences": {"erros": 6, "execucoes": 6, "meses": ["2026-08"]}}])
        self.assertEqual(alarmes, ["U_x.D (reforço): cresceu: 6 erros ≥ 3 × 2"])

    def test_monitorada_malformada_nao_confere(self):
        e1, _ = cm.entrada(doc("U_x.C"), self.gravar("a.json", doc("U_x.C")))
        reg, _ = cm.registrar({"itens": []}, [{**e1, "monitorada": {"tipo": "outra"}}])
        self.assertTrue(any("`monitorada`" in x for x in cm.conferir(reg)))

    def test_cli_monitorar(self):
        reg = self.gravar("memorias.json", {"o_que_e": "x", "itens": []})
        mon = self.gravar("mon.json", {"itens": []})
        cat = self.p / "cat.json"
        cm.main([str(self.gravar("a.json", doc("U_x.C"))), "--saida", str(cat)])
        cm.main(["--registrar", str(cat), "--registro", str(reg)])
        self.assertEqual(cm.main(["--monitorar", "U_x.C", "--tipo", "reforço", "--motivo", "m", "--registro", str(reg),
                                  "--monitoramento", str(mon)]), 0)
        self.assertEqual(json.loads(reg.read_text(encoding="utf-8"))["itens"][0]["monitorada"]["tipo"], "reforço")
        with self.assertRaises(SystemExit):
            cm.main(["--monitorar", "U_x.Z", "--tipo", "rara", "--motivo", "m", "--registro", str(reg),
                     "--monitoramento", str(mon)])

    def test_o_catalogo_do_repositorio_confere(self):
        self.assertEqual(cm.conferir(cm.ler_registro(cm.REGISTRO)), [])


if __name__ == "__main__":
    unittest.main()
