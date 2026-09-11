"""Embedding factory module with automatic fallback to local ONNX embeddings."""

import os
import logging
from typing import Any
import chromadb.utils.embedding_functions as ef
from ..config import settings

logger = logging.getLogger(__name__)

def get_chroma_embedding_function() -> Any:
    """Returns an embedding function for ChromaDB.
    
    Priority:
    1. OpenAI Embeddings (if OPENAI_API_KEY is configured)
    2. Google Gemini Embeddings (if GEMINI_API_KEY is configured)
    3. ChromaDB local DefaultEmbeddingFunction (all-MiniLM-L6-v2 ONNX, free & offline)
    """
    if settings.openai_api_key and settings.openai_api_key.startswith("sk-"):
        try:
            logger.info("Using OpenAI Embeddings (text-embedding-3-small)...")
            return ef.OpenAIEmbeddingFunction(
                api_key=settings.openai_api_key,
                model_name="text-embedding-3-small"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI Embeddings: {e}. Falling back...")

    if settings.gemini_api_key and settings.gemini_api_key.startswith("AIza"):
        try:
            logger.info("Using Google Gemini Embeddings...")
            return ef.GoogleGenerativeAiEmbeddingFunction(
                api_key=settings.gemini_api_key
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini Embeddings: {e}. Falling back...")

    # Default: Local ONNX all-MiniLM-L6-v2 (Runs 100% offline, free, zero cost)
    logger.info("Using ChromaDB default local ONNX embedding function (all-MiniLM-L6-v2)...")
    return ef.DefaultEmbeddingFunction()
