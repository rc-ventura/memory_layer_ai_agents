---
type: specification
title: "Blueprint das POCs Mínimas do M1"
description: A especificação executável das POCs de agentes mínimos do Entregável 1 (Sub 1.6/1.7) — as perguntas Q1–Q7, os dois polos de memória (Hermes nativo × smolagents programático), a suite sintética de tarefas A–D com origem empírica nas unidades mineradas, as etapas E0–E7 e os experimentos EX-1–EX-7.
tags: [poc-blueprint, memory-mechanism, sub-1.6, sub-1.7, experiments, m1-deliverable]
verified:
  - by: openwiki/0.6.0
    at: 2026-10-09T17:09:54.387Z
sources:
  - id: openwiki-source-4859aa37b78a50a40f57623f
    resource: repo://pocs/blueprint-m1-pocs-minimos.md
generated: { by: "claude-code", at: "2026-10-09T17:09:54.387Z" }
---

`pocs/blueprint-m1-pocs-minimos.md` (28/09/2026, proposta para aprovação) é o plano executável da pendência central do **Entregável 1** da Macroatividade 1 — a construção das POCs mínimas que a Sub 1.6 pede e a análise comparativa implícito × explícito da Sub 1.7. Ele **não** é a POC nem o relatório comparativo: é a especificação do que construir, em que ordem e quais experimentos rodar para que o relatório comparativo tenha evidência real em vez de opinião. É também a **bancada de teste da hipótese knowledge-as-infra** — ver [Hipótese "Knowledge as Infra"](../arquitetura/hipotese-knowledge-as-infra.md), cujos gaps ("what has to happen before this becomes Sub 2.2") alimentam as perguntas.

A regra estrutural do blueprint: **nenhum experimento sem uma pergunta na frente; nenhuma pergunta sem um experimento.**

## As sete perguntas (Q1–Q7)

Cada pergunta tem origem declarada num documento canônico do projeto:

| # | Pergunta | Origem |
|---|---|---|
| Q1 | O recall **explícito via tool call** (`recall_memory`, MCP, agnóstico de framework) atinge eficácia comparável à **injeção automática nativa** (Hermes)? | hipótese KaI, "what has to happen" |
| Q2 | O **trigger ponderado por severidade** do Update Engine se comporta de forma sensata — ou o "150" do Generative Agents é intransferível e a escala precisa nascer do zero? | hipótese KaI |
| Q3 | O check de **qualidade de sinal** do Commit Gate (agreement, erro correlacionado, anti-sycophancy) reduz de verdade o risco que Casper et al. nomeia — ou é teatro de segurança sem diversidade real de raters? | `thumbs-feedback-reliability.md` |
| Q4 | Aprendizado **implícito** (conversão sessão→skill automática, sem gate) vs. **explícito** (sinal certo/errado + gate humano): prós, contras e riscos no jurídico | Sub 1.7 do Plano de Trabalho |
| Q5 | O **gate de promoção** log→LTM segura o ruído sem perder o caso raro (meta ~20–30% de promoção)? | `promotion-policy-log-to-ltm.md` |
| Q6 | Os campos do **score DMF-lite** (`w1..w4`) existem de fato na base de traces real? | open-questions, "cinco gaps de storage" |
| Q7 | A família de erro com destino **harness** (a unidade nº10) é corretamente **não** absorvida como memória? | `09-metodologia-erro-a-memoria.md`, Ajuste 5 |

## Os dois polos

**POC-A — loop de aprendizado fechado nativo (Hermes Agent, Nous Research).** Memória em camadas nativa (`MEMORY.md`/`USER.md` + arquivo episódico SQLite FTS5 + skill memory), conversão automática sessão→skill, persistência cross-session por padrão. É o polo (a) do Plano e o benchmark "o que o estado da arte resolve sozinho" das Q1/Q4 — e onde ele para: sem gate de revisão humana, sem versionamento/rollback, sem hard-delete auditável, sem toque externo de sinal.

**POC-B — memória transparente com controle programático explícito (smolagents, CodeAgent).** O polo (b) do Plano e **o mesmo framework dos traces da esteira** já analisados em `analysis/` — o que permite reusar o vocabulário empírico (ActionStep/PlanningStep, `agent.memory.steps`). Nenhuma memória automática: sobre ele se implementa o **esqueleto mínimo do mecanismo do projeto** — log episódico append-only, gate de promoção determinístico, LTM tipada (`exemplar`/`reflexão`), `recall_memory` como tool explícita no loop, trigger ponderado por severidade, Update Engine produzindo **proposta** (nunca commit direto), Commit Gate com revisão humana manual, decay `R = e^(−τ/S)` + rebaixamento + hard-delete gated.

**Recorte v1-POC consciente:** MCP de verdade (a `recall_memory` é registrada localmente no harness com o mesmo contrato — MCP é decisão de integração do Sub 2.5/2.6), NLI no Commit Gate (a revisão é humana manual sobre a proposta versionada) e o adapter de STM via `dump_trajectory()` (POC usa a Opção A, adapter framework-specific sobre `agent.memory.steps`).

## A suite de tarefas — o "jogo" compartilhado

As POCs só comparam algo se rodarem **as mesmas tarefas**, com erro injetado de forma controlada. A suite é **sintética** — ferramentas mockadas cujas assinaturas de erro reproduzem as famílias **reais** mineradas na esteira (nunca conteúdo jurídico real — a mesma disciplina de PII de `analysis/`):

| Grupo | O que injeta | Origem empírica | O que testa |
|---|---|---|---|
| **A — memória-resgatável** | contrato de retorno que o agente não compreende, erro recorrente e ensinável | unidade nº2 minerada | aprendizado cross-trial (Q1, Q4) |
| **B — sinal de harness** | system prompt que declara o mesmo nome de campo para retorno de tool e JSON final | unidade nº10 | falso-positivo de escrita — não deve virar memória (Q7, Q3) |
| **C — beabá** | casos triviais sem nada a aprender (~90% do volume) | premissa do tutor (checkpoint 28/08) | o gate de promoção não deve promover (Q5) |
| **D — falha silenciosa** | timeout no fim de um plano, constraint impede retry, `final_answer` pula a etapa | achado de 25/09, roadmap 26 | detectores sinalizam o que a exceção não vê (Q2/Q7) |

**Regime temporal:** N≈20–30 repetições por tarefa em lotes simulados = "meses", para que a métrica central — **recorrência do mesmo erro entre execuções** — exista de fato (o espelho controlado do achado da esteira: o agente aprende a lição dentro da execução e a perde na próxima). O critério de acerto/erro de cada tarefa é um spec no formato Task.md da skill Eval Engineering — que já é em si um pedaço do documento de especificação preliminar dos sinais de feedback do Entregável 1.

**Formato de execução — decisão aberta em E0:** Harbor (o framework de eval dos criadores do Terminal-Bench: orquestração de trials em paralelo, trajetórias ATIF padronizadas, dataset versionado, adapter Hermes nativo) × runner próprio (mais leve, ao custo de reimplementar trials e perder o formato padronizado). O que fica nosso nos dois casos: a camada de memória entre trials, o Update Engine + Commit Gate rodando **entre** lotes, a instrumentação dentro do loop e o adapter `BaseAgent` da POC-B. Spike de 1 task Harbor como prova.

## Etapas E0–E7

Ordem de execução — cada etapa termina num artefato versionado; **E1 antes de E2/E3** (a suite primeiro, senão cada POC nasce enviesada pelo que o framework facilita):

| Etapa | Conteúdo |
|---|---|
| **E0** | Branch datada `YYYY-MM-DD-pocs-m1`; deps separadas (`uv add --optional pocs`); decisão de backend de LLM; decisão Harbor × runner; diretório `pocs/2026-09-min-agents/` datado como em `analysis/` |
| **E1** | Os 4 grupos de tarefas com tools mockadas + specs Task.md + verifier determinístico (antes de qualquer juiz-LLM) |
| **E2** | POC-A: Hermes mínimo sobre a suite, persistência nativa ligada, conversão sessão→skill coletada |
| **E3** | POC-B: agente mínimo + controle explícito (log incondicional, `recall_memory` no loop, ciclo de vida S→decay→rebaixamento→hard-delete) |
| **E4** | Esqueleto do mecanismo (cold path): filtro de anomalia, Update Engine (1ª × 2ª reflexão), trigger por severidade, proposta versionada, Commit Gate manual com git history como trilha |
| **E5** | Rodar EX-1..EX-7, registrar por experimento |
| **E6** | Confrontar Q1–Q7 com os resultados; resoluções vão para `scope-and-terminology-decisions.md` e `open-questions.md` |
| **E7** | Relatório comparativo (Sub 1.7) + integração no Entregável 1 |

## Experimentos EX-1–EX-7

Cada experimento segue pergunta → desenho → medição → critério, todos sobre a suite E1:

| Exp | Pergunta | O que mede |
|---|---|---|
| **EX-1** | Q1 | recall explícito × injeção nativa × baseline sem memória — taxa de acerto, custo em tokens, miss/over-call da tool |
| **EX-2** | Q4 | redução de recorrência cross-trial — curva erro-por-volta, paralela direta ao achado da esteira |
| **EX-3** | Q2 | trigger por severidade × contagem flat-N nos três cenários (grave isolado, graves concentrados, muitos baratos) |
| **EX-4** | Q3 | Commit Gate sob raters com vieses conhecidos (sycophantic, correlacionado, thumbs assimétrico) — falsa aceitação/rejeição |
| **EX-5** | Q7 | destino memória × harness: grupo B nunca pode ser escrito na strategy layer — falso-positivo grave |
| **EX-6** | Q5 | gate de promoção com ~90% de beabá + um caso raro — fração promovida vs. meta ~20–30% |
| **EX-7** | Q4/Q1 | esquecimento controlado e reversibilidade: decay → rebaixamento → gate de delete; replay do log imutável reconstrói a strategy layer após "commit ruim" |

EX-3 a EX-6 dependem de calibração (θ1, pesos DMF-lite, predicado do filtro, janela) — tratada como **primeira passada documentada**, não número final: θ calibrado na POC prova que o procedimento de calibração funciona e onde a sensibilidade mora.

## Riscos e decisões abertas

1. **Reunião com [ENGENHEIRO-3] pendente** — a POC-A assume o Hermes open source; a variante de plataforma atualiza só as notas de integração, não a POC.
2. **Backend de LLM** — decide em E0 (custo de API × reprodutibilidade local; o tutor descartou fine-tuning por opex GPU em 28/08).
3. **Campos reais do trace** — se os campos do DMF-lite não existirem na base, a POC usa stub determinístico com campos que existam e documenta a substituição.
4. **Harbor × runner próprio** — risco de overhead de Docker para tarefas puro-LLM+mock; mitigado pelo spike de E0.
5. **PII** — POCs rodam 100% em tools mockadas: nenhum conteúdo de trace real é versionado ou entra em prompt de LLM externo; traces reais entram só como evidência de projeto (assinaturas, contagens).
6. **Escopo do cold path** — NLI, redundância real de raters e otimização map-reduce do Engine ficam para a Macroatividade 2, declarado no relatório.

## Como se conecta ao resto do projeto

- Alimenta diretamente o terceiro item do Entregável 1 (*"relatório comparativo entre as abordagens de memória avaliadas, com as respectivas POCs mínimas"*) — ver [Plano de Trabalho](plano-de-trabalho.md).
- Cada pergunta testa um gap da [Hipótese "Knowledge as Infra"](../arquitetura/hipotese-knowledge-as-infra.md); as resoluções voltam para `scope-and-terminology-decisions.md` e `open-questions.md` em E6 — ver [Escopo, Terminologia e Questões Abertas](../arquitetura/escopo-terminologia-e-questoes-abertas.md).
- Os grupos A/B/D da suite têm origem empírica direta nas unidades mineradas pela [Metodologia de Taxonomia de Erros](../fluxos/metodologia-de-taxonomia-de-erros.md) — a suite é o espelho sintético do trace real.
