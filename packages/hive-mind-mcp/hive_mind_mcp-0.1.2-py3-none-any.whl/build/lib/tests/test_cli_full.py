import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import argparse
import sys
import os
from src.cli import parse_kv, resolve_paths, main, run_init, find_free_port

class TestCLIUtils(unittest.TestCase):
    def test_parse_kv_valid(self):
        result = parse_kv(["openai:gpt-4", "anthropic:claude-3"])
        self.assertEqual(result, [{"provider": "openai", "model": "gpt-4"}, {"provider": "anthropic", "model": "claude-3"}])

    def test_parse_kv_invalid_ignored(self):
        # Should log warning but continue/ignore
        with patch("src.cli.logger") as mock_logger:
            result = parse_kv(["openai:gpt-4", "invalid"])
            self.assertEqual(result, [{"provider": "openai", "model": "gpt-4"}])
            mock_logger.warning.assert_called()

    def test_parse_kv_empty(self):
        self.assertIsNone(parse_kv(None))
        self.assertIsNone(parse_kv([]))

    def test_resolve_paths(self):
        with patch("os.path.isfile", side_effect=lambda x: x.endswith(".py")), \
             patch("os.path.isdir", side_effect=lambda x: not x.endswith(".py")), \
             patch("os.walk") as mock_walk:
            
            # recursive directory mock
            mock_walk.return_value = [
                ("root", [], ["test.py", "ignore.bin"])
            ]
            
            # Case 1: Direct file
            res = resolve_paths(["script.py"])
            self.assertEqual(res, ["script.py"])
            
            # Case 2: Directory
            res = resolve_paths(["root"])
            self.assertEqual(res, [os.path.join("root", "test.py")])

class TestCLICommands(unittest.IsolatedAsyncioTestCase):
    async def test_run_init(self):
        with patch("builtins.open") as mock_file, \
             patch("os.path.exists", return_value=False), \
             patch("builtins.input", return_value='y'), \
             patch("os.makedirs"):
            
            args = MagicMock()
            await run_init(args)
            
            # Should open .gitignore, .env, .mcp/config.toml
            self.assertTrue(mock_file.called)
            # count calls roughly
            self.assertGreaterEqual(mock_file.call_count, 3)

    def test_find_free_port(self):
        # Mock socket to succeed on first try
        with patch("socket.socket") as mock_sock:
            mock_sock.return_value.__enter__.return_value.connect_ex.return_value = 1 # fail to connect = free
            port = find_free_port(8000)
            self.assertEqual(port, 8000)

    def test_main_parser_help(self):
        # Test that main() with --help raises SystemExit (handled by argparse)
        with patch("sys.argv", ["mcp", "--help"]):
            with self.assertRaises(SystemExit):
                main()

    def test_main_calls_command(self):
        # Test that main() parses args and calls the corresponding async function
        with patch("sys.argv", ["mcp", "init"]), \
             patch("src.cli.run_init", new_callable=AsyncMock) as mock_init, \
             patch("src.cli.load_dotenv"):
             
             main()
             mock_init.assert_called_once()    
