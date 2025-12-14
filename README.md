# Telegram Proxy Bot on Render

This project implements a Telegram bot that proxies URLs through your Render deployment.

## Features
- **Telegram Bot**: Accepts a URL message and returns a proxied URL.
- **Web Proxy**: A generic proxy endpoint (`/api/<url>`) that fetches and returns the content of the target URL.

## Deployment on Render

1.  **Create a New Web Service**
    -   Go to your [Render Dashboard](https://dashboard.render.com/).
    -   Click **New +** and select **Web Service**.
    -   Connect your GitHub repository containing this code.

2.  **Configure the Service**
    -   **Name**: `krvpn` (or any unique name). This determines your URL (e.g., `https://krvpn.onrender.com`).
    -   **Region**: Select **Singapore** (as requested).
    -   **Runtime**: **Python 3**.
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `gunicorn app:app`

3.  **Environment Variables**
    Add the following environment variables in the "Environment" tab:
    -   `TELEGRAM_TOKEN`: Your Telegram Bot API Token (get it from [@BotFather](https://t.me/BotFather)).
    -   `PYTHON_VERSION`: `3.9.0` (optional, or rely on default).

4.  **Set the Webhook**
    After deployment, you need to tell Telegram where to send messages. Run this command in your terminal (replace values):

    ```bash
    curl -F "url=https://<YOUR-RENDER-APP-NAME>.onrender.com/webhook" https://api.telegram.org/bot<YOUR-TELEGRAM-TOKEN>/setWebhook
    ```

    Example:
    ```bash
    curl -F "url=https://krvpn.onrender.com/webhook" https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/setWebhook
    ```

## Usage

1.  Open your bot in Telegram.
2.  Send a URL (e.g., `https://google.com`).
3.  The bot will reply with: `https://krvpn.onrender.com/api/google.com`.
4.  Clicking that link will open the proxied content.
