# Docs

Reference material this project is answerable to: the formal work plan, the sub-activity map used to tag everything else, records of meetings that shaped scope or architecture, and the monthly reports submitted to the fellowship institution.

| File / folder | What it is |
|---|---|
| [`work-plan.md`](work-plan.md) | The official Plano de Trabalho, kept verbatim in Portuguese. Source: [`sources/Plano_de_Trabalho_Rafael_Ventura.docx`](sources/Plano_de_Trabalho_Rafael_Ventura.docx). |
| [`sub-activity-map.md`](sub-activity-map.md) | Macroatividade/sub-atividade signal table, used to tag [research diary](../research-diary/) entries. |
| [`checkpoints/`](checkpoints/) | Factual summaries of transcribed meetings (tutor, infra, colleagues), Portuguese, matching the source language. One `.md` per meeting; cross-cutting analysis lives in [`../discussion/`](../discussion/). |
| [`reports/`](reports/) | Monthly reports submitted to the fellowship institution (Inova Talentos / IPT Open), one file per month (`relatorio-mensal-AAAA-MM.md`) plus its short send-ready summary. Versioned record of what was actually submitted. |
| `sources/` | Original artifacts (transcripts, the formal work-plan docx) behind the files above, untouched. |

## Meeting-record pattern

When a new meeting (tutor, infra, colleague) gets transcribed and needs to enter the repo, follow the pattern set by the 20/08 tutor checkpoint:

1. Source transcript → `sources/<slug>.docx` (or original format), untouched.
2. Factual summary → `checkpoints/<slug>.md`, Portuguese, no analysis — just what was said/shown.
3. Cross-cutting reflections → [`../discussion/<slug>-reflections.md`](../discussion/), English by default — connecting the meeting to the work plan, existing decisions, and open questions, and updating those files with backlinks (see [`../discussion/README.md`](../discussion/README.md)).
4. Close the loop in the [research diary](../research-diary/): if a prior entry flagged the meeting/transcript as pending, update that entry rather than only adding a new one.

Meetings recorded so far: `checkpoints/checkpoint-2026-08-20-tutor-kickoff.md` and `checkpoints/checkpoint-2026-08-21-infra-arquitetura.md`. Still pending this treatment: the meeting on the Hermes framework's native agent memory.

## Language

Official artifacts (the work plan) and meeting summaries derived from a specific source stay in **Portuguese**, matching the source. This differs from [`discussion/`](../discussion/), which defaults to English — see the [root README's language note](../README.md#a-note-on-language).
