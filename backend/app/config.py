from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env from the repository root regardless of the process working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    nebius_api_key: str
    nebius_base_url: str = "https://api.tokenfactory.nebius.com/v1/"
    nebius_model: str = "nvidia/Nemotron-3_5-Lightning"
    max_repair_attempts: int = 2
    max_test_seconds: int = 30
    max_upload_mb: int = 20
    max_uncompressed_mb: int = 100
    workspace_root: str = "./workspaces"
    cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
