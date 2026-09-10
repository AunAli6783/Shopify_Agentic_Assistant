import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """Application configuration loaded from environment variables / .env file."""
    
    # Shopify Configuration
    shopify_shop_domain: str = Field(
        default="agentic-ai-ugdsezfx.myshopify.com",
        description="Shopify store domain (e.g. your-store.myshopify.com)"
    )
    shopify_admin_api_version: str = Field(
        default="2026-10",
        description="Shopify Admin GraphQL API version"
    )
    shopify_admin_access_token: str = Field(
        default="",
        description="Shopify Admin API Access Token (shpat_...)"
    )
    shopify_client_id: str = Field(
        default="",
        description="Shopify App Client ID"
    )
    shopify_client_secret: str = Field(
        default="",
        description="Shopify App Client Secret"
    )
    
    # LLM Providers
    openai_api_key: str = Field(default="", description="OpenAI API Key")
    gemini_api_key: str = Field(default="", description="Google Gemini API Key")
    
    # RAG / Vector Store
    chroma_persist_directory: str = Field(
        default=str(BASE_DIR / "chroma_db"),
        description="Directory for local ChromaDB persistence"
    )
    
    # Backend Server
    app_env: str = Field(default="development", description="Application environment")
    host: str = Field(default="0.0.0.0", description="FastAPI host")
    port: int = Field(default=8000, description="FastAPI port")
    debug: bool = Field(default=True, description="Debug mode")

    @property
    def shopify_graphql_url(self) -> str:
        """Computes the full Shopify Admin GraphQL endpoint URL."""
        domain = self.shopify_shop_domain.strip().replace("https://", "").replace("http://", "").rstrip("/")
        return f"https://{domain}/admin/api/{self.shopify_admin_api_version}/graphql.json"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Global settings instance
settings = Settings()
