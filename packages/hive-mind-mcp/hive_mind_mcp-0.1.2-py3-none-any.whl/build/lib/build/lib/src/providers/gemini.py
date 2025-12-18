import os
import google.generativeai as genai
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from .base import LLMProvider
from ..config import settings

class GeminiProvider(LLMProvider):
    PROVIDER_NAME = "gemini"
    
    def __init__(self, timeout: Optional[float] = None):
        self.api_key = os.getenv("GEMINI_API_KEY") # Or GOOGLE_API_KEY
        if not self.api_key:
            # Fallback
            self.api_key = os.getenv("GOOGLE_API_KEY")
            
        if not self.api_key:
             # Just warn, don't crash yet
             from src.logger import get_logger
             get_logger("gemini_provider").warning("gemini_key_missing")
        else:
            genai.configure(api_key=self.api_key)
            
        self.timeout = timeout or settings.default_timeout

    def _convert_messages(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None):
        """
        Convert standard messages to Gemini history.
        Gemini uses 'user'/'model' roles. 'system' is separate or handled via config.
        """
        gemini_history = []
        
        # If system prompt is present, Gemini 1.5 allows it in generation_config or as first part.
        # But simpler SDK usage often puts system prompt in Model construction.
        # Here we only instantiate model per request, so we can pass system_instruction there.
        
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [m["content"]]})
            
        return gemini_history

    @retry(
        stop=stop_after_attempt(3), # Less aggressive retry for non-standard providers initially
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_response(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not set")

        # Map model name if needed, but let's assume user passes 'gemini-1.5-flash' etc.
        if not model.startswith("gemini"):
            model = "gemini-1.5-flash"

        # Instantiate model with system instruction
        gen_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt
        )
        
        gemini_messages = self._convert_messages(messages)
        
        # Gemini expects the chat to start. 
        # If we have a history, we use it.
        # However, generate_content is stateless if we pass contents list?
        # Note: genai.GenerativeModel.generate_content (async?)
        # The library supports async.
        
        # We need a proper async call.
        response = await gen_model.generate_content_async(
            contents=gemini_messages
        )
        
        return response.text

    def list_models(self) -> List[str]:
        # Static list for now
        return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
