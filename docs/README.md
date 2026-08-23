# Docs

Reference material this project is answerable to: the formal work plan, the sub-activity map used to tag everything else, and records of meetings that shaped scope or architecture.

| File | What it is |
|---|---|
| [`work-plan.md`](work-plan.md) | The official Plano de Trabalho, kept verbatim in Portuguese. Source: [`sources/Plano_de_Trabalho_Rafael_Ventura.docx`](sources/Plano_de_Trabalho_Rafael_Ventura.docx). |
| [`sub-activity-map.md`](sub-activity-map.md) | Macroatividade/sub-atividade signal table, used to tag [research diary](../research-diary/) entries. |
| [`checkpoint-2026-08-20-tutor-kickoff.md`](checkpoint-2026-08-20-tutor-kickoff.md) | Summary of the 20/08 tutor checkpoint meeting (Portuguese, at Rafael's request). Source: [`sources/Checkpoint_Tutor_2026-08-20.docx`](sources/Checkpoint_Tutor_2026-08-20.docx). |
| `sources/` | Original artifacts (transcripts, the formal work-plan docx) behind the files above, untouched. |

## Meeting-record pattern

When a new meeting (tutor, infra, colleague) gets transcribed and needs to enter the repo, follow the pattern set by the 20/08 tutor checkpoint:

1. Source transcript → `sources/<slug>.docx` (or original format), untouched.
2. Factual summary → `<slug>.md` here, Portuguese, no analysis — just what was said/shown.
3. Cross-cutting reflections → [`../discussion/<slug>-reflections.md`](../discussion/), English by default — connecting the meeting to the work plan, existing decisions, and open questions, and updating those files with backlinks (see [`../discussion/README.md`](../discussion/README.md)).
4. Close the loop in the [research diary](../research-diary/): if a prior entry flagged the meeting/transcript as pending, update that entry rather than only adding a new one.

The infra meeting with Fed/Yoshio (21/08) is still pending this treatment — transcript not yet attached.

## Language

Official artifacts (the work plan) and meeting summaries derived from a specific source stay in **Portuguese**, matching the source. This differs from [`discussion/`](../discussion/), which defaults to English — see the [root README's language note](../README.md#a-note-on-language).
