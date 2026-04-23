import json
import logging
from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.workflow import WorkflowCreate, WorkflowResponse, WorkflowListResponse
from app.models.workflow import WorkflowStatus
from app.utils.crud import CRUDBase
from app.models.workflow import Workflow
from app.utils.exceptions import NotFoundError

router = APIRouter()
logger = logging.getLogger(__name__)
workflow_crud = CRUDBase(Workflow)


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED,
             summary="Create and enqueue an agentic workflow")
async def create_workflow(
    payload: WorkflowCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    workflow = await workflow_crud.create(db, obj_in={
        "title": payload.title,
        "goal": payload.goal,
        "tools_selected": json.dumps(payload.tools_selected),
        "llm_provider": payload.llm_provider,
        "llm_model": payload.llm_model,
        "status": WorkflowStatus.PENDING,
    })
    # Kick off execution asynchronously
    from app.services.workflow_service import execute_workflow_bg
    background_tasks.add_task(execute_workflow_bg, workflow.id)
    logger.info("Workflow created: %s (%s)", workflow.id, workflow.title)
    return workflow


@router.get("", response_model=WorkflowListResponse, summary="List all workflows")
async def list_workflows(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    items = await workflow_crud.list(db, skip=skip, limit=limit)
    return {"total": len(items), "items": items}


@router.get("/{workflow_id}", response_model=WorkflowResponse, summary="Get workflow by ID")
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    workflow = await workflow_crud.get(db, workflow_id)
    if not workflow:
        raise NotFoundError("Workflow", workflow_id)
    return workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a workflow")
async def delete_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await workflow_crud.delete(db, record_id=workflow_id)
    if not deleted:
        raise NotFoundError("Workflow", workflow_id)
