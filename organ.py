"""
Matt persona organ — architecture composition, interpretation, and decision logic.

Pure organ: stdlib-only, no side effects, deterministic.

The organ encapsulates:
- compose(state, context) -> {prompt, model}
- interpret(state, context, response) -> {output, rationale, self_metric}
- decide(state, context) -> {output, rationale, self_metric}

An organ is the reusable logic for a persona. It reads accumulated knowledge,
applies domain expertise, and produces structured decisions.
"""

import json
import os
import sys
from typing import Any


def compose(state: dict[str, Any], context: dict[str, Any]) -> dict[str, str]:
    """
    Compose the system prompt from state and context.

    Args:
        state: Current work item state {variant, knowledge_text, directive, capabilities}
        context: Execution context {accumulated_knowledge, platform_identity}

    Returns:
        {prompt, model} ready for inference
    """
    variant = state.get("variant", "v1")
    knowledge_text = state.get("knowledge_text", "")
    directive = state.get("directive", "")
    capabilities_summary = state.get("capabilities_summary", "")
    platform_identity = context.get("platform_identity", "")

    # Load genome variant
    if variant == "v2":
        template_path = "genome/v2_architecture_deep_dive.txt"
    else:
        template_path = "genome/v1_general_session.txt"

    try:
        with open(template_path, "r") as f:
            template = f.read()
    except FileNotFoundError:
        # Fallback inline template if file not available
        template = """You are Matt, the CTO at DataFlow Advisory.

YOUR EXPERTISE: systems architecture, infrastructure design, technical risk assessment, scalability engineering, database architecture, API design

COMMUNICATION STYLE: precise, technically rigorous, focused on trade-offs and long-term resilience

DIRECTIVE FROM THE BOARD:
{directive}

YOUR ACCUMULATED KNOWLEDGE:
{knowledge_text}

--- YOUR CAPABILITIES ---
{capabilities_summary}

{platform_identity}
"""

    # Substitute placeholders
    prompt = template.format(
        knowledge_text=knowledge_text,
        directive=directive,
        capabilities_summary=capabilities_summary,
        platform_identity=platform_identity,
    )

    # Load model from ribosome
    try:
        with open("ribosome.json", "r") as f:
            ribosome = json.load(f)
        model = ribosome["model"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # Fallback model
        model = "anthropic/claude-sonnet-4.6"

    return {"prompt": prompt, "model": model}


def interpret(
    state: dict[str, Any], context: dict[str, Any], response: str
) -> dict[str, Any]:
    """
    Interpret the LLM response and extract structured signals.

    Args:
        state: Current work item state
        context: Execution context
        response: Raw LLM response text

    Returns:
        {output, rationale, self_metric} where self_metric ∈ [0, 10]
    """
    # Extract output as the full response
    output = response.strip()

    # Compute self_metric based on response characteristics
    # 0-10 scale: 10 = high confidence, clear architecture analysis, evidence-based
    # 0 = low confidence, unclear, no technical substance
    self_metric = _compute_self_metric(response)

    # Extract rationale: explain why this metric
    rationale = _extract_rationale(response, self_metric)

    return {"output": output, "rationale": rationale, "self_metric": {"confidence": self_metric}}


def decide(state: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """
    Make a high-level decision based on state without calling an LLM.

    This is for lightweight decisions that don't require inference.
    Example: comparing two variants via select.py.

    Args:
        state: Current work item state {option_a, option_b, metric}
        context: Execution context

    Returns:
        {output, rationale, self_metric}
    """
    option_a = state.get("option_a")
    option_b = state.get("option_b")
    metric = state.get("metric", "self_metric")

    if not option_a or not option_b:
        return {
            "output": "Insufficient options to decide",
            "rationale": "Missing option_a or option_b in state",
            "self_metric": {"confidence": 3},
        }

    # Compare based on metric
    metric_a = option_a.get(metric, 0)
    metric_b = option_b.get(metric, 0)

    if metric_a > metric_b:
        chosen = "option_a"
        delta = metric_a - metric_b
    elif metric_b > metric_a:
        chosen = "option_b"
        delta = metric_b - metric_a
    else:
        chosen = "tie"
        delta = 0

    output = f"Selected {chosen} (delta={delta:.2f})"
    rationale = (
        f"Compared {metric}: option_a={metric_a}, option_b={metric_b}. "
        f"Chose {chosen}."
    )
    confidence = min(10, int(delta * 5))  # Higher delta = higher confidence

    return {
        "output": output,
        "rationale": rationale,
        "self_metric": {"confidence": confidence},
    }


# --- Private helpers ---


def _compute_self_metric(response: str) -> int:
    """
    Compute confidence metric [0, 10] based on response characteristics.

    Heuristics:
    - Length: longer = more thought (but not linearly)
    - Structure: bullet points, numbered lists = structured thinking
    - Architecture terms: scalability, latency, throughput, consistency, availability
    - Technical depth: specific technologies, patterns, constraints
    - Confidence words: "clearly", "should" = high confidence
    - Uncertainty words: "might", "unclear" = low confidence
    """
    if not response:
        return 0

    score = 3  # Start at low (let evidence build it up)

    # Reward length (more thinking)
    words = len(response.split())
    if words > 500:
        score += 3
    elif words > 200:
        score += 2
    elif words > 50:
        score += 1

    # Reward structure
    newline_count = response.count("\n")
    if newline_count > 5:
        score += 2  # Multiple paragraphs
    elif newline_count > 2:
        score += 1

    # Count bullet points/lists
    bullet_count = response.count("- ") + response.count("* ")
    if bullet_count > 3:
        score += 2  # Well-structured list
    elif bullet_count > 0:
        score += 1

    # Reward architecture-specific terms (technical focus)
    arch_terms = [
        "architecture",
        "scalability",
        "latency",
        "throughput",
        "consistency",
        "availability",
        "trade-off",
        "database",
        "api",
        "load",
        "cache",
        "replica",
        "shard",
        "failover",
        "resilience",
        "bottleneck",
        "performance",
        "monitoring",
        "deployment",
    ]
    arch_term_count = sum(1 for term in arch_terms if term in response.lower())
    if arch_term_count > 5:
        score += 2
    elif arch_term_count > 2:
        score += 1

    # Reward technical depth (specific technologies, patterns)
    tech_terms = [
        "postgres",
        "redis",
        "kubernetes",
        "aws",
        "docker",
        "sql",
        "nosql",
        "event",
        "queue",
        "stream",
        "consensus",
        "circuit breaker",
        "service mesh",
        "rate limit",
    ]
    tech_term_count = sum(1 for term in tech_terms if term in response.lower())
    if tech_term_count > 3:
        score += 2
    elif tech_term_count > 0:
        score += 1

    # Confidence language
    confidence_words = [
        "clearly",
        "definitely",
        "certainly",
        "should",
        "will",
        "recommend",
        "strong",
        "proven",
    ]
    uncertainty_words = [
        "might",
        "could",
        "possibly",
        "perhaps",
        "uncertain",
        "unclear",
        "weak",
        "risky",
    ]

    response_lower = response.lower()

    confidence_count = sum(1 for word in confidence_words if word in response_lower)
    uncertainty_count = sum(1 for word in uncertainty_words if word in response_lower)

    score += confidence_count
    score -= uncertainty_count

    # Clamp to [0, 10]
    return max(0, min(10, score))


def _extract_rationale(response: str, metric: int) -> str:
    """Extract a one-line rationale explaining the self_metric."""
    response_lower = response.lower()

    if metric >= 9:
        return "High confidence with clear architecture analysis and evidence"
    elif metric >= 7:
        return "Confident response with technical depth and trade-off analysis"
    elif metric >= 5:
        return "Moderate confidence with reasonable technical analysis"
    elif metric >= 3:
        return "Limited confidence due to lack of structure or technical substance"
    else:
        return "Low confidence or incomplete response"


def main() -> int:
    """Entry point for organ execution."""
    path = os.environ.get("ORGAN_INPUT")
    raw = open(path).read() if path else sys.stdin.read()
    try:
        payload = json.loads(raw)
        state = payload["state"]
    except Exception as e:
        print(json.dumps({"error": f"invalid input: {e}"}), file=sys.stderr)
        return 1
    print(json.dumps(decide(state, payload.get("context")), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
