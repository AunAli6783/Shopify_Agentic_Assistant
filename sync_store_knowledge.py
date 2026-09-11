import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.rag import ingest_shopify_catalog, ingest_markdown_knowledge, vector_store_manager

def main():
    print("==================================================")
    print("  SHOPIFY AI AGENT: HYBRID RAG INGESTION PIPELINE")
    print("==================================================")

    # 1. Ingest Store Policies & FAQs
    knowledge_dir = ROOT_DIR / "knowledge_base"
    print(f"\n[1/2] Ingesting policies & FAQs from: {knowledge_dir}...")
    num_policies = ingest_markdown_knowledge(knowledge_dir)
    print(f"  -> Ingested {num_policies} knowledge chunks into ChromaDB.")

    # 2. Ingest Live Shopify Catalog
    print("\n[2/2] Fetching live catalog from Shopify and indexing...")
    try:
        num_products = ingest_shopify_catalog(limit=50)
        print(f"  -> Ingested {num_products} products into ChromaDB vector store.")
    except Exception as e:
        print(f"  -> [ERROR] Failed to ingest catalog from Shopify: {e}")

    prod_col = vector_store_manager.get_products_collection()
    know_col = vector_store_manager.get_knowledge_collection()

    print("\n--------------------------------------------------")
    print("RAG VECTOR STORE STATUS:")
    print(f"  - Products Collection Count:  {prod_col.count()} embeddings")
    print(f"  - Knowledge Collection Count: {know_col.count()} embeddings")
    print("==================================================")
    print("  RAG KNOWLEDGE SYNC COMPLETE!")
    print("==================================================")

if __name__ == "__main__":
    main()
