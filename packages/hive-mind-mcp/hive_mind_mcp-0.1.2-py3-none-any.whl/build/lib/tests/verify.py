import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.server"],
        env=os.environ.copy()
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print("Tools available:", [t.name for t in tools.tools])
            
            # Call list_models
            try:
                models = await session.call_tool("list_models", {})
                print("Models result:", models.content)
            except Exception as e:
                print(f"Error calling list_models: {e}")

if __name__ == "__main__":
    asyncio.run(main())
