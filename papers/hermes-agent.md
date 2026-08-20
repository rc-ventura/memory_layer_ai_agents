> **Sub-atividade:** 1.1 · **Status:** Industry (open-source repo) · **Theme:** Frameworks (industry) · **Read by Rafael:** not yet

# Hermes Agent

- **Authors:** Nous Research
- **Year:** —
- **Venue:** Open-source, MIT license
- **Link:** https://github.com/NousResearch/hermes-agent
- **Tags:** closed-learning-loop, skills, session-to-skill, layered-memory, comparison-target

## Core contribution

A closed learning loop that (a) tracks multi-step tasks in an episodic layer (every tool call, decision branch, correction), (b) after several successful completions of a task pattern distills a reusable skill as a `SKILL.md` file (agentskills.io-compatible) with progressive disclosure so idle skills cost near-zero tokens, and (c) can patch its own skills mid-session via a `skill_manage` tool. Layered memory: MEMORY.md (facts), USER.md (user model), plus the skills library; cross-session recall via SQLite FTS5 with LLM summarization; optional deeper self-improvement via the Atropos RL pipeline (RLHF/DPO).

## Relevance to the project

A production embodiment of the project's thesis (session history → reusable rules/skills with a native learning loop); skill-file transparency and trust-tiering (builtin > official > community) are attractive for auditable legal use. One pole of the [three-way framework comparison](../discussion/framework-comparison-hermes-smolagents-deepagents.md).

**Note:** Claims come from vendor docs/blogs, not independent peer review. A fan site (hermes-agent.ai) is unaffiliated — cite the official repo/docs (hermes-agent.nousresearch.com).

---
Source review: [`memory-in-ai-agents.md`](../literature-review/memory-in-ai-agents.md)
