# Glossário — os códigos e termos das análises, explicados uma vez

**Para que serve:** os documentos das análises usam códigos curtos (M1, S5, `U_repr_colado`, "o [4]"…) para caber em
tabelas e para o histórico (commits, livro-razão, diário) continuar legível. **Este arquivo diz o que cada um quer
dizer.** Todo documento que usa códigos aponta para cá no topo. Código novo entra aqui no mesmo commit em que aparece.

---

## 1 · Os dois baldes de erro

| Termo | O que é |
|---|---|
| **balde visível** | os erros que levantaram exceção (`ActionStep.error` preenchido). É o que o notebook da esteira classifica (família → assinatura → mecanismo → unidade). |
| **balde invisível** / **falha silenciosa** | a ferramenta falhou, mas devolveu o erro **como texto** (`"Error calling tool '<nome>': …"`), e o step ficou com `error: null`. Para o pipeline, o step "deu certo". Notebook `falhas_silenciosas.ipynb`, docs 13–15. |
| **consolidação** | a etapa que junta as ocorrências dos dois baldes numa triagem só: `consolidacao_unidades.ipynb` (§14.x), Ajuste 12. Desde o plano 4.2c é onde **mora a triagem** (global e por papel) e onde se grava o `candidatos_memoria.csv`. Conta execuções, meses e papéis sobre a união dos canais; erros e tokens continuam do visível. |
| **canal** | de onde vem uma ocorrência de unidade: **visível** (erro com exceção) ou **silencioso** (falha devolvida como texto). A mesma unidade pode ter os dois — hoje, a `U_repr_colado`. |
| **`REGRAS_INVISIVEL`** | as regras que levam uma falha silenciosa a uma unidade do catálogo, sem nome de ferramenta (`base_pipeline.py`). Hoje, uma: JSON inválido com argumento colado de um retorno impresso → `U_repr_colado`. O que não casa fica sem unidade. |
| **ocorrência** | uma **cascata × unidade**, nos dois baldes (decisão de 02/10, aplicada no Ajuste 12): erros — ou falhas silenciosas — seguidos do mesmo papel contam uma vez por unidade. |
| **cascata** | erros consecutivos do mesmo papel na mesma execução. O 1º é o que importa; os seguintes são "seguidores". |
| **trajetória** | um papel numa execução (execução × agente × papel), do primeiro ao último ActionStep. É a unidade de contagem da recuperação depois do erro na base 3 (23/10, `execucao/recuperacao.py`): cada trajetória com erro conta uma vez — um erro só, cascata, recaída, terminou no erro, limite de passos ou indeterminado. |
| **recaída** | numa trajetória, o agente erra, passa ao menos um passo sem erro estruturado e erra de novo mais adiante (duas ou mais cascatas no mesmo papel). Diferente da cascata, em que o erro seguinte vem no passo logo depois. |

## 2 · As unidades de memória (os nomes `U_…`, `H_…`, `X_…`, `C_…`)

O prefixo diz **quem corrige**: `U_` = o agente (candidata a memória), `H_` = o harness ou a plataforma (não é
memória), `X_` = resíduo sem regra (revisar), `C_` = erro crítico (a execução morreu).

| Código | Nome | Em uma frase |
|---|---|---|
| `U_texto_literal` | Texto longo nunca dentro de literal de string | o agente põe um texto grande dentro de aspas no código e quebra a sintaxe |
| `U_contrato_dict` | Retorno das ferramentas de documento é dict | o agente indexa o retorno como lista, mas ele é um dicionário |
| `U_tipo_retorno` | Retorno pode chegar como string | o agente trata como dicionário um retorno que veio como texto |
| `U_campo_inexistente` | Campo inexistente no retorno estruturado | o agente pede uma chave que o retorno não tem |
| `U_texto_solto` | Explicação nunca solta no bloco de código | o agente escreve explicação em prosa dentro do bloco de código |
| `U_arg_nomeado` | Ferramentas só aceitam argumento nomeado | chamada posicional numa ferramenta que exige `nome=valor` |
| `U_sandbox` | Inventário do sandbox | uso de módulo ou função que o ambiente bloqueia |
| `U_next_gerador` | `next()` sobre expressão geradora falha no sandbox | um idioma de Python que o ambiente não aceita |
| `U_estado_perdido` | Após step com erro, o que ele definiria não existe | o agente usa uma variável que o step com erro nunca chegou a criar |
| `U_nome_inventado` | Nome usado sem ter sido definido | o agente usa um nome (variável ou função) que não existe |
| `U_verificacao_existencia` | Verificação de existência de variável (instruída pelo prompt) | o prompt manda checar se uma variável já existe antes de chamar a ferramenta, e o sandbox barra as duas formas: `'x' in globals()` (proibida) e `except NameError` (não pega o erro do sandbox); destino harness. Era `U_verificacao_try_nameerror` (Ajuste 17), renomeada e ampliada à introspecção no Ajuste 21 |
| `U_ferramenta_nao_declarada` | Ferramenta citada no prompt e não declarada | o prompt manda usar uma ferramenta que não está entre as declaradas (os `def` do prompt), e o agente tenta importá-la; sinal de harness — o conserto é declarar a ferramenta ou tirar a menção (Ajuste 26, 20/10/2026; hoje só `get_document_text`, no OBFCivel) |
| `U_verificacao_try_nameerror` | — | nome antigo de `U_verificacao_existencia`, até o Ajuste 21 (19/10/2026); aparece nos documentos de antes |
| `U_repr_colado` | Não colar retorno impresso de volta no código | o agente copia o print de um retorno para dentro do código em vez de usar a variável |
| `U_codigo_lento` | Não rodar laço pesado dentro do bloco de código | o tempo do interpretador estoura num laço sem ferramenta |
| `U_resultado_bruto` | Não entregar o resultado bruto de uma ferramenta na resposta final | o agente põe o retorno inteiro da ferramenta no `final_answer` e estoura o tempo |
| `H_bloco_code` | Protocolo do harness | a resposta do modelo veio sem o bloco `<code>…</code>` que o harness exige (família própria, docs 10–12) |
| `H_timeout_ferramenta` | Ferramenta excedeu o timeout | a ferramenta demorou mais que o limite — conserto na plataforma |
| `H_infra_llm` | Falha do LLM upstream | o serviço do modelo falhou — política de retry |
| `C_limite_passos` | Limite de passos atingido | a execução morreu sem se recuperar ("erro crítico") |
| `X_causa_nao_identificada` | Causa não identificada | o sintoma é conhecido, a causa não tem regra |
| `X_sintoma_nao_reconhecido` | Sintoma não reconhecido | nenhuma regra reconhece a mensagem — cobertura |

**Decisões da triagem:** *candidata* = passa na régua de recorrência (≥3 execuções e ≥2 meses) e vira memória
candidata; *sinal de harness* = recorrente, mas quem corrige é o prompt ou a ferramenta, não a memória; *não-memória* =
plataforma; *fora: sem recorrência* = não passou na régua; *revisar* = resíduo.

**Lista do prompt × lista do interpretador:** *lista do prompt* = os módulos que o system prompt anuncia ("You can use
imports in your code, but only from the following list of modules: [...]"); *lista do interpretador* = os que o sandbox
aceita (a da mensagem "Import of X is not allowed. Authorized imports are: [...]", e os imports que rodam). No smolagents
saem da mesma configuração, mas na plataforma podem divergir (21/10: o `json`); o degrau 2 confere o ambiente pela do
interpretador.

**Tipos de monitoramento** (o `tipo` de um item do `registros/monitoramento.json`, no nível da unidade, ou de uma
memória no catálogo `registros/memorias.json`, no nível da memória — os dois níveis: `16`, "O monitoramento"): *sinal de harness* = espera o conserto da
plataforma (o alarme que importa é "sumiu"); *memória rara* = espera ficar frequente (o alarme é "passou na régua");
*memória de reforço (repete o prompt)* = a memória só repetiria o que o prompt já diz e não é injetada (alarmes: "cresceu",
e, nas bases com prompt, "o prompt deixou de dizer" — aí deixa de ser repetição e vira candidata). Decidido em 20/10/2026
(`decisoes.md`); o experimento de reforço é o EX-8 do blueprint das POCs.

## 3 · Os mecanismos do erro de protocolo (M1–M6)

A família `H_bloco_code` — "a resposta veio sem o bloco de código" — tem seis mecanismos, descritos em
[`2026-09-trace-law-flow/docs/10-racionais-protocolo-harness.md`](2026-09-trace-law-flow/docs/10-racionais-protocolo-harness.md) §4.

| Código | Nome | O que acontece | Quem corrige |
|---|---|---|---|
| **M1** | resposta final fora do bloco | o modelo escreve a resposta final (relatório, JSON pedido, pergunta ao usuário) sem o bloco `<code>`; no step seguinte reembrulha em `final_answer` | o prompt (sinal de harness) |
| **M2** | ferramenta concorrente do `final_answer` | uma ferramenta chamada "resposta final" faz o modelo achar que já terminou | o contrato da ferramenta (sinal de harness) |
| **M3** | marca do bloco digitada errada | intenção certa, tag errada (só o plano, ou `</code>` na abertura) | ninguém — taxa de fundo |
| **M4** | resposta esvaziada pelo modelo | o modelo gasta centenas de tokens e entrega pouco ou nada de texto | a plataforma (modelo/modo) |
| **M5** | step vazio aceito | a resposta vem vazia e o harness roda um bloco vazio sem erro | o harness |
| **M6** | narração executada como código | o harness concatena trechos do pensamento e executa narração como se fosse código | o harness |

## 4 · As medidas do balde invisível ([1]–[4])

Os números entre colchetes são as seções da saída do `drill_down.py silenciosas` e do notebook §13.

| Código | Nome | Pergunta |
|---|---|---|
| **[1]** | por ferramenta | onde as falhas silenciosas se concentram |
| **[1b]** | por grupo do motivo | o que a ferramenta reclamou: sem resultado · fora da cobertura · argumento do agente · plataforma · JSON inválido · não reconhecido |
| **[2]** | o que vem depois | o 1º erro com exceção do mesmo papel nos 3 steps seguintes (se nenhum, a falha passou sem rastro) |
| **[3]** | contrato precedido | quanto das memórias de contrato de retorno vem logo depois de uma falha silenciosa |
| **[4]** | candidato a sucesso falso | a ferramenta falhou de verdade e o papel entregou a resposta final sem ela ter funcionado — **teto**, só a leitura confirma |
| **[4b]** | sucesso falso conferido (proposta) | o mesmo, conferido pelo estado final das variáveis (`txt_vrvl_locl`) — `transversal #1` (antigo plano 4.1c) |

**Sucesso falso** = a execução parece ter dado certo, mas a resposta usa um dado que a ferramenta não entregou.
**Desfecho de uma falha real de ferramenta** (o que aconteceu com a tarefa — não é família, submecanismo nem unidade;
decidido em 02/10): **recuperou** (a ferramenta funcionou numa nova tentativa) · **não dependia** (a resposta não
precisava do dado, ou ele veio de outra fonte) · **falha declarada** (a resposta diz ao usuário que não conseguiu) ·
**sucesso falso** (a resposta usa o dado que não veio — inventa, ou omite a falha).

## 5 · As seções do `drill_down.py protocolo` ([1]–[9])

[1] por mês · [2] por papel · [3] mês × papel · [4] a forma do que o modelo escreveu no lugar do bloco · [5]
recuperação · [6] cascata (o que vem logo depois) · [7] modo do agente (versões do prompt: JSON × texto com `<code>`) ·
[8] modelo e versão do agente · [9] a medida da resposta final fora do bloco (M1).

## 6 · Os itens do plano (S1–S6, D2, números como 4.2b)

Os números (4.1b, 4.2b-0, 4.11…) são as seções do plano antigo (de 06/10/2026); onde cada um está hoje, no de-para do [`plano-atual.md`](plano-atual.md) §3. Os códigos S e D vêm da
investigação do erro crítico (01/10):

| Código | Nome |
|---|---|
| **S1** | leitura do erro crítico da base 2 |
| **S2** / **S2b** | o detector de falhas silenciosas / os grupos do motivo |
| **S3** | medir a narração executada como código (M6) nas duas bases |
| **S4** | ferramentas que respeitam as chamadas do papel (o `idx` mistura chamadas) |
| **S5** | sucesso em três níveis: o Python executou · a ferramenta funcionou · a tarefa foi concluída |
| **S6** | o erro crítico como gatilho de destino |
| **D2** | os erros de protocolo do RespostaBacen na base 2 |
| **roadmap #N** | o item N do backlog numerado da análise (`2026-09-trace-law-flow/docs/04-roadmap.md`) |
| **Ajuste N** | a N-ésima mudança de regra do método, registrada no livro-razão (`pipeline-entre-bases.md` §3) |

## 7 · Bases, máquinas e o grau de certeza

| Termo | O que é |
|---|---|
| **base 1** / **base 2** / **base 3** | três extrações independentes de 1.000 execuções da esteira (base 1: out/2025–ago/2026; base 2: lote de ago/2026) |
| **máquina 2** | a máquina de compliance onde a base 2 está; de lá só saem contagens e nomes, nunca texto de caso nem `exec_id` |
| **[conferido]** | verificado de forma determinística (contagem, AST, regex reproduzida) |
| **[assistido]** | leitura feita por LLM na máquina 2 — entra como hipótese, nunca como fato |
| **teto** | contagem que inclui tudo o que *pode* ser o fenômeno; o número real é menor ou igual |

---

## 8 · Medidas de custo e de economia (base 3)

| Termo | O que é |
|---|---|
| **degrau 1–4 (da validação)** | a escada da candidata à memória validada ([`17`](2026-09-trace-law-flow/docs/17-validacao-memorias.md)): **1 · candidata** (a mineração: o erro existe), **2 · conferida** (cinco checagens determinísticas contra o ambiente e o prompt), **3 · revisada** (leitura de casos com dois leitores e o gate do pesquisador), **4 · validada** (o experimento: injetada, reduz o erro) |
| **teto de economia** | tokens dos passos com erro das unidades **candidatas** (por papel e no total): o máximo que uma memória poderia economizar, com eficácia de 100% e sem contar o custo dela — **hipótese**, não previsão ([racionais da base 3 §7](2026-10-trace-law-flow-third/docs/01-racionais.md#7--o-teto-de-economia-e-o-teste-de-compensação-da-memória)) |
| **orçamento de injeção** | o teto dividido pelos passos em que a memória seria injetada: o tamanho máximo da memória, em tokens por passo, para empatar |
| **linha de base** | a rodada, a fonte e as contagens congeladas (com hash) contra as quais se mede o efeito de uma memória |
| **ponto de equilíbrio** | tamanho da memória = eficácia × orçamento de injeção; abaixo disso, a memória compensa |
| **eficácia** | economia medida ÷ teto de economia |

---

## 9 · Pré-destino e destino (29/10/2026)

| Termo | O que é |
|---|---|
| **roteamento** | o processo que leva cada erro, por regra, de assinatura → mecanismo → unidade → pré-destino: a "árvore de roteamento" do [doc 09](2026-09-trace-law-flow/docs/09-metodologia-erro-a-memoria.md) |
| **pré-destino** | o encaminhamento que a triagem dá a uma unidade **antes da investigação**: candidata a memória (com o tipo da lição, factual · ambiente ou experiencial · estratégia), harness / infra (não-memória, por taxonomia), resíduo, crítico ou sem recorrência. É provisório e por regra. Os gráficos de volume (`destinos`, `unidades_destino_tipo` e a genealogia pelo destino) mostram pré-destinos. O **sinal de harness** é um pré-destino híbrido: só aparece quando uma mineração anterior já decidiu "harness" para a unidade naquela base |
| **destino** | a decisão sobre uma unidade (ou sobre uma parte dela) **depois da investigação**, com evidência: memória catalogada (com o degrau), harness registrado, monitorada ou em aberto. É do pesquisador e vale só na base em que foi decidido (`DESTINO_MINERACAO`, catálogo das memórias; Ajuste 7) |
| **destino decidido nesta base** | a unidade consta em `DESTINO_MINERACAO` ou no catálogo das memórias para o `BASE_ID` da rodada. Antes disso, o destino é "em aberto" |

No código, a coluna `destino_proposto` da triagem e a coluna "destino" da genealogia guardam o **pré-destino** (a decisão da
triagem); só `DESTINO_MINERACAO` e o catálogo guardam destino decidido. Os nomes não mudam (os arquivos que os definem
entram no hash de código da rodada). A decisão e o porquê: [`decisoes.md`](decisoes.md), 29/10; os números do estado
atual: [racionais da base 3 §8](2026-10-trace-law-flow-third/docs/01-racionais.md#8--pré-destino-e-destino-29102026).

## 10 · Lição (30/10/2026, revista no mesmo dia)

| Termo | O que é |
|---|---|
| **lição** | o que o agente deveria fazer diferente: um fato a lembrar ou um hábito a mudar. Tem dois níveis. A **lição da unidade** é a ideia geral proposta na classificação (terceiro campo de `UNI[u]`): uma por unidade, ainda hipótese. A **lição da memória** é a instrução específica de uma parte da unidade, com escopo (global ou por papel) e destino, montada pela mineração a partir da mensagem de erro (`correction_guidance`): uma unidade pode gerar várias, uma por memória. A pergunta da Conferida é se a memória tem **uma lição só** |

"Conserto" não é termo do projeto; vale como palavra comum ("o conserto é na plataforma"). A coluna `conserto` do roteiro
`candidata` (L3: `corrigiu_a_licao`, `contornou`, `repetiu`, `desistiu`) é outra coisa: o que o agente fez depois do erro.
Código e esquema não mudam (`correction_guidance` e o `esquema-memoria.json` entram no hash da rodada). O termo vale para
os textos novos, os slides e as legendas. A decisão e o porquê: [`decisoes.md`](decisoes.md), 30/10.
