## Branches and pull requests

Applies to every agent in this repo (Claude Code here, Copilot on the compliance-side environment). Branch names follow `YYYY-MM-DD-short-slug` ([`CLAUDE.md`](CLAUDE.md)); commit and push only when Rafael asks.

- **Before any push**, check whether the branch is already in `main` (`git fetch origin main && git merge-base --is-ancestor HEAD origin/main && echo merged`). If it is, never force-push over it: `git stash push -u`, `git checkout -B <branch> origin/main`, `git stash pop`, then commit and push normally.
- **A branch that is already on `origin` is synced by merge, never by rebase** (`git merge origin/<base>`), so nothing already published is rewritten. Rebase only while the branch exists only locally.
- **Stacked PR:** a branch created from another branch whose PR is still open opens its own PR against that branch, so the diff shows only its own work, and the base PR merges first. Once the base PR merges, retarget the stacked PR (`gh pr edit <n> --base main`) and merge `origin/main` into the branch.
- **After a PR merges, it receives nothing more.** New work goes on a new dated branch (created from the updated `main`, or from the merged branch and then synced with `main`) and a new PR. Don't delete a branch at merge time if work will continue from it.
- **Conflicts in `analysis/decisoes.md`** are almost always two new entries added at the same spot: keep both. The list "Decisões de método, por data" runs oldest first, and a new decision goes **at the end of its own date** (the file's rule, line 12) — never at the end of the file nor at the top.

## Pipeline code hash (base 3)

A base-3 rodada records the hash of every file listed in `mineracao_observada.versoes_codigo()` (`analysis/2026-10-trace-law-flow-third/pipeline/`): among them `executar.py`, `genealogia_sankey.py`, `base_pipeline.py`, `paleta.py`. Changing any of them makes the specific mining and the rodada check refuse the current rodada until a new one runs on the compliance-side environment. Figures and reports that only read a rodada belong in `pipeline/execucao/` files outside that list and run as scripts (e.g. `execucao/figuras_genealogia.py`); don't add a command to `executar.py` for them.

## Working on the compliance-side environment (the "ambiente da base")

Applies to the Copilot agent there. The repository is the source of the code; that environment only runs it and holds the data.

- **Never edit a file in the base-3 hash list** (`mineracao_observada.versoes_codigo()`) **or the kit's `manifesto.json`** to get around an error, such as adding a mapping for a name an old round still has. Stop and bring the error text to Rafael: the cause is usually an outdated clone (`git fetch origin && git status -sb`, look for `behind`) or a round generated before a rename (pass `--rodada <the new one>`). A local edit there makes the next rodada record a code version that does not exist in the repository.
- **Running the pipeline and generating figures there is expected.** Display changes (a label, a title, a color) go only in files outside the hash list, such as `pipeline/execucao/figuras_*.py`; labels that live in `base_pipeline.py`, `paleta.py` or `genealogia_sankey.py` are in the hash list, so those changes are made in the repository.
- **Any change made there returns to the repository the same day** (a commit on a dated branch, or `git diff` brought to Rafael); otherwise the next `git pull` conflicts.

<!-- OPENWIKI:START -->

## OpenWiki

This repository has a generated `openwiki/` evidence index. It is optional just-in-time context, not required startup reading.

- Do not enumerate, preload, or search wikis at task start. Use retrieval when the user asks for it, when unfamiliar architecture or dependency behavior materially affects the task, or when source inspection leaves an important uncertainty. Stop once the question is grounded.
- When those conditions apply and OpenWiki retrieval tools are available, use `openwiki_search` for just-in-time context and `openwiki_read` for the relevant complete sections. If search returns `workspace_required`, ask which listed workspace to use and retry with its ID.
- Use `openwiki_list_workspaces` or `openwiki_list_wikis` when workspace membership itself needs to be discovered.
- If the retrieval tools are unavailable, read `openwiki/quickstart.md` and follow its links to the relevant pages.
- Treat source code and tests as authoritative. A brief's unknowns and review items are verification gaps, not automatic requirements.
- Prefer the narrowest quiet validation that proves the changed behavior. Preserve complete failure output.

The scheduled OpenWiki GitHub Actions workflow refreshes the repository wiki. Do not hand-edit generated OpenWiki pages unless explicitly asked; prefer updating source code/docs and letting OpenWiki regenerate.

<!-- OPENWIKI:END -->
