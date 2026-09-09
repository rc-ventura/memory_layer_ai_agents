# Relatório de achados — trace cru da esteira de agentes jurídicos

**Data:** 2026-09-08 · **Fonte:** `85cb11b5-b58b-40c4-a2cf-a3e99ac86521.csv.xz` (1.000 execuções, nov/2025–ago/2026)
**Pipeline reproduzível:** [`analise_trace_esteira_juridica.ipynb`](../pipeline/analise_trace_esteira_juridica.ipynb)
**Fichamentos (texto completo lido):** [`literature/`](../literature/)
**Antes de apresentar isto:** siga [`03-procedimento-validacao.md`](03-procedimento-validacao.md) — auditoria do
pipeline, ordem de leitura dos papers, e como triangular qualquer número aqui com um caso real no trace cru.
**Para entender a lógica, não só executar:** [`01-racionais.md`](01-racionais.md) — por que a taxonomia não veio dos
papers, e o que significa um achado ser corrigido vs. retirado.

> **Versão 2.** A v1 classificava erros por *sintoma* (tipo de exceção, via regex) e ancorava-se na literatura por
> resumo de busca. Esta versão classifica por **causa-raiz** e se apoia na leitura de texto completo de quatro
> papers. Três afirmações da v1 foram **refutadas** pelos próprios dados — ver §7.

---

## TL;DR

O trace confirma a premissa da pesquisa, mas o achado mais forte não é o que a v1 dizia. Dos 5.781 steps,
498 (8,6%) erram, atingindo 37% das execuções — e **nenhuma execução termina em erro: 100% se recuperam**.
Os erros são **custo, não falha**: uma execução com erro consome 3× mais tokens (mediana 146 mil vs 48 mil).

Duas causas-raiz explicam **59% de tudo**: o agente monta relatórios jurídicos longos dentro de literais de
string Python (159 erros) e trata como lista o dicionário que as ferramentas de documento retornam (136 erros).

O resultado decisivo para a tese: **86,3% das mensagens de erro entram comprovadamente no contexto do step
seguinte — e, dessas, 11,9% caem de novo na mesma categoria de causa-raiz.** O agente relê a falha e reincide. Somado
a isso, as assinaturas dominantes reaparecem em **8 dos 9 meses** da amostra, em execuções distintas. O sistema
não acumula nada entre execuções: repete o mesmo erro há dez meses. É o argumento empírico direto para uma
camada de memória persistente — e ele não existia na v1.

---

## 1 · O que o trace é

Cada linha é uma execução; `txt_etap_memo` guarda o dump da memória de trabalho no estilo *smolagents*: por papel
(`managerAgent`, `ConversationAgent`, `WorkflowManager` + agentes de domínio), uma lista de steps. Cada
`ActionStep` traz o raciocínio (`model_output`), o código emitido (`code_action`), a observação, o **erro tipado**,
o **`token_usage`**, o **`timing`** e o **contexto recebido** (`model_input_messages`).

Arquitetura CodeAgent: a única ferramenta registrada é `python_interpreter` — mas o system prompt de cada papel
**declara ferramentas de domínio como assinaturas Python** (`def nome(...)`), chamadas de dentro do código
gerado. São **90 ferramentas declaradas** somando todos os papéis, distribuídas por papel (`ConversationAgent`
recebe 9, `managerAgent` recebe 3): `answer_question_using_documents` (821 chamadas),
`get_available_documents` (730), `validar_quebra_sigilo`, `calculo_correcoes_monetarias`, `validador_calculo`…
A delegação a subagentes também acontece dentro do código (`ConversationAgent(task=...)`).

> Cuidado ao contar ferramentas pelo código: nem todo nome chamado é ferramenta. `grab` (135×) e `get_meta`
> (100×) são **funções auxiliares que o próprio agente define** num step e reutiliza nos seguintes — o
> namespace Python persiste entre steps. A fonte autoritativa é o system prompt, não a observação das chamadas.

Números gerais: 840 execuções com memória preservada · 5.781 ActionSteps · **142,6 milhões de tokens**.

## 2 · Taxonomia por causa-raiz

| Família | Erros | % | Assinatura dominante |
|---|---:|---:|---|
| **Geração de código** | 225 | 45,2% | String não fechada — relatório longo em literal (159) |
| **Contrato de retorno da ferramenta** | 168 | 33,7% | Retorno é `dict`, agente indexa como lista (136) |
| **Convenção de chamada de ferramenta** | 35 | 7,0% | Argumento posicional onde só cabe nomeado (12 ferramentas) |
| **Protocolo do harness** | 33 | 6,6% | Resposta sem bloco de código — **inativo desde dez/2025** |
| **Ambiente & sandbox** | 19 | 3,8% | Import não autorizado (11), módulo sem import (6) |
| **Suposição sobre estado** | 8 | 1,6% | Variável de step que falhou |
| **Infra / LLM upstream** | 7 | 1,4% | `AgentGenerationError` (6) |
| **Suposição sobre dados** | 2 | 0,4% | Formato/valor inválido |
| *(não classificado)* | 1 | 0,2% | — |

497 dos 498 erros classificados. Os dois casos concretos que dominam:

- **`{'result': [[...]]}` indexado como lista** (136 erros, 119 execuções, 7 meses, 4 papéis). O agente escreve
  `docs[0][0]` ou `[d['hashDocumento'] for d in docs[0]]` sobre um dicionário. Uma única unidade de memória
  semântica — o contrato de retorno dessas ferramentas — endereçaria **27% de todos os erros**.
- **Relatório dentro de literal** (159 erros). `final_answer("""# ANÁLISE DETALHADA...` com tabelas markdown e
  texto jurídico dentro; o literal quebra. **Testei e descartei a hipótese de truncamento por limite de tokens**:
  esses steps chegam a 3.894 tokens de saída enquanto steps normais vão a 9.657 — não há teto sendo batido.

### 2.1 · Quem erra: os agentes de domínio, não os orquestradores

Em contagem absoluta, `ConversationAgent` (224) e `managerAgent` (180) dominam — mas isso é só porque concentram
os steps. **Normalizado por step, a ordem se inverte:**

| Papel | Taxa de erro | Steps |
|---|---:|---:|
| CadastroTrabalhista | **35%** | 51 |
| CalculoCivel | **29%** | 58 |
| RespostaBacen | 18% | 135 |
| RoteadorCivel | 11% | 131 |
| ConversationAgent | 9% | 2.478 |
| managerAgent | 8% | 2.325 |
| WorkflowManager | 0,3% | 301 |

Os agentes de domínio erram **3 a 4× mais por step** que os orquestradores. Consequência de projeto: as unidades
de memória devem ser **escopadas por papel**, e os agentes de domínio são o alvo prioritário — não o
`ConversationAgent`, que parecia o problema quando se olhava só o total.

### 2.2 · Cada papel de domínio erra de um jeito específico, não de uma amostra da média geral

Normalizando por papel (% dos erros DAQUELE papel, não do total do dataset) — a única forma de ver o padrão
de papéis de baixo volume, que a contagem bruta esconde:

| Papel | Assinatura dominante | % dos erros do papel | n |
|---|---|---:|---:|
| **CadastroTrabalhista** | Argumento posicional onde só cabe nomeado | **94%** | 18 |
| **CalculoCivel** | Retorno é dict, agente indexa como lista | **76%** | 17 |
| **RespostaBacen** | Retorno é dict, agente indexa como lista | 62% | 24 |
| **managerAgent** | String não fechada | 56% (vs. 45% na média geral) | 180 |
| ConversationAgent | Retorno é dict (45%) + String não fechada (24%) | mix, sem 1 dominante | 224 |

`CadastroTrabalhista` é o caso mais acionável do relatório inteiro: **94% dos seus erros são uma única causa**
(convenção de chamada de ferramenta). Uma unidade de memória procedural só pra esse papel — "sempre chame
ferramenta com argumento nomeado" — endereçaria quase tudo que ele erra. `CalculoCivel` tem o mesmo padrão de
concentração (76%) numa causa diferente (contrato de retorno). Isso confirma que cada papel de domínio tem
uma **assinatura própria**, não uma amostra aleatória da distribuição geral — e reforça que a chave de
recuperação da memória deve ser `(papel, assinatura)`, não uma memória global por tipo de erro.

### 2.3 · Duração por família de erro — tokens e tempo às vezes divergem

> **Teste de robustez aplicado após a primeira versão** (que apontava "Falha do LLM interno" como 115s,
> 10-30× mais lenta que qualquer causa): variar o corte mínimo de amostra mostrou que esse número **não
> sobrevive** a um corte razoável (`n ≥ 10`) — são só 6 pontos, com variância de quase 3 ordens de magnitude
> (6,8s a 818,7s). "Mediana 115s" descrevia o meio de uma amostra minúscula e dispersa, não um fato estável.
> Detalhe do teste em [`03-procedimento-validacao.md`](03-procedimento-validacao.md) §1.6.

Só famílias com amostra confiável (n ≥ 20 — o que sobrevive ao teste):

| Assinatura | Duração mediana | n |
|---|---:|---:|
| Texto do documento colado em literal | 15,6s | 20 |
| Resposta sem bloco de código [INATIVO desde dez/2025] | 15,6s | 33 |
| String não fechada | 15,3s | 159 |
| Retorno é dict | 7,7s | 136 |
| Sintaxe inválida | 7,6s | 39 |
| Tipo diferente do esperado | 7,5s | 22 |
| Argumento posicional | 3,2s | 35 |

**Achado robusto:** entre as famílias com amostra confiável, "string não fechada" (n=159) é **~2× mais lenta**
que "retorno é dict" (n=136) — 15,3s contra 7,7s, diferença real, sobrevive a qualquer corte razoável de
amostra.

**Indício, não fato — não usar como número firme:** duas famílias raras (`Falha do LLM interno` e `Módulo
usado sem import`, n=6 cada) mostram duração elevada e poderiam sugerir que erro de infra é caro em *tempo*
mesmo barato em *token* — hipótese plausível (viria de espera de rede/timeout), mas a amostra é pequena demais
e dispersa demais pra sustentar um número específico. Fica como hipótese a testar com mais dados, não como
achado do relatório.

## 3 · Os erros são custo, não falha

- **0 de 1.550 trajetórias terminam em step com erro**; 100% das trajetórias com erro chegam a `final_answer`.
- Execução **com** erro: mediana 146 mil tokens, 7 steps. **Sem** erro: 48 mil, 5 steps. ~3× o custo.
- 13,9M tokens (9,8% do total) gastos em steps cujo output foi descartado; 159 minutos de latência.
- **Coeficiente de propagação: 1,8×** — P(erro em k+1 | erro em k) = 17,7% contra 9,7% sem erro anterior.

Isso reenquadra a proposta de valor da memória para os erros visíveis: **eficiência e latência, não correção**.
(Para correção, ver o ponto cego em §5.)

### 3.1 · Verificado por conteúdo: o mesmo padrão sobrevive a um teste mais rigoroso

O "0 trajetórias terminam em erro" acima é uma checagem **mecânica** — só confirma que `final_answer(...)`
foi chamado, não que a resposta era boa. Um teste mais exigente: entre as execuções cuja resposta **de fato
tem conteúdo** (não é uma recusa), quantas ainda assim tiveram erro pelo caminho?

O campo de status do banco não serve pra essa checagem — é a mesma anomalia notada em achados anteriores:
das 1.000 execuções, a maioria não tem `dat_hor_encm_exeo`/status de "concluída" persistido, mas **100% das
memórias preservadas contêm um `final_answer` de verdade**. O banco não registra o que de fato aconteceu na
execução. Em vez de inventar um critério de "resposta boa" (lista de palavras — já vimos nesse relatório que
isso é frágil), usei uma **fonte autoritativa dentro do próprio system prompt**: ele instrui o agente a
responder literalmente *"Não encontrado na base"* ou *"Informação insuficiente na base"* quando não consegue
responder. Usei essas duas frases exatas — não uma heurística minha — pra separar resposta de conteúdo de
recusa, no texto que cada execução realmente devolveu ao usuário (`action_output` do `final_answer` do
`managerAgent`).

**Resultado:** 834 de 840 execuções (99,3%) tiveram resposta de conteúdo. Dentro delas:

| | Com erro na trajetória | Sem erro |
|---|---:|---:|
| Resposta com conteúdo | 310 (37,2%) | 524 (62,8%) |

37,2% é praticamente a mesma taxa de erro do dataset inteiro (37,3% das execuções em geral) — o erro não está
empurrando execuções pra fora do grupo "resposta boa". A distribuição de famílias de erro dentro desse grupo é
a mesma do dataset geral (string não fechada 159, retorno-é-dict 136...) — não são só os erros leves que
aparecem em execuções com resposta boa. O custo se confirma: mediana de 148 mil tokens nas execuções com
resposta boa **e** erro, contra 48 mil nas sem erro — o mesmo ~3× de antes, agora verificado dentro do
subconjunto cujo conteúdo se confirmou substantivo.

> **Limite desta checagem:** o detector de "resposta degenerada" só pega as duas frases exatas que o sistema
> declara — não pega pedidos de esclarecimento (ex.: "Por favor, especifique um valor de filtro...") nem
> avalia se a resposta é **factualmente correta**. Prova que o erro não gera recusa; não prova que o conteúdo
> está certo — essa é a pergunta de groundedness, ainda em aberto (§10, item 1).

### 3.2 · A "forma" da chamada confirma o mecanismo de cada erro dominante

A razão tokens de entrada / tokens de saída, por step, separa os dois erros dominantes por um sinal limpo:

| | Mediana in/out |
|---|---:|
| Steps OK (geral) | 33,5 |
| **String não fechada** | **17,5** (bem abaixo — o step está gerando muito texto) |
| **Retorno é dict, indexa como lista** | **58,9** (bem acima — trava logo após receber payload grande) |

Confirma numericamente os dois mecanismos já descritos em prosa: "string não fechada" quebra *gerando*
texto longo; "retorno é dict" quebra *processando* uma entrada grande, quase sem chegar a escrever saída. Um
step com razão anormalmente alta logo após uma chamada de ferramenta pesada é candidato a esse segundo erro
— verificável antes da exceção acontecer, não só depois.

### 3.3 · Eficiência por chamada de ferramenta — um eixo que a taxa de erro não mostra

Taxa de erro mede comportamento errado; tokens por chamada de ferramenta declarada mede quanto custa **uma
unidade de trabalho real**. São eixos independentes:

| Papel | Tokens/chamada | Taxa de erro (§2.1, "quem erra") |
|---|---:|---:|
| **CalculoCivel** | **141.673** (11,6× a mediana por execução) | 29% |
| **CalculoTrabalhista** | **50.624** (4,2×) | 9% — não se destacava por erro |
| ConversationAgent | 27.988 | 9% |
| managerAgent | 18.775 | 8% |

Razão agregada do dataset inteiro: 21.420 tokens/chamada; mediana da execução típica: 12.192 — a agregada é
maior porque o custo é concentrado numa cauda de execuções caras (§3.4), que pesam mais na soma do que numa
mediana simples. `CalculoCivel` é o pior nos dois eixos ao mesmo tempo (erro **e** ineficiência), reforçando
prioridade #1. `CalculoTrabalhista` só aparece como alvo relevante nesta métrica — a taxa de erro sozinha o
esconderia.

### 3.4 · Concentração de custo — a cauda importa mais que a média

| Fatia do topo (por tokens) | Nº de execuções | % de todo o gasto do sistema |
|---|---:|---:|
| 1% | 8 | 16,8% |
| 5% | 42 | 41,9% |
| **10%** | **84** | **54,6%** |
| 20% | 168 | 69,1% |
| 50% | 420 | 89,8% |

**10% das execuções respondem por mais da metade de todo o gasto de tokens do sistema.** Otimizar o caso
médio rende pouco; o retorno de qualquer intervenção está em mirar o perfil dessas execuções-cauda.

### 3.5 · Desperdício em tokens absolutos — três rankings que discordam

Percentual do orçamento de tokens de cada papel perdido em steps com erro, contra o volume absoluto:

| Papel | Tokens totais | Tokens em erro | % desperdiçado |
|---|---:|---:|---:|
| **CalculoCivel** | 7,9M | 2,0M | **25,0%** (pior por %) |
| **ConversationAgent** | 76,8M | **7,5M** | 9,8% (pior por volume absoluto — quase 4× o de CalculoCivel) |
| managerAgent | 45,8M | 3,5M | 7,6% |
| RespostaBacen | 1,8M | 0,39M | 21,3% |

Por **percentual**, `CalculoCivel` continua o pior. Por **volume absoluto**, `ConversationAgent` desperdiça
quase 4× mais tokens que `CalculoCivel`, apesar de uma taxa "saudável" (9,8%) — só porque processa um volume
total muito maior. Os dois critérios apontam pra alvos diferentes; qual seguir depende de o objetivo do
projeto ser "corrigir o comportamento mais quebrado" ou "maximizar economia absoluta".

### 3.6 · Evolução mensal — o sistema não melhora sozinho

Mediana de tokens por execução, mês a mês (jan e mar/2026 têm `n` pequeno demais — 7 e 9 — pra confiar):

| Mês | n | Mediana tokens/execução |
|---|---:|---:|
| nov/2025 | 33 | 56.725 |
| dez/2025 | 208 | 54.086 |
| abr/2026 | 65 | 94.585 |
| mai/2026 | 183 | 81.927 |
| jun/2026 | 268 | 75.430 |
| jul/2026 | 44 | 91.623 |
| ago/2026 | 23 | 61.524 |

Não há tendência de queda: a linha de base de nov–dez/2025 fica em 54–57 mil, e todos os meses de 2026 com
amostra confiável ficam acima disso — abril chega a quase o dobro. Sem melhora orgânica ao longo de 9 meses, o argumento "com o tempo o problema se resolve
sozinho" não se sustenta — reforça que só um mecanismo ativo de memória endereçaria a recorrência já
documentada em §4.

## 4 · O resultado central: o agente lê o erro e reincide

| Medida | Valor |
|---|---:|
| Steps com erro seguidos de outro step | 498 |
| Mensagem de erro **presente no `model_input_messages` do step k+1** | **430 (86,3%)** |
| Desses, erraram de novo no step seguinte | 76 (17,7%) |
| Desses, na **mesma categoria de causa-raiz** | **51 (11,9%)** |

> **Nota de método:** "mesma categoria" é comparado pela taxonomia (`classify()`), não por prefixo/sufixo de
> texto. Um teste de robustez comparando três heurísticas (prefixo de 45 caracteres, sufixo de 45 caracteres,
> categoria da taxonomia) mostrou que prefixo confunde texto genérico de abertura ("Code execution failed at
> line...") com repetição real (dava 13,7%), e que sufixo é rigoroso demais — perde repetições da mesma causa
> em código diferente (dava só 4,3%). A categoria da taxonomia é o nível certo de granularidade, e é o mesmo
> usado no resto do relatório. O "chegou ao contexto" (86,3%) é robusto ao método: prefixo e sufixo convergem
> em 84,9%–86,3%.

E entre execuções: **"string não fechada" aparece em 125 execuções ao longo de 8 meses; "retorno é dict" em 119
execuções ao longo de 7 meses.** Recorde de 10 repetições consecutivas da mesma assinatura num `managerAgent`.

O feedback intra-trajetória existe, é lido, e demonstravelmente não corrige — nem dentro da execução, nem entre
execuções. Este é o caso empírico para memória externa persistente, e é mensurável como métrica de RL
não-paramétrico: *a assinatura S para o papel R voltou a ocorrer depois que a unidade de memória foi escrita?*

## 5 · O ponto cego, agora medido

O TRAIL classifica seus 841 erros por visibilidade a exceção de runtime: **≥59% são estruturalmente invisíveis**
e apenas **3,3%** são integralmente capturáveis pelo método que usei. Mais grave: no split SWE-Bench do TRAIL —
que usa CodeAct + interpretador Python + `final_answer` + allowlist, **arquitetonicamente idêntico à esteira** —
o erro nº 1 não é sintaxe, é **Instruction Non-compliance (35,5%)**, que meu regex quase não vê. E das 304 falhas
de impacto ALTO do TRAIL, ~79% estão em categorias invisíveis a exceção.

Detectores determinísticos que rodei para abrir parte desse ponto cego (nenhum levanta exceção):

| Detector | Resultado |
|---|---|
| **Result-Ignore** — retorno de ferramenta atribuído e nunca usado | **103 de 3.053 (3,4%)** ✅ *robusto* — o número não se move ao excluir ferramentas de efeito colateral nem ao trocar o inventário. E o refinamento fortalece o achado: **96 dos 103 são chamadas caras** (subagente / `answer_question_using_documents`), ou seja, o desperdício se concentra onde custa. Padrão típico: `resposta = WorkflowManager(...)` seguido de `final_answer('Workflow...')`, descartando o retorno |
| **RAC** — chamada idêntica repetida na trajetória, em steps sem erro | **125 repetições redundantes** (número conservador) ⚠️ *sensível à definição* — era 461 com a lista de ferramentas observada e contando `final_answer`; a escolha muda o resultado em 3,7×. A causa: `grab` e `get_meta` não são ferramentas, são funções que o próprio agente define — repeti-las é programação normal |
| ~~**Reasoning-action mismatch** (MAST FM-2.6)~~ | ⚠️ **número retirado** — reprovado no teste de robustez: varia de 0 a 63 steps conforme a lista de palavras de "sucesso" usada. O fenômeno provavelmente existe, mas medi-lo exige anotação de amostra ou juiz LLM, não regex de palavra-chave |
| ~~**Tool-Skip**~~ — chega a `final_answer` sem chamar ferramenta | ⚠️ **número retirado** — o inventário de 43 ferramentas usado no detector estava errado: o system prompt declara **90** (e por papel), e nomes como `grab`/`get_meta` são funções que o próprio agente define, não ferramentas. Refazer com a lista declarada |
| **Nomes de função alucinados (IFN)** | **zero** — nenhum nome chamado gera erro de "não definida". Os nomes fora do inventário são ou ferramentas declaradas que eu não tinha listado, ou funções auxiliares que o próprio agente define e reutiliza |

Ainda **não** investigado e de maior valor: **groundedness da resposta final** — extrair número de processo (CNJ),
CPF/CNPJ, datas e valores do payload do `final_answer` e testar suporte nas observações anteriores. É o erro de
maior impacto do TRAIL e o risco material da esteira.

## 6 · Candidatos a unidades de memória

Triagem fundamentada no AgentDebug: **o módulo que produziu o erro roteia o tipo de memória**; e a política de
escrita é **uma unidade por cascata, na raiz** — não uma por step com erro (a ablação deles confirma que focar
causa-raiz, e não sintomas de superfície, é o que produz ganho).

| # | Candidato | Tipo | Erros | Execuções | Meses | Tokens |
|---|---|---|---:|---:|---:|---:|
| 1 | **Contrato de retorno das ferramentas de documento** — `r['result'][0]`, nunca `r[0]` | semântica | 136 | 119 | 7 | 4,69M |
| 2 | **Relatório longo nunca dentro de literal** — montar por variáveis, depois `final_answer` | procedural | 159 | 125 | 8 | 3,57M |
| 3 | **Toda ferramenta exige argumento nomeado** — `f(arg=v)`, nunca posicional | procedural | 35 | 22 | 6 | 0,36M |
| 4 | **Inventário do sandbox** — imports autorizados; `json`/`pandas` explícitos; sem `openpyxl` | semântica | 11 | 11 | 6 | 0,91M |
| 5 | **Após erro, a variável não existe** — re-derivar, não reusar | experiencial-procedural | 8 | 7 | 4 | 0,30M |
| 6 | `AgentGenerationError`/422 → **retry com backoff**, não memória | harness | 6 | 6 | 3 | 0,02M |
| 7 | **Protocolo do harness [INATIVO]** — gatilho de reabertura, não correção | harness | 33 | 24 | 3 | 0,81M |

> Linhas 4 e 6 corrigidas em 2026-09-09: a tabela publicada trazia 19/19/6/1,10M e 7/7/4/0,12M, que não batiam
> com uma reexecução completa do notebook contra o trace. Valor correto conferido em
> `E[E.assinatura=='Import/ferramenta não autorizado']` e `E[E.assinatura=='Falha do LLM interno']` — ver
> [`01-racionais.md`](01-racionais.md) §7 Passo 5.

**Escopo de escrita:** os candidatos 1–3 são transversais (aparecem em vários papéis), mas a taxa de erro por
papel indica que o *ganho* se concentra nos agentes de domínio. A chave de recuperação da unidade de memória
deveria portanto ser `(papel, assinatura)` — não global. §2.2 confirma isso com números diretos: o candidato 3
sozinho (argumento nomeado) é **94% de todos os erros do `CadastroTrabalhista`** — não é um entre vários
problemas daquele papel, é praticamente o único. Escrever essa unidade escopada a `CadastroTrabalhista`
provavelmente resolveria a maior parte do que esse papel específico erra, mesmo sendo só 7% dos 498 erros do
dataset inteiro — o volume pequeno no agregado esconde que é *quase todo* o problema de um papel específico.

Os candidatos 1 e 2 sozinhos cobrem **59% dos erros e 59% dos tokens desperdiçados**. O candidato 1 é o mais
promissor como **memória semântica viva**: é minerável automaticamente dos próprios traces, sem LLM — agregar os
erros de contrato de retorno e consolidar o schema real observado. Isso é, literalmente, o mecanismo de
atualização de memória alimentado por sinal de erro que o projeto propõe.

**Rebaixado da v1, reintegrado como linha 7 (harness) nesta sessão:** "sempre emitir bloco de código" era
candidato de conteúdo #3 na v1. Os 33 casos estão concentrados em dez/2025 (31 deles, 21,0 erros/1k steps) e
**desaparecem a partir de mai/2026** (0 em 3.461 steps; IC95% para zero eventos ≤ 0,87/1k, 24× abaixo do pico
do incidente) — não é candidato de conteúdo, o agente não tem nada pra aprender aqui. Mas a v1→v2 tinha
descartado o achado por completo, sem registro estruturado, enquanto o outro achado de harness da mesma
triagem (linha 6, `AgentGenerationError`) virou linha formal na tabela mesmo sem ser memória de conteúdo. Regra
aplicada de forma inconsistente entre os dois — corrigido aplicando a mesma régua aos dois: linha 7, mesmo
`tipo="harness"`.

Isso também não é "resolvido" — não sabemos a causa (o harness é infra de terceiro, fora do nosso controle) nem
temos garantia de que não volta. É **inativo**, com gatilho de reabertura explícito como conteúdo da linha:
**≥2 casos num mês, ou taxa > 1/1k steps, reabre o candidato** (limiar = teto do IC95% acima). Tratado como
memória dormente, não deletada — teste de caso para a política de aposentar/reativar unidades de memória que o
mecanismo do projeto precisa ter, não só criar. Passo a passo completo da construção desta tabela e do gráfico
em [`01-racionais.md`](01-racionais.md) §7.

## 7 · O que a leitura dos papers refutou

Três afirmações da v1 não sobreviveram:

1. **"Suposição sobre dados ≡ erros de argumento do ToolScan."** Testei quebrando o balde `TypeError` pelos
   padrões que identificam IAN (nome de argumento alucinado) e IAV (obrigatório omitido): **1 caso de IAN, zero de
   IAV.** A família é uma classe **ausente** das taxonomias de tool-call estruturado — suposição sobre o *schema
   de retorno*, que só existe porque no paradigma CodeAgent o modelo precisa **manipular** o retorno em código,
   não apenas lê-lo. A migração do erro do ponto-de-chamada para o ponto-de-manipulação é, em si, um resultado.
2. **O mapeamento ao MAST não se sustentava.** MAST rotula por *trace*, binário, como diagnóstico de causa-raiz
   organizacional; o meu rotula por *step*, como sintoma. Os percentuais não são comparáveis. E o MAST **não tem
   nenhum modo de falha para "o código levantou exceção"** — os autores põem isso explicitamente fora de escopo.
   Minha família dominante cai justo na zona que o MAST excluiu de propósito. Isso é achado, não fracasso: a
   arquitetura CodeAgent expõe uma superfície de falha que os 7 sistemas do MAST não expõem, porque neles a ação
   do agente é *mensagem*, não *código executável*. O simétrico é mais forte: no paradigma estruturado o erro de
   formato está praticamente resolvido (GPT-4 marca 1.00 em IFE), e no CodeAgent ele **ressurge como a categoria
   dominante** — um custo do paradigma que a literatura de benchmark não mede.
3. **A taxonomia do ToolScan que citei estava parcialmente inventada.** O sumarizador de busca devolveu sete tipos
   ("Tool Hallucination, Argument Hallucination, Invalid Tool Invocation…") que **não aparecem no paper**. Os sete
   reais são IAC, IAV, IAN, IAT, RAC, IFN e IFE. O paper também mudou de nome entre versões (v1 = *SpecTool*).
   Confabulação do sumarizador — exatamente o risco de citar por snippet.

## 8 · Ancoragem na literatura (texto completo lido por subagente, 🔎)

- **MAST** — Cemri, Pan, Yang et al., UC Berkeley, **NeurIPS 2025 Datasets & Benchmarks**, arXiv:2503.13657v3.
  14 modos em 3 categorias. Encaixes que **se sustentam**: import não autorizado → FM-1.1; repetição de assinatura
  → FM-1.3 (o modo mais frequente da taxonomia, 15,7%). Alerta metodológico do Apêndice J.1: *"Successful runs are
  not failure-free"* — modos de verificação aparecem em execuções bem-sucedidas, e minha análise inteira está
  condicionada em `err_type != null`.
- **TRAIL** — arXiv:2505.08638 (Patronus AI). Fornece o tamanho medido do ponto cego (≥59%) e o schema de anotação
  reusável. O 11% do abstract é *joint accuracy* (categoria + localização); decomposto, a localização chega a 0,82.
  Como **já tenho a localização de graça**, o problema vira classificação — viável, desde que se mande **um step**
  por vez, não o trace inteiro (a performance é anticorrelacionada com o comprimento de entrada, r = −0,38).
- **AgentDebug** — arXiv:2509.25370. Aporta o roteador módulo→tipo-de-memória, a política "uma unidade por
  cascata", e o schema do registro de feedback (tipo, evidência, diretiva, proveniência, escopo do dano) como
  schema da unidade de memória. **Não é precedente de memória persistente**: o Stage 3 é re-rollout intra-tarefa,
  inaplicável a uma esteira com efeitos colaterais reais e desfecho esparso e atrasado.
- **ToolScan / SpecTool** — Kokane et al., Salesforce AI Research, **Building Trust Workshop @ ICLR 2025**,
  arXiv:2411.13547v2. O achado mais relevante para a tese é o **mecanismo de feedback (§5 do paper original)**: injetar no contexto
  o inventário correto de ferramentas/argumentos derivado do erro observado, medindo ganho de sucesso sem tocar em
  pesos — literalmente atualização de memória não-paramétrica, e o antecedente mais próximo do mecanismo do
  projeto. Ele cobre o lado **semântico** (inventário); o **procedural** ("quando X falhar, faça Y") está aberto.
  Nota lateral útil: o paper observa que modelos de código superam modelos gerais maiores em function calling —
  argumento a favor do paradigma CodeAgent adotado pela esteira.
- **ToolFailBench** — Harsh Soni (UC Berkeley), arXiv:2607.04686v1, *ICML 2026 Workshops*. Define quatro modos
  (Tool-Skip, Result-Ignore, Output-Fabrication, Unnecessary-Tool-Use) — o snippet que a v1 citou trazia só três.
  **Tem direito entre seus cinco domínios profissionais**, e seu mecanismo de "armadilha paramétrica" (o retorno
  da ferramenta contradiz de propósito um valor memorizado no pré-treino) é um desenho de avaliação diretamente
  transportável para medir se a esteira responde do documento ou da memória do modelo.

## 9 · Limitações

- **Amostra**: exatamente 1.000 linhas (provável `LIMIT`); proporções são estimativas. O pico de taxa de erro em
  mar/2026 (16%) assenta sobre 43 steps.
- **Semântica dos status** (1/2/3/34) foi inferida por correlação, não confirmada com o time da esteira.
- **Comparações com os datasets dos papers são indicativas, não métricas**: um *span* do TRAIL ≠ um `ActionStep`;
  e os traces do TRAIL têm erro **parcialmente induzido por desenho experimental**, então sua distribuição não é
  taxa-base natural.
- **PII**: o payload traz nomes de clientes e números de processo em claro. `resultados/` está no `.gitignore`
  local; o `.csv.xz` não deve ser versionado em claro.

## 10 · Próximos passos, em ordem de valor

1. **Groundedness-como-presença do `final_answer` (determinístico)** — tokens tipados (CNJ, CPF/CNPJ, datas,
   valores) sem suporte textual nas observações. Proxy, não prova de correção — mas é regex puro, sem LLM,
   cabe no princípio de pipeline determinístico já documentado (ver
   [`../../../discussion/open-questions.md`](../../../discussion/open-questions.md)). Maior impacto no TRAIL e maior
   risco material da esteira. A versão que exigiria juiz LLM (a citação está *certa*, não só presente) fica
   fora do v1 — é observabilidade/agent-evals.
2. **Minerar o candidato 1 automaticamente** — consolidar o schema real de retorno a partir dos próprios erros,
   sem LLM. É o protótipo direto do mecanismo do projeto.
3. **Rodar os detectores nas execuções SEM erro — versão determinística primeiro** — o MAST mostra que os
   modos de verificação vivem lá, e 63% das minhas execuções estão fora da análise atual. Tentar primeiro o
   proxy determinístico (padrão de validação no `code_action` — `assert`/`if not`/`len(`/`try-except` antes de
   usar um valor, vs. steps que só consomem sem checar); juiz LLM só se isso não bastar.
4. **Segunda extração sem `LIMIT`** e confirmação dos códigos de status com o time da esteira.
5. **Instruction Non-compliance** — enumerar as regras explícitas do system prompt e escrever um detector
   determinístico por regra (é o erro nº 1 na arquitetura idêntica à nossa).
6. **Resolver Tool-Skip de vez** — hoje marcado `[PROVISÓRIO]` no notebook: deu 14, 8 e 10 execuções conforme
   o inventário de ferramentas usado, nunca convergiu num número testado. Extrair as 90 ferramentas declaradas
   **por papel** (não a união de todos) do `model_input_messages[0]` e recomputar. O inventário por papel
   também é insumo direto do candidato de memória nº 4 (hoje escrito a partir de observação, não da fonte
   autoritativa).
7. **Reasoning-action mismatch — versão determinística primeiro** — o detector por palavra-chave foi retirado
   por estar conceitualmente errado (ver [`01-racionais.md`](01-racionais.md) §2), isso não muda. Mas existe
   uma versão estrutural, sem juiz: comparar o agente/ferramenta que o *thought* anuncia (regex) contra o que
   o `code_action` de fato chama (AST) no mesmo step — divergência é candidato, determinístico. Só cogitar
   juiz LLM se isso não capturar o fenômeno.
8. ~~Gráficos para os achados desta rodada~~ — **feito em 2026-09-08**: 6 gráficos construídos (§8.7–8.12),
   2 avaliados e deliberadamente não construídos (3.2, 2.3).

## Fontes

Todas verificadas contra o PDF (autoria, ID, data e venue lidos do próprio texto), não contra resumo de busca:

- Cemri, Pan, Yang et al. **Why Do Multi-Agent LLM Systems Fail?** UC Berkeley. NeurIPS 2025, Datasets & Benchmarks.
  [arXiv:2503.13657v3](https://arxiv.org/abs/2503.13657)
- Deshpande, Gangal et al. **TRAIL: Trace Reasoning and Agentic Issue Localization.** Patronus AI.
  [arXiv:2505.08638](https://arxiv.org/abs/2505.08638) · [dataset](https://huggingface.co/datasets/PatronusAI/TRAIL)
- **Where LLM Agents Fail and How They can Learn From Failures** (AgentDebug).
  [arXiv:2509.25370](https://arxiv.org/abs/2509.25370) · [código](https://github.com/ulab-uiuc/AgentDebug)
- Kokane et al. **ToolScan: A Benchmark for Characterizing Errors in Tool-Use LLMs.** Salesforce AI Research.
  Building Trust Workshop @ ICLR 2025. [arXiv:2411.13547v2](https://arxiv.org/abs/2411.13547)
  — *publicado originalmente como* **SpecTool**; citar os dois nomes.
- Soni, H. **ToolFailBench: Diagnosing Tool-Use Failures in LLM Agents.** UC Berkeley. ICML 2026 Workshops.
  [arXiv:2607.04686v1](https://arxiv.org/abs/2607.04686)
