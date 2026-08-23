# Discussion

Cross-cutting synthesis that goes beyond any single source — findings from cross-referencing tables across papers, scope/terminology decisions, and open questions. This is where the [research diary](../research-diary/)'s "Achado" and "Decisão" entries get distilled into standing, revisable notes, rather than staying buried in daily chronological order.

| Note | What it covers |
|---|---|
| [`cross-trial-vs-forgetting-gap.md`](cross-trial-vs-forgetting-gap.md) | The central finding for Entregável 1: no model in the Zhang et al. corpus has both cross-trial learning and controlled forgetting — the empty intersection this project's mechanism targets. |
| [`framework-comparison-hermes-smolagents-deepagents.md`](framework-comparison-hermes-smolagents-deepagents.md) | The three-way Hermes Agent / smolagents / LangChain Deep Agents comparison — not found together in any existing source, spanning both literature reviews. |
| [`scope-and-terminology-decisions.md`](scope-and-terminology-decisions.md) | Decision log: non-parametric memory scope, what "RL" means in the project's title, cross-trial vs. cross-agent, a benchmark-dating correction, and the Reference Accuracy metric's scope. |
| [`open-questions.md`](open-questions.md) | Items flagged but not yet resolved — kept in one place instead of scattered across diary entries. |
| [`thumbs-feedback-reliability.md`](thumbs-feedback-reliability.md) | Is thumbs up/down a reliable RL signal? General RLHF literature on feedback noise, annotator disagreement, sycophancy, and reward overoptimization — and what it implies for Sub 1.5's acerto/erro criteria. |
| [`checkpoint-2026-08-20-reflections.md`](checkpoint-2026-08-20-reflections.md) | Reflections on the 20/08 tutor checkpoint meeting: primary-source confirmation of the harness-not-retraining decision, real-world grounding for the cross-agent scope narrowing, and two new open items on business-rule/MCP boundaries and dual signal-capture design. |

## When something belongs here vs. staying in the diary's `Reflexão` field

- Stays in the diary: a reflection tied to one day, not meant to be found or cited again later.
- Becomes a file here: it cross-references multiple sources, produces a decision or a new open question, or other documents will need to link to it. When adding a note here for that reason, also update whatever it resolves or corroborates (`open-questions.md`, `scope-and-terminology-decisions.md`, the relevant decision entry) and add it to the index table above — don't leave the loop half-closed.

Language: English by default, for consistency across this folder's cross-links. Write a specific note in Portuguese only on Rafael's explicit request for that note — a per-file override, not a folder-wide change.

## Relationship to the rest of the repo

```
literature-review/   →  the report-grade deliverables (prose, by theme)
papers/               →  one atomic note per source (lookup-oriented)
discussion/           →  synthesis ACROSS sources/reviews/diary (this folder)
research-diary/        →  the raw episodic + weekly-semantic log these notes are distilled from
```

A new discussion note should generally trace back to something already recorded in the diary or already claimed in a review — this folder is for connecting dots, not for introducing new unverified claims.
