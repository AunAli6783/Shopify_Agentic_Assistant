"""LangChain Tools for Hybrid RAG Product Discovery & Store Policy Retrieval."""

import json
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from ..rag.retriever import hybrid_retriever

class SemanticSearchInput(BaseModel):
    query: str = Field(
        description="Natural language description of what the user wants (e.g. 'warm winter gear for skiing', 'gifts under 5000 PKR', 'waterproof boots')"
    )
    limit: int = Field(default=5, ge=1, le=10, description="Max products to return")
    in_stock_only: bool = Field(default=False, description="If True, filters out items that are currently out of stock")

class PolicySearchInput(BaseModel):
    query: str = Field(
        description="Customer question regarding store policies (e.g. 'How long do refunds take?', 'Do you ship to the US?', 'Can I return an item after 2 weeks?')"
    )
    limit: int = Field(default=3, ge=1, le=5, description="Max relevant sections to return")

@tool("shopify_semantic_product_search", args_schema=SemanticSearchInput)
def semantic_product_search(query: str, limit: int = 5, in_stock_only: bool = False) -> str:
    """Performs semantic vector search across the product catalog using natural language,
    returning matching products along with real-time stock and price verification.
    Use this when the user is asking conceptual questions ('warm clothes', 'gifts', 'outdoor sports')
    rather than searching for exact titles.
    """
    try:
        results = hybrid_retriever.semantic_search_products(
            query=query,
            top_k=limit,
            fetch_live_stock=True
        )

        if not results:
            return f"No products found semantically matching: '{query}'."

        if in_stock_only:
            results = [r for r in results if r.get("is_in_stock", True)]
            if not results:
                return f"Matching products were found for '{query}', but none are currently in stock."

        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error performing semantic product search: {e}"

@tool("shopify_search_store_policies", args_schema=PolicySearchInput)
def search_store_policies(query: str, limit: int = 3) -> str:
    """Searches official store policies, shipping rates, return windows, warranties, and FAQs.
    Use this tool whenever a customer asks about store procedures, delivery times, or return rules.
    """
    try:
        chunks = hybrid_retriever.search_store_policies(query=query, top_k=limit)
        if not chunks:
            return f"No store policies found matching query: '{query}'."

        formatted = []
        for c in chunks:
            formatted.append({
                "topic": c.get("heading", "Policy Section"),
                "source": c.get("source_file"),
                "content": c.get("content")
            })

        return json.dumps(formatted, indent=2)
    except Exception as e:
        return f"Error retrieving store policies: {e}"
