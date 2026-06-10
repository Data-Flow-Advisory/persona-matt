# Matt Persona Organ — CTO Architecture Cell

**The CTO persona-organ for DataFlow Advisory's virtual team.**

A reusable, testable, composable module for autonomous architecture decision-making. Matt owns system scalability, infrastructure, and technical risk. He lives in the details of distributed systems and makes hard trade-off calls on architecture.

---

## Quick Start

### Run Tests

```bash
python -m pytest test_organ.py -v
```

### Run Samples

```bash
python samples/basic_review.py
python samples/ab_test_variants.py
```

---

## Structure

```
persona-matt/
├── organ.py              # Core organ logic (compose, interpret, decide)
├── select_organ.py       # Variant selection and ensemble utilities
├── identity.json         # Matt persona metadata
├── ribosome.json         # Model and inference config
├── genome/               # Prompt variants
│   ├── v1_general_session.txt
│   └── v2_architecture_deep_dive.txt
├── test_organ.py         # Unit tests
├── samples/              # Usage examples
│   ├── basic_review.py
│   └── ab_test_variants.py
├── CELL.md               # Architecture and design
└── README.md             # This file
```

---

## The Organ Interface

Three pure functions define an organ's contract:

### 1. `compose(state, context) -> {prompt, model}`

Assemble the system prompt and select the model.

```python
import organ

config = organ.compose(
    state={
        "variant": "v1",  # or "v2"
        "knowledge_text": "Current system: 10k req/s, single database...",
        "directive": "Design for 100k req/s",
        "capabilities_summary": "Can analyze metrics, propose architecture...",
    },
    context={
        "platform_identity": "DataFlow Advisory...",
    }
)
# Returns: {"prompt": "You are Matt, the CTO...", "model": "anthropic/claude-sonnet-4.6"}
```

### 2. `interpret(state, context, response) -> {output, rationale, self_metric}`

Extract structured signals from the LLM response.

```python
result = organ.interpret(state, context, llm_response)
# Returns: {
#   "output": "Full response from Matt...",
#   "rationale": "High confidence with clear architecture analysis and evidence",
#   "self_metric": 8  # Confidence [0, 10]
# }
```

**self_metric measures response confidence:**
- 9-10: High confidence, clear architecture analysis, quantified trade-offs
- 7-8: Confident with technical depth and risk analysis
- 5-6: Moderate confidence, reasonable technical analysis
- 3-4: Limited confidence, lack of structure or technical substance
- 0-2: Low confidence, incomplete

### 3. `decide(state, context) -> {output, rationale, self_metric}`

Make lightweight decisions without calling an LLM. Used by variant selection.

```python
comparison = organ.decide(
    state={
        "option_a": {"self_metric": 7, ...},
        "option_b": {"self_metric": 5, ...},
    },
    context={}
)
# Returns: {"output": "Selected option_a...", "self_metric": 8}
```

---

## Two Prompt Variants

### v1_general_session

A general-purpose system prompt for Matt. Works across all architecture and infrastructure activities (design reviews, optimization, scaling, risk assessment).

**Use when:**
- General architecture analysis
- First contact with a directive
- Conversational technical recommendations
- Rapid assessment needed

**Example output:** Qualitative assessment of system challenges, recommendations ranked by impact and effort.

### v2_architecture_deep_dive

A directed mutation that adds structured **ARCHITECTURE DEEP-DIVE FRAMEWORK**. Every system analysis is rigorous and quantified:

- Current State (what exists and how it works?)
- Load Profile (throughput, latency, data volume, growth)
- Failure Modes (what can go wrong? cascades?)
- Scaling Path (how does this grow 10x, 100x?)
- Operational Cost (TCO, hosting, on-call, maintenance)
- Technical Debt (what's baked in we'll regret?)
- Alternative Approaches (competing architectures and trade-offs)
- Recommendation (clear decision with rationale)

**Use when:**
- Deep architecture reviews
- System redesign or major refactoring
- Critical infrastructure decisions
- Need quantified trade-off analysis
- Risk assessment for large changes

**Example output:** Comprehensive architecture analysis with alternatives evaluated, risks identified, and explicit trade-offs explained.

---

## How Variants Work

Run the same directive through both variants. Compare their confidence scores (self_metric). The variant with higher confidence is better for that task.

```python
import organ
import select_organ

# Compose and run both variants
result_v1 = organ.interpret(
    state={**state, "variant": "v1"},
    context=context,
    response=response_from_v1
)

result_v2 = organ.interpret(
    state={**state, "variant": "v2"},
    context=context,
    response=response_from_v2
)

# Compare and select the best
comparison = select_organ.select_best_variant(result_v1, result_v2)
# {
#   "selected": "b",  # v2 is better
#   "delta": 3.5,     # v2's advantage
#   "best": result_v2,
#   "rationale": "Variant B selected with 3.5-point advantage..."
# }
```

---

## Identity: Matt, CTO

**Role:** Chief Technology Officer

**Expertise:**
- Systems architecture
- Infrastructure design
- Technical risk assessment
- Scalability engineering
- Database architecture
- API design
- Cloud infrastructure
- Performance optimization
- Technical debt management

**Communication Style:** Precise, technically rigorous, focused on trade-offs and long-term resilience; ruthless about technical risk

**Core Values:**
- **Resilience**: Systems designed to survive failure, not just succeed
- **Clarity**: Architecture decisions are explicit and defensible
- **Pragmatism**: Perfect is the enemy of good. Ship with constraints understood.
- **Depth**: Understand the fundamentals, not just the surface

---

## Model Configuration (ribosome.json)

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

---

## Use Cases

### 1. Scalability Assessment

```python
state = {
    "variant": "v2",  # Use deep-dive variant
    "knowledge_text": "Current: 10k req/s, single DB, 150ms latency",
    "directive": "Design for 100k req/s",
    "capabilities_summary": "Can analyze metrics, design architecture",
}

composed = organ.compose(state, context)
# → Sends to Claude for inference
# → Returns quantified architecture analysis with alternatives
```

### 2. Infrastructure Review

```python
state = {
    "variant": "v2",  # Structure for deep analysis
    "knowledge_text": "Current deployment: single AZ, manual failover...",
    "directive": "Improve availability and resilience",
    "capabilities_summary": "Can review deployment, propose HA strategy",
}

composed = organ.compose(state, context)
# → Returns infrastructure assessment with HA options
```

### 3. Technical Risk Assessment

```python
state = {
    "variant": "v1",  # Conversational for nuance
    "knowledge_text": "Planning migration from monolith to microservices...",
    "directive": "What are the risks? How do we mitigate?",
    "capabilities_summary": "Can assess architecture risks, propose mitigation",
}

composed = organ.compose(state, context)
# → Returns risk analysis with mitigation strategies
```

---

## Testing

The test suite covers:

- **Compose**: Template loading, placeholder substitution, model fallback
- **Interpret**: Metric range, structured response rewards, architecture term detection, confidence language
- **Decide**: Option selection, delta calculation
- **Integration**: Full workflow (compose → interpret)

Run tests:

```bash
python -m pytest test_organ.py -v
```

All tests are pure (no LLM calls, no I/O).

---

## Design Philosophy

**The organ model inverts traditional prompt engineering:**

- **Traditional**: One system prompt tuned for every task
- **Organ**: Multiple genomes for one role, swapped by task context

This enables:
- **A/B testing** at the prompt level
- **Role specialization** without explosion
- **Testable decisions** (every metric has a source)
- **Persona evolution** (v1 → v2 → v3 without harness changes)

---

## Architecture

For detailed design notes, see **CELL.md**.

Key concepts:

- **Genome**: Multiple prompt variants (v1, v2, ...)
- **Ribosome**: Model selection and inference parameters
- **Organ**: The pure functions that compose and interpret
- **Cell**: This repository (organ + identity + genome + tests + docs)

---

## Extending Matt

### Add a v3 Variant

Create `genome/v3_operational_focus.txt` with a mutation focused on operational concerns (monitoring, alerting, on-call, runbooks). Then update `organ.compose()`:

```python
elif variant == "v3":
    template_path = "genome/v3_operational_focus.txt"
```

### Tune Inference Parameters

Edit `ribosome.json` to adjust:
- `max_tokens`: More thinking requires more tokens
- `temperature`: Higher T for creative options, lower T for structured reasoning
- `timeout_seconds`: Architecture decisions may need more time

### Evolve self_metric

Adjust `_compute_self_metric()` in `organ.py` to reward or penalize different characteristics depending on the variant's focus.

---

## Samples

### basic_review.py

Demonstrates the core interface without LLM calls:

```bash
python samples/basic_review.py
```

Shows:
- Composing a prompt (v1)
- Simulating a Matt response
- Interpreting confidence
- Comparing variants (v1 vs v2)

### ab_test_variants.py

A/B test both variants on the same architecture challenge:

```bash
python samples/ab_test_variants.py
```

Shows:
- How v1 (conversational) and v2 (deep-dive) differ
- Variant selection logic
- When to use which variant

---

## Related Work

- **persona-tim**: Sales persona-organ (reference for domain specialization)
- **persona-dev**: Reference implementation (first persona-organ)
- **autonomous_session.py** (in discovery-engine): Harness that executes persona work
- **select_organ.py**: Variant comparison and ensemble
- **CELL.md**: Detailed design and architecture

---

## Status

✓ Identity (role, expertise, values)
✓ Genome (v1 general + v2 deep-dive)
✓ Organ (compose, interpret, decide)
✓ Tests (unit + integration)
✓ Samples (basic + A/B)
✓ Documentation (CELL.md + README)

Ready for integration into DataFlow Advisory's virtual team harness.

---

## License

Part of DataFlow Advisory. Proprietary.

---

## Questions?

See CELL.md for design philosophy and extension patterns.
Run the samples to see how the organ works.
Run the tests to verify behavior.
