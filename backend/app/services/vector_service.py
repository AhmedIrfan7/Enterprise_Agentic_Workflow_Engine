from __future__ import annotations
import logging
import os
from typing import List

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    JSONLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.core.memory.vector_store import add_documents

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 1000
_CHUNK_OVERLAP = 150


def _load_documents(file_path: str, content_type: str) -> List[Document]:
    loaders = {
        "application/pdf": lambda: PyPDFLoader(file_path).load(),
        "text/plain": lambda: TextLoader(file_path, encoding="utf-8").load(),
        "text/csv": lambda: CSVLoader(file_path).load(),
        "application/json": lambda: JSONLoader(file_path, jq_schema=".", text_content=False).load(),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            lambda: UnstructuredWordDocumentLoader(file_path).load(),
    }
    loader_fn = loaders.get(content_type)
    if loader_fn is None:
        raise ValueError(f"Unsupported content type for ingestion: {content_type}")
    return loader_fn()


def _chunk_documents(docs: List[Document], source: str) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(docs)
    for chunk in chunks:
        chunk.metadata["source"] = source
    return chunks


def ingest_document_bg(file_path: str, filename: str, content_type: str) -> None:
    """Background task: load → chunk → embed → store in FAISS."""
    logger.info("Ingesting document: %s (%s)", filename, content_type)
    try:
        raw_docs = _load_documents(file_path, content_type)
        chunks = _chunk_documents(raw_docs, source=filename)
        add_documents(chunks)
        logger.info("Ingestion complete: %s — %d chunks indexed", filename, len(chunks))
    except Exception as e:
        logger.error("Document ingestion failed for %s: %s", filename, e)
