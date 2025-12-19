from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    llm_api_key: str | None = Field(
        default=None,
        env="LLM_API_KEY",
        description="API key for the configured large language model provider.",
    )
    llm_base_url: str = Field(
        default="https://api.openai.com/v1",
        env="LLM_BASE_URL",
        description="Base URL for the LLM API (OpenAI-compatible by default).",
    )
    llm_model: str = Field(
        default="gpt-4o-mini",
        env="LLM_MODEL",
        description="Model name used when requesting the LLM.",
    )


settings = Settings()
