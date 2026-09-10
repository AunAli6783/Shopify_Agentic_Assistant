import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.config import settings
from backend.app.shopify.client import ShopifyGraphQLClient, ShopifyAPIError
from backend.app.shopify.queries import SHOP_INFO_QUERY

def main():
    print("==================================================")
    print("  SHOPIFY AI AGENT: PHASE 1 CONNECTION TEST")
    print("==================================================")
    print(f"Store Domain:    {settings.shopify_shop_domain}")
    print(f"API Version:     {settings.shopify_admin_api_version}")
    print(f"GraphQL URL:     {settings.shopify_graphql_url}")
    has_token = bool(settings.shopify_admin_access_token)
    has_credentials = bool(settings.shopify_client_id and settings.shopify_client_secret)
    print(f"Token Configured:{'YES' if has_token else ('CLIENT ID/SECRET' if has_credentials else 'NO (Pending in .env)')}")
    print("--------------------------------------------------")

    if not has_token and not has_credentials:
        print("\n[!] Notice: Neither SHOPIFY_ADMIN_ACCESS_TOKEN nor (SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET) is set.")
        print("    You can either:")
        print("    1. Set SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET in .env (from Dev Dashboard -> App settings)")
        print("    2. Or set SHOPIFY_ADMIN_ACCESS_TOKEN (shpat_...) directly in .env")
        return

    client = ShopifyGraphQLClient()
    print("\nAttempting query: GetShopInformation...")
    try:
        data = client.execute(SHOP_INFO_QUERY)
        print("\n[SUCCESS] Connected to Shopify store!")
        shop = data.get("shop", {})
        print(f"Shop Name:   {shop.get('name')}")
        print(f"Shop Email:  {shop.get('email')}")
        print(f"Currency:    {shop.get('currencyCode')}")
    except ShopifyAPIError as e:
        print(f"\n[ERROR] Shopify API returned an error: {e}")
    except Exception as e:
        print(f"\n[ERROR] Network/Connection error: {e}")

if __name__ == "__main__":
    main()
