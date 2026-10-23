"""Testa, no interpretador do smolagents, quais funções embutidas do Python ele aceita e quais barra (b3 #55).

O degrau 2 da validação das memórias (`conferir_memorias.py`, kit) confere se o que uma memória manda usar existe no
ambiente. Para as funções do Python o prompt não diz nada, e o sandbox barra algumas (`repr`, `dir`, `open`…): sem esta
lista, a checagem sai "não verificável". Aqui cada nome de `dir(builtins)` (sem os dunder, salvo `__import__`) roda
sozinho num `LocalPythonExecutor` novo (`_f = <nome>`); "barrada" é o erro do próprio sandbox ("Forbidden function
evaluation", "is not defined"); qualquer outro erro para o script (não é um caso previsto). Código sintético, nenhum
dado de caso. Resultado em 21/10/2026, smolagents 1.26.0, Python 3.13: 111 funcionam, 40 barradas — entre elas as 7
que a memória E do sandbox proíbe (`repr`, `dir`, `exec`, `__import__`, `bytes`, `open`, `hash`); `print`, `type` e `str`
funcionam. A versão do smolagents da plataforma não é conhecida.

Uso, da raiz (o smolagents não é dependência do projeto):
    uv run --no-project --with smolagents==1.26.0 python analysis/2026-10-trace-law-flow-third/pipeline/validacao/testar_sandbox_funcoes.py --saida analysis/registros/funcoes_sandbox.json
"""
import argparse
import builtins
import datetime
import json
from pathlib import Path
import platform
import sys

import smolagents
from smolagents.local_python_executor import LocalPythonExecutor

DO_SANDBOX = ("Forbidden function evaluation", "is not defined")


def testar(nome):
    ex = LocalPythonExecutor(additional_authorized_imports=[])
    ex.send_tools({})
    try:
        ex(f"_f = {nome}")
        return True
    except Exception as e:   # o sandbox lança InterpreterError; só os dele contam como barrada
        if any(s in str(e) for s in DO_SANDBOX):
            return False
        raise


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--saida", required=True, type=Path)
    a = p.parse_args(argv)
    nomes = sorted(n for n in dir(builtins) if not n.startswith("_") or n == "__import__")
    res = {n: testar(n) for n in nomes}
    doc = {"o_que_e": "As funções embutidas do Python que o interpretador do smolagents aceita e as que barra, testadas "
                      "uma a uma (testar_sandbox_funcoes.py). Lido pelo conferir_memorias.py (--funcoes), no degrau 2.",
           "interpretador": f"smolagents {smolagents.__version__}, Python {platform.python_version()}",
           "gerado_em": datetime.date.today().isoformat(),
           "funcionam": [n for n in nomes if res[n]], "barradas": [n for n in nomes if not res[n]]}
    a.saida.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{doc['interpretador']}: {len(doc['funcionam'])} funcionam, {len(doc['barradas'])} barradas → {a.saida}")
    print("barradas:", ", ".join(doc["barradas"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
