> **Sub-atividade:** 1.1, 1.3 · **Status:** Peer-reviewed (ICLR 2024) · **Theme:** Update, consolidation & forgetting · **Read by Rafael:** not yet

# Retroformer: Retrospective Large Language Agents with Policy Gradient Optimization

- **Authors:** Weiran Yao, Shelby Heinecke, Juan Carlos Niebles, Zhiwei Liu, Yihao Feng, Le Xue, Rithesh Murthy, Zeyuan Chen, Jianguo Zhang, Devansh Arpit, Ran Xu, Phil Mui, Huan Wang, Caiming Xiong, Silvio Savarese (Salesforce AI Research)
- **Year:** 2023/2024
- **Venue:** arXiv:2308.02151; ICLR 2024
- **Link:** https://arxiv.org/abs/2308.02151
- **Tags:** literal-rl, policy-gradient, retrospective-model, priority-5

## Core contribution

A principled framework for reinforcing large language agents by learning a separate **retrospective model** that automatically tunes the language agent's prompts from environment feedback via **policy gradient** — genuine gradient-based RL, not verbal self-critique. The retrospective model reflects on failed attempts and assigns credit to the agent's past actions based on future rewards, learning across arbitrary reward signals from multiple environments and tasks.

## Relevance to the project

Priority #5 in the [reading queue](reading-queue.md), and the diary's own anchor for Sub 1.3: the corpus's **only case of literal RL** (policy-gradient optimization against a reward signal), as opposed to [Reflexion](reflexion-2023.md)'s verbal self-critique or [Memory-R1](memory-r1-2025.md)'s PPO/GRPO over discrete memory operations. See [`../discussion/scope-and-terminology-decisions.md#2-what-reinforcement-learning-means-in-this-projects-title`](../discussion/scope-and-terminology-decisions.md#2-what-reinforcement-learning-means-in-this-projects-title) — Retroformer is direct evidence for what "genuinely RL" looks like among the corpus's cross-trial-learning models (it's one of the six with cross-trial ✓ in [the forgetting-gap finding](../discussion/cross-trial-vs-forgetting-gap.md)).

---
Source: verified directly against the arXiv abstract, ICLR 2024 poster page, and OpenReview listing (not from the original bibliographic review docx) — added 19/08/2026 at the user's request. This is bibliographic verification, not a substitute for Rafael's own reading — this item on the [reading checklist](reading-queue.md) stays open until he's actually read it.
