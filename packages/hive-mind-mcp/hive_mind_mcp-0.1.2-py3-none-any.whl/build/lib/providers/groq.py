import os
from .openai_compatible import OpenAICompatibleProvider

class GroqProvider(OpenAICompatibleProvider):
    """
    Dedicated Groq provider.
    """
    def __init__(self, model: str = None, timeout: int = 300):
        base_url = "https://api.groq.com/openai/v1"
        api_key = os.getenv("GROQ_API_KEY")
        
        if not model:
            model = "llama-3.3-70b-versatile" # Updated from deprecated llama3-8b
        
        if not api_key:
             from src.logger import get_logger
             get_logger("groq_provider").warning("groq_key_missing")
        
        super().__init__(base_url=base_url, api_key=api_key, model=model, timeout=timeout)

    def list_models(self):
        return ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"]
