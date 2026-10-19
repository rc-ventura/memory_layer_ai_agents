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

### A · O Ajuste 21 (aprovado e implementado em 19/10)

A introspecção que verifica a variável e guarda a criação dela por uma chamada (regra (b)) sai de `U_sandbox` e entra em
`U_verificacao_existencia` (a antiga `U_verificacao_try_nameerror`), destino harness. Esperado na base 3: ≈ 2.218 erros
mudam de unidade; o resíduo de 157 do ContestacaoCivel fica no sandbox (aceito). → livro-razão, Ajuste 21; `b3 #46`.

## 2b · Depois do Ajuste 21: a mineração na rodada `observada_85706f1e94f88f59` (19/10, fotos `IMG_5905`–`IMG_5907`)

9 passos fechados: **1.436 erros · 1.291 execuções · 10 meses · 16 papéis · 43 nomes**; cobertura **99,7%**; encontro **61
medidas iguais**; memória aprovada no esquema 0.2; 2 erros repetem o nome na mesma execução; 6 listas de imports autorizados.

| Parte | Nomes (erros) | Erros |
|---|---|---:|
| **C · módulo usado sem import** | `json` 415 (10 papéis, 10 meses), `pd` 233 (2 papéis), `re` 5, `datetime` 3 | 656 |
| **E · funções e atributos proibidos** | `__name__` 182, `globals` 142 (o resíduo da regra (b)), `repr` 98, `eval` 49, `locals` 14, `dir` 9, `exec` 8, `__import__` 5, `bytes` 5, `open` 5, `hash` 2, `vars` 1, `__class__` 1, `__doc__` 1, `__len__` 1 | 523 |
| **B · ferramenta importada como módulo** | `get_document_text` 167, `python_interpreter` 35, `tools` 4, `tool_usage` 2, `tool_functions` 1, `mcp` 1, `mcp_client.tools` 1, `smolagents` 1 | 212 |
| **D · import fora da lista autorizada** | `ast` 8, `copy` 7, `typing` 6, `tabulate` 4, `calendar` 2, `numbers` 2, `textwrap` 2, e 9 nomes com 1 erro | 40 |
| sem nome | — | 5 |

A parte "funções proibidas" do dossiê de 16/10 (antes junto da D) é, depois do ajuste, a maior parte nova: **E**, 523 erros,
ainda concentrada no ContestacaoCivel (`__name__` 172 de 182, `eval` 46 de 49, `repr` 54 de 98, e o resíduo de `globals`).
Se ela vem também do prompt desse papel é pergunta aberta — o Ajuste 21 só cobriu a verificação de existência.

## 2c · A parte E em investigação (decisão do Rafael, 19/10)

Os destinos de B, C e D estão decididos (`decisoes.md`, 19/10): **C → memória global**, **B → memória do `OBFCivel`**,
**D → memória por papel**. A parte E só vira memória depois de responder: **ela também vem do prompt do
`ContestacaoCivel`?** Se vem, é sinal de harness (como a verificação de existência) e uma memória "não chame `eval`"
brigaria com o prompt; se é uso espontâneo, é memória.

**O que a base 1 já mostra (19/10, aqui; 3 execuções do `ContestacaoCivel`, poucas para responder):** os 7 erros da
parte E estão todos **fora** do `ContestacaoCivel` e são espontâneos — `repr` 3 e `dir` 1 dentro de um `print` (depuração),
`type(x).__name__` 1 (nome do tipo, num `print`), `eval(str(...))` 1 (ler a observação como lista), `globals().get(...)` 1.
Nenhum prompt desses papéis menciona `__name__`, `type(`, `repr`, `eval` ou `except Exception`. O prompt de julho do
`ContestacaoCivel` também não menciona nenhum desses; o que ele tem perto disso é a instrução de **acumular as seções com
falha** ("→ acumule: secoes_geradas (dict), secoes_com_falha (lista)") — uma candidata a origem do `type(e).__name__`, se é
assim que o agente registra a falha. É hipótese até o teste.

**Os testes (rodar na máquina da base):**

| Base | Script | Responde |
|---|---|---|
| 3 | `pipeline/validacao/contar_proibidas_linha.py --fonte <parquet>` | para que o agente usa cada função barrada (nome do tipo da exceção, nome do tipo, depuração, converter texto, função auxiliar…), por grupo `ContestacaoCivel` × outros e mês; se a linha está num bloco `except`; se o código tem a verificação instruída |
| 2 | `scripts/contar_proibidas_prompt_base2.py --trace <trace>` | se o prompt de cada execução menciona os termos (versão do trecho, por papel); as linhas do prompt do `ContestacaoCivel` com os termos; se o nome barrado está escrito no prompt |

**Como ler:** se, no `ContestacaoCivel`, o uso dominante for "nome do tipo da exceção" dentro de `except` (e a base 2
mostrar a instrução de registrar falhas), a origem é o prompt → harness, com a lição "registre a falha com `str(e)`, não
`type(e).__name__`" ao lado; se for depuração ou converter texto, espalhado e sem termo no prompt → memória (global, com
os nomes do papel). O teste da base 1 com o script da base 2 (mesmo formato) deu 7 erros, os da tabela acima.

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

### 2c · O resultado dos testes da parte E (19/10, fotos `IMG_5920`–`IMG_5928`)

**Base 3** (`contar_proibidas_linha.py`): **523 erros** (o esperado), **450 no ContestacaoCivel** (jul–ago/26) e 73 nos
outros papéis. O uso da linha que falhou, no ContestacaoCivel:

| Nome | Erros | Uso dominante | Forma mais comum (mascarada) |
|---|---:|---|---|
| `__name__` | 172 | nome do tipo 157, num `print` (nome do tipo da exceção 10) | `print('…', type(provas_brutas_json).__name__)` |
| `globals` (resíduo da regra (b)) | 137 | verificação de existência 124, função auxiliar 7 | `if '…' not in globals(): id_processo = '…'`; `missing = [v for v in required_vars if v not in globals()]` |
| `repr` | 54 | depuração (`print`) 52 | `print('…', repr(peticao_json)[:5000])` |
| `eval` | 46 | **função auxiliar 40** | `if not _exists('…'): peticao_json = get_peticao_inicial_from_pasta(...)` (também `defined('…')`, `exists('…')`) |
| `locals` | 10 | verificação de existência 10 | `if '…' not in locals(): analogas_json = '…'` |
| `dir` 9, `exec` 8, `__import__` 5, `bytes` 5, `hash` 2, `__class__` 1, `vars` 1 | 31 | — | `__import__('…').loads(peticao_json_str)` (o `json` por `__import__`) |

Contexto no código (tabela D): o código do passo tem a verificação instruída (`except NameError` / `in globals()`) em
**44 de 46** erros de `eval`, 117 de 137 de `globals`, 10 de 10 de `locals`; em 6 de 172 de `__name__` e **0 de 54** de
`repr`. Nenhuma linha está dentro de um `except`. Nos outros papéis: `repr` 44 (depuração 43, ex.:
`print(repr(docs_with_obligations[:500]))`), `__name__` 10, `globals` 5, `open` 5, `locals` 4, `eval` 3.

**Base 2** (`contar_proibidas_prompt_base2.py`, trace completo): só **7 erros** da parte E (ContestacaoCivel `repr` 4,
`__name__` 1, `globals` 1; CalculoTrabalhista `open` 1) — pouco para testar o prompt. **Nenhum prompt menciona** `__name__`,
`type(`, `repr`, `eval` ou `exec(` (nome escrito no prompt: 0 em todos). Todos os prompts do ContestacaoCivel falam de
falha (`secoes_com_falha`, 224 de 224); uma versão (`caaf94536d`, 20 execuções) traz a política de erros com
`except Exception` e `traceback` — e 0 erros da parte E.

**A leitura (hipótese até a decisão):** a parte E tem duas causas no ContestacaoCivel:
1. **a verificação instruída feita por outro meio** — `eval` dentro de uma função auxiliar que verifica e guarda a criação
   da variável por uma chamada (`if not _exists('x'): x = ferramenta(...)`, o mesmo comportamento do Ajuste 21, que só
   olhou `globals`/`locals`/`vars`) e a verificação com valor padrão (`if 'x' not in globals(): x = '…'`, que a regra (b)
   deixou no sandbox). O corpo da função auxiliar não foi visto (inferência, como no Ajuste 21);
2. **a inspeção de depuração** — `print(type(x).__name__)` e `print(repr(x))` sobre o retorno das ferramentas,
   espontânea (nenhum prompt pede; aparece também nos outros papéis) → memória: inspecionar com `print(type(x))` e
   `print(str(x)[:n])`.

**Decisão do Rafael (19/10): Ajuste 23** — o `eval` da função auxiliar de verificação (o item 1 acima, só a parte do
`eval`; ≈ 40 erros) vai para `U_verificacao_existencia`. A verificação com valor padrão (`if 'x' not in globals(): x = '…'`)
segue no sandbox pela regra (b) do Ajuste 21. A confirmar na rodada nova da base 3.

### 2c · A divisão no script (emenda 4, Ajuste 22, 19/10)

O script passa a montar **uma memória por parte**: `U_sandbox.C` (global), `U_sandbox.B.<papel>`, `U_sandbox.D.<papel>`
e `U_sandbox.E` (global, destino em aberto). As fechadas (C, B, D) entram no catálogo `analysis/registros/memorias.json`;
a E fica fora até a investigação acima. Ensaio na base 1: 4 memórias, 3 no catálogo. Na base 3: falta a rodada nova
(o esquema 0.3 entra no hash do código) e a revalidação.

## 2d · O fechamento na base 3: rodada `aedb9b5db70d6c92` (19/10, fotos `IMG_5929`–`IMG_5936`)

Código com os Ajustes 21–23 e as emendas 4–6 (a rodada anterior, `85706f1e`, era do código de antes). O primeiro
`minerar.py` parou no passo 7 com **35 erros só na auditoria** (`funcao_proibida`): a auditoria da máquina da base ainda era
a de antes da emenda 5; com a auditoria nova, fechou.

| Passo | Resultado |
|---|---|
| 3 · parte genérica | **1.401 erros** · 1.259 execuções · 10 meses · 16 papéis (eram 1.436: o Ajuste 23 tirou **35** `eval`, que caiu de 49 para 14) |
| 4 · parte específica | script aprovado · 1.401 erros lidos · 43 nomes |
| 5 · confiança | cobertura **99,6%** (limiar 95%) |
| 6 · destino | 6 listas autorizadas; 2 erros repetem o nome na mesma execução |
| 7 · auditoria e encontro | **75 medidas iguais** |
| 8 · arquivo final | **14 memórias** aprovadas no esquema 0.3 |
| 9 · saída | 35 arquivos no manifesto · catálogo: **14 fechadas, 0 fora** · varredura limpa |

| Memória | Erros | Execuções | Papéis | Meses |
|---|---:|---:|---:|---:|
| `U_sandbox.C` (global) | 656 | 554 | 10 | 10 |
| `U_sandbox.E` (global) | 488 | 461 | 13 | 9 |
| `U_sandbox.B.OBFCivel` | 211 | 210 | 1 | 5 |
| `U_sandbox.B.RespostaBacen` | 1 | 1 | 1 | 1 |
| `U_sandbox.D.CalculoTrabalhista` | 14 | 13 | 1 | 6 |
| `U_sandbox.D.OBFCivel` | 5 | 5 | 1 | 3 |
| `U_sandbox.D.RespostaBacen` | 5 | 5 | 1 | 4 |
| `U_sandbox.D.JoogleAnalytics` | 4 | 4 | 1 | 3 |
| `U_sandbox.D.CalculoCivel` | 3 | 3 | 1 | 1 |
| `U_sandbox.D.Consultivo` | 3 | 3 | 1 | 3 |
| `U_sandbox.D.ContestacaoCivel` | 3 | 3 | 1 | 1 |
| `U_sandbox.D.AgenteTestemunhas` | 1 | 1 | 1 | 1 |
| `U_sandbox.D.OficiosResposta` | 1 | 1 | 1 | 1 |
| `U_sandbox.D.RespostaOficios` | 1 | 1 | 1 | 1 |

Guidances (do resumo; truncadas na foto): C "Importe antes de usar: json, pd, re, datetime."; B "As ferramentas já estão no
escopo como funções: chame-as direto, sem import. Não importe: …"; D, por papel, "Não importe: …; imports autorizados
neste papel: …"; E "Não chame: globals, repr, eval, locals, dir, exec, `__import__`, bytes, open, hash, vars; Não acesse: …"
+ o complemento fixo. **Observação:** 6 das 14 memórias têm 1 a 3 erros (B.RespostaBacen e D em 5 papéis): o catálogo
as registra como estão; a régua de memória rara (`monitoramento.json`) é o próximo filtro, se o Rafael quiser.

## 2e · Os prompts dos papéis de B, C e D (base 1, 19/10, depois do fechamento)

Os destinos de C, B e D (memória) foram decididos sem ler os prompts desses papéis; só a parte E foi testada contra
prompts. A base 1 (trace completo) tem o prompt de todos os papéis. Comando:
`uv run python analysis/2026-09-trace-law-flow-second/scripts/contar_ferramentas_prompt_base2.py --trace analysis/2026-09-trace-law-flow/data/85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz`
(o mesmo script é o teste na base 2).

- **B — provável sinal de harness.** O prompt do OBFCivel (base 1: 11 execuções, uma versão, abr–ago/26) manda "If you
  need to read the raw text of a specific document, use `get_document_text` with the document's `cod_hash_arqu_juri`",
  mas **`get_document_text` não está entre as ferramentas declaradas** (os `def` do prompt: `extract_documents_metadata`,
  `extract_obf_requests`, `final_answer`, `get_docs_from_filters`, `get_fields_definition`, `get_final_answer_schema`).
  O agente tenta importá-la e o sandbox barra: na base 3, 167 dos 212 erros de B. Se vale na base 2, o conserto é no
  prompt (declarar a ferramenta ou tirar a instrução), e a memória atual ("chame-as direto, sem import") **mandaria
  chamar uma função que não existe**. A base 1 não tem erro de B (0); `python_interpreter` não aparece no prompt.
- **C — memória, com um empurrão do prompt.** Os 16 papéis têm a lista de imports autorizados, com `json` e `pandas`
  onde cabe. Mas o retorno de algumas ferramentas é descrito com `pandas` sem falar em import: CalculoTrabalhista ("json
  que pode ser lido com `pd.read_json(io.StringIO(saida))`", 6 de 8 execuções) e JoogleAnalytics ("o resultado da
  consulta como pandas DataFrame"), o papel de 231 dos 233 erros de `pd` na base 3.
- **D — memória de valor incerto.** A lista de imports autorizados já está em **todos** os prompts (16 de 16 papéis):
  a memória D repete o que o prompt diz e o agente ignora.

**Enquanto a base 2 não responde:** o catálogo fica como está, com `U_sandbox.B.OBFCivel` **em verificação**
(`b3 #49`).

## 2f · O degrau 2 (conferida) das 14 memórias — o que falta (19/10)

A escada de validação está em [`17-validacao-memorias.md`](../../../2026-09-trace-law-flow/docs/17-validacao-memorias.md).
As 14 memórias estão no degrau 1 (candidata). O degrau 2, checagem por checagem, com o que já se sabe:

| Memória | 1 · ambiente | 2 · conflito com o prompt | 3 · repete o prompt | 4 · recorrência | 5 · uma causa só |
|---|---|---|---|---|---|
| **C** (global) | **falha:** manda importar `pd` também nos papéis sem `pandas` na lista (Consultivo, OBFCivel, OficiosResposta, RespostaOficios, ContestacaoCivel, e outros sem a lista na base 3) | não (o prompt descreve retornos em `pandas`, empurra o `pd`, não contradiz) | não | ok (554 exec, 10 meses) | ok |
| **E** (global) | a conferir: as alternativas (`print(type(x))`, `str(x)[:n]`, `json.loads`) são permitidas? `json` está nas 6 listas | **falha provável:** "não chame `globals`" × o prompt do ContestacaoCivel que manda verificar a variável | não | ok (461 exec, 9 meses) | **falha:** junta a depuração com a verificação com valor padrão (~134) e o `eval(texto)` |
| **B.OBFCivel** | **falha provável:** `get_document_text` não é ferramenta declarada (base 1) — `b3 #49`, falta a base 2 | **falha provável:** o prompt manda usar `get_document_text`; a memória diz "chame direto" | não | ok | a conferir: `get_document_text` (167) × `python_interpreter`/`tools`/`mcp` (44) podem ter causas diferentes |
| **B.RespostaBacen** | a conferir (`python_interpreter`) | a conferir | não | **falha** (1 exec, 1 mês) | ok |
| **D** (10 por papel) | ok (por construção: só nomes fora da lista, e a lista do papel) | não | **falha:** a lista já está no prompt dos 16 papéis (base 1) | **falha em 5** (AgenteTestemunhas, CalculoCivel, OficiosResposta, RespostaOficios, ContestacaoCivel); ok em 5 | ok |

**Para fechar o degrau 2 do sandbox:**
1. **o script do degrau 2** (`conferir_memorias.py`, no kit), que roda as cinco checagens sobre o catálogo, as listas e
   o prompt de cada papel, e grava o resultado; as checagens 1 (ferramentas), 2 e 3 rodam na base 2 (prompt completo);
2. **a base 2:** rodar o script lá (fecha também o `b3 #49`);
3. **as correções no script específico** (com revalidação): C com o `pd` só nos papéis que têm `pandas`; E sem a parte
   de verificação; B conforme o `#49`;
4. **as decisões do Rafael:** D (repete o prompt — manter, monitorar ou descartar) e as 6 que falham na recorrência
   (`b3 #48`); o destino da verificação com valor padrão (harness, junto do grupo A, ou memória);
5. **a mineração de novo** na máquina da base e o catálogo atualizado, com o degrau de cada memória.

## 3 · A memória que o script montou (antes da emenda 4)

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
