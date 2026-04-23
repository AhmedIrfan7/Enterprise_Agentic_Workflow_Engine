from fastapi import APIRouter
from app.api.v1.endpoints import health, workflows, documents, logs, tools
from app.api.v1.endpoints.websocket import router as ws_router

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(logs.router, prefix="/logs", tags=["execution-logs"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
