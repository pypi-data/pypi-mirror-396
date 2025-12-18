import unittest
from unittest.mock import patch, MagicMock, AsyncMock, ANY
import asyncio
import os
from src.tools import LLMManager

class TestToolsAdvanced(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.manager = LLMManager()

    @patch("asyncio.gather")
    @patch("src.tools.LLMManager.summarize_file")
    async def test_map_reduce_context(self, mock_summarize, mock_gather):
        # Mock gather to return an awaitable that yields the list
        future = asyncio.Future()
        future.set_result(["Summary 1", "Summary 2"])
        mock_gather.return_value = future
        
        # Mock file reading by creating temp files? 
        # Or mock os.path.exists and open
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", unittest.mock.mock_open(read_data="Content")):
             
            result = await self.manager.map_reduce_context(["file1.py", "file2.py"])
            
        self.assertEqual(result, "Summary 1\n\nSummary 2")
        self.assertEqual(mock_summarize.call_count, 2)

    @patch("src.tools.LLMManager.map_reduce_context")
    @patch("src.tools.LLMManager.round_table_debate")
    async def test_analyze_project_success(self, mock_debate, mock_map):
        mock_map.return_value = "Combined Context"
        mock_debate.return_value = "Final Answer"
        
        result = await self.manager.analyze_project(["f1"], "Prompt")
        
        self.assertEqual(result, "Final Answer")
        mock_map.assert_called_once()
        mock_debate.assert_called_once()
        # Verify prompt construction in round_table call
        call_kwargs = mock_debate.call_args[1]
        self.assertIn("Combined Context", call_kwargs["prompt"])
        self.assertIn("Prompt", call_kwargs["prompt"])

    @patch("src.tools.LLMManager.map_reduce_context")
    async def test_analyze_project_empty(self, mock_map):
        mock_map.return_value = ""
        result = await self.manager.analyze_project(["f1"], "Prompt")
        self.assertIn("Error", result)

    async def test_summarize_file_success(self):
        mock_provider = MagicMock()
        mock_provider.generate_response = AsyncMock(return_value="Summary")
        self.manager._get_provider = MagicMock(return_value=mock_provider)
        
        result = await self.manager.summarize_file("test.py", "code", "openai")
        self.assertIn("### Summary of test.py", result)
        self.assertIn("Summary", result)

    async def test_summarize_file_error(self):
        mock_provider = MagicMock()
        mock_provider.generate_response = AsyncMock(side_effect=Exception("API Error"))
        self.manager._get_provider = MagicMock(return_value=mock_provider)
        
        result = await self.manager.summarize_file("test.py", "code")
        self.assertIn("(Error generating summary", result)

    # Patch where SessionRecorder is IMPORTED, which is src.persistence NOT src.tools
    # But wait, src.tools does "from src.persistence import SessionRecorder" inside methods
    # So we should patch "src.persistence.SessionRecorder"
    @patch("src.persistence.SessionRecorder")
    async def test_round_table_debate_full_flow(self, mock_recorder_cls):
        # Mock providers
        mock_p1 = MagicMock()
        mock_p1.generate_response = AsyncMock(return_value="Draft 1")
        
        mock_p2 = MagicMock()
        mock_p2.generate_response = AsyncMock(return_value="Draft 2")
        
        mock_mod = MagicMock()
        mock_mod.generate_response = AsyncMock(return_value="Consensus")
        
        # Mock _get_provider to return these based on input
        def get_prov(name):
            if name == "p1": return mock_p1
            if name == "p2": return mock_p2
            if name == "mod": return mock_mod
            return mock_p1 # Default
            
        self.manager._get_provider = MagicMock(side_effect=get_prov)
        
        panelists = [{"provider": "p1", "model": "m1"}, {"provider": "p2", "model": "m2"}]
        
        # For Phase 2 (Critique), generate_response is called again
        # We need to ensure mocks handle multiple calls
        mock_p1.generate_response.side_effect = ["Draft 1", "Critique 1"]
        mock_p2.generate_response.side_effect = ["Draft 2", "Critique 2"]
        
        result = await self.manager.round_table_debate(
            "Topic", 
            panelists=panelists, 
            moderator_provider="mod"
        )
        
        self.assertIn("Consensus", result)
        
        # Phase 1: 2 calls (parallel)
        # Phase 2: 2 calls (parallel)
        # Phase 3: 1 call (moderator)
        mock_mod.generate_response.assert_called_once()


    @patch("src.persistence.SessionRecorder")
    async def test_round_table_debate_all_fail(self, mock_recorder_cls):
        mock_p1 = MagicMock()
        mock_p1.generate_response = AsyncMock(side_effect=Exception("Fail"))
        
        self.manager._get_provider = MagicMock(return_value=mock_p1)
        
        panelists = [{"provider": "p1", "model": "m1"}]
        
        result = await self.manager.round_table_debate("Topic", panelists=panelists)
        
        self.assertIn("CRITICAL ERROR", result)

    def test_list_models(self):
        # Mock _get_provider to return a provider with list_models
        mock_openai = MagicMock()
        mock_openai.list_models.return_value = ["gpt-4"]
        
        mock_anthropic = MagicMock()
        # list_models is synchronous in LLMProvider
        mock_anthropic.list_models.side_effect = Exception("Auth Error")
        
        def get_prov(name):
            if name == "openai": return mock_openai
            if name == "anthropic": return mock_anthropic
            # Return dummy for others to avoid AttributeError
            dummy = MagicMock()
            dummy.list_models.return_value = []
            return dummy
            
        self.manager._get_provider = MagicMock(side_effect=get_prov)
        
        models = self.manager.list_models()
        
        self.assertEqual(models["openai"], ["gpt-4"])
        self.assertIn("Error", models["anthropic"][0])
        # Check others are present (and failed gracefully)
        self.assertIn("deepseek", models)
        self.assertIn("gemini", models)

    @patch("src.persistence.SessionRecorder")
    async def test_collaborative_refine_custom_reviewers(self, mock_recorder):
        # Test parsing logic in collaborative_refine
        # We must ensure os.environ patch works. unittest.mock.patch.dict
        with patch.dict(os.environ, {"DEFAULT_REVIEWERS": "p1:m1, p2:m2"}, clear=True):
             # Mock providers to avoid errors
             mock_prov = MagicMock()
             mock_prov.generate_response = AsyncMock(return_value="Valid Response")
             
             # Need to ensure subsequent calls (reviews) also work
             # The flow calls drafter first, then reviewers (parallel), then drafter again
             mock_prov.generate_response.side_effect = ["Draft", "Review", "Review", "Refined"]
             
             self.manager._get_provider = MagicMock(return_value=mock_prov)
             
             await self.manager.collaborative_refine("Topic", max_turns=1)
             
             # Verify recorder was indeed called implies we got past parsing
             self.assertTrue(mock_recorder.called)

