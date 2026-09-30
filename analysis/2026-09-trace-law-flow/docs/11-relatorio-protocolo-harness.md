# Relatório da família "Protocolo do harness" — continuação de `02-relatorio-achados.md`

**Data:** 30/09/2026 · **Lógica e catálogo de mecanismos (M1–M5):**
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
| Mecanismos | M1 (20), M2 (6), M3 (2), 5 não lidos | M4/M5 no RoteadorCivel (7 casos lidos; a causa dos tokens gastos é hipótese); resto não lido |
| Investigação | **fechada** (28 com mecanismo lido; 5 do managerAgent declarados "não lidos") | RoteadorCivel explicado (7 casos + metadados + campos crus); CalculoCivel e RespostaBacen a seguir |
| Destino | não-memória / sinal de harness | não-memória, achado para a plataforma (modelo) |

---

## 1 · Base 1 — fechada

### 1.1 Quando e onde

33 erros: **out/2025 24, nov 1, dez 7, fev 1**; zero desde mar/2026. Forma: 31 texto sem marcador de código, 2 em
```` ``` ````. Recuperação: 33/33. Logo depois, 7 erros `U_texto_solto` (cascata).

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

### 2.5 O que falta na base 2

| Papel | Erros | Pergunta | Prioridade |
|---|---:|---|---|
| **CalculoCivel** | 4 | 4 erros numa execução só (fev) — o agente **não** se recuperou? É a execução do único erro crítico da base 2 (limite de passos, 48 steps; item 39)? Se for, é o único caso em que esta família pode ter contribuído para matar uma execução | **1ª** |
| **RespostaBacen** | 4 | M2 de novo? Pelo menos parte cai na declaração `resposta_gerada` (55 execuções × 1 com `json_resposta`). Se for M2, o mecanismo reapareceu em outra base e com outro contrato — pela regra do `10` §5, **vira memória candidata por ferramenta** | **2ª** |
| RoteadorCivel | 56 | os 49 não lidos seguem o mesmo padrão de metadados (M4/M5)? | baixa |
| OBFCivel | 4 | mesmo modelo novo, mesmo mês — provavelmente M4/M5 | baixa |
| CalculoTrabalhista | 1 | `gpt-4.1` em ago — fundo? | baixa |

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
