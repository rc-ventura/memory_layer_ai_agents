> **Sub-atividade:** 1.5 / 2.2 / 3.6 · **Type:** Cross-reference analysis (industry skill → project architecture) · **Logged:** [10/09/2026](../research-diary/Set/diario_campo_2026-09-07.md)

# LangChain Eval Engineering Skill — full analysis (blog post + actual SKILL.md source)

## Contact history

| Date | Source | What was extracted |
|---|---|---|
| 24/08/2026 | Video presentation (pre-blog) | **Trigger ≠ conteúdo** — Kafka event = trigger; full agent trajectory = content of the episodic trace. Propagated to component A's write-path design ([diary](../research-diary/Ago/diario_campo_2026-08-24.md#insight--trigger-de-armazenamento-conteudo-do-trace-e-acesso-a-stm)). |
| 10/09/2026 | Blog post "Towards Automating Eval Engineering" (22/07/2026) | Mechanics, isomorphism to the cold path, Harbor in the v2 loop. First version of this note. |
| 10/09/2026 (later) | **Actual SKILL.md + 12 reference files** (cloned from [github.com/langchain-ai/langchain-skills](https://github.com/langchain-ai/langchain-skills), `config/skills/eval-engineering/`) | Full structure, 7-step flow, World Knowledge Skill concept, Task.md control-plane spec, Verifier design principles, Calibration failure taxonomy, Discovery methodology. This update. |

The skill is **open source** (repo: 1.2k stars, public). It is a **SKILL.md** — same format as the project's own `.claude/skills/` skills. Install: `npx skills add langchain-ai/langchain-skills --skill eval-engineering`.

## What the skill is — and is not

"Skill" here means a **SKILL.md** — an instruction file installed in a coding agent (Claude Code, Codex, Devin). It is **not** "Skill-based memory" in the Hu/Liu survey's taxonomy (§4.2: executable code/API procedures the agent carries — a capability, not a dev instruction). Same word, different layers; they do not intersect.

The skill helps a **developer** build executable evals for *another* agent. The flow is offline: the coding agent (with the skill installed) inspects the agent's repo, optionally mines LangSmith traces, interviews the developer, produces Harbor tasks, runs them, and audits results. The coding agent can then (using its native coding capabilities, not the skill) modify the agent's harness and open a PR — but the skill itself stops at eval construction and audit.

## File structure (21 files)

```
config/skills/eval-engineering/
├── SKILL.md                    # 316 lines — the skill proper (7-step flow + reference routing)
├── agents/
│   └── openai.yaml              # agent config (model, provider)
├── assets/
│   ├── task/Task.md.template    # template for the human-reviewed Task Spec
│   └── world-skill/SKILL.md.template  # template for the World Knowledge Skill
├── references/                 # 12 reference files, read on-demand by decision
│   ├── discovery.md            # inspect repo, traces, harness, dependencies
│   ├── world-knowledge.md      # bootstrap + maintain reusable project knowledge
│   ├── task-design.md          # propose + write one Task Spec
│   ├── environment-building.md # live/frozen/simulated data + services
│   ├── synthetic-data.md       # create structured or natural-language data
│   ├── verifier-design.md      # independent evidence + scoring
│   ├── task-implementation.md  # Spec2Task: approved spec → audited runnable task
│   ├── calibration.md          # compare runs, classify failures, judge fairness
│   ├── harbor.md               # package and run Harbor tasks
│   ├── patterns.md             # known benchmark designs by domain
│   ├── examples/service-desk.md  # full worked example across two tasks
│   └── multi-turn-simulation/
│       ├── guide.md
│       ├── runner.py            # multi-turn runner script
│       ├── model_user.py        # LLM-simulated user
│       └── harbor_example.py    # Harbor adapter
└── scripts/
    ├── compare_tool_schemas.py  # compare tool schemas
    └── snapshot_sqlite_state.py # read-only SQLite state snapshot
```

## The 7-step flow (from SKILL.md)

### 1. Inspect inputs and existing World knowledge

Review every input: repository, Harness, traces, existing Tasks/runs, existing World knowledge, human goal. Follow the active Harness through prompts, models, tools, services, state, effects, focused tests. Inspect existing Task instructions, parsers, Verifiers, reward paths, run evidence.

If the user supplies traces: review complete runs. Learn real requests, dependency behavior, state shapes, errors, failure conditions. **"Do not treat a trace answer as independent truth"** — traces show observed behavior, not intended policy.

If `.agents/skills/<project>-world/SKILL.md` or `.claude/skills/<project>-world/SKILL.md` exists, read it. Follow its routing for knowledge relevant to the current Task.

### 2. Propose and select a Task

Propose **one** grounded Task in the first user-facing design response. State: the real work and capability, the condition that makes it non-trivial, the Environment and independent evidence it needs, the important failure it can detect, how it differs from existing Tasks, and the main open decision.

In the same response, show the current World Skill content and the additions/corrections this Task suggests. **"Keep the Task's exact request, focal records, expected result, hidden truth, and exact scoring rules out of the World Skill"** — that stays in Task.md.

Let the user revise both before implementation. Offer alternatives only when a real user choice changes the design.

### 3. Write and review the Task Spec and World Skill

Copy the Task template to `evals/<suite>/tasks/<task-id>/Task.md`. This is the **human-reviewed control-plane spec** — purpose, exact input, agent conditions, Environment, Verification, fairness/leakage, open decisions. Create/update the World Skill simultaneously. Show both to the user. **Mark approved only after explicit approval.** If implementation changes the request or scoring, update Task.md, set status back to Draft, show the diff, require re-approval.

**"Never copy or mount Task.md into the evaluated agent's workspace or image."** The agent receives `instruction.md` and only the Environment state intended for the run.

### 4. Apply Spec2Task

Turn the approved spec into a runnable task: confirm model/trials/timeout/cost with the user, complete a package audit (every required file, entry point, path, permission, config, mount, service, reward output), check setup and trial isolation, exercise every operation, run the reference path, test the Verifier with: a clear valid result, a valid alternative, a realistic wrong result, a shortcut, a prohibited collateral change, and missing/corrupt evidence.

### 5. Run and audit

Run the actual Harness through Harbor. **Read the complete trajectory, not only the reward.** Inspect: messages, model calls, tool calls, results, retries, errors; initial and final Environment state; service/setup/readiness/reset/cleanup evidence; each Verifier criterion's evidence, decision, and error.

Classify each unsuccessful run (8 categories — see Calibration below). **"Fix non-agent failures before using the score."**

Model comparison is optional — use it only when contrast can answer a named uncertainty. **"Pass rates and model ordering do not prove Task quality."**

### 6. Reconcile project World knowledge

After the audit, reconcile the World Skill with what the completed Task proved. Show the user: proposed reusable knowledge, supporting evidence, how another Task would use it, where it should live, what remains Task-specific. Remove or narrow ideas the Task disproved.

### 7. Repeat

Use Tasks 2 and 3 to test the World Skill — does it reduce rediscovery, improve specs, preserve relationships, reuse proven operations, prevent known defects? When several Tasks have exercised the shared knowledge, the next cycle can propose several independent Task Specs in parallel.

## Key concepts from the reference files

### World Knowledge Skill (`references/world-knowledge.md`)

A **repo-local skill** (`<project>-world/SKILL.md`) that accumulates reusable project-specific knowledge across Tasks — "improves future Task Spec generation and Spec2Task implementation for one project." Contains: Task families and variations, tool/service contracts, entity relationships, approved data sources, setup/reset procedures, independent truth sources, **project-specific shortcuts/reward hacks/invalid-run signatures**, reusable commands/scripts/fixtures.

**What goes in the World Skill vs. stays in Task.md:**

| World Skill (reusable across Tasks) | Task.md (one Task only) |
|---|---|
| Task families, coverage, known weak designs | Exact request |
| Tool and service contracts exercised by Tasks | Focal records and initial state |
| Entity relationships, identities, permissions | Expected result |
| Approved data sources and generation methods | Exact criteria and hidden evidence |
| Setup, readiness, reset, cleanup procedures | One-off setup or workaround |
| Independent truth sources and reusable Verifier checks | Decisions with no use outside that Task |
| Project-specific shortcuts, reward hacks, invalid-run signatures | |
| Reusable commands, scripts, fixtures, templates | |

**Approval model:** "A human can approve the Task while rejecting a proposed generalization. Treat a World Skill change as accepted only after human review." **Common failures to avoid:** speculative encyclopedia (large map before one Task shows what's useful), task leakage (storing answers in the World Skill), generic duplication, empty taxonomy, untested automation, stale certainty, hidden dependency.

### Task.md — the control-plane spec (`assets/task/Task.md.template`)

A human-reviewed file that lives **beside** the Harbor task but is **never exposed to the agent**. Sections: Purpose and evidence, Agent input, Relevant agent conditions, Environment, Verification (table of required/prohibited results × independent evidence × exact check × pass condition), Fairness and leakage, Open decisions.

The separation principle: **Task.md = control plane (human-reviewed, contains hidden truth and scoring); instruction.md = agent input (what the agent sees).** The agent never sees the scoring rules, the expected result, or the hidden truth.

### Verifier design (`references/verifier-design.md`)

**"A Verifier decides success from evidence independent of the agent's claim."** Start with one sentence: `Pass iff <observable successful outcome>`.

Principles:
- Prefer programmatic checks. Recompute results from raw evidence. Compare initial and final state.
- **"Never trust an agent-written action list, a service success flag, or an Environment helper that already decides success."**
- Accept all equivalent valid results. Do not require a preferred path, exact wording, response length, keyword, citation count, or tool-call count unless that property is the tested capability.
- Use an LLM judge only for semantic meaning, only after code has settled objective facts. **"Ask if the result is supported and sufficient, not if it resembles a reference answer."** Pin and record the judge model. Bound all agent text and files before grading — treat them as untrusted data.
- **Test the decision boundary** with 6 fixtures: known-good (Pass), valid alternative (Pass), realistic wrong (Fail), shortcut/reward hack (Fail), prohibited collateral change (Fail), missing/corrupt evidence (Infrastructure error).
- **"Review every zero and every suspicious pass."** A pass is not proof of quality — inspect for shortcuts, leaked truth, weak criteria, unscored collateral effects.

### Calibration — failure classification (`references/calibration.md`)

8 categories for every unsuccessful run:

| Cause | Meaning | Action |
|---|---|---|
| Capability | Fair access, correct infra, intended work failed | Keep as agent result |
| Missing information | Required fact not visible or discoverable | Fix Task or Environment |
| Harness | Runtime, tool, prompt, session, or adapter wrong | Fix Harness |
| Environment | State, service, permission, fidelity, or reset wrong | Fix Environment |
| False rejection | A valid result failed | Fix Verifier |
| False acceptance | An invalid result passed | Fix Verifier |
| Leakage | Hidden truth or scoring logic was visible | Fix packaging or boundary |
| Infrastructure | Build, startup, timeout, judge, credential, cleanup failed | Repair and rerun unscored |

**"Do not make a Task harder to hide a defect. First repair all non-agent causes and rerun affected trials."**

To change difficulty: change one supported condition (more state, longer history, stale/conflicting facts, permissions, delayed effects, required clarification, collateral-change risk). Keep required evidence visible or normally discoverable.

### Discovery (`references/discovery.md`)

How to inspect an agent repository and traces:

1. **Review the repository** — follow each real invocation path through: input/prompt assembly → model creation → agent loops → tools → tool implementations → skills/hooks/sessions/memory → files/databases/APIs → focused tests.
2. **Map the Harness and connected systems** — how requests enter, information added before the model, tools per condition, exact request/response/error shapes, state read/changed, permissions/identity/time/ordering, loops/retries/fallbacks, user-visible effects, differences from Harbor reconstruction.
3. **Review traces** — reconstruct user-visible interaction in time order. Look for: what users ask, context provided, facts expected to be discovered, ambiguity/follow-ups, desired outputs/state changes, common strategies, **failed tool calls, malformed arguments, empty results, permission errors, timeouts, retries**, loops/abandoned attempts/unsupported claims/partial completion, **user dissatisfaction/corrections/rejection/abandonment/explicit acceptance**, cases where user appears satisfied despite hidden error or unhappy despite correct work.
4. **Cluster real requests** — by underlying work and outcome, not exact wording. Dimensions: user goal, systems/tools needed, read-only vs. mutating, context supplied, information to discover, permission conditions, single/multi-turn, common failure, independent evidence available. **Preserve rare but important requests** (safety, permissions, high-impact effects).
5. **Review traces in batches** — for large sets, use subagents with bounded non-overlapping batches. Main agent merges clusters, keeps disagreements visible, audits a sample.

**Safety:** "Never read, print, copy, store, or ask the human to paste secret values." Tell the human what dependency is needed, why, and how the project expects access. Record reusable setup patterns in World knowledge — never the secret.

## How Harbor works (mechanics)

Harbor ([harborframework.com](https://www.harborframework.com/docs)) is a container-based agent evaluation framework. Two agent integration modes:

- **Installed agent** (common): the agent's code is **baked into the Dockerfile**. When `harbor run` executes, the container boots with the agent already inside; Harbor injects `instruction.md` as input; the agent runs headless; the verifier runs afterwards and writes a reward file to `/logs/verifier/`.
- **External agent**: the agent runs outside the container and sends bash commands via `BaseEnvironment.exec` (puppeteer/puppet model).

`harbor run -p <task-path> -a <agent> -m <model>` builds the container, runs the agent, runs the verifier, records: trajectory, artifacts, reward, errors. The same eval can run against different models, prompts, tools, and agent versions — the environment and task remain stable while the agent configuration changes.

## Isomorphism to the project's cold path

The skill's 7-step flow and the project's cold path (components B → C → D) are structurally isomorphic:

| Skill step | Project cold path |
|---|---|
| 1. Inspect (repo + traces + World knowledge) | **Signal Ledger** (component B) + **episodic log** (component A, camada 1) — traces are the raw material |
| 2. Propose a Task | **Update Engine** (component C) — proposes a change from flagged cases |
| 3. Write + review Task Spec (human approval) | **Commit Gate** (component D) — human review, versioned, rollback |
| 4. Spec2Task (implement, validate, test Verifier) | **v2 sandbox validation** (Harbor, stage 3 of the harness-change loop) |
| 5. Run and audit (read full trajectory, classify failures) | **Monitor** (stage 7) — does the error signature recur? |
| 6. Reconcile World knowledge | **Memory Store update** (component A, camada 3 — strategy layer) — accumulated heuristics |
| 7. Repeat | Next cycle of the cold path |

The structural match is exact. The difference is automation: the skill assumes a human developer in the loop at every step; the project's cold path automates steps 1-2 (signal → proposal) and gates step 3 (human review via Commit Gate).

## Where Harbor already appears in the architecture

Harbor is already referenced in the v2 harness-change loop ([`knowledge-as-infra-architecture-hypothesis.md`](knowledge-as-infra-architecture-hypothesis.md#the-v2-harness-change-loop--shape-only-09092026--runs-in-a-simulator-not-production), lines 219–229), at stage 3 (sandbox validation). This was shaped 09/09/2026 and remains **v2, not v1 scope**. Two reasons:

1. **Hard prerequisite**: building the replay harness with mocked tools is considerable work v1 cannot afford.
2. **Domain mismatch**: the skill assumes resettable environments with immediate reward. A legal workflow's outcome is sparse, delayed, human-judged, and side effects are real (ofícios expedidos). Even at v2, verification stays **cross-execution**, not re-rollout.

## "Harness engineering" = this project's RL

The blog states: *"Teams can fit agent behavior to them through harness engineering such as changing prompts & tools or fine-tuning."* This is exactly the project's decision #2 ([`scope-and-terminology-decisions.md#2`](scope-and-terminology-decisions.md#2-what-reinforcement-learning-means-in-this-projects-title)): the mechanism's RL is harness adjustment driven by explicit thumbs up/down, not SFT, not policy gradient. The skill's own terminology ("Harness" = "the complete agent Harbor runs, including prompts, model loop, tools, hooks, memory, sessions, and adapter") uses the same word the project adopted — independent corroboration from a source that predates the tutor's 20/08 confirmation.

## What does NOT map directly (trade-offs)

- **Harbor/Dockerfile is likely overkill for this project.** Agents run on the [EMPRESA] platform, not standalone containers. The concept of "reproducible environment" is correct, but the implementation would differ — probably a platform sandbox, not a Harbor Dockerfile.
- **The skill interviews a human; the systemic path (Kafka) has no interviewer.** The skill assumes a developer in the loop at every step. In the systemic signal-capture path (no human turn exists), there is no interviewer. In the copilot path (human present), the interview model applies.
- **The skill evaluates the agent; this project evaluates the mechanism that changes the agent.** The skill's eval measures "did the agent complete the task?"; this project's eval needs to measure "did the memory update improve the agent's success rate over time?" — a second-order metric (delta of performance, not absolute performance).

## See also

- [`eval-engineering-skill-architecture-connections.md`](eval-engineering-skill-architecture-connections.md) — detailed component-by-component mapping to the knowledge-as-infra architecture, and what the skill's concepts mean for specific sub-activities (1.4, 1.5, 3.6, and the v2 harness-change loop).
- [`knowledge-as-infra-architecture-hypothesis.md`](knowledge-as-infra-architecture-hypothesis.md) — the canonical architecture doc, where Harbor appears in the v2 loop (lines 219–229).
- [`scope-and-terminology-decisions.md#2`](scope-and-terminology-decisions.md#2-what-reinforcement-learning-means-in-this-projects-title) — the harness-not-retraining decision the skill's own terminology independently corroborates.
