> **Sub-atividade:** 1.1 · **Status:** Peer-reviewed · **Theme:** Architectures: short-term vs. long-term

# Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

- **Authors:** Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, Sebastian Riedel, Douwe Kiela
- **Year:** 2020
- **Venue:** NeurIPS 2020 (arXiv:2005.11401)
- **Link:** https://arxiv.org/abs/2005.11401
- **Tags:** rag, retrieval, non-parametric, foundational

## Core contribution

Introduces RAG, combining a parametric LLM with a non-parametric retrieval store (Wikipedia via dense retrieval) to ground generation and reduce hallucination.

## Relevance to the project

The foundational "external memory as retrieval" pattern; for legal agents, statutes/case law form an authoritative non-parametric memory that can be updated far more cheaply than retraining. (The Harvard Journal of Law & Technology explicitly frames RAG's vector database as "non-parametric memory" for law — practitioner motivation, non-academic.)

---
Source review: [`memory-in-ai-agents.md`](../literature-review/memory-in-ai-agents.md)
