from __future__ import annotations
import logging
import os
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.vectorstores import VectorStore

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_embeddings: Optional[HuggingFaceEmbeddings] = None
_vector_store: Optional[FAISS] = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        logger.info("Loading embedding model (all-MiniLM-L6-v2)…")
        _embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def get_vector_store() -> Optional[FAISS]:
    global _vector_store
    if _vector_store is not None:
        return _vector_store
    path = settings.VECTOR_STORE_PATH
    if os.path.exists(os.path.join(path, "index.faiss")):
        try:
            _vector_store = FAISS.load_local(path, _get_embeddings(), allow_dangerous_deserialization=True)
            logger.info("FAISS index loaded from %s", path)
        except Exception as e:
            logger.error("Failed to load FAISS index: %s", e)
    return _vector_store


def add_documents(docs: list) -> None:
    global _vector_store
    emb = _get_embeddings()
    if _vector_store is None:
        _vector_store = FAISS.from_documents(docs, emb)
    else:
        _vector_store.add_documents(docs)
    os.makedirs(settings.VECTOR_STORE_PATH, exist_ok=True)
    _vector_store.save_local(settings.VECTOR_STORE_PATH)
    logger.info("FAISS index saved: %d documents added", len(docs))
