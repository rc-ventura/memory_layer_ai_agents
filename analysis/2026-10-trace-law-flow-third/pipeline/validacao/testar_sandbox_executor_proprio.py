"""Mostra, no smolagents, que a lista de imports do prompt e a do interpretador podem divergir (dossiê do sandbox §2h, 21).

O `CodeAgent` monta o prompt com `authorized_imports` (a lista-base + `additional_authorized_imports`) e usa o
interpretador que recebe em `executor=` como está; só o interpretador criado pelo próprio agente recebe a lista dele
(`agents.py`, l. 1544, 1585, 1598–1606 e 1620–1630, v1.26.0). Aqui um modelo falso responde sempre `import json`
(nenhuma chamada a LLM, nenhum dado de caso). Resultado em 21/10/2026, smolagents 1.26.0:

  A padrão (sem executor=) ................. prompt sem json, interpretador sem json: barrado ("Import of json is not allowed")
  B executor= com json, agente sem ......... prompt sem json, interpretador com json: RODA — o que se vê no trace (§2h, 18 e 20)
  C o inverso .............................. prompt com json, interpretador sem json: barrado, com o prompt dizendo que pode

Mostra que o caso B é possível; não mostra que a plataforma o faz assim (um prompt próprio, `prompt_templates` ou
`instructions`, com a lista escrita à mão, deixa a mesma marca no trace).

Uso, da raiz (o smolagents não é dependência do projeto):
    uv run --with smolagents==1.26.0 python analysis/2026-10-trace-law-flow-third/pipeline/validacao/testar_sandbox_executor_proprio.py
"""
import re

import smolagents
from smolagents import CodeAgent, LocalPythonExecutor
from smolagents.models import ChatMessage, MessageRole, Model

CODIGO = '<code>\nimport json\nprint(json.dumps({"ok": 1}))\nfinal_answer("rodou")\n</code>'


class ModeloFalso(Model):
    def generate(self, messages, **kw):
        return ChatMessage(role=MessageRole.ASSISTANT, content="Thought: teste\n" + CODIGO)


def rodar(nome, **kw):
    agente = CodeAgent(tools=[], model=ModeloFalso(), verbosity_level=-1, **kw)
    prompt = agente.initialize_system_prompt()
    lista_prompt = re.search(r"only from the following list of modules: (\[[^\]]*\])", prompt).group(1)
    agente.run("teste", max_steps=1)
    erros = [str(s.error) for s in agente.memory.steps[1:] if getattr(s, "error", None)]
    barrado = any("Import of json is not allowed" in e for e in erros)
    print(f"{nome}\n  json na lista do prompt: {'json' in lista_prompt}"
          f" · json no interpretador: {'json' in agente.python_executor.authorized_imports}"
          f" · import json: {'BARRADO' if barrado else 'RODA'}")


print("smolagents", smolagents.__version__)
rodar("A padrão (sem executor=)")
rodar("B executor= com json, agente sem", executor=LocalPythonExecutor(additional_authorized_imports=["json"]))
rodar("C o inverso", additional_authorized_imports=["json"], executor=LocalPythonExecutor(additional_authorized_imports=[]))
