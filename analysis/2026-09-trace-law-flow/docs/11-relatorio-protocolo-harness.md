# Relatório da família "Protocolo do harness" — continuação de `02-relatorio-achados.md`

> **Códigos e siglas** (M1–M6, [1]–[4], S1–S6, `U_…`/`H_…`, Ajuste N, roadmap #N, [conferido]/[assistido]): o que cada um quer dizer está no [glossário](../../glossario.md).

**Data:** 30/09/2026 · **Lógica e catálogo de mecanismos (M1–M6):**
[`10-racionais-protocolo-harness.md`](10-racionais-protocolo-harness.md) · **Como replicar:**
[`12-procedimento-protocolo-harness.md`](12-procedimento-protocolo-harness.md) · **História e correções:**
[`../../pipeline-entre-bases.md`](../../pipeline-entre-bases.md), Etapa 10b.

**Fontes:** base 1 — este repositório (`drill_down.py protocolo`, `protocolo --casos`, `metadados_steps.py`); base 2 —
máquina de compliance, só contagens, nomes de papel, ferramenta e modelo, hashes e sim/não lidos das fotos e das
leituras do Rafael (nenhum texto de caso sai de lá).

## TL;DR

| | Base 1 | Base 2 |
|---|---|---|
| Erros | 33 | 69 |
| Padrão no tempo | incidente em out/2025 (24) + dez/2025 (7) + 2 isolados; **0 desde mar/2026** | **incidente em ago/2026 (61)** + 8 espalhados |
| Camada que explica o surto | **modo** (out/2025) e **contrato de ferramenta** (dez/2025) | **modelo** (`gpt-5.6-terra`, só em ago) |
| Mecanismos | resposta final fora do bloco (20), ferramenta concorrente do `final_answer` (6), marca do bloco digitada errada (2), 5 não lidos | RoteadorCivel: resposta esvaziada pelo modelo + step vazio aceito (7 casos lidos; a causa dos tokens gastos é hipótese). CalculoCivel: resposta fora do bloco + narração executada como código na cadeia do erro crítico. RespostaBacen: resposta fora do bloco 3, ferramenta concorrente 1 (com o contrato antigo `json_resposta`, dez/2025; leitura assistida de 02/10). OBFCivel e CalculoTrabalhista não lidos |
| Investigação | **fechada** (28 com mecanismo lido; 5 do managerAgent declarados "não lidos") | RoteadorCivel explicado (7 casos + metadados + campos crus); CalculoCivel e o erro crítico explicados (§2.5); RespostaBacen lido (§2.6, 02/10) |
| Destino | não-memória / sinal de harness | não-memória, achado para a plataforma (modelo) |

---

## 1 · Base 1 — fechada

### 1.1 Quando e onde

33 erros: **out/2025 24, nov 1, dez 7, fev 1**; zero desde mar/2026. Forma: 31 texto sem marcador de código, 2 em
```` ``` ````. Recuperação: 33/33. Logo depois (`protocolo` [6]): 25 seguidos de step sem erro, 7 `U_texto_solto` e 1
`U_estado_perdido` (cascata; o `U_estado_perdido` faltava aqui até a ressalva B da auditoria de 02/10).

### 1.2 A camada — modo e contrato

| Versão do prompt | Modo | Papéis | Steps | Erros |
|---|---|---|---:|---:|
| `82de8f07` | texto | managerAgent (só out/2025) | 130 | 21 |
| `2f96aa69` | texto | ConversationAgent (só out/2025) | 83 | 3 |
| `a34f495f`, `febfeb55` | **JSON** | managerAgent, ConversationAgent (out/2025 → ago/2026) | 4.590 | **0** |
| `b0f37eea` | texto | RespostaBacen, CalculoCivel (sempre) | 193 | 9 |

- **Incidente 1 (out/2025):** parte das execuções do managerAgent e do ConversationAgent rodou em modo texto naquele
  mês; no resto do tempo, JSON, 0 erros.
- **Dez/2025 (RespostaBacen, 7):** o `resposta_final` declarado com `json_resposta` (dict aninhado + `validade_resposta`;
  47 steps, 6 execuções, só dez/2025) teve os 7 erros; declarado com `resposta_gerada` (texto simples; jan–jun/2026, 88
  steps, 20 execuções), 0. Mesmo formato (`b0f37eea`) e mesmo modelo (`o4-mini`) nos dois períodos — o que muda é a
  declaração da ferramenta dentro do prompt. **Correlação** (6 × 20 execuções; outra coisa pode ter mudado em dez/2025).
  O `o4-mini` é o único modelo do papel: **não** há base para dizer que ele erra mais.

### 1.3 Por papel — o mecanismo

| Papel | Erros | Modelo | Mecanismo | Como se sabe |
|---|---:|---|---|---|
| managerAgent | 21 | `gpt-4.1` (12), não registrado (9) | **M1** em 15 (relatório em markdown, reembrulhado em `final_answer` no step seguinte, sobreposição mediana 97%); **M1 variante** "falar com o usuário" em 1; **5 não lidos** | medida + leitura de 3 |
| ConversationAgent | 3 | `gpt-4.1` | **M1** nos 3: o relatório de sub-agente ("### 1. Task outcome…") em texto (1) ou `final_answer("""…` sem `<code>` e sem Thought (2) | leitura dos 3 |
| RespostaBacen | 7 | `o4-mini` | **M2** em 6 (4 "achou que terminou" depois do `resposta_final`; 2 "sucesso falso"); **M1** em 1 (o JSON do negócio em ```` ``` ````) | leitura dos 7 |
| CalculoCivel | 2 | `gpt-4.1` | **M3** nos 2: só o plano, parou antes do código (nov/2025); `</code>` no lugar de `<code>` (fev/2026) | leitura dos 2 |

Total: M1 20 · M2 6 · M3 2 · não lidos 5 = 33.

**RespostaBacen, reconfirmado em 05/10 por um método reproduzível** (kit de mineração, investigação; dossiê
`pipeline/resultados/dossie_protocolo_RespostaBacen-dez_base1_2026-10-05.md`, no ambiente):
- **Leitura:** dois leitores, às cegas um do outro, concordaram em 5 de 5 casos (kappa 1,00). Os 7 ficaram M2 5 ·
  M1 1 · indeterminado 1.
- **O indeterminado** é um dos 2 "sucesso falso" desta tabela. O sinal de resto impediu a classificação, e a medida
  mostrou que ele tem razão. Os leitores acharam que o `o4-mini` gasta assim em todo step, mas os 2 "sucesso falso"
  entregam 0,08 caractere por token contra 0,66–0,72 nos steps bons do papel: 0,11–0,12 do normal (livro-razão
  Ajuste 15; `10` §4 M4). O texto desses 2 é um resto.
- **Regra contada sobre os 7, sem leitura** ("o step anterior chamou uma ferramenta cujo nome a apresenta como
  resposta final, e o texto não reaparece na resposta final"): pega os 5 M2 lidos, nenhum a mais, e nenhum fora do
  RespostaBacen. Virou regra do pipeline (`drill_down.py protocolo` [10]; Ajuste 16).
- **A declaração do `resposta_final`:** com objeto aninhado na entrada (dez/2025, 47 steps, 6 execuções), os 7 erros;
  com texto simples (jan–jun/2026, 88 steps, 20 execuções), 0. É correlação, como acima.

**Três observações da leitura:**

- **ConversationAgent — a instrução que contradiz o envelope.** O fim do prompt diz *"Se voce não precisar de nenhuma
  tool para responder a pergunta do usuario pode responder diretamente"*. A frase existe **só nesse papel** (não está
  nos prompts do managerAgent, RespostaBacen nem CalculoCivel). O formato do relatório ("Task outcome") **não** está no
  system prompt: chega na tarefa que o managerAgent passa ao sub-agente.
- **A medida de sobreposição não viu o ConversationAgent** (0/3): ao reembrulhar, o LLM **reescreveu** o texto. A leitura
  confirmou M1 nos 3.
- **CalculoCivel — os 2 no 1º step do papel**, com ~120 mil tokens de entrada (os documentos do processo) e razão
  tokens/caracteres normal: o que ele escreveu, chegou; errou só as marcas.

### 1.4 Destino (decisões de 30/09)

| Mecanismo | Destino | Dono / conserto |
|---|---|---|
| Incidente 1 (modo) | não-memória, achado para a plataforma | configuração: manter o modo JSON |
| M1 | sinal de harness | prompt: a instrução do negócio pedir o conteúdo **dentro** de `final_answer` em `<code>`; retirar o "pode responder diretamente" |
| M2 | sinal de harness; memória candidata por ferramenta **só se reaparecer** | renomear a ferramenta ou dizer no prompt que ela não encerra a tarefa |
| M3 | não-memória (proposta) | — fundo do modo texto; o agente se recupera |

---

## 2 · Base 2 — em andamento

### 2.1 Quando e onde

| Bloco | Fato |
|---|---|
| total | **69 erros** |
| mês | **ago/2026: 61** (37,8 por 1k steps, 58 execuções); dez/2025 1, fev 4, abr 2, mai 1 |
| papel | **RoteadorCivel 56** (todos em ago); em ago também OBFCivel 4 e CalculoTrabalhista 1; fora de ago, CalculoCivel 4 (fev, 1 execução) e RespostaBacen 4 (3 meses) |
| forma | 67 texto sem marcador, 2 vazios; mediana **138 caracteres**, tokens de saída mediana **242** |
| recuperação | papel entregou resposta depois em 66/69; execução com resposta em 69/69 |
| cascata | 61 seguidos de step sem erro; 5 `U_estado_perdido`, 3 `U_texto_solto`; nunca repetiu |

### 2.2 A camada — o modelo

Todos os papéis com o erro rodam **em modo texto o tempo todo** (RoteadorCivel e OBFCivel `168d70e2`; RespostaBacen,
CalculoCivel e CalculoTrabalhista `b0f37eea` — o mesmo hash da base 1). O modo explica por que o erro **pode** acontecer;
não explica o surto. O modelo explica:

| Papel | Modelo | Meses | Steps | Erros | Por 1k |
|---|---|---|---:|---:|---:|
| RoteadorCivel | `gpt-4.1-2025-04-14` | mai → ago (381 em ago) | 1.341 | 0 | 0 |
| RoteadorCivel | **`gpt-5.6-terra-2026-07-09`** | só ago | 478 | **54** | **113** |
| RoteadorCivel | (não registrado) | jul, ago | 17 | 2 | 118 |
| OBFCivel | `claude-sonnet-4-5` | abr → ago | 721 | 0 | 0 |
| OBFCivel | **`gpt-5.6-terra-2026-07-09`** | só ago | 22 | **4** | **182** |

Mesmo papel, mesmo mês, mesmo prompt, mesmo modo: `gpt-4.1` 0 em 381 steps de agosto; `gpt-5.6-terra` 54 em 478.
**Incidente 2 = o modelo novo.**

### 2.3 RoteadorCivel — 7 casos lidos (Rafael) + metadados (`metadados_steps.py`)

Todos: `gpt-5.6-terra`, versão `168d70e2`, papel chamado 1 vez na execução (não é cascata entre chamadas), tarefa de 123
caracteres que **não** menciona falha nem traz o molde `fluxo_encerramento`, e o 1º step com a mesma entrada (2.546
tokens).

| Caso | Step do erro | O que ficou visível | Texto (car.) | Tokens de saída | Antes do erro | Leitura |
|---|---:|---|---:|---:|---|---|
| 1 | 2 | frase "não foi possível executar a consulta…" | 89 | 207 | step 1 **vazio**: 0 car., 229 tokens, sem erro | M5 → M4 |
| 2 | 1 | meio JSON com as chaves do retorno do `busca_obf` | 144 | 308 | — | M4 |
| 3 | 1 | só um nome de variável (`resultado_obrigacao`) | 26 | 260 | — | M4 |
| 4 | 1 | o Thought, sem código | 136 | 59 | — | M3? (razão normal); depois 2 steps **vazios** sem erro (M5) |
| 5 | 1 | meio JSON, como o 2 | 106 | 300 | — | M4 |
| 6 | 2 | quase nada | 9 | 149 | step 1 **vazio**: 0 car., 260 tokens | M5 → M4 |
| 7 | 2 | frase "não foi possível consultar…" | 184 | 320 | step 1 **vazio**: 0 car., 255 tokens | M5 → M4 |

Os 7 recuperam: no step seguinte, `<code>` correto chamando a ferramenta de busca de decisões e seguindo a cadeia.
`finish_reason = stop` e sem filtro de conteúdo em todos. Nos steps que funcionam, 2,6–3,3 caracteres por token.
(O `len_texto` inclui o `</code>` que o harness devolve: 26 = `resultado_obrigacao` (19) + 7.)

**Leitura retirada.** Antes dos metadados, os casos 2–5 foram lidos como "antecipou a saída final no molde do
`busca_obf`" e os casos 1, 6, 7 como "falha inventada". Com os metadados, a leitura não se sustenta: **o texto visível é
um resto** — 200 a 300 tokens gerados não viraram texto. Não se lê intenção num fragmento. (O prompt do papel diz que a
saída do `busca_obf` é a resposta final sem mudanças e pede uma ferramenta por step; as chaves nos casos 2 e 5 são as do
retorno declarado do `busca_obf`. Fica registrado; não é a explicação.)

**Campos crus da resposta da API (`metadados_steps.py`, linha `cru:`, 30/09).** Em todos os steps dos 7 casos, a
mensagem da API tem só `content` preenchido; `tool_calls`, `function_call`, `audio` e `images` vêm vazios, sem campo
extra; o `usage` gravado tem só `prompt_tokens`, `completion_tokens`, `total_tokens`. O `content` da API é o que o
smolagents leu menos o `</code>` que ele devolve (caso 3: 19 → 26; caso 6: 2 → 9; caso 7: 177 → 184; steps vazios: 0 →
0). **A resposta não foi para outro campo, e o harness não perdeu nada: a API já entregou curto ou vazio.**

**Leitura atual:** M4 — o terra gasta 150–320 tokens de saída e **entrega pouco ou nada** (`finish = stop`: parou
sozinho); causa mais provável, não comprovável com o que o trace grava, raciocínio interno. M5 — quando o `content` vem
vazio, o harness roda um bloco vazio **sem erro**, e o erro aparece um step depois como "não foi possível" — achado de
harness. Os dois medidos nos 7 casos; a causa dos tokens gastos, hipótese.

Leitura anterior, de 3 outros casos do RoteadorCivel (30/09, livro-razão): frase só; o dict de decisão sem código;
recuperação com `final_answer(answer=…, human_request=…)`. Compatível com M4 (fragmentos).

### 2.4 Conclusão até aqui (30/09)

**Protocolo do harness na base 2 = plataforma (o modelo novo).** Nos 56 erros do RoteadorCivel (81%): sem lição
aprendida (o agente se recupera no step seguinte; o conserto é modelo/modo) e **sem sinal de harness** no sentido do
projeto (nenhum prompt ou ferramenta induzindo o erro). **Um achado de harness** — outra categoria: o harness aceita o
`content` vazio sem erro (M5), aviso à plataforma. Os mecanismos da base 1 (M1/M2) **não** aparecem no RoteadorCivel;
nos 13 erros dos outros papéis, **não verificado**.

### 2.5 CalculoCivel — os 4 erros e o único erro crítico da base 2 (01/10)

**Fontes.**

| Fonte | Tipo | Conteúdo |
|---|---|---|
| `drill_down.py critico CalculoCivel` | determinística, máquina 2 | a fila dos críticos, a ligação ao protocolo e a trajetória por tipo |
| 4 arquivos `protocolo --casos CalculoCivel 4` | leitura do Rafael | — |
| relatório "cascata crítica" (12 fotos) | leitura assistida por LLM (GPT-6.1 Sol, máquina 2) | — |
| relatório "calculadora" (5 fotos) | leitura assistida por LLM (GPT-6.1 Sol, máquina 2) | — |

Abaixo, **[conferido]** = verificado no cru de forma determinística (AST, reprodução da regex, tipo da variável,
contagem); **[assistido]** = leitura do LLM, hipótese.

**Mesma execução.** Os 4 erros de protocolo (idx 20, 30, 35, 40) estão na execução do único erro crítico da base 2
(fev/2026, 49 steps no papel, limite de passos no idx 48). **[conferido: `critico`]**

**A execução tem 4 chamadas do papel**, não uma tentativa contínua. O `idx` do pipeline conta as chamadas juntas, e o
`step_number` recomeça a cada uma. **[conferido: 4 `TaskStep`]**

| Chamada | idx | Steps | Erros | Como terminou |
|---|---|---:|---:|---|
| 1 | 0–16 | 17 | 9 | `final_answer` |
| 2 | 17–19 | 3 | 0 | `final_answer` |
| 3 | 20–27 | 8 | 5 | `final_answer` (a mensagem de que o cálculo não pode ser feito para a data pedida) |
| **4** | **28–48** | **21** | **11** + o limite | **`AgentMaxStepsError`, sem `final_answer`** |

**A cadeia que matou a 4ª chamada:**

1. **idx 28 — a calculadora falha em silêncio.** `calculo_correcoes_monetarias` devolve a string
   `"Error calling tool 'calculo_correcoes_monetarias': 'DEFAULT'"` no lugar do `dict` declarado (`valor_corrigido`,
   `valor_correcao`). A falha volta como **valor**, não como exceção, e o step fica com `error: null`. A variável
   `resultado_corr` no namespace (`txt_vrvl_locl`) é `str`. **[conferido]**
   - Nas 5 chamadas da ferramenta na execução: 4 devolvem esse texto; 1 devolve "data_inicial deve ser anterior ou igual
     a data_final", porque o fallback de data do agente inverteu o intervalo.
   - O que é o `DEFAULT` — provável `KeyError` numa chave ausente da calculadora — **não** se fecha pelo trace: faltam a
     exceção original, o traceback e a implementação. **[assistido]**
   - "O índice não estava disponível" foi a explicação **do agente**, não da ferramenta.
2. **idx 29 — o agente monta e imprime as tabelas.**
3. **idx 30 — responde em texto, sem `<code>`** → erro de protocolo (**M1**). **[conferido]**
4. **idx 31–46 — narração capturada como código (M6, `10` §4).** Ao corrigir o formato, o agente escreve no pensamento
   que o código deve ficar "entre `<code>` e `</code>`". A regex do harness extrai o que está entre os delimitadores e o
   executa. **[conferido: a reprodução da regex bate com o `code_action` nos 12 steps do padrão]**
   - Os casos: frases da explicação viram código (31–32); a letra "e" é executada antes do `print` (33, 41); só "e"
     (44); reticências (46).
   - Os erros resultantes ("variável não definida", sintaxe) recebem os rótulos `U_estado_perdido`, `U_nome_inventado`,
     `U_texto_solto` e `X_causa_nao_identificada`. **Não** são perda de estado nem nome inventado.
5. **O agente diagnostica errado e repete:** atribui a texto oculto, colagem, caracteres especiais. Alterna entre
   imprimir as tabelas, imprimir "ok", responder em texto e corrigir de novo. **Nenhum step da 4ª chamada chama o
   `final_answer`; o `print` não entrega nada ao usuário.** **[conferido]**
6. **idx 48 — limite de passos.**

**Custo da 4ª chamada:** ~2,09 milhões de tokens (entrada + saída, somados por step, com o contexto relido) e ~8,8
min. **[conferido]**

**Persistência.** O `txt_rspa_fina` da execução guarda a resposta da **3ª** chamada; o registro terminal tem
`AgentMaxStepsError`. "Execução com resposta" **não** prova que a última solicitação foi atendida. **[conferido]**

**Leitura retirada (01/10).** Antes do cru, este relatório chegou a dizer:

| Leitura anterior | O que o cru mostrou |
|---|---|
| "4 ciclos do mesmo loop, desde o idx 20" | 4 **chamadas**; a 3ª, que começa no idx 20, terminou bem |
| "morte por acúmulo de 25 erros" | a morte é da 4ª chamada, com 11 erros |
| "o passo crítico é o idx 20" | a cadeia terminal começa no idx 28 (calculadora) e no 30 (protocolo) |

O `critico` induziu ao erro porque a "primeira unidade" mistura as chamadas: mostrou `U_nome_inventado` no idx 1.
Nesse idx 1, aliás, a causa também é outra: o código do idx 0 ficou numa linha só, e tudo depois do primeiro `#` virou
comentário. **[conferido: AST]**

**O que muda para a família:**

- **é a primeira exceção ao "o agente se recupera no step seguinte"**: aqui ele corrigiu o formato, mas não a tarefa;
- o protocolo aparece **no meio de uma cadeia**, depois de uma falha silenciosa da ferramenta;
- **contar só o `H_bloco_code` subestima o alcance** desta família, porque os efeitos do M6 aparecem como erros de
  execução com rótulos de memória.

**Em aberto (não muda a leitura):**

- se o `request`/`accepted` do fim de cada chamada é o pedido ao humano ou o registro da resposta final;
- o que a 4ª tarefa dizia;
- o `DEFAULT` da calculadora.

### 2.6 O que falta na base 2

| Papel | Erros | Pergunta | Prioridade |
|---|---:|---|---|
| ~~CalculoCivel~~ | 4 | feito — §2.5 | — |
| ~~RespostaBacen~~ | 4 | **feito 02/10** (máquina 2, assistido): `o4-mini`, `b0f37eea`, modo texto. **M1 em 3**: JSON do negócio ×2 e pergunta ao usuário, os 3 com `resposta_gerada` e o prompt pedindo formato. **M2 em 1**: dez/2025, logo depois do `resposta_final`, com `json_resposta`. 3/4 recuperam no step seguinte, 4/4 entregam `final_answer` depois. O M2 **não** reapareceu com o contrato atual: segue sinal de harness, já corrigido, não vira memória (`10` §4 M2) | — |
| RoteadorCivel | 56 | os 49 não lidos seguem o mesmo padrão de metadados (M4/M5)? | baixa |
| OBFCivel | 4 | mesmo modelo novo, mesmo mês — provavelmente M4/M5 | baixa |
| CalculoTrabalhista | 1 | `gpt-4.1` em ago — fundo? | baixa |

**M1 medido na base 2 (`protocolo` [9], máquina 2, 02/10).** Antecipou a resposta final / mediana / copiou da
observação anterior:

| Papel | Erros | Antecipou (≥ 50%) | Mediana | Copiou da observação |
|---|---:|---:|---:|---:|
| RoteadorCivel | 56 | 0/56 | 0% | 0/56 |
| OBFCivel | 4 | 0/4 | 0% | 0/4 |
| CalculoCivel | 4 | 0/4 | 0% | **3/4** |
| RespostaBacen | 4 | **2/4** | 56% | 1/4 |
| CalculoTrabalhista | 1 | 0/1 | 32% | 0/1 |

**Leitura:** o surto de ago/2026 **não é M1**. O RoteadorCivel (0/56) escreve pouco (mediana de 138 caracteres) e nada
do que escreve reaparece na resposta — bate com M4/M5 do §2.3, o modelo que esquece as marcas. O RespostaBacen (2/4)
é o único com sinal de M1. A leitura de 02/10 deu M1 em 3: o 3º é a pergunta ao usuário, de 496 caracteres, o falso
negativo conhecido da medida. No CalculoCivel, 3/4 copiam a observação anterior: o texto fora do bloco repete o que a ferramenta tinha
acabado de devolver. Isso pode ser parte da cadeia do erro crítico (§2.5), mas não foi lido. A medida indica; a
leitura confirma.

---

## 3 · Comparação entre bases

| | Base 1 | Base 2 |
|---|---|---|
| Modo | trocou (texto só em out/2025 para 2 papéis) | texto o tempo todo |
| O que disparou o surto | modo; contrato de ferramenta | modelo |
| Onde na tarefa | **no fim** (a resposta final) — M1, M2 | **no começo** (1º e 2º step) — M4, M5 |
| O que o LLM escreveu | texto longo e completo (mediana 2.859 car.) | fragmento curto (mediana 138 car.) com tokens "sumidos" |
| Recuperação | step seguinte | step seguinte |
| Hash comum | `b0f37eea` (RespostaBacen, CalculoCivel) | `b0f37eea` (RespostaBacen, CalculoCivel, CalculoTrabalhista) |

O que vale nas duas: o erro só existe no modo texto; um surto se explica por uma troca de configuração lida no trace;
o agente se recupera; memória não é o conserto.
