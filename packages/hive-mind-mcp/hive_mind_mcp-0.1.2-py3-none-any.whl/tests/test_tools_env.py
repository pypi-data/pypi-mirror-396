import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import os
from src.tools import LLMManager

class TestToolsEnv(unittest.IsolatedAsyncioTestCase):
    async def test_round_table_default_reviewers_env_simple(self):
        # Test "provider:model" format
        with patch.dict(os.environ, {"DEFAULT_REVIEWERS": "openai:gpt-4, anthropic:claude-3"}):
            manager = LLMManager()
            # Mock _get_provider to avoid actual init
            manager._get_provider = MagicMock()
            manager._get_provider.return_value.generate_response = AsyncMock(return_value="Answer")
            # Also mock round_table_synthesis calls if needed, which might call generate_response too or chat_complete
            
            res = await manager.round_table_debate("Topic")
            self.assertIn("Consensus", res)

    async def test_round_table_default_reviewers_env_json(self):
        # Test JSON format
        json_str = '[{"provider": "google", "model": "gemini"}]'
        with patch.dict(os.environ, {"DEFAULT_REVIEWERS": json_str}):
             manager = LLMManager()
             manager._get_provider = MagicMock()
             manager._get_provider.return_value.generate_response = AsyncMock(return_value="Answer")
             
             res = await manager.round_table_debate("Topic")
             self.assertIn("Consensus", res)

    async def test_round_table_default_reviewers_env_invalid(self):
        # Test Invalid format -> Should fallback to default default
        with patch.dict(os.environ, {"DEFAULT_REVIEWERS": "invalid_json["}):
             manager = LLMManager()
             manager._get_provider = MagicMock()
             manager._get_provider.return_value.generate_response = AsyncMock(return_value="Answer")
             
             res = await manager.round_table_debate("Topic")
             self.assertIn("Consensus", res)
