"""Knowledge Base & Product Ingestion Pipeline."""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any

from ..shopify.client import ShopifyGraphQLClient
from .vector_store import vector_store_manager

logger = logging.getLogger(__name__)

def ingest_shopify_catalog(limit: int = 100) -> int:
    """Fetches all active products from Shopify GraphQL and indexes them into ChromaDB."""
    client = ShopifyGraphQLClient()
    collection = vector_store_manager.get_products_collection()

    gql_query = """
    query IngestProducts($first: Int!) {
      products(first: $first) {
        edges {
          node {
            id
            title
            handle
            description
            productType
            vendor
            tags
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
      }
    }
    """
    data = client.execute(gql_query, {"first": limit})
    edges = data.get("products", {}).get("edges", [])

    if not edges:
        logger.warning("No products found to index from Shopify.")
        return 0

    documents = []
    metadatas = []
    ids = []

    for edge in edges:
        p = edge["node"]
        price_info = p.get("priceRangeV2", {}).get("minVariantPrice", {})
        price_str = f"{price_info.get('amount', '0.00')} {price_info.get('currencyCode', '')}".strip()
        tags_str = ", ".join(p.get("tags", []))

        # Build a rich semantic representation of the product
        doc_text = (
            f"Product Title: {p['title']}\n"
            f"Category/Type: {p.get('productType', 'General')}\n"
            f"Vendor/Brand: {p.get('vendor', 'Unknown')}\n"
            f"Tags: {tags_str}\n"
            f"Base Price: {price_str}\n"
            f"Description: {p.get('description', '') or 'No detailed description available.'}"
        )

        documents.append(doc_text)
        metadatas.append({
            "product_id": p["id"],
            "title": p["title"],
            "handle": p.get("handle", ""),
            "vendor": p.get("vendor", ""),
            "price": str(price_info.get("amount", "0.00")),
            "currency": str(price_info.get("currencyCode", "")),
            "status": p.get("status", "ACTIVE")
        })
        ids.append(p["id"])

    # Upsert into ChromaDB vector collection
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    logger.info(f"Successfully ingested {len(ids)} products into ChromaDB vector store.")
    return len(ids)

def ingest_markdown_knowledge(knowledge_dir: Path) -> int:
    """Ingests store policy and FAQ markdown files into the knowledge vector store."""
    collection = vector_store_manager.get_knowledge_collection()
    if not knowledge_dir.exists():
        logger.warning(f"Knowledge directory '{knowledge_dir}' does not exist.")
        return 0

    documents = []
    metadatas = []
    ids = []

    doc_counter = 0

    for file_path in knowledge_dir.glob("*.md"):
        content = file_path.read_text(encoding="utf-8")
        filename = file_path.name

        # Split markdown into sections by header level 2 (## )
        sections = re.split(r"\n(?=##\s+)", content)

        for idx, section in enumerate(sections):
            clean_section = section.strip()
            if not clean_section:
                continue

            # Extract heading if available
            lines = clean_section.split("\n")
            heading = lines[0].replace("#", "").strip() if lines else "General"

            doc_id = f"{file_path.stem}_{idx}"
            documents.append(clean_section)
            metadatas.append({
                "source_file": filename,
                "heading": heading,
                "doc_type": "store_policy" if "policy" in filename else "faq"
            })
            ids.append(doc_id)
            doc_counter += 1

    if ids:
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    logger.info(f"Successfully ingested {len(ids)} knowledge chunks into ChromaDB.")
    return len(ids)
