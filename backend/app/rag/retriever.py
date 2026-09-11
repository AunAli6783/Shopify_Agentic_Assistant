"""Hybrid RAG Retriever combining vector search with real-time Shopify GraphQL data."""

import json
import logging
from typing import List, Dict, Any, Optional

from ..shopify.client import ShopifyGraphQLClient, ShopifyAPIError
from .vector_store import vector_store_manager

logger = logging.getLogger(__name__)

class HybridRetriever:
    """Combines dense semantic vector retrieval with real-time Shopify GraphQL inventory & pricing."""

    def __init__(self):
        self.vector_mgr = vector_store_manager
        self.shopify_client = ShopifyGraphQLClient()

    def semantic_search_products(
        self,
        query: str,
        top_k: int = 5,
        fetch_live_stock: bool = True
    ) -> List[Dict[str, Any]]:
        """Finds products semantically matching a natural language prompt,
        then fetches real-time inventory and pricing from Shopify GraphQL.
        """
        collection = self.vector_mgr.get_products_collection()
        
        # 1. Semantic Vector Search in ChromaDB
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        ids = results.get("ids", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not ids:
            return []

        products_found = []
        for i in range(len(ids)):
            meta = metadatas[i]
            # Convert cosine distance to approximate similarity score (0-1)
            dist = distances[i] if i < len(distances) else 1.0
            similarity = round(max(0.0, 1.0 - dist), 3)

            products_found.append({
                "product_id": ids[i],
                "title": meta.get("title"),
                "handle": meta.get("handle"),
                "vendor": meta.get("vendor"),
                "indexed_price": f"{meta.get('price')} {meta.get('currency', '')}".strip(),
                "similarity_score": similarity
            })

        # 2. Hybrid Step: Live inventory & price verification from Shopify GraphQL
        if fetch_live_stock and products_found:
            for item in products_found:
                try:
                    gql = """
                    query GetLiveProduct($id: ID!) {
                      product(id: $id) {
                        status
                        totalInventory
                        priceRangeV2 {
                          minVariantPrice {
                            amount
                            currencyCode
                          }
                        }
                      }
                    }
                    """
                    data = self.shopify_client.execute(gql, {"id": item["product_id"]})
                    live_prod = data.get("product")
                    if live_prod:
                        price_obj = live_prod.get("priceRangeV2", {}).get("minVariantPrice", {})
                        item["live_status"] = live_prod.get("status")
                        item["live_inventory"] = live_prod.get("totalInventory", 0)
                        item["live_price"] = f"{price_obj.get('amount', 'N/A')} {price_obj.get('currencyCode', '')}".strip()
                        item["is_in_stock"] = (live_prod.get("totalInventory", 0) > 0)
                except Exception as e:
                    logger.warning(f"Failed to fetch live stock for {item['product_id']}: {e}")

        return products_found

    def search_store_policies(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Performs semantic search across store policies, return windows, shipping rates, and FAQs."""
        collection = self.vector_mgr.get_knowledge_collection()

        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        policy_chunks = []
        for i in range(len(docs)):
            dist = distances[i] if i < len(distances) else 1.0
            similarity = round(max(0.0, 1.0 - dist), 3)

            policy_chunks.append({
                "content": docs[i],
                "heading": metas[i].get("heading"),
                "source_file": metas[i].get("source_file"),
                "doc_type": metas[i].get("doc_type"),
                "relevance_score": similarity
            })

        return policy_chunks

# Global retriever instance
hybrid_retriever = HybridRetriever()
