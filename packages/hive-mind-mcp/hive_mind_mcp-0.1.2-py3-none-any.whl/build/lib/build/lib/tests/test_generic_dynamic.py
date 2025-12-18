import pytest
import os
from unittest.mock import AsyncMock, patch
from src.providers.openai_compatible import OpenAICompatibleProvider

@pytest.mark.asyncio
async def test_generic_dynamic_model_mapping():
    # Setup the mock create return
    mock_choice = AsyncMock()
    mock_choice.message.content = "Mock Response"
    
    mock_client_instance = AsyncMock()
    mock_client_instance.chat.completions.create.return_value.choices = [mock_choice]
            
    # Initialize provider by patching the CLIENT creation
    with patch("openai.AsyncOpenAI", return_value=mock_client_instance):
        # We pass dummy args, but the patch prevents real connection
        provider = OpenAICompatibleProvider(base_url="http://test", api_key="test")
        
        # Action: Call generating response with a SPECIFIC model
        target_model = "mistral-medium-dynamically-mapped"
        await provider.generate_response(
            model=target_model, 
            messages=[{"role": "user", "content": "hi"}]
        )
        
        # Assert: The client was called with that EXACT model
        call_args = mock_client_instance.chat.completions.create.call_args
        assert call_args.kwargs["model"] == target_model
