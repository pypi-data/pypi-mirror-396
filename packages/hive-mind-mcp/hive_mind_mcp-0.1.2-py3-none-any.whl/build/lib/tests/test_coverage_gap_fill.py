import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import time
import asyncio
from src.security import BudgetManager, BudgetAwareProviderWrapper
from src.providers.gemini import GeminiProvider

class TestSecurityGaps(unittest.TestCase):
    def test_load_usage_exception(self):
        # Cover lines 49-50: Exception in _load_usage
        with patch("builtins.open", side_effect=IOError("Disk fail")):
            bm = BudgetManager()
            data = bm._load_usage()
            self.assertEqual(data, {"total_usd": 0.0})

    def test_history_truncation(self):
        # Cover 66-67 (init history) and 76-77 (truncate)
        # We need to mock _load_usage to return data with many entries
        
        # 1. Init history coverage
        with patch.object(BudgetManager, "_load_usage", return_value={"total_usd": 0.0}) as m_load:
            with patch.object(BudgetManager, "_save_usage") as m_save:
                bm = BudgetManager()
                bm.add_cost(0.1, "prov", "mod")
                # assertions
                saved_data = m_save.call_args[0][0]
                self.assertIn("history", saved_data)
                self.assertEqual(len(saved_data["history"]), 1)

        # 2. Truncation coverage
        # Mock history with 100 items
        many_items = [{"cost": 0.1}] * 100
        with patch.object(BudgetManager, "_load_usage", return_value={"total_usd": 10.0, "history": many_items}) as m_load:
            with patch.object(BudgetManager, "_save_usage") as m_save:
                bm = BudgetManager()
                bm.add_cost(0.1, "prov", "mod")
                
                saved_data = m_save.call_args[0][0]
                # Should still be 100 items (trimmed)
                self.assertEqual(len(saved_data["history"]), 100)
                # Last item should be the new one?
                # Actually logic is: append then [-100:]. So yes.
                # But mock had 100. Append 1 -> 101. Slice [-100:] -> 100.
                self.assertEqual(saved_data["total_usd"], 10.1)

    async def test_wrapper_delegation(self):
        # Cover 110: __getattr__
        mock_prov = MagicMock()
        mock_prov.custom_method.return_value = "delegated"
        bm = MagicMock()
        wrapper = BudgetAwareProviderWrapper(mock_prov, bm, "test")
        
        self.assertEqual(wrapper.custom_method(), "delegated")
        mock_prov.custom_method.assert_called()

class TestGeminiGaps(unittest.IsolatedAsyncioTestCase):
    def test_init_fallback_and_warning(self):
        # Cover 15 (fallback) and 19-20 (warning)
        
        # Case 1: No keys at all -> Warning
        with patch.dict(os.environ, {}, clear=True):
            with patch("src.logger.get_logger") as mock_get_logger:
                p = GeminiProvider()
                mock_get_logger.return_value.warning.assert_called_with("gemini_key_missing")
                self.assertIsNone(p.api_key)

        # Case 2: Fallback to GOOGLE_API_KEY
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "fallback_key"}, clear=True):
            with patch("google.generativeai.configure") as mock_conf:
                p = GeminiProvider()
                self.assertEqual(p.api_key, "fallback_key")
                mock_conf.assert_called_with(api_key="fallback_key")

    async def test_generate_error_no_key(self):
        # Cover 54: Raise ValueError if no key
        # Tenacity will retry on ValueError, eventually raising RetryError
        from tenacity import RetryError
        with patch.dict(os.environ, {}, clear=True):
            with patch("src.logger.get_logger"): # suppress warning
                p = GeminiProvider()
                with self.assertRaises(RetryError): 
                    await p.generate_response("model", [])

    async def test_default_model_selection(self):
        # Cover 58: default model logic
        with patch.dict(os.environ, {"GEMINI_API_KEY": "key"}):
            with patch("google.generativeai.GenerativeModel") as mock_model_cls:
                p = GeminiProvider()
                mock_model_instance = mock_model_cls.return_value
                mock_model_instance.generate_content_async = MagicMock()
                
                # Mock response structure
                mock_resp = MagicMock()
                mock_resp.text = "Response"
                # Make it async return
                f = asyncio.Future()
                f.set_result(mock_resp)
                mock_model_instance.generate_content_async.return_value = f
                
                await p.generate_response("simple-model", [{"role": "user", "content": "hi"}])
                
                await p.generate_response("simple-model", [{"role": "user", "content": "hi"}])
                
                # Check args/kwargs
                mock_model_cls.assert_called()
                call_args = mock_model_cls.call_args
                # It might be passed as positional or keyword
                # genai.GenerativeModel(model_name=...) or (model_name, ...)
                if len(call_args.args) > 0:
                    self.assertEqual(call_args.args[0], "gemini-1.5-flash")
                else:
                    self.assertEqual(call_args.kwargs.get("model_name"), "gemini-1.5-flash")

class TestOtherProvidersGaps(unittest.TestCase):
    def test_mistral_init_warning(self):
        from src.providers.mistral import MistralProvider
        with patch.dict(os.environ, {}, clear=True):
            with patch("src.logger.get_logger") as mock_logger:
                p = MistralProvider()
                mock_logger.return_value.warning.assert_called_with("mistral_key_missing")

    def test_openrouter_init_warning(self):
        from src.providers.openrouter import OpenRouterProvider
        with patch.dict(os.environ, {}, clear=True):
            with patch("src.logger.get_logger") as mock_logger:
                p = OpenRouterProvider()
                mock_logger.return_value.warning.assert_called_with("openrouter_key_missing")
                
    def test_deepseek_init_error(self):
        from src.providers.deepseek import DeepSeekProvider
        # DeepSeek uses 'settings' object, so we must mock it
        with patch("src.providers.deepseek.settings") as mock_settings:
             mock_settings.deepseek_api_key = None
             with self.assertRaises(ValueError):
                p = DeepSeekProvider()

    async def test_deepseek_generation(self):
        from src.providers.deepseek import DeepSeekProvider
        # Mock settings AND client
        with patch("src.providers.deepseek.settings") as mock_settings:
            mock_settings.deepseek_api_key.get_secret_value.return_value = "sk-deepseek"
            mock_settings.default_timeout = 10.0
            
            with patch("src.providers.deepseek.AsyncOpenAI") as mock_client_cls:
                p = DeepSeekProvider()
                
                # Mock response
                mock_stream = MagicMock()
                mock_stream.choices = [MagicMock(message=MagicMock(content="DeepSeek Response"))]
                
                mock_client_instance = mock_client_cls.return_value
                f = asyncio.Future()
                f.set_result(mock_stream)
                mock_client_instance.chat.completions.create.return_value = f
                
                resp = await p.generate_response("deepseek-chat", [{"role": "user", "content": "hi"}])
                self.assertEqual(resp, "DeepSeek Response")

    def test_groq_init_warning(self):
        from src.providers.groq import GroqProvider
        with patch.dict(os.environ, {}, clear=True):
            with patch("src.logger.get_logger") as mock_logger:
                p = GroqProvider()
                mock_logger.return_value.warning.assert_called_with("groq_key_missing")
