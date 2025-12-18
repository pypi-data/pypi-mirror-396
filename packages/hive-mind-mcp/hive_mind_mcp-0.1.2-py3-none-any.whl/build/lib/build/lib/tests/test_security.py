import unittest
from unittest.mock import patch, mock_open, MagicMock, AsyncMock
import json
import time
from src.security import BudgetManager, TokenBucket

class TestBudgetManager(unittest.TestCase):
    def setUp(self):
        self.mock_usage_file = "/tmp/mock_usage.json"
        
    def test_init_creates_file(self):
        with patch("pathlib.Path.exists", return_value=False), \
             patch("pathlib.Path.mkdir"), \
             patch("builtins.open", mock_open()) as mock_file:
            
            manager = BudgetManager(budget_limit_usd=5.0)
            mock_file.assert_called()
            # Verify initial structure written
            handle = mock_file()
            handle.write.assert_called()

    def test_check_budget_under(self):
        with patch("src.security.BudgetManager._load_usage", return_value={"total_usd": 1.0}):
            manager = BudgetManager(budget_limit_usd=5.0)
            self.assertTrue(manager.check_budget())

    def test_check_budget_exceeded(self):
        with patch("src.security.BudgetManager._load_usage", return_value={"total_usd": 6.0}):
            manager = BudgetManager(budget_limit_usd=5.0)
            self.assertFalse(manager.check_budget())

    def test_add_cost(self):
        mock_data = {"total_usd": 1.0, "history": []}
        
        with patch("src.security.BudgetManager._load_usage", return_value=mock_data), \
             patch("src.security.BudgetManager._save_usage") as mock_save:
            
            manager = BudgetManager(budget_limit_usd=5.0)
            manager.add_cost(0.5, "openai", "gpt-4")
            
            # Verify usage updated
            self.assertEqual(mock_data["total_usd"], 1.5)
            self.assertEqual(len(mock_data["history"]), 1)
            self.assertEqual(mock_data["history"][0]["provider"], "openai")
            
            mock_save.assert_called_with(mock_data)

    def test_get_status(self):
        with patch("src.security.BudgetManager._load_usage", return_value={"total_usd": 2.5}):
            manager = BudgetManager(budget_limit_usd=10.0)
            status = manager.get_status()
            self.assertEqual(status, "$2.5000 / $10.00")

class TestTokenBucket(unittest.TestCase):
    @patch("time.time")
    def test_consume_success(self, mock_time):
        mock_time.return_value = 1000.0
        bucket = TokenBucket(rate=1.0, capacity=10.0)
        
        # Initial fill
        self.assertEqual(bucket.tokens, 10.0)
        
        # Consume
        self.assertTrue(bucket.consume(5.0))
        self.assertEqual(bucket.tokens, 5.0)
        
        # Advance time by 1s
        mock_time.return_value = 1001.0
        # Accessing consume triggers refill
        self.assertTrue(bucket.consume(1.0))
        # 5.0 remaining + 1.0 refill - 1.0 consumed = 5.0?
        # refill: (1001-1000)*1.0 = 1.0. 
        # current = 5.0 + 1.0 = 6.0.
        # consume 1.0 -> 5.0.
        self.assertAlmostEqual(bucket.tokens, 5.0)

    def test_consume_fail(self):
        bucket = TokenBucket(rate=1.0, capacity=10.0)
        bucket.tokens = 0.5
        self.assertFalse(bucket.consume(1))

    def test_refill(self):
        bucket = TokenBucket(rate=10.0, capacity=10.0)
        bucket.tokens = 0.0
        bucket.last_update = time.time() - 1.0 # 1 second ago
        
        # Should refill 10 tokens
        self.assertTrue(bucket.consume(5))

class TestBudgetWrapper(unittest.IsolatedAsyncioTestCase):
    async def test_wrapper_calls_provider_and_tracks_cost(self):
        mock_provider = AsyncMock()
        mock_provider.generate_response.return_value = "Response"
        
        mock_budget = MagicMock()
        mock_budget.check_budget.return_value = True
        
        from src.security import BudgetAwareProviderWrapper
        wrapper = BudgetAwareProviderWrapper(mock_provider, mock_budget, "test_prov")
        
        resp = await wrapper.generate_response("model", [], "sys")
        
        self.assertEqual(resp, "Response")
        mock_provider.generate_response.assert_called_once()
        mock_budget.add_cost.assert_called_once()

    async def test_wrapper_blocks_on_budget(self):
        mock_provider = AsyncMock()
        mock_budget = MagicMock()
        mock_budget.check_budget.return_value = False
        mock_budget.get_status.return_value = "Over Limit"
        
        from src.security import BudgetAwareProviderWrapper
        wrapper = BudgetAwareProviderWrapper(mock_provider, mock_budget, "test_prov")
        
        with self.assertRaises(Exception) as logic:
            await wrapper.generate_response("model", [])
        
        self.assertIn("Budget Limit Exceeded", str(logic.exception))
        mock_provider.generate_response.assert_not_called()
