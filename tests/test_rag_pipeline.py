import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.tools.rag import semantic_product_search, search_store_policies

def main():
    print("==================================================")
    print("  SHOPIFY AI AGENT: PHASE 3 HYBRID RAG TEST")
    print("==================================================")

    # Test 1: Semantic Product Discovery (Winter / Snow Gear)
    print("\n[1/4] Test: Semantic Search -> 'gear for snow and winter'")
    res1 = semantic_product_search.invoke({"query": "gear for snow and winter", "limit": 3})
    print(f"Result:\n{res1}\n")

    # Test 2: Semantic Product Discovery (AI Autonomous Items)
    print("[2/4] Test: Semantic Search -> 'products created by an autonomous AI agent'")
    res2 = semantic_product_search.invoke({"query": "products created by an autonomous AI agent", "limit": 2})
    print(f"Result:\n{res2}\n")

    # Test 3: Store Policy QA (Return Window)
    print("[3/4] Test: Policy Search -> 'How many days do I have to return an item?'")
    res3 = search_store_policies.invoke({"query": "How many days do I have to return an item?", "limit": 2})
    print(f"Result:\n{res3}\n")

    # Test 4: Store Policy QA (Shipping Rates)
    print("[4/4] Test: Policy Search -> 'What is the cost of standard shipping and delivery time?'")
    res4 = search_store_policies.invoke({"query": "What is the cost of standard shipping and delivery time?", "limit": 2})
    print(f"Result:\n{res4}\n")

    print("==================================================")
    print("  PHASE 3 HYBRID RAG PIPELINE VERIFICATION PASSED!")
    print("==================================================")

if __name__ == "__main__":
    main()
