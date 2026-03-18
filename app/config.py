"""Application configuration via environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Review Slayer application settings.

    All values are loaded from environment variables or a .env file.
    """

    # --- Application ---
    environment: str = "development"
    log_level: str = "INFO"
    app_name: str = "Review Slayer"

    # --- OpenAI ---
    openai_api_key: str = ""

    # --- GitHub App ---
    github_app_id: int = 0
    github_private_key_path: str = "./private-key.pem"
    github_webhook_secret: str = ""

    @property
    def github_private_key(self) -> str:
        """Read the GitHub App private key from file."""
        key_path = Path(self.github_private_key_path)
        if key_path.exists():
            return key_path.read_text()
        return ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
