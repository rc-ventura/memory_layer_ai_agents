> **Sub-atividade:** 1.1 · **Status:** Preprint · **Theme:** Surveys · **Read by Rafael:** ✅ 20/08/2026

# Memory in the Age of AI Agents

- **Authors:** Yuyang Hu, Shichun Liu, and a large multi-institution author group
- **Year:** Dec 2025
- **Venue:** arXiv:2512.13564
- **Link:** https://arxiv.org/abs/2512.13564
- **Tags:** survey, taxonomy, forms, functions, dynamics, benchmarks

## Core contribution

A very large, recent survey proposing a three-axis taxonomy — Forms (token-level, parametric, latent), Functions (factual, experiential, working), and Dynamics (formation, evolution, retrieval) — explicitly distinguishing agent memory from RAG and context engineering; compiles benchmarks and open-source frameworks. Companion list: github.com/Shichun-Liu/Agent-Memory-Paper-List.

## Relevance to the project

The most current map of the field; its "Dynamics → evolution (consolidation & forgetting)" axis is exactly the project's sub-topic, and it lists RL-integration and trustworthiness as frontiers. See [mind map 2](../literature-review/visual-synthesis/README.md#2-memory-in-the-age-of-ai-agents) for the full Forms/Functions/Dynamics/Resources-and-Frontiers taxonomy.

## Full-text confirmation (25/08/2026, agent-read directly from the PDF, not Rafael-read — even though Rafael's own earlier read is marked ✅ above)

Downloaded the full 107-page PDF and grep'd it directly (`pdftotext`) to resolve a specific question: does §4.1 Factual Memory subdivide into episodic/semantic, as the redrawn mind map's simplified "User Factual / Environment Factual" leaves ambiguous? Confirmed precisely — both are true, at different levels:

- **§4.1's own operational taxonomy is User factual / Environment factual** (entity-centric — "User factual memory... denotes facts that sustain the consistency of interactions... including identities, stable preferences, task constraints"; "Environment factual memory... document states, resource availability, capabilities of other agents"). The mind map's redraw is accurate on this point.
- **But episodic/semantic *is* discussed explicitly, as the cognitive-science grounding**, and — this is the part the mind map's two-level simplification misses — the paper treats it **not as two separate storage categories but as a processing continuum**: "Systems typically initiate this process by logging concrete interaction histories as episodic traces... Subsequent processing stages apply summarization, **reflection** (citing Park et al. 2023 — Generative Agents), entity extraction, and fact induction... raw event streams are gradually transformed into reusable semantic fact bases." Semantic memory, in this survey's own framing, *is what episodic memory becomes after reflection* — not a parallel, separately-populated store.
- **§4.2 Experiential Memory has a finer three-way split** than the mind map's four labels suggest: **Case-based** (raw episode records, for replay/exemplars), **Strategy-based** (distilled reasoning patterns/heuristics for planning), **Skill-based** (executable procedural capacities — code, API protocols) — "Hybrid" (shown in the mind map) is a combination category layered on top of these three, not a fourth peer type.
- **§7.8.1** later draws the same episodic/semantic/procedural line explicitly via Tulving (1972)/Squire (2004), noting current frameworks (Zhong et al. 2024 = MemoryBank, Park et al. 2023 = Generative Agents, Gutierrez et al. 2024 = HippoRAG) "operationalize these biological categories into engineering artifacts, where episodic memory provides autobiographical continuity and semantic memory offers generalized world knowledge" — and flags a real limitation: agent systems mostly do verbatim/RAG-style retrieval, lacking the constructive, reconstructive quality of human memory recall.

**Consequence for this project's architecture:** [`knowledge-as-infra-architecture-hypothesis.md`](../discussion/knowledge-as-infra-architecture-hypothesis.md)'s Memory Store two-tier design (raw per-case records + a distilled rules layer) is precisely this survey's episodic→semantic continuum, with the Update Engine's ExpeL-style extraction playing the role of "reflection." The distilled layer is more accurately named **strategy-based** (§4.2's term) than "skill," which the survey reserves for executable procedures — a possible future addition, not the current design.

---
Source review: [`memory-in-ai-agents.md`](../literature-review/memory-in-ai-agents.md)
