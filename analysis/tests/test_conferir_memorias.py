"""O degrau 2 da validação das memórias (conferir_memorias.py, kit), o esquema 0.4 (`validation.nomes`) no validador e no
catálogo, e o extrator do prompt das bases 1 e 2. Sintético."""
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
KIT = RAIZ / ".claude/skills/mineracao-candidata/scripts"


def carregar(nome, arq):
    spec = spec_from_file_location(nome, arq)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


cf = carregar("conferir_memorias", KIT / "conferir_memorias.py")
cm = carregar("catalogar_memoria", KIT / "catalogar_memoria.py")
vm = carregar("validar_memoria", KIT / "validar_memoria.py")
sys.path.insert(0, str(RAIZ / "analysis/2026-09-trace-law-flow-second/scripts"))
ep = carregar("extrair_prompts_base2", RAIZ / "analysis/2026-09-trace-law-flow-second/scripts/extrair_prompts_base2.py")
ea = carregar("extrair_ambiente_base2", RAIZ / "analysis/2026-09-trace-law-flow-second/scripts/extrair_ambiente_base2.py")
am = carregar("ambiente_da_mineracao",
              RAIZ / "analysis/2026-10-trace-law-flow-third/pipeline/validacao/ambiente_da_mineracao.py")

LISTA = "You can use imports in your code, but only from the following list of modules: {}"
COM_PANDAS = "def get_docs(p: string) -> object:\n    pass\n" + LISTA.format("['json', 'pandas', 're']")
SEM_PANDAS = "def get_docs(p: string) -> object:\n    pass\n" + LISTA.format("['json', 're']")
INSTRUIDO = SEM_PANDAS + "\nAntes de chamar qualquer tool, VERIFIQUE se a variável de saída já está preenchida."
CITA = SEM_PANDAS + "\nIf you need the raw text, use `get_document_text` with the hash."
INSTR = [("U_x", re.compile(r"(?i)verifi\w*\s+se\s+a\s+vari[aá]vel"), {"globals", "locals"})]
RG = {"execucoes": 3, "meses": 2}


def nomes(**kw):
    return {"importar": [], "usar": [], "nao_importar": [], "nao_usar": [], **kw}


def versao(prompt, v="v1", execucoes=2):
    return {"role": "P", "versao": v, "meses": ["2026-07"], "execucoes": execucoes, "prompt": prompt}


def entrada(n, role=None, execucoes=5, meses=("2026-07", "2026-08")):
    return {"id": "U_x.C", "base": "base3", "scope": {"role": role, "tool": None}, "nomes": n,
            "occurrences": {"erros": 9, "execucoes": execucoes, "meses": list(meses)}}


class TestChecagens(unittest.TestCase):
    def test_ambiente_modulo_fora_da_lista(self):
        self.assertEqual(cf.ambiente(nomes(importar=["pandas"]), COM_PANDAS)[0], cf.PASSA)
        r, motivos = cf.ambiente(nomes(importar=["pandas"]), SEM_PANDAS)
        self.assertEqual(r, cf.FALHA)
        self.assertIn("importar pandas: fora da lista autorizada", motivos)

    def test_ambiente_ferramenta_atributo_e_funcao_do_python(self):
        self.assertEqual(cf.ambiente(nomes(usar=["get_docs"]), SEM_PANDAS)[0], cf.PASSA)
        self.assertEqual(cf.ambiente(nomes(usar=["get_document_text"]), SEM_PANDAS)[0], cf.FALHA)
        self.assertEqual(cf.ambiente(nomes(usar=["json.loads"]), SEM_PANDAS)[0], cf.PASSA)
        self.assertEqual(cf.ambiente(nomes(usar=["pandas.read_json"]), SEM_PANDAS)[0], cf.FALHA)
        self.assertEqual(cf.ambiente(nomes(usar=["print"]), SEM_PANDAS)[0], cf.NV)   # só função do Python

    def test_ambiente_proibir_o_que_o_ambiente_permite(self):
        self.assertEqual(cf.ambiente(nomes(nao_importar=["re"]), SEM_PANDAS)[0], cf.FALHA)
        self.assertEqual(cf.ambiente(nomes(nao_importar=["ast"]), SEM_PANDAS)[0], cf.PASSA)

    def test_ambiente_sem_lista_no_prompt(self):
        self.assertEqual(cf.ambiente(nomes(importar=["json"]), "def f(x):\n    pass\n")[0], cf.NV)

    def test_conflito_nome_citado_e_instrucao_registrada(self):
        self.assertEqual(cf.conflito(nomes(nao_importar=["get_document_text"]), CITA, INSTR)[0], cf.FALHA)
        self.assertEqual(cf.conflito(nomes(nao_importar=["get_document_text"]), SEM_PANDAS, INSTR)[0], cf.PASSA)
        self.assertEqual(cf.conflito(nomes(nao_usar=["globals", "repr"]), INSTRUIDO, INSTR)[0], cf.FALHA)
        self.assertEqual(cf.conflito(nomes(nao_usar=["repr"]), INSTRUIDO, INSTR)[0], cf.PASSA)   # não induzido
        self.assertEqual(cf.conflito(nomes(nao_usar=["globals"]), SEM_PANDAS, INSTR)[0], cf.PASSA)  # sem a instrução

    def test_citado_so_em_forma_de_codigo(self):
        self.assertTrue(cf.citado("use `tools` here", "tools"))
        self.assertTrue(cf.citado("x = globals()", "globals"))
        self.assertTrue(cf.citado("import copy", "copy"))
        self.assertFalse(cf.citado("the tools are listed below; copy the result", "tools"))
        self.assertFalse(cf.citado("the tools are listed below; copy the result", "copy"))
        self.assertFalse(cf.citado("x.copy()", "copy"))   # método de outro objeto, não o módulo
        # Ajuste 28: a prosa em inglês do prompt do OBFCivel (base 1) não é citação
        self.assertFalse(cf.citado("and mandatory fallback tools (actions to take if missing)", "tools"))
        self.assertFalse(cf.citado("not in the document or in the returns from tools.", "tools"))
        self.assertTrue(cf.citado("from tools import get_docs", "tools"))
        self.assertTrue(cf.citado("from tools.sub import x", "tools"))

    def test_repete_lista_autorizada(self):
        self.assertEqual(cf.repete(nomes(nao_importar=["ast", "copy"]), SEM_PANDAS)[0], cf.FALHA)
        self.assertEqual(cf.repete(nomes(importar=["json"]), SEM_PANDAS)[0], cf.PASSA)
        self.assertEqual(cf.repete(nomes(importar=["json"], usar=["get_docs"]), SEM_PANDAS + "\nget_docs(p)")[0],
                         cf.PARCIAL)
        self.assertEqual(cf.repete(nomes(), SEM_PANDAS)[0], cf.NV)


class TestMemoria(unittest.TestCase):
    def test_global_falha_se_algum_papel_falha(self):
        prompts = {"A": [versao(COM_PANDAS)], "B": [versao(SEM_PANDAS)]}
        ch = cf.conferir_memoria(entrada(nomes(importar=["pandas"])), prompts, INSTR, RG)
        self.assertEqual(ch["1_ambiente"]["resultado"], cf.FALHA)
        self.assertEqual(ch["1_ambiente"]["papeis"]["A"]["resultado"], cf.PASSA)
        self.assertEqual(ch["1_ambiente"]["papeis"]["B"]["resultado"], cf.FALHA)

    def test_papel_falha_se_alguma_versao_falha(self):
        prompts = {"P": [versao(COM_PANDAS, "v1", 3), versao(SEM_PANDAS, "v2", 2)]}
        d = cf.conferir_memoria(entrada(nomes(importar=["pandas"]), role="P"), prompts, INSTR, RG)["1_ambiente"]
        self.assertEqual(d["resultado"], cf.FALHA)
        self.assertEqual((d["papeis"]["P"]["versoes_que_falham"], d["papeis"]["P"]["execucoes_que_falham"]), (1, 2))

    def test_papel_sem_prompt_e_sem_nomes(self):
        ch = cf.conferir_memoria(entrada(nomes(importar=["json"]), role="Q"), {"P": [versao(SEM_PANDAS)]}, INSTR, RG)
        self.assertEqual(ch["1_ambiente"]["resultado"], cf.NV)
        ch = cf.conferir_memoria({**entrada(None), "nomes": None}, {"P": [versao(SEM_PANDAS)]}, INSTR, RG)
        self.assertEqual({ch[c]["resultado"] for c in ("1_ambiente", "2_conflito", "3_repete")}, {cf.NV})

    def test_repete_parcial_se_so_parte_dos_papeis(self):
        prompts = {"A": [versao(SEM_PANDAS)], "B": [versao("def f(x):\n    pass\n")]}
        ch = cf.conferir_memoria(entrada(nomes(nao_importar=["ast"])), prompts, INSTR, RG)
        self.assertEqual(ch["3_repete"]["resultado"], cf.PARCIAL)

    def test_recorrencia_e_uma_causa(self):
        p = {"P": [versao(SEM_PANDAS)]}
        self.assertEqual(cf.conferir_memoria(entrada(nomes(), execucoes=3), p, INSTR, RG)["4_recorrencia"]["resultado"], cf.PASSA)
        self.assertEqual(cf.conferir_memoria(entrada(nomes(), execucoes=5, meses=("2026-07",)), p, INSTR, RG)
                         ["4_recorrencia"]["resultado"], cf.FALHA)
        self.assertEqual(cf.conferir_memoria(entrada(nomes()), p, INSTR, RG)["5_uma_causa"]["resultado"], cf.NV)
        dois = {**entrada(nomes()), "causas": {"repr": "depuração", "globals": "verificação"}}
        self.assertEqual(cf.conferir_memoria(dois, p, INSTR, RG)["5_uma_causa"]["resultado"], cf.FALHA)

    def test_regua_e_instrucoes_do_monitoramento(self):
        mon = {"itens": [{"id": "a", "gatilhos": [{"tipo": "regua", "execucoes": 3, "meses": 2}]},
                         {"id": "b", "instrucao_prompt": "VERIFIQUE", "nomes_induzidos": ["globals"]}]}
        self.assertEqual(cf.regua(mon), RG)
        self.assertEqual([(i, n) for i, _, n in cf.instrucoes(mon)], [("b", {"globals"})])
        with self.assertRaises(SystemExit):
            cf.regua({"itens": [{"gatilhos": [{"tipo": "regua", "execucoes": 3}]},
                                {"gatilhos": [{"tipo": "regua", "execucoes": 5}]}]})

    def test_registro_real_tem_regua_unica_e_a_instrucao(self):
        mon = json.loads((RAIZ / "analysis/registros/monitoramento.json").read_text(encoding="utf-8"))
        self.assertEqual(cf.regua(mon), RG)
        self.assertTrue(any(n == {"globals", "locals", "vars", "eval"} for _, _, n in cf.instrucoes(mon)))


class TestMain(unittest.TestCase):
    def test_saida_e_registrar(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "p.jsonl").write_text(json.dumps({**versao(SEM_PANDAS), "role": "P"}) + "\n", encoding="utf-8")
            (d / "mon.json").write_text(json.dumps({"itens": [{"id": "a", "gatilhos": [{"tipo": "regua", "execucoes": 3,
                                                                                         "meses": 2}]}]}), encoding="utf-8")
            (d / "reg.json").write_text(json.dumps({"itens": [entrada(nomes(importar=["pandas"]), role="P")]}),
                                        encoding="utf-8")
            cf.main(["--prompts", str(d / "p.jsonl"), "--registro", str(d / "reg.json"), "--monitoramento",
                     str(d / "mon.json"), "--saida", str(d / "out.json"), "--registrar"])
            out = json.loads((d / "out.json").read_text(encoding="utf-8"))
            self.assertEqual(out["memorias"][0]["checagens"]["1_ambiente"]["resultado"], cf.FALHA)
            e = json.loads((d / "reg.json").read_text(encoding="utf-8"))["itens"][0]
            self.assertEqual(e["degrau"], 1)
            self.assertEqual(e["conferencia"]["checagens"]["1_ambiente"], cf.FALHA)


class TestEsquema04(unittest.TestCase):
    def test_validar_pendencia_sem_nomes(self):
        esquema = json.loads((RAIZ / "analysis/registros/esquema-memoria.json").read_text(encoding="utf-8"))
        self.assertEqual(esquema["versao"], "0.4")
        mem = {"category": "c", "scope": {"role": None, "tool": None},
               "location": {"total_erros": 1, "casos": [{"step_ref": "a", "fonte_id": "f", "rodada_id": "r",
                                                          "role": "P", "mes": "2026-08"}]},
               "evidence": [], "description": "d", "correction_guidance": "g", "occurrences": {}, "status": "hipotese",
               "validation": {}, "impact": None}
        arq = {"esquema": "0.4", "unidade": "U_x", "base": "base3", "gerado_em": "2026-10-20",
               "parte_especifica": "script:x", "memoria": mem, "origem": {c: {"tipo": "checado", "comando": "x"} for c in mem}}
        erros, pend, _ = vm.validar(esquema, arq)
        self.assertEqual(erros, [])
        self.assertIn("campo `validation.nomes` ausente", pend)
        mem["validation"]["nomes"] = nomes(importar=["json"])
        self.assertNotIn("campo `validation.nomes` ausente", vm.validar(esquema, arq)[1])

    def test_catalogo_copia_nomes(self):
        n = nomes(importar=["json"])
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "memoria.json"
            doc = {"esquema": "0.4", "unidade": "U_x", "id": "U_x.C", "parte": "C", "base": "base3",
                   "gerado_em": "2026-10-20", "parte_especifica": "script:x",
                   "memoria": {"category": "c", "scope": {"role": None, "tool": None}, "description": "d",
                               "correction_guidance": "g", "status": "derived-and-checked",
                               "location": {"casos": [{"rodada_id": "r", "fonte_id": "f"}]},
                               "occurrences": {"erros": 1, "execucoes": 1, "meses": ["2026-08"]},
                               "validation": {"destino": "memória", "nomes": n}}}
            arq.write_text(json.dumps(doc), encoding="utf-8")
            e, _ = cm.entrada(doc, arq)
            self.assertEqual(e["nomes"], n)

    def test_catalogo_real_tem_nomes_em_toda_memoria(self):
        reg = json.loads((RAIZ / "analysis/registros/memorias.json").read_text(encoding="utf-8"))
        for e in reg["itens"]:
            self.assertEqual(set(e["nomes"]), {"importar", "usar", "nao_importar", "nao_usar"}, e["id"])


COM_JSON = {"listas": [{"modulos": ["json", "re"], "meses": ["2026-07"], "erros": 2}], "importados": {}}
FUNCOES = {"funcionam": ["print", "type", "str"], "barradas": ["repr", "dir"]}


class TestAmbienteDoInterpretador(unittest.TestCase):
    """Ajuste 28: a checagem 1 pelo que o interpretador mostrou (--ambiente) e pelas funções testadas (--funcoes)."""

    def test_o_interpretador_vence_o_prompt(self):
        r, motivos = cf.ambiente(nomes(importar=["json"]), LISTA.format("['re']"), COM_JSON)
        self.assertEqual(r, cf.PASSA)
        self.assertIn("a lista veio do interpretador", motivos)

    def test_em_todas_as_listas_do_papel(self):
        duas = {"listas": COM_JSON["listas"] + [{"modulos": ["re"], "meses": ["2026-05"], "erros": 1}]}
        r, motivos = cf.ambiente(nomes(importar=["json"]), SEM_PANDAS, duas)
        self.assertEqual(r, cf.FALHA)
        self.assertIn("importar json: fora da lista do interpretador: fora de 1 de 2 listas do interpretador (2026-05)",
                      motivos)

    def test_sem_lista_um_import_que_rodou_basta(self):
        rodou = {"listas": [], "importados": {"pandas": {"passos": 3, "meses": ["2026-07"]}}}
        self.assertEqual(cf.ambiente(nomes(importar=["pandas"]), SEM_PANDAS, rodou)[0], cf.PASSA)
        self.assertEqual(cf.ambiente(nomes(usar=["pandas.read_json"]), SEM_PANDAS, rodou)[0], cf.PASSA)

    def test_papel_fora_do_ambiente_cai_no_prompt(self):
        r, motivos = cf.ambiente(nomes(importar=["pandas"]), SEM_PANDAS, {})
        self.assertEqual(r, cf.FALHA)
        self.assertIn("importar pandas: fora da lista autorizada", motivos)
        self.assertIn("a lista veio do prompt", motivos)

    def test_proibir_o_que_o_interpretador_aceita(self):
        r, motivos = cf.ambiente(nomes(nao_importar=["json"]), LISTA.format("['re']"), COM_JSON)
        self.assertEqual(r, cf.FALHA)
        self.assertIn("não importar json: o interpretador aceita (numa lista do interpretador)", motivos)
        self.assertEqual(cf.ambiente(nomes(nao_importar=["ast"]), SEM_PANDAS, COM_JSON)[0], cf.PASSA)

    def test_funcoes_testadas_no_interpretador(self):
        self.assertEqual(cf.ambiente(nomes(usar=["print", "type", "str"]), SEM_PANDAS, None, FUNCOES)[0], cf.PASSA)
        r, motivos = cf.ambiente(nomes(usar=["repr"]), SEM_PANDAS, None, FUNCOES)
        self.assertEqual(r, cf.FALHA)
        self.assertIn("usar repr: função do Python barrada no interpretador", motivos)
        self.assertEqual(cf.ambiente(nomes(usar=["len"]), SEM_PANDAS, None, FUNCOES)[0], cf.NV)   # fora da lista
        self.assertEqual(cf.ambiente(nomes(usar=["print"]), SEM_PANDAS)[0], cf.NV)              # sem --funcoes

    def test_papel_so_no_ambiente(self):
        amb = {"papeis": {"Q": COM_JSON}}
        ch = cf.conferir_memoria(entrada(nomes(importar=["json"])), {"P": [versao(SEM_PANDAS)]}, INSTR, RG, amb)
        self.assertEqual(ch["1_ambiente"]["papeis"]["Q"]["resultado"], cf.PASSA)
        self.assertEqual(ch["2_conflito"]["papeis"]["Q"]["resultado"], cf.NV)
        self.assertEqual(ch["1_ambiente"]["papeis"]["P"]["resultado"], cf.PASSA)   # P cai no prompt, que tem json

    def test_sem_ambiente_nada_muda(self):
        e = entrada(nomes(importar=["pandas"]), role="P")
        self.assertEqual(cf.conferir_memoria(e, {"P": [versao(SEM_PANDAS)]}, INSTR, RG)["1_ambiente"]["papeis"]["P"],
                         {"resultado": cf.FALHA, "versoes": 1, "versoes_que_falham": 1, "execucoes_que_falham": 2,
                          "motivos": ["importar pandas: fora da lista autorizada"]})


class TestDecisaoDoPesquisador(unittest.TestCase):
    def decisao(self, sobre, motivos):
        return {"id": "U_x.C", "base": "base3", "checagem": "3_repete", "sobre": sobre, "motivos": motivos,
                "por": "R", "em": "2026-10-21", "motivo": "ruído"}

    def test_vale_com_o_mesmo_resultado_e_motivos_cobertos(self):
        ch = {"resultado": cf.PARCIAL, "papeis": {"P": {"resultado": cf.PARCIAL, "motivos": ["usar print: o prompt já cita"]}}}
        r = cf.aplicar_decisao(ch, self.decisao(cf.PARCIAL, ["usar print: o prompt já cita"]))
        self.assertEqual((r["resultado"], r["resultado_do_script"]), (cf.DECIDIDO, cf.PARCIAL))

    def test_nao_vale_se_o_resultado_ou_os_motivos_mudam(self):
        d = self.decisao(cf.PARCIAL, ["usar print: o prompt já cita"])
        falha = {"resultado": cf.FALHA, "papeis": {"P": {"resultado": cf.FALHA, "motivos": ["usar print: o prompt já cita"]}}}
        self.assertEqual(cf.aplicar_decisao(falha, d)["resultado"], cf.FALHA)
        self.assertIn("o script deu 'falha'", cf.aplicar_decisao(falha, d)["decisao_nao_vale"])
        novo = {"resultado": cf.PARCIAL, "papeis": {"P": {"resultado": cf.PARCIAL, "motivos": ["usar type: o prompt já cita"]}}}
        self.assertIn("motivos novos: usar type", cf.aplicar_decisao(novo, d)["decisao_nao_vale"])

    def test_decidir_e_o_degrau(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "p.jsonl").write_text(json.dumps(versao(SEM_PANDAS)) + "\n", encoding="utf-8")
            (d / "mon.json").write_text(json.dumps({"itens": [{"id": "a", "gatilhos": [{"tipo": "regua", "execucoes": 3,
                                                                                         "meses": 2}]}]}), encoding="utf-8")
            (d / "reg.json").write_text(json.dumps({"itens": [entrada(nomes(importar=["json"]), role="P")]}),
                                        encoding="utf-8")
            base = ["--prompts", str(d / "p.jsonl"), "--registro", str(d / "reg.json"), "--monitoramento",
                    str(d / "mon.json"), "--decisoes", str(d / "dec.json")]
            cf.main(base + ["--saida", str(d / "antes.json")])
            antes = json.loads((d / "antes.json").read_text(encoding="utf-8"))["memorias"][0]
            self.assertEqual((antes["degrau"], antes["checagens"]["5_uma_causa"]["resultado"]), (1, cf.NV))
            cf.main(base + ["--decidir", "U_x.C", "5_uma_causa", "--motivo", "a parte tem um mecanismo só", "--por", "R"])
            dec = json.loads((d / "dec.json").read_text(encoding="utf-8"))["itens"]
            self.assertEqual((len(dec), dec[0]["sobre"], dec[0]["por"]), (1, cf.NV, "R"))
            cf.main(base + ["--saida", str(d / "depois.json"), "--registrar"])
            depois = json.loads((d / "depois.json").read_text(encoding="utf-8"))["memorias"][0]
            self.assertEqual(depois["checagens"]["5_uma_causa"]["resultado"], cf.DECIDIDO)
            self.assertEqual(depois["degrau"], 2)
            self.assertEqual(json.loads((d / "reg.json").read_text(encoding="utf-8"))["itens"][0]["degrau"], 2)

    def test_decidir_o_que_ja_passa_nao_registra(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "p.jsonl").write_text(json.dumps(versao(SEM_PANDAS)) + "\n", encoding="utf-8")
            (d / "mon.json").write_text(json.dumps({"itens": [{"id": "a", "gatilhos": [{"tipo": "regua"}]}]}),
                                        encoding="utf-8")
            (d / "reg.json").write_text(json.dumps({"itens": [entrada(nomes(importar=["json"]), role="P")]}),
                                        encoding="utf-8")
            with self.assertRaises(SystemExit):
                cf.main(["--prompts", str(d / "p.jsonl"), "--registro", str(d / "reg.json"), "--monitoramento",
                         str(d / "mon.json"), "--decisoes", str(d / "dec.json"), "--decidir", "U_x.C", "1_ambiente",
                         "--motivo", "x"])
            self.assertFalse((d / "dec.json").exists())


class TestExtrairAmbiente(unittest.TestCase):
    def test_listas_da_mensagem_e_imports_que_rodaram(self):
        S = pd.DataFrame([
            {"role": "P", "mes": "2026-07", "code": "import ast",
             "err_msg": "Code execution failed due to: InterpreterError: Import of ast is not allowed. "
                        "Authorized imports are: ['re', 'json']"},
            {"role": "P", "mes": "2026-08", "code": "import json\nfrom datetime.x import y\nimport a.b as c, d", "err_msg": ""},
            {"role": "P", "mes": "2026-08", "code": "import pandas as pd", "err_msg": "outro erro"},   # não rodou
            {"role": "Q", "mes": "2026-08", "code": "x = 1", "err_msg": ""},                         # nada a dizer
        ])
        amb = ea.ambiente(S)
        self.assertEqual(list(amb), ["P"])
        self.assertEqual(amb["P"]["listas"], [{"modulos": ["json", "re"], "meses": ["2026-07"], "erros": 1}])
        self.assertEqual(sorted(amb["P"]["importados"]), ["a", "d", "datetime", "json"])

    def test_tabela_da_mineracao(self):
        linhas = [{"lista_autorizada": "json, re", "erros": "5", "papeis": "P, Q", "meses": "2026-07, 2026-08"}]
        amb = am.ambiente(linhas)
        self.assertEqual(sorted(amb), ["P", "Q"])
        self.assertEqual(amb["Q"]["listas"][0], {"modulos": ["json", "re"], "meses": ["2026-07", "2026-08"], "erros": 5})

    def test_registro_das_funcoes(self):
        f = json.loads((RAIZ / "analysis/registros/funcoes_sandbox.json").read_text(encoding="utf-8"))
        self.assertTrue({"print", "type", "str"} <= set(f["funcionam"]))
        self.assertTrue({"repr", "dir", "exec", "__import__", "bytes", "open", "hash"} <= set(f["barradas"]))
        self.assertFalse(set(f["funcionam"]) & set(f["barradas"]))


class TestExtrairPrompts(unittest.TestCase):
    def test_uma_linha_por_papel_e_versao(self):
        S = pd.DataFrame([
            {"exec_id": "e1", "agente": 1, "role": "P", "idx": 0, "mes": "2026-07", "sysprompt": SEM_PANDAS},
            {"exec_id": "e1", "agente": 1, "role": "P", "idx": 1, "mes": "2026-07", "sysprompt": SEM_PANDAS},
            {"exec_id": "e2", "agente": 1, "role": "P", "idx": 0, "mes": "2026-08", "sysprompt": SEM_PANDAS},
            {"exec_id": "e3", "agente": 1, "role": "P", "idx": 0, "mes": "2026-08", "sysprompt": COM_PANDAS},
            {"exec_id": "e4", "agente": 1, "role": "Q", "idx": 0, "mes": "2026-08", "sysprompt": ""},
        ])
        v = ep.versoes(S)
        self.assertEqual(len(v), 2)
        sem = [r for r in v if r["prompt"] == SEM_PANDAS][0]
        self.assertEqual((sem["role"], sem["execucoes"], sem["meses"]), ("P", 2, ["2026-07", "2026-08"]))


if __name__ == "__main__":
    unittest.main()
