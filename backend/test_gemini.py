import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("API Key Loaded:", api_key[:10] + "..." if api_key else "No API Key Found")

genai.configure(api_key=api_key)

print("\nAvailable Models:\n")

for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(model.name)