> **Sub-atividade:** 1.4 / 1.5 / 2.2 / 3.6 · **Type:** Architecture cross-reference (LangChain Eval Engineering Skill → knowledge-as-infra) · **Logged:** [10/09/2026](../research-diary/Set/diario_campo_2026-09-07.md)

# Eval Engineering Skill ↔ knowledge-as-infra: component-by-component connections

Companion to [`langchain-eval-engineering-skill-analysis.md`](langchain-eval-engineering-skill-analysis.md), which documents the skill's mechanics. This note maps each skill concept to the project's architecture and identifies what's genuinely new — what the skill gives the project that the current design doesn't have, and what it merely corroborates.

## 1. World Knowledge Skill ↔ Strategy Layer (camada 3)

This is the strongest structural isomorphism in the entire analysis.

| World Knowledge Skill (eval-engineering) | Strategy layer (knowledge-as-infra, camada 3) |
|---|---|
| Repo-local skill (`<project>-world/SKILL.md`) | Memory Store camada 3 — "meta-reflexão destilada" |
| Accumulates reusable knowledge across Tasks | Accumulates reusable heuristics across cases |
| Human-reviewed before accepted ("Treat a World Skill change as accepted only after human review") | Commit Gate (component D) — human review, versioned, rollback |
| "Remove or narrow ideas that the Task disproved" | Forgetting (component E) + rebaixamento (`R < θ1`) — stale/narrowed items demoted |
| "Keep Task's exact request, hidden truth, scoring rules out of the World Skill" | Camada 1 (episodic log) holds raw traces; camada 3 holds only the distilled strategy, not the raw case content |
| "Do not build a large project encyclopedia from repository shape alone. Add the small set of supported facts that help the current Task" | Cold path: Update Engine processes only flagged cases (anomaly filter), not every case — incremental, not bulk |
| Common failure: "speculative encyclopedia — building a large project map before one Task shows what is useful" | Risk the architecture already guards against by gating writes and using anomaly-triggered batch processing |
| Common failure: "stale certainty — preserving a rule after later evidence contradicts it" | Exactly what Forgetting (component E) and rebaixamento exist to address |
| Common failure: "task leakage — storing focal records, expected answers, or exact criteria in the World Skill" | The architecture's provenance design (source_trace_ids, derived_from) keeps raw traces in camada 1, not duplicated into camada 3 |

**What's new:** The World Knowledge Skill gives a **concrete, working implementation** of the strategy-layer pattern — a SKILL.md with a references/ folder, scripts/, and accumulated knowledge, maintained through a human-reviewed update loop. The project's strategy layer is currently a hypothesis; this is a shipped, iterated example of the same pattern in a different domain. The World Skill's anti-patterns ("speculative encyclopedia," "stale certainty," "task leakage") are concrete failure modes the project's Commit Gate and Forgetting components should explicitly guard against — and now have a named reference for.

**What's corroborated, not new:** The human-review gate, the incremental accumulation, the separation of raw vs. distilled content — all already in the architecture. The World Skill confirms the pattern is sound, but doesn't change the design.

## 2. Task.md (control-plane spec) ↔ Sub 1.5 (acerto/erro criteria)

Sub 1.5 ("Definição preliminar dos critérios de 'acerto/erro'") is open. The Task.md template gives a **concrete structure** for what "criteria" means:

| Task.md section | What it means for Sub 1.5 |
|---|---|
| Purpose and evidence | What capability is being tested, why it matters, source evidence |
| Agent input | The exact instruction given to the agent (the legal task) |
| Verification table | For each required/prohibited result: independent evidence, exact check, pass condition |
| Accepted alternatives | Valid equivalent results (not just one "correct" answer) |
| Complete pass rule | The full boolean logic of pass/fail |
| Invalid-run conditions | When the run itself is invalid (not the agent's fault) |
| Fairness and leakage | Why the task is solvable, what shortcuts might work, how hidden truth stays hidden |
| Realistic wrong result that must fail | A concrete example of what "wrong" looks like |
| Prohibited collateral change that must fail | What must NOT happen even if the primary task succeeds |

**What's new:** This transforms Sub 1.5 from "write a criteria document" into "produce a set of Task.md files, one per capability being tested, each with a verification table." The verification table format (required/prohibited result × independent evidence × exact check × pass condition) is directly usable. The "accepted alternatives" and "prohibited collateral change" fields are things the current Sub 1.5 discussion hasn't addressed but are essential — a legal agent can produce a correct result with a prohibited side effect (e.g., expediting an ofício that shouldn't have been expedited).

**The "never expose to the agent" principle:** Task.md is never mounted in the agent's container. The agent sees instruction.md only. This maps to the project's design: the acerto/erro criteria exist outside the agent's view — the agent doesn't know what's being scored, it just does the task. This prevents the agent from optimizing for the scoring rubric instead of the task itself (a form of reward hacking).

## 3. Verifier design ↔ Sub 3.6 (Reference Accuracy) + Commit Gate (component D)

### For Sub 3.6 (Reference Accuracy)

The verifier design principles are directly applicable:

- **"Decides success from evidence independent of the agent's claim"** — Reference Accuracy compares what was retrieved against a gold standard, not against what the agent says it retrieved.
- **"Never trust an agent-written action list, a service success flag"** — the gold standard is external, not the agent's self-report.
- **"Accept all equivalent valid results"** — in a legal flow, there may be multiple valid paths to the same outcome. The verifier should accept all equivalent valid results, not just one preferred path.
- **"Use an LLM judge only for semantic meaning, only after code has settled objective facts"** — for legal text evaluation, an LLM judge may be needed for semantic assessment, but only after deterministic checks (did the agent cite the right documents? did it produce the right document type?) have passed.
- **Test the decision boundary** with 6 fixtures — the Reference Accuracy metric should be tested with: a known-good retrieval (Pass), a valid alternative retrieval (Pass), a realistic wrong retrieval (Fail), a shortcut/gaming attempt (Fail), a retrieval with prohibited side effects (Fail), and missing/corrupt evidence (infrastructure error, not agent failure).

### For Commit Gate (component D)

The verifier design's anti-gaming principles reinforce the Commit Gate:

- **"Review every zero and every suspicious pass"** — every rejection AND every approval should be inspected. A pass can be a false acceptance (the agent gamed the verifier).
- **"A pass is not proof of quality: inspect for shortcuts, leaked truth, weak criteria, and unscored collateral effects"** — a memory update that "passes" the Commit Gate can still be harmful if the gate's criteria are too weak or if the agent found a way to satisfy the proxy without actual improvement.

## 4. Calibration failure taxonomy ↔ signal attribution in the cold path

The skill's 8-category failure taxonomy gives the project a concrete framework for the **attribution problem** it already faces but hasn't formalized: when an agent fails after a memory update, was it the memory's fault?

| Calibration category | Project translation |
|---|---|
| **Capability** — fair access, correct infra, intended work failed | The memory update was correct, but the agent still couldn't do the task — a genuine capability gap |
| **Missing information** — required fact not visible/discoverable | The memory update didn't include information the agent needed — the recall_memory or the trace was incomplete |
| **Harness** — runtime, tool, prompt, session, or adapter wrong | The agent's harness (prompt, tools) has a defect independent of the memory update |
| **Environment** — state, service, permission, reset wrong | The [EMPRESA] platform environment changed (API, Kafka, business rules) |
| **False rejection** — valid result failed | The acerto/erro criteria (Sub 1.5) are too strict — the agent did right but the verifier says wrong |
| **False acceptance** — invalid result passed | The criteria are too weak — the agent did wrong but the verifier says right (the Commit Gate didn't catch it) |
| **Leakage** — hidden truth or scoring logic was visible | The agent found the expected answer through a shortcut, not through correct reasoning |
| **Infrastructure** — build, startup, timeout, credential, cleanup failed | Platform infra failure — not the agent's or the memory's fault |

**What's new:** The project's open question about "does thumbs up/down transfer from Reflexion/Retroformer's assumptions" ([open-questions.md](open-questions.md)) gets a concrete complement: the problem isn't just whether the signal is reliable, it's also about **attributing** failures correctly after a memory update. The 8-category taxonomy gives a structured way to do that attribution — and "false rejection" and "false acceptance" are exactly the Commit Gate's failure modes. "Do not make a Task harder to hide a defect" is a principle the cold path should adopt: if the verifier or the Commit Gate has a gap, fix the gap, don't make the criteria stricter to compensate.

## 5. Discovery methodology ↔ Sub 1.4 (mapear fluxos jurídicos)

The skill's `references/discovery.md` gives a concrete methodology that maps to Sub 1.4:

| Discovery step | Sub 1.4 equivalent |
|---|---|
| Follow each real invocation path through code | Map each legal flow from intake to output |
| Map the Harness and connected systems | Map the agent's tools, MCP integrations, Kafka topics, APIs |
| Review traces — reconstruct interactions in time order | Analyze raw agent traces (already happening in `analysis/`) |
| Cluster requests by work and outcome, not wording | Cluster legal cases by flow type and outcome, not by petition text |
| "Preserve rare but important requests" (safety, permissions, high-impact) | Preserve rare but high-impact legal cases (grande causa, contestação crítica) |
| "Look for: failed tool calls, malformed arguments, empty results, permission errors, timeouts, retries" | Look for: failed MCP calls, Kafka errors, pipeline stage failures in the legal flow |
| "Look for: user dissatisfaction, corrections, rejection, abandonment, explicit acceptance" | Look for: 👍👎 signals, revisão humana corrections, case rework |
| "Cases where user appears satisfied despite hidden error, or unhappy despite correct work" | Cases where the legal outcome was correct but the process was wrong (or vice versa) |

**What's new:** The "cluster by work and outcome, not by exact wording" principle is directly applicable to the legal domain — cases should be clustered by flow type and outcome (e.g., "cadastro → subsídios → contestação, outcome: 👎"), not by petition text similarity. The "preserve rare but important" principle is what the DMF-lite importance score's `is_grande_causa` signal already captures, but the skill gives it a methodological framing the project didn't have.

## 6. The "fix only non-agent failures" principle ↔ the project's verification gap

The skill is emphatic: **"Fix non-agent failures before using the score."** If the environment is broken, the verifier is wrong, the harness has a bug, or the infrastructure failed — fix that first, then re-run. Don't attribute an environment failure to the agent's capability.

The project's cold path has the same problem at a different level: if a memory update is proposed based on a signal that was actually an environment failure (API changed, Kafka topic misconfigured, business rule updated), the Update Engine will propose the wrong fix. The deterministic anomaly filter (component A/C) should flag environment failures differently from agent capability failures — and the calibration taxonomy gives a concrete way to classify them.

**What's new:** This principle suggests the deterministic anomaly filter should have at least two categories of anomaly: "agent behavior anomaly" (candidate for memory update) and "environment anomaly" (not a memory-update candidate — fix the environment first). The skill's taxonomy gives the categories; the architecture's filter currently doesn't distinguish.

## 7. "Complete only when" checklist ↔ POC validation (Sub 1.6/1.7)

The skill defines completion criteria that could be adapted for the POC validation in Sub 1.6/1.7:

- Task.md matches the built instruction, Environment, and Verifier → the memory mechanism's spec matches what was actually built
- The Task is solvable from agent-visible information → the agent can succeed with the memory it has, not by guessing
- Valid and invalid Verifier cases behave as intended → the Commit Gate correctly accepts good updates and rejects bad ones
- At least one real run was read in full → at least one real legal case was processed end-to-end with the mechanism active
- Non-agent failures were repaired or reported → environment/platform failures were separated from agent failures
- The user receives the Task path, run command, results, evidence, and remaining limits → the tutor receives the POC results with full evidence

## What's genuinely new vs. what's corroboration

### Genuinely new (the skill gives the project something it didn't have)

1. **The World Knowledge Skill pattern** — a working, shipped implementation of the strategy-layer concept (accumulated knowledge, human-reviewed, versioned, with named anti-patterns). The project's strategy layer is a hypothesis; this is a reference implementation.
2. **Task.md as a concrete format for Sub 1.5** — transforms "define acerto/erro criteria" from an abstract document into a structured spec with verification tables, accepted alternatives, prohibited collateral changes, and fairness/leakage analysis.
3. **The 8-category calibration taxonomy** — gives the project a structured way to attribute failures (agent vs. environment vs. verifier vs. infrastructure) that the current design lacks.
4. **"Fix non-agent failures before using the score"** — a principle suggesting the anomaly filter should distinguish agent-behavior anomalies from environment anomalies.
5. **The 6 Verifier test fixtures** (known-good, valid alternative, realistic wrong, shortcut, prohibited collateral, missing evidence) — a concrete test matrix for the Commit Gate and for Sub 3.6's Reference Accuracy.
6. **"Accept all equivalent valid results"** — the project hasn't addressed that a legal agent can produce a correct result through different valid paths; the verifier should accept all, not just one preferred path.
7. **"A pass is not proof of quality"** — the Commit Gate should inspect accepted updates for shortcuts and weak criteria, not just rejected ones.

### Corroboration (the skill confirms what the project already decided)

1. **Harness engineering as RL** — the skill uses the same "harness" terminology the project adopted (decision #2), independently.
2. **Human review before applying** — the skill's "Mark approved only after explicit approval" matches the Commit Gate's mandatory human review.
3. **Incremental accumulation, not bulk** — the skill's "add the small set that helps the current Task" matches the cold path's anomaly-triggered batch processing.
4. **Separation of raw vs. distilled** — the skill's "keep Task truth in Task.md, not World Skill" matches the architecture's camada 1 (raw log) vs. camada 3 (strategy) separation.
5. **Reward hacking is real** — the skill's anti-gaming principles validate the Commit Gate's Casper-informed signal quality check as necessary, not paranoid.
6. **Traces ≠ truth** — "Do not treat a trace answer as independent truth" matches the architecture's "traces show observed behavior, not intended policy."

## Implications for specific sub-activities

### Sub 1.4 (mapear fluxos jurídicos) — Discovery methodology
The skill's discovery process (follow invocation paths, map harness + systems, cluster by work/outcome, preserve rare high-impact cases) is a ready-made methodology. The project's `analysis/` folder is already doing trace analysis; the discovery reference gives it a structure.

### Sub 1.5 (critérios de acerto/erro) — Task.md + Verifier design
Instead of writing an abstract criteria document, produce Task.md files with verification tables. The 6 test fixtures give a concrete test matrix. "Accepted alternatives" and "prohibited collateral change" are fields the current discussion hasn't addressed.

### Sub 1.6/1.7 (POCs) — "Complete only when" checklist
The skill's completion criteria adapt to POC validation: spec matches built, solvable from visible info, valid/invalid cases behave correctly, at least one real run read in full, non-agent failures separated, results delivered with evidence.

### Sub 3.6 (Reference Accuracy) — Verifier design principles
"Independent of the agent's claim," "never trust agent self-report," "accept equivalent results," "LLM judge only after code settles facts," "test the decision boundary with 6 fixtures."

### v2 harness-change loop — Harbor at stage 3
Already in the architecture (lines 219-229). The skill's Spec2Task (step 4) and Run-and-audit (step 5) give concrete sub-steps for what "sandbox validation" means: package audit, trial isolation, exercise every operation, test verifier fixtures, read full trajectory, classify failures.
