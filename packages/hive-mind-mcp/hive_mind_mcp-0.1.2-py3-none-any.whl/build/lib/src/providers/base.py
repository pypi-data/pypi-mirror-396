from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMProvider(ABC):
    @abstractmethod
    async def generate_response(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generates a response from the LLM.
        
        Args:
            model: The model identifier (e.g., 'gpt-4', 'claude-3-opus').
            messages: A list of message dictionaries with 'role' and 'content'.
            system_prompt: An optional system prompt to guide the model behavior.
            
        Returns:
            The string content of the model's response.
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """Returns a list of supported models for this provider."""
        pass
        
    @property
    @abstractmethod
    def PROVIDER_NAME(self) -> str:
        """Returns the unique name of the provider (e.g., 'openai')."""
        pass
