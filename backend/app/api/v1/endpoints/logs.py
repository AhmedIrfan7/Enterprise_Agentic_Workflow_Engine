from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.execution_log import ExecutionLogListResponse
from app.utils.crud import CRUDBase
from app.models.execution_log import ExecutionLog

router = APIRouter()
log_crud = CRUDBase(ExecutionLog)


@router.get("/{workflow_id}", response_model=ExecutionLogListResponse, summary="Get execution logs for a workflow")
async def get_logs(workflow_id: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    items = await log_crud.list(db, skip=skip, limit=limit, filters={"workflow_id": workflow_id})
    return {"total": len(items), "items": items}
