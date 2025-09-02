# crewai_app/config.py

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === CORE CONFIGURATION ===
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# === FORCE GROQ USAGE ===
# Remove any OpenAI / Gemini keys to prevent conflicts
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']
if 'GOOGLE_API_KEY' in os.environ:
    del os.environ['GOOGLE_API_KEY']

# Set Groq as the default model for all LiteLLM calls
os.environ['GROQ_API_KEY'] = GROQ_API_KEY or ''

# === UPDATED GROQ MODEL CONFIGURATION ===
# Based on current available models as of September 2025
GROQ_MODELS = {
    "fast": "llama-3.1-8b-instant",         # Fastest option
    "versatile": "llama-3.3-70b-versatile",  # Updated: Replaced deprecated model
    "guard": "meta-llama/llama-guard-4-12b", # Content safety
    "gemma": "gemma2-9b-it"                   # Alternative model
}

# Primary model for all agents (UPDATED)
GROQ_MODEL = GROQ_MODELS["versatile"]  # Now uses llama-3.3-70b-versatile

# BACKWARD COMPATIBILITY - for existing agent files
LLM_MODEL = f"groq/{GROQ_MODEL}"

# LLM Configuration for CrewAI - Only supported parameters
DEFAULT_LLM_CONFIG = {
    "model": f"groq/{GROQ_MODEL}",
    "api_key": GROQ_API_KEY,
    "temperature": 0.7,
    "max_tokens": 4096,
    # Removed unsupported parameters: top_p, top_k
}

# === GROQ SUPPORTED PARAMETERS ===
# Only these parameters work with Groq API
GROQ_SUPPORTED_PARAMS = {
    'model', 'messages', 'temperature', 'max_tokens', 
    'stream', 'stop', 'seed', 'tools', 'tool_choice',
    'presence_penalty', 'frequency_penalty', 'logit_bias',
    'user', 'response_format'
}

def filter_groq_params(params):
    """Filter out unsupported parameters for Groq API calls"""
    if isinstance(params, dict):
        model = params.get('model', '')
        if 'groq/' in model or 'llama' in model.lower():
            filtered = {k: v for k, v in params.items() if k in GROQ_SUPPORTED_PARAMS}
            removed = set(params.keys()) - set(filtered.keys())
            if removed:
                print(f"Filtered unsupported Groq params: {removed}")
            return filtered
    return params

# === EXPORT ALL VARIABLES FOR AGENTS ===
__all__ = [
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_CHAT_ID',
    'TAVILY_API_KEY',
    'SERPER_API_KEY',
    'GROQ_API_KEY',
    'LLM_MODEL',
    'GROQ_MODEL',
    'DEFAULT_LLM_CONFIG',
    'GROQ_SUPPORTED_PARAMS',
    'filter_groq_params',
    'validate_config'
]

# === VALIDATION ===
def validate_config():
    """Validate that all required configuration is present"""
    missing = []
    
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_CHAT_ID:
        missing.append("TELEGRAM_CHAT_ID")
    if not (TAVILY_API_KEY or SERPER_API_KEY):
        missing.append("TAVILY_API_KEY or SERPER_API_KEY")
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    print("Configuration validated successfully!")
    print(f"Using LLM: {DEFAULT_LLM_CONFIG['model']}")
    print(f"Search APIs: {'Tavily' if TAVILY_API_KEY else ''}{',' if TAVILY_API_KEY and SERPER_API_KEY else ''}{'Serper' if SERPER_API_KEY else ''}")
    print(f"Groq parameters filtered: {len(GROQ_SUPPORTED_PARAMS)} supported")
    
    return True

# Validate configuration on import
if __name__ == "__main__":
    validate_config()
else:
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please check your .env file and ensure all required variables are set.")