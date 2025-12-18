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

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="MCP LLM Orchestrator CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
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

    args = parser.parse_args()
    
    try:
        asyncio.run(args.func(args))
    except KeyboardInterrupt:
        logger.warning("operation_cancelled")
    except Exception as e:
        logger.error("cli_error", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
