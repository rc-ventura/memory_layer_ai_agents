> **Sub-atividade:** 1.2 · **Status:** Industry (blog) · **Theme:** Deep-agent ecosystem & orchestration

# Context Engineering for AI Agents: Lessons from Building Manus

- **Authors:** Yichao 'Peak' Ji (Manus)
- **Year:** 2025 (Jul 18, 2025)
- **Venue:** manus.im/blog
- **Tags:** filesystem-as-memory, context-engineering, restorable-compression

## Core contribution

"We treat the file system as the ultimate context in Manus: unlimited in size, persistent by nature, and directly operable by the agent itself… Our compression strategies are always designed to be restorable" (e.g., drop web-page content but keep the URL). A typical task "requires around 50 tool calls on average"; uses a recited todo.md to fight "lost-in-the-middle."

## Relevance to the project

The intellectual source for Deep Agents' file-system pillar; directly relevant to designing signal-driven, reversible memory updates.

---
Source review: [`deep-agents.md`](../literature-review/deep-agents.md)
