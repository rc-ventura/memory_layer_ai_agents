<!-- Fragmento verbatim de ../knowledge-as-infra-architecture-hypothesis.md — versão canônica (mantém todos os links de entrada do repo). Índice: ./README.md — editar a canônica, não este fragmento. -->

### B. Signal capture — dual path, already mapped to the platform

Copilot/chat mode (human present, direct thumbs up/down) and systemic/event-driven mode (no human turn — [API-INTERNA] API response via Kafka, ex-post annotation derived from case outcome). Both write into the same signal ledger; the Update Engine doesn't need to know which path a signal came from. Casper et al.'s findings apply to both: don't trust a single signal at face value, log disagreement, watch for correlated (not just insufficient-volume) annotator error, anchor to case outcome rather than reviewer satisfaction.

### Signal Capture — status snapshot (added 26/08/2026)

Closed out working through it in conversation, same format as component A's snapshot above.

**Settled:**
- Two capture paths, both writing into the same **Signal Ledger** — a data store separate from the Memory Store (component A); the Update Engine doesn't need to know which path a signal came from.
- Copilot path: a human evaluates the agent's result directly, thumbs up/down, during the interaction.
- Systemic path: no human turn — ex-post annotation derived from case outcome, transported via the [API-INTERNA] API's Kafka response topic (confirmed real infra, the same mechanism already validated for component A's write trigger).
- **Neither path is exposed as an MCP tool — same reasoning already established for the episodic ADD (component A).** MCP is reserved for actions the *agent* decides to invoke inside its own reasoning trace. Neither a human's thumbs click nor a system Kafka event is an agent decision, so both sit outside the MCP surface by design, not by gap — the same category of "trigger external to the agent's loop" as the episodic write, just triggered by a human UI action or a system event instead of a pipeline-stage completion.
- The Signal Ledger and the Memory Store only connect indirectly: the Update Engine reads from the Ledger, and — only after Commit Gate approval — writes into the Memory Store's **strategy layer**. Signal Ledger content never becomes part of the episodic traces.

**Still open:**
- **Exact schema/structure of the Signal Ledger** — not defined, same class of gap as component A's storage mechanics (see the write-path status snapshot above).
- **Transport mechanism for the copilot path is not documented.** The systemic path's transport ([API-INTERNA]/Kafka) is confirmed real infra; the copilot path's transport — plausibly a direct API call from the chat UI, since a synchronous human click doesn't need an async event bus — is inference, not a decision recorded anywhere.
- **What exactly gets captured in systemic mode, beyond "the outcome,"** is still open (see [`open-questions.md`](../open-questions.md)).
- **No rater redundancy.** Only one signal per case is captured on either path — no mechanism exists for deliberately getting a second, independent opinion on a sample of cases, which the Commit Gate's "agreement rate" check needs in order to be computable at all (already flagged under the Commit Gate's own open gaps, component D).

### Signal Capture — additions from the 28/08/2026 tutor checkpoint

Three inputs from the tutor (reflections [`checkpoint-2026-08-28-reflections.md#2`](../checkpoint-2026-08-28-reflections.md), [`#3`](../checkpoint-2026-08-28-reflections.md)), all still open, none designed:

- **Thumbs is asymmetric, and it composes rather than triggers.** The tutor independently reached "thumbs is one signal to compose, not a trigger" (second convergence, after 20/08's batch-review one) and added a prior: thumbs-*up* is near-worthless (*"muito mais comum sempre darem up"*), thumbs-*down* is strong (*"pra dar down, deu ruim mesmo"*). Consistent with Casper's sycophancy finding. Carry as a fixed assumption for this component, separate from the v2 adaptive path-weighting.
- **Outcome-signal latency is agent-type-dependent — the single systemic path is too coarse.** Cadastro: a usable signal in ~1–2 months, and it is a **third systemic signal type** the doc doesn't name — *downstream human correction / reclassification*, detectable as a diff on the record (not thumbs, not a Kafka case-outcome). Contestação: case-outcome median ~13 months, so the online outcome signal is near-useless for it on the fellowship horizon; its near-term primary signal has to be the deterministic trace-shape one (component C's first filter), not outcome. Component B needs a **per-agent-type signal-latency model**.
- **Prefer querying the existing trace store over a dedicated Signal Ledger.** The tutor's cadence is *"puxa do banco os traces de um período"* and *actively pulling* "cases that now have an outcome I haven't used yet" — plus a **trace ID + a consumed-list** so one case can't drive multiple updates. Folds into the "reuse vs. build the Signal Ledger" open question, hard toward reuse.
