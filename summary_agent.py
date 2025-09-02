# crewai_app/agents/summary_agent.py

from crewai.tools import tool
from litellm import completion
from ..config import LLM_MODEL
from typing import Any
import json, time


@tool("summarize_financial_news")
def summary_agent(news: Any) -> str:
    """Summarizes a list of financial news headlines into under 200 words.
    Accepts list|dict|string input and has an LLM fallback.
    """
    print("📝 summary_agent called with type:", type(news), "preview:", repr(news)[:300])

    # --- Extract list of headlines robustly ---
    headlines = []
    if isinstance(news, list):
        headlines = news
    elif isinstance(news, dict):
        if "news" in news and isinstance(news["news"], list):
            headlines = news["news"]
        elif "description" in news and isinstance(news["description"], list):
            headlines = news["description"]
        else:
            for v in news.values():
                if isinstance(v, list):
                    headlines = v
                    break
    elif isinstance(news, str):
        try:
            parsed = json.loads(news)
            if isinstance(parsed, list):
                headlines = parsed
            else:
                headlines = [line.strip() for line in news.splitlines() if line.strip()]
        except Exception:
            headlines = [line.strip() for line in news.splitlines() if line.strip()]

    if not headlines:
        return "No news available to summarize."

    text = "\n".join(headlines)

    # --- Retry logic for LLM ---
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = completion(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a financial analyst."},
                    {"role": "user", "content": f"Summarize these points under 200 words:\n{text}"}
                ]
            )
            summary = response['choices'][0]['message']['content']
            print("📝 summary_agent: LLM returned summary (len):", len(summary))
            return summary
        except Exception as e:
            wait_time = 2 ** attempt
            print(f"⚠️ summary_agent: LLM failed (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("❌ Max retries reached, falling back to simple summary.")
                # Safe fallback
                simple = " ".join(headlines)
                words = simple.split()
                if len(words) > 200:
                    return " ".join(words[:200]) + "..."
                return simple
