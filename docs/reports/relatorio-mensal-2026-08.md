# Relatório Mensal — Agosto de 2026

- **Projeto:** Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos
- **Programa:** [PROGRAMA-FOMENTO] — Nº [ANONIMIZADO]
- **Bolsista:** Rafael Coelho Ventura
- **Período de referência:** 01/08/2026 a 31/08/2026
- **Data de emissão:** 29/08/2026

Este arquivo guarda, versionado, o que foi submetido no formulário mensal da instituição. Os dois blocos abaixo correspondem aos dois campos do formulário. O resumo curto para envio está em [`relatorio-mensal-2026-08-resumo-envio.md`](relatorio-mensal-2026-08-resumo-envio.md).

---

## Desenvolvimento das atividades no período

*(etapas e atividades realizadas, alterações introduzidas, acompanhamento, orientação e cumprimento do cronograma)*

No mês de agosto as atividades concentraram-se na **Macroatividade 1** (fundamentação teórica e revisão bibliográfica) e avançaram sobre o desenho inicial da **Macroatividade 2** (arquitetura do mecanismo).

**Revisão bibliográfica (Sub 1.1 e 1.2).** Foram lidos integralmente dois *surveys* de referência sobre memória de agentes de IA — *A Survey on the Memory Mechanism of LLM-based Agents* (Zhang et al., ACM TOIS 2025) e *Memory in the Age of AI Agents* (Hu, Liu et al., 2026) — e iniciada a leitura de um terceiro (*From Storage to Experience*, Luo et al., 2026). O cruzamento sistemático das taxonomias dos dois primeiros produziu o **achado central do período**: entre os 27 modelos do corpus de Zhang et al., os que aprendem com a experiência acumulada entre casos distintos (*cross-trial*) e os que implementam esquecimento controlado (*forgetting*) formam conjuntos disjuntos — nenhum modelo combina as duas propriedades. Essa lacuna é exatamente o espaço que o mecanismo do projeto (Entregável M3) se propõe a ocupar, e entrará como achado explícito no relatório do Entregável M1. As duas taxonomias foram conciliadas em documento próprio, adotando-se o eixo operacional (escrita / gestão / leitura / esquecimento) como vocabulário principal do relatório. Foi montada e priorizada uma fila de leitura estruturada por componente da arquitetura; uma triagem prévia em profundidade dos oito artigos de maior prioridade foi conduzida com apoio de agentes de IA — sem substituir a leitura própria do bolsista, ainda em curso — e confirmou o achado central também em nível de mecanismo, não apenas de tabela comparativa.

**Terminologia e escopo (Sub 1.3).** Em reunião de acompanhamento com o tutor, definiu-se formalmente a natureza do "aprendizado por reforço" previsto no título do projeto: trata-se de **ajuste de *harness*** (prompt, ferramentas, configuração) a partir de sinal explícito de aprovação/reprovação do usuário, agregado em lote antes de cada atualização — e não de *fine-tuning* supervisionado nem de gradiente de política. Como desdobramento, revisou-se a literatura sobre confiabilidade de feedback humano binário (Christiano et al., Stiennon et al., Sharma et al., Gao et al., Casper et al.), da qual se extraíram riscos concretos (baixa concordância entre anotadores; *sycophancy* amplificado pelo próprio RLHF) a tratar no desenho do sinal (Sub 1.5 e 3.6).

**Mapeamento dos fluxos jurídicos (Sub 1.4).** Concluiu-se o mapeamento da esteira jurídica-alvo (cadastro → produção de subsídios → contestação → encaminhamento a escritório terceirizado), com registro da arquitetura de agentes da plataforma (agentes especializados que não se comunicam entre si; regras de negócio servidas por ferramentas MCP, externas à memória do agente). A transcrição da reunião de *checkpoint* com o tutor foi anexada ao repositório do projeto.

**Desenho da arquitetura (Sub 2.2 / 2.3 / 2.5).** A partir da fundamentação acima, elaborou-se uma primeira **hipótese de arquitetura** para o mecanismo: uma camada de memória agnóstica de *framework*, acessível pelos agentes como ferramenta via MCP, organizada em componentes (armazenamento por caso, motor de atualização, *gate* de *commit* com versionamento e *rollback*, esquecimento com remoção efetiva). Trata-se explicitamente de hipótese de trabalho, a validar contra comportamento real nas provas de conceito mínimas do Sub 1.6 e na comparação implícito-vs-explícito do Sub 1.7; a prototipagem dessa validação foi iniciada ao fim do mês. A partir de reunião de infraestrutura com a equipe técnica e o tutor, mapearam-se ainda os três mecanismos de memória que já coexistem na plataforma sem coordenação entre si — o que abre uma questão de escopo (conviver, unificar ou substituir) a decidir com a orientação.

**Alterações introduzidas.** Consolidaram-se três ajustes de escopo/entendimento: (i) o Entregável M3 é tratado como funcionalidade integrada à plataforma, não como biblioteca reutilizável independente; (ii) a terminologia de "RL" do projeto foi fixada como ajuste de *harness* por sinal binário em lote, em documento de decisões de escopo; (iii) acrescentou-se a métrica de *Reference Accuracy* (F1 de recuperação contra gabarito anotado) ao Sub 3.6, em escopo restrito ao fluxo do projeto e condicionada à definição das Sub 1.4/1.5.

**Acompanhamento e orientação.** No período houve reunião de *checkpoint* com o tutor (mapeamento de fluxos e definição da natureza do RL) e reunião com a equipe de arquitetura de agentes e o tutor sobre as implementações de memória em curso na plataforma. Permanece pendente uma reunião com o responsável pela memória dos agentes no *framework* Hermes.

**Cumprimento do cronograma.** As atividades da Macroatividade 1 avançaram conforme o previsto, com as Sub 1.1 a 1.4 substancialmente cobertas no período. A Sub 1.5 (critérios de acerto/erro) segue em aberto, dependente da definição fina do fluxo-alvo. O desenho da arquitetura (Macroatividade 2) foi antecipado em relação ao cronograma, na forma de hipótese a validar, para orientar as provas de conceito. A leitura integral, pelo bolsista, dos artigos prioritários da fila permanece em andamento e não foi substituída pela triagem assistida.

---

## Observações/comentários

*(qualquer aspecto considerado relevante para o andamento das atividades)*

O achado de que aprendizado entre casos e esquecimento controlado não coexistem na literatura reforça a pertinência do objetivo do projeto e será o argumento central do relatório do Entregável M1.

Registra-se, por transparência metodológica, a distinção mantida no diário de campo entre **triagem bibliográfica assistida por agentes de IA** e **leitura própria do bolsista**: os oito artigos prioritários foram pré-triados dessa forma, mas a leitura integral pelo bolsista — necessária para sustentar decisões de projeto perante o tutor — segue em andamento.

O principal ponto de atenção para o próximo período é a definição do fluxo jurídico-alvo e dos critérios de acerto/erro (detalhamento do Sub 1.4 e Sub 1.5), dos quais dependem tanto a instrumentação de avaliação (Sub 3.6) quanto o início efetivo das provas de conceito. Questão secundária a levar à orientação: a relação entre o mecanismo proposto e os três mecanismos de memória já existentes na plataforma (convivência, unificação ou substituição).
