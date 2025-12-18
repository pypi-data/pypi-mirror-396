
import asyncio
import os
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

async def main():
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("No API Key found")
        return

    print(f"Testing Anthropic with key ending in ...{api_key[-4:]}")
    
    client = AsyncAnthropic(api_key=api_key)
    print(f"Base URL: {client.base_url}")
    
    try:
        print("\n--- Listing Available Models ---")
        # Note: client.models may not exist in all versions, checking...
        # Also commonly models.list()
        # Newer SDKs use client.models.list()
        if hasattr(client, 'models'):
            async for model in await client.models.list():
                print(f" - {model.id}")
        else:
            print("Client has no 'models' attribute.")
            
    except Exception as e:
        print(f"❌ List Models Failed: {type(e).__name__}: {e}")

    models_to_test = [
        "claude-3-5-sonnet-20240620",
        "claude-3-5-sonnet-latest",
        "claude-3-opus-20240229"
    ]
    
    for model in models_to_test:
        print(f"\n--- Testing {model} ---")
        try:
            message = await client.messages.create(
                model=model,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": "Hello, world"}
                ]
            )
            print(f"✅ Success! Response: {message.content[0].text[:50]}...")
        except Exception as e:
            print(f"❌ Failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
