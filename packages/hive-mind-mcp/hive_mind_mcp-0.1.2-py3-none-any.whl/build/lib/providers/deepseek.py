import os
from typing import List, Dict
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from .base import LLMProvider
from ..config import settings
from typing import Optional

class DeepSeekProvider(LLMProvider):
    def __init__(self, timeout: Optional[float] = None):
        api_key = settings.deepseek_api_key.get_secret_value() if settings.deepseek_api_key else None
        if not api_key:
            # Fallback or specific error
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        
        timeout_val = timeout if timeout is not None else settings.default_timeout
        # DeepSeek is OpenAI compatible
        self.client = AsyncOpenAI(
            api_key=api_key, 
            base_url="https://api.deepseek.com",
            timeout=timeout_val
        )
    
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
        return ["deepseek-chat", "deepseek-coder"]
