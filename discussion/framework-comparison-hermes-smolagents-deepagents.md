> **Sub-atividade:** 1.1 / 1.2 / 1.6 · **Type:** Synthesis (spans both literature reviews)

# Three design philosophies: Hermes Agent vs. smolagents vs. LangChain Deep Agents

## Why this comparison exists

Neither literature review alone produces this table — [`memory-in-ai-agents.md`](../literature-review/memory-in-ai-agents.md) compares Hermes Agent and smolagents; [`deep-agents.md`](../literature-review/deep-agents.md) adds LangChain Deep Agents as a third pole and checks the literature for an existing three-way comparison. **None exists.** The closest source, Workspace-Bench 1.0 ([`../papers/workspace-bench-2026.md`](../papers/workspace-bench-2026.md), arXiv:2605.03596), benchmarks Hermes + Deep Agents + OpenClaw but omits smolagents. That gap is why this project's comparative framing is a defensible original contribution to Sub-activity 1.1 — and directly informs the choice of substrate for the Sub 1.6 minimal agents (native closed loop vs. transparent programmatic memory).

**Revise this novelty claim if** a survey or benchmark explicitly evaluating all three emerges — downgrade to "extends existing comparisons" rather than claiming originality.

## The comparison

| Dimension | Hermes Agent (Nous Research) | smolagents (Hugging Face) | LangChain Deep Agents |
|---|---|---|---|
| Design philosophy | Closed native learning loop; "the agent that grows with you" | Transparent, minimal, code-first step memory | Opinionated harness: plan + delegate + offload |
| Memory | Multi-layer: prompt memory (MEMORY.md/USER.md) + episodic SQLite FTS5 archive + skill memory; pluggable providers | `agent.memory.steps` list of ActionStep/PlanningStep logs; programmatically editable | StateBackend/StoreBackend/CompositeBackend + AGENTS.md |
| Learning | Autonomous session-to-skill conversion; self-improving skills | None native; developer controls everything | Skills + memory updated from usage; not a closed loop by default |
| Persistence | Persistent across sessions by default | In-run; persistence is developer-implemented | Opt-in cross-session via StoreBackend |
| Control surface | Curated/automatic | Fully explicit/white-box | Configurable middleware stack |
| Planning | Skills-driven | Optional PlanningStep at intervals | `write_todos` no-op planning tool |

Full source entries: [`hermes-agent.md`](../papers/hermes-agent.md) · [`smolagents.md`](../papers/smolagents.md) · [`langchain-deep-agents.md`](../papers/langchain-deep-agents.md).

## Reading the triangle

- **Hermes** = the closest thing to a ready-made version of this project's thesis: session history → reusable skills, with a native learning loop shipped out of the box. Strong reference design, but vendor-documented (not independent peer review) and opinionated/curated rather than explicit.
- **smolagents** = the opposite pole: nothing is automatic, but nothing is hidden either. Full programmatic access to `agent.memory.steps` makes it the natural substrate to *build* a controlled update mechanism on top of, since every read/write is inspectable and interceptable.
- **Deep Agents** = a third axis entirely — not really about the memory object itself, but about *context engineering around* a long-horizon task (planning, sub-agent isolation, filesystem offload), with memory persistence as an opt-in add-on (CompositeBackend) rather than the core design concern.

## Working recommendation (from the literature review's own conclusion)

Build the controlled update mechanism on **smolagents** (full programmatic memory access), adopt **Hermes'** skill-file format / progressive disclosure / trust-tiering as design patterns, and reference **Deep Agents'** CompositeBackend routing model (explicit, file-based, auditable, no mandatory embeddings) for how to make memory writes inspectable and permission-controllable — a requirement for financial-sector compliance. This is a starting hypothesis for Sub 1.6/1.7, not a locked-in architecture decision — Macroatividade 2 (Sub 2.2) is where the real stack choice gets made, informed by the Sub 1.6 minimal-agent POCs.

**Elaborated 24/08/2026:** [`knowledge-as-infra-architecture-hypothesis.md`](knowledge-as-infra-architecture-hypothesis.md) takes this starting point further — a six-component stack (Memory Store, Signal Capture, Update Engine, Commit Gate, Forgetting, MCP Integration) informed by the [24/08 reading sprint](reading-sprint-2026-08-24-queue-papers.md) — still a hypothesis, not a locked decision, same status as this note.

**Independent industry convergence found 25/08/2026:** LangChain's own "loop engineering" framing (blog: [The Art of Loop Engineering](https://www.langchain.com/blog/the-art-of-loop-engineering), verified via WebFetch — not an academic paper, an industry post, cited as such) describes Deep Agents' harness design as four nested loops — Agent (tool-calling), Verification (rubric-graded retry), Event-Driven (external trigger), Hill-Climbing (traces → analysis agent → proposed harness/prompt/tool changes, optionally human-reviewed). This maps closely onto the KaI hypothesis's hot-path/cold-path split (Loop 1 ≈ `recall_memory`; Loops 2/3 ≈ Signal Capture's copilot/systemic duality; Loop 4 ≈ Update Engine + Commit Gate) — and explicitly names memory as a hill-climbing target ("auxiliary context like memory and retrieved skills can be improved the same way"), independently confirming the memory-update-as-harness-adjustment framing this project already committed to via the tutor's own words. Two confirmed gaps in LangChain's current public design, though: human review before deploying a harness change is described as **optional**, not mandatory, and there is **no mention of versioning, rollback, or an audit trail** for hill-climbing changes — both are exactly what the Commit Gate (component D, SSGM-informed) adds on top. Practical implication if KaI gets built to plug into a Deep Agent: Loops 1–3 are a clean fit as-is; Loop 4 alone is insufficient for this project's compliance requirements and would need the stricter mandatory-gate-plus-versioning layer added, not just reused off the shelf.
