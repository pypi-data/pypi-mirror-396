
import unittest
from unittest.mock import AsyncMock, MagicMock
from src.tools import LLMManager

class TestDebateFlow(unittest.IsolatedAsyncioTestCase):
    async def test_collaborative_refine_flow(self):
        print("Testing collaborative_refine flow...")
        
        # 1. Setup Mocks
        manager = LLMManager()
        
        # Mock Drafter
        mock_drafter = AsyncMock()
        # Scenario: Drafter improves over time
        mock_drafter.generate_response.side_effect = [
            "Draft 1: The sky is blue because of water.", # Initial draft (bad)
            "Draft 2: The sky is blue due to scattering.", # Refined draft (better)
        ]
        
        # Mock Reviewer
        mock_reviewer = AsyncMock()
        # Scenario: Reviewer rejects first, approves second
        mock_reviewer.generate_response.side_effect = [
            # Feedback 1: REVISE
            '{"status": "REVISE", "score": 4, "feedback": "Incorrect. Raleigh scattering causes this, not water reflection."}',
            # Feedback 2: APPROVED
            '{"status": "APPROVED", "score": 9, "feedback": "Correct explanation."}'
        ]
        
        # Inject mocks
        manager._get_provider = MagicMock(side_effect=lambda p: mock_drafter if p == "drafter" else mock_reviewer)
        
        # 2. Execute
        result = await manager.collaborative_refine(
            prompt="Why is the sky blue?",
            drafter_model="gpt-4o",
            reviewers=[{"provider": "reviewer", "model": "claude-3-5-sonnet"}],
            max_turns=3,
            drafter_provider="drafter"
        )
        
        # 3. Verify Output
        print(f"\nResult:\n{result}\n")
        
        # Verify calls
        assert mock_drafter.generate_response.call_count == 2, "Drafter should be called twice (Initial + 1 refinement)"
        assert mock_reviewer.generate_response.call_count == 2, "Reviewer should be called twice"
        
        print("SUCCESS: Collaborative refine loop verified with mocks.")
