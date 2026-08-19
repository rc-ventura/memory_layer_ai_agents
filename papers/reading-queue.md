# Reading Queue

Sources named in the [research diary](../research-diary/) (from cross-referencing the Zhang et al. survey's full 27-model corpus, Tables 1 & 3) but **not yet given a full atomic note** — no verified authors/venue/link have been pulled for these yet, so this file deliberately does not fabricate bibliographic details. Promote an entry to `papers/<slug>.md` (using [`_TEMPLATE.md`](_TEMPLATE.md)) once it's actually been read and verified against a primary source.

Source: diary entry [18/08/2026](../research-diary/diario_campo_2026-08.md#18082026), Sub-atividade 1.1.

## Priority reading list (as of 18/08/2026)

Ranked by the diary's own priority order. **All five are now cleared** (as of 19/08/2026) — #2 and #3 already had full entries from the bibliographic review; #1, #4, and #5 were added directly from verified arXiv/proceedings pages.

| Priority | Model | Why it was queued | Status |
|---|---|---|---|
| 1 | **ExpeL** | Success/failure insight-extraction protocol → feeds the operation vocabulary for Sub 3.2 | ✅ Reviewed 19/08/2026 — see [`expel-2024.md`](expel-2024.md) |
| 2 | **MemoryBank** | Ebbinghaus-style decay, fills the forgetting gap | ✅ Already reviewed — see [`memorybank-2023.md`](memorybank-2023.md) |
| 3 | **Generative Agents** | Reflection trigger + recency/importance/relevance score | ✅ Already reviewed — see [`generative-agents-2023.md`](generative-agents-2023.md) |
| 4 | **SCM** | Dedicated memory controller — maps directly onto the "controlado" in the project's title | ✅ Reviewed 19/08/2026 — see [`scm-2023.md`](scm-2023.md) |
| 5 | **Retroformer** | The corpus's only case of literal RL — anchor for Sub 1.3 | ✅ Reviewed 19/08/2026 — see [`retroformer-2024.md`](retroformer-2024.md) |

## Priority reading list — rodada 2 (19/08/2026)

Consolidado e ordenado por urgência — não por ordem de descoberta. Verificação rápida feita antes de entrar aqui: os dois arXiv IDs abaixo foram confirmados contra a página do arXiv (título e tema batem com o que está descrito). **Isso não substitui a lista de ontem** (ExpeL, MemoryBank, Generative Agents, SCM, Retroformer, já zerada acima) — é adição condicionada a checagem.

| Prioridade | Paper | Onde focar a leitura | Pergunta específica que resolve | O que essa resposta decide |
|---|---|---|---|---|
| **1** | **SAGE** (Liang et al., set/2024, arXiv:2409.00872) | Seção de protocolo experimental — não o método, não a arquitetura | Os insights da LTM formados numa tarefa são reaproveitados numa tarefa **diferente e posterior** (cross-trial real), ou o "multi-tasking" do abstract é só lidar com várias coisas dentro de uma sessão longa (working memory bem gerida)? | Se a interseção cross-trial × forgetting no [achado central](../discussion/cross-trial-vs-forgetting-gap.md) continua vazia, ou se precisa de uma frase de ressalva/diferenciação no Entregável 1 |
| **2** | **Mem-α** (Wang et al., set/2025, arXiv:2509.25911) | Seção de método — especificamente o que o RL atualiza | O reward/gradiente atualiza os **pesos do agente** (RL de política, mesma categoria de [Retroformer](retroformer-2024.md)/[Memory-R1](memory-r1-2025.md)), ou treina um **controlador separado** enquanto o conteúdo da memória segue sendo texto puro? | Se cita como inspiração conceitual sem risco de escopo, ou se adotar como base implica um salto de arquitetura (SFT/QLoRA → RL de política) que precisa passar pelo Luis Felipe antes de qualquer coisa — ver [`../discussion/scope-and-terminology-decisions.md`](../discussion/scope-and-terminology-decisions.md) |

**Condicional, não agora — só se Sub 1.4 fechar num sentido específico:**

GraphRAG (Edge et al.) ou G-Memory viram leitura ativa **somente se** o fluxo jurídico-alvo exigir navegação entre evidência bruta e síntese de nível mais alto (pergunta em aberto — ver [`../discussion/open-questions.md`](../discussion/open-questions.md)). Antes disso fechar, ler qualquer um dos dois é esforço sem alvo — não dá pra saber ainda se hierarchical é sequer relevante pro caso.

**No radar, não é pra ler agora:**

Um survey de fev/2026 com seção dedicada a forgetting, e um paper de dez/2025 catalogando seis políticas de forgetting distintas — registrados aqui porque existem e porque confirmam que o campo publicou mais coisa relevante a essa lacuna específica nos últimos meses do que em todo 2024. Sem título/arXiv ID confirmado ainda — não têm pergunta pendente amarrada a eles. Viram candidatos quando (e se) a parte de desenhar o mecanismo de forgetting propriamente dito (Sub 2.2/3.2) começar.

## Named in the cross-trial × forgetting gap analysis, not yet reviewed

From the full-corpus cross-reference behind [`../discussion/cross-trial-vs-forgetting-gap.md`](../discussion/cross-trial-vs-forgetting-gap.md) — models with cross-trial ✓ or forgetting ✓ in the Zhang et al. survey's Tables 1/3 that don't yet have an atomic note here:

- **Synapse**, **GITM**, **MetaGPT** — cross-trial ✓ in the survey corpus.
- **TiM**, **RecAgent**, **S³** — forgetting ✓ in the survey corpus.

## Downgraded / deprioritized (18/08/2026 session)

Recorded for traceability, not as a permanent exclusion — revisit if the project's scope changes:

- **GITM** — downgraded: no signal of genuine performance in the corpus review.
- **Role-play cluster** (persona/character agents) — deprioritized: memory form doesn't match the project's needs.
- **Medical fine-tuning cluster** — deprioritized: parametric memory form incompatible with the project's non-parametric scope decision (see [`../discussion/scope-and-terminology-decisions.md`](../discussion/scope-and-terminology-decisions.md)).
