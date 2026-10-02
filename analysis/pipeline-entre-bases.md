# Pipeline entre bases — o livro-razão dos ajustes do método

**Data:** 2026-09-25 (atualizado 02/10) · **Estado:** ajustes 1 a 5 e 8 conferidos nas duas bases; 6 revertido; 7 e 9 conferidos na base 2; 10 e 11 feitos neste repo, falta conferir na base 2; Etapas 10b/10c (protocolo do harness, falhas silenciosas) registradas; o "o que fazer agora" vive em [`plano-atual.md`](plano-atual.md).

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

### Ajuste 11 — o [4] (candidato a sucesso falso) respeita o step final e a fronteira de chamada

**Gatilho.** A revisão da auditoria de 02/10 (`2026-09-trace-law-flow/audit/2026-10-02-auditoria-…md`, Parte II).
Conferindo o balde invisível com uma implementação independente (`audit_recompute9.py`), a definição do [4] se
mostrou mais estreita que a prosa do `13` §4. O `idx_final_depois` era o 1º `final_answer` **estritamente depois**
da falha, em **qualquer chamada** do papel.

**Evidência (base 1, rodando).**

| # | O quê | Contagem |
|---|---|---:|
| 1 | falhas reais no **próprio step** do `final_answer` (a ferramenta falha e o mesmo bloco entrega a resposta: o caso mais direto de sucesso falso) | 2 |
| 2 | … das quais a regra antiga contava | 1 (por acaso: achou um final de **outra** chamada) |
| 3 | falhas reais cujo "final seguinte" era de outra chamada (um `TaskStep` no meio) | 2 |
| 4 | papéis chamados mais de uma vez na mesma execução (o `idx` junta as chamadas — plano S4) | 491 de 2.252 |

**Solução.** `falhas_silenciosas()` ganha a coluna `chamada` (os `TaskStep` antes do step, na lista do papel), e o
`idx_final_depois` passa a ser o 1º `final_answer` **com `f >= i` e na mesma chamada**. O
`sucesso_falso_candidato()` não muda: na falha do próprio step final não há chamada sem falha no meio, então ela
vira candidato.

**Por quê.** O [4] é declarado **teto**, e um teto que deixa fora o caso mais direto não é teto. E um final que
responde a outra tarefa não diz nada sobre a falha. É a mesma lição do S4: o `idx` mistura as chamadas.

**Verificação (base 1).** [4] 53/75 → **54/75**: `nao_reconhecido` 7/9 → 8/9; plataforma continua 16/19 (o caso 2
mudou de motivo, não de resultado); argumento 30/41 e `json_invalido` 0/6 iguais. O `drill_down.py silenciosas` e o
notebook (reexecutado) dão o mesmo número; o `audit_recompute9.py` (implementação independente) também, com 0
divergências. Nenhuma outra saída do notebook muda (diff das saídas); os CSVs da esteira não são tocados e a
`ocorrencias.csv` não tem as colunas que mudaram (o `casos.csv` das silenciosas ganha a coluna `chamada`).

**Esperado na base 2 (escrito antes de rodar).** O [4] pode mudar em poucos casos (o publicado era 20/116, plataforma 16/22). A leitura
"plataforma quase sempre termina sem a ferramenta ter funcionado × `json_invalido` nunca" só cai se a plataforma
mudar muito — improvável, porque a regra nova só **acrescenta** falhas no step final e **tira** finais de outra
chamada.

**Conferido na base 2 (máquina 2, 02/10, fotos do `silenciosas` e do `audit_recompute9`, 0 divergências).** [4]
20/116 → **24/116**. As 4 a mais são falhas no próprio step do `final_answer`: plataforma 16 → 17/22 e **`json_invalido`
0 → 3/86**. Nenhum final de outra chamada (24 de 1.000 papéis têm mais de uma chamada na base 2). A leitura muda em um
ponto. O `json_invalido` **quase nunca** vira sucesso falso (3%), em vez de "nunca". O contraste com a plataforma (77%)
continua. A regra antiga, reimplementada, dá exatamente o 20/116 publicado.

**Replicar na máquina 2 (feito em 02/10):** `base_pipeline.py` (restaurar `TRACE` e `BASE_ID`) e `drill_down.py` →
`falhas_silenciosas.ipynb` → `audit/scripts/audit_recompute9.py --base base2 --trace <xz> --em <erros_mecanismo.csv>
--fonte <base_pipeline.py>`. Trazer a foto do [4] por grupo.

**Junto, sem mudar número:** a regra `^'default'$` de `MOTIVO_REGRAS` era anotada só `b2`; ela dispara 2 vezes na
base 1 (CalculoCivel, `calculo_correcoes_monetarias`, fev/2026 — a mesma calculadora do erro crítico da base 2). A
anotação passa a `b1 b2`.

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

> **O plano vivo está em [`plano-atual.md`](plano-atual.md) (desde 01/10/2026):** o que vale, o que foi feito, o que
> ficou velho e o que vem agora. Esta seção ficou como **registro de cada etapa**. A tabela abaixo é a ordem de 25/09.

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

> **Leitura consolidada (30/09):** esta seção é a história, na ordem, com as correções. O estado atual da família — o
> catálogo de mecanismos M1–M6, os resultados por base e o roteiro para uma base nova — está em
> `2026-09-trace-law-flow/docs/10-racionais-protocolo-harness.md`, `11-relatorio-protocolo-harness.md` e
> `12-procedimento-protocolo-harness.md`.

**Contexto.** Na base 1, 33 erros num incidente (out/2025, cauda até fev/2026, zero desde mar/2026), não-memória e
monitorado com gatilho (≥ 2 casos num mês ou > 1 por 1k steps). Na base 2 o gatilho disparou (~68 erros na família) e
a decisão "não-memória" — tomada na base 1 — ainda não tem evidência própria (as bases são independentes, Ajuste 7).

**Medida.** `drill_down.py protocolo` (só contagens): por mês e por papel (erros, por 1k steps, gatilho), mês × papel,
**o que o LLM escreveu no lugar do bloco** — só a forma: vazio; abriu `<code>` e não fechou (cortado?); bloco em ```
em vez de `<code>`; texto sem nenhum marcador de código —, recuperação e cascata. Os casos, com `exec_id`, vão para
`resultados/evidencia/protocolo/casos.csv` (git-ignored). **Conferido na base 1:** 33 erros; out/2025 24, nov 1, dez 7,
fev 1, zero desde mar; forma: 31 texto sem marcador, 2 em ```; 33/33 recuperados; logo depois, 25 steps sem erro, 7 `U_texto_solto` e 1
`U_estado_perdido` — tudo como no relatório (o `U_estado_perdido` foi acrescentado em 02/10, ressalva B da auditoria).

**Decisão conforme o resultado.** Concentrado num período → incidente de plataforma, "não-memória" continua (registrar
as datas). Espalhado e com uma forma dominante → ver se há lição (ex.: "sempre responder com bloco de código, inclusive a
resposta final") — ajuste próprio, com evidência.

**Resultado na base 2 (máquina 2, 30/09; só contagens).**

| Bloco | Fato |
|---|---|
| total | **69 erros** (os 69 vistos antes já eram só o `H_bloco_code`; a família, com o erro crítico, tinha 70) |
| mês | **ago/2026: 61** (37,8 por 1k steps, 58 execuções, 3 papéis); resto espalhado — dez/2025 1, fev 4, abr 2, mai 1 |
| papel | **RoteadorCivel 56, todos em ago**; em ago também OBFCivel 4 e CalculoTrabalhista 1; fora de ago, CalculoCivel 4 (fev, 1 execução) e RespostaBacen 4 (3 meses) |
| forma | 67 texto sem marcador de código, 2 vazios; 1 começa como markdown; 0 citam `final_answer`; mediana **138 caracteres**; tokens de saída mediana **242**, máx 2.604 |
| recuperação | o papel entregou resposta depois em 66/69; execução com resposta em 69/69 |
| cascata | 61 seguidos de step sem erro; 5 `U_estado_perdido`, 3 `U_texto_solto`; nunca repetiu; 14 erros seguidos no total, máx 4 |

**Conclusão: incidente 2 de plataforma** — concentrado em ago/2026 (88% dos casos), quase todo num papel, e três papéis
começando no mesmo mês. **"Não-memória" continua, agora com evidência da base 2**: o agente se recupera no step
seguinte e nunca repete; o custo é um step desperdiçado por erro. Nenhuma regra muda.

**A forma mudou em relação à base 1:** lá, relatório longo em texto (mediana 2.859 caracteres, 12 em markdown — "achou
que tinha terminado"); aqui, **frase curta** sem código. E 242 tokens de saída para 138 caracteres visíveis (~35
tokens) sugerem tokens que não aparecem no texto — raciocínio interno de outro modelo, ou resposta cortada/filtrada.
**Não verificado.** Coincide com outros sinais de mudança no mesmo período: a mensagem de parsing em formato novo no
RoteadorCivel (desde jun/2026, Ajuste 2.1) e o pico de Timeout de ferramenta em 10–11/08 (Ajuste 4).

**Em aberto (opcional):** ler 2–3 casos do RoteadorCivel de ago e 1 dos vazios (`evidencia`, trecho `model_output` do
step do erro; exec_id em `resultados/evidencia/protocolo/casos.csv`) e classificar o que o LLM escreveu: plano sem
código, resposta em texto, cortado, outro. Nomearia a mudança de plataforma; não muda a decisão.

**Achado de método (Etapa 6):** o gatilho dispara com 1 caso em mês pequeno (dez/2025: 1 em 21 steps = 47,6/1k),
porque a regra é "≥ 2 casos **ou** > 1/1k steps". Rever junto com a robustez do alarme.

**Leitura de 3 casos do RoteadorCivel (Rafael, 30/09):** (1) o modelo escreveu só uma frase, e no step seguinte usou
`textos_decisoes` como se o step tivesse rodado → `U_estado_perdido`; (2) escreveu **a própria decisão final como dict**
(`{fluxo_encerramento: …, resultado_ultima_decisao: …}`), sem código — o `</code>` do fim é o harness devolvendo a
sequência de parada; (3) recuperação: no step seguinte, `<code>final_answer(answer=…, human_request=…)</code>`, `error =
null`. O erro é do agente (o LLM quebrou o formato), mas **uma memória não o evitaria**: o prompt já ensina o formato,
a mensagem de erro mostra o exemplo e ele acerta no step seguinte. A parte aprendível — não supor que o step que falhou
rodou — já é o `U_estado_perdido`.

**Hipótese do Rafael: o prompt — o achado: o MODO do agente.** `drill_down.py protocolo` ganhou o bloco [7]: as
versões do formato no system prompt por papel (hash só das linhas com `<code>`, ```` ``` ````, `<end_code>`,
`Thought:`, `final_answer(` — o prompt inteiro muda a cada execução, essas linhas não), com o **modo**, os meses e os
erros de cada versão; e `--prompt <versão>`, que grava o texto da versão para ler na máquina. As formas de [4] ficaram:
frase/texto, dict/JSON, ```` ``` ````, vazio (o `</code>` do fim é o harness devolvendo a sequência de parada).

As versões são **os dois modos do CodeAgent do smolagents**, cada um com o seu modelo de prompt:

| Modo | O que o modelo entrega | Como o harness acha o código | O erro "regex pattern" |
|---|---|---|---|
| **JSON estruturado** | `{"thought": …, "code": …}` — formato imposto na geração | lê o campo `code` | **não existe** |
| **texto com `<code>`** | texto livre com `Thought:` e `<code>…</code>` — as marcas são só instrução | procura o bloco com a regex | **só aqui** |

**Base 1:** managerAgent e ConversationAgent rodam em JSON (`a34f495f`, `febfeb55`: 0 erros em 4.590 steps, out/2025 →
ago/2026), **exceto em out/2025**, quando parte das execuções rodou em texto (`82de8f07`: 21 erros em 130 steps;
`2f96aa69`: 3 em 83) — **é o incidente 1, cuja causa nunca tinha sido achada**. RespostaBacen e CalculoCivel rodam
sempre em texto (`b0f37eea`: 9 em 193 steps, taxa de fundo). Ou seja: o erro é do modelo (esquece as marcas ou entrega
a resposta direto — o dict do caso 2), mas **só pode acontecer no modo texto**, e os surtos coincidem com execuções
mudando de modo. **Não vira memória:** o agente não escolhe o modo; o conserto é configuração da plataforma (qual modo,
e mantê-lo); a parte aprendível — não supor que o step que falhou rodou — já é o `U_estado_perdido`. **Vira achado para a
plataforma.** Ressalva: que o modo JSON imponha o formato depende de a API do modelo aceitar saída estruturada (não
conferido na configuração de vocês); o que se afirma são os números.

**Correção registrada:** um commit anterior (`4f6ecaa`) leu as versões como "prompt que mistura dois formatos
(`<code>` e ```` ```py ````)". Errado: o ```` ```python ```` aparece nas duas só para listar as ferramentas. A diferença
real é JSON × texto; o [7] passou a mostrar o modo.

**Base 2 ([7], máquina 2, 30/09):** **todos os papéis com o erro rodam no modo texto, o tempo todo** — RoteadorCivel e
OBFCivel na versão `168d70e2`, RespostaBacen, CalculoCivel e CalculoTrabalhista na `b0f37eea`. **Ninguém mudou de modo.**
O RoteadorCivel usa a mesma versão de mai a ago: **965 steps e 0 erros em mai–jul; 871 steps e 56 erros em ago**. O modo
explica por que o erro **pode** acontecer na base 2 inteira, mas **não explica o surto de agosto** — outra coisa mudou.

**Próxima medida — o modelo.** O trace registra, por step, o modelo que respondeu (`model_output_message.raw.model`) e,
por execução, a versão do agente (`cod_vers_aget`). `drill_down.py protocolo` ganhou o [8]: papel × modelo e papel ×
versão, com meses, steps, erros e taxa. Pista: 242 tokens de saída para 138 caracteres visíveis é o padrão de modelo que
raciocina por dentro (`o4-mini`, `gpt-5.2`). Na base 1, o RespostaBacen roda em `o4-mini` e tem a maior taxa do erro
(7 em 116 steps, 60/1k); o managerAgent em `gpt-4.1` erra só em out/2025, no modo texto. `cod_vers_aget` na base 1 é
quase sempre vazio ou 0 — pouco informativo lá. **Hipótese para ago/2026:** o RoteadorCivel trocou de modelo, e o modelo
novo esquece as marcas `<code>` no modo texto (e entrega o dict direto, como no caso 2).

**Resultado ([8], máquina 2, 30/09) — a causa do incidente 2: troca de modelo.**

| Papel | Modelo | Meses | Steps | Erros | Por 1k |
|---|---|---|---:|---:|---:|
| RoteadorCivel | `gpt-4.1-2025-04-14` | mai → ago (381 em ago) | 1.341 | **0** | 0 |
| RoteadorCivel | **`gpt-5.6-terra-2026-07-09`** | **só ago** | 478 | **54** | **113** |
| RoteadorCivel | (não registrado) | jul, ago | 17 | 2 | 118 |
| OBFCivel | `claude-sonnet-4-5` | abr → ago | 721 | 0 | 0 |
| OBFCivel | **`gpt-5.6-terra-2026-07-09`** | **só ago** | 22 | **4** | **182** |

(Somas conferidas contra o [7]: RoteadorCivel 1.836 steps e 56 erros; OBFCivel 750 e 4.) **Mesmo papel, mesmo mês,
mesmo prompt, mesmo modo texto: `gpt-4.1` 0 erros em 381 steps de agosto; `gpt-5.6-terra` 54 em 478** — quase um
experimento controlado. Dos 61 erros de agosto, 58 estão no modelo novo ou em steps sem modelo registrado (1 no
`gpt-4.1` do CalculoTrabalhista). `cod_vers_aget` é sempre 0 na base 2 — não informa.

**Conclusão: incidente 2 = o modelo `gpt-5.6-terra` (só em ago/2026, parte das execuções do RoteadorCivel e do
OBFCivel) rodando no modo texto com `<code>` — esquece as marcas em ~11% dos steps (18% no OBFCivel).** Explica as outras
pistas: 242 tokens para 138 caracteres visíveis (padrão de modelo que raciocina por dentro — a confirmar) e o dict de
roteamento entregue direto (caso 2). Na base 1, sinal parecido: RespostaBacen em `o4-mini`, 60/1k.

**Destino: não-memória — achado para a plataforma**, com causa, dono e correção: usar o modo JSON com esse modelo (o
formato é imposto na geração), ou manter o `gpt-4.1` nesses papéis, ou testar o formato ao trocar de modelo antes de
produção. **Método:** o surto se explica cruzando **modo × modelo** por papel e mês — tudo registrado no trace, lido de
forma determinística, sem LLM na análise. Vale como monitor: modelo novo num papel → conferir a taxa do erro de formato.

**Base 1, investigação por papel (30/09; cenário 4 — managerAgent, RespostaBacen, ConversationAgent, CalculoCivel =
os 33 erros).** Medida determinística aqui (fração dos trechos de 5 palavras do que o modelo escreveu que aparece na
observação anterior e na resposta final entregue depois) + leitura de casos com `drill_down.py protocolo --casos`:

| Papel | Erros | Modelo | O que escreveu | Tamanho mediano | Cópia da ferramenta | **Antecipou a resposta final** |
|---|---:|---|---|---:|---:|---:|
| managerAgent | 21 | `gpt-4.1` (12) + não registrado (9) | 11 markdown, 10 texto | 3.254 | 2/21 | **15/21** (mediana 97%) |
| RespostaBacen | 7 | `o4-mini` (7) | 6 texto, 1 ```` ``` ```` | 101 | 1/7 | 1/7 |
| ConversationAgent | 3 | `gpt-4.1` | 2 texto, 1 ```` ``` ```` | 3.295 | 0/3 | 0/3 |
| CalculoCivel | 2 | `gpt-4.1` | 2 texto | 4.084 | 0/2 | 0/2 |

**managerAgent — mecanismo A, "entregou a resposta final em texto, sem código" (15/21), confirmado na leitura de 3
casos** (`protocolo --casos managerAgent 82de8f07 3`): nos casos 1 e 3 o modelo escreveu a resposta completa ao usuário
em markdown, sem `<code>`, e no step seguinte embrulhou **o mesmo texto** em `final_answer("""…""")` (100% e 97% de
sobreposição com o código seguinte e com a resposta final). O caso 3 começa com *"Resposta detalhada em formato markdown
**conforme solicitado**"* — cita a instrução do negócio no fim do prompt (*"Sempre dê a resposta mais detalhada
possível. Responda … em formato markdown"*): o modelo segue a instrução do negócio e esquece a regra do `<code>`. Caso
2, variação: o modelo quis **falar com o usuário** (tabela parcial + perguntas, esperando confirmação) em texto, em vez
de `final_answer(..., human_request=…)`; 44% veio da observação anterior; a recuperação falhou (o código seguinte começa
com texto solto) — a cascata para `U_texto_solto`.

**RespostaBacen — lidos os 7 casos** (`protocolo --casos RespostaBacen 7`; todos `o4-mini`, todos em dez/2025 — na
base 1 é concentrado, não crônico):
- **1/7 — mecanismo A com o JSON do negócio:** *"I have successfully drafted and validated the response. The final
  structured JSON is:"* e o JSON da resposta dentro de ```` ``` ````, sem `<code>`; no step seguinte, `final_answer({…})`
  com o mesmo JSON (95%). O "devolva um JSON" do fim do prompt **foi** seguido — o teste pela primeira letra não o viu
  porque há uma frase antes.
- **6/7 — "achou que terminou" (corrigido após a leitura do Rafael, 30/09).** Os 7 erros são de **3 execuções**. Na
  sequência de ferramentas de cada uma: em **4** dos 6, o `resposta_final` **já tinha rodado** — o modelo viu na
  observação o JSON da resposta, concluiu que terminou e escreveu a mensagem de sucesso **em texto, sem `<code>` e sem
  `final_answer`**. Em **2**, **sucesso falso**: *"generated and validated … and submitted"* quando só o rascunho tinha
  rodado; e *"invoked `resposta_final` with all required fields"* logo depois de a observação mostrar *"Error calling
  tool 'resposta_final': resposta_cliente must be a dict with 'texto_resposta', 'anexos' keys"*. Numa das execuções o
  agente chama o `resposta_final` **5 vezes e nunca o `final_answer`**: chama, escreve "pronto!" em texto, leva o erro
  de formato, chama de novo.
- **A causa candidata — sinal de harness, não só protocolo:** `resposta_final` é uma **ferramenta real** do negócio
  (`drill_down.py ferramenta resposta_final`), descrita como a que devolve *"json da resposta gerada para o cliente"* — o
  nome e o papel competem com o `final_answer` do harness. E ela tem **duas versões**: a 1 (jan–jun/2026, 88 steps, 20
  execuções; recebe `resposta_gerada: string`) com **0 erros**, e a 2 (**só dez/2025**, 47 steps, 6 execuções; recebe
  `json_resposta` — dict aninhado com `resposta_cliente`, `anexos` bacen/cliente e `quebra_sigilo` — e
  `validade_resposta`) com **os 7**. Mesmo modelo (`o4-mini`) nos dois períodos: o que mudou foi o contrato da
  ferramenta. Correlação forte (6 × 20 execuções), não prova; o texto do negócio no fim do prompt pode ter mudado junto
  (o hash de formato `b0f37eea` é o mesmo). **Conserto, da plataforma:** renomear a ferramenta (ex.:
  `enviar_resposta_bacen`), ou dizer no prompt "depois do `resposta_final`, encerre com `final_answer(...)` em
  `<code>`", ou o modo JSON.
- **Destino: sinal de harness (decisão do Rafael, 30/09)** — não memória: o conserto na origem (nome/contrato no prompt)
  resolve todas as execuções, e na base 1 o problema sumiu quando o contrato mudou (versão 2 só em dez/2025) — uma
  memória hoje seria sobre um contrato já trocado. **Memória candidata por ferramenta, se reaparecer** com o contrato
  atual e a plataforma não corrigir: *"`resposta_final` não encerra a tarefa; depois dele, `final_answer(...)` em
  `<code>`"*. Teste: os 4 erros do RespostaBacen na base 2 (3 meses) — mesmo mecanismo?

**Hipótese do Rafael — sinal de harness: o prompt torna o momento da resposta final ambíguo** (30/09). O modelo lê no
começo do prompt (modelo do smolagents, em inglês) que precisa pôr o código em `<code>`; quando chega à resposta final,
lembra da instrução do negócio no fim do prompt (em português: "devolva um JSON no formato…", "responda em markdown…") e
escreve **o conteúdo** pedido — o JSON, o relatório — esquecendo o envelope `<code>final_answer(…)</code>`. No step
seguinte, com a mensagem de erro mostrando o formato, ele põe o `<code>`. Evidência até aqui: RespostaBacen caso 1 (o JSON
do negócio, em ```` ``` ````, sem `<code>`; depois `final_answer({…})` com o mesmo JSON); managerAgent casos 1 e 3 (o
relatório em markdown; o 3 abre com *"conforme solicitado"*). Se vale, **o erro se concentra no step da resposta final**
e o conserto é de prompt/harness: a instrução do negócio dizer explicitamente *"entregue esse JSON/relatório com
`final_answer(...)` dentro de `<code>`"*, ou o harness aceitar a resposta final estruturada (modo JSON). Teste possível,
determinístico: em quantos erros o step seguinte é o `final_answer` (managerAgent: 15/21 anteciparam a resposta final).
ConversationAgent e CalculoCivel (5): textos longos, nem cópia nem antecipação — sem mecanismo claro pela medida.
**Lidos depois (30/09):** ConversationAgent 3/3 = M1 (o relatório de sub-agente fora do envelope; a medida não viu porque
o LLM reescreveu ao reembrulhar; o prompt desse papel diz "pode responder diretamente"); CalculoCivel 2/2 = M3 (só o
plano; `</code>` no lugar de `<code>`). Base 1 fechada — `11-relatorio-protocolo-harness.md` §1.

**Base 2, RoteadorCivel — 7 casos lidos + `metadados_steps.py` (30/09).** A leitura "antecipou a saída / inventou a
falha" foi feita e **retirada**: nos steps do erro, 200–300 tokens de saída para 9–184 caracteres visíveis (nos steps que
funcionam, ~3 caracteres por token), `finish = stop`, sem filtro; em 3 casos o step anterior veio **vazio sem erro**.
Hipóteses M4 (texto que não chega) e M5 (step vazio silencioso) — `11-relatorio-protocolo-harness.md` §2.3.
**Campos crus (30/09, `metadados_steps.py` linha `cru:`):** só o `content` da API vem preenchido (os outros campos ∅,
`usage` sem detalhe de raciocínio), e ele já vem curto ou vazio — o smolagents leu o mesmo mais o `</code>`. Descartado
"conteúdo em outro campo"; M4 = o terra gasta a saída e entrega pouco ou nada (causa provável: raciocínio interno, não
comprovável pelo trace); M5 = o harness aceita o `content` vazio sem erro (achado de harness).

**Estado da família em 30/09.** Base 1 **fechada** (33: M1 20, M2 6, M3 2, 5 do managerAgent declarados "não lidos" —
decisão do Rafael). Base 2: plataforma (modelo); sem lição aprendida e sem sinal de harness nos 56 do RoteadorCivel; 1
achado de harness (M5). **Próximo:** CalculoCivel (4 erros numa execução — é a do erro crítico?) e RespostaBacen (M2 de
novo? → memória candidata por ferramenta). `11-relatorio-protocolo-harness.md` §2.4–2.5.

**CalculoCivel e o erro crítico da base 2 (01/10).**

- **Fontes:** `drill_down.py critico` (novo, `7c1625d`), a leitura dos 4 casos e duas leituras assistidas por LLM
  na máquina 2.
- **A execução:** os 4 erros de protocolo estão na execução do único crítico. Ela tem **4 chamadas** do papel; as 3
  primeiras terminam com `final_answer`, e a 4ª (idx 28–48, 11 erros) morre no limite.
- **A cadeia da 4ª chamada:**
  1. a calculadora devolve uma string de erro (`'DEFAULT'`) com `error: null` — falha silenciosa;
  2. resposta em texto (M1);
  3. **narração com `<code>`/`</code>` capturada como código (M6, novo)** — os rótulos `U_estado_perdido`/`U_texto_solto`
     dessa chamada são o harness executando narração;
  4. repetição, sem nenhum `final_answer`.
- **Leitura retirada:** a anterior ("4 ciclos de um loop desde o idx 20; morte por 25 erros") — o `critico` mistura as
  chamadas.
- **Registro:** `11` §2.5, `10` §4 (M1, M6); roadmap item 39.

### Etapa 10c — falhas silenciosas de ferramenta (S2/S2b, 01/10)

**Gatilho.** No erro crítico da base 2, a calculadora devolveu `"Error calling tool 'calculo_correcoes_monetarias':
'DEFAULT'"` como **valor**: `resultado_corr` é `str` (o contrato declara `dict`), o step ficou com `error: null`, e a
falha só aparece na observação. **Pergunta:** isso é um caso só, ou um canal de falha que a taxonomia não vê?

**Medida (determinística, sem LLM).**

- `falhas_silenciosas()` (`base_pipeline.py`) percorre os steps e procura `Error calling tool '<nome>'` na observação
  ou no `action_output`:
  - com `error: null` → **silenciosa**;
  - com erro → **com exceção**.
- `motivo_da_falha()` (S2b) põe o texto depois do `:` num de 6 grupos, por palavras-chave. Cada regra anota a base de
  origem.
- Comandos: `drill_down.py silenciosas [--motivos] [<ferramenta>]`. Saída só com contagens e motivos mascarados
  (`mascarar_motivo`). Commits `78ed696`, `0a69ad0`, `41b43b9`.

**Resultado nas duas bases.** Base 2 **conferida rodando** (fotos de 01/10: `silenciosas` e `silenciosas --forma
busca_obf`, commits `6123716`, `de5b601`); o [1b] bate grupo a grupo com o que fora calculado sobre as contagens do
`--motivos`.

| | Base 1 | Base 2 |
|---|---:|---:|
| falhas de ferramenta com exceção | 9 | 20 |
| **falhas silenciosas** | **120** (90 execuções, 10 meses) | **134** (124 execuções, 7 meses) |
| % silenciosas entre as falhas de ferramenta | 93% | 87% |
| sem nenhum erro nos 3 steps seguintes | 107 | 122 |
| `U_tipo_retorno` precedido de falha silenciosa (até 3 steps) | 4/47 (9%) | 5/79 (6%) |
| `U_campo_inexistente` precedido | 0/10 | 3/38 (8%) |
| grupo **sem resultado** ("não foram encontrados…", "No text … found") | 43 | 8 |
| grupo **argumento do agente** ("necessário passar", "maximum amount of documents", "validation error for call", "Query falhou"…) | **41** | 6 |
| grupo **plataforma** ("internally hosted model failed", "Failed to fetch", "Wrong credentials", "object has no attribute", `'DEFAULT'`…) | 19 | 22 |
| grupo **JSON inválido** (`busca_obf`: "Expecting property name enclosed in double quotes") | 6 | **86** |
| grupo **fora da cobertura** ("Assunto não previsto…", "Coeficiente não encontrado") | 2 | 10 |
| não reconhecido | 9 | 2 |
| [4] final_answer depois de uma falha real, sem chamada bem-sucedida da mesma ferramenta (teto de sucesso falso) | 53/75 | 20/116 |
| … dos quais **plataforma** | 16/19 | 16/22 |
| … dos quais **argumento do agente** | 30/41 | 2/6 |
| … dos quais **JSON inválido** | **0/6** | **0/86** |
| … dos quais não reconhecido | 7/9 | 2/2 |

*(Os números do [4] acima são de antes do Ajuste 11, de 02/10. Agora: base 1 54/75 (não reconhecido 8/9); base 2
24/116 (plataforma 17/22, JSON inválido 3/86). Ver §3, Ajuste 11.)*
| `busca_obf`: forma do 1º argumento (`--forma`) | 6 `str(dict colado de um retorno impresso)` | 80 `str(dict colado…)` + 6 string colada |

**Conclusões:**

1. **A maior parte das falhas de ferramenta é silenciosa nas duas bases.** A taxonomia, construída sobre `ActionStep.error`,
   não vê ~90% delas.
2. **As memórias de contrato continuam bem atribuídas.** `U_tipo_retorno` e `U_campo_inexistente` não nascem de falha
   silenciosa (91–94%). **Nenhum Ajuste.**
3. **A composição é de cada base.** Os grupos se repetem; as mensagens não (são do dev de cada ferramenta). As regras foram
   escritas olhando as duas bases (decisão do Rafael), e o resto fica como cobertura.

**Hipótese forte.** **O contrato da plataforma — a ferramenta devolver a falha como texto, não como erro — é a causa
comum.** Ele:

- (a) esconde do aprendizado os erros de argumento do agente (41 na base 1) e o `repr_colado` silencioso (6 e 86, abaixo),
  que nunca viram exceção;
- (b) deixa o agente seguir sem o resultado (sucesso falso; o "índice indisponível" do CalculoCivel);
- (c) é o primeiro elo da cascata do erro crítico.

**Destinos:**

- **sinal de harness** (exceção tipada ou resultado estruturado, uma mudança só para todas as ferramentas);
- **canal novo de candidatos a memória** (o grupo argumento do agente, lido das observações);
- **método:** a fonte de erros de uma taxonomia de traces não pode ser só o campo de exceção;
- **métricas:** step sem erro ≠ ferramenta funcionou ≠ tarefa concluída.

**Achado (01/10, duas bases): o JSON inválido do `busca_obf` é o `repr_colado` no canal silencioso.**

- **O gesto.** O `RoteadorCivel` recebe o dict do `puxa_doc_decisao` (`{"anteriores": [{"resultado": …, "resumo": …}]}`)
  e, ao chamar o `busca_obf`, **cola o print** em vez de passar a variável — o mesmo gesto do Ajuste 2.2. Quando a
  colagem quebra a sintaxe → `SyntaxError` → `U_repr_colado` (visível). Quando a colagem é Python válido e vem dentro de
  `str()` (ou como string) → aspas simples → o `json.loads` da ferramenta falha → falha **silenciosa**.
- **A medida.** `silenciosas --forma busca_obf` (determinístico; "colado" = o critério do `repr_colado`: ≥2 pares
  `"chave": "texto"` e ≥2 chaves já impressas numa observação anterior do papel). Base 1: 6/6. Base 2: 86/86 (80
  `str(dict colado)`, 6 string colada). **Nenhum** `json.dumps` nem variável — o JSON quebrado não vem da ferramenta.
- **O contrato.** `textos_decisoes (str)`: "… em JSON formatado como string" (declaração lida na máquina 2). O texto pede
  JSON; o tipo `(str)` convida ao `str(...)`. O dict vem de outra ferramenta da mesma esteira.
- **O peso.** Na base 2 o canal silencioso é ~12× o visível (86 contra os 7 do `repr_colado`; *corrigido em 02/10: o visível são 18, ~5×*): a unidade foi medida pela
  parte pequena.
- **O custo é retrabalho, não resposta errada.** 0/6 e 0/86 viram sucesso falso — o agente refaz a chamada e acerta.
  *(Corrigido pelo Ajuste 11, 02/10: base 2 3/86 — falha e `final_answer` no mesmo bloco. "Quase nunca", não "nunca".)*
  A falha de plataforma é o oposto (16/19, 16/22). O grupo argumento do agente **não** segue um padrão (30/41 contra 2/6):
  "erro do agente se recupera" não vale nas duas bases.
- **Dono:** o agente (quem precisa mudar para o erro não acontecer: passar a variável com `json.dumps`). O rótulo do
  grupo `json_invalido` no `drill_down.py` **continua "a conferir"** — o grupo é genérico, e em outra base o dono pode ser
  a ferramenta; quem decide em cada base é o `--forma` (decisão do Rafael).
- **Destinos:** memória (a lição do `repr_colado` estendida: "use a variável; converta com `json.dumps`, nunca cole o
  print nem use `str()`") **e** aviso à plataforma (o passe dict → string JSON entre duas ferramentas da esteira: o
  `busca_obf` aceitar dict, ou a declaração pedir `json.dumps`).

**Em aberto:**

- **decisão de método (Rafael):** as falhas silenciosas `json_invalido` com o gesto colado entram como canal silencioso de
  `U_repr_colado` (a contagem e a lição da unidade mudam — Ajuste próprio) ou ficam como unidade separada;
- o [4] é teto: conferir no caso os 16 de plataforma de cada base (sai só sim/não e contagem).

**Onde isto vai morar.** O roadmap item 26 já decidiu (22/09) que erro invisível ganha notebook próprio (§13.x), fora
do notebook da esteira. `falhas_silenciosas()` e `motivo_da_falha()` são a primeira peça dele, e não uma célula do
notebook da esteira (proposta de 01/10, revista). O nome do par de docs reservado lá (`10-/11-…-falhas-silenciosas.md`)
colidia com os docs 10/11 da família Protocolo do harness. **Decidido (Rafael, 01/10):** o conjunto das falhas
silenciosas fica `13-racionais`, `14-relatorio`, `15-procedimento-falhas-silenciosas.md` + notebook próprio
(`plano-atual.md` §4.2). **Feito (01/10):** `pipeline/falhas_silenciosas.ipynb` (§13.x) — o **balde invisível** do
desenho de três notebooks (visível · invisível · consolidação, `plano-atual.md` §1). As medidas [1]–[4] e a forma
subiram para o `base_pipeline.py` (`DONO_DO_GRUPO`, `forma_argumento`, `formas_das_falhas`, `erro_depois_da_falha`,
`contrato_precedido`, `sucesso_falso_candidato`) e o `drill_down.py silenciosas` passou a chamá-las — saída idêntica,
byte a byte, nos três modos (base 1). O §7 da esteira migrou inteiro para a §13.7 (mesmos números na base 1: inventário
90, Result-Ignore 103/3.053, RAC 125, Tool-Skip 10/840); na esteira ficou um parágrafo de limite. A §13.8 grava
`resultados/evidencia/silenciosas/ocorrencias.csv`, a entrada do balde para a consolidação. **Replicar na máquina 2:**
`base_pipeline.py` (restaurar `TRACE` e `BASE_ID`), `drill_down.py`, `falhas_silenciosas.ipynb` e o notebook da esteira.

**Base 2 rodada (02/10, tarde) — relatório do agente da máquina 2 (prompt do plano 4.2a; 10 fotos).** O que é
**[conferido]** veio de contagem determinística; o que é **[assistido]** é leitura do LLM da máquina 2, ou seja,
hipótese.

*Como rodou.* O `nbconvert` dos dois notebooks não terminou no editor ("Cell did not finish executing"). Os passos 1–3
foram recalculados pelas funções do pipeline e pela lógica dos detectores da §13.7, e conferem com os agregados
gravados. O `drill_down.py caso` caiu num dos casos com `UnicodeEncodeError` (terminal cp1252); o agente leu esse caso
direto do trace. Corrigido no `drill_down.py` (stdout em UTF-8). Os SHA-256 das cópias da máquina 2 não batem com o
repo (cópias com edição local). O que sustenta os números é o `audit_recompute9`, uma implementação independente, com
0 divergências lá.

| Passo | Resultado | Tipo |
|---|---|---|
| 1 · triagem | 479 erros · 16 unidades · **8 candidatas** (370 erros, 77%) · 1 crítico; os 6 esperados dos Ajustes 2.2–10 conferem (`U_repr_colado` candidata, `U_resultado_bruto` fora com 3/2/1, `U_codigo_lento` ausente, `H_timeout_ferramenta` não-memória, `U_campo_inexistente` candidata e não sinal, 1 crítico) | [conferido] |
| 2 · `U_repr_colado` visível | **18 erros em 18 execuções**, só RoteadorCivel (jun 3, jul 10, ago 5) — o "7" era só o recorte do Ajuste 2.2 | [conferido] |
| 3 · funil | 3.907 ActionSteps · 479 com exceção · 20 falhas de ferramenta com exceção · 134 silenciosas em 134 steps (87,01%) · sobreposição 0 · [4] 24/116 | [conferido] |
| 3 · detectores §13.7 | inventário 116 · Result-Ignore 203/8.661 (2,34%) · RAC 350 · mismatch 23 (só registro) · Tool-Skip 3/1.000 (0,3%) · chamadas × declaradas 103 × 116 | [conferido]; contagem de detector, não falha confirmada |
| 4 · sucesso falso (4.1b), 6 casos | plataforma 3 (as 3 calculadoras): o `final_answer` **não** usa o dado que faltou (1 não precisa dele, 2 vieram de outra ferramenta). `json_invalido` 3: falha e `final_answer` no mesmo step, e a resposta **declara a falha** (não omite, não inventa) → **0/6 sucessos falsos** | [assistido]; amostra não aleatória, 3 de 17 na plataforma |
| 5 · RespostaBacen (D2), 4 erros | `o4-mini`, `b0f37eea`, modo texto: **M1 em 3** (JSON do negócio ×2, pergunta ao usuário), todos com a declaração `resposta_gerada` e o prompt pedindo formato; **M2 em 1** (dez/2025, depois do `resposta_final`, com a declaração **`json_resposta`**); 3/4 recuperam no step seguinte e 4/4 entregam `final_answer` depois | M1/M2 [assistido]; tokens, caracteres, `finish` e recuperação [conferido] |

*Leitura.*

- **O [4] é um teto frouxo.** Na amostra, nenhum dos 6 candidatos é sucesso falso. A plataforma tinha outra fonte
  para o dado, e o `json_invalido` termina numa **falha declarada**: uma terceira categoria, que o [4] não separa
  hoje. "O risco à resposta está na plataforma" passa a ser **hipótese não confirmada** (0/3), não achado. O caminho
  para medir de verdade é o 4.1c (o retorno no `txt_vrvl_locl`) e o S5 (sucesso em três níveis).
- **O M2 segue a declaração `json_resposta` nas duas bases.** Base 1: os 6 M2 em dez/2025, todos no período
  `json_resposta`. Base 2: o único M2, também em dez/2025 e com `json_resposta`. Com `resposta_gerada` (desde
  jan/2026): base 1, 0 erros em 88 steps; base 2, 0 M2 nos 3 casos. É um experimento natural nas duas bases. O
  contrato induzia o M2, e a troca do contrato o eliminou. Destino: **sinal de harness, já corrigido pela
  plataforma**; não é memória.
- **O M1 do RespostaBacen na base 2 tem o gatilho da base 1.** Nos 3 casos, o prompt pede formato e o modelo entrega o
  conteúdo pedido sem o envelope. O `protocolo` [9] viu 2 dos 3 (o terceiro é a pergunta ao usuário, 496 caracteres:
  o falso negativo conhecido da medida).
- **Novo: `U_nome_inventado` é a maior candidata da base 2** (118 erros, 112 execuções; na base 1, 5). Ainda não foi
  lida nem minerada. É também a 1ª unidade do único erro crítico. Conferir se é nome inventado, definição que expirou
  entre steps (roadmap #23) ou narração executada como código (M6, plano 4.3).

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

**Auditoria nº 6, checagem E.** Usava o mês do lote (`202512`) e esperava 26/33 erros de "Explicação solta" em
dez/2025; com o relógio da execução são 25/33 em out/2025 (`01` §7 Passo 7). **Corrigida em 02/10** (ressalva A da
auditoria de 02/10; roadmap 36): a expectativa é a do mês da execução e a checagem roda sem divergência.

## 6. Estado das duas bases (02/10/2026)

| | Base 1 | Base 2 |
|---|---|---|
| Erros | 498 (313 execuções) | **479** |
| Unidades | 15: **10 candidatas** (440 erros, 88%), 1 sinal de harness (10), 2 não-memória (40), 2 revisar (8) | 16: **8 candidatas** (370 erros, 77%), 1 crítico, 3 não-memória (90), 2 revisar (9), 2 fora (9) |
| Maior candidata | `U_texto_literal` (182 erros) | **`U_nome_inventado` (118 erros, 112 execuções, 5 meses, 6 papéis)** — na base 1, 5 erros |
| `U_campo_inexistente` | sinal de harness (decisão da mineração, só base 1) | candidata (38 erros, 2 papéis) |
| `U_repr_colado` | candidata (6 erros, 4 meses) | candidata (**18** erros, 18 execuções, 3 meses, só RoteadorCivel); o "7" antigo contava só o Ajuste 2.2 |
| Críticos | 0 | 1 (CalculoCivel, fev/2026, 49 steps, 25 erros antes, 1ª unidade `U_nome_inventado`) |
| Resíduo | 8 erros (1,6%): 7 causa + 1 sintoma; 1 padrão recorrente (parênteses) | 9 erros: 7 causa + 2 sintoma (antes dos Ajustes 3–9: 32) |
| Alarme de cobertura | não dispara (1 erro, 0,2%) | 25/09: dispara (5,2%); depois dos Ajustes 3, 4, 8 e 9 o sintoma não reconhecido caiu para 2 erros — reconferir na Etapa 6 |
| Balde invisível | 9 com exceção · 120 silenciosas (93%) · [4] 54/75 | 20 · 134 (87%) · [4] 24/116 |

*Base 2: triagem recalculada na máquina 2 pelas funções do pipeline (relatório da máquina 2, 02/10), coincide com o
agregado gravado; o notebook não foi reexecutado inteiro lá (ver Etapa 10c, "Base 2 rodada").*
