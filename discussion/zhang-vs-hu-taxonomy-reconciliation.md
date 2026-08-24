> **Sub-atividade:** 1.1 · **Type:** Cross-cutting literature synthesis · **Logged:** [24/08/2026](../research-diary/diario_campo_2026-08-24.md#24082026)

# Do the two anchor surveys' taxonomies actually reconcile?

This is the "mind map dos dois surveys" comparison that had been pending since [21/08](../research-diary/diario_campo_2026-08.md#21082026) — cross-referencing [Zhang et al.'s mind map](../literature-review/visual-synthesis/README.md#1-memory-in-llm-based-agents) (Sources → Forms → Operations) against [Hu/Liu et al.'s mind map](../literature-review/visual-synthesis/README.md#2-memory-in-the-age-of-ai-agents) (Forms → Functions → Dynamics), branch by branch, instead of assuming from axis names alone whether they conflict.

**Caveat on what "verified" means here:** both mind maps are themselves redrawn recreations (see the visual-synthesis README's own note), not the primary paper text — this is a structural comparison at the mind-map level, useful for spotting real convergence/divergence, but not a substitute for close-reading either paper's actual prose if a specific branch needs to be cited precisely.

## Where they agree — and it's exactly where it matters most

**Zhang's "Memory Operations" (Writing / Management / Reading) and Hu's "Dynamics" (Formation / Evolution / Retrieval) are substantially the same lifecycle, with Hu's being a finer-grained refinement:**

| Zhang | Hu | Relationship |
|---|---|---|
| Management → Merging redundant info | Evolution → Consolidation | Same concept |
| Management → **Forgetting** | Evolution → **Forgetting** | **Identical term in both surveys** |
| Management → Reflection (high-level) | Evolution → Updating | Close overlap |
| Reading (context retrieval, similarity matching) | Retrieval (timing/intent, query construction, strategies, post-processing) | Hu splits Zhang's 2 items into 4 |
| Writing (raw storage, summarization) | Formation (semantic summarization, knowledge distillation, structured construction, latent representation, parametric internalization) | Hu splits Zhang's 2 items into 5 |

The load-bearing result: **"forgetting" is named identically in both surveys**, at the same position in the lifecycle (the management/evolution stage). That's reassuring specifically for [the cross-trial × forgetting gap finding](cross-trial-vs-forgetting-gap.md) — the two independently-taxonomized surveys agree on what forgetting *is* and where it sits, even though everything around it is organized differently.

## Where they genuinely diverge — not just different words for the same thing

- **Zhang's "Memory Sources"** (Inside-trial / Cross-trial / External Knowledge — an *origin* axis) **has no equivalent branch in Hu's taxonomy at all.** Hu doesn't organize memory by where it came from at the top level.
- **Hu's "Functions"** (Factual / Experiential / Working — a *purpose* axis, why the agent needs memory) **has no equivalent in Zhang's mind map.** Zhang's closest branch, "Necessity of Memory," has no sub-detail in the mind map to compare against.
- **"Forms" means a differently-cut thing in each survey**, despite the shared name: Zhang's Textual Form bundles structure *and* recency/retrieval-status together (Complete / Recent-cache-based / Retrieved-similarity-based) into one branch. Hu separates these cleanly — pure structure goes under Forms → Token-level (Flat / Planar / Hierarchical), while recency and retrieval behavior go under the entirely different Dynamics → Retrieval branch. Concretely: Zhang's "Recent (Cache-based)" sits conceptually closer to Hu's "Retrieval → Timing and Intent" than to anything in Hu's own "Forms" branch.
- Hu also has a whole memory-form category Zhang's binary Textual/Parametric split doesn't capture: **Latent Memory** (Generate / Reuse / Transform — memory as embeddings/vectors, neither text nor weights).

## Verdict

Not "incommensurable" — that framing (mistakenly attributed to this repo earlier in a working session, actually traceable to an unverified external memory export) overstates it. The two surveys **converge strongly on the operational/lifecycle axis** (what happens to memory over time — write/manage/read ≈ form/evolve/retrieve), which is the axis this project's mechanism actually operates on. They **diverge on the classificatory framing** around that shared core: why organize by origin (Zhang) vs. by purpose (Hu), and how finely to split "form." Mixing terminology from both without a note would still be sloppy — but the fix is a short bridging paragraph, not treating them as two separate, uncombinable vocabularies.

## Recommendation for the M1 report

Use Zhang's **Operations** (Writing/Management/Reading) as the primary organizing vocabulary — it's already the backbone of [`memory-in-ai-agents.md`](../literature-review/memory-in-ai-agents.md) and the sub-activity map — and cite Hu's **Dynamics** branch as the more granular decomposition of the same lifecycle where extra precision helps (e.g., naming *Consolidation* specifically rather than just "management" when discussing the mechanism's forgetting behavior). Don't try to reconcile Zhang's Sources with Hu's Functions — they're answering different questions (where content comes from vs. why it's needed) and can both be cited independently without conflict.
