> **Sub-atividade:** 1.1 · **Status:** Preprint · **Theme:** Update, consolidation & forgetting · **Read by Rafael:** not yet

# Memory-R1: Enhancing Large Language Model Agents to Manage and Utilize Memories via Reinforcement Learning

- **Authors:** Sikuan Yan, Xiufeng Yang, Zuchao Huang, Ercong Nie, Zifeng Ding, Zonggen Li, Xiaowen Ma, et al. (LMU Munich / MCML; senior authors Hinrich Schütze, Volker Tresp, Yunpu Ma)
- **Year:** 2025
- **Venue:** arXiv:2508.19828
- **Link:** https://arxiv.org/abs/2508.19828
- **Tags:** rl, ppo, grpo, add-update-delete-noop, literal-rl

## Core contribution

An RL framework with a Memory Manager that learns structured operations — ADD, UPDATE, DELETE, NOOP — after each dialogue turn, and an Answer Agent that filters retrieved entries before reasoning; both fine-tuned with PPO/GRPO using only QA-correctness as reward. "With only 152 training QA pairs, Memory-R1 outperforms strong baselines and generalizes across diverse question types, three benchmarks (LoCoMo, MSC, LongMemEval), and multiple model scales (3B-14B)" (per abstract).

## Relevance to the project

The closest analogue to the project's core goal — learning when/how to update memory via a reward/RL signal rather than heuristics; the discrete ADD/UPDATE/DELETE/NOOP action set is a ready-made controlled-update vocabulary. One of two genuinely literal-RL sources in the corpus (see [scope decisions](../discussion/scope-and-terminology-decisions.md)).

**Note:** Author count/order varies slightly across secondary citation lists; lead and senior authors are consistent.

---
Source review: [`memory-in-ai-agents.md`](../literature-review/memory-in-ai-agents.md)
