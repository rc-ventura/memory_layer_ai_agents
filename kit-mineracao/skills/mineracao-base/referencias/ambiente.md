# Ambiente — rodar a análise em qualquer sistema

## Python e dependências

- O ambiente é o do `pyproject.toml` da raiz do repositório. Instale com `uv sync`; o `pyarrow`, que lê parquet, já
  está lá.
- Rode tudo com `uv run` na frente (`uv run python …`, `uv run jupyter …`) quando o `.venv` não estiver ativo.

## Onde rodar

- **Os agentes (subagentes) são disparados da raiz do repositório**, a pasta que tem o `CLAUDE.md`. Disparado de uma
  subpasta, o Claude Code vê o `AGENTS.md` importado pelo `CLAUDE.md` como "fora da pasta de trabalho", pergunta se
  pode carregá-lo, e o agente fica parado até alguém responder no painel dele.

- Os comandos do pipeline rodam **de dentro de `pipeline/`** da pasta da análise: `drill_down.py`, `checklist.py` e
  os notebooks usam caminhos relativos a essa pasta.
- As auditorias rodam da pasta da análise: `python audit/scripts/audit_recompute9.py …`.

## Notebooks: sempre pelo terminal

```
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 <notebook>.ipynb
```

- O notebook roda de ponta a ponta, sem depender do editor. Rodado pelo editor, ele já deixou de terminar.
- O `--inplace` grava as saídas no próprio notebook. Elas não entram na conferência de versão: só o código das células
  conta.
- Notebook que falha: registre a última linha do erro, sem dado de caso, e pare a skill.

## Windows

- **Terminal em UTF-8:** antes de rodar, use `export PYTHONIOENCODING=utf-8` (Git Bash) ou `set PYTHONIOENCODING=utf-8`
  (cmd). Os scripts do pipeline já reconfiguram a saída, mas o terminal precisa aceitar.
- **Limite de 260 caracteres no caminho.** As pastas de evidência têm nomes longos, por exemplo
  `resultados/evidencia/<seção>_<análise>/derivados/<tabela>.csv`. Se a raiz do repositório for funda (OneDrive,
  `Documentos\projects\…`), a gravação falha com `FileNotFoundError` num caminho que parece existir. Encurte a raiz
  com uma unidade virtual, que não precisa de administrador e dura até sair da sessão:
  ```
  cmd //c subst R: "<raiz do repositório>"      # Git Bash; no cmd: subst R: "<raiz>"
  cd /r/analysis/<pasta-da-analise>/pipeline
  ```
  Para conferir antes de rodar, some o comprimento da raiz com o do maior caminho de evidência. Precisa ficar abaixo
  de 260.

## O trace

- O arquivo do trace é o `TRACE` do `pipeline/base_pipeline.py` da análise. Pode ser CSV (puro, `.xz`, `.gz`) ou um
  único parquet, porque o leitor decide pelo conteúdo.
- O trace nunca é versionado: o `.gitignore` da raiz cobre `*.csv`, `*.csv.xz`, `*.csv.gz` e `*.parquet`.
