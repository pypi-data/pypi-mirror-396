import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import os
from src.providers.openai import OpenAIProvider
from src.providers.anthropic import AnthropicProvider
from src.providers.deepseek import DeepSeekProvider

class TestOpenAIProvider(unittest.IsolatedAsyncioTestCase):
    async def test_generate_response(self):
        with patch('src.providers.openai.AsyncOpenAI') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.chat.completions.create = AsyncMock()
            mock_instance.chat.completions.create.return_value.choices = [
                MagicMock(message=MagicMock(content="Test Response"))
            ]
            
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                provider = OpenAIProvider()
                response = await provider.generate_response(
                    model="gpt-4",
                    messages=[{"role": "user", "content": "Hello"}],
                    system_prompt="System"
                )
            
            self.assertEqual(response, "Test Response")
            mock_instance.chat.completions.create.assert_called_once()
            call_kwargs = mock_instance.chat.completions.create.call_args.kwargs
            self.assertEqual(call_kwargs['model'], "gpt-4")
            self.assertEqual(call_kwargs['messages'][0]['role'], 'system')
            self.assertEqual(call_kwargs['messages'][0]['content'], 'System')

    def test_list_models(self):
         with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
             provider = OpenAIProvider()
             models = provider.list_models()
             self.assertIn("gpt-4o", models)
             self.assertIsInstance(models, list)

class TestAnthropicProvider(unittest.IsolatedAsyncioTestCase):
    async def test_generate_response(self):
        with patch('src.providers.anthropic.AsyncAnthropic') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.messages.create = AsyncMock()
            
            # Anthropic response structure mock
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="Claude Response", type="text")]
            mock_instance.messages.create.return_value = mock_message
            
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                provider = AnthropicProvider()
                response = await provider.generate_response(
                    model="claude-3",
                    messages=[{"role": "user", "content": "Hi"}],
                    system_prompt="Be helpful"
                )
            
            self.assertEqual(response, "Claude Response")
            mock_instance.messages.create.assert_called_once()
            call_kwargs = mock_instance.messages.create.call_args.kwargs
            self.assertEqual(call_kwargs['system'], "Be helpful")

class TestDeepSeekProvider(unittest.IsolatedAsyncioTestCase):
    async def test_generate_response(self):
        with patch('src.providers.deepseek.AsyncOpenAI') as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.chat.completions.create = AsyncMock()
            mock_instance.chat.completions.create.return_value.choices = [
                MagicMock(message=MagicMock(content="DeepSeek Response"))
            ]
            
            # Patch the settings object directly since it's already loaded
            with patch('src.providers.deepseek.settings') as mock_settings:
                mock_settings.deepseek_api_key.get_secret_value.return_value = "test-key"
                mock_settings.default_timeout = 300.0
                
                provider = DeepSeekProvider()
                response = await provider.generate_response(
                    model="deepseek-coder",
                    messages=[{"role": "user", "content": "Code"}],
                    system_prompt=None
                )
    
            self.assertEqual(response, "DeepSeek Response")
            # Verify base url was set
            MockClient.assert_called_with(
                api_key="test-key",
                base_url="https://api.deepseek.com",
                timeout=300.0
            )
