> **Sub-atividade:** 1.6 / 1.7 / 2.2 · **Type:** Comparative analysis of a primary source — hypothesis-level, based on documentation only (no code read, nothing run) · **Logged:** 12/11/2026

# The internal memory SDK vs. this project's mechanism — what it solves, what it doesn't, how to use it

**Source:** the transcription of the documentation of an internal long-term memory SDK built by [EMPRESA]'s research institute, kept in [`../../pocs/sdk-memory-docs/`](../../pocs/sdk-memory-docs/README.md). Company, product, gateway and internal-URL names are replaced with neutral placeholders there (`memory-sdk`, `MEMSDK_*`, "gateway GenAI"); this note uses the same names.

**Limit of this note:** everything below comes from the SDK's documentation, not its code. Claims about what the SDK *cannot* do (no direct write, the internal repository interface, how its judge behaves on text that is not a customer utterance) need confirmation against the code or with the SDK team before they are used to argue a design decision. The SDK also only runs with credentials for the internal GenAI gateway and the internal package index, so any experiment with it runs inside [EMPRESA]'s environment, not here.

## Short answer

The SDK does **not** solve the project's central problem: it stores a different kind of memory. It does give already-implemented, in-house answers to several **secondary design gaps** that are still open in this repo. It is usable as a **comparison arm in the POCs** and as a **design source**, not as the **substrate of the mechanism**.

## 1. The difference that decides everything: what the memory is about

| | The SDK | This project |
|---|---|---|
| Memory is about | **the customer** — name, city, marital status, preferences, banking events, life experiences | **the agent's work** — a tool's return contract, what the sandbox allows, the right strategy for a role ([`analysis/registros/esquema-memoria.json`](../../analysis/registros/esquema-memoria.json): `scope = {role, tool}`, `correction_guidance`) |
| Hu/Liu type | factual memory about the user (persona / profile) | experiential memory — case-based and strategy-based ([`knowledge-as-infra-architecture-hypothesis.md`](knowledge-as-infra-architecture-hypothesis.md) §A) |
| Learns from | the user's last message in a chat turn | the agent's trajectory: tool errors, code, observations ([`02-relatorio-achados.md`](../../analysis/2026-09-trace-law-flow/docs/02-relatorio-achados.md)) |
| Isolation unit | one collection per `user_id` | role / tool / domain, with a cross-agent reusable class still open ([`open-questions.md`](../open-questions.md), the `task-private` vs. `cross-agent-reusable` item) |
| Who decides a write | an LLM judge, every turn, then an LLM verifier and an LLM conflict checker | a deterministic filter, then a batched curator that only *proposes*, then a human-reviewed gate |
| Serves | copilot / chat agents facing a customer | systemic pipeline agents (cadastro, contestação), where there is no customer utterance to record |

Most of what follows is a consequence of this table. One sentence positions the two: **the SDK remembers the customer; the mechanism remembers the work.**

## 2. Gaps in this project that the SDK gives a concrete answer to

| Open gap in this repo | What the SDK already implements |
|---|---|
| **How the mechanism relates to the memory mechanisms already live in the platform** ([`open-questions.md`](../open-questions.md); three islands mapped in [`checkpoint-2026-08-21-infra-reflections.md`](../reflexoes/checkpoint-2026-08-21-infra-reflections.md) §5) | The SDK is **one more island, and an official one** — long-term memory from [EMPRESA]'s own institute. It has to go on that map. "Why not use the internal SDK?" now replaces "why not Mem0?" as the likely tutor question; see §6 for the answer material. |
| **The ranking for `recall_memory`** (relevance + importance + freshness, never given numbers — architecture §A, "Retrieval mechanics") | A worked, parametrized model: `W_global = B × F × Q × U × C × R` (base weight, saturating frequency, extractor confidence, user confirmation, conflict penalty, recency with a per-category half-life); retrieval **per category** with K proportional to B; **retrieval reinforcement** (distance ≤ 0.60 and a 600 s cooldown → `mention_count + 1`, refresh `last_mentioned_at`). It is the same shape the architecture composed from DMF-lite + MemoryBank + Generative Agents, with default numbers ([`07-scoring.md`](../../pocs/sdk-memory-docs/07-scoring.md)). |
| **The layer-2 governance gate** ("grounding, dedup, ACL" — named in the 01/09 consolidation, never detailed) | The verifier's rubric: 8 weighted dimensions (faithfulness 0.25, temporal fit 0.15, scope completeness, category fit, subject fit, polarity fit, atomicity, 1 − hallucination risk) plus hard caps (e.g. hallucination risk > 0.20 → score ≤ 0.60). A concrete candidate for "grounding". **Caveat:** it is an uncalibrated LLM judge; this project already records that TRAIL's best judge reaches 11% joint accuracy ([`open-questions.md`](../open-questions.md), gold-standard item) — it would have to be calibrated against the gold standard before it counts. |
| **Consolidation** (architecture §G — "no dedicated mechanism") | Deterministic **duplicate detection**: text similarity (`SequenceMatcher`) > 0.85 against the closest memory in the same category → no new record, only `mention_count + 1`. Cheap, auditable, consistent with the "no LLM on this path" principle ([`08-historico-duplicatas.md`](../../pocs/sdk-memory-docs/08-historico-duplicatas.md)). |
| **The schema of a memory that changes** (versioned commit + rollback, architecture §D/§E — no field-level design) | **Linked history**: `previous_memory_id`, `is_current`, demote-instead-of-overwrite, `conflicting_memory_ids`, and a three-step cascade to find the current node (explicit id → filter by category + key + current → similarity). A concrete schema for "update a lesson without losing the previous one". |
| **Update an existing lesson or create a new one** | A stable `subject_key` that the judge is told to reuse. Here the natural key already exists (unit + role); the part worth copying is the **reuse rule** when the curator proposes a change. |
| **Physical substrate and vector-storage category** (two of the five write-path gaps in architecture §A) | The SDK chose embedded **ChromaDB**, with a `MemoryRepository` interface + `build_repository()` factory and **pgvector** named as a planned, not-yet-available backend ([`04-persistencia.md`](../../pocs/sdk-memory-docs/04-persistencia.md)). Consistent with this project's Postgres lean, and it shows where [EMPRESA] is heading. |
| **Externalize parameters so they can become adaptive in v2** ([`open-questions.md`](../open-questions.md), static-vs-adaptive item) | Already done there: `config.yaml` → `MEMSDK_*` environment variables → a frozen `Config` per instance, with a documented precedence order. |
| **Parsing the curator's output robustly** | The judge-output normalization layer (`pipeline/actions.py`): strips markdown fences, normalizes category and key, drops invalid actions, clamps scores with a fallback. The Update Engine will need the same. |
| **"Deterministic check before any LLM"** | The temporal guard: a regex-and-marker check between retrieval and the judge, zero cost, short-circuits the turn. One more in-house data point that the "deterministic filter first" pattern of the 01/09 consolidation is how [EMPRESA] already builds. |

## 3. What the SDK does not solve

1. **The source of learning.** It learns from the user's utterance — only the last user message is the main input. The project learns from the agent's trajectory.
2. **The external signal — the "reinforcement" of the project's title** ([`scope-and-terminology-decisions.md`](../scope-and-terminology-decisions.md) §2). No thumbs (asymmetric or not), no case outcome, no downstream human correction, no per-agent-type latency model. The `U` factor exists "so that confirmed memories can gain a boost via future mechanisms" and is fixed at 1.0 today.
3. **The cadence.** LLM on every turn, on the hot path — at least three LLM calls (judge, verifier, conflict checker) plus embeddings per turn. The tutor rejected this explicitly on cost (~300k contestação runs/year; [`checkpoint-2026-08-28-reflections.md`](../reflexoes/checkpoint-2026-08-28-reflections.md) §1), and it weighs directly against the base-3 compensation test (measured saving minus injection cost).
4. **The human gate.** In the SDK the proposal *is* the write. There is no "curator proposes, gate decides", and none of the three curator triggers (scheduled, severity-weighted, human-initiated).
5. **An immutable log and rollback by replay.** The linked history is a per-topic chain, not an episodic source of truth from which the memory can be rebuilt after a bad commit.
6. **Real, audited forgetting.** Decay and conflicts only demote in the ranking; "memories extracted with low confidence never leave the base". `delete_memory` is manual and does not repair `previous_memory_id` chains. This is the same gap the project named in MemoryBank and Mem0 (architecture, "Knowledge as infra / product framing").
7. **The memory vs. harness destination.** The concept does not exist. The largest unit in base 3 — the `try/except NameError` signature, 5,764 errors — is a harness signal and would be stored as memory.
8. **Evidence and provenance.** A memory is text plus counters: no `source_trace_ids`, no occurrences, no case locations, no evidence pack.
9. **A strategy layer.** It stores atomic facts and its verifier penalizes anything that is not single-topic; a heuristic distilled from many cases is composite by nature.
10. **v1 determinism.** The write path is 100% LLM-judged; this project's v1 is static and auditable by decision.
11. **Efficacy.** Nothing measures whether a memory reduces an error — exactly the last step of the validation ladder ([`17-validacao-memorias.md`](../../analysis/2026-09-trace-law-flow/docs/17-validacao-memorias.md)) that the POCs exist to answer.
12. **Confidentiality.** Its `fixed_profile` examples include CPF; this project's PII discipline is the opposite.

## 4. How to use it

**(a) As a third arm in the POCs.** The [blueprint](../../pocs/blueprint-m1-pocs-minimos.md) compares the native closed loop (Hermes) with smolagents plus the mechanism skeleton. The SDK is a third pole: **implicit, LLM-curated per turn, and in-house.** In the recurrence experiments it would show what the company's ready-made solution delivers on the same mocked tasks. Wiring:
- `user_id` = the agent's role (e.g. `CalculoCivel`).
- `store_memories` fed with a message built from the failing step's error and code.
- A `prompts.yaml` overlay rewriting the judge's objective ("capture operational lessons about tools and environment") and the category examples.
- `get_relevant_memories` injected before each run.

Two experiments get sharper with it:
- **memory vs. harness destination** — the expectation is that it stores the harness signal, a false positive;
- **the promotion gate on trivial cases** — does its judge answer `respond_only` to the "beabá" cases?

Caveat: this is a forced fit — the judge writes third-person facts about "the user", and the five categories are fixed (an unknown category becomes `dynamic_profile`). That forced fit is itself part of the result.

**(b) As a design source for the smolagents POC.** Copy into the mechanism skeleton:
- the ranking formula and its defaults;
- the linked-history schema;
- duplicate detection;
- the verifier rubric, as a *candidate* layer-2 gate, calibrated before it counts;
- the action-normalization layer.

**(c) As a conversation with the SDK team.** Three concrete hooks:
- the **`U` factor** — the documented placeholder for "future mechanisms" of confirmation is exactly where this project's signal capture would plug in;
- the **`MemoryRepository` interface** — the extension point for a Postgres backend;
- **direct write** — whether an API that stores a memory without going through the judge exists or could exist.

**Why not as the mechanism's substrate.** By the documentation, every write goes through the SDK's own judge — the public operations are `store_memories`, `get_relevant_memories`, `get_all_memories`, `mem_count`, `delete_memory`, `clear_memories` and `chat`; there is no `add_memory(text, category, key)`. This project's gate has to be the one deciding what enters, so "the gate approved it, now store it" does not fit the SDK as documented. The fixed customer-centric categories and per-user isolation (instead of domain/RBAC) weigh against it too.

## 5. What this changes in the research

- **It confirms the thesis rather than weakening it.** [EMPRESA] already has a Mem0-style memory in-house, and it has exactly the gaps this project mapped in the literature ([`cross-trial-vs-forgetting-gap.md`](../teoria/cross-trial-vs-forgetting-gap.md)): no external signal, no gate, no real forgetting, no memory/harness distinction. The project's contribution — gate + forgetting + destination, applied to the agent's experience — reads more sharply with the SDK next to it.
- **Complementary, not competing.** The SDK serves customer-facing copilot agents; the mechanism serves systemic agents with no customer utterance.
- **The project's recall may need less than the SDK offers.** The tutor already questioned whether elaborate retrieval is needed for such a narrow scope (28/08). The project's memories have a deterministic key (role + tool), so injection could be a **scope filter, with no semantic search**. Per-category retrieval with `W_global` solves the SDK's problem (many loose facts per customer), not necessarily this one. Worth testing both retrieval forms in the POCs.

## 6. Open question created

"Why not use the internal SDK?" — tracked in [`open-questions.md`](../open-questions.md). The material for the answer is §1 and §3 of this note. What still needs checking with the SDK team or the code is in the "Limit of this note" paragraph at the top.
