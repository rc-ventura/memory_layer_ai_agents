# Memory Layer for AI Agents — Research Repository

Personal research repository for Rafael Coelho Ventura's Inova Talentos / IPT Open fellowship project (Instituto Itaú de Ciência, Tecnologia e Inovação, Nº 1335844346):

> **Mecanismo de atualização de memória para agentes de IA generativa com aprendizado por reforço aplicado a fluxos jurídicos**

The project builds and validates a memory-update mechanism for generative AI agents in legal workflows — using performance signals (human review, user-area feedback) to adjust, in a controlled way, the instructions/examples/operational context stored in an agent's memory. Bolsista: Rafael Coelho Ventura. Tutor: Luis Felipe Chary de Lima. Aug 2026 – Jul 2027. Full details in [`docs/work-plan.md`](docs/work-plan.md).

This repo *is* the study/lab notebook for that work: bibliographic review, per-source notes, cross-cutting discussion, and a daily research diary — kept together and versioned instead of scattered across documents.

## Structure

```
docs/                   Work plan (Plano de Trabalho) and the sub-activity map used to tag everything else
literature-review/      The two report-grade bibliographic reviews (Sub 1.1, Sub 1.2) + two survey mind maps
papers/                 One atomic note per paper/framework cited (36 so far) + a reading queue
discussion/             Cross-cutting synthesis: findings, framework comparisons, scope decisions, open questions
research-diary/         Daily episodic log + weekly synthesis, one file per month, in progress
```

Each folder has its own `README.md` with more detail. Suggested entry points depending on what you're after:

- **Want the state of the art, read start-to-end?** → [`literature-review/`](literature-review/)
- **Looking up one specific paper?** → [`papers/README.md`](papers/README.md) (indexed table)
- **Want the "why," the decisions, the gaps found?** → [`discussion/`](discussion/)
- **Want to know what happened this week?** → [`research-diary/`](research-diary/)

## How the pieces relate

The four content folders sit at different altitudes over the same material:

```
literature-review/  →  report-grade deliverables, prose, organized by theme (what gets submitted)
papers/              →  one atomic note per source, organized for lookup (what gets cited)
discussion/          →  synthesis across sources/reviews/diary (what gets decided)
research-diary/       →  raw episodic + weekly-semantic log (what actually happened, day by day)
```

The diary is where new findings first land; the strongest ones get distilled into `discussion/`; sources cited along the way get an atomic note in `papers/`; and the two `literature-review/` reports are the polished, submittable form of Sub 1.1 and Sub 1.2 — refined continuously, not written once.

## Status

**Macroatividade 1** (theoretical grounding + comparative exploration of memory approaches) is in progress, target 30/10/2026. See [`docs/work-plan.md`](docs/work-plan.md) for all five macroatividades and their deliverables, and the [research diary](research-diary/) for day-to-day progress.

## A note on language

Source documents that are official or personal artifacts (the work plan, the research diary) are kept verbatim in their original Portuguese. Everything written to connect them — this README, folder READMEs, discussion notes, paper-note scaffolding — defaults to English, matching the language the two bibliographic reviews were authored in. Say the word if you'd rather have the connective material in Portuguese instead; it's a straightforward pass to redo.
