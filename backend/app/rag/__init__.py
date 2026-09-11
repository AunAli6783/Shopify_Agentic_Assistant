"""RAG (Retrieval-Augmented Generation) Package for Shopify Store Intelligence."""

from .vector_store import vector_store_manager, PRODUCTS_COLLECTION_NAME, KNOWLEDGE_COLLECTION_NAME
from .ingestion import ingest_shopify_catalog, ingest_markdown_knowledge
from .retriever import hybrid_retriever, HybridRetriever

__all__ = [
    "vector_store_manager",
    "PRODUCTS_COLLECTION_NAME",
    "KNOWLEDGE_COLLECTION_NAME",
    "ingest_shopify_catalog",
    "ingest_markdown_knowledge",
    "hybrid_retriever",
    "HybridRetriever",
]
