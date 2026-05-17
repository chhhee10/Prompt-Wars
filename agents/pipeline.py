import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

# Initialize Vertex AI with the specific project and region
vertexai.init(project="gen-lang-client-0301002559", location="us-central1")

# We use gemini-2.5-flash-lite, which is fully supported and exactly 50% cheaper than gemini-2.5-flash!
MODEL_NAME = "gemini-2.5-flash-lite"

def get_model(system_instruction: str = None):
    return GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_instruction
    )

def analyze_document(text: str, language: str = "en") -> dict:
    """
    Runs the 3 batched Gemini calls to analyze the document.
    """

    # ---------------------------------------------------------
    # CALL 1: PARSER + CLASSIFIER (Agent 1 & 2)
    # ---------------------------------------------------------
    sys_prompt_1 = """You are a legal AI. Extract and chunk clauses from the provided contract text.
    Classify each clause into one of these types: arbitration, IP, privacy, financial, termination, employment, or other.
    Output JSON with a list of 'clauses', each having 'clause_text' and 'clause_type'."""
    
    model_1 = get_model(system_instruction=sys_prompt_1)
    response_1 = model_1.generate_content(
        text,
        generation_config=GenerationConfig(response_mime_type="application/json", temperature=0.0)
    )
    
    try:
        clauses_data = json.loads(response_1.text)
        if isinstance(clauses_data, list):
            clauses = clauses_data
        else:
            clauses = clauses_data.get('clauses', [])
    except Exception:
        clauses = []
        
    if not clauses:
        return _fallback_error(f"Could not parse any clauses from the document. API Output: {response_1.text}")

    # ---------------------------------------------------------
    # CALL 2: ADVERSARY + BENCHMARK (Agent 3 & 4)
    # ---------------------------------------------------------
    sys_prompt_2 = """You are an adversarial legal expert. For each clause provided, assume worst intent and find hidden risks.
    Also, compare it against fair industry standards.
    Output JSON MUST be an array of objects matching the input list exactly, but adding these fields to each object: 
    'risk_level' (HIGH|MEDIUM|LOW), 
    'why_flagged' (reason in plain English), 
    'what_it_means' (practical implication), 
    'fair_version' (balanced clause), 
    'dark_pattern' (true/false), 
    'dark_pattern_type' (e.g., forced_consent, hidden_renewal, null)."""
    
    model_2 = get_model(system_instruction=sys_prompt_2)
    response_2 = model_2.generate_content(
        json.dumps(clauses),
        generation_config=GenerationConfig(response_mime_type="application/json", temperature=0.0)
    )
    
    try:
        analyzed_clauses = json.loads(response_2.text)
        # Handle cases where model returns an object with a list instead of a direct array
        if isinstance(analyzed_clauses, dict):
            for val in analyzed_clauses.values():
                if isinstance(val, list):
                    analyzed_clauses = val
                    break
        if not isinstance(analyzed_clauses, list):
             analyzed_clauses = clauses
    except Exception:
        analyzed_clauses = clauses

    # ---------------------------------------------------------
    # CALL 3: CONSEQUENCE SIMULATOR + EXPLAINER + RISK SCORER/TRANSLATOR (Agent 5, 6, 7)
    # ---------------------------------------------------------
    sys_prompt_3 = f"""You are a consumer rights advocate and translator. Review the analyzed clauses.
    For each clause, calculate risks, consequences, and translate explanations into {language}.

    Output JSON MUST EXACTLY match this structure:
    {{
      "document_type": "string (e.g. employment_contract, tos, rental)",
      "overall_risk_score": 0,
      "safe_to_sign": false,
      "power_imbalance": "string (e.g. Company: 90% / You: 10%)",
      "summary": "string (2 sentence summary)",
      "flagged_clauses": [
        {{
          "clause_text": "string",
          "clause_type": "string",
          "risk_level": "string",
          "confidence": 0.95,
          "why_flagged": "string",
          "what_it_means": "string",
          "fair_version": "string",
          "consequence": "string",
          "financial_impact": "string",
          "dark_pattern": false,
          "dark_pattern_type": "string",
          "plain_english": "string (8th grade rewrite)",
          "translated_explanation": "string (in {language})",
          "translated_consequence": "string (in {language})",
          "translated_fair_version": "string (in {language})",
          "negotiation_tip": "string"
        }}
      ],
      "red_flags_count": 0,
      "dark_patterns_count": 0,
      "negotiation_summary": "string",
      "translated_summary": "string (in {language})"
    }}"""
    
    model_3 = get_model(system_instruction=sys_prompt_3)
    response_3 = model_3.generate_content(
        json.dumps(analyzed_clauses),
        generation_config=GenerationConfig(response_mime_type="application/json", temperature=0.0)
    )
    
    try:
        final_result = json.loads(response_3.text)
        return final_result
    except Exception as e:
        return _fallback_error(f"Failed to generate final analysis: {str(e)}")

def _fallback_error(msg: str) -> dict:
    return {
      "document_type": "unknown",
      "overall_risk_score": 0,
      "safe_to_sign": False,
      "power_imbalance": "Unknown",
      "summary": msg,
      "flagged_clauses": [],
      "red_flags_count": 0,
      "dark_patterns_count": 0,
      "negotiation_summary": "",
      "translated_summary": msg
    }
