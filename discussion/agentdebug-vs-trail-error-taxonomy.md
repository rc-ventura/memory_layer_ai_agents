> **Sub-atividade:** 2.1 · **Type:** Cross-cutting literature synthesis · **Logged:** [14/09/2026](../research-diary/Set/diario_campo_2026-09-14.md#14092026)

# AgentDebug vs. TRAIL: two different error-taxonomy axes over the same trace

Surfaced while reviewing [`analysis/2026-09-trace-law-flow/`](../analysis/2026-09-trace-law-flow/)'s memory-candidate table (`docs/01-racionais.md` §7, `docs/02-relatorio-achados.md` §6) with an agent. Two things came out of the same working session: a citation correction on AgentDebug, and a clarifying comparison against TRAIL that turned out to answer a real question — are the two papers redundant for this project, or complementary?

## The overclaim, and what's actually citable

The memory-candidate table (7 candidates, 4 `tipo` labels — semântica / procedural / experiencial-procedural / harness) was described as "fundamentado no AgentDebug (o módulo que produziu o erro roteia o tipo de memória)". Checked against the primary source (arXiv:2509.25370, full 32-page PDF, not just the reading-queue note) by grepping the extracted text for `rout`, `memory type`, `semantic memory`, `procedural memory`: **zero occurrences**. The paper proposes a 5-module diagnostic taxonomy (memory/reflection/planning/action/system — Table 2, p. 14) and confirms by ablation that root-cause-only write policy beats fixing every surface mistake (p. 2 and p. 8) — both real and citable. It does **not** propose memory *types*, and never uses "routing" language. The four `tipo` labels are the project's own analogy, mapped onto the paper's 5-module structure, not a transferred finding.

Corrected in three places same day: notebook cell 9 (`analysis/2026-09-trace-law-flow/pipeline/analise_trace_esteira_juridica.ipynb`), `docs/01-racionais.md` §7 Passo 2, `docs/02-relatorio-achados.md` §6. See [`../papers/reading-queue.md`](../papers/reading-queue.md) for the project's standing distinction between "a note exists" and "actually read/verified" — this is a direct instance of that distinction mattering: the AgentDebug note had already been promoted from 🔎 (subagent skim) to ✅ (Rafael's own directed reading, [09/09](../research-diary/Set/diario_campo_2026-09-07.md#09092026)) and the overclaim still slipped through, because the ✅ promotion checked the taxonomy and the ablation claim, not this specific downstream inference built on top of them.

## Two different taxonomy axes, not two versions of the same thing

Once the overclaim was isolated, the natural next question was whether TRAIL (arXiv:2505.08638) — the project's other error-taxonomy source, still at 🔎 depth — would be a better or a redundant fit for the same table. It's neither: the two taxonomies classify along genuinely different axes.

| | AgentDebug | TRAIL |
|---|---|---|
| Classifies by | which **cognitive module** of the agent's own reasoning produced the error (memory / reflection / planning / action / system) | what **kind of mistake** occurred, observed from the trace itself (3 areas, 20 leaf types — hallucination, tool selection, formatting, instruction non-compliance, resource abuse, goal deviation, ...) |
| Unit of analysis | a module's output at one decision step — requires the agent to expose `<memory>/<reflection>/<plan>/<action>` as separate tags | a span (one LLM or tool call) — no dependency on the agent exposing its internal process |
| Covers multi-agent delegation? | No — the 5 modules are explicitly intra-agent; the paper defers coordination failures to other work (Cemri et al. 2025) | Yes — has its own category (*Task Orchestration*) |
| Carries severity? | Not per error type; only a binary "critical or not" at the whole-trajectory level | Yes, `impact ∈ {LOW, MEDIUM, HIGH}` per error |
| Output shape | cause + `correction_guidance` (prescriptive — what the agent should do differently) | category + evidence + `impact` (diagnostic — what happened and how much it mattered) |
| Directly applicable to this esteira's `CodeAgent`? | Mostly no, partially yes (see 14/09 update below) — needs the forced XML-tag architecture for 10 of 12 roles; 2 roles (`RespostaBacen`, `CalculoTrabalhista`) emit a native `PlanningStep` that gives real (not analogical) `planning`-module attribution | Yes, "with minimal adaptation" per its own span-based schema ([`../analysis/2026-09-trace-law-flow/literature/trail-2505.08638.md`](../analysis/2026-09-trace-law-flow/literature/trail-2505.08638.md) §"O schema é reusável no nosso trace?") |

The practical confirmation that this axis difference is real, not just a reading of the abstracts: applying TRAIL's own taxonomy to size the current pipeline's blind spot showed **59% of TRAIL's error types are structurally invisible to exception-based detection** (the method the pipeline uses today), and only 3.3% are fully visible. On TRAIL's architecturally-identical split (SWE-Bench, same CodeAct + Python-interpreter + import-whitelist pattern as this esteira), the #1 error is **Instruction Non-compliance (35.5%)**, not a syntax/formatting error — exactly the kind of thing AgentDebug's module taxonomy was never trying to measure, because it operates one level up (which module failed), not on the phenomenology of the failure.

## Why this matters for the mechanism, not just for this one trace

The two axes map onto two different needs the memory mechanism actually has:

- **AgentDebug's axis (module → routing)** is a candidate for the *shape* of a written memory unit once a root cause is known — cause + corrective instruction, one per cascade. This is upstream, structural work: deciding what a memory unit looks like.
- **TRAIL's axis (phenomenon + severity)** is a candidate for *coverage measurement and prioritization* — sizing how much of the agent's actual failure surface the current signal-capture method can even see, and weighting candidates by measured impact rather than by how loud the failure was (a `SyntaxError` is loud and cheap; a hallucinated case number is silent and expensive). This bears directly on the deterministic anomaly filter and severity-attribution questions already open in [`open-questions.md`](open-questions.md) (Signal Capture / Update Engine sections) — TRAIL's `impact` field is a concrete, already-piloted answer to "where does severity live," worth revisiting there once TRAIL is read at ✅ depth.

**Verdict: complementary, not competing.** AgentDebug informs the *form* of a memory unit; TRAIL informs *what's being missed* and *how much it costs*. Neither replaces the other for this project's own trace, and neither should be cited for what the other one actually says — which is the exact failure this note started from.

## Update 14/09/2026 (same day, later) — the "no native module signal" premise was too broad

Written the same afternoon this note was first published: a follow-up drill into the raw trace (`drill_down.py caso ... --json`) found that `txt_etap_memo` carries a third step class besides `TaskStep`/`ActionStep` — **`PlanningStep`**, produced by smolagents' own `planning_interval` mechanism, with an isolated `plan` field matching the framework's built-in template verbatim. It exists for only 2 of 12 roles (`RespostaBacen`, `CalculoTrabalhista`), but for those it means **real `planning`-module attribution is possible, not analogy** — compare the `plan` against the subsequent `ActionStep`s, no LLM needed. Full finding, census, and the proposed detector are in [`../analysis/2026-09-trace-law-flow/docs/04-roadmap.md`](../analysis/2026-09-trace-law-flow/docs/04-roadmap.md) item 10.

This corrects the "Directly applicable" row above and the parallel claim in [`../analysis/2026-09-trace-law-flow/literature/agentdebug-2509.25370.md`](../analysis/2026-09-trace-law-flow/literature/agentdebug-2509.25370.md) (ressalva 7, and the "não emite essas tags" line in "O que é") — both scoped now to "10 of 12 roles," not "the esteira."

**What this does *not* change:** the earlier correction in this same note (the "overclaim" section above) — AgentDebug still never proposes memory *types* or "routing," regardless of whether plan/thought are separable. That was a citation-accuracy question, orthogonal to this one, which is about how much of the paper's *method* (module attribution) is actually runnable on this trace. Nor does it touch `classify()`'s 15 symptom-based signatures (the taxonomy behind the CAND table's row counts) — that taxonomy was built bottom-up from raw exception messages and never depended on module separability in the first place; only the *labeling* of those rows as AgentDebug-module-analogous did.

## Left open, tracked at the analysis level, not here

- TRAIL is still read at 🔎 depth (subagent skim); Rafael is reading it directly next, to promote it to ✅ the way AgentDebug was on [09/09](../research-diary/Set/diario_campo_2026-09-07.md#09092026).
- Whether to credit TRAIL explicitly where its mechanism is already used uncredited (roadmap item 6, "Reasoning-action mismatch," is TRAIL's *Tool Selection Errors* detector with the origin unstated), and whether to add TRAIL-derived detectors (only ~2 of 11 are on the roadmap today, ranked by the note's own cost×impact read) — these are operational TODOs for [`../analysis/2026-09-trace-law-flow/docs/04-roadmap.md`](../analysis/2026-09-trace-law-flow/docs/04-roadmap.md), not architecture-level open questions, so they're tracked there rather than duplicated in [`open-questions.md`](open-questions.md).
