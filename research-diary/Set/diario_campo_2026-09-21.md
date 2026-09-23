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
