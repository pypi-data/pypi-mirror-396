import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import argparse
from src.cli import run_analyze, run_debate, run_review, run_round_table, run_config

class TestCLICommandsCoverage(unittest.IsolatedAsyncioTestCase):
    async def test_run_analyze(self):
        args = MagicMock()
        args.paths = ["/tmp/test.py"]
        args.prompt = "Analyze this"
        args.panelists = "openai:gpt-4"
        args.exclude = ["*.pyc"]
        
        with patch("src.cli.LLMManager") as mock_cls, \
             patch("os.path.isfile", return_value=True), \
             patch("src.cli.logger"):
            
            manager = mock_cls.return_value
            manager.analyze_project = AsyncMock(return_value="Analysis Result")
            
            await run_analyze(args)
            
            manager.analyze_project.assert_called_once()
            # Verify file collection logic happened (simplified check via logs or just coverage)

    async def test_run_debate(self):
        args = MagicMock()
        args.prompt = "Debate this"
        args.reviewers = "openai:gpt-4"
        args.drafter_model = "gpt-4"
        args.drafter_provider = "openai"
        args.max_turns = 2
        args.context = None
        args.map_reduce = False
        
        with patch("src.cli.LLMManager") as mock_cls, \
             patch("src.cli.logger"):
             
            manager = mock_cls.return_value
            manager.collaborative_refine = AsyncMock(return_value="Debate Result")
            
            await run_debate(args)
            
            manager.collaborative_refine.assert_called_once()

    async def test_run_review(self):
        args = MagicMock()
        args.content = "/tmp/test.py"
        args.reviewers = "openai:gpt-4"
        args.map_reduce = False
        
        with patch("src.cli.LLMManager") as mock_cls, \
             patch("builtins.open", new_callable=unittest.mock.mock_open, read_data="code"), \
             patch("os.path.exists", return_value=True), \
             patch("src.cli.resolve_paths", return_value=["/tmp/test.py"]), \
             patch("src.cli.logger"):
             
            manager = mock_cls.return_value
            manager.evaluate_content = AsyncMock(return_value="Review Result")
            manager.map_reduce_context = AsyncMock(return_value="Mapped Content")
            
            await run_review(args)
            
            manager.evaluate_content.assert_called_once()

    async def test_run_round_table(self):
        args = MagicMock()
        args.topic = "Round Table Topic"
        args.panelists = "openai:gpt-4"
        args.context = None
        args.map_reduce = False
        
        with patch("src.cli.LLMManager") as mock_cls, \
             patch("src.cli.logger"):
             
             manager = mock_cls.return_value
             manager.round_table_debate = AsyncMock(return_value="Round Table Result")
             
             await run_round_table(args)
             
             manager.round_table_debate.assert_called_once()

    async def test_run_config_exists(self):
        # Test generic config run if file exists
        args = MagicMock()
        with patch("os.path.exists", return_value=True), \
             patch("subprocess.call") as mock_call, \
             patch("shutil.which", return_value="/usr/bin/code"):
             
             await run_config(args)
             mock_call.assert_called()
