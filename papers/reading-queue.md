# Reading Queue

Sources named in the [research diary](../research-diary/) (from cross-referencing the Zhang et al. survey's full 27-model corpus, Tables 1 & 3) but **not yet given a full atomic note** — no verified authors/venue/link have been pulled for these yet, so this file deliberately does not fabricate bibliographic details. Promote an entry to `papers/<slug>.md` (using [`_TEMPLATE.md`](_TEMPLATE.md)) once it's actually been read and verified against a primary source.

Source: diary entry [18/08/2026](../research-diary/diario_campo_2026-08.md#18082026), Sub-atividade 1.1.

## A note about what "reviewed" means here

**A note existing in `papers/` is not the same as Rafael having read the paper.** Every atomic note in this repo so far — including the ones below — was produced by verifying bibliographic facts (authors, venue, abstract, headline results) against a primary source (arXiv, proceedings page) and writing a summary from that. That is real verification work, and it's useful: it catches fake citations, wrong venues, mismatched titles. But it is **not** the close reading that produces the kind of understanding Rafael needs to defend this material to Luis Felipe or make an architecture call on top of it.

So: nothing in this file is "done" in the reading sense until Rafael says he read it. The checklist below reflects that — every item is unchecked, regardless of whether a note already exists.

## ☐ Full priority checklist — nothing read yet

All open items, ranked. **Ranking criterion** (so the order is arguable, not asserted): risco ao achado central do Entregável 1 > ganho direto de design pro mecanismo > risco de escopo/arquitetura a sinalizar antes de adotar > leitura complementar/de fechamento de quadro. **📝 = nota já existe** (verificada por Claude, não é leitura); marque o checkbox só quando Rafael efetivamente ler.

- [ ] **1. SAGE** (arXiv:2409.00872) — protege o [achado central](../discussion/cross-trial-vs-forgetting-gap.md): risco de precisar de ressalva no Entregável 1. *Detalhe → [rodada 2](#priority-reading-list--rodada-2-19082026).*
- [ ] **2. Memento** (arXiv:2508.16153) — maior ganho de design isolado: candidato mais forte até agora pra conciliar RL com memória não-paramétrica. *Detalhe → [rodada 2](#priority-reading-list--rodada-2-19082026).*
- [ ] **3. Mem-α** (arXiv:2509.25911) — checagem de risco de escopo antes de citar como inspiração. *Detalhe → [rodada 2](#priority-reading-list--rodada-2-19082026).*
- [ ] **4. ExpeL** 📝 (arXiv:2308.10144) — protocolo de extração de insight sucesso/falha → vocabulário de operações pro Sub 3.2.
- [ ] **5. MemoryBank** 📝 (arXiv:2305.10250) — decay tipo Ebbinghaus, resolve o buraco de forgetting.
- [ ] **6. Generative Agents** 📝 (arXiv:2304.03442) — gatilho de reflexão + score recency/importance/relevance.
- [ ] **7. SCM** 📝 (arXiv:2304.13343) — memory controller dedicado, mapeia direto pro "controlado" do título do projeto.
- [ ] **8. Retroformer** 📝 (arXiv:2308.02151) — único caso de RL literal (policy gradient) do corpus, âncora do Sub 1.3.
- [ ] **9. Synapse** — completa o quadro cross-trial ✓ do corpus Zhang et al., sem nota ainda.
- [ ] **10. MetaGPT** — idem, cross-trial ✓, sem nota ainda.
- [ ] **11. TiM** — completa o quadro forgetting ✓ do corpus, sem nota ainda.
- [ ] **12. RecAgent** — idem, forgetting ✓, sem nota ainda.
- [ ] **13. S³** — idem, forgetting ✓, sem nota ainda.

**Fora do checklist ativo, por design:** GraphRAG/G-Memory (bloqueados por Sub 1.4 — ver [condicional](#priority-reading-list--rodada-2-19082026)), o survey de forgetting fev/2026 e o catálogo de políticas dez/2025 (sem arXiv ID confirmado ainda), e GITM (já descartado — ver [downgraded](#downgraded--deprioritized-18082026-session)).

## Notes that already exist (📝 verified, not read)

Items 4–8 above already have a full atomic note in `papers/` — the bibliographic facts are verified, but reading is still open:

| Model | Note | Why it was queued |
|---|---|---|
| **ExpeL** | [`expel-2024.md`](expel-2024.md) | Success/failure insight-extraction protocol → feeds the operation vocabulary for Sub 3.2 |
| **MemoryBank** | [`memorybank-2023.md`](memorybank-2023.md) | Ebbinghaus-style decay, fills the forgetting gap |
| **Generative Agents** | [`generative-agents-2023.md`](generative-agents-2023.md) | Reflection trigger + recency/importance/relevance score |
| **SCM** | [`scm-2023.md`](scm-2023.md) | Dedicated memory controller — maps directly onto the "controlado" in the project's title |
| **Retroformer** | [`retroformer-2024.md`](retroformer-2024.md) | The corpus's only case of literal RL — anchor for Sub 1.3 |

## Priority reading list — rodada 2 (19/08/2026)

Consolidado e ordenado por urgência — não por ordem de descoberta. Verificação rápida feita antes de entrar aqui: os três arXiv IDs abaixo foram confirmados contra a página do arXiv (título e tema batem com o que está descrito; Memento tem uma ressalva de título, ver a linha dele) — **isso é verificação, não leitura**, ver a seção acima.

| Prioridade | Paper | Onde focar a leitura | Pergunta específica que resolve | O que essa resposta decide |
|---|---|---|---|---|
| **1** | **SAGE** (Liang et al., set/2024, arXiv:2409.00872) | Seção de protocolo experimental — não o método, não a arquitetura | Os insights da LTM formados numa tarefa são reaproveitados numa tarefa **diferente e posterior** (cross-trial real), ou o "multi-tasking" do abstract é só lidar com várias coisas dentro de uma sessão longa (working memory bem gerida)? | Se a interseção cross-trial × forgetting no [achado central](../discussion/cross-trial-vs-forgetting-gap.md) continua vazia, ou se precisa de uma frase de ressalva/diferenciação no Entregável 1 |
| **2** | **Memento** (Zhou et al., ago/2025, arXiv:2508.16153) | Seção de método — como a política de seleção de casos é treinada, e como a memória episódica escreve/descarta casos | A escrita/descarte na memória episódica é **explícita e controlável**, ou implícita dentro do loop de RL? E o reward que treina a política de seleção vem de um sinal externo (tipo revisão humana/área usuária, o que o projeto usa) ou só de correctness fim-a-fim? | Se vira referência arquitetural direta pro Sub 2.2 — RL sobre um controlador de seleção, sem tocar no LLM nem no formato textual/não-paramétrico da memória. Nota de verificação: título aparece como "AgentFly" em uma indexação secundária (mesmo arXiv ID) — confirmar versão exata antes de citar formalmente; repo oficial usa "Memento". Resultado reportado: top-1 no GAIA validation (87,88% Pass@3). |
| **3** | **Mem-α** (Wang et al., set/2025, arXiv:2509.25911) | Seção de método — especificamente o que o RL atualiza | O reward/gradiente atualiza os **pesos do agente** (RL de política, mesma categoria de [Retroformer](retroformer-2024.md)/[Memory-R1](memory-r1-2025.md)), ou treina um **controlador separado** enquanto o conteúdo da memória segue sendo texto puro? | Se cita como inspiração conceitual sem risco de escopo, ou se adotar como base implica um salto de arquitetura (SFT/QLoRA → RL de política) que precisa passar pelo Luis Felipe antes de qualquer coisa — ver [`../discussion/scope-and-terminology-decisions.md`](../discussion/scope-and-terminology-decisions.md) |

**Condicional, não agora — só se Sub 1.4 fechar num sentido específico:**

GraphRAG (Edge et al.) ou G-Memory viram leitura ativa **somente se** o fluxo jurídico-alvo exigir navegação entre evidência bruta e síntese de nível mais alto (pergunta em aberto — ver [`../discussion/open-questions.md`](../discussion/open-questions.md)). Antes disso fechar, ler qualquer um dos dois é esforço sem alvo — não dá pra saber ainda se hierarchical é sequer relevante pro caso.

**No radar, não é pra ler agora:**

Um survey de fev/2026 com seção dedicada a forgetting, e um paper de dez/2025 catalogando seis políticas de forgetting distintas — registrados aqui porque existem e porque confirmam que o campo publicou mais coisa relevante a essa lacuna específica nos últimos meses do que em todo 2024. Sem título/arXiv ID confirmado ainda — não têm pergunta pendente amarrada a eles. Viram candidatos quando (e se) a parte de desenhar o mecanismo de forgetting propriamente dito (Sub 2.2/3.2) começar.

## Other candidates surfaced, not urgent (20/08/2026)

Found while Rafael was reading "Memory in the Age of AI Agents" (arXiv:2512.13564) — real, verified, relevant, but not blocking any specific open decision the way the checklist items above are. No specific question is attached because none is needed yet; promote to a full atomic note whenever convenient, no particular urgency.

- **Kim, Cochez, François-Lavet, Neerincx, Vossen — "A Machine with Short-Term, Episodic, and Semantic Memory Systems"** (AAAI 2023, pp. 48–56, DOI 10.1609/AAAI.V37I1.25075; arXiv:2212.02098). A DQN-based (literal RL) agent that learns, inside a custom RL environment called "the Room," whether an aging short-term memory should be forgotten or promoted to episodic or semantic memory, to maximize return on a question-answering task. Directly operationalizes the exact short/long-term + episodic/semantic taxonomy named in the project's own Sub 1.1 description — and it's a sixth RL flavor the corpus didn't have yet: RL over **tier-routing decisions** (which store a memory goes to), distinct from RMM (retrieval reranking), Memory-R1 (write operations), Retroformer (prompt adaptation), and Mem-α (target unconfirmed). Code: github.com/humemai/explicit-memory. First surfaced by Rafael from a citation inside 2512.13564 ("Room," Kim et al., 2023b) that needed the full reference before it could be identified — resolved 20/08/2026.
- **Westhäußer, Minker, Zepf — "Enabling Personalized Long-term Interactions in LLM-based Agents through Persistent Memory and User Profiles"** (2025, arXiv:2510.07925). A framework integrating persistent memory, dynamic coordination, self-validation, and evolving user profiles for personalized long-term agent interactions. Cited by 2512.13564 under both "long-horizon/life-long agents" and "user-specific personalization" — relevant to the project's persistence-across-sessions requirement, but not urgent since no specific open question is riding on it.

## Named in the cross-trial × forgetting gap analysis, no note yet

From the full-corpus cross-reference behind [`../discussion/cross-trial-vs-forgetting-gap.md`](../discussion/cross-trial-vs-forgetting-gap.md) — models with cross-trial ✓ or forgetting ✓ in the Zhang et al. survey's Tables 1/3 that don't yet have an atomic note here (and, like everything above, haven't been read yet either):

- **Synapse**, **MetaGPT** — cross-trial ✓ in the survey corpus (GITM also has cross-trial ✓ but is excluded — see Downgraded below).
- **TiM**, **RecAgent**, **S³** — forgetting ✓ in the survey corpus.

## Downgraded / deprioritized (18/08/2026 session)

Recorded for traceability, not as a permanent exclusion — revisit if the project's scope changes:

- **GITM** — downgraded: no signal of genuine performance in the corpus review.
- **Role-play cluster** (persona/character agents) — deprioritized: memory form doesn't match the project's needs.
- **Medical fine-tuning cluster** — deprioritized: parametric memory form incompatible with the project's non-parametric scope decision (see [`../discussion/scope-and-terminology-decisions.md`](../discussion/scope-and-terminology-decisions.md)).
