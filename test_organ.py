"""
Unit tests for Matt persona organ.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open

import organ
import select_organ


class TestOrganCompose(unittest.TestCase):
    """Tests for organ.compose()"""

    def test_compose_returns_dict_with_prompt_and_model(self):
        """compose() returns {prompt, model}"""
        state = {
            "variant": "v1",
            "knowledge_text": "Sample architecture",
            "directive": "Design scalable API layer",
            "capabilities_summary": "Can review systems, design architecture",
        }
        context = {
            "platform_identity": "DataFlow Advisory",
        }

        result = organ.compose(state, context)

        self.assertIsInstance(result, dict)
        self.assertIn("prompt", result)
        self.assertIn("model", result)

    def test_compose_v1_variant(self):
        """compose() can load v1 genome variant"""
        state = {
            "variant": "v1",
            "knowledge_text": "Test architecture",
            "directive": "Test directive",
            "capabilities_summary": "Test capabilities",
        }
        context = {"platform_identity": "Test platform"}

        result = organ.compose(state, context)
        self.assertIn("Matt", result["prompt"])

    def test_compose_v2_variant(self):
        """compose() can load v2 genome variant"""
        state = {
            "variant": "v2",
            "knowledge_text": "Test architecture",
            "directive": "Test directive",
            "capabilities_summary": "Test capabilities",
        }
        context = {"platform_identity": "Test platform"}

        result = organ.compose(state, context)
        self.assertIn("Matt", result["prompt"])

    def test_compose_defaults_model_on_error(self):
        """compose() returns fallback model when ribosome.json missing"""
        state = {
            "variant": "v1",
            "knowledge_text": "Test",
            "directive": "Test",
            "capabilities_summary": "Test",
        }
        context = {"platform_identity": "Test"}

        # Should not raise even if ribosome.json is missing
        result = organ.compose(state, context)
        self.assertIsNotNone(result["model"])

    def test_compose_substitutes_placeholders(self):
        """compose() substitutes placeholders in template"""
        state = {
            "variant": "v1",
            "knowledge_text": "UNIQUE_KNOWLEDGE_123",
            "directive": "UNIQUE_DIRECTIVE_456",
            "capabilities_summary": "UNIQUE_CAPABILITIES_789",
        }
        context = {"platform_identity": "UNIQUE_PLATFORM_999"}

        result = organ.compose(state, context)

        self.assertIn("UNIQUE_KNOWLEDGE_123", result["prompt"])
        self.assertIn("UNIQUE_DIRECTIVE_456", result["prompt"])
        self.assertIn("UNIQUE_CAPABILITIES_789", result["prompt"])


class TestOrganInterpret(unittest.TestCase):
    """Tests for organ.interpret()"""

    def test_interpret_returns_structured_result(self):
        """interpret() returns {output, rationale, self_metric}"""
        state = {}
        context = {}
        response = "Matt's analysis: This system needs better scalability. Current throughput is 10k req/s but peak is 50k."

        result = organ.interpret(state, context, response)

        self.assertIsInstance(result, dict)
        self.assertIn("output", result)
        self.assertIn("rationale", result)
        self.assertIn("self_metric", result)
        self.assertIsInstance(result["self_metric"], int)

    def test_interpret_metric_in_range(self):
        """interpret() self_metric is between 0 and 10"""
        state = {}
        context = {}
        response = "Clear architecture decision with quantified trade-offs and scaling analysis."

        result = organ.interpret(state, context, response)

        self.assertGreaterEqual(result["self_metric"], 0)
        self.assertLessEqual(result["self_metric"], 10)

    def test_interpret_empty_response_returns_low_metric(self):
        """interpret() returns low metric for empty response"""
        state = {}
        context = {}
        response = ""

        result = organ.interpret(state, context, response)

        self.assertEqual(result["self_metric"], 0)

    def test_interpret_structured_response_higher_metric(self):
        """interpret() rewards structured technical analysis"""
        state = {}
        context = {}
        response = """
Architecture analysis:
- Current Throughput: 10k req/s
- Peak Throughput: 50k req/s
- Scalability Issues:
  - Database query latency at 150ms (target: <50ms)
  - Redis cache hit rate at 70% (target: >90%)
  - Single availability zone risk
- Recommendations:
  - Add read replicas to reduce query latency
  - Implement distributed cache with multiple nodes
  - Multi-AZ deployment strategy
"""

        result = organ.interpret(state, context, response)

        self.assertGreater(result["self_metric"], 3)

    def test_interpret_with_architecture_terms_higher_metric(self):
        """interpret() rewards architecture-specific terminology"""
        state = {}
        context = {}
        response = (
            "Scalability analysis shows throughput bottleneck at the database layer. "
            "Latency is too high due to cache misses. "
            "Recommend sharding strategy for availability and consistency trade-offs."
        )

        result = organ.interpret(state, context, response)

        self.assertGreater(result["self_metric"], 4)

    def test_interpret_confidence_words_increase_metric(self):
        """interpret() rewards confidence language"""
        low_conf = "This might be a scalability issue, possibly needs improvement."
        high_conf = "This is clearly a bottleneck. We should definitely add caching."

        low_result = organ.interpret({}, {}, low_conf)
        high_result = organ.interpret({}, {}, high_conf)

        self.assertLess(low_result["self_metric"], high_result["self_metric"])


class TestOrganDecide(unittest.TestCase):
    """Tests for organ.decide()"""

    def test_decide_returns_structured_result(self):
        """decide() returns {output, rationale, self_metric}"""
        state = {
            "option_a": {"output": "Architecture A", "self_metric": 7},
            "option_b": {"output": "Architecture B", "self_metric": 5},
        }
        context = {}

        result = organ.decide(state, context)

        self.assertIsInstance(result, dict)
        self.assertIn("output", result)
        self.assertIn("rationale", result)
        self.assertIn("self_metric", result)

    def test_decide_selects_higher_metric_option(self):
        """decide() selects option with higher metric"""
        state = {
            "option_a": {"output": "Option A", "self_metric": 8},
            "option_b": {"output": "Option B", "self_metric": 4},
        }
        context = {}

        result = organ.decide(state, context)

        self.assertIn("option_a", result["output"])

    def test_decide_handles_missing_options(self):
        """decide() gracefully handles missing options"""
        state = {"option_a": None, "option_b": None}
        context = {}

        result = organ.decide(state, context)

        self.assertEqual(result["self_metric"], 3)
        self.assertIn("Insufficient", result["output"])


class TestSelectOrgan(unittest.TestCase):
    """Tests for select_organ module"""

    def test_select_best_variant_returns_structure(self):
        """select_best_variant() returns proper structure"""
        variant_a = {"output": "Analysis A", "rationale": "Reason A", "self_metric": 7}
        variant_b = {"output": "Analysis B", "rationale": "Reason B", "self_metric": 5}

        result = select_organ.select_best_variant(variant_a, variant_b)

        self.assertIsInstance(result, dict)
        self.assertIn("selected", result)
        self.assertIn("delta", result)
        self.assertIn("best", result)
        self.assertIn("rationale", result)

    def test_select_best_variant_chooses_higher_metric(self):
        """select_best_variant() chooses higher-metric variant"""
        variant_a = {"output": "A", "self_metric": 8}
        variant_b = {"output": "B", "self_metric": 5}

        result = select_organ.select_best_variant(variant_a, variant_b)

        self.assertEqual(result["selected"], "a")
        self.assertEqual(result["delta"], 3)

    def test_select_best_variant_tie_prefers_a(self):
        """select_best_variant() prefers variant_a on tie"""
        variant_a = {"output": "A", "self_metric": 7}
        variant_b = {"output": "B", "self_metric": 7}

        result = select_organ.select_best_variant(variant_a, variant_b)

        self.assertEqual(result["selected"], "a")

    def test_compute_ensemble_returns_structure(self):
        """compute_ensemble() returns proper structure"""
        responses = [
            {"output": "A", "self_metric": 8},
            {"output": "B", "self_metric": 6},
        ]

        result = select_organ.compute_ensemble(responses)

        self.assertIn("ensemble_output", result)
        self.assertIn("ensemble_metric", result)
        self.assertIn("explanation", result)

    def test_compute_ensemble_handles_empty_list(self):
        """compute_ensemble() handles empty response list"""
        result = select_organ.compute_ensemble([])

        self.assertEqual(result["ensemble_output"], "")
        self.assertEqual(result["ensemble_metric"], 0)


class TestOrganIntegration(unittest.TestCase):
    """Integration tests for full organ workflow"""

    def test_compose_interpret_cycle(self):
        """Can compose a prompt and interpret a response"""
        state = {
            "variant": "v1",
            "knowledge_text": "Current system: 10k req/s, single database, 150ms query latency",
            "directive": "Assess scalability requirements for 10x growth",
            "capabilities_summary": "Can review system metrics and design improvements",
        }
        context = {"platform_identity": "DataFlow Advisory"}

        composed = organ.compose(state, context)
        self.assertIn("Matt", composed["prompt"])

        # Simulate a response
        fake_response = (
            "Scalability analysis: Current throughput 10k req/s needs 100k req/s capacity. "
            "Database latency is the bottleneck at 150ms. "
            "Recommend read replicas and distributed caching strategy. "
            "Trade-off: complexity vs resilience. "
            "Timeline: 3 months to implement."
        )

        interpreted = organ.interpret(state, context, fake_response)
        self.assertGreater(interpreted["self_metric"], 4)

    def test_variant_comparison(self):
        """Can run both variants and compare outputs"""
        state_v1 = {
            "variant": "v1",
            "knowledge_text": "Test",
            "directive": "Test",
            "capabilities_summary": "Test",
        }
        state_v2 = {
            "variant": "v2",
            "knowledge_text": "Test",
            "directive": "Test",
            "capabilities_summary": "Test",
        }
        context = {"platform_identity": "Test"}

        v1 = organ.compose(state_v1, context)
        v2 = organ.compose(state_v2, context)

        # Both should load successfully
        self.assertIsNotNone(v1["prompt"])
        self.assertIsNotNone(v2["prompt"])


if __name__ == "__main__":
    unittest.main()
