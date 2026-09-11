import json
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from ..shopify.client import ShopifyGraphQLClient, ShopifyAPIError
from .products import _normalize_gid

class CheckInventoryInput(BaseModel):
    product_id: str = Field(description="The Shopify Product ID to check stock for")

class AdjustInventoryInput(BaseModel):
    inventory_item_id: str = Field(description="Shopify InventoryItem ID (e.g. 'gid://shopify/InventoryItem/12345')")
    location_id: str = Field(description="Shopify Location ID where inventory is stored (e.g. 'gid://shopify/Location/12345')")
    available_delta: int = Field(description="Quantity to add (positive number) or remove (negative number)")

@tool("shopify_check_inventory_levels", args_schema=CheckInventoryInput)
def check_inventory_levels(product_id: str) -> str:
    """Checks the inventory quantities across all variants and store locations for a given product."""
    client = ShopifyGraphQLClient()
    normalized_id = _normalize_gid(product_id, "Product")
    
    gql_query = """
    query GetInventoryLevels($id: ID!) {
      product(id: $id) {
        id
        title
        totalInventory
        variants(first: 10) {
          nodes {
            id
            title
            sku
            inventoryQuantity
            inventoryItem {
              id
              inventoryLevels(first: 5) {
                nodes {
                  location {
                    id
                    name
                  }
                  quantities(names: ["available", "on_hand"]) {
                    name
                    quantity
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    try:
        data = client.execute(gql_query, {"id": normalized_id})
        product = data.get("product")
        if not product:
            return f"Product '{normalized_id}' not found."

        summary = {
            "product_title": product["title"],
            "total_inventory": product["totalInventory"],
            "variants": []
        }
        for v in product.get("variants", {}).get("nodes", []):
            inv_item = v.get("inventoryItem", {})
            locations = []
            for lvl in inv_item.get("inventoryLevels", {}).get("nodes", []):
                loc_name = lvl.get("location", {}).get("name", "Unknown Location")
                loc_id = lvl.get("location", {}).get("id", "")
                qty_map = {q["name"]: q["quantity"] for q in lvl.get("quantities", [])}
                locations.append({
                    "location_name": loc_name,
                    "location_id": loc_id,
                    "quantities": qty_map
                })

            summary["variants"].append({
                "variant_id": v["id"],
                "variant_title": v["title"],
                "sku": v["sku"],
                "inventory_item_id": inv_item.get("id"),
                "locations": locations
            })

        return json.dumps(summary, indent=2)
    except ShopifyAPIError as e:
        return f"Shopify API Error checking inventory: {e}"
    except Exception as e:
        return f"Unexpected error checking inventory: {e}"

@tool("shopify_adjust_inventory", args_schema=AdjustInventoryInput)
def adjust_inventory(inventory_item_id: str, location_id: str, available_delta: int) -> str:
    """Adjusts available stock for an inventory item at a specific location by adding or subtracting units."""
    client = ShopifyGraphQLClient()
    norm_inv_id = _normalize_gid(inventory_item_id, "InventoryItem")
    norm_loc_id = _normalize_gid(location_id, "Location")

    gql_mutation = """
    mutation AdjustInventory($input: InventoryAdjustQuantitiesInput!) {
      inventoryAdjustQuantities(input: $input) {
        userErrors {
          field
          message
        }
        inventoryAdjustmentGroup {
          createdAt
          changes {
            name
            delta
            quantityAfterChange
          }
        }
      }
    }
    """
    payload = {
        "reason": "correction",
        "name": "available",
        "changes": [
            {
                "inventoryItemId": norm_inv_id,
                "locationId": norm_loc_id,
                "delta": available_delta
            }
        ]
    }
    try:
        data = client.execute(gql_mutation, {"input": payload})
        res = data.get("inventoryAdjustQuantities", {})
        user_errors = res.get("userErrors", [])
        if user_errors:
            err_msg = "; ".join([f"{e.get('message')}" for e in user_errors])
            return f"Shopify error adjusting inventory: {err_msg}"

        group = res.get("inventoryAdjustmentGroup", {})
        changes = group.get("changes", [{}])[0]
        return (
            f"Successfully adjusted inventory!\n"
            f"- Delta: {changes.get('delta')}\n"
            f"- Quantity After Change: {changes.get('quantityAfterChange')}"
        )
    except ShopifyAPIError as e:
        return f"Shopify API Error adjusting inventory: {e}"
    except Exception as e:
        return f"Unexpected error adjusting inventory: {e}"
