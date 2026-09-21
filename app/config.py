from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Indian IPO Intelligence Agent"
    environment: str = "development"

    data_dir: Path = BASE_DIR / "data"
    raw_data_dir: Path = BASE_DIR / "data" / "raw"
    processed_data_dir: Path = BASE_DIR / "data" / "processed"
    metadata_dir: Path = BASE_DIR / "data" / "metadata"
    chroma_dir: Path = BASE_DIR / "data" / "chroma"

    database_url: str = "sqlite:///ipo_intelligence.db"

    model_config = SettingsConfigDict(env_file=".env")

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"
    alpha_vantage_api_key: str | None = None


settings = Settings()

SEBI_SOURCE = "SEBI"

CULTFIT_IPO_ID = "cultfit-2026"

CULTFIT_DOCUMENT_ID = "cultfit-drhp-2026"

CULTFIT_COMPANY_NAME = "CULT.FIT LIMITED"

CULTFIT_DOCUMENT_TYPE = "DRHP"