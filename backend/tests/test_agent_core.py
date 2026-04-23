"""
Unit tests for the core agentic loop components.
Run with: pytest backend/tests/ -v
"""
import asyncio
import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.agents.token_tracker import TokenUsageTracker
from app.core.agents.llm_factory import estimate_cost
from app.core.tools.registry import get_tools, list_available_tools
from app.utils.retry import async_retry


# ---------------------------------------------------------------------------
# Token tracker
# ---------------------------------------------------------------------------

def test_token_tracker_initial_state():
    tracker = TokenUsageTracker(model="gpt-4o-mini")
    assert tracker.total_tokens == 0
    assert tracker.llm_calls == 0
    assert tracker.estimated_cost_usd == 0.0


def test_token_tracker_summary_structure():
    tracker = TokenUsageTracker(model="gpt-4o-mini")
    s = tracker.summary()
    for key in ("model", "llm_calls", "prompt_tokens", "completion_tokens", "total_tokens", "estimated_cost_usd"):
        assert key in s


def test_estimate_cost_known_model():
    cost = estimate_cost("gpt-4o-mini", prompt_tokens=1000, completion_tokens=500)
    assert cost > 0.0
    assert isinstance(cost, float)


def test_estimate_cost_unknown_model():
    cost = estimate_cost("unknown-model", prompt_tokens=1000, completion_tokens=500)
    assert cost == 0.0


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

def test_list_available_tools_returns_nonempty():
    tools = list_available_tools()
    assert len(tools) > 0
    for tool in tools:
        assert "id" in tool
        assert "description" in tool


def test_get_tools_empty_ids_returns_all():
    all_tools = get_tools([])
    named_tools = get_tools(list(t["id"] for t in list_available_tools()))
    assert len(all_tools) == len(named_tools)


def test_get_tools_specific_ids():
    tools = get_tools(["web_search"])
    assert len(tools) == 1
    assert tools[0].name == "web_search"


def test_get_tools_invalid_id_falls_back():
    tools = get_tools(["nonexistent_tool_xyz"])
    # falls back to all tools when none matched
    assert len(tools) == len(get_tools([]))


# ---------------------------------------------------------------------------
# Retry utility
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_retry_succeeds_on_first_attempt():
    mock_fn = AsyncMock(return_value="success")
    result = await async_retry(mock_fn, max_attempts=3)
    assert result == "success"
    mock_fn.assert_awaited_once()


@pytest.mark.asyncio
async def test_retry_retries_on_failure_then_succeeds():
    call_count = 0

    async def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("transient error")
        return "recovered"

    result = await async_retry(flaky, max_attempts=4, base_delay=0.01)
    assert result == "recovered"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_raises_after_max_attempts():
    async def always_fails():
        raise RuntimeError("permanent failure")

    with pytest.raises(RuntimeError, match="permanent failure"):
        await async_retry(always_fails, max_attempts=3, base_delay=0.01)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def test_settings_loads_defaults():
    from app.config import get_settings
    s = get_settings()
    assert s.APP_NAME == "Enterprise Agentic Workflow Engine"
    assert s.API_V1_PREFIX == "/api/v1"
    assert s.LLM_TEMPERATURE >= 0.0
