# Relatório da mineração das unidades nº2/nº10 — continuação de `02-relatorio-achados.md`

**Data:** 16–17/09/2026 · **Fonte:** a mesma do relatório principal — `85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz`
mais as saídas da análise genérica · **Pipeline reproduzível:**
[`mineracao_unidades_n2_n10.ipynb`](../pipeline/mineracao_unidades_n2_n10.ipynb)

**De onde vem:** [`02-relatorio-achados.md`](02-relatorio-achados.md) §6 — a tabela de candidatos a unidade de
memória de onde a nº2 e a nº10 saíram. **Lógica por trás:**
[`06-racionais-mineracao-unidades-n2-n10.md`](06-racionais-mineracao-unidades-n2-n10.md) §9. **Validação:**
[`03-procedimento-validacao.md`](03-procedimento-validacao.md) §1.7–§1.11.

**Numeração preservada.** As seções abaixo continuam numeradas §§6.1–6.3 — eram as subseções finais da §6 do
relatório principal e foram separadas em 18/09/2026, quando a mineração virou análise própria. Referências já
escritas a "§6.x do relatório" seguem corretas, agora neste arquivo.

---

### 6.1 · Mineração das unidades nº2 e nº10 — o schema real, derivado do trace (16/09/2026)

Os 8 passos rodados (Passos 1–3 em 16/09, 4–8 e verificação humana em 17/09), mais o addendum ao Passo 2; saídas
salvas no notebook [`mineracao_unidades_n2_n10.ipynb`](../pipeline/mineracao_unidades_n2_n10.ipynb), §11. Método e réguas em [`06-racionais-mineracao-unidades-n2-n10.md`](06-racionais-mineracao-unidades-n2-n10.md) §9; como foi rodado,
conferido e onde desviou do pré-registro em [`03-procedimento-validacao.md`](03-procedimento-validacao.md) §1.7 e
§1.9; os cinco logs que sustentam a leitura do system prompt em §1.8. **Evidência:** cada resultado abaixo tem uma
pasta em `pipeline/resultados/evidencia/<seção>_<análise>/` com os casos escolhidos por regra, o trace cru de cada um e
uma visão derivada que só espelha o cru (git-ignored, com PII). O resultado final são **dois registros de memória
derivados do trace** — no fim desta seção.

**De qual ferramenta vem cada erro (Passo 1).**

| Unidade | Função de origem | Erros | Ocorrências | Execuções | Meses | Papel | Destino |
|---|---|---:|---:|---:|---:|---|---|
| nº2 | `get_available_documents` | 91 | 86 | 86 | 6 | `ConversationAgent` | candidata |
| nº2 | não resolvido / função auxiliar do agente | 5 | 1 | 1 | 1 | `ConversationAgent` | documentar — atribuição a refazer |
| nº10 | `validar_quebra_sigilo` | 7 | 7 | 7 | 3 | `RespostaBacen` | candidata |
| nº10 | `extrair_evidencias` | 1 | 1 | 1 | 1 | `RespostaBacen` | documentar e monitorar (2ª extração) |
| nº10 | `get_available_documents` | 1 | 1 | 1 | 1 | `ConversationAgent` | documentar e monitorar (2ª extração) |
| nº10 | não resolvido | 1 | 1 | 1 | 1 | `ConversationAgent` | documentar — atribuição a refazer |

- **nº2 — uma ferramenta só (regra (a)).** `get_available_documents` em 91/96 erros (94,8%) e 86/87 ocorrências
  (98,9%) — o plural "ferramentas" do nome da unidade era imprecisão de texto. Os 5 erros restantes são "dict
  iterado como lista" com o `.get` falhando dentro de função auxiliar escrita pelo agente: 4 não resolvidos e 1
  atribuído à própria função auxiliar (`meta_map`); juntos são 1 ocorrência. Mesmo contando os 5 contra, 94,8% ≥
  90%.
- **nº10 — divide (regra (b)).** `validar_quebra_sigilo` tem 7/10 (70%); as outras três origens têm 1 caso cada —
  exatamente 10%, no limite frágil da régua. A unidade passa a ser `(RespostaBacen, validar_quebra_sigilo)`; o
  "conteúdo proposto" atual misturava esse fato com uma regra genérica ("na dúvida, inspecionar `r.keys()`").
- **Bucket de consulta:** vazio — nenhuma função ficou abaixo de 10% da sua unidade sem passar na triagem.

**O schema real (Passo 2).** Lido do objeto que a própria mensagem de erro imprime — só estrutura, nunca valores.
Os dois métodos de leitura concordaram em todos os casos (teste em `03-procedimento-validacao.md` §1.7).

- **`get_available_documents`** — `{'result': [[{hashDocumento: str, tipoExtracaoOcr: str, metadado:
  [{nomeMetadado: str, valorMetadado: str}]}, …], {<campo>: {<valor>: int}}]}`. `result` é uma lista de **dois**
  elementos: na posição 0, a lista de documentos; na posição 1, um resumo com a contagem por valor de cada campo
  (entre 4 e 25 campos, conforme a execução). Estrutura igual nos 86 erros em que o objeto indexado é o retorno
  inteiro, e o agente pediu `[0]` — confirma pelo dado o conteúdo escrito à mão (`r['result'][0]`, nunca `r[0]`) e
  mostra o que ele não dizia: `result[1]` não é documento. **Nos outros 5, o objeto é um documento de dentro da
  lista** — o agente tratou um documento único como lista, um nível abaixo da mesma estrutura (o padrão "desce um
  nível demais" de `01-racionais.md` §3 Passo 8): em **3**, indexado por `[0]` (2) ou por fatia (1), a mensagem
  imprime o objeto direto; nos outros **2**, o código **itera** o documento (`for d in doc`) e chama `.get()` numa
  chave dele — a mensagem só revela essa chave (`hashDocumento`), não o objeto inteiro, mas ela bate com o schema já
  derivado dos outros 89 erros: **confirmação indireta** (17/09, achado da verificação humana do Passo 6 —
  `06-racionais-mineracao-unidades-n2-n10.md` §9, `03-procedimento-validacao.md` §1.9). Em 1 caso os documentos trazem dois campos a mais,
  nulos (`iuDocsId`, `iuDocsTenantId`) — se é mudança ao longo do tempo é pergunta do Passo 4. O `thought` do step
  cita o nome da ferramenta em só 5/91: em 90 casos ela foi chamada num step anterior. *Corrigido em 16/09: a
  primeira leitura descrevia só o primeiro elemento de `result` (ver `03-procedimento-validacao.md` §1.7).*
- **`validar_quebra_sigilo`** — `{vazamento_sigilo: str, justificativa: str}` em 7/7. O agente pediu
  `quebra_sigilo` em 7/7, e o `thought` do step cita `quebra_sigilo` literalmente em 7/7: ele já esperava a chave
  errada antes de escrever o código.

**Sub-unidades documentadas — o que ficou fora da memória, e por quê.** Não viram memória agora (1 caso não é
recorrência), mas não foram descartadas.

| Unidade | Papel | Função | O que aconteceu | Schema lido (Passo 2) | Destino |
|---|---|---|---|---|---|
| nº10 | `RespostaBacen` | `extrair_evidencias` | pediu `informacoes_evidencias` | `{dados_evidencias: [{4 campos}]}` — a própria mensagem do smolagents sugeriu `dados_evidencias` | monitorar na 2ª extração |
| nº10 | `ConversationAgent` | `get_available_documents` | pediu `nom_docm_juri_mode` a um item de metadado, como se os metadados fossem um dicionário por nome | `{nomeMetadado, valorMetadado}` | monitorar na 2ª extração; candidato a entrar no conteúdo da nº2 (mesma ferramenta) |
| nº10 | `ConversationAgent` | não resolvido | colunas inexistentes num DataFrame montado pelo agente | não lido (o objeto é um DataFrame) | atribuição a refazer |
| nº2 | `ConversationAgent` | não resolvido / `meta_map` (5 erros) | `.get` dentro de função auxiliar escrita pelo agente | sem valor na mensagem | atribuição a refazer |

**O que o system prompt diz que cada ferramenta devolve (addendum ao Passo 2).** Duas leituras. Primeiro, o texto
literal com que o bloco `def ferramenta(...)` descreve o retorno — documentação da ferramenta, igual em todos os steps
com erro de cada uma:

| Ferramenta | O prompt diz que devolve | Devolve de verdade (Passo 2) |
|---|---|---|
| `validar_quebra_sigilo` | `{"quebra_sigilo": "SIM" ou "NÃO", "motivo": "justificativa"}` | `{vazamento_sigilo: str, justificativa: str}` |
| `extrair_evidencias` | `{"informacoes_evidencias": [<lista de informações extraídas de cada evidência>]}` | `{dados_evidencias: [{4 campos}]}` |
| `get_available_documents` | `-> object`; *"returns a list of documents and a summary of the kinds of documents"* — nenhuma chave | `{result: [[{documento}], {<campo>: {<valor>: int}}]}` |

Depois, a presença de cada chave no prompt, na forma estrita — como chave de JSON (`'chave':`); as formas frouxas
inflam com prosa e valores de exemplo (teste em `03-procedimento-validacao.md` §1.7).

| Ferramenta | Chave | Real ou errada | Como chave no prompt | Declarada no bloco da própria ferramenta |
|---|---|---|---:|---:|
| `get_available_documents` | `result` | real | 0/91 | 0/91 |
| `get_available_documents` | `metadado`, `nomeMetadado`, `valorMetadado` | real | 0/91 | 0/91 |
| `get_available_documents` | `hashDocumento`, `tipoExtracaoOcr` | real | 91/91 | 0/91 |
| `validar_quebra_sigilo` | `vazamento_sigilo` | real | 0/7 | 0/7 |
| `validar_quebra_sigilo` | `justificativa` | real | 0/7 | 0/7 |
| `validar_quebra_sigilo` | `quebra_sigilo` | **errada** | **7/7** | **7/7** |
| `extrair_evidencias` | `dados_evidencias` | real | 0/1 | 0/1 |
| `extrair_evidencias` | `informacoes_evidencias` | **errada** | **1/1** | **1/1** |

Dois quadros diferentes, com força diferente:

- **`validar_quebra_sigilo` — o prompt declara o contrato errado, em dois lugares.** O bloco da ferramenta diz que ela
  devolve `{"quebra_sigilo": …, "motivo": …}`, e o modelo do JSON final do mesmo prompt repete `"quebra_sigilo":
  "<saída da tool validar_quebra_sigilo>"`. Ela devolve `{vazamento_sigilo, justificativa}` nos 7 casos. O agente pediu
  exatamente a chave declarada em 7/7; `"justificativa"` só aparece no prompt como valor de exemplo. A declaração é a
  mesma no trace inteiro — 2 variantes do bloco, que só diferem na quebra de linha, em 135 steps de 26 execuções
  (dez/2025 e mar–jun/2026) —, e o modelo do JSON final está em 135/135. **O valor também diverge:** o prompt declara
  `"NÃO"`; os 7 objetos trazem `'NAO'` (6) ou `'SIM'` (1), e em 3 dos 7 o código que quebrou compara com o literal do
  prompt (`== "NÃO"`). Com a chave certa, essa comparação seria falsa sem exceção nenhuma — uma falha silenciosa
  possível, ainda não procurada. `extrair_evidencias` repete o padrão num caso só: declara `informacoes_evidencias`,
  devolve `dados_evidencias`, e a ferramenta seguinte, `draft_resposta`, é declarada com um argumento chamado
  `informacoes_evidencias` — o agente escreveu `draft_resposta(informacoes_evidencias=r["informacoes_evidencias"])`.
  Aqui o erro não nasce de informação ausente, e sim de documentação da ferramenta divergente da implementação —
  falha do ambiente, não do agente.
- **`get_available_documents` — o prompt não declara errado; declara incompleto.** Nenhuma chave aparece no bloco, e
  `hashDocumento`/`tipoExtracaoOcr` só aparecem fora dele, no formato de documento que outras ferramentas recebem como
  argumento. A descrição — "uma lista de documentos e um resumo dos tipos de documento" — é exatamente o conteúdo de
  `result` (os documentos na posição 0, o resumo na 1) sem o envelope `{'result': …}`, e o `[0]` que o agente pede nos
  88 erros de índice é o que essa descrição sugere. Nenhuma das 5 variantes do bloco no trace menciona `result`. Mas
  nos dois logs desta ferramenta o retorno impresso, com `result`, **já estava no contexto antes do erro**: o prompt
  omisso é causa plausível, não a única. É lacuna de informação, o tipo de buraco que uma memória factual tapa.
  **Confirmado (17/09):** não existe nenhum canal mais rico escondido no trace além desse texto — o smolagents não usa
  function-calling nativo da API pra essas ferramentas (o único "tool" que a API vê é `python_interpreter`, a caixa de
  execução de código; `tool_calls` e `raw` da resposta da API não trazem schema nenhum). O texto do prompt é, de fato,
  tudo que o agente recebe sobre a ferramenta — não tem informação mais completa sendo perdida na nossa leitura.

**Evidência caso a caso (cinco logs — `03-procedimento-validacao.md` §1.8).** Nos três logs de
`validar_quebra_sigilo`/`extrair_evidencias`, a chave real não está no prompt nem no contexto antes do erro; aparece
pela primeira vez na resposta do step que falhou (o log do `print` do mesmo step e a mensagem de erro, que imprime o
objeto), e o `thought` do conserto nomeia a troca — *"a chave retornada pela validação de sigilo é 'vazamento_sigilo'
e não 'quebra_sigilo'"*. Nos dois de `get_available_documents`, o `thought` do conserto descreve o aninhamento
(*"documentos['result'] é uma lista de listas"*). Dois dos cinco consertos escrevem código que aceita os dois
contratos: `.get("quebra_sigilo", <var>.get("vazamento_sigilo"))` com o valor comparado a `["NÃO", "NAO", "Não",
"Nao"]`, e `docs['result'][0] if isinstance(docs, dict) else docs[0]`. **Os logs mostram a sequência, não provam a
causa:** que a documentação certa evitaria o erro, só o replay contrafactual testa (`06-racionais-mineracao-unidades-n2-n10.md` §9 Passo 7).

**O que a verificação do Passo 6 acrescentou (17/09) — o agente não está sem informação nenhuma, mas erra ao
aplicá-la.** No caso resíduo `3f44a68b…` (`03-procedimento-validacao.md` §1.9), o próprio `thought` do step que
quebrou diz *"a variável `docs` é um dicionário com chave 'result'"* — o agente sabia que `result` existia — e mesmo
assim escreveu `docs['result'][0][0]`, fundo demais (o certo é `docs['result'][0]`). No conserto seguinte, ele ainda
não sabia a profundidade certa e teve que investigar em tempo de execução (`print(type(...))`, `print(len(...))`).
**Não sabemos, com este método, por que ele erra** (é atenção? é como ele generaliza o que já viu? — pergunta de
causa cognitiva, fora do escopo determinístico deste pipeline, registrada em `04-roadmap.md`). **Sabemos que:** (1)
o prompt não declara o schema, em lugar nenhum, nem fora do bloco da ferramenta (0/91, checado no addendum ao Passo
2); (2) não existe outro canal estruturado no trace com essa informação (confirmado acima); e (3) o agente às vezes
já tem algum conhecimento do schema, vindo da própria observação dentro da execução, e mesmo assim erra a aplicação.
As três coisas juntas não decidem a causa — decidem que uma memória com o schema certo tapa um buraco real (não
existe hoje nenhuma fonte confiável, nem externa nem interna, que o agente possa consultar).

**O que o agente fez no step seguinte (Passo 3).**

| Ferramenta | Erros | (1) Troca de chave | … dessas, com guarda de tipo | (2) Conserto silencioso | (3) Sem conserto comparável | Repetiu, sem guarda | Não aplicável |
|---|---:|---:|---:|---:|---:|---:|---:|
| `get_available_documents` (nº2) | 91 | 81 | 17 | 0 | 7 | 1 | 2 |
| `validar_quebra_sigilo` (nº10) | 7 | 6 | 0 | 1 | 0 | 0 | 0 |

- **nº2:** nas 81 trocas a chave nova é `result` (em 1, junto com chaves de documento), e todas batem com o schema do
  Passo 2; o step seguinte roda sem erro em 72/81. Em 17 delas o agente mantém o acesso antigo num ramo alternativo
  (`docs['result'][0] if 'result' in docs else docs[0]`): corrige, mas se protege dos dois formatos — não confia
  que a forma do retorno é estável. Os 7 sem conserto comparável são, na maioria, steps que só inspecionam o objeto
  (`print(type(...))`, `json.dumps`). 1 caso repete o acesso sem guarda e mesmo assim o step seguinte não tem
  erro — não inspecionado. Os 2 "não aplicável" são erros de atributo ("dict iterado como lista"), fora da regra de
  chave/índice.
- **nº10:** 6/7 trocam para `vazamento_sigilo` (1 também lê `justificativa`), todos sem erro no step seguinte. O
  caso restante é um conserto silencioso, e benigno: o agente chama a ferramenta de novo e escreve
  `.get("quebra_sigilo", <var>.get("vazamento_sigilo"))` — a chave declarada pelo prompt com a chave real como
  segundo parâmetro, um código que funciona com os dois contratos (a mesma proteção das 17 guardas da nº2).
- **Dormentes:** `extrair_evidencias` troca para `dados_evidencias` (o step seguinte ainda erra, por outro motivo); o
  caso de metadado de `get_available_documents` troca para `hashDocumento` / `tipoExtracaoOcr`.
- **Nenhuma troca contradiz o schema do Passo 2.** São duas fontes independentes — o objeto que o erro imprime e o
  código que o próprio agente escreveu depois — apontando a mesma chave.

Evidência dos Passos 1–3: `11.1_origem_do_erro/` (12 casos), `11.2_schema_real/` (10), `11.3_prompt_declara/` (3) e
`11.4_conserto/` (os 5 logs).

**O schema é o mesmo em todos os meses? (Passo 4)** Por nível da estrutura — o retorno inteiro ou um documento de
dentro dele —, cada forma comparada com a mais comum do nível. Só os meses com erro são observados.

| Ferramenta | Nível (chaves de topo) | Erros | Meses com erro | Veredito | Leitura estrita |
|---|---|---:|---|---|---|
| `get_available_documents` | `{result}` — retorno inteiro | 86 | 6: dez/2025, abr–ago/2026 | **estável**; 1 com campos a mais em ago/2026 | difere em ago/2026 |
| `get_available_documents` | `{hashDocumento, metadado, tipoExtracaoOcr}` — um documento | 3 | 1: jun/2026 | estável | estável |
| `validar_quebra_sigilo` | `{justificativa, vazamento_sigilo}` | 7 | 3: abr–jun/2026 | **estável** | estável |

- **Nenhuma contradição.** Em 85 dos 86 retornos inteiros a forma é idêntica, nos 6 meses. O único diferente traz
  dois campos a mais nos documentos, nulos (`iuDocsId`, `iuDocsTenantId`), com todo o resto igual — e em ago/2026, o
  mesmo mês em que outros 3 erros têm a forma comum. É variação entre execuções, não mudança no tempo.
- **"Campos a mais" não conta como contradição** porque a memória usa as chaves da forma comum, e elas estão lá. Essa
  definição foi escrita depois de o Passo 2 já ter mostrado o caso — por isso a leitura estrita vai ao lado.
- Evidência: `11.5_estabilidade/` — o primeiro caso de cada mês em cada nível, mais o caso diferente (11 casos).

**Status (Passo 5).**

| Ferramenta | Ocorrências lidas ou confirmadas | Erros lidos ou confirmados | Contradições | Campos a mais | Status | Leitura estrita |
|---|---:|---:|---:|---:|---|---|
| `get_available_documents` (nº2) | 86/86 (100%) | 91/91 | 0 | 1 | **derived-and-checked** | parcial |
| `validar_quebra_sigilo` (nº10) | 7/7 (100%) | 7/7 | 0 | 0 | **derived-and-checked** | derived-and-checked |

**O resíduo fechou em 17/09.** Eram 2 erros da nº2 (jun e ago/2026), os dois `Object hashDocumento has no attribute
get`: o agente percorre um documento como se fosse lista de documentos, recebe as chaves (`hashDocumento`…) e chama
`.get` numa delas — a mensagem não imprime o objeto inteiro, só essa chave. É o mesmo mecanismo "desce um nível
demais" dos outros 3 já lidos, e a chave revelada bate com o schema já derivado dos outros 89 (achado da verificação
humana do Passo 6, `03-procedimento-validacao.md` §1.9). A régua do Passo 2 foi estendida — regra geral (checa
qualquer chave contra o schema já conhecido), não escrita para estes 2 casos especificamente — para reconhecer esse
formato de mensagem como confirmação indireta. **Cobertura por erro sobe de 89/91 para 91/91**; por ocorrência já
era 100% antes (os 2 estavam em execuções com outro erro lido diretamente) — por isso o **status não muda**
(`derived-and-checked`; a leitura estrita continua `parcial`, mas por causa dos "campos a mais" do Passo 4, não do
resíduo). O resíduo de verdade (sem nenhuma evidência) é **0**. Os dois casos — `3f44a68b…` e `aa3de754…` — estão
documentados em `03-procedimento-validacao.md` §1.9; `3f44a68b…` também está na amostra do Passo 6 abaixo.

**Amostra conferida contra o trace cru (Passo 6).** 10 erros sorteados com semente fixa (`20260917`): na nº2, 1 do
resíduo e 4 com objeto lido; na nº10, 5 dos 7 (não há resíduo).

| Fonte conferida | nº2 | nº10 |
|---|---:|---:|
| (1) o objeto da mensagem de erro tem a forma comum *(mesmo leitor do Passo 2 — consistência)* | 4/4 lidos | 5/5 |
| (2) as chaves do schema aparecem no log de `print` que o agente recebeu *(outro texto)* | 5/5 (6/6 chaves) | 5/5 (2/2 chaves) |
| (3) o conserto do agente lê uma chave do schema | 4/4 (`result`; o resíduo é "não aplicável") | 5/5 (4 trocas + 1 `.get` com a chave real de padrão) |

Um detalhe que repete os logs 4–5 de `03` §1.8: na nº2, nos 5 casos o `print` com as chaves está num step **anterior**
ao erro (o agente tinha a estrutura na frente); na nº10, no retorno do **próprio** step que falhou. A leitura dos
arquivos crus confirma as chaves nos 9 objetos lidos. **A verificação humana pré-registrada do Passo 6 está pendente**
— a pasta `11.7_amostra_passo6/` tem o cru dos 10 casos e as instruções no `leia-me.md`.

**O registro final de cada candidata (Passos 7 e 8).** No schema de `01-racionais.md` §8, só com o que os passos
derivaram; `description` e `correction_guidance` saem de um molde fixo. Registro completo em
`pipeline/resultados/unidades_memoria.json` e na saída do notebook §11.8; evidência em `11.8_registro_final/`.

- **nº2 — `(ConversationAgent, get_available_documents)` · status `derived-and-checked`**
  - `description`: "`get_available_documents` devolve `{result: [[{hashDocumento: str, metadado: [{nomeMetadado:
    str, valorMetadado: str}], tipoExtracaoOcr: str}] | {<campo>: {<valor>: int}}]}`. O agente indexou o retorno por
    posição (`r[0]`), como se fosse lista, em 88/91 erros. O bloco da ferramenta no system prompt não declara nenhuma
    chave do retorno."
  - `correction_guidance`: "Ao ler o retorno de `get_available_documents`, use `r['result'][0]`. Forma do retorno:
    `{…}`." — o acesso `r['result'][0]` é o que o próprio agente escreveu em 59 dos 72 consertos que rodaram sem erro.
    *(17/09, achado da verificação humana do Passo 6 — `03-procedimento-validacao.md` §1.9 — motivou tirar o
    contraste "não `r[0]`": o erro dominante é de menos (`r[0]`, 88/91), mas o caso resíduo mostra o oposto —
    `r['result'][0][0]`, fundo demais. A frase diz só o caminho certo, cobrindo os dois sentidos.)*
  - `location`: 91 erros; 10 casos alternando os 6 meses. `impact`: `null`.
- **nº10 — `(RespostaBacen, validar_quebra_sigilo)` · status `derived-and-checked`**
  - `description`: "`validar_quebra_sigilo` devolve `{justificativa: str, vazamento_sigilo: str}`. O agente pediu a
    chave `'quebra_sigilo'`, que não existe no retorno, em 7/7 erros. É a chave que o bloco da ferramenta no system
    prompt declara (7/7 prompts)."
  - `correction_guidance`: "Ao ler o retorno de `validar_quebra_sigilo`, use `r['vazamento_sigilo']`. […] O system
    prompt declara `'quebra_sigilo'` para esta ferramenta; o retorno real não tem essa chave." — acesso escrito pelo
    agente em 6/6 consertos sem erro.
  - `validation.destino`: **harness** (17/09, decidido — ver §6.2). `impact`: **9/21 respostas entregues (43%) com o
    campo regulatório de quebra de sigilo inválido, sem nenhum erro registrado.**
- **O que o registro substitui.** O "conteúdo proposto" da §6 de `02-relatorio-achados.md` era escrito à mão. O da nº2 dizia o mesmo que o derivado
  (`r['result'][0]`) — agora com a forma completa, incluindo que `result[1]` é um resumo e não documento. O da nº10
  misturava o fato com uma regra genérica ("na dúvida, inspecionar `r.keys()`"), que o registro derivado não tem.
- **O que os registros não dizem.** Não medem gravidade (`impact` nulo), não dizem se a memória **basta** — isso é o
  replay contrafactual (`06-racionais-mineracao-unidades-n2-n10.md` §9 Passo 7) — e não cobrem falha silenciosa: erro sem exceção não entra na
  mineração.

**O que isso muda para as duas candidatas.** A nº2 tem o que uma memória factual precisa: o fato, confirmado por duas
fontes independentes, ausente do prompt, e sem nenhum canal mais rico escondido no trace que pudesse supri-lo. **Não
sabemos se essa ausência é a causa completa do erro** — o agente às vezes já tem algum conhecimento do schema, vindo
de observação própria, e erra mesmo assim (acima) —, mas isso não muda o que escrever: o schema certo já está
derivado e validado, e não existe hoje nenhuma fonte confiável (prompt ou memória própria do agente) que substitua a
memória. O conserto na origem — documentar o envelope `result` no bloco da
ferramenta — é barato e não conflita com a memória. A nº10 **foi decidida como harness** (17/09) — ver §6.2.

### 6.2 · Análise funda de `validar_quebra_sigilo` — falha silenciosa medida no payload entregue (17/09/2026)

Racional completo, com a história caso a caso, em [`06-racionais-mineracao-unidades-n2-n10.md`](06-racionais-mineracao-unidades-n2-n10.md) §9, subseções "Execução da
análise funda" e seguintes. Conferência e a retratação registrada em
[`03-procedimento-validacao.md`](03-procedimento-validacao.md) §1.10.

**A pergunta.** Os 7 erros já conhecidos (§6.1) são as leituras que *quebraram* — visíveis, custam retry. Esta
análise mede as que não quebram: o mesmo pedido de chave errada pode passar em silêncio e entregar um valor
incorreto na resposta final, sem nenhum erro no log.

**A medida usada.** Não o código do agente (proxy), e sim **o payload que a esteira entregou** — o `request` que a
ferramenta de submissão recebe está guardado, estruturado, no `action_output` de cada step final. Onde o trace
guarda o resultado de fato, a medida direta substitui a inferência por código.

**O achado.** Das 26 execuções que declaram a ferramenta, 21 chegaram a entregar um payload com o campo
`quebra_sigilo`:

| o que foi entregue no campo | execuções | meses |
|---|---|---|
| `'NAO'` ou `'SIM'` — o valor esperado | 12 | 4 |
| **o dicionário inteiro da ferramenta** (`{justificativa, vazamento_sigilo}`) | **7** | 2 |
| um **texto de 203 caracteres** (a justificativa, não o valor) | **1** | 1 |
| **string vazia** (`''`) | **1** | 1 |

**9 de 21 respostas entregues (43%) trazem no campo regulatório de quebra de sigilo algo que não é `SIM` nem `NAO`**,
em três meses (dez/2025, mai/2026, jun/2026) — sem nenhuma exceção registrada em nenhuma delas.

**Por que o objeto inteiro vaza (7 casos, o mecanismo dominante).** O prompt usa **o mesmo nome**, `quebra_sigilo`,
para o campo da resposta final e para o campo do retorno da ferramenta que ele (erradamente) descreve. Diante do
mesmo nome nos dois lados, atribuir o objeto de um ao outro é a leitura mais natural da instrução — não é descuido do
agente, é a instrução puxando pro erro.

**O campo vazio (1 caso, `dbc472b0…`, dez/2025)** confirma a hipótese que a §11.5 revertida em 16/09 tinha levantado,
sem prova então: `quebra.get('quebra_sigilo', '')` — chave errada, `.get` com padrão vazio, sem exceção, campo em
branco na resposta.

**A grafia do valor (`"NÃO"` declarado × `'NAO'` real, sem acento).** Duas comparações divergentes encontradas, nas
duas o erro de chave já tinha estourado a execução **na mesma linha** — a comparação nunca chegou a ser avaliada.
**O erro de chave blinda o erro de acento hoje; corrigir só a chave liga o segundo, que é silencioso.** Os dois
precisam ser corrigidos juntos.

**Retratação registrada.** A primeira rodada desta análise apontou um caso diferente como "confirmado", por ler
código (`.get` aninhado) sem enxergar que era uma **cadeia** (chave certa com plano B na errada) — o classificador
contava o plano B como leitura que valeu, mesmo nunca executando. A medida direta no payload desmentiu esse caso;
corrigido antes de publicar. Detalhe completo em `03-procedimento-validacao.md` §1.10.

**Decisão.** A regra fixada antes de rodar (≥1 caso confirmado chegando à resposta final → harness) foi atingida —
e por 9 casos, não 1. **`validation.destino` da nº10: harness.** `impact`: os 43% acima. Registrado em §6.1.

**Extensão a outras ferramentas com documentação divergente (mesma sessão).** `get_available_documents` (nº2,
730 chamadas) tem a mesma forma de bug — `.get('documents')`/`.get('summary')`, chaves que não existem no schema real,
sem plano B. Uma exploração inicial, fora do notebook e sem pré-registro, achou 2 casos e não sabia como confirmar
sem ler conteúdo de resposta. **Isso mudou — ver §6.3 abaixo, que substitui essa leitura preliminar.**
`extrair_evidencias` foi checada e descartada para este aprofundamento: só 8 execuções a declaram, 1 erro
conhecido, amostra pequena demais e sem campo único mensurável. Detalhe em `06-racionais-mineracao-unidades-n2-n10.md` §9.

**Ainda não feito:** replicar esta análise na segunda extração; quantificar exaustivamente o achado "guarda sobre
chave fantasma" da §6.3 (`04-roadmap.md`).

### 6.3 · Análise funda de `get_available_documents` — leituras silenciosas, universo completo (17/09/2026)

Racional e pré-registro completos em [`01-racionais.md`](01-racionais.md), "Análise funda da nº2"; conferência e
retratação em [`03-procedimento-validacao.md`](03-procedimento-validacao.md) §1.11; código no notebook, §11.10;
evidência em `resultados/evidencia/11.10_leituras_get_available_documents/`.

**A pergunta.** A nº2 já tem 91 erros que quebram (§6.1). Existe, ao lado deles, leitura da mesma chave errada que
**não quebra** — e, se existe, ela chega a produzir uma resposta final errada (o mesmo tipo de achado que decidiu a
nº10), ou só existe como mecanismo, sem dano medível?

**O método, em uma frase.** Rastrear, por AST, toda chamada a `get_available_documents` no trace inteiro (não só os
91 erros já conhecidos) e toda leitura subsequente da variável entre steps do mesmo papel, classificando cada uma
por chave (real/errada) e por proteção (guardada por um `if`, protegida por `try/except`, ou nenhuma das duas). Dois
mecanismos distintos, os dois quantificados de ponta a ponta, não só o primeiro:

1. **".get sem plano B"** — leitura errada, sem proteção, sem exceção: o `.get` devolve `None` em silêncio.
2. **"guarda sobre chave fantasma"** — um `if 'chave' in retorno` cuja `chave` nunca existe no schema real: o ramo
   que usaria os documentos reais nunca roda, e eles somem por inteiro (não viram um valor errado).

Para os dois, três checagens estruturais na resposta **real** entregue pelo `managerAgent` (nunca a saída
intermediária do `ConversationAgent`, nem conteúdo de documento): `DEGENERADO` (recusa explícita, já validado, do
texto do próprio system prompt — `01-racionais.md` §4); presença literal de `None`/`null` (o valor que o `.get`
sem plano B devolve, se vazar pro texto); e um regex para "parece um dict/objeto Python impresso" (o mesmo
mecanismo da classe "objeto inteiro repassado" da nº10, §6.2 — cobre vazar a estrutura toda, não só `None`).

**O resultado.** 635 papéis declaram a ferramenta; 597 leituras rastreadas. O teste de consistência bateu (as
leituras erradas-e-desprotegidas com erro no step reconciliam com os 91 já conhecidos). **4 ocorrências do
mecanismo 1** — uma por execução (`175cd9f2…`, `26e300f1…`, `910fde1e…`, `a47d6e3b…`), 3 meses (2025-11 ×2,
2026-05, 2026-06) — e **1 ocorrência do mecanismo 2**, no trace inteiro (`15f6ad52…`, 2026-05; abaixo do piso de
recorrência de qualquer candidata a memória, ≥3 execuções e ≥2 meses, `01-racionais.md` §7 Passo 5). Nas 5, o `managerAgent` chega a
um `final_answer` real — a execução não trava — e **nenhuma bate nenhuma das três checagens**.

| Fonte | Confirmado | Consequência medida (3 checagens na resposta real) |
|---|---|---|
| Mecanismo 1 (".get sem plano B") | **sim** — 4 ocorrências, universo exaustivo | 0/4 em qualquer checagem |
| Mecanismo 2 ("guarda sobre chave fantasma") | **sim** — 1 ocorrência, universo exaustivo | 0/1 |
| Dano à resposta entregue | — | não eleva `impact` nem muda `destino` |

**Retratação.** Uma exploração anterior (fora do notebook, sem pré-registro) tinha chamado 2 de 3 casos olhados a
dedo de "confirmado: chega a `final_answer` errado", e citado o caso do mecanismo 2 como "achado mais forte" sem
contar quantas vezes ele acontece — usando uma lista de palavras inventada ("não encontr...", "ausente"...) sobre
a saída **intermediária** do `ConversationAgent`, não a resposta real do `managerAgent`, nem um detector já
testado. Com o universo completo e as três checagens, essa afirmação **não se sustenta** e é retirada — mesma
disciplina do §2 de `01-racionais.md`: os dois mecanismos são reais e agora contados exaustivamente (5 ocorrências
no total, não 2-3 a dedo); o dano à resposta, tal como afirmado antes, não é.

**O que isso muda para a nº2.** `status` (`derived-and-checked`) e `destino` (`memória`) não mudam. `impact`
continua `null` — a mesma razão de sempre: nenhuma proxy inventada substitui uma consequência medida, e aqui as
três consequências medidas deram zero nas duas mecânicas. O que muda é `validation.analise_funda`, de `"pendente"`
para este resultado. **O que isso não prova:** que a resposta entregue nesses 5 casos está factualmente completa
ou correta — só que não há recusa explícita nem corrupção estrutural óbvia no texto. Essa é a pergunta de
*groundedness*, ainda fora de escopo do v1 (`04-roadmap.md` item 1).
