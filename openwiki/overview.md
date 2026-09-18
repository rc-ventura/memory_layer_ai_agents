---
type: overview
title: Visão Geral do Repositório
description: O que este repositório é (o laboratório de pesquisa do projeto de bolsa de Rafael Coelho Ventura), a quem serve, e como suas seis pastas de conteúdo se relacionam em altitudes diferentes sobre o mesmo material.
tags: [overview, research-repository, fellowship-project, repository-structure]
verified:
  - by: openwiki/0.5.1
    at: 2026-09-18T11:27:06.172Z
sources:
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
generated: { by: "claude-code", at: "2026-09-18T11:27:06.172Z" }
---

Este é o repositório de pesquisa **pessoal** de Rafael Coelho Ventura para o projeto de bolsa [PROGRAMA-FOMENTO] ([INSTITUIÇÃO-FOMENTO], Nº [ANONIMIZADO]):

> **Mecanismo de atualização de memória para agentes de IA generativa com aprendizado por reforço aplicado a fluxos jurídicos**

O projeto constrói e valida um mecanismo de atualização de memória para agentes de IA generativa em fluxos jurídicos — usando sinais de desempenho (revisão humana, feedback da área usuária) para ajustar, de forma controlada, as instruções/exemplos/contexto operacional armazenados na memória de um agente. Bolsista: Rafael Coelho Ventura. Tutor: [TUTOR]. Vigência: agosto/2026 a julho/2027. Detalhes completos no [Plano de Trabalho](referencia/plano-de-trabalho.md).

**Este não é um repositório de software de produção.** É o caderno de laboratório do próprio trabalho: revisão bibliográfica, notas por fonte, síntese cross-cutting, um diário de pesquisa diário, e análises empíricas de traces reais de agentes — tudo versionado junto em vez de espalhado por documentos separados.

## As seis pastas de conteúdo

```
docs/                   Plano de Trabalho oficial, mapa de sub-atividades, registros de reunião (checkpoints/), relatórios mensais à instituição (reports/)
literature-review/      As duas revisões bibliográficas de nível relatório (Sub 1.1, Sub 1.2) + dois mapas mentais de survey
papers/                 Uma nota atômica por paper/framework citado + uma fila de leitura priorizada
discussion/             Síntese cross-cutting: achados, comparações de framework, decisões de escopo, questões abertas
research-diary/         Log episódico diário (um arquivo por semana, em pastas por mês) + digest mensal
analysis/               Análises empíricas de traces brutos de agentes (notebooks executados + relatórios de achados; dados derivados git-ignored)
```

Cada pasta tem seu próprio `README.md` com mais detalhe.

## Como as peças se relacionam — quatro altitudes sobre o mesmo material

```
literature-review/  →  entregáveis de nível relatório, prosa, organizados por tema (o que é submetido)
papers/               →  uma nota atômica por fonte, organizada para consulta (o que é citado)
discussion/           →  síntese entre fontes/revisões/diário (o que é decidido)
research-diary/       →  log episódico cru + digest mensal (o que de fato aconteceu, dia a dia)
```

O diário é onde achados novos pousam primeiro; os mais fortes são destilados em `discussion/`; fontes citadas ao longo do caminho ganham uma nota atômica em `papers/`; e os dois relatórios de `literature-review/` são a forma polida e submissível de Sub 1.1 e Sub 1.2 — refinados continuamente, não escritos uma vez só. `analysis/` soma uma quinta dimensão, empírica: em vez de sintetizar literatura, ela constrói uma ponte entre o comportamento real de agentes em produção e as mesmas perguntas de arquitetura de memória que as outras quatro pastas discutem em nível conceitual.

## A quem serve, e por quê essa estrutura

O README raiz nomeia três audiências que cada entrada do diário serve ao mesmo tempo, sem edição extra: a própria memória de trabalho de Rafael, o acompanhamento do coordenador do projeto, e a rastreabilidade formal contra os Entregáveis do Plano de Trabalho. Essa mesma lógica de "uma escrita, múltiplos leitores auditáveis" se repete na separação entre `docs/checkpoints/` (resumo factual em português) e `discussion/` (reflexão analítica em inglês) para registros de reunião — ver [Registros de Reunião e Notas de Discussão](fluxos/registros-de-reuniao-e-notas-de-discussao.md).

## Convenção de idioma

Documentos que são artefatos oficiais ou pessoais (o Plano de Trabalho, o diário de campo, resumos de reunião derivados de uma fonte específica) ficam verbatim no português original. Tudo que é escrito para *conectar* esses artefatos — este README, os READMEs de pasta, notas de discussão, o scaffolding das notas de paper — usa inglês por padrão, casando com o idioma em que as duas revisões bibliográficas foram escritas. Notas individuais de `discussion/` podem ser em português por pedido explícito de Rafael — uma exceção por arquivo, não uma mudança de convenção de pasta inteira.

## Status

A Macroatividade 1 (fundamentação teórica + exploração prática comparativa de abordagens de memória) está em andamento, com prazo 30/10/2026. Ver o [Plano de Trabalho](referencia/plano-de-trabalho.md) para as cinco macroatividades e seus entregáveis.

## Por onde começar

- Quer o estado da arte, do início ao fim? → `literature-review/`
- Está procurando um paper específico? → `papers/README.md` (tabela indexada)
- Quer o "porquê", as decisões, as lacunas encontradas? → [Escopo, Terminologia e Questões Abertas](arquitetura/escopo-terminologia-e-questoes-abertas.md) e a [Hipótese de Arquitetura](arquitetura/hipotese-knowledge-as-infra.md)
- Quer saber o que aconteceu esta semana? → [Diário de Campo](fluxos/diario-de-campo.md)
- Quer o plano de trabalho ou um registro de reunião? → [Plano de Trabalho](referencia/plano-de-trabalho.md) e [Registros de Reunião](fluxos/registros-de-reuniao-e-notas-de-discussao.md)
- Quer entender a evidência empírica por trás da arquitetura? → [Metodologia de Análise de Traces](fluxos/metodologia-de-analise-de-traces.md)
