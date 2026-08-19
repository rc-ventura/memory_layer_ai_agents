> **Sub-atividade:** 1.2 · **Status:** Industry (engineering blog) · **Theme:** Deep-agent ecosystem & orchestration

# How We Built Our Multi-Agent Research System

- **Authors:** Anthropic
- **Year:** 2025 (published June 2025; feature launched April 2025)
- **Venue:** Anthropic engineering blog
- **Link:** https://www.anthropic.com/engineering/built-multi-agent-research-system
- **Tags:** orchestrator-worker, sub-agents, plan-persistence

## Core contribution

Orchestrator-worker pattern — a LeadResearcher plans, spawns subagents in parallel, then a CitationAgent attributes sources. "The lead agent spins up 3-5 subagents in parallel rather than serially... subagents use 3+ tools in parallel. These changes cut research time by up to 90% for complex queries." A multi-agent system with Opus 4 lead + Sonnet 4 subagents "outperformed single-agent Claude Opus 4 by 90.2%" on Anthropic's internal research eval, while using "about 15× more tokens than chats." The lead agent persists its plan to memory when context approaches the token limit.

## Relevance to the project

The canonical sub-agent orchestration reference; the "save the plan to memory to survive context overflow" pattern is directly transferable to long legal-research tasks.

---
Source review: [`deep-agents.md`](../literature-review/deep-agents.md) (the review named the source but did not include a URL; the link above was found and verified separately on 19/08/2026, at anthropic.com/engineering — not claude.com/blog).
