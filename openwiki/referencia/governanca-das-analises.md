---
type: governance-reference
title: "Governança das Análises: Roadmaps, Decisões e Glossário"
description: A camada de governança que organiza o trabalho empírico em analysis/ — o schema de roadmaps por base e transversal, o índice de decisões em vigor, o glossário único de códigos e os registros JSON lidos por scripts.
tags: [governance, roadmap-schema, decisions, glossary, registries, analysis-workflow]
verified:
  - by: openwiki/0.6.0
    at: 2026-10-09T17:09:54.387Z
sources:
  - id: openwiki-source-b1f655aa6d87090fc6d82043
    resource: repo://analysis/decisoes.md
  - id: openwiki-source-afeb1c5ba90e2da2476aeaf0
    resource: repo://analysis/glossario.md
  - id: openwiki-source-295082e85eb115be41963847
    resource: repo://analysis/plano-atual.md
  - id: openwiki-source-c4fb8acd94b51651383c6dea
    resource: repo://analysis/registros/esquema-memoria.json
  - id: openwiki-source-eb3a346108886797f62f7271
    resource: repo://analysis/registros/README.md
  - id: openwiki-source-7c2d1833faef47d99e8e11da
    resource: repo://analysis/roadmap-transversal.md
generated: { by: "claude-code", at: "2026-10-09T17:09:54.387Z" }
---

Desde a reorganização de 09/10/2026, "o que fazer" nas análises não mora mais num plano único que cresce — vive numa **camada de governança** de arquivos com papéis separados. A divisão de trabalho é explícita e cada arquivo cobre um pedaço só:

| Arquivo | O que diz | O que **não** diz |
|---|---|---|
| `docs/04-roadmap.md` de cada pasta + `roadmap-transversal.md` | **o quê** fazer e o que foi feito | porquê, números, histórico |
| `docs/NN-racionais-*.md` | o **porquê** de cada mineração | o backlog |
| `docs/NN-relatorio-*.md` | os **números** | a fila |
| `pipeline-entre-bases.md` | o **histórico** de cada ajuste do método (o livro-razão) | o que falta |
| `decisoes.md` | as decisões **em vigor** (para não rediscutir) | o que fazer agora |
| `glossario.md` | o que cada **código** quer dizer | — |
| `registros/*.json` | os dados lidos **por script**, comuns a todas as bases | — |
| `plano-atual.md` | o **schema** que tudo isso segue + o de-para do plano antigo | a lista em si |

## `plano-atual.md` — o schema, não mais a lista

Desde 09/10/2026 o arquivo **não é mais uma lista do que fazer** (a versão de 298 linhas está preservada em `git show e0335aa:analysis/plano-atual.md`). Ele define três coisas:

1. **Onde mora cada roadmap** — `docs/04-roadmap.md` dentro de cada pasta de análise (base 1, base 2, base 3) mais `roadmap-transversal.md` para o que atravessa bases. De fora, os itens se citam com prefixo: `b1 #N`, `b2 #N`, `b3 #N`, `transversal #N`; um "roadmap #N" sem prefixo em documento anterior a 09/10 é o da base 1.
2. **O schema** que todo `04-roadmap.md` segue — seções `Backlog`, `Monitoramento` (opcional), `Fora de escopo / adiado` (opcional) e `Fechado`, com sete regras:
   - checkbox (`[x]` feito, `[ ]` não feito — nada de riscado);
   - **`[x]` exige prova** escrita na linha (commit, ajuste do livro-razão ou documento);
   - o item marcado desce para `Fechado` com o **mesmo número e o texto original**;
   - **números estáveis, nunca renumerados nem apagados**, por pasta;
   - cada item cabe numa frase e aponta para onde está o contexto;
   - **um item mora num roadmap só** — se vale para mais de uma base, vai para o transversal e as bases apontam para ele;
   - cabeçalho (data e branch) atualizado a cada mudança.
3. **O de-para** do plano antigo — para cada item dos §1–§5 antigos, onde ele está agora.

`roadmap-transversal.md` é a instância desse schema para o que não pertence a uma base só — método, kit, skills, medidas transversais, o que vai à plataforma — e carrega a **tabela de referência** de onde cada mineração vive em documentos (racional/procedimento/relatório/skill para silenciosas, protocolo, candidatas, resíduo, erro crítico).

## `decisoes.md` — o índice do já decidido

Uma página com as decisões que valem para todas as análises — regras de trabalho, organização do método, destinos decididos por achado e decisões de método por data — cada uma numa linha com o link para o porquê. A regra de escrita: decisão nova entra no fim da seção da data; **decisão revogada nunca é apagada** — ganha "revogada em `<data>` por `<link>`".

As regras de trabalho registradas lá incluem:

- **uma solução por vez** — contexto, solução, argumento com evidência; espera aprovação; verifica na base 1; diz o que rodar na máquina 2;
- **regra nova só olhando as duas bases** (Ajuste 7);
- **leitura por LLM é `[assistido]`** e vale como hipótese; o determinístico é `[conferido]` — nenhum LLM no caminho da classificação;
- **fronteira da máquina de compliance**: da máquina 2 só saem contagens, nomes de papel/ferramenta/modelo, hashes, sim/não, tamanhos, tokens e motivos mascarados — nunca texto de caso nem `exec_id`.

## `glossario.md` — uma definição por código

Os documentos de análise usam códigos curtos para caber em tabelas e manter o histórico legível — e o glossário é a fonte única do que cada um significa: todo documento que usa códigos aponta para ele no topo, e **código novo entra no glossário no mesmo commit em que aparece**.

- **Prefixos de unidade** — dizem **quem corrige**: `U_` = o agente (candidata a memória), `H_` = harness/plataforma (não é memória), `X_` = resíduo sem regra (revisar), `C_` = erro crítico (a execução morreu);
- **Os dois baldes e a consolidação** — visível (exceção) × invisível (falha devolvida como texto), canal, ocorrência = cascata × unidade, `REGRAS_INVISIVEL`;
- **M1–M6** — os mecanismos da família `H_bloco_code` (protocolo do harness);
- **[1]–[4]** — as medidas do balde invisível, onde **[4]** é sempre **teto** (candidato a sucesso falso — inclui tudo que *pode* ser o fenômeno; o real é menor ou igual);
- **S1–S6 / D2 / números de plano** — os itens do plano antigo citados no histórico;
- **grau de certeza** — `[conferido]` (verificado de forma determinística) × `[assistido]` (leitura por LLM, hipótese nunca fato), `teto`, base/máquina.

## `registros/` — os JSONs que os scripts leem

Dois arquivos versionados, sem dado de caso (só decisões, regras, contagens e estrutura), comuns a todas as bases — um registro novo lido por script entra aqui, com uma linha na tabela do README:

- **`monitoramento.json`** — o que o pesquisador decidiu monitorar entre as bases: linha de base, regras de contagem e gatilhos de reabertura. Lido pelo `monitorar.py` do kit, no passo 0 de toda rodada de mineração — alerta disparado, a lição volta ao gate do pesquisador antes de minerar;
- **`esquema-memoria.json`** — a estrutura do arquivo final de uma memória (provisória por declaração, versão carimbada; para mudar a estrutura, muda-se só este arquivo e registra-se no livro-razão). Lido pelo `validar_memoria.py` da mineração de candidatas e pelo `mineracao_observada.py` da base 3 — entra no hash do código da rodada.

## Como se conecta ao resto do projeto

- Os roadmaps apontam para as análises descritas em [Análises Multi-Base](../fluxos/analises-multi-base.md) e os registros são consumidos pelo [Kit de Mineração de Traces](../fluxos/kit-de-mineracao.md) (`monitorar.py` no passo 0, `validar_memoria.py` na candidata).
- Os códigos do glossário são o vocabulário da [Metodologia de Taxonomia de Erros](../fluxos/metodologia-de-taxonomia-de-erros.md) e a disciplina `[conferido]`/`[assistido]` é a mesma da [Metodologia de Análise de Traces](../fluxos/metodologia-de-analise-de-traces.md).
