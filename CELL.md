# Matt Persona Organ — Biology and Design

**The third reusable persona-organ cell for the DataFlow Advisory virtual team.**

A persona-organ is a pure, stdlib-only module for autonomous decision-making in a specific domain. It encapsulates:

- **Identity**: role, expertise, communication style, values
- **Genome**: multiple prompt variants (v1 general, v2+ directed mutations)
- **Ribosome**: model selection and inference parameters
- **Interface**: three pure functions—`compose()`, `interpret()`, `decide()`

---

## Biology Metaphor

The organ is the reusable logic for a persona. Think of it as:

- **Genome**: The DNA. Multiple variants (v1, v2, ...) encode different "strategies" for the same role.
- **Ribosome**: The machinery. Model selection, temperature, timeout—how the inference runs.
- **Organ**: The living module. Reads state, applies domain expertise, produces structured decisions.
- **Cell**: The repository. A full persona-organ cell includes tests, samples, docs, and identity metadata.

---

## Identity: Matt, CTO

```json
{
  "role": "Chief Technology Officer",
  "expertise": [
    "systems architecture",
    "infrastructure design",
    "technical risk assessment",
    "scalability engineering",
    "database architecture",
    "API design",
    "cloud infrastructure",
    "performance optimization",
    "technical debt management"
  ],
  "communication_style": "precise, technically rigorous, focused on trade-offs and long-term resilience; ruthless about technical risk"
}
```

Matt's domain is **technical architecture and infrastructure scalability**. He lives in system design, evaluates trade-offs quantitatively, and owns technical risk.

---

## Genome: Two Prompt Variants

### v1_general_session

A faithful, general-purpose system prompt for Matt. Works across all architecture activities (design reviews, optimization, scaling, risk assessment). Emphasizes:

- Architecture clarity ("Architecture decisions are explicit and defensible")
- Trade-off rigor ("focused on trade-offs and long-term resilience")
- Evidence-based thinking (quantified analysis)
- Autonomous work with guidance ("Stay in your lane")
- Technical communication via the `draft_email` tool

**When to use v1:**
- General architecture analysis
- First contact with a directive
- Conversational technical recommendations
- Rapid assessment needed

### v2_architecture_deep_dive

A directed mutation that adds **ARCHITECTURE DEEP-DIVE FRAMEWORK** — rigorous system analysis. Structures every architecture decision around:

- Current State (what exists and how it works?)
- Load Profile (throughput, latency, data volume, growth trajectory)
- Failure Modes (what can go wrong? Cascade risks?)
- Scaling Path (how does this scale with 10x, 100x?)
- Operational Cost (TCO, hosting costs, on-call burden)
- Technical Debt (what's baked into the system we'll regret?)
- Alternative Approaches (competing architectures and trade-offs)
- Recommendation (clear architecture decision with rationale)

Emphasizes quantified analysis, explicit alternatives, and rigorous trade-off evaluation.

**When to use v2:**
- Deep architecture reviews
- System redesign or major refactoring
- Critical infrastructure decisions
- Need quantified trade-off analysis
- Risk assessment for large changes

---

## The Organ Interface

Three pure functions. No side effects. Deterministic.

### 1. compose(state, context) → {prompt, model}

**Assemble the system prompt and select the model.**

```python
config = organ.compose(
    state={
        "variant": "v1",  # or "v2"
        "knowledge_text": "...",          # accumulated system context
        "directive": "...",               # the board's instruction
        "capabilities_summary": "...",    # what Matt can do
    },
    context={
        "platform_identity": "...",       # system brand/identity
    }
)
# Returns: {
#   "prompt": "You are Matt, the CTO...",
#   "model": "anthropic/claude-sonnet-4.6"
# }
```

**Load order:**
1. Read `genome/v1_general_session.txt` or `genome/v2_architecture_deep_dive.txt`
2. Substitute placeholders: `{knowledge_text}`, `{directive}`, `{capabilities_summary}`, `{platform_identity}`
3. Load model from `ribosome.json` (fallback: `anthropic/claude-sonnet-4.6`)

### 2. interpret(state, context, response) → {output, rationale, self_metric}

**Extract structured signals from the LLM response.**

```python
result = organ.interpret(state, context, llm_response)
# Returns: {
#   "output": "Full response text",
#   "rationale": "High confidence with clear architecture analysis and evidence",
#   "self_metric": 8  # [0, 10] confidence scale
# }
```

**self_metric computation:**
- Base score: 3 (low, let evidence build it up)
- Reward for length: +1 to +3 (more thinking)
- Reward for structure: +1 to +2 (paragraphs, lists)
- Reward for architecture terms: +1 to +2 (scalability, latency, throughput, consistency, availability, trade-off, database, API)
- Reward for technical depth: +1 to +2 (Postgres, Redis, Kubernetes, AWS, Docker, SQL, event, consensus)
- Reward for confidence words: +1 per instance (clearly, should, recommend, proven)
- Penalty for uncertainty words: -1 per instance (might, unclear, possibly, risky)
- Final: clamp to [0, 10]

**High-confidence indicators:**
- Quantified metrics (throughput, latency, cost)
- Scaling analysis (how this grows 10x, 100x)
- Failure mode discussion
- Multiple alternatives evaluated
- Explicit trade-offs and trade-off rationale
- Operational considerations (monitoring, on-call, runbooks)

### 3. decide(state, context) → {output, rationale, self_metric}

**Make lightweight decisions without calling an LLM.**

Used by `select_organ.select_best_variant()` to compare variant outputs and choose the higher-confidence one.

```python
comparison = organ.decide(
    state={
        "option_a": {"output": "...", "self_metric": 7},
        "option_b": {"output": "...", "self_metric": 5},
    },
    context={}
)
# Returns: {
#   "output": "Selected option_a (delta=2.0)",
#   "rationale": "Compared self_metric: option_a=7, option_b=5. Chose option_a.",
#   "self_metric": 10  # confidence in the choice
# }
```

---

## Inference Configuration (ribosome.json)

```json
{
  "model": "anthropic/claude-sonnet-4.6",
  "parameters": {
    "max_tokens": 1500,
    "temperature": 0.7,
    "top_p": 0.9,
    "timeout_seconds": 45
  },
  "fallback_model": "anthropic/claude-3.5-haiku",
  "fallback_parameters": {
    "max_tokens": 1000,
    "temperature": 0.5,
    "timeout_seconds": 30
  }
}
```

**Tuning notes:**
- **temperature 0.7**: Balanced between structured reasoning (lower T) and creative alternatives (higher T). For architecture, we want rigorous analysis but multiple options.
- **max_tokens 1500**: Standard for persona work. May need to raise for complex system designs.
- **timeout 45s**: Architecture decisions require time to reason. Fallback Haiku at 30s for quicker assessments.

---

## Variant Selection: A/B Testing Personas

Use `select_organ.select_best_variant()` to compare v1 and v2 on the same task:

```python
# Run inference with v1
result_v1 = organ.interpret(state_v1, context, response_from_v1)

# Run inference with v2
result_v2 = organ.interpret(state_v2, context, response_from_v2)

# Compare
comparison = select_organ.select_best_variant(result_v1, result_v2)
# {
#   "selected": "b",
#   "delta": 3.5,
#   "best": result_v2,
#   "rationale": "Variant B selected: metric_a=6, metric_b=9.5, delta=3.5"
# }
```

**Delta interpretation:**
- `delta < 1`: Variants are equivalent; choose by context (v1 = faster, v2 = rigorous)
- `1 ≤ delta < 3`: Weak preference for selected variant
- `delta ≥ 3`: Strong preference; selected variant is significantly better

---

## Design: Pure and Composable

The organ is **pure**:
- No I/O (except file reads for templates)
- No network calls
- No database access
- Deterministic (same input = same output)
- No global state

This makes it:
- **Testable**: Mock the LLM response, assert the metric
- **Composable**: Stack multiple organs, ensemble their outputs
- **Versionable**: Swap organs in the execution harness without redeploying
- **Portable**: Run on local dev, cloud runner, or integration tests

---

## Known Patterns

### Architecture Review Session

1. **Compose v2** (architecture_deep_dive variant)
2. **Feed state** with current system context
3. **Run inference** on the assembled prompt
4. **Interpret** the response → get quantified architecture analysis
5. **Check self_metric** → if < 6, re-run with v1 or ask for clarification

### Scaling Analysis

1. Run both v1 and v2 on the same scaling challenge
2. **Compare metrics** via select_organ
3. If v2 wins (delta > 2), use v2's rigorous analysis
4. If v1 wins or tie, use conversational approach but ask for quantified verification

### Ensemble Across Directives

Multiple Matt work items can land simultaneously. Use `select_organ.compute_ensemble()` to combine their outputs:

```python
responses = [
    organ.interpret(..., response_from_item_1),
    organ.interpret(..., response_from_item_2),
    organ.interpret(..., response_from_item_3),
]

ensemble = select_organ.compute_ensemble(responses)
# {
#   "ensemble_output": "...",  # best response
#   "ensemble_metric": 7.3,    # average confidence
#   "explanation": "Ensemble of 3 responses..."
# }
```

---

## Testing

Run the test suite:

```bash
python -m pytest test_organ.py -v
```

**Test categories:**
- **Compose**: Template loading, placeholder substitution, model selection, fallbacks
- **Interpret**: Metric range [0, 10], architecture term rewards, confidence language, technical depth detection
- **Decide**: Option selection, metric comparison, tie-breaking
- **Integration**: Full cycle (compose → simulate response → interpret)

---

## Files

```
persona-matt/
├── identity.json                    # Matt's metadata
├── ribosome.json                    # Inference config
├── organ.py                         # Core logic
├── select_organ.py                  # Variant selection
├── genome/
│   ├── v1_general_session.txt       # General-purpose prompt
│   └── v2_architecture_deep_dive.txt # Rigorous architecture analysis
├── test_organ.py                    # Unit tests
├── samples/
│   ├── basic_review.py              # Simple usage example
│   └── ab_test_variants.py          # Variant comparison
├── CELL.md                          # This file
├── README.md                        # Quick start
└── .gitignore
```

---

## Extending Matt

### Adding a v3 Variant

Create `genome/v3_operational_focus.txt` with a different mutation:
- Focus on operational concerns (monitoring, alerting, on-call)
- Optimize for operational resilience
- Emphasis on runbooks, incident response, observability

Then update `organ.compose()`:

```python
elif variant == "v3":
    template_path = "genome/v3_operational_focus.txt"
```

### Tuning self_metric for a New Variant

If v3 emphasizes operational concerns, adjust `_compute_self_metric()` to reward:
- Operational language (monitoring, alerting, incident, runbook)
- Reliability markers (MTTF, MTTR, availability SLO)
- Observability terms (logging, tracing, metrics, dashboards)

### Evolving the Ribosome

If Matt's work requires more depth (longer responses, higher reasoning), raise:

```json
{
  "max_tokens": 2000,     // up from 1500
  "temperature": 0.8,     // slightly more creative for alternatives
  "timeout_seconds": 60   // more time to reason
}
```

---

## Evolution Notes

This is the third persona-organ cell. The first (Dev) and second (Tim) demonstrate the pattern. Matt's cell adds:

1. **Technical domain specialization**: Architecture terminology in self_metric, not code-review or sales language
2. **Variant divergence**: v1 general vs v2 deep-dive (analysis depth, not just quality mutation)
3. **Identity cohesion**: Values (resilience, clarity, pragmatism, depth) reflected in genome and scoring

Future cells (Product, Engineering, Compliance) will follow the same pattern.

---

## Philosophy

The persona-organ model inverts the traditional approach:

**Traditional:** One system prompt, tuned for every possible task.

**Organ:** Multiple genomes for one role, swapped by task context. Pure logic that's testable, versionable, and composable.

This enables:
- **A/B testing** at the prompt level (not just response evaluation)
- **Role specialization** without role explosion
- **Auditable decisions** (every metric has a source)
- **Persona evolution** (v1 → v2 → v3 without breaking the harness)

---

## Related Work

- **persona-tim**: The second organ cell (sales pipeline and deal management)
- **persona-dev**: The first organ cell (code review and architecture)
- **autonomous_session.py**: The harness that executes persona work
- **select_organ.py**: Variant comparison and ensemble logic
- **memory promotion**: How persona outputs become accumulated knowledge

---

## Questions?

See the sample scripts:
- `samples/basic_review.py` — Simple usage
- `samples/ab_test_variants.py` — Variant comparison

Run tests:
- `python -m pytest test_organ.py -v`
