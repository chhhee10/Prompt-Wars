import os
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

models = [
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-3-flash-preview"
]

for m in models:
    print(f"Testing {m}...")
    try:
        model = genai.GenerativeModel(model_name=m)
        response = model.generate_content("Hello, this is a test. Reply with 'OK'.")
        print(f"SUCCESS: {m} -> {response.text.strip()}")
    except Exception as e:
        print(f"FAILED: {m} -> {e}")
