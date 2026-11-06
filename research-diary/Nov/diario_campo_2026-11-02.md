# Diário de Campo — Rafael Coelho Ventura

## Semana de 02/11 a 06/11/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 03/11/2026

**Tipo:** implementação — **Sub-atividade:** transversal / 2.6 — **Canal:** pessoal

**Registro objetivo:** Comecei a montar os diagramas da apresentação "Do erro à memória: o quê 30 mil erros estão me ensinando", para o gestor/tutor do Itaú, em draw.io editável. Subi ao repositório (`docs/sources/draw.io/`), com o PNG de cada um, os diagramas de: como erros diferentes viram a mesma lição, o que fazer com 30 mil erros, a genealogia (e um exemplo dela), sinal de harness, harness/infra, erro crítico, resíduo, como investigamos, como revisamos uma lição, o estudo de caso do sandbox, um exemplo de caso de uso e "retorno pode chegar como string". Os textos e os números dos diagramas foram conferidos com a ajuda de um agente (sem provider definido) contra o pipeline e a rodada `99e032ad` da base 3.

**Reflexão:** Cada destino da taxonomia ganhou um slide de definição: sinal de harness (decidido na investigação), harness/infra (decidido na classificação), resíduo (nenhuma regra explica; pendente é regra que existe sem o dado), crítico (desfecho, não causa). Manter os números fora dos slides de definição evita que eles envelheçam quando a rodada mudar.

**Tags:** apresentacao, draw-io, taxonomia, destinos, sinal-de-harness, harness-infra, residuo, critico, sub-2.6

### 03/11/2026

**Tipo:** achado — **Sub-atividade:** 2.2 / 2.6 — **Canal:** formal-tutor

**Registro objetivo:** O tutor disse que a causa B do exemplo da unidade "Retorno das ferramentas de documento é dict" não parecia ter a lição correta. Conferi na base 1: os 7 erros da causa B usam `result` e têm um `[0]` a mais (`docs["result"][0][0]`), e 6 dos 7 vêm logo depois de um erro da causa A na mesma execução. A lição do código ("acessar `r['result'][0]` …; nunca `r[0]`, nunca iterar o dict") fala do erro da causa A, mas não do `[0]` a mais.

**Reflexão:** O tutor tinha razão sobre a redação: a unidade junta as duas causas, mas a lição só ensinava a evitar uma delas. A unidade continua certa; a frase é que precisava cobrir as duas.

**Decisão/próximo passo:** A lição passa a ser "Ferramentas de documento retornam `{'result': [[...]]}`: use `r['result'][0]`, que é a lista de documentos; `r['result'][0][0]` é um documento só", e os slides já seguem essa redação. No pipeline, entrou como item **#60 (URGENTE)** do roadmap da base 3: alinhar o `UNI` e a `correction_guidance`, nas bases 1 e 3, e registrar no livro-razão. Mudar o `base_pipeline.py` exige uma rodada nova na base 3.

**Tags:** tutor, contrato-dict, causa-b, licao, b3-60, sub-2.2

### 03/11/2026

**Tipo:** decisão — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Aprovei sem ajuste a lista de categorias dos dois leitores do degrau 3 do sandbox (`causa`, `tambem_json`, `conserto`, `licao_livre`). Os dois leitores (agentes, em chats separados, o segundo às cegas) rodaram no ambiente da base sobre a amostra de 30 casos da memória C: causa `esqueceu_import` em 30 de 30 nos dois; conserto em 28 de 30 (kappa 0,63). No mesmo dia, documentei o `--junto-com` (memória que só vale junto com outra) e registrei a decisão de 30/10 sobre a memória do JoogleAnalytics, que fica como está e só vale junto com a C (commit `bdc7c5c`).

**Tags:** sandbox, degrau-3, leitores, memoria-c, concordancia, junto-com, sub-2.5

## 04/11/2026

**Tipo:** decisão — **Sub-atividade:** 2.2 / 2.5 — **Canal:** pessoal

**Registro objetivo:** Fechei a leitura dupla das três memórias do sandbox que estavam no degrau 2:
- **Módulo sem import no JoogleAnalytics:** causa em 30 de 30; "também `json` sem import" em 29 de 30, igual nos dois leitores.
- **Funções proibidas (E):** causa em 26 de 30 (kappa 0,30). Duas das quatro discordâncias são o mesmo rótulo livre escrito de outro jeito; unificados, 28 de 30. Conserto em 22 de 30 (kappa 0,52), sem definição de categoria que separe "corrigiu" de "contornou".
- **Módulo sem import, global (C):** antes do gate, li os 3 casos de `datetime`, que a amostra não trouxe: 3 de 3 `esqueceu_import`.

**Decisão/próximo passo:**
- **Gate aprovado** para a C ("Importe antes de usar: import json, import re, import datetime.") e para a do JoogleAnalytics ("Importe antes de usar: import pandas as pd.", sempre junto com a C), as duas com destino memória.
- **Gate da E em aberto:** antes de decidir o texto, ler as 2 discordâncias reais da causa, para testar a hipótese de que o limite de "inspecionar um valor" não foi definido.
- Falta gravar o degrau 3 no catálogo, que ainda não tem comando.

**Tags:** sandbox, degrau-3, gate, memoria-c, joogleanalytics, memoria-e, kappa, sub-2.5

### 04/11/2026

**Tipo:** decisão — **Sub-atividade:** transversal — **Canal:** pessoal

**Registro objetivo:** Decidi o vocabulário dos documentos: o lugar onde ficam as bases 2 e 3 se chama **ambiente da base** (e não "máquina"); a evidência cita data e comando, sem dizer de onde veio a transcrição; a coluna da leitura dos casos passa a ser `onde_no_trace`. Apliquei nos agentes, nas skills do kit, no `CLAUDE.md`, no `AGENTS.md` e nos docs das análises (commit `48c08cb`). Arquivos com hash registrado ficam como estão até a próxima mudança neles, porque a rodada da base 3 e o manifesto do kit dependem deles.

**Tags:** vocabulario, ambiente-da-base, kit, sigilo, transversal

### 04/11/2026

**Tipo:** implementação — **Sub-atividade:** transversal / 2.6 — **Canal:** pessoal

**Registro objetivo:** Continuei a apresentação. Subi a genealogia da unidade "contrato dict", sinal de harness, harness/infra, erro crítico e resíduo. Com um agente (sem provider definido), fechei o anexo com uma ficha por unidade (19 fichas, com os nomes iguais aos da figura de unidades e sem números, que envelhecem), fechei a ordem dos slides e acrescentei à genealogia uma coluna "final da mensagem": a assinatura "Could not index" é só o sintoma, e é o final da mensagem que separa as causas (`KeyError: 0` → posição; `string indices must be integers` → tipo real do retorno; `KeyError: 'campo'` → campo inexistente).

**Reflexão:** A assinatura descreve o sintoma; a causa é o que o agente tentou fazer. É a resposta pronta para quem perguntar se "Could not index" é mesmo uma assinatura.

**Tags:** apresentacao, genealogia, fichas, could-not-index, assinatura, causa, sub-2.6

## 05/11/2026

**Tipo:** implementação — **Sub-atividade:** transversal / 2.6 — **Canal:** pessoal

**Registro objetivo:** Subi minhas versões de "como investigamos", do estudo de caso do sandbox e de "retorno pode chegar como string". Com um agente (sem provider definido), ajustei os diagramas que ainda não estão commitados:
- **Como investigamos:** a etapa Minerar ganhou perguntas ("Quanto, onde e quando? O que vem antes e depois? Precisamos separar a unidade? Qual a lição específica? Os números fecham?") e o balão "auditoria independente", que é um script que relê o parquet cru sem usar o pipeline.
- **Estudo de caso do sandbox:** mostra a lição genérica da unidade, as partes e o destino do harness em duas unidades (verificação de existência e ferramenta não declarada).
- **Como erros diferentes viram a mesma lição:** as causas A e B passam a vir da mesma execução (jul/26: `docs[0][0]` → `docs["result"][0][0]` → no passo 4, `docs["result"][0]`, que roda sem erro), e a caixa da unidade mostra a lição genérica ao lado da revisada.
- **Slide novo** com a mesma ideia para "retorno pode chegar como string": três mensagens diferentes (indexar, calcular, `json.loads`), uma causa e uma lição.
- **Revisão das 19 fichas:** famílias completas (três fichas omitiam uma das famílias da unidade), lições próximas do texto do código e notas sem pendência de trabalho.

**Reflexão:** Na revisão apareceu um achado: na base 1, 2 dos 5 erros de "estado perdido" são a letra `e`, que o passo anterior não criava. A regra olha só a posição do passo, então esses dois não são perda de estado; parecem narração executada como código (hipótese, não li os casos). A ficha passou a usar um caso em que o passo anterior criava mesmo a variável.

**Decisão/próximo passo:** Ordem do corpo da apresentação: o estudo de caso vem logo depois de "como investigamos", "como revisamos" vai para o anexo, e a eficácia medida (degrau 4) fica no fim, antes das decisões. Pendentes: commitar os diagramas, ajustar o slide do erro crítico ("sem chamar `final_answer`") e decidir se o slide de "contrato dict" fica com o exemplo novo ou volta ao anterior.

**Tags:** apresentacao, como-investigamos, sandbox, licao-generica, partes, fichas, estado-perdido, retorno-string, sub-2.6

### 05/11/2026

**Tipo:** achado — **Sub-atividade:** 2.2 / 3.6 — **Canal:** pessoal

**Registro objetivo:** Fechei a leitura do teto de economia para a apresentação:
- **Teto do sistema:** os tokens dos erros de candidatas são 339,0 mi, 9,1% dos 3.729,3 mi gastos; divididos pelos 283.925 passos, dão cerca de 1.194 tokens por passo, o tamanho máximo de uma memória para empatar com 100% de eficácia.
- **Por que o 387 mi:** é a rodada anterior. Os 2.553 erros do sandbox que foram para sinal de harness explicam a diferença: candidatas 387 → 339 mi e sinal 112 → 160 mi; o total em erro não muda.
- **Por papel:** no ContestacaoCivel, 39,3% dos 896 mi vão para passos com erro (cerca de 352 mi). O teto de 160 mi é 17,9% do gasto do papel, ou cerca de 45% dos tokens em erro dele.

**Reflexão:** As duas porcentagens do papel são o mesmo teto contra bases diferentes; 45% de 39,3% dá os 17,9%. É um teto bruto: não desconta o custo de injetar a memória, que entra em todo passo.

**Tags:** teto-de-economia, orcamento-de-injecao, tokens, contestacaocivel, rodada, sub-3.6
