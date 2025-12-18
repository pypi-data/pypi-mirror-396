import pytest
import os
import json
import pandas as pd
from unittest.mock import patch, mock_open
from src.dashboard import load_usage, load_sessions

def test_load_usage_exists():
    mock_data = {"total_usd": 10.0, "history": []}
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        data = load_usage()
        assert data == mock_data

def test_load_usage_not_exists():
    with patch("os.path.exists", return_value=False):
        data = load_usage()
        assert data == {}

def test_load_sessions_empty():
    with patch("os.path.exists", return_value=False):
        sessions = load_sessions()
        assert sessions == []

def test_load_sessions_with_data():
    # Mock directory structure:
    # artifacts/
    #   chat/
    #     session_1/
    #       metadata.json
    
    with patch("os.path.exists", return_value=True), \
         patch("glob.glob") as mock_glob, \
         patch("os.path.isdir", return_value=True), \
         patch("builtins.open", mock_open(read_data='{"topic": "test", "cost": 0.5}')):
        
        # Setup glob returns
        # 1. artifacts/* -> [artifacts/chat]
        # 2. artifacts/chat/* -> [artifacts/chat/session_1]
        # 3. session_1/* -> [file1, file2]
        mock_glob.side_effect = [
            ["artifacts/chat"],
            ["artifacts/chat/2025-01-01_10-00-00_session_1"],
            ["file1", "file2"]
        ]
        
        sessions = load_sessions("artifacts")
        
        assert len(sessions) == 1
        s = sessions[0]
        assert s["Type"] == "chat"
        assert s["Topic"] == "test"
        assert s["Cost"] == 0.5
        assert s["Files"] == 2
