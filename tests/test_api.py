"""Tests for the FastAPI endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from llm_cost_calculator.api import app


class TestAPI:
    @pytest.mark.asyncio
    async def test_health(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_track_usage(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/track",
                json={
                    "model": "gpt-4o-mini",
                    "input_tokens": 1000,
                    "output_tokens": 500,
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "gpt-4o-mini"
        assert data["total_cost"] > 0
        assert data["total_tokens"] == 1500

    @pytest.mark.asyncio
    async def test_get_summary(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.post(
                "/track",
                json={"model": "gpt-4o-mini", "input_tokens": 1000, "output_tokens": 500},
            )
            response = await client.get("/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["total_requests"] >= 1
        assert "by_model" in data

    @pytest.mark.asyncio
    async def test_get_recent(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.post(
                "/track",
                json={"model": "gpt-4o-mini", "input_tokens": 100, "output_tokens": 50},
            )
            response = await client.get("/recent?limit=5")
        assert response.status_code == 200
        records = response.json()
        assert isinstance(records, list)

    @pytest.mark.asyncio
    async def test_list_models(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/models")
        assert response.status_code == 200
        data = response.json()
        assert "gpt-4o-mini" in data["models"]

    @pytest.mark.asyncio
    async def test_track_invalid_model(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/track",
                json={"model": "fake-model", "input_tokens": 100, "output_tokens": 50},
            )
        assert response.status_code == 500 or response.status_code == 422
