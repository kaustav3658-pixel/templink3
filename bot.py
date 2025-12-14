import os
import time
import logging
import requests
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

def send_message(chat_id, text):
    """
    Send a message back to Telegram.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

def process_message(message):
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')

    if chat_id and text:
        clean_url = text.strip()
        parsed = urlparse(clean_url)

        if parsed.scheme:
             target_path = clean_url[len(parsed.scheme)+3:] if clean_url.startswith(parsed.scheme + '://') else clean_url
        else:
             target_path = clean_url

        # Construct the proxy URL
        # Use RENDER_EXTERNAL_URL if available
        base_url = RENDER_EXTERNAL_URL

        # Fallback if RENDER_EXTERNAL_URL is not set (e.g. local dev)
        if not base_url:
             # In polling mode without a web context, we can't guess the URL easily unless provided.
             # We'll use a placeholder or localhost if not set.
             base_url = "https://krvpn.onrender.com" # Default to project name based on README if not set
        else:
            base_url = base_url.rstrip('/')

        if not base_url.startswith('http'):
            base_url = f"https://{base_url}"

        proxy_link = f"{base_url}/api/{target_path}"

        logger.info(f"Generated proxy link for {chat_id}: {proxy_link}")
        send_message(chat_id, proxy_link)

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {'timeout': 100, 'offset': offset}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
        return None

def delete_webhook():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook"
    try:
        requests.get(url)
        logger.info("Webhook deleted.")
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not set")
        return

    # Delete webhook to prevent conflicts with polling
    delete_webhook()

    logger.info("Starting polling...")
    offset = None

    while True:
        updates = get_updates(offset)

        if updates and updates.get('ok'):
            for update in updates.get('result', []):
                offset = update['update_id'] + 1
                if 'message' in update:
                    process_message(update['message'])
        else:
            if updates and not updates.get('ok'):
                logger.error(f"Telegram API Error: {updates.get('description')}")
                time.sleep(5) # Backoff on error

        time.sleep(1)

if __name__ == '__main__':
    main()
