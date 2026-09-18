---
type: reference
title: Plano de Trabalho e Macroatividades
description: O Plano de Trabalho oficial do bolsista — as cinco macroatividades, sub-atividades e entregáveis, os prazos, e como o mapa de sub-atividades amarra as entradas do diário de campo de volta a este plano.
tags: [work-plan, macroatividades, sub-atividades, deliverables, fellowship-project]
verified:
  - by: openwiki/0.5.1
    at: 2026-09-18T11:27:06.172Z
sources:
  - id: openwiki-source-7511ca81756684a871195f29
    resource: repo://docs/sub-activity-map.md
  - id: openwiki-source-772c65043efca65313937108
    resource: repo://docs/work-plan.md
generated: { by: "claude-code", at: "2026-09-18T11:27:06.172Z" }
---

O [`docs/work-plan.md`](../../docs/work-plan.md) é o Plano de Trabalho do Bolsista oficial do programa [PROGRAMA-FOMENTO], mantido **verbatim em português**, fonte de verdade da qual todo o resto do repositório deriva sua estrutura de tags e prazos. Fonte original: [`docs/sources/Plano_de_Trabalho_Rafael_Ventura.docx`](../../docs/sources/Plano_de_Trabalho_Rafael_Ventura.docx).

**Programa:** [PROGRAMA-FOMENTO] · **Razão Social:** [INSTITUIÇÃO-FOMENTO] · **Nº do Projeto:** [ANONIMIZADO] · **Bolsista:** Rafael Coelho Ventura · **Tutor:** [TUTOR] · **Início:** 07/08/2026 · **Término:** 31/07/2027

## As cinco macroatividades

| # | Macroatividade | Prazo | Entregável |
|---|---|---|---|
| 1 | Fundamentação teórica e exploração prática comparativa de abordagens de memória em agentes de IA | 30/10/2026 | Relatório de revisão bibliográfica e mapeamento de técnicas + especificação preliminar dos sinais de feedback + relatório comparativo entre abordagens de memória, com POCs mínimas |
| 2 | Design da arquitetura, POCs e validação local do mecanismo | 31/12/2026 | Documento de arquitetura técnica + protótipo conceitual documentado e testado localmente + mapeamento dos pontos de integração com a plataforma de agentes do [INTERESSADO] |
| 3 | Desenvolvimento e implantação do mecanismo de atualização de memória | 31/03/2027 | Mecanismo implantado em dev/homologação/produção + métricas de desempenho + relatório técnico + resultados de testes unitários/integração + desenho do teste A/B e público beta |
| 4 | Validação, métricas de desempenho e piloto em ambiente real | 31/05/2027 | Relatório de resultados do piloto com métricas consolidadas + registro dos ajustes realizados |
| 5 | Consolidação da funcionalidade, documentação técnica e entrega final | 31/07/2027 | Funcionalidade integrada à plataforma do [INTERESSADO] + documentação técnica completa + relatório final |

**Nota de datação interna, não no Plano formal:** o mapa de sub-atividades do projeto ([`docs/sub-activity-map.md`](../../docs/sub-activity-map.md)) registra que, embora o Plano formal date o fim da Macroatividade 1 em 30/10/2026, o bolsista trabalha internamente com 30/11/2026 como prazo de fato.

## Sub-atividades da Macroatividade 1 (em andamento)

A Macroatividade 1 é a que está ativa no momento e organiza a maior parte do trabalho documentado no restante do repositório:

| Sub | Descrição |
|---|---|
| 1.1 | Revisão bibliográfica inicial sobre memória em agentes de IA generativa (curto/longo prazo, episódica x semântica), com refinamento contínuo |
| 1.2 | Estudo teórico de arquiteturas de "deep agents" — loop de aprendizado nativo, planejamento explícito, memória persistente entre sessões |
| 1.3 | Levantamento de técnicas de aprendizado por reforço aplicáveis à atualização de memória (RLHF, RLAIF, bandits contextuais) |
| 1.4 | Mapeamento dos fluxos jurídicos alvo do projeto e identificação dos pontos de coleta de sinal de desempenho |
| 1.5 | Definição preliminar dos critérios de "acerto/erro" como sinal de atualização |
| 1.6 | Construção de agentes mínimos representando abordagens distintas: (a) loop de aprendizado fechado nativo com conversão automática de sessões em regras/skills; (b) memória transparente com controle programático explícito do log |
| 1.7 | Análise comparativa entre aprendizado implícito e sinal de feedback explícito (certo/errado) — prós, contras e riscos para fluxos jurídicos |

## O mapa de sub-atividades — como o diário se amarra ao plano

[`docs/sub-activity-map.md`](../../docs/sub-activity-map.md) é uma tabela de referência derivada do Plano de Trabalho, mantida em português por usar a mesma nomenclatura, e serve um único propósito: classificar o campo **Sub-atividade** de cada entrada do [diário de campo](../fluxos/diario-de-campo.md). Cada sub-atividade das cinco macroatividades tem uma lista de "sinais" (palavras-chave) que orientam essa classificação — por exemplo, a Sub 1.6 é sinalizada por termos como "POC de agente", "Hermes", "smolagents", "agente mínimo".

Três categorias adicionais, fora da lista formal do Plano, existem para uso deliberado no diário:

- **`transversal`** — gestão do projeto, ferramentas, reuniões que não mapeiam 1:1 a uma sub-atividade.
- **`governança`** — registros sobre a distinção coordenador informal vs. tutor formal, ou sobre validação de mudança de escopo.
- **`não classificado (confirmar)`** — usado quando a classificação automática não tem confiança suficiente; revisão manual pendente.

## Como se conecta ao resto do projeto

- Toda entrada do [diário de campo](../fluxos/diario-de-campo.md) é tagueada contra este plano via o mapa de sub-atividades.
- A [Hipótese de Arquitetura "Knowledge as Infra"](../arquitetura/hipotese-knowledge-as-infra.md) é rotulada explicitamente como pré-Sub-2.2 — só vira a arquitetura formal da Sub 2.2 depois que os POCs das Subs 1.6/1.7 a testarem contra comportamento real.
- Vários itens em [Escopo, Terminologia e Questões Abertas](../arquitetura/escopo-terminologia-e-questoes-abertas.md) estão formalmente bloqueados por sub-atividades específicas deste plano (ex.: a métrica Reference Accuracy da Sub 3.6, bloqueada pelas Subs 1.4 e 1.5).
