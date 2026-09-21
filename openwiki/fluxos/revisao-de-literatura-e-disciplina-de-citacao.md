---
type: process-convention
title: Revisão de Literatura e Disciplina de Citação
description: Como literature-review/, papers/ e papers/reading-queue.md se relacionam, e a disciplina de três níveis do projeto para nunca confundir "nota existe", "agente leu texto completo" e "Rafael leu" — incluindo a restrição de usar WebSearch em vez de WebFetch para verificar arXiv.
tags: [literature-review, citation-discipline, reading-queue, bibliographic-verification, arxiv]
verified:
  - by: openwiki/0.5.1
    at: 2026-09-21T19:21:20.640Z
sources:
  - id: openwiki-source-5809f342a2c80efa4a9f4820
    resource: repo://literature-review/README.md
  - id: openwiki-source-674dfb0e25b8acca2dea113b
    resource: repo://papers/reading-queue.md
  - id: openwiki-source-31e2a9b2a16c1a37af36abb9
    resource: repo://papers/README.md
  - id: openwiki-source-84c8ba53358ba5f16899f53e
    resource: repo://papers/ssgm-2026.md
generated: { by: "claude-code", at: "2026-09-21T19:21:20.640Z" }
---

Três pastas guardam a mesma base bibliográfica em três formas diferentes, cada uma otimizada para um uso:

```
literature-review/  →  os dois relatórios prontos para entrega (prosa, organizada por tema, formato Entregável 1)
papers/              →  uma nota atômica por fonte (organizada para consulta, não leitura corrida)
papers/reading-queue.md → a fila priorizada do que ainda falta ler de verdade
```

## `literature-review/` — os relatórios prontos para entrega

Dois documentos **vivos** (não entregáveis únicos — Sub 1.1 e Sub 2.1 pedem refinamento contínuo): [`memory-in-ai-agents.md`](../../literature-review/memory-in-ai-agents.md) (Sub 1.1 — memória em agentes de IA generativa) e [`deep-agents.md`](../../literature-review/deep-agents.md) (Sub 1.2 — arquiteturas de agente de longo horizonte). Cada um segue TL;DR → Achados-chave → Detalhes por tema → Recomendações → Ressalvas, com status de revisão por pares marcado inline por fonte. Quando uma fonte nova entra numa das revisões, a mesma mudança também adiciona a nota atômica correspondente em `papers/` e atualiza seu índice — as três camadas nunca ficam dessincronizadas por muito tempo.

## `papers/` — uma nota atômica por fonte

`papers/README.md` abre afirmando "39 sources indexed below", mas a pasta já tem 41 arquivos de nota atômica nesta data (a contagem do índice ficou para trás conforme fontes novas foram adicionadas — `ssgm-2026.md`, por exemplo, existe como nota completa mas não aparece em nenhuma das tabelas do índice). Cada nota segue [`_TEMPLATE.md`](../../papers/_TEMPLATE.md): autores, ano, venue, link, tags, "Core contribution" (o que a fonte de fato afirma/faz, com citação quase-verbatim para qualquer estatística, sem editorializar) e "Relevance to the project". A maioria foi extraída fielmente das duas revisões; algumas (ExpeL, SCM, Retroformer, Mem0, MemoryBank, SAGE, SSGM, Hermes Agent, smolagents, LangChain Deep Agents, "Memory in the Age of AI Agents", Workspace-Bench) foram adicionadas depois direto de páginas arXiv/proceedings/repositório verificadas, à medida que iam sendo lidas ou citadas em notas de `discussion/`.

## `reading-queue.md` — a fila priorizada, nada lido ainda

Nomeia fontes cruzadas do corpus completo de 27 modelos do survey de Zhang et al. (Tabelas 1 e 3) que **ainda não têm nota atômica completa** — nenhum ID de arXiv, lista de autor ou link é inventado antes de ser verificado. Uma vez lida e verificada contra fonte primária, uma entrada é promovida para `papers/<slug>.md`. A fila é organizada em **tiers** (1 = alimenta uma decisão de arquitetura já em uso agora; 2 = refina um componente específico; 3 = background/contraste, menor urgência), reordenados conforme achados de leitura mudam a urgência de cada item — não é uma lista estática.

## A disciplina de três níveis — nunca colapsar

O núcleo de integridade desta parte do repositório é uma distinção que se repete deliberadamente em várias fontes: **uma nota existir em `papers/` não é o mesmo que Rafael ter lido o paper.** Toda nota atômica do repositório — incluindo as mais antigas — foi produzida verificando fatos bibliográficos (autores, venue, resumo, resultados principais) contra uma fonte primária e escrevendo um resumo a partir disso. Isso é trabalho de verificação real e útil (pega citação falsa, venue errado, título incompatível) — mas **não é** a leitura atenta que dá a Rafael autoridade para defender o material com o tutor ou tomar uma decisão de arquitetura em cima dele. Três marcadores, nunca colapsados entre si:

| Marcador | Significa | Não significa |
|---|---|---|
| 📝 | Fatos bibliográficos verificados contra fonte primária (uma nota existe) | Que alguém leu o texto |
| 🔎 | Texto completo lido por um **agente** (sem provider definido) via sub-agente, extraindo mecanismos/fórmulas/respostas específicas | Que Rafael leu — é mais forte que 📝, mas ainda não é "lido" no sentido que conta para defender uma escolha de design |
| ✅ | Rafael **efetivamente leu** | — este é o único marcador que autoriza tratar algo como "lido" num relatório ou numa defesa de design |

Nenhum item da fila de leitura é marcado como lido (☐, nenhuma caixa ainda marcada) só porque tem nota 📝 ou leitura de agente 🔎 — o checkbox só é marcado quando Rafael de fato lê.

## Como verificar sem fabricar

Nunca se fabrica um ID de arXiv, lista de autores ou data. `arxiv.org` via fetch direto (`WebFetch`) é bloqueado pelo egress de rede deste ambiente — a verificação usa `WebSearch` para confirmar título/autores/data/alegações principais, prática que tem se mostrado confiável para esse fim.

## Como se conecta ao resto do projeto

- A disciplina 📝/🔎/✅ também se aplica às notas de literatura dentro de cada pasta de análise de trace — ver [Metodologia de Análise de Traces](metodologia-de-analise-de-traces.md).
- Muitos dos componentes da [Hipótese de Arquitetura "Knowledge as Infra"](../arquitetura/hipotese-knowledge-as-infra.md) citam papers específicos desta fila como fundamento — o guia de leitura por componente, dentro de `reading-queue.md`, é um corte diferente do mesmo corpus organizado por qual paper explica qual componente da arquitetura.
- Os papers de taxonomia de erro (MAST, TRAIL, AgentDebug, ToolScan/SpecTool/ToolFailBench, Hu/Liu) que fundamentam a classificação de erros seguem a mesma disciplina de verificação e alimentam a [Metodologia de Taxonomia de Erros (Genealogia)](metodologia-de-taxonomia-de-erros.md).
