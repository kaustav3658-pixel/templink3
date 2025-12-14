import os
import logging
from flask import Flask, request, Response, jsonify
import requests
from urllib.parse import urlparse

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

@app.route('/')
def index():
    return "Telegram Proxy Bot is running."

@app.route('/api/<path:url>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(url):
    """
    Proxy request to the target URL.
    """
    target_url = url
    if not target_url.startswith('http'):
        target_url = 'https://' + target_url

    logger.info(f"Proxying request to: {target_url}")

    try:
        # Forward the request to the target URL
        # We try to forward the method and data/params as well
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=True
        )

        # Exclude some headers that might cause issues
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(resp.content, resp.status_code, headers)

    except Exception as e:
        logger.error(f"Error proxying request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route(f'/webhook', methods=['POST'])
def webhook():
    """
    Handle incoming Telegram updates.
    """
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not set")
        return "TELEGRAM_TOKEN not set", 500

    update = request.get_json()

    if not update or 'message' not in update:
        return "OK", 200

    message = update['message']
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')

    if chat_id and text:
        # Check if text looks like a URL
        # Simple check: contains '.' and doesn't contain spaces (basic)
        # Or just trust the user input as per requirements "anyone put a url"

        # Strip http/https for the output link as requested
        # Example: https://google.com --> .../api/google.com

        clean_url = text.strip()
        parsed = urlparse(clean_url)

        # If schema is present (http/https), remove it to match the example format
        # but keep the rest (netloc + path + params)
        if parsed.scheme:
             # urlparse('https://google.com/foo') -> scheme='https', netloc='google.com', path='/foo'
             # We want google.com/foo
             # If the user just typed 'google.com', parsed.scheme is empty (or '' depending on python version/input)
             target_path = clean_url[len(parsed.scheme)+3:] if clean_url.startswith(parsed.scheme + '://') else clean_url
        else:
             target_path = clean_url

        # Remove trailing slash if you want, or keep it.
        # Construct the proxy URL
        # Use RENDER_EXTERNAL_URL if available
        base_url = RENDER_EXTERNAL_URL if RENDER_EXTERNAL_URL else request.host_url.rstrip('/')

        # Ensure base_url starts with http/https
        if not base_url.startswith('http'):
            base_url = f"https://{base_url}" # Render provides https

        proxy_link = f"{base_url}/api/{target_path}"

        reply_text = f"{proxy_link}"

        send_message(chat_id, reply_text)

    return "OK", 200

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

if __name__ == '__main__':
    # For local testing
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
