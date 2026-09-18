---
type: architecture-hypothesis
title: Hipótese de Arquitetura "Knowledge as Infra"
description: A arquitetura de trabalho (ainda não travada) do mecanismo de atualização de memória do projeto — seis componentes que combinam armazenamento não-paramétrico, captura dual de sinal, um Update Engine batched, um Commit Gate de governança e forgetting real, mais o critério de graduação para o Plano de Trabalho formal.
tags: [architecture-hypothesis, memory-mechanism, commit-gate, update-engine, mcp-integration, forgetting, non-parametric-memory]
verified:
  - by: openwiki/0.5.1
    at: 2026-09-18T11:27:06.172Z
sources:
  - id: openwiki-source-89148645df3f0c0dfb8af600
    resource: repo://discussion/knowledge-as-infra-architecture-hypothesis.md
generated: { by: "claude-code", at: "2026-09-18T11:27:06.172Z" }
---

## Status — hipótese, não arquitetura travada

O documento canônico ([`discussion/knowledge-as-infra-architecture-hypothesis.md`](../../discussion/knowledge-as-infra-architecture-hypothesis.md)) é explícito: isto é "a melhor suposição fundamentada dado o que já foi lido", não algo a defender como final para o tutor. Ele só vira decisão formal (Sub 2.2) depois que os POCs de agentes mínimos (Sub 1.6) e a comparação implícito-vs-explícito (Sub 1.7) testarem essas alegações contra comportamento real. Uma versão verbatim, dividida por seção, existe em [`knowledge-as-infra-architecture-hypothesis/`](../../discussion/knowledge-as-infra-architecture-hypothesis/README.md) apenas para leitura — o arquivo canônico, editável, é o `.md` na raiz de `discussion/`.

## As duas perguntas de enquadramento que o desenho resolve

1. **"Módulo plugável/agnóstico" vs. "memória no loop do agente é mais eficaz" não são opostos.** A tensão se desfaz quando "no loop" é lido corretamente: significa que o próprio agente decide invocar uma operação de memória como uma tool call explícita e auditável — não que o mecanismo precisa estar embutido nos internals proprietários de um framework específico. Uma interface de tool-call (MCP, já padrão de integração cross-framework da plataforma) é ao mesmo tempo agnóstica e loop-native.
2. **"RL depois de ~100 casos" ≠ "atualização de memória" — são cadências diferentes, e o Plano já codifica essa separação.** Sub 3.1 (captura/armazenamento — contínua, por caso) e Sub 3.2 (ajuste controlado — em lote, com gate) já são sub-atividades separadas. Escritas de memória contínuas são baratas e reversíveis; mudar o comportamento padrão do agente é caro e precisa de controle.

## Os seis componentes

| Componente | Papel | O que já está assentado | Maior gap aberto |
|---|---|---|---|
| **A. Memory Store** | Registro textual não-paramétrico por caso, contínuo | ADD incondicional, disparado por evento de sistema (conclusão de estágio do pipeline via Kafka), não por tool call do agente; log append-only imutável separado da camada mutável derivada | O que exatamente um "episodic trace" contém (resumo de business-record vs. trajetória completa ReAct/ExpeL) — resolvido a favor da trajetória completa em 27/08, mas schema exato, substrato físico e chunking seguem indefinidos |
| **B. Signal Capture** | Dois caminhos de captura de sinal (copiloto humano 👍👎, sistêmico via evento Kafka), ambos escrevendo no mesmo Signal Ledger | Nenhum dos dois caminhos é exposto como tool MCP — nem um clique humano nem um evento de sistema é uma decisão do agente | Schema do Signal Ledger indefinido; sem redundância de avaliador (nenhum mecanismo para uma segunda opinião independente); latência de sinal de desfecho varia por tipo de agente (cadastro: ~1–2 meses; contestação: ~13 meses) |
| **C. Update Engine** | Camada de cognição: comparação estilo ExpeL de casos de sucesso/falha, gatilho por severidade cumulativa, produz uma **proposta**, nunca um commit | O trigger é uma soma ponderada por severidade + teto de N casos, não um N fixo; o Engine lê tanto o Signal Ledger quanto os traces episódicos do Memory Store | Se deve ter acesso a contexto além dos próprios traces episódicos (traces relacionados, RAG jurídico externo, ferramentas MCP de regra de negócio); se é o candidato certo para propor mudanças de harness em uma v2 |
| **D. Commit Gate** | Camada de governança: revisão (não auto-voto de um único modelo) que checa qualidade agregada do sinal (taxa de concordância, risco de erro correlacionado) antes de commitar uma atualização versionada e reversível | Formalizado como o Write Validation Gate do SSGM (`ΔM ∧ M_core ⊨ ⊥`, checagem NLI de contradição contra fatos protegidos) | Sem redundância de avaliador ainda desenhada para calcular "taxa de concordância"; checagem NLI via classificador dedicado vs. LLM prompteado ainda não decidida |
| **E. Forgetting** | Decay + um passo real de hard-delete, com razão logada | Decay Weibull do SSGM (`w(Δτ) = exp(−(Δτ/η)^κ)`) mais expressivo que o exponencial simples da MemoryBank; princípio de Reversible Reconciliation (log imutável + camada derivada mutável, recuperável por replay) resolve o rollback da Sub 3.4 | Se o hard-delete deve continuar automático no hot path ou virar um item "candidato a deleção" roteado por um gate de revisão humana |
| **F. MCP Integration** | `recall_memory()` e `propose_memory_update()` expostas como tools MCP, chamáveis por qualquer framework de agente da plataforma sem adotar uma implementação de memória interna compartilhada | A escrita episódica automática fica deliberadamente fora dessa superfície de tool — é um gatilho de sistema, não algo que o agente decide invocar | — |
| **G. Consolidation** *(gap, ainda não é um componente desenhado)* | Merge/dedup de memória redundante (o eixo "Evolution" da taxonomia Hu/Liu, além de Updating e Forgetting) | Nenhum — hoje conteúdo redundante só é podado por obsolescência (Forgetting), nunca por checagem de redundância | Candidatos levantados e não adotados: o "Checker" do SAGE (ainda ambíguo — mecanismo de consolidação ou refinamento de política que nunca toca memória?), o UPDATE julgado por LLM do Mem0, A-Mem, ReasoningBank |

## Mapeamento com o framework SSGM (adicionado 27/08/2026)

Esta arquitetura implementa a mesma estrutura conceitual de três camadas do SSGM (arXiv:2603.11768, Figura 4) — Cognition Layer → Governance Layer → Memory Layer — mas com a governança distribuída nos pontos onde é necessária, em vez de centralizada num único middleware:

| Camada SSGM | Este projeto | Componente |
|---|---|---|
| Cognition Layer | Update Engine | C |
| Governance Layer (Write Validation) | Commit Gate | D |
| Memory Layer (log imutável + substrato mutável) | Memory Store | A |

A adaptação chave: o Governance Middleware do SSGM intercepta *todas* as interações de memória (leitura e escrita) num único middleware; este desenho intercepta só a *escrita na strategy layer* (cold path, Commit Gate) — o log episódico é ADD-incondicional (sem gate, por exigência de auditabilidade), e a filtragem de ACL/frescor do caminho de leitura já está embutida no próprio `recall_memory` (fórmula de retrieval do SSGM, componente A).

## Refinamento de 01/09/2026 — três camadas operacionais dentro do Memory Store

O Memory Store deixa de ser um "two-tier" simples (log cru + índice recuperável) e passa a ter três camadas operacionais, com um único filtro determinístico (sem LLM) servindo de gate antes do Update Engine para os dois caminhos de escrita:

| # | Camada | Conteúdo | Recuperável via `recall_memory`? |
|---|---|---|---|
| 1 | Log episódico | trajetórias cruas, append-only, texto puro, sem embedding | Não — só auditoria + input do Update Engine |
| 2 | LTM recuperável (tipada) | `exemplar` (trace concreto) + `reflexão` (1ª reflexão do Update Engine), ambos com score `S` e decay `R = e^(−τ/S)` | Sim |
| 3 | Strategy layer | heurística destilada (2ª reflexão / meta-reflexão do Update Engine) | Sim |

Consequência prática: `R ≥ θ1` deixa de decidir *entrada* na camada 2 (que passa a depender do filtro determinístico de anomalia — tamanho do trace, nº de tool calls, distribuição de 👎, outlier) e vira só regra de *permanência/rebaixamento* dentro dela. O Update Engine passa a produzir **dois writes**: uma 1ª reflexão (camada 2, gate mais leve de grounding/dedup/ACL) e uma 2ª reflexão/meta-reflexão (camada 3, via o Commit Gate NLI completo). Detalhe e trade-offs em [`promotion-policy-log-to-ltm.md`](../../discussion/promotion-policy-log-to-ltm.md).

## Por que nenhum candidato da literatura bastava sozinho

Nenhum dos oito papers lidos no reading sprint combina memória não-paramétrica + gate humano/externo + controle em lote + versionamento/rollback + forgetting real ao mesmo tempo: ExpeL sobrescreve silenciosamente sem trilha de auditoria; Memento e SCM nunca descartam; MemoryBank nunca faz hard-delete de fato. O Commit Gate é onde essa combinação é efetivamente construída — a contribuição que o projeto trata como a sua própria.

## Primeira instância empírica concreta do sinal de mudança de harness (17/09/2026)

A análise de traces (`analysis/2026-09-trace-law-flow/`) minerou uma unidade candidata (nº10, `validar_quebra_sigilo`) que é exatamente o caso "proponha uma mudança de harness em vez de uma unidade de memória" que a Seção C só tinha em forma abstrata até então: o prompt de sistema declara o **mesmo nome de campo** para o retorno da ferramenta e para o campo de saída do JSON final, o agente conflacia os dois, e o valor errado é mensurável diretamente no payload entregue — 9 de 21 respostas entregues (43%, ao longo de 3 meses) carregam um campo regulatório inválido, sem nenhuma exceção levantada em log. A regra de decisão pré-registrada (≥1 caso confirmado chegando ao payload final → harness, não memória) não precisou do replay em sandbox da Etapa 3 do AgentDebug — comparar o contrato declarado contra o schema real e o payload entregue já bastou.

## Exemplo trabalhado (condensado)

Um caso de contestação de consignado: o agente chama `recall_memory`, recebe uma heurística ("priorizar contestação quando a assinatura biométrica é validada — 14/16 casos históricos ganhos; checar o prazo prescricional primeiro") mais episódios passados relevantes. O caso é logado no Memory Store independente do desfecho. Um revisor sinaliza um caso relacionado com 👎; meses depois, um desfecho adverso de um caso não relacionado chega via Kafka sem envolvimento humano. Três erros relacionados a prazo acumulam severidade suficiente para cruzar o threshold do Update Engine bem antes de 100 casos — ele propõe apertar a heurística para checar o prazo primeiro. O Commit Gate checa se o mesmo revisor sinalizou os três (risco de erro correlacionado) e se as sinalizações são sobre substância ou estilo, então commita uma nova heurística versionada com um ponteiro de rollback para a anterior.

## Relação com o que já existe, e limites de escopo

Não substitui nem unifica os três mecanismos de memória já vivos na plataforma (checkpoints LangGraph do Manager, dump por execução do Small Agent, memória nativa do Hermes) — todos os três são escopados por sessão/execução; este é o quarto, uma camada cross-trial que qualquer um deles poderia chamar via a mesma interface MCP. Fora de escopo por decisão prévia: fatos de negócio estruturados e de mudança rápida (já servidos por ferramentas MCP de regra de negócio) e o compartilhamento de memória de **substância de caso** entre agentes distintos. Revisão de 28/08/2026: essa linha foi estreitada de um "cross-agent sharing" genérico para especificamente *substância de caso*, depois que o tutor trouxe de volta à mesa uma classe de memória operacional reutilizável entre *tipos* de agente (o exemplo dele: uma mudança de API AWS que quebrou uma query, descoberta por um agente, que qualquer agente deveria encontrar antes de bater na mesma parede) — ainda não desenhada, rastreada como questão aberta.

## Estático por desenho (v1); onde a adaptação poderia entrar (v2)

A arquitetura é **estática por desenho** — todas as operações são regras fixas, auditáveis e determinísticas, a escolha certa para auditabilidade e compliance no domínio jurídico. O princípio que governa qualquer extensão adaptativa futura: **adaptativo pode calibrar parâmetros, nunca mudar regras.** Onde o mecanismo decide "quanto" (thresholds, pesos, taxas de decay), a adaptação pode aprender; onde decide "se" (deletar ou não, validar ou não, capturar ou não), tem que continuar fixo e governado. Exemplos do lado permitido: os pesos do score `S` (componente A), os thresholds `θ1`/`θ2` do gate SAGE, o mapeamento `outcome_type → severidade` (componente B). Exemplos do lado proibido: a exigência de revisão humana do Commit Gate, o contrato da interface MCP, o fato de o Update Engine sempre propor e nunca commitar.

## Critério de graduação para a Sub 2.2

Os agentes mínimos da Sub 1.6 (loop de aprendizado fechado nativo vs. memória transparente programática) precisam testar as alegações reais deste desenho, não só assumi-las: um recall explícito via tool call MCP alcança eficácia comparável à injeção nativa automática do Hermes? O trigger ponderado por severidade se comporta de forma sensata contra casos reais anotados? A checagem de qualidade de sinal do Commit Gate reduz de fato o risco de erro correlacionado/sicofância que Casper et al. descrevem, ou é teatro de segurança sem diversidade real de avaliadores? A comparação implícito-vs-explícito da Sub 1.7 é onde esta hipótese sobrevive ao contato com um POC ou é revisada.
