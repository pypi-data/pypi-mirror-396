import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from src.tools import LLMManager

class TestLLMManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.manager = LLMManager()

    async def test_chat_completion(self):
        with patch.object(self.manager, '_get_provider') as mock_get_provider:
            mock_provider = AsyncMock()
            mock_provider.generate_response.return_value = "Manager Response"
            mock_get_provider.return_value = mock_provider
            
            response = await self.manager.chat_completion(
                provider="openai", model="gpt-4", messages=[]
            )
            
            self.assertEqual(response, "Manager Response")
            mock_provider.generate_response.assert_called_once()
            
    async def test_collaborative_refine_logic(self):
        """Test the debate loop logic without hitting APIs"""
        # Mock Drafter
        mock_drafter = AsyncMock()
        mock_drafter.generate_response.side_effect = ["Draft 1", "Draft 2"]
        
        # Mock Reviewer
        mock_reviewer = AsyncMock()
        # Review 1: Revise, Review 2: Approved
        mock_reviewer.generate_response.side_effect = [
            '{"status": "REVISE", "score": 5, "feedback": "Fix this"}',
            '{"status": "APPROVED", "score": 10, "feedback": "Good job"}'
        ]
        
        self.manager._get_provider = MagicMock(side_effect=lambda p: mock_drafter if p == "drafter" else mock_reviewer)
        
        result = await self.manager.collaborative_refine(
            prompt="Test Prompt",
            drafter_provider="drafter",
            reviewers=[{"provider": "reviewer", "model": "rev-1"}]
        )
        
        self.assertIn("Final Answer (Approved by Council)", result)
        self.assertIn("Draft 2", result)
        # Drafter called twice (initial + refine)
        self.assertEqual(mock_drafter.generate_response.call_count, 2)
        
    async def test_evaluate_content(self):
         mock_prov = AsyncMock()
         mock_prov.generate_response.return_value = '{"status": "APPROVED", "score": 8, "feedback": "LGTM"}'
         
         self.manager._get_provider = MagicMock(return_value=mock_prov)
         
         result = await self.manager.evaluate_content(
             content="Some code",
             reviewers=[{"provider": "openai", "model": "gpt-4"}]
         )
         
         self.assertIn("Reviewer 1", result)
         self.assertIn("LGTM", result)
         self.assertIn("✅", result)

    async def test_round_table_debate(self):
        # Mock provider for panelists
        mock_panelist = AsyncMock()
        mock_panelist.generate_response.return_value = "My Perspective"
        
        # Mock moderator
        mock_mod = AsyncMock()
        mock_mod.generate_response.return_value = "Consensus Reached"
        
        self.manager._get_provider = MagicMock(side_effect=lambda p: mock_mod if p == "mod" else mock_panelist)
        
        result = await self.manager.round_table_debate(
            prompt="Topic",
            panelists=[{"provider": "p1", "model": "m1"}, {"provider": "p2", "model": "m2"}],
            moderator_provider="mod"
        )
        
        self.assertIn("Consensus Reached", result)
        # 2 panelists * (1 generation + 1 critique) = 4 calls
        # We need to account for how many times generic provider is called.
        # Implementation details: we check calls or result content
        self.assertIn("My Perspective", str(mock_panelist.generate_response.mock_calls))
