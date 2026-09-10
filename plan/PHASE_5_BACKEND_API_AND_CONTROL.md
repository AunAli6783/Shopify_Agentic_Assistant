# Phase 5: FastAPI Backend API & Control Plane

## Goal
Expose the LangGraph state machine and tools via a high-performance **FastAPI backend**. This backend acts as the control plane for triggering agent runs, streaming tokens, managing sessions, and handling human approvals from any UI or webhook.

---

## 1. REST & WebSocket Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/chat` | Send a message to the agent and receive a complete response |
| `WS` | `/api/v1/chat/stream` | WebSocket for real-time token streaming and intermediate tool progress |
| `GET` | `/api/v1/sessions/{session_id}/state` | Inspect current LangGraph state & message history |
| `POST` | `/api/v1/actions/approve` | Submit Human-in-the-Loop approval (`{"session_id": "...", "approved": true}`) |
| `POST` | `/api/v1/sync/catalog` | Trigger background re-indexing of products into the ChromaDB vector store |
| `POST` | `/api/v1/webhooks/shopify` | Ingest Shopify webhooks (e.g. `products/update`) to keep RAG embeddings fresh |

---

## 2. Streaming Architecture (WebSocket / SSE)
Allows clients to see:
1. **Thinking / Routing**: *"Supervisor delegating to Catalog Agent..."*
2. **Tool Invocations**: *"Executing GraphQL query `products(first: 5)`..."*
3. **Approval Prompt**: *"Waiting for merchant approval: Update price to $29.99"*
4. **Final Response**: Word-by-word streaming of the final synthesized answer.

---

## 3. Project File Structure for Implementation
```
backend/
├── app/
│   ├── main.py              # FastAPI app definition & middleware
│   ├── config.py            # Environment & secrets config
│   ├── api/
│   │   ├── routes.py        # Chat & session endpoints
│   │   └── webhooks.py      # Shopify webhook handlers
│   ├── agent/
│   │   ├── graph.py         # LangGraph state graph definition
│   │   ├── state.py         # AgentState typed dictionary
│   │   ├── supervisor.py    # Supervisor router
│   │   ├── specialists.py   # Catalog and Support specialist nodes
│   │   └── memory.py        # Checkpointer configuration
│   ├── rag/
│   │   ├── vector_store.py  # ChromaDB client & embeddings
│   │   ├── ingestion.py     # Product & policy text chunking
│   │   └── retriever.py     # Hybrid search retriever
│   └── shopify/
│       ├── client.py        # Async GraphQL client
│       └── tools.py         # LangChain @tool definitions
```

---

## 4. Run & Deployment Commands
- **Local Dev**: `uvicorn app.main:app --reload --port 8000`
- **Dockerized**: `docker build -t shopify-langgraph-agent . && docker run -p 8000:8000 --env-file .env shopify-langgraph-agent`
