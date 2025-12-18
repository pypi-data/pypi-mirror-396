#!/usr/bin/env python3
"""
E2E CLI Verification Script.
Runs 'mcp' commands via subprocess to verify the full application lifecycle.
"""

import subprocess
import sys
import os

def run_command(name, cmd_list):
    print(f"\n--- Testing Command: {name} ---")
    print(f"Executing: {' '.join(cmd_list)}")
    
    try:
        # Use existing python environment
        full_cmd = [sys.executable, "-m", "src.cli"] + cmd_list
        result = subprocess.run(
            full_cmd, 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        if result.returncode == 0:
            print(f"✅ Success!")
            # Print a snippet of output to verify content
            print(f"Output Snippet: {result.stdout.strip()[:200]}...")
            return True
        else:
            print(f"❌ Failed (Return Code {result.returncode})")
            print(f"Stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    print("🚀 Starting E2E CLI Verification")
    
    # Define scenarios
    scenarios = [
        (
            "Debate (OpenAI Drafter, Anthropic Reviewer)",
            ["debate", "Why is Python great?", "--drafter-provider", "openai", "--drafter-model", "gpt-4o", "--reviewers", "anthropic:claude-3-opus", "--max-turns", "2"]
        ),
        (
            "Round Table (OpenAI & Anthropic)",
            ["round_table", "Is functional programming better than OOP?", "--panelists", "openai:gpt-4o", "anthropic:claude-3-5-sonnet-20240620", "--moderator", "openai"]
        ),
        (
            "Review (OpenAI Reviewer)",
            ["review", "src/cli.py", "--reviewers", "openai:gpt-4o"]
        )
    ]
    
    results = {}
    for name, cmd in scenarios:
        results[name] = run_command(name, cmd)
        
    print("\n\n=== Final Summary ===")
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name.ljust(40)}: {status}")
        if not passed: all_passed = False
        
    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
