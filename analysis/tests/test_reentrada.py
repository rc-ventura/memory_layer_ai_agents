"""A re-entrada (`especificas/reentrada.py` da base 3): o delta pelo `step_ref` entre a foto da mineração e a rodada
nova, a cobertura de cada erro que entrou, a variação por memória, o estado e a idempotência. Fixtures sintéticas."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import pandas as pd

ARQ = (Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third" / "pipeline" / "especificas"
       / "reentrada.py")
spec = importlib.util.spec_from_file_location("reentrada", ARQ)
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


def erro(ref, mid, role="P1", mes="2026-07"):
    return {"step_ref": ref, "exec_id": f"e{ref}", "agente": "1", "role": role, "step_pos": 1, "mes": mes,
            "memoria_id": mid}


# a foto: 4 erros, a memória C (no catálogo) com 3 e a parte B.P2 (decidida, sem memória) com 1
FOTO = pd.DataFrame([erro("a", "U.C"), erro("b", "U.C"), erro("c", "U.C"), erro("d", "U.B.P2", role="P2")])
CATALOGO = {"U.C"}


class TestDelta(unittest.TestCase):
    def test_igual(self):
        D = R.delta(FOTO, FOTO, CATALOGO)
        self.assertTrue(D.empty)
        self.assertEqual(R.estado(D, R.por_memoria(FOTO, FOTO, CATALOGO)), ["igual"])

    def test_cobertura_dos_que_entraram(self):
        agora = pd.concat([FOTO, pd.DataFrame([
            erro("e", "U.C"),                    # cai numa memória do catálogo
            erro("f", "U.B.P2", role="P2"),      # cai numa parte já decidida, sem memória
            erro("g", "U.B.P3", role="P3"),      # parte por papel com um papel novo
            erro("h", None),                     # a regra não lê: sem parte
        ])])
        D = R.delta(FOTO, agora, CATALOGO)
        self.assertEqual(dict(zip(D.step_ref, D.cobertura)),
                         {"e": "memoria_no_catalogo", "f": "parte_decidida_sem_memoria", "g": "parte_nova",
                          "h": "sem_parte"})
        self.assertTrue(D.situacao.eq("entrou").all())
        # U.C passa de 3 para 4 (+33%, acima da régua de 20%): também revisar
        self.assertEqual(R.estado(D, R.por_memoria(FOTO, agora, CATALOGO)), ["descoberto", "revisar"])

    def test_cresceu_coberto_saiu_e_mudou(self):
        agora = pd.DataFrame([erro("a", "U.C"), erro("b", "U.C"), erro("c", "U.B.P2"), erro("e", "U.C")])
        D = R.delta(FOTO, agora, CATALOGO)
        sit = dict(zip(D.step_ref, D.situacao))
        self.assertEqual(sit, {"e": "entrou", "c": "mudou_de_parte", "d": "saiu"})
        M = R.por_memoria(FOTO, agora, CATALOGO)
        self.assertEqual(R.estado(D, M), ["cresceu_coberto", "encolheu", "mudou_de_parte"])

    def test_revisar_pela_variacao(self):
        # a memória do catálogo passa de 3 para 5 erros: +67% > 20%
        agora = pd.concat([FOTO, pd.DataFrame([erro("e", "U.C"), erro("f", "U.C")])])
        M = R.por_memoria(FOTO, agora, CATALOGO).set_index("memoria_id")
        self.assertTrue(M.loc["U.C", "revisar"])
        self.assertFalse(M.loc["U.B.P2", "revisar"])          # fora do catálogo: não revisa
        D = R.delta(FOTO, agora, CATALOGO)
        self.assertEqual(R.estado(D, M.reset_index()), ["cresceu_coberto", "revisar"])
        # 3 → 3 com um a mais e um a menos: variação 0
        agora2 = pd.DataFrame([erro("a", "U.C"), erro("b", "U.C"), erro("e", "U.C"), erro("d", "U.B.P2")])
        self.assertFalse(R.por_memoria(FOTO, agora2, CATALOGO).set_index("memoria_id").loc["U.C", "revisar"])

    def test_memoria_do_catalogo_fora_da_foto_nao_revisa(self):
        # U.Z está no catálogo mas não na foto: a foto é de outra mineração; não é variação
        M = R.por_memoria(FOTO, FOTO, CATALOGO | {"U.Z"}).set_index("memoria_id")
        self.assertEqual((M.loc["U.Z", "erros_foto"], bool(M.loc["U.Z", "revisar"])), (0, False))
        self.assertFalse(M.revisar.any())

    def test_vazios_viram_sem_parte(self):
        agora = pd.concat([FOTO, pd.DataFrame([erro("x", float("nan")), erro("y", "")])])
        D = R.delta(FOTO, agora, CATALOGO)
        self.assertEqual(set(D.cobertura), {"sem_parte"})

    def test_vazio_na_foto_e_agora_nao_mudou_de_parte(self):
        """O caso do ambiente (12/11): erros sem memória na foto (o CSV volta NaN) e sem memória agora (None, NaN ou
        "") não mudaram de parte; antes, NaN != NaN dava 5 `mudou_de_parte` falsos no inventário do sandbox."""
        foto = pd.concat([FOTO, pd.DataFrame([erro("s1", None), erro("s2", None), erro("s3", None)])])
        with tempfile.TemporaryDirectory() as tmp:
            foto.to_csv(Path(tmp) / "f.csv", index=False)
            foto = pd.read_csv(Path(tmp) / "f.csv")           # memoria_id vazio volta como NaN
        agora = pd.concat([FOTO, pd.DataFrame([erro("s1", None), erro("s2", float("nan")), erro("s3", "")])])
        D = R.delta(foto, agora, CATALOGO)
        self.assertTrue(D.empty, D.to_string())
        M = R.por_memoria(foto, agora, CATALOGO)
        self.assertNotIn("", set(M.memoria_id))
        self.assertEqual(R.estado(D, M), ["igual"])


class TestUnidade(unittest.TestCase):
    """O fluxo de uma unidade, com a rodada e a parte específica falsas: os arquivos, o resumo e a idempotência."""

    def _rodar(self, tmp, agora):
        mineracao = Path(tmp) / "mineracao"
        mineracao.mkdir(exist_ok=True)
        FOTO.to_csv(mineracao / "erros_lidos.csv", index=False)
        (mineracao / "passo1_rodada.json").write_text(json.dumps({"rodada_id": "r0" * 32, "fonte_id": "f"}))
        catalogo = Path(tmp) / "memorias.json"
        catalogo.write_text(json.dumps({"itens": [{"id": "U.C", "unidade": "U", "base": "b"},
                                                  {"id": "X.C", "unidade": "X", "base": "b"}]}))
        m = {"base": "b", "rodada_id": "r1" * 32, "fonte_id": "f"}
        with mock.patch.object(R, "parte_especifica", return_value=None), \
                mock.patch.object(R, "ler_agora", return_value=agora):
            return R.conferir_unidade("U", None, m, None, mineracao, catalogo, Path(tmp) / "saida")

    def test_arquivos_resumo_e_idempotencia(self):
        agora = pd.concat([FOTO, pd.DataFrame([erro("h", None, role="P9", mes="2026-08"), erro("e", "U.C")])])
        with tempfile.TemporaryDirectory() as tmp:
            out, r = self._rodar(tmp, agora)
            self.assertEqual(r["estado"], ["descoberto", "revisar"])   # U.C: 3 → 4
            self.assertEqual(r["revisar"], ["U.C"])
            self.assertEqual((r["entraram"], r["sairam"], r["mudaram_de_parte"]), (2, 0, 0))
            self.assertEqual(r["cobertura"]["sem_parte"], 1)
            self.assertEqual(r["descobertos_por_papel"], {"P9": 1})
            self.assertEqual(r["memorias_no_catalogo"], ["U.C"])     # só as da unidade
            self.assertTrue(r["mesma_fonte"])
            self.assertEqual(r["catalogo_fora_da_foto"], [])
            self.assertIsNone(r["foto_da_rodada_do_catalogo"])      # o catálogo de teste não tem rodada_id
            self.assertEqual(len(pd.read_csv(out / "descobertos.csv")), 1)
            antes = {n: (out / n).read_bytes() for n in ("delta.csv", "descobertos.csv", "por_memoria.csv",
                                                         "resumo.json")}
            self._rodar(tmp, agora)
            depois = {n: (out / n).read_bytes() for n in antes}
            self.assertEqual(antes, depois)                           # idempotente, byte a byte

    def test_sem_foto_para(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(R.Parada):
                R.ler_foto(Path(tmp))


class TestSaida(unittest.TestCase):
    def test_codigos(self):
        m = {"base": "b", "rodada_id": "r" * 64, "fonte_id": "f"}
        casos = {"U": (Path("x"), {"estado": ["igual"]}), "V": (Path("x"), {"estado": ["descoberto"]})}

        def conferir(u, *a, **k):
            if u == "W":
                raise R.Parada("sem foto")
            return casos[u]
        with mock.patch.object(R, "carregar_rodada", return_value=(None, m, None)), \
                mock.patch.object(R, "conferir_unidade", side_effect=conferir), \
                mock.patch.object(R, "_imprimir"), mock.patch("builtins.print"):
            self.assertEqual(R.main(["U", "--rodada", "r"]), 0)
            self.assertEqual(R.main(["U", "V", "--rodada", "r"]), 1)
            self.assertEqual(R.main(["V", "W", "--rodada", "r"]), 2)


if __name__ == "__main__":
    unittest.main()
