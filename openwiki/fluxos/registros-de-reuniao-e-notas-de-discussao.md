---
type: process-convention
title: Registros de Reunião e Notas de Discussão
description: O padrão de quatro passos para transformar uma reunião transcrita num registro do repositório (transcrição → checkpoint factual → reflexões em discussion/ → fechamento no diário), e o critério de quando uma síntese vira uma nota permanente em discussion/ em vez de ficar só no campo Reflexão do diário.
tags: [meeting-record-pattern, discussion-notes, process-convention, language-convention]
verified:
  - by: openwiki/0.5.1
    at: 2026-09-18T11:27:06.172Z
sources:
  - id: openwiki-source-b722e400a021a974a539908e
    resource: repo://discussion/checkpoint-2026-08-20-reflections.md
  - id: openwiki-source-cbc389a6440fea38fae5198f
    resource: repo://discussion/README.md
  - id: openwiki-source-2644ca6047be181485e4d0ee
    resource: repo://docs/checkpoints/checkpoint-2026-08-20-tutor-kickoff.md
  - id: openwiki-source-196170e31ff8ec60a116165b
    resource: repo://docs/README.md
generated: { by: "claude-code", at: "2026-09-18T11:27:06.172Z" }
---

Duas convenções deste repositório trabalham juntas para transformar conversas efêmeras (reuniões, sínteses cruzadas) em registro permanente e citável: o **padrão de registro de reunião** (`docs/`) e o critério de **quando algo vira uma nota de discussão** (`discussion/`).

## O padrão de registro de reunião

Quando uma reunião nova (tutor, infra, colega) é transcrita e precisa entrar no repositório, o padrão tem quatro passos, estabelecido pelo checkpoint do tutor de 20/08:

1. **Transcrição-fonte → `docs/sources/<slug>.docx`** (ou formato original), intocada.
2. **Resumo factual → `docs/checkpoints/<slug>.md`**, em português, sem análise — só o que foi dito/mostrado. Ver [`docs/checkpoints/checkpoint-2026-08-20-tutor-kickoff.md`](../../docs/checkpoints/checkpoint-2026-08-20-tutor-kickoff.md) como exemplo: descreve o fluxo jurídico da "esteira" explicado pelo tutor, em prosa factual, sem interpretação.
3. **Reflexões cross-cutting → uma nota em `discussion/<slug>-reflections.md`**, em inglês por padrão — conectando a reunião ao plano de trabalho, decisões já existentes e questões abertas, e atualizando esses arquivos com backlinks.
4. **Fechar o loop no [diário de campo](diario-de-campo.md):** se uma entrada anterior sinalizou a reunião/transcrição como pendente, atualizar essa entrada em vez de só adicionar uma nova.

O par [`docs/checkpoints/checkpoint-2026-08-20-tutor-kickoff.md`](../../docs/checkpoints/checkpoint-2026-08-20-tutor-kickoff.md) (factual, português) e [`discussion/checkpoint-2026-08-20-reflections.md`](../../discussion/checkpoint-2026-08-20-reflections.md) (analítico, inglês) demonstra a divisão de trabalho na prática: o checkpoint registra a citação exata do tutor sobre "corrigir a memória... não retreinando"; a nota de reflexões usa essa mesma citação como a fonte primária citável para a decisão de escopo #2 registrada em [Escopo, Terminologia e Questões Abertas](../arquitetura/escopo-terminologia-e-questoes-abertas.md), e abre dois itens novos na lista de questões abertas a partir do que a reunião revelou.

## Quando algo vira uma nota permanente em `discussion/`

O critério que separa o que fica só no campo **Reflexão** de uma entrada do diário do que vira um arquivo próprio em `discussion/`:

- **Fica no diário:** uma reflexão amarrada a um dia específico, não pensada para ser encontrada ou citada de novo depois.
- **Vira um arquivo aqui:** faz referência cruzada a múltiplas fontes, produz uma decisão ou uma questão nova em aberto, ou outros documentos vão precisar linkar para ela. Ao adicionar uma nota por esse motivo, o mesmo commit também deve atualizar o que ela resolve ou corrobora (`open-questions.md`, `scope-and-terminology-decisions.md`, a entrada de decisão relevante) e adicioná-la à tabela-índice de `discussion/README.md` — nunca deixar o loop meio-fechado.

Uma nota nova em `discussion/` geralmente remonta a algo já registrado no diário ou já alegado numa revisão de literatura — a pasta serve para **conectar pontos**, não para introduzir alegações novas não verificadas.

## Regra de idioma — a exceção não é a regra

`discussion/` é **inglês por padrão**, para manter consistência entre os cross-links da pasta. Uma nota específica só fica em português **por pedido explícito** de Rafael, nota a nota — é uma exceção de arquivo individual, não uma mudança de convenção da pasta inteira. Isso é diferente de `docs/checkpoints/`, onde os resumos factuais de reunião ficam sempre em português, casando com o idioma da fonte (a transcrição da reunião). Não confundir as duas regras: `docs/checkpoints/` é português por padrão (idioma da fonte); `discussion/` é inglês por padrão, com português como exceção pontual.

## Reuniões registradas até agora

`docs/checkpoints/` contém, nesta data, os checkpoints de 20/08 (tutor, kickoff), 21/08 (infra, arquitetura) e 28/08 (tutor). Cada um tem sua nota de reflexões correspondente em `discussion/`.

## Como se conecta ao resto do projeto

- As reflexões produzidas aqui alimentam diretamente o log de decisões e a lista de questões abertas em [Escopo, Terminologia e Questões Abertas](../arquitetura/escopo-terminologia-e-questoes-abertas.md).
- O fechamento de loop no passo 4 depende das convenções descritas em [Diário de Campo: Convenções e Ciclo](diario-de-campo.md).
