
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, field_validator
from typing import Optional, Union

import os
class Settings(BaseSettings):
    # Model Configuration
    # Prioritizes PWD .env over global config
    model_config = SettingsConfigDict(
        env_file=(
            os.path.expanduser("~/.mcp_orchestrator/.env"), 
            ".env"
        ), 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # OpenAI
    openai_api_key: Optional[SecretStr] = Field(None, alias="OPENAI_API_KEY")
    openai_default_model: str = "gpt-4o"
    
    # Anthropic
    anthropic_api_key: Optional[SecretStr] = Field(None, alias="ANTHROPIC_API_KEY")
    anthropic_default_model: str = "claude-sonnet-4-5-20250929"
    
    # DeepSeek
    deepseek_api_key: Optional[SecretStr] = Field(None, alias="DEEPSEEK_API_KEY")
    deepseek_default_model: str = "deepseek-coder"
    
    # System Robustness
    default_timeout: float = Field(60.0, description="Default timeout for LLM calls in seconds")
    max_retries: int = Field(2, description="Maximum number of retries for API calls")
    concurrency_limit: int = Field(10, description="Max concurrent map-reduce tasks")

    # Validated Lists
    openai_models: Union[list[str], str] = Field(
        default=["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        description="Available OpenAI models"
    )
    anthropic_models: Union[list[str], str] = Field(
        default=["claude-sonnet-4-5-20250929", "claude-opus-4-5-20251101", "claude-haiku-4-5-20251001", "claude-3-5-haiku-20241022"],
        description="Available Anthropic models"
    )
    deepseek_models: Union[list[str], str] = Field(
        default=["deepseek-coder", "deepseek-chat"],
        description="Available DeepSeek models"
    )

    @field_validator("openai_models", "anthropic_models", "deepseek_models", mode="before")
    @classmethod
    def split_comma(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Check if it's a JSON string (e.g. '["a", "b"]') just in case
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except:
                    pass
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    def get_api_key(self, provider: str) -> Optional[str]:
        if provider == "openai":
            return self.openai_api_key.get_secret_value() if self.openai_api_key else None
        elif provider == "anthropic":
            return self.anthropic_api_key.get_secret_value() if self.anthropic_api_key else None
        elif provider == "deepseek":
            return self.deepseek_api_key.get_secret_value() if self.deepseek_api_key else None
        return None

# Singleton instance
settings = Settings()
