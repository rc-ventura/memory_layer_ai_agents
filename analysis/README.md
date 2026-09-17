# analysis/

Empirical analyses of raw agent traces from the legal-workflow pipeline (esteira jurídica) —
the "working memory" evidence base for the project's memory-layer hypothesis.

Each analysis lives in its own dated folder (`YYYY-MM-slug/`) containing:

- `pipeline/` — the executed Jupyter notebook (the reproducible pipeline, with outputs embedded)
  and any companion scripts (e.g. `drill_down.py` for case-level triangulation);
- `docs/` — the narrative documents: `01-racionais.md` (the plain-language logic), `02-relatorio-achados.md`
  (the findings report, Portuguese), `03-procedimento-validacao.md` (validation/audit procedure),
  `04-roadmap.md` (what's left);
- `literature/` — 🔎-level notes on the papers that ground the analysis (full text read by a
  sub-agent, bibliography verified against the PDF). See `papers/reading-queue.md` for what
  🔎 means and why it is not the same as "read";
- `resultados/` — derived CSVs, **git-ignored**: they carry client names, case numbers and
  document excerpts in the clear. Regenerate by running the notebook;
- `audit/` (optional) — independent audit reports and recomputation scripts.

Raw trace files (`*.csv.xz` at repo root or elsewhere) must never be committed in the clear
either — they contain unanonymized legal-case data.

## Methodological big picture

`analysis/` is not just a place to count errors or collect charts. The recurring goal is to build an
**empirical bridge** between:

1. the **raw trace** of a real agent system,
2. the **actual mechanisms of failure** visible in that trace,
3. and the smallest reusable **lesson / memory / operational correction** that could prevent the same failure from recurring.

In other words, the analyses try to answer a question of this form:

> What reusable knowledge, extracted from repeated failures in the raw trace, should be persisted,
> operationalized, or explicitly kept out of the agent so that the system stops rediscovering the same lesson in every execution?

### The ladder from trace to memory

```text
                          ┌─────────────────────────────┐
                          │ Literature                  │
                          │ - tests external fit        │
                          │ - suggests new analyses     │
                          │ - gives conceptual language │
                          └──────────────┬──────────────┘
                                         │
                                         │
┌────────────────┐    ┌────────────────┐ │  ┌──────────────────────────┐
│ Raw trace      │ -> │ Symptoms /     │-┼->│ Mechanisms / root-cause  │
│ (source truth) │    │ aggregates     │ │  │ proxies                  │
└────────────────┘    └────────────────┘ │  └──────────────────────────┘
                                         │                │
                                         │                v
                          ┌──────────────┴──────────────┐ ┌──────────────────────────┐
                          │ Validation                  │ │ Right unit of analysis   │
                          │ - recomputation             │ │ error -> cascade ->      │
                          │ - robustness tests          │ │ occurrence -> unit       │
                          │ - case drill-down           │ └──────────────────────────┘
                          │ - raw > derived             │                │
                          │ - independent audits        │                v
                          └─────────────────────────────┘ ┌──────────────────────────┐
                                                          │ Reusable lesson /        │
                                                          │ guidance                 │
                                                          └──────────────────────────┘
                                                                           │
                                                                           v
                                                          ┌──────────────────────────┐
                                                          │ Candidate memory unit /  │
                                                          │ operational decision     │
                                                          └──────────────────────────┘
                                                                           │
                                                                           v
                                                          ┌──────────────────────────┐
                                                          │ Evidence pack            │
                                                          │ + audit trail            │
                                                          └──────────────────────────┘
```

### What this means in practice

#### 1. Start from the raw trace

Start from the **raw trace**, not from papers, polished tables, or intuitions. Derived CSVs, notebooks,
and summary tables are for **counting and navigation**; they are not the final authority.

#### 2. Separate symptom from mechanism

A visible exception (`KeyError`, `TypeError`, `SyntaxError`, `Could not index`) is often only a
**surface signature**. If one signature mixes several different phenomena, the analysis should refine it
into a better **mechanism** or **root-cause proxy** that actually matches the research question.

#### 3. Use the right analytical unit

Step-level errors are not always independent events. When repeated failures are really one continuing
underlying problem, the right unit may be a **cascade**, an **occurrence**, or a **role-scoped unit**, not
one count per failing step.

#### 4. Move from "what failed" to "what should be remembered"

The end product is not just a label for an error. The stronger target is the smallest reusable
**lesson/guidance** that could help a future execution avoid the same failure. That lesson may become:

- **factual / environment** knowledge — facts about tools, schemas, documents, sandbox constraints;
- **experiential / strategy** knowledge — rules for how the agent should act;
- **non-memory** operational handling — harness, infra, retry policy, monitoring triggers.

#### 5. Let validation depth match claim strength

Not every claim needs the same evidentiary package.

- **Direct counts** (`n` errors, tokens, executions, durations, monthly totals) are often robust by
  construction -> independent recomputation may be enough.
- **Heuristic-dependent claims** (thresholds, matching rules, inventories, text comparisons) need
  **robustness tests** against plausible alternatives.
- **Prescriptive / memory-bearing / causal claims** ("this is the lesson to write", "this tool really
  returns schema X", "the agent corrected itself by doing Y") deserve the strongest treatment:
  **raw-case evidence packs, rule-based case selection, and independent audit reports**.

#### 6. Treat derived artifacts and evidence packs as different things

A useful default separation is:

- **derived artifacts** = compact views that help navigate and aggregate;
- **evidence packs** = analysis-specific folders that preserve the link back to selected raw cases;
- **independent audit reports** = a second reading that checks whether the analysis claim actually holds
  when reopened from the raw trace.

This matters because code can be wrong in a perfectly consistent way. A notebook can produce the same wrong
number hundreds of times. Evidence packs and independent audits exist so that a human can reopen the claim
without trusting the same computation that first produced it.

### Default rule of thumb for future analyses

If an analysis is mainly **descriptive**, lean on recomputation and selective case illustration.
If it is **heuristic**, add robustness testing.
If it is **prescriptive**, **causal**, or meant to produce a **memory unit**, escalate to the full chain:

```text
aggregate -> selected cases by explicit rule -> raw trace -> derived view -> independent audit
```

That is the default methodological move in `analysis/`: not just "count errors", but move from observed
trace behavior to a reusable, auditable explanation of what should be remembered, changed, monitored, or
kept outside the agent.

## Index

| Folder | What it analyzes |
|---|---|
| [`2026-09-trace-law-flow/`](2026-09-trace-law-flow/) | First raw trace (1,000 executions, Nov 2025 – Aug 2026): root-cause error taxonomy from step-level working memory, token/latency cost of failures, error propagation, cross-execution recurrence, silent-failure detectors, and the resulting memory-unit candidates. Grounded in four full-text-read taxonomy papers (`literature/`). Before presenting: `docs/03-procedimento-validacao.md` — pipeline audit, paper-reading order, and how to triangulate any number against a concrete raw-trace case (`pipeline/drill_down.py`); `docs/01-racionais.md` — the plain-language logic behind the analysis and what a robustness test is, for explaining rather than executing. |
