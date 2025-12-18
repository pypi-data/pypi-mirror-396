import os
import json
import re
import datetime
from typing import Any, Dict, Optional

class SessionRecorder:
    def __init__(self, base_dir: str = ".hive_mind"):
        self.base_dir = base_dir
        
    def _slugify(self, text: str) -> str:
        """Create a filename-safe slug from a string."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        return text[:50]

    def create_session_dir(self, tool_name: str, topic: str) -> str:
        """Creates a timestamped directory for the session."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        slug = self._slugify(topic)
        session_dir = os.path.join(self.base_dir, tool_name, f"{timestamp}_{slug}")
        
        os.makedirs(session_dir, exist_ok=True)
        return session_dir

    def save_artifact(self, session_dir: str, filename: str, content: str):
        """Saves a text/markdown artifact."""
        path = os.path.join(session_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
            
    def save_metadata(self, session_dir: str, metadata: Dict[str, Any]):
        """Saves JSON metadata about the session."""
        path = os.path.join(session_dir, "metadata.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def cleanup_old_sessions(self, retention_days: int):
        """
        Deletes session directories older than retention_days.
        Structure is base_dir/tool_name/timestamp_slug.
        """
        if retention_days <= 0:
            return

        import time
        import shutil
        from src.logger import get_logger
        logger = get_logger("persistence")

        cutoff_time = time.time() - (retention_days * 86400)
        cleaned_count = 0

        if not os.path.exists(self.base_dir):
            return

        # Iterate over tool directories (e.g., .hive_mind/debate)
        for tool_name in os.listdir(self.base_dir):
            tool_path = os.path.join(self.base_dir, tool_name)
            if not os.path.isdir(tool_path):
                continue
            
            # Iterate over sessions (e.g., .hive_mind/debate/2023-10-01_topic)
            for session_name in os.listdir(tool_path):
                session_path = os.path.join(tool_path, session_name)
                if not os.path.isdir(session_path):
                    continue

                try:
                    # Check modification time
                    mtime = os.path.getmtime(session_path)
                    if mtime < cutoff_time:
                        shutil.rmtree(session_path)
                        cleaned_count += 1
                except Exception as e:
                    logger.warning("cleanup_failed", path=session_path, error=str(e))
        
        if cleaned_count > 0:
            logger.info("cleanup_completed", removed_sessions=cleaned_count, retention_days=retention_days)
