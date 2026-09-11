import json
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from ..shopify.client import ShopifyGraphQLClient, ShopifyAPIError

# Pydantic Input Schemas for Strict Tool Validation

class SearchProductsInput(BaseModel):
    query: str = Field(
        default="",
        description="Search filter string (e.g. 'title:Snowboard', 'status:active', 'tag:winter', or keyword)"
    )
    limit: int = Field(default=5, ge=1, le=20, description="Max number of products to return (1-20)")

class GetProductDetailsInput(BaseModel):
    product_id: str = Field(
        description="The Shopify Global ID of the product (e.g. 'gid://shopify/Product/1234567890' or numbers only)"
    )

class CreateProductInput(BaseModel):
    title: str = Field(description="Title of the new product")
    description_html: str = Field(default="", description="HTML or plain text description")
    price: str = Field(default="0.00", description="Base price for the product variant (e.g. '49.99')")
    product_type: str = Field(default="", description="Category or product type (e.g. 'Electronics', 'Clothing')")
    tags: List[str] = Field(default_factory=list, description="List of string tags for categorization")
    vendor: str = Field(default="", description="Product vendor or brand name")
    status: str = Field(default="ACTIVE", description="Product status: 'ACTIVE', 'DRAFT', or 'ARCHIVED'")

class UpdateProductInput(BaseModel):
    product_id: str = Field(description="The Shopify Global ID of the product to update")
    title: Optional[str] = Field(default=None, description="New title")
    description_html: Optional[str] = Field(default=None, description="New HTML description")
    tags: Optional[List[str]] = Field(default=None, description="New list of tags (replaces existing)")
    status: Optional[str] = Field(default=None, description="New status ('ACTIVE', 'DRAFT', 'ARCHIVED')")
    vendor: Optional[str] = Field(default=None, description="New vendor")

class SetProductMetafieldInput(BaseModel):
    product_id: str = Field(description="The Shopify Product ID")
    namespace: str = Field(default="custom", description="Metafield namespace (default: 'custom')")
    key: str = Field(description="Metafield key name (e.g. 'promo_message', 'material', 'care_instructions')")
    value: str = Field(description="The value string to store")
    type: str = Field(default="single_line_text_field", description="Metafield type (e.g. 'single_line_text_field')")

def _normalize_gid(raw_id: str, resource_type: str = "Product") -> str:
    """Ensures the ID is formatted as a full Shopify Global ID (gid://shopify/{Type}/{id})."""
    raw = str(raw_id).strip()
    if raw.startswith("gid://shopify/"):
        return raw
    # If numbers only, build full GID
    clean_num = "".join(filter(str.isdigit, raw))
    return f"gid://shopify/{resource_type}/{clean_num}" if clean_num else raw

# LangChain Tools

@tool("shopify_search_products", args_schema=SearchProductsInput)
def search_products(query: str = "", limit: int = 5) -> str:
    """Searches and filters products in the Shopify catalog by keyword, tag, or status.
    Returns a summary list with IDs, titles, status, inventory count, and price range.
    """
    client = ShopifyGraphQLClient()
    gql_query = """
    query SearchProducts($first: Int!, $query: String) {
      products(first: $first, query: $query) {
        edges {
          node {
            id
            title
            handle
            status
            totalInventory
            tags
            vendor
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
    try:
        variables = {"first": limit, "query": query if query.strip() else None}
        data = client.execute(gql_query, variables)
        edges = data.get("products", {}).get("edges", [])
        
        if not edges:
            return f"No products found matching query: '{query}'."

        results = []
        for edge in edges:
            node = edge["node"]
            min_price = node.get("priceRangeV2", {}).get("minVariantPrice", {})
            price_str = f"{min_price.get('amount', 'N/A')} {min_price.get('currencyCode', '')}".strip()
            results.append({
                "id": node["id"],
                "title": node["title"],
                "status": node["status"],
                "price": price_str,
                "inventory": node.get("totalInventory", 0),
                "tags": node.get("tags", []),
                "vendor": node.get("vendor", "")
            })
        return json.dumps(results, indent=2)
    except ShopifyAPIError as e:
        return f"Shopify API Error searching products: {e}"
    except Exception as e:
        return f"Unexpected error searching products: {e}"

@tool("shopify_get_product_details", args_schema=GetProductDetailsInput)
def get_product_details(product_id: str) -> str:
    """Fetches comprehensive details for a specific Shopify product including variants, options, and description."""
    client = ShopifyGraphQLClient()
    normalized_id = _normalize_gid(product_id, "Product")
    
    gql_query = """
    query GetProductDetails($id: ID!) {
      product(id: $id) {
        id
        title
        description
        descriptionHtml
        handle
        status
        totalInventory
        tags
        vendor
        productType
        createdAt
        updatedAt
        variants(first: 10) {
          nodes {
            id
            title
            sku
            price
            inventoryQuantity
            availableForSale
          }
        }
        metafields(first: 10) {
          nodes {
            namespace
            key
            value
          }
        }
      }
    }
    """
    try:
        data = client.execute(gql_query, {"id": normalized_id})
        product = data.get("product")
        if not product:
            return f"Product with ID '{normalized_id}' not found in store."

        summary = {
            "id": product["id"],
            "title": product["title"],
            "status": product["status"],
            "productType": product["productType"],
            "vendor": product["vendor"],
            "totalInventory": product["totalInventory"],
            "description": product["description"][:300] if product["description"] else "",
            "tags": product["tags"],
            "variants": [
                {
                    "variant_id": v["id"],
                    "title": v["title"],
                    "sku": v["sku"],
                    "price": v["price"],
                    "inventory": v["inventoryQuantity"],
                    "available": v["availableForSale"]
                }
                for v in product.get("variants", {}).get("nodes", [])
            ],
            "metafields": [
                f"{m['namespace']}.{m['key']} = {m['value']}"
                for m in product.get("metafields", {}).get("nodes", [])
            ]
        }
        return json.dumps(summary, indent=2)
    except ShopifyAPIError as e:
        return f"Shopify API Error retrieving product details: {e}"
    except Exception as e:
        return f"Unexpected error retrieving product: {e}"

@tool("shopify_create_product", args_schema=CreateProductInput)
def create_product(
    title: str,
    description_html: str = "",
    price: str = "0.00",
    product_type: str = "",
    tags: List[str] = [],
    vendor: str = "",
    status: str = "ACTIVE"
) -> str:
    """Creates a new product in the Shopify store with title, description, pricing, and category tags."""
    client = ShopifyGraphQLClient()
    gql_mutation = """
    mutation CreateProduct($input: ProductInput!) {
      productCreate(input: $input) {
        product {
          id
          title
          handle
          status
          createdAt
          variants(first: 1) {
            nodes {
              id
              price
            }
          }
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    input_payload = {
        "title": title,
        "descriptionHtml": description_html or f"<p>{title}</p>",
        "status": status.upper(),
        "tags": tags,
    }
    if product_type:
        input_payload["productType"] = product_type
    if vendor:
        input_payload["vendor"] = vendor

    try:
        data = client.execute(gql_mutation, {"input": input_payload})
        res = data.get("productCreate", {})
        user_errors = res.get("userErrors", [])
        if user_errors:
            err_msg = "; ".join([f"{e.get('field')}: {e.get('message')}" for e in user_errors])
            return f"Shopify validation error creating product: {err_msg}"

        created = res.get("product")
        if not created:
            return "Failed to create product: empty response from Shopify."

        # If price was provided and variant exists, update variant price
        variant_nodes = created.get("variants", {}).get("nodes", [])
        if price and price != "0.00" and variant_nodes:
            variant_id = variant_nodes[0]["id"]
            price_mutation = """
            mutation UpdateVariantPrice($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
              productVariantsBulkUpdate(productId: $productId, variants: $variants) {
                productVariants { id price }
                userErrors { message }
              }
            }
            """
            client.execute(price_mutation, {
                "productId": created["id"],
                "variants": [{"id": variant_id, "price": str(price)}]
            })

        return (
            f"Successfully created product!\n"
            f"- Title: {created['title']}\n"
            f"- ID: {created['id']}\n"
            f"- Status: {created['status']}\n"
            f"- Base Price: {price}"
        )
    except ShopifyAPIError as e:
        return f"Shopify API Error creating product: {e}"
    except Exception as e:
        return f"Unexpected error creating product: {e}"

@tool("shopify_update_product", args_schema=UpdateProductInput)
def update_product(
    product_id: str,
    title: Optional[str] = None,
    description_html: Optional[str] = None,
    tags: Optional[List[str]] = None,
    status: Optional[str] = None,
    vendor: Optional[str] = None
) -> str:
    """Updates basic details of an existing product (title, description, tags, status, vendor)."""
    client = ShopifyGraphQLClient()
    normalized_id = _normalize_gid(product_id, "Product")
    
    input_payload = {"id": normalized_id}
    if title is not None:
        input_payload["title"] = title
    if description_html is not None:
        input_payload["descriptionHtml"] = description_html
    if tags is not None:
        input_payload["tags"] = tags
    if status is not None:
        input_payload["status"] = status.upper()
    if vendor is not None:
        input_payload["vendor"] = vendor

    gql_mutation = """
    mutation UpdateProduct($input: ProductInput!) {
      productUpdate(input: $input) {
        product {
          id
          title
          status
          tags
          updatedAt
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    try:
        data = client.execute(gql_mutation, {"input": input_payload})
        res = data.get("productUpdate", {})
        user_errors = res.get("userErrors", [])
        if user_errors:
            err_msg = "; ".join([f"{e.get('field')}: {e.get('message')}" for e in user_errors])
            return f"Shopify validation error updating product: {err_msg}"

        updated = res.get("product")
        return (
            f"Successfully updated product!\n"
            f"- ID: {updated['id']}\n"
            f"- Title: {updated['title']}\n"
            f"- Status: {updated['status']}\n"
            f"- Tags: {', '.join(updated.get('tags', []))}"
        )
    except ShopifyAPIError as e:
        return f"Shopify API Error updating product: {e}"
    except Exception as e:
        return f"Unexpected error updating product: {e}"

@tool("shopify_set_product_metafield", args_schema=SetProductMetafieldInput)
def set_product_metafield(
    product_id: str,
    key: str,
    value: str,
    namespace: str = "custom",
    type: str = "single_line_text_field"
) -> str:
    """Attaches a custom metafield (custom attribute or message) to a product."""
    client = ShopifyGraphQLClient()
    normalized_id = _normalize_gid(product_id, "Product")
    
    gql_mutation = """
    mutation SetMetafields($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields {
          id
          namespace
          key
          value
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    metafield_input = [{
        "ownerId": normalized_id,
        "namespace": namespace,
        "key": key,
        "value": value,
        "type": type
    }]
    try:
        data = client.execute(gql_mutation, {"metafields": metafield_input})
        res = data.get("metafieldsSet", {})
        user_errors = res.get("userErrors", [])
        if user_errors:
            err_msg = "; ".join([f"{e.get('message')}" for e in user_errors])
            return f"Shopify error setting metafield: {err_msg}"

        mf = res.get("metafields", [])[0]
        return f"Successfully set metafield '{mf['namespace']}.{mf['key']}' to '{mf['value']}' on product {normalized_id}."
    except ShopifyAPIError as e:
        return f"Shopify API Error setting metafield: {e}"
    except Exception as e:
        return f"Unexpected error setting metafield: {e}"
