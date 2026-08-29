# Research Diary (Diário de Campo)

Rafael's personal field diary for the project — kept in Portuguese, as an ongoing practice, not a one-time document. It lives under `research-diary/`. New content is appended daily; a new file starts each week (see [File convention](#file-convention)).

## Design

The diary is deliberately structured as a miniature application of the same memory theory the project studies (Zhang et al., ACM TOIS 2025; Generative Agents/Park et al.): an **episodic** layer (raw daily entries, cheap to write) and a **semantic** layer (periodic distilled synthesis, more expensive, higher rereading value). The two layers are functionally distinct — the episodic layer is never rewritten or summarized in place; the semantic layer is derived, and can be regenerated if understanding changes. This isn't decorative — it's the same separation the work plan proposes for the agent's own memory mechanism (Sub 2.2), applied to the fellow's own research practice.

The diary serves three audiences at once, and every entry keeps serving all three without extra editing:

1. Rafael's own personal working memory (don't lose anything).
2. The project coordinator's tracking (reads the raw file, no processing needed).
3. Formal traceability against the Plano de Trabalho's Entregáveis (every entry is tagged by sub-atividade — see [`../docs/sub-activity-map.md`](../docs/sub-activity-map.md)).

## File convention

**One file per week, starting 24/08/2026.** `diario_campo_AAAA-MM-DD.md`, where `DD-MM-AAAA` is the Monday that opens the week. **The diary week runs Monday–Friday (5 working days)** — Saturday and Sunday are not part of it (e.g. `diario_campo_2026-08-24.md` covers the week of 24–28/08). A new week starts a new file with a standard header (project name, project number, one-line description of the scheme, and the week's date range). The weekly file *is* the week and holds **only** episodic entries — the week's distilled reflection lives in the [monthly digest](#the-monthly-digest-summarization), not at the bottom of the weekly file.

**Before 24/08/2026:** one file per calendar month (`diario_campo_AAAA-MM.md`), with weekly syntheses inserted at each week boundary inside that file. `diario_campo_2026-08.md` is the only file under this older convention — it stays as-is (synthesis included), not retroactively split.

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

## Convention — provider-agnostic agent attribution

When an entry (or a digest record) states that an **AI agent** did something rather than Rafael himself — read a paper, ran a reading sprint, helped design a scheme — refer to it **generically**: "an agent (no defined provider)", "agent-read, not Rafael-read". Never name the assistant, model, or provider. What the note carries is the *not-Rafael's-own-work* flag; which tool produced it is not the point and dates the record. Topical mentions of AI products as **subject matter** (a paper note about a given system, a tooling/quota fact from a meeting) keep their names — this convention is only about attributing work done for the diary.

## The monthly digest (`summarization/`)

The semantic layer is **one file per month**: `summarization/sintese_AAAA-MM.md`, holding **up to 4 records — one per week**. Each record is that week's reflection, drawn from the week's episodic entries and only *organized* here (the interpretation was already done in the entries themselves). Format per record: a heading `### Semana N · DD–DD/MM/AAAA · N registros`, a short paragraph of what happened, then `**Decidido:**` and `**Em aberto:**` lines. It is deliberately short — built to be read quickly, week by week.

An entry logged on a Saturday or Sunday still belongs to the week that just closed on Friday (that Monday's file); it doesn't open a new one. A week whose Monday falls in a given month counts toward that month (so a week spanning a month boundary goes to the month of its Monday).

The digest is derived and regenerable — safe to rebuild any time the understanding of a past week changes. It does **not** duplicate the episodic log and does **not** replace the coordinator `.docx` export. Generated and refreshed by the `sintese-diario` skill.

## Monthly close-out

At the start of a new calendar month (or on request), once the monthly digest holds every week of the closing month: export a clean `.docx` for the coordinator — cover (month/year, project number, entry count) + the digest's weekly records, in order, as the main body + the full episodic log (from that month's weekly files) as an appendix.

## Files

- [`diario_campo_2026-08.md`](diario_campo_2026-08.md) — August 2026, week 17–23/08 (last file under the monthly-file convention; keeps its embedded `## Síntese da Semana`).
- [`diario_campo_2026-08-24.md`](diario_campo_2026-08-24.md) — week of 24–28/08, first file under the weekly-file convention; episodic entries only.
- [`summarization/`](summarization/) — one monthly digest per calendar month (`sintese_AAAA-MM.md`), ≤4 condensed weekly records. Derived/regenerable; maintained by the `sintese-diario` skill.
