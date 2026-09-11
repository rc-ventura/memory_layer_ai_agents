# Diário de Campo — Rafael Coelho Ventura

## Semana de 07/09 a 11/09/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos ([PROGRAMA-FOMENTO], Nº [ANONIMIZADO])

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 09/09/2026

**Tipo:** leitura — **Sub-atividade:** 2.1 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Finalizou a leitura própria do AgentDebug (*"Where LLM Agents Fail and How They Can Learn From Failures"*, arXiv:2509.25370), promovido de 🔎 (leitura por agente) para ✅ no fichamento e na fila de leitura. Pontos extraídos:

- **Taxonomia modular de erro.** O framework classifica erros por **módulo** (memory, reflection, planning, action, system), não como um balde único — e a abordagem de construir uma taxonomia de erro dedicada é a que interessou.
- **Propagação como gargalo (insight central do paper).** Um erro num step cedo cascateia pelos steps seguintes e, nos benchmarks deles (só de trajetórias de falha), derruba o trace inteiro. *Ressalva:* isso **não transfere direto para a esteira** — no nosso trace `0 de 1.550` trajetórias terminam em falha e 99,3% entregam resposta de conteúdo; aqui a cascata é "cara mas recuperada", não "descarrilada". O que transfere é a estrutura iniciador→seguidor (para custo e para dimensionar unidade de memória), não o "leva o trace à falha".
- **Classificação por step, não por trace.** Contraste direto com o MAST (que rotula por trace, como diagnóstico de causa-raiz). É o que fundamentou o mapeamento do projeto: **módulo do erro-raiz → tipo de unidade de memória** (memory → semântica; planning → procedural; reflection → experiencial-procedural; action → procedural de formato; system → ticket de infra), com a política de escrita "uma unidade por cascata, na raiz".
- **AgentDebug (o agente) ≈ Update Engine v2.** É um agente que pega traces com erro, analisa cada step (Stage 1), identifica o step crítico e o classifica, e gera um feedback acionável (Stage 2). Esse loop diagnóstico → conserto é o análogo publicado mais próximo do escopo **v2** do Update Engine (mexer no harness — prompt, rubrica, tool-config).

**Reflexão:** Cruzei os pontos contra o fichamento e a conversa antes de registrar; a leitura bate, com três precisões. (1) O "propagação leva o trace todo à falha" é achado do paper sobre benchmarks só de falha — diverge do que a esteira mostra (erro = custo, não fracasso). (2) O mapeamento é *módulo do erro-raiz → tipo de memória*, não "tipo de trace → tipo de memória"; e a taxonomia-folha do projeto continua sendo do trace, construída de baixo pra cima — o AgentDebug deu o roteamento por módulo, não as categorias. (3) No paralelo com o v2: só o front-end de diagnóstico (Stage 1+2) mapeia em "propor mudança de harness". O Stage 3 (re-rollout: resetar o ambiente no step crítico, injetar o feedback, re-executar e checar `Eval(τ)`) **não é adotável** — a esteira não tem reward automático, não tem ambiente resetável e os efeitos colaterais são reais (ofícios expedidos, respostas ao Bacen). Mesmo no v2, a verificação de uma mudança de harness fica cross-execução (a assinatura de erro reincidiu depois da mudança?) e passa pelo Commit Gate, não por re-rollout.

**Decisão/próximo passo:** Propaguei os achados que sustentam decisão para os docs canônicos nesta sessão — `analysis/2026-09-trace-law-flow/docs/04-roadmap.md` (seção "Fundamentação emprestada do AgentDebug": causa-raiz > superfície; propagação → análises de cascata; detecção de erro crítico 45% / 24,3% → LLM é gerador de candidatos, não rotulador), `03-procedimento-validacao.md` (caveat sobre juiz LLM para localização de step) e `discussion/knowledge-as-infra-architecture-hypothesis.md` §C (política "uma unidade por cascata, na raiz"; AgentDebug como análogo do v2; âncora custo + reincidência vs. `Eval(τ)`). Adendo no fichamento §B: o proxy observacional `P(falha | first_err_type)` é fraco na esteira porque o desfecho quase não varia. Próximo: promover MAST, TRAIL e ToolScan de 🔎 para ✅.

**Tags:** leitura, agentdebug, taxonomia-de-erro, propagacao-de-erro, cascata, classificacao-por-step, modulo-para-tipo-de-memoria, mapeamento, update-engine, v2, harness, stage-3, re-rollout, eval-tau, commit-gate, custo-vs-fracasso, iniciador-seguidor, roadmap, knowledge-infra, fichamento, sub-2.1, sub-2.2

### Leitura — TRAIL: Trace Reasoning and Agentic Issue Localization

**Tipo:** leitura — **Sub-atividade:** 2.1 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Está finalizando hoje (09/09) a leitura própria do TRAIL (*"Trace Reasoning and Agentic Issue Localization"*, arXiv:2505.08638) — segunda leitura própria do cluster de quatro papers de taxonomia de erro de agentes (depois do AgentDebug hoje mais cedo); faltam MAST e ToolScan. Amanhã (10/09) pretende focar exclusivamente nos resultados das análises do trace da esteira jurídica (`analysis/2026-09-trace-law-flow/`).

**Reflexão:** Fechar o TRAIL marca a transição de "ler os papers que ancoram a taxonomia de erro" para "trabalhar sobre os resultados da análise do trace" — o foco declarado para amanhã.

**Decisão/próximo passo:** (1) 10/09: foco exclusivo nos resultados das análises. (2) Ao confirmar o TRAIL como lido, promovê-lo de 🔎 para ✅ no fichamento e na fila de leitura, como foi feito com o AgentDebug. (3) Depois, MAST e ToolScan.

**Tags:** leitura, trail, taxonomia-de-erro, ponto-cego, anotacao-por-step, issue-localization, cluster-quatro-papers, analise-de-trace, esteira-juridica, transicao-literatura-para-dados, sub-2.1, sub-2.2

### Observação livre — o loop v2 do Update Engine (mexer no harness) roda dentro de um simulador, não em produção

**Tipo:** observação livre — **Sub-atividade:** 2.2 — **Canal:** pessoal

**Registro objetivo:** Trabalhou o mecanismo do Stage 3 do AgentDebug (o *re-rollout*) até entender que ele acontece **inteiramente dentro de um simulador** (ALFWorld / WebShop / GAIA) — nada toca produção, não há usuário nem consequência real. "Replay do ambiente" = re-aplicar as ações gravadas dos steps `1…t*−1` num ambiente novo e determinístico (ou carregar um snapshot) para reconstruir o estado exato antes do step crítico, e só então re-executar o agente ao vivo dali com o feedback injetado. A partir disso, articulou o formato do loop **v2** do Update Engine (mexer no harness), que roda no mesmo tipo de ambiente offline:

1. **Sinal** — trigger + filtro determinístico selecionam casos flagados.
2. **Update Engine (LLM, lote)** — diagnóstico cross-caso (estilo Stage 1+2) + **proposta** de mudança de harness (prompt / rubrica / tool-config).
3. **Validação no sandbox / replay harness** (esqueleto tipo Harbor / Terminal-Bench) — aplica a mudança, re-roda a **suíte curada** com um agente-cópia, checa regressão.
4. **"Passou"** = as assinaturas-alvo pararam de ocorrer **e** nenhum caso que passava antes regrediu (controles limpos).
5. **Commit Gate** — revisão humana, versionado, rollback.
6. **Aplica** de forma controlada.
7. **Monitora** em produção (a assinatura reincide?).

**Reflexão:** Duas coisas ficaram claras. (a) O que me confundia era pensar num agente em produção — mas todo o ciclo AgentDebug, da 1ª run com erro à re-execução, é dentro do simulador; o único artefato que "sai" pra produção é o aprendizado consolidado, já validado. (b) No v2 do projeto, a LLM só entra no passo 2 ("propor"); a verificação (passos 3–4, a suíte de regressão) é **determinística** — "a assinatura `S` ocorreu? s/n" — então o v2 preserva a auditabilidade do v1. Duas correções ao meu primeiro entendimento: o Commit Gate fica **entre** "passou no sandbox" e "aplicado" (passar a suíte é necessário, não suficiente); e "propor mudança no código do agente" é forte demais — o Update Engine não faz commit nos ~130 repos, produz proposta versionada/gateada que segue o processo de engenharia normal.

**Decisão/próximo passo:** Registrado o formato do loop v2 em [`discussion/knowledge-as-infra-architecture-hypothesis.md`](../../discussion/knowledge-as-infra-architecture-hypothesis.md) §C (nota datada, marcada como v2 / fora do escopo v1). O pré-requisito continua sendo construir o **replay harness com ferramentas mockadas** — sem ele, o v1 fica com "escreve memória → observa reincidência nas execuções reais seguintes", sem simulador.

**Tags:** observacao-livre, agentdebug, stage-3, re-rollout, replay-do-ambiente, simulador, sandbox, harbor, terminal-bench, update-engine, v2, mudanca-de-harness, suite-de-regressao, commit-gate, determinismo, auditabilidade, replay-harness, ferramentas-mockadas, knowledge-infra, sub-2.2

## 10/09/2026

**Tipo:** reunião — **Sub-atividade:** 1.4 — **Canal:** formal-tutor

**Registro objetivo:** Apresentou ao tutor os gráficos e relatórios das análises dos traces da esteira jurídica (`analysis/2026-09-trace-law-flow/`). Retorno positivo: as análises geraram insights quantitativos (e potencialmente qualitativos) que a própria esteira de agentes não produzia — dados pioneiros sobre o comportamento da esteira a partir dos traces crus. O tutor se comprometeu a (a) expandir a base de dados de traces disponível para análise e (b) investigar o que o campo `status` do schema dos traces significa, já que é preenchido com números que provavelmente referenciam tabelas (categorias de caso, estágios do pipeline, ou outro domínio enumeraível). O checkpoint não foi transcrito (ambos esqueceram durante a reunião).

**Reflexão:** O fato de a análise ter produzido insights que a própria esteira não tinha confirma o valor da mineração sistemática de traces como fonte de sinais — conecta diretamente ao Signal Ledger (componente B) e ao Sub 1.4 (mapear fluxos). O campo `status` com números referenciando tabelas é um novo ponto de investigação: pode revelar categorias de caso ou estágios do pipeline que enriquecem o filtro determinístico de anomalia (componente A/C) e o DMF-lite importance score (ex.: `status` como peso no cálculo de `S`).

**Decisão/próximo passo:** (1) Semana seguinte: continuar minerando a base de dados em busca de novos insights, seguindo o roadmap em `analysis/2026-09-trace-law-flow/docs/04-roadmap.md`. (2) Continuar refinando `01-racionais.md` para expor as regras e análises de forma transparente e receber contribuições de ajuste para evitar vieses. (3) Continuar auditando os resultados do pipeline. (4) Expandir a base de análises com a nova base de dados que o tutor fornecerá. (5) Agendar o descritor do campo `status` para análise assim que a base expandida chegar.

**Tags:** reuniao, tutor, analise-de-traces, retorno-positivo, insights-pioneiros, status-do-schema, expandir-base, roadmap, racionais, transparencia, vieses, auditoria-pipeline, sem-transcricao, sub-1.4

### Achado — LangChain Eval Engineering Skill: implementação open source que mapeia para a arquitetura do projeto

**Tipo:** achado — **Sub-atividade:** 1.5 / 2.2 — **Canal:** pessoal

**Registro objetivo:** Aprofundou o estudo de evals e descobriu que a LangChain possui uma skill open source de "Eval Engineering" (`langchain-ai/langchain-skills`, `config/skills/eval-engineering/`, 1.2k stars) — uma SKILL.md instalável em coding agents (Claude Code, Codex, Devin) que inspeciona o repo de um agente, opcionalmente minera traces do LangSmith, entrevista o desenvolvedor, e constrói evals em formato Harbor (containerizados, reproduzíveis, com verifier). A skill tem 21 arquivos, 12 referências, um fluxo de 7 passos, e conceitos que mapeiam quase 1:1 com a arquitetura do projeto: World Knowledge Skill ↔ strategy layer (camada 3), Task.md (control-plane spec) ↔ Sub 1.5 (critérios de acerto/erro), Verifier design ↔ Sub 3.6 + Commit Gate (componente D), Calibration taxonomy (8 categorias de falha) ↔ atribuição de causa no cold path, Discovery methodology ↔ Sub 1.4. Documentado em duas notas em `discussion/`: `langchain-eval-engineering-skill-analysis.md` (mecânica completa da skill + isomorfismo com o cold path) e `eval-engineering-skill-architecture-connections.md` (mapeamento componente-por-componente, separando 7 itens genuinamente novos de 6 que são corroboração). Nova open question registrada em `open-questions.md`: o filtro determinístico de anomalia deveria distinguir anomalia de comportamento do agente de anomalia de ambiente/infraestrutura antes de rotear para o Update Engine. Terceiro contato com este material (primeiro: 24/08 via vídeo → trigger ≠ conteúdo; segundo: 10/09 via blog post; terceiro: 10/09 via source code da skill).

**Reflexão:** A skill é a implementação de referência mais concreta do padrão que o projeto desenha na teoria — especialmente o World Knowledge Skill, que é a strategy layer (camada 3) com anti-patterns nomeados ("speculative encyclopedia", "stale certainty", "task leakage") que o Commit Gate e o Forgetting (componente E) deveriam explicitamente prevenir. A taxonomy de calibration (8 categorias: capability, missing information, harness, environment, false rejection, false acceptance, leakage, infrastructure) dá ao projeto um framework estruturado para a atribuição de causa que o cold path atual não tem — quando um agente falha após uma atualização de memória, foi a memória ou foi o ambiente? A distinção entre Caminho A (memória — barato, incremental, reversível, sem deploy) e Caminho B (harness — caro, discreto, precisa deploy) ficou clara como v1 vs. v2 do projeto, não como concorrentes mas como camadas complementares do mesmo loop de melhoria.

**Decisão/próximo passo:** (1) Estudar a skill com calma antes de instalar — o valor metodológico (Task.md, Verifier design, Calibration) independe do Harbor. (2) Quando chegar a Sub 1.6 (agentes mínimos), testar a skill instalando no Claude Code e construindo evals para os agentes POC. (3) A open question sobre o filtro distinguir agent vs. environment anomaly já foi registrada em `open-questions.md`.

**Tags:** eval-engineering, langchain, harbor, skill-md, open-source, world-knowledge-skill, task-md, verifier-design, calibration-taxonomy, 8-categorias, discovery-methodology, isomorfismo, cold-path, strategy-layer, sub-1.5, sub-2.2, sub-3.6, open-questions-atualizado, sub-1.6-futuro, caminho-a-vs-b
