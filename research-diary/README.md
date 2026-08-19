# Research Diary (Diário de Campo)

Rafael's personal field diary for the project — kept in Portuguese, as an ongoing practice, not a one-time document. New content is appended daily; each calendar month gets a new file.

## Design

The diary is deliberately structured as a miniature application of the same memory theory the project studies (Zhang et al., ACM TOIS 2025; Generative Agents/Park et al.): an **episodic** layer (raw daily entries, cheap to write) and a **semantic** layer (periodic distilled synthesis, more expensive, higher rereading value). The two layers are functionally distinct — the episodic layer is never rewritten or summarized in place; the semantic layer is derived, and can be regenerated if understanding changes. This isn't decorative — it's the same separation the work plan proposes for the agent's own memory mechanism (Sub 2.2), applied to the fellow's own research practice.

The diary serves three audiences at once, and every entry keeps serving all three without extra editing:

1. Rafael's own personal working memory (don't lose anything).
2. The project coordinator's tracking (reads the raw file, no processing needed).
3. Formal traceability against the Plano de Trabalho's Entregáveis (every entry is tagged by sub-atividade — see [`../docs/sub-activity-map.md`](../docs/sub-activity-map.md)).

## File convention

One file per calendar month: `diario_campo_AAAA-MM.md` (e.g. `diario_campo_2026-08.md`). A new month starts a new file with a standard header (project name, project number, one-line description of the episodic/semantic scheme).

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

Whenever a new entry crosses into a new Monday–Sunday week, the previous week gets a `## Síntese da Semana — DD/MM a DD/MM/AAAA` block (Achados centrais / Decisões tomadas / Itens em aberto) inserted right after that week's last entry — generated automatically, not on request.

## Monthly close-out

At the start of a new calendar month (or on request), once every week of the closing month has its synthesis: export a clean `.docx` for the coordinator — cover (month/year, project number, entry count) + weekly syntheses as the main body + the full episodic log as an appendix.

## On persistence — read this if you're picking the diary back up in a new session

The workflow this diary was originally designed under (see the `diario-campo` skill) assumed an **ephemeral** execution environment with no persistent filesystem between sessions — the only durable storage was re-uploading the month's file to a Claude Project's Project Files after every update, with a manual reminder to do so baked into the skill's instructions.

**That constraint no longer applies now that this diary lives in this git repository.** A session with access to this repo can read the current month's file directly from `research-diary/`, append to it, and `git commit`/`git push` — no manual re-upload/reminder loop needed. If you're running the `diario-campo` skill from a session that has this repo checked out, prefer reading/writing here directly over the Project-Files round-trip; the skill's field schema, weekly-synthesis logic, and monthly-export process all still apply unchanged.

## Files

- [`diario_campo_2026-08.md`](diario_campo_2026-08.md) — August 2026 (current, in progress).
