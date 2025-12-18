from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Optional
from .tools import LLMManager
from src.logger import configure_logger, get_logger

# Configure logger (globally for the process)
configure_logger()
logger = get_logger("server")

# Initialize the FastMCP server
mcp = FastMCP("mcp-llm-orchestrator")
manager = LLMManager()

@mcp.tool()
async def chat_completion(
    provider: str, 
    model: str, 
    messages: List[Dict[str, str]], 
    system_prompt: Optional[str] = None
) -> str:
    """
    Generate a chat completion using the specified LLM provider.
    
    Args:
        provider: The provider to use ('openai' or 'anthropic').
        model: The model identifier (e.g. 'gpt-4o', 'claude-3-5-sonnet').
        messages: List of message objects with 'role' and 'content'.
        system_prompt: Optional system instructions.
    """
    return await manager.chat_completion(provider, model, messages, system_prompt)

@mcp.tool()
def list_models() -> Dict[str, List[str]]:
    """
    List available models from configured providers.
    """
    return manager.list_models()

@mcp.tool()
async def collaborative_refine(
    prompt: str,
    drafter_model: Optional[str] = None,
    reviewers: Optional[List[Dict[str, str]]] = None,
    max_turns: int = 3,
    drafter_provider: Optional[str] = None,
) -> str:
    """
    Orchestrate a debate between a drafter and a Council of Reviewers.
    
    Args:
        prompt: The initial user request.
        drafter_model: (Optional) Model ID for the drafter. Defaults to env config.
        reviewers: (Optional) List of dicts. Defaults to env config.
        max_turns: Maximum number of refinement loops.
        drafter_provider: (Optional) Provider. Defaults to env config.
    """
    return await manager.collaborative_refine(
        prompt, 
        drafter_model, 
        reviewers,
        max_turns, 
        drafter_provider, 
    )

@mcp.tool()
async def evaluate_content(
    content: str,
    reviewers: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Submit content for peer review by the Council of Experts.
    
    Args:
        content: The text/code to evaluate.
        reviewers: (Optional) List of reviewers. Defaults to env config.
    """
    return await manager.evaluate_content(content, reviewers)

@mcp.tool()
async def round_table_debate(
    prompt: str,
    panelists: Optional[List[Dict[str, str]]] = None,
    moderator_provider: str = "openai",
) -> str:
    """
    Run a full Round Table: Parallel generation -> Cross-Critique -> Consensus Synthesis.
    Args:
        prompt: The problem to solve.
        panelists: (Optional) List of models to participate.
        moderator_provider: Provider to synthesize the final answer.
    """
    return await manager.round_table_debate(prompt, panelists, moderator_provider)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
