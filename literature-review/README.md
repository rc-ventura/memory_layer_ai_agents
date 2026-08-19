# Literature Review

The canonical review reports produced for the project's bibliographic deliverables, plus the primary and companion source files they were built from.

| Document | Sub-atividade | Scope |
|---|---|---|
| [`memory-in-ai-agents.md`](memory-in-ai-agents.md) | 1.1 | Memory in generative AI agents: short/long-term, episodic vs. semantic, update/consolidation/forgetting techniques, Hermes Agent vs. smolagents, legal application context. |
| [`deep-agents.md`](deep-agents.md) | 1.2 | LangChain Deep Agents and the "deep agent" architectural category: planning, sub-agents, filesystem-as-memory, long-horizon orchestration, governance/security surveys. |

Both documents are **living reviews** — Sub 1.1 and Sub 2.1 of the [work plan](../docs/work-plan.md) call for continuous refinement, not a one-time deliverable. When a new source is added to either review, also add its atomic note under [`../papers/`](../papers/) and update the index there.

## Structure

- `memory-in-ai-agents.md`, `deep-agents.md` — the two review reports (TL;DR → Key Findings → Details by theme → Recommendations → Caveats), each carrying peer-review status inline per source.
- [`visual-synthesis/`](visual-synthesis/) — a 15-page visual synthesis of the field's anchor survey (Zhang et al., ACM TOIS 2025), generated as a Gemini Notebook study aid and logged in the [research diary on 18/08/2026](../research-diary/diario_campo_2026-08.md).
- `sources/` — the original `.docx` deliverables these reviews were converted from, kept for provenance.

## How this relates to `papers/` and `discussion/`

- **`literature-review/`** — the report-grade deliverables: prose, organized by theme, matching the Plano de Trabalho's Entregável 1 format.
- **[`../papers/`](../papers/)** — one atomic note per source, same underlying facts, organized for lookup rather than reading start-to-end.
- **[`../discussion/`](../discussion/)** — cross-cutting synthesis that goes beyond either review alone (e.g. gaps found by cross-referencing tables, scope decisions, open questions).
