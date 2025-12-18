import os
import json
import re
import datetime
from typing import Any, Dict, Optional

class SessionRecorder:
    def __init__(self, base_dir: str = "orchestrator_artifacts"):
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
