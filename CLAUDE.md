# Instructions for Claude working in this repo

Repo overview, folder purposes, and general conventions are in [`README.md`](README.md) — read that first. This file only covers working rules established during actual sessions, that aren't obvious from the folder structure alone.

## Language

- `research-diary/` — always Portuguese. Personal artifact, never touch this rule.
- `docs/` — an official artifact (the work plan) or a summary derived from one specific source in Portuguese (e.g., a meeting transcript) stays in **Portuguese**, verbatim in spirit even when it's a written summary, not a transcript copy.
- `discussion/` — **English by default**, for consistency across the folder (cross-links between notes rely on this). Write a specific note in Portuguese only if Rafael explicitly asks for that note — it's a per-file override, not a folder-wide change. Don't infer the override from context; ask if unsure.

## When a reflection belongs in the diary vs. in `discussion/`

- Stays in the diary's `Reflexão` field: a note tied to one day, not meant to be found or cited again later.
- Becomes a `discussion/` file: it cross-references multiple sources, produces a decision or a new open question, or other documents will need to link to it. If you're creating a `discussion/` note, also update whatever it resolves or corroborates (`open-questions.md`, `scope-and-terminology-decisions.md`, the relevant decision entry) and add it to `discussion/README.md`'s index — don't leave the loop half-closed.

## Citation discipline

- Never fabricate an arXiv ID, author list, or date. This repo's own convention (`papers/reading-queue.md`) already distinguishes **verified** (bibliographic facts checked against a primary or citing source) from **read** (Rafael actually read it) — never conflate the two when adding or citing a paper.
- `arxiv.org` direct fetch (`WebFetch`) is blocked by this environment's network egress. Use `WebSearch` instead to verify titles/authors/dates/claims — it works and has been reliable for this.

## The project's RL terminology — keep this precise

The mechanism (decided 20/08/2026 with the tutor, primary source in [`docs/checkpoint-2026-08-20-tutor-kickoff.md`](docs/checkpoint-2026-08-20-tutor-kickoff.md)) is **non-parametric, harness-level RL** — closer to a contextual bandit or Reflexion's "verbal RL" than to policy-gradient RL. It updates memory/harness content from a reward signal (thumbs up/down, batched), not model weights. Never describe it as "just prompt engineering" (it has the trial→reward→update structure of RL) and never conflate it with Retroformer/Memory-R1-style policy-gradient fine-tuning (a different family, useful only as contrast). Full reasoning in [`discussion/scope-and-terminology-decisions.md#2`](discussion/scope-and-terminology-decisions.md#2-what-reinforcement-learning-means-in-this-projects-title).

## Meeting records — the established pattern

When a new meeting (tutor, infra, colleague) gets transcribed and needs to enter the repo, follow the pattern set by the 20/08 tutor checkpoint:

1. Source transcript → `docs/sources/<slug>.docx` (or original format), untouched.
2. Factual summary → `docs/<slug>.md`, Portuguese, no analysis — just what was said/shown.
3. Cross-cutting reflections → `discussion/<slug>-reflections.md`, English by default, connecting the meeting to the work plan, existing decisions, and open questions — and updating those files with backlinks, per the rule above.
4. Close the loop in `research-diary/`: if a prior entry flagged the meeting/transcript as pending, update that entry rather than only adding a new one.

The infra meeting with Fed/Yoshio (21/08) is still pending this treatment — transcript not yet attached.

## Diary logging

Only create or edit a `research-diary/` entry when Rafael explicitly asks (the `diario-campo` skill's own trigger rules already cover this — don't log passing mentions of work as diary entries).

## Git workflow note specific to this project

This branch (`claude/rl-user-feedback-flows-sbynzm`) has been merged mid-session more than once while work continued. Before pushing, check whether it's already merged:

```
git fetch origin main
git merge-base --is-ancestor HEAD origin/main && echo "merged"
```

If merged, don't force-push over it — `git stash push -u`, `git checkout -B <branch> origin/main`, `git stash pop`, then commit and push normally.
