import os
import logging
from typing import Optional
from .base import LLMProvider
from .openai import OpenAIProvider

class OpenAICompatibleProvider(OpenAIProvider):
    """
    Generic provider for any OpenAI-compatible API (Ollama, Groq, Azure, vLLM, DeepInfra).
    Reuses the OpenAIProvider logic but overrides the client initialization.
    """
    PROVIDER_NAME = "generic"

    def __init__(self,
                 base_url: Optional[str] = None,
                 api_key: Optional[str] = None,
                 timeout: Optional[float] = None):
        # We don't call super().__init__ directly because it might force standard OPENAI_ API keys.
        # Instead, we set up what we need manually or call it carefully.
        # Looking at openai.py, __init__ sets self.client using env vars.
        
        # We will override the client creation logic.
        from openai import AsyncOpenAI
        
        # 1. Determine Config
        # Priority: Constructor Args -> Env Vars specific to Generic -> Fallback
        self.base_url = base_url or os.getenv("GENERIC_BASE_URL")
        self.api_key = api_key or os.getenv("GENERIC_API_KEY", "dummy-key-for-local")
        
        if not self.base_url:
            # Maybe the user didn't config, but we can't crash blindly.
            # But for a proactive provider, we should warn.
            logging.getLogger("llm_manager").warning(
                "generic_provider_config_missing: GENERIC_BASE_URL not set. Defaulting to localhost:11434/v1 (Ollama)."
            )
            self.base_url = "http://localhost:11434/v1"

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout,
            max_retries=2
        )

    def list_models(self):
        # Many local providers support the /models endpoint
        # For now, let's return a placeholder that says "User Configured".
        return ["generic-model (configured in env)"]
