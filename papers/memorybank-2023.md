> **Sub-atividade:** 1.1 · **Status:** Peer-reviewed · **Theme:** Update, consolidation & forgetting · **Read by Rafael:** partial — §2.1 Storage, §2.2 Retrieval, §2.3 Forgetting read 27/08/2026 (see "Nota do Rafael" sections below); introduction/experiments/eval sections not yet read

# MemoryBank: Enhancing Large Language Models with Long-Term Memory

- **Authors:** Wanjun Zhong, Lianghong Guo, Qiqi Gao, Yanlin Wang, Yan Wang
- **Year:** 2023/2024
- **Venue:** arXiv:2305.10250; AAAI 2024 (DOI 10.1609/aaai.v38i17.29946)
- **Link:** https://arxiv.org/abs/2305.10250
- **Code:** https://github.com/zhongwanjun/MemoryBank-SiliconFriend (SiliconFriend companion chatbot — the demo implementation described in the paper)
- **Tags:** forgetting, decay, ebbinghaus, faiss, priority-read

## Core contribution

Hierarchical event-based memory with an updating mechanism inspired by the Ebbinghaus forgetting curve — memories are reinforced on recall and decay over time; retrieval via FAISS dense representations; demonstrated in the SiliconFriend companion chatbot.

## Relevance to the project

The canonical forgetting/decay mechanism; a legal agent needs controlled decay so superseded law fades while durable doctrine is reinforced. Priority-reading anchor #2 in the [18/08/2026 diary entry](../research-diary/diario_campo_2026-08.md#18082026) — "resolve o buraco de forgetting."

## §2.1 "Memory Storage: The Warehouse of MemoryBank" — verbatim excerpt (p.3)

Added 27/08/2026. Quoted **verbatim** from the paper (arXiv:2305.10250, p.3). This specific passage is on record; the rest of the paper is still 🔎 (agent-read via sub-agent), not Rafael-read. Reflection kept in the separate section below.

> Memory storage, the warehouse of MemoryBank, is a robust data repository holding a meticulous array of information. As shown in Fig. 1, it stores daily conversations records, summaries of past events, and evolving assessments of user personalities, thereby constructing a dynamic and multi-layered memory landscape.
>
> **In-Depth Memory Storage:** MemoryBank's storage system captures the richness of AI-user interactions by recording multi-turn conversations in a detailed, chronological fashion. Each piece of dialogue is stored with timestamps, creating an ordered narrative of past interactions. This detailed record not only aids in precise memory retrieval but also facilitates the memory updating process afterwards, offering a detailed index of conversational history.
>
> **Hierarchical Event Summary:** Reflecting the intricacies of human memory, MemoryBank goes beyond mere detailed storage. It processes and distills conversations into a high-level summary of daily events, much like how humans remember key aspects of their experiences. We condense verbose dialogues into a concise daily event summary, which is further synthesized into a global summary. This process results in a hierarchical memory structure, providing a bird's eye view of past interactions and significant events. Specifically, taken previous daily conversations or daily events as input, we ask the LLMs to summarize daily events or global events with the prompt "Summarize the events and key information in the content [dialog/events]".
>
> **Dynamic Personality Understanding:** MemoryBank focuses on user personality understanding. It continuously assesses and updates these understandings with the long-term interactions and creates daily personality insights. These insights are further aggregated to form a global understanding of the user's personality. This multi-tiered approach results in an AI companion that learns, adapts, and tailors its responses to the unique traits of each user, enhancing user experience. Specially, taken the daily conversations or personality analysis, we ask the LLM to deduce with prompts: "Based on the following dialogue, please summarize the user's personality traits and emotions.[dialog]" or "The following are the user's exhibited personality traits and emotions throughout multiple days. Please provide a highly concise and general summary of the user's personality[daily Personalities]".

## Reflection — MemoryBank's storage vs. the Component A sketch

Added 27/08/2026. Based only on the §2.1 excerpt above. The "does differently" column is the current sketch, not a closed decision.

**What the passage describes:** a three-layer store — (1) raw multi-turn record, chronological + timestamped, feeding both retrieval and the later update step; (2) event summary, LLM-generated at ingest on a daily → global cadence; (3) user personality model, same daily → global LLM aggregation, continuously refreshed. Raw layer append-only; the two derived layers overwritten in place. The "LLM" doing (2) and (3) is the agent's own backbone via a separate prompt — no model trained for memory.

**What Component A does the same:**
- A raw per-case record as the base layer, kept minimally processed.
- That raw layer feeds both retrieval (`recall_memory`) and the update step.
- A layered structure: raw → distilled.
- Vector-indexed retrieval.

**What it does differently / not (current sketch):**
- No LLM summarisation on the write path — distillation is deferred to the batched cold path (Update Engine), not done at ingest.
- No fixed daily cadence — the distil/update trigger is event/severity-driven.
- Raw layer immutable and the derived (strategy) layer versioned — not overwritten in place.
- No user/personality model — only case/experience content; entity facts sit outside Component A.
- Two tiers only — no separate descriptive "event summary" layer between raw and strategy.

## §2.2 "Memory Retrieval" — verbatim excerpt

Added 27/08/2026. Quoted **verbatim** from the paper (arXiv:2305.10250, §2.2). Reflection in the separate section below.

> Built on the robust infrastructure of memory storage, our memory retrieval mechanism operates akin to a knowledge retrieval task. In this context, we adopt a dual-tower dense retrieval model similar to Dense Passage Retrieval (Karpukhin et al., 2020). In this paradigm, every turn of conversations and event summaries is considered as a memory piece m, which is pre-encoded into a contextual representation h_m using the encoder model E(·). Consequently, the entire memory storage M is pre-encoded into M = {h⁰_m, h¹_m, ...h^|M|_m}, where each h_m is a vector representation of a memory piece. These vector representations are then indexed using FAISS (Johnson et al., 2019) for efficient retrieval. Parallel to this, the current context of conversation c is encoded by E(·) into h_c, which serves as the query to search M for the most relevant memory. In practice, the encoder E(·) can be interchanged to any suitable model.

## Reflection — MemoryBank's retrieval vs. the Component A sketch

Added 27/08/2026. Based only on the §2.2 excerpt above. The "does differently" column is the current sketch, not a closed decision.

**What the passage describes:** dense **dual-tower** retrieval (DPR-style). The unit is a *memory piece* = one conversation turn **or** one event summary. Every piece is pre-encoded offline by an encoder `E(·)` and indexed in FAISS; the query is the current conversation context, encoded by the same `E(·)`; retrieval returns the nearest vectors ("the most relevant memory"). This passage is **pure semantic similarity** — decay (§2.3) is a separate mechanism. The encoder is swappable.

**What Component A does the same:**
- Dense vector retrieval over pre-encoded items, FAISS-style index.
- Query = encode the current context, nearest-neighbour search.
- Raw records and distilled entries share one retrievable space (MemoryBank: turns + event summaries; sketch: episodic traces + strategy entries, one `recall_memory` call).
- The encoder is a swappable component.

**What it does differently / not (current sketch):**
- Not pure top-k similarity — the sketch adds a **freshness/recency + access-control gate** and a **re-rank by relevance + importance** on top of the vector search.
- No access control in MemoryBank; the sketch has an ACL gate (still undefined).
- MemoryBank ranks by query similarity alone; the sketch reuses the write-time importance score in ranking.
- "Memory piece" fixed at one turn / one summary; the sketch has not fixed the unit of an episodic trace.
- Query is "the current conversation context"; in the tool-call design the query is whatever the agent explicitly passes to `recall_memory`, not the raw rolling context.

## §2.3 "Memory Updating Mechanism" — verbatim excerpt (forgetting principles)

Added 27/08/2026. Quoted **verbatim** from the paper (arXiv:2305.10250, §2.3). This is the *principles* part; the formula that operationalises them (`R = e^(−Δt/S)`, `S → S+1` on recall) is elsewhere in the same section. Reflection below.

> Forgetting less important memory pieces that are long time ago and have not been recalled much can make the AI companion more natural. Our memory forgetting mechanism is inspired from Ebbinghaus Forgetting Curve theory and follow the following principle rules:
>
> • **Rate of Forgetting.** Ebbinghaus found that memory retention decreases over time. He quantified this in his forgetting curve, showing that information is lost rapidly after learning unless it is consciously reviewed.
> • **Time and Memory Decay.** The curve is steep at the beginning, indicating that a significant amount of learned information is forgotten within the first few hours or days after learning. After this initial period, the rate of memory loss slows down.
> • **Spacing Effect.** Ebbinghaus discovered that relearning information is easier than learning it for the first time. Regularly revisiting and repeating the learned material can reset the forgetting curve, making it less steep and thereby improving memory retention.

## Reflection — MemoryBank's forgetting vs. the Component A sketch

Added 27/08/2026. Based only on the §2.3 excerpt above. The "does differently" column is the current sketch, not a closed decision.

**What the passage describes:** the *principles* behind the forgetting mechanism — three Ebbinghaus rules: retention falls over time unless reviewed; the curve is steep early then flattens; recall resets the curve (spacing effect). Stated motivation: drop old, rarely-recalled, low-importance pieces so the companion feels "more natural."

**What Component A does the same:**
- Time-based retention decay, Ebbinghaus-inspired — a settled requirement (component E).
- Steep-then-flat curve shape is exactly what is under consideration (MemoryBank's exponential, or SSGM's Weibull whose `κ` tunes the shape).
- Reinforcement on recall (spacing effect) — recalled items get their decay reset / strengthened.
- "Old + rarely recalled + low importance → forget" — the sketch ranks down and eventually removes on the same three inputs.

**What it does differently / not (current sketch):**
- Motivation is **auditability**, not naturalness — provable expiry of stale content, with a logged reason.
- MemoryBank only de-prioritises in retrieval ranking (no hard delete) — so **storage grows monotonically**: an old, un-recalled item has `R ≈ 0` (functionally invisible) but is never removed, and nothing in the mechanism bounds store size (not stress-tested — ~10-day eval). The sketch adds a **hard-delete below `θ2`, with a logged reason**.
- Tier 1 is the immutable source of truth — deletion is allowed but must be logged; content is never silently rewritten.
- MemoryBank's "importance" is essentially recall frequency (`S` counts recalls); the sketch's importance is a deterministic write-time score from structured signals, not just popularity.
- Decay function not fixed — MemoryBank commits to plain exponential; the sketch keeps Weibull on the table for per-memory-class shaping.

## Nota do Rafael — o caráter do mecanismo (27/08/2026)

Lendo §2.1 e §2.2:

> MemoryBank, pelo que parece, usa muito a questão da memória de sessão (short-term): a memória da sessão é armazenada e sumarizada. Então aqui não temos uma tool, nem nenhum sistema de escolha — apenas uma LLM que sumariza a memória de sessão em event summaries e user personalities.

(Retrieval e forgetting confirmam a leitura: similaridade vetorial pura + decay por fórmula de Ebbinghaus, sem controller e sem hard-delete. Obs.: não há split STM/LTM explícito — isso é do SAGE; aqui é uma store de conversa única, escopada a um usuário.)

## Nota do Rafael — ideia de design a partir do forgetting do MemoryBank (27/08/2026)

> Então nossa arquitetura pode ter um sistema de hard delete por decaimento — a partir de um threshold, hard delete. Ou ainda ter um componente de **consolidation** que analisa dedup e apaga memórias antigas.
>
> A ideia central: **o Memory Store não atua apagando — ele só decai.** Quem faz a gestão de deleção é outro componente (de repente o Update Engine). Porque aí teríamos um **gate**: por exemplo, "posso apagar isso?" (Update Engine) → ativa o gate de revisão humana.

(Implicação: isso moveria o hard-delete de uma ação automática por threshold — como o componente E está esboçado hoje — para uma ação **gated e revisada**, dona de outro componente. Propagado em 27/08 pro doc de arquitetura, componentes [E](../discussion/knowledge-as-infra-architecture-hypothesis.md#e-forgetting--decay-plus-a-real-delete-step) e [G](../discussion/knowledge-as-infra-architecture-hypothesis.md#g-consolidation--an-open-gap-in-evolution-not-yet-a-designed-component-added-25082026), e pro [`open-questions.md`](../discussion/open-questions.md).)

---
Source review: [`memory-in-ai-agents.md`](../literature-review/memory-in-ai-agents.md)
