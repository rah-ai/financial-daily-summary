#!/usr/bin/env python3
"""
Test script to verify all fixes are working
"""

import os
import sys
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import crewai
        print(f"✅ CrewAI: {crewai.__version__}")
    except Exception as e:
        print(f"❌ CrewAI import failed: {e}")
        return False
        
    try:
        import litellm
        print(f"✅ LiteLLM: {litellm.__version__}")
    except Exception as e:
        print(f"❌ LiteLLM import failed: {e}")
        return False
        
    try:
        import httpx
        print(f"✅ HTTPX: {httpx.__version__}")
    except Exception as e:
        print(f"❌ HTTPX import failed: {e}")
        return False
        
    return True

def test_environment():
    """Test environment variables"""
    print("\nTesting environment variables...")
    
    required_vars = ['GROQ_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
        else:
            print(f"✅ {var}: {'*' * 8}...{os.getenv(var)[-4:]}")
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    
    return True

def test_groq_model():
    """Test Groq API with new model"""
    print("\nTesting Groq API with updated model...")
    
    try:
        from litellm import completion
        
        response = completion(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hello, respond with just 'API working'"}],
            api_key=os.getenv('GROQ_API_KEY'),
            max_tokens=10
        )
        
        result = response['choices'][0]['message']['content']
        print(f"✅ Groq API Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Groq API test failed: {e}")
        return False

def test_telegram_http():
    """Test Telegram API using httpx"""
    print("\nTesting Telegram API with httpx...")
    
    try:
        import httpx
        
        url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/getMe"
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Telegram Bot: {bot_info.get('first_name', 'Unknown')} (@{bot_info.get('username', 'Unknown')})")
                return True
            else:
                print(f"❌ Telegram API error: {data}")
                return False
                
    except Exception as e:
        print(f"❌ Telegram HTTP test failed: {e}")
        return False

def test_agents():
    """Test individual agent tools"""
    print("\nTesting agent tools...")
    
    try:
        # Test search agent
        from crewai_app.agents.search_agent import search_agent
        news_result = search_agent.run("test query")
        print(f"✅ Search Agent: Found {len(news_result) if isinstance(news_result, list) else 1} items")
        
        # Test summary agent
        from crewai_app.agents.summary_agent import summary_agent
        summary_result = summary_agent.run(["Test market news item"])
        print(f"✅ Summary Agent: Generated {len(summary_result)} character summary")
        
        # Test send agent (with test data)
        from crewai_app.agents.send_agent import send_agent
        test_data = {
            "summary": "Test summary for verification",
            "charts": ["https://dummyimage.com/300x200/000/fff&text=Test"],
            "translations": {"Hindi": "परीक्षण", "Arabic": "اختبار", "Hebrew": "מבחן"}
        }
        
        send_result = send_agent.run(test_data)
        print(f"✅ Send Agent: {send_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def main():
    """Run all tests"""
    print(f"🧪 Running system tests at {datetime.now()}")
    print("="*50)
    
    tests = [
        test_imports,
        test_environment, 
        test_groq_model,
        test_telegram_http,
        test_agents
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed! System is ready.")
    else:
        print(f"⚠️  {passed}/{total} tests passed. Check failures above.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)