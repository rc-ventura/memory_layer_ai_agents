# Reading Queue

Sources named in the [research diary](../research-diary/) (from cross-referencing the Zhang et al. survey's full 27-model corpus, Tables 1 & 3) but **not yet given a full atomic note** — no verified authors/venue/link have been pulled for these yet, so this file deliberately does not fabricate bibliographic details. Promote an entry to `papers/<slug>.md` (using [`_TEMPLATE.md`](_TEMPLATE.md)) once it's actually been read and verified against a primary source.

Source: diary entry [18/08/2026](../research-diary/diario_campo_2026-08.md#18082026), Sub-atividade 1.1.

## ✅ Consolidated priority checklist (19/08/2026)

All currently open items, ranked. **Ranking criterion** (so the order is arguable, not asserted): risco ao achado central do Entregável 1 > ganho direto de design pro mecanismo > risco de escopo/arquitetura a sinalizar antes de adotar > leitura complementar/de fechamento de quadro. Marque conforme for lendo — os detalhes de cada item (pergunta específica, o que a resposta decide) estão nas seções abaixo.

- [ ] **1. SAGE** (arXiv:2409.00872) — protege o [achado central](../discussion/cross-trial-vs-forgetting-gap.md): risco de precisar de ressalva no Entregável 1 se a interseção cross-trial×forgetting não estiver mais vazia. *Ver detalhe → [rodada 2](#priority-reading-list--rodada-2-19082026).*
- [ ] **2. Memento** (arXiv:2508.16153) — maior ganho de design isolado: candidato mais forte até agora pra conciliar RL com memória não-paramétrica (Sub 2.2). *Ver detalhe → [rodada 2](#priority-reading-list--rodada-2-19082026).*
- [ ] **3. Mem-α** (arXiv:2509.25911) — checagem de risco de escopo antes de citar como inspiração (RL sobre pesos vs. RL sobre controlador). *Ver detalhe → [rodada 2](#priority-reading-list--rodada-2-19082026).*
- [ ] **4. Synapse** — completa o quadro cross-trial ✓ do corpus Zhang et al., sem pergunta específica amarrada ainda.
- [ ] **5. MetaGPT** — idem, cross-trial ✓.
- [ ] **6. TiM** — completa o quadro forgetting ✓ do corpus.
- [ ] **7. RecAgent** — idem, forgetting ✓.
- [ ] **8. S³** — idem, forgetting ✓.

**Fora do checklist ativo, por design:** GraphRAG/G-Memory (bloqueados por Sub 1.4 — ver [condicional](#priority-reading-list--rodada-2-19082026)), o survey de forgetting fev/2026 e o catálogo de políticas dez/2025 (sem arXiv ID confirmado ainda), e GITM (já descartado — ver [downgraded](#downgraded--deprioritized-18082026-session)).

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

Consolidado e ordenado por urgência — não por ordem de descoberta. Verificação rápida feita antes de entrar aqui: os três arXiv IDs abaixo foram confirmados contra a página do arXiv (título e tema batem com o que está descrito; Memento tem uma ressalva de título, ver a linha dele). **Isso não substitui a lista de ontem** (ExpeL, MemoryBank, Generative Agents, SCM, Retroformer, já zerada acima) — é adição condicionada a checagem. Ordem consolidada com o restante da fila no [checklist no topo do arquivo](#-consolidated-priority-checklist-19082026).

| Prioridade | Paper | Onde focar a leitura | Pergunta específica que resolve | O que essa resposta decide |
|---|---|---|---|---|
| **1** | **SAGE** (Liang et al., set/2024, arXiv:2409.00872) | Seção de protocolo experimental — não o método, não a arquitetura | Os insights da LTM formados numa tarefa são reaproveitados numa tarefa **diferente e posterior** (cross-trial real), ou o "multi-tasking" do abstract é só lidar com várias coisas dentro de uma sessão longa (working memory bem gerida)? | Se a interseção cross-trial × forgetting no [achado central](../discussion/cross-trial-vs-forgetting-gap.md) continua vazia, ou se precisa de uma frase de ressalva/diferenciação no Entregável 1 |
| **2** | **Memento** (Zhou et al., ago/2025, arXiv:2508.16153) | Seção de método — como a política de seleção de casos é treinada, e como a memória episódica escreve/descarta casos | A escrita/descarte na memória episódica é **explícita e controlável**, ou implícita dentro do loop de RL? E o reward que treina a política de seleção vem de um sinal externo (tipo revisão humana/área usuária, o que o projeto usa) ou só de correctness fim-a-fim? | Se vira referência arquitetural direta pro Sub 2.2 — RL sobre um controlador de seleção, sem tocar no LLM nem no formato textual/não-paramétrico da memória. Nota de verificação: título aparece como "AgentFly" em uma indexação secundária (mesmo arXiv ID) — confirmar versão exata antes de citar formalmente; repo oficial usa "Memento". Resultado reportado: top-1 no GAIA validation (87,88% Pass@3). |
| **3** | **Mem-α** (Wang et al., set/2025, arXiv:2509.25911) | Seção de método — especificamente o que o RL atualiza | O reward/gradiente atualiza os **pesos do agente** (RL de política, mesma categoria de [Retroformer](retroformer-2024.md)/[Memory-R1](memory-r1-2025.md)), ou treina um **controlador separado** enquanto o conteúdo da memória segue sendo texto puro? | Se cita como inspiração conceitual sem risco de escopo, ou se adotar como base implica um salto de arquitetura (SFT/QLoRA → RL de política) que precisa passar pelo Luis Felipe antes de qualquer coisa — ver [`../discussion/scope-and-terminology-decisions.md`](../discussion/scope-and-terminology-decisions.md) |

**Condicional, não agora — só se Sub 1.4 fechar num sentido específico:**

GraphRAG (Edge et al.) ou G-Memory viram leitura ativa **somente se** o fluxo jurídico-alvo exigir navegação entre evidência bruta e síntese de nível mais alto (pergunta em aberto — ver [`../discussion/open-questions.md`](../discussion/open-questions.md)). Antes disso fechar, ler qualquer um dos dois é esforço sem alvo — não dá pra saber ainda se hierarchical é sequer relevante pro caso.

**No radar, não é pra ler agora:**

Um survey de fev/2026 com seção dedicada a forgetting, e um paper de dez/2025 catalogando seis políticas de forgetting distintas — registrados aqui porque existem e porque confirmam que o campo publicou mais coisa relevante a essa lacuna específica nos últimos meses do que em todo 2024. Sem título/arXiv ID confirmado ainda — não têm pergunta pendente amarrada a eles. Viram candidatos quando (e se) a parte de desenhar o mecanismo de forgetting propriamente dito (Sub 2.2/3.2) começar.

## Named in the cross-trial × forgetting gap analysis, not yet reviewed

From the full-corpus cross-reference behind [`../discussion/cross-trial-vs-forgetting-gap.md`](../discussion/cross-trial-vs-forgetting-gap.md) — models with cross-trial ✓ or forgetting ✓ in the Zhang et al. survey's Tables 1/3 that don't yet have an atomic note here:

- **Synapse**, **MetaGPT** — cross-trial ✓ in the survey corpus (GITM also has cross-trial ✓ but is excluded — see Downgraded below).
- **TiM**, **RecAgent**, **S³** — forgetting ✓ in the survey corpus.

## Downgraded / deprioritized (18/08/2026 session)

Recorded for traceability, not as a permanent exclusion — revisit if the project's scope changes:

- **GITM** — downgraded: no signal of genuine performance in the corpus review.
- **Role-play cluster** (persona/character agents) — deprioritized: memory form doesn't match the project's needs.
- **Medical fine-tuning cluster** — deprioritized: parametric memory form incompatible with the project's non-parametric scope decision (see [`../discussion/scope-and-terminology-decisions.md`](../discussion/scope-and-terminology-decisions.md)).
