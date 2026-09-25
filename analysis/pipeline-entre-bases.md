# Pipeline entre bases — o livro-razão dos ajustes do método

**Data:** 2026-09-25 · **Estado:** ajustes 1, 2.1, 2.2 e 3 fechados neste repo (o 3 falta replicar na base 2); próxima etapa: 4, o Timeout (§5).

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
| 3 | 25/09 | `Import from` (4) e `final_answer` com argumento inexistente (1) no resíduo da base 2; o segundo também na base 1 | `Import from` na regra do sandbox; mecanismo `argumento_inexistente` → unidade do argumento nomeado | 1 erro muda; 11 candidatas; 450 cobertos | esperado: causa não identificada 12 → 7 | sem commit |

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

**Esperado na base 2:** a causa não identificada cai de **12 para 7**; "Inventário do sandbox" +4; "argumento nomeado" +1.

**Replicar na máquina 2** (`base_pipeline.py`): o ramo do sandbox em `submecanismo()` (`"Import from"`), a regra
`argumento_inexistente` logo depois da do `argumento_posicional`, a entrada no `SUB2UNI` e o texto de `U_arg_nomeado`;
rodar o notebook inteiro e o `genealogia_sankey.py`.

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
| 4 | sintoma não reconhecido | Timeout de ferramenta → unidade de plataforma | 4 respostas do cru | não (0 ocorrências na base 1) |
| 5 | sintoma não reconhecido | a chave `?` e a chave sem impressão digital | 1 categoria por caso, 6 casos | não deve (verificar) |
| 6 | — | o alarme de cobertura | decisões abaixo | não |
| 7 | — | comparar bases; achados laterais; auditoria E | rodar na máquina 2 | não |

### Etapa 3 — a causa não identificada da base 2 ✅

Feita em 25/09/2026 — é o **Ajuste 3** da §3. Falta replicar na base 2 e conferir: a causa não identificada deve
cair de 12 para 7.

### Etapa 4 — o Timeout de ferramenta

**Contexto.** Base 2: 16 erros, 15 execuções, 1 mês, 1 papel; caem em `X_sintoma_nao_reconhecido` porque `classify()`
(`base_pipeline.py`) não tem regra para `Timeout`. No primeiro caso lido (`ContestacaoCivel`): o código do agente está
certo (`laudo_str = laudo_contestacao(dados)`); quem falhou foi a ferramenta. A mensagem é **em português** — o
smolagents emite mensagens em inglês, então o wrapper que lança isso é da esteira (a confirmar). O pensamento do
agente cita a "regra de execução única" do prompt e o fallback permitido: **o prompt já tem a política para esse
caso e o agente a seguiu**, terminando **sem a etapa do laudo**. A literatura já lida classifica assim: AgentDebug
(`llm_limit` — "timeouts, token limits"; `literature/agentdebug-2509.25370.md:375`: "system → não é memória do agente,
é ticket de infra") e TRAIL (*System Execution Errors › Timeout Issues*, `trail-2505.08638.md:50`). A triagem já trata
`H_*` assim: `tipo == NAO` vai direto a "não-memória", sem passar pela recorrência.

**Solução.** Pela Frente 3 (passo 6: sintoma primeiro, causa depois), (1) `classify()`: sintoma novo "Ferramenta
excedeu o timeout"; (2) `submecanismo()`: `timeout_ferramenta` → `SUB2UNI` → `H_timeout_ferramenta`, tipo
não-memória, com o conteúdo "ajustar o timeout ou tornar a ferramenta assíncrona"; (3) o **gatilho de reabertura**
com dono, no `04-roadmap.md` § Monitoramento (o modelo é o do `H_bloco_code`); (4) `genealogia_sankey.py`
(`NOME_CURTO`/`CURTO_MEM`) e o `audit_recompute6.py`.

**Por que esta.** Não é memória: o agente já sabe o que fazer, então nada há para lhe ensinar. Não é extensão de
`H_infra_llm`: o dono do conserto é outro (quem mantém a ferramenta, não o LLM). E tira o Timeout do resíduo por uma
**regra**, sem tocar no limiar — o alarme desliga por uma razão certa (25 → 9 erros, 1,9%).

**Decisão sua.** A família do sintoma: reutilizar `Infra / LLM upstream` ou criar **`Infra / ferramenta`**
(recomendo esta: mantém cada família ligada a um dono; custa uma entrada em `paleta.COR_ERRO`, e sem ela a cor cai no
cinza com aviso).

**O que falta de você** (só categorias e números): (a) os outros casos do Timeout são iguais — mesma ferramenta, mesmo
papel, mesmo fallback? (b) em quantos dias distintos caem os 16 (incidente ou estrutural)? (c) o timeout em segundos;
(d) como a execução termina — status e se a resposta final cita ou omite o laudo (sim/não).

**Aceitação.** Base 1 sem mudança (0 ocorrências de Timeout — verificado em `erros_classificados.csv`); auditoria com 0
divergências; base 2: os 16 erros saem do resíduo, o sintoma não reconhecido cai a 9, e a triagem mostra `H_timeout_ferramenta`.

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
| Unidades | 15: **11 candidatas** (450 erros, 90%), 2 não-memória (40), 2 revisar (8) | não vista depois do 2.2 |
| Resíduo | 8 erros (1,6%): 7 causa + 1 sintoma; 1 padrão recorrente (parênteses) | 37 erros: 25 sintoma + 12 causa; 13 padrões, 1 passa (`?`) — esperado depois do Ajuste 3: 32 (25 + 7) |
| Alarme de cobertura | não dispara (1 erro, 0,2%) | **dispara**: 25 erros, 5,2% (sem o Timeout, 1,9%) |
| `U_repr_colado` | candidata (6 erros, 4 meses) | 7 erros no `RoteadorCivel` (jun 1, jul 4, ago 2) |

*Base 2: números lidos das fotos do notebook e das saídas do `drill_down.py`; o total de erros é a soma da tabela de
assinaturas do §9.2.*
