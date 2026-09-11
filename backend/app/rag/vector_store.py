"""ChromaDB Persistent Vector Store Manager."""

import os
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from ..config import settings
from .embeddings import get_chroma_embedding_function

PRODUCTS_COLLECTION_NAME = "shopify_products"
KNOWLEDGE_COLLECTION_NAME = "shopify_knowledge"

class VectorStoreManager:
    """Manages persistent ChromaDB vector storage and semantic collections."""

    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or settings.chroma_persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.embedding_function = get_chroma_embedding_function()

    def get_products_collection(self) -> chromadb.Collection:
        """Retrieves or creates the collection for product catalog embeddings."""
        return self.client.get_or_create_collection(
            name=PRODUCTS_COLLECTION_NAME,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )

    def get_knowledge_collection(self) -> chromadb.Collection:
        """Retrieves or creates the collection for store policies, FAQs, and documentation."""
        return self.client.get_or_create_collection(
            name=KNOWLEDGE_COLLECTION_NAME,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )

    def reset_collection(self, name: str):
        """Empties a collection for fresh re-indexing."""
        try:
            self.client.delete_collection(name)
        except Exception:
            pass

# Global vector store manager instance
vector_store_manager = VectorStoreManager()
