# `memory-sdk` — reference copy of the documentation

A transcription of the internal documentation site of a company's long-term memory engine SDK for conversational agents in a banking context. Company, product, gateway and internal-URL names were replaced with neutral placeholders (`memory-sdk`, `memory_sdk`, `MEMSDK_*`, "gateway GenAI", `GENAI_*`). It is kept here as reference material for the POC design work (see [`../blueprint-m1-pocs-minimos.md`](../blueprint-m1-pocs-minimos.md)).

- **Source:** photos of the documentation site taken on 2026-11-11 (site version as of that date). The photos themselves are not in the repo.
- **Fidelity:** the chapters keep the original Portuguese verbatim, including code, YAML and tables. Diagrams were redrawn as Mermaid, and dashboard screenshots are described in text. Wherever the photo cut something off or a page was not photographed, a `> **Nota de transcrição:**` block says so. Internal links point to the chapters below.
- **Not an analysis:** nothing here compares the SDK with this project's architecture. That comparison lives in [`../../discussion/hipoteses/internal-memory-sdk-vs-mechanism.md`](../../discussion/hipoteses/internal-memory-sdk-vs-mechanism.md).

## Chapters

The order follows the site's own "Anterior / Próxima" navigation.

### Documentação — how to use the SDK

| # | Chapter | What it covers |
|---|---|---|
| 01 | [Quickstart](01-quickstart.md) | Installation, GenAI gateway credentials, first example (`store_memories` → `get_relevant_memories`), the `memory-dashboard` |
| 02 | [Operações de memória](02-operacoes.md) | The seven `MemoryClient` operations, their return values, operational notes, an end-to-end example |
| 03 | [Configuração](03-configuracao.md) | Precedence, the `.memory/` folder, `config.yaml` (`persistence`, `providers`, `importance`), `prompts.yaml` overlays, `MEMSDK_*` env vars, programmatic `Config` |
| 04 | [Persistência](04-persistencia.md) | ChromaDB (one collection per `user_id`), where the data lives, other backends (pgvector not yet available) |

### Conceitos — how the engine works inside

| # | Chapter | What it covers |
|---|---|---|
| 05 | [Conceitos](05-conceitos.md) | Section entry page: overview of the 7-stage pipeline |
| 06 | [Categorias de memória](06-categorias.md) | `fixed_profile`, `dynamic_profile`, `preferences`, `events`, `experiences`; INSERT vs UPDATE per category; blocked sensitive topics |
| 07 | [Scoring de importância](07-scoring.md) | `W_global = B × F × Q × U × C × R`, defaults per category, the 8 verifier dimensions behind Q, per-category retrieval, retrieval reinforcement |
| 08 | [Histórico vinculado e duplicatas](08-historico-duplicatas.md) | Linked history (`previous_memory_id`, `is_current`), how the current node is found, duplicate detection (`SequenceMatcher` > 0.85), conflicts |
| 09 | [Pipeline do motor](09-pipeline.md) | Stages 0–6 one by one (multimodal, retrieve, temporal guard, judge, verifier, conflict checker, writes, responder) and parallelism |
| 10 | [Ações do judge](10-acoes-judge.md) | The judge's JSON, `insert` / `update` / `respond_only`, validation and normalization, multiple actions per turn |
| 11 | [Guarda temporal](11-guarda-temporal.md) | Deterministic tense-versus-year check, short-circuit and clarification, `_pending_temporal`, known limits |
| 12 | [Pré-processamento multimodal](12-multimodal.md) | Attachment format, audio and image prompts, `enriched_text`, graceful failure, default provider |

## Quick lookup

| Looking for… | Go to |
|---|---|
| Public API (`MemoryClient` methods) | [02 · Sumário das operações](02-operacoes.md#sumário-das-operações) |
| Memory record fields (`subject_key`, `is_current`, `previous_memory_id`, `mention_count`, `conflict_count`, `user_confirmed`, `last_mentioned_at`) | [08](08-historico-duplicatas.md), [07](07-scoring.md) |
| The six LLM/embedding roles and their stage | [03 · providers](03-configuracao.md#providers) |
| Ranking formula and default parameters | [07 · A fórmula](07-scoring.md#a-fórmula) |
| Judge output schema | [10 · O JSON emitido](10-acoes-judge.md#o-json-emitido) |
| Conflict checker output schema | [09 · Conflict checker](09-pipeline.md#4-conflict-checker-paralelo-a-3) |
| Deterministic (non-LLM) parts of the engine | [11 · Guarda temporal](11-guarda-temporal.md), [10 · Validação e normalização](10-acoes-judge.md#validação-e-normalização), [08 · Detecção de duplicatas](08-historico-duplicatas.md#detecção-de-duplicatas) |
| Numeric thresholds (0.85 duplicate, 0.25 minimum similarity, 0.60 reinforcement distance, 600 s cooldown, top-5 fallback) | [08](08-historico-duplicatas.md), [07](07-scoring.md#reforço-de-recuperação) |

## Known gaps in the transcription

- **Not photographed:** the "Defaults completos" page (`memory_sdk/config/defaults/prompts.yaml`) that chapter 03 cites, and the site's "ajuda" section.
- **Cut off in the photos:** the tail of the first line of the printed example output (chapter 01); the middle of the second dashboard screenshot (chapter 01). The Conceitos topic cards (chapter 05) are only partly visible, so the topic list there was rebuilt from the page navigation.
- **Inferred:** chapter 08's URL path is not visible in its photo.
