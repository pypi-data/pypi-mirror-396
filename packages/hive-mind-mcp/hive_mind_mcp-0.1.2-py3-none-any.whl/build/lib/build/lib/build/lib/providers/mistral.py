import os
from .openai_compatible import OpenAICompatibleProvider

class MistralProvider(OpenAICompatibleProvider):
    """
    Dedicated Mistral provider.
    """
    def __init__(self, timeout: int = 300):
        base_url = "https://api.mistral.ai/v1"
        api_key = os.getenv("MISTRAL_API_KEY")
        
        if not api_key:
             from src.logger import get_logger
             get_logger("mistral_provider").warning("mistral_key_missing")
        
        super().__init__(base_url=base_url, api_key=api_key, timeout=timeout)

    def list_models(self):
        return ["mistral-large-latest", "mistral-medium", "mistral-small", "open-mixtral-8x22b"]
