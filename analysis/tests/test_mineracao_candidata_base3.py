"""Mineração de candidata na base 3 (procedimento 06): o script do inventário do sandbox, a auditoria independente e o
minerar.py. Sintético: mensagens montadas aqui, nenhum caso real."""
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

RAIZ = Path(__file__).resolve().parents[2]
B3 = RAIZ / "analysis/2026-10-trace-law-flow-third"


def carregar(nome, arq):
    spec = spec_from_file_location(nome, arq)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# o script da lição: o aprovado (pipeline/especificas/) ou a proposta (propostas/U_sandbox/), como o minerar.py acha
_SB = next(p for p in (B3 / "pipeline/especificas/mineracao_U_sandbox.py", B3 / "propostas/U_sandbox/mineracao_U_sandbox.py")
           if p.exists())
sb = carregar("mineracao_U_sandbox", _SB)
aud = carregar("audit_candidata_base3", B3 / "audit/scripts/audit_candidata_base3.py")
vm = carregar("validar_memoria", RAIZ / ".claude/skills/mineracao-candidata/scripts/validar_memoria.py")
ESQUEMA = json.loads((RAIZ / "analysis/registros/esquema-memoria.json").read_text(encoding="utf-8"))

AUT = "Authorized imports are: ['re', 'math', 'json']"
MSGS = [  # (papel, mês, mensagem)
    ("PapelA", "2026-01", "Code execution failed at line 'x = repr(y)' due to: InterpreterError: Forbidden function evaluation: 'repr' is not among the explicitly allowed tools"),
    ("PapelA", "2026-02", "Code execution failed at line 'x = repr(y)' due to: InterpreterError: Forbidden function evaluation: 'repr' is not among the explicitly allowed tools"),
    ("PapelB", "2026-01", f"Code execution failed at line 'import ast' due to: InterpreterError: Import of ast is not allowed. {AUT}"),
    ("PapelB", "2026-02", "Code execution failed at line 'd = json.loads(s)' due to: InterpreterError: The variable `json` is not defined."),
    ("PapelC", "2026-03", "Code execution failed at line 'import openpyxl' due to: ModuleNotFoundError: No module named 'openpyxl'"),
    ("PapelC", "2026-03", "Code execution failed at line 'n = f.__name__' due to: InterpreterError: Forbidden access to dunder attribute: __name__"),
]


def casos_e_mensagens(msgs=MSGS, estado="sem_corte_sql"):
    casos = pd.DataFrame([{"exec_id": f"e{i}", "agente": 1, "role": p, "step_pos": 3, "step_ref": f"r{i}", "mes": m}
                          for i, (p, m, _) in enumerate(msgs)])
    mensagens = pd.DataFrame([{"step_ref": f"r{i}", "mensagem": t, "estado": estado} for i, (_, _, t) in enumerate(msgs)])
    return casos, mensagens


class TestRegraDoSandbox(unittest.TestCase):
    def test_cada_tipo(self):
        self.assertEqual([sb.extrair(t) for _, _, t in MSGS],
                         [("funcao_proibida", "repr"), ("funcao_proibida", "repr"), ("import_bloqueado", "ast"),
                          ("modulo_sem_import", "json"), ("modulo_ausente", "openpyxl"), ("atributo_dunder", "__name__")])

    def test_so_o_ultimo_trecho(self):
        # a linha de código do agente repete o padrão; o que vale é a frase do interpretador
        msg = "Code execution failed at line 'print(\"Import of os is not allowed\")' due to: InterpreterError: Import of ast is not allowed."
        self.assertEqual(sb.extrair(msg), ("import_bloqueado", "ast"))

    def test_sem_nome(self):
        self.assertEqual(sb.extrair("x due to: ValueError: outra coisa"), ("sem_nome", "ValueError"))

    def test_lista_autorizada_em_ordem(self):
        self.assertEqual(sb.lista_autorizada(MSGS[2][2]), "json, math, re")

    def test_mensagem_nao_integra_conta_sem_nome(self):
        t = sb.medir(*casos_e_mensagens(estado="possivelmente_cortado"))
        self.assertTrue(t["erros_lidos"].tipo.eq("sem_nome").all())
        self.assertFalse(sb.confianca(t)["passa"])

    def test_confianca_e_limiar(self):
        t = sb.medir(*casos_e_mensagens())
        c = sb.confianca(t)
        self.assertEqual((c["com_nome"], c["erros"], c["passa"]), (6, 6, True))
        msgs = MSGS + [("PapelA", "2026-01", "x due to: ValueError: nada")]
        self.assertFalse(sb.confianca(sb.medir(*casos_e_mensagens(msgs)))["passa"])  # 6/7 < 95%

    def test_destino(self):
        d = sb.destino(sb.medir(*casos_e_mensagens()))
        self.assertEqual(d["listas_autorizadas_distintas"], 1)
        self.assertTrue(d["lista_unica_em_todos_papeis_e_meses"])
        self.assertEqual(d["erros_que_repetem_o_nome_na_mesma_execucao_e_papel"], 0)

    def test_repeticao_e_pelo_nome_nao_pelo_tipo(self):
        msgs = [("PapelA", "2026-01", "x due to: InterpreterError: The variable `json` is not defined."),
                ("PapelA", "2026-01", "x due to: InterpreterError: Import of json is not allowed.")]
        casos, mensagens = casos_e_mensagens(msgs)
        casos["exec_id"] = "e0"   # os dois na mesma execução e papel
        casos["step_pos"] = [3, 5]
        d = sb.destino(sb.medir(casos, mensagens))
        self.assertEqual(d["erros_que_repetem_o_nome_na_mesma_execucao_e_papel"], 1)

    def test_partes(self):
        self.assertEqual(sb.parte_de("modulo_sem_import", "json"), "C")
        self.assertEqual(sb.parte_de("funcao_proibida", "repr"), "E")
        self.assertEqual(sb.parte_de("atributo_dunder", "__name__"), "E")
        self.assertEqual(sb.parte_de("import_bloqueado", "get_document_text"), "B")
        self.assertEqual(sb.parte_de("import_bloqueado", "mcp_client.tools"), "B")
        self.assertEqual(sb.parte_de("modulo_ausente", "python_interpreter"), "B")
        self.assertEqual(sb.parte_de("import_bloqueado", "ast"), "D")
        self.assertIsNone(sb.parte_de("sem_nome", "ValueError"))
        self.assertEqual(sb.memoria_id("B", "OBFCivel"), "U_sandbox.B.OBFCivel")
        self.assertEqual(sb.memoria_id("C", "OBFCivel"), "U_sandbox.C")
        P = sb.medir(*casos_e_mensagens())["partes"].set_index("memoria_id").erros.to_dict()
        self.assertEqual(P, {"U_sandbox.C": 1, "U_sandbox.D.PapelB": 1, "U_sandbox.D.PapelC": 1, "U_sandbox.E": 3})

    def test_memorias_validas_no_esquema(self):
        t = sb.medir(*casos_e_mensagens())
        perfil = {"erros_observaveis": 6, "ocorrencias_condicionais": 6, "execucoes": 6}
        enc = [{"medida": "populacao.erros", "mineracao": 6, "auditoria": 6, "igual": True}]
        lista = sb.memorias(perfil, t, sb.confianca(t), sb.destino(t), {"fonte_id": "f" * 64, "rodada_id": "r" * 64}, enc)
        por_id = {m["id"]: m["memoria"] for m in lista}
        self.assertEqual(sorted(por_id), ["U_sandbox.C", "U_sandbox.D.PapelB", "U_sandbox.D.PapelC", "U_sandbox.E"])
        for item in lista:
            doc = {"esquema": ESQUEMA["versao"], "unidade": "U_sandbox", "id": item["id"], "parte": item["parte"],
                   "base": "base3", "gerado_em": "2026-10-19", "parte_especifica": "script:mineracao_U_sandbox",
                   "memoria": item["memoria"], "origem": {c: {"tipo": "checado", "comando": "x"} for c in item["memoria"]}}
            self.assertEqual(vm.validar(ESQUEMA, doc)[0], [], item["id"])
        self.assertEqual(por_id["U_sandbox.C"]["correction_guidance"], "Importe antes de usar: json.")
        self.assertIsNone(por_id["U_sandbox.C"]["scope"]["role"])
        self.assertEqual(por_id["U_sandbox.D.PapelB"]["scope"]["role"], "PapelB")
        self.assertEqual(por_id["U_sandbox.D.PapelB"]["correction_guidance"],
                         "Não importe: ast; imports autorizados neste papel: json, math, re.")
        self.assertEqual(por_id["U_sandbox.D.PapelC"]["correction_guidance"], "Não existe no ambiente: openpyxl.")
        self.assertEqual(por_id["U_sandbox.E"]["correction_guidance"], "Não chame: repr; Não acesse: __name__. " + sb.GUIA_E)
        self.assertEqual(por_id["U_sandbox.E"]["validation"]["destino"], "memória")
        self.assertEqual(por_id["U_sandbox.C"]["validation"]["destino"], "memória")
        self.assertEqual(por_id["U_sandbox.E"]["location"]["total_erros"], 3)
        self.assertTrue(all(m["status"] == "derived-and-checked" for m in por_id.values()))
        enc[0]["igual"] = False   # o encontro não fecha: o status cai em todas
        lista = sb.memorias(perfil, t, sb.confianca(t), sb.destino(t), {"fonte_id": "f", "rodada_id": "r"}, enc)
        self.assertTrue(all(m["memoria"]["status"] == "parcial" for m in lista))

    def test_ferramenta_por_papel(self):
        msgs = [("OBFCivel", "2026-07", "x due to: InterpreterError: Import of get_document_text is not allowed."),
                ("OBFCivel", "2026-07", "x due to: InterpreterError: Import from tools is not allowed.")]
        t = sb.medir(*casos_e_mensagens(msgs))
        m = sb.memorias({"erros_observaveis": 2}, t, sb.confianca(t), sb.destino(t), {"fonte_id": "f", "rodada_id": "r"}, [])
        self.assertEqual([x["id"] for x in m], ["U_sandbox.B.OBFCivel"])
        self.assertIn("chame-as direto, sem import", m[0]["memoria"]["correction_guidance"])


class TestAuditoria(unittest.TestCase):
    def test_populacao_em_prosa(self):
        self.assertTrue(aud.populacao_sandbox("Forbidden function evaluation: 'repr' is not"))
        self.assertFalse(aud.populacao_sandbox("Forbidden function evaluation: 'minha_funcao' is not"))  # nome inventado
        self.assertTrue(aud.populacao_sandbox("The variable `json` is not defined"))
        self.assertFalse(aud.populacao_sandbox("The variable `resultado` is not defined"))
        self.assertFalse(aud.populacao_sandbox("SyntaxError ... Import of ast is not allowed"))  # o pipeline decide antes
        # emenda 3 (Ajuste 21)
        m = "x failed at line 'if 'p' not in globals():' due to: InterpreterError: Forbidden function evaluation: 'globals' is not"
        self.assertFalse(aud.populacao_sandbox(m, "if 'p' not in globals():\n    p = get_doc(n)"))
        self.assertTrue(aud.populacao_sandbox(m, "if 'p' not in globals():\n    p = 'padrão'"))
        # emenda 2: a função proibida junto do timeout de ferramenta é do timeout (o 1 erro da base 3)
        self.assertFalse(aud.populacao_sandbox("TimeoutError ... Forbidden function evaluation: 'repr' is not"))
        self.assertFalse(aud.populacao_sandbox("Error in code parsing: regex pattern ... Import of ast is not allowed"))

    def test_auditoria_e_script_concordam(self):
        rows = [{"cod_idef_exeo": f"e{i}", "cod_idef_aget": 1, "papel": p, "step_pos": 3, "mes_execucao": m,
                 "structured_error": 1, "error_type": "InterpreterError", "error_message": t, "error_code_action": ""}
                for i, (p, m, t) in enumerate(MSGS)]
        rows.append({"cod_idef_exeo": "e9", "cod_idef_aget": 1, "papel": "PapelA", "step_pos": 4, "mes_execucao": "2026-01",
                     "structured_error": 1, "error_type": "KeyError", "error_message": "Could not index x",
                     "error_code_action": ""})
        # emenda 3 (Ajuste 21): verifica e cria a variável por uma chamada → fora do sandbox
        rows.append({"cod_idef_exeo": "e8", "cod_idef_aget": 1, "papel": "PapelC", "step_pos": 2, "mes_execucao": "2026-07",
                     "structured_error": 1, "error_type": "InterpreterError",
                     "error_message": "Code execution failed at line 'if 'p' not in globals():' due to: InterpreterError: "
                                      "Forbidden function evaluation: 'globals' is not among the explicitly allowed tools",
                     "error_code_action": "if 'p' not in globals():\n    p = get_doc(n)"})
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "fonte.parquet"
            pq.write_table(pa.Table.from_pylist(rows), f)
            a = aud.auditar("U_sandbox", str(f))
        s = sb.para_encontro(sb.medir(*casos_e_mensagens()))
        for bloco in ("inventario", "listas_autorizadas", "partes"):
            self.assertEqual(a[bloco], s[bloco], bloco)
        self.assertEqual(a["populacao"]["chaves"], [["e0", "1", "PapelA", 3], ["e1", "1", "PapelA", 3],
                                                    ["e2", "1", "PapelB", 3], ["e3", "1", "PapelB", 3],
                                                    ["e4", "1", "PapelC", 3], ["e5", "1", "PapelC", 3]])
        self.assertEqual(s["populacao"]["chaves"], a["populacao"]["chaves"])


class TestMinerar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(B3 / "pipeline"))
        cls.mn = carregar("minerar", B3 / "pipeline/especificas/minerar.py")

    def test_funil_da_base3(self):
        self.assertEqual(self.mn.linha_do_funil("U_sandbox"), "script:mineracao_U_sandbox")
        self.assertEqual(self.mn.linha_do_funil("U_tipo_retorno"), "investigação:candidata")
        with self.assertRaises(self.mn.Parada):
            self.mn.linha_do_funil("U_nao_existe")

    def test_filho_com_saida_fora_do_utf8_nao_quebra(self):
        # no Windows o filho imprime em cp1252: o "ú" de "Itaú" vira o byte 0xfa (b3, passo 2 na máquina da base)
        rc, out = self.mn._rodar([sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'Ita\\xfa'); sys.exit(2)"])
        self.assertEqual(rc, 2)
        self.assertTrue(out.startswith("Ita"))

    def test_skills_em_claude_ou_github(self):
        pastas = self.mn.PASTAS_SKILLS
        with tempfile.TemporaryDirectory() as d:
            alvo = Path(d) / ".github" / "skills" / "mineracao-base" / "scripts"
            alvo.mkdir(parents=True)
            (alvo / "so_no_github.py").write_text("")
            self.mn.PASTAS_SKILLS = [Path(d) / ".claude" / "skills", Path(d) / ".github" / "skills"]
            try:
                self.assertEqual(self.mn.script_da_skill("mineracao-base", "so_no_github.py"), alvo / "so_no_github.py")
                with self.assertRaises(self.mn.Parada):
                    self.mn.script_da_skill("mineracao-base", "nao_existe.py")
            finally:
                self.mn.PASTAS_SKILLS = pastas

    def test_rodada_inexistente_para(self):
        with self.assertRaises(self.mn.Parada):
            self.mn.pasta_rodada("nao_existe_0000")

    ENSAIO = B3 / "pipeline/resultados/ensaio_base1"

    @unittest.skipUnless((ENSAIO / "rodada" / "manifesto.json").exists(), "sem a rodada de ensaio da base 1")
    def test_ponta_a_ponta_no_ensaio_da_base1(self):
        with tempfile.TemporaryDirectory() as d:
            m = self.mn.Mineracao("U_sandbox", str(self.ENSAIO / "rodada"), str(self.ENSAIO / "fonte_base1_v1.parquet"), d)
            from contextlib import redirect_stdout
            import io
            with redirect_stdout(io.StringIO()):
                rc = m.rodar()
            if rc and "outro código" in str(m.registro.get(1, "")):
                self.skipTest("a rodada de ensaio é de outro código: refaça com validacao/rodada_base1.py")
            self.assertEqual(rc, 0, m.registro)
            self.assertTrue((Path(d) / "memoria_U_sandbox.C_base3.json").exists())
            cat = json.loads((Path(d) / "catalogo_U_sandbox_base3.json").read_text(encoding="utf-8"))
            self.assertIn("U_sandbox.C", [e["id"] for e in cat["entradas"]])
            self.assertIn("U_sandbox.E", [e["id"] for e in cat["entradas"]])   # emenda 6: E é memória
            self.assertTrue(json.loads((Path(d) / "manifesto_mineracao.json").read_text())["artefatos"])

    @unittest.skipUnless((ENSAIO / "rodada" / "manifesto.json").exists(), "sem a rodada de ensaio da base 1")
    def test_divergencia_e_explicada(self):
        with tempfile.TemporaryDirectory() as d:
            m = self.mn.Mineracao("U_sandbox", str(self.ENSAIO / "rodada"), str(self.ENSAIO / "fonte_base1_v1.parquet"), d)
            from contextlib import redirect_stdout
            import io
            with redirect_stdout(io.StringIO()):
                if m.rodar() and "outro código" in str(m.registro.get(1, "")):
                    self.skipTest("a rodada de ensaio é de outro código")
            aud = json.loads((Path(d) / "auditoria.json").read_text(encoding="utf-8"))
            mod, _ = m.modulo()
            scr = mod.para_encontro(m.tabelas())
            aud["linhas"] = aud["linhas"][1:]   # um erro que só a mineração contou
            m.diagnostico(aud, scr)
            G = pd.read_csv(Path(d) / "passo7_divergencia.csv")
            self.assertEqual(G.groupby("lado").erros.sum().to_dict(), {"só na mineração": 1})


if __name__ == "__main__":
    unittest.main()
