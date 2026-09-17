# backend/data_processor.py

import json
import re

def parse_and_validate_gemini_response(raw_text: str) -> dict:
    """Cleans raw model output and parses JSON into dashboard data."""
    if not raw_text:
        raise ValueError("Model returned an empty response.")
    
    # Strip markdown code fences if present
    cleaned = re.sub(r"```json\s*", "", raw_text, flags=re.IGNORECASE)
    cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    
    try:
        data = json.loads(cleaned)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Gemini output as valid JSON: {str(e)}\nRaw response:\n{raw_text[:300]}")