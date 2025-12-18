
import os
from typing import List, Dict
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from .base import LLMProvider
from ..config import settings
from typing import Optional

class OpenAIProvider(LLMProvider):
    def __init__(self, timeout: Optional[float] = None):
        self.api_key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.timeout = timeout if timeout is not None else settings.default_timeout
        self.client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout)
    
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_response(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> str:
        # OpenAI handles system prompts via the messages list usually as the first message
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        formatted_messages.extend(messages)
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=formatted_messages
        )
        
        return response.choices[0].message.content or ""

    def list_models(self) -> List[str]:
        # Returned simplified list of common models
        return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
