from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.execution_log import LogLevel


class ExecutionLogResponse(BaseModel):
    id: str
    workflow_id: str
    event_type: str
    level: LogLevel
    message: str
    metadata_json: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ExecutionLogListResponse(BaseModel):
    total: int
    items: List[ExecutionLogResponse]
