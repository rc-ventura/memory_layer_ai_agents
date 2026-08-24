# Instructions for Claude working in this repo

This file is an index, not a rulebook — each doc below is the actual source of truth. Update the doc, not this file, when a convention changes; add a link here only when something new needs a home.

## Where things live

- **Repo structure, folder purposes, language convention** → [`README.md`](README.md)
- **Diary: entry schema, weekly-file cadence, when to log** → [`research-diary/README.md`](research-diary/README.md)
- **Work plan, sub-activity map, meeting-record pattern** → [`docs/README.md`](docs/README.md)
- **When something becomes a `discussion/` note vs. staying in the diary's `Reflexão` field** → [`discussion/README.md`](discussion/README.md)
- **Citation verification discipline (verified vs. read, WebSearch not WebFetch for arXiv)** → [`papers/reading-queue.md`](papers/reading-queue.md)
- **The project's RL terminology — non-parametric/harness, not SFT, not policy-gradient** → [`discussion/scope-and-terminology-decisions.md#2`](discussion/scope-and-terminology-decisions.md#2-what-reinforcement-learning-means-in-this-projects-title)
- **Open items across the project** → [`discussion/open-questions.md`](discussion/open-questions.md)

## Session-specific operational notes

Only create or edit a `research-diary/` entry when Rafael explicitly asks (the `diario-campo` skill's own trigger rules already cover this).

This branch has been merged mid-session more than once while work continued. Before pushing:

```
git fetch origin main
git merge-base --is-ancestor HEAD origin/main && echo "merged"
```

If merged, don't force-push over it — `git stash push -u`, `git checkout -B <branch> origin/main`, `git stash pop`, then commit and push normally.
