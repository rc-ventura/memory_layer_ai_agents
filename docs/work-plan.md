# Plano de Trabalho do Bolsista

*Documento oficial do programa, preservado no idioma original (português). Fonte: [`sources/Plano_de_Trabalho_Rafael_Ventura.docx`](sources/Plano_de_Trabalho_Rafael_Ventura.docx).*

**Programa:** Inova Talentos – IPT Open
**Razão Social:** Instituto Itaú de Ciência, Tecnologia e Inovação
**Nº do Projeto:** 1335844346
**Título do Projeto:** Mecanismo de atualização de memória para agentes de IA generativa com aprendizado por reforço aplicado a fluxos jurídicos
**Nome do Bolsista:** Rafael Coelho Ventura
**Nome do Tutor:** Luis Felipe Chary de Lima
**Início do Projeto:** 07/08/2026
**Término do Projeto:** 31/07/2027

---

## Objetivos

Justificativa do trabalho do bolsista dentro do projeto:

O bolsista atuará no desenvolvimento e validação de um mecanismo de atualização de memória para agentes de IA generativa aplicados a fluxos jurídicos, utilizando sinais de desempenho (feedback positivo/negativo, oriundos de critérios da área usuária e/ou revisão humana) para ajustar de forma controlada as instruções, exemplos e contexto operacional armazenados na memória de cada agente. A atuação abrange desde a fundamentação teórica em técnicas de atualização de memória e aprendizado por reforço — com refinamento bibliográfico contínuo ao longo do projeto —, passando pela exploração prática comparativa entre diferentes abordagens de memória e aprendizado em agentes (loop de aprendizado fechado nativo vs. memória transparente com controle programático explícito), pelo design e validação de arquitetura em ambiente local (POCs), até o desenvolvimento, a implantação nos ambientes da plataforma (desenvolvimento, homologação e produção) e a validação em piloto real, com consolidação de uma funcionalidade integrada ao fluxo da plataforma de agentes do INTERESSADO, entregando ao final do ciclo um componente documentado, testado e pronto para expansão a outros agentes do ecossistema do INTERESSADO, incluindo arquiteturas de agentes de longo horizonte ("deep agents").

## Macroatividades

### Macroatividade 1 — Fundamentação teórica e exploração prática comparativa de abordagens de memória em agentes de IA

*Prazo: 30/10/2026*

- **Sub 1.1:** Revisão bibliográfica inicial sobre memória em agentes de IA generativa (memória de curto/longo prazo, episódica x semântica) e técnicas de atualização, com refinamento contínuo ao longo do projeto.
- **Sub 1.2:** Estudo teórico de arquiteturas de agentes de longo horizonte ("deep agents"), com loop de aprendizado nativo, planejamento explícito e memória persistente entre sessões, mapeando como o aprendizado incremental é descrito na literatura.
- **Sub 1.3:** Levantamento de técnicas de aprendizado por reforço aplicáveis à atualização de memória (RLHF, RLAIF, bandits contextuais, entre outras).
- **Sub 1.4:** Mapeamento dos fluxos jurídicos alvo do projeto e identificação dos pontos onde os sinais de desempenho serão coletados.
- **Sub 1.5:** Definição preliminar dos critérios de "acerto/erro" que servirão de sinal de atualização (revisão humana e/ou área usuária).
- **Sub 1.6:** Construção de agentes mínimos representando abordagens distintas de memória e aprendizado: (a) loop de aprendizado fechado nativo, com memória em camadas e conversão automática de sessões em regras/skills reutilizáveis; (b) memória transparente, com controle programático explícito do log de execução.
- **Sub 1.7:** Análise comparativa entre aprendizado implícito e um modelo de sinal de feedback explícito (certo/errado), avaliando prós, contras e riscos para o contexto de fluxos jurídicos.

**Entregáveis 1:** Relatório de revisão bibliográfica e mapeamento de técnicas + documento de especificação preliminar dos sinais de feedback + relatório comparativo entre as abordagens de memória avaliadas, com as respectivas POCs mínimas.

### Macroatividade 2 — Design da arquitetura, POCs e validação local do mecanismo

*Prazo: 31/12/2026*

- **Sub 2.1:** Refinamento bibliográfico contínuo, com novos levantamentos direcionados a sustentar as decisões de arquitetura, stack tecnológica e design do mecanismo.
- **Sub 2.2:** Definição da arquitetura do mecanismo com base nos aprendizados da Macroatividade 1 (onde os sinais entram, como regras/exemplos/contexto são armazenados e versionados, e qual stack servirá de base para a implementação).
- **Sub 2.3:** Construção de um protótipo conceitual (POC) do mecanismo, incorporando os conceitos validados nas etapas anteriores.
- **Sub 2.4:** Testes locais do POC em ambiente controlado (sandbox), testando e refinando as escolhas de arquitetura e stack frente à implementação prática, com apoio de levantamento bibliográfico adicional quando necessário.
- **Sub 2.5:** Levantamento dos pontos de integração com a plataforma de agentes do INTERESSADO (contratos de API, requisitos de segurança e observabilidade).
- **Sub 2.6:** Revisão da arquitetura com o tutor e a área responsável pela plataforma, validando a viabilidade de integração antes do início da implementação.

**Entregáveis 2:** Documento de arquitetura técnica (com justificativa da stack escolhida, sustentada por levantamento bibliográfico) + protótipo conceitual documentado e testado localmente + mapeamento dos pontos de integração com a plataforma de agentes do INTERESSADO.

### Macroatividade 3 — Desenvolvimento e implantação do mecanismo de atualização de memória

*Prazo: 31/03/2027*

- **Sub 3.1:** Implementação do módulo de captura e armazenamento dos sinais de desempenho.
- **Sub 3.2:** Implementação do ajuste controlado das instruções/exemplos/contexto armazenados na memória do agente.
- **Sub 3.3:** Implementação de testes unitários e de integração do mecanismo.
- **Sub 3.4:** Implementação de salvaguardas (versionamento e rollback) para evitar degradação da memória.
- **Sub 3.5:** Implantação do mecanismo nos ambientes de desenvolvimento, homologação e produção da plataforma de agentes do INTERESSADO.
- **Sub 3.6:** Definição e implementação das métricas de desempenho (taxa de sucesso, estabilidade, latência).
- **Sub 3.7:** Definição do público beta e desenho do teste A/B para a validação em ambiente real, com base nas métricas definidas (grupos de controle e tratamento, critérios de elegibilidade e tamanho de amostra).

**Entregáveis 3:** Mecanismo implantado nos ambientes de desenvolvimento, homologação e produção + métricas de desempenho definidas e implementadas + relatório técnico de implementação + resultados dos testes unitários e de integração + desenho do teste A/B e definição do público beta para o piloto.

### Macroatividade 4 — Validação, métricas de desempenho e piloto em ambiente real

*Prazo: 31/05/2027*

- **Sub 4.1:** Execução do piloto em produção com o público beta e o desenho de teste A/B definidos na Macroatividade 3, monitorando os sinais de feedback.
- **Sub 4.2:** Coleta e análise dos dados do piloto (evolução da taxa de acerto, redução de retrabalho, comparação entre grupos do teste A/B).
- **Sub 4.3:** Ajuste e refinamento do mecanismo com base nos resultados observados.
- **Sub 4.4:** Testes de regressão e validação de estabilidade após ciclos sucessivos de atualização.

**Entregáveis 4:** Relatório de resultados do piloto com métricas consolidadas + registro dos ajustes realizados.

### Macroatividade 5 — Consolidação da funcionalidade, documentação técnica e entrega final

*Prazo: 31/07/2027*

- **Sub 5.1:** Consolidação do mecanismo como funcionalidade integrada ao fluxo da plataforma de agentes do INTERESSADO.
- **Sub 5.2:** Elaboração da documentação técnica completa (arquitetura, contratos de integração, guia de uso e extensão).
- **Sub 5.3:** Elaboração de roteiro para expansão do mecanismo a outros agentes do ecossistema, incluindo arquiteturas de agentes de longo horizonte ("deep agents").
- **Sub 5.4:** Apresentação final dos resultados ao tutor e à área usuária.
- **Sub 5.5:** Elaboração do relatório final consolidado do projeto.

**Entregáveis 5:** Funcionalidade integrada à plataforma de agentes do INTERESSADO + documentação técnica completa + relatório final.

## Resultados Esperados

Ao final do ciclo de bolsa, espera-se entregar uma funcionalidade de atualização de memória integrada ao fluxo da plataforma de agentes do INTERESSADO, validada em piloto real, com métricas consolidadas de taxa de sucesso, estabilidade e latência, além de documentação técnica que permita a expansão do mecanismo para outros agentes do sistema multiagente aplicado a fluxos jurídicos, incluindo arquiteturas de agentes de longo horizonte ("deep agents").

---

*Ver [`sub-activity-map.md`](sub-activity-map.md) para a tabela de sinais usada para classificar registros do [diário de campo](../research-diary/) por sub-atividade.*
