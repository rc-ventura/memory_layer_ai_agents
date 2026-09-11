<!-- Fragmento verbatim de ../knowledge-as-infra-architecture-hypothesis.md — versão canônica (mantém todos os links de entrada do repo). Índice: ./README.md — editar a canônica, não este fragmento. -->

## Static vs. adaptive memory — where each component could become adaptive, and where it shouldn't (added 27/08/2026)

SSGM frames a distinction between **static memory systems** (Generative Agents, MemoryBank — content changes but operations are fixed rules) and **adaptive memory systems** (MemGPT, Memory-R1 — the operations themselves are learned policies). This architecture is **static by design** — all operations are fixed, auditable, deterministic rules. See the analysis in [`../papers/ssgm-2026.md`](../../papers/ssgm-2026.md) (the "Static vs. adaptive memory" section) for why static is the right choice for this domain (auditability, predictability, legal compliance). This section maps where each component *could* become adaptive in a v2, and where it explicitly should not.

**Governing principle: adaptive can calibrate parameters, never change rules.** Where the mechanism decides "how much" (thresholds, weights, decay rates), adaptive can learn. Where the mechanism decides "whether" (delete or not, validate or not, capture or not), it must remain fixed and governed.

### Per-component adaptive map (v2 direction, not v1)

**A. Memory Store (Memory Layer):**
- **Adaptive OK — score `S` weights (w1, w2, w3, w4):** the DMF-lite weights could auto-adjust based on which features correlate with flagged errors. Regression online: if `is_grande_causa` cases tend to be flagged more, w1 rises. Calibration, not rule change.
- **Adaptive OK — SAGE gate `θ1`/`θ2`:** auto-calibrate based on LTM hit rate. If LTM is empty (too few promoted), lower θ1; if LTM is noisy (too many trivial trajectories), raise θ1. The gate still exists — its threshold learns, its rule doesn't.
- **Adaptive OK — decay `κ` per memory class:** each class (prazo fact, jurisprudência, case exemplar) learns its own `κ`. Prazo facts decay faster than consolidated jurisprudência — `κ` captures that automatically. Needs volume per class for statistical significance.
- **Adaptive with caution — retrieval ranking weights (relevance vs. importance vs. freshness):** could adjust based on which retrievals the agent actually used. Risk: changing how the agent sees memory without it knowing is subtle and hard to audit. Lowest priority.

**B. Signal Capture:**
- **Adaptive OK — `outcome_type → severity` mapping:** the severity of each outcome type adjusts based on correlation with final case outcome. If "deadline missed" cases tend to have adverse final outcomes, severity of "deadline missed" rises. Learns from the signal the system already collects.
- **Adaptive OK — path weighting (copilot vs. systemic):** learns which path is more reliable per case type. If systemic signals are more predictive than copilot thumbs for trabalhista cases, weights diverge. Needs volume.
- **Adaptive NO — "what counts as a signal" threshold:** silently stopping capture of certain signal types could recreate the completeness gap the design avoids in the log. Never adaptive.

**C. Update Engine (Cognition Layer):**
- **Adaptive OK — trigger threshold:** auto-calibrates based on Commit Gate approval rate. If many triggers produce rejected proposals, threshold is too low; if real patterns are missed, too high. Already has the feedback signal (approval rate).
- **Adaptive OK — window size (how many recent cases to pull):** learns how many cases are needed to see a pattern. If quality insights come from 5 cases, no need for 100.
- **Adaptive with caution — reflection strategy:** learns which comparison axes (by error type, by pipeline stage, by case domain) produce more useful insights. This is where adaptive starts becoming a black box — "why did the Engine compare by error type instead of stage?" has no deterministic answer. Useful but needs explainability safeguards.
- **Adaptive NO — the fact that it produces a proposal (not a commit):** this is a rule, not a parameter. The Engine always proposes, the Gate always decides. Never adaptive.

**D. Commit Gate (Governance Layer) — minimal or zero adaptive:**
- **Adaptive with caution — NLI model:** fine-tune on legal-domain contradiction pairs. The model improves, but remains deterministic/auditable against a fixed benchmark. Only the model's accuracy improves, not the rule of "always check contradiction."
- **Adaptive NO — signal quality thresholds (agreement rate minimum, correlated-error threshold):** these are compliance/policy decisions, not optimization targets. "How many reviewers must agree" is a governance rule, not a parameter to tune.
- **Adaptive NO — which checks run:** silently dropping a check is exactly the drift the Gate exists to prevent.
- **Adaptive NO — human review requirement:** if this becomes adaptive, the Gate loses its purpose. The guard cannot learn to be more lenient.

**E. Forgetting:**
- **Adaptive OK — `κ` per class:** same as component A — each memory class learns its decay shape.
- **Adaptive OK — `θ2` (hard-delete candidate threshold):** auto-calibrates based on storage pressure + retrieval miss rate. But the actual deletion remains gated (human review) — only the *candidate generation* is adaptive, not the *decision*.
- **Adaptive OK — log retention policy:** learns how long each trace type needs to stay before archiving. Grande causa traces get longer retention than simple cadastro.
- **Adaptive NO — deleting without the gate:** the hard-delete decision must remain human-reviewed. Adaptive can surface candidates; humans approve deletion.

**F. MCP Integration:**
- **Adaptive OK — query rewriting:** before searching, rewrites the agent's query to be more effective. If "consignado contestado" returns few results, expands to "consignado + contestação + prescrição." Retrieval optimization, not policy change.
- **Adaptive OK — pre-fetching:** pre-loads memories the agent will likely need. If cadastro agent always recalls after step 3, pre-fetch at step 2.
- **Adaptive NO — the MCP interface/contract itself:** `recall_memory()` and `propose_memory_update()` are the integration contract. Changing them breaks agnosticism. Never adaptive.

### Summary: the adaptive/static boundary

```
ADAPTIVE OK (calibrate parameters, keep rules):
├── A: score S weights, SAGE θ1/θ2, decay κ per class
├── B: outcome_type → severity mapping, path weighting
├── C: trigger threshold, window size
├── E: decay κ per class, θ2 candidate threshold, log retention
└── F: query rewriting, pre-fetching

ADAPTIVE WITH CAUTION (improve model, keep rules):
├── D: NLI model fine-tune (accuracy up, rule fixed)
└── C: reflection strategy (black-box risk, needs explainability)

ADAPTIVE NO (would undermine the design):
├── D: validation rules, human review requirement, which checks run
├── B: stopping signal capture (completeness gap)
├── F: MCP interface/contract
├── E: deleting without gate
└── C: proposal-not-commit (the Engine always proposes, never commits)
```

This is a **v2 direction, explicitly out of scope for v1** — v1 is fully static (all parameters calibrated manually in Sub 1.6/1.7). The value of recording it now is to ensure the v1 design doesn't foreclose the v2 path: parameters should be externalized (config, not hardcoded) so they can be learned later without architectural change. See also the [v2 harness-change direction](05-component-c-update-engine.md#c-update-engine-cognition-layer--the-harness-adjustment-layer-batched) recorded in component C's header note.
