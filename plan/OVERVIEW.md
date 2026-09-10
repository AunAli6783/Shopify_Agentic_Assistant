# Shopify AI Agent & RAG System: Master Architecture & Roadmap

## 1. Project Vision
Build an enterprise-grade, stateful, and autonomous **Shopify AI Agent system** combining **LangChain, LangGraph, RAG (Retrieval-Augmented Generation)**, and a **FastAPI backend**. 

The system allows merchants and administrators to:
1. **Talk to their store in natural language** to query sales, inventory, and order analytics.
2. **Perform autonomous actions** (create products, update collections, adjust discounts, restock).
3. **Power an intelligent customer-facing RAG chatbot** that understands product catalogs, policies, and order tracking semantically.
4. **Safeguard operations with Human-in-the-Loop (HITL)** approvals before destructive mutations (e.g., price updates, product deletion).
5. **Control everything from a robust backend API** that can connect to web apps, Slack, WhatsApp, or embedded Shopify Admin extensions.

---

## 2. High-Level Architecture Diagram

```
                        ┌──────────────────────────────────────────────┐
                        │      Client Interfaces (Web / Admin / Chat)  │
                        └───────────────────────┬──────────────────────┘
                                                │ REST / WebSocket
                                                ▼
                        ┌──────────────────────────────────────────────┐
                        │            FastAPI Backend Controller        │
                        │    - Auth & Session Management               │
                        │    - Endpoint Routing & Streaming            │
                        └───────────────────────┬──────────────────────┘
                                                │
                                                ▼
                        ┌──────────────────────────────────────────────┐
                        │      LangGraph Multi-Agent State Machine     │
                        │                                              │
                        │  ┌────────────────────────────────────────┐  │
                        │  │             Supervisor Agent           │  │
                        │  └───────────┬─────────────┬──────────────┘  │
                        │              │             │                 │
                        │              ▼             ▼                 │
                        │      ┌──────────────┐ ┌──────────────┐       │
                        │      │ Catalog/Ops  │ │ Support/RAG  │       │
                        │      │    Agent     │ │    Agent     │       │
                        │      └──────┬───────┘ └──────┬───────┘       │
                        │             │                │               │
                        │  [Human-in-the-Loop]  [Memory/State Checkpoint]
                        └─────────────┼────────────────┼───────────────┘
                                      │                │
                     ┌────────────────┴────┐    ┌──────┴───────────────┐
                     ▼                     ▼    ▼                      ▼
        ┌─────────────────────────┐            ┌────────────────────────┐
        │  Shopify GraphQL Tools  │            │   Hybrid RAG Engine    │
        │ - productCreate/Update  │            │ - Vector DB (Chroma)   │
        │ - orders/draftOrders    │            │ - Store Policies / FAQ │
        │ - inventoryAdjust       │            │ - Product Embeddings   │
        └────────────┬────────────┘            └────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │  Shopify Admin API      │
        │  (2026-10 GraphQL)      │
        └─────────────────────────┘
```

---

## 3. Technology Stack

| Layer | Component | Purpose |
|---|---|---|
| **Orchestration & Workflow** | `LangGraph` | Cyclic state machine, multi-agent routing, human-in-the-loop |
| **Tool Framework & LLM** | `LangChain` | Tool abstractions (`@tool`), chat prompt templates, output parsers |
| **Vector Database (RAG)** | `ChromaDB` / `FAISS` | Semantic search over product catalog, store FAQs, and policy documents |
| **Embeddings** | `text-embedding-3-small` / Gemini Embeddings | Dense vector embeddings for products and documentation |
| **Shopify Engine** | `Shopify Admin GraphQL API` | Low-latency, strongly typed interaction with Shopify store |
| **Backend API** | `FastAPI` + `Uvicorn` | Asynchronous REST and WebSocket streaming interface |
| **State Persistence** | `LangGraph MemorySaver` / SQLite | Checkpointing agent state across multi-turn sessions |

---

## 4. Phase Breakdown

- **[Phase 1: Foundation & Authentication](./PHASE_1_ENVIRONMENT_AND_AUTH.md)**
  - Python virtual environment setup, dependencies, Shopify API credentials, and connectivity verification.
- **[Phase 2: Shopify GraphQL Toolset](./PHASE_2_SHOPIFY_GRAPHQL_TOOLS.md)**
  - Comprehensive LangChain tools for querying and mutating products, collections, inventory, orders, and customers.
- **[Phase 3: Hybrid RAG Knowledge Engine](./PHASE_3_RAG_STORE_INTELLIGENCE.md)**
  - Ingestion pipeline, semantic vector search for products, policy documents, and dynamic catalog syncing.
- **[Phase 4: LangGraph Agentic Workflows & Human-in-the-Loop](./PHASE_4_LANGGRAPH_AGENTIC_WORKFLOWS.md)**
  - Multi-agent state machine, supervisor routing, conversation memory, and approval checkpoints for destructive mutations.
- **[Phase 5: Backend API & Control Plane](./PHASE_5_BACKEND_API_AND_CONTROL.md)**
  - FastAPI server, streaming responses, session management, and external webhook triggers.
