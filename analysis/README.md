# analysis/

Empirical analyses of raw agent traces from the legal-workflow pipeline (esteira jurídica) —
the "working memory" evidence base for the project's memory-layer hypothesis.

Each analysis lives in its own dated folder (`YYYY-MM-slug/`) containing:

- `pipeline/` — the executed Jupyter notebook(s) (the reproducible pipeline, with outputs embedded), a shared
  `base_pipeline.py` when the folder hosts more than one analysis (trace loading, step explosion, error
  classification — every notebook builds on it instead of copying cells), and any companion scripts (e.g.
  `drill_down.py` for case-level triangulation). **One notebook per analysis pass** — a pre-registered method
  applied to a set of objects: the §11 schema-mining pass covers units nº2 and nº10 in a single notebook
  because they share the method; units needing a different method wait for their own pass. Not one notebook
  per object, not one giant notebook — the boundary is the method. Each notebook **owns a section-number
  range** (the mining notebook owns §11.x, the next takes §12.x, and so on — a number is never reused);
- `docs/` — the narrative documents: `01-racionais.md` (the plain-language logic), `02-relatorio-achados.md`
  (the findings report, Portuguese), `03-procedimento-validacao.md` (validation/audit procedure),
  `04-roadmap.md` (what's left), `05-schema.md` (the raw-trace schema). Each analysis pass gets its own
  numbered pair named after the pass — `06-racionais-mineracao-unidades-n2-n10.md` +
  `07-relatorio-mineracao-unidades-n2-n10.md` for the nº2/nº10 mining pass, so the doc slug matches the
  notebook slug (`mineracao_unidades_n2_n10.ipynb`) — keeping the original section numbering so existing
  cross-references still resolve;
- `literature/` — 🔎-level notes on the papers that ground the analysis (full text read by a
  sub-agent, bibliography verified against the PDF). See `papers/reading-queue.md` for what
  🔎 means and why it is not the same as "read";
- `resultados/` — derived CSVs, **git-ignored**: they carry client names, case numbers and
  document excerpts in the clear. Regenerate by running the notebook. Case-level evidence lives in
  `resultados/evidencia/<section>_<analysis>/` — one folder per analysis, prefixed by the section number of
  the notebook that generated it (`11.4_conserto/` = §11.4 of the mining notebook). **Two-stage generation:**
  the notebook writes the structural part (`casos.csv`, `leia-me.md`, `derivados/`); `drill_down.py evidencia
  <folder>` writes `crus/` (the untouched raw-trace row — the source) and the per-case views, checking each
  excerpt against the raw row as it writes. `resultados/unidades_memoria.json` is the **canonical registry**
  of memory-unit records — not per-notebook: each pass reads it and rewrites it with its own records added or
  updated;
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

```mermaid
flowchart TB
    subgraph Ladder["The ladder — raw trace to memory unit"]
        direction TB
        Raw[("Raw trace<br/>(source of truth)")]
        Sym["Symptoms /<br/>aggregates"]
        Mec["Mechanisms /<br/>root-cause proxies"]
        Unit["Right unit of analysis<br/>error → cascade → occurrence → unit"]
        Lesson("Reusable lesson /<br/>guidance")
        Memory("Candidate memory unit /<br/>operational decision")
        Pack[("Evidence pack<br/>+ audit trail")]

        Raw --> Sym --> Mec --> Unit --> Lesson --> Memory --> Pack
    end

    Lit["Literature<br/>tests external fit · suggests new analyses<br/>gives conceptual language"]
    Val["Validation<br/>recomputation · robustness tests · case drill-down<br/>raw > derived · independent audits"]

    Lit -.->|conceptual language,<br/>candidate mechanisms| Mec
    Lit -.->|grounds| Val
    Val -.->|recomputes| Sym
    Val -.->|stress-tests| Mec
    Val -.->|drills into| Unit
    Val -.->|independently audits| Pack

    classDef stage fill:#e8f0fe,stroke:#4285f4,stroke-width:1.5px,color:#1a1a1a
    classDef output fill:#e6f4ea,stroke:#34a853,stroke-width:1.5px,color:#1a1a1a
    classDef crosscut fill:#f3e5f5,stroke:#8e24aa,stroke-width:1.5px,color:#1a1a1a,stroke-dasharray: 3 2

    class Raw,Sym,Mec,Unit stage
    class Lesson,Memory,Pack output
    class Lit,Val crosscut
```

Solid arrows are the main pipeline (top to bottom); dashed arrows are the two cross-cutting practices — Literature feeds vocabulary/candidate mechanisms and grounds Validation, while Validation checks back into every stage from symptoms to the final evidence pack, per [validation depth matching claim strength](#5-let-validation-depth-match-claim-strength) below.

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

Standalone reference (PT, sits at `analysis/` root rather than inside a dated folder because it's written to
be reusable groundwork for later analyses, not a one-pass deliverable):
[`schema-e-taxonomia-de-erros.md`](schema-e-taxonomia-de-erros.md) — where the error lives in the raw trace
(`ActionStep.error`), the N0→N4 symptom→mechanism→unit taxonomy cascade, and the guideline for the
per-family study report. Its §7 named the genealogy Sankey before it existed; that figure now lives in
`2026-09-trace-law-flow/docs/09-metodologia-erro-a-memoria.md` §1.1.

**Portable-code watch.** `2026-09-trace-law-flow/pipeline/genealogia_sankey.py` renders that Sankey with a
generic layout engine (barycenter column ordering + minimum node height for legibility — see its own
docstring) that has no dependency on error taxonomy specifically; only the data-prep half of that file is
analysis-specific. Not yet split into its own module — one caller isn't enough to validate the boundary — but
if a future analysis needs a similarly legible many-node Sankey, that's the code to lift out, and `analysis/`
(this level, not inside a dated folder) is the natural home for it.
