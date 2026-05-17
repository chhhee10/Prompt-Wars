import os
from agents.pipeline import analyze_document
from parser import extract_text
import json

# User's text
test_contract = "By clicking agree, you grant the company full rights to share your data with third-party partners. Additionally, you waive all rights to a jury trial and agree to mandatory binding arbitration."

def main():
    text = extract_text(test_contract)
    result = analyze_document(text, language="hi")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
