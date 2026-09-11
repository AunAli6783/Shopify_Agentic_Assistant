import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from ..shopify.client import ShopifyGraphQLClient, ShopifyAPIError
from .products import _normalize_gid

class GetOrderDetailsInput(BaseModel):
    order_id: str = Field(description="Shopify Order ID (e.g. 'gid://shopify/Order/12345' or numeric ID)")

class LineItemInput(BaseModel):
    title: str = Field(description="Title of the line item")
    price: str = Field(description="Decimal price string (e.g. '25.00')")
    quantity: int = Field(default=1, ge=1, description="Quantity")

class CreateDraftOrderInput(BaseModel):
    customer_email: str = Field(description="Customer email address for invoice")
    line_items: List[LineItemInput] = Field(description="List of items to include in the draft order")
    note: str = Field(default="", description="Optional note or message for the order")

class SearchCustomerInput(BaseModel):
    query: str = Field(description="Search query (name, email, or phone number)")
    limit: int = Field(default=5, ge=1, le=10, description="Max customers to return (1-10)")

@tool("shopify_get_order_details", args_schema=GetOrderDetailsInput)
def get_order_details(order_id: str) -> str:
    """Retrieves order status, line items, fulfillment state, customer info, and total price."""
    client = ShopifyGraphQLClient()
    norm_order_id = _normalize_gid(order_id, "Order")

    gql_query = """
    query GetOrder($id: ID!) {
      order(id: $id) {
        id
        name
        createdAt
        displayFinancialStatus
        displayFulfillmentStatus
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        customer {
          displayName
          email
        }
        lineItems(first: 10) {
          nodes {
            title
            quantity
            originalUnitPriceSet {
              shopMoney {
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
        data = client.execute(gql_query, {"id": norm_order_id})
        order = data.get("order")
        if not order:
            return f"Order '{norm_order_id}' not found."

        items = [
            f"{item['title']} (Qty: {item['quantity']}, Price: {item.get('originalUnitPriceSet', {}).get('shopMoney', {}).get('amount')})"
            for item in order.get("lineItems", {}).get("nodes", [])
        ]
        total_money = order.get("totalPriceSet", {}).get("shopMoney", {})
        summary = {
            "order_id": order["id"],
            "order_number": order["name"],
            "created_at": order["createdAt"],
            "financial_status": order["displayFinancialStatus"],
            "fulfillment_status": order["displayFulfillmentStatus"],
            "total_price": f"{total_money.get('amount')} {total_money.get('currencyCode')}",
            "customer": order.get("customer", {}).get("displayName", "Guest"),
            "customer_email": order.get("customer", {}).get("email", ""),
            "line_items": items
        }
        return json.dumps(summary, indent=2)
    except ShopifyAPIError as e:
        return f"Shopify API Error getting order: {e}"
    except Exception as e:
        return f"Unexpected error retrieving order: {e}"

@tool("shopify_create_draft_order", args_schema=CreateDraftOrderInput)
def create_draft_order(customer_email: str, line_items: List[LineItemInput], note: str = "") -> str:
    """Creates a draft order (invoice) with specified items, prices, customer email, and custom notes."""
    client = ShopifyGraphQLClient()
    gql_mutation = """
    mutation CreateDraftOrder($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
          name
          status
          invoiceUrl
          totalPrice
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    formatted_items = [
        {"title": item.title, "originalUnitPrice": item.price, "quantity": item.quantity}
        for item in line_items
    ]
    payload = {
        "email": customer_email,
        "note": note,
        "lineItems": formatted_items
    }
    try:
        data = client.execute(gql_mutation, {"input": payload})
        res = data.get("draftOrderCreate", {})
        user_errors = res.get("userErrors", [])
        if user_errors:
            err_msg = "; ".join([f"{e.get('message')}" for e in user_errors])
            return f"Shopify error creating draft order: {err_msg}"

        draft = res.get("draftOrder")
        return (
            f"Successfully created Draft Order!\n"
            f"- Order Name: {draft['name']}\n"
            f"- ID: {draft['id']}\n"
            f"- Total: {draft.get('totalPrice', 'N/A')}\n"
            f"- Invoice URL: {draft.get('invoiceUrl', 'N/A')}"
        )
    except ShopifyAPIError as e:
        return f"Shopify API Error creating draft order: {e}"
    except Exception as e:
        return f"Unexpected error creating draft order: {e}"

@tool("shopify_search_customer", args_schema=SearchCustomerInput)
def search_customer(query: str, limit: int = 5) -> str:
    """Searches customer records by name, email, or phone number and returns their purchase history summary."""
    client = ShopifyGraphQLClient()
    gql_query = """
    query SearchCustomers($first: Int!, $query: String!) {
      customers(first: $first, query: $query) {
        edges {
          node {
            id
            displayName
            email
            phone
            numberOfOrders
            amountSpent {
              amount
              currencyCode
            }
          }
        }
      }
    }
    """
    try:
        data = client.execute(gql_query, {"first": limit, "query": query})
        edges = data.get("customers", {}).get("edges", [])
        if not edges:
            return f"No customers found matching '{query}'."

        results = [
            {
                "id": e["node"]["id"],
                "name": e["node"]["displayName"],
                "email": e["node"]["email"],
                "phone": e["node"]["phone"],
                "total_orders": e["node"]["numberOfOrders"],
                "total_spent": f"{e['node'].get('amountSpent', {}).get('amount', '0')} {e['node'].get('amountSpent', {}).get('currencyCode', '')}"
            }
            for e in edges
        ]
        return json.dumps(results, indent=2)
    except ShopifyAPIError as e:
        return f"Shopify API Error searching customers: {e}"
    except Exception as e:
        return f"Unexpected error searching customers: {e}"
