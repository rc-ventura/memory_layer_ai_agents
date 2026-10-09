# Registros — arquivos de dados lidos por scripts, compartilhados por todas as bases

Dois arquivos JSON versionados, sem dado de caso (só decisões, regras, contagens e estrutura). Ficam aqui, e não na
pasta de uma base, porque valem para todas.

| Arquivo | O que é | Quem lê | Onde se explica |
|---|---|---|---|
| [`monitoramento.json`](monitoramento.json) | o que o pesquisador decidiu monitorar entre as bases: linha de base, regras, gatilhos | `.claude/skills/mineracao-base/scripts/monitorar.py` (passo 0 de toda mineração) | `2026-09-trace-law-flow/docs/16-procedimento-mineracao-candidatas.md` (§ O monitoramento) |
| [`esquema-memoria.json`](esquema-memoria.json) | a estrutura do arquivo final de uma memória (provisória, ajustável num lugar só) | `.claude/skills/mineracao-candidata/scripts/validar_memoria.py`; `2026-10-trace-law-flow-third/pipeline/mineracao_observada.py` (entra no hash do código da rodada) | `16` § A estrutura do arquivo final; `06` §10 |

**Regra:** um registro novo, lido por script e comum às bases, entra aqui, com uma linha nesta tabela. Os arquivos
específicos de uma base ficam na pasta dela.
