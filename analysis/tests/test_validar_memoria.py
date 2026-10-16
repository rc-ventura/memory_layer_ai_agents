"""validar_memoria com o esquema 0.2 (b3 #44): o localizador da base 3 e os arquivos 0.1 da base 1. Sintético."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

RAIZ = Path(__file__).resolve().parents[2]
ESQUEMA = json.loads((RAIZ / "analysis/registros/esquema-memoria.json").read_text(encoding="utf-8"))
_spec = importlib.util.spec_from_file_location(
    "validar_memoria", RAIZ / ".claude/skills/mineracao-candidata/scripts/validar_memoria.py")
vm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vm)

CASO_BASE1 = {"exec_id": "e-1", "role": "PapelA", "idx": 3, "mes": "2026-01"}
CASO_BASE3 = {"step_ref": "a1b2", "fonte_id": "908aa005", "rodada_id": "96958e65", "role": "PapelA", "mes": "2026-08"}


def arquivo(casos, versao="0.2", parte="script:sandbox"):
    mem = {"category": "c", "scope": {"role": None, "tool": None},
           "location": {"total_erros": len(casos), "casos": casos}, "evidence": [], "description": "d",
           "correction_guidance": "g", "occurrences": {}, "status": "hipotese", "validation": {}, "impact": None}
    origem = {c: {"tipo": "checado", "comando": "x"} for c in mem}
    return {"esquema": versao, "unidade": "U_x", "base": "base3", "gerado_em": "2026-10-16",
            "parte_especifica": parte, "memoria": mem, "origem": origem}


class TestValidarMemoria(unittest.TestCase):
    def erros(self, arq):
        return vm.validar(ESQUEMA, arq)[0]

    def test_localizador_da_base3_sem_exec_id_nem_idx(self):
        self.assertEqual(self.erros(arquivo([CASO_BASE3])), [])

    def test_localizador_da_base1(self):
        self.assertEqual(self.erros(arquivo([CASO_BASE1], parte="notebook:n")), [])

    def test_arquivo_01_continua_valido(self):
        self.assertEqual(self.erros(arquivo([CASO_BASE1], versao="0.1", parte="notebook:n")), [])

    def test_versao_desconhecida_reprova(self):
        self.assertTrue(any("versão" in e for e in self.erros(arquivo([CASO_BASE3], versao="0.9"))))

    def test_localizador_incompleto_reprova(self):
        for falta in ("step_ref", "fonte_id", "rodada_id"):
            caso = {k: v for k, v in CASO_BASE3.items() if k != falta}
            self.assertTrue(any("localizador" in e for e in self.erros(arquivo([caso]))), falta)

    def test_idx_sem_exec_id_reprova(self):
        caso = {k: v for k, v in CASO_BASE1.items() if k != "exec_id"}
        self.assertTrue(any("localizador" in e for e in self.erros(arquivo([caso]))))

    def test_caso_sem_papel_ou_mes_reprova(self):
        for falta in ("role", "mes"):
            caso = copy.deepcopy(CASO_BASE3); caso.pop(falta)
            self.assertTrue(any(f"sem {falta}" in e for e in self.erros(arquivo([caso]))), falta)

    def test_prefixo_da_parte_especifica(self):
        self.assertEqual(self.erros(arquivo([CASO_BASE3], parte="investigacao:candidata")), [])
        self.assertTrue(any("parte específica" in e for e in self.erros(arquivo([CASO_BASE3], parte="planilha:x"))))

    def test_arquivos_finais_da_base1_no_repositorio(self):
        achados = sorted((RAIZ / "analysis/2026-09-trace-law-flow").rglob("memoria_U_*_base1.json"))
        for p in achados:
            self.assertEqual(self.erros(json.loads(p.read_text(encoding="utf-8"))), [], p.name)


if __name__ == "__main__":
    unittest.main()
