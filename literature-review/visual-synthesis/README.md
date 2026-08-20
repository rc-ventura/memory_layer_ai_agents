# Visual Resources — Mind Maps

Two mind maps of the field's anchor surveys. Each ships in two forms: a rendered **PNG** (real image file, for pasting into docs/slides or viewing outside GitHub) and the **Mermaid source** it was generated from (`source/*.mmd`, a few KB of text, edit and re-render with `mmdc -i source/<file>.mmd -o <file>.png`, or just paste the block into any Mermaid live editor). Both replace the earlier 17MB PDF export. Each is a redrawn recreation of a mind map shared in conversation — faithful to the structure and labels shown, but not a pixel copy of an original image file. If a branch/label looks off to you, it's worth a quick correction rather than assuming it's exactly right.

## 1. Memory in LLM-Based Agents

Synthesizes *"A Survey on the Memory Mechanism of Large Language Model based Agents"* (Zhang et al., 2024/2025 — see [`../memory-in-ai-agents.md`](../memory-in-ai-agents.md#theme-4-highlighted-first--survey--review-papers-on-memory-in-llm-agents) and the atomic note at [`../../papers/zhang-2025-memory-survey.md`](../../papers/zhang-2025-memory-survey.md)). Logged: diary entry [18/08/2026](../../research-diary/diario_campo_2026-08.md#18082026), Sub-atividade 1.1.

![Mind map: Memory in LLM-based Agents](memory-in-llm-based-agents.png)

<details>
<summary>Mermaid source (click to expand)</summary>

```mermaid
graph LR
  A["Memory in LLM-based Agents"]

  A --> B["Concept and Definitions"]
  A --> C["Necessity of Memory"]
  A --> D["Implementation Strategies"]
  A --> E["Evaluation Framework"]
  A --> F["Memory-enhanced Applications"]
  A --> G["Future Directions"]

  D --> D1["Memory Sources"]
  D1 --> D1a["Inside-trial (Interaction steps)"]
  D1 --> D1b["Cross-trial (Past experiences)"]
  D1 --> D1c["External Knowledge (Tools/Wikis)"]

  D --> D2["Memory Forms"]
  D2 --> D2a["Textual Form"]
  D2a --> D2a1["Complete Interactions"]
  D2a --> D2a2["Recent (Cache-based)"]
  D2a --> D2a3["Retrieved (Similarity-based)"]
  D2 --> D2b["Parametric Form"]
  D2b --> D2b1["Fine-tuning (Domain expertise)"]
  D2b --> D2b2["Knowledge Editing (Facts/Traits)"]

  D --> D3["Memory Operations"]
  D3 --> D3a["Writing"]
  D3a --> D3a1["Raw storage"]
  D3a --> D3a2["Summarization"]
  D3 --> D3b["Management"]
  D3b --> D3b1["Merging redundant info"]
  D3b --> D3b2["Reflection (High-level)"]
  D3b --> D3b3["Forgetting (Unimportant)"]
  D3 --> D3c["Reading"]
  D3c --> D3c1["Context retrieval"]
  D3c --> D3c2["Similarity matching"]

  E --> E1["Direct Evaluation"]
  E1 --> E1a["Subjective (Coherence, Rationality)"]
  E1 --> E1b["Objective (Correctness, F1-score, Latency)"]
  E --> E2["Indirect Evaluation"]
  E2 --> E2a["Conversation consistency"]
  E2 --> E2b["QA performance"]
  E2 --> E2c["Task success rate (Minecraft, Code)"]

  F --> F1["Social Simulation (Role-playing)"]
  F --> F2["Personal Assistant (Contextual chat)"]
  F --> F3["Open-world Games (Skill learning)"]
  F --> F4["Expert Systems"]
  F --> F5["Code Generation & Recommendation"]
```

</details>

**Reading note:** this maps directly onto the **Sources → Forms → Operations** structure used throughout [`../memory-in-ai-agents.md`](../memory-in-ai-agents.md) and the [sub-activity map](../../docs/sub-activity-map.md) — the "Implementation Strategies" branch above is the same taxonomy behind [the cross-trial × forgetting gap finding](../../discussion/cross-trial-vs-forgetting-gap.md).

## 2. Memory in the Age of AI Agents

Synthesizes *"Memory in the Age of AI Agents"* (Hu, Liu, et al., Dec 2025, arXiv:2512.13564 — see [`../../papers/memory-in-the-age-of-ai-agents-2025.md`](../../papers/memory-in-the-age-of-ai-agents-2025.md)), the survey behind the project's three-axis vocabulary: **Forms, Functions, Dynamics**.

![Mind map: Memory in the Age of AI Agents](memory-in-the-age-of-ai-agents.png)

<details>
<summary>Mermaid source (click to expand)</summary>

```mermaid
graph LR
  A["Memory in the Age of AI Agents"]

  A --> P["Preliminaries"]
  A --> FO["Forms (Representational Units)"]
  A --> FU["Functions (Why Agents Need Memory)"]
  A --> DY["Dynamics (Operational Lifecycle)"]
  A --> RF["Resources and Frontiers"]

  P --> P1["Definitions"]
  P1 --> P1a["LLM-based Agent Systems"]
  P1 --> P1b["Agent Memory Systems"]
  P --> P2["Conceptual Comparisons"]
  P2 --> P2a["vs. LLM Memory (Model Internal Dynamics)"]
  P2 --> P2b["vs. RAG (Static Knowledge Access)"]
  P2 --> P2c["vs. Context Engineering (Resource Management)"]

  FO --> FO1["Token-level Memory"]
  FO1 --> FO1a["Flat (1D)"]
  FO1a --> FO1a1["Dialogue"]
  FO1a --> FO1a2["Preference"]
  FO1a --> FO1a3["Profile"]
  FO1a --> FO1a4["Experience"]
  FO1a --> FO1a5["Multimodal"]
  FO1 --> FO1b["Planar (2D)"]
  FO1b --> FO1b1["Tree Structures"]
  FO1b --> FO1b2["Graph Structures"]
  FO1 --> FO1c["Hierarchical (3D)"]
  FO1c --> FO1c1["Pyramid Structures"]
  FO1c --> FO1c2["Multi-Layer Graphs"]
  FO --> FO2["Parametric Memory"]
  FO2 --> FO2a["Internal Parametric"]
  FO2 --> FO2b["External Parametric"]
  FO --> FO3["Latent Memory"]
  FO3 --> FO3a["Generate"]
  FO3 --> FO3b["Reuse"]
  FO3 --> FO3c["Transform"]

  FU --> FU1["Factual Memory"]
  FU1 --> FU1a["User Factual"]
  FU1 --> FU1b["Environment Factual"]
  FU --> FU2["Experiential Memory"]
  FU2 --> FU2a["Case-based"]
  FU2 --> FU2b["Strategy-based"]
  FU2 --> FU2c["Skill-based"]
  FU2 --> FU2d["Hybrid"]
  FU --> FU3["Working Memory"]
  FU3 --> FU3a["Single-turn"]
  FU3 --> FU3b["Multi-turn"]

  DY --> DY1["Memory Formation"]
  DY1 --> DY1a["Semantic Summarization"]
  DY1 --> DY1b["Knowledge Distillation"]
  DY1 --> DY1c["Structured Construction"]
  DY1 --> DY1d["Latent Representation"]
  DY1 --> DY1e["Parametric Internalization"]
  DY --> DY2["Memory Evolution"]
  DY2 --> DY2a["Consolidation"]
  DY2 --> DY2b["Updating"]
  DY2 --> DY2c["Forgetting"]
  DY --> DY3["Memory Retrieval"]
  DY3 --> DY3a["Timing and Intent"]
  DY3 --> DY3b["Query Construction"]
  DY3 --> DY3c["Retrieval Strategies"]
  DY3 --> DY3d["Post-Retrieval Processing"]

  RF --> RF1["Current Resources"]
  RF1 --> RF1a["Benchmarks and Datasets"]
  RF1 --> RF1b["Open-Source Frameworks"]
  RF --> RF2["Research Frontiers"]
  RF2 --> RF2a["Automated Memory Management"]
  RF2 --> RF2b["RL-Memory Integration"]
  RF2 --> RF2c["Multimodal Memory"]
  RF2 --> RF2d["Shared Multi-Agent Memory"]
  RF2 --> RF2e["Trustworthy Memory"]
```

</details>

**Reading note:** the **Dynamics → Memory Evolution (Consolidation / Updating / Forgetting)** branch is exactly the project's sub-topic — see [`../../papers/memory-in-the-age-of-ai-agents-2025.md`](../../papers/memory-in-the-age-of-ai-agents-2025.md) for why this survey's axis maps onto the project. **Research Frontiers → RL-Memory Integration** is the direct link to Sub 1.3.
