# Pipeline entre bases — o livro-razão dos ajustes do método

**Data:** 2026-09-25 (atualizado 29/09) · **Estado:** ajustes 1 a 5 e 8 conferidos nas duas bases; 6 revertido; 7 e 9 conferidos na base 2; 10 feito neste repo, falta conferir; depois, a Etapa 6 do plano (§5).

Este documento registra **como o método muda quando uma base nova o testa**. Não repete o método (que está nos docs
da análise) nem os números de uma base (que estão nos relatórios dela): registra, ajuste por ajuste, o que
disparou a mudança, a evidência, o que foi alterado, como foi verificado, o efeito em cada base e o que replicar
na outra máquina.

## 1. Por que ele existe

`2026-09-trace-law-flow/` é a **análise fundamental**: a base 1 (1.000 execuções, out/2025–ago/2026) é onde
nasceram a taxonomia (`classify()`, `submecanismo()`, `SUB2UNI`, `UNI`), a triagem e a cadeia erro → memória. Essas
funções são **hipóteses mineradas numa base** — o checklist de intake (`README.md`, "Intake checklist — a new trace
base") já diz isso: copie-as sem mudar e leia o balde "sintoma não reconhecido" como sinal de cobertura.

A base 2 (lote de ago/2026, 9 meses reais, 0 `exec_id` em comum com a base 1 — `04-roadmap.md` item 27) roda o mesmo
pipeline **na máquina de compliance** (pasta `2026-09-trace-law-flow-second`); o cru dela não sai de lá. Onde as
regras não alcançam, o resíduo cresce e o alarme dispara — e a resposta certa é **corrigir o método**, com a base 1
como teste de regressão, e não remendar a base nova.

| Pergunta | Onde está a resposta |
|---|---|
| Qual é o método, e por quê | `2026-09-trace-law-flow/docs/01-racionais.md` (§7) e `09-metodologia-erro-a-memoria.md` |
| Quais são os números da base 1 | `02-relatorio-achados.md` — **atualizados a cada ajuste** (coerência total, não parcial) |
| Como validar um número, e o que fazer com cada decisão da triagem | `03-procedimento-validacao.md` (Frente 3; §1.16 é este ciclo) |
| O que falta fazer | `04-roadmap.md` (itens 29–36) |
| **O que mudou entre bases, por quê, e o que replicar** | **este documento** |

## 2. Como uma base nova entra — o fluxo entre as duas máquinas

**O que sai da máquina de compliance:** só contagens, nomes de classe de exceção (`error_type`), nomes de papel e
de ferramenta, meses, verdadeiro/falso e esqueletos mascarados. **Não saem**: texto de caso, código do agente,
nome de cliente, número de processo, `exec_id`. As colunas novas do `drill_down.py residuo` existem para isso
(§3, Ajuste 1).

**O ciclo de um ajuste** — o mesmo em todos os itens da §3:

1. **Evidência na base nova.** A tabela por padrão (`residuo_padroes.csv`, notebook 9.2), `drill_down.py padrao` e
   `caso`. Quem lê o cru é o Rafael; de volta vêm categorias, não texto.
2. **Diagnóstico.** De quem é a falha (agente × plataforma — Frente 3, passo 4) e se o padrão é um erro só (passo 3).
3. **Ajuste escrito e testado neste repo.** Critério de aceitação: a **base 1 muda só nos erros previstos** (ou em
   nenhum) e a **auditoria nº 6** (`audit/scripts/audit_recompute6.py`, reimplementação independente feita da
   prosa dos racionais) dá **0 divergências**.
4. **Réplica na cópia da base 2** (as funções mudadas estão listadas em cada ajuste; o diff é o do commit) e novo
   run do notebook. De volta vem a tabela nova.
5. **Registro.** Aqui, na §3; a regra em `01-racionais.md` §7 Passo 2; os casos em `03` §1.16; o item no roadmap.

**Coerência.** Um ajuste que muda número da base 1 refaz, no mesmo passo: notebook, `genealogia_sankey.py` e os
docs (`01`, `02`, `03`, `09`, `schema-e-taxonomia-de-erros.md`). As auditorias congeladas ganham um banner; não são
reescritas.

## 3. Registro dos ajustes

| # | Data | O que disparou | O que mudou | Base 1 | Base 2 | Commit |
|---|---|---|---|---|---|---|
| 1 | 25/09 | dois padrões "recorrentes" no resíduo (`SyntaxError`, `?`) sem prova de que eram padrões | `drill_down.py`: 3 colunas de estrutura da mensagem, bloco de contagens, `padrao` com nome exato | idêntica | mostrou que as duas chaves eram de fallback | `20d7c93` |
| 2.1 | 25/09 | mensagem de parsing em formato novo (sem o código) | `linha_do_codigo()`; `padrao_residuo()` lê o motivo na linha do `due to:` | idêntica | causa não identificada 19 → 12; os 7 `SyntaxError` saem do resíduo | `20d7c93` |
| 2.2 | 25/09 | os 7 caiam na unidade errada (`texto_solto`) | `sinais_de_parsing()`, regra do retorno colado inteiro | 4 erros mudam; **10 → 11 candidatas** | os 7 → `repr_colado` | `2943c1b` |
| 3 | 25/09 | `Import from` (4) e `final_answer` com argumento inexistente (1) no resíduo da base 2; o segundo também na base 1 | `Import from` na regra do sandbox; mecanismo `argumento_inexistente` → unidade do argumento nomeado | 1 erro muda; 11 candidatas; 450 cobertos | causa não identificada 12 → 7; resíduo com 8 padrões | branch `2026-09-25-residuo-base2` |
| 4 | 25/09 | 16 erros de Timeout no sintoma não reconhecido; alarme disparado (5,2%) | sintoma e causa novos: família `Infra / ferramenta` → `H_timeout_ferramenta` (não-memória) | nenhum CSV muda | esperado: sintoma não reconhecido 25 → 9, alarme desliga | branch `2026-09-25-residuo-base2` |
| 5 | 28/09 | a nº10 aparecia como memória nas figuras, mas a mineração decidiu `harness` | `DESTINO_MINERACAO` + decisão "sinal de harness" na triagem | 1 decisão muda; **11 → 10 candidatas**, 440 cobertos | a nº10, se passar na triagem, também vira sinal | branch `2026-09-25-residuo-base2` |
| 6 | 28/09 | a nº10 herdou "harness" na base 2; "Nome usado sem ter sido definido" foi de 5 para ~117 erros | comparar a composição de cada unidade com a base de referência | **revertido** (overengineering para a fase atual — ver Ajuste 7) | — | `c39fdb2`, revertido em `d2f2ec8` |
| 7 | 28/09 | a decisão da mineração vazava entre bases | `DESTINO_MINERACAO` guarda a base; `BASE_ID` ao lado do `TRACE` | nada muda | a nº10 volta a candidata (destino em aberto) | branch `2026-09-28-mineracao-base2` |
| 8 | 28/09 | o `?` da base 2 juntava 7 erros de três tipos e "passava" na recorrência | tempo do interpretador (plataforma × código lento), limite de passos como erro crítico, chave sem nome de exceção fora da recorrência | nada muda (só colunas novas) | conferido: o `?` some; sintoma não reconhecido 9 → 2; 1 erro crítico | `d306666` |
| 9 | 29/09 | Etapa 5b: os 3 "código lento" eram o resultado bruto da busca entregue no `final_answer` | causa `resultado_bruto_na_resposta` → `U_resultado_bruto`; lições do `U_codigo_lento` e do `H_timeout_ferramenta` corrigidas | idêntica (+1 coluna, toda falsa) | esperado: `U_codigo_lento` 3 → 0, `U_resultado_bruto` 3 ("fora") | branch `2026-09-28-mineracao-base2` |
| 10 | 29/09 | o erro crítico saía cinza ("plataforma"), na família do protocolo do harness | família própria `Erro crítico`, cor preta; nenhuma cor muda | idêntica | esperado: 1 erro troca de família e cor | branch `2026-09-28-mineracao-base2` |

### Ajuste 1 — evidência estrutural do resíduo

**Gatilho.** O run da base 2 deu 14 padrões no resíduo, 2 passando na recorrência, e o alarme de cobertura
disparou. Lendo `padrao_residuo()` (`base_pipeline.py`), as duas linhas `True` são as duas **chaves de fallback**:
`?` (a mensagem não tem nenhuma palavra `*Error` ou `*Exception`) e `SyntaxError` sem motivo (a mensagem não tem linha
`Error:`). Nenhuma das duas identifica um erro.

**Mudança** (`drill_down.py`). `residuo` grava em `casos.csv` três colunas verdadeiro/falso — `tem_due_to`,
`tem_linha_error`, `linha_rejeitada_ok` — e imprime o bloco "estrutura por padrão" (só classe e 0/1). `padrao "<nome>"`
aceita o nome **exato** mesmo quando outro padrão o contém (antes recusava `SyntaxError`, que é substring de
`SyntaxError: invalid syntax`).

**Verificação.** Base 1: 9 erros, colunas antigas idênticas; os 4 `codigo_mal_escrito` saem com `1/1/1`.

**O que a base 2 mostrou:**

| Padrão | Erros | Leitura |
|---|---:|---|
| `SyntaxError` | 7 | `due_to=1 error=0 rejeitada=0`; todos `RoteadorCivel`, `idx=1`, jun–ago/2026 |
| `?` | 7 | 6 `AgentExecutionError` sem `due to` (5 execuções, 3 meses, 3 papéis) + 1 `AgentMaxStepsError` |
| `TimeoutError: Tool <q> excedeu o timeout de <n>s` | 16 | 15 execuções, 1 mês, 1 papel |
| `Import from <módulo> is not allowed` (4 padrões) | 4 | 1 erro cada; o `classify()` reconhece, o `submecanismo()` não |

### Ajuste 2.1 — o formato novo da mensagem de parsing

**Diagnóstico.** As regras de sintaxe do `submecanismo()` (`repr_colado`, `texto_em_literal` por linha,
`texto_solto_no_codigo`) leem **a linha de código que o parser rejeitou**. No formato antigo ela vem dentro da
mensagem (`due to: SyntaxError`, a linha, `^`, `Error: <motivo>`). No formato novo — `Code parsing failed on line N
due to: SyntaxError: <motivo>`, numa linha só — não vem. Contando no cru da base 1: **222 mensagens no formato
antigo e 3 no novo**, todas do `RoteadorCivel` em jun–jul/2026. O formato muda **por papel e por versão**, e as regras
falham **em silêncio**: sem a linha, o erro cai em `codigo_mal_escrito` "por falta de formato, não por diagnóstico".

**Mudança** (`base_pipeline.py`). `linha_do_codigo(m, code)` devolve a linha N do `code_action` — só quando a mensagem
é do formato novo. `linha_rejeitada(m, linha_codigo)` usa a da mensagem ou, na falta, essa. `padrao_residuo()` lê o
motivo que vem na linha do `due to:`. `explodir_memoria()` guarda `linha_codigo_erro`; `submecanismo(m, linha_codigo)`.
O `audit_recompute6.py` faz o mesmo, escrito à parte.

**A fonte foi conferida.** Nos 222 erros do formato antigo, a linha N do `code_action` é a linha que a mensagem traz
em **221**. A exceção é uma f-string de várias linhas: o parser aponta o início e N é o fim.

**Efeito.** Base 1: **0 mudanças** (os 3 do formato novo continuam em `texto_em_literal`, por palavra-chave da
mensagem). Base 2: os 7 ganham linha e motivo, saem do resíduo (causa não identificada 19 → 12) e caem em
`texto_solto_no_codigo` — a unidade errada, porque o retorno colado tem palavras em português. É o efeito que o 2.2
corrige; ele foi previsto e medido, não escondido.

### Ajuste 2.2 — o retorno colado inteiro

**Diagnóstico.** `repr_colado` só reconhecia o retorno impresso colado quando a linha tinha "truncado". O caso real
da base 2 (3 traces lidos pelo Rafael, `RoteadorCivel`): o agente chama `puxa_doc_decisao`, recebe
`{"anteriores": [{"resultado": …, "resumo": …}]}` e, ao chamar `busca_obf`, **cola o dict impresso como argumento em
vez de passar a variável** — um colchete trocado e dá `SyntaxError`. O mesmo gesto existia na base 1, escondido em
`texto_em_literal`, porque as palavras-chave da mensagem ("forgot a comma") eram testadas antes.

**As três unidades vizinhas** (todas são erro de sintaxe por *texto que foi parar no código*; muda **que texto** e **para
onde**):

| Unidade | Que texto | Para onde vai | Lição |
|---|---|---|---|
| `repr_colado` | **dado** que já estava numa variável (retorno de ferramenta) | **entrada** de outro código (argumento, atribuição) | usar a variável, não colar o print |
| `texto_em_literal` | o **relatório** que o agente escreve | dentro de aspas, em geral o `final_answer` | montar em variáveis e só então chamar `final_answer` |
| `texto_solto_no_codigo` | **explicação** do agente | sem aspas nenhuma | o bloco de código só tem Python; a explicação vai no pensamento |

**A regra** (testada logo depois de "truncado" e **antes** das palavras-chave da mensagem): a linha rejeitada tem ≥2 pares
`"chave": "texto"`, ≥2 dessas chaves já apareceram impressas como chave numa observação anterior do mesmo papel, e a
instrução não é um `final_answer(`.

**Por que os três critérios, e não um.**

- **Só a estrutura** pegaria um dict de relatório que o próprio agente escreveu.
- **Só a origem** ("o texto já apareceu numa observação") pegaria **70 erros de `texto_em_literal`** da base 1: o agente
  também copia texto de documento das observações para dentro de strings, e essa é outra lição.
- **`final_answer` fora** porque ali o texto é o relatório final. Dois casos revistos pelo Rafael no cru
  confirmaram: o `managerAgent` de fev/2026 (uma tabela markdown vinda do subagente, colada dentro do
  `final_answer`) e o `ConversationAgent` de mar/2026 (o dict do próprio `final_answer`, fechado com `)` sem `}`). A
  primeira versão da regra os movia — eram 6; ficaram **4**.

**Mudança.** `base_pipeline.py`: `PAR_CHAVE_TEXTO`, `sinais_de_parsing(m, code, obs_ant)` (guarda **só números e a
linha**, nunca o texto das observações: `linha_codigo_erro`, `chaves_vistas_antes`, `em_final_answer`), a regra em
`submecanismo()`, e a lição de `U_repr_colado` ("truncado ou inteiro"). `audit_recompute6.py`: a mesma regra reescrita
à parte (`retorno_colado()`).

**Evidência.** `pipeline/resultados/evidencia/A6_repr_colado/` (git-ignored): 9 erros com ≥2 pares na linha
rejeitada, passem ou não na regra, com o esqueleto mascarado e o cru.

**Efeito na base 1.**

| | Antes | Depois |
|---|---|---|
| Erros que mudam | — | **4**, de `texto_em_literal` para `repr_colado`: 3 `RoteadorCivel` (jun–jul/2026) + 1 `ConversationAgent` (mai/2026) |
| `U_repr_colado` | fora (2 erros, 2 execuções, 1 mês) | **candidata** (6 erros, 6 execuções, 4 meses, 2 papéis); passa também na régua estrita |
| `U_texto_literal` | 186 erros · 149 execuções · 6 papéis | 182 · 145 · 5 (o `RoteadorCivel` sai) |
| Candidatas | 10 (447 erros, 90%) | **11 (449 erros, 90%)**; tokens 92% |
| Triagem por papel (9.4/9.5) | 18 células candidatas · 8 caem na régua estrita | **19 · 9** (herdadas: 14 de 33) |
| Auditoria nº 6 | 0 divergências | **0 divergências**; 437 ocorrências; 15 unidades conferidas |

**Efeito na base 2.** Os 7 erros do `RoteadorCivel` vão a `repr_colado` (1 em jun, 4 em jul, 2 em ago) — confirmado
pela consulta por mês e submecanismo. A triagem da base 2 depois do 2.2 ainda não foi vista: confirmar que
`U_repr_colado` sai candidata lá (7 execuções em 3 meses).

**Replicar na máquina 2** (o diff é o do commit `2943c1b`): `base_pipeline.py` — `__all__`, `explodir_memoria`,
`PAR_CHAVE_TEXTO`, `sinais_de_parsing`, `submecanismo`, `montar_unidades`, o texto de `U_repr_colado`; rodar o
notebook inteiro e `genealogia_sankey.py`.

### Ajuste 3 — `Import from` e o argumento que a ferramenta não tem

**Gatilho.** Depois do Ajuste 2, a causa não identificada da base 2 ficou com 12 erros, nenhum recorrente. Dois grupos
tinham causa conhecida e só faltava a regra:

- **`Import from X is not allowed`** (4 erros; módulos `get_document_text` ×2, `python_interpreter`, `typing`). O
  `classify()` reconhecia o sintoma; o `submecanismo()` só casava o texto `"Import of"`. A mensagem mudou de forma —
  o mesmo tipo de falha silenciosa do Ajuste 2.1.
- **`FinalAnswerTool….forward() got an unexpected keyword argument`** (1 erro na base 2, com a classe renomeada para
  `FinalAnswerToolOrHumanAssistance`; e **1 na base 1**, argumento `docs`, `ConversationAgent`, mai/2026 — a única
  mensagem "unexpected keyword" dela). O agente chama a ferramenta com um nome de argumento que a assinatura não tem.

**Decisão (Rafael, opção B).** O argumento inexistente vai para a unidade que já existe, "Ferramentas só aceitam
argumento nomeado", e não para uma unidade própria. Uma lição só — **usar a assinatura declarada** — previne a chamada
posicional e o nome errado; é o mesmo critério que já junta "módulo sem import" ao "inventário do sandbox". Os erros
de uma ocorrência só (7 na base 2) ficam como cobertura, sem trabalho agora (Frente 3, baixa prioridade).

**Mudança.** `base_pipeline.py`: `submecanismo()` casa `"Import of"` **ou** `"Import from"`; regra nova
`\.forward\(\) got an unexpected keyword argument` → `argumento_inexistente` → `SUB2UNI` → `U_arg_nomeado`; a lição
passa a "chamar as ferramentas com argumentos nomeados e só com os nomes da assinatura declarada". O `classify()` não
muda: o sintoma continua "Tipo diferente do esperado" (o sintoma não decide a unidade — `09` §2). `audit_recompute6.py`:
as mesmas duas regras, escritas à parte.

**Efeito na base 1** (conferido contra o `erros_mecanismo.csv` de antes):

| | Antes | Depois |
|---|---|---|
| Erros que mudam | — | **1** (o `final_answer` com `docs`): `causa_sem_regra` → `argumento_inexistente` |
| "Ferramentas só aceitam argumento nomeado" | 35 erros · 22 execuções · 10 meses | 36 · 23 · 11 (continua candidata) |
| Causa não identificada | 8 erros · 6 meses | 7 · 5 (continua "revisar — prioridade", pelo padrão dos parênteses) |
| Candidatas | 11 (449 erros) | **11 (450 erros, 90%)**; tokens 92% |
| Triagem por papel | 9 das 19 células caem na régua estrita | **8 das 19** ("ConversationAgent · argumento nomeado" passa de 4 a 5 execuções) |
| `Import from` | — | 0 ocorrências na base 1: nada muda |
| Auditoria nº 6 | 0 divergências | **0 divergências** |

**Na base 2 (conferido):** o resíduo ficou com **8 padrões** — Timeout, `?`, `invalid syntax`, `invalid character`,
`IndexError`, `Could not index` com lista, `APIConnectionError`, `UnicodeDecodeError`; os 4 `Import from` e o
`FinalAnswer` saíram, e a causa não identificada caiu de 12 para 7.

**Replicar na máquina 2** (`base_pipeline.py`): o ramo do sandbox em `submecanismo()` (`"Import from"`), a regra
`argumento_inexistente` logo depois da do `argumento_posicional`, a entrada no `SUB2UNI` e o texto de `U_arg_nomeado`;
rodar o notebook inteiro e o `genealogia_sankey.py`.

### Ajuste 4 — o Timeout de ferramenta

**Gatilho.** O maior padrão do resíduo da base 2 — 16 dos 25 erros do sintoma não reconhecido, o que sozinho faz o
alarme de cobertura disparar. O `classify()` não conhecia a mensagem.

**Evidência** (base 2, só contagens, com o comando da Etapa 4):

| O quê | Resultado | Leitura |
|---|---|---|
| Erros / execuções | 16 / 15 | — |
| Papel | só `ContestacaoCivel` | um fluxo |
| Ferramentas | `ingestao_peticao_inicial` 9, `laudo_contestacao` 4, `auditoria_final_contestacao` 1, `interpretar_provas_contestacao` 1, `buscar_hibrida` 1 | 5 ferramentas: é o limite de tempo do fluxo, não o defeito de uma |
| Limite | 600 s em 12, 1800 s em 4 | configurado por ferramenta |
| Dias | 10/08 (6), 11/08 (6), 18/08 (1), 20/08 (2), 25/08 (1) | pico de dois dias (incidente) e uma cauda |
| Status da execução | 3 em 7, 2 em 9, nunca 67 (falha) | o status não registra o timeout |
| Terminou com `final_answer` | 16 de 16 | o agente segue o fallback do prompt ("regra de execução única") |

A mensagem é em português — é o wrapper de ferramentas da esteira, não o smolagents. O código do agente estava certo
(no caso lido: `laudo_str = laudo_contestacao(dados)`).

**Decisões (Rafael).**

- **Família nova, `Infra / ferramenta`.** As três famílias de plataforma dizem de onde vem a falha: o **protocolo do
  harness** (o harness não consegue ler a resposta do LLM, sem bloco de código), a **infra do LLM** (o provedor não
  responde ou recusa — `AgentGenerationError`, HTTP 422) e a **infra de ferramenta** (a ferramenta passa do limite de
  tempo). Isso basta para separar os donos; não se criou um eixo de "alavanca".
- **Cor: o mesmo cinza-médio da `Infra / LLM upstream`.** A regra da paleta (`03` §1.14) é que a cor é fixa por família
  e uma família nova só **acrescenta** — mudar a cor de uma família existente quebraria as figuras e as bases. Um terceiro
  cinza ficaria indistinguível; o cinza-médio é "infra externa ao harness", e o nome escrito em cada barra separa as duas.

**Mudança.** `base_pipeline.py`: regra no `classify()` (testada primeiro), `timeout_ferramenta` no `submecanismo()` (logo
depois do `infra_llm`), `SUB2UNI`, `UNI["H_timeout_ferramenta"]` (não-memória). `paleta.py`: a cor e o nome legível (e
o nome de `argumento_inexistente`, que faltava desde o Ajuste 3). `genealogia_sankey.py`: rótulos curtos.
`audit_recompute6.py`: a regra escrita à parte. Gatilho no `04-roadmap.md` § Monitoramento.

**Como o erro percorre a cadeia** (igual a qualquer outro — o `submecanismo()` roteia; a família só dá a cor):

```
mensagem ──classify()──► família "Infra / ferramenta", assinatura "Ferramenta excedeu o timeout"
         └─submecanismo()─► timeout_ferramenta ──SUB2UNI──► H_timeout_ferramenta (tipo não-memória) ──triagem()──► não-memória
```

A triagem manda o tipo não-memória direto para "não-memória", sem o teste de recorrência — por isso "1 mês" não é
problema. Nos gráficos ele conta como erro (Pareto, custo, genealogia) e, no 9.3, é uma barra própria na seção
não-memória; nunca entra na cobertura das candidatas.

**Efeito na base 1.** Nenhum: não há Timeout; todos os CSVs de `resultados/` saem idênticos; auditoria com 0 divergências.

**Esperado na base 2.** Resíduo de 8 para 7 padrões; sintoma não reconhecido de 25 para 9 (1,9%) → **o alarme desliga**;
`H_timeout_ferramenta` aparece como não-memória com 16 erros; o sintoma não reconhecido continua "revisar — prioridade"
só por causa do `?` (Etapa 5).

**Replicar na máquina 2:** `base_pipeline.py` (4 trechos), `paleta.py` (2), `genealogia_sankey.py` (2).

### Ajuste 5 — a decisão da mineração entra na triagem: "sinal de harness"

**Gatilho.** Ao definir a família do Timeout (Ajuste 4), a pergunta: a nº10 — "Campo inexistente no retorno
estruturado", que a mineração mandou para o harness — é da mesma natureza das três famílias de plataforma?

**Resposta (decidida com o Rafael, 28/09): não.** Nas três de plataforma, a plataforma falhou e o agente fez certo; a
saída é ticket e monitoramento. Na nº10, **o agente errou**, induzido por um contrato contraditório — o system prompt
declara o mesmo nome de campo para o retorno de `validar_quebra_sigilo` e para o JSON final — e **quem descobriu foi o
próprio pipeline de memória** (a mineração: 9 de 21 respostas entregues com o campo inválido, `07` §6.2). Memória
sozinha não protegeria a resposta; o conserto certo é mudar o ambiente. É uma **terceira saída do mecanismo**:

| Saída | Quem errou | O que produz | Exemplo |
|---|---|---|---|
| **memória** | o agente | uma lição que o agente aprende | as 10 candidatas |
| **sinal de harness** | o agente, induzido pelo ambiente | uma proposta de mudança no ambiente (contrato, validação) | a nº10 |
| **não-memória operacional** | a plataforma | ticket e gatilho de monitoramento | harness, LLM, timeout |

É a forma que a hipótese de arquitetura dá à saída de mudança de harness do Update Engine v2, e que ela registrava
como lacuna ("o campo `validation.destino` existe só como código ad hoc") — `knowledge-as-infra-architecture-hypothesis.md` §C.

**Mudança.** `base_pipeline.py`: `DESTINO_MINERACAO` (`U_contrato_dict: memória`, `U_campo_inexistente: harness`;
ausente = em aberto) e, na `triagem()`, a unidade que passaria como candidata e tem destino `harness` vira **`sinal de
harness`**; coluna nova `destino (mineração)`; ordem das seções candidato → sinal de harness → não-memória → revisar →
fora. `triagem_por_papel()`: o sinal de harness fica fora do recorte por papel (não há memória por papel a escrever; sem
isso o 9.5 mostraria células "reveladas", que não existem). Notebook: seção nova no 9.3, o 9.4 sem a unidade.
`genealogia_sankey.py`: destino `SINAL-HARNESS <nome>`. `audit_recompute6.py`: a parte C confere a cobertura nova e a
unidade sinalizada contra uma tabela escrita à parte. **Nenhuma cor muda**: a barra fica laranja (família Contrato de
retorno — foi erro do agente); a seção e o rótulo dizem que o conserto é no ambiente.

**Efeito na base 1.** Nenhum erro muda de unidade (`erros_mecanismo.csv` idêntico); muda **uma decisão**. Candidatas
**11 → 10** (4 factual · 6 estratégia), cobrindo **440 dos 498 erros (88%)** e 91% dos tokens; 1 sinal de harness (10
erros). Por papel: 18 células candidatas de 31 (antes 19 de 33), 13 herdadas, 8 das 18 caem na régua estrita. Auditoria
nº 6: 0 divergências; cobertura e unidade sinalizada conferidas.

**Replicar na máquina 2:** `base_pipeline.py` (a tabela, a `triagem()`, a ordem, a `triagem_por_papel()`, o `__all__`),
`genealogia_sankey.py` (import e destino) e as 3 células do notebook (9.2, 9.3, 9.4).

### Ajuste 6 (revertido) e Ajuste 7 — as bases são independentes; a decisão da mineração vale só onde foi tomada

**O que o Ajuste 6 fazia.** Comparava a composição de cada unidade (papel, assinatura, submecanismo, chave pedida, taxa
por 1.000 steps) com a da base em que ela foi validada, e mandava para "revisar composição" a que não espelhasse. A
motivação era real: a regra de causa lê a mensagem, e uma base nova pode trazer a mesma mensagem com outra causa (a nº10
da base 2 herdou "harness" pelo nome; "Nome usado sem ter sido definido" foi de 5 para ~117 erros).

**Por que foi revertido (decisão do Rafael, 28/09).** Pelo protocolo (`03` Frente 3), **toda candidata passa pela
mineração** antes de virar memória, e a mineração começa agregando os erros da unidade por papel, identificador e mês —
é ali que um problema de composição aparece. As bases são **independentes**: cada uma é triada e minerada por conta
própria; "a candidata aparece em outra base?" é uma comparação **posterior**, entre resultados já minerados (Etapa 7).
Um alarme de composição dentro da triagem anteciparia o que a mineração faz de qualquer jeito, ao custo de regras,
limites, arquivo de referência e — com a base 3 — uma referência acumulada. É **overengineering para a fase atual**.

**Quando faria sentido.** Quando a análise virar **operação contínua** (a extração de ~1M; o Update Engine em lote por
período): aí não dá para minerar cada candidata a cada lote, e um monitor que só aponta anomalias economiza verificação
humana. A calibração feita fica registrada para essa hora: dentro da base 1 (meses antigos × recentes), com piso de 10
erros, 50% de categorias conhecidas e taxa ×4, só as unidades com referência pequena foram sinalizadas; sem o piso e com
nomes de variável, 5 de 10 unidades eram sinalizadas (alarme falso demais). O raciocínio e o desenho estão no commit
`c39fdb2`; o roadmap guarda o item.

**O que ficou (Ajuste 7).** O único problema concreto: **a decisão da mineração vazava entre bases**. Agora
`DESTINO_MINERACAO` guarda a base em que a decisão foi tomada (`base1` para a nº2 e a nº10), e `base_pipeline.py` tem um
**`BASE_ID`** logo abaixo do `TRACE` — as duas linhas que se ajustam ao copiar o pipeline para uma base nova
(`"base2"` na `-second`, `"base3"` na `-third`). `destino_mineracao(u)` só devolve o destino se a base bater; senão, "em
aberto". Base 1: tudo idêntico ao Ajuste 5 (a nº10 segue sinal de harness); com `BASE_ID = "base2"`, a nº2 e a nº10
voltam a candidatas, com destino em aberto, até serem mineradas lá.

**Replicar na máquina 2:** `base_pipeline.py` (restaurar o `TRACE` e ajustar o `BASE_ID`), o notebook e o
`genealogia_sankey.py`; nada da pasta `referencia/`.

### Ajuste 8 — desmontar o `?`: tempo do interpretador, código lento e o erro crítico

**Problema.** O `?` é a chave que sobra quando a mensagem não tem palavra de exceção. Na base 2 ele juntou 7 erros de três
tipos e "passava" na recorrência sem ser um padrão. Lidos no cru pelo Rafael:

| Erros | Mensagem | O que o código do step fazia | De quem é |
|---:|---|---|---|
| 3 | `Code execution exceeded the maximum execution time of 30 seconds` | chamava ferramentas (OBFCivel: `extract_obf_requests`; `get_docs_from_filters`…; RespostaOficios: `estrutura_subsidios`, `gera_transcricao_imagens`) | **plataforma**: o sandbox corta o bloco em 30 s e a ferramenta leva mais (as ferramentas longas têm 600/1800 s no wrapper — limites desencontrados) |
| 3 | a mesma | AgenteProcuracoes: só `final_answer`, 13 e 41 linhas, concatenando resultados de busca enormes ("estou concatenando blocos muito grandes, o que estoura o tempo") | **agente**: código lento |
| 1 | `Reached max steps.` (`AgentMaxStepsError`) | CalculoCivel, step 48: nenhum código; 48 steps de erros em cascata | **desfecho**: o agente não se recuperou |

**Solução.**

1. **Tempo do interpretador** — sintoma "Bloco de código excedeu o tempo do interpretador" (família Ambiente & sandbox: o
   limite é do sandbox). A causa se separa pelo código do step: chama ferramenta declarada no system prompt (fora
   `final_answer`) → `timeout_interpretador` → `H_timeout_ferramenta` (a lição passa a citar os dois limites); não chama →
   `codigo_lento` → **`U_codigo_lento`** (estratégia: "não manipular textos enormes no bloco"). O sinal
   `chama_ferramenta` é calculado em `explodir_memoria` só nesses erros.
2. **Limite de passos — erro crítico** (decisão do Rafael). Não é lição nem tarefa de plataforma: é consequência. Com 100
   casos, "100 execuções morreram" não diria o que prevenir. Classe à parte, **`C_limite_passos`**, tipo "erro crítico ·
   não se recuperou", decisão **"investigar — crítico"** sem limite mínimo: todo caso vai para investigação (humana ou
   com LLM; a classificação continua determinística). `caminho_dos_criticos()` grava `resultados/criticos.csv` — por
   execução morta, as unidades dos erros anteriores do papel e a primeira delas, o ponto de partida para achar o **passo
   crítico** (AgentDebug). Na triagem, cada unidade ganha **"execuções mortas com esta unidade no caminho"**: o peso de
   gravidade que a contagem de erros não dá. Acumulado, é sinal de qualidade do harness (roadmap 39).
3. **Chave sem nome de exceção** — `padrao_residuo(m, sub, err_type)` devolve `sem nome de exceção: <tipo>` em vez de
   `?`, e `residuo_por_padrao()` marca essas chaves (coluna `chave`) como fora da recorrência.

**Ainda por medir:** o número da lição do `U_codigo_lento` ("textos de ~N caracteres") — tamanhos das observações e das
variáveis nos 6 casos de tempo, na máquina 2. **Medido em 29/09 — ver Etapa 5b (§5): o tamanho não explica o estouro, e
a lição está em aberto.**

**Conferido na base 2 (29/09):** o `?` sumiu; sintoma não reconhecido com 2 erros, em baixa prioridade; 1 erro crítico
(CalculoCivel) em "investigar — crítico".

**Efeito na base 1.** Nenhum desses erros existe lá: `erros_mecanismo.csv` e a triagem idênticos; entram só as colunas
novas (`chama_ferramenta`, `chave`, "execuções mortas…", todas zeradas/"identificada"); auditoria nº 6 com 0 divergências.

**Esperado na base 2.** O `?` some. Sintoma não reconhecido de 9 para **2** (`APIConnectionError`, `UnicodeDecodeError`)
→ "revisar — baixa prioridade". `H_timeout_ferramenta` +3; `U_codigo_lento` com 3 erros em 2 execuções e 1 mês → "fora:
sem recorrência"; 1 erro crítico (CalculoCivel) em "investigar — crítico", com o caminho em `criticos.csv`.

**Replicar na máquina 2:** `base_pipeline.py` (restaurar `TRACE` e `BASE_ID`), `drill_down.py`, `paleta.py`,
`genealogia_sankey.py` e o notebook.

### Ajuste 9 — o resultado bruto entregue na resposta final

**Problema.** O Ajuste 8 chamou de "código lento" os 3 erros de tempo do AgenteProcuracoes, com a lição "não manipular
textos enormes no bloco". A leitura (Etapa 5b, §5) mostrou que não era isso.

**Evidência (máquina 2, 29/09; `drill_down.py tempo` e leitura do cru pelo Rafael — só tamanhos, nomes e o sentido dos
pensamentos, sem texto de caso).**

| # | O quê | Onde |
|---|---|---|
| 1 | Código do step: sem laço, sem `+=`; a única chamada é o `final_answer` (e `strip`) | `tempo` |
| 2 | O que ia para o `final_answer`: `resposta` (2.857) + `resultado_busca` (60.539); `answer_final` (26.762, ≈ os dois `resultado_busca` somados + texto) | `tempo` (variáveis no estado final) |
| 3 | Régua do papel: os 3 `final_answer` que deram certo entregaram mediana 441, máximo 2.921 caracteres; nenhum ≥ 25 mil | `tempo` |
| 4 | Recuperação: execução 1 entregou 2.921 (a `resposta` sem o `resultado_busca`) em 39,8 s; execução 2 repetiu a tentativa grande, estourou de novo, e entregou 441 | `tempo` + cru |
| 5 | Pensamento, execução 1: "o timeout ocorreu por concatenar e devolver o `resultado_busca` inteiro, muito extenso" | cru |
| 6 | Custo: sem o texto, respondeu "pelos trechos visíveis na observação" — execução 1: "não localizei procurações concluídas" (possível falso negativo, em aberto); execução 2: pedido de ajuda humana ("preciso do PDF integral…") | cru |

**Solução.** `final_answer_sem_laco()` (coluna nova em `explodir_memoria`): tempo do interpretador + o bloco chama o
`final_answer` + sem laço (`tem_laco()`, via `ast`). Em `submecanismo()`: chamou ferramenta declarada →
`timeout_interpretador` (como antes); senão, `final_answer` sem laço → **`resultado_bruto_na_resposta`** →
**`U_resultado_bruto`** (estratégia: *"extrair no código o trecho que responde e entregar a conclusão com esse trecho;
não resumir às cegas pelo que ficou visível na observação"*); senão → `codigo_lento`. O `U_codigo_lento` fica para laço
pesado sem ferramenta, com a lição corrigida e sem caso observado (opção (a), decisão do Rafael). A lição do
`H_timeout_ferramenta` passa a citar os dois limites do interpretador vistos na base 2: 30 s e **180 s** (OBFCivel, ago).

**Por que "extrair" e não "resumir".** Resumir às cegas foi o que levou ao pedido de ajuda humana e ao possível falso
negativo. **Por que não é o `repr_colado`:** lá o agente cola o texto impresso **no código** (erro de sintaxe; lição
"use a variável"); aqui ele usa a variável e entrega o conteúdo inteiro (tempo esgotado; lição "extraia o trecho").
**Por que sem tamanho na regra:** o trace só guarda o tamanho das variáveis no fim da execução; a regra lê a forma do
código, e o `drill_down.py tempo` confere o tamanho em cada base nova.

**Verificação.** 6 formatos sintéticos (ferramenta sem/com laço, só `final_answer`, laço + `final_answer`, sem
ferramenta, compreensão no `final_answer`): pipeline e auditoria (regex, strings e comentários removidos) concordam.
Base 1: todos os CSVs idênticos, exceto a coluna nova `final_answer_sem_laco` em `erros_classificados.csv` (toda
falsa); auditoria nº 6 com 0 divergências.

**Esperado na base 2.** `U_codigo_lento` 3 → 0 (some da triagem); **`U_resultado_bruto` com 3 erros, 2 execuções, 1 mês
→ "fora: sem recorrência"**. Nada mais muda.

**Replicar na máquina 2:** `base_pipeline.py` (restaurar `TRACE` e `BASE_ID`), `paleta.py`, `genealogia_sankey.py`,
`drill_down.py`.

### Ajuste 10 — o erro crítico ganha família e cor próprias

**Problema.** O Ajuste 8 pôs o limite de passos (`Reached max steps` / `AgentMaxStepsError`) na família `Protocolo do
harness`, que a paleta pinta de **cinza** — e cinza quer dizer "plataforma, não é erro do agente". O erro crítico não é
plataforma: é a execução que morreu depois de uma cascata. Além disso, ele somava aos números da família de protocolo
(a do `H_bloco_code`), que vai ser investigada na base 2.

**Solução.** `classify()`: o limite de passos vai para a família **`Erro crítico`** (assinatura igual). `paleta.py`:
`COR_ERRO["Erro crítico"] = INK` (**preto**) — uma entrada nova, nenhuma cor existente muda (o vermelho já é de
`Suposição sobre dados`). Genealogia: rótulo e legenda "preto = erro crítico".

**Por quê.** A cor tem que dizer o que o erro é; e a família de protocolo fica só com erro de protocolo.

**Verificação.** Base 1 (não tem o erro): todos os CSVs de `resultados/` idênticos; auditoria nº 6 com 0 divergências.
Com um erro crítico sintético injetado na base 1, a genealogia mostra a família em nós pretos, `C_limite_passos` e o
destino `CRÍTICO` (as fitas saem cinza-escuro, pela transparência).

**Esperado na base 2.** O erro crítico do CalculoCivel troca de família (`Protocolo do harness` → `Erro crítico`) e de
cor (preto); a família de protocolo perde 1 erro. Nenhuma decisão de triagem muda.

**Replicar na máquina 2:** `base_pipeline.py` (restaurar `TRACE` e `BASE_ID`), `paleta.py`, `genealogia_sankey.py`.

## 4. O que os ajustes ensinam sobre o método

1. **Regra que lê a forma da mensagem falha em silêncio quando a forma muda.** O erro de parsing tem dois formatos e
   o segundo é por papel e por versão. Vale um teste de formato no intake: contar os formatos de mensagem de parsing
   por papel e mês (as três colunas do Ajuste 1 são o embrião).
2. **A chave do padrão do resíduo falha nos dois sentidos.** *União* excessiva: `?` e a classe sozinha juntam erros
   diferentes e passam na recorrência sem provar nada. *Divisão* excessiva: a máscara só troca o que está entre
   aspas, então `Import from get_document_text …` e `Import from typing …` viram 2 padrões, e `FinalAnswerTool` e
   `FinalAnswerToolOrHumanAssistance` não se juntam. É a "aproximação declarada" de `01` §7 Passo 5, agora medida.
3. **O alarme acusou uma lacuna real, mas o número enganava.** 5,2% de sintoma não reconhecido (25 de ~479) eram **64%
   um único padrão** — o Timeout, 16 erros, 15 execuções, 1 mês, 1 papel. Sem ele, 1,9%.
4. **A régua de recorrência (≥3 execuções e ≥2 meses) é da memória do agente, não do incidente de plataforma.** O
   Timeout reprova por ter 1 mês, e é justamente um incidente. Unidades `H_*` já escapam dela (`triagem()` manda o tipo
   não-memória direto), então a saída é dar ao Timeout uma regra, não mexer no limiar.
5. **A mesma chave pode esconder mecanismos diferentes.** O padrão priorizado da base 1 (`SyntaxError: closing
   parenthesis …`, 3 execuções, 2 meses) é o motivo que a base 2 traz nos 7 erros do `RoteadorCivel`. No cru da base 1
   são **2 erros de digitação e 1 texto longo dentro de uma chamada**; na base 2 é retorno colado. "O mesmo padrão em
   outra base sobe de prioridade" (Frente 3) precisa conferir o **mecanismo**, não só a chave.

## 5. Próximas etapas — o plano

Cada etapa segue o combinado: **contexto verificado → solução → por que ela e não outra → o que falta de você →
critério de aceitação.** Uma etapa por vez; cada uma abre uma nova conversa de plano. A ordem segue os baldes: primeiro
fecha-se a **causa não identificada** (o balde em que a sintaxe da Etapa 2 estava), depois o **sintoma não
reconhecido** (Timeout e `?`), e só então o alarme, que depende dos dois.

| Etapa | Balde | Assunto | Depende de você | Mexe em número da base 1? |
|---|---|---|---|---|
| 3 | causa não identificada | `Import from` (4), `final_answer` com argumento inexistente (1); 7 de uma ocorrência ficam | nada | 1 erro — **feito** (Ajuste 3, §3) |
| 4 | sintoma não reconhecido | Timeout de ferramenta → unidade de plataforma | — | não — **feito** (Ajuste 4, §3); falta conferir na base 2 |
| 5 | sintoma não reconhecido | a chave `?` e a chave sem impressão digital | 1 categoria por caso, 6 casos | não — **feito** (Ajuste 8, §3); conferido na base 2 |
| 5b | — | o tempo esgotado do AgenteProcuracoes: plataforma ou agente? | rodar `drill_down.py tempo` na máquina 2 | não — **feito** (Ajuste 9, §3); conferido na base 2 |
| 6 | — | o alarme de cobertura | decisões abaixo | não |
| 7 | — | comparar bases; achados laterais; auditoria E | rodar na máquina 2 | não |

### Etapa 3 — a causa não identificada da base 2 ✅

Feita em 25/09/2026 — é o **Ajuste 3** da §3. Conferida na base 2: 8 padrões no resíduo, causa não identificada 12 → 7.

### Etapa 4 — o Timeout de ferramenta ✅

Feita neste repo em 25/09/2026 — é o **Ajuste 4** da §3. Falta conferir na base 2: o sintoma não reconhecido deve
cair de 25 para 9 e o alarme desligar.

### Etapa 5 — a chave `?` e a chave sem impressão digital

**Contexto.** `padrao_residuo()` devolve `?` quando a mensagem não tem `*Error`/`*Exception`, e só a classe quando a
sintaxe não tem motivo — o `err_type` do step (`AgentExecutionError`, `AgentMaxStepsError`, `AgentParsingError`) já
está em `EU` e não é usado. `residuo_por_padrao()` calcula `passa na recorrência` sobre essa chave, e `triagem()` lê o
`passa` para o motivo "padrão recorrente". Base 2: o `?` são **6 `AgentExecutionError` sem `due to` + 1
`AgentMaxStepsError`**, em 3 papéis e 4 meses: passa na recorrência **sem ser um padrão**.

**Solução.** (a) `padrao_residuo(m, sub, err_type)`: sem palavra de exceção, a chave passa a ser
`sem impressão digital: <err_type>` — o `AgentMaxStepsError` vira um padrão próprio; (b) `residuo_por_padrao()`
marca essas chaves com `passa = False` e uma coluna **`chave`** (`identificada` × `sem impressão digital`), para o
resíduo dizer o que **não sabe** em vez de fingir recorrência; (c) os 6 do `?` são lidos no cru e ganham regra, se
forem um erro só.

**Por que esta.** O falso positivo nasce na chave; subir o limiar o esconderia. Marcar em vez de descartar mantém
o erro visível na fila de trabalho.

**O que falta de você.** Uma categoria por caso dos 6 `?`: limite de passos, timeout, rede/API,
interpretador/harness ou outro (3 a 5 palavras).

**Aceitação.** Base 1: `residuo_padroes.csv` idêntico (os 7 padrões dela têm palavra de exceção); base 2: o `?` deixa
de passar, o `AgentMaxStepsError` aparece à parte, e o motivo do sintoma na triagem deixa de ser "padrão recorrente".

### Etapa 5b — o tempo esgotado do AgenteProcuracoes: plataforma ou agente?

**O que procuramos.** Nos 6 erros "o bloco passou de 30 s", quem gastou o tempo: uma ferramenta (plataforma, não vira
memória) ou o código do agente (`U_codigo_lento`). O Ajuste 8 decide pelo código do step, sem contar o `final_answer`
como ferramenta: OBFCivel e RespostaOficios (3) → ferramenta; AgenteProcuracoes (3) → código lento.

**O que encontramos (máquina 2, 29/09, só tamanhos e estrutura).**

| | OBFCivel / RespostaOficios | AgenteProcuracoes |
|---|---|---|
| Textos em jogo | 15 a 36 mil caracteres | 25 a 60 mil (`resultado_busca`, `resultado_busca_2`) |
| Código do step | 431 a 607 caracteres; chama busca/transcrição (1 caso com laço) | 3 a 4 mil caracteres; **sem laço, sem `+=`** |
| Chamadas | ferramentas de busca e de transcrição | **só `final_answer`** (e `strip`) |

O tamanho das variáveis é o do fim da execução (`txt_vrvl_locl`), não o do step.

**O que dá para concluir.** O código do AgenteProcuracoes não é lento: sem laço, roda uma vez, e 60 mil caracteres o
Python processa em milissegundos. O tempo foi gasto **dentro do `final_answer`**, que recebeu o texto montado com as
buscas de steps anteriores (as buscas já tinham terminado sem erro).

**O que não sabemos.** Por que o `final_answer` demorou: independente do tamanho (grava, chama serviço, lentidão
momentânea) → **plataforma**; ou porque o texto é grande → **plataforma + agente** (lição "resumir o resultado da busca
antes de mandar para o `final_answer`").

**Como descobrir.** `drill_down.py tempo` (subcomando novo, reutilizável em qualquer base): por erro de tempo, os
tamanhos, a estrutura do código, o que ia para o `final_answer` e o que o agente fez depois no papel; por papel, os
`final_answer` que deram certo (texto entregue e duração) como régua. Só números e nomes.

**Decisão conforme o resultado** (nenhuma regra muda antes):

| A medida mostra | Conclusão | Mudança proposta |
|---|---|---|
| os que deram certo entregam textos tão grandes quanto os que estouraram | tamanho não importa → plataforma | `final_answer` num bloco sem laço conta como ferramenta → `H_timeout_ferramenta` |
| os que deram certo são bem menores, e o agente conseguiu depois de encurtar | tamanho importa → plataforma + agente | causa nova "texto grande demais para o `final_answer`" → lição "resumir antes de entregar" |
| misturado ou poucos casos | não dá para decidir com 3 erros de 1 papel | nada muda; em aberto até a base 3 |

**Nota de processo.** Uma primeira versão da regra (o primeiro caso da tabela) foi feita e revertida no mesmo dia
(`7340154` → `6b15f37`): assumia a plataforma antes de medir se o tamanho importa.

**Resultado (29/09): a segunda linha da tabela** — o tamanho importa. Virou o **Ajuste 9** (§3). Os outros 3 casos de
tempo (OBFCivel, RespostaOficios) chamam ferramentas de verdade e continuam plataforma; se há ferramenta dentro de laço
ali, ainda está por medir.

**Achados da leitura do cru (29/09), sem mudança de código:**

1. **Várias chamadas pesadas num bloco.** OBFCivel jul (limite 30 s): `get_final_answer_schema`, `get_fields_definition`
   e `get_docs_from_filters` no mesmo bloco; o pensamento seguinte diz "estou chamando muitas ferramentas de uma vez,
   preciso quebrar em steps pequenos". RespostaOficios mar (30 s): `estrutura_subsidios` + `gera_transcricao_imagens`
   no mesmo bloco, sem pensamento confirmando. Lição candidata: **"uma ferramenta pesada por step"**. Sem regra: 2 casos,
   1 confirmado, e contar ferramentas não diz quais são pesadas. Espera a medida abaixo e a base 3.
2. **Ferramenta dentro de laço?** OBFCivel ago (limite **180 s**, step de 222 s): `extract_obf_requests` + `for … in
   enumerate(docs)` com `doc.get`. Dentro do laço → agente (a ferramenta repete a cada volta); fora → plataforma (uma
   chamada lenta mesmo com 180 s). No OBFCivel jul, o Rafael leu um `for` com `get_docs_from_filters` e o `tempo` mediu
   `laços=0`: um dos dois está errado. **Medida:** `drill_down.py tempo` passou a mostrar, por laço, a linha, o que se
   repete a cada volta e o que roda uma vez, e as linhas em que `for`/`while` aparece só como palavra (comentário, texto).
   **Medido na máquina 2 (29/09) — fechado:** ago: `laço na linha 5 (for): repete {print, doc.get} · cabeçalho
   {enumerate}` — o `extract_obf_requests` roda **uma vez, fora do laço** → uma chamada lenta mesmo com 180 s →
   plataforma (Ajuste 8 certo). jul: `laços=0`; `for` só como palavra na linha 13 (comentário/texto); cada uma das 3
   ferramentas chamada uma vez → é o achado 1 ("várias ferramentas num bloco"). **Nenhum caso de ferramenta em laço nem
   de código lento na base 2: a regra acerta os 6.**
3. **O contrato `['result']` generalizado.** RespostaOficios, step seguinte: `Could not index {qualidade_evidencias…}
   with 'result'` — o agente supôs `{'result': …}` numa ferramenta de validação. É o desvio já visto na base 1, agora
   confirmado na base 2 (já classificado; não é erro de tempo). A lição do contrato precisa dizer a quais ferramentas se
   aplica.
4. **A busca de procurações só com CPF não achou; com nome + CPF achou** (AgenteProcuracoes, execução 1). Achado sobre
   a ferramenta: pede o nome, ou a documentação dela não diz isso. Uma execução só.
5. **Possível falso negativo** (AgenteProcuracoes, execução 1): a busca com nome + CPF achou procurações, e a resposta
   final foi "não localizei procurações concluídas", dada "pelos trechos visíveis na observação". Em aberto: se o que
   achou não eram concluídas, a resposta está certa; se eram, o erro custou uma resposta errada.
6. **Limites diferentes no interpretador:** 30 s (jul, mar) e 180 s (ago). A lição do `H_timeout_ferramenta` já cita os
   dois (Ajuste 9).

### Etapa 10b — "resposta sem bloco de código" (`H_bloco_code`) na base 2

**Contexto.** Na base 1, 33 erros num incidente (out/2025, cauda até fev/2026, zero desde mar/2026), não-memória e
monitorado com gatilho (≥ 2 casos num mês ou > 1 por 1k steps). Na base 2 o gatilho disparou (~68 erros na família) e
a decisão "não-memória" — tomada na base 1 — ainda não tem evidência própria (as bases são independentes, Ajuste 7).

**Medida.** `drill_down.py protocolo` (só contagens): por mês e por papel (erros, por 1k steps, gatilho), mês × papel,
**o que o LLM escreveu no lugar do bloco** — só a forma: vazio; abriu `<code>` e não fechou (cortado?); bloco em ```
em vez de `<code>`; texto sem nenhum marcador de código —, recuperação e cascata. Os casos, com `exec_id`, vão para
`resultados/evidencia/protocolo/casos.csv` (git-ignored). **Conferido na base 1:** 33 erros; out/2025 24, nov 1, dez 7,
fev 1, zero desde mar; forma: 31 texto sem marcador, 2 em ```; 33/33 recuperados; logo depois, 7 `U_texto_solto` —
tudo como no relatório.

**Decisão conforme o resultado.** Concentrado num período → incidente de plataforma, "não-memória" continua (registrar
as datas). Espalhado e com uma forma dominante → ver se há lição (ex.: "sempre responder com bloco de código, inclusive a
resposta final") — ajuste próprio, com evidência.

### Etapa 6 — o alarme de cobertura

**Contexto.** `triagem()` calcula o alarme sobre **erros** (`(EU["unidade"] == "X_sintoma_nao_reconhecido").mean()`), e
o resto da triagem sobre **ocorrências** (`01` §7 Passo 4: contar erros infla o que o agente repete em sequência).
O limiar de 5% (`ALARME_COBERTURA`) é, pelo texto do método generalizado, "escolha da instanciação — declarado e
testável", sem calibração empírica registrada. Base 2: 5,22%, margem de cerca de 1 erro; 64% do balde é um
padrão de 1 mês.

**Solução.** (1) **Manter o 5%** — calibrar com 2 bases seria ajustar o limiar à amostra. (2) Enriquecer o motivo da
triagem: fração, **maior padrão** do balde e sua parcela, fração **sem ele**, meses do maior. (3) Contar sobre
ocorrências, como o resto da triagem.

**Por que esta.** O alarme fez o que devia: achou um sintoma novo. O que faltava era a triagem **dizer** que era um
padrão só. (2) põe isso à vista sem mudar nenhuma decisão; (3) é coerência, e não mexe na base 1 (1/437 contra 1/498).

**Decisões suas.** (a) Concorda em manter o 5%? (b) Concorda em passar o alarme para ocorrências?

**Aceitação.** Base 1: mesma decisão e mesmo texto do motivo (não há alarme). Base 2: a triagem mostra
"5,2% — o maior padrão responde por 64%; sem ele, 1,9%" (com a etapa 4, o alarme desliga).

### Etapa 7 — comparação entre bases, achados laterais, auditoria E

**Comparar as bases.** A chave mascarada falha nos dois sentidos (§4, itens 2 e 5): junta mecanismos diferentes
(os parênteses) e separa o mesmo mecanismo (o `FinalAnswer` da Etapa 3b, as 4 mensagens de `Import from`). Comparar por **classe
de exceção + mecanismo**, com uma tabela feita nas duas máquinas e cruzada à mão (o cru não sai). Antes de somar bases,
`checklist.py <outra-base>` confere a sobreposição de `exec_id` (README, intake); o item 27 já registra 0.

**Achados laterais** (base 1, `ConversationAgent`, mar/2026, o caso de referência do `repr_colado`): (a) o step seguinte
falha em "Could not index" com causa de raiz de **contrato dict** — `docs_summary[0]` num dict `{'result': …}` dá lista
vazia; conferir se o `submecanismo()` manda esses casos a `U_contrato_dict`; (b) a resposta final diz "Nenhum documento
encontrado" com a ferramenta tendo devolvido documentos — falha **silenciosa**, para o roadmap item 26.

**Auditoria nº 6, checagem E.** Usa o mês do lote (`202512`) e espera 26/33 erros de "Explicação solta" em dez/2025;
com o relógio da execução são 25/33 em out/2025 (`01` §7 Passo 7). Atualizar a expectativa; as checagens A, B, C e G não
são afetadas.

## 6. Estado das duas bases (25/09/2026)

| | Base 1 | Base 2 |
|---|---|---|
| Erros | 498 (313 execuções) | ~479 (soma da tabela de assinaturas) |
| Unidades | 15: **10 candidatas** (440 erros, 88%), 1 sinal de harness (10), 2 não-memória (40), 2 revisar (8) | não vista depois do 2.2 |
| Resíduo | 8 erros (1,6%): 7 causa + 1 sintoma; 1 padrão recorrente (parênteses) | 32 erros: 25 sintoma + 7 causa; 8 padrões, 1 passa (`?`) |
| Alarme de cobertura | não dispara (1 erro, 0,2%) | **dispara**: 25 erros, 5,2% (sem o Timeout, 1,9%) |
| `U_repr_colado` | candidata (6 erros, 4 meses) | 7 erros no `RoteadorCivel` (jun 1, jul 4, ago 2) |

*Base 2: números lidos das fotos do notebook e das saídas do `drill_down.py`; o total de erros é a soma da tabela de
assinaturas do §9.2.*
