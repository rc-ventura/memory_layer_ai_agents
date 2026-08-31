# Diário de Campo — Rafael Coelho Ventura

## Semana de 31/08 a 04/09/2026

Projeto: Mecanismo de atualização de memória para agentes de IA generativa aplicado a fluxos jurídicos (Inova Talentos / IPT Open, Nº 1335844346)

*Registro pessoal de pesquisa, testes, leituras e decisões. Camada episódica (entradas diárias); a camada semântica é o digest mensal em `summarization/`. Uso: memória de trabalho pessoal + acompanhamento do coordenador + rastreabilidade para os Entregáveis do Plano de Trabalho.*

---

## 31/08/2026

**Tipo:** reunião — **Sub-atividade:** 2.2 / 2.6 — **Canal:** formal-tutor

**Registro objetivo:** Registro da reunião de checkpoint com o tutor (Luis Felipe) de 28/08/2026, feito agora depois de cruzar o conteúdo com a documentação técnica já existente. Na reunião apresentei a hipótese de arquitetura inteira — o "mega brain" como memory layer agnóstico de framework, acessível por qualquer agente via uma tool MCP. Retorno geral: parte das ideias elogiada, parte não bloqueada mas desencorajada.

- **Gate seletivo STM→LTM.** O tutor desencorajou depender só de escrita incondicional de todo trace. Mesmo que não haja uma tool seletiva do que vira memória de longo prazo, é preciso ao menos um gate para que nem toda STM/trace vire LTM — a volumetria é grande demais e, nas palavras dele, a maioria dos traces "pode não ser nada", então persistir tudo é gravar ruído no mega brain. Precisamos de um mecanismo seletivo do tipo "analisei este trace e isto pode sim ser persistido no mega brain". Os artigos DMF e SAGE implementam algo parecido.
- **Sem tool ADD de memória.** Continuo não achando interessante ter uma tool de ADD de memória; a escrita deve fluir por trigger de sistema.
- **Update Engine como LLM** — o "cérebro" do memory layer — foi bem elogiado. A **camada de governança** (governance layer) também.
- **Banco de traces / signal ledger.** Já existe um banco de traces (o tutor vai fornecer para eu inspecionar), ou seja, já temos ou a base do nosso signal ledger, ou pelo menos um banco bruto para gerar os insights e ativar os triggers. A fonte de trigger do Update Engine passa a ser esse banco de traces, além do sinal de human feedback **negativo** (não o positivo). Ainda cabe termos um signal ledger próprio do Update Engine: um mecanismo determinístico analisa os traces, seleciona os que parecem relevantes/anômalos, junta com os sinais de human feedback e grava no signal ledger para o Update Engine monitorar e avaliar.
- Preciso ainda ler alguns artigos para ter ideia mais clara dos ajustes que teremos que fazer na infra.

Resumo factual da reunião em [`docs/checkpoints/checkpoint-2026-08-28-tutor.md`](../docs/checkpoints/checkpoint-2026-08-28-tutor.md); reflexões cross-cutting em [`discussion/checkpoint-2026-08-28-reflections.md`](../discussion/checkpoint-2026-08-28-reflections.md); atualizações datadas em `open-questions.md`, no doc de arquitetura e no `scope-and-terminology-decisions.md` (feitas na mesma sessão).

**Reflexão:** Cruzei o relato com a documentação antes de registrar, e ele bate — em um ponto eu estava sendo mais conservador do que precisava. O gate seletivo STM→LTM **não é uma modificação nova** do que a gente vinha pensando: é a resolução que já está no `open-questions.md` desde 27/08 — um split de duas camadas em que o **log episódico** recebe ADD incondicional (só texto, sem embedding, barato, serve auditoria e alimenta o Update Engine com sucesso *e* falha) e a **LTM** só recebe o que passa por um gate estilo SAGE (`R ≥ θ1`, ~20–30% do volume). A própria nota de 27/08 diz que SAGE e ADD incondicional nunca foram incompatíveis — a seletividade do SAGE é sobre *promoção para a LTM*, não sobre *escrever o log cru*. O que a reunião de 28/08 acrescenta é corroboração independente do tutor, chegando ao mesmo desenho pelo lado de volumetria e custo. DMF (score determinístico no write) e SAGE (mecânica θ1/θ2) que citei estão certos e já estão na arquitetura e no reading-queue; o gate reusa o `S` do DMF-lite e o decay `R = e^(−τ/S)`, sem máquina nova.

O que é genuinamente novo e vale como questão aberta: **quem é dono do gate de admissão?** O Curador (Update Engine) faz a gestão do que entra no mega brain, ou ele só faz a evolução/update da memória? O lean documentado hoje aponta para dois mecanismos separados — gate de admissão determinístico, barato, sem LLM (`R ≥ θ1`); Update Engine LLM, em lote, para evoluir a strategy layer — mas a linguagem "curador" da reunião borrou os dois. Isso se conecta a sub-perguntas ainda abertas no `open-questions.md` de 27/08 (o `S` do gate é o mesmo do DMF-lite ou um "promotion score" à parte? o gate avalia em schedule, no recall, ou os dois?).

Sobre o signal ledger: comecei conflando "banco de traces" com "signal ledger" e depois separei certo. O banco de traces ≈ fonte bruta para insights/triggers (lado episódico do Memory Store); o Signal Ledger (componente B) é outro store, que guarda os sinais de correção (thumbs, desfecho, flags do filtro determinístico) que o Update Engine monitora. O fluxo que descrevi no fim — filtro determinístico varre os traces → seleciona os relevantes/anômalos → junta com human feedback → grava no signal ledger → Update Engine monitora — é o cold path da arquitetura + o que já ficou registrado em 28/08 (reusar o banco existente, trace-ID + lista de consumidos, latência de sinal assimétrica por tipo de agente).

**Decisão/próximo passo:** (1) Levar ao `open-questions.md` a questão "quem é dono do gate de admissão da LTM — mecanismo determinístico separado ou o Update Engine/curador?", ligando às sub-perguntas de 27/08 sobre o score e a cadência de avaliação do gate. (2) Tratar o gate seletivo STM→LTM como **necessário, não opcional** (lean de 27/08 agora com respaldo do tutor) — mas ainda dependente de calibração de θ1/θ2 no Sub 1.6/1.7. (3) Ler os artigos que sustentam o ajuste de infra, na ordem: SSGM (#1 — governance gate + rollback), SAGE (#19, urgência Tier 2 — a mecânica do promotion gate STM→LTM), DMF (#11 — o princípio do score determinístico) e DarwinMem (#42 — seleção por utilidade + poda, adicionado hoje). (4) Aguardar o tutor fornecer o banco de traces para validar as suposições de schema/conteúdo do trace e o que serve de sinal.

**Tags:** reuniao, tutor, mega-brain, memory-layer, mcp, gate-seletivo, stm-ltm, promotion-gate, sage, dmf, darwinmem, add-tool, update-engine, curador, governance-layer, signal-ledger, banco-de-traces, human-feedback-negativo, trigger, componente-a, componente-b, componente-c, open-questions, checkpoint-28-08, sub-2.2, sub-2.6
