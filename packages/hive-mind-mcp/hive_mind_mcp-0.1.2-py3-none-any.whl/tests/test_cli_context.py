import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import os
from src.tools import LLMManager
from src.cli import run_analyze
import argparse

class TestContextFeatures(unittest.IsolatedAsyncioTestCase):
    async def test_collaborative_refine_with_context(self):
        manager = LLMManager()
        mock_drafter = AsyncMock()
        mock_drafter.generate_response.return_value = "Draft"
        
        # Inject mock provider
        manager._get_provider = MagicMock(return_value=mock_drafter)
        
        context_data = "IMPORTANT_CONTEXT_DATA"
        await manager.collaborative_refine(
            prompt="Test Prompt",
            drafter_provider="openai",
            context=context_data,
            max_turns=0 # Skip loops
        )
        
        # Verify context was injected into the first call
        call_args = mock_drafter.generate_response.call_args_list[0]
        messages = call_args.kwargs['messages']
        user_content = messages[0]['content']
        
        self.assertIn("Test Prompt", user_content)
        self.assertIn("--- ADDITIONAL CONTEXT ---", user_content)
        self.assertIn("IMPORTANT_CONTEXT_DATA", user_content)

    async def test_round_table_with_context(self):
        manager = LLMManager()
        mock_prov = AsyncMock()
        mock_prov.generate_response.return_value = "Response"
        manager._get_provider = MagicMock(return_value=mock_prov)
        
        context_data = "ROUND_TABLE_CONTEXT"
        await manager.round_table_debate(
            prompt="Topic",
            panelists=[{"provider": "openai", "model": "gpt-4o"}],
            context=context_data
        )
        
        # Check first call (Independent Generation)
        call_args = mock_prov.generate_response.call_args_list[0]
        messages = call_args.kwargs['messages']
        self.assertIn("ROUND_TABLE_CONTEXT", messages[0]['content'])

    async def test_analyze_exclude_logic(self):
        # We need to test the logic inside run_analyze or similar.
        # Since run_analyze is hard to test directly without mocking OS walk,
        # let's mock os.walk and verifying the filtering logic.
        
        with patch('src.cli.LLMManager') as MockManager, \
             patch('os.path.isdir', return_value=True), \
             patch('os.path.isfile', return_value=False), \
             patch('os.walk') as mock_walk:
            
            mock_instance = MockManager.return_value
            mock_instance.analyze_project = AsyncMock()
            
            # Setup fake file structure
            # root/
            #   keep.py
            #   ignore.log
            #   node_modules/bad.py
            mock_walk.return_value = [
                ('root', [], ['keep.py', 'ignore.log']),
                ('root/node_modules', [], ['bad.py'])
            ]
            
            args = argparse.Namespace(
                command="analyze",
                paths=["root"],
                prompt="Test",
                panelists=[],
                exclude=["*.log", "*node_modules*"]
            )
            
            await run_analyze(args)
            
            # Extract the file_paths passed to analyze_project
            call_args = mock_instance.analyze_project.call_args
            file_paths = call_args.kwargs['file_paths']
            
            # 'keep.py' should be there
            self.assertTrue(any('keep.py' in f for f in file_paths))
            # 'ignore.log' should NOT be there
            self.assertFalse(any('ignore.log' in f for f in file_paths))
            # 'bad.py' inside node_modules logic check?
            # Our cli excludes based on fnmatch.
            # *node_modules* should match 'root/node_modules/bad.py' if full path checked?
            # CLI code: "if fnmatch(file, pattern) or fnmatch(full_path, pattern):"
            
    async def test_map_reduce_flag(self):
        # Test that --map-reduce calls map_reduce_context
        from src.cli import run_debate
        
        with patch('src.cli.LLMManager') as MockManager, \
             patch('src.cli.resolve_paths', return_value=['file1.py']), \
             patch('os.path.exists', return_value=True):
            
            mock_instance = MockManager.return_value
            mock_instance.collaborative_refine = AsyncMock()
            mock_instance.map_reduce_context = AsyncMock(return_value="SUMMARIZED_CONTEXT")
            
            args = argparse.Namespace(
                command="debate",
                prompt="test",
                drafter_provider="openai",
                drafter_model="gpt-4o",
                reviewers=[],
                max_turns=3,
                context=["dir"],
                map_reduce=True # FLAG ON
            )
            
            await run_debate(args)
            
            # Verify map_reduce_context was called
            mock_instance.map_reduce_context.assert_called_once_with(['file1.py'])
            
            # Verify the RESULT of map reduce was passed to refine
            call_args = mock_instance.collaborative_refine.call_args
            self.assertEqual(call_args.kwargs['context'], "SUMMARIZED_CONTEXT")
