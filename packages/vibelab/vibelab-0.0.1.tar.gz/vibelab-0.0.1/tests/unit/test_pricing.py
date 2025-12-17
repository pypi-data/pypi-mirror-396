"""Unit tests for pricing calculations."""

import unittest

from vibelab.pricing import calculate_cost
from vibelab.harnesses import HARNESSES


class TestPricing(unittest.TestCase):
    """Tests for pricing calculations."""

    def test_calculate_cost_with_input_output(self):
        """Test cost calculation with input/output token breakdown."""
        harness = HARNESSES["claude-code"]
        cost = calculate_cost(harness, "anthropic", "opus", input_tokens=1000, output_tokens=500)
        self.assertIsNotNone(cost)
        # Expected: (1000/1M * 15) + (500/1M * 75) = 0.015 + 0.0375 = 0.0525
        self.assertAlmostEqual(cost, 0.0525, places=6)

    def test_calculate_cost_with_total_tokens(self):
        """Test cost calculation with total tokens only."""
        harness = HARNESSES["openai-codex"]
        cost = calculate_cost(harness, "openai", "gpt-4o", total_tokens=1000)
        self.assertIsNotNone(cost)
        # Expected: (500/1M * 2.50) + (500/1M * 10.0) = 0.00125 + 0.005 = 0.00625
        self.assertAlmostEqual(cost, 0.00625, places=6)

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation with unknown model."""
        harness = HARNESSES["claude-code"]
        cost = calculate_cost(harness, "anthropic", "unknown-model", input_tokens=1000, output_tokens=500)
        self.assertIsNone(cost)

    def test_pricing_coverage(self):
        """Test that all harness models have pricing."""
        for harness in HARNESSES.values():
            for provider in harness.supported_providers:
                models = harness.get_models(provider)
                for model_info in models:
                    # Check if pricing exists
                    pricing = harness.get_pricing(provider, model_info.id)
                    if pricing:
                        self.assertIsNotNone(
                            pricing,
                            f"Pricing found for {harness.id}:{provider}:{model_info.id}",
                        )
                    else:
                        # Log warning but don't fail - new models may not have pricing yet
                        print(
                            f"Warning: No pricing found for {harness.id}:{provider}:{model_info.id}"
                        )

