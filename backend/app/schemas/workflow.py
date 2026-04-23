from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.workflow import WorkflowStatus


class WorkflowCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Short human-readable title")
    goal: str = Field(..., min_length=10, description="Detailed goal for the agent to accomplish")
    tools_selected: List[str] = Field(default_factory=list, description="Tool IDs to enable")
    llm_provider: str = Field(default="openai")
    llm_model: str = Field(default="gpt-4o-mini")

    model_config = {"json_schema_extra": {"example": {
        "title": "Market Research Report",
        "goal": "Research the top 5 AI startups in 2024 and produce a structured summary with funding data.",
        "tools_selected": ["web_search", "file_write"],
        "llm_provider": "openai",
        "llm_model": "gpt-4o-mini",
    }}}


class WorkflowResponse(BaseModel):
    id: str
    title: str
    goal: str
    tools_selected: str
    llm_provider: str
    llm_model: str
    status: WorkflowStatus
    result: Optional[str]
    token_usage: int
    estimated_cost_usd: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowListResponse(BaseModel):
    total: int
    items: List[WorkflowResponse]
