"""Um import feito num passo continua valendo nos passos seguintes, no interpretador do smolagents? (dossiê do sandbox §2h, 24)

A memória C do sandbox ("importe antes de usar") supõe que o erro "The variable `json` is not defined" vem de o agente
esquecer o import. Outra causa possível: o agente importou num passo anterior e o nome sumiu entre passos (estado
perdido — o conserto seria no ambiente, não memória). Aqui o mesmo `LocalPythonExecutor` roda três passos: o primeiro
importa, os seguintes usam. Código sintético, nenhum dado de caso. Resultado em 22/10/2026, smolagents 1.26.0: os três
passos rodam — o import persiste. Então, no trace, um "não definido" depois de um import que rodou no mesmo papel e
execução aponta para estado perdido, não para esquecimento (`contar_casos_memoria_base2.py`, bases 1 e 2;
`contar_modulo_sem_import_papel.py`, parte C, base 3). A versão do smolagents da plataforma não é conhecida.

Uso, da raiz (o smolagents não é dependência do projeto):
    uv run --no-project --with smolagents==1.26.0 --with pandas python analysis/2026-10-trace-law-flow-third/pipeline/validacao/testar_sandbox_import_persiste.py
"""
from smolagents.local_python_executor import LocalPythonExecutor

PASSOS = ["import json\nimport pandas as pd\nx = 1",
          "print(json.dumps({'a': x}))",
          "print(type(pd).__qualname__ if False else 'pd ainda existe')"]

ex = LocalPythonExecutor(additional_authorized_imports=["json", "pandas"])
ex.send_tools({})
for i, codigo in enumerate(PASSOS, 1):
    try:
        ex(codigo)
        print(f"passo {i}: roda")
    except Exception as e:   # o que o sandbox lança, para mostrar
        print(f"passo {i}: ERRO {str(e)[:120]}")
