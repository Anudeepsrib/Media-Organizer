"""
Centralized application configuration.
Loads settings from .env file via Pydantic BaseSettings.

Usage:
    from config import settings
    print(settings.app_version)
"""
import logging
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    All application configuration loaded from environment variables / .env file.
    Pydantic validates types and provides sensible defaults.
    """

    # ── Application ──────────────────────────────────────────────
    app_env: str = Field("development", description="Environment: development | staging | production")
    app_version: str = Field("2.0.0", description="Semantic version shown in /health and OpenAPI")
    app_host: str = Field("0.0.0.0", description="Bind host for uvicorn")
    app_port: int = Field(8000, description="Bind port for uvicorn")
    log_level: str = Field("INFO", description="Python logging level")

    # ── CORS ─────────────────────────────────────────────────────
    cors_origins: str = Field(
        "http://localhost:3000,http://localhost:8000",
        description="Comma-separated allowed origins (use * only in development)"
    )

    # ── AI / Gemini ──────────────────────────────────────────────
    gemini_api_key: str = Field("", description="Google Gemini API key")
    gemini_model: str = Field("gemini-2.0-flash", description="Gemini model name")
    thumbnail_max_size: int = Field(512, description="Max thumbnail dimension in pixels")
    chroma_db_path: str = Field(".chromadb", description="Path for ChromaDB persistent storage")

    # ── Helpers ──────────────────────────────────────────────────
    @property
    def cors_origin_list(self) -> List[str]:
        """Parse comma-separated CORS_ORIGINS into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def resolved_chroma_path(self) -> str:
        """Resolve ChromaDB path relative to the api/ directory."""
        p = Path(self.chroma_db_path)
        if not p.is_absolute():
            p = Path(__file__).parent / p
        return str(p)

    model_config = {
        "env_file": str(Path(__file__).parent.parent / ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


# ── Singleton ────────────────────────────────────────────────────
settings = Settings()

# ── Configure root logger based on settings ──────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("Config")
logger.info(f"Environment: {settings.app_env} | Version: {settings.app_version}")
