# LLM Cost Calculator

[![CI](https://github.com/marlonbarreto-git/llm-cost-calculator/actions/workflows/ci.yml/badge.svg)](https://github.com/marlonbarreto-git/llm-cost-calculator/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

API service that tracks and optimizes LLM API costs with per-model analytics.

## Overview

LLM Cost Calculator provides a FastAPI service for recording LLM API usage, calculating costs based on up-to-date per-model pricing, and querying usage summaries. It stores all usage records in SQLite and supports models from OpenAI (GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo) and Anthropic (Claude Opus, Sonnet, Haiku).

## Architecture

```
HTTP Request (model, input_tokens, output_tokens)
  |
  v
FastAPI Router
  |
  +---> POST /track     ---> UsageTracker.record()
  +---> GET  /summary   ---> UsageTracker.get_summary()
  +---> GET  /recent    ---> UsageTracker.get_recent()
  +---> GET  /models    ---> Pricing.get_supported_models()
  |
  v
Pricing Engine (per-model $/1M tokens)
  |
  v
SQLite Storage (usage table)
  |
  v
JSON Response (cost breakdown / summary)
```

## Features

- Track LLM API usage with per-request cost calculation
- Pricing data for 7 OpenAI and Anthropic models
- Usage summary with per-model cost aggregation
- Recent usage history with configurable limits
- SQLite-backed persistent storage (in-memory by default)
- Per-endpoint attribution for cost analysis

## Tech Stack

- Python 3.11+
- FastAPI + Uvicorn
- SQLite (via stdlib sqlite3)
- Pydantic
- Rich

## Quick Start

```bash
git clone https://github.com/marlonbarreto-git/llm-cost-calculator.git
cd llm-cost-calculator
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn llm_cost_calculator.api:app --reload
```

## Project Structure

```
src/llm_cost_calculator/
  __init__.py
  api.py        # FastAPI app with /track, /summary, /recent, /models
  pricing.py    # Per-model pricing data and cost calculation
  tracker.py    # SQLite-backed usage recording and querying
tests/
  test_api.py
  test_pricing.py
  test_tracker.py
```

## Testing

```bash
pytest -v --cov=src/llm_cost_calculator
```

23 tests covering API endpoints, pricing calculations, and usage tracking with SQLite.

## License

MIT