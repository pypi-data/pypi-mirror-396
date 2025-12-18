import argparse
import asyncio
import os
import sys
import fnmatch
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Ensure src can be imported if running from root
sys.path.append(os.getcwd())

from src.tools import LLMManager
from src.logger import configure_logger, get_logger

# Initialize logger
configure_logger()
logger = get_logger("cli")

def parse_kv(items: Optional[List[str]]) -> Optional[List[Dict[str, str]]]:
    """Parse list of 'provider:model' strings into dicts."""
    if not items:
        return None
    result = []
    for item in items:
        try:
            provider, model = item.split(":", 1)
            result.append({"provider": provider, "model": model})
        except ValueError:
            logger.warning("invalid_reviewer_format", item=item, expected="provider:model")
    return result

def resolve_paths(paths: List[str]) -> List[str]:
    """Resolve directories to a list of file paths."""
    resolved = []
    for path in paths:
        if os.path.isfile(path):
            resolved.append(path)
        elif os.path.isdir(path):
             for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(('.py', '.md', '.txt', '.json', '.yaml', '.yml', '.js', '.ts', '.html', '.css', '.env', '.sh', '.sql')):
                         resolved.append(os.path.join(root, file))
    return resolved

def collect_context_content(paths: List[str]) -> str:
    """Read files or directories (recursively) and return collected context."""
    context_content = ""
    # Use the shared resolver
    files_to_read = resolve_paths(paths)
    logger.info("loading_context", count=len(files_to_read))

    for file_path in files_to_read:
        try:
            with open(file_path, 'r', errors='ignore') as f:
                 context_content += f"\n--- Context from {file_path} ---\n{f.read()}\n"
        except Exception as e:
             logger.warning("context_read_error", file=file_path, error=str(e))
             
    return context_content

async def run_debate(args):
    manager = LLMManager()
    reviewers = parse_kv(args.reviewers)
    
    logger.info("starting_debate", topic=args.prompt)
    
    
    context_content = ""
    if args.context:
         if args.map_reduce:
             # Use the new Universal Map-Reduce
             files = resolve_paths(args.context)
             context_content = await manager.map_reduce_context(files)
         else:
             context_content = collect_context_content(args.context)


    result = await manager.collaborative_refine(
        prompt=args.prompt,
        drafter_model=args.drafter_model,
        drafter_provider=args.drafter_provider,
        reviewers=reviewers,
        max_turns=args.max_turns,
        context=context_content if context_content else None
    )
    print(result)

async def run_review(args):
    manager = LLMManager()
    reviewers = parse_kv(args.reviewers)
    
    # If content is a file path, read it
    
    # If content is a file path or directory, read it using our context collector
    content = args.content
    if os.path.exists(content):
        if args.map_reduce:
             files = resolve_paths([content])
             content = await manager.map_reduce_context(files)
        else:
             content = collect_context_content([content])
            
    logger.info("starting_peer_review")
    result = await manager.evaluate_content(
        content=content,
        reviewers=reviewers
    )
    print(result)

async def run_round_table(args):
    manager = LLMManager()
    panelists = parse_kv(args.panelists)
    
    # Default panel if none provided (logic usually in tool.py, but explicit here for CLI help)
    if not panelists:
        # We rely on tool.py defaults, or user passed flags
        pass 
        
    logger.info("starting_round_table", topic=args.prompt)
    
    
    context_content = ""
    if args.context:
        if args.map_reduce:
             files = resolve_paths(args.context)
             context_content = await manager.map_reduce_context(files)
        else:
             context_content = collect_context_content(args.context)


    result = await manager.round_table_debate(
        prompt=args.prompt,
        panelists=panelists,
        moderator_provider=args.moderator,
        context=context_content if context_content else None
    )
    print(result)

async def run_analyze(args):
    manager = LLMManager()
    panelists = parse_kv(args.panelists)
    
    # Collect all file paths
    collected_files = []
    for p in args.paths:
        if os.path.isfile(p):
            collected_files.append(p)
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for file in files:
                    full_path = os.path.join(root, file)
                    # Check exclusions
                    if args.exclude:
                        should_exclude = False
                        for pattern in args.exclude:
                             if fnmatch.fnmatch(file, pattern) or fnmatch.fnmatch(full_path, pattern):
                                 should_exclude = True
                                 break
                        if should_exclude:
                            continue
                            
                    if file.endswith(('.py', '.md', '.txt')): # Basic filter
                         collected_files.append(full_path)
    
    logger.info("starting_analysis", file_count=len(collected_files), topic=args.prompt)
    result = await manager.analyze_project(
        file_paths=collected_files,
        prompt=args.prompt,
        panelists=panelists
    )
    print(result)

async def run_init(args):
    """Scaffold a new MCP Orchestrator project in the current directory."""
    print(f"🚀 Initializing MCP Orchestrator in {os.getcwd()}...")
    
    # 1. Create .gitignore
    gitignore_path = ".gitignore"
    gitignore_content = "\n# Orchestrator Artifacts\n.hive_mind/\noutputs/\n\n# Env\n.env\n"
    
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore")
    else:
        # Check if already ignored
        with open(gitignore_path, "r") as f:
            current_content = f.read()
            
        if ".hive_mind" not in current_content or ".env" not in current_content:
            print("⚠️  .gitignore exists but might be missing critical ignores.")
            should_append = input("❓ Append defaults (.hive_mind/, .env) to .gitignore? [y/N] ").lower() == 'y'
            if should_append:
                with open(gitignore_path, "a") as f:
                    f.write(gitignore_content)
                print("✅ Updated .gitignore")
            else:
                print("ℹ️  Skipped .gitignore update. PLEASE MANUALLY IGNORE '.hive_mind/' and '.env'!")
        else:
            print("ℹ️  .gitignore already valid (skipped)")

    # 2. Create .env scaffold
    env_path = ".env"
    if not os.path.exists(env_path):
        retention = input("🗑️  Enable automated cleanup of old sessions? (Default: 30 days) [Y/n] ")
        retention_days = "30"
        if retention.lower() == 'n':
            retention_days = "0"
            print("   -> Cleanup disabled.")
        else:
            print("   -> Retention set to 30 days.")

        with open(env_path, "w") as f:
            f.write(f"# API Keys\nOPENAI_API_KEY=\nANTHROPIC_API_KEY=\nDEEPSEEK_API_KEY=\n\n# Security\nDAILY_BUDGET_USD=2.00\n\n# Maintenance\nARTIFACT_RETENTION_DAYS={retention_days}\n")
        print("✅ Created .env (Please fill in your keys!)")
    else:
        print("ℹ️  .env already exists (skipped)")

    # 3. Create .mcp/ directory
    mcp_dir = ".mcp"
    if not os.path.exists(mcp_dir):
        os.makedirs(mcp_dir)
        with open(os.path.join(mcp_dir, "config.toml"), "w") as f:
            f.write("# Project Configuration\n[orchestrator]\nproject_name = 'my_project'\n")
        print("✅ Created .mcp/config.toml")
    else:
        print("ℹ️  .mcp/ directory already exists (skipped)")
        
    print("\n🎉 Done! You can now run 'mcp-orchestrator round_table \"Topic\"'")

def find_free_port(start_port: int, max_retries: int = 10) -> int:
    """Find a free port starting from start_port."""
    import socket
    for port in range(start_port, start_port + max_retries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) != 0:
                return port
    raise RuntimeError(f"Could not find a free port between {start_port} and {start_port + max_retries}")

async def run_dashboard(args):
    """Launch the Streamlit dashboard."""
    import subprocess
    import sys
    
    # 1. Ensure artifacts dir exists
    if not os.path.exists(".hive_mind"):
        print("Warning: '.hive_mind' directory not found. Dashboard main be empty.")

    # 2. Path to dashboard script
    script_path = os.path.join(os.path.dirname(__file__), "dashboard.py")
    
    # 3. Launch Streamlit
    print("📊 Launching Dashboard...")
    cmd = [sys.executable, "-m", "streamlit", "run", script_path, "--server.port", "8503"]
    
    try:
        # Run and wait
        process = subprocess.Popen(cmd)
        await asyncio.to_thread(process.wait)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
        process.terminate()

async def run_config(args):
    """Open the global configuration file in default editor."""
    import shutil
    
    config_dir = os.path.expanduser("~/.mcp_orchestrator")
    config_path = os.path.join(config_dir, ".env")
    
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(f"Created config directory: {config_dir}")
        
    if not os.path.exists(config_path):
        # Copy template if exists or create empty
        base_env = ".env.example"
        if os.path.exists(base_env):
            shutil.copy(base_env, config_path)
            print("Initialized config from .env.example")
        else:
            with open(config_path, "w") as f:
                f.write("# MCP Orchestrator Configuration\n")
            print("Created empty config file.")
    
    print(f"Opening config file: {config_path}")
    
    # Try opening in editor
    editor = os.getenv("EDITOR", "nano")
    if shutil.which("code"):
        editor = "code"
    elif shutil.which("vim"):
        editor = "vim"
        
    import subprocess
    subprocess.call([editor, config_path])

async def run_models(args):
    """List available models, optionally filtered by search term or provider."""
    manager = LLMManager()
    print("🔍 Discovering models... (this may take a moment)")
    
    # This triggers dynamic discovery
    models_data = manager.list_models()
    
    print(f"\n--- Available Models ---")
    total_matches = 0
    
    for provider, models in sorted(models_data.items()):
        # Filter by provider if specified
        if args.provider and args.provider.lower() != provider.lower():
            continue
            
        # Filter models by search term
        filtered_models = []
        for m in models:
            full_id = f"{provider}:{m}"
            if not args.search or (args.search.lower() in full_id.lower()):
                filtered_models.append(m)
        
        if filtered_models:
            print(f"\n📦 {provider.upper()} ({len(filtered_models)})")
            for m in filtered_models:
                print(f"  • {provider}:{m}")
            total_matches += len(filtered_models)
            
    if total_matches == 0:
        print("\n❌ No models found matching your criteria.")
    else:
        print(f"\nTotal: {total_matches} models found.")

def main():
    load_dotenv()
    
def get_parser(parser_cls=argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser."""
    parser = parser_cls(
        description="MCP LLM Orchestrator CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Config Command
    config_parser = subparsers.add_parser("config", help="Edit global configuration")
    config_parser.set_defaults(func=run_config)
    
    # Debate Command
    debate_parser = subparsers.add_parser("debate", help="Run a collaborative refinement debate")
    debate_parser.add_argument("prompt", help="The initial prompt or task")
    debate_parser.add_argument("--drafter-provider", default="openai", help="Provider for the drafter")
    debate_parser.add_argument("--drafter-model", default="gpt-4o", help="Model for the drafter")

    debate_parser.add_argument("--reviewers", nargs="+", help="List of reviewers in 'provider:model' format", default=[])
    debate_parser.add_argument("--max-turns", type=int, default=3, help="Maximum refinement loops")
    debate_parser.add_argument("--context", nargs="+", help="List of files to provide as context", default=[])
    debate_parser.add_argument("--map-reduce", action="store_true", help="Summarize context using Map-Reduce before debating")
    debate_parser.set_defaults(func=run_debate)
    
    # Review Command
    review_parser = subparsers.add_parser("review", help="Peer review existing content")
    review_parser.add_argument("content", help="Content string or path to file")
    review_parser.add_argument("--reviewers", nargs="+", help="List of reviewers in 'provider:model' format", default=[])
    review_parser.add_argument("--map-reduce", action="store_true", help="Summarize content using Map-Reduce before reviewing")
    review_parser.set_defaults(func=run_review)
    
    # Round Table Command
    rt_parser = subparsers.add_parser("round_table", help="Run a multi-model round table consensus")
    rt_parser.add_argument("prompt", help="The topic or question")
    rt_parser.add_argument("--panelists", nargs="+", help="Panelists in 'provider:model' format", default=[])
    rt_parser.add_argument("--moderator", default="openai", help="Moderator provider")
    rt_parser.add_argument("--context", nargs="+", help="List of files to provide as context", default=[])
    rt_parser.add_argument("--map-reduce", action="store_true", help="Summarize context using Map-Reduce before debating")
    rt_parser.set_defaults(func=run_round_table)

    # Analyze Command (Map-Reduce)
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a project or files using Map-Reduce")
    analyze_parser.add_argument("paths", nargs="+", help="Files or directories to analyze")
    analyze_parser.add_argument("prompt", help="The question or task")
    analyze_parser.add_argument("--panelists", nargs="+", help="Panelists for Reduce phase", default=[])
    analyze_parser.add_argument("--exclude", nargs="+", help="Glob patterns to exclude from analysis", default=[])
    analyze_parser.set_defaults(func=run_analyze)

    # Init Command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.set_defaults(func=run_init)

    # Dashboard Command
    dash_parser = subparsers.add_parser("dashboard", help="Launch the Observability Dashboard")
    dash_parser.set_defaults(func=run_dashboard)
    
    # Models Command
    models_parser = subparsers.add_parser("models", help="List and search available models")
    models_parser.add_argument("--search", help="Filter by name (e.g. 'claude')")
    models_parser.add_argument("--provider", help="Filter by provider (e.g. 'openai')")
    models_parser.set_defaults(func=run_models)
    
    return parser

def parse_args(args=None):
    """Parse command line arguments."""
    parser = get_parser()
    return parser.parse_args(args)

def main():
    load_dotenv()
    
    args = parse_args()
    
    try:
        asyncio.run(args.func(args))
    except KeyboardInterrupt:
        logger.warning("operation_cancelled")
    except Exception as e:
        logger.error("cli_error", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
