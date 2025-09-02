from crewai.tools import tool
from litellm import completion
from ..config import LLM_MODEL
import json
import re
from typing import Any

@tool("translate_summary")
def translate_agent(summary: Any) -> dict:
    """
    Translates the summary into Hindi, Arabic, and Hebrew in one LLM call.
    Accepts string or dict; returns dict with keys 'Hindi', 'Arabic', 'Hebrew'.
    Falls back to original text if translation fails.
    """
    print("🌍 translate_agent called with:", type(summary), repr(summary)[:300])

    # Normalize summary -> string
    text = ""
    if isinstance(summary, str):
        text = summary
    elif isinstance(summary, dict):
        if "summary" in summary and isinstance(summary["summary"], str):
            text = summary["summary"]
        elif "text" in summary and isinstance(summary["text"], str):
            text = summary["text"]
        else:
            parts = [v for v in summary.values() if isinstance(v, str)]
            text = "\n".join(parts)
    else:
        text = str(summary)

    if not text.strip():
        return {"Hindi": "", "Arabic": "", "Hebrew": ""}

    try:
        # Strict prompt to ensure ONLY JSON output
        prompt = f"""
Translate the following text into Hindi, Arabic, and Hebrew.
STRICTLY return valid JSON ONLY. NO extra text, NO explanations.
The JSON must have exactly these keys: "Hindi", "Arabic", "Hebrew".

Text:
{text}
"""

        response = completion(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response["choices"][0]["message"]["content"]
        
        # Extract JSON from response in case LLM adds extra text
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            translations = json.loads(match.group())
        else:
            raise ValueError("No JSON found in LLM response")

        # Ensure all keys exist
        for lang in ["Hindi", "Arabic", "Hebrew"]:
            if lang not in translations:
                translations[lang] = text

        return translations

    except Exception as e:
        print(f"⚠️ translate_agent: translation failed: {e}")
        return {
            "Hindi": text,
            "Arabic": text,
            "Hebrew": text
        }
