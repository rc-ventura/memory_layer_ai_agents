"""`validacao/contar_recorrencia_causa_residuo.py` (base 3): as famílias do balde "causa não identificada" e a régua de
recorrência (≥ 3 execuções e ≥ 2 meses). Fixtures sintéticas."""
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

import pandas as pd

ARQ = (Path(__file__).resolve().parents[1] / "2026-10-trace-law-flow-third" / "pipeline" / "validacao"
       / "contar_recorrencia_causa_residuo.py")
spec = importlib.util.spec_from_file_location("recorrencia_causa", ARQ)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def msg(exc, linha="x = f(1)"):
    return f"Code execution failed at line '{linha}' due to: {exc}"


# uma mensagem real-ish por família (o código da linha traz palavras que NÃO devem decidir a família)
POR_FAMILIA = {
    "sintaxe_continuacao_barra": "Code parsing failed on line 3 due to: SyntaxError\n  x = \\\n ^\nError: unexpected "
                                 "character after line continuation character (<unknown>, line 3)",
    "sintaxe_fstring": "Code parsing failed on line 2 due to: SyntaxError: f-string expression part cannot include a "
                       "backslash",
    "sintaxe_invalid_syntax": "Code parsing failed on line 1 due to: SyntaxError\n  texto: x\n ^\nError: invalid syntax",
    "sintaxe_outra": "Code parsing failed on line 4 due to: IndentationError: unexpected indent",
    "indexacao_do_interpretador": msg("InterpreterError: Could not index [] with 'x': IndexError: list index out of range"),
    "round_ou_formato_em_texto": msg("TypeError: type str doesn't define __round__ method", "round(x, 2)"),
    "numero_invalido_da_ferramenta": msg("ValueError: Número inválido: deve conter 20 dígitos numéricos"),
    "json_nao_serializavel": msg("TypeError: Object of type DataFrame is not JSON serializable", "json.dumps(df)"),
    "json_ausente_no_retorno": msg("ValueError: Nenhum objeto JSON encontrado no texto."),
    "dataframe_construtor": msg("ValueError: DataFrame constructor not properly called!", "pd.DataFrame('x')"),
    "data_ou_hora": msg("TypeError: <class 'list'> is not convertible to datetime"),
    "pandas_outro": msg("ValueError: Index contains duplicate entries, cannot reshape"),
    # o código da linha cita DataFrame e datetime, mas a exceção é a soma entre tipos
    "soma_ou_concatenacao_entre_tipos": msg("TypeError: unsupported operand type(s) for +: 'int' and 'str'",
                                            "df = pd.DataFrame(datetime.now() + 1)"),
    "comparacao_entre_tipos": msg("TypeError: '<' not supported between instances of 'str' and 'int'"),
    "objeto_nao_chamavel": msg("TypeError: 'dict' object is not callable"),
    "indice_de_lista_com_texto": msg("TypeError: list indices must be integers or slices, not str"),
    "chave_ausente": msg("KeyError: 'valor'"),
    "tipo_outro": msg("TypeError: unhashable type: 'list'"),
    "valor_outro": msg("ValueError: cannot convert float NaN to integer"),
    "outro": "AgentExecutionError",
}


def caso(i, mensagem, padrao, mes="2026-07", role="P1", unidade=M.BALDE, execucao=None):
    return {"exec_id": execucao or f"e{i}", "agente": "1", "role": role, "mes": mes, "unidade": unidade,
            "padrao": padrao, "tok_tot": 10, "idx": 1, "mensagem": mensagem}


class TestFamilia(unittest.TestCase):
    def test_cada_mensagem_cai_na_sua_familia(self):
        for esperada, m in POR_FAMILIA.items():
            self.assertEqual(M.familia(m), esperada, esperada)

    def test_so_vale_o_trecho_depois_do_ultimo_due_to(self):
        self.assertEqual(M.trecho("Code execution failed at line 'a due to: b' due to: KeyError: 'x'"), " KeyError: 'x'")
        self.assertEqual(M.familia("Code execution failed at line 'x = json.loads(s)' due to: KeyError: 'k'"),
                         "chave_ausente")

    def test_mais_especifica_antes_da_geral(self):
        # `Could not index ... TypeError: list indices must be integers` é a indexação do interpretador
        self.assertEqual(M.familia(msg("InterpreterError: Could not index [] with 'x': TypeError: list indices must "
                                       "be integers or slices, not str")), "indexacao_do_interpretador")
        # `DataFrame ... not JSON serializable` é o JSON, não o pandas
        self.assertEqual(M.familia(msg("TypeError: Object of type Timestamp is not JSON serializable")),
                         "json_nao_serializavel")

    def test_todas_as_familias_tem_exemplo(self):
        self.assertEqual({n for n, _ in M.FAMILIAS} | {"outro"}, set(POR_FAMILIA))


def populacao():
    L = []
    # sintaxe invalid syntax: 5 execuções em 3 meses, 1 padrão → passa sozinho
    for i, mes in enumerate(["2026-02", "2026-02", "2026-05", "2026-05", "2026-07"]):
        L.append(caso(f"is{i}", POR_FAMILIA["sintaxe_invalid_syntax"], "SyntaxError: invalid syntax", mes))
    # soma entre tipos: 3 padrões diferentes, 3 execuções em 2 meses → passa só somando
    for i, (pad, mes) in enumerate([("TypeError: unsupported operand type(s) for +: <q> and <q>", "2026-02"),
                                    ("TypeError: unsupported operand type(s) for -: <q> and <q>", "2026-05"),
                                    ("TypeError: can only concatenate str (not <q>) to str", "2026-05")]):
        L.append(caso(f"so{i}", POR_FAMILIA["soma_ou_concatenacao_entre_tipos"], pad, mes))
    # chave ausente: 3 execuções, 1 mês → não passa
    for i in range(3):
        L.append(caso(f"ka{i}", POR_FAMILIA["chave_ausente"], "KeyError: <q>", "2026-08"))
    # sem nome → outro
    L.append(caso("ou0", "AgentExecutionError", "sem nome de exceção: AgentExecutionError"))
    # outro balde: não entra
    L.append(caso("fora", POR_FAMILIA["chave_ausente"], "KeyError: <q>", unidade="X_sintoma_nao_reconhecido"))
    return pd.DataFrame(L)


class TestRegua(unittest.TestCase):
    def setUp(self):
        self.S = M.contar(populacao())
        self.T = M.tabela(self.S).set_index("familia")

    def test_so_o_balde_da_causa_e_a_soma_fecha(self):
        self.assertNotIn("efora", set(self.S.exec_id))
        self.assertEqual(int(self.T.erros.sum()), len(self.S))

    def test_passa_sozinho_quando_um_padrao_recorre(self):
        r = self.T.loc["sintaxe_invalid_syntax"]
        self.assertTrue(r.passa and r.passa_sozinho)
        self.assertEqual((r.padroes, r.padroes_que_passam, r.padrao_dominante_pct), (1, 1, 100.0))
        self.assertEqual(r.motivo, "passa a régua")

    def test_passa_so_somando_e_diz_o_motivo(self):
        r = self.T.loc["soma_ou_concatenacao_entre_tipos"]
        self.assertTrue(r.passa)
        self.assertFalse(r.passa_sozinho)
        self.assertEqual((r.padroes, r.padroes_que_passam), (3, 0))
        self.assertIn("passa só somando padrões", r.motivo)

    def test_um_mes_so_nao_passa(self):
        r = self.T.loc["chave_ausente"]
        self.assertFalse(r.passa)
        self.assertIn("1 mês", r.motivo)

    def test_a_chave_sem_impressao_digital_nunca_passa_sozinha(self):
        r = self.T.loc["outro"]
        self.assertFalse(r.passa_sozinho)

    def test_os_que_passam_sozinhos_vem_primeiro(self):
        self.assertEqual(M.tabela(self.S).familia.iloc[0], "sintaxe_invalid_syntax")

    def test_padroes_com_a_familia(self):
        P = M.tabela_padroes(self.S).set_index("padrao")
        self.assertEqual(P.loc["SyntaxError: invalid syntax", "familia"], "sintaxe_invalid_syntax")
        self.assertTrue(P.loc["SyntaxError: invalid syntax", "passa_na_recorrencia"])
        self.assertFalse(P.loc["KeyError: <q>", "passa_na_recorrencia"])


def fonte(linhas):
    """A fonte sintética: um passo por erro, com o passo seguinte (número e mensagem de erro)."""
    return pd.DataFrame([{"cod_idef_exeo": f"e{i}", "cod_idef_aget": "1", "papel": "P1", "step_pos": 1,
                          "cod_vers_aget": "v", "mes_execucao": "2026-07", "error_code_action": None,
                          "prev_code_action": None, "next_step_number": n, "next_code_action": None,
                          "next_error_message": e, "next2_step_number": None, "next2_code_action": None,
                          "next2_error_message": None} for i, (n, e) in enumerate(linhas)])


class TestDepois(unittest.TestCase):
    def test_o_que_veio_no_passo_seguinte(self):
        casos = pd.DataFrame([caso(i, POR_FAMILIA["chave_ausente"], "KeyError: <q>") for i in range(5)])
        S = M.contar(casos)
        F = fonte([(None, None),                                              # sem passo
                   (2, None),                                                 # sem erro
                   (2, msg("KeyError: 'outra'")),                             # a mesma família de novo
                   (2, msg("ValueError: cannot convert float NaN to integer")),  # outra família
                   (2, "")])                                                  # mensagem vazia: sem erro
        dep, faltam = M.depois(S, F)
        self.assertEqual(list(dep), ["sem_passo", "sem_erro", "mesma_familia", "outra_familia", "sem_erro"])
        self.assertEqual(faltam, 0)

    def test_erro_sem_linha_na_fonte(self):
        S = M.contar(pd.DataFrame([caso(i, POR_FAMILIA["chave_ausente"], "KeyError: <q>") for i in range(2)]))
        dep, faltam = M.depois(S, fonte([(2, None)]))
        self.assertEqual((list(dep), faltam), (["sem_erro", "sem_passo"], 1))


class TestLinhaDeComando(unittest.TestCase):
    def test_grava_as_duas_tabelas_e_imprime_os_que_passam(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = Path(tmp) / "casos.csv"
            populacao().to_csv(c, index=False)
            saida = io.StringIO()
            with contextlib.redirect_stdout(saida):
                self.assertEqual(M.main(["--casos", str(c)]), 0)
            T = pd.read_csv(Path(tmp) / "recorrencia_causa.csv")
            P = pd.read_csv(Path(tmp) / "padroes_causa.csv")
        txt = saida.getvalue()
        self.assertEqual(list(T.columns), M.COLUNAS)
        self.assertNotIn("mensagem", list(T.columns) + list(P.columns))
        self.assertIn("PASSA SOZINHO", txt)
        self.assertIn("passam com um padrão que recorre sozinho: sintaxe_invalid_syntax", txt)
        self.assertIn("atenção: há erros em `outro`", txt)
        self.assertIn("1 · sem nome de exceção: AgentExecutionError", txt)

    def test_com_a_fonte_mostra_o_passo_seguinte(self):
        with tempfile.TemporaryDirectory() as tmp:
            c, a = Path(tmp) / "casos.csv", Path(tmp) / "fonte.parquet"
            populacao().to_csv(c, index=False)
            # a fonte tem os erros da causa pela chave (e{i} do `caso`); os ids do fixture são strings "eis0"…
            linhas = [{"cod_idef_exeo": e, "cod_idef_aget": "1", "papel": "P1", "step_pos": 1, "cod_vers_aget": "v",
                       "mes_execucao": "2026-07", "error_code_action": None, "prev_code_action": None,
                       "next_step_number": 2, "next_code_action": None, "next_error_message": None,
                       "next2_step_number": None, "next2_code_action": None, "next2_error_message": None}
                      for e in populacao().exec_id]
            pd.DataFrame(linhas).to_parquet(a)
            saida = io.StringIO()
            with contextlib.redirect_stdout(saida):
                self.assertEqual(M.main(["--casos", str(c), "--fonte", str(a)]), 0)
        self.assertIn("passo seguinte: {'sem_erro': 5}", saida.getvalue())

    def test_sem_coluna_ou_sem_erro_do_balde_para_com_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = Path(tmp) / "casos.csv"
            populacao().drop(columns=["mensagem"]).to_csv(c, index=False)
            self.assertEqual(M.main(["--casos", str(c)]), 1)
            p = populacao()
            p[p.unidade.eq(M.BALDE)].assign(unidade="X_sintoma_nao_reconhecido").to_csv(c, index=False)
            self.assertEqual(M.main(["--casos", str(c)]), 1)


if __name__ == "__main__":
    unittest.main()
