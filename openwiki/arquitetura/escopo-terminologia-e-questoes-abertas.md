---
type: decision-log
title: Escopo, Terminologia e Questões Abertas
description: Log de decisões de escopo/terminologia do mecanismo de memória (forma não-paramétrica, o sentido de "RL" no título do projeto, cross-trial vs. cross-agent) e o catálogo vivo de questões ainda não resolvidas sobre a arquitetura hipotética.
tags: [scope-decisions, terminology, open-questions, architecture-hypothesis, reinforcement-learning, non-parametric-memory]
verified:
  - by: openwiki/0.6.0
    at: 2026-09-24T16:54:16.453Z
sources:
  - id: openwiki-source-569719c5da69b38f321cdb6a
    resource: repo://analysis/2026-09-trace-law-flow/pipeline/base_pipeline.py
  - id: openwiki-source-631277a618f3e5073c6d0450
    resource: repo://analysis/2026-09-trace-law-flow/pipeline/checklist.py
  - id: openwiki-source-968204141b3124543370ca68
    resource: repo://analysis/README.md
  - id: openwiki-source-7f7d00c2d53f56cf831f9d45
    resource: repo://analysis/schema-e-taxonomia-de-erros.md
  - id: openwiki-source-fb0fb67897cb389c902db805
    resource: repo://analysis/status_execucao_agente.csv
  - id: openwiki-source-23df8725c93a4ea44539b97e
    resource: repo://discussion/open-questions.md
  - id: openwiki-source-1564f2f4d84d9043ebdb5351
    resource: repo://discussion/scope-and-terminology-decisions.md
  - id: openwiki-source-d841fc5e9e282ddb91a8cfaf
    resource: repo://research-diary/Set/diario_campo_2026-09-21.md
generated: { by: "claude-code", at: "2026-09-23T23:38:13.077Z" }
---

Este par de documentos — [`discussion/scope-and-terminology-decisions.md`](../../discussion/scope-and-terminology-decisions.md) e [`discussion/open-questions.md`](../../discussion/open-questions.md) — funciona como o registro de governança do projeto: um é o log de **decisões já tomadas** (append-only, atualizado no lugar quando uma decisão é revisitada), o outro é a **lista viva de itens ainda não resolvidos**. Quando uma questão aberta se resolve, a resolução migra para o log de decisões e o item é apagado da lista de abertas — as duas fontes nunca duplicam o mesmo fato por muito tempo.

## Decisões de escopo e terminologia

| # | Decisão | Onde |
|---|---|---|
| 1 | **Forma de memória: não-paramétrica, por desenho.** O vocabulário do Plano de Trabalho ("instruções, exemplos e contexto operacional armazenados na memória") é textual/não-paramétrico. Métodos de edição de memória paramétrica (MEND, KnowledgeEditor, PersonalityEdit, APP, MAC) ficam fora do escopo de implementação — mas continuam citados como "alternativa considerada e rejeitada" no documento de arquitetura. | [`scope-and-terminology-decisions.md#1`](../../discussion/scope-and-terminology-decisions.md#1-memory-form-non-parametric-by-design) |
| 2 | **O que "aprendizado por reforço" significa no título do projeto.** Resolvido em 20/08/2026 com o tutor (canal formal): o RL do próprio mecanismo **não é SFT** — é um ajuste de harness, dirigido por um sinal explícito do usuário (👍/👎), mais próximo da família "verbal RL" da Reflexion do que do fine-tuning literal por policy-gradient (Retroformer, Memory-R1). Reforçado duas vezes depois (28/08, por argumento de custo de inferência) e parcialmente auditado contra o corpus de leitura (24/08): nenhum dos modelos lidos até agora é um precedente limpo de "RL via prompt engineering". | [`scope-and-terminology-decisions.md#2`](../../discussion/scope-and-terminology-decisions.md#2-what-reinforcement-learning-means-in-this-projects-title) |
| 3 | **Cross-trial vs. cross-agent — fronteiras diferentes, não sinônimos.** Cross-trial é um limite **temporal** (mesmo agente, invocações separadas); cross-agent é um limite de **identidade** (agentes distintos trocando informação via protocolo). Isso restringe o escopo da preocupação de confidencialidade original da Macroatividade 2 a handoffs entre agentes especializados dentro do mesmo fluxo — não à persistência de um único agente entre suas próprias sessões. | [`scope-and-terminology-decisions.md#3`](../../discussion/scope-and-terminology-decisions.md#3-cross-trial-vs-cross-agent) |
| 4 | **Correção de datação de benchmark direto.** A survey de Zhang et al. (§6.3) afirma que, na época, não existia benchmark dedicado para avaliação direta de módulos de memória — mas esse gap fechou meses depois (LoCoMo, LongMemEval). Qualquer citação da frase original da survey precisa carregar essa correção junto. | [`scope-and-terminology-decisions.md#4`](../../discussion/scope-and-terminology-decisions.md#4-direct-evaluation-benchmark-dating-correction) |
| 5 | **Métrica Reference Accuracy (Sub 3.6) — escopo restrito.** Entra como uma quarta métrica, mas com gabarito anotado manualmente sobre casos do próprio fluxo jurídico do projeto — não um benchmark generalizável estilo LoCoMo/LongMemEval (seria overengineering frente ao cronograma). Está **bloqueada**, não indecisa: só pode ser implementada depois que a Sub 1.4 (fluxo-alvo) e a Sub 1.5 (critério de acerto/erro) fecharem. | [`scope-and-terminology-decisions.md#5`](../../discussion/scope-and-terminology-decisions.md#5-reference-accuracy-metric--scope-sub-36) |

## Um refinamento recente que ainda não é uma "decisão" formal

Ao minerar o primeiro trace bruto (`analysis/2026-09-trace-law-flow/`), o projeto precisou decidir se a mineração de insights cobre também a **correção/groundedness** da resposta final do agente, não só falhas de execução. A resolução de trabalho (08–16/09/2026, ainda não promovida ao log de decisões) é uma divisão em três, não em duas:

- **(a) Falha de execução/processo** — quebra mecânica do próprio agente (tool call malformado, retorno mal tratado, loop de retry). Extraível de graça do trace, sem LLM, sem gabarito.
- **(b) Groundedness-como-presença** — verificar se um token tipado da resposta final (nº CNJ, CPF/CNPJ, data, valor) aparece em alguma observação anterior da mesma execução. Proxy determinístico e auditável, mas presença ≠ correção.
- **(c) Groundedness-como-correção-semântica** — se a conclusão jurídica citada realmente diz o que se afirma. Exige juiz (LLM-as-judge) ou humano — **genuinamente fora do escopo v1**, que exige determinismo/auditabilidade.

Ver [`discussion/open-questions.md`](../../discussion/open-questions.md) (o item que começa com "Does the memory-mechanism's insight-mining scope include output correctness/groundedness...") para o raciocínio completo e as atualizações de 16/09/2026.

## Questões em aberto (catálogo, não cópia integral)

`open-questions.md` é atualizado quase diariamente e carrega muito mais nuance do que cabe aqui — esta tabela é um mapa de navegação por tema, não um substituto. Para o raciocínio completo, os trade-offs registrados e as atas de reunião que os alimentam, siga o link de cada linha.

| Tema | Status resumido |
|---|---|
| Auditoria do corpus de leitura por "RL via prompt engineering" | Parcialmente feita (24/08); Synapse/MetaGPT/TiM/RecAgent/S³ ainda não auditados. |
| Cadência de síntese semanal do diário de campo | Desenhada, ainda não testada sob uso real prolongado. |
| Memória do agente vs. fatos já servidos por ferramenta MCP de regra de negócio | Levantado no checkpoint de 20/08; ainda sem decisão. |
| Signal Capture precisa de dois desenhos (copiloto com humano vs. modo sistêmico via Kafka)? | Ponto de entrada sistêmico já identificado (API interna); o que exatamente capturar nesse caminho ainda está aberto. |
| Ambiguidade canal informal-coordenador vs. formal-tutor | Questão de governança do projeto, não só de logging; pendente de check-in explícito com o tutor. |
| Relação com os três mecanismos de memória já vivos na plataforma (LangGraph checkpoints, dump por execução do Small Agent, memória nativa do Hermes) | Tutor sinalizou "ao lado, como uma 4ª camada distinta" como leitura provável (28/08), não uma resolução. |
| Classe `task-private` vs. `cross-agent-reusable` de memória | Reabre parcialmente o limite "cross-agent fora de escopo" — recomendação de reconciliação registrada (28/08), não decidida. |
| `ACL(μ, uid)` — visibilidade cross-domínio/cross-squad | Lean para RBAC por domínio + Collaborative Memory (arXiv:2505.18279) como candidato de modelo; não desenhado — não existe auth centralizada na plataforma hoje. |
| A arquitetura de 6 componentes sobrevive ao POC (Sub 1.6/1.7)? | Ainda não testada contra comportamento real. |
| Falta um componente de Consolidação (G) — merge/dedup de memória redundante | Candidatos levantados (SAGE Checker, Mem0 UPDATE, A-Mem, ReasoningBank), nenhum adotado. |
| Confiabilidade do sinal thumbs up/down | Tutor confirmou de forma independente uma assimetria (👍 quase sem sinal, 👎 forte) em 28/08; cruzamento com a literatura de RLHF ainda pendente. |
| Granularidade do trigger de escrita episódica (componente A): por estágio de pipeline ou por caso inteiro? | Lean de trabalho: por estágio (26/08), ainda sem aval do tutor. |
| Gaps do write path do componente A (schema, substrato físico, tipo de vector store, chunking, o que é um "episodic trace") | Parcialmente resolvido: trace = trajetória completa, não resumo de business-record (27/08). Os outros quatro seguem abertos. |
<!-- openwiki: broken internal link [../../discussion/promotion-policy-log-to-ltm.md] file "../../discussion/promotion-policy-log-to-ltm.md" does not exist. Fix the href or restore the target, then delete this comment. -->
| Política de promoção log episódico → LTM (gate estilo SAGE) | Lean forte de que o gate é estruturalmente necessário, não opcional; consolidada em nota própria ([`promotion-policy-log-to-ltm.md`](../../discussion/promotion-policy-log-to-ltm.md)) com nove componentes de política ainda abertos. |
| Quem é dono do gate de admissão — mecanismo determinístico separado ou o próprio Update Engine ("curador")? | Lean atualizado em 01/09: filtro determinístico de anomalia, unificado, roda antes do Update Engine; predicado exato ainda não decidido. |
| Hard-delete automático por threshold vs. gated/revisado por humano | Não decidido; alternativa gated dá um remit concreto ao componente G hipotético. |
| Quais parâmetros do v1 (estático) viram adaptativos no v2, mantendo as regras fixas | Mapa por componente registrado (27/08) — princípio: "adaptativo calibra parâmetro, nunca muda regra". Não é requisito do v1, mas os parâmetros devem ser externalizados como config. |
| Segunda extração de trace: isolar em pasta nova ou mesclar com a primeira? | Decidido (16/09): isolar primeiro, com o núcleo analítico copiado byte-idêntico entre as pastas — desde 18/09 esse núcleo vive em `pipeline/base_pipeline.py`, o que torna a exigência trivialmente verificável. **A segunda extração já aconteceu**: uma base independente de 1.000 execuções ("base 2"), que trouxe um `error.type` novo (`AgentMaxStepsError`, n=1), reabriu o bucket de protocolo do harness (22/09) e expôs que `anomesdia` data o lote de extração, não a execução — a data real passou a vir de `dat_hor_inio_exeo`. A tabela de status também chegou (`analysis/status_execucao_agente.csv`; o dicionário 1/2/3/34/67 está em `schema-e-taxonomia-de-erros.md`). O intake de uma base nova agora é operacionalizado por `pipeline/checklist.py` (censo de `error.type`, drift de colunas, checagem de sobreposição de `cod_idef_exeo` entre bases). |
| Dataset gold-standard anotado por especialistas para calibrar um LLM-as-judge | Proposto em 15/09; gated na leitura própria do Rafael de Casper et al. (ainda 🔎, não lida) antes de fechar o protocolo de anotação. |
| Filtro de anomalia deveria distinguir causa comportamental (do agente) de causa ambiental/infra antes de rotear ao Update Engine? | Levantado em 10/09 a partir da Eval Engineering Skill da LangChain; não decidido. |

## Como este par de documentos se conecta ao resto do projeto

- A [Hipótese de Arquitetura "Knowledge as Infra"](hipotese-knowledge-as-infra.md) é o alvo de boa parte das questões em aberto listadas acima (componentes A–G).
- O [Plano de Trabalho](../referencia/plano-de-trabalho.md) define as sub-atividades (Sub 1.4, 1.5, 1.6, 1.7, 3.6 etc.) que essas decisões e questões referenciam constantemente como dependência ou bloqueio.
- Itens abertos nascem tipicamente de uma entrada do [diário de campo](../fluxos/diario-de-campo.md) ou de um [registro de reunião](../fluxos/registros-de-reuniao-e-notas-de-discussao.md) — ambos os documentos-fonte deste log citam essas entradas como proveniência de cada decisão.
