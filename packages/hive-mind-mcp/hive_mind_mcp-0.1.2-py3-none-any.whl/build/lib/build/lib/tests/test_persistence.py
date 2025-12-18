
import unittest
import os
import shutil
import time
from src.persistence import SessionRecorder

class TestPersistence(unittest.TestCase):
    def setUp(self):
        self.test_dir = ".test_persistence_artifacts"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        self.recorder = SessionRecorder(base_dir=self.test_dir)
    
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_slugify(self):
        self.assertEqual(self.recorder._slugify("Hello World"), "hello-world")
        self.assertEqual(self.recorder._slugify("Test 123!"), "test-123")
        self.assertEqual(self.recorder._slugify("  Spaces  "), "spaces")

    def test_create_session_dir(self):
        path = self.recorder.create_session_dir("test_tool", "Test Topic")
        self.assertTrue(os.path.exists(path))
        self.assertIn("test_tool", path)
        self.assertIn("test-topic", path)

    def test_save_artifact(self):
        path = self.recorder.create_session_dir("tool", "topic")
        self.recorder.save_artifact(path, "test.txt", "content")
        with open(os.path.join(path, "test.txt"), "r") as f:
            self.assertEqual(f.read(), "content")

    def test_cleanup_old_sessions(self):
        # Create "old" session
        tool_dir = os.path.join(self.test_dir, "tool")
        os.makedirs(tool_dir)
        
        old_session = os.path.join(tool_dir, "old_session")
        os.makedirs(old_session)
        # Set mtime to 35 days ago
        old_time = time.time() - (35 * 86400)
        os.utime(old_session, (old_time, old_time))
        
        # Create "new" session
        new_session = os.path.join(tool_dir, "new_session")
        os.makedirs(new_session)
        
        # Run cleanup (30 days)
        self.recorder.cleanup_old_sessions(retention_days=30)
        
        self.assertFalse(os.path.exists(old_session), "Old session should be deleted")
        self.assertTrue(os.path.exists(new_session), "New session should remain")

if __name__ == "__main__":
    unittest.main()
