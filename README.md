# Telegram Web Proxy Bot

This project is a Telegram bot that acts as a web proxy. It allows users to send a URL to the bot, which then returns a proxied link. This is particularly useful for accessing websites that may be blocked or restricted in certain regions (e.g., India), or for bypassing geo-restrictions.

The application is hosted on Render and consists of two main components:
1.  **Flask Web Server (`app.py`):** Handles the proxying of web requests.
2.  **Telegram Bot (`bot.py`):** Uses long polling to listen for user messages containing URLs and responds with a proxied link.

## Features

*   **URL Proxying:** Converts standard URLs into proxied URLs routed through the application server.
*   **Telegram Interface:** Simple interaction via Telegram chat. Send a link, get a proxy link.
*   **Bypass Restrictions:** Helps access content that might be blocked by ISPs.
*   **CORS Handling:** Modifies headers to facilitate access.

## Architecture

*   **`app.py`**: A Flask application that serves as the proxy. It accepts requests at `/api/<url>`, fetches the content from the target URL, and returns it to the user.
*   **`bot.py`**: A Python script that polls the Telegram API for updates. When it receives a URL, it constructs a proxy URL pointing to the Flask app.
*   **`start.sh`**: The entry point script that runs both the Flask app (via Gunicorn) and the Bot script concurrently.

## Tech Stack

*   **Python 3**
*   **Flask:** Web framework.
*   **Gunicorn:** WSGI HTTP Server.
*   **Requests:** HTTP library for Python.
*   **Telegram Bot API:** For bot interaction.

## Setup & Installation

### Prerequisites

*   Python 3.x installed.
*   A Telegram Bot Token (obtained from @BotFather).

### Local Development

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables:**
    The Telegram Token is currently hardcoded in `bot.py` and `app.py`.

    Optionally set `RENDER_EXTERNAL_URL` if you want the bot to generate links using a specific domain (e.g., your local tunnel URL or production URL).
    ```bash
    export RENDER_EXTERNAL_URL="http://localhost:5000"
    ```

4.  **Run the application:**
    You can run the components separately or use the start script.

    *   **Start the Web Server:**
        ```bash
        python app.py
        ```
    *   **Start the Bot:**
        ```bash
        python bot.py
        ```

### Deployment (Render)

The project is configured for deployment on Render.

1.  **Build Command:** `pip install -r requirements.txt`
2.  **Start Command:** `./start.sh`
3.  **Environment Variables:**
    *   `RENDER_EXTERNAL_URL`: The URL of your Render web service (e.g., `https://your-app-name.onrender.com`). This is important so the bot knows how to construct the proxy links.

## Usage

1.  Start a chat with the bot on Telegram.
2.  Send a website URL (e.g., `google.com` or `https://blocked-site.com`).
3.  The bot will reply with a proxied link (e.g., `https://your-app.onrender.com/api/google.com`).
4.  Click the link to browse the site through the proxy.

## Note on Security

This is a basic proxy implementation. It does not handle advanced security features, authentication, or complex session management. Use with caution and avoid logging into sensitive accounts through the proxy.

## Troubleshooting

*   **Bot not responding:** Check if the `bot.py` script is running. If on Render, check the logs for any crashes.
*   **Proxy link 404/500:** The target site might block automated requests or the URL format might be incorrect. Check `app.log` (if enabled) or server logs.
