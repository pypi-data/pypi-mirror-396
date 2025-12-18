import unittest
from unittest.mock import patch, MagicMock
import os
from src.providers.openai_compatible import OpenAICompatibleProvider

class TestOpenAICompatible(unittest.TestCase):
    def test_init_with_defaults(self):
        # Test that it defaults to localhost if no base_url provided
        with patch.dict(os.environ, {}, clear=True):
             with patch("logging.getLogger") as mock_logger:
                 provider = OpenAICompatibleProvider()
                 
                 # Check warning
                 mock_logger.return_value.warning.assert_called_with(
                     "generic_provider_config_missing: GENERIC_BASE_URL not set. Defaulting to localhost:11434/v1 (Ollama)."
                 )
                 
                 self.assertEqual(provider.base_url, "http://localhost:11434/v1")
                 self.assertEqual(provider.api_key, "dummy-key-for-local")

    def test_init_with_env(self):
        with patch.dict(os.environ, {"GENERIC_BASE_URL": "http://test:1234", "GENERIC_API_KEY": "sk-test"}):
            provider = OpenAICompatibleProvider()
            self.assertEqual(provider.base_url, "http://test:1234")
            self.assertEqual(provider.api_key, "sk-test")

    def test_list_models(self):
        provider = OpenAICompatibleProvider()
        models = provider.list_models()
        self.assertEqual(models, ["generic-model (configured in env)"])
