"""
Script to list available Gemini models
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available Gemini models...\n")

try:
    models = genai.list_models()
    print("Available models:")
    print("-" * 60)
    for model in models:
        name = model.name
        supported_methods = model.supported_generation_methods
        print(f"Model: {name}")
        print(f"  Supported methods: {supported_methods}")
        if 'generateContent' in supported_methods:
            print(f"  ✅ Supports generateContent")
        print()
except Exception as e:
    print(f"Error listing models: {e}")
    import traceback
    traceback.print_exc()

