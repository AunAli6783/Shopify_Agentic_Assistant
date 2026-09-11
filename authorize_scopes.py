import sys
from urllib.parse import urlparse, parse_qs
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.config import settings
from backend.app.shopify.client import ShopifyGraphQLClient

SCOPES = "write_products,read_products,write_orders,read_orders,write_inventory,read_inventory,write_customers,read_customers"
REDIRECT_URI = "https://example.com/api/auth"

def main():
    client_id = settings.shopify_client_id
    shop = settings.shopify_shop_domain

    auth_url = (
        f"https://{shop}/admin/oauth/authorize?"
        f"client_id={client_id}&"
        f"scope={SCOPES}&"
        f"redirect_uri={REDIRECT_URI}"
    )

    print("==================================================")
    print("  SHOPIFY AI AGENT: ONE-TIME SCOPE AUTHORIZATION")
    print("==================================================")
    print("\n1. Open this link in your browser:")
    print(f"\n{auth_url}\n")
    print("2. Click 'Update app' or 'Install app'.")
    print("3. When you are redirected to 'Example Domain', copy the entire address bar URL")
    print("   (it will look like: https://example.com/?code=...&hmac=...)")
    print("--------------------------------------------------")

    user_input = input("\nPaste the URL or code here: ").strip()
    if not user_input:
        print("Cancelled.")
        return

    # Extract code if full URL was pasted
    if "code=" in user_input:
        parsed = urlparse(user_input)
        params = parse_qs(parsed.query)
        code = params.get("code", [""])[0]
    else:
        code = user_input

    if not code:
        print("Could not find authorization code in input.")
        return

    print(f"\nExchanging authorization code for permanent access token...")
    client = ShopifyGraphQLClient()
    try:
        token = client.exchange_code_for_token(code)
        print(f"\n[SUCCESS] Token acquired and saved to .env!")
        print(f"Token: {token[:10]}...{token[-4:]}")
        print("\nNow you have FULL access to Products, Orders, Inventory, and Customers!")
    except Exception as e:
        print(f"[ERROR] Failed to exchange code: {e}")

if __name__ == "__main__":
    main()
