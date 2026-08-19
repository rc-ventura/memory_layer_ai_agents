> **Sub-atividade:** 1.1 / 1.3 / 3.6 · **Type:** Decision log · **Logged:** [18/08/2026](../research-diary/diario_campo_2026-08.md)

# Scope and terminology decisions

A running log of scoping/terminology calls made during the literature review, each traceable back to a diary entry. Update this file (don't just append to the diary) when a decision here gets revisited.

## 1. Memory form: non-parametric, by design

**Decision:** the project's vocabulary (Objetivo, Sub 2.2, Sub 3.2 — "instruções, exemplos e contexto operacional armazenados na memória") is textual/non-parametric. Parametric memory-editing methods (MEND, KnowledgeEditor, PersonalityEdit, APP, MAC) are **out of implementation scope**.

**Where they still belong:** as "alternative considered and rejected" in the Sub 2.2 architecture document — not simply dropped from the review. See the "Parametric Form" branch (Fine-tuning vs. Knowledge Editing) in mind map 1 of [`../literature-review/visual-synthesis/README.md`](../literature-review/visual-synthesis/README.md) for the framing this decision is reacting to.

## 2. What "reinforcement learning" means in this project's title

**Decision:** **Reflexion** ([`../papers/reflexion-2023.md`](../papers/reflexion-2023.md)) is probably the origin of "aprendizado por reforço" in the project's title ("verbal reinforcement learning") — but it is **not literal RL**: no reward model, no policy gradient, just textual self-critique concatenated to the prompt.

**Retroformer** and **Memory-R1** ([`../papers/memory-r1-2025.md`](../papers/memory-r1-2025.md)) are the corpus's genuine literal-RL cases (PPO/GRPO fine-tuning against a reward signal).

**Open item:** the Plano needs to explicitly state, somewhere in Sub 1.3 or 1.7, which sense of "RL" the mechanism actually implements. **Not yet done** — see [`open-questions.md`](open-questions.md).

## 3. Cross-trial vs. cross-agent

**Decision:** these are different boundaries, not synonyms.

- **Cross-trial** = a time boundary. Same agent, separate invocations (e.g., a new chat session reading a preference recorded in an old chat session on the same project).
- **Cross-agent** = an identity boundary. Distinct agents exchanging information via a protocol (e.g., triagem → redação → compliance handoffs between specialized agents in the same flow).

**Supporting fact:** the Agent Communication Protocol (IBM) was absorbed into the Agent2Agent Protocol (Google) under the Linux Foundation in August 2025 — it no longer exists as a separate spec.

**Consequence:** this narrows the scope of the confidentiality concern originally flagged for Macroatividade 2. It applies specifically to **handoffs between distinct specialized agents within the same flow**, not to a single agent's persistence between its own sessions.

## 4. Direct-evaluation benchmark dating correction

**What the survey says:** Zhang et al. (§6.3, submitted 21/04/2024) states that, at the time, no dedicated open-source benchmark existed for direct, isolated evaluation of memory modules.

**Correction:** that gap closed within months. **LoCoMo** (Maharana et al., arXiv:2402.17753, 27/02/2024) — published ~2 months *before* the survey but absent from its references, likely because the survey's literature cutoff predates late February 2024 — and **LongMemEval** became the de facto standard through 2025–2026 (Mem0, DMF, A-Mem, and Memory-R1 are all evaluated on them).

**Caveat that must travel with any citation of the original claim:** LoCoMo/LongMemEval are mostly **indirect** evaluation (end-to-end QA accuracy), not pure Reference Accuracy (retrieval vs. gold standard, independent of the final answer). A benchmark isolating pure retrieval quality still doesn't dedicatedly exist. Citing the Zhang et al. sentence without this correction would contradict the project's own bibliography.

**Consequence:** this is what motivated decision #5 below.

## 5. Reference Accuracy metric — scope (Sub 3.6)

**Decision:** Reference Accuracy (F1 between what the mechanism retrieved and an annotated gold standard) enters Sub 3.6 as a **fourth metric**, in **restricted scope**: gold annotations built manually over cases from the project's own legal flow, **not** a generalizable LoCoMo/LongMemEval-style benchmark. A dedicated benchmark would be overengineering — it fights the project's own reframing (reusable library → integrated Itaú platform functionality) and doesn't fit Macroatividade 3's already-compressed timeline.

**Why it can't be implemented yet:** "what should have been retrieved" only exists once the target legal flow (Sub 1.4) and correctness criteria (Sub 1.5) are defined. Annotating a gold standard for a flow that hasn't been chosen yet cannot work.

**Status:** blocked by Sub 1.4 and Sub 1.5, not by an open scope question — mark as ready to implement the moment those two close.
