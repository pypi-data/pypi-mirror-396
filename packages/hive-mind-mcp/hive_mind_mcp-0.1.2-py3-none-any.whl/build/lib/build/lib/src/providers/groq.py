import os
from .openai_compatible import OpenAICompatibleProvider

class GroqProvider(OpenAICompatibleProvider):
    PROVIDER_NAME = "groq"
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
        
        super().__init__(base_url=base_url, api_key=api_key, timeout=timeout)

    def list_models(self):
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "meta-llama/llama-guard-4-12b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "whisper-large-v3",
            "whisper-large-v3-turbo",
            "playai-tts", 
            "playai-tts-arabic"
        ]
