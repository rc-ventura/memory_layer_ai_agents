---
type: methodology
title: Metodologia de Taxonomia de Erros (Genealogia)
description: O método determinístico, sem LLM, que roteia cada erro bruto de trace até a menor lição de memória que o evitaria — cinco elos (granularidade, sintoma, mecanismo, unidade, triagem), dois eixos paralelos que dividem e depois fundem, e por que a memória vive no nível da unidade, não do sintoma.
tags: [error-taxonomy, genealogy, memory-candidates, trace-analysis, deterministic-classification, triage]
sources:
  - id: openwiki-source-61e9034accfd6552e38f7eff
    resource: repo://analysis/2026-09-trace-law-flow/docs/09-metodologia-erro-a-memoria.md
  - id: openwiki-source-569719c5da69b38f321cdb6a
    resource: repo://analysis/2026-09-trace-law-flow/pipeline/base_pipeline.py
  - id: openwiki-source-2d51aa76f8fc441a01852754
    resource: repo://discussion/hipoteses/trace-error-taxonomy-methodology/general-error-taxonomy-methodology.md
  - id: openwiki-source-e2588285d2ac910e627dab99
    resource: repo://discussion/teoria/agentdebug-vs-trail-error-taxonomy.md
generated: { by: "claude-code", at: "2026-09-23T23:38:13.077Z" }
verified:
  - by: openwiki/0.5.1
    at: 2026-09-23T23:38:13.077Z
---

Sistemas de agentes sem memória persistente redescobrem as mesmas falhas em cada execução. Transformar erros registrados em memória útil exige uma taxonomia — mas taxonomia boa não é rótulo bonito, é **roteamento**: cada erro bruto precisa chegar, por regras determinísticas e reabíveis no dado cru, até a menor lição reutilível que o evitaria (ou até fora da memória). A contribuição central é a **genealogia de erros** — dois eixos paralelos de classificação (o que o sistema reclamou × o que o agente fez de errado) que se **dividem** (um sintoma pode ter várias causas) e se **fundem** (causas diferentes podem pedir a mesma cura) até convergir numa decisão de escrita.

Dois documentos, dois papéis que não se confundem: a hipótese de método **genérica** — [`general-error-taxonomy-methodology.md`](../../discussion/hipoteses/trace-error-taxonomy-methodology/general-error-taxonomy-methodology.md) — abstrai os elos, perguntas e racionais para qualquer trace futuro; a **instanciação** verificada — [`analysis/2026-09-trace-law-flow/docs/09-metodologia-erro-a-memoria.md`](../../analysis/2026-09-trace-law-flow/docs/09-metodologia-erro-a-memoria.md) — aplica o método ao trace real da esteira jurídica com funções, números e o Sankey de genealogia. Método aqui (nesta página, resumindo o primeiro); evidência lá.

## Os cinco elos

| Elo | Pergunta que responde | Saída | Papel na memória |
|---|---|---|---|
| **E0 · Granularidade** | O que conta como 1 evento de erro? | eventos extraídos do trace | define a base de contagem — sem isso, contar antes de definir a unidade fabrica números |
| **E1 · Sintoma** | O que o sistema reclamou? | família + assinatura | chave de proveniência/busca — **não decide** |
| **E2 · Mecanismo** | O que o agente fez de errado? | causa, erro a erro | diagnóstico — desambigua o sintoma |
| **E3 · Unidade** | Uma lição só previne todos os erros do grupo? | agrupamento de mecanismos | conteúdo — o card em si, um fato/regra por unidade |
| **E4/E5 · Triagem** | Merece persistir? Onde a correção vive? | candidata / não-memória / fora / revisar | decisão — não é um nível da taxonomia |

Cada elo é uma regra determinística sobre texto (mensagem de erro + o sinal local mais informativo que o trace já registre, como a linha de código rejeitada) — nunca um classificador neural ou LLM-as-judge. A razão não é custo: é que uma regra determinística é **reabível** — qualquer rótulo se triangula de volta ao caso cru — enquanto um classificador neural seria mais uma afirmação a validar, não uma base para validar as outras.

## Dois eixos paralelos, não uma árvore

Sintoma (E1) e mecanismo (E2) são duas leituras independentes da mesma mensagem de erro — um não chama o outro — com papéis independentes (**descrever × decidir**), não estatisticamente independentes: costumam compartilhar a mesma porta de entrada (o texto da mensagem). O que o eixo mecanismo acrescenta é um **salto de evidência local** que o sintoma nunca toca — por exemplo, no trace da esteira jurídica, a linha de código rejeitada pelo interpretador. A relação entre os dois é muitos-para-muitos nos dois sentidos, o que uma árvore não representaria:

| Aresta | Cardinalidade | O que significa |
|---|---|---|
| sintoma → mecanismo | **1:N** | a mesma reclamação de superfície admite causas diferentes — é onde a taxonomia se **abre** |
| mecanismo → unidade | **N:1** | causas diferentes com a mesma cura convergem — é onde a taxonomia se **fecha** |
| unidade → decisão | **N:1** | a triagem decide pela unidade **global**, não por (contexto × unidade) |

Consequência arquitetural: o eixo sintoma **não alimenta a decisão** — é a camada de descrição, proveniência e descoberta (o censo dos sintomas, a trilha de auditoria, o catch-all que sinaliza erro novo numa extração maior). Quem decide é sempre o eixo mecanismo — **com uma única exceção, declarada**: no fechamento da unidade (`montar_unidades()` na instanciação), a família do sintoma é consultada só para separar os dois baldes de resíduo entre si (ver abaixo), que nunca viram memória. Nenhuma candidata depende disso — na base 1 as 10 candidatas saem idênticas com ou sem a separação.

### O resíduo — dois baldes, não um catch-all

Todo classificador por regras tem uma sobra, e aqui ela é dividida em dois baldes porque as duas leituras podem falhar de formas diferentes — e cada falha pede um trabalho diferente:

|| Balde | Quando | O que pede |
|---|---|---|---|
|| **Sintoma não reconhecido** (`X_sintoma_nao_reconhecido`) | nem E1 nem E2 reconhecem a mensagem | alarme de **cobertura**: a taxonomia não cobre esse erro — escrever regra de sintoma primeiro, depois de causa |
|| **Causa não identificada** (`X_causa_nao_identificada`) | E1 reconhece o sintoma, E2 não identifica a causa | metade do caminho feita — escrever só a regra de causa. Inclui o código malformado (sintaxe), ruído até se provar recorrente |

Cada erro cai em **no máximo um** balde — não há sobreposição — e "causa não identificada" descreve a **regra**, não o erro (não significa que aconteceu uma vez). O tamanho de cada balde é parte do relato de cobertura de qualquer instanciação: onde o resíduo cresce, as regras não alcançam.

### Exemplo real — a assinatura "Could not index" se divide, dois mecanismos se fundem

No trace da esteira jurídica, 136 erros compartilham a mesma mensagem de sintoma ("Could not index"), mas `submecanismo()` — que lê a mensagem **mais** a linha de código rejeitada — os separa em três causas distintas: `dict_indexado_por_posicao` (89 erros, `doc[0]` num retorno que é dict), `tipo_real_do_retorno` (37, indexou uma string como se fosse dict) e `campo_inexistente_no_retorno` (10, `KeyError` numa chave que não existe). As duas primeiras convergem na mesma unidade de memória (`U_contrato_dict`, 96 erros ao somar um terceiro mecanismo de sintoma diferente) porque a mesma lição — "ferramentas de documento retornam `{'result': [[...]]}`, acesse `r['result'][0]`" — previne ambas; a terceira mecanismo vira uma unidade separada (`U_campo_inexistente`), porque nenhuma frase única cobriria as duas causas sem virar disjunção. Esse par (divide pelo sintoma, funde pelo mecanismo) é o padrão que se repete em toda a taxonomia, não uma exceção.

## Por que a memória vive na unidade, não no sintoma

Se a memória fosse escrita por sintoma, o exemplo acima produziria um único card para "Could not index" — e falharia em dois sentidos ao mesmo tempo:

| Defeito | Por quê |
|---|---|
| **Ambíguo e diluído** | O card cobriria três causas com três consertos diferentes — viraria um checklist ("pode ser X, Y ou Z") em vez de um fato ensinável. A chave também é **não-injetiva**: nem roteamento determinístico seria possível sem re-rodar o mecanismo. |
| **Duplicado** (o oposto, no caso inverso) | Quando o mecanismo nasce de *outro* sintoma mas pede a mesma cura, escrever por sintoma separaria o que deveria ser um card só — custo de manutenção dobrado, risco de as duas cópias divergirem. |
| **Genérico demais** | Um card do tipo "inspecione tipo e chaves antes de indexar" preveniria tudo — mas perde exatamente o que dá valor a uma unidade factual: os fatos específicos do ambiente (o contrato real de retorno, os nomes de campo reais). Conselho genérico é o que a memória já daria sem dado nenhum. |

O equilíbrio que o método persegue: granular o suficiente para ser ensinável, fundido o suficiente para ser uma lição só — e concreto porque nasce do trace, não de intuição.

## Triagem — três perguntas, na mesma ordem para toda unidade

Uma unidade só vira candidata a memória depois de passar, em ordem, por três perguntas de gate:

1. **É memória do agente?** Se quem falhou foi o harness ou o LLM upstream, o agente não tem o que aprender — a correção vai para política operacional (retry, monitoramento), não para memória.
2. **Tem conteúdo único — uma frase que previne?** Se o agrupamento é heterogêneo demais para uma frase só — o caso dos dois baldes de resíduo — ele **não é descartado nem vira não-memória**: vai para **revisar**, a fila de trabalho da taxonomia.
3. **Recorre entre execuções e no tempo?** Memória entre execuções só se justifica se o problema atravessa execuções e tempo — senão é episódico, não estrutural.

Os desfechos possíveis da triagem são, portanto, quatro: **candidata**, **não-memória**, **fora** (sem recorrência) e **revisar**. Os baldes de resíduo passam pelo mesmo teste de recorrência das candidatas, mas contado **por padrão de erro** (classe da exceção + mensagem com os dados do caso mascarados), não pelo balde — que junta erros diferentes por construção. Um padrão recorrente põe o balde em **revisar — prioridade**; sem nenhum, **revisar — baixa prioridade**. Nenhum dos dois é memória: o trabalho é na taxonomia (escrever a regra que falta), e uma vez escrita o erro vira unidade normal e refaz a triagem como qualquer outra.

Os limiares de recorrência (quantas execuções, quanto tempo) são **escolhas calibradas por instanciação, não constantes do método** — na instanciação da esteira jurídica, o corte adotado foi ≥3 execuções e ≥2 meses. Testar a sensibilidade do limiar (mover a régua e refazer a conta) é parte obrigatória da triagem, não um passo opcional.

## Validação — a mesma escada, aplicada à classificação

A profundidade de validação por elo segue a mesma régua geral do projeto (contagem direta → recomputação; heurística → teste de robustez; afirmação prescritiva/geradora de memória → cadeia completa com auditoria independente) — ver [Metodologia de Análise de Traces](metodologia-de-analise-de-traces.md#práticas-de-validação-em-uso). Dois instrumentos específicos da genealogia: **reabibilidade total** (qualquer rótulo — família, mecanismo, unidade — volta ao caso cru por `exec_id`) e a distinção entre **corrigir** (o fenômeno é real, a régua estava errada) e **retirar** (o exame caso a caso mostra que o fenômeno não estava lá) como os dois desfechos possíveis de um teste de robustez que falha.

## O papel da literatura — bancada de teste, nunca fonte da taxonomia

A ordem de construção importa e inverte a intuição: a taxonomia nasce do trace primeiro, só depois é testada contra a literatura — nunca o contrário. Nesse papel, a literatura só faz três coisas: **testa** o mapeamento contra taxonomias externas, **sugere** análises ainda não rodadas, e **dá vocabulário** para nomear o que o trace já mostrava — nunca "dá a taxonomia" pronta, porque isso seria importação, não genealogia.

Um incidente concreto ilustra por que essa disciplina importa: uma versão anterior da tabela de candidatas a memória descrevia uma alegação como "fundamentada no AgentDebug (o módulo que produziu o erro roteia o tipo de memória)" — verificado contra o PDF completo do paper (arXiv:2509.25370), essa frase não existe em lugar nenhum; o paper propõe uma taxonomia diagnóstica de 5 módulos e confirma por ablação que uma política de escrita por causa-raiz supera corrigir todo erro de superfície, mas nunca propõe "tipos" de memória ou "roteamento". A alegação era uma analogia do próprio projeto, não um achado transferido do paper — corrigida em três lugares no mesmo dia. Ver [`agentdebug-vs-trail-error-taxonomy.md`](../../discussion/teoria/agentdebug-vs-trail-error-taxonomy.md), que também mostra o resultado construtivo do mesmo exercício: AgentDebug (eixo módulo → correção prescritiva) e TRAIL (eixo fenômeno + severidade → medição diagnóstica) classificam ao longo de eixos diferentes e complementares, nenhum dos dois substitui o outro nem "é" a genealogia deste projeto.

## Limites declarados

1. **Só entra erro que levanta exceção.** Erros silenciosos (código que roda e entrega resultado errado sem lançar exceção) ficam fora da genealogia — exigem detectores próprios, não este método.
2. **O eixo sintoma não é descrição neutra.** Os nomes de família/assinatura já carregam alguma interpretação causal — leia como descrição *assistida*, não como rótulo neutro de superfície.
3. **Não lê intenção.** Classifica pelo que o trace mostra (mensagem + sinal local), não pelo raciocínio do agente — responde "que conteúdo evitaria o erro", não "em qual módulo ele nasceu" (lentes complementares, não rivais — ver a comparação AgentDebug/TRAIL acima).
4. **Sem eixo de severidade.** Frequência e custo (tokens) existem; uma medida de gravidade da consequência do erro, em geral, não — um erro recuperável frequente pode pesar, na priorização por contagem, tanto quanto uma falha rara e grave.
5. **A cascata olha uma janela curta.** Estado perdido vários passos atrás pode aparecer como outra unidade — aproximação declarada, não resolvida.
6. **Thresholds de triagem são escolhas com teste de sensibilidade, não constantes do método** — mudam por instanciação, junto com as regras de classificação e o sinal local disponível no trace.

## Como se conecta ao resto do projeto

- As unidades de memória candidatas que este método produz alimentam diretamente os componentes Memory Store e Update Engine da [Hipótese de Arquitetura "Knowledge as Infra"](../arquitetura/hipotese-knowledge-as-infra.md).
- O método pressupõe o layout de pasta, a disciplina de PII e a escada de validação descritos em [Metodologia de Análise de Traces](metodologia-de-analise-de-traces.md) — esta página cobre só a classificação em si.
- A disciplina de verificação bibliográfica (📝/🔎/✅) que evitou o incidente do AgentDebug é a mesma documentada em [Revisão de Literatura e Disciplina de Citação](revisao-de-literatura-e-disciplina-de-citacao.md).
