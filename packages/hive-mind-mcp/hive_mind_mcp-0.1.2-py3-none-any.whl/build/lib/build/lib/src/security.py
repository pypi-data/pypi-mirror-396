import time
import json
import os
from pathlib import Path
from typing import Dict, Optional

class TokenBucket:
    """
    Standard Token Bucket algorithm for Rate Limiting.
    tokens: current available tokens
    rate: tokens refilled per second
    capacity: max burst size
    """
    def __init__(self, rate: float, capacity: float):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()

    def consume(self, amount: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now

        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False

class BudgetManager:
    """
    Tracks estimated cost usage to prevent bill shock.
    """
    def __init__(self, budget_limit_usd: float = 1.0):
        self.budget_limit = budget_limit_usd
        self.usage_file = Path(os.path.expanduser("~/.mcp_orchestrator/usage.json"))
        self._ensure_file()

    def _ensure_file(self):
        if not self.usage_file.exists():
            self.usage_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_usage({"total_usd": 0.0, "history": []})

    def _load_usage(self) -> Dict:
        try:
            with open(self.usage_file, "r") as f:
                return json.load(f)
        except:
             return {"total_usd": 0.0}

    def _save_usage(self, data: Dict):
        with open(self.usage_file, "w") as f:
            json.dump(data, f, indent=2)

    def check_budget(self) -> bool:
        data = self._load_usage()
        current = data.get("total_usd", 0.0)
        return current < self.budget_limit

    def add_cost(self, usd_amount: float, provider: str, model: str):
        data = self._load_usage()
        data["total_usd"] = data.get("total_usd", 0.0) + usd_amount
        
        # Keep a small history log (last 100 entries)
        if "history" not in data:
            data["history"] = []
            
        entry = {
            "timestamp": time.time(),
            "provider": provider,
            "model": model,
            "cost": usd_amount
        }
        data["history"].append(entry)
        if len(data["history"]) > 100:
            data["history"] = data["history"][-100:]
            
        self._save_usage(data)

    def get_status(self) -> str:
        data = self._load_usage()
        return f"${data.get('total_usd', 0.0):.4f} / ${self.budget_limit:.2f}"

class BudgetAwareProviderWrapper:
    """
    Wraps an LLMProvider to enforce budget checks and track usage transparently.
    """
    def __init__(self, provider, budget_manager: BudgetManager, provider_name: str):
        self.provider = provider
        self.budget_manager = budget_manager
        self.provider_name = provider_name
        
    async def generate_response(self, model: str, messages, system_prompt: Optional[str] = None) -> str:
        if not self.budget_manager.check_budget():
            raise Exception(f"Daily Budget Limit Exceeded! Status: {self.budget_manager.get_status()}")
            
        # Estimated cost tracking (Hardcoded avg price for now)
        # TODO: Implement per-model pricing in v2.1
        estimated_cost = 0.002 
        
        response = await self.provider.generate_response(model, messages, system_prompt)
        
        # Track successes
        self.budget_manager.add_cost(estimated_cost, self.provider_name, model)
        return response
        
    def __getattr__(self, name):
        # Delegate other methods (list_models, etc.)
        return getattr(self.provider, name)
