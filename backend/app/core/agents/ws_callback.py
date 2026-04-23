from __future__ import annotations
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult
from fastapi import WebSocket

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class WebSocketStreamingCallback(AsyncCallbackHandler):
    """
    Forwards every LangChain event to a FastAPI WebSocket as a typed JSON event.
    Event schema: { type, timestamp, data }
    Types: thinking | token | tool_start | tool_end | tool_error | agent_finish | error
    """

    def __init__(self, websocket: WebSocket, workflow_id: str) -> None:
        super().__init__()
        self.websocket = websocket
        self.workflow_id = workflow_id
        self._thinking_buffer: list[str] = []

    async def _send(self, event_type: str, data: dict[str, Any]) -> None:
        payload = json.dumps({
            "type": event_type,
            "workflow_id": self.workflow_id,
            "timestamp": _now_iso(),
            "data": data,
        })
        try:
            await self.websocket.send_text(payload)
        except Exception as e:
            logger.warning("WebSocket send failed: %s", e)

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self._thinking_buffer.append(token)
        await self._send("token", {"token": token})

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self._thinking_buffer.clear()

    async def on_tool_start(
        self, serialized: dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        tool_name = serialized.get("name", "unknown_tool")
        await self._send("tool_start", {"tool": tool_name, "input": input_str[:500]})

    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        await self._send("tool_end", {"output": output[:1000]})

    async def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        await self._send("tool_error", {"error": str(error)})

    async def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        output = finish.return_values.get("output", "") if hasattr(finish, "return_values") else str(finish)
        await self._send("agent_finish", {"output": output})

    async def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        await self._send("error", {"error": str(error)})
