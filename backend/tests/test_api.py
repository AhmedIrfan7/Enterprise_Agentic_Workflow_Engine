"""
Integration tests for the FastAPI endpoints.
Run with: pytest backend/tests/ -v
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_create_workflow_missing_fields():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/workflows", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_nonexistent_workflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/workflows/nonexistent-id-12345")
    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_list_documents_empty():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/documents/list")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
