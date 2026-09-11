import sys
import json
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.tools import (
    search_products,
    create_product,
    get_product_details,
    update_product,
    set_product_metafield,
    list_collections,
    ALL_SHOPIFY_TOOLS
)

def main():
    print("==================================================")
    print("  SHOPIFY AI AGENT: PHASE 2 TOOLS VERIFICATION")
    print("==================================================")
    print(f"Total Registered LangChain Tools: {len(ALL_SHOPIFY_TOOLS)}")
    for t in ALL_SHOPIFY_TOOLS:
        print(f"  - {t.name}: {t.description[:65]}...")
    print("--------------------------------------------------\n")

    # Test 1: Search Products
    print("[1/5] Testing `shopify_search_products` tool...")
    res = search_products.invoke({"query": "", "limit": 3})
    print(f"Result:\n{res}\n")

    # Test 2: Create a Product using the tool
    print("[2/5] Testing `shopify_create_product` tool...")
    test_title = "LangChain Autonomous Product"
    create_res = create_product.invoke({
        "title": test_title,
        "description_html": "<p>Created autonomously via LangChain tool execution.</p>",
        "price": "39.99",
        "product_type": "AI Gear",
        "tags": ["ai", "langchain", "autonomous"],
        "vendor": "LangChain Agent"
    })
    print(f"Result:\n{create_res}\n")

    # Test 3: List Collections
    print("[3/5] Testing `shopify_list_collections` tool...")
    col_res = list_collections.invoke({"limit": 5})
    print(f"Result:\n{col_res}\n")

    # Test 4: Search for the newly created product to get its ID
    print("[4/5] Searching for newly created product to fetch details...")
    search_res = search_products.invoke({"query": f"title:'{test_title}'", "limit": 1})
    try:
        products = json.loads(search_res)
        if products and isinstance(products, list):
            target_id = products[0]["id"]
            print(f"Found Product ID: {target_id}")

            # Test 5: Get Product Details
            print(f"\n[5/5] Testing `shopify_get_product_details` for {target_id}...")
            detail_res = get_product_details.invoke({"product_id": target_id})
            print(f"Result:\n{detail_res}\n")

            # Metafield test
            print(f"Testing `shopify_set_product_metafield` on {target_id}...")
            mf_res = set_product_metafield.invoke({
                "product_id": target_id,
                "key": "agent_note",
                "value": "Validated by LangChain test suite",
                "namespace": "custom"
            })
            print(f"Result:\n{mf_res}\n")
    except Exception as e:
        print(f"Note: Could not parse product search JSON: {e}")

    print("==================================================")
    print("  PHASE 2 TOOLKIT VERIFICATION COMPLETE!")
    print("==================================================")

if __name__ == "__main__":
    main()
