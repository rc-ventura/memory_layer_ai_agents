> **Sub-atividade:** 1.1 / 1.6 / 1.7 / 2.2 · **Type:** agent-conducted literature sprint (via 9 parallel sub-agents) · **Logged:** [24/08/2026](../research-diary/Ago/diario_campo_2026-08-24.md#24082026)

# Reading sprint on the queue's architecture-relevant papers — what full-text reading changes

## Provenance — read this before citing anything below

**This is not Rafael's own reading.** At Rafael's request, an agent (no defined provider) dispatched 9 parallel sub-agents, each assigned one paper from [`../papers/reading-queue.md`](../papers/reading-queue.md) plus the specific gating question already recorded there (or, where none existed, a question derived from the emerging architecture hypothesis — see the framework discussion in the same conversation this sprint came from). Each sub-agent was instructed to read full text (via ar5iv HTML render, since direct `arxiv.org` fetch is blocked in this environment — consistent with the note already in `reading-queue.md`) rather than rely on the abstract, and to flag explicitly if it couldn't.

This sits in a **new tier**, distinct from the two already established in this repo: stronger than "📝 verified" (bibliographic facts checked against a primary source, no content read), because full text was actually read and specific mechanisms extracted — but still not "✅ read by Rafael," because Rafael has not personally read these papers. Treat every claim below as **agent-read, not Rafael-read** — don't cite it to Luis Felipe as "I read X and it says Y" without Rafael having actually done that reading himself first. The value here is scoping and risk-reduction: knowing *before* spending real reading time which papers resolve cleanly, which need a caveat, and which are dead ends for this project's non-parametric scope.

**Scope:** all 9 assigned papers reported back in full (Casper et al.'s sub-agent initially went idle without a report; a follow-up prompt recovered it). Synapse, MetaGPT, TiM, RecAgent, and S³ were deliberately excluded from this sprint — they only support the "checked the full 27-model corpus" exhaustiveness claim for Entregável 1, not architecture design, so they weren't worth the read-budget here.

## Per-paper findings

### SAGE (arXiv:2409.00872) — does it threaten the central finding?

Title confirmed: "SAGE: Self-evolving Agents with Reflective and Memory-augmented Abilities" (Liang, Shi et al.; v1 Sep 2024, v2 Apr 2025, "Preprint. Under review." — also indexed as accepted in *Neurocomputing* Vol. 647 2025 per a secondary search hit, not independently verified). Full primary PDF read (sections 1–5 + Appendix A.1).

- **Cross-trial reuse: ambiguous, not experimentally demonstrated.** §3.2 textually claims LTM "accumulate[s] knowledge from past interactions and appl[ies] it to future tasks" — a genuine cross-trial claim in prose. But both worked examples in the paper (Fig. 2 TriviaQA, Fig. 4 HotpotQA) show reflection operating *within* one task's iterative refinement loop, not carried into a separately-instantiated later task. The ablation (Table 5, §4.7) only toggles "memory optimization" as a whole, never isolating within-task STM from across-episode LTM. Whether LTM even persists across the many episodes composing one benchmark score is left unstated.
- **Forgetting: yes, explicit and well-formalized** — "MemorySyntax": Ebbinghaus retention `R(I,τ) = e^(−τ/S)`, thresholds θ1 > θ2 (`R ≥ θ1` → keep in STM, `θ2 ≤ R < θ1` → promote to LTM, `R < θ2` → discard). Appendix A.1 formalizes `S(Iₜ) = H(Iₜ)/f(t)` (entropy-weighted) as constrained utility maximization under a capacity cap.
- **Verdict: probably not a threat, but the closest call in the corpus so far.** Recommended citation stance for Entregável 1: "SAGE claims but does not experimentally isolate cross-trial transfer" — a one-sentence caveat, not a rewrite of the central finding.

### Memento (arXiv:2508.16153) — the RL-controller candidate

Official title confirmed: **"Memento: Fine-tuning LLM Agents without Fine-tuning LLMs"** (Zhou, Chen, Guo, Yan, Lee, Wang, Lee, Zhang, Shao, Yang, Wang). The "AgentFly" alternate title in some secondary indexing is resolved: it's the GitHub org name (`Agent-on-the-Fly/Memento`), not an alternate paper title — cite "Memento" only. Full text via ar5iv (arxiv.org/abs blocked).

- **Memory writes: explicit and inspectable, but write-only.** `Write(s_t,a_t,r_t,M_t) = M_{t+1} = M_t ∪ {(s_t,a_t,r_t)}` (Eq. 12) — every case appended as a textual/embedded (state, action, reward) triple to a plain case bank. **No delete/forget/discard operation is documented anywhere** — memory only grows.
- **What the RL trains: confirmed non-parametric w.r.t. the LLM, but a real trained neural policy.** The LLM (`p_LLM`) is frozen throughout — "without... fine-tuning the base model." Two read variants exist: `Read_NP` (pure non-parametric top-K similarity, zero training) and `Read_P` (a trained Q-network controller via soft Q-learning, Eq. 16). The parametric variant trains real gradients on the *selection policy*, not the LLM.
- **Reward: fully automatic, no human in the loop.** Binary task success/failure (`r ∈ {0,1}`) from end-to-end task completion — no human-labeled correctness signal anywhere in training. This is a direct mismatch with this project's human/outcome-signal-gated, batched design.
- **Headline result confirmed:** GAIA validation 87.88% Pass@3 (top-1 on the leaderboard at time of writing), 79.40% GAIA test; DeepResearcher 66.6% F1 / 80.4% PM, beating prior training-based baselines by 4.7–9.6 points OOD.
- **Verdict: partially safe as a reference, with two caveats that must travel with any citation** — (a) no forgetting mechanism exists (append-only), (b) the reward is fully automatic, not human-gated like this project's design. Cite the "frozen LLM + external case memory + separate lightweight controller" pattern, not the specific reward/forgetting design.

### Mem-α (arXiv:2509.25911) — resolved: parametric, out of scope

Title confirmed: "Mem-α: Learning Memory Construction via Reinforcement Learning" (Wang, Takanobu, Liang, Mao, Hu, McAuley, Wu; submitted 30/09/2025). Full method text (ar5iv) cross-checked against an independent WebSearch synthesis citing the same details — not a single-source read.

- **Confirmed PARAMETRIC — same bucket as Retroformer/Memory-R1, not Memento.** Fine-tunes the agent's own backbone LLM (Qwen3-4B) via **GRPO**, 32 H100 GPUs. Base Qwen3-4B scores 0.389 → post-RL Mem-α scores 0.642 on the same model — gradients change the acting model itself. The memory store (core/episodic/semantic) and BM25 retrieval are fixed, not learned; what's learned is the *policy for calling* `memory_insert`/`memory_update`/`memory_delete` tools.
- **Reward:** `r_t = r1 + r2,t + β·r3 + γ·r4,t` — downstream QA correctness via RAG over memory, tool-call format validity, compression ratio, and an LM-judge content-quality score.
- **Verdict: not safe to cite as an in-scope non-parametric architectural reference** — this is textbook policy-gradient fine-tuning of the acting LLM, architecturally indistinguishable in kind from Retroformer/Memory-R1. Citable only as background/contrast, like the other two — adopting its patterns would need the same explicit sign-off this project's scope decision already requires for that category (see [`scope-and-terminology-decisions.md#2`](scope-and-terminology-decisions.md#2-what-reinforcement-learning-means-in-this-projects-title)).

### ExpeL (arXiv:2308.10144) — the lightweight Update Engine candidate

Full text via ar5iv, cross-checked against the official GitHub README (`LeapLabTHU/ExpeL`) and secondary review sources.

- **Trigger: batched, post-training-phase, not continuous.** The agent runs all training tasks first (ReAct + self-reflection on failures), pooling trajectories; only afterward does a separate `LLMinsights` stage compare success/failure pairs and lists of successes, processed in chunks. No insight updates happen mid-episode.
- **Form: free-text natural-language rules**, e.g. (HotpotQA) "When searching for information, try breaking down complex questions into simpler sub-questions"; (ALFWorld) "When searching for an item, consider its nature and typical usage." Few-shot trajectory exemplars are a *separate*, independently-retrieved component (FAISS + all-mpnet-base-v2, top-k similarity).
- **Storage/retrieval:** all insights are concatenated into *every* prompt (no filtering); exemplars are retrieved by similarity.
- **Pruning: not monotonic-only.** Four ops per candidate insight — ADD / EDIT / UPVOTE / DOWNVOTE — with an importance counter (init = 2, ±1 per vote/edit) that removes an insight at 0. But this curation is fully LLM-autonomous (the model votes on its own insights), **not human-reviewed**, and EDIT/DOWNVOTE overwrite/delete silently — no diff or version history kept.
- **Parametric updates: confirmed none** — frozen GPT-3.5/4 via API throughout; the paper explicitly motivates the prompt-only approach by citing fine-tuning's generalization risk.
- **Assessment:** maps well onto the *lightweight* end of the Update Engine — periodic, batched, text-only, which mirrors this project's architecture directly. The gap for a legal/compliance context: no explicit human correctness-signal gate (self-critique only), no versioned snapshots between update cycles, no rollback — would need to be added, not inherited.

### MemoryBank (arXiv:2305.10250) — the Memory Store / forgetting candidate

Full text via ar5iv, cross-checked with WebSearch.

- **Decay formula:** `R = e^(−Δt/S)` (Sec. 2.3) — `Δt` = time since last retrieval, `S` = a discrete "memory strength" counter initialized at 1. The authors themselves call this "an exploratory and highly simplified" model.
- **Reinforcement on recall:** `S → S+1`, `Δt → 0` — a pure counter increment plus timer reset, fully auditable (two integers per item, closed-form formula: "this memory's `S=k`, `Δt=n` days, so `R=e^(−n/k)`").
- **Retrieval:** dense dual-tower (DPR-style) + FAISS, indexing both raw conversation turns *and* event summaries as separate pieces; a separately-tracked, evolving "user portrait" is not clearly subject to the same decay math.
- **Hard delete: not specified.** `R` decays asymptotically toward 0 but items appear to persist in storage indefinitely — forgetting is de-prioritization in retrieval ranking, not deletion. No stated configurable cutoff threshold — a real gap for an audit trail ("nothing to point to as the rule that fired").
- **Eval setting:** SiliconFriend, a personal-companion chatbot (10-day simulated histories, 15 personas, 194 probe QA pairs) — purely social/companionship-oriented, nothing tested against task-correctness or compliance-sensitive retrieval.
- **Assessment:** the decay math itself is simple and explainable enough for an audit trail, but two things need to be added, not inherited, for legal/compliance use: (a) an actual hard-delete/threshold step (none exists), (b) a replacement for "importance" — MemoryBank's signal is pure recall frequency (a social-relevance proxy), not legal correctness or case-outcome severity.

### Generative Agents (arXiv:2304.03442) — the adaptive-trigger candidate

Full text via ar5iv, cross-checked against the ACM DL full HTML.

- **Retrieval score:** `score = α_recency·recency + α_importance·importance + α_relevance·relevance`, all `α = 1`, each component min-max normalized. Recency = exponential decay (0.995/hour) since the memory was last *accessed* (not created). Relevance = cosine similarity to the query embedding.
- **Importance:** a pure LLM-prompted 1–10 "poignancy" rating at memory-creation time, cached on the object (exact prompt anchors on social/personal-life examples — "brushing teeth" vs. "a break up").
- **Reflection trigger: not a fixed count** — fires when the *cumulative sum of importance scores* for recent events exceeds a threshold (150 in their implementation), ≈2–3×/day/agent. This is exactly the adaptive-trigger pattern flagged as a candidate to replace this project's flat "every N cases."
- **Reflection process:** pull the 100 most recent records → prompt for the "3 most salient high-level questions" answerable from them → use those as retrieval queries → synthesize a cited insight per question. Reflections are written back into the *same* memory stream (their own importance/timestamp/embedding) and can chain into a tree (raw observations as leaves, increasingly abstract thoughts as internal nodes).
- **Sandbox-specific caveats that don't transfer as-is:** the importance-prompt anchors are social/personal-life calibrated (would need legal reanchoring, e.g. "case dismissed," "statute of limitations missed"); recency is keyed to *access* time, tuned for a socially-circulating memory — a legal pipeline processing cases more independently may want decay from creation/ingestion instead; the whole pipeline is tuned and evaluated against human *believability* ratings, with no ground-truth-correctness analog — so the threshold constant (150) and the question-count (3) are unvalidated tuning knobs, not empirically-proven values.
- **Assessment:** structurally adaptable — replace "sum of raw event importance" with "sum of case-error-severity scores" (LLM- or rubric-scored per annotated case) and fire the Update Engine when cumulative severity crosses a calibrated threshold, instead of a flat N=100. Catches a cluster of severe errors fast without over-triggering on long runs of correct cases. Recommended as a hybrid: severity-threshold trigger **or** a hard max-N cap, since a legal pipeline (unlike Smallville's continuous stream) may go long stretches with only low-severity cases and still want periodic drift-checking.

### SCM (arXiv:2304.13343, DASFAA 2025) — the explicit-controller candidate

Full text via ar5iv, venue confirmed via WebSearch.

- **What the controller decides / how:** prompted-LLM judgment, **not** a trained model or hard rules — two fixed yes/no prompts gate (a) whether to activate memory retrieval at all, and (b) whether a summary suffices vs. full text. This revises the earlier assumption that SCM was "rule-based" — it's LLM judgment wrapped around one explicit scoring formula.
- **Operations governed:** Store (every turn: index, observation, response, summary, embedding) · Retrieve (top-k via `rank_score = recency_score + relevance_score`; relevance = cosine similarity; recency favors recently-accessed items but **no formula/decay function is given** — genuinely unspecified) · Compress (LLM-decided full-text vs. summary above a token threshold) · Discard: **none** — memory grows unbounded (tested only to 200 turns; the authors themselves flag unbounded growth as a limitation).
- **Auditability: mixed.** The retrieval *ranking* math is fully explicit and traceable (a simple sum of two scores). But the store/retrieve/compress *decisions* are opaque LLM completions to a prompt — the same black-box problem as any LLM-judge. A human can read the prompt template and the yes/no output, but not a deterministic decision trace.
- **Learning: none** — explicitly static, no fine-tuning, fixed prompts + fixed formula, no online adaptation.
- **Evaluation:** the controller step specifically buys ~18pp accuracy over flat search (77.1% vs. 59.3% without the controller, davinci-003 backbone); without "activation memory" at all, accuracy collapses to 10.5% (retrieval recall → 0%) — the gating step matters a lot empirically, even though it's a black box.
- **Assessment — spectrum placement revised:** sits closer to the reflection/heuristic boundary than to genuine rule-based control — more inspectable than Memento (no learned policy to interpret) but less controllable than a true rule engine would be, since the gating logic ultimately resolves to "ask an LLM and trust its answer." No discard mechanism at all is a real gap if compliance ever requires provable memory expiry.

### Retroformer (arXiv:2308.02151, ICLR 2024) — confirmed contrast case, with one reusable idea

Full HTML via ar5iv; high confidence on architecture/reward mechanics, medium confidence on one exact benchmark number (see below).

- **What's fine-tuned:** a **separate, small local retrospective model** `M_r` (LongChat-7b-16k, LoRA r=4 + PPO). The main acting LLM `M_a` (GPT-3/4) stays fully frozen — "without accessing the Actor LLM parameters or needing to propagate gradients through it." Confirms this is a real gradient-trained component, keeping it out of implementation scope, but clarifies it's not the *main* agent being tuned.
- **Reward:** `r = G_{k,i+1} − G_{k,i}` — the change in episode return between consecutive trials, grounded in environment success/failure (not a learned reward model).
- **What `M_r` produces, and a non-parametric fallback that already exists:** self-reflection text (root-cause diagnosis + revised plan) spliced into the frozen actor's next prompt — **structurally identical to what Reflexion produces via pure prompting with zero training**, and that pure-prompting version is literally Retroformer's own baseline in the paper.
- **Benchmarks vs. Reflexion (3–4 retries):** HotPotQA (GPT-3) 54% vs. 50%; AlfWorld (GPT-4) 100% vs. 85.07%; WebShop (GPT-3) ~36–45% vs. 35% (two extraction passes disagreed on this exact number — flagged as lower-confidence). PPO buys a modest 1–10pt improvement over pure prompting in most cases, a larger jump only on AlfWorld.
- **Reusable non-parametric idea:** use the reward *concept* (Δ episode return across trials) not to train weights but as a non-parametric **selection/ranking heuristic** — generate multiple candidate reflections via pure prompting and empirically prefer whichever historically correlated with better downstream outcomes (a best-of-N / rejection-sampling analog). "The reward concept survives, the gradient step doesn't."

### Casper et al. (arXiv:2307.15217) — is a binary thumbs-up/down signal trustworthy?

Full text via ar5iv + arxiv.org/html/2307.15217v2, agreement figure cross-checked twice via WebSearch. Full detail and the resulting five concrete risks now live in [`thumbs-feedback-reliability.md`](thumbs-feedback-reliability.md#full-text-confirmation-of-casper-et-al-24082026-agent-read-via-sub-agent-not-rafael-read); summary here:

- **The paper's own "binary" category means paired comparison, not single-output approval.** It never analyzes thumbs-up/down-on-one-output on its own terms — the closest analog, "scalar feedback," is flagged as poorly calibrated. This project's signal (a degenerate 2-point scalar) inherits that calibration weakness without pairwise comparison's relative-anchor benefit.
- **Annotator-researcher agreement: only 63–77%** (§3.2.1, citing Stiennon 2020/Ouyang 2022/Bai 2022a), and mistakes can be *correlated* across annotators — majority vote over a batch doesn't cancel systematic bias. **No minimum batch size is specified anywhere in the paper** — the project's "~100 cases" design has no principled floor to borrow here.
- **Sycophancy "can worsen with model size" and RLHF "can amplify it"** (§3.1.1); §3.2.2 names the approval-vs-benefit gap directly — a case can be "approved" for being confident and fluent rather than correct.
- **No concrete mitigation guidance for a batched/periodic design** — §3.4 states the generic tradeoff (too-frequent vs. too-infrequent updates) but gives no aggregation method or batch-size number. This is a real gap in the source, not something the project failed to find.
- **Five concrete risks for Sub 1.5's acerto/erro criteria:** target inter-rater agreement above the paper's own ~77% ceiling before trusting a label; treat correlated (not just insufficient-volume) annotator error as first-class; build an explicit anti-sycophancy audit (do "approved" cases cluster on style over substance?); define acerto/erro against case *outcome*, not reviewer *satisfaction*; log per-case disagreement even inside batches that clear a majority threshold.

## What this changes about the architecture hypothesis

The prior working hypothesis (from the conversation this sprint came out of) was a **controller spectrum** — SCM (rule-based) → ExpeL (reflection-based) → Memento (RL-trained) — to inform the Update Engine's design. Full-text reading revises and sharpens this:

- **SCM isn't rule-based** — it's prompted-LLM judgment around one explicit scoring formula. The real spectrum is closer to: *SCM (LLM-judgment gate, explicit ranking math, zero learning) → ExpeL (LLM self-curated insight pool, zero gradient, but has an actual add/edit/vote/prune protocol) → Memento (a genuinely trained neural policy, via RL gradients, on a separate controller)*.
- **The strongest, most concrete confirmation yet of the project's central finding** ([`cross-trial-vs-forgetting-gap.md`](cross-trial-vs-forgetting-gap.md)) comes not from a survey table this time, but from mechanism-level reading: **none of the eight papers read here combines all five of** (a) non-parametric memory content, (b) an external/human correctness-signal gate, (c) batched/controlled update, (d) versioning + rollback, and (e) real hard-delete forgetting.
  - MemoryBank and SAGE have real decay math (Ebbinghaus-style) — but MemoryBank never hard-deletes, and SAGE's cross-trial claim isn't experimentally isolated.
  - ExpeL and SCM have real update/gating logic — but neither has versioning, an audit trail, or a human-gated signal; ExpeL overwrites silently, SCM never discards at all.
  - Memento has fully explicit, inspectable writes — but no discard mechanism whatsoever, and its reward is fully automatic (no human in the loop).
  - Mem-α and Retroformer both genuinely fine-tune a model with gradients (Mem-α: the main LLM; Retroformer: a separate small model) — confirmed out of this project's non-parametric scope, useful only as contrast.
- **Practical read for the mechanism's design:** no candidate can be adopted wholesale. The plausible path is a composite — SCM/ExpeL-style explicit, inspectable gating and update logic; MemoryBank/SAGE-style decay math *with an actual delete step added*; Generative Agents' cumulative-severity trigger instead of a flat N; and, unlike any of the eight, an explicit external correctness-signal gate plus real versioning/rollback (Sub 3.4) around the commit step — which is exactly the whitespace [`scope-and-terminology-decisions.md`](scope-and-terminology-decisions.md) and the earlier framework discussion already pointed at, now confirmed at the level of specific formulas and mechanisms rather than survey-table checkmarks.
- **Open question this sprint sharpens rather than closes:** [`open-questions.md`](open-questions.md)'s item on which corpus models implement RL via prompt engineering (PE) rather than policy-gradient fine-tuning — none of Mem-α, Memento, or Retroformer turn out to be PE-based; all three train real gradients somewhere (main LLM, a separate controller, or a separate small model, respectively). ExpeL and SCM are non-parametric but aren't really "RL" either (no formal reward-optimized policy — ExpeL's vote/prune loop and SCM's LLM-judgment gate are heuristic self-curation, not policy optimization). This suggests the read corpus may not contain a clean "RL-via-PE" precedent at all — worth flagging as something this project's own mechanism may have to define from scratch rather than adopt.

## Still open

All 9 sub-agents have now reported. None of the above should be treated as Rafael's own reading for citation purposes — see the provenance note at the top. Synapse, MetaGPT, TiM, RecAgent, and S³ remain unread (by anyone) — see the scope note above.
