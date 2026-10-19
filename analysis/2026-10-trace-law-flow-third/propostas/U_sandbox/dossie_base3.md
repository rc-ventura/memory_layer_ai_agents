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

### A · Resultado dos testes (19/10, máquina da base): a hipótese se confirma

**Base 2** (`contar_introspeccao_prompt_base2.py --trace <base 2>`), ContestacaoCivel, primeiro passo de cada execução:

| Versão do trecho do prompt | Diz como verificar? | Como o primeiro passo verificou | Execuções | Com erro |
|---|---|---|---:|---:|
| `4b8c6d76ff` (jun–ago): "VERIFIQUE se a variável… PULE a chamada" | não | com `globals`/`locals`/`vars` | 36 | 35 |
| `4b8c6d76ff` | não | não verificou | 91 | 1 |
| `2802ad7768` (só ago): a mesma instrução + "não use `globals()`/`locals()`; use `try/except NameError`" | sim | com `try/except NameError` | 97 | 97 |

Os 36 erros de introspecção da base 2 são todos verificação de existência na linha que falhou. Com o prompt antigo, 28% verificaram (todos com introspecção, barrada) e 72% não verificaram (sem erro); com o novo, 100% verificaram como ensinado e 100% falharam. Os 9 erros de `globals` de agosto vêm das 52 execuções de agosto que ainda tinham o prompt antigo.

**Base 3** (`contar_introspeccao_linha.py --fonte <parquet v2>`), a linha que falhou, ContestacaoCivel:

| Mês | Introspecção como verificação de existência | Introspecção em "outro uso" | `try/except NameError` |
|---|---:|---:|---:|
| jun/26 | 3 | 0 | 0 |
| jul/26 | 1.527 | 74 | 95 |
| ago/26 | 709 | 62 | 5.667 |

Nos outros papéis, 9 verificações soltas. Nenhum erro de atribuição dinâmica (`globals()['x'] = …`) nem de leitura por nome.
Os formatos mais comuns de "outro uso" são **verificação por função auxiliar** que o agente escreveu e que chama
`globals()` por dentro: `if not has_var('…'): x = ferramenta(...)`, `x = ensure('…', lambda: ferramenta(...))`,
`if not exists('…')`, `_has('…')`, `_is_filled('…')`, `is_defined('…')`; e `globals_dict = globals()` (4).

**Como a função auxiliar falha (inferência, não vista):** o agente define `def has_var(nome): return nome in globals()` e
depois chama `if not has_var('x'): x = ferramenta(...)`. Definir a função não executa nada; o `globals()` roda quando a
função é chamada, e o sandbox o barra nesse momento — por isso a mensagem é "Forbidden function evaluation: 'globals'" e a
linha que falhou é a da chamada, que não tem `globals()` escrito. Só a linha da chamada está nas fotos; a linha do `def`
não foi vista. Para virar fato: contar, no código do passo com erro (`error_code_action`), as funções definidas com
`globals()` dentro.

**Conclusão:** a instrução "verifique se a variável existe" do prompt do ContestacaoCivel causa os dois sintomas: introspecção
(prompt antigo, sem dizer como) e `try/except NameError` (prompt novo, que manda esse jeito). O sandbox barra os dois.
É um sinal de harness com dois sintomas, não uma lição de memória.

### A · A evidência, achado por achado

| Achado | Fato ou inferência | Fonte | Comando que reproduz |
|---|---|---|---|
| O prompt antigo (jul/26) manda verificar sem dizer como; 1 de 3 execuções verifica com `globals()` e é barrada; as 2 que não verificam passam | fato (base 1, n = 3) | o trace da base 1, nesta máquina; trecho do prompt citado acima | `uv run python analysis/2026-09-trace-law-flow-second/scripts/contar_introspeccao_prompt_base2.py --trace <trace da base 1>` (partes C e E) |
| O prompt novo (ago/26) manda `try/except NameError` e proíbe `globals()`/`locals()` | fato (base 2, leitura de 3 casos) | relatório da base 3, §7.9 | — (leitura de casos, 13/10) |
| Prompt antigo: 36 de 127 verificam, todos com introspecção, 35 com erro; 91 não verificam, 1 com erro. Prompt novo: 97 de 97 com `try/except`, 97 com erro | fato (base 2) | fotos `IMG_5892`–`IMG_5894` (pasta `introspeccaco`) e `IMG_5896`–`IMG_5897` (pasta `introspeccaco_2`), 19/10 | `contar_introspeccao_prompt_base2.py --trace <base 2>` (partes C, D, E) |
| Os 36 erros de introspecção da base 2 são verificação de existência | fato (base 2) | as mesmas fotos, parte D | idem |
| Base 3, ContestacaoCivel: verificação por introspecção 3 / 1.527 / 709 (jun/jul/ago) × `try/except` 0 / 95 / 5.667 | fato (base 3) | foto `IMG_5895` (pasta `introspeccaco`) e `IMG_5898` (pasta `introspeccaco_2`) | `uv run python analysis/2026-10-trace-law-flow-third/pipeline/validacao/contar_introspeccao_linha.py --fonte <parquet v2>` (partes A, B) |
| Os 136 de "outro uso" são, nos formatos mais comuns, verificação por função auxiliar | fato (o formato da linha); o `globals()` dentro da função é inferência | foto `IMG_5898`, parte C | idem (parte C) |
| A introspecção do ContestacaoCivel concentra-se em jul–ago e é 73% da lição do sandbox | fato (base 3) | fotos `IMG_5874`–`IMG_5891` (pasta `U_sandbox_mineracao`): `inventario_papel.csv`, `inventario_mes.csv` | `uv run python analysis/2026-10-trace-law-flow-third/pipeline/especificas/minerar.py U_sandbox --rodada observada_e3ebc8274dcf108c` |
| A instrução causa os dois sintomas (sinal de harness com dois sintomas) | conclusão dos fatos acima | — | — |
| Corrigir o prompt (ou dar um dicionário de estado) faz os dois sumirem juntos | **previsão, a verificar** | — | o monitoramento (`b3 #28`), depois do conserto |

As fotos ficam no iCloud do Rafael (`Analista …/introspeccaco`, `introspeccaco_2`, `U_sandbox_mineracao`); os arquivos
gravados pela mineração ficam na máquina da base, em `pipeline/resultados/mineracao/U_sandbox/`.

### A · Fora do ContestacaoCivel: verificação espontânea? (base 1, 19/10)

- Na base 1, **só o prompt do ContestacaoCivel tem a instrução de verificar** (3 de 3 execuções); nenhum dos outros papéis.
- O único erro de introspecção-verificação fora dele é do `ConversationAgent` (mai/26, segundo passo):
  `user_context = globals().get('…', '…')` — lê a variável com valor padrão. O prompt desse papel não fala em verificar
  variáveis: **a verificação é espontânea** (hábito do agente), não instruída. Na base 3 há ≈ 9 casos assim em outros
  papéis; a parte F do `contar_introspeccao_prompt_base2.py` conta, na base 2, se algum outro papel tem a instrução.
- **Base 2, parte F (19/10, foto `IMG_5899`):** em todos os papéis, só o ContestacaoCivel tem a instrução no prompt (224
  de 224 execuções) e só ele verifica (133 no primeiro passo, 134 em algum passo); nenhum outro papel tem a instrução nem
  verifica. Logo, as ≈ 9 verificações de outros papéis na base 3 são espontâneas, como a do `ConversationAgent` na base 1.
- Consequência para o Ajuste 21: uma regra só pela linha junta a verificação instruída (harness) com a espontânea
  (lição do sandbox).

### A · O teste da regra (b) na base 3 (19/10, foto `IMG_5900`)

`contar_introspeccao_linha.py --fonte <parquet v2>`, parte D — a verificação guarda a criação da variável por uma chamada
("instruída") ou não ("espontânea")?

| Papel | Instruída | Espontânea | Não verifica |
|---|---:|---:|---:|
| ContestacaoCivel (jun/jul/ago) | 2.218 (3 / 1.521 / 694) | 102 (0 / 41 / 61) | 55 (0 / 39 / 16) |
| os outros 7 papéis | **0** | 8 | 1 |

- **Separa os papéis:** nenhum erro de outro papel cai em "instruída" — a regra não leva verificação espontânea para o
  harness.
- **Resíduo no ContestacaoCivel:** 157 erros (6,6%) não saem "instruída" — 102 verificam sem a criação reconhecida na
  linha ou no código, 55 não têm nome verificado reconhecível (ex.: a função auxiliar com um nome entre aspas diferente da
  variável criada). Como todo prompt do papel tem a instrução, provavelmente também são instruídos, em formas que a regra
  não pega. Pela regra (b), ficam no sandbox.

### A · Decisão pendente: o Ajuste 21

Proposta (não aplicada; espera o Rafael): a introspecção proibida usada para verificar a existência de uma variável —
direta (`'x' in globals()`, `globals().get('x')`) ou por função auxiliar (a linha chama uma função com o nome de uma
variável entre aspas e cria essa mesma variável) — sai de `U_sandbox` e entra na unidade do `try/except`, renomeada
`U_verificacao_existencia` (destino harness). Efeito esperado na base 3: ≈ 2.250–2.380 erros mudam de unidade; o total de
erros não muda. → `b3 #46`.

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
