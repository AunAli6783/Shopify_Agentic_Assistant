# Phase 3: Hybrid RAG Knowledge Engine

## Goal
Build a Retrieval-Augmented Generation (RAG) system that equips the AI agent with semantic understanding of:
1. The **entire product catalog** (natural language search beyond exact keyword matching).
2. **Store policies** (shipping, returns, refunds, terms of service).
3. **Frequently Asked Questions (FAQs)** and brand voice guidelines.

---

## 1. Why Hybrid RAG?
Keyword search (`query: "title:boots"`) fails when a customer asks:
> *"I need waterproof footwear for muddy hikes under $100."*

A **Hybrid RAG approach** solves this:
- **Vector Search (ChromaDB)** finds products by conceptual similarity, features, and use-cases.
- **Shopify GraphQL Live Query** fetches the current real-time price and inventory count for those items.

```
User Query: "Warm jackets for rainy winter"
      │
      ▼
[ChromaDB Vector Retrieval] ──> Returns top 3 matching Product IDs based on semantic embeddings
      │
      ▼
[Shopify GraphQL Live Query] ─> Fetches live inventory & exact pricing for those 3 IDs
      │
      ▼
[LLM Synthesis] ─────────────> Presents personalized recommendation with real-time in-stock confirmation
```

---

## 2. Ingestion Pipeline
1. **Catalog Ingestion**:
   - Background sync pulls all active products via GraphQL pagination.
   - Generates unified text representations:
     ```
     Title: Arctic Parka
     Type: Outerwear
     Tags: winter, waterproof, insulated
     Description: Built with triple-layer Gore-Tex and goose down. Keeps warm down to -20C.
     Price: $189.00
     ```
   - Computes dense vector embeddings and stores them in ChromaDB.

2. **Policy & FAQ Ingestion**:
   - Ingests markdown/PDF documents: `shipping_policy.md`, `refund_policy.md`, `faq.md`.
   - Chunks text using `RecursiveCharacterTextSplitter` (chunk size: 500 tokens, overlap: 50).
   - Tagged with metadata `{"doc_type": "policy", "category": "refunds"}`.

---

## 3. Retrieval Tools for the Agent
- `search_store_knowledge(query: str, category: str = "all")`
  - Retrieves relevant policy sections or answers store-specific procedural questions.
- `semantic_product_search(natural_language_description: str, max_price: float = None)`
  - Returns top semantically relevant products.
