import os
from .openai_compatible import OpenAICompatibleProvider

class OpenRouterProvider(OpenAICompatibleProvider):
    PROVIDER_NAME = "openrouter"
    """
    OpenRouter specific provider.
    Inherits from Generic Provider but forces the correct Base URL and adds required headers.
    """
    def __init__(self, timeout: int = 300):
        # Force these values
        base_url = "https://openrouter.ai/api/v1"
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not api_key:
             from src.logger import get_logger
             get_logger("openrouter_provider").warning("openrouter_key_missing")
        
        # Initialize parent (Generic)
        super().__init__(base_url=base_url, api_key=api_key, timeout=timeout)
        
        # Add OpenRouter specific headers to the client
        # OpenAI Python client allows extra_headers in constructor? No, check docs.
        # It allows `default_headers`.
        # Since we initialized client in super().__init__, we need to modify it or re-init.
        # super().__init__ creates self.client.
        
        # Re-create client with headers
        from openai import AsyncOpenAI
        
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout,
            max_retries=2,
            default_headers={
                "HTTP-Referer": "https://github.com/mcp-llm-orchestrator", # Required by OpenRouter
                "X-Title": "MCP LLM Orchestrator"
            }
        )

    def list_models(self):
        try:
            import httpx
            with httpx.Client(timeout=10) as client:
                response = client.get("https://openrouter.ai/api/v1/models")
                if response.status_code == 200:
                    data = response.json().get("data", [])
                    return [m["id"] for m in data]
                else:
                    return [f"Error fetching models: {response.status_code}"]
        except Exception as e:
            return [f"Error fetching models: {str(e)}"]
