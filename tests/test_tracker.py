"""Tests for the usage tracker (SQLite storage)."""

import pytest

from llm_cost_calculator.tracker import UsageTracker


class TestUsageTracker:
    def setup_method(self):
        self.tracker = UsageTracker(db_path=":memory:")

    def teardown_method(self):
        self.tracker.close()

    def test_record_usage(self):
        cost = self.tracker.record("gpt-4o-mini", input_tokens=1000, output_tokens=500)
        assert cost.model == "gpt-4o-mini"
        assert cost.input_tokens == 1000
        assert cost.output_tokens == 500
        assert cost.total_cost > 0

    def test_record_with_endpoint(self):
        self.tracker.record(
            "gpt-4o-mini", input_tokens=100, output_tokens=50, endpoint="/api/chat"
        )
        records = self.tracker.get_recent(1)
        assert records[0].endpoint == "/api/chat"

    def test_get_summary_empty(self):
        summary = self.tracker.get_summary()
        assert summary.total_cost == 0.0
        assert summary.total_requests == 0
        assert summary.by_model == {}

    def test_get_summary_with_data(self):
        self.tracker.record("gpt-4o-mini", 1000, 500)
        self.tracker.record("gpt-4o", 2000, 1000)
        self.tracker.record("gpt-4o-mini", 500, 200)

        summary = self.tracker.get_summary()
        assert summary.total_requests == 3
        assert summary.total_input_tokens == 3500
        assert summary.total_output_tokens == 1700
        assert "gpt-4o-mini" in summary.by_model
        assert "gpt-4o" in summary.by_model

    def test_get_recent_ordering(self):
        self.tracker.record("gpt-4o-mini", 100, 50)
        self.tracker.record("gpt-4o", 200, 100)
        self.tracker.record("gpt-4o-mini", 300, 150)

        records = self.tracker.get_recent(2)
        assert len(records) == 2
        assert records[0].id > records[1].id  # Most recent first

    def test_get_recent_limit(self):
        for i in range(5):
            self.tracker.record("gpt-4o-mini", 100 * (i + 1), 50)

        records = self.tracker.get_recent(3)
        assert len(records) == 3

    def test_record_unknown_model_raises(self):
        with pytest.raises(ValueError, match="Unknown model"):
            self.tracker.record("nonexistent", 100, 50)
