# Phase 4: LangGraph Multi-Agent Architecture & Agentic Workflows

## Goal
Implement stateful, cyclical multi-agent workflows using **LangGraph**. The system coordinates tasks between specialized agents, retains conversational memory, and halts for **Human-in-the-Loop (HITL)** approval before performing sensitive store operations.

---

## 1. Multi-Agent Topology

```
                       ┌──────────────────────┐
                       │     User Message     │
                       └──────────┬───────────┘
                                  ▼
                       ┌──────────────────────┐
                       │   Supervisor Agent   │
                       │ (Routes conversation)│
                       └──────┬────────┬──────┘
                              │        │
           ┌──────────────────┘        └─────────────────┐
           ▼                                             ▼
┌─────────────────────────┐                   ┌─────────────────────────┐
│   Catalog & Ops Agent   │                   │  Customer Support Agent │
│  - Create/Edit products │                   │  - Order lookup         │
│  - Adjust stock/prices  │                   │  - Policy Q&A (RAG)     │
│  - Generate collections │                   │  - Draft refund/replace │
└──────────┬──────────────┘                   └──────────┬──────────────┘
           │                                             │
           ▼                                             ▼
┌─────────────────────────┐                   ┌─────────────────────────┐
│   Approval Interrupt    │                   │      Standard Tools     │
│  (Requires merchant OK) │                   └─────────────────────────┘
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Execute Store Mutation │
└─────────────────────────┘
```

---

## 2. LangGraph State Schema
```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_agent: str
    pending_action: dict | None       # Mutation payload waiting for HITL approval
    approval_granted: bool | None     # Human decision: True / False
    store_context: dict               # Active shop domain, currency, etc.
```

---

## 3. Human-in-the-Loop (HITL) Checkpoints
Critical store mutations (e.g. bulk price adjustments, product archiving, or refund issuance) shouldn't happen blindly.

Using LangGraph's `interrupt()` or conditional edge with a checkpointer:
1. Agent decides to run `update_product_price(product_id="...", new_price="19.99")`.
2. The graph transitions to `human_approval_node` and pauses execution.
3. The system returns an action confirmation request to the user:
   > *"I have prepared a price update for 'AI Snowboard' from $35.00 to $19.99. Would you like me to apply this change?"*
4. Once the merchant responds with "Yes" or "No", the graph resumes with the human decision.

---

## 4. Cyclic Self-Correction & Reasoning Loop
If a GraphQL mutation returns a validation error (e.g., `userErrors: [{"message": "Barcode already taken"}]`):
- The agent does not crash.
- The state machine routes the error back into the LLM reasoning loop.
- The LLM modifies the parameters (e.g. generates a new unique barcode) and retries the mutation autonomously.
