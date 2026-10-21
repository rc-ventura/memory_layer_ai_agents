"""Base 3: a parte E do inventário do sandbox (funções e atributos proibidos) — para que o agente usa a função barrada?

Depois do Ajuste 21, a parte E tem 523 erros (dossiê do sandbox, `propostas/U_sandbox/dossie_base3.md`, §2b), ainda
concentrada no ContestacaoCivel: `__name__` 172 de 182, `eval` 46 de 49, `repr` 54 de 98, e o resíduo de `globals`. A
pergunta (b3 #12, decisão de 19/10): ela também vem do prompt desse papel, como a verificação de existência (Ajuste 21)?
Se vem, é sinal de harness; se é uso espontâneo (depuração, converter texto), é memória.

Na base 1 (pequena, 3 execuções do ContestacaoCivel), os 7 erros da parte E estão todos fora do ContestacaoCivel e são
espontâneos: `print(repr(x))`, `print(type(x).__name__)`, `print(dir(x))`, `eval(str(...))` para ler a observação.

  A. os erros da parte E por grupo (ContestacaoCivel × outros) × mês × nome;
  B. o uso da linha que falhou, por grupo × nome:
       'nome do tipo da exceção'  `type(e).__name__` com `e` de um `except … as e` no código (tratamento de erro);
       'nome do tipo'             `type(x).__name__`, `x.__class__.__name__` (fora de except);
       'nome de função/objeto'    `f.__name__`;
       'bloco __main__'           `if __name__ == '__main__'`;
       'converter texto (eval)'   `eval(texto)` para virar lista/dicionário;
       'depuração (print)'        a função barrada dentro de um `print(...)`;
       'código dinâmico'          `exec`, `__import__`;
       'abrir arquivo'            `open`;
       'introspecção · …'         o resíduo de `globals`/`locals`/`vars` (a regra do `contar_introspeccao_linha.py`);
       'função auxiliar'          o nome barrado não está na linha: está numa função que o agente definiu e chamou;
       'outro uso'                o resto;
  C. os formatos mais comuns da linha que falhou, por grupo × nome (textos entre aspas → '…', números longos → '#');
  D. o contexto no código do passo: a linha está num bloco `except`? o código tem a verificação instruída
     (`except NameError` ou `in globals()`)? Por grupo × nome.

Mesma população da auditoria (`audit/scripts/audit_candidata_base3.py`, `populacao_sandbox`), tipos `funcao_proibida` e
`atributo_dunder`. Lê o parquet cru com o pyarrow. Não grava nada. Imprime só contagens, nomes de papel, meses e
formatos mascarados de código. Uso, da raiz, na máquina da base:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_proibidas_linha.py --fonte <parquet>
"""
import argparse
from pathlib import Path
import re
import sys

import pandas as pd
import pyarrow.parquet as pq

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "audit" / "scripts"))
from contar_introspeccao_linha import uso_da_linha  # noqa: E402
from audit_candidata_base3 import extrair_sandbox, populacao_sandbox  # noqa: E402

LINHA_FALHA = re.compile(r"failed at line '(.*?)' due to", re.S)
PARTE_E = ("funcao_proibida", "atributo_dunder")
VERIFICACAO = re.compile(r"except\s+\(?[^)\n:]*\bNameError\b|\bin\s+(?:globals|locals|vars)\s*\(\s*\)")


def _no_texto(nome, texto):
    """O nome barrado aparece no texto como chamada (`f(`) ou atributo (`.__x__`)?"""
    return re.search(rf"(?<![\w.]){re.escape(nome)}\s*\(" if not nome.startswith("__") or nome == "__import__"
                     else rf"\.{re.escape(nome)}\b|\b{re.escape(nome)}\s*==", texto) is not None


def _funcao_auxiliar(nome, linha, codigo):
    """Uma função definida no código tem o nome barrado no corpo, e a linha que falhou a chama?"""
    for m in re.finditer(r"^([ \t]*)def\s+(\w+)\s*\(.*?(?=^\1\S|\Z)", codigo or "", re.S | re.M):
        if _no_texto(nome, m.group(0)) and re.search(rf"\b{re.escape(m.group(2))}\s*\(", linha):
            return True
    return False


def uso_proibida(nome, linha, codigo=""):
    """O uso da função/atributo barrado na linha que falhou (ver o docstring do módulo)."""
    if not _no_texto(nome, linha):
        return "função auxiliar" if _funcao_auxiliar(nome, linha, codigo) else "outro uso"
    if nome in ("globals", "locals", "vars"):
        return "introspecção · " + uso_da_linha(linha)
    if nome == "__name__" and re.search(r"\b__name__\s*==", linha):
        return "bloco __main__"
    if nome in ("__name__", "__class__"):
        t = re.search(r"type\s*\(\s*(\w+)\s*\)\s*\.\s*__name__|\b(\w+)\s*\.\s*__class__", linha)
        if t:
            v = t.group(1) or t.group(2)
            if re.search(rf"except\b[^\n:]*\bas\s+{re.escape(v)}\b", f"{codigo or ''}\n{linha}"):
                return "nome do tipo da exceção"
            return "nome do tipo"
        if re.search(r"\w\s*\.\s*__name__", linha):
            return "nome de função/objeto"
    if nome in ("exec", "__import__"):
        return "código dinâmico"
    if nome == "open":
        return "abrir arquivo"
    if re.search(rf"\bprint\s*\(.*(?<![\w.]){re.escape(nome)}\s*\(", linha, re.S):
        return "depuração (print)"
    if nome == "eval":
        return "converter texto (eval)"
    return "outro uso"


def em_except(linha, codigo):
    """A linha que falhou está dentro de um bloco `except` do código? (pela indentação; uma pista)"""
    primeira = next((l for l in linha.splitlines() if l.strip()), "").strip()
    linhas = (codigo or "").splitlines()
    for i, l in enumerate(linhas):
        if primeira and l.strip() == primeira:
            recuo = len(l) - len(l.lstrip())
            for ant in reversed(linhas[:i]):
                if ant.strip() and len(ant) - len(ant.lstrip()) < recuo:
                    if re.match(r"\s*except\b", ant):
                        return True
                    recuo = len(ant) - len(ant.lstrip())
                    if recuo == 0:
                        break
            return False
    return False


def mascarar(linha):
    s = re.sub(r"'[^']*'|\"[^\"]*\"", "'…'", " ".join(linha.split()))
    return re.sub(r"\d{6,}", "#", s)[:110]


def grupo(papel):
    return "ContestacaoCivel" if "ontestacaoCivel" in str(papel) else "outros"


def medir(linhas):
    """linhas: dicts com papel, mes_execucao, structured_error, error_type, error_message, error_code_action."""
    regs = []
    for r in linhas:
        if not (r.get("structured_error") == 1 and str(r.get("error_type") or "").strip()):
            continue
        msg, cod = str(r.get("error_message") or ""), str(r.get("error_code_action") or "")
        if not populacao_sandbox(msg, cod):
            continue
        tipo, nome = extrair_sandbox(msg)
        if tipo not in PARTE_E:
            continue
        m = LINHA_FALHA.search(msg)
        linha = m.group(1) if m else ""
        regs.append({"grupo": grupo(r["papel"]), "papel": r["papel"], "mes": r["mes_execucao"], "nome": nome,
                     "uso": uso_proibida(nome, linha, cod), "forma": mascarar(linha),
                     "no_except": em_except(linha, cod), "codigo_verifica": bool(VERIFICACAO.search(cod))})
    R = pd.DataFrame(regs, columns=["grupo", "papel", "mes", "nome", "uso", "forma", "no_except", "codigo_verifica"])
    A = R.pivot_table(index=["grupo", "nome"], columns="mes", values="uso", aggfunc="size", fill_value=0)
    A["total"] = A.sum(axis=1)
    A = A.sort_values(["total"], ascending=False).sort_index(level=0, sort_remaining=False).reset_index()
    A.columns.name = None
    B = R.groupby(["grupo", "nome", "uso"]).size().rename("erros").reset_index().sort_values(["grupo", "erros"],
                                                                                              ascending=[True, False])
    C = (R.groupby(["grupo", "nome", "forma"]).size().rename("erros").reset_index()
         .sort_values(["grupo", "nome", "erros"], ascending=[True, True, False]).groupby(["grupo", "nome"]).head(4))
    C = C[C.groupby(["grupo", "nome"]).erros.transform("sum").ge(5)]
    D = (R.groupby(["grupo", "nome"]).agg(erros=("uso", "size"), no_except=("no_except", "sum"),
                                         codigo_com_verificacao=("codigo_verifica", "sum"))
         .reset_index().sort_values(["grupo", "erros"], ascending=[True, False]))
    return {"total": len(R), "A": A, "B": B, "C": C, "D": D}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fonte", required=True, help="o parquet da base 3 (a v2, em data/)")
    a = p.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    cols = ["papel", "mes_execucao", "structured_error", "error_type", "error_message", "error_code_action"]
    T = medir(pq.read_table(a.fonte, columns=cols).to_pylist())
    pd.set_option("display.width", 220)
    pd.set_option("display.max_colwidth", 120)
    print(f"parte E: {T['total']} erros (esperado 523, dossiê §2b)")
    print("\nA · grupo × nome × mês")
    print(T["A"].to_string(index=False) if len(T["A"]) else "  nenhum")
    print("\nB · o uso da linha que falhou, por grupo × nome")
    print(T["B"].to_string(index=False) if len(T["B"]) else "  nenhum")
    print("\nC · os formatos mais comuns da linha que falhou (nomes com 5+ erros; textos → '…', números longos → '#')")
    print(T["C"].to_string(index=False) if len(T["C"]) else "  nenhum")
    print("\nD · contexto no código: a linha num bloco except? o código tem a verificação instruída (except NameError / in globals())?")
    print(T["D"].to_string(index=False) if len(T["D"]) else "  nenhum")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
