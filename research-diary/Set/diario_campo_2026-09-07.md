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
