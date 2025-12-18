
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from typing import Optional

class Settings(BaseSettings):
    # Model Configuration
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI
    openai_api_key: Optional[SecretStr] = Field(None, alias="OPENAI_API_KEY")
    openai_default_model: str = "gpt-4o"
    
    # Anthropic
    anthropic_api_key: Optional[SecretStr] = Field(None, alias="ANTHROPIC_API_KEY")
    anthropic_default_model: str = "claude-3-5-sonnet-20240620"
    
    # DeepSeek
    deepseek_api_key: Optional[SecretStr] = Field(None, alias="DEEPSEEK_API_KEY")
    deepseek_default_model: str = "deepseek-coder"
    
    # System Robustness
    default_timeout: float = Field(300.0, description="Default timeout for LLM calls in seconds")
    max_retries: int = Field(5, description="Maximum number of retries for API calls")
    concurrency_limit: int = Field(10, description="Max concurrent map-reduce tasks")

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
