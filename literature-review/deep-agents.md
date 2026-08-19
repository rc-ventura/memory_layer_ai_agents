> **Sub-atividade:** 1.2 · **Status:** living document, refined continuously (Sub 2.1) · **Source:** [`sources/Revisao_Bibliografica_Deep_Agents.docx`](sources/Revisao_Bibliografica_Deep_Agents.docx) · **See also:** per-source notes in [`../papers/`](../papers/)

# LangChain Deep Agents and the "Deep Agent" Architectural Category: A Sourced Bibliographic Review

## TL;DR

- LangChain's Deep Agents is a genuine, well-documented framework — the open-source deepagents Python library (github.com/langchain-ai/deepagents), an official blog post by Harrison Chase ("Deep Agents," July 30, 2025), and formal docs at docs.langchain.com — built on the LangGraph runtime as an "agent harness" defined by four pillars: a detailed system prompt, a planning tool, sub-agent delegation, and a virtual file system. It is a legitimate third concrete reference point alongside Hermes Agent and smolagents.
- "Deep agents" is a real emerging architectural category — long-horizon LLM agents distinguished from shallow/reactive ReAct-style agents by explicit planning, context offloading to a file system, sub-agent orchestration, and (optionally) cross-session persistent memory — popularized primarily by LangChain and grounded in patterns from Claude Code, Anthropic's multi-agent research system, OpenAI Deep Research, and Manus. The term is largely industry-coined, not yet a formal academic taxonomy label.
- No single source compares all three frameworks (Hermes Agent / smolagents / LangChain Deep Agents). The closest is Workspace-Bench (arXiv:2605.03596), which benchmarks Hermes, LangChain Deep Agents, and OpenClaw — but omits smolagents. This is a genuine, defensible gap the fellowship review can claim to address.

## Key Findings

- Deep Agents is verified and legitimately documented. Primary sources are the deepagents GitHub repo, the July 30, 2025 LangChain blog post by Harrison Chase, and the official documentation. LangChain describes it as an "agent harness" — the same core tool-calling loop as other frameworks, but with built-in capabilities. In Chase's own words on the Sequoia Capital podcast "Context Engineering Our Way to Long-Horizon Agents," "now we have deep agents, which I'd call an agent harness… Harnesses are more like batteries included. So when we talk about deep agents… we actually give it a planning tool by default."
- The four defining characteristics per Chase's original blog: (a) a detailed system prompt (inspired by Claude Code's recreated prompts), (b) a planning tool, (c) sub-agents for context isolation, and (d) a file system for offloading/memory. The blog is explicit that applications like "Deep Research," "Manus," and "Claude Code" "have gotten around this limitation by implementing a combination of four things: a planning tool, sub agents, access to a file system, and a detailed prompt," and that "Planning (even if done via a no-op tool call) is a big component of that" — i.e., the to-do tool is a context-engineering device, not an execution engine.
- Memory in Deep Agents is layered and configurable, with genuine cross-session persistence available but not on by default. The default StateBackend is ephemeral (scoped to a thread_id); durable cross-thread memory requires a CompositeBackend routing a path such as /memories/ to a StoreBackend backed by a LangGraph Store. Persistent instructions/preferences also load at startup from AGENTS.md memory files.
- The broader "deep agent" discourse distinguishes deep/long-horizon agents from shallow ReAct loops and connects to Anthropic's orchestrator-worker research system, Manus's file-system-as-memory context engineering, and academic long-horizon agent work.
- The academic literature uses "long-horizon agents" rather than "deep agents" as the scholarly term. There is a distinct RUC-NLPIR paper literally titled "DeepAgent" (arXiv:2510.21618, WWW 2026) — an unrelated end-to-end reasoning model, NOT LangChain's library. Care must be taken to avoid conflating the two.

## Details

### 1. Primary sources verifying LangChain Deep Agents

**(A) LangChain blog — "Deep Agents"** (INDUSTRY BLOG POST / primary announcement)

- Author/org: Harrison Chase (co-founder & CEO, LangChain). Date: July 30, 2025. URL: langchain.com/blog/deep-agents.
- Core contribution: Coins/popularizes the term "deep agents" for agents able to "dive deep" and plan/execute over long horizons, contrasting them with "shallow" agents (an LLM calling tools in a loop naively). Identifies the four components — detailed system prompt, planning tool, sub-agents, file system — abstracted from Claude Code, Deep Research, and Manus. Announces the deepagents pip package. Notably candid that the planning to-do tool "doesn't do anything! It's basically a no-op … just context engineering strategy to keep the agent on track."
- Relevance: This is the canonical definitional source for the framework and the term. For legal workflows it establishes planning-as-context-engineering and file-system offloading as the two mechanisms most relevant to controlled memory updates.

**(B) `deepagents` GitHub repository** (INDUSTRY / OPEN-SOURCE CODE)

- Org: langchain-ai. URL: github.com/langchain-ai/deepagents. Also a JS/TS port (deepagentsjs), a UI (deep-agents-ui), a tutorial repo (deep-agents-from-scratch), and a managed offering (managed-deepagents).
- Core contribution: Reference implementation. create_deep_agent(model=..., tools=..., system_prompt=..., subagents=..., backend=...). Built on LangGraph for durable execution, streaming, human-in-the-loop. Describes itself as "the batteries-included agent harness."
- Relevance: Auditable, self-hostable, model-agnostic — important for a financial institution needing on-prem/compliance control.

**(C) Official documentation — Deep Agents overview & context engineering** (INDUSTRY DOCS)

- URL: docs.langchain.com/oss/python/deepagents/overview (plus /context-engineering, /customization, /comparison).
- Core contribution: The most complete architecture reference. Organizes the harness into four capability groups: Execution environment (tools/MCP, virtual filesystem with ls/read_file/write_file/edit_file/delete/glob/grep, filesystem permissions, code execution), Context management (skills via SKILL.md progressive disclosure, memory via AGENTS.md, summarization/offloading, prompt caching), Delegation (opt-in TodoListMiddleware task planning as of v0.7, and task-tool subagents with fresh/isolated context), and Steering (human-in-the-loop interrupts).
- Memory specifics: Short-term StateBackend (ephemeral, per-thread), long-term StoreBackend (persists across threads/sessions via LangGraph Store), hybrid CompositeBackend (routes /memories/ to persistent store). Memory files in AGENTS.md are always loaded; the agent can update memory based on interactions so preferences carry forward across threads.
- Relevance: Directly maps to the fellowship's memory-update focus — Deep Agents implements memory as plain files edited by the agent, with routing/persistence handled outside the agentic loop (no vector DB or embeddings required by default).

**Architecture summary for the review:**

| Pillar | Mechanism in Deep Agents |
|---|---|
| Planning | `write_todos` no-op to-do tool (opt-in `TodoListMiddleware` v0.7+); status tracking pending/in_progress/completed, persisted in state |
| Sub-agents | Built-in `task` tool spawns ephemeral, stateless sub-agents with isolated context; single final-report handoff ("context quarantine") |
| Context offload | Virtual filesystem; large tool results written to files and summarized; automatic compression/summarization middleware |
| Memory / persistence | `StateBackend` (ephemeral) / `StoreBackend` (cross-session) / `CompositeBackend` (hybrid) + `AGENTS.md` always-loaded memory |
| System prompt | Detailed base prompt inspired by Claude Code; user instructions injected as custom section |

### 2. Other well-documented "deep agent" / long-horizon frameworks worth comparing

**(D) Anthropic — "How we built our multi-agent research system"** (INDUSTRY ENGINEERING BLOG)

- Org: Anthropic. Published June 2025 (Research feature launched April 2025).
- Core contribution: Orchestrator-worker pattern — a LeadResearcher plans, spawns subagents in parallel, then a CitationAgent attributes sources. Per Anthropic's post, "the lead agent spins up 3-5 subagents in parallel rather than serially; (2) the subagents use 3+ tools in parallel. These changes cut research time by up to 90% for complex queries." On performance and cost, "a multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval," while multi-agent systems "use about 15× more tokens than chats." The lead agent persists its plan to memory when context approaches the model's token limit. Anthropic is explicit that multi-agent systems suit breadth-first, parallelizable tasks but not tightly interdependent work (e.g., most coding).
- Relevance: The canonical sub-agent orchestration reference; the "save the plan to memory to survive context overflow" pattern is directly transferable to long legal-research tasks.

**(E) Anthropic/Claude — "When to use multi-agent systems (and when not to)"** (INDUSTRY BLOG)

- Org: Anthropic (claude.com/blog). Core contribution: Guidance on orchestrator-subagent contracts (objective, output format, tool guidance, boundaries), verification subagents, and effort-scaling rules. Relevance: practical governance guidance for delegating legal subtasks safely.

**(F) Manus — "Context Engineering for AI Agents: Lessons from Building Manus"** (INDUSTRY BLOG)

- Author: Yichao 'Peak' Ji (Manus). Date: July 18, 2025. URL: manus.im/blog. Core contribution: In the author's words, "we treat the file system as the ultimate context in Manus: unlimited in size, persistent by nature, and directly operable by the agent itself… Our compression strategies are always designed to be restorable" (e.g., drop web-page content but keep the URL; drop a document but keep its path). Manus notes a typical task "requires around 50 tool calls on average," and uses a recited todo.md to fight "lost-in-the-middle."
- Relevance: The intellectual source for Deep Agents' file-system pillar; directly relevant to designing signal-driven, reversible memory updates.

**(G) Claude Agent SDK (Anthropic) & OpenAI Agents SDK** (INDUSTRY SDKs)

- LangChain's own docs provide a side-by-side "Deep Agents vs. Claude Agent SDK" comparison: the key differentiator is model/infrastructure flexibility (Deep Agents is model-agnostic; Claude Agent SDK is Claude-native). The OpenAI Agents SDK is noted as lighter on long-horizon planning/filesystem context management. Relevance: situates Deep Agents among production harnesses.

### 3. Academic papers (2024–2026) on long-horizon/deep-agent architectures NOT already in the fellowship list

**(H) DeepAgent: A General Reasoning Agent with Scalable Toolsets** (PEER-REVIEWED — WWW 2026 Oral)

- Authors: Xiaoxi Li, Wenxiang Jiao, Jiarui Jin, Guanting Dong, Jiajie Jin, Yinuo Wang, Hao Wang, Yutao Zhu, Ji-Rong Wen, Yuan Lu, Zhicheng Dou (Renmin University of China, RUC-NLPIR). arXiv:2510.21618; accepted as Oral at The Web Conference (WWW) 2026 (April 13–17, 2026, Dubai).
- Core contribution: An end-to-end deep reasoning agent that unifies thinking, dynamic tool discovery, and action in one reasoning stream. Introduces an autonomous memory folding mechanism that compresses history into brain-inspired episodic, working, and tool memories, plus a reinforcement-learning strategy (ToolPO) for tool use.
- Important disambiguation: This is a DIFFERENT artifact from LangChain's deepagents library — same name, unrelated. The memory-folding mechanism is directly relevant to signal-driven memory consolidation for legal agents.

**(I) Always-On Agents: A Survey of Persistent Memory, State, and Governance in LLM Agents** (ACADEMIC PREPRINT)

- Authors: Tianyu Ding, Aditya Nannapaneni, Bingfan Liu, Ling Zhang. arXiv:2606.30306, submitted June 29, 2026.
- Core contribution: Surveys a 435-work corpus through six diagnostic axes (authority, scope, mutability, provenance, recoverability, actionability) and a state lifecycle (written, validated, organized, retrieved, acted upon, updated, forgotten, audited, rolled back). Finds the literature over-focuses on accumulating/retrieving state vs. governing/recovering it; proposes the Always-On Evaluation Protocol (AOEP-v0).
- Relevance: Excellent framing for a controlled, signal-driven memory-update mechanism — its governance axes (mutability, provenance, recoverability) map directly onto compliance needs in legal/financial workflows.

**(J) A Survey on Long-Term Memory Security in LLM Agents: Attacks, Defenses, and Governance Across the Memory Lifecycle** (ACADEMIC PREPRINT)

- Lead author: Zehao Lin et al. (8 authors). arXiv:2604.16548.
- Core contribution: A Memory Lifecycle Framework (six phases: Write, Store, Retrieve, Execute, Share/Propagate, Forget/Rollback × four objectives: Integrity, Confidentiality, Availability, Governance) and Verifiable Memory Governance (VMG) primitives. Relevance: memory-poisoning and governance risk is a first-order concern for a bank's legal AI; this frames controls on memory writes.

**(K) Rethinking Memory Mechanisms of Foundation Agents in the Second Half: A Survey** (ACADEMIC PREPRINT)

- Large multi-author consortium (lead Wei-Chieh Huang et al.). arXiv:2602.06052 (v1 Jan 14, 2026). Core contribution: Surveys self-evolving/long-horizon agent memory beyond the 2024 Zhang survey. Relevance: updates the fellowship's existing Zhang (2024/2025) survey with 2025–2026 developments.

**(L) Supporting taxonomy sources** (ACADEMIC): "A Taxonomy of Architecture Options for Foundation Model-based Agents" (arXiv:2408.02920); "The Landscape of Emerging AI Agent Architectures for Reasoning, Planning, and Tool Calling: A Survey" (arXiv:2404.11584). These provide the reasoning/planning/memory/reflection component vocabulary that situates "deep agents" against ReAct.

Note on the fellowship's existing anchor: the subagent confirmed Zeyu Zhang et al., "A Survey on the Memory Mechanism of Large Language Model-based Agents" (arXiv:2404.13501) was accepted to ACM Transactions on Information Systems (TOIS), 2025, Vol. 43, Issue 6, pp. 1–47, DOI 10.1145/3748302 — the peer-reviewed venue is verified.

### 4. Direct three-way comparison: does it exist?

No. No academic paper or authoritative industry write-up compares Hermes Agent, smolagents, and LangChain Deep Agents together. The closest sources:

- **(M) Workspace-Bench 1.0: Benchmarking AI Agents on Workspace Tasks with Large-Scale File Dependencies** (ACADEMIC PREPRINT — closest comparison). arXiv:2605.03596. Benchmarks three harnesses — OpenClaw, LangChain Deep Agents, and Hermes — across 5 foundation models. Characterizes Deep Agents as a "highly controllable, white-box harness … built on LangGraph … enforcing built-in planning tools (write_todos) … fully transparent and traceable execution" and Hermes as a "built-in learning loop … four-layer decoupled memory engine." Omits smolagents. No confirmed peer-reviewed venue yet.
- Pairwise industry comparisons abound (e.g., "Deep Agents vs Claude Agent SDK," "Hermes vs OpenClaw") but are mostly vendor/SEO content and never include smolagents.

Conclusion for the review: The specific three-way comparison — closed native learning loop (Hermes) vs. transparent programmatic step-memory (smolagents) vs. planning/sub-agent/filesystem harness (Deep Agents) — does not appear in the literature and is a defensible original contribution of the fellowship's Sub-activity 1.1. *(Elaborated further in [`../discussion/framework-comparison-hermes-smolagents-deepagents.md`](../discussion/framework-comparison-hermes-smolagents-deepagents.md).)*

**Framework contrast table (from primary sources):**

| Dimension | Hermes Agent (Nous Research) | smolagents (Hugging Face) | LangChain Deep Agents |
|---|---|---|---|
| Design philosophy | Closed native learning loop; "the agent that grows with you" | Transparent, minimal, code-first step memory | Opinionated harness: plan + delegate + offload |
| Memory | Multi-layer: prompt memory (MEMORY.md/USER.md) + episodic SQLite FTS5 archive + skill memory; pluggable providers | `agent.memory.steps` list of ActionStep/PlanningStep logs; programmatically editable | StateBackend/StoreBackend/CompositeBackend + AGENTS.md |
| Learning | Autonomous session-to-skill conversion; self-improving skills | None native; developer controls everything | Skills + memory updated from usage; not a closed loop by default |
| Persistence | Persistent across sessions by default | In-run; persistence is developer-implemented | Opt-in cross-session via StoreBackend |
| Control surface | Curated/automatic | Fully explicit/white-box | Configurable middleware stack |
| Planning | Skills-driven | Optional PlanningStep at intervals | `write_todos` no-op planning tool |

## Recommendations

- Add LangChain Deep Agents to the bibliography as a first-class framework entry, citing three primary sources: the July 30, 2025 blog post (definitional), the deepagents GitHub repo (implementation), and the docs overview + context-engineering pages (architecture and memory). Flag all three as industry sources (blog/docs/repo), not peer-reviewed.
- Position Deep Agents explicitly as the third pole of a design-philosophy triangle: Hermes = closed native learning loop with layered memory + session-to-skill conversion; smolagents = transparent programmatic step-memory; Deep Agents = planning/sub-agent/filesystem harness with opt-in cross-session persistence. Use the contrast table above.
- Explicitly disambiguate the two "DeepAgent(s)" in the text: LangChain's deepagents library (industry harness) vs. RUC-NLPIR's "DeepAgent" (arXiv:2510.21618, WWW 2026, peer-reviewed reasoning model with memory folding). Cite both but never conflate.
- Add the newly identified academic anchors most relevant to controlled memory updates: Always-On Agents survey (arXiv:2606.30306) for governance axes; the long-term memory security survey (arXiv:2604.16548) for write-control/poisoning risk; and the "Second Half" memory survey (arXiv:2602.06052) to refresh the 2024 Zhang survey.
- Claim the three-way comparison gap. State that no source compares Hermes/smolagents/Deep Agents together (nearest is Workspace-Bench, arXiv:2605.03596, which covers Hermes + Deep Agents + OpenClaw but not smolagents), and that the fellowship's comparative framing is therefore novel. Threshold to revise this claim: if a survey or benchmark explicitly evaluating all three emerges, downgrade the novelty claim to "extends existing comparisons."
- For the legal-workflow memory mechanism design, prefer Deep Agents' CompositeBackend routing model (explicit, file-based, auditable, no mandatory embeddings) as an architectural reference, because it makes memory writes inspectable and permission-controllable — critical for financial-sector compliance. Pair with the governance axes from the Always-On Agents survey to define what to persist, mutate, and roll back.

## Caveats

- Source-type honesty: Deep Agents, Hermes, smolagents, and Anthropic's and Manus's write-ups are industry (blogs, docs, repos), not peer-reviewed. Only the arXiv/conference papers (DeepAgent WWW 2026; the surveys) are academic; several are recent preprints without confirmed peer-reviewed venues.
- Version volatility: Deep Agents is fast-moving (v0.7 made task planning opt-in; docs reference forthcoming model versions like "gpt-5.5"/"gemini-3.6-flash"). Cite version numbers and access dates.
- "No-op" planning nuance: The to-do tool does not execute logic; its benefit is purely context-engineering. Do not overstate it as a planner/executor.
- Persistence is not default: Deep Agents does NOT persist memory across sessions unless a StoreBackend/CompositeBackend is configured; the default StateBackend is ephemeral. Contrast with Hermes, which persists by default.
- Popularity/quantitative metrics (GitHub star counts, Hermes launch dates, Terminal-Bench scores) come from secondary/industry sources and should be independently reconfirmed before formal citation.
- The term "deep agents" itself is industry-coined, largely by LangChain/Harrison Chase; the academic literature prefers "long-horizon agents." Present it as an industry-originated category, not an established academic taxonomy term.
- Recent-preprint dating: arXiv IDs in the 2602–2607 range are 2026 preprints consistent with the current date; verify author lists/versions with a direct arXiv fetch before formal citation.
