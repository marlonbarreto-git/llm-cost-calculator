"""Usage tracker - stores and queries LLM API usage in SQLite."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from llm_cost_calculator.pricing import CostBreakdown, calculate_cost

DEFAULT_RECENT_LIMIT = 10


@dataclass
class UsageRecord:
    """A single persisted usage record retrieved from the database."""

    id: int
    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    endpoint: str | None


@dataclass
class UsageSummary:
    """Aggregate statistics across all recorded usage."""

    total_cost: float
    total_input_tokens: int
    total_output_tokens: int
    total_requests: int
    by_model: dict[str, float]


class UsageTracker:
    """Tracks LLM API usage costs in a SQLite database."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        """Initializes the tracker with a SQLite database.

        Args:
            db_path: Path to the SQLite file, or ":memory:" for in-memory storage.
        """
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                input_cost REAL NOT NULL,
                output_cost REAL NOT NULL,
                total_cost REAL NOT NULL,
                endpoint TEXT
            )
        """)
        self._conn.commit()

    def record(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        endpoint: str | None = None,
    ) -> CostBreakdown:
        """Records a single LLM API call and returns its cost breakdown.

        Args:
            model: LLM model identifier.
            input_tokens: Number of input tokens consumed.
            output_tokens: Number of output tokens produced.
            endpoint: Optional API endpoint that originated the call.

        Raises:
            ValueError: If the model is not recognized.
        """
        cost = calculate_cost(model, input_tokens, output_tokens)
        now = datetime.now(timezone.utc).isoformat()

        self._conn.execute(
            """INSERT INTO usage (timestamp, model, input_tokens, output_tokens,
               input_cost, output_cost, total_cost, endpoint)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (now, model, input_tokens, output_tokens,
             cost.input_cost, cost.output_cost, cost.total_cost, endpoint),
        )
        self._conn.commit()
        return cost

    def get_summary(self) -> UsageSummary:
        """Returns aggregate cost and token statistics across all records."""
        row = self._conn.execute(
            """SELECT
                COALESCE(SUM(total_cost), 0) as total_cost,
                COALESCE(SUM(input_tokens), 0) as total_input,
                COALESCE(SUM(output_tokens), 0) as total_output,
                COUNT(*) as total_requests
               FROM usage"""
        ).fetchone()

        by_model_rows = self._conn.execute(
            "SELECT model, SUM(total_cost) as cost FROM usage GROUP BY model"
        ).fetchall()

        by_model = {r["model"]: r["cost"] for r in by_model_rows}

        return UsageSummary(
            total_cost=row["total_cost"],
            total_input_tokens=row["total_input"],
            total_output_tokens=row["total_output"],
            total_requests=row["total_requests"],
            by_model=by_model,
        )

    def get_recent(self, limit: int = DEFAULT_RECENT_LIMIT) -> list[UsageRecord]:
        """Returns the most recent usage records in descending order.

        Args:
            limit: Maximum number of records to return.
        """
        rows = self._conn.execute(
            "SELECT * FROM usage ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()

        return [
            UsageRecord(
                id=r["id"],
                timestamp=r["timestamp"],
                model=r["model"],
                input_tokens=r["input_tokens"],
                output_tokens=r["output_tokens"],
                input_cost=r["input_cost"],
                output_cost=r["output_cost"],
                total_cost=r["total_cost"],
                endpoint=r["endpoint"],
            )
            for r in rows
        ]

    def close(self) -> None:
        """Closes the underlying database connection."""
        self._conn.close()
