"""Tests for LLM pricing calculations."""

import pytest

from llm_cost_calculator.pricing import CostBreakdown, calculate_cost, get_supported_models


class TestCostBreakdown:
    def test_total_cost(self):
        cb = CostBreakdown(
            model="gpt-4o-mini",
            input_tokens=1000,
            output_tokens=500,
            input_cost=0.00015,
            output_cost=0.0003,
        )
        assert cb.total_cost == pytest.approx(0.00045)

    def test_total_tokens(self):
        cb = CostBreakdown(
            model="gpt-4o-mini",
            input_tokens=1000,
            output_tokens=500,
            input_cost=0.0,
            output_cost=0.0,
        )
        assert cb.total_tokens == 1500


class TestCalculateCost:
    def test_gpt4o_mini_cost(self):
        cost = calculate_cost("gpt-4o-mini", input_tokens=1_000_000, output_tokens=1_000_000)
        assert cost.input_cost == pytest.approx(0.15)
        assert cost.output_cost == pytest.approx(0.60)
        assert cost.total_cost == pytest.approx(0.75)

    def test_gpt4o_cost(self):
        cost = calculate_cost("gpt-4o", input_tokens=1_000_000, output_tokens=1_000_000)
        assert cost.input_cost == pytest.approx(2.50)
        assert cost.output_cost == pytest.approx(10.00)

    def test_claude_sonnet_cost(self):
        cost = calculate_cost(
            "claude-sonnet-4-5-20250929", input_tokens=1_000_000, output_tokens=1_000_000
        )
        assert cost.input_cost == pytest.approx(3.00)
        assert cost.output_cost == pytest.approx(15.00)

    def test_zero_tokens(self):
        cost = calculate_cost("gpt-4o-mini", input_tokens=0, output_tokens=0)
        assert cost.total_cost == 0.0

    def test_unknown_model_raises(self):
        with pytest.raises(ValueError, match="Unknown model"):
            calculate_cost("nonexistent-model", 100, 100)

    def test_small_token_count(self):
        cost = calculate_cost("gpt-4o-mini", input_tokens=100, output_tokens=50)
        assert cost.input_cost == pytest.approx(0.000015)
        assert cost.output_cost == pytest.approx(0.00003)


class TestGetSupportedModels:
    def test_returns_list(self):
        models = get_supported_models()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_includes_known_models(self):
        models = get_supported_models()
        assert "gpt-4o-mini" in models
        assert "claude-sonnet-4-5-20250929" in models
