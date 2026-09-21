---
type: quickstart
title: Quickstart
description: Mapa de navegação por tarefa de pesquisa comum neste repositório — onde registrar um achado, processar uma reunião, contribuir uma leitura, entender a arquitetura proposta, ou rodar uma análise de trace e sua metodologia de taxonomia de erros.
tags: [quickstart, navigation, task-routing]
verified:
  - by: openwiki/0.5.1
    at: 2026-09-21T19:21:20.640Z
sources:
  - id: openwiki-source-593cb6afa0d403199fc28ec9
    resource: repo://.claude/skills/checkpoint-reuniao/SKILL.md
  - id: openwiki-source-54a2eb94e13cee4cde117c20
    resource: repo://.claude/skills/diario-campo/SKILL.md
  - id: openwiki-source-ca8957828e82541a58258a70
    resource: repo://.claude/skills/sintese-diario/SKILL.md
generated: { by: "claude-code", at: "2026-09-21T19:21:20.640Z" }
---

Este repositório é um laboratório de pesquisa pessoal, não um projeto de software — não há build, entrypoints ou testes para rodar. A navegação aqui é por **tarefa de pesquisa**: o que você está tentando fazer agora, e onde isso vive.

## Por tarefa

| Você quer... | Comece aqui |
|---|---|
| Entender o repositório do zero | [Visão Geral do Repositório](overview.md) |
| Registrar um achado, leitura, decisão ou observação do dia | [Diário de Campo: Convenções e Ciclo](fluxos/diario-de-campo.md) → `research-diary/README.md` |
| Processar a transcrição de uma reunião nova (tutor, infra, colega) | [Registros de Reunião e Notas de Discussão](fluxos/registros-de-reuniao-e-notas-de-discussao.md) → `docs/README.md` |
| Decidir se uma síntese vira nota permanente em `discussion/` ou fica só no diário | [Registros de Reunião e Notas de Discussão](fluxos/registros-de-reuniao-e-notas-de-discussao.md) → `discussion/README.md` |
| Adicionar ou verificar uma fonte bibliográfica nova | [Revisão de Literatura e Disciplina de Citação](fluxos/revisao-de-literatura-e-disciplina-de-citacao.md) → `papers/README.md`, `papers/reading-queue.md` |
| Entender o estado da arte revisado até agora, do início ao fim | `literature-review/README.md` |
| Entender a hipótese de arquitetura do mecanismo de memória (os seis componentes) | [Hipótese de Arquitetura "Knowledge as Infra"](arquitetura/hipotese-knowledge-as-infra.md) |
| Ver decisões de escopo/terminologia já tomadas, ou o que ainda está em aberto | [Escopo, Terminologia e Questões Abertas](arquitetura/escopo-terminologia-e-questoes-abertas.md) |
| Rodar ou entender uma análise empírica de trace bruto de agente (layout de pasta, PII, validação) | [Metodologia de Análise de Traces](fluxos/metodologia-de-analise-de-traces.md) → `analysis/README.md` |
| Entender como um erro bruto vira uma unidade de memória candidata (a genealogia sintoma → mecanismo → unidade → destino) | [Metodologia de Taxonomia de Erros (Genealogia)](fluxos/metodologia-de-taxonomia-de-erros.md) |
| Ver o Plano de Trabalho oficial, prazos e sub-atividades | [Plano de Trabalho e Macroatividades](referencia/plano-de-trabalho.md) |

## Convenções que atravessam quase toda tarefa

- **Idioma:** artefatos oficiais/pessoais (Plano de Trabalho, diário, resumos de reunião) ficam em português verbatim; material de conexão (READMEs, `discussion/`, notas de paper) usa inglês por padrão — ver [Visão Geral do Repositório](overview.md#convenção-de-idioma).
- **Verificação bibliográfica:** nunca confundir "nota existe" (📝), "lido por agente" (🔎) e "Rafael leu" (✅) — ver [Revisão de Literatura e Disciplina de Citação](fluxos/revisao-de-literatura-e-disciplina-de-citacao.md).
- **Dados sensíveis:** traces brutos e CSVs derivados de análises (`analysis/*/resultados/`, `analysis/*/data/`) são sempre git-ignored — nunca versionados em claro. Ver [Metodologia de Análise de Traces](fluxos/metodologia-de-analise-de-traces.md).
- **Estrutura de `discussion/`:** hoje organizada por subtema — `hipoteses/` (arquiteturas e políticas ainda hipotéticas), `teoria/` (comparações contra a literatura), `reflexoes/` (notas de reunião) — ver [Registros de Reunião e Notas de Discussão](fluxos/registros-de-reuniao-e-notas-de-discussao.md#quando-algo-vira-uma-nota-permanente-em-discussion).

## Skills do projeto que automatizam parte destes fluxos

Este repositório tem skills dedicadas (fora do escopo desta wiki, mas vale saber que existem) para automatizar partes destes fluxos quando usadas via Claude Code: `diario-campo` (registrar/consultar o diário), `sintese-diario` (gerar o digest mensal), e `checkpoint-reuniao` (processar uma transcrição de reunião nova seguindo o padrão de registro descrito em [Registros de Reunião e Notas de Discussão](fluxos/registros-de-reuniao-e-notas-de-discussao.md)).
