# Racionais da família "Protocolo do harness" — continuação de `01-racionais.md`

**Para que serve este documento:** o mesmo papel do [`01-racionais.md`](01-racionais.md), mas só para uma família de
erro: "Protocolo do harness" — o erro *"Your code snippet is invalid, because the regex pattern `<code>(.*?)</code>`
was not found in it"* (assinatura "Resposta sem bloco de código", unidade `H_bloco_code`). Explica **por que** a
investigação é feita assim e **o que** cada mecanismo é. Os números por base estão em
[`11-relatorio-protocolo-harness.md`](11-relatorio-protocolo-harness.md); o roteiro para repetir numa base nova, em
[`12-procedimento-protocolo-harness.md`](12-procedimento-protocolo-harness.md). A história, com as correções na ordem
em que aconteceram, fica no livro-razão ([`../../pipeline-entre-bases.md`](../../pipeline-entre-bases.md), Etapa 10b).

**Por que um conjunto próprio (30/09/2026).** A família apareceu nas duas bases com causas diferentes — na base 1, uma
troca de **modo** e um **contrato de ferramenta**; na base 2, uma troca de **modelo**. O que se aprendeu estava espalhado
entre o livro-razão e uma linha em cada doc. Aqui fica num lugar só, com o **catálogo de mecanismos** no centro, para que
a base 2 e a base 3 sejam investigadas procurando os mesmos padrões.

---

## 1 · O que é a família

O agente é um `CodeAgent` do smolagents: a cada step o LLM escreve um texto, o harness procura nele o bloco de código,
executa e devolve a observação. O erro desta família é o harness **não achar o bloco**. Nada foi executado; o step
se perde.

- **Não é código Python errado** (isso é "Geração de código"): aqui não há código nenhum para rodar.
- **É plataforma na cor** (cinza, `paleta.py`): o erro está no contrato entre o LLM e o harness, não no raciocínio do
  agente sobre a tarefa.
- **O agente quase sempre se recupera no step seguinte**: a mensagem de erro mostra o formato certo
  (base 1: 33/33; base 2: 66/69 papéis entregaram resposta depois, 69/69 execuções com resposta).

O custo é **um step desperdiçado** (e, às vezes, um erro em cascata — `U_estado_perdido`, `U_texto_solto`), não uma
execução perdida.

## 2 · Por que o erro pode existir: os dois modos do CodeAgent

O smolagents tem dois modos, cada um com o seu modelo de prompt. A diferença decide se esta família **pode** acontecer.

| Modo | O que o LLM entrega | Como o harness acha o código | Esta família |
|---|---|---|---|
| **JSON estruturado** | `{"thought": …, "code": …}` — formato imposto na geração | lê o campo `code` | **não existe** |
| **Texto com `<code>`** | texto livre com `Thought:` e `<code>…</code>` — as marcas são só instrução ("Always provide … a '<code>' sequence ending with '</code>', else you will fail") | procura o bloco com a regex | **só aqui** |

Duas consequências:

1. **O modo é configuração da plataforma**, não escolha do agente. O `drill_down.py protocolo` [7] identifica o modo de
   cada versão do prompt (hash das linhas de formato — `<code>`, ```` ``` ````, `Thought:`, `final_answer(` — com dígitos
   mascarados).
2. **`</code>` é a sequência de parada**, e as versões novas do smolagents a devolvem ao texto quando a geração para.
   Um `</code>` no fim do texto do erro não prova que o LLM o escreveu: **o que falta é sempre a abertura `<code>`**.

## 3 · A lógica da investigação: sintoma → camada → mecanismo → destino

O sintoma é um só (a regex não achou o bloco). O que muda é **por que o LLM não escreveu o bloco**. A investigação
desce em três níveis, **nesta ordem**:

1. **Camada de configuração — antes de ler qualquer caso.** Três coisas mudam fora do agente e mudam a taxa do erro:
   - **modo** (JSON × texto) — `protocolo` [7];
   - **modelo** que respondeu o step (`model_output_message.raw.model`) — `protocolo` [8];
   - **contrato das ferramentas e texto do negócio no fim do prompt** — `drill_down.py ferramenta <nome>` e
     `protocolo --prompt <versão>`.

   Por que primeiro: **nas duas bases, o surto se explicou por uma troca de configuração**, lida de forma determinística
   no trace — base 1, parte das execuções de out/2025 em modo texto; base 2, o modelo `gpt-5.6-terra` só em ago/2026
   (mesmo papel, mesmo mês, mesmo prompt: `gpt-4.1` 0 erros em 381 steps; o novo, 54 em 478). Ler casos antes disso
   leva a explicar pelo comportamento o que é configuração.
2. **Mecanismo — lendo casos.** Com a camada conhecida, a leitura responde *o que o LLM escreveu no lugar do bloco* e
   *em que momento da tarefa*. Isso nomeia o mecanismo (§4). Quando o texto não basta (o LLM escreveu quase nada), os
   **metadados do step** — tamanho do texto, tokens de saída, motivo de parada — dizem o que o texto não diz
   (`metadados_steps.py`).
3. **Destino — quem corrige** (§5).

## 4 · O catálogo de mecanismos

Cada mecanismo tem: **como reconhecer** (o que o trace mostra), **gatilho** (a camada que o dispara), **destino** e
**status**. Um erro de base nova é classificado **contra este catálogo**; o que não couber é mecanismo novo (hipótese) e
entra aqui.

### M1 — Resposta final fora do envelope

- **O que é:** o LLM chega ao fim da tarefa e escreve **o conteúdo** da resposta — relatório em markdown, o JSON pedido
  pelo negócio, uma pergunta ao usuário, ou até `final_answer("""…""")` — **sem o envelope** `<code>…</code>`.
- **Como reconhecer:** o step seguinte é um `final_answer` com o mesmo conteúdo (reembrulhado). Medida: fração dos
  trechos de 5 palavras do texto do erro que reaparece na resposta do 1º `final_answer` seguinte do papel; antecipou se
  ≥ 50% (`sobreposicao()` e `M1_LIMIAR`, `base_pipeline.py`; `drill_down.py protocolo` [9]). Base 1: managerAgent
  15/21, mediana 97%; RespostaBacen 1/7; ConversationAgent 0/3; CalculoCivel 0/2. A medida foi feita avulsa em 30/09 e
  virou função em 02/10. O limiar de 30/09 não foi registrado: 0,5 é o reconstruído, e reproduz as 4 linhas
  publicadas (qualquer valor em (0,48; 0,52] reproduz). **Limite:** quando o LLM reescreve o texto ao reembrulhar (ConversationAgent, base 1), a sobreposição cai e a
  medida não vê — a leitura confirmou os 3.
- **Gatilho:** modo texto **mais** uma instrução do negócio no fim do prompt que pede o conteúdo sem lembrar o envelope:
  "responda em markdown", "devolva um JSON no formato…", e — no ConversationAgent — *"Se voce não precisar de nenhuma
  tool para responder a pergunta do usuario **pode responder diretamente**"*, que contradiz a regra 1 do próprio prompt.
- **Variante:** "falar com o usuário" em texto (tabela parcial + perguntas) em vez de `final_answer(..., human_request=…)`.
- **Nem sempre se recupera:** na base 2 (CalculoCivel, `11` §2.5), o M1 aparece no meio da cadeia que matou uma
  execução. Veio depois de uma falha silenciosa da ferramenta e foi seguido do M6. O agente alternou entre `print`,
  texto e correção de formato, e nunca chamou o `final_answer`.
- **Destino:** sinal de harness (§5). **Status:** confirmado na base 1.

### M2 — Ferramenta do negócio que concorre com o `final_answer`

- **O que é:** existe uma ferramenta real cujo nome e descrição dizem "resposta final" (`resposta_final`: *"devolve o
  json da resposta gerada para o cliente"*). O LLM a chama, vê o JSON na observação, **conclui que terminou** e escreve a
  mensagem de sucesso em texto — ou declara sucesso sem ela ter rodado ("sucesso falso").
- **Como reconhecer:** o erro vem logo depois de uma chamada dessa ferramenta; `final_answer` nunca é chamado na
  execução, ou só muito depois; às vezes a ferramenta é chamada várias vezes em laço.
- **Gatilho:** o contrato da ferramenta. Na base 1, só a declaração com `json_resposta` (dict aninhado; dez/2025) teve
  erros; a com `resposta_gerada` (texto simples; jan–jun/2026), 0 — mesmo formato e mesmo modelo nos dois períodos.
  Correlação (6 × 20 execuções), não prova. (O `drill_down.py ferramenta` numera as variantes pela quantidade de steps,
  não pelo tempo — por isso os nomes aqui são os do argumento.)
- **Destino:** sinal de harness; memória candidata **por ferramenta** só se reaparecer com o contrato atual.
  **Status:** confirmado na base 1.

### M3 — Digitação do envelope

- **O que é:** o LLM tem a intenção certa, mas erra as marcas: escreve só o plano (Thought) e para antes do código, ou
  abre o bloco com `</code>` no lugar de `<code>`.
- **Como reconhecer:** Thought presente e código 0; ou o código visível, com a tag de abertura errada. O step seguinte
  reescreve o mesmo código com a tag certa. A razão tokens/caracteres é normal (o que ele escreveu, chegou).
- **Gatilho:** nenhum identificado — taxa de fundo do modo texto.
- **Destino:** não-memória (proposta). **Status:** confirmado na base 1 (2 casos).

### M4 — O modelo gasta a saída e entrega pouco ou nada *(base 2)*

- **O que é:** o LLM gasta centenas de tokens de saída, mas **a API entrega quase nada de texto** — um fragmento (uma
  frase, meio JSON, um nome de variável). Sem `<code>` no fragmento, o parse falha. **Não há perda no caminho:** o que o
  smolagents leu é o `content` da API mais o `</code>` que ele devolve (7 caracteres), e todos os outros campos da
  resposta (`tool_calls`, `function_call`, `audio`, `images`) vêm vazios (`metadados_steps.py`, linha `cru:`, 7 casos).
- **Como reconhecer:** `tok_saída` muito maior que `len_texto`/3. Nos steps que funcionam, a razão é de 2,6 a 3,3
  caracteres por token; nos steps do erro, 26 caracteres para 260 tokens, 106 para 300, 144 para 308
  (`metadados_steps.py`).
- **Gatilho:** o modelo `gpt-5.6-terra` (todos os casos lidos). `finish_reason = stop` e sem filtro de conteúdo: não é
  limite de tokens nem filtro — o modelo parou por conta própria. **Descartado:** conteúdo em outro campo da resposta.
  **Mais provável, não comprovado:** os tokens foram gastos em raciocínio interno, que não vira texto — o `usage`
  gravado no trace só tem `prompt_tokens`, `completion_tokens` e `total_tokens`, sem o detalhe de raciocínio. (Na base 1,
  o `o4-mini` também gasta muito mais tokens que texto e entrega a resposta inteira: o que distingue o terra é, depois
  de raciocinar, entregar pouco ou nada.)
- **Consequência de leitura:** o fragmento **não é a resposta inteira** — não se deve ler nele a intenção do modelo
  ("antecipou", "inventou a falha"). Essa leitura foi feita e retirada (30/09; `11` §2).
- **Destino:** plataforma — comportamento do modelo neste modo (trocar o modelo, usar o modo JSON, ou testar o formato
  antes de produção). **Status:** o fato (a API entrega pouco ou nada) está medido em 7 casos; a causa (raciocínio
  oculto) é hipótese.

### M5 — Step vazio silencioso *(base 2)*

- **O que é:** a API entrega o `content` **vazio** (0 caracteres, com tokens de saída > 0). O harness não acusa erro: executa um bloco vazio e devolve
  `Last output from code snippet: None`. No step seguinte o LLM lê o `None`, conclui que a consulta falhou e escreve em
  texto "não foi possível…" — aí sim, erro de parse.
- **Como reconhecer:** `len_texto` 0, `len_código` 0, erro "não", tokens de saída > 0; o step seguinte é o erro.
- **Gatilho:** o mesmo do M4 (é o caso extremo dele: nada chegou).
- **Por que importa:** é um **segundo achado de harness** — uma resposta vazia do LLM passa sem erro e sem registro,
  e o erro aparece um step depois, com outra cara.
- **Destino:** plataforma — **achado de harness** (não "sinal de harness": não é o desenho do prompt induzindo o
  agente, é o harness aceitando uma resposta vazia sem acusar). **Status:** medido em 3 casos (1, 6, 7) e em 2 steps do
  caso 4.

### M6 — Narração com delimitadores capturada como código *(base 2)*

- **O que é:** ao corrigir um erro de formato, o LLM **escreve os delimitadores `<code>`/`</code>` na própria
  explicação** (ex.: "o código deve ficar entre `<code>` e `</code>`"). A regex do harness extrai **tudo** o que está
  entre delimitadores e executa como Python: frases da explicação, a letra "e", reticências.
- **Como reconhecer:**
  - o `model_output` tem mais de um bloco `<code>`, ou delimitadores dentro do pensamento;
  - o `code_action` contém (ou é só) um fragmento de narração;
  - o erro que sai é de sintaxe ou "variável não definida" (`name 'e' is not defined`).
- **O que ele esconde:** os rótulos que o pipeline dá hoje — `U_texto_solto`, `U_estado_perdido`, `U_nome_inventado`,
  `X_causa_nao_identificada` — tratam como erro de código do agente o que é o **harness executando narração**. Contar
  só o `H_bloco_code` subestima o alcance desta família.
- **Gatilho:** um erro de protocolo anterior (o LLM tenta explicar o formato e repete os delimitadores) e o parser que
  junta todos os blocos achados.
- **Destino (proposta):** **sinal de harness** — o parser deveria rejeitar delimitadores no pensamento ou blocos
  ambíguos, ou separar pensamento e ação em campos estruturados (o modo JSON). A lição procedural ("ao corrigir o
  formato, não escreva os delimitadores na explicação; um bloco só; entregue com `final_answer` — `print` não encerra")
  fica **candidata, não promovida**: um caso só.
- **Status:** 1 execução (base 2, CalculoCivel, a do erro crítico; `11` §2.5), 12 steps. A regex reproduzida bate com o
  `code_action` nos 12 (conferido na máquina 2). Frequência nas duas bases: a medir.

## 5 · Quem corrige, e por que (quase) nunca é memória

Três perguntas decidem o destino, na ordem:

1. **O erro some com uma mudança de configuração?** (modo, modelo) → **não-memória, achado para a plataforma**, com dono
   e correção. É o caso dos incidentes: base 1 out/2025 (modo), base 2 ago/2026 (modelo).
2. **O desenho do prompt ou de uma ferramenta induz o erro?** (instrução do negócio que compete com o envelope; nome de
   ferramenta que compete com o `final_answer`) → **sinal de harness**: o conserto na origem (texto do prompt, nome ou
   contrato da ferramenta) resolve todas as execuções de uma vez.
3. **Sobra algo que o agente poderia aprender e que se repete com a configuração atual?** → só aí **memória
   candidata**, com escopo (por ferramenta, por papel).

Por que memória raramente ajuda aqui: o prompt **já ensina** o formato; a mensagem de erro **mostra** o exemplo; e o
agente **acerta no step seguinte**. Uma memória dizendo "use `<code>`" repetiria o que já está no contexto. A parte que o
agente aprende de fato — não supor que o step que falhou rodou — já é a unidade `U_estado_perdido`, na família própria.

## 6 · A hipótese do prompt ambíguo (Rafael, 30/09)

O prompt tem duas vozes. No começo, o modelo do smolagents (em inglês) ensina o envelope. No fim, antes de "Now Begin!",
o texto do negócio (em português) pede o **conteúdo** da resposta — "responda em markdown", "devolva um JSON no
formato…", "pode responder diretamente". No momento da resposta final, o LLM segue a voz mais próxima e esquece o
envelope.

- **A favor:** M1 inteiro na base 1 (managerAgent caso 3 abre com *"conforme solicitado"*; RespostaBacen escreve o JSON
  do negócio; ConversationAgent tem a instrução explícita "pode responder diretamente"). M2 é a mesma ambiguidade vinda de
  uma ferramenta.
- **O que ela não explica:** M3 (erro de digitação, sem conteúdo do negócio) e a base 2 (M4/M5: o modelo gasta a saída e
  entrega pouco ou nada — não há conteúdo do negócio para seguir).
- **Consequência prática:** o conserto de M1/M2 é de prompt: a instrução do negócio dizer *"entregue esse JSON/relatório
  com `final_answer(...)` dentro de `<code>`"*, renomear a ferramenta concorrente, ou o modo JSON.

## 7 · Limites

- **A forma** no `protocolo` [4] (vazio / ```` ``` ```` / dict-JSON / frase) é grossa: não separa M1 de M3 nem M4. O
  mecanismo vem da leitura e dos metadados.
- **A medida de sobreposição** do M1 (`protocolo` [9], desde 02/10) tem falso negativo quando o LLM reescreve, e o
  limiar 0,5 foi reconstruído (o de 30/09 não ficou registrado): indica, não classifica.
- **M4 e M5:** o fato está medido (a API entrega pouco ou nada; o harness aceita o vazio); a causa dos tokens gastos
  (raciocínio oculto) não dá para comprovar com o que o trace grava.
- **Cobertura por leitura é amostral**: 5 dos 21 erros do managerAgent (os que não anteciparam a resposta final) não
  foram lidos.
- **O catálogo ainda não é classificação.** No pipeline, a família inteira é um submecanismo só (`harness_bloco_code`
  → `H_bloco_code`, `NAO`), e os destinos "sinal de harness" de M1/M2 não estão no `DESTINO_MINERACAO`
  (`base_pipeline.py`). Transformar os indicadores do §4 em regras determinísticas — e a família em mecanismos nas
  figuras — é a próxima etapa (mineração da família, como a da nº2/nº10).
- **Nada disso usa LLM na análise**: camadas e metadados são lidos do trace; a leitura de casos é humana.
