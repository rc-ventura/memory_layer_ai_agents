# Relatório Mensal — Setembro de 2026

- **Projeto:** Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos
- **Programa:** [PROGRAMA-FOMENTO] — Nº [ANONIMIZADO]
- **Bolsista:** Rafael Coelho Ventura
- **Período de referência:** 01/09/2026 a 30/09/2026
- **Data de emissão:** 25/09/2026

Este arquivo guarda, versionado, o que foi submetido no formulário mensal da instituição. Os dois blocos abaixo correspondem aos dois campos do formulário.

---

## Desenvolvimento das atividades no período

*(etapas e atividades realizadas, alterações introduzidas, acompanhamento, orientação e cumprimento do cronograma)*

Em setembro as atividades concentraram-se no aprofundamento empírico da **Macroatividade 1** e no avanço da **Macroatividade 2**, em três frentes: consolidação teórica da arquitetura de memória, leitura integral do cluster de artigos de taxonomia de erros em agentes, e — frente principal do período — a análise sistemática de traces reais da plataforma de agentes do INTERESSADO.

**Revisão bibliográfica dirigida (Sub 1.1 / 2.1).** Foram concluídas as leituras integrais do SSGM e do SAGE — deste último extraiu-se a mecânica de promoção de conteúdo à memória de longo prazo por dois gatilhos independentes (decaimento temporal e reflexão gerada na resolução de erro), insumo direto para o desenho do *gate* seletivo do mecanismo. Avançou a leitura própria do cluster de taxonomia de falhas em agentes: *AgentDebug* e *TRAIL* lidos integralmente (restam MAST e ToolScan). Do primeiro, adotou-se a classificação por passo de execução e o mapeamento módulo-do-erro-raiz → tipo de unidade de memória; do segundo, a constatação de que a maioria dos tipos de falha é estruturalmente invisível à classificação por exceção — achado que fundamenta uma frente de detectores dedicados. Foi ainda estudada a implementação open source "Eval Engineering" (LangChain), cuja estrutura mapeia de perto a arquitetura proposta.

**Desenho da arquitetura (Sub 2.2).** Consolidou-se a arquitetura de memória em três camadas — log de execução cru e imutável; camada intermediária tipada (exemplar + reflexão); camada de estratégia por meta-reflexão — e o *gate* seletivo de promoção à memória de longo prazo foi confirmado como requisito pelo tutor no *checkpoint* de 28/08. Definiu-se também o formato do ciclo de atualização de *harness* (v2 do motor de atualização): a LLM apenas propõe mudanças, a validação é determinística em ambiente de simulação/replay, e a aplicação depende de *commit gate* com revisão humana.

**Análise de traces reais (Sub 1.4 / 1.5 / 2.5) — frente principal.** Construiu-se um pipeline determinístico (sem LLM na classificação, integralmente reauditável) que roteia cada erro registrado nos traces até a menor lição reutilizável que o evitaria, numa "genealogia" família → assinatura → mecanismo → unidade → destino. Sobre a primeira base analisada (1.000 execuções reais, out/2025–ago/2026): 498 erros classificados e 11 unidades candidatas a memória cobrindo ~90% dos erros e ~92% dos tokens gastos em passos com erro. Foram mineradas e validadas no dado bruto as duas primeiras unidades de memória — ambas com causa-raiz concreta e ensinável (uma decorre de contrato de retorno não compreendido pelo agente; outra, de campo induzido pelo próprio prompt e inexistente no contrato real). O trabalho está documentado em relatório de achados, racionais de cada análise, procedimento de validação e auditorias independentes com recomputação dos resultados.

**Replicação em segunda base e correção metodológica.** O mesmo pipeline foi aplicado a uma segunda base de 1.000 execuções, independente da primeira: a taxa de erro ficou em ~37% (contra ~32% na base 1) e o custo dos passos com erro em ~4x (contra ~3x). O exercício expôs e corrigiu um problema metodológico relevante: o campo de data usado até então (`anomesdia`) é a data de partição da extração, não da execução — corrigida a datação para o campo de início de execução, todas as análises foram refeitas (na base 1, o lote de extração coincidia com o mês de execução em apenas ~36% dos casos). O diagnóstico dos erros não classificados na base 2 gerou ajustes concretos na taxonomia — novos sintomas reconhecidos (timeout de ferramenta, nova redação de import proibido) — e identificou o primeiro caso de **falha silenciosa**: um agente entregou resposta final omitindo uma etapa planejada que falhou por timeout, sem que o erro constasse no resultado.

**Alterações introduzidas.** (i) Correção do campo de tempo da análise (`anomesdia` → `dat_hor_inio_exeo`), com refação das análises e marcação explícita das auditorias que ficaram desatualizadas; (ii) formalização das três etiquetas de classificação de erro — sintoma, mecanismo e motivo — e correção de dois excessos de atribuição à literatura detectados em verificação de fontes; (iii) instituição de checklist de entrada para toda base nova (consistência de colunas, pré-censo de tipos de erro, deduplicação contra bases anteriores) e de alarme de cobertura da taxonomia.

**Acompanhamento e orientação.** Duas reuniões com o tutor no período: em 10/09, apresentação dos gráficos e relatórios das análises de trace — retorno positivo, com o compromisso de expandir a base de traces disponível e de investigar o significado do campo `status` do schema; em 18/09, definição da tarefa seguinte — expressar a taxonomia de erros como **query hierárquica** (do campo indicador de erro ao tipo nativo à assinatura) para extrair, via AWS, o dataset completo de erros da base de ~1 milhão de registros, superando a limitação de representatividade das amostras de 1.000. O *checkpoint* de 28/08 (registrado neste período) formalizou o endosso do tutor ao *gate* seletivo de promoção de memória.

**Cumprimento do cronograma.** A Macroatividade 1 (prazo 30/10/2026) segue conforme o previsto, com avanço substancial das Sub 1.4 e 1.5 — a taxonomia empírica de erros operacionaliza os critérios de acerto/erro e o mapeamento dos pontos de coleta de sinais. A Macroatividade 2 avançou em 2.1, 2.2 e 2.5. Permanecem como pendências principais do Entregável M1: a conclusão das leituras MAST e ToolScan, a consolidação das POCs de agentes mínimos (Sub 1.6, iniciada em agosto) e a comparação implícito-vs-explícito (Sub 1.7), dependentes da estabilização da frente de análise de traces.

---

## Observações/comentários

*(qualquer aspecto considerado relevante para o andamento das atividades)*

O mês produziu um resultado que transcende o diagnóstico: a análise de traces gerou insights quantitativos que a própria plataforma de agentes não produzia — avaliação positiva registrada pelo tutor na reunião de 10/09 — e confirmou empiricamente a premissa do projeto (erros recorrentes e reincidência de mesmas causas entre execuções, a matéria-prima que a memória de trabalho visa capturar).

Dois pontos de atenção para o próximo período: (a) a limitação de representatividade — as análises atuais usam amostras de 1.000 registros sobre uma base de ~1 milhão, o que motivou a tarefa de extração do dataset completo de erros via query na AWS; (b) o achado da falha silenciosa indica que a classificação por exceção cobre só o erro visível — os detectores de falha sem exceção (planejamento abandonado, ferramenta não chamada, resposta divergente da observação) serão desenvolvidos em frente dedicada, já prevista no roadmap da análise.

Registra-se, por transparência metodológica, que toda cadeia numérica publicada nos relatórios da análise passa por auditoria independente (recomputação a partir do dado bruto por caminho de código separado), e que se mantém no diário de campo a distinção entre leitura bibliográfica assistida por agentes de IA e leitura própria do bolsista — esta última é a que sustenta decisões de projeto.
