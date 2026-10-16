"""Reproduz, no interpretador do smolagents, o que cada tipo de valor produz no "Could not index" (roadmap b3 #34, #35).

A pergunta: um "Could not index" com `string indices must be integers` pode vir de um dict? Os casos rodam no
`LocalPythonExecutor`, com dados sintéticos. Resultado em 14/10/2026, smolagents 1.26.0:

  1 dict, chave inexistente ......... valor `{'` | KeyError: 'nao_existe'
  2 dict indexado com 0 ............. valor `{'` | KeyError: 0                 (o retorno-dict da base 1)
  3 JSON em texto, chave ............ valor `{"` | string indices must be integers, not 'str'
  4 str(dict) em texto, chave ....... valor `{'` | string indices must be integers, not 'str'
  5 campo texto dentro de dict ...... valor `{"` | string indices must be integers, not 'str'  (o valor é o campo)
  6 JSON em texto, .get ............. ... has no attribute get

Um dict nunca dá o erro de string: ele só sai quando o valor indexado é TEXTO. O primeiro caractere não separa dict de
texto; a aspa depois do `{` separa JSON (`{"`) de repr Python (`{'`), mas um dict e um repr em texto começam igual.

Uso, da raiz (o smolagents não é dependência do projeto):
    uv run --with smolagents python analysis/2026-10-trace-law-flow-third/pipeline/validacao/testar_sandbox_indexar.py
"""
import json
from smolagents.local_python_executor import LocalPythonExecutor
import smolagents
print("smolagents", smolagents.__version__)
dado = {"result": [{"hashDocumento": "h1", "texto": "conteudo"}], "status": "ok"}
def ferramenta_dict(): return dado
def ferramenta_json(): return json.dumps(dado)
def ferramenta_repr(): return str(dado)
CASOS = {
  "1 dict, chave inexistente":        "r = ferramenta_dict()\nr['nao_existe']",
  "2 dict indexado com 0":            "r = ferramenta_dict()\nr[0]",
  "3 JSON em texto, chave":           "r = ferramenta_json()\nr['result']",
  "4 str(dict) em texto, chave":      "r = ferramenta_repr()\nr['result']",
  "5 dict com campo texto, aninhado": "r = {'result': ferramenta_json()}\nr['result']['status']",
  "6 JSON em texto, .get":            "r = ferramenta_json()\nr.get('result')",
}
for nome, code in CASOS.items():
    ex = LocalPythonExecutor(additional_authorized_imports=[])
    ex.send_tools({"ferramenta_dict": ferramenta_dict, "ferramenta_json": ferramenta_json, "ferramenta_repr": ferramenta_repr})
    try:
        ex(code); print(f"{nome}: OK")
    except Exception as e:
        m = str(e)
        i = m.find("Could not index ")
        ini = m[i+16:i+18] if i >= 0 else "-"
        print(f"{nome}:\n   começo do valor {ini!r} | fim: ...{m[-70:]!r}")
