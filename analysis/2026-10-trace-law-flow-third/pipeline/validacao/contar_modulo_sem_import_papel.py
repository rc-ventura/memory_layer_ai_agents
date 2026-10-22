"""Base 3: o "módulo usado sem import" de um papel — quando começa, e o sandbox deixa importar o módulo nesse papel?

Pergunta (dossiê do sandbox na base 3, `propostas/U_sandbox/dossie_base3.md`, §2h, 12–16): o RoteadorCivel é o papel com
mais "`json` sem import" (241 de 415). O prompt dele (bases 1 e 2) diz que as ferramentas devolvem "JSON formatado como
string" — o agente precisa de `json.loads` — e, desde a versão de mai/26, a lista de imports autorizados do prompt não tem
o `json` (a de dez/25 tinha). Duas leituras: o prompt induz o erro (sinal de harness) ou o agente esquece (memória).

  A. a linha do tempo: por mês, as execuções do papel com algum erro, as com o erro do módulo e os erros. Se o erro
     começa ou dispara quando o módulo saiu da lista do prompt, a leitura de harness se sustenta; se já existia antes, o
     agente esquece de qualquer jeito (memória). (A base 3 só tem erros: o denominador é "execuções do papel com algum
     erro", não todas as execuções.)
  B. o sandbox deixa importar o módulo nesse papel? (1) depois do erro, o passo seguinte importa o módulo — e dá erro ou
     não; (2) algum passo com erro do papel tem `import <módulo>` numa linha antes da que falhou (o import rodou); (3)
     quantos "Import of <módulo> is not allowed" há no papel e na base inteira.
  C. uma causa só? (acrescentado em 22/10, dossiê §2h, 24) o passo anterior do papel (n-1, a única janela de antes que a
     base 3 guarda) importou o módulo e rodou sem erro. No interpretador do smolagents um import vale nos passos
     seguintes (testado em 22/10, 1.26.0): se o import rodou no passo anterior e o nome sumiu, a causa é o estado
     perdido entre passos, não esquecer o import. É um limite inferior: um import mais antigo que n-1 não se vê.
`--papel todos` olha todos os papéis; `--nome` é o nome usado sem import quando difere do módulo (`--modulo pandas
--nome pd`).

Lê o parquet cru com o pyarrow (não usa o pipeline). Não grava nada. Imprime só contagens e meses. Uso, da raiz, na
máquina da base:
    uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_modulo_sem_import_papel.py --fonte <parquet> [--papel RoteadorCivel|todos] [--modulo json] [--nome pd]
"""
import argparse
from collections import Counter, defaultdict
import re
import sys

import pyarrow.parquet as pq

LINHA_FALHA = re.compile(r"failed at line '(.*?)' due to", re.S)
COLUNAS = ["cod_idef_exeo", "papel", "mes_execucao", "structured_error", "error_type", "error_message",
           "error_code_action", "next_code_action", "next_error_type", "next_error_message", "prev_code_action",
           "prev_error_type"]


def importa(codigo, modulo):
    """O código tem um `import <módulo>` (ou `import <módulo> as …`, ou `from <módulo> import …`) numa linha própria?"""
    m = re.escape(modulo)
    return bool(re.search(rf"(?m)^\s*(?:import\s+{m}\b|from\s+{m}(?:\.\w+)*\s+import\b)", codigo or ""))


def importou_antes_da_falha(codigo, msg, modulo):
    """O `import <módulo>` está numa linha do código antes da que falhou (então rodou sem ser barrado)?"""
    f = LINHA_FALHA.search(msg or "")
    if not (f and codigo):
        return False
    falhou = f.group(1).strip().splitlines()[0].strip() if f.group(1).strip() else ""
    linhas = codigo.splitlines()
    pos = next((i for i, l in enumerate(linhas) if falhou and l.strip() == falhou), None)
    return pos is not None and importa("\n".join(linhas[:pos]), modulo)


def medir(linhas, papel, modulo, nome=None):
    """`papel` "todos": todos os papéis; `nome`: o nome usado sem import (padrão: o módulo)."""
    sem_import = re.compile(rf"The variable `{re.escape(nome or modulo)}` is not defined")
    barrado = re.compile(rf"Import (?:of|from) {re.escape(modulo)}\b[\w.]* is not allowed")
    A = defaultdict(lambda: {"execucoes_com_erro": set(), "execucoes_com_o_erro": set(), "erros": 0})
    B = Counter()
    for r in linhas:
        if not (r.get("structured_error") == 1 and str(r.get("error_type") or "").strip()):
            continue
        msg = str(r.get("error_message") or "")
        B["barrado_na_base"] += bool(barrado.search(msg))
        if papel != "todos" and r.get("papel") != papel:
            continue
        mes, ex = str(r.get("mes_execucao")), str(r.get("cod_idef_exeo"))
        A[mes]["execucoes_com_erro"].add(ex)
        B["barrado_no_papel"] += bool(barrado.search(msg))
        if importou_antes_da_falha(r.get("error_code_action"), msg, modulo):
            B["import_rodou_antes_da_falha"] += 1
            B["import_rodou · " + mes] += 1
        if sem_import.search(msg.rsplit("due to:", 1)[-1]):
            A[mes]["execucoes_com_o_erro"].add(ex)
            A[mes]["erros"] += 1
            if importa(r.get("prev_code_action"), modulo) and not str(r.get("prev_error_type") or "").strip():
                B["antes: o passo anterior importou e rodou sem erro"] += 1
            nxt = r.get("next_code_action")
            if not importa(nxt, modulo):
                B["depois: o passo seguinte não importa"] += 1
            elif not str(r.get("next_error_type") or "").strip():
                B["depois: importa e o passo roda sem erro"] += 1
            elif barrado.search(str(r.get("next_error_message") or "")):
                B["depois: importa e é barrado"] += 1
            else:
                B["depois: importa e dá outro erro"] += 1
    tempo = [{"mes": m, "execucoes_com_erro": len(d["execucoes_com_erro"]),
              "execucoes_com_o_erro": len(d["execucoes_com_o_erro"]), "erros": d["erros"]} for m, d in sorted(A.items())]
    return tempo, B


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fonte", required=True, help="o parquet da base 3 (a v2, em data/)")
    p.add_argument("--papel", default="RoteadorCivel")
    p.add_argument("--modulo", default="json")
    p.add_argument("--nome", help="o nome usado sem import, se difere do módulo (pd para pandas)")
    a = p.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    tempo, B = medir(pq.read_table(a.fonte, columns=COLUNAS).to_pylist(), a.papel, a.modulo, a.nome)
    print(f"A · `{a.modulo}` sem import no {a.papel}, por mês (denominador: execuções do papel com algum erro)")
    print(f"{'mês':8} {'execuções c/ erro':>17} {'c/ o erro':>10} {'erros':>6}")
    for t in tempo:
        print(f"{t['mes']:8} {t['execucoes_com_erro']:>17} {t['execucoes_com_o_erro']:>10} {t['erros']:>6}")
    print(f"\nB · o sandbox deixa importar `{a.modulo}` no {a.papel}?")
    for k in ("depois: importa e o passo roda sem erro", "depois: importa e é barrado", "depois: importa e dá outro erro",
              "depois: o passo seguinte não importa"):
        print(f"  {k:45} {B[k]}")
    meses = ", ".join(f"{k.split(' · ')[1]} {v}" for k, v in sorted(B.items()) if k.startswith("import_rodou · "))
    print(f"  {'passos com erro em que o import rodou antes da falha':45} {B['import_rodou_antes_da_falha']}"
          + (f"  ({meses})" if meses else ""))
    print(f"  {'Import of ' + a.modulo + ' is not allowed — no papel':45} {B['barrado_no_papel']}")
    print(f"  {'Import of ' + a.modulo + ' is not allowed — na base':45} {B['barrado_na_base']}")
    print(f"\nC · uma causa só? (o erro × o passo anterior do papel)")
    print(f"  {'antes: o passo anterior importou e rodou sem erro':45} {B['antes: o passo anterior importou e rodou sem erro']}"
          f" de {sum(t['erros'] for t in tempo)} erros")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
