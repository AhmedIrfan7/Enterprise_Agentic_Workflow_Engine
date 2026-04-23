import os
import shutil
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

ALLOWED_TYPES = {
    "application/pdf", "text/plain", "text/csv",
    "application/json",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED, summary="Upload document to Vector Store pipeline")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, TXT, CSV, JSON, DOCX.",
        )
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    dest_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    size = 0
    with open(dest_path, "wb") as f:
        while chunk := await file.read(1024 * 64):
            size += len(chunk)
            if size > max_bytes:
                os.remove(dest_path)
                raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit.")
            f.write(chunk)

    from app.services.vector_service import ingest_document_bg
    background_tasks.add_task(ingest_document_bg, dest_path, file.filename, file.content_type)
    logger.info("Document queued for ingestion: %s (%d bytes)", file.filename, size)
    return {"message": "Document accepted for ingestion.", "filename": file.filename, "size_bytes": size}


@router.get("/list", summary="List uploaded documents")
async def list_documents():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    files = []
    for fname in os.listdir(settings.UPLOAD_DIR):
        fpath = os.path.join(settings.UPLOAD_DIR, fname)
        files.append({"filename": fname, "size_bytes": os.path.getsize(fpath)})
    return {"total": len(files), "items": files}


@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a document")
async def delete_document(filename: str):
    fpath = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail="File not found.")
    os.remove(fpath)
