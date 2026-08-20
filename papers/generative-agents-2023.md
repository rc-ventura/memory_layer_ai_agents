> **Sub-atividade:** 1.1 · **Status:** Peer-reviewed · **Theme:** Episodic vs. semantic memory · **Read by Rafael:** not yet

# Generative Agents: Interactive Simulacra of Human Behavior

- **Authors:** Joon Sung Park, Joseph C. O'Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein
- **Year:** 2023
- **Venue:** UIST 2023 (arXiv:2304.03442, DOI 10.1145/3586183.3606763)
- **Link:** https://arxiv.org/abs/2304.03442
- **Tags:** episodic, semantic, reflection, memory-stream, recency-importance-relevance

## Core contribution

Introduces the "memory stream" (a chronological episodic log of observations) retrieved by a weighted combination of recency, importance, and relevance, plus a reflection mechanism that periodically synthesizes memories into higher-level insights (semantic memory). Ablations show memory, reflection, and planning are each critical to believable behavior.

## Relevance to the project

The canonical operationalization of episodic vs. semantic for LLM agents; the recency/importance/relevance scoring is a direct model for a signal-driven retrieval/update policy in a legal agent. Priority-reading anchor named in the [18/08/2026 diary entry](../research-diary/diario_campo_2026-08.md#18082026).

---
Source review: [`memory-in-ai-agents.md`](../literature-review/memory-in-ai-agents.md)
