
import os
import urllib.request
import urllib.error

# Optimized for Dashboard (Size 40px)
ICONS = {
    "openai": [
        "https://cdn.simpleicons.org/openai",
        "https://avatars.githubusercontent.com/u/14957082?s=40&v=4"
    ],
    "anthropic": [
        "https://cdn.simpleicons.org/anthropic",
        "https://avatars.githubusercontent.com/u/79036324?s=40&v=4"
    ],
    "google": [
        "https://cdn.simpleicons.org/google",
        "https://avatars.githubusercontent.com/u/1342004?s=40&v=4"
    ],
    "gemini": [
        "https://cdn.simpleicons.org/googlegemini",
        "https://avatars.githubusercontent.com/u/1342004?s=40&v=4"
    ],
    "deepseek": [
        "https://avatars.githubusercontent.com/u/146768390?s=40&v=4"
    ],
    "mistral": [
        "https://cdn.simpleicons.org/mistralai",
        "https://avatars.githubusercontent.com/u/130635444?s=40&v=4"
    ],
    "groq": [
        "https://avatars.githubusercontent.com/u/104537243?s=40&v=4"
    ],
    "openrouter": [
        "https://avatars.githubusercontent.com/u/118365638?s=40&v=4"
    ]
}

TARGET_DIR = "src/assets/icons"
os.makedirs(TARGET_DIR, exist_ok=True)

def download_icon(name, urls):
    # Always overwrite to ensure size fix
    for url in urls:
        try:
            print(f"Trying {url} for {name}...")
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()
                
                ext = "svg"
                if b"<svg" in content: ext = "svg"
                elif b"PNG" in content[:4]: ext = "png"
                elif b"JFIF" in content[:20]: ext = "jpg"
                
                file_path = os.path.join(TARGET_DIR, f"{name}.{ext}")
                with open(file_path, "wb") as f:
                    f.write(content)
                print(f"✅ Downloaded {name} as {ext}")
                return
        except Exception as e:
            print(f"❌ Failed {url}: {e}")
    print(f"⚠️ Could not find icon for {name}")

for name, urls in ICONS.items():
    download_icon(name, urls)
