"""
Full-stack integration test: exercises the complete request path from HTTP endpoint
down to the database and back, using an AsyncClient against the live ASGI app.
No real LLM calls are made — the agent execution is mocked at the service boundary.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app


@pytest.mark.asyncio
async def test_health_check_returns_healthy():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_workflow_create_and_retrieve():
    """
    POST /workflows → 201 with workflow object
    GET  /workflows/{id} → 200 with same object
    """
    payload = {
        "title": "Integration Test Workflow",
        "goal": "This is a full-stack automated integration test. Summarize the number 42.",
        "tools_selected": ["web_search"],
        "llm_provider": "openai",
        "llm_model": "gpt-4o-mini",
    }

    # Mock the background execution so no real LLM call is made
    with patch("app.api.v1.endpoints.workflows.execute_workflow_bg", new=AsyncMock()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            create_resp = await client.post("/api/v1/workflows", json=payload)

    assert create_resp.status_code == 201, create_resp.text
    workflow = create_resp.json()
    assert workflow["title"] == payload["title"]
    assert workflow["goal"] == payload["goal"]
    assert workflow["status"] == "pending"
    assert "id" in workflow
    assert "created_at" in workflow

    workflow_id = workflow["id"]

    # Retrieve
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        get_resp = await client.get(f"/api/v1/workflows/{workflow_id}")

    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == workflow_id
    assert fetched["goal"] == payload["goal"]

    # List — should contain our new workflow
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        list_resp = await client.get("/api/v1/workflows")

    assert list_resp.status_code == 200
    ids = [w["id"] for w in list_resp.json()["items"]]
    assert workflow_id in ids

    # Logs — empty for this workflow (no real execution ran)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        logs_resp = await client.get(f"/api/v1/logs/{workflow_id}")

    assert logs_resp.status_code == 200
    assert isinstance(logs_resp.json()["items"], list)

    # Delete
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        del_resp = await client.delete(f"/api/v1/workflows/{workflow_id}")

    assert del_resp.status_code == 204

    # Confirm 404 after delete
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        gone_resp = await client.get(f"/api/v1/workflows/{workflow_id}")

    assert gone_resp.status_code == 404
    assert gone_resp.json()["error_code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_tools_endpoint_returns_tools():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/tools")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    tool_ids = [t["id"] for t in data["items"]]
    assert "web_search" in tool_ids
    assert "query_knowledge_base" in tool_ids


@pytest.mark.asyncio
async def test_document_upload_unsupported_type():
    import io
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("malware.exe", io.BytesIO(b"\x00\x01\x02"), "application/octet-stream")},
        )
    assert resp.status_code == 415


@pytest.mark.asyncio
async def test_validation_error_returns_422():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/workflows", json={"title": "No goal field"})
    assert resp.status_code == 422
    assert resp.json()["error_code"] == "REQUEST_VALIDATION_ERROR"
