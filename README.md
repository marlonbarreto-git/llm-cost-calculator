# llm-cost-calculator

Service that tracks and optimizes LLM API costs. Log every API call, monitor spending by model, and get per-request cost breakdowns.

## Features

- **Cost tracking**: Record token usage and calculate costs per request
- **Multi-model pricing**: Supports GPT-4o, GPT-4o-mini, Claude Opus/Sonnet/Haiku
- **SQLite storage**: Persistent usage history with zero infrastructure
- **REST API**: FastAPI endpoints for tracking, summaries, and recent usage
- **Per-endpoint attribution**: Track which API endpoints generate the most cost

## Architecture

```
llm_cost_calculator/
├── pricing.py    # Token pricing per model, cost calculation
├── tracker.py    # SQLite-backed usage tracker
└── api.py        # FastAPI endpoints (/track, /summary, /recent, /models)
```

## Quick Start

```bash
uv sync

# Run server
uvicorn llm_cost_calculator.api:app --reload

# Track usage
curl -X POST http://localhost:8000/track \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "input_tokens": 1000, "output_tokens": 500}'

# Get cost summary
curl http://localhost:8000/summary

# Recent requests
curl http://localhost:8000/recent?limit=10

# List supported models
curl http://localhost:8000/models
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/track` | Record token usage and get cost |
| GET | `/summary` | Total cost, tokens, and breakdown by model |
| GET | `/recent` | Recent usage records |
| GET | `/models` | List supported models with pricing |

## Supported Models & Pricing

| Model | Input ($/1M tokens) | Output ($/1M tokens) |
|-------|---------------------|----------------------|
| gpt-4o | $2.50 | $10.00 |
| gpt-4o-mini | $0.15 | $0.60 |
| claude-opus-4 | $15.00 | $75.00 |
| claude-sonnet-4.5 | $3.00 | $15.00 |
| claude-haiku-4.5 | $0.80 | $4.00 |

## Development

```bash
uv sync --all-extras
uv run pytest tests/ -v
```

## Roadmap

- **v2**: Web dashboard with cost graphs, budget alerts
- **v3**: Auto model recommendations, prompt caching analysis

## License

MIT
