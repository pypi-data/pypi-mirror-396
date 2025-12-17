"""Core settings for the GuardianHub Core library."""
from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, Field, ConfigDict
from pydantic_settings import BaseSettings


def _load_config_defaults():
    """Load default values from config_dev.json if it exists."""
    import json
    from pathlib import Path
    
    config_path = Path(__file__).parent / "config_dev.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            # Return a dictionary with both endpoints and vector config
            return {
                "endpoints": config.get("endpoints", {}),
                "vector": config.get("vector", {}),
                "llm": config.get("llm", {})
            }
        except Exception as e:
            print(f"Warning: Could not load config_dev.json: {e}")
    return {"endpoints": {}, "vector": {}, "llm": {}}


class ServiceEndpoints(BaseModel):
    """Endpoints for essential shared services with local development defaults."""

    def __init__(self, **data):
        # Load defaults from config_dev.json first
        config_defaults = _load_config_defaults().get("endpoints", {})

        # Get valid fields from the model
        valid_fields = set(self.model_fields.keys())

        # Filter the loaded config to only include valid fields
        filtered_config = {k: v for k, v in config_defaults.items() if k in valid_fields}

        # Merge with any provided data (which takes precedence)
        merged_data = {**filtered_config, **data}

        # Initialize with the merged data
        super().__init__(**merged_data)

    def get(self, key, default=None):
        """Dictionary-style get method for backward compatibility."""
        return getattr(self, key, default)

    # Infrastructure
    POSTGRES_URL: str = Field(
        "postgresql://user:password@localhost:5432/guardianhub",
        description="PostgreSQL connection string or host."
    )
    CONSUL_HTTP_ADDR: str = Field(
        "http://localhost:8500",
        description="Consul service discovery address."
    )

    # Shared Application Services
    TOOL_REGISTRY_URL: str = Field(
        "http://localhost:8000",
        description="URL for the Tool Registry service."
    )
    LLM_URL: str = Field(
        "http://localhost:8001",
        description="URL for the LLM service."
    )
    LANGFUSE_HOST: str = Field(
        "http://localhost:3000",
        description="URL for the Langfuse web server."
    )
    KG_INGESTION_URL: str = Field(
        "http://localhost:8002",
        description="The URL for ingestion."
    )
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(
        "http://localhost:4317",
        description="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    VECTOR_SERVICE_URL: str = Field(
        "http://localhost:8003",
        description="URL for the shared Vector Database Service."
    )
    ENVIRONMENT: str = Field(
        "development",
        description="The deployment environment name."
    )


class VectorConfig(BaseModel):
    """Vector database configuration."""
    default_collection: str = Field(
        "",
        description="Default collection name for vector database operations"
    )

class CoreSettings(BaseSettings):
    """
    Core settings for services, loaded from environment variables.
    These are the base settings that all agents will use.
    """
    model_config = ConfigDict(extra="allow")  # Allow extra fields for flexibility

    endpoints: ServiceEndpoints = Field(
        default_factory=ServiceEndpoints,
        description="Shared service endpoints."
    )
    vector: VectorConfig = Field(
        default_factory=VectorConfig,
        description="Vector database configuration"
    )
    max_retries: int = Field(3, description="Maximum number of retries for HTTP requests.")
    retry_delay: int = Field(2, description="Delay in seconds between retries.")
    http_timeout: int = Field(30, description="Timeout in seconds for HTTP requests.")

# Create a function to get settings to avoid circular imports
def get_settings() -> CoreSettings:
    """Return a new instance of the core settings."""
    return CoreSettings()


# Use lru_cache to cache the settings
@lru_cache()
def get_cached_settings() -> CoreSettings:
    """Return a cached instance of the core settings."""
    return get_settings()


# Export the settings object for easy import access across the application
settings: CoreSettings = get_cached_settings()