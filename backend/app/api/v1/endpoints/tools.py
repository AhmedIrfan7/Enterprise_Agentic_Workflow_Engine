from fastapi import APIRouter
from app.core.tools.registry import list_available_tools

router = APIRouter()


@router.get("", summary="List all available agent tools")
async def list_tools():
    """Returns metadata for all tools the agent can use, suitable for the Workflow Builder UI."""
    tools = list_available_tools()
    return {"total": len(tools), "items": tools}
