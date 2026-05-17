import os
from agents.pipeline import analyze_document
from parser import extract_text
import json

# Dummy text
test_contract = """
TERMS OF SERVICE
1. The company reserves the right to charge a monthly fee of $99 without prior notice.
2. You agree to give up your right to sue us and must use binding arbitration in our state.
3. We may share your personal data with third-party partners at any time.
"""

def main():
    print("Testing extraction...")
    text = extract_text(test_contract)
    print("Extracted length:", len(text))
    
    print("\nRunning analyze_document...")
    result = analyze_document(text, language="en")
    print("\nResult:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
