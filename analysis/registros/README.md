# Registros — arquivos de dados lidos por scripts, compartilhados por todas as bases

Arquivos JSON versionados, sem dado de caso (só decisões, regras, contagens e estrutura). Ficam aqui, e não na
pasta de uma base, porque valem para todas.

| Arquivo | O que é | Quem lê | Onde se explica |
|---|---|---|---|
| [`monitoramento.json`](monitoramento.json) | o que o pesquisador decidiu monitorar entre as bases: linha de base, regras, gatilhos | `.claude/skills/mineracao-base/scripts/monitorar.py` (passo 0 de toda mineração) | `2026-09-trace-law-flow/docs/16-procedimento-mineracao-candidatas.md` (§ O monitoramento) |
| [`memorias.json`](memorias.json) | o catálogo das memórias fechadas, em todas as bases (destino memória, derived-and-checked; sem os casos); a memória não injetada leva o `monitorada` (rara ou reforço, linha de base, gatilhos — Ajuste 29) | `.claude/skills/mineracao-candidata/scripts/catalogar_memoria.py` (montado no passo 9 do `minerar.py`) | `pipeline-entre-bases.md`, Ajuste 22 |
| [`decisoes_degrau2.json`](decisoes_degrau2.json) | as decisões do pesquisador no degrau 2 (conferida): numa checagem que o script não fecha, o resultado aceito, os motivos de então e o porquê | `.claude/skills/mineracao-candidata/scripts/conferir_memorias.py` (grava com `--decidir`, lê sempre) | `2026-09-trace-law-flow/docs/17-validacao-memorias.md`; `pipeline-entre-bases.md`, Ajuste 28 |
| [`funcoes_sandbox.json`](funcoes_sandbox.json) | as funções embutidas do Python que o interpretador do smolagents aceita e as que barra, testadas uma a uma (versão no arquivo) | `conferir_memorias.py` (`--funcoes`) | gerado por `2026-10-trace-law-flow-third/pipeline/validacao/testar_sandbox_funcoes.py`; Ajuste 28 |
| [`esquema-memoria.json`](esquema-memoria.json) | a estrutura do arquivo final de uma memória (provisória, ajustável num lugar só) | `.claude/skills/mineracao-candidata/scripts/validar_memoria.py`; `2026-10-trace-law-flow-third/pipeline/mineracao_observada.py` (entra no hash do código da rodada) | `16` § A estrutura do arquivo final; `06` §10 |

**Regra:** um registro novo, lido por script e comum às bases, entra aqui, com uma linha nesta tabela. Os arquivos
específicos de uma base ficam na pasta dela.
