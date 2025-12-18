import asyncio
import os
import sys
from dotenv import load_dotenv

# Force load .env
load_dotenv()

async def test_openai():
    print(f"\n--- Testing OpenAI ---")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY missing")
    else:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key)
            print(f"Key found: {api_key[:8]}...")
            completion = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print(f"✅ Success! Response: {completion.choices[0].message.content}")
        except Exception as e:
            print(f"❌ Failed: {e}")

async def test_anthropic():
    print(f"\n--- Testing Anthropic ---")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY missing")
    else:
        # User indicates access to Haiku 3.5
        model = "claude-3-5-haiku-latest"
        print(f"Key found: {api_key[:8]}... Using model: {model}")
        
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=api_key)
            message = await client.messages.create(
                model=model,
                max_tokens=5,
                messages=[{"role": "user", "content": "Hello"}]
            )
            print(f"✅ Success! Response: {message.content[0].text}")
        except Exception as e:
            print(f"❌ Failed with '{model}': {e}")
            print("Trying fallback model: claude-3-haiku-20240307")
            try:
                 message = await client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=5,
                    messages=[{"role": "user", "content": "Hello"}]
                )
                 print(f"✅ Success with fallback! Response: {message.content[0].text}")
            except Exception as e2:
                 print(f"❌ Fallback Failed: {e2}")

async def test_deepseek():
    print(f"\n--- Testing DeepSeek ---")
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY missing")
    else:
        try:
            from openai import AsyncOpenAI
            # DeepSeek uses OpenAI client compatible
            client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            print(f"Key found: {api_key[:8]}...")
            completion = await client.chat.completions.create(
                model="deepseek-coder",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print(f"✅ Success! Response: {completion.choices[0].message.content}")
        except Exception as e:
            print(f"❌ Failed: {e}")

async def test_openrouter():
    print(f"\n--- Testing OpenRouter ---")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY missing")
    else:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(
                api_key=api_key, 
                base_url="https://openrouter.ai/api/v1",
                default_headers={"HTTP-Referer": "https://github.com/franciscojunqueira/hive-mind-mcp", "X-Title": "MCP LLM Orchestrator"}
            )
            print(f"Key found: {api_key[:8]}...")
            completion = await client.chat.completions.create(
                model="openrouter/auto",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print(f"✅ Success! Response: {completion.choices[0].message.content}")
        except Exception as e:
            print(f"❌ Failed: {e}")

async def test_groq():
    print(f"\n--- Testing Groq ---")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY missing")
    else:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            print(f"Key found: {api_key[:8]}...")
            completion = await client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print(f"✅ Success! Response: {completion.choices[0].message.content}")
        except Exception as e:
            print(f"❌ Failed: {e}")

async def test_mistral():
    print(f"\n--- Testing Mistral ---")
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("❌ MISTRAL_API_KEY missing")
    else:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key, base_url="https://api.mistral.ai/v1")
            print(f"Key found: {api_key[:8]}...")
            completion = await client.chat.completions.create(
                model="mistral-tiny",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print(f"✅ Success! Response: {completion.choices[0].message.content}")
        except Exception as e:
            print(f"❌ Failed: {e}")

async def test_gemini():
    print(f"\n--- Testing Gemini ---")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or "your_gemini_key_here" in api_key:
        print("❌ GEMINI_API_KEY missing or default")
    else:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')
            print(f"Key found: {api_key[:8]}...")
            response = await model.generate_content_async("Hello")
            print(f"✅ Success! Response: {response.text[:20]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")

async def main():
    print("Starting Comprehensive Auth Debug...")
    await test_openai()
    await test_anthropic()
    await test_deepseek()
    await test_openrouter()
    await test_groq()
    await test_mistral()
    await test_gemini()

if __name__ == "__main__":
    asyncio.run(main())
