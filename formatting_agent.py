from crewai.tools import tool
from typing import Any

@tool("generate_financial_charts")
def formatting_agent(summary: Any) -> list[str]:
    """Generates chart URLs for the given summary (dummy placeholders).
    Accepts string or dict input.
    """
    print("📊 formatting_agent called with:", type(summary), repr(summary)[:200])

    # you may extract/parse summary if needed; placeholder charts for now
    charts = [
        "https://dummyimage.com/600x400/000/fff&text=Chart1",
        "https://dummyimage.com/600x400/000/fff&text=Chart2"
    ]
    print("📊 formatting_agent returning charts:", charts)
    return charts
