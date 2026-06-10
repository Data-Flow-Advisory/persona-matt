"""
Variant selection via self_metric comparison.

Compares two organ outputs on their self_metric and selects the higher-confidence variant.
"""

from typing import Any


def select_best_variant(
    variant_a: dict[str, Any], variant_b: dict[str, Any]
) -> dict[str, Any]:
    """
    Select the best variant based on self_metric.

    Args:
        variant_a: {output, rationale, self_metric} from variant 1
        variant_b: {output, rationale, self_metric} from variant 2

    Returns:
        {selected: "a" | "b", delta: float, best: dict, rationale: str}
    """
    metric_a = variant_a.get("self_metric", 0)
    metric_b = variant_b.get("self_metric", 0)

    delta = abs(metric_a - metric_b)

    if metric_a > metric_b:
        selected = "a"
        best = variant_a
    elif metric_b > metric_a:
        selected = "b"
        best = variant_b
    else:
        # Tie: prefer variant_a by default
        selected = "a"
        best = variant_a

    rationale = (
        f"Variant {selected.upper()} selected: "
        f"metric_a={metric_a}, metric_b={metric_b}, delta={delta:.1f}"
    )

    return {
        "selected": selected,
        "delta": delta,
        "best": best,
        "rationale": rationale,
    }


def compute_ensemble(
    responses: list[dict[str, Any]], weight_by_metric: bool = True
) -> dict[str, Any]:
    """
    Ensemble multiple organ outputs via weighted voting (if weight_by_metric)
    or simple averaging (if not).

    Args:
        responses: List of {output, rationale, self_metric}
        weight_by_metric: If True, weight responses by confidence

    Returns:
        {ensemble_output, ensemble_metric, explanation}
    """
    if not responses:
        return {
            "ensemble_output": "",
            "ensemble_metric": 0,
            "explanation": "No responses to ensemble",
        }

    # For now, select highest metric (simple ensemble)
    best = max(responses, key=lambda r: r.get("self_metric", 0))

    avg_metric = sum(r.get("self_metric", 0) for r in responses) / len(responses)

    explanation = (
        f"Ensemble of {len(responses)} responses. "
        f"Selected highest-metric response (metric={best.get('self_metric')}). "
        f"Average metric across all: {avg_metric:.1f}"
    )

    return {
        "ensemble_output": best.get("output", ""),
        "ensemble_metric": avg_metric,
        "explanation": explanation,
    }
