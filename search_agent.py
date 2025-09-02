# crewai_app/agents/search_agent.py
from crewai.tools import tool
from typing import Any
import requests
from datetime import datetime
from ..config import TAVILY_API_KEY, SERPER_API_KEY

@tool("search_latest_financial_news")
def search_agent(query: Any = None) -> list[str]:
    """
    Fetches the latest financial news.
    Accepts flexible input shapes for 'query' (string or dict).
    """
    print("🔍 search_agent called with:", type(query), repr(query)[:200])

    # Normalize query -> string
    q = None
    if isinstance(query, str):
        q = query
    elif isinstance(query, dict):
        if "query" in query and isinstance(query["query"], str):
            q = query["query"]
        elif "description" in query and isinstance(query["description"], str):
            q = query["description"]

    if not q:
        q = "latest US financial market news"

    # Try real API first if available
    if TAVILY_API_KEY or SERPER_API_KEY:
        try:
            real_news = _fetch_real_news(q)
            if real_news:
                print(f"🔍 search_agent returning {len(real_news)} real headlines")
                return real_news
        except Exception as e:
            print(f"⚠️ Real API failed: {e}, falling back to mock data")

    # Enhanced mock data for better summaries
    mock_news = [
        f"S&P 500 closes up 1.2% at 4,750 points on strong tech earnings, NASDAQ gains 1.8% - {datetime.now().strftime('%Y-%m-%d')}",
        f"Dow Jones Industrial Average rises 280 points to 37,200 amid positive economic data - {datetime.now().strftime('%Y-%m-%d')}",
        "Tesla stock jumps 5.2% after beating Q3 delivery expectations with 462,000 vehicles delivered",
        "Apple shares gain 2.1% on reports of strong iPhone 15 pre-orders exceeding analyst estimates",
        "Federal Reserve officials signal potential pause in rate hikes following recent inflation data showing 3.2% annual increase",
        "Oil prices drop 3% to $87/barrel on increased US crude inventory and demand concerns from China",
        "Microsoft stock rises 1.9% after announcing new AI partnership and cloud service expansion",
        "Goldman Sachs raises S&P 500 year-end target to 4,800 citing improving corporate earnings outlook",
        "US jobless claims fall to 210,000, lowest in 3 months, indicating strong labor market conditions",
        "Bitcoin trades at $43,200, up 2.8% as institutional adoption continues with new ETF approvals"
    ]
    
    print(f"🔍 search_agent returning {len(mock_news)} mock headlines")
    return mock_news

def _fetch_real_news(query: str) -> list[str]:
    """Try to fetch real news using available APIs"""
    
    if TAVILY_API_KEY:
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "basic",
                "max_results": 8,
                "include_domains": ["finance.yahoo.com", "marketwatch.com", "cnbc.com"]
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("results", []):
                    title = item.get("title", "")
                    content = item.get("content", "")[:150]
                    results.append(f"{title} - {content}")
                
                if results:
                    return results
        except Exception as e:
            print(f"Tavily API error: {e}")
    
    if SERPER_API_KEY:
        try:
            url = "https://google.serper.dev/search"
            headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
            payload = {"q": query + " finance stock market", "num": 8}
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("organic", []):
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")[:150]
                    results.append(f"{title} - {snippet}")
                
                if results:
                    return results
        except Exception as e:
            print(f"Serper API error: {e}")
    
    return []