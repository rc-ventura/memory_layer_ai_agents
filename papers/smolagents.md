> **Sub-atividade:** 1.1 · **Status:** Industry (open-source repo) · **Theme:** Frameworks (industry) · **Read by Rafael:** not yet

# smolagents

- **Authors:** Hugging Face
- **Year:** —
- **Venue:** Open-source, Apache-2.0
- **Link:** https://huggingface.co/docs/smolagents
- **Tags:** transparent-memory, code-agent, programmatic-control, comparison-target

## Core contribution

A minimalist library ("the logic for agents fits in ~1,000 lines of code") whose flagship CodeAgent writes and executes Python at each step, while a ToolCallingAgent uses JSON tool calls; code-writing agents reportedly cut "steps and LLM calls by about 30%" vs. standard JSON tool-calling. Memory model: an explicit `agent.memory` object holding an ordered list of steps (TaskStep, ActionStep, PlanningStep); `agent.write_memory_to_messages()` serializes logs into chat messages, and developers can read, replay, or directly modify `agent.memory.steps`. Secure execution via a restricted local interpreter or E2B/Docker/Blaxel sandboxes.

## Relevance to the project

Transparent, inspectable short-term/working memory with full programmatic control, but no native long-term learning loop or automatic session→skill consolidation — the contrast that motivates the project. Recommended substrate for the controlled update mechanism (memory fully exposed) in the review's [Recommendations](../literature-review/memory-in-ai-agents.md#recommendations). Other pole of the [three-way framework comparison](../discussion/framework-comparison-hermes-smolagents-deepagents.md).

---
Source review: [`memory-in-ai-agents.md`](../literature-review/memory-in-ai-agents.md)
