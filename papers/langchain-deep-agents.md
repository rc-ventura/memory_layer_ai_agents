> **Sub-atividade:** 1.1 · **Status:** Industry (blog + open-source repo + docs) · **Theme:** Frameworks (industry)

# LangChain Deep Agents (`deepagents`)

- **Authors:** LangChain (Harrison Chase, co-founder & CEO)
- **Year:** 2025–
- **Venue:** Blog (langchain.com/blog/deep-agents, Jul 30 2025); GitHub (github.com/langchain-ai/deepagents); Docs (docs.langchain.com/oss/python/deepagents)
- **Link:** https://github.com/langchain-ai/deepagents
- **Tags:** agent-harness, planning, sub-agents, filesystem-memory, comparison-target

## Core contribution

An "agent harness" built on LangGraph, defined by four pillars: a detailed system prompt (inspired by Claude Code), a planning tool (`write_todos`, explicitly a context-engineering no-op rather than an execution engine), sub-agent delegation (isolated context, "context quarantine"), and a virtual file system for context offload/memory. Memory is layered and opt-in: ephemeral `StateBackend` by default; durable cross-thread memory via `CompositeBackend` routing to a `StoreBackend`; `AGENTS.md` always-loaded instructions/preferences.

## Relevance to the project

Third pole of the [three-way framework comparison](../discussion/framework-comparison-hermes-smolagents-deepagents.md): planning/sub-agent/filesystem harness with opt-in cross-session persistence, contrasted with Hermes' closed learning loop and smolagents' transparent step-memory. The CompositeBackend routing model (explicit, file-based, auditable, no mandatory embeddings) is recommended as an architectural reference for legal-workflow memory design.

**Note:** Do not confuse with RUC-NLPIR's unrelated "DeepAgent" paper (arXiv:2510.21618, WWW 2026) — see that entry's disambiguation note.

---
Source review: [`deep-agents.md`](../literature-review/deep-agents.md)
