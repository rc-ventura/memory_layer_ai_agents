---
type: process-convention
title: "Diário de Campo: Convenções e Ciclo"
description: Como o diário de campo pessoal do projeto está estruturado — duas camadas (episódica/semântica), convenções de arquivo semanal por mês, o schema obrigatório de entrada, a convenção de atribuição a agentes de IA e o ciclo de digest mensal e fechamento.
tags: [research-diary, process-convention, episodic-memory, semantic-memory, provider-agnostic-attribution]
verified:
  - by: openwiki/0.5.1
    at: 2026-09-18T11:27:06.172Z
sources:
  - id: openwiki-source-3ebb84af95de1901cf00d880
    resource: repo://research-diary/Ago/diario_campo_2026-08-24.md
  - id: openwiki-source-25fde8545a4952aa4cbe56e5
    resource: repo://research-diary/README.md
generated: { by: "claude-code", at: "2026-09-18T11:27:06.172Z" }
---

O diário de campo (`research-diary/`) é o registro pessoal de pesquisa de Rafael para o projeto — leituras, testes, decisões, reuniões. Fica em português, como prática contínua (não um documento único), e serve três audiências ao mesmo tempo sem edição extra: a memória de trabalho do próprio Rafael, o acompanhamento do coordenador do projeto (lê o arquivo cru, sem processamento) e a rastreabilidade formal contra os Entregáveis do [Plano de Trabalho](../referencia/plano-de-trabalho.md) (cada entrada é tagueada por sub-atividade).

## Desenho: duas camadas, deliberadamente inspirado na própria teoria do projeto

O diário é estruturado como uma aplicação em miniatura da mesma teoria de memória que o projeto estuda: uma camada **episódica** (entradas diárias cruas, baratas de escrever) e uma camada **semântica** (síntese periódica destilada, mais cara, de maior valor de releitura). As duas são funcionalmente distintas — a camada episódica nunca é reescrita ou resumida no lugar; a semântica é derivada, e pode ser regenerada se o entendimento mudar. Não é decorativo: é a mesma separação que o Plano de Trabalho propõe para a memória do próprio agente (Sub 2.2), aplicada à prática de pesquisa do bolsista.

## Convenção de arquivo

**Um arquivo por semana**, a partir de 24/08/2026: `diario_campo_AAAA-MM-DD.md`, onde `AAAA-MM-DD` é a segunda-feira que abre a semana. **A semana do diário roda de segunda a sexta** (5 dias úteis) — sábado e domingo não fazem parte dela. Um arquivo novo começa cada semana com um cabeçalho padrão (nome do projeto, número do projeto, descrição de uma linha do esquema, e o intervalo de datas da semana) — ver o cabeçalho do exemplo em [`research-diary/Ago/diario_campo_2026-08-24.md`](../../research-diary/Ago/diario_campo_2026-08-24.md). O arquivo semanal é a semana, e guarda **só** entradas episódicas — a reflexão destilada da semana vive no digest mensal, não no rodapé do arquivo semanal.

**Pastas por mês (a partir de 09/2026).** Arquivos semanais são agrupados numa pasta por mês, nomeada com a abreviação de três letras do português, title case (`Ago`, `Set`, `Out`, ...). Assim: `research-diary/Ago/diario_campo_2026-08-24.md`, `research-diary/Set/diario_campo_2026-09-07.md`.

**A regra da quarta-feira — qual pasta de mês uma semana pertence.** Uma semana segunda–sexta pertence ao mês que contém sua **quarta-feira** (equivalente a dizer: o mês que detém a maioria dos 5 dias úteis). Uma semana que atravessa uma virada de mês vai para o mês que detém ≥3 de seus dias. O **nome do arquivo mantém a segunda-feira de abertura**, mesmo quando a pasta é de outro mês — nome = a segunda-feira, pasta = o mês ao qual a semana pertence.

**Antes de 24/08/2026:** um arquivo por mês calendário (`diario_campo_AAAA-MM.md`), com sínteses semanais inseridas em cada virada de semana dentro do próprio arquivo. Só `diario_campo_2026-08.md` segue essa convenção mais antiga — fica na sua pasta de mês (`Ago/`), permanece como está (síntese embutida), e nunca é retroativamente dividido.

## Schema de entrada

Cada entrada é um bloco `##` por data (`###` para uma segunda ou posterior entrada no mesmo dia). Campos obrigatórios:

- **Tipo** — `leitura | teste/POC | implementação | reunião | decisão | achado | observação livre`
- **Sub-atividade** — tagueada contra [`docs/sub-activity-map.md`](../../docs/sub-activity-map.md); cai para `transversal` ou `não classificado (confirmar)` quando não se encaixa
- **Canal** — `pessoal | informal-coordenador | formal-tutor` — mantém a orientação informal do coordenador separada do aval formal do tutor
- **Registro objetivo** — o fato em si, o componente episódico

Campos opcionais (só quando há conteúdo real): **Reflexão** (interpretação subjetiva, hipótese, ressalva), **Decisão/próximo passo**, **Tags** (livre, minúsculas, separadas por vírgula). Um exemplo real do schema completo em uso está na entrada de 24/08/2026 sobre o survey Hu/Liu, em [`research-diary/Ago/diario_campo_2026-08-24.md`](../../research-diary/Ago/diario_campo_2026-08-24.md).

## Convenção de atribuição provider-agnostic

Quando uma entrada (ou um registro do digest) afirma que um **agente de IA** fez algo em vez do próprio Rafael — leu um paper, rodou um sprint de leitura, ajudou a desenhar um esquema — a referência é **genérica**: "um agente (sem provider definido)", "lido por agente, não lido pelo Rafael". Nunca se nomeia o assistente, modelo ou provedor. O que a nota carrega é a marca *não-é-trabalho-do-próprio-Rafael*; qual ferramenta produziu isso não é o ponto e data o registro. Menções tópicas a produtos de IA como **assunto** (uma nota de paper sobre um sistema específico, um fato de tooling/quota de uma reunião) mantêm seus nomes — a convenção só vale para atribuição de trabalho feito para o diário.

## O digest mensal (`summarization/`)

A camada semântica é **um arquivo por mês**: `summarization/<Mês>/sintese_AAAA-MM.md`, guardando **até 4 registros — um por semana**. Cada registro é a reflexão daquela semana, tirada das entradas episódicas da semana e só *organizada* ali (a interpretação já foi feita nas próprias entradas). Formato por registro: um cabeçalho `### Semana N · DD–DD/MM/AAAA · N registros`, um parágrafo curto do que aconteceu, depois linhas `**Decidido:**` e `**Em aberto:**`. É deliberadamente curto — feito para ser lido rápido, semana a semana. Uma entrada logada num sábado ou domingo ainda pertence à semana que acabou de fechar na sexta; não abre uma nova. O digest é derivado e regenerável — seguro de reconstruir a qualquer momento que o entendimento de uma semana passada mude. Gerado e atualizado pela skill `sintese-diario`.

## Fechamento mensal

No início de um novo mês calendário (ou sob pedido), uma vez que o digest mensal contenha todas as semanas do mês que está fechando: exporta-se um `.docx` limpo para o coordenador — capa (mês/ano, número do projeto, contagem de entradas) + os registros semanais do digest, em ordem, como corpo principal + o log episódico completo (dos arquivos semanais daquele mês) como apêndice.

## Como se conecta ao resto do projeto

- Toda entrada é tagueada contra o [Plano de Trabalho](../referencia/plano-de-trabalho.md) via `docs/sub-activity-map.md`.
- Achados e decisões fortes o bastante para serem citados de novo, não só relidos cronologicamente, são destilados para uma nota permanente em `discussion/` — ver [Registros de Reunião e Notas de Discussão](registros-de-reuniao-e-notas-de-discussao.md) para o critério exato de quando isso acontece.
- A cadência de síntese semanal ainda está sendo testada sob uso real prolongado — ver [Escopo, Terminologia e Questões Abertas](../arquitetura/escopo-terminologia-e-questoes-abertas.md) para esse e outros itens em aberto.
