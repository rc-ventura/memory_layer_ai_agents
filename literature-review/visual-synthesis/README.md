# Visual Synthesis — "The Memory Mechanism of LLM-Based Agents"

**File:** [`agent-memory-blueprint.pdf`](agent-memory-blueprint.pdf) (15 pages)
**Generated with:** Gemini Notebook, synthesized from *"A Survey on the Memory Mechanism of Large Language Model based Agents"* (Zhang et al., 2024 — see the full entry in [`../memory-in-ai-agents.md`](../memory-in-ai-agents.md#theme-4-highlighted-first--survey--review-papers-on-memory-in-llm-agents) and the atomic note at [`../../papers/zhang-2025-memory-survey.md`](../../papers/zhang-2025-memory-survey.md)).
**Logged:** diary entry [18/08/2026](../../research-diary/diario_campo_2026-08.md#18082026), Sub-atividade 1.1.

A slide-style infographic companion to the Zhang et al. taxonomy — useful as a quick-reference/teaching aid distinct from the prose review. Page-by-page index below (one line per page, so it's searchable without opening the PDF):

| # | Title | Content |
|---|---|---|
| 1 | *The Memory Mechanism of LLM-Based Agents* | Cover page. Subtitle: "A Comprehensive Survey on the Architecture of Artificial Cognition." |
| 2 | From Stateless Generators to Evolving Agents | Contrasts static LLMs (isolated tasks, no adaptation) with evolving agents (autonomous exploration, feedback-driven learning) — memory as the transition mechanism. |
| 3 | Expanding the Scope of Artificial Memory | Narrow sense (current trial: the sequential ξₜ = {a₁,o₁,…,aₜ₋₁,oₜ₋₁} history) vs. broad sense (lifespan & external: accumulation across past trials + injected external knowledge). |
| 4 | The Three Pillars of Agent Cognition | Cognitive Psychology, Self-Evolution, Application Necessity — the three motivations for memory, framed as pillars supporting "Autonomous Intelligence." |
| 5 | Deconstructing the Memory Architecture | Master diagram: Sources (inside-trial / cross-trial / external) → Forms (textual / parametric) → Operations (reading / writing / management). This is the same three-part taxonomy behind the mind-map shared with the coordinator. |
| 6 | Three Streams of Artificial Experience | Detail on Sources: inside-trial information (immediate, narrow), cross-trial information (long-term experiential data, common patterns, failed strategies), external knowledge (real-time facts via APIs) — all feeding the "Agent Memory Pool." |
| 7 | Storing Memories as Explicit Natural Language | Detail on textual form: Complete Interactions (full concatenation), Recent Interactions (sliding window / locality), Retrieved Interactions (vector/SQL similarity search), External Knowledge (tool-injected text). |
| 8 | Encoding Memories Implicitly into Model Weights | Detail on parametric form: Fine-Tuning (SFT — powerful, costly, risks catastrophic forgetting) vs. Knowledge Editing (targeted, lower-overhead, precise online updates). |
| 9 | Evaluating Memory Storage Paradigms | Textual vs. parametric compared on Effectiveness, Efficiency, and Interpretability — textual wins interpretability, parametric wins read-cost. |
| 10 | The Agent-Environment Interaction Loop | Formalizes Write / Manage / Read as equations: mₜᵏ = W({aₜᵏ,oₜᵏ}), Mₜᵏ = P(Mₜ₋₁ᵏ, mₜᵏ), M̂ₜᵏ = R(Mₜᵏ, cₜ₊₁ᵏ). |
| 11 | Abstracting Raw Data into Intelligence | Detail on Management: Merging (reduce redundancy), Reflection (abstract high-level rules from raw observations), Forgetting (discard unimportant/outdated content). |
| 12 | Proving the Efficacy of Artificial Memory | Evaluation framework: Direct (Subjective — coherence/rationality; Objective — correctness/F1/cost) vs. Indirect (Conversation consistency, Multi-Source QA, Long-Context retrieval & summarization). |
| 13 | Memory at Work Across Industries | Applications: Social Simulation & Role-Playing, Personal Assistants, Open-World Games, Code Generation, Recommendation Systems, Expert Systems (Med/Fin). |
| 14 | Navigating the Frontiers of Agent Cognition | Future directions: Parametric Advances, Multi-Agent Systems (sync/asymmetry), Lifelong Learning (overlap/temporality/selective forgetting), Humanoid Agents (aligning memory flaws with human psychology). |
| 15 | Closing | Elie Wiesel quote on memory and civilization; closing statement: "Memory is the architecture of artificial experience." |

## Reading note

This deck maps directly onto the **Sources → Forms → Operations** structure used throughout [`../memory-in-ai-agents.md`](../memory-in-ai-agents.md) and the [sub-activity map](../../docs/sub-activity-map.md). Pages 5–12 in particular are a faster way to re-orient on the taxonomy than re-reading the prose review, which is why it's kept as a first-class artifact here rather than just an attachment.
