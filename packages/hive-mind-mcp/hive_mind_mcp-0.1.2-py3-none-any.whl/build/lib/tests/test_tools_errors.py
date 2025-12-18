import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from tenacity import RetryError
from concurrent.futures import Future
import os
from src.tools import LLMManager

class TestToolsErrors(unittest.IsolatedAsyncioTestCase):
    def test_format_error_retry(self):
        manager = LLMManager()
        
        # Mock a RetryError
        future = Future()
        future.set_exception(ValueError("Original Error"))
        retry_err = RetryError(future)
        
        msg = manager._format_error(retry_err)
        # Should unwrap to ValueError
        self.assertIn("ValueError: Original Error", msg)
        
        # Test generic error
        msg = manager._format_error(RuntimeError("Generic"))
        self.assertIn("RuntimeError: Generic", msg)

    def test_list_models_errors(self):
        manager = LLMManager()
        
        # Mock _get_provider to raise exception
        manager._get_provider = MagicMock(side_effect=Exception("Init Failed"))
        
        with patch.object(manager, "logger"):
            models = manager.list_models()
            
            self.assertIn("(Error initializing OpenAI provider)", models.get("openai", []))
            self.assertIn("(Error initializing Anthropic provider)", models.get("anthropic", []))
            self.assertIn("(Error initializing DeepSeek provider)", models.get("deepseek", []))
    
    async def test_evaluate_content_defaults(self):
        # Test env var loading for evaluate_content
        with patch.dict(os.environ, {"DEFAULT_REVIEWERS": "openai:gpt-4"}):
            manager = LLMManager()
            manager._get_provider = MagicMock()
            manager._get_provider.return_value.generate_response = AsyncMock(return_value='{"status": "APPROVED", "score": 10, "feedback": "Good"}')
            
            # Mock persistence
            with patch("src.persistence.SessionRecorder") as mock_rec:
                 res = await manager.evaluate_content("Content")
                 # Should rely on env var reviewers
                 manager._get_provider.assert_called_with("openai")

