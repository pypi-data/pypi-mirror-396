
import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

class TestDashboardFull(unittest.TestCase):
    def setUp(self):
        # Create a comprehensive mock for streamlit
        self.mock_st = MagicMock()
        # Custom side effect for st.columns to match unpacking size
        def mock_columns(spec, *args, **kwargs):
            if isinstance(spec, int):
                count = spec
            elif isinstance(spec, (list, tuple)):
                count = len(spec)
            else:
                count = 2 # Default fallback
            return [MagicMock() for _ in range(count)]
            
        self.mock_st.columns.side_effect = mock_columns
        self.mock_st.tabs.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock())
        self.mock_st.expander.return_value.__enter__.return_value = MagicMock()
        
        # Configure inputs to ensure filters return valid data
        # Date input returns tuple (start, end)
        # Date input returns tuple (start, end)
        self.mock_st.date_input.return_value = (
            datetime.now().date() - timedelta(days=365),
            datetime.now().date() + timedelta(days=365)
        )
        # Multiselect returns list
        # Must match exact provider names in mock_usage_data
        # Dynamic Multiselect Mock
        def multiselect_side_effect(label, options, default=None, **kwargs):
            if "Filter by Type" in label:
                return ["debate_type"]
            return ["openai:gpt-4", "anthropic:claude-3"]
        self.mock_st.multiselect.side_effect = multiselect_side_effect

        # Dynamic Radio Mock (for Artifact Explorer file selection)
        def radio_side_effect(label, options, **kwargs):
             if options:
                 return options[0] # Return first file
             return None
        self.mock_st.radio.side_effect = radio_side_effect

        # Text input returns string
        self.mock_st.text_input.return_value = "Topic"
        
        # Session State
        self.mock_st.session_state = {}

        # Mock pandas to avoid dependency issues if needed, but real pandas is usually fine
        # We will use real pandas as it is complex to mock
        
    def test_dashboard_execution(self):
        """Test the full execution of dashboard.py by importing it with mocks."""
        
        # Mock file system for usage and sessions
        import time
        now = time.time()
        mock_usage_data = {
            "total_usd": 10.0,
            "history": [
                {"timestamp": now, "provider": "openai:gpt-4", "cost": 0.5, "model": "gpt-4"},
                {"timestamp": now - 60, "provider": "anthropic:claude-3", "cost": 0.2, "model": "claude-3"}
            ]
        }
        
        # Mock Glob for sessions
        # Structure: artifacts/TYPE/SESSION/metadata.json
        def mock_glob(pattern, recursive=False, reverse=False):
            # Dynamic date string to ensure it passes date filter
            date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            session_dir = f".hive_mind/debate_type/{date_str}"
            
            if pattern.endswith("*") and ".hive_mind" in pattern:
                if ".hive_mind/*" in pattern:
                    # Session types
                    return [".hive_mind/debate_type"]
                if "debate_type/*" in pattern:
                    # Sessions
                    return [session_dir]
                if f"{date_str}/*" in pattern:
                    # Files in session
                    return [f"{session_dir}/metadata.json",
                            f"{session_dir}/log.md"]
            return []

        # Helper to stringify json
        import json
        def import_json(data):
            return json.dumps(data)
    
        # Simpler approach: Mock json.load
    
        with patch.dict(sys.modules, {
            "streamlit": self.mock_st, 
            "plotly.express": MagicMock(), 
            "plotly.graph_objects": MagicMock(),
            "streamlit_adjustable_columns": MagicMock()
        }):
            with patch("builtins.open", mock_open()) as m_open, \
                 patch("json.load") as m_json_load, \
                 patch("glob.glob", side_effect=mock_glob), \
                 patch("os.path.exists", return_value=True), \
                 patch("os.path.isdir", return_value=True), \
                 patch("os.getenv", return_value="5.0"):
                 
                 # Configure Open Read Side Effect (For icons and manually read files)
                 # json.load calls are mocked separately so they don't consume this.
                 # Icons need bytes (rb), Explorer needs str (r).
                 m_open.return_value.read.side_effect = [b"<svg>icon</svg>"] * 20 + ["File Content"]
    
                 # Configure JSON load sequence
                 # Use cycle to prevent StopIteration
                 from itertools import cycle
                 m_json_load.side_effect = cycle([
                     mock_usage_data, # usage.json
                     {"topic": "Test Topic", "cost": 0.1}, # metadata
                     {"key": "value"} # explorer selection (if needed) or just noise
                 ])
    
                 # Trigger Import
                 # If src.dashboard was already imported, we must reload it
                 import importlib
                 if "src.dashboard" in sys.modules:
                     importlib.reload(sys.modules["src.dashboard"])
                 else:
                     import src.dashboard
                 
                 # Verify functionality
                 if self.mock_st.info.called:
                     print("DEBUG: st.info called with:", self.mock_st.info.call_args)
                 
                 if not self.mock_st.plotly_chart.called:
                      print("DEBUG: plotly_chart NOT called")
                 
                 # Verify metrics were displayed (via columns, hard to check directly on st.metric)
                 self.assertTrue(self.mock_st.columns.called)
                 
                 # Using or assertion to catch either path
                 # If info is called, we failed to load data. If plotly is called, we succeeded.
                 # We want to succeed.
                 self.assertFalse(self.mock_st.info.called, "Data loading failed, st.info was called")
                 self.assertTrue(self.mock_st.plotly_chart.called, "st.plotly_chart was not called")
                 # It's called inside render_dashboard
                 
                 # Verify DataFrame creation
                 # Should have processed usage data and session data
