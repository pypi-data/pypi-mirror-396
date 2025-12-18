#!/usr/bin/env python3
"""
Integration Test Script: Verify All Providers with Real API Calls.
Requirement: Make at least 3 calls to each provider.
"""

import asyncio
import os
import sys
import time
from typing import List

# Ensure src is in path
sys.path.append(os.getcwd())

from src.tools import LLMManager
from src.providers.base import LLMProvider
from src.logger import get_logger

logger = get_logger("integration_test")

async def test_provider(provider_name: str, provider: LLMProvider):
    print(f"\n--- Testing Provider: {provider_name} ---")
    
    # Simple prompt
    messages = [{"role": "user", "content": "Say 'OK' and nothing else."}]
    
    # Use default model or valid model
    # Most providers list models, we pick the first one or a known default.
    models = provider.list_models()
    if not models:
        print(f"❌ {provider_name}: No models returned.")
        return False
        
    model = models[0]
    # Handle descriptive strings in list_models (e.g. from generic)
    if " " in model: 
        model = "gpt-3.5-turbo" # Fallback for generic
    if "generic" in provider_name:
         model = "llama3" # Typical local default
    
    print(f"   Using model: {model}")
    
    success_count = 0
    latencies = []
    
    for i in range(1, 4):
        print(f"   Call {i}/3...", end="", flush=True)
        start_t = time.time()
        try:
            resp = await provider.generate_response(model, messages)
            duration = time.time() - start_t
            latencies.append(duration)
            print(f" ✅ Success ({duration:.2f}s) -> '{resp.strip()[:20]}...'")
            success_count += 1
        except Exception as e:
            print(f" ❌ Failed: {str(e)}")
            # Don't break, try next call
            
    avg_latency = sum(latencies)/len(latencies) if latencies else 0
    print(f"   Results: {success_count}/3 passed. Avg Latency: {avg_latency:.2f}s")
    return success_count == 3

async def main():
    print("🚀 Starting Integration Tests (Real API Calls)")
    print("   Target: 3 calls per provider")
    
    manager = LLMManager()
    
    # We want to test ALL registered provider classes,
    # regardless of whether LLMManager initialized them (it only inits generic usually?)
    # No, LLMManager.providers is a cache. provider_classes has the types.
    
    results = {}
    
    for name, cls in manager.provider_classes.items():
        try:
            # Instantiate provider (might fail if env vars missing)
            # Some inits take args, but our standard is mostly arg-less or optional
            # Groq takes headers? check code.
            # Groq init signature: `def __init__(self, model: str = None, timeout: int = 300)`
            # Mistral: `def __init__(self, api_key=None, timeout=None)`
            # We rely on env vars being present.
            
            provider = cls() 
            results[name] = await test_provider(name, provider)
            
        except ValueError as e:
            print(f"\n⚠️ Skipping {name}: {str(e)} (Missing Configuration)")
            results[name] = "Skipped"
        except Exception as e:
            print(f"\n❌ Eror Init {name}: {str(e)}")
            results[name] = "Error"

    print("\n\n=== Final Summary ===")
    for p, res in results.items():
        status = "✅ PASS" if res is True else "⚠️ SKIP" if res == "Skipped" else "❌ FAIL"
        print(f"{p.ljust(15)}: {status}")

if __name__ == "__main__":
    asyncio.run(main())
