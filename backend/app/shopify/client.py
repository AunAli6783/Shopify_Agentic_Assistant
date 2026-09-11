import logging
from typing import Any, Dict, Optional
import httpx
from ..config import settings

logger = logging.getLogger(__name__)

class ShopifyAPIError(Exception):
    """Custom exception for Shopify GraphQL API errors."""
    def __init__(self, message: str, errors: Optional[list] = None):
        super().__init__(message)
        self.errors = errors or []

class ShopifyGraphQLClient:
    """Production-ready client for executing queries & mutations against Shopify Admin API."""

    def __init__(
        self,
        shop_domain: Optional[str] = None,
        access_token: Optional[str] = None,
        api_version: Optional[str] = None,
        timeout: float = 30.0
    ):
        self.shop_domain = shop_domain or settings.shopify_shop_domain
        self.access_token = access_token or settings.shopify_admin_access_token
        self.client_id = settings.shopify_client_id
        self.client_secret = settings.shopify_client_secret
        self.api_version = api_version or settings.shopify_admin_api_version
        self.timeout = timeout

    @property
    def endpoint_url(self) -> str:
        clean_domain = self.shop_domain.strip().replace("https://", "").replace("http://", "").rstrip("/")
        return f"https://{clean_domain}/admin/api/{self.api_version}/graphql.json"

    @property
    def token_exchange_url(self) -> str:
        clean_domain = self.shop_domain.strip().replace("https://", "").replace("http://", "").rstrip("/")
        return f"https://{clean_domain}/admin/oauth/access_token"

    def fetch_access_token(self) -> str:
        """Fetches access token using Client ID and Client Secret (client_credentials grant)."""
        if self.access_token:
            return self.access_token
        if not self.client_id or not self.client_secret:
            raise ShopifyAPIError("Neither SHOPIFY_ADMIN_ACCESS_TOKEN nor (SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET) are set.")

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(self.token_exchange_url, json=payload)
            if resp.status_code != 200:
                raise ShopifyAPIError(f"Token exchange failed ({resp.status_code}): {resp.text}")
            data = resp.json()
            self.access_token = data.get("access_token", "")
            return self.access_token

    def exchange_code_for_token(self, code: str) -> str:
        """Exchanges an authorization code for a permanent access token and persists it to .env."""
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code.strip()
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(self.token_exchange_url, json=payload)
            if resp.status_code != 200:
                raise ShopifyAPIError(f"OAuth code exchange failed ({resp.status_code}): {resp.text}")
            data = resp.json()
            token = data.get("access_token", "")
            if token:
                self.access_token = token
                # Update .env file automatically
                env_path = settings.model_config.get("env_file")
                if env_path:
                    from pathlib import Path
                    p = Path(env_path)
                    if p.exists():
                        content = p.read_text(encoding="utf-8")
                        import re
                        new_content = re.sub(
                            r"SHOPIFY_ADMIN_ACCESS_TOKEN=.*",
                            f"SHOPIFY_ADMIN_ACCESS_TOKEN={token}",
                            content
                        )
                        p.write_text(new_content, encoding="utf-8")
            return token

    def _get_headers(self) -> Dict[str, str]:
        if not self.access_token and self.client_id and self.client_secret:
            self.fetch_access_token()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.access_token:
            headers["X-Shopify-Access-Token"] = self.access_token
        return headers

    def execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synchronously execute a GraphQL query or mutation."""
        payload = {"query": query, "variables": variables or {}}
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                self.endpoint_url,
                json=payload,
                headers=self._get_headers()
            )
            return self._process_response(response)

    async def aexecute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Asynchronously execute a GraphQL query or mutation."""
        payload = {"query": query, "variables": variables or {}}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.endpoint_url,
                json=payload,
                headers=self._get_headers()
            )
            return self._process_response(response)

    def _process_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Validates HTTP status code and parses GraphQL payload & userErrors."""
        if response.status_code != 200:
            raise ShopifyAPIError(
                f"Shopify API HTTP Error {response.status_code}: {response.text}",
                errors=[{"status": response.status_code, "body": response.text}]
            )

        data = response.json()
        
        # Check for top-level GraphQL errors (syntax, authorization, etc.)
        if "errors" in data:
            error_messages = [err.get("message", str(err)) for err in data["errors"]]
            raise ShopifyAPIError(
                f"GraphQL Syntax/Execution Errors: {'; '.join(error_messages)}",
                errors=data["errors"]
            )

        return data.get("data", {})
