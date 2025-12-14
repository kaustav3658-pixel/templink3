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


if __name__ == '__main__':
    # For local testing
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
