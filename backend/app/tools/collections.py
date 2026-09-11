import json
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from ..shopify.client import ShopifyGraphQLClient, ShopifyAPIError
from .products import _normalize_gid

class ListCollectionsInput(BaseModel):
    limit: int = Field(default=10, ge=1, le=50, description="Max collections to list (1-50)")

class CreateCollectionInput(BaseModel):
    title: str = Field(description="Title of the new collection")
    description_html: str = Field(default="", description="HTML or plain text description of the collection")
    product_ids: List[str] = Field(default_factory=list, description="Optional list of product IDs to add into this collection")

@tool("shopify_list_collections", args_schema=ListCollectionsInput)
def list_collections(limit: int = 10) -> str:
    """Lists store collections (categories) with IDs, titles, handles, and product counts."""
    client = ShopifyGraphQLClient()
    gql_query = """
    query ListCollections($first: Int!) {
      collections(first: $first) {
        edges {
          node {
            id
            title
            handle
            productsCount {
              count
            }
            updatedAt
          }
        }
      }
    }
    """
    try:
        data = client.execute(gql_query, {"first": limit})
        edges = data.get("collections", {}).get("edges", [])
        if not edges:
            return "No collections found in this store."

        results = [
            {
                "id": e["node"]["id"],
                "title": e["node"]["title"],
                "handle": e["node"]["handle"],
                "products_count": e["node"].get("productsCount", {}).get("count", 0),
                "updated_at": e["node"]["updatedAt"]
            }
            for e in edges
        ]
        return json.dumps(results, indent=2)
    except ShopifyAPIError as e:
        return f"Shopify API Error listing collections: {e}"
    except Exception as e:
        return f"Unexpected error listing collections: {e}"

@tool("shopify_create_collection", args_schema=CreateCollectionInput)
def create_collection(title: str, description_html: str = "", product_ids: List[str] = []) -> str:
    """Creates a new custom product collection (category) and optionally adds products to it."""
    client = ShopifyGraphQLClient()
    gql_mutation = """
    mutation CreateCollection($input: CollectionInput!) {
      collectionCreate(input: $input) {
        collection {
          id
          title
          handle
          updatedAt
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    normalized_products = [_normalize_gid(pid, "Product") for pid in product_ids]
    payload = {
        "title": title,
        "descriptionHtml": description_html or f"<p>{title}</p>",
        "products": normalized_products
    }
    try:
        data = client.execute(gql_mutation, {"input": payload})
        res = data.get("collectionCreate", {})
        user_errors = res.get("userErrors", [])
        if user_errors:
            err_msg = "; ".join([f"{e.get('message')}" for e in user_errors])
            return f"Shopify error creating collection: {err_msg}"

        col = res.get("collection")
        return (
            f"Successfully created collection!\n"
            f"- Title: {col['title']}\n"
            f"- ID: {col['id']}\n"
            f"- Handle: {col['handle']}\n"
            f"- Associated Products: {len(normalized_products)}"
        )
    except ShopifyAPIError as e:
        return f"Shopify API Error creating collection: {e}"
    except Exception as e:
        return f"Unexpected error creating collection: {e}"
