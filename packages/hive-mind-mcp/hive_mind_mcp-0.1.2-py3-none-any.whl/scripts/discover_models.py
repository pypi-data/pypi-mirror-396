
import sys
import os
sys.path.append(os.getcwd())
from src.tools import LLMManager
from dotenv import load_dotenv

load_dotenv()

def main():
    print("Initializing LLMManager...")
    manager = LLMManager()
    models = manager.list_models()
    
    available_models = []
    
    print("\n--- Discovered Models ---")
    for provider, model_list in models.items():
        for m in model_list:
            if "Error" not in m and "Generic" not in m:
                print(f"✅ {provider}: {m}")
                available_models.append((provider, m))
            else:
                print(f"❌ {provider}: {m}")
                
    if not available_models:
        print("\nNo working models found. Please check .env")
        sys.exit(1)
        
    print(f"\nTotal Valid Models: {len(available_models)}")

if __name__ == "__main__":
    main()
