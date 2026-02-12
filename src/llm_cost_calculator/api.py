"""FastAPI application for LLM cost tracking."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from llm_cost_calculator import __version__
from llm_cost_calculator.pricing import get_supported_models
from llm_cost_calculator.tracker import UsageTracker

app = FastAPI(
    title="LLM Cost Calculator",
    description="Track and optimize LLM API costs.",
    version=__version__,
)

tracker = UsageTracker()


class UsageRequest(BaseModel):
    model: str = Field(description="LLM model name")
    input_tokens: int = Field(ge=0, description="Number of input tokens")
    output_tokens: int = Field(ge=0, description="Number of output tokens")
    endpoint: str | None = Field(default=None, description="API endpoint that made the call")


@app.get("/health")
async def health():
    return {"status": "healthy", "version": __version__}


@app.post("/track")
async def track_usage(request: UsageRequest):
    try:
        cost = tracker.record(
            model=request.model,
            input_tokens=request.input_tokens,
            output_tokens=request.output_tokens,
            endpoint=request.endpoint,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {
        "model": cost.model,
        "input_cost": round(cost.input_cost, 6),
        "output_cost": round(cost.output_cost, 6),
        "total_cost": round(cost.total_cost, 6),
        "total_tokens": cost.total_tokens,
    }


@app.get("/summary")
async def get_summary():
    summary = tracker.get_summary()
    return {
        "total_cost": round(summary.total_cost, 6),
        "total_input_tokens": summary.total_input_tokens,
        "total_output_tokens": summary.total_output_tokens,
        "total_requests": summary.total_requests,
        "by_model": {k: round(v, 6) for k, v in summary.by_model.items()},
    }


@app.get("/recent")
async def get_recent(limit: int = 10):
    records = tracker.get_recent(limit=limit)
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "model": r.model,
            "input_tokens": r.input_tokens,
            "output_tokens": r.output_tokens,
            "total_cost": round(r.total_cost, 6),
            "endpoint": r.endpoint,
        }
        for r in records
    ]


@app.get("/models")
async def list_models():
    return {"models": get_supported_models()}
