# test_config.py - Run this first to verify everything works

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        from crewai_app.config import (
            GOOGLE_API_KEY, 
            TELEGRAM_BOT_TOKEN, 
            TELEGRAM_CHAT_ID,
            LLM_MODEL,
            validate_config
        )
        print("✅ Config imports successful")
        
        # Test agent imports
        from crewai_app.agents.summary_agent import summary_agent
        print("✅ Summary agent import successful")
        
        from crewai_app.agents.search_agent import search_agent
        print("✅ Search agent import successful")
        
        from crewai_app.agents.translate_agent import translate_agent
        print("✅ Translate agent import successful")
        
        from crewai_app.agents.formatting_agent import formatting_agent
        print("✅ Formatting agent import successful")
        
        from crewai_app.agents.send_agent import send_agent
        print("✅ Send agent import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration values"""
    print("\n🔧 Testing configuration...")
    
    try:
        from crewai_app.config import validate_config
        validate_config()
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_agents():
    """Test individual agents"""
    print("\n🤖 Testing individual agents...")
    
    try:
        # Test that agent modules can be imported and contain tools
        from crewai_app.agents.search_agent import search_agent
        from crewai_app.agents.summary_agent import summary_agent
        from crewai_app.agents.translate_agent import translate_agent
        from crewai_app.agents.formatting_agent import formatting_agent
        from crewai_app.agents.send_agent import send_agent
        
        # Check that tools have the right attributes
        tools = [search_agent, summary_agent, translate_agent, formatting_agent, send_agent]
        tool_names = []
        
        for tool in tools:
            if hasattr(tool, 'name'):
                tool_names.append(tool.name)
            else:
                tool_names.append(str(tool))
        
        print(f"✅ All agent tools loaded: {tool_names}")
        print("✅ Agent tools are ready for CrewAI framework")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test error: {e}")
        return False

def test_gemini_api():
    """Test Gemini API connectivity"""
    print("\n🤖 Testing Gemini API...")
    
    try:
        import litellm
        from crewai_app.config import LLM_MODEL, GOOGLE_API_KEY
        
        if not GOOGLE_API_KEY:
            print("⚠️ GOOGLE_API_KEY not set, skipping API test")
            return False
        
        response = litellm.completion(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": "Say 'Gemini API test successful'"}],
            api_key=GOOGLE_API_KEY,
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        print(f"✅ Gemini API test: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Configuration Tests")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config), 
        ("Agents", test_agents),
        ("Gemini API", test_gemini_api)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Ready to run main.py")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before running main.py")
        print("\nCommon fixes:")
        print("- Check your .env file has all required API keys")
        print("- Verify your Gemini API key is valid")
        print("- Install missing packages: pip install google-generativeai litellm")
    
    return all_passed

if __name__ == "__main__":
    main()