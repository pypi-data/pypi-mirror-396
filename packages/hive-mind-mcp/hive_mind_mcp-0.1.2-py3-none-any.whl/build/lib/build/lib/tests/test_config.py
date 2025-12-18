import unittest
from unittest.mock import patch
import os
from src.config import Settings

class TestConfig(unittest.TestCase):
    def test_settings_initialization(self):
        # Test defaults
        s = Settings()
        self.assertEqual(s.openai_default_model, "gpt-4o")
        self.assertEqual(s.max_retries, 2)

    def test_split_comma_validator(self):
        # 1. List input
        self.assertEqual(Settings.split_comma(["a", "b"]), ["a", "b"])
        
        # 2. String comma input
        self.assertEqual(Settings.split_comma("a, b, c"), ["a", "b", "c"])
        
        # 3. JSON input
        self.assertEqual(Settings.split_comma('["x", "y"]'), ["x", "y"])
        
        # 4. JSON invalid fallback to string split?
        # If json.loads fails, it calls split(",")
        self.assertEqual(Settings.split_comma('[invalid'), ['[invalid']) 
        
        # 5. Non-list non-str
        self.assertEqual(Settings.split_comma(123), 123)

    def test_get_api_key(self):
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk-test",
            "ANTHROPIC_API_KEY": "sk-ant",
            "DEEPSEEK_API_KEY": "sk-deep"
        }):
            s = Settings()
            self.assertEqual(s.get_api_key("openai"), "sk-test")
            self.assertEqual(s.get_api_key("anthropic"), "sk-ant")
            self.assertEqual(s.get_api_key("deepseek"), "sk-deep")
            self.assertIsNone(s.get_api_key("unknown"))
            
    def test_get_api_key_none(self):
        # Disable env file loading entirely
        with patch.dict(os.environ, {}, clear=True):
            s = Settings(_env_file=None)
            self.assertIsNone(s.get_api_key("openai"))
