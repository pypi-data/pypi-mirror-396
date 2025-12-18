import unittest
from unittest.mock import AsyncMock, patch
from src.server import chat_completion, list_models, collaborative_refine, evaluate_content, round_table_debate, manager

class TestMCPServer(unittest.IsolatedAsyncioTestCase):
    
    async def test_chat_completion(self):
        with patch.object(manager, 'chat_completion', new_callable=AsyncMock) as mock_method:
            mock_method.return_value = "Result"
            res = await chat_completion("p", "m", [])
            self.assertEqual(res, "Result")
            mock_method.assert_called_with("p", "m", [], None)

    def test_list_models(self):
         with patch.object(manager, 'list_models') as mock_method:
             mock_method.return_value = {"p": ["m"]}
             res = list_models()
             self.assertEqual(res, {"p": ["m"]})
             mock_method.assert_called_once()
             
    async def test_collaborative_refine(self):
        with patch.object(manager, 'collaborative_refine', new_callable=AsyncMock) as mock_method:
            mock_method.return_value = "Refined"
            res = await collaborative_refine("prompt")
            self.assertEqual(res, "Refined")
            # Verify defaults are passed
            mock_method.assert_called_with("prompt", None, None, 3, None)

    async def test_evaluate_content(self):
        with patch.object(manager, 'evaluate_content', new_callable=AsyncMock) as mock_method:
            mock_method.return_value = "Evaluated"
            res = await evaluate_content("content")
            self.assertEqual(res, "Evaluated")
            mock_method.assert_called_with("content", None)

    async def test_round_table_debate(self):
        with patch.object(manager, 'round_table_debate', new_callable=AsyncMock) as mock_method:
            mock_method.return_value = "Debated"
            res = await round_table_debate("prompt")
            self.assertEqual(res, "Debated")
            mock_method.assert_called_with("prompt", None, "openai")
