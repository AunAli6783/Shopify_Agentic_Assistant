# Shopify Agentic Assistant

An enterprise-grade, stateful, and autonomous AI Agent and RAG system connecting **LangChain, LangGraph, and ChromaDB** to the **Shopify Admin GraphQL API**, controllable via a **FastAPI backend**.

---

## 🌟 Overview & Capabilities

- **Shopify GraphQL Engine**: Native, high-performance async/sync integration with Shopify Admin API (2026-10).
- **LangChain & LangGraph Orchestration**: Stateful multi-agent graphs with memory, reasoning loops, and Human-in-the-Loop (HITL) checkpoints.
- **Hybrid RAG Intelligence**: Semantic search over product catalog and store policies using vector embeddings + live GraphQL fallback.
- **Backend Control Plane**: FastAPI REST & WebSocket streaming for AI-powered store administration.

---

## 📁 Project Structure

```
Shopify_Agentic_Assistant/
├── .env.example              # Template for environment variables (secrets are gitignored)
├── .gitignore                # Protects secrets, virtual environments, and vector databases
├── requirements.txt          # Core dependencies (LangChain, LangGraph, FastAPI, ChromaDB, etc.)
├── README.md                 # Project documentation
├── plan/                     # Full architecture & implementation roadmap
│   ├── OVERVIEW.md           # Master system architecture & diagram
│   ├── PHASE_1_ENVIRONMENT_AND_AUTH.md
│   ├── PHASE_2_SHOPIFY_GRAPHQL_TOOLS.md
│   ├── PHASE_3_RAG_STORE_INTELLIGENCE.md
│   ├── PHASE_4_LANGGRAPH_AGENTIC_WORKFLOWS.md
│   └── PHASE_5_BACKEND_API_AND_CONTROL.md
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── config.py         # Pydantic settings loading .env
│       └── shopify/
│           ├── __init__.py
│           ├── client.py     # Production-grade Shopify GraphQL Client (Auto OAuth & Token Exchange)
│           └── queries.py    # Reusable GraphQL queries & mutations
├── tests/
│   └── test_shopify_connection.py # Verification script for live store connection
└── my-test-app/              # Shopify App scaffolding (Remix + Polaris)
```

---

## 🚀 Quick Start (Phase 1)

### 1. Setup Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your Shopify credentials:
```env
SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
SHOPIFY_ADMIN_API_VERSION=2026-10

# Either provide direct Admin Access Token:
SHOPIFY_ADMIN_ACCESS_TOKEN=shpat_...

# OR Client ID & Secret from Shopify Dev Dashboard:
SHOPIFY_CLIENT_ID=your_client_id
SHOPIFY_CLIENT_SECRET=your_client_secret
```

### 3. Verify Live Store Connection
Run the Phase 1 test script:
```bash
python tests/test_shopify_connection.py
```

Expected output:
```text
==================================================
  SHOPIFY AI AGENT: PHASE 1 CONNECTION TEST
==================================================
Store Domain:    your-store.myshopify.com
API Version:     2026-10
...
[SUCCESS] Connected to Shopify store!
Shop Name:   ...
Shop Email:  ...
Currency:    ...
```

---

## 🗺️ Roadmap Phases

- **Phase 1 (Completed)**: Environment setup, dependencies, GraphQL client, and automated token exchange.
- **Phase 2 (Next)**: LangChain `@tool` toolkit (search, create, update products, inventory, orders).
- **Phase 3**: Hybrid RAG (ChromaDB semantic product search + store policies).
- **Phase 4**: LangGraph multi-agent state machine, supervisor routing, and Human-in-the-Loop approvals.
- **Phase 5**: FastAPI backend control plane, WebSocket streaming, and Shopify webhooks.
