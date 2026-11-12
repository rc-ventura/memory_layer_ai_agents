> **Sub-atividade:** 1.6 / 1.7 (alimenta 2.2, 2.4 e 3.6) · **Tipo:** Plano de experimento genérico (pré-registro em rascunho), com adendo por unidade · **Status:** proposta para aprovação · **Data:** 12/11/2026

# Plano do experimento — a memória injetada reduz o erro e compensa o custo?

> Os termos do projeto (degrau da validação, unidade, sinal de harness, memória de reforço) estão explicados no
> [glossário](../analysis/glossario.md). O plano usa nomes; um identificador interno só aparece, entre parênteses, numa
> coluna de fonte.

## 0. O que este documento é

O plano, do início ao fim, do **degrau 4 da validação** ([`17-validacao-memorias.md`](../analysis/2026-09-trace-law-flow/docs/17-validacao-memorias.md)):
o experimento que diz se uma memória, injetada, reduz o erro sem criar outro, e se a economia paga o custo de
injetar (o teste de compensação, que o roadmap da base 3 já previa).

**Ele vale para qualquer unidade de memória.** O protocolo (braços, medidas, estatística, etapas, critério de sucesso)
é o mesmo; o que muda de uma unidade para outra está num **adendo**, escrito pela ficha do §16:

| Adendo | Unidade | Estado |
|---|---|---|
| [A · Inventário do sandbox](plano-experimento-adendo-sandbox.md) | erros por usar algo que o interpretador do agente barra (como `repr`) ou por esquecer um import que ele aceita (como `json`): as 3 memórias que chegaram ao degrau 3 | rascunho; é a primeira rodada |
| [B · Memória consultada no erro](plano-experimento-adendo-memoria-no-erro.md) | não é uma unidade: é um **braço** (a memória entra por um middleware depois do erro), com medida e poder próprios; vale para toda unidade | rascunho; o braço segue exploratório neste plano |
| (próximos) | qualquer unidade cuja memória chegue ao degrau 3 | a escrever pela ficha do §16 |

Regra de leitura: o que está neste documento vale para toda unidade; um número ou nome de papel só aparece aqui como
**exemplo declarado**, e o valor medido fica no adendo. Onde uma escolha do protocolo foi feita olhando só a primeira
unidade, o texto diz que ela é uma hipótese de generalidade (§2.3).

Este plano **não substitui** o [blueprint das POCs](blueprint-m1-pocs-minimos.md). O blueprint lista oito experimentos
sobre o mecanismo inteiro. Este plano detalha o primeiro que dá para rodar com o que já existe: memórias revisadas e o
smolagents. Onde ele entra no blueprint, e onde diverge dele:

| No blueprint | Neste plano | Divergência, e por quê |
|---|---|---|
| E0 · setup, backend de LLM, Harbor × runner próprio | etapa 0 | o plano supõe o **runner próprio** (ferramentas simuladas como funções Python do smolagents); a decisão do blueprint segue aberta (§15) |
| E1 · a suíte de tarefas (grupos A–D, sintéticos) | §7: tarefas **por memória** do catálogo — uma unidade se divide em partes, e cada parte gera memórias com lição e escopo próprios (global ou de um papel); a tarefa-gatilho provoca o erro daquela memória, naquele papel | a suíte do blueprint foi pensada antes das memórias existirem (o grupo A era a ferramenta de documento da base 1). Aqui as tarefas nascem do erro-alvo de cada memória. Os grupos B (sinal de harness), C (casos triviais) e D (falha silenciosa) não estão neste plano |
| E3 · POC-B (smolagents + memória programática) | a parte de leitura: injetor, ferramenta `recall_memory`, registro | o caminho de escrita da POC-B (log, gate de promoção, decaimento) fica fora (§14) |
| EX-1 · recall explícito × injeção nativa | braços "injetada" × "por ferramenta" (hipótese 3) | sem o braço Hermes. A "injeção automática" daqui é a memória **nativa no contexto do agente**, numa região `<memory>` no prompt de sistema, com o conteúdo escolhido em tempo de execução por uma heurística; não é a injeção do laço do Hermes, que lê a memória pelo próprio mecanismo dele |
| EX-2 · redução de recorrência entre execuções | só a comparação final: memória já persistida × sem memória | a curva de aprendizado ao longo de "meses" simulados **não** é medida: a memória é congelada (§6). Isso continua no EX-2 do blueprint |
| Regime temporal: N ≈ 20–30 execuções por tarefa | 3 a 5 repetições por tarefa, com muitas tarefas | o poder vem do número de tarefas; repetir a mesma só encolhe a variação dentro dela (§9.1; Miller, 2024, §3.1). O "3 a 5" é de partida, e o piloto escolhe `K` |
| Q4 · implícito × explícito (Sub 1.7) | braço "autogerada" (hipótese 8) | o polo implícito aqui é o próprio smolagents escrevendo a lição, não a conversão sessão→skill do Hermes |
| EX-8 · memória de reforço | braço exploratório (§6.1) | igual |
| §8 · critério de "pronto" (os 6 casos de fronteira, uma execução lida inteira, falhas que não são do agente separadas) | etapas 2 e 7 | igual |
| EX-3 a EX-7 (gatilho, gate, destino memória × harness, promoção, esquecimento) | — | fora deste plano (§14) |

Nada aqui foi rodado. Toda previsão está escrita como hipótese. O que é fato medido traz a fonte.

## 1. Resumo

| | |
|---|---|
| **Pergunta** | A memória revisada reduz o erro que ela descreve? A economia de tokens e de tempo paga a injeção? Qual forma de entrega funciona: injetada no contexto (nativa, na região `<memory>`), por ferramenta ou só depois do erro? E ela vale mais que a lição que o agente escreve sozinho, sem gate (o implícito × explícito do Sub 1.7)? |
| **Memórias testadas** | Toda memória do catálogo no degrau 3 (revisada) de uma unidade; a lista e os textos literais ficam no adendo da unidade. As que estão no degrau 1 ou 2, ou monitoradas, entram só como exploratórias |
| **Agentes** | Trilha 1 (já): agentes mínimos em smolagents que espelham os papéis onde o erro da unidade mora. Trilha 2 (quando a permissão sair): os agentes reais, no mesmo protocolo |
| **Braços** | sem memória · memória injetada no contexto · memória por ferramenta · memória no erro · placebo · memória autogerada (sem gate) |
| **Unidade de observação** | uma execução do agente numa tarefa sintética, com ferramentas simuladas; pareada por tarefa |
| **Medida principal** | a execução teve o erro da unidade? (classificado pelas mesmas regras do pipeline, sem LLM) |
| **Medida de compensação** | tokens totais e tempo por execução, com × sem memória (já incluem o custo da injeção) |
| **Métricas do Plano** | as três do Sub 3.6 — taxa de sucesso, estabilidade, latência — e o custo em tokens; a latência é decomposta em modelo, ferramenta e interpretador (§8) |
| **Tamanho** | por agente-espelho: piloto de 130 execuções por modelo; confirmatório de 2.160 (versão cheia) ou 1.080 (enxuta), com 6 braços; o total é esse valor vezes o número de agentes-espelho da unidade (§9) |
| **Sucesso** | erro cai (teste corrigido para comparações múltiplas), tokens líquidos caem na incidência real do papel, sucesso da tarefa e latência não pioram além da margem, placebo não reproduz o efeito (§11) |
| **Modelo** | Fator do experimento, não detalhe: a plataforma trocou de modelo em agosto/2026. O piloto roda no modelo antigo e no atual do papel e decide o principal (§5.3) |
| **Fonte de verdade** | A base 3 dá as taxas reais (contagens + a v2 de erros). As bases 1 e 2 dão o que a base 3 não tem: prompt, modelo, execução inteira (§2.1) |

## 2. O que a análise do repositório impõe ao desenho

Cada linha é um fato do repositório que vale para qualquer unidade, e a consequência para o experimento. Os fatos que
são de uma unidade só estão no adendo dela.

| Fato | Fonte | Consequência |
|---|---|---|
| Só as memórias no degrau 3 (revisada) estão prontas para o degrau 4; as demais do catálogo são monitoradas, não injetadas | [`memorias.json`](../analysis/registros/memorias.json); [`decisoes.md`](../analysis/decisoes.md) | O teste confirmatório usa só as do degrau 3. O resto entra como exploratório |
| Uma memória pode valer só junto com outra (`vale_junto_com`) ou não valer em um papel (`nao_vale_em`) | catálogo; doc 17, Ajustes 30 e 31 | O injetor lê os dois campos. Memórias dependentes são testadas como par, nunca sozinhas, e o papel excluído não recebe a memória |
| A revisão do degrau 3 vale para o texto exato da memória | [`17`](../analysis/2026-09-trace-law-flow/docs/17-validacao-memorias.md), "O degrau 3 no catálogo" | O texto injetado é o `correction_guidance` literal, sem reescrita |
| Um passo médio custa ≈ 13.135 tokens; as candidatas somam 387 mi de tokens, 10,4% do gasto (teto, hipótese) | [racionais da base 3, §7](../analysis/2026-10-trace-law-flow-third/docs/01-racionais.md) | A medida de compensação é em tokens, por papel, nunca pelo total |
| A comparação tem de ser por taxa e por papel: a mistura de papéis muda o custo sem mudar a eficiência | racionais §7; roadmap da base 3 (gráfico da taxa por papel e mês, #37) | Análise estratificada por agente; nada de somar agentes diferentes |
| A classificação do erro é determinística (família → assinatura → mecanismo → unidade) | [`09-metodologia-erro-a-memoria.md`](../analysis/2026-09-trace-law-flow/docs/09-metodologia-erro-a-memoria.md) | A medida do experimento usa as mesmas regras: o instrumento que achou o erro é o que mede se ele sumiu |
| A plataforma trocou de modelo em agosto/2026, e a taxa de um erro de protocolo mudou com a troca (no RoteadorCivel: 0 erros em 381 passos no modelo antigo; 54 em 478 no novo, com o mesmo prompt) | [relatório da base 2, §2](../analysis/2026-09-trace-law-flow-second/docs/02-relatorio-base2.md) | A taxa de erro depende do modelo. Uma memória validada num modelo não está validada no outro: o modelo é um fator do experimento |
| Agosto/2026 concentra 58% dos erros observáveis da base 3, e a base 3 não exporta o nome do modelo | [relatório da base 3](../analysis/2026-10-trace-law-flow-third/docs/02-relatorio-achados.md), TL;DR; roadmap da base 3, pedido C | Não se sabe, pela base 3, em que modelo cada erro aconteceu. A base 2 pode responder para agosto (§10, etapa 1) |
| Nenhum conteúdo de trace real entra em prompt de LLM externo | blueprint §7, item 6; [`analysis/README.md`](../analysis/README.md) | Tarefas e retornos de ferramenta são sintéticos |
| A arquitetura supõe `recall_memory` como ferramenta MCP chamada dentro do loop; o tutor questionou (28/08) se um retrieval elaborado é necessário num escopo tão estreito | [arquitetura, §F](../discussion/hipoteses/knowledge-as-infra-architecture-hypothesis.md); [reflexões de 28/08](../discussion/reflexoes/checkpoint-2026-08-28-reflections.md) | O braço "memória por ferramenta" contra o "injetada" é o teste direto dessa hipótese |
| O caminho quente não leva chamada de LLM | arquitetura, §A | Nenhum braço usa LLM para escolher ou reescrever a memória |
| O Plano define três métricas de desempenho: taxa de sucesso, estabilidade, latência; a arquitetura pede tokens como métrica de primeira classe ao lado delas | [Plano de Trabalho](../docs/work-plan.md), Sub 3.6; [arquitetura, §D](../discussion/hipoteses/knowledge-as-infra-architecture-hypothesis/06-component-d-commit-gate.md), "custo de LLM" | As quatro entram no experimento, cada uma com definição e análise (§8) |
| Um update aprovado escreve só na camada de estratégia, nunca no prompt de sistema dos repositórios: prompt que cresce é inchaço de tokens e quebra a revelação progressiva | [arquitetura, "Scope clarification"](../discussion/hipoteses/knowledge-as-infra-architecture-hypothesis/09-add-trigger-and-scope-clarification.md) | O braço "injetada" não edita o prompt do agente: o harness compõe o contexto na hora, a partir do catálogo, filtrado por papel, e registra o que entrou (§6) |
| O laço de validação da arquitetura roda num simulador: ferramentas simuladas com respostas gravadas; passa se a assinatura do erro não volta e nenhum caso limpo regride; a verificação é determinística | [arquitetura, §C, 09/09](../discussion/hipoteses/knowledge-as-infra-architecture-hypothesis/05-component-c-update-engine.md) | Este experimento é a primeira construção desse simulador; as tarefas neutras são os "casos limpos" (§7) |
| Quase nenhuma execução da esteira termina em erro (0 de 1.550; 99,3% entregam resposta): a cascata é cara, mas se recupera | arquitetura, §C, 09/09 (base 1) | O sucesso da tarefa está perto do teto. O efeito de uma memória aparece em custo e tempo, não em sucesso: sucesso é guarda, não alvo |
| "Latência não necessariamente melhora com uma memory layer efetiva: um trace lento pode ser infra instável ou latência do modelo" | [política de promoção](../discussion/hipoteses/promotion-policy-log-to-ltm.md), "Observabilidade" (02/09) | A latência é decomposta e o tempo de ferramenta, controlado; o tempo economizado vem da duração real do passo com erro (§8.3) |
| Toda execução que falhou se classifica numa de 8 causas (capacidade, informação ausente, harness, ambiente, falsa rejeição, falsa aceitação, vazamento, infraestrutura), e o que não é do agente se conserta antes de usar a nota; o que o projeto mede é o **delta** que a mudança causa, não o desempenho absoluto | [Eval Engineering, conexões §4, §6](../discussion/hipoteses/eval-engineering-skill-architecture-connections.md); [análise da skill](../discussion/hipoteses/langchain-eval-engineering-skill-analysis.md), "What does NOT map" | Etapa 7 (§10) e §13; a medida principal é sempre uma diferença entre braços |
| O Sub 1.7 pede comparar aprendizado implícito e sinal explícito | Plano, Sub 1.7 | O braço "autogerada" é o polo implícito dentro do smolagents (§6) |

### 2.1 O papel de cada base no experimento

A base 3 é a fonte de verdade, mas só tem as contagens e a v2 dos erros. O experimento usa cada base para o que ela
consegue responder:

| Base | O que tem | O que entrega ao experimento | O que não entrega |
|---|---|---|---|
| **Base 3** (ambiente da base; a real) | As contagens de todos os passos e execuções, por papel e mês (283.925 ActionSteps); a v2 dos erros: cada passo com erro, a mensagem inteira, o código, os tokens e a janela do passo anterior aos dois seguintes | **A incidência real `π`** de cada memória por papel e mês (execuções com o erro ÷ execuções do papel); os tokens do passo que errou e do seguinte; os passos por execução; o teto de economia por papel | O prompt, o modelo, as execuções sem erro, a recuperação além de dois passos. Por isso o custo `c` da memória numa execução limpa **só o experimento mede** |
| **Base 2** (ambiente da base; trace inteiro, lote de ago/2026) | 1.000 execuções completas, com prompt e modelo por passo | O prompt e as listas de ambiente de cada papel para a ficha de fidelidade (`extrair_prompts_base2.py`, `extrair_ambiente_base2.py`); **o modelo de cada erro da unidade em agosto**; os contextos reais para o replay de passo da trilha 2 | Taxas confiáveis: é amostra de 1.000, com 479 erros |
| **Base 1** (local; trace inteiro, out/2025–ago/2026) | 1.000 execuções completas (840 com os passos), 498 erros | Desenvolver e testar aqui todo script antes de levar ao ambiente; o formato do registro; o modelo por papel até agosto | Volume nos papéis de cada unidade: é dominada pelo `managerAgent` e pelo `ConversationAgent` |

Duas consequências:

1. **Nenhum número da base 3 é afirmado aqui sem ter vindo do ambiente.** Os que o plano usa (13.135 tokens por passo,
   283.925 passos) estão nos racionais e no relatório da base 3. Os de cada unidade (contagem de erros por papel) estão
   no dossiê dela e são citados no adendo; os que faltam (`π` por papel) são a etapa 1.
2. **A medida de compensação junta duas fontes:** `c` e `s` saem do experimento; `π` sai da base 3. O `s` do experimento
   é conferido contra os tokens do passo com erro na v2 — se o passo perdido do espelho for muito menor que o real, a
   conta usa o real e diz isso. O mesmo vale para o tempo: a duração de um passo com erro vem da v2 (§8.3).

### 2.2 O que o experimento testa da arquitetura

| Peça da [arquitetura](../discussion/hipoteses/knowledge-as-infra-architecture-hypothesis.md) | Testada? | Como |
|---|---|---|
| Leitura da memória (componentes A e F: `recall_memory` × entrega automática) | **sim** | braços "injetada" × "por ferramenta" — a pergunta do recall explícito (blueprint, experimento do recall explícito), sem o Hermes |
| Valor de uma memória já aprovada (o degrau 4) | **sim** | todos os braços contra "sem memória" e "placebo" |
| Implícito × explícito (Sub 1.7) | **sim**, no smolagents | "autogerada" (sem gate) × "injetada" (revisada no degrau 3) |
| Laço de validação no simulador (§C, passos 3–4) | **sim**, a primeira versão | tarefas com ferramentas simuladas, casos limpos como controle |
| Leitura da STM pelo adapter (opção A de [`open-questions.md`](../discussion/open-questions.md)) | **em parte** | o registro lê `agent.memory.steps` e o grava no formato do trace |
| Escrita: filtro de anomalia, Update Engine, Commit Gate, esquecimento, consolidação | **não** | §14 |

### 2.3 O que varia de uma unidade para outra — e o que é hipótese de generalidade

O protocolo foi desenhado olhando a primeira unidade (o sandbox). Este quadro separa o que o desenho garante para
qualquer unidade do que ele só supõe.

| Dimensão | Varia por unidade? | Onde fica |
|---|---|---|
| Braços, medidas, estatística, etapas, critérios | não: é o protocolo | este documento |
| O erro-alvo (a regra do classificador, a mensagem, o passo) | **sim** | adendo, ficha §16.2 |
| Papéis onde o erro mora; incidência `π`; meses | **sim** | adendo, §16.3 |
| Tipo da lição: **fato do ambiente** (o que o sandbox aceita) ou **estratégia** (como agir) | **sim** | adendo, §16.4 |
| Como se faz o erro acontecer numa tarefa sintética (a tarefa-gatilho) | **sim** | adendo, §16.6 |
| Modelo(s) em que o erro acontece | **sim** | adendo, §16.5 |
| Tamanhos (taxa de base, `ρ`, número de espelhos) | **sim**, mas pela mesma fórmula do §9 | adendo, §16.8 |

**Hipóteses de generalidade** (o que pode não valer numa unidade de outro tipo):

1. *A memória por ferramenta perde para a injetada* (hipótese 3): o argumento é sobre lições de **fato do ambiente com
   chave por papel**. Numa lição de estratégia, em que a lição só é útil naquele passo, pode dar outro resultado.
2. *O espelho consegue reproduzir o erro.* Para um erro de fato do ambiente (o interpretador barra uma função), basta o
   mesmo interpretador. Para um erro de **contrato de ferramenta** (o retorno que chega como texto, o argumento que só
   aceita nome=valor), o espelho só erra se a ferramenta simulada reproduzir o contrato real, e isso exige a definição
   da ferramenta (§5.4). O risco da trilha 1 é maior.
3. *A taxa de base de 20% nas tarefas-gatilho é alcançável.* Depende do erro: um erro que o modelo comete por hábito é
   fácil de provocar; um erro que depende de uma instrução específica do prompt, não.
4. *O classificador do pipeline reconhece o erro nos dados sintéticos.* Vale para qualquer unidade (as regras são as
   mesmas), mas cada unidade precisa do teste de conferência do §12.

A primeira unidade nova que passar por este protocolo é, ao mesmo tempo, um teste de generalidade: se alguma dessas
quatro hipóteses falhar, o §2.3 é atualizado e o adendo registra o desvio.

## 3. O SDK de memória interno: usar neste experimento?

**Não.** A análise já feita ([`internal-memory-sdk-vs-mechanism.md`](../discussion/hipoteses/internal-memory-sdk-vs-mechanism.md),
só pela documentação, sem ler o código) dá os motivos, e este experimento acrescenta dois:

1. **Ele guarda outra coisa.** O SDK lembra do cliente (perfil, preferências); as memórias daqui são sobre o trabalho do
   agente (o que o ambiente aceita, o contrato de uma ferramenta).
2. **Toda escrita passa por um juiz LLM dele.** Não há, na documentação, uma operação para gravar um texto aprovado como
   está. O texto do degrau 3 seria reescrito, e a revisão deixa de valer.
3. **Só roda com as credenciais do gateway interno**, isto é, no ambiente da empresa, não aqui.
4. **Novo — com poucas memórias por papel, a recuperação é uma consulta por chave.** A chave já existe (papel, e
   ferramenta quando houver). Busca semântica acrescenta um ponto de falha sem ganho: num estudo de diagnóstico, a maior
   parte das falhas de memória estava na recuperação, não no uso do que foi recuperado (Yuan et al., 2026). Se uma
   unidade tiver muitas memórias por papel, esse argumento deixa de valer e o item entra no adendo.
5. **Novo — o SDK entraria como mais uma variável.** No mínimo três chamadas de LLM por turno mudariam custo e latência
   de todos os braços e esconderiam o efeito que se quer medir.

Como **braço de comparação** (a ideia do §4a daquela nota), ele fica para depois deste experimento, e só no ambiente da
empresa.

**O que dá para aproveitar já, como desenho** (nada disso exige o SDK instalado):

| Ideia do SDK | Onde entra aqui |
|---|---|
| Contadores de uso (`mention_count`, `last_mentioned_at`) | O registro de cada execução anota qual memória foi entregue e se foi usada. É a matéria-prima do decaimento, sem custo agora |
| Histórico encadeado (`previous_memory_id`, `is_current`) | O arquivo de memórias do experimento guarda a versão e o hash do texto; trocar o texto cria versão nova, não sobrescreve |
| Parâmetros fora do código (`config.yaml`) | Braços, tarefas, modelo e tamanho de amostra ficam num arquivo de configuração congelado no pré-registro |
| Detecção de duplicata por similaridade de texto (> 0,85) | Só quando o catálogo crescer; fora deste experimento |
| Fórmula de ranking (`W_global`) | Fora: não há o que ordenar com poucas memórias |

## 4. Perguntas e hipóteses

Escritas antes dos dados, e as mesmas para toda unidade. As hipóteses 1 a 4 e a 8 são confirmatórias; a 5, a 6 e a 7,
exploratórias (Nosek et al., 2018, sobre separar previsão de exploração). Cada adendo pode acrescentar hipóteses
próprias, rotuladas como tal.

| # | Pergunta | Hipótese | Por que se espera isso |
|---|---|---|---|
| 1 | A memória injetada no contexto (região `<memory>`) reduz o erro da unidade? | Reduz, nas tarefas em que o erro pode acontecer | Instruções em arquivos de contexto são seguidas pelos agentes (Gloaguen et al., 2026); documentação de ferramenta substitui exemplos (Hsieh et al., 2023); lições extraídas de falhas melhoram execuções seguintes (Shinn et al., 2023; Zhao et al., 2024; Ouyang et al., 2025; Suzgun et al., 2025) |
| 2 | A economia paga a injeção, em tokens e em tempo? | Paga, se a incidência real do erro no papel passar de um limiar baixo (§8.2). No tempo, a memória acrescenta a leitura de dezenas de tokens e o erro evitado tira um passo inteiro (§8.3) | A memória tem dezenas de tokens e o passo perdido, milhares. Mas contexto a mais tem custo próprio: arquivos de contexto gerados por LLM subiram o custo em ~20% e os passos em 2,5–3,9 sem mudar o sucesso (Gloaguen et al., 2026) |
| 3 | A memória por ferramenta funciona tão bem quanto a injetada? | Não, para lições de fato do ambiente com chave por papel (hipótese de generalidade, §2.3) | O agente não sabe que vai cometer o erro, então não tem por que consultar; e no `CodeAgent` consultar custa um passo, o mesmo que o erro custaria. Em memória por ferramenta (o desenho do MemGPT, Packer et al., 2023), a qualidade depende de o agente decidir chamar — apontado na descrição dos sistemas, **sem medida direta que eu tenha encontrado** na busca desta rodada; é justamente o que o braço testa |
| 4 | O efeito é do conteúdo ou de qualquer texto a mais? | Do conteúdo: o placebo não reduz o erro | Texto irrelevante no prompt muda o comportamento do modelo (Shi et al., 2023); sem placebo não se separa uma coisa da outra |
| 5 | A memória entregue só depois do erro ajuda? | Não evita o primeiro erro; encurta a recuperação quando o erro se repete em cascata | Realimentar a correção no passo crítico recupera execuções (Zhu et al., 2025; Ma et al., 2025) |
| 6 | Consertar o ambiente vale mais que a memória? | Sim, onde o conserto existe | É a fronteira memória × sinal de harness do projeto; serve de teto prático |
| 7 | Mais memórias no prompt pioram? | Pioram custo; efeito no erro incerto | Desempenho cai com contexto maior (Hong et al., 2025; Liu et al., 2023) |
| 8 | A memória revisada vale mais que a autogerada (a lição que o próprio agente escreve sobre o erro, sem gate)? | Vale: a autogerada reduz menos o erro e cria mais efeito colateral | Lições escritas pelo próprio modelo não deram ganho médio, e as curadas deram +16 pontos (SkillsBench, v1, 2026); arquivos de contexto escritos por desenvolvedor superaram os gerados por LLM (Gloaguen et al., 2026); memória com erro é copiada e amplificada pelo agente (Xiong et al., 2025). É a comparação implícito × explícito do Sub 1.7 |

Se a hipótese 3 se confirmar, a consequência para a arquitetura é: lições do tipo "fato do ambiente", com chave por
papel, são injetadas no contexto, por filtro de escopo; a ferramenta `recall_memory` fica reservada para memórias
maiores ou raras, a testar depois. Se for refutada, a premissa do recall explícito sai fortalecida. A hipótese 8 não
entra no veredito de nenhuma memória (§11): é o resultado comparativo do Sub 1.7.

## 5. Agentes

### 5.1 Duas trilhas, um protocolo

Hoje não há agente rodando localmente: os reais existem, mas não estão no repositório. Por isso:

- **Trilha 1 — agentes-espelho (começa já).** Agentes mínimos do smolagents (`CodeAgent`). Cada um copia de um papel real
  as condições em que o erro da unidade acontece, e nada do conteúdo jurídico.
- **Trilha 2 — agentes reais (quando houver permissão).** Os mesmos braços, medidas e análise, com o prompt e as
  ferramentas reais. É a que dá validade externa. O pedido de permissão vai em paralelo (§5.4).

A trilha 1 não é desperdício se a 2 chegar: é nela que o executor, o registro e a análise ficam prontos e auditados, e
eles servem a toda unidade seguinte.

### 5.2 Como se escolhe e se constrói um agente-espelho

**Escolha.** Os papéis onde o erro da unidade se concentra, pela tabela por papel da triagem da base 3
(`triagem_por_papel.csv`). Poucos papéis costumam concentrar quase todos os erros de uma unidade ("aparece em N papéis"
não quer dizer que a lição vale para N papéis: relatório da base 3, §3). A tabela dos espelhos fica no adendo.

**Ficha de fidelidade.** Antes do piloto, cada espelho ganha uma ficha com o que foi copiado do papel real, só nomes e
contagens: o formato do prompt (bloco `<code>` ou JSON), as listas de ambiente (imports do prompt e do interpretador),
as assinaturas das ferramentas, a forma do retorno (dict, lista, texto JSON), o limite de passos, o modelo. As fontes já
existem: `extrair_prompts_base2.py`, `extrair_ambiente_base2.py` e as tabelas da mineração da unidade. O que não se
conseguir copiar fica escrito na ficha como limite.

**O risco principal da trilha 1** é o espelho não errar: se o agente mínimo, sem memória, quase nunca cometer o erro,
não há o que reduzir. O piloto mede isso e tem um critério de passagem (§10, etapa 3). Quando o erro depende do contrato
de uma ferramenta, o risco sobe (§2.3, item 2).

### 5.3 Modelo

A plataforma trocou de modelo no meio do período, e a taxa de erro mudou com a troca (relatório da base 2, §2). Por
isso o modelo entra como fator, e cada adendo traz a tabela do modelo antigo e do atual **dos papéis da unidade** (as
bases 1 e 2 gravam o modelo de cada passo).

- **O piloto roda nos dois modelos** (só o braço sem memória). O principal do confirmatório é o **atual**, se o erro
  ainda acontecer nele: é nele que o mecanismo vai operar. O outro roda só nos braços "sem memória" e "memória
  injetada", como checagem.
- **Se o modelo atual não comete mais o erro**, isso é um achado: a memória descreve um erro do modelo antigo e não
  precisa ser injetada no atual. Ela fica monitorada, e a troca de modelo vira gatilho de revalidação.
- **O que falta saber, e a etapa 1 busca:** em que modelo os erros da unidade aconteceram. A base 3 não diz; a base 2
  diz para agosto.
- O veredito do degrau 4 vale para o modelo em que foi medido (§11).
- A resposta do modelo varia entre execuções mesmo com temperatura zero (Atil et al., 2024). Por isso cada tarefa roda
  várias vezes, com a versão do modelo fixada e a temperatura da plataforma (se conhecida; senão, a padrão, registrada).

### 5.4 O que pedir na permissão dos agentes reais

Para os papéis da unidade (os do adendo):

1. o prompt de sistema de cada papel e versão;
2. as definições das ferramentas (assinatura e descrição) e a forma do retorno de cada uma;
3. o modelo e os parâmetros (temperatura, limite de passos, intervalo de planejamento);
4. a lista de imports autorizados e como o interpretador é configurado;
5. a versão do smolagents;
6. onde pode rodar: aqui, com ferramentas simuladas e tarefas sintéticas, ou só no ambiente da empresa;
7. se houver, um ambiente de homologação das ferramentas.

Um pedido de permissão serve a várias unidades: quanto mais papéis o primeiro pedido cobrir, menos pedidos depois.

## 6. Braços: tratamentos e controles

Todos os braços usam o mesmo agente, as mesmas tarefas, o mesmo modelo. Só muda como a memória chega.

| Braço | O que faz | Como (smolagents) | Para que serve |
|---|---|---|---|
| **sem memória** | o agente como é | — | controle; mede a taxa de erro de base |
| **memória injetada no contexto** (nativa, na região `<memory>`) | o texto aprovado da memória entra **dentro do contexto do agente**, numa região rotulada `<memory>…</memory>` no fim do prompt de sistema. Quem a compõe é o harness, a cada execução, por uma heurística que escolhe as memórias do catálogo (abaixo); o agente a lê sem fazer nada | parâmetro `instructions` do agente | o tratamento principal; o polo "memória nativa no contexto" da pergunta do recall |
| **memória por ferramenta** | a região `<memory>` não existe. O agente tem a ferramenta `recall_memory`, que devolve o mesmo texto; ele decide se chama | ferramenta local com descrição de quando usar | testa o recall explícito da arquitetura |
| **memória no erro** (consulta por *middleware*) | a memória **não está no contexto no começo**. Depois de cada passo, um middleware do harness roda o classificador do pipeline no resultado do passo; se o erro for o da unidade, ele **consulta o catálogo** (pela unidade e pelo papel) e anexa o texto da memória à observação que o agente lê no passo seguinte. A consulta é decidida pelo harness, não pelo agente | `step_callbacks`, que recebe o passo e o agente e pode alterar a observação | custo zero em execução limpa (nada entra no contexto sem erro); mede o valor de reagir ao erro em vez de antecipar |
| **placebo** | a mesma região `<memory>` e o mesmo invólucro, com texto do mesmo tamanho, verdadeiro e sem relação com as tarefas | `instructions` | separa o efeito do conteúdo do efeito de "mais texto" |
| **memória autogerada** | a mesma região `<memory>`, com a lição que o próprio agente escreveu depois de errar, no piloto, sem leitura de casos nem gate | `instructions` | o polo implícito do Sub 1.7 (hipótese 8) |

**Três momentos de entrega, e quem decide cada um.** Os braços com memória diferem em *quando* a memória chega ao
agente e em *quem decide*:

| Momento | Braço | Quem decide | Pergunta que responde |
|---|---|---|---|
| **antes** (antecipação) | injetada no contexto | o harness, ao montar o agente | basta o agente ter a memória à mão? |
| **durante, se o agente quiser** | por ferramenta (`recall_memory`) | o agente | o agente sabe quando consultar? |
| **depois do erro** | no erro (middleware) | o harness, ao ver o erro | basta reagir quando o erro aparece? |

O terceiro braço não testa recuperação nem antecipação: o erro **acontece** uma vez, e a memória entra na consulta que o
middleware faz a partir da assinatura do erro. O que ele não faz é evitar o primeiro erro (hipótese 5). O que ele pode
reduzir é o que vem depois: a cascata e os passos perdidos (§8.4). Num par de memórias como o do pandas com os imports,
a assinatura do primeiro erro dispara a consulta das duas, e o segundo erro some (hipótese S2 do adendo do sandbox).

**O terceiro braço tem a medida e o poder dele no [adendo B](plano-experimento-adendo-memoria-no-erro.md).** A medida é a
reincidência (dado o primeiro erro, houve um segundo?), e não "teve o erro?". Neste plano ele segue exploratório, fora
da família corrigida por Holm.

**A região `<memory>` é igual em todos os braços que a têm** (injetada, placebo, autogerada): o mesmo rótulo, a mesma
frase de abertura e o mesmo formato de itens. O que muda é só o conteúdo. Assim, qualquer diferença entre eles é de
conteúdo, não de formato. No braço da ferramenta o prompt não tem a região, mas tem uma linha dizendo que a ferramenta
existe e quando usá-la; os tokens dessa linha entram no custo `c` desse braço (§8.2). Forma da região:

```
<memory>
Lições aprovadas para o seu papel (aplique-as quando o caso pedir):
- <texto literal da memória 1>
- <texto literal da memória 2>
</memory>
```

**O conteúdo da região é decidido em tempo de execução, não escrito à mão.** Os braços de entrega são só dois: memória
**nativa** (na região `<memory>`) e memória **por ferramenta**. Dentro da nativa, o que vai na região não é um texto
fixo no código: uma **heurística** escolhe, a cada execução, quais memórias entram. A heurística dos braços
confirmatórios é determinística e simples: o papel do agente, mais as regras do catálogo (`nao_vale_em`,
`vale_junto_com`, só memórias do degrau 3), lendo o texto na versão do dia. Não há busca semântica nem LLM nessa escolha
(§3, item 4). Outras heurísticas (por exemplo, uma que olhe o conteúdo da tarefa) são variantes exploratórias do §6.1.
O que continua fixo nos braços confirmatórios é a posição (o fim do prompt de sistema) e o momento (uma vez, ao montar o
agente).

**Como nasce a memória autogerada.** No piloto (etapa 3), depois de cada execução em que o erro da unidade aconteceu, o
mesmo modelo recebe o passo que falhou e a pergunta "escreva, em uma ou duas frases, a lição para não repetir este
erro". Nada é filtrado, corrigido ou lido por um humano, como no Reflexion (Shinn et al., 2023). Por papel, entram as
três lições mais recentes. É o desenho do aprendizado implícito: o agente escreve a própria memória. O tamanho dela
difere do da revisada; o registro guarda os tokens de cada uma, e a comparação de custo usa essa diferença.

Decisões de desenho e a razão de cada uma:

- **Injetar no contexto não é editar o prompt do repositório.** A arquitetura proíbe escrever no prompt de sistema dos
  repositórios dos agentes. A região `<memory>` é composta pelo harness na hora de montar a execução, a partir do
  catálogo, filtrada por papel, como a revelação progressiva pede: só a memória do papel entra. O arquivo do prompt
  do agente não muda. Como o harness registra o que injetou (quais memórias, qual versão do texto), a entrega
  automática não é silenciosa, que era a objeção da arquitetura à injeção (§F, "loop-native").
- **A memória fica no fim do prompt de sistema, em itens.** A posição pesa (Liu et al., 2023), e conteúdo no fim do
  prompt de sistema preserva o cache do prefixo (Lumer et al., 2026). Itens separados evitam o colapso que reescritas
  em bloco causam (ACE, 2025).
- **A região diz ao agente que aquilo é a memória dele.** O rótulo `<memory>` e a frase de abertura não são enfeite: a
  ideia é que o agente entenda o conteúdo como a sua própria memória, e não como mais um trecho do prompt. O Rafael
  lembra de um artigo que mostra que ter uma região assim no contexto é mais efetivo; **o artigo ainda precisa ser
  localizado, e até lá isso é uma hipótese do plano, não uma citação**. O braço exploratório "sem rótulo" (§6.1) testa
  a ideia dentro do experimento.
- **Sem busca semântica.** A heurística é um filtro por papel e pelas regras do catálogo. Ver §3, item 4.
- **O conteúdo é congelado.** Nenhum braço aprende durante o teste. Aqui se mede o valor de uma memória aprovada; a
  dinâmica de aprender entre execuções é outro experimento. Memória que cresce sem controle propaga erro (Xiong et al.,
  2025), e por isso o projeto tem o gate.
- **MCP não é um braço.** No `CodeAgent`, uma ferramenta MCP e uma local chegam ao modelo como a mesma função Python; o
  que muda é o transporte. MCP entra só como checagem (§6.1).
- **O injetor respeita o catálogo.** Memória com `nao_vale_em` não entra no papel excluído; memória com
  `vale_junto_com` só entra com a outra; nenhuma memória abaixo do degrau 3 entra nos braços confirmatórios.

### 6.1 Braços exploratórios

Rodam depois, com amostra menor, e não entram na decisão do degrau 4. Cada adendo diz quais se aplicam à unidade.

| Braço | Pergunta |
|---|---|
| **conserto no ambiente** (o que o sinal de harness da unidade pediria: o ambiente configurado de outro jeito, uma ferramenta nova) | hipótese 6: o teto prático, e memória × harness |
| **carga de memória** (todas as memórias do catálogo do papel no prompt, e não só as da unidade) | hipótese 7 |
| **ferramenta via MCP** (a mesma `recall_memory` num servidor MCP local, por `MCPClient`) | o transporte muda o comportamento ou só a latência? Muitas ferramentas no contexto degradam a escolha (Gan e Sun, 2025) |
| **sem rótulo** (o mesmo texto da memória solto no fim do prompt, sem a região `<memory>` nem a frase de abertura) | a região que o agente reconhece como a memória dele pesa mais que o texto solto? É a hipótese do §6; ela precisa do artigo para virar citação. É barato: o mesmo conteúdo, só muda o invólucro |
| **heurística de seleção** (a região escolhida por outra regra: o papel mais o conteúdo da tarefa, como as ferramentas ou os termos citados nela; ou todas as do papel) | uma seleção mais fina reduz o ruído ou introduz erro de recuperação? Em memória, a maior parte das falhas está na recuperação, não no uso (Yuan et al., 2026) |
| **posição e momento da região `<memory>`** (início do prompt de sistema; na mensagem da tarefa; renovada a cada passo por `step_callbacks`, com o catálogo relido) | a posição e a renovação mudam o efeito? A instrução do prompt perde peso com a distância (Liu et al., 2023; Li et al., 2024); renovar a cada passo custa tokens a cada passo |
| **ferramenta com consulta obrigatória** (o prompt manda consultar antes do primeiro código) | quanto da diferença para a injetada é a decisão de chamar |
| **memória de reforço** (as memórias que só repetem o prompt e não são injetadas) | o experimento de memória de reforço do blueprint |

## 7. Tarefas e replay

### 7.1 Três níveis de replay

| Nível | O que é | Para que serve | Onde |
|---|---|---|---|
| **Replay de passo** | Congela-se o contexto exato de um passo que errou e gera-se de novo só esse passo, com e sem a memória; o código gerado roda no interpretador | Triagem barata: uma chamada de LLM por caso. É "os casos que falharam, de novo, com a memória" do doc `17`, e o método de intervenção de Ma et al. (2025) | Trilha 1: contextos colhidos no piloto. Trilha 2: contextos reais, no ambiente da base |
| **Execução com ferramentas simuladas** | O agente roda a tarefa do início ao fim; as ferramentas devolvem respostas fixas, gravadas em arquivo | O teste confirmatório. Respostas fixas tiram a instabilidade de ferramenta real da comparação (Guo et al., 2024) | Local |
| **Execução real** | Os agentes reais, em homologação | Validade externa; depois, o teste A/B do piloto (Sub 3.7) | Depende da permissão |

**Um cuidado no replay de passo.** Os casos foram escolhidos porque erraram. Rodados de novo sem memória, parte deles
acerta sozinha, por variação do modelo. Comparar "antes: 100% de erro" com "depois, com memória" exagera o efeito: é
regressão à média (Barnett et al., 2005). Por isso o controle também é rodado de novo, e a comparação é entre os dois
replays.

### 7.2 As tarefas sintéticas

**O que é um gerador.** É um programa pequeno e determinístico (não um LLM) que fabrica tarefas. Escreve-se **uma vez** o
modelo da tarefa, deixando alguns pontos como parâmetros; cada combinação de parâmetros dá uma tarefa diferente, e o
verificador calcula a resposta certa a partir dos mesmos parâmetros. Exemplo, para um espelho que lê um registro
devolvido como texto: o modelo é "a ferramenta devolve um registro; leia o campo indicado e decida o destino", e os
parâmetros são os nomes dos campos, o número de registros, a profundidade do aninhamento, os valores e a redação da
instrução. Neste plano, **"gerador" e "modelo de tarefa" querem dizer a mesma coisa**, e o texto usa "gerador". Tarefas do
mesmo gerador se parecem entre si, e isso pesa no cálculo de `K` e `N` (§9.3).

Para cada agente-espelho, duas populações:

- **Tarefas-gatilho:** a lição é necessária. É onde se mede a eficácia. Como fazer o erro acontecer é específico da
  unidade (adendo, §16.6).
- **Tarefas neutras:** a lição não é necessária. É onde se mede o custo puro da memória e o dano.

Regras, para toda unidade:

1. Cada tarefa sai de um **gerador com parâmetros** (nomes de campos, tamanho do retorno, número de registros,
   redação), para haver muitas tarefas distintas; o que dá poder estatístico é o número de tarefas, não o de repetições
   (§9).
2. A tarefa **nunca menciona** o objeto da lição (o módulo, a função, a chave, o formato que a memória ensina). Se
   mencionar, o teste mede a tarefa, não a memória.
3. Cada tarefa tem um **verificador determinístico** do resultado (o formato Task.md do blueprint, §3): resposta certa,
   alternativas aceitas, atalho proibido.
4. Nenhum texto de caso real. As formas (chaves, aninhamento, tipos) vêm dos campos `evidence` das memórias, que só têm
   estrutura.
5. O conjunto de tarefas é congelado com hash antes do confirmatório. As tarefas do piloto não entram no confirmatório.

## 8. Medidas

Todas saem do registro da execução por script, sem LLM. O mapa com as métricas do Plano (Sub 3.6):

| Métrica do Plano | O que ela vira aqui | Seção |
|---|---|---|
| **Taxa de sucesso** | duas leituras: a taxa do erro da unidade (principal) e o sucesso da tarefa (guarda) | §8.1, §8.5 |
| **Estabilidade** | entre repetições da mesma tarefa: `pass^k` e a variância da medida principal por tarefa. A estabilidade **depois de ciclos sucessivos de atualização** (Sub 4.4) não cabe aqui: a memória não muda durante o teste | §8.4 |
| **Latência** | tempo da execução, decomposto em modelo, ferramenta e interpretador, com a compensação em segundos | §8.3 |
| **Custo** (pedido pela arquitetura, §D) | tokens totais por execução, com a compensação em tokens | §8.2 |

### 8.1 Principal — o erro da unidade

**A execução teve pelo menos um passo com erro classificado na unidade da memória?** (sim/não). O registro é gravado no
formato do trace real (`{papel: [passos]}`, o `agent.memory` do smolagents), e o classificador é o do pipeline. A
contagem das regras nos dados sintéticos é conferida por uma segunda implementação (§12). Quando a memória cobre só uma
parte da unidade (uma memória por papel ou por nome), o erro-alvo é o daquela parte, e o adendo diz qual.

### 8.2 Compensação — tokens líquidos

**Tokens totais da execução** (entrada + saída, somados nos passos). Como a memória injetada é contada na entrada de
cada passo, a diferença com × sem memória já é a economia menos o custo.

Para levar o resultado ao mundo real, combina-se o efeito nas duas populações pela incidência real do erro no papel:

- `c` = tokens a mais numa execução neutra (o custo puro);
- `s` = tokens a menos numa execução-gatilho (a economia);
- `π` = fração das execuções do papel em que o erro acontece (da base 3, por papel e mês);
- efeito esperado por execução = `(1 − π)·c − π·s`. **A memória compensa se for negativo**, isto é, se `π > c ÷ (c + s)`.

O experimento entrega `c` e `s`; a base 3 entrega `π`. O relatório dá, por memória e papel, a **incidência de
equilíbrio** `c ÷ (c + s)`. É a mesma ideia do "ponto de equilíbrio" do glossário (§8), medida em vez de suposta.

*Conta de ordem de grandeza (hipótese, para saber o que esperar; os valores reais são do adendo):* memória de 20
tokens × 7 passos ≈ 140 tokens por execução; um passo evitado ≈ 13.135 tokens. Com eficácia de 50%, a incidência de
equilíbrio fica perto de 2% das execuções do papel. Para a ferramenta, a consulta custa um passo inteiro, o mesmo que o
erro: a conta não fecha a menos que uma consulta evite mais de um erro.

### 8.3 Latência

**Por que não basta cronometrar a execução.** Num agente, o tempo de uma execução soma três coisas que a memória afeta
de jeitos diferentes, e uma delas o experimento não reproduz:

| Parte | Como se mede | O que a memória faz com ela |
|---|---|---|
| **tempo do modelo** | um invólucro no objeto do modelo marca o início e o fim de cada chamada | a injeção acrescenta tokens de entrada (alguns milissegundos de leitura); o erro evitado tira uma chamada inteira |
| **tempo das ferramentas** | as ferramentas simuladas respondem na hora e registram cada chamada | no experimento é quase zero por construção; na plataforma não é, e por isso o tempo real entra na conta abaixo |
| **tempo do interpretador** | o resto do passo: o `timing` do ActionStep menos o modelo e as ferramentas | separa código lento de modelo lento |

Também se registra o tempo da execução inteira (do primeiro ao último passo) e o número de chamadas ao modelo.

**A compensação em segundos**, na mesma forma da de tokens (§8.2):

- `c_t` = segundos a mais numa execução neutra, medidos no experimento (só tempo de modelo: é o único que a injeção
  muda);
- `s_t` = (passos a menos por execução-gatilho, medidos no experimento) × (duração mediana real de um passo com erro do
  papel). **A duração vem da base 3**: a v2 tem a duração de cada passo com erro (roadmap da base 3, tabela dos passos com erro, #38); a base 1, com
  o `timing` de todos os passos, serve para conferir. Assim o tempo das ferramentas reais entra na conta, e não o zero do
  simulador;
- a incidência de equilíbrio em tempo é `c_t ÷ (c_t + s_t)`, comparada com o mesmo `π`.

**Como ler.** A latência é a medida mais ruidosa: depende da carga do provedor e da hora. Três cuidados: (1) os braços
de uma mesma tarefa rodam em sequência, em ordem sorteada, para que a deriva do provedor caia igual em todos; (2) a
análise é pareada por tarefa, em escala logarítmica; (3) reportam-se a mediana (p50) e a cauda (p95), porque é a cauda
que estoura um tempo-limite. A previsão é que, nas tarefas neutras, a diferença fique abaixo do ruído — por isso a
latência entra como guarda, com margem (§11). O cache do provedor também muda o tempo: memória no fim do prompt de
sistema preserva o prefixo reaproveitável (Lumer et al., 2026), e os tokens em cache são registrados quando o provedor
informa.

**Limite declarado.** A velocidade do provedor usado aqui não é a da plataforma. O que transfere é a forma (quantas
chamadas a menos, quantos tokens a mais), não os segundos absolutos. A ressalva do próprio projeto vale aqui: um passo
lento pode ser infraestrutura ou modelo, não falta de memória (política de promoção, 02/09).

### 8.4 Secundárias

| Medida | Definição | Por quê |
|---|---|---|
| passos por execução | número de ActionSteps | eficiência independente do tamanho do prompt; entra no `s_t` |
| tamanho da cascata | passos seguidos com erro, depois do primeiro | o que a "memória no erro" pode reduzir |
| tokens em passos com erro | a medida do teto de economia da base 3 | liga o resultado à linha de base |
| adesão à lição | o código fez o que a memória diz (por AST, com a regra de cada unidade no adendo) | separa "a memória foi seguida" de "o erro não apareceu por acaso" |
| uso da ferramenta | chamou? em que passo? antes do ponto de gatilho? chamou sem precisar? | a mecânica da hipótese 3 |
| estabilidade (`pass^k`) | fração das tarefas em que todas as `k` repetições passam (Yao et al., 2024) | média alta com muita variação não serve em produção; é a "estabilidade" do Plano |
| custo por acerto | tokens por execução ÷ taxa de sucesso (Erol et al., 2025) | junta custo e resultado num número |
| tokens em cache | se o provedor informar | o trace de produção não registra; aqui dá para medir |

### 8.5 Guardas — o que não pode piorar

1. **Sucesso da tarefa** (verificador determinístico).
2. **Erros de outras unidades** ("sem criar outro"): taxa de qualquer erro fora da unidade da memória. Cada adendo
   nomeia as unidades vizinhas que mais merecem olhar (as que uma instrução nova poderia induzir).
3. **Falha silenciosa:** resposta final entregue com uma ferramenta que falhou não conta como sucesso.
4. **Latência nas tarefas neutras:** a mediana não sobe além da margem do pré-registro (§11).

Custo, tempo e acerto são lidos juntos, nunca só o acerto (Kapoor et al., 2024).

## 9. Quantos casos

### 9.1 A conta

Tamanho por braço para detectar a redução do erro, teste bilateral, 5% de significância, 80% de poder, execuções
independentes (calculado em 12/11; o script entra na etapa 0). Vale para qualquer unidade: o que muda é a taxa de erro
sem memória, que vem do piloto da unidade.

| Taxa de erro sem memória | redução de 30% | de 50% | de 70% |
|---:|---:|---:|---:|
| 80% | 59 | 23 | 12 |
| 60% | 120 | 42 | 20 |
| 40% | 244 | 82 | 38 |
| 20% | 615 | 199 | 90 |
| 10% | 1.356 | 435 | 194 |
| 5% | 2.838 | 906 | 402 |

Três correções sobre essa tabela:

1. **Comparações múltiplas.** Quatro comparações confirmatórias (§12), corrigidas por Holm (1979). Com a taxa de base em
   40% e redução de 50%, sobe de 82 para cerca de 116 por braço.
2. **Repetições da mesma tarefa não são independentes.** Miller (2024, §3.1) decompõe a variância da média em
   `(Var(x) + E[σ²]/K) / n`: repetir a tarefa `K` vezes só encolhe o segundo termo (a variação dentro da tarefa); o
   primeiro (a variação entre tarefas) só encolhe com mais tarefas. Escrito como efeito de desenho, com `ρ =
   Var(x) / (Var(x) + E[σ²])`, o tamanho efetivo é dividido por `1 + (k − 1)·ρ`. **Essa forma é uma derivação a partir da
   decomposição dele, não uma fórmula do paper.** Com `k = 4` e `ρ = 0,3` (perto do `ρ = 1/3` do exemplo dele, de
   escore binário e dificuldade uniforme), divide por 1,9. Por isso vale mais ter tarefas diferentes do que repetir as
   mesmas. O número de repetições se escolhe pelo critério do paper, `E[σ²]/K ≪ Var(x)`, estimado no piloto; o "3 a 5" do
   plano é uma estimativa de partida, não um número do paper. O paper também avisa que calcular o erro-padrão sobre as
   `K·N` execuções empilhadas é inconsistente: o cálculo é sobre a média por tarefa (§12).
3. **A taxa de erro real costuma ser baixa demais para testar direto.** Na base 1, 37% das execuções têm algum erro,
   mas uma unidade sozinha aparece em poucos por cento. Com 5% de base seriam mais de 900 execuções por braço. Por isso
   a eficácia é medida nas tarefas-gatilho, onde o erro é provável, e o custo nas neutras; a incidência real entra
   depois, na conta do §8.2.

Para a guarda do sucesso (não-inferioridade, margem de 5 pontos, sucesso de 90%): 446 execuções por braço, antes da
correção por agrupamento. Só fecha juntando os agentes-espelho da unidade, e é assim que ela é testada.

### 9.2 Os números, por agente-espelho

**Piloto (calibração), só o braço sem memória:** por agente-espelho, 20 tarefas-gatilho × 5 repetições e 10 neutras × 3
→ **130 execuções por modelo** (260 nos dois). Entrega a taxa de base em cada modelo, o `ρ`, os tokens por execução e os
contextos para o replay de passo. As execuções do piloto em que o erro aconteceu dão também as lições do braço
autogerado (uma chamada de LLM por execução com erro, sem execução nova).

**Replay de passo:** por memória, 30 contextos que erraram × 5 gerações × 2 (com e sem) → **300 chamadas de um passo**.

**Confirmatório**, por agente-espelho e por braço (6 braços), no modelo principal. **Os valores abaixo são de partida:**
o número de tarefas (N) e de repetições (K) é decidido pelo §9.3, com contas antes do piloto e medidas depois dele.

| Versão | Tarefas-gatilho × repetições | Neutras × repetições | Por agente-espelho (6 braços) | Quando usar |
|---|---|---|---:|---|
| **cheia** | 60 × 4 = 240 | 30 × 4 = 120 | **2.160** | taxa de base do piloto entre 40% e 60% |
| **enxuta** | 40 × 3 = 120 | 20 × 3 = 60 | **1.080** | taxa de base ≥ 60%, ou redução esperada ≥ 70% no replay de passo |

**Total da unidade** = (número de agentes-espelho) × (valor da tabela). O adendo dá a conta da unidade. A checagem no
outro modelo (só "sem memória" e "memória injetada") acrescenta 2 ÷ 6 do total.

Conferência da versão cheia: 240 execuções-gatilho com `ρ = 0,3` valem cerca de 126 independentes, acima das 116
necessárias (taxa de base de 40%, redução de 50%, Holm). Na guarda, com três espelhos: 3 × 360 = 1.080 por braço, cerca
de 570 efetivas, acima das 446. Com um ou dois espelhos, a guarda não fecha com esse tamanho, e o adendo diz o que fazer
(mais tarefas neutras ou uma margem maior).

**A regra:** o tamanho final (N e K) é recalculado com a taxa de base e o `ρ` do piloto, pelo §9.3, e fixado no
pré-registro **antes** do confirmatório. Não se acrescentam execuções depois de olhar o resultado.

**Custo (hipótese, a medir no piloto):** se uma execução do espelho gastar 15–25 mil tokens, cada agente-espelho na
versão cheia fica na ordem de 32 a 54 milhões de tokens e na enxuta, na metade. O valor em dinheiro depende do modelo;
fecha-se na etapa 3, com o número do piloto.

### 9.3 Como K (repetições) e N (tarefas) são decididos

> **Status: em discussão (12/11/2026).** Esta seção se apoia no Miller (2024), cujo fichamento é 🔎 e ainda **falta o ✅**
> do Rafael ([`literature/miller-2411.00640.md`](literature/miller-2411.00640.md)). Depois da leitura dele, a seção é
> fechada ou ajustada, e a discussão continua: o que ainda está aberto está no §15 (decisões 7 a 9). Os valores de
> partida do §9.2 valem até lá.

**O que o Miller (2024, §3.1) dá.** A variância da taxa medida é `(Var(x) + E[σ²]/K) / N`: a variação **entre tarefas**
`Var(x)` só diminui com mais tarefas; a variação **dentro** da tarefa `E[σ²]` diminui com as repetições `K`. A razão
`ρ = Var(x) / (Var(x) + E[σ²])` diz qual das duas domina: `ρ` alto, repetir ajuda pouco; `ρ` baixo, repetir ajuda mais. O
`ρ` só se conhece depois de medir, mas dá para calcular antes com valores supostos e ver o que é robusto. As duas
fórmulas abaixo decorrem da decomposição dele, e a segunda é um resultado clássico de amostragem em dois estágios;
**nenhuma está escrita no paper** (derivação minha). Os números das tabelas são de uma conta e de uma simulação feitas em
12/11/2026, e a simulação reproduziu a fórmula do Miller até a terceira casa.

**Passo 1 — antes do piloto: calcular com suposições.**

*(a) Quantas tarefas, dado K.* Se o §9.1 pede `n` execuções independentes por braço, com `K` repetições por tarefa e
correlação `ρ`, o número de tarefas é `N = n · (1 + (K − 1)·ρ) / K`. Exemplo, com `n = 116` (taxa de base de 40%,
redução de 50%, Holm) e `ρ = 0,3`:

| Repetições K | Tarefas N necessárias | Execuções por braço (N × K) |
|---:|---:|---:|
| 1 | 116 | 116 |
| 2 | 76 | 152 |
| 3 | 62 | 186 |
| 4 | 56 | 224 |
| 5 | 52 | 260 |
| 8 | 45 | 360 |
| infinitas | 35 (o piso: `ρ·n`) | — |

Mais repetições poupam tarefas, mas com retorno decrescente, e **nunca menos que `ρ·n` tarefas**. O ponto de partida do §9.2
(60 tarefas × 4) é o caso `K = 4`, que pede 56.

*(b) Qual K, dado o custo.* Com `c` = (custo marginal de criar e validar **mais uma tarefa** de um gerador já pronto) ÷
(custo de **uma execução**), na mesma unidade (dinheiro ou tempo), o `K` que dá a menor variância para um orçamento fixo é
`K* = √( c · (1 − ρ) / ρ )`:

| ρ \ c | 1 | 5 | 10 | 30 | 100 |
|---:|---:|---:|---:|---:|---:|
| 0,1 | 3,0 | 6,7 | 9,5 | 16,4 | 30,0 |
| 0,3 | 1,5 | 3,4 | 4,8 | 8,4 | 15,3 |
| 0,5 | 1,0 | 2,2 | 3,2 | 5,5 | 10,0 |
| 0,8 | 0,5 | 1,1 | 1,6 | 2,7 | 5,0 |

**Como ler.** A perda por errar o `K` é plana perto do ótimo: `K = 4` fica **a menos de 10% do ótimo** para `ρ` entre 0,3 e
0,5 e `c` entre 5 e 30. Só custa caro nos extremos (até 1,5 a 2 vezes a variância: `ρ` alto com tarefa barata, ou `ρ`
baixo com tarefa cara). Isso é o que torna o `K` uma decisão robusta, mesmo antes de medir o `ρ`. Um caso a ter em mente:
com gerador paramétrico, o `c` marginal pode ser quase zero, e o `K` ótimo cai para 1 ou 2; nesse caso, `K` acima de 2 só
se justifica pela **estabilidade** (a medida `pass^k` exige `k` repetições) e pela estimativa do próprio `ρ`.

**Passo 2 — no piloto: medir ρ.** O piloto (só o braço sem memória) tem 20 tarefas-gatilho × 5 repetições por espelho. O
`ρ` se estima por análise de variância de um fator (entre e dentro das tarefas). A variância das médias por tarefa
superestima `Var(x)` em `σ²/K`, e a estimativa subtrai esse termo (o apêndice C do paper usa `K` bem maior que 1 e divide
por `K − 1` para a variância de dentro). Precisão do `ρ` estimado, por simulação (escore binário, taxa de 40%):

| Piloto | ρ estimado, para ρ verdadeiro de 0,15 · 0,33 · 0,60 |
|---|---|
| 20 tarefas × 5 | 0,15 ± 0,10 · 0,33 ± 0,12 · 0,60 ± 0,12 |
| 40 tarefas × 5 | ± 0,07 · ± 0,08 · ± 0,08 |
| 60 tarefas × 4 | ± 0,07 · ± 0,07 · ± 0,07 |

Com 20 × 5, o piloto separa `ρ` baixo de `ρ` alto, mas não distingue 0,3 de 0,4. **Isso basta**, porque a perda por errar
o `K` é plana (tabela do passo 1). Se quiser a precisão de ±0,08, o piloto passa a 40 tarefas-gatilho × 5 repetições:
100 execuções a mais por espelho e por modelo. É decisão do §15.

**Passo 3 — com os dados do piloto: testar a hipótese e fixar K e N.** Três verificações, todas determinísticas e
reproduzíveis:

1. **O `ρ` com intervalo** (reamostragem das tarefas do piloto). `ρ` alto: poucas repetições. `ρ` baixo: mais
   repetições compensam.
2. **A curva do erro-padrão × K nos dados do piloto.** Com as 5 repetições de cada tarefa, sorteiam-se 1, 2, 3, 4 e 5
   repetições, reamostram-se as tarefas e mede-se o erro-padrão da taxa. Compara-se com a fórmula do Miller. Se a curva
   achata em `K = 2` ou `3`, repetir mais é desperdício **nesta unidade**. É o teste direto de que a decomposição vale
   nos nossos dados.
3. **O poder por simulação, para o N.** Reamostram-se as tarefas do piloto (com as suas probabilidades de erro),
   aplica-se a redução hipotética, simula-se o confirmatório inteiro (N tarefas, K repetições, 6 braços, Holm) muitas
   vezes e conta-se quantas vezes ele detecta o efeito. O `N` é o menor que chega a 80%. Confere-se com a fórmula pareada do
   Miller (Eq. 9, §5), que usa `ω²` e `σ²` estimados do piloto. Para escore binário e poucas centenas de casos, a
   simulação é mais confiável que a fórmula gaussiana (Bowyer et al., 2025).

**Passo 4 — congelar.** `K` e `N` por espelho, a versão (cheia ou enxuta) e os números de poder entram no pré-registro
(etapa 4). Vale a regra do §9.2: nada se acrescenta depois de olhar o resultado.

**Um limite sobre as tarefas.** Tarefas do mesmo gerador se parecem entre si, e se comportam como o "grupo de perguntas
relacionadas" do §2.2 do paper. Para o que o plano afirma (a memória reduz o erro neste tipo de tarefa), o gerador *define*
a população e não há problema. Para generalizar além dele, vários geradores por espelho são melhores que um só, e o
erro-padrão agrupado por gerador se aplica (§12). **[inferência minha]**

**O que depende de duas decisões suas (§15):** o `c` (quanto custa criar uma tarefa a mais, que se mede na etapa 2) e se a
estabilidade `pass^k` é medida confirmatória ou só secundária, porque é ela que pode exigir `K ≥ 3`.

## 10. Etapas, do início ao fim

Cada etapa termina num artefato e num critério de passagem. As durações são estimativas em dias úteis, para uma unidade
com três agentes-espelho. **Para a segunda unidade em diante, a etapa 0 já está feita e a 2 reaproveita o executor, o
registro e os braços:** só mudam as fichas, as tarefas e os verificadores.

| Etapa | O que se faz | Sai com | Critério para seguir | Dias |
|---|---|---|---|---:|
| **0 · Preparação** (uma vez só) | Branch e a pasta do código das POCs (a mesma que o blueprint cria na E0; o nome é decisão do §15); dependências num grupo separado (`uv add --optional pocs smolagents`…); acesso ao modelo; um agente "olá" com o registro inspecionável e o invólucro que mede o tempo de cada chamada ao modelo; os scripts das contagens deste plano (modelo por papel, tamanho de amostra); o pedido de permissão da trilha 2 (§5.4) enviado | ambiente rodando; pedido enviado | uma execução gravada no formato do trace e lida pelo `leitor_trace` | 2 |
| **1 · Linha de base real** | **Base 3** (contagens + v2 de erros), por papel da unidade e mês: execuções do papel, execuções com o erro de cada memória, passos por execução, tokens e duração do passo com erro e do seguinte. **Base 2** (trace inteiro): o modelo de cada erro da unidade, e o prompt e o ambiente de cada papel para a ficha. Os scripts são escritos e testados aqui na base 1 e levados ao ambiente; de lá só saem contagens e nomes. Congelar num registro versionado (o registro da linha de base do teste de compensação, roadmap da base 3, #39) | `π` por papel e mês; o teto de economia por papel e memória; a duração mediana do passo com erro por papel; o modelo dos erros em agosto | números conferidos pela auditoria independente | 2 (+ ida ao ambiente) |
| **2 · Agentes-espelho e tarefas** | As fichas de fidelidade; os agentes; os geradores de tarefa com verificador; os seis braços; o executor com ordem sorteada; o registro | código + testes; as fichas | os seis casos de fronteira do verificador passam (válido, alternativa válida, errado realista, atalho, efeito colateral proibido, evidência corrompida); os seis braços rodam uma tarefa cada | 4 |
| **3 · Piloto** | Só o braço sem memória, nos dois modelos (130 execuções por modelo e por espelho). Medir taxa de base, `ρ`, tokens, tempo e a variância da latência (que fixa a margem do §11), e ler uma amostra das execuções inteiras; escolher o modelo principal (§5.3); gerar as lições do braço autogerado | relatório do piloto; contextos para o replay; as lições autogeradas, congeladas | **taxa de base ≥ 20% nas tarefas-gatilho** e o erro classificado é o da unidade. Se não: ajustar a fidelidade do espelho (uma rodada), e, se continuar baixo, a memória vai para o replay de passo com contexto real (trilha 2) | 2 |
| **4 · Pré-registro** | Congelar hipóteses, braços, tarefas (hash), textos das memórias (hash do catálogo), modelo, tamanho, medidas, script de análise e critérios | `pre_registro.json` + commit | aprovação do Rafael | 1 |
| **5 · Replay de passo** | 300 chamadas por memória; com × sem memória no mesmo contexto | efeito por memória no passo; adesão à lição | serve de triagem: memória sem efeito aqui é relida antes de gastar o confirmatório | 1 |
| **6 · Confirmatório** | As execuções do §9.2, ordem sorteada em blocos por tarefa, agente e interpretador novos a cada execução | registros crus + manifesto com hash | todas as execuções previstas existem; falhas de infraestrutura separadas e rodadas de novo | 2–3 |
| **7 · Análise e auditoria** | Antes de qualquer número, cada execução que falhou é classificada numa das 8 causas do Eval Engineering, e as que não são do agente (ambiente, infraestrutura, verificador, vazamento) são consertadas e rodadas de novo, fora da nota. Depois, o script congelado; a segunda implementação independente das medidas; o encontro medida a medida; uma execução inteira de cada braço lida pelo Rafael | tabelas, intervalos, o veredito por memória | as duas implementações batem | 3 |
| **8 · Exploratórios** | Os braços do §6.1 e o segundo modelo | notas por braço | — | 2–3 |
| **9 · Fechamento** | Relatório; o degrau 4 no catálogo (como gravar é decisão a tomar); atualizar a hipótese de arquitetura e as perguntas abertas; a seção do relatório comparativo (Sub 1.7) | documentos atualizados | gate do pesquisador | 2 |
| **Trilha 2** | Com a permissão: replay de passo com contexto real e o confirmatório nos agentes reais, mesmo pré-registro com adendo | o mesmo, com validade externa | — | a estimar |

Total da trilha 1: cerca de 20 dias úteis para a primeira unidade; menos para as seguintes. Não cabe no prazo interno
de 30/11; o piloto e o pré-registro cabem.

## 11. Critério de sucesso

Uma memória passa ao **degrau 4 (validada)**, num agente, numa forma de entrega e num modelo, se as quatro condições
valerem:

1. **Eficácia.** Nas tarefas-gatilho, a taxa do erro da unidade é menor que a do braço sem memória, com p < 0,05 depois
   da correção de Holm, e o intervalo de 95% da diferença não inclui zero.
2. **Compensação.** A incidência de equilíbrio `c ÷ (c + s)` fica abaixo da incidência real `π` do papel (etapa 1), com
   o limite superior do intervalo de `c ÷ (c + s)` ainda abaixo de `π`.
3. **Sem dano.** O sucesso da tarefa não é inferior ao do controle (margem de 5 pontos, os agentes-espelho da unidade
   juntos); a taxa de erros de outras unidades não sobe (intervalo da diferença inclui zero ou é negativo); e a latência
   mediana nas tarefas neutras não sobe além da margem do pré-registro (proposta: 10%, fixada com a variância medida no
   piloto).
4. **Especificidade.** A memória é melhor que o placebo na medida principal.

**Entre as formas de entrega** que passarem, escolhe-se a de menor custo esperado por execução na incidência real;
empatando, a de menor tempo esperado; empatando de novo, a mais simples. A compensação em segundos (§8.3) é reportada,
mas não é condição: os segundos do provedor do experimento não são os da plataforma.

**Os outros desfechos também são resultado, e cada um tem destino:**

| Desfecho | Leitura | Destino |
|---|---|---|
| Reduz o erro, mas não compensa | A lição está certa e é cara para o que evita | Monitorada; reavaliar com `π` maior ou texto menor |
| Não reduz o erro, e a adesão é alta | O agente segue a lição e erra do mesmo jeito: a causa é outra | Volta ao degrau 3 |
| Não reduz o erro, e a adesão é baixa | O agente ignora a memória nessa forma de entrega | Testar outra posição ou forma; registrar como limite |
| Reduz o erro e piora o sucesso ou cria outro erro | Dano | Não injetar; investigar o texto |
| O placebo reduz tanto quanto a memória | O efeito é de perturbar o prompt, não do conteúdo | Não validar |
| O espelho não erra (piloto) | A trilha 1 não mede essa memória | Trilha 2 |
| O erro acontece no modelo antigo e não no atual | A lição era do modelo antigo | Monitorada; a troca de modelo vira gatilho de revalidação |
| A autogerada reduz o erro tanto quanto a revisada | Para este tipo de lição, o agente escreve sozinho o que precisa | Resultado do Sub 1.7; o gate continua justificado pelo que ele barra (dano, harness), não pela eficácia |

O planejamento usou "redução de 50%" para dimensionar a amostra. Isso **não** é critério de sucesso: o critério é a
compensação, que depende do custo e da incidência reais.

## 12. Análise estatística

- **Unidade de análise:** a **tarefa**. As `K` repetições de cada tarefa viram uma média por tarefa, e a incerteza se
  calcula sobre as tarefas, nunca sobre as execuções empilhadas (Miller, 2024, §3.1). Diferenças **pareadas por
  tarefa**, porque todos os braços rodam as mesmas tarefas (§4.2 do paper). Se as tarefas nascem de um mesmo gerador, elas
  são perguntas agrupadas no sentido do §2.2 dele, e o erro-padrão agrupado por gerador ou por espelho se aplica a essa
  parte. Depois do piloto, o tamanho de amostra se refaz pela fórmula pareada do paper (Eq. 9), com a variância entre
  tarefas e a variância dentro da tarefa estimadas do piloto; a tabela do §9.1, de duas proporções independentes, é o
  teto conservador. Não se mexe na temperatura para reduzir variância (§3.3 do paper).
- **Medida principal:** regressão logística com efeito aleatório da tarefa e efeito fixo do braço, por agente. Como
  conferência, o teste de McNemar sobre o resultado majoritário de cada tarefa (Dietterich, 1998). Reporta-se a
  diferença de risco com intervalo de 95%.
- **Amostras pequenas** (replay de passo, exploratórios): intervalos bayesianos ou exatos, não a aproximação normal, que
  subestima a incerteza com poucas centenas de casos (Bowyer et al., 2025).
- **Estratificação por agente:** a taxa de erro também pelo teste de Cochran-Mantel-Haenszel com os agentes como
  estratos, e tokens e passos por testes de permutação estratificados por tarefa — o tratamento de Gloaguen et al. (2026)
  para um desenho parecido.
- **Tokens e passos:** média por tarefa e braço; diferença pareada com intervalo por reamostragem das tarefas. Reportar
  média e mediana (a distribuição tem cauda longa).
- **Latência:** modelo misto no logaritmo do tempo, com efeito aleatório da tarefa; a diferença das medianas pareada por
  tarefa, com intervalo por reamostragem; p50 e p95. A guarda (margem do §11) é um teste de não-inferioridade unilateral
  sobre a razão das medianas.
- **Incidência de equilíbrio:** intervalo por reamostragem conjunta de `c` e `s` (e de `c_t` e `s_t`).
- **Família confirmatória e Holm:** quatro comparações na medida principal, por memória — injetada × sem memória
  (hipótese 1), injetada × placebo (4), injetada × por ferramenta (3) e injetada × autogerada (8) —, corrigidas juntas por
  Holm. Os demais contrastes (memória no erro, exploratórios) sem correção e rotulados como tal.
- **Sem olhar e parar:** uma análise só, no fim.
- **Auditoria independente:** uma segunda implementação recalcula as medidas direto dos registros crus, sem usar o
  código da análise, e os números são confrontados um a um — a regra do projeto, "re-rodar não é verificar".
- **Evidência:** cada achado leva os identificadores das execuções, a tabela derivada com o filtro e o comando que
  reproduz.
- **Mais de uma unidade:** cada unidade tem o pré-registro e o veredito dela. Não se juntam unidades diferentes numa
  mesma análise: a mistura de papéis e de erros muda o custo sem mudar a eficiência.

## 13. Controles e ameaças à validade

| Ameaça | Controle |
|---|---|
| O efeito é de "mais texto", não da lição | braço placebo |
| Variação do modelo entre execuções | repetições; versão do modelo fixada; análise agrupada |
| O provedor muda ao longo do dia (afeta sobretudo a latência) | ordem sorteada em blocos por tarefa: os seis braços de uma tarefa rodam juntos; análise pareada por tarefa |
| A ferramenta simulada responde na hora e esconde o tempo real | a economia em segundos usa a duração real do passo com erro, da base 3 (§8.3) |
| A tarefa ou o verificador vazam a resposta ao agente | o agente vê só a instrução; a especificação da tarefa (Task.md) e o verificador nunca entram no contexto dele (Eval Engineering) |
| A lição autogerada é mais longa ou mais curta que a revisada | tokens de cada uma registrados; a comparação de custo usa a diferença; o placebo controla o tamanho só da revisada (limite) |
| Estado que vaza entre execuções | agente e interpretador novos a cada execução; memória só de leitura |
| A tarefa entrega a resposta (cita o objeto da lição) | regra 2 do §7.2, conferida por script |
| Ajustar a tarefa até dar certo | tarefas do piloto fora do confirmatório; conjunto congelado com hash |
| Regressão à média no replay de passo | o controle também é rodado de novo |
| O classificador erra nos dados sintéticos | segunda implementação; leitura de uma amostra de execuções |
| Sucesso falso | verificador por evidência independente, não pelo relato do agente |
| O espelho não representa o agente real | ficha de fidelidade com os limites escritos; a trilha 2 é a resposta; a conclusão da trilha 1 é sobre a memória no espelho |
| A plataforma trocou de modelo, e a base 3 não diz em qual cada erro aconteceu | o piloto roda no antigo e no atual; a base 2 dá o modelo dos erros de agosto; o veredito vale por modelo |
| O passo do espelho é mais barato que o real, e a economia sai subestimada | o `s` é conferido contra os tokens do passo com erro na v2 da base 3 (§2.1) |
| O protocolo foi desenhado olhando uma unidade só e não generaliza | o §2.3 lista as hipóteses de generalidade; a segunda unidade é o teste, e os desvios entram no adendo e no §2.3 |
| Graus de liberdade do analista | pré-registro; confirmatório separado de exploratório |
| Falha de infraestrutura contada como erro do agente | separadas antes de qualquer medida e rodadas de novo |

## 14. O que este experimento não testa

- O caminho de escrita: gatilho, curador, gate, destino memória × harness, promoção, esquecimento e rollback (EX-3 a
  EX-7 do blueprint).
- A curva de aprendizado entre execuções (o EX-2 do blueprint como desenhado lá): aqui só a comparação final.
- Os grupos B, C e D da suíte do blueprint (sinal de harness, casos triviais, falha silenciosa).
- O aprendizado ao longo de execuções: a memória aqui já está pronta (a autogerada também é congelada antes do teste).
- A estabilidade depois de ciclos sucessivos de atualização (Sub 4.4).
- O laço nativo (Hermes, o polo (a) do Sub 1.6) e o SDK interno como braços.
- O sinal humano (polegar para cima ou para baixo) e seus vieses: aqui o sinal é o classificador determinístico do erro,
  e os riscos de Casper et al. sobre feedback humano não se aplicam à medida.
- A qualidade jurídica da resposta: o sucesso é o do verificador da tarefa sintética.
- Memórias do tipo estratégia ou de contrato de ferramenta (por exemplo, as unidades candidatas de retorno que chega
  como texto e de argumento nomeado, ainda sem memória catalogada): entram neste mesmo protocolo quando chegarem ao
  degrau 3, com as hipóteses de generalidade do §2.3 como pontos de atenção.

## 15. Decisões que dependem do Rafael

Decisões do protocolo (valem para toda unidade):

1. **Onde roda o modelo.** O plano supõe acesso por API aos dois modelos do §5.3, com dados só sintéticos. Se o modelo
   atual de uma unidade só existir pelo gateway interno, ou o experimento roda no ambiente da empresa, ou o modelo atual
   passa a ser outro disponível, com o limite declarado.
2. **O braço autogerado** entra no confirmatório? Custa um sexto a mais de execuções; sem ele, o implícito × explícito
   do Sub 1.7 fica para depois.
3. **Versão cheia ou enxuta** — decide-se depois do piloto, mas o teto de gasto pode ser dito já.
4. **Como o degrau 4 é gravado no catálogo** (um campo novo muda o esquema; fica para a etapa 9).
5. **Harbor ou runner próprio** (a decisão aberta da E0 do blueprint). O plano supõe o runner próprio. Recomendação:
   ficar com ele nesta rodada. As tarefas são um modelo mais ferramentas simuladas, sem estado de ambiente para
   reiniciar; o próprio blueprint aponta o risco do custo do Docker para esse caso (§7, item 8), e a análise do Eval
   Engineering registra o Harbor como provavelmente excessivo para o projeto. O formato de tarefa (Task.md e
   verificador separados do que o agente vê) é o mesmo nos dois, então a troca depois não refaz as tarefas.
6. **O nome da pasta do código.** O blueprint e o `CLAUDE.md` indicam `pocs/2026-09-min-agents/`, que ainda não existe.
   Criada agora, a convenção de data do repositório pediria um nome de novembro. Uma pasta só, para o blueprint e este
   plano.
7. **O tamanho do piloto de tarefas-gatilho** (§9.3, passo 2): 20 tarefas × 5 repetições por espelho estima o `ρ` com
   erro de cerca de ±0,10; 40 × 5 reduz para ±0,08, ao custo de 100 execuções a mais por espelho e por modelo. Como o
   `K` é robusto a esse erro, a recomendação é ficar com 20 × 5, a menos que o `ρ` medido caia perto de uma fronteira da
   tabela de `K`.
8. **A estabilidade (`pass^k`) é medida confirmatória ou secundária?** Hoje é secundária (§8.4). Se for confirmatória,
   ela exige `K ≥ 3` mesmo que a estatística pedisse menos, e o §9.3 passa a ter esse piso.
9. **Fechar o §9.3 depois da leitura do Miller pelo Rafael.** Hoje a seção está marcada como em discussão. Pontos a levar
   para essa conversa: (a) se "poucas repetições, muitas tarefas" se mantém como regra de partida; (b) quantos geradores
   por espelho, já que tarefas do mesmo gerador se parecem; (c) o custo `c` de uma tarefa a mais, que se mede na etapa 2.

As decisões de cada unidade (quais agentes-espelho, quais memórias exploratórias) ficam no adendo dela.

## 16. Modelo de adendo — a ficha de uma unidade

Para acrescentar uma unidade, copie esta ficha para `pocs/plano-experimento-adendo-<nome-da-unidade>.md` (o nome por extenso, sem o código), preencha cada item
com o fato e a fonte (nada que não tenha vindo do catálogo, da mineração ou do ambiente da base) e acrescente a linha
na tabela do §0. O que a ficha não preencher fica escrito como "falta".

| # | Item | O que preencher | De onde vem |
|---|---|---|---|
| 16.1 | **Unidade e memórias** | os ids do catálogo no degrau 3, o texto literal e o hash de cada uma, o escopo (global ou por papel), `nao_vale_em`, `vale_junto_com`, a data e a evidência da revisão; as memórias monitoradas que entram como exploratórias | `memorias.json`; dossiê da unidade |
| 16.2 | **Erro-alvo** | a regra do classificador que define o erro (a assinatura e o mecanismo) e, se a memória cobre só uma parte da unidade, qual parte | `base_pipeline.py`; script específico da mineração |
| 16.3 | **Onde o erro mora** | por papel: erros, execuções, meses; a incidência `π` por papel e mês (quando a etapa 1 sair); o teto de economia | tabelas da mineração; base 3 |
| 16.4 | **Tipo da lição** | fato do ambiente × estratégia, e a consequência para os braços (a hipótese 3 vale? o espelho consegue reproduzir o erro sem o contrato da ferramenta?) | glossário; §2.3 |
| 16.5 | **Modelos** | por papel da unidade, o modelo antigo e o atual, e em qual deles o erro acontece | bases 1 e 2 (`raw.model`) |
| 16.6 | **Agentes-espelho** | os papéis espelhados, a ficha de fidelidade, as tarefas-gatilho (como se provoca o erro sem citar o objeto da lição) e as neutras, as ferramentas simuladas e o contrato delas | base 2; tabelas da mineração |
| 16.7 | **Vizinhos a vigiar** | as unidades que a memória poderia induzir ou atrapalhar (a guarda de outros erros, §8.5) e a regra de adesão por AST (§8.4) | catálogo; dossiê |
| 16.8 | **Tamanhos** | número de agentes-espelho, taxa de base esperada (se houver), totais do §9.2 com a conta | piloto |
| 16.9 | **Hipóteses e braços próprios** | o que esta unidade acrescenta ao §4 e ao §6.1, rotulado como confirmatório ou exploratório | — |
| 16.10 | **Riscos próprios** | o que desta unidade ameaça a validade e o controle | — |
| 16.11 | **Decisões abertas** | o que depende do Rafael para esta unidade | — |

## Leitura recomendada

Se for ler um artigo só: **Gloaguen et al. (2026), *Evaluating AGENTS.md*.** É o experimento publicado mais parecido
com este: compara agentes sem arquivo de contexto, com arquivo gerado por LLM e com arquivo escrito pelo desenvolvedor
(o "sem memória", o "autogerada" e o "revisada" daqui); mede sucesso, passos, custo e se o agente segue as instruções;
usa testes estratificados (Cochran-Mantel-Haenszel, permutação, McNemar). E traz o resultado que mais ameaça as
hipóteses 1 e 2: o contexto gerado por LLM não mudou o sucesso e subiu o custo em ~20%. O que ele não tem e este plano
tem: latência (não medida lá), repetições por tarefa (lá é uma amostra por instância), placebo e um erro-alvo definido.
Para a parte estatística (§9 e §12), o complemento é Miller (2024).

## Referências

**Estado da verificação:** os itens sem † tiveram título, autores, ano e identificador conferidos por busca na web em
12/11/2026. Os marcados com † (Reflexion, ExpeL, ReasoningBank, MemGPT, Lost in the Middle, AgentDebug) **não foram
buscados de novo**: o identificador vem das notas já existentes em `papers/` e da fila de leitura. Só três tiveram mais
que o resumo lido, por um agente, em 12/11: **Miller (2024)**, o PDF inteiro, com fichamento em
[`pocs/literature/miller-2411.00640.md`](literature/miller-2411.00640.md); **Gloaguen et al.** (o texto do
arXiv, quase inteiro: desenho, medidas, estatística e limites conferidos); e o **SkillsBench** (as páginas de resumo da
v1 e da v4). **Nenhum foi lido pelo Rafael** (o fichamento do Miller está marcado como 🔎, falta o ✅); os outros números
citados vêm dos resumos.

*Fontes internas que o plano usa:* a [hipótese de arquitetura](../discussion/hipoteses/knowledge-as-infra-architecture-hypothesis.md)
(§A, §C, §D, §F, "Scope clarification"), a [política de promoção](../discussion/hipoteses/promotion-policy-log-to-ltm.md),
as conexões com o [Eval Engineering](../discussion/hipoteses/eval-engineering-skill-architecture-connections.md), a
[análise do SDK interno](../discussion/hipoteses/internal-memory-sdk-vs-mechanism.md), as
[reflexões de 28/08](../discussion/reflexoes/checkpoint-2026-08-28-reflections.md), as
[perguntas abertas](../discussion/open-questions.md), o [doc 17](../analysis/2026-09-trace-law-flow/docs/17-validacao-memorias.md),
os relatórios das bases 2 e 3 e o [blueprint](blueprint-m1-pocs-minimos.md).

*Método estatístico e desenho*

- Miller, E. (2024). *Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations.* arXiv:2411.00640.
- Bowyer, S., Aitchison, L., Ivanova, D. R. (2025). *Position: Don't Use the CLT in LLM Evals With Fewer Than a Few Hundred Datapoints.* ICML 2025. arXiv:2503.01747.
- Atil, B. et al. (2024). *Non-Determinism of "Deterministic" LLM Settings.* arXiv:2408.04667.
- Dietterich, T. G. (1998). *Approximate Statistical Tests for Comparing Supervised Classification Learning Algorithms.* Neural Computation 10(7), 1895–1923.
- Holm, S. (1979). *A Simple Sequentially Rejective Multiple Test Procedure.* Scandinavian Journal of Statistics 6(2), 65–70.
- Barnett, A. G., van der Pols, J. C., Dobson, A. J. (2005). *Regression to the mean: what it is and how to deal with it.* International Journal of Epidemiology 34(1), 215–220.
- Nosek, B. A., Ebersole, C. R., DeHaven, A. C., Mellor, D. T. (2018). *The preregistration revolution.* PNAS 115(11), 2600–2606.

*Medidas de eficiência e confiabilidade de agentes*

- Kapoor, S., Stroebl, B., Siegel, Z., Nadgir, N., Narayanan, A. (2024). *AI Agents That Matter.* TMLR 2025. arXiv:2407.01502.
- Yao, S., Shinn, N., Razavi, P., Narasimhan, K. (2024). *τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains.* ICLR 2025. arXiv:2406.12045.
- Erol, M. H., El, B., Suzgun, M., Yuksekgonul, M., Zou, J. (2025). *Cost-of-Pass: An Economic Framework for Evaluating Language Models.* arXiv:2504.13359.
- Lumer, E. et al. (2026). *Don't Break the Cache: An Evaluation of Prompt Caching for Long-Horizon Agentic Tasks.* arXiv:2601.06007.

*Contexto a mais: quando ajuda e quando custa*

- Gloaguen, T., Mündler, N., Müller, M., Raychev, V., Vechev, M. (2026). *Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?* arXiv:2602.11988. Desenho conferido no texto: SWE-bench Lite (300 tarefas) e CTXbench (138), quatro pares agente-modelo, uma amostra por instância; latência não medida.
- Li, X. et al. (2026). *SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks.* arXiv:2602.12670. A frase sobre lições autogeradas ("no benefit on average") está no resumo da v1 (13/02/2026); o da v4 (14/06/2026) não a traz e dá, para as curadas, 33,9% → 50,5%.
- Hsieh, C.-Y. et al. (2023). *Tool Documentation Enables Zero-Shot Tool-Usage with Large Language Models.* arXiv:2308.00675.
- Shi, F., Chen, X. et al. (2023). *Large Language Models Can Be Easily Distracted by Irrelevant Context.* ICML 2023. arXiv:2302.00093.
- Hong, K., Troynikov, A., Huber, J. (2025). *Context Rot: How Increasing Input Tokens Impacts LLM Performance.* Relatório técnico, Chroma.
- Liu, N. F. et al. (2023). *Lost in the Middle: How Language Models Use Long Contexts.* TACL. arXiv:2307.03172. †
- Li, Liu, Bashkansky, Bau, Viégas, Pfister, Wattenberg (2024). *Instruction (In)Stability.* COLM 2024. arXiv:2402.10962. † (autores e título como na fila de leitura do repositório, item 48; não conferido de novo, e o título pode estar abreviado)
- Gan, T., Sun, Q. (2025). *RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection via Retrieval-Augmented Generation.* arXiv:2505.03275.

*Memória de experiência em agentes*

- Shinn, N. et al. (2023). *Reflexion.* arXiv:2303.11366. †
- Zhao, A. et al. (2024). *ExpeL.* arXiv:2308.10144. †
- Ouyang, S. et al. (2025). *ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory.* ICLR 2026. arXiv:2509.25140. †
- Suzgun, M., Yuksekgonul, M., Bianchi, F., Jurafsky, D., Zou, J. (2025). *Dynamic Cheatsheet: Test-Time Learning with Adaptive Memory.* arXiv:2504.07952.
- *Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models* (ACE, 2025). ICLR 2026. arXiv:2510.04618.
- Wang, Z. Z., Mao, J., Fried, D., Neubig, G. (2024). *Agent Workflow Memory.* arXiv:2409.07429.
- Xiong, Z., Lin, Y. et al. (2025). *How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior.* arXiv:2505.16067.
- Yuan, B., Su, Y., Yao, K. (2026). *Diagnosing Retrieval vs. Utilization Bottlenecks in LLM Agent Memory.* arXiv:2603.02473.
- Packer, C. et al. (2023). *MemGPT.* arXiv:2310.08560. †
- Hu, Y., Wang, Y., McAuley, J. (2025). *Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions* (MemoryAgentBench). arXiv:2507.05257.
- Wei, T. et al. (2025). *Evo-Memory: Benchmarking LLM Agent Test-time Learning with Self-Evolving Memory.* arXiv:2511.20857.

*Replay, intervenção e ferramentas simuladas*

- Ma, M. et al. (2025). *DoVer: Intervention-Driven Auto Debugging for LLM Multi-Agent Systems.* ICLR 2026. arXiv:2512.06749.
- Zhu, K. et al. (2025). *Where LLM Agents Fail and How They Can Learn From Failures* (AgentDebug). arXiv:2509.25370. †
- Guo, Z. et al. (2024). *StableToolBench: Towards Stable Large-Scale Benchmarking on Tool Learning of Large Language Models.* Findings of ACL 2024. arXiv:2403.07714.
- Feng, E., Zhou, W. et al. (2025). *Get Experience from Practice: LLM Agents with Record & Replay.* arXiv:2505.17716.

*Documentação de framework:* smolagents — `instructions`, `step_callbacks`, `agent.step` e `MCPClient` (tutoriais
"Manage your agent's memory", "Building good agents" e "Tools", consultados em 12/11/2026).
