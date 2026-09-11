# System Architecture, Call-Graph & Component Linking Guide

This document provides a comprehensive visual and structural map of **every file, class, and function** in the project, explicitly detailing **which file calls which function in other files**.

---

## 1. Master Call-Graph & Dependency Matrix

| Source File | Function / Class Called | Target File | Why & How It Is Used |
|---|---|---|---|
| `backend/app/config.py` | `BaseSettings`, `Field` | `pydantic_settings` | Loads environment variables from `.env` with validation |
| `backend/app/shopify/client.py` | `settings.*` | `backend/app/config.py` | Pulls domain, credentials, and API version from config |
| `backend/app/shopify/client.py` | `httpx.Client.post()` | Shopify Cloud API | Sends GraphQL requests & OAuth requests to Shopify |
| `backend/app/tools/products.py` | `ShopifyGraphQLClient()` | `backend/app/shopify/client.py` | Instantiates client for catalog queries |
| `backend/app/tools/products.py` | `client.execute(query, vars)` | `backend/app/shopify/client.py` | Executes `productCreate`, `productUpdate`, `metafieldsSet` |
| `backend/app/tools/inventory.py` | `ShopifyGraphQLClient()` | `backend/app/shopify/client.py` | Instantiates client for stock inspection |
| `backend/app/tools/inventory.py` | `_normalize_gid(id, type)` | `backend/app/tools/products.py` | Formats raw numeric IDs into `gid://shopify/...` |
| `backend/app/tools/inventory.py` | `client.execute(query, vars)` | `backend/app/shopify/client.py` | Executes `inventoryAdjustQuantities` mutation |
| `backend/app/tools/collections.py`| `ShopifyGraphQLClient()` | `backend/app/shopify/client.py` | Instantiates client for category creation |
| `backend/app/tools/collections.py`| `_normalize_gid(id, type)` | `backend/app/tools/products.py` | Formats product IDs when associating to collections |
| `backend/app/tools/collections.py`| `client.execute(query, vars)` | `backend/app/shopify/client.py` | Executes `collectionCreate` mutation |
| `backend/app/tools/orders.py` | `ShopifyGraphQLClient()` | `backend/app/shopify/client.py` | Instantiates client for customer/order operations |
| `backend/app/tools/orders.py` | `_normalize_gid(id, type)` | `backend/app/tools/products.py` | Formats order IDs into `gid://shopify/Order/...` |
| `backend/app/tools/orders.py` | `client.execute(query, vars)` | `backend/app/shopify/client.py` | Executes `draftOrderCreate` mutation |
| `backend/app/tools/__init__.py` | All 12 tool functions | `backend/app/tools/*.py` | Collects tools into `ALL_SHOPIFY_TOOLS` list |
| `tests/test_shopify_connection.py` | `client.execute(SHOP_INFO_QUERY)`| `backend/app/shopify/client.py` | Runs healthcheck query against live store |
| `tests/test_shopify_tools.py` | `.invoke(dict)` on each tool | `backend/app/tools/__init__.py` | Executes tools using LangChain's invocation pipeline |
| `authorize_scopes.py` | `client.exchange_code_for_token()` | `backend/app/shopify/client.py` | Trades OAuth `?code=` for permanent access token |

---

## 2. Visual Architecture & Function Call Diagram

```mermaid
graph TD
    classDef envLayer fill:#ffe3e3,stroke:#c92a2a,stroke-width:2px;
    classDef configLayer fill:#ffe8cc,stroke:#e67700,stroke-width:2px;
    classDef clientLayer fill:#d0ebff,stroke:#1971c2,stroke-width:2px;
    classDef shopifyLayer fill:#d3f9d8,stroke:#2b8a3e,stroke-width:2px;
    classDef toolLayer fill:#e6fcf5,stroke:#099268,stroke-width:2px;
    classDef registryLayer fill:#f3d9fa,stroke:#862e9c,stroke-width:2px;
    classDef testLayer fill:#fff9db,stroke:#f08c00,stroke-width:2px;

    subgraph CONFIG_TIER ["1. Configuration Tier"]
        ENV[".env / .env.example\nSHOPIFY_SHOP_DOMAIN\nSHOPIFY_ADMIN_ACCESS_TOKEN\nSHOPIFY_CLIENT_ID / SECRET"]:::envLayer
        CONFIG["backend/app/config.py\nclass Settings\nsettings (instance)"]:::configLayer
    end

    subgraph CLIENT_TIER ["2. Communication Engine"]
        CLIENT["backend/app/shopify/client.py\nclass ShopifyGraphQLClient\n• execute(query, variables)\n• aexecute(query, variables)\n• fetch_access_token()\n• exchange_code_for_token(code)\n• _process_response(response)"]:::clientLayer
        QUERIES["backend/app/shopify/queries.py\nSHOP_INFO_QUERY\nPRODUCTS_QUERY"]:::clientLayer
    end

    subgraph SHOPIFY_CLOUD ["3. External Shopify Cloud"]
        SHOPIFY["Shopify Admin GraphQL API (2026-10)\nEndpoint: /admin/api/2026-10/graphql.json\nOAuth: /admin/oauth/access_token"]:::shopifyLayer
    end

    subgraph TOOLS_TIER ["4. LangChain Tools Suite (backend/app/tools/)"]
        PROD["products.py\n• shopify_search_products()\n• shopify_get_product_details()\n• shopify_create_product()\n• shopify_update_product()\n• shopify_set_product_metafield()\n• Helper: _normalize_gid()"]:::toolLayer
        INV["inventory.py\n• shopify_check_inventory_levels()\n• shopify_adjust_inventory()"]:::toolLayer
        COL["collections.py\n• shopify_list_collections()\n• shopify_create_collection()"]:::toolLayer
        ORD["orders.py\n• shopify_get_order_details()\n• shopify_create_draft_order()\n• shopify_search_customer()"]:::toolLayer
    end

    subgraph REGISTRY_TIER ["5. Master Agent Registry"]
        REGISTRY["backend/app/tools/__init__.py\nALL_SHOPIFY_TOOLS = [12 tools]\nReady for: llm.bind_tools(...)"]:::registryLayer
    end

    subgraph TEST_TIER ["6. Execution & Verification"]
        TEST_CONN["tests/test_shopify_connection.py\nPhase 1 Healthcheck"]:::testLayer
        TEST_TOOLS["tests/test_shopify_tools.py\nPhase 2 Live Tools Suite Test"]:::testLayer
        AUTH_SCRIPT["authorize_scopes.py\nOne-Time Scope Exchange Helper"]:::testLayer
    end

    %% Call Relationships
    ENV -->|Loaded by Pydantic| CONFIG
    CONFIG -->|settings.* domain & tokens| CLIENT
    QUERIES -.->|Provides query strings| CLIENT
    
    CLIENT -->|HTTP POST with X-Shopify-Access-Token| SHOPIFY

    %% Tools to Client calls
    PROD -->|client = ShopifyGraphQLClient()\ncalls client.execute()| CLIENT
    INV -->|client = ShopifyGraphQLClient()\ncalls client.execute()| CLIENT
    COL -->|client = ShopifyGraphQLClient()\ncalls client.execute()| CLIENT
    ORD -->|client = ShopifyGraphQLClient()\ncalls client.execute()| CLIENT

    %% Cross-tool helper calls
    PROD -.->|imports _normalize_gid()| INV
    PROD -.->|imports _normalize_gid()| COL
    PROD -.->|imports _normalize_gid()| ORD

    %% Tools to Registry
    PROD -->|exported into| REGISTRY
    INV -->|exported into| REGISTRY
    COL -->|exported into| REGISTRY
    ORD -->|exported into| REGISTRY

    %% Tests and Scripts
    CLIENT -->|client.execute(SHOP_INFO_QUERY)| TEST_CONN
    REGISTRY -->|search_products.invoke()\ncreate_product.invoke()| TEST_TOOLS
    CLIENT -->|client.exchange_code_for_token(code)| AUTH_SCRIPT
    AUTH_SCRIPT -->|Updates token in| ENV
```

---

## 3. How to View the Diagrams

1. **Excalidraw Native Diagram**:
   - Open [`docs/architecture.excalidraw`](file:///C:/Users/buzz%202/OneDrive/Desktop/SHOPIFY_practice/docs/architecture.excalidraw).
   - In VS Code, install the **Excalidraw** extension to view and edit visually.
   - Alternatively, drag and drop `docs/architecture.excalidraw` onto **[excalidraw.com](https://excalidraw.com)**.

2. **Mermaid Markdown Diagram**:
   - Open this file ([`docs/ARCHITECTURE_DIAGRAM.md`](file:///C:/Users/buzz%202/OneDrive/Desktop/SHOPIFY_practice/docs/ARCHITECTURE_DIAGRAM.md)) and open the Markdown Preview (`Ctrl + Shift + V` in VS Code) or view it directly on GitHub.
