# crewai_app/agents/send_agent.py

from crewai.tools import tool
import asyncio
import logging
import json
from typing import Dict, List, Any, Union
from ..config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import re
from datetime import datetime, timezone, timedelta
import httpx

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================
# FIXED: Use httpx instead of python-telegram-bot to avoid dependency issues
# ================================

@tool("send_to_telegram")
def send_agent(data: Union[str, dict]) -> str:
    """
    Telegram sender using httpx (no external dependencies).
    Handles: Summary text, Charts (image URLs), Translations
    """
    
    def send_sync():
        """Synchronous version to avoid async issues"""
        try:
            print("Starting Telegram send process...")
            print(f"Input data type: {type(data)}")

            # Parse and structure data
            structured_data = _parse_input_data(data)
            print(f"Structured data keys: {list(structured_data.keys())}")
            print(f"Summary length: {len(structured_data.get('summary', ''))}")
            print(f"Charts count: {len(structured_data.get('charts', []))}")
            print(f"Languages available: {list(structured_data.get('translations', {}).keys())}")

            if not any([structured_data.get('summary'), structured_data.get('charts'), structured_data.get('translations')]):
                print("No meaningful data to send!")
                return "No data available to send"

            # Send main message
            _send_main_message_sync(structured_data)

            # Send chart images
            charts_sent = _send_chart_images_sync(structured_data.get('charts', []))

            success_msg = f"Successfully sent to Telegram! Charts sent: {charts_sent}"
            print(success_msg)
            return success_msg

        except Exception as e:
            error_msg = f"Error sending to Telegram: {str(e)}"
            print(error_msg)
            logger.error(f"Telegram send error: {e}")

            # Send error notification
            _send_error_notification_sync(e)
            return error_msg

    return send_sync()


# ================================
# Data Parsing & Structuring
# ================================
def _parse_input_data(data: Union[str, dict, Any]) -> dict:
    """Parse input data into expected structured format"""
    if isinstance(data, dict):
        # Handle direct dictionary input
        if 'summary' in data or 'charts' in data or 'translations' in data:
            return {
                'summary': str(data.get('summary', '')),
                'charts': list(data.get('charts', [])),
                'translations': dict(data.get('translations', {}))
            }
        
        # Handle CrewAI task result format
        if 'raw' in data:
            return _parse_input_data(data['raw'])
        
        # Handle nested data structures
        for key, value in data.items():
            if isinstance(value, (dict, list, str)) and any(term in str(value).lower() for term in ['summary', 'chart', 'translation']):
                return _parse_input_data(value)

    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            if isinstance(parsed, dict):
                return _parse_input_data(parsed)
        except json.JSONDecodeError:
            return {
                'summary': data,
                'charts': [],
                'translations': {}
            }

    if hasattr(data, '__dict__') or isinstance(data, (list, tuple)):
        return _extract_from_complex_data(data)

    return {
        'summary': str(data),
        'charts': [],
        'translations': {}
    }


def _extract_from_complex_data(data: Any) -> dict:
    """Extract summary, charts, translations from complex CrewAI data"""
    result = {'summary': '', 'charts': [], 'translations': {}}
    text = str(data)

    # Extract summary - look for financial keywords
    if any(k in text.lower() for k in ['market', 'stock', 'trading', 'financial', 'dow', 'nasdaq', 's&p', 'price']):
        lines = text.split('\n')
        summary_lines = [line.strip() for line in lines if len(line.strip()) > 20 and not line.strip().startswith('http')][:10]
        result['summary'] = '\n'.join(summary_lines)

    # Extract chart URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+(?:\.(?:jpg|jpeg|png|gif|webp|svg)|\&text=Chart\d*)'
    chart_urls = re.findall(url_pattern, text, re.IGNORECASE)
    result['charts'] = list(set(chart_urls))

    # Extract translations
    translation_patterns = {
        'Hindi': [r'hindi[:\s]*([^A-Za-z\n]+)', r'हिंदी[:\s]*([^\n]+)', r'दैनिक[^A-Za-z\n]*'],
        'Arabic': [r'arabic[:\s]*([^A-Za-z\n]+)', r'عربي[:\s]*([^\n]+)', r'يومي[^A-Za-z\n]*'],
        'Hebrew': [r'hebrew[:\s]*([^A-Za-z\n]+)', r'עברית[:\s]*([^\n]+)', r'יומי[^A-Za-z\n]*']
    }
    
    for lang, patterns in translation_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match and match.group().strip():
                result['translations'][lang] = match.group().strip()
                break

    return result


# ================================
# FIXED: Synchronous HTTP calls using httpx
# ================================

def _send_main_message_sync(data: dict):
    """Send main summary + translations using httpx (synchronous)"""
    message_parts = []
    message_parts.append("📊 *DAILY MARKET SUMMARY*")
    message_parts.append("="*30)

    # Summary
    summary = data.get('summary', '').strip()
    if summary:
        summary = _escape_markdown(summary)
        message_parts.append(f"\n📈 *Market Overview:*\n{summary}")

    # Translations
    translations = data.get('translations', {})
    if translations:
        message_parts.append("\n🌐 *Translations Available:*")
        for lang, text in translations.items():
            if text and text.strip():
                display_text = _escape_markdown(str(text).strip())
                message_parts.append(f"\n🔸 *{lang.title()}:*\n{display_text}")

    # Charts info
    charts = data.get('charts', [])
    if charts:
        message_parts.append(f"\n📊 *Market Charts:* {len(charts)} charts attached below")

    message_parts.append(f"\n⏰ *Generated:* {_get_current_time()}")
    message_parts.append("📱 *Daily Financial Summary Bot*")

    full_message = "\n".join(message_parts)

    # Split if too long
    if len(full_message) > 4000:
        chunks = _split_message(full_message)
        for i, chunk in enumerate(chunks):
            _send_telegram_message(f"Part {i+1}/{len(chunks)}:\n\n{chunk}")
    else:
        _send_telegram_message(full_message)


def _send_chart_images_sync(charts: List[str]) -> int:
    """Send chart images using httpx (synchronous)"""
    charts_sent = 0
    for i, url in enumerate(charts[:5]):  # limit to 5
        if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
            print(f"Invalid chart URL {i+1}: {url}")
            continue
        
        try:
            _send_telegram_photo(url, f"📊 Market Chart {i+1}\n{_get_current_time()}")
            charts_sent += 1
        except Exception as e:
            print(f"Failed to send chart {i+1}: {e}")
            continue
    return charts_sent


def _send_error_notification_sync(error: Exception):
    """Send error notification using httpx (synchronous)"""
    try:
        error_msg = _escape_markdown(str(error))
        _send_telegram_message(f"⚠️ *Daily Summary Error*\n\n`{error_msg}`\n\n⏰ {_get_current_time()}")
    except Exception as e:
        logger.error(f"Failed to send error notification: {e}")


# ================================
# Low-level HTTP calls using httpx
# ================================

def _send_telegram_message(text: str):
    """Send text message to Telegram using httpx"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            print("Message sent successfully")
    except Exception as e:
        print(f"Failed to send message with markdown: {e}")
        # Fallback without markdown
        payload['parse_mode'] = None
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                print("Message sent successfully (plain text)")
        except Exception as e2:
            print(f"Failed to send message: {e2}")
            raise


def _send_telegram_photo(photo_url: str, caption: str):
    """Send photo to Telegram using httpx"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'photo': photo_url,
        'caption': caption,
        'parse_mode': 'Markdown'
    }
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()


# ================================
# Helper Functions
# ================================

def _escape_markdown(text: str) -> str:
    """Escape special characters for Telegram Markdown"""
    if not isinstance(text, str):
        text = str(text)
    # Escape special Markdown characters
    chars_to_escape = ['*', '_', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in chars_to_escape:
        text = text.replace(char, f'\\{char}')
    return text

def _split_message(message: str, max_length: int = 4000) -> List[str]:
    """Split message into chunks"""
    chunks, current = [], ""
    for line in message.split('\n'):
        if len(current) + len(line) + 1 <= max_length:
            current += line + '\n'
        else:
            if current.strip():
                chunks.append(current.strip())
            current = line + '\n'
    if current.strip():
        chunks.append(current.strip())
    return chunks or ["Empty message"]

def _get_current_time() -> str:
    """Get current time in IST"""
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    return now.strftime("%Y-%m-%d %H:%M IST")


# ================================
# Debug tool
# ================================
@tool("debug_telegram_data")
def debug_telegram_data(data: Any) -> str:
    """Debug tool to inspect data before sending to Telegram"""
    print("TELEGRAM DEBUG - Data Inspection:")
    print(f"Data type: {type(data)}")
    print(f"Data repr: {repr(data)[:500]}...")

    if isinstance(data, dict):
        print("Dictionary keys:")
        for key, value in data.items():
            print(f"  - {key}: {type(value)} (length: {len(str(value))})")

    structured = _parse_input_data(data)
    print(f"Structured data: {list(structured.keys())}")

    return f"Debug complete - Original: {type(data)}, Structured keys: {list(structured.keys())}"