import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

class TestDashboardTabs(unittest.TestCase):
    def setUp(self):
        self.mock_st = MagicMock()
        self.mock_st.columns.side_effect = lambda spec: [MagicMock() for _ in range(len(spec) if isinstance(spec, list) else spec)]
        self.mock_st.tabs.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock())
        self.mock_st.session_state = {}
        
    def test_explorer_tab_file_view(self):
        # Target lines 745-776: Session Explorer Detail View
        
        # We need to construct the DataFrame that the dashboard uses
        # But since dashboard.py is a script, we can't just inject the DF easily.
        # We have to mock the data loading part to return our desired sessions.
        
        # Mock Glob to return a session and files
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        def mock_glob(pattern, recursive=False, reverse=False):
            # Return session dir
            if ".hive_mind/*" in pattern: return [".hive_mind/test_type"]
            if "test_type/*" in pattern: return [f".hive_mind/test_type/{date_str}"]
            if f"{date_str}/*" in pattern: 
                return [
                    f".hive_mind/test_type/{date_str}/metadata.json",
                    f".hive_mind/test_type/{date_str}/test.json",
                    f".hive_mind/test_type/{date_str}/readme.md" 
                ]
            return []

        # Mock Inputs to pass filters
        self.mock_st.date_input.return_value = (
            datetime.now().date() - timedelta(days=1),
            datetime.now().date() + timedelta(days=1)
        )
        self.mock_st.multiselect.return_value = ["test_type"] # Select our type
        self.mock_st.text_input.return_value = "" # No text filter
        
        # Mock Radio to select a file
        def radio_side_effect(label, options, key=None):
            return "test.json" # Select the JSON file
        self.mock_st.radio.side_effect = radio_side_effect
        
        # Mock file read
        m_open = mock_open(read_data='{"key": "value"}')
        from itertools import cycle
        
        with patch.dict(sys.modules, {
            "streamlit": self.mock_st,
            "streamlit.components": MagicMock(),
            "streamlit.components.v1": MagicMock(),
            "plotly": MagicMock(),
            "plotly.express": MagicMock(),
            "plotly.graph_objects": MagicMock()
        }):
            with patch("builtins.open", m_open), \
                 patch("glob.glob", side_effect=mock_glob), \
                 patch("os.path.exists", return_value=True), \
                 patch("os.path.isdir", return_value=True), \
                 patch("json.load", side_effect=cycle([{}, {"key": "value"}])): # Metadata, then file content, then infinity
                 
                 # Reload dashboard to run the script
                 import src.dashboard
                 import importlib
                 importlib.reload(src.dashboard)
                 
                 # Assertions
                 # Check if st.json was called (line 767)
                 self.mock_st.json.assert_called()
                 
    def test_analytics_tab(self):
        # Target lines 668-692: Analytics Tab logic
        # Needs valid usage data
        
        import time
        now = time.time()
        mock_usage = {
            "total_usd": 100.0,
            "history": [
                {"timestamp": now, "provider": "openai:gpt-4", "cost": 0.5, "model": "gpt-4"},
                {"timestamp": now, "provider": "anthropic:claude-3", "cost": 0.5, "model": "claude-3"}
            ]
        }
        
        # Robust Mocking Strategy
        m_open = mock_open()
        
        def open_side_effect(file, *args, **kwargs):
            handle = m_open(file, *args, **kwargs)
            handle.name = str(file) # Store filename on handle
            return handle
            
        def smart_json_load(fp, *args, **kwargs):
            fname = getattr(fp, "name", "UNKNOWN")
            if "usage.json" in fname:
                return mock_usage
            return {} # Default for others (Plotly schemas, etc)
            
        mock_components = MagicMock()
        
        # We need glob to return something so load_sessions creates a non-empty df_sessions
        # Otherwise Logic skips to "No sessions available..."
        formatted_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        def glob_side_effect(pattern, *args, **kwargs):
            if ".hive_mind/*" in pattern: return [".hive_mind/test_type"]
            if "test_type/*" in pattern: return [f".hive_mind/test_type/{formatted_date}"]
            if f"{formatted_date}/*" in pattern: return ["file1.json"] # Just file count
            return []
    
        with patch.dict(sys.modules, {
            "streamlit": self.mock_st,
            "streamlit.components": mock_components,
            "streamlit.components.v1": mock_components,
            "plotly": MagicMock(),
            "plotly.express": MagicMock(),
            "plotly.graph_objects": MagicMock()
        }):
             with patch("builtins.open", side_effect=open_side_effect), \
                  patch("json.load", side_effect=smart_json_load), \
                  patch("glob.glob", side_effect=glob_side_effect), \
                  patch("os.path.exists", return_value=True), \
                  patch("os.path.isdir", return_value=True): # needed for load_sessions checks
    
                  # Mock inputs for analytics flow
                  self.mock_st.date_input.return_value = (
                      datetime.now().date() - timedelta(days=7),
                      datetime.now().date()
                  )
                  self.mock_st.text_input.return_value = "" # Search term
                  self.mock_st.multiselect.return_value = ["test_type"] # Type filter
                  
                  import src.dashboard
                  import importlib
                  importlib.reload(src.dashboard)
    
                  # Check if plotly charts were created for analytics
                  
                  # logic: if usage_history: ... st.plotly_chart ...
                  self.assertTrue(self.mock_st.plotly_chart.called)
