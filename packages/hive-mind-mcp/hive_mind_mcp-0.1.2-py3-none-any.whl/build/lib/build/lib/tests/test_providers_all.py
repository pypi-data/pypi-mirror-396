import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import os
from src.providers.gemini import GeminiProvider
from src.providers.groq import GroqProvider 
from src.providers.openrouter import OpenRouterProvider
from src.providers.mistral import MistralProvider

class TestProviders(unittest.IsolatedAsyncioTestCase):
    
    # --- GEMINI ---
    async def test_gemini_init_and_generate(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
            with patch("src.providers.gemini.genai") as mock_genai:
                mock_model = MagicMock()
                mock_genai.GenerativeModel.return_value = mock_model
                mock_response = MagicMock()
                mock_response.text = "Gemini Response"
                
                mock_model.generate_content_async = AsyncMock(return_value=mock_response)
                
                provider = GeminiProvider()
                resp = await provider.generate_response("gemini-1.5-flash", [{"role": "user", "content": "hi"}])
                
                self.assertEqual(resp, "Gemini Response")
                self.assertEqual(provider.PROVIDER_NAME, "gemini") # Fixed

    async def test_gemini_list_models(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
            with patch("src.providers.gemini.genai"):
                 provider = GeminiProvider()
                 models = provider.list_models()
                 # Provider returns static list currently
                 self.assertIn("gemini-1.5-flash", models)

    # --- GROQ (Uses OpenAI Compatible) ---
    async def test_groq_init_and_generate(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}):
             # Patch at the root where it interacts
             with patch("openai.AsyncOpenAI") as mock_client_cls:
                 mock_client = AsyncMock()
                 mock_client_cls.return_value = mock_client
                 
                 mock_re = MagicMock()
                 mock_re.choices[0].message.content = "Groq Response"
                 mock_client.chat.completions.create.return_value = mock_re
                 
                 provider = GroqProvider()
                 resp = await provider.generate_response("llama3", [{"role": "user", "content": "hi"}])
                 self.assertEqual(resp, "Groq Response")

    def test_groq_list_models(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"}):
            with patch("openai.AsyncOpenAI"):
                p = GroqProvider()
                models = p.list_models()
                self.assertIsInstance(models, list)
                # Update to match new behavior which filters models
                self.assertIn("llama-3.3-70b-versatile", models)
                self.assertIn("whisper-large-v3", models)

    # --- OPENROUTER (Uses OpenAI Compatible) ---
    async def test_openrouter_init_and_generate(self):
         with patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_key"}):
             with patch("openai.AsyncOpenAI") as mock_client_cls:
                 mock_client = AsyncMock()
                 mock_client_cls.return_value = mock_client
                 
                 mock_re = MagicMock()
                 mock_re.choices[0].message.content = "OR Response"
                 mock_client.chat.completions.create.return_value = mock_re
                 
                 provider = OpenRouterProvider()
                 resp = await provider.generate_response("model", [])
                 self.assertEqual(resp, "OR Response")

    # --- MISTRAL (Uses OpenAI Compatible) ---
    async def test_mistral_init_and_generate(self):
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "fake_key"}):
             with patch("openai.AsyncOpenAI") as mock_client_cls:
                 mock_client = AsyncMock() # Used async client
                 mock_client_cls.return_value = mock_client
                 
                 mock_resp = MagicMock()
                 mock_resp.choices[0].message.content = "Mistral Response"
                 mock_client.chat.completions.create.return_value = mock_resp
                 
                 provider = MistralProvider()
                 resp = await provider.generate_response("mistral-large", [])
                 self.assertEqual(resp, "Mistral Response")
