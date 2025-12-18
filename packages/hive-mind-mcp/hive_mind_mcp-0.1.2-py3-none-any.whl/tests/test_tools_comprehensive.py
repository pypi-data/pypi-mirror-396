import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import os
from src.tools import LLMManager

class TestLLMManagerComprehensive(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Prevent dynamic scanning during init
        with patch("src.tools.LLMManager._discover_providers"):
             self.manager = LLMManager()

    def test_get_provider_instantiation(self):
        # Register a mock provider class
        mock_cls = MagicMock()
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        self.manager.provider_classes["mock_p"] = mock_cls
        
        # Call get_provider
        prov = self.manager._get_provider("mock_p")
        
        # Should have instantiated
        mock_cls.assert_called_once()
        # Should return a wrapper (BudgetAwareProviderWrapper) or the provider depending on implementation
        # The implementation wraps it.
        from src.security import BudgetAwareProviderWrapper
        self.assertIsInstance(prov, BudgetAwareProviderWrapper)
        self.assertEqual(prov.provider, mock_instance)

    def test_get_provider_cached(self):
        mock_cls = MagicMock()
        self.manager.provider_classes["mock_p"] = mock_cls
        
        p1 = self.manager._get_provider("mock_p")
        p2 = self.manager._get_provider("mock_p")
        
        self.assertIs(p1, p2)
        # Should instantiate only once
        mock_cls.assert_called_once()

    async def test_evaluate_content_flow(self):
        # Test the review loop
        mock_reviewer = AsyncMock()
        mock_reviewer.generate_response.return_value = '{"status": "APPROVED", "score": 9, "feedback": "Great"}'
        
        self.manager._get_provider = MagicMock(return_value=mock_reviewer)
        
        # We also need to patch SessionRecorder to avoid disk IO
        with patch("src.persistence.SessionRecorder") as MockRecorder:
            result = await self.manager.evaluate_content(
                content="Test Content",
                reviewers=[{"provider": "mock_p", "model": "gpt-4"}]
            )
        
        self.assertIn("APPROVED", result)
        self.assertIn("Great", result)

    async def test_map_reduce_context(self):
        # Mock map phase
        mock_mapper = AsyncMock()
        # Side effect for summarize_file -> generate_response
        mock_mapper.generate_response.side_effect = ["Summary 1", "Summary 2"]
        
        # Mock reduce phase (not testing reduce here, just map output)
        
        # Inject provider
        self.manager._get_provider = MagicMock(return_value=mock_mapper)
        
        file_paths = ["file1.txt", "file2.txt"]
        
        with patch("builtins.open", new_callable=unittest.mock.mock_open, read_data="File Content"), \
             patch("os.path.exists", return_value=True):
             
             result = await self.manager.map_reduce_context(file_paths)
             
             self.assertIn("Summary 1", result)
             self.assertIn("Summary 2", result)
             self.assertEqual(mock_mapper.generate_response.call_count, 2)

    async def test_round_table_debate(self):
        mock_panelist = AsyncMock()
        mock_panelist.generate_response.return_value = "I agree."
        
        mock_mod = AsyncMock()
        mock_mod.generate_response.return_value = "Consensus Reached: Yes."
        
        def get_prov_side_effect(name):
            if name == "moderator": return mock_mod
            return mock_panelist
            
        self.manager._get_provider = MagicMock(side_effect=get_prov_side_effect)
        
        with patch("src.persistence.SessionRecorder") as MockRecorder:
            result = await self.manager.round_table_debate(
                prompt="Topic",
                panelists=[{"provider": "p1", "model": "m1"}],
                moderator_provider="moderator"
            )
        
        self.assertIn("Consensus Reached", result)
