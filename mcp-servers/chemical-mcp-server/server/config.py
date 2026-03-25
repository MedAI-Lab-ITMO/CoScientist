from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_ENV_FILE = _PACKAGE_ROOT / ".env"


class Settings(BaseSettings):
    """All environment-driven settings for the chemical MCP server."""

    model_config = SettingsConfigDict(
        env_file=str(_DEFAULT_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Chemical service
    chem_services_host: str = Field(default="localhost", min_length=1)
    chem_services_port: int = Field(default=8005, ge=1, le=65535)
    chem_services_timeout: int = Field(default=60, ge=1, le=3600)

    # Local annotated images (OCR pipeline)
    processed_img_storage_path: Path = Field(
        default=Path("/tmp/chemical_mcp_annotated"),
    )

    # Retrosynthesis
    retrosynthesis_services_host: str = Field(default="localhost", min_length=1)
    retrosynthesis_services_port: int = Field(default=8001, ge=1, le=65535)
    retrosynthesis_request_timeout: int = Field(default=60, ge=1, le=3600)

    # S3-compatible storage
    s3_endpoint_url: str | None = None
    s3_bucket_name: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None

    chem_mcp_host: str = Field(default="0.0.0.0", min_length=1)
    chem_mcp_port: int = Field(default=7331, ge=1, le=65535)
    chem_mcp_path: str = Field(default="/mcp", min_length=1)


def get_settings() -> Settings:
    """Load and validate settings (cached). Call from `main()` for fail-fast startup."""
    return Settings()
