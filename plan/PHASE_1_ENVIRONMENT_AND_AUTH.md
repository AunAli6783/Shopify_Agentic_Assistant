# Phase 1: Environment, Dependencies & Shopify Authentication

## Goal
Establish a clean Python development environment, install all core libraries, configure environment variables, and establish an authenticated connection to the Shopify GraphQL Admin API.

---

## 1. Project Directory Structure
```
SHOPIFY_practice/
├── .env                  <-- Ignored by git, stores API keys & tokens
├── .env.example          <-- Template for required environment variables
├── .gitignore
├── requirements.txt      <-- Python dependencies
├── plan/                 <-- Project roadmap & phases
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py     <-- Pydantic settings
│   │   ├── shopify/
│   │   │   ├── client.py <-- GraphQL HTTP Client with retry & rate-limiting
│   │   │   └── queries.py
├── tests/
│   └── test_shopify_connection.py
```

---

## 2. Python Dependencies (`requirements.txt`)
```text
# LangChain & LangGraph
langchain>=0.3.0
langchain-core>=0.3.0
langchain-community>=0.3.0
langgraph>=0.2.20
langchain-openai>=0.2.0
langchain-google-genai>=2.0.0

# Vector Database & RAG
chromadb>=0.5.0
tiktoken>=0.7.0

# Backend & HTTP
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
httpx>=0.27.0
requests>=2.32.0
pydantic>=2.8.0
pydantic-settings>=2.4.0
python-dotenv>=1.0.1
```

---

## 3. Environment Variables Configuration (`.env.example`)
```env
# Shopify Credentials
SHOPIFY_SHOP_DOMAIN=your-store-name.myshopify.com
SHOPIFY_ADMIN_API_VERSION=2026-10
SHOPIFY_ADMIN_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxx

# LLM Providers (Choose one or both)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...

# Agent & Server Configuration
APP_ENV=development
PORT=8000
DEBUG=True
```

---

## 4. Shopify GraphQL Client Implementation (`client.py`)
Key features:
- Uses `httpx` async client for high performance.
- Injects `X-Shopify-Access-Token` and `Content-Type: application/json`.
- Automatic retry on GraphQL cost limit / rate-limiting (`THROTTLED` extensions).
- Full type verification on responses.

---

## 5. Verification Checklist
- [ ] Virtual environment created (`python -m venv venv`).
- [ ] Dependencies installed (`pip install -r requirements.txt`).
- [ ] Test script successfully queries `shop { name myshopifyDomain }` and returns 200 OK.
