import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from src.tools import LLMManager

class TestToolsDiscovery(unittest.TestCase):
    def setUp(self):
        # We need to unpatch the _discover_providers that we patched in other tests if they leaked?
        # unittest.IsolatedAsyncioTestCase usually cleans up.
        # Here we WANT to test _discover_providers, so we instantiate LLMManager normally
        # BUT we must mock the calls inside it to avoid real side effects.
        pass

    # @unittest.skip("Mocking issues with pkgutil.iter_modules")
    def test_discover_providers_scan_package(self):
        """Test _scan_package matches expected behavior"""
        import pkgutil
        # Patch where it is used
        with patch("importlib.import_module") as mock_import, \
             patch.object(pkgutil, "iter_modules") as mock_iter:
            
            # Use concrete class for module to ensure hasattr works reliably
            class DummyModule:
                __path__ = ["/fake/path"]
            
            universal_mock = DummyModule()
            mock_import.return_value = universal_mock
            
            # Setup modules found
            mock_iter.return_value = [
                (None, "module_one", False)
            ]
            
            manager = LLMManager()
            # Reset mocks from init
            mock_import.reset_mock()
            mock_iter.reset_mock()
            
            # Run scan
            with patch.object(manager, "_register_providers_from_module") as mock_register:
                manager._scan_package("src.providers")
                
                # Check assertions
                # 1. Import package
                mock_import.assert_any_call("src.providers")
                
                # 2. Iterate
                mock_iter.assert_called_with(["/fake/path"])
                
                # 3. Import submodule
                mock_import.assert_any_call("src.providers.module_one")
                
                # 4. Register
                mock_register.assert_called_with(universal_mock)

    def test_register_providers_logic(self):
        """Test _register_providers_from_module extracts classes"""
        from src.providers.base import LLMProvider
        
        class MockProvider(LLMProvider):
            PROVIDER_NAME = "mock_prov"
            def list_models(self): return []
            async def generate_response(self, *args, **kwargs): return ""
            
        # Create a fake module object
        class FakeModule:
            pass
        
        mod = FakeModule()
        mod.MockProvider = MockProvider
        mod.Calculus = int # Ignored
        
        with patch("src.security.BudgetManager"), \
             patch("src.tools.LLMManager._discover_providers"): # Don't run auto discovery
             
            manager = LLMManager()
            manager._register_providers_from_module(mod)
            
            self.assertIn("mock_prov", manager.provider_classes)
            self.assertEqual(manager.provider_classes["mock_prov"], MockProvider)

    def test_discover_plugins(self):
        """Test plugin discovery logic"""
        with patch("os.path.exists", return_value=True), \
             patch("pkgutil.iter_modules") as mock_iter, \
             patch("importlib.import_module") as mock_import:
             
             # Mock plugin found
             mock_iter.return_value = [(None, "my_plugin", False)]
             
             mock_plugin_mod = MagicMock()
             from src.providers.base import LLMProvider
             class PluginProvider(LLMProvider):
                 PROVIDER_NAME = "plugin_prov"
                 def list_models(self): return []
                 async def generate_response(self, *args, **kwargs): return ""
             
             mock_plugin_mod.Plugin = PluginProvider
             mock_import.return_value = mock_plugin_mod
             
             with patch("src.security.BudgetManager"):
                 # We want to force _discover_providers to run the plugin part
                 # It checks os.getcwd()/plugins
                 manager = LLMManager()
                 self.assertIn("plugin_prov", manager.provider_classes)

    def test_get_provider_error_handling(self):
        with patch("src.security.BudgetManager"):
            manager = LLMManager()
            
            # 1. Unknown provider
            with self.assertRaises(ValueError):
                manager._get_provider("non_existent")
            
            # 2. Instantiation Error
            # Register a broken class
            class BrokenProvider:
                PROVIDER_NAME = "broken"
                def __init__(self): raise Exception("Boom")
            
            manager.provider_classes["broken"] = BrokenProvider
            
            with self.assertRaises(RuntimeError):
                manager._get_provider("broken")
