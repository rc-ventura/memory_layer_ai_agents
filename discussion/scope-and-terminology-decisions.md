> **Sub-atividade:** 1.1 / 1.3 / 3.6 · **Type:** Decision log · **Logged:** [18/08/2026](../research-diary/diario_campo_2026-08.md), updated [20/08/2026](../research-diary/diario_campo_2026-08.md)

# Scope and terminology decisions

A running log of scoping/terminology calls made during the literature review, each traceable back to a diary entry. Update this file (don't just append to the diary) when a decision here gets revisited.

## 1. Memory form: non-parametric, by design

**Decision:** the project's vocabulary (Objetivo, Sub 2.2, Sub 3.2 — "instruções, exemplos e contexto operacional armazenados na memória") is textual/non-parametric. Parametric memory-editing methods (MEND, KnowledgeEditor, PersonalityEdit, APP, MAC) are **out of implementation scope**.

**Where they still belong:** as "alternative considered and rejected" in the Sub 2.2 architecture document — not simply dropped from the review. See the "Parametric Form" branch (Fine-tuning vs. Knowledge Editing) in mind map 1 of [`../literature-review/visual-synthesis/README.md`](../literature-review/visual-synthesis/README.md) for the framing this decision is reacting to.

## 2. What "reinforcement learning" means in this project's title

**Decision:** **Reflexion** ([`../papers/reflexion-2023.md`](../papers/reflexion-2023.md)) is probably the origin of "aprendizado por reforço" in the project's title ("verbal reinforcement learning") — but it is **not literal RL**: no reward model, no policy gradient, just textual self-critique concatenated to the prompt.

**Retroformer** and **Memory-R1** ([`../papers/memory-r1-2025.md`](../papers/memory-r1-2025.md)) are the corpus's genuine literal-RL cases (PPO/GRPO fine-tuning against a reward signal).

**Resolved 20/08/2026 (with tutor, formal channel):** the mechanism's own RL is **not SFT**. It is a **harness adjustment** — RL driven by an explicit user signal (thumbs up / thumbs down) as the input reward. This settles which sense of "RL" the Plano's title refers to for Sub 1.3/1.7: closer to Reflexion's verbal/no-gradient family than to Retroformer/Memory-R1's literal policy-gradient fine-tuning, but with a structured binary reward instead of free-text self-critique.

**Primary source for this decision:** the [20/08 tutor checkpoint](../docs/checkpoint-2026-08-20-tutor-kickoff.md) ([transcript](../docs/sources/Checkpoint_Tutor_2026-08-20.docx)) is where this was actually settled, not just recorded. The tutor described the desired mechanism unprompted ("corrija a memória... para tentar diminuir ao longo do tempo esses casos errados"); Rafael checked it against the RL framing ("só reforçando, não retreinando... mexendo no harness... uma skill nova, uma memória de procedure"); the tutor confirmed ("Perfeito, exatamente isso"). See [`checkpoint-2026-08-20-reflections.md#1`](checkpoint-2026-08-20-reflections.md#1-the-tutor-independently-confirms-the-harness-not-retraining-decision--with-the-exact-vocabulary) for the full exchange and what else that meeting confirms (the cross-agent scope narrowing in decision #3 below also gets real-world corroboration there).

**New open item this decision creates:** audit every model in the reading corpus for which ones implement RL via **PE (prompt engineering)** — i.e., behavior adjustment through prompt/harness engineering rather than policy-gradient fine-tuning — since that is the family the project's own mechanism now belongs to. See [`open-questions.md`](open-questions.md).

**Partial resolution (24/08/2026, Claude-read via sub-agents, not Rafael-read):** a full-text reading sprint ([`reading-sprint-2026-08-24-queue-papers.md`](reading-sprint-2026-08-24-queue-papers.md)) confirms **Mem-α** (arXiv:2509.25911) belongs in the same bucket as Retroformer/Memory-R1, not the PE family — it fine-tunes the agent's own backbone LLM (Qwen3-4B) via GRPO, with a measured base→post-RL jump (0.389→0.642) confirming real gradient updates to the acting model. **Memento** (arXiv:2508.16153) is a third, distinct case: its LLM stays frozen (non-parametric w.r.t. the agent itself), but its best-performing read variant trains a *separate* neural Q-network controller via real RL gradients — not prompt engineering either, just a smaller and different target for the gradients. Net result: **none of Mem-α, Memento, or Retroformer turn out to be PE-based**, and the non-parametric candidates in the same sprint (ExpeL, SCM) aren't really "RL" in a formal sense either — they're heuristic self-curation (vote/prune, LLM-judgment gating) without a reward-optimized policy. This suggests the reading corpus may not contain a clean RL-via-PE precedent at all — the audit isn't fully closed (Synapse/MetaGPT/TiM/RecAgent/S³ and Casper et al. remain unread), but the shape of the answer so far is "this family may need to be defined by the project itself, not adopted from the corpus."

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
