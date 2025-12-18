import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
import argparse
import asyncio
from src.cli import main, parse_args
from src import cli

class TestCLICoverage(unittest.TestCase):
    
    def setUp(self):
        # Clean env
        self.patcher_env = patch.dict("os.environ", {}, clear=True)
        self.patcher_env.start()
        # Patch load_dotenv to prevent file system access
        self.patcher_dotenv = patch("src.cli.load_dotenv")
        self.patcher_dotenv.start()
        
    def tearDown(self):
        self.patcher_env.stop()
        self.patcher_dotenv.stop()

    def run_cli(self, args_list):
        """Helper to run CLI with specific args"""
        with patch.object(sys, "argv", ["mcp"] + args_list):
             # Ensure we don't actually exit if sys.exit is called (though we mock it often)
             return main()

    @patch("src.cli.LLMManager")
    def test_debate_command(self, mock_manager_cls):
        mock_manager = mock_manager_cls.return_value
        mock_manager.collaborative_refine = AsyncMock(return_value="Debate Result")
        
        with patch("builtins.print") as mock_print:
            # Fix arguments
            self.run_cli(["debate", "Test Prompt", "--drafter-provider", "openai", "--drafter-model", "gpt-4"])
        
        mock_manager.collaborative_refine.assert_called_once()
        call_args = mock_manager.collaborative_refine.call_args
        self.assertEqual(call_args[1]["prompt"], "Test Prompt")
        self.assertEqual(call_args[1]["drafter_model"], "gpt-4")

    @patch("src.cli.LLMManager")
    def test_review_command(self, mock_manager_cls):
        mock_manager = mock_manager_cls.return_value
        mock_manager.evaluate_content = AsyncMock(return_value="Review Result")
        
        # Mock file reading
        with patch("builtins.open", unittest.mock.mock_open(read_data="File Content")) as mock_file:
            with patch("builtins.print"):
                # Mock resolve_paths (cli.py resolves paths)
                with patch("src.cli.resolve_paths", return_value=["file.txt"]), \
                     patch("src.cli.collect_context_content", return_value="File Content"), \
                     patch("src.cli.os.path.exists", return_value=True):
                    self.run_cli(["review", "file.txt"])
                
        mock_manager.evaluate_content.assert_called_once()

    @patch("src.cli.LLMManager")
    def test_round_table_command(self, mock_manager_cls):
        mock_manager = mock_manager_cls.return_value
        mock_manager.round_table_debate = AsyncMock(return_value="Round Table Result")
        
        with patch("builtins.print"):
             # Fix panelists format provider:model uses parse_kv logic
             # parse_kv splits on :
            self.run_cli(["round_table", "Topic", "--panelists", "openai:gpt-4", "anthropic:claude-3"])
        
        mock_manager.round_table_debate.assert_called_once()
        self.assertEqual(mock_manager.round_table_debate.call_args[1]["prompt"], "Topic")
        # Check panelists list
        expected = [{'provider': 'openai', 'model': 'gpt-4'}, {'provider': 'anthropic', 'model': 'claude-3'}]
        self.assertEqual(mock_manager.round_table_debate.call_args[1]["panelists"], expected)

    @patch("src.cli.LLMManager")
    def test_analyze_command(self, mock_manager_cls):
        mock_manager = mock_manager_cls.return_value
        mock_manager.analyze_project = AsyncMock(return_value="Analysis Result")
        
        # Mock glob/isdir
        with patch("src.cli.os.path.isdir", return_value=True), \
             patch("src.cli.os.walk") as mock_walk:
             
            mock_walk.return_value = [(".", [], ["file1.py"])]
             
            with patch("builtins.print"):
                self.run_cli(["analyze", ".", "Prompt"])
                
        mock_manager.analyze_project.assert_called_once()
        self.assertEqual(mock_manager.analyze_project.call_args[1]["prompt"], "Prompt")

    def test_dashboard_command(self):
        # Logic: run_dashboard calls subprocess.Popen
        with patch("subprocess.Popen") as mock_popen, \
             patch("builtins.print"):
                
            mock_process = MagicMock()
            mock_process.wait = MagicMock()
            mock_popen.return_value = mock_process
            
            # Note: run_dashboard checks os.path.exists for artifacts
            with patch("os.path.exists", return_value=True):
                self.run_cli(["dashboard"])
                
            mock_popen.assert_called()


    def test_init_command_existing(self):
        # Test that we handle existing files gracefully
        with patch("os.path.exists", return_value=True), \
             patch("builtins.print") as mock_print, \
             patch("builtins.open") as mock_open, \
             patch("builtins.input", return_value='n'): # Default no update
             
            self.run_cli(["init"])
            
            # Should print "(skipped)" messages
            output = [c[0][0] for c in mock_print.call_args_list]
            self.assertTrue(any("skipped" in str(s) for s in output))
            # Should NOT open files for writing (w/a)
            # mock_open.assert_not_called() -> We do read files now, so this is invalid.
            # verify no write calls
            write_calls = [c for c in mock_open.call_args_list if 'w' in c[0] or 'a' in c[0]]
            self.assertEqual(len(write_calls), 0)

    def test_config_command_creation(self):
        # Test creation of config dir/file
        with patch("os.path.exists", return_value=False), \
             patch("os.makedirs") as mock_mkdirs, \
             patch("builtins.open", unittest.mock.mock_open()) as mock_file, \
             patch("shutil.copy") as mock_copy, \
             patch("subprocess.call"), \
             patch("builtins.print"):
             
            self.run_cli(["config"])
            
            mock_mkdirs.assert_called()
            mock_file.assert_called() # Creates empty config
            
    def test_analyze_logic_advanced(self):
        mock_manager = MagicMock()
        mock_manager.analyze_project = AsyncMock(return_value="Analysis")
        
        with patch("src.cli.LLMManager", return_value=mock_manager), \
             patch("os.path.isfile", return_value=False), \
             patch("os.path.isdir", return_value=True), \
             patch("os.walk") as mock_walk, \
             patch("builtins.print"):
             
            # Setup walk to return a structure with ignore files
            # root, dirs, files
            mock_walk.return_value = [
                ("/root", [], ["source.py", "ignored.py", "node_modules/junk.js"])
            ]
            
            # Test exclusions
            self.run_cli(["analyze", ".", "Prompt", "--exclude", "*ignored*", "*node_modules*"])
            
            # Check what was passed to analyze_project
            call_args = mock_manager.analyze_project.call_args
            paths = call_args[1]["file_paths"]
            
            self.assertTrue(any("source.py" in p for p in paths))
            self.assertFalse(any("ignored.py" in p for p in paths))

    def test_collect_context_error(self):
         # Test error handling in context collection
         with patch("src.cli.resolve_paths", return_value=["bad.txt"]), \
              patch("builtins.open", side_effect=Exception("Read Error")), \
              patch("src.cli.logger") as mock_log, \
              patch("builtins.print"):
              
              # Debate triggers context collection
              with patch("src.cli.LLMManager"):
                  try:
                      self.run_cli(["debate", "P", "--context", "bad.txt"])
                  except SystemExit:
                      pass
                      
              mock_log.warning.assert_called_with("context_read_error", file="bad.txt", error="Read Error")


    def test_general_exception(self):
        with patch("src.cli.parse_args") as mock_parse:
            mock_parse.side_effect = Exception("Boom")
            with patch("src.cli.logger") as mock_log:
                with self.assertRaises(Exception) as cm:
                    main()
                self.assertEqual(str(cm.exception), "Boom")
