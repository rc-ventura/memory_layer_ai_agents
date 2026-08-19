> **Sub-atividade:** 1.1 · **Type:** Achado (finding) · **Logged:** [18/08/2026](../research-diary/diario_campo_2026-08.md#achado--lacuna-cross-trial--forgetting-confirmada-no-corpus-completo)

# The cross-trial × forgetting gap

## The finding

Cross-referencing Table 1 (cross-trial ✓) against Table 3 (Forgetting ✓) of the Zhang et al. survey ([`../papers/zhang-2025-memory-survey.md`](../papers/zhang-2025-memory-survey.md)) across the **full 27-model corpus** — not just the 4 "full-source" models from a first pass — produces a clean, exhaustive split:

| Has **cross-trial** ✓ | Has **forgetting** ✓ |
|---|---|
| [Retroformer](../papers/retroformer-2024.md), [ExpeL](../papers/expel-2024.md), Synapse, GITM, [Reflexion](../papers/reflexion-2023.md), MetaGPT | [MemoryBank](../papers/memorybank-2023.md), TiM, [Generative Agents](../papers/generative-agents-2023.md), RecAgent, S³ |
| **6 models** | **5 models** |

*(Synapse, GITM, MetaGPT, TiM, RecAgent, S³ remain unreviewed — see [`../papers/reading-queue.md`](../papers/reading-queue.md).)*

**The intersection of these two sets is empty.** No model in the surveyed corpus has both cross-trial learning and controlled forgetting. This was confirmed exhaustively over the whole corpus, not observed as a tendency in a partial sample.

## Why it matters

This is a central finding for the Sub-1.1 deliverable (Entregável 1): **the models that learn from experience across different cases have no controlled forgetting, and the models that forget have no cross-case learning.** That is exactly the gap Macroatividade 3's memory-update mechanism proposes to fill — a mechanism that both accumulates cross-trial experience *and* forgets it in a controlled way.

## Reading correction this depends on

Table 1 (memory sources) answers *where content comes from*, not *how content gets updated* — which is what the project's Objetivo actually asks. The right axis for everything downstream is **operations** (Table 3: writing/management/reading — merging, reflection, forgetting), not source. This reframing is what made the gap visible in the first place; see the "Implementation Strategies" branch (Sources → Forms → Operations) in mind map 1 of [`../literature-review/visual-synthesis/README.md`](../literature-review/visual-synthesis/README.md).

## Status

Registered as an explicit finding, citing the full table (not the earlier 4-model sample observation), in the Sub-1.1 deliverable. Reading priorities were set directly off this gap — see [`../papers/reading-queue.md`](../papers/reading-queue.md). The top-5 priority order (ExpeL, MemoryBank, Generative Agents, SCM, Retroformer) all have Claude-verified notes as of 19/08/2026, but **none have actually been read by Rafael yet** — that's a separate, still-open step tracked on the reading checklist.
