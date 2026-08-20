> **Sub-atividade:** 1.1 · **Status:** Peer-reviewed · **Theme:** Update, consolidation & forgetting · **Read by Rafael:** not yet

# Reflexion: Language Agents with Verbal Reinforcement Learning

- **Authors:** Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao
- **Year:** 2023
- **Venue:** NeurIPS 2023 (arXiv:2303.11366)
- **Link:** https://arxiv.org/abs/2303.11366
- **Tags:** verbal-rl, reflection, feedback-signal, not-literal-rl

## Core contribution

Reinforces agents through linguistic feedback rather than weight updates — the agent verbally reflects on task feedback signals and stores self-reflections in an episodic memory buffer to improve subsequent trials. "Reflexion achieves a 91% pass@1 accuracy on the HumanEval coding benchmark, surpassing the previous state-of-the-art GPT-4 that achieves 80%" (per abstract).

## Relevance to the project

The seminal "signal → reflection → memory update" loop without fine-tuning; the "feedback signal" framing maps directly to the project's "signal-driven" update requirement. Likely origin of the project title's "aprendizado por reforço" phrasing — but NOT literal RL: no reward model, no policy gradient, just autocritique concatenated to the prompt (see [scope decisions](../discussion/scope-and-terminology-decisions.md)).

---
Source review: [`memory-in-ai-agents.md`](../literature-review/memory-in-ai-agents.md)
