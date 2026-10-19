# Dossiê — inventário do sandbox (`U_sandbox`) na base 3

> Códigos e siglas: [glossário](../../../glossario.md). Racional: [`racional.md`](racional.md). Procedimento:
> [`06`](../../docs/06-procedimento-mineracao-candidatas.md); porquê: [`07`](../../docs/07-racionais-mineracao-candidatas.md).

**Rodada:** `observada_e3ebc8274dcf108c` (fonte `908aa005…`, extração v2) · **Mineração:** `minerar.py`, 9 passos, 16/10/2026,
máquina da base · **Evidência:** `pipeline/resultados/mineracao/U_sandbox/` na máquina da base (`memoria_U_sandbox_base3.json`,
`inventario.csv`, `inventario_papel.csv`, `inventario_mes.csv`, `manifesto_mineracao.json`), lida por fotos em 19/10/2026.

## 1 · A mineração fechou

| Passo | Resultado |
|---|---|
| 1 · rodada | 37 artefatos no manifesto |
| 2 · monitoramento | não conferido: o `monitorar.py` não lê as tabelas da base 3 (`b3 #28`) |
| 3 · parte genérica | 3.653 erros · 3.475 ocorrências · 3.451 execuções · 10 meses (nov/25–ago/26) · 16 papéis |
| 4 · parte específica | 43 nomes recusados |
| 5 · confiança | cobertura 3.648 / 3.653 = **99,86%** (limiar 95%); os 5 sem nome são `InterpreterError` sem padrão |
| 6 · destino | 6 listas de imports autorizados; 5 erros repetem o nome na mesma execução e papel |
| 7 · encontro | **61 medidas iguais**, 0 diferentes (depois da emenda 2 do racional: o 1 erro com timeout de ferramenta) |
| 8 · arquivo final | aprovado no esquema 0.2, `status: derived-and-checked`, `destino: "em aberto"` |
| 9 · saída | 17 arquivos no manifesto, varredura limpa |

**A hipótese "a lição sai da mensagem" está confirmada na base 3.** O script faz o que o racional diz.

## 2 · O que os números mostram: a lição tem quatro partes, com donos diferentes

Somas das linhas de `inventario_papel.csv` e `inventario_mes.csv`. "ontestacaoCivel" é o `ContestacaoCivel` com o nome cortado
na origem (`b3 #45` b).

| Parte | Erros | % | Onde | Quando |
|---|---:|---:|---|---|
| **A · Introspecção no `ContestacaoCivel`**: `globals` 2.347, `__name__` 172, `repr` 54, `eval` 46, `locals` 15, `dir` 9, `exec` 8, `bytes` 5, `__import__` 5, `vars` 3, `hash` 2, `__class__` 1 | 2.667 | 73% | 1 papel | `globals`: 1.592 em jul/26 e 754 em ago/26 (2.346 de 2.352); antes de julho, 6 |
| **B · Ferramenta importada como módulo, no `OBFCivel`**: `get_document_text` 167, `python_interpreter` 34, `tools` 4, `tool_usage` 2, `tool_functions` 1, `mcp` 1, `mcp_client.tools` 1, `smolagents` 1 | 211 | 6% | 1 papel | `get_document_text` crescendo: 1 (mar) → 14 → 25 → 54 → 73 (jul) |
| **C · Módulo usado sem import**: `json` 415, `pd` 233, `re` 5, `datetime` 3 | 656 | 18% | `json` em 10 papéis (RoteadorCivel 241, JoogleAnalytics 105, CalculoTrabalhista 41…); `pd` 231 no JoogleAnalytics | todos os meses; `json` sobe em jun–jul (114, 173) |
| **D · Import fora da lista autorizada** (`copy`, `typing`, `ast`, `tabulate`, `calendar`, `textwrap`, `numbers`, `base64`, `operator`, `pprint`, `traceback`, …) | ≈ 115 | 3% | espalhado | espalhado |

O resto (as outras combinações pequenas e os 5 sem nome) fecha os 3.653.

### A · Hipótese: é a mesma instrução do prompt do `try/except NameError`

- 73% da lição é um papel só, o `ContestacaoCivel`, e quase tudo em julho e agosto de 2026.
- O mesmo papel e o mesmo período têm o sinal de harness `U_verificacao_try_nameerror`: 5.764 erros, **95 em julho e 5.667
  em agosto** ([`02` §7.9–7.10](../../docs/02-relatorio-achados.md); `b3 #28`). Na base 2, a causa foi uma instrução do prompt
  que o ambiente não suporta: "verificar se a variável existe".
- **A troca de mês é a pista:** em julho o `globals` dispara (1.592) e o `try/except` é baixo (95); em agosto o `try/except`
  explode (5.667) e o `globals` cai à metade (754). Leitura: o mesmo pedido do prompt ("confira se a variável existe"),
  implementado de dois jeitos que o sandbox recusa — `'x' in globals()` em julho e `try: x / except NameError` em agosto.
- **É hipótese, não achado:** falta mostrar a instrução no prompt de julho (o hash do prompt por mês é o pedido C, `05`;
  ou o `b2 #3`, se o parágrafo já estava no prompt de julho).
- **Primeira evidência (19/10, base 1, n pequeno):** o prompt de julho/26 do ContestacaoCivel na base 1 (3 execuções) já
  tem a instrução, **sem dizer como**: "Antes de chamar qualquer tool, VERIFIQUE se a variável de saída correspondente já
  está preenchida em memória. Se já estiver, PULE a chamada e siga para a próxima etapa." Não menciona `NameError` nem
  proíbe `globals()`. Uma das 3 execuções cumpre a instrução com `'x' in globals()` (a linha que falhou é uma verificação
  de existência) e é barrada. Comando: `uv run python analysis/2026-09-trace-law-flow-second/scripts/contar_introspeccao_prompt_base2.py --trace <trace da base 1>`.
- **Os testes que fecham a hipótese** (rodam na máquina da base):
  - base 2: `analysis/2026-09-trace-law-flow-second/scripts/contar_introspeccao_prompt_base2.py --trace <trace da base 2>`
    — papel × mês × versão do trecho do prompt × erros de introspecção e de `try/except`;
  - base 3: `analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_introspeccao_linha.py --fonte <parquet v2>`
    — se a linha que falhou é verificação de existência, e o lado a lado com o `try/except` por papel e mês.
- **Consequência para o destino:** uma memória "não chame `globals`" brigaria com a instrução do próprio prompt. O conserto
  é no prompt (harness), como no `try/except`, e não memória.

### B · Uma sub-lição própria: as ferramentas já estão no escopo

O `OBFCivel` tenta `import get_document_text` / `from tools import …` em vez de chamar a ferramenta, que já está disponível
como função. É outra lição ("chame a ferramenta direto; não importe"), de um papel só e crescendo mês a mês.

### C · O núcleo de memória de verdade

`json` e `pandas` estão na lista autorizada dos papéis que erram (por exemplo, `JoogleAnalytics` tem `json` e `pandas`):
o agente só esqueceu o `import`. É transversal (10 papéis, 10 meses) e o agente quase não repete na mesma execução (5 casos):
o custo é a primeira tentativa de cada execução, e é isso que uma memória injetada no começo evita.

### D · O ambiente muda por papel

São 6 listas de imports autorizados. Ex.: `pandas`/`numpy`/`dateutil` só para `CalculoTrabalhista` e `JoogleAnalytics`;
`Consultivo`/`OBFCivel` sem `pandas` nem `numpy`; `CalculoCivel` com `openpyxl` e `os`. Uma memória de "imports autorizados"
precisa ser por papel.

## 3 · A memória que o script montou

`scope: role null` (global) e uma `correction_guidance` única: "Não chame: globals, repr, eval, locals, dir, exec,
`__import__`, bytes, open, vars, hash; Não importe: …; Importe antes de usar: …; …; Imports autorizados (papéis …): …"
(as 6 listas). Está correta como inventário, mas mistura as quatro partes acima, cada uma com um destino diferente.

## 4 · As decisões do Rafael

| # | Decisão | Opções | Recomendação |
|---|---|---|---|
| 1 | O script | aprovar (vai de `propostas/` para `pipeline/especificas/`) · não aprovar | **aprovar**: cobertura 99,86%, encontro 61/61, validador aprovado |
| 2 | Dividir a lição? | manter uma memória única · dividir nas partes A–D | **dividir** ("dividir a unidade é resultado normal", `16`): cada parte tem dono e destino próprios |
| 3 | Destino de A (introspecção, `ContestacaoCivel`) | harness · memória · em aberto | **harness**, junto do `try/except` (hipótese a confirmar pelo prompt de julho) |
| 4 | Destino de B (ferramenta como módulo, `OBFCivel`) | memória do papel · harness (o prompt explica a chamada) | **memória do papel** `OBFCivel`; harness se o prompt não disser que as ferramentas já estão no escopo |
| 5 | Destino de C + D (imports) | memória global · memória por papel | **memória por papel**: "importe X antes de usar; os imports autorizados aqui são …" |

Nenhuma decisão muda número: dividir é um ajuste da lição (o racional ganha as partes e o script passa a montar uma
`correction_guidance` por parte), com nova validação.
