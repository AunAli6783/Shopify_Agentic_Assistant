"""Shopify LangChain Tools Suite.

This module exposes strongly-typed, schema-validated LangChain tools
wrapping Shopify Admin GraphQL API for products, inventory, collections, and orders.
"""

from .products import (
    search_products,
    get_product_details,
    create_product,
    update_product,
    set_product_metafield,
)
from .inventory import (
    check_inventory_levels,
    adjust_inventory,
)
from .collections import (
    list_collections,
    create_collection,
)
from .orders import (
    get_order_details,
    create_draft_order,
    search_customer,
)

# Product & Catalog Tools
CATALOG_TOOLS = [
    search_products,
    get_product_details,
    create_product,
    update_product,
    set_product_metafield,
]

# Inventory & Stock Tools
INVENTORY_TOOLS = [
    check_inventory_levels,
    adjust_inventory,
]

# Marketing & Collection Tools
COLLECTION_TOOLS = [
    list_collections,
    create_collection,
]

# Order & Customer Tools
ORDER_TOOLS = [
    get_order_details,
    create_draft_order,
    search_customer,
]

# Master list of all tools for LangGraph agents
ALL_SHOPIFY_TOOLS = [
    *CATALOG_TOOLS,
    *INVENTORY_TOOLS,
    *COLLECTION_TOOLS,
    *ORDER_TOOLS,
]

__all__ = [
    "search_products",
    "get_product_details",
    "create_product",
    "update_product",
    "set_product_metafield",
    "check_inventory_levels",
    "adjust_inventory",
    "list_collections",
    "create_collection",
    "get_order_details",
    "create_draft_order",
    "search_customer",
    "CATALOG_TOOLS",
    "INVENTORY_TOOLS",
    "COLLECTION_TOOLS",
    "ORDER_TOOLS",
    "ALL_SHOPIFY_TOOLS",
]
