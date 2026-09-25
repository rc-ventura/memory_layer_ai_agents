# Diário de Campo — Rafael Coelho Ventura

## Semana de 21/09 a 25/09/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 21/09/2026

**Tipo:** implementação — **Sub-atividade:** 2.1 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Finalizou o relatório para entrega ao tutor sobre a taxonomia de erros e o schema dos records da esteira — documento necessário para definir como extrair da base todas as execuções que contêm pelo menos um erro (filtro sobre o campo `txt_etap_memo`), de onde sairá a base completa de erros para a taxonomia. Até aqui a análise trabalhou com apenas 1.000 registros. Em paralelo, fundamentou a metodologia de criação da taxonomia — da classificação mais genérica (presença do erro, tipo nativo, família/assinatura) até as unidades de memória — que será consolidada como hipótese própria em `discussion/hipoteses/`, com fundamentação empírica e referências bibliográficas, como pré-trabalho apresentável.

**Reflexão:** O ponto que a fundamentação precisa deixar claro é a genealogia — o roteamento do erro até seu destino final, a unidade de memória. A relação entre família genérica do erro, mecanismo e lição aprendida não é direta: como na analogia da febre, o mesmo sintoma decorre de vários mecanismos e de agentes causadores diferentes — e, no sentido inverso, mecanismos diferentes convergem para a mesma lição.

**Decisão/próximo passo:** Criar o documento de hipótese da taxonomia em `discussion/hipoteses/` e construir a figura da genealogia (erro → família → assinatura → mecanismo → unidade → decisão).

**Tags:** taxonomia-de-erro, schema, extracao-de-erros, metodologia, genealogia, hipoteses, relatorio-tutor, sintoma-mecanismo-unidade, analogia-febre, sub-2.1, sub-2.2

## 22/09/2026

**Tipo:** achado — **Sub-atividade:** 2.1 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Rodou o mesmo pipeline de análise numa segunda base de dados — também 1.000 registros, mas recortada num único mês (agosto/2026), diferente da primeira base. A taxa de erro dos steps ficou em torno de 37%, contra ~32% na primeira base — a faixa de erro se mantém na mesma ordem de grandeza entre as duas bases. O custo segue mais caro nos steps com erro: na segunda base, cerca de 4x o número de tokens gastos em steps com erro vs. sem erro (na primeira base, essa razão ficava em ~3x). Um erro que parecia ter desaparecido reapareceu com força — associado a uma resposta que sinaliza bloco de código "Inativo desde dez/2025". Os dois erros mais proeminentes na segunda base foram "Variável não definida" e "Falha ao indexar o retorno" (could not index) — este último também é um dos mais fortes na primeira base.

**Reflexão:** Como essa segunda base cobre só um mês, a análise de erros por mês de referência fica prejudicada — não há como ter uma leitura temporal com um recorte tão curto. Isso também compromete o roteamento de candidatos de memória, que hoje usa uma regra canônica de corte (≥2 meses e ≥2–3 execuções); essa regra precisa ser reanalisada antes de mais nada. Ainda assim, mesmo sob essa limitação, faz sentido continuar gerando candidatos de memória escopados por papel/agente.

**Decisão/próximo passo:** Ao longo desta semana: continuar analisando esse segundo run; ajustar o roadmap com base na primeira execução, que segue como fundamento; ler os docs dos racionais e finalizar os artigos pendentes da fila de leitura; revisar algumas análises do notebook que ainda não ficaram claras, para checar se fazem sentido e qual o fundamento delas. Decidiu também criar um checklist de ajuste a aplicar sempre que uma nova base entrar na análise: (1) checar se as colunas da tabela ainda existem/batem com o schema esperado; (2) fazer uma pré-rodagem de erros e famílias de erro do smolagents antes da análise completa, para confirmar que todos os erros estão sendo captados; (3) deduplicar a base nova contra a mais antiga e checar se há linhas duplicadas entre elas.

**Tags:** achado, segunda-base, taxa-de-erro, 37-vs-32-por-cento, custo-4x-vs-3x, erro-reaparecido, label-inativo-dez-2025, variavel-nao-definida, could-not-index, corte-de-1-mes, roteamento-candidatos-memoria, regra-2-meses, escopo-por-papel, checklist-nova-base, dedup, familias-smolagents, sub-2.1, sub-2.2

### 23/09/2026

**Tipo:** achado — **Sub-atividade:** 2.5 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Duas descobertas na análise das bases de trace. (1) O campo `anomesdia`, usado até aqui como indicador temporal, não mede o instante da execução: na base 2 ele sugeria um recorte de um único mês (ago/2026), mas a base na verdade cobre ~9 meses quando se usa `dat_hor_inio_exeo`. Um agente (sem provider definido) rodou um teste em três vias — `anomesdia` × `start_time` (timestamp dentro do JSON do step) × `dat_hor_inio_exeo` — e o `start_time` do JSON, que é o tempo de runtime da execução, teve sobreposição forte com `dat_hor_inio_exeo` e fraca com `anomesdia`: `anomesdia` é o recorte/partição da extração da plataforma, não o tempo da execução. (2) Erros mal classificados estão caindo em buckets comuns sem auditoria: na base 1 só 9 erros ficaram não classificados por sintoma (insignificante), mas na base 2 são 25 — e no roteamento de memória aparecem como "erros pontuais" no submecanismo.

**Reflexão:** O `start_time` dentro do JSON do agente se mostra a fonte de verdade do instante de execução — e sem campo de tempo correto, toda leitura temporal fica comprometida (a evolução mês a mês e a regra de ≥2 meses da triagem de candidatos), o que explica por que a base 2 "parecia" um mês só. O bucket "pontual" do submecanismo pode estar escondendo erro classificável: vale cruzar quem cai em "não classificado" por sintoma (`classify`) com quem cai em "pontual" por mecanismo (`submecanismo`) e investigar mais de perto.

**Decisão/próximo passo:** Refazer as análises nas duas bases usando `dat_hor_inio_exeo` como campo de tempo (corrigir o campo no doc de schema). Ajustar a lógica do notebook da esteira para auditar os dois buckets — "não classificado" por sintoma × "pontual" por submecanismo — e investigar os 25 casos da base 2.

**Tags:** anomesdia, dat-hor-inio-exeo, start-time, campo-de-tempo, recorte-de-extracao, base-2, schema, erros-nao-classificados, bucket-pontual, auditoria-classificacao, classify-submecanismo, sub-2.5, sub-2.2

## 24/09/2026

**Tipo:** implementação — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Executou ajustes na segunda base de traces a partir do diagnóstico dos dois baldes de resíduo da taxonomia: 25 erros sem sintoma reconhecido pelo `classify()` (`X_sintoma_nao_reconhecido`) e cerca de 19 erros com sintoma identificado mas sem mecanismo mapeado (`X_causa_nao_identificada`, sem submecanismo). Passou o dia analisando esse diagnóstico caso a caso para responder a duas perguntas: o que mudou de fato na segunda base (erros/padrões novos) e o que exige ajuste na própria metodologia de classificação (regras novas ou estendidas para rotular esses erros).

**Reflexão:** Os dois baldes de resíduo cumpriram o papel previsto de fila de trabalho — em vez de rotular errado, a taxonomia sinalizou exatamente onde falta regra. A pergunta metodológica que o dia abriu é a distinção entre "a base nova trouxe erro novo" (cobertura: estender `classify()`/`submecanismo()`) e "a taxonomia precisa de novo eixo" (rever o desenho do roteamento) — e isso se decide no dado cru, padrão a padrão, não na contagem agregada do balde.

**Decisão/próximo passo:** Transformar a análise dos dois baldes em decisões concretas de regra: para cada padrão recorrente do resíduo da base 2, decidir entre estender uma regra existente, criar regra nova ou manter como cobertura documentada — e portar de volta para a base 1 o que for generalização da metodologia, não peculiaridade da base 2.

**Tags:** base-2, residuo, erros-nao-classificados, sintoma-nao-reconhecido, causa-nao-identificado, classify, submecanismo, taxonomia, cobertura-da-taxonomia, ajuste-de-regras, pipeline-entre-bases, sub-2.2

## 25/09/2026

**Tipo:** achado — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Continuou o refinamento da análise comparando a base 2 com a base 1. Descobriu que alguns erros antes identificados deixaram de ser reconhecidos na base 2, aparentemente por mudança na versão do agente — e o trabalho atual é investigar essas anomalias não classificadas a fundo para responder: são erros novos que pedem classificação nova, ou erros já conhecidos que o regex não capturou, ou ainda sinal de que a taxonomia precisa rediscutir submecanismos/causa-raiz? Está documentando todo esse processo. No meio do dia encontrou um **erro invisível** (sem exceção): o agente planejou 17 passos, mas no passo 15 a ferramenta de consulta deu timeout — um problema que está aparecendo bastante na base 2 — e uma restrição do system prompt impedia reexecutar a mesma ferramenta; o agente então entregou o `final_answer` pulando a etapa 15, e menciona explicitamente essa omissão no `thought`, ou seja, está consciente do que fez.

**Reflexão:** O caso do passo 15 é exatamente a classe de falha que a taxonomia por exceção não enxerga: o plano perde uma etapa obrigatória silenciosamente e o `final_answer` se apresenta como completo — só o `thought` denuncia. Reforça a decisão já tomada de separar as falhas silenciosas num notebook próprio com detectores determinísticos dedicados (roadmap, item 26). O timeout de ferramenta, além de erro visível recorrente, está gerando também esse modo de falha composto — visível na ferramenta, invisível no resultado.

**Decisão/próximo passo:** Seguir a investigação caso a caso das anomalias não classificadas da base 2. Além disso, fatiar melhor a documentação — os docs estão ficando grandes demais; a ideia é criar um índice e dividir em vários `.md`.

**Tags:** base-2, taxonomia, erros-nao-classificados, versao-do-agente, regex, comparacao-entre-bases, erro-invisivel, falha-silenciosa, timeout-de-ferramenta, final-answer, thought, plano-pulado, constraint-system-prompt, item-26, fatiamento-de-docs, indice-de-docs, sub-2.2
