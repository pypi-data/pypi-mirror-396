import unittest
from unittest.mock import patch, MagicMock
import os
import asyncio
from src.providers.openai import OpenAIProvider
from src.providers.base import LLMProvider

class TestOpenAICoverage(unittest.IsolatedAsyncioTestCase):
    def test_init_raises(self):
        # Force settings.openai_api_key to be None
        with patch("src.providers.openai.settings") as mock_settings:
            mock_settings.openai_api_key = None
            with self.assertRaises(ValueError):
                OpenAIProvider()

    async def test_generate_response_success(self):
        with patch("src.providers.openai.settings") as mock_settings:
            mock_settings.openai_api_key.get_secret_value.return_value = "sk-test"
            mock_settings.default_timeout = 5.0
            mock_settings.max_retries = 1
            
            with patch("src.providers.openai.AsyncOpenAI") as mock_client_cls:
                provider = OpenAIProvider()
                
                # Mock client.chat.completions.create
                # Need to return an object with choices[0].message.content
                mock_msg = MagicMock()
                mock_msg.content = "Hello World"
                mock_choice = MagicMock()
                mock_choice.message = mock_msg
                mock_resp = MagicMock()
                mock_resp.choices = [mock_choice]
                
                # Async mock setup
                f = asyncio.Future()
                f.set_result(mock_resp)
                
                mock_client_instance = mock_client_cls.return_value
                mock_client_instance.chat.completions.create.return_value = f
                
                response = await provider.generate_response(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": "hi"}],
                    system_prompt="Be helpful"
                )
                
                self.assertEqual(response, "Hello World")
                
                # Verify args
                mock_client_instance.chat.completions.create.assert_called_once()
                call_args = mock_client_instance.chat.completions.create.call_args
                self.assertEqual(call_args.kwargs["model"], "gpt-4o")
                msgs = call_args.kwargs["messages"]
                self.assertEqual(len(msgs), 2)
                self.assertEqual(msgs[0]["role"], "system")
                self.assertEqual(msgs[1]["role"], "user")

    def test_list_models(self):
        with patch("src.providers.openai.settings") as mock_settings:
            mock_settings.openai_api_key.get_secret_value.return_value = "sk-test"
            mock_settings.openai_models = ["gpt-4o", "gpt-3.5-turbo"]
            
            with patch("src.providers.openai.AsyncOpenAI"):
                provider = OpenAIProvider()
                models = provider.list_models()
                self.assertEqual(models, ["gpt-4o", "gpt-3.5-turbo"])

class TestBaseCoverage(unittest.TestCase):
    def test_abstract_instantiation(self):
        # Ensure we can't instantiate abstract class directly
        with self.assertRaises(TypeError):
            LLMProvider()
            
    def test_dummy_implementation(self):
        # Create a concrete implementation to verify abstract methods exist
        class DummyProvider(LLMProvider):
            def PROVIDER_NAME(self): return "dummy"
            async def generate_response(self, m, msgs, s=None): return "ok"
            def list_models(self): return []
            
        d = DummyProvider()
        self.assertIsInstance(d, LLMProvider)

class TestAnthropicCoverage(unittest.IsolatedAsyncioTestCase):
    def test_init_raises(self):
        with patch("src.providers.anthropic.settings") as mock_settings:
            mock_settings.anthropic_api_key = None
            with self.assertRaises(ValueError):
                from src.providers.anthropic import AnthropicProvider
                AnthropicProvider()

    async def test_generate_success(self):
        with patch("src.providers.anthropic.settings") as mock_settings:
            mock_settings.anthropic_api_key.get_secret_value.return_value = "sk-ant"
            mock_settings.default_timeout = 5.0
            
            # Since AsyncAnthropic is imported at top level, we patch it there
            with patch("src.providers.anthropic.AsyncAnthropic") as mock_cls:
                from src.providers.anthropic import AnthropicProvider
                p = AnthropicProvider()
                
                # Mock response: object with content=[block(text="resp")]
                mock_block = MagicMock()
                mock_block.type = "text"
                mock_block.text = "Claude Response"
                
                mock_msg = MagicMock()
                mock_msg.content = [mock_block]
                
                # Ensure async return
                mock_instance = mock_cls.return_value
                f = asyncio.Future()
                f.set_result(mock_msg)
                mock_instance.messages.create.return_value = f
                
                resp = await p.generate_response("claude-3", [{"role": "user", "content": "hi"}])
                self.assertEqual(resp, "Claude Response")

class TestMistralCoverage(unittest.TestCase):
    def test_init_defaults(self):
        from src.providers.mistral import MistralProvider
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "sk-mistral"}):
            with patch("src.providers.mistral.OpenAICompatibleProvider.__init__") as mock_super:
                p = MistralProvider()
                mock_super.assert_called_with(
                    base_url="https://api.mistral.ai/v1",
                    api_key="sk-mistral",
                    timeout=None
                )
                self.assertIn("mistral-large-latest", p.list_models())

class TestGroqCoverage(unittest.TestCase):
    def test_init_defaults(self):
        from src.providers.groq import GroqProvider
        with patch.dict(os.environ, {"GROQ_API_KEY": "gsk-groq"}):
            with patch("src.providers.groq.OpenAICompatibleProvider.__init__") as mock_super:
                p = GroqProvider()
                mock_super.assert_called_with(
                    base_url="https://api.groq.com/openai/v1",
                    api_key="gsk-groq",
                    timeout=300
                )
                # Update to match new behavior which filters models
                models = p.list_models()
                self.assertIn("llama-3.3-70b-versatile", models)
                self.assertIn("whisper-large-v3", models)

class TestOpenRouterCoverage(unittest.TestCase):
    def test_init_headers(self):
        from src.providers.openrouter import OpenRouterProvider
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or"}):
            # AsyncOpenAI is imported INSIDE __init__ in OpenRouterProvider
            # So we must patch 'openai.AsyncOpenAI'
            with patch("openai.AsyncOpenAI") as mock_client:
                p = OpenRouterProvider()
                # Verify client was init with headers
                # Because we patched the class, p.client is the mock instance
                # The constructor was called on the class
                _, kwargs = mock_client.call_args
                self.assertEqual(kwargs["base_url"], "https://openrouter.ai/api/v1")
                self.assertIn("HTTP-Referer", kwargs["default_headers"])
                self.assertEqual(kwargs["default_headers"]["X-Title"], "MCP LLM Orchestrator")
                
                # Check list_models
                self.assertTrue(len(p.list_models()) > 0)
