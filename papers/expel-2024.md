> **Sub-atividade:** 1.1 · **Status:** Peer-reviewed (AAAI 2024) · **Theme:** Update, consolidation & forgetting · **Read by Rafael:** not yet

# ExpeL: LLM Agents Are Experiential Learners

- **Authors:** Andrew Zhao, Daniel Huang, Quentin Xu, Matthieu Lin, Yong-Jin Liu, Gao Huang
- **Year:** 2023/2024
- **Venue:** arXiv:2308.10144; Proceedings of the AAAI Conference on Artificial Intelligence (AAAI 2024), pp. 19632–19642
- **Link:** https://arxiv.org/abs/2308.10144
- **Tags:** insight-extraction, success-and-failure, no-fine-tuning, priority-1

## Core contribution

An agent that autonomously gathers experiences from a collection of training tasks and extracts natural-language insights from them — without any parametric updates to the underlying LLM. Insights are distilled by comparing successful and failed trajectories, then stored and retrieved to guide future decisions. Official code: github.com/LeapLabTHU/ExpeL.

## Relevance to the project

This is priority #1 in the [reading queue](reading-queue.md), tagged in the diary as the "protocolo de extração de insight sucesso/falha" that would feed the operation vocabulary for Sub 3.2. ExpeL is the corpus's clearest example of turning raw trial outcomes (win/loss) directly into reusable natural-language insight — the same signal-driven distillation pattern the project's Objetivo describes, but implemented with an explicit success-vs-failure comparison step rather than reflection alone (contrast with [Reflexion](reflexion-2023.md)) or full RL fine-tuning (contrast with [Retroformer](retroformer-2024.md)).

---
Source: verified directly against the arXiv abstract and AAAI proceedings page (not from the original bibliographic review docx) — added 19/08/2026 at the user's request. This is bibliographic verification, not a substitute for Rafael's own reading — #1 on the [reading checklist](reading-queue.md) stays open until he's actually read it.
