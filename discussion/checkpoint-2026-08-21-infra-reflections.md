> **Sub-atividade:** 1.4 / 2.2 / 2.5 / 3.1 · **Type:** Cross-cutting reflection on a primary source · **Logged:** [24/08/2026](../research-diary/diario_campo_2026-08-24.md#24082026)

# Reflections on the 21/08 infra checkpoint — what it confirms, corrects, and opens

Source: [`../docs/checkpoint-2026-08-21-infra-arquitetura.md`](../docs/checkpoint-2026-08-21-infra-arquitetura.md) (filtered summary) and [`../docs/sources/Infra_dos_agentes_2026-08-21.docx`](../docs/sources/Infra_dos_agentes_2026-08-21.docx) (transcript). This is the meeting flagged as pending since [21/08](../research-diary/diario_campo_2026-08.md#21082026) — attached now.

## 1. Cross-trial vs. cross-agent gets a sharper, first-hand confirmation

[`scope-and-terminology-decisions.md#3`](scope-and-terminology-decisions.md#3-cross-trial-vs-cross-agent) and the [20/08 checkpoint reflections](checkpoint-2026-08-20-reflections.md#2-the-cross-agent-confidentiality-concern-from-1808-gets-a-real-world-confirmation) already established that agents don't share memory across each other. This meeting adds something more precise: even in an architecture with heavy agent-to-agent chaining (Manager → Workflow sub-agent → Trigger Worker tool → a whole new ECS runtime for the domain agent), the memory actually being built (Fed's LangGraph checkpoints) is explicitly scoped to one user's conversation — Yoshio's own words: *"a memória daquela execução, a memória daquele chat... não é algo que a gente está falando, que é cross memory."* So cross-agent *orchestration* (agents calling agents) and cross-agent *memory sharing* are cleanly decoupled in the actual implementation — the platform does a lot of the former and none of the latter. Useful precision for Sub 2.2: the mechanism doesn't need to solve a cross-agent memory problem that doesn't exist yet in production, only the cross-trial one.

## 2. The platform-side forgetting gap is now empirically confirmed, not just an academic finding

[`cross-trial-vs-forgetting-gap.md`](cross-trial-vs-forgetting-gap.md) is the project's central finding, built from Zhang et al.'s literature corpus: no model has both cross-trial learning and controlled forgetting. This meeting shows the exact same gap **inside the platform this project will integrate into**: Fed's Manager memory has a real cross-trial mechanism (checkpoints across a conversation, rolling incremental summarization) — and Fed's own assessment of forgetting is *"tá bem simples, a gente não consegue entrar muito no detalhe."* That's not a hypothetical literature gap anymore; it's a live gap in the actual system, acknowledged by the person building it. This is strong, concrete grounding for the M1 report's motivation section — the central finding isn't just true of a survey corpus, it's true of the specific platform the mechanism has to ship into.

## 3. LangGraph checkpointing *and* GraphRAG — both, not either/or

An earlier pass at this note (same day, before Rafael checked) downgraded the GraphRAG framing to "just LangGraph checkpointing," reasoning from the transcript alone: Fed's *verbal* description covers conversation → checkpoints → rolling summaries, a state/persistence mechanism, not an entity-graph retrieval system. That downgrade was itself premature. Rafael inspected Fed's actual code directly and confirmed a GraphRAG-style component genuinely is being built — code-level evidence beats a secondhand meeting paraphrase every time, and this note should have said "not yet confirmed" rather than actively downgrading based on the transcript alone.

The two aren't necessarily in conflict: LangGraph is an orchestration/state framework (checkpoints, threads) and doesn't preclude a graph-based *retrieval* layer (entities, relations, GraphRAG-style querying) being built inside or alongside it — Fed could plausibly be using LangGraph for the conversational state machine while implementing GraphRAG-style entity/relationship memory as the content layer within it. The transcript's "combining graph with vector search" line, read this way, may describe a component already further along than "possible future direction" suggested.

**Consequence:** the Lewis/Gao/Edge/Peng reading track in [`../papers/reading-queue.md`](../papers/reading-queue.md) reverts to its original, stronger motivation — Fed is building something GraphRAG-adjacent, confirmed at the code level, not just theorized from a meeting description. See the update to `reading-queue.md` alongside this note.

## 4. The "two signal-capture designs" open question now has a concrete second mechanism to point to

[`checkpoint-2026-08-20-reflections.md#5`](checkpoint-2026-08-20-reflections.md#5-new-scope-question-signal-capture-likely-needs-two-designs-not-one) asked whether Sub 3.1 needs separate designs for copilot/chat mode vs. systemic/event-driven mode. This meeting names the systemic path concretely: the **"Yoda" API**, which bypasses the chat frontend entirely and returns results asynchronously via the same **Kafka topic** used for slow chat responses. That's a real, existing integration point — Sub 3.1's systemic-mode signal capture would plug in at the Yoda/Kafka boundary, not somewhere theoretical. Still open: *what* signal gets attached there (there's no human tapping thumbs up/down in this path), but *where* it would technically attach is no longer an open question.

## 5. New finding: three uncoordinated memory mechanisms already coexist in the platform

Worth naming as a fact for Sub 2.2, not folded into the points above: the platform today has **three separate, non-interacting memory mechanisms** — Fed's Manager-level LangGraph checkpoints (conversation-scoped), the Small Agent's per-execution memory dump (run-scoped, stored as a DB entity distinct from Fed's graph), and Hermes' native memory (not yet detailed, pending the meeting with Adriano). None of them do cross-trial learning with controlled forgetting across cases — each is its own island. Before designing M3's mechanism, it's worth explicitly mapping these three against each other (what does each store, at what scope, queried how) rather than assuming a blank slate — the mechanism may need to sit *alongside* or *unify* existing memory, not just add a fourth island.

## 6. Minor governance note: token propagation has no centrally enforced validation

Auth today is informal: a user token is passed forward through every layer (proxy → Manager → MCP), and each application decides independently whether/how to validate it — there's no platform-enforced authorization boundary. Not urgent, but worth keeping in mind for Sub 2.5/governance once the mechanism starts reading or writing memory across these layers — an update path that assumes centralized auth would be assuming something that doesn't currently exist.

## Not investigated here

Repository-level details (which repo holds which agent, exact folder layout) are logistics for whenever Rafael actually starts building, not research findings — kept in the [docs summary](../docs/checkpoint-2026-08-21-infra-arquitetura.md) rather than analyzed here.
