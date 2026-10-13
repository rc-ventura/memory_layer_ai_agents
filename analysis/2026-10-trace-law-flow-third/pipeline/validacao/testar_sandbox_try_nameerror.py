"""Reproduz, no interpretador do smolagents, a causa do erro de nome no primeiro passo (relatório da base 3 §7.9).

O system prompt do ContestacaoCivel manda verificar se uma variável existe com `try: nome` / `except NameError:`.
Aqui o mesmo padrão e as alternativas rodam no `LocalPythonExecutor`, com código sintético (nenhum dado de caso).
Resultado em 13/10/2026, smolagents 1.26.0 (a versão da plataforma não é conhecida):

  1 except NameError ............ FALHA: InterpreterError "The variable `x` is not defined" (a mesma mensagem do trace)
  2 except InterpreterError ..... FALHA: o nome `InterpreterError` não existe dentro do sandbox
  3 except Exception ............ OK
  4 except (sem tipo) ........... OK
  5 'x' in globals() ............ FALHA: globals() é proibida
  6 dicionário de estado injetado OK
  7 chamada direta .............. OK (o que o agente faz no passo seguinte)
  e, com a variável já criada num passo anterior, o `except NameError` funciona: o erro só acontece quando a variável
  ainda não existe — isto é, no primeiro passo.

Uso, da raiz (o smolagents não é dependência do projeto):
    uv run --with smolagents python analysis/2026-10-trace-law-flow-third/pipeline/validacao/testar_sandbox_try_nameerror.py
"""
from smolagents.local_python_executor import LocalPythonExecutor

def ferramenta():
    return "resultado da ferramenta"

VARIANTES = {
    "1 except NameError (o prompt atual)": "try:\n    x\nexcept NameError:\n    x = ferramenta()\nprint(x)",
    "2 except InterpreterError": "try:\n    x\nexcept InterpreterError:\n    x = ferramenta()\nprint(x)",
    "3 except Exception": "try:\n    x\nexcept Exception:\n    x = ferramenta()\nprint(x)",
    "4 except (bare)": "try:\n    x\nexcept:\n    x = ferramenta()\nprint(x)",
    "5 'x' in globals()": "if 'x' not in globals():\n    x = ferramenta()\nprint(x)",
    "6 dicionário de estado injetado": "if 'x' not in estado:\n    estado['x'] = ferramenta()\nprint(estado['x'])",
    "7 chamada direta (o que o agente faz no passo seguinte)": "x = ferramenta()\nprint(x)",
}

for nome, code in VARIANTES.items():
    ex = LocalPythonExecutor(additional_authorized_imports=[])
    ex.send_tools({"ferramenta": ferramenta, "final_answer": lambda a: a})
    ex.send_variables({"estado": {}})
    try:
        out = ex(code)
        print(f"{nome}: OK -> {out.logs.strip()!r}")
    except Exception as e:
        print(f"{nome}: FALHA -> {type(e).__name__}: {str(e).splitlines()[-1][:160]}")

# reentrada: a variável já existe de um passo anterior (o caso para o qual a instrução foi escrita)
print("\n-- segundo passo, com x já definido no primeiro --")
for nome in ["1 except NameError (o prompt atual)", "3 except Exception"]:
    ex = LocalPythonExecutor(additional_authorized_imports=[])
    ex.send_tools({"ferramenta": ferramenta, "final_answer": lambda a: a})
    ex("x = 'já existia'")
    try:
        out = ex(VARIANTES[nome]); print(f"{nome}: OK -> {out.logs.strip()!r}")
    except Exception as e:
        print(f"{nome}: FALHA -> {type(e).__name__}: {str(e).splitlines()[-1][:160]}")
