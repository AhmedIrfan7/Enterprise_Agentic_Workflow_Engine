import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.workflow_service import execute_workflow_bg
from app.database import AsyncSessionLocal
from app.utils.crud import CRUDBase
from app.models.workflow import Workflow, WorkflowStatus

router = APIRouter()
logger = logging.getLogger(__name__)
workflow_crud = CRUDBase(Workflow)


@router.websocket("/ws/execution/{workflow_id}")
async def execution_websocket(websocket: WebSocket, workflow_id: str):
    """
    Real-time execution stream for a workflow.
    Connect immediately after POSTing to /workflows.
    Receives typed JSON events:
      { type, workflow_id, timestamp, data }
    Event types: token | tool_start | tool_end | tool_error | agent_finish | error | status
    """
    await websocket.accept()
    logger.info("WebSocket connected for workflow %s", workflow_id)

    async with AsyncSessionLocal() as db:
        workflow = await workflow_crud.get(db, workflow_id)

    if workflow is None:
        await websocket.send_text(json.dumps({
            "type": "error",
            "workflow_id": workflow_id,
            "data": {"error": f"Workflow {workflow_id} not found."},
        }))
        await websocket.close(code=4004)
        return

    if workflow.status == WorkflowStatus.COMPLETED:
        await websocket.send_text(json.dumps({
            "type": "agent_finish",
            "workflow_id": workflow_id,
            "data": {"output": workflow.result or ""},
        }))
        await websocket.close()
        return

    await websocket.send_text(json.dumps({
        "type": "status",
        "workflow_id": workflow_id,
        "data": {"status": "connected", "message": "Execution stream open. Agent starting…"},
    }))

    try:
        await execute_workflow_bg(workflow_id, websocket=websocket)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for workflow %s", workflow_id)
    except Exception as exc:
        logger.exception("WebSocket execution error for %s: %s", workflow_id, exc)
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "workflow_id": workflow_id,
                "data": {"error": str(exc)},
            }))
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
