import os
from typing import List, Dict, Optional
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from .base import LLMProvider
from ..config import settings

class AnthropicProvider(LLMProvider):
    def __init__(self, timeout: Optional[float] = None):
        api_key = settings.anthropic_api_key.get_secret_value() if settings.anthropic_api_key else None
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            
        timeout_val = timeout if timeout is not None else settings.default_timeout
        self.client = AsyncAnthropic(api_key=api_key, timeout=timeout_val)
    
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
        
        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": 4096,
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
            
        response = await self.client.messages.create(**kwargs)
        
        # Anthropic response content is a list of blocks, usually we want the text
        text_content = ""
        for block in response.content:
            if block.type == "text":
                text_content += block.text
                
        return text_content

    def list_models(self) -> List[str]:
        return ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
