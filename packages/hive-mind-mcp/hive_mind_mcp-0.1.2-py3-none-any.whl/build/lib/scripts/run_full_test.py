
import subprocess
import sys
import os
import random
import time

# List of core models to guarantee 5 calls for
CORE_MODELS = [
    "openai:gpt-4o",
    "anthropic:claude-sonnet-4-5-20250929",
    "deepseek:deepseek-coder",
    "mistral:mistral-large-latest",
    "groq:llama-3.3-70b-versatile",
    "openai:o1-preview",
    "anthropic:claude-opus-4-5-20251101"
    # Keeping it to 7 to ensure frequency
]

COMMANDS = ["analyze", "debate", "review", "round_table"]

def run_command(cmd_args, env_vars):
    cmd = [sys.executable, "-m", "src.cli"] + cmd_args
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, env={**os.environ, **env_vars}, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        return False

def main():
    usage_counts = {m: 0 for m in CORE_MODELS}
    
    # We will run loops until min usage is met.
    # To prevent infinite loops if something fails, we cap it.
    max_cycles = 15
    cycle = 0
    
    print("🚀 Starting Test Suite...")
    print(f"Target Models: {len(CORE_MODELS)}")
    
    env_vars = {
        "DAILY_BUDGET_USD": "100.00",
        "LOG_LEVEL": "ERROR" # keep output clean
    }

    while min(usage_counts.values()) < 5 and cycle < max_cycles:
        cycle += 1
        print(f"\n=== CYCLE {cycle} ===")
        
        # 1. DEBATE
        # Needs: Drafter (1), Reviewers (2)
        drafter = random.choice(CORE_MODELS)
        reviewers = random.sample([m for m in CORE_MODELS if m != drafter], 2)
        
        provider, model = drafter.split(":", 1)
        r_args = []
        for r in reviewers:
            r_args.extend(["--reviewers", r])
            
        args = ["debate", "Is Rust better than C++?", 
                "--drafter-provider", provider, 
                "--drafter-model", model,
                "--max-turns", "1"] + r_args
        
        if run_command(args, env_vars):
            usage_counts[drafter] += 1
            for r in reviewers: usage_counts[r] += 1

        # 2. REVIEW
        # Needs: Reviewers (2)
        reviewers = random.sample(CORE_MODELS, 2)
        r_args = []
        for r in reviewers:
            r_args.extend(["--reviewers", r])
            
        # Review this script itself
        args = ["review", "scripts/run_full_test.py"] + r_args
        
        if run_command(args, env_vars):
            for r in reviewers: usage_counts[r] += 1

        # 3. ROUND TABLE
        # Needs: Panelists (3)
        panelists = random.sample(CORE_MODELS, 3)
        p_args = []
        for p in panelists:
            p_args.extend(["--panelists", p])
            
        args = ["round_table", "What is the future of AI agents?"] + p_args
        
        if run_command(args, env_vars):
            for p in panelists: usage_counts[p] += 1

        # 4. ANALYZE
        # Needs: Panelists (2)
        panelists = random.sample(CORE_MODELS, 2)
        p_args = []
        for p in panelists:
            p_args.extend(["--panelists", p])
            
        # Analyze README
        args = ["analyze", "README.md", "Summarize this project"] + p_args
        
        if run_command(args, env_vars):
            for p in panelists: usage_counts[p] += 1
            
        # Status Update
        print("\n--- Usage Counts ---")
        for m, c in usage_counts.items():
            print(f"{m}: {c}")


    print("\n✅ Test Suite Completed!")
    print("Final Counts:")
    for m, c in usage_counts.items():
        print(f"{m}: {c}")

if __name__ == "__main__":
    main()
