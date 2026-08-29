# Research Diary (Diário de Campo)

Rafael's personal field diary for the project — kept in Portuguese, as an ongoing practice, not a one-time document. New content is appended daily; each calendar month gets a new file.

## Design

The diary is deliberately structured as a miniature application of the same memory theory the project studies (Zhang et al., ACM TOIS 2025; Generative Agents/Park et al.): an **episodic** layer (raw daily entries, cheap to write) and a **semantic** layer (periodic distilled synthesis, more expensive, higher rereading value). The two layers are functionally distinct — the episodic layer is never rewritten or summarized in place; the semantic layer is derived, and can be regenerated if understanding changes. This isn't decorative — it's the same separation the work plan proposes for the agent's own memory mechanism (Sub 2.2), applied to the fellow's own research practice.

The diary serves three audiences at once, and every entry keeps serving all three without extra editing:

1. Rafael's own personal working memory (don't lose anything).
2. The project coordinator's tracking (reads the raw file, no processing needed).
3. Formal traceability against the Plano de Trabalho's Entregáveis (every entry is tagged by sub-atividade — see [`../docs/sub-activity-map.md`](../docs/sub-activity-map.md)).

## File convention

**One file per week, starting 24/08/2026.** `diario_campo_AAAA-MM-DD.md`, where `DD-MM-AAAA` is the Monday that opens the week (e.g. `diario_campo_2026-08-24.md` for the week of 24–30/08). A new week starts a new file with a standard header (project name, project number, one-line description of the episodic/semantic scheme, and the week's date range). The file *is* the week: entries accumulate through the week and the file closes with its own [weekly synthesis](#weekly-synthesis-the-semantic-layer) at the bottom — no more inserting a synthesis mid-file.

**Before 24/08/2026:** one file per calendar month (`diario_campo_AAAA-MM.md`), with weekly syntheses inserted at each week boundary inside that file. `diario_campo_2026-08.md` is the only file under this older convention — it stays as-is, not retroactively split into weekly files.

## Entry schema

Each entry (one `##` block per date; `###` for a second-or-later entry on the same day) carries:

**Required:**
- **Tipo** — `leitura | teste/POC | implementação | reunião | decisão | achado | observação livre`
- **Sub-atividade** — tagged against [`../docs/sub-activity-map.md`](../docs/sub-activity-map.md); falls back to `transversal` or `não classificado (confirmar)`
- **Canal** — `pessoal | informal-coordenador | formal-tutor` — keeps informal coordinator steering separate from formal tutor sign-off, a distinction the project explicitly needed (see [`../discussion/open-questions.md`](../discussion/open-questions.md))
- **Registro objetivo** — the fact itself, the episodic component

**Optional (only when there's real content):**
- **Reflexão** — subjective interpretation, hypothesis, caveat
- **Decisão/próximo passo** — anything decided or left as a next step
- **Tags** — free-form, lowercase, comma-separated

## Weekly synthesis (the semantic layer)

Whenever a new entry would start a new Monday–Sunday week, the closing week gets a `## Síntese da Semana — DD/MM a DD/MM/AAAA` block (Achados centrais / Decisões tomadas / Itens em aberto) appended at the bottom of that week's file — generated automatically, not on request. The point of reading a past week is now: open its file, read the synthesis at the bottom. The point of starting a new week is: open the new (near-empty) file, check the previous file's "Itens em aberto" to know what's still pending going in.

## Monthly close-out

At the start of a new calendar month (or on request), once every week that falls (even partially) in the closing month has its weekly file and synthesis: export a clean `.docx` for the coordinator — cover (month/year, project number, entry count) + the weekly syntheses of every week touching that month, in order, as the main body + the full episodic log (from those same weekly files) as an appendix. A week that spans a month boundary counts toward the month containing its Monday.

## Second semantic layer — monthly rollup (`summarization/`)

`summarization/sintese_AAAA-MM.md` is a derived, regenerable month-level digest: the weekly syntheses of every week whose Monday falls in that month, consolidated into one file — a real month-level distillation (central findings, decisions, still-open items, per-sub-activity counts) sitting on top of the verbatim weekly syntheses. It does **not** duplicate the episodic log and does **not** replace the coordinator `.docx` export — it's the cheap, in-repo semantic layer above the weekly one. Generated and refreshed by the `sintese-diario` skill; safe to regenerate any time the understanding of a past week changes.

## On persistence — read this if you're picking the diary back up in a new session

The workflow this diary was originally designed under (see the `diario-campo` skill) assumed an **ephemeral** execution environment with no persistent filesystem between sessions — the only durable storage was re-uploading the month's file to a Claude Project's Project Files after every update, with a manual reminder to do so baked into the skill's instructions.

**That constraint no longer applies now that this diary lives in this git repository.** A session with access to this repo can read the current month's file directly from `research-diary/`, append to it, and `git commit`/`git push` — no manual re-upload/reminder loop needed. If you're running the `diario-campo` skill from a session that has this repo checked out, prefer reading/writing here directly over the Project-Files round-trip; the skill's field schema, weekly-synthesis logic, and monthly-export process all still apply unchanged.

## Files

- [`diario_campo_2026-08.md`](diario_campo_2026-08.md) — August 2026, 17–23/08 (the last week under the monthly-file convention; complete, with its synthesis).
- [`diario_campo_2026-08-24.md`](diario_campo_2026-08-24.md) — week of 24–30/08 (current, in progress), first file under the new weekly-file convention.
- [`summarization/`](summarization/) — month-level rollups (`sintese_AAAA-MM.md`), one per calendar month, consolidating that month's weekly syntheses. Derived/regenerable; maintained by the `sintese-diario` skill.
