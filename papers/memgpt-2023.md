> **Sub-atividade:** 1.1 · **Status:** Preprint (widely cited) · **Theme:** Architectures: short-term vs. long-term

# MemGPT: Towards LLMs as Operating Systems

- **Authors:** Charles Packer, Sarah Wooders, Kevin Lin, Vivian Fang, Shishir G. Patil, Ion Stoica, Joseph E. Gonzalez
- **Year:** 2023
- **Venue:** arXiv:2310.08560 (now the Letta framework)
- **Link:** https://arxiv.org/abs/2310.08560
- **Tags:** os-analogy, paging, tiered-memory, context-management

## Core contribution

Virtual context management inspired by OS memory hierarchies — tiered "main context / recall / archival" storage with function-call-driven paging and interrupts, letting the LLM manage its own memory across the context boundary.

## Relevance to the project

The canonical short-term/long-term tiering pattern; the function-call paging model is a concrete template for a controlled write path. Caveat from later work: MemGPT provides no principled forgetting, confidence estimation, or offline consolidation — its compression is append-then-summarize, not homeostatic.

---
Source review: [`memory-in-ai-agents.md`](../literature-review/memory-in-ai-agents.md)
