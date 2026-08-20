# Diário de Campo — Rafael Coelho Ventura

## Agosto de 2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos (Inova Talentos / IPT Open, Nº 1335844346)

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias) + camada semântica (síntese semanal, toda vez que uma semana se encerra). Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 18/08/2026

**Tipo:** leitura — **Sub-atividade:** 1.1 — **Canal:** pessoal

**Registro objetivo:** Revisei uma síntese visual (Gemini Notebook) do survey de Zhang et al. (ACM TOIS 2025) cobrindo fontes de memória (inside-trial/cross-trial/external), formas (textual x paramétrica), o ciclo write-manage-read e os dois eixos de avaliação (direta/indireta). A partir disso, fechei a lista de leitura priorizada para os Subs 1.1/3.2: prioridade 1 ExpeL (protocolo de extração de insight sucesso/falha → vocabulário de operações pro Sub 3.2), 2 MemoryBank (decay tipo Ebbinghaus, resolve o buraco de forgetting), 3 Generative Agents (gatilho de reflexão + score recency/importance/relevance), 4 SCM (memory controller dedicado, mapeia direto pro "controlado" do título do projeto), 5 Retroformer (único caso de RL literal do corpus, âncora do Sub 1.3). Rebaixei/descartei nesta sessão: GITM (sem sinal de desempenho genuíno) e os clusters de role-play e fine-tuning médico (forma de memória incompatível com o projeto).

**Reflexão:** A tabela de fontes (Tabela 1) tinha me enganado antes — responde "de onde vem o conteúdo", não "como o conteúdo é atualizado", que é o que o Objetivo do projeto pede. O eixo certo pra tudo que vier depois é operação (Tabela 3), não fonte.

**Tags:** zhang-survey, expel, memorybank, generative-agents, scm, retroformer, leitura-priorizada

### Achado — lacuna cross-trial × forgetting confirmada no corpus completo

**Tipo:** achado — **Sub-atividade:** 1.1 — **Canal:** pessoal

**Registro objetivo:** Cruzei a Tabela 1 (cross-trial ✓) com a Tabela 3 (Forgetting ✓) sobre os 27 modelos do corpus do Zhang et al., não só os 4 modelos "full-source" da primeira leitura. Resultado: exatamente 6 modelos têm cross-trial ✓ (Retroformer, ExpeL, Synapse, GITM, Reflexion, MetaGPT) e exatamente 5 têm forgetting ✓ (MemoryBank, TiM, Generative Agents, RecAgent, S³) — e a interseção entre os dois conjuntos é vazia. Confirmação exaustiva sobre o corpus inteiro, não uma tendência de amostra parcial.

**Reflexão:** Isso é achado central pro relatório do Entregável 1: os modelos que aprendem com experiência entre casos diferentes não têm esquecimento controlado, e os que esquecem não aprendem entre casos diferentes. É exatamente a lacuna que o mecanismo da Macroatividade 3 se propõe a preencher — vale entrar como finding explícito, com a tabela completa como evidência.

**Decisão/próximo passo:** Registrar esse finding formalmente no relatório do Entregável 1 (Sub 1.1), citando a tabela cheia, não só a observação da amostra de 4 modelos.

**Tags:** zhang-survey, cross-trial, forgetting, lacuna-literatura, entregavel-1

### Decisão — três pendências fechadas nesta sessão

**Tipo:** decisão — **Sub-atividade:** 1.1 — **Canal:** pessoal

**Registro objetivo:** Fechei três pontos que estavam em aberto. (1) Forma de memória: confirmado não-paramétrico — o vocabulário do Objetivo/Sub 2.2/Sub 3.2 é textual, então métodos de memory editing (MEND, KnowledgeEditor, PersonalityEdit, APP, MAC) ficam fora do escopo de implementação do M3, mas podem entrar como "alternativa considerada e rejeitada" no documento de arquitetura do Sub 2.2. (2) Papel do Reflexion: é provavelmente a origem do "aprendizado por reforço" no título do projeto ("verbal reinforcement learning"), mas não é RL literal — sem reward model, sem gradiente de política, só autocrítica textual concatenada ao prompt. Retroformer e Memory-R1 são RL literal de fato. (3) Cross-trial x cross-agent: cross-trial é fronteira de tempo (mesmo agente, invocações separadas); cross-agent é fronteira de identidade (agentes distintos trocando info via protocolo). A Agent Communication Protocol (IBM) foi incorporada à Agent2Agent Protocol (Google) sob a Linux Foundation em agosto de 2025 — não existe mais como spec separada. Confirmado: "chat novo lendo preferência de chat antigo no mesmo projeto" é cross-trial, não cross-agent.

**Reflexão:** A distinção cross-trial x cross-agent muda o alcance da preocupação de confidencialidade que eu tinha registrado pra M2 — ela se aplica especificamente a handoffs entre agentes especializados distintos dentro do mesmo fluxo (triagem → redação → compliance), não à persistência entre sessões do mesmo agente. Isso estreita bastante o escopo do risco.

**Decisão/próximo passo:** O Plano precisa declarar explicitamente, em algum ponto do Sub 1.3 ou 1.7, qual sentido de "RL" o mecanismo de fato implementa — ainda não fiz isso.

**Tags:** memoria-nao-parametrica, reflexion, cross-trial, cross-agent, a2a, governanca

### Achado — correção de datação sobre benchmark de avaliação direta

**Tipo:** achado — **Sub-atividade:** 1.1 — **Canal:** pessoal

**Registro objetivo:** O Zhang et al. (§6.3, submissão 21/04/2024) afirma que até aquele momento não havia benchmark open-source dedicado à avaliação direta e isolada de módulos de memória. Essa lacuna fechou nos meses seguintes: o LoCoMo (Maharana et al., arXiv:2402.17753, 27/02/2024) — publicado ~2 meses antes do survey mas ausente das referências dele, provavelmente por corte do levantamento antes de fevereiro/2024 — e o LongMemEval se tornaram o padrão de fato 2025-2026 (Mem0, DMF, A-Mem e Memory-R1 são todos avaliados neles). Ressalva: LoCoMo/LongMemEval são majoritariamente avaliação indireta (acurácia de QA fim-a-fim), não Reference Accuracy pura (recuperação vs. gabarito, independente da resposta final). Um benchmark que isole só qualidade de recuperação ainda não existe de forma dedicada.

**Reflexão:** Se eu for citar a frase original do Zhang et al. sobre ausência de benchmark no relatório do Entregável 1, preciso vir com essa correção de datação — citar sem a ressalva contradiz a própria bibliografia que já reuni (Mem0/DMF/A-Mem/Memory-R1 avaliados em LoCoMo).

**Decisão/próximo passo:** Adicionar Reference Accuracy (F1 sobre recuperação vs. gabarito) como quarta métrica no Sub 3.6, aproveitando as anotações de gabarito de recuperação do LoCoMo.

**Tags:** locomo, longmemeval, zhang-survey, sub-3.6, metricas

### Decisão — desenho do diário de campo

**Tipo:** decisão — **Sub-atividade:** transversal — **Canal:** pessoal

**Registro objetivo:** Desenhei com o Claude o esquema do diário de campo pessoal de pesquisa. Decisões fechadas: (a) camada episódica diária + camada semântica via síntese semanal automática toda vez que uma semana se encerra; (b) arquivo corrido por mês (`diario_campo_AAAA-MM.md`); (c) export limpo em docx no fechamento do mês, para o coordenador acompanhar; (d) esquema de campos por entrada — tipo, sub-atividade (mapeada contra o Plano de Trabalho), canal (pessoal / informal-coordenador / formal-tutor), registro objetivo, reflexão opcional, decisão/próximo passo opcional, tags.

**Reflexão:** O campo "canal" resolve de forma direta uma ambiguidade que já estava registrada como pendência do projeto — separar direção informal do coordenador de validação formal do tutor. Também virou uma aplicação prática da própria teoria do projeto: separar registro episódico bruto de síntese semântica destilada, exatamente como o Plano propõe fazer no mecanismo de memória do agente (Sub 2.2).

**Decisão/próximo passo:** Rodar a skill por pelo menos uma semana em uso real antes de considerá-la fechada. Reavaliar se a cadência semanal da síntese é suficiente e se o export mensal em docx deveria ser quinzenal, dado que o coordenador acompanha de perto.

**Tags:** meta-memória, diário-de-campo, governança, skill

### Decisão — escopo da métrica Reference Accuracy (Sub 3.6)

**Tipo:** decisão — **Sub-atividade:** 3.6 — **Canal:** pessoal

**Registro objetivo:** Decidido: Reference Accuracy (F1 entre o que o mecanismo recuperou e um gabarito anotado) entra no Sub 3.6 como quarta métrica, mas em escopo restrito — gabarito anotado manualmente sobre casos do próprio fluxo jurídico do projeto, sem construir um benchmark generalizável no estilo LoCoMo/LongMemEval. Um benchmark dedicado seria overengineering: rema contra o reenquadramento já feito (biblioteca reutilizável → funcionalidade integrada à plataforma do Itaú) e não se justifica dado o cronograma do M3 já comprimido.

**Reflexão:** A métrica não pode ser implementada ainda, mesmo em escopo restrito — "o que deveria ter sido recuperado" só existe depois que o fluxo jurídico alvo (Sub 1.4) e os critérios de acerto/erro (Sub 1.5) estiverem definidos. Anotar gabarito pra um fluxo que ainda não foi escolhido não tem como funcionar.

**Decisão/próximo passo:** Marcar Reference Accuracy como métrica pronta pra implementar assim que Sub 1.4 e Sub 1.5 fecharem — bloqueada por elas, não por falta de decisão de escopo.

**Tags:** reference-accuracy, sub-3.6, escopo, dependencia-1.4-1.5

---

## 20/08/2026

**Tipo:** leitura — **Sub-atividade:** 1.1 — **Canal:** pessoal

**Registro objetivo:** Comecei ontem (19/08) a ler "Memory in the Age of AI Agents" (Hu, Liu et al., arXiv:2512.13564), investigando conceitos relacionados a memória, principalmente topologias de memória. O artigo está se mostrando interessante porque propõe uma taxonomia de conceitos, servindo como artigo fundamental para o relatório. Descobri alguns modelos interessantes citados nele, como Memento e SAGE. Pretendo finalizar a leitura hoje, dia 20/08.

**Reflexão:** Esse survey já estava catalogado no repo (nota em `papers/memory-in-the-age-of-ai-agents-2025.md` e mind map 2 em `literature-review/visual-synthesis/`), mas só a partir de verificação de abstract, não de leitura própria — essa é a primeira leitura de fato dele. Achado colateral interessante: Memento e SAGE, citados dentro desse survey, já são as prioridades #1 e #2 do reading queue do projeto, encontrados por um caminho independente (o cruzamento cross-trial × forgetting do corpus Zhang et al.) — é uma segunda confirmação, vinda de fonte diferente, de que esses dois merecem prioridade.

**Decisão/próximo passo:** Finalizar a leitura hoje (20/08). Depois de terminar, atualizar o campo "Read by Rafael" na nota do paper e no reading queue.

**Tags:** memory-in-the-age-of-ai-agents, topologias-de-memoria, taxonomia, memento, sage, leitura-fundamental
