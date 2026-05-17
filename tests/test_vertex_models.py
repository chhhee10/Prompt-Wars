import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="gen-lang-client-0301002559", location="us-central1")

models = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-2.0-flash-exp",
    "gemini-1.5-pro",
    "gemini-2.5-flash"
]

for m in models:
    print(f"Testing Vertex model: {m}...")
    try:
        model = GenerativeModel(m)
        response = model.generate_content("Reply with 'OK'.")
        print(f"SUCCESS: {m} -> {response.text.strip()}")
        break
    except Exception as e:
        print(f"FAILED: {m} -> {e}")
