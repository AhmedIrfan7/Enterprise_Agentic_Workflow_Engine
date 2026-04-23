from __future__ import annotations
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models.workflow import WorkflowStatus
from app.models.execution_log import ExecutionLog, LogLevel
from app.utils.crud import CRUDBase
from app.models.workflow import Workflow
from app.core.agents.base_agent import EnterpriseAgent
from app.core.agents.token_tracker import TokenUsageTracker
from app.core.tools.registry import get_tools
from app.utils.retry import async_retry

logger = logging.getLogger(__name__)
settings = get_settings()
workflow_crud = CRUDBase(Workflow)
log_crud = CRUDBase(ExecutionLog)


async def _log_event(
    workflow_id: str,
    event_type: str,
    message: str,
    level: LogLevel = LogLevel.INFO,
    metadata: Optional[dict] = None,
) -> None:
    async with AsyncSessionLocal() as db:
        await log_crud.create(db, obj_in={
            "workflow_id": workflow_id,
            "event_type": event_type,
            "level": level,
            "message": message,
            "metadata_json": json.dumps(metadata) if metadata else None,
        })


async def execute_workflow_bg(workflow_id: str, websocket=None) -> None:
    """
    Core execution loop. Runs as a background task (POST /workflows)
    or directly from the WebSocket endpoint for real-time streaming.
    """
    async with AsyncSessionLocal() as db:
        workflow = await workflow_crud.get(db, workflow_id)
        if not workflow:
            logger.error("Workflow %s not found — aborting execution.", workflow_id)
            return

        tool_ids: list[str] = json.loads(workflow.tools_selected or "[]")
        tools = get_tools(tool_ids)

        await workflow_crud.update(db, record_id=workflow_id, obj_in={"status": WorkflowStatus.RUNNING})

    await _log_event(workflow_id, "start", f"Starting execution for: {workflow.goal[:120]}")

    callbacks = []
    token_tracker = TokenUsageTracker(model=workflow.llm_model)
    callbacks.append(token_tracker)

    if websocket is not None:
        from app.core.agents.ws_callback import WebSocketStreamingCallback
        callbacks.append(WebSocketStreamingCallback(websocket, workflow_id))

    agent = EnterpriseAgent(
        workflow_id=workflow_id,
        tools=tools,
        llm_provider=workflow.llm_provider,
        llm_model=workflow.llm_model,
        callbacks=callbacks,
    )

    try:
        result = await async_retry(
            agent.arun,
            workflow.goal,
            max_attempts=3,
            base_delay=2.0,
            retryable_exceptions=(Exception,),
        )
        output = result.get("output", str(result))
        usage = token_tracker.summary()

        async with AsyncSessionLocal() as db:
            await workflow_crud.update(db, record_id=workflow_id, obj_in={
                "status": WorkflowStatus.COMPLETED,
                "result": output,
                "token_usage": usage["total_tokens"],
                "estimated_cost_usd": usage["estimated_cost_usd"],
                "updated_at": datetime.now(timezone.utc),
            })

        await _log_event(
            workflow_id, "complete",
            "Workflow completed successfully.",
            metadata={"token_usage": usage},
        )
        logger.info("Workflow %s completed. Tokens: %d, Cost: $%.6f", workflow_id, usage["total_tokens"], usage["estimated_cost_usd"])

    except Exception as exc:
        logger.exception("Workflow %s failed: %s", workflow_id, exc)
        async with AsyncSessionLocal() as db:
            await workflow_crud.update(db, record_id=workflow_id, obj_in={
                "status": WorkflowStatus.FAILED,
                "updated_at": datetime.now(timezone.utc),
            })
        await _log_event(workflow_id, "error", str(exc), level=LogLevel.ERROR)
