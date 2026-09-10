# Phase 2: Shopify GraphQL LangChain Tool Library

## Goal
Build a suite of strongly-typed, schema-validated LangChain tools (`@tool`) wrapping the Shopify Admin GraphQL API. These tools allow LLMs to read data and perform actions with precision.

---

## 1. Tool Categories

### A. Catalog & Product Tools
1. `search_products(query: str, limit: int = 5)`
   - Full-text search with status, tags, and title filtering.
2. `get_product_details(product_id: str)`
   - Detailed product info, variants, pricing, metafields, and inventory count.
3. `create_product(title: str, description: str, price: float, product_type: str, tags: list[str])`
   - Creates a product and initial variant with pricing.
4. `update_product(product_id: str, fields: dict)`
   - Updates title, description, price, tags, or status.
5. `manage_product_metafields(product_id: str, key: str, value: str, namespace: str = "custom")`
   - Attaches custom promotional messages, specifications, or attributes.

### B. Inventory & Logistics Tools
1. `check_inventory_levels(product_variant_id: str)`
   - Returns current stock across store locations.
2. `adjust_inventory(inventory_item_id: str, location_id: str, delta: int)`
   - Modifies available quantities up or down.

### C. Collections & Marketing Tools
1. `list_collections(limit: int = 10)`
   - Fetches smart and custom collections.
2. `create_collection(title: str, description: str, product_ids: list[str])`
   - Creates a curated collection and associates products.

### D. Orders & Customer Service Tools
1. `get_order_status(order_id: str)`
   - Checks fulfillment status, tracking numbers, line items, and payment state.
2. `create_draft_order(line_items: list[dict], customer_email: str, note: str = "")`
   - Creates a customizable draft invoice with custom notes and discounts.
3. `search_customer(email_or_phone: str)`
   - Looks up customer lifetime spend, previous orders, and profile.

---

## 2. Pydantic Tool Schema Pattern Example
```python
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class CreateProductInput(BaseModel):
    title: str = Field(description="The marketing title of the product")
    description_html: str = Field(description="HTML formatted product description")
    price: str = Field(description="Decimal price string, e.g. '29.99'")
    tags: list[str] = Field(default=[], description="Tags for categorization and search")
    product_type: str = Field(default="", description="Product category/type")

@tool("create_shopify_product", args_schema=CreateProductInput)
def create_shopify_product(title: str, description_html: str, price: str, tags: list[str] = [], product_type: str = "") -> str:
    """Creates a new active product in the Shopify catalog with title, pricing, and tags."""
    # Executes GraphQL mutation productCreate
    ...
```

---

## 3. Error Handling & Guardrails
- **Input Validation**: Pydantic models prevent malformed data from reaching Shopify.
- **Safe Response Formatting**: Only essential fields are returned to the LLM context to avoid token bloat.
- **User Error Extraction**: GraphQL `userErrors` are parsed and converted to clear human-readable explanations.
