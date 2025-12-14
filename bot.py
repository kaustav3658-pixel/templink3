import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import json
import html
from flask import Flask
from threading import Thread
import os

# Telegram Bot Token
TOKEN = "8486043863:AAH8JiiRfD89_xJuQtLLGMpK4FIgk2LroVY"

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# API Mapping
API_MAP = {
    'cdn': 'https://pbx1botapi.vercel.app/api/hubcdn',
    'eflix': 'https://pbx1botapi.vercel.app/api/extraflix',
    'elink': 'https://pbx1botapi.vercel.app/api/extralink',
    'gd': 'https://pbx1botapi.vercel.app/api/driveleech',
    'gdr': 'https://pbx1botapi.vercel.app/api/gdrex',
    'ged': 'https://pbx1botapi.vercel.app/api/gdflix',
    'hb': 'https://pbx1botsapi2.vercel.app/api/hblinks',
    'hub': 'https://pbx1botapi.vercel.app/api/hubcloud',
    'lux': 'https://pbx1botapi.vercel.app/api/luxdrive',
    'neo': 'https://pbx1botapi.vercel.app/api/neo',
    'nex': 'https://pbx1botsapi2.vercel.app/api/nexdrive',
    'pcdn': 'https://pbx1botapi.vercel.app/api/pixelcdn',
    'seed': 'https://pbx1botapi.vercel.app/api/hubdrive',
    'vcl': 'https://pbx1botapi.vercel.app/api/vcloud',
    'vega': 'https://pbx1botsapi2.vercel.app/api/vega',
    'atv': 'https://appletv.pbx1bots.workers.dev/',
    'prime': 'https://primevideo.pbx1bots.workers.dev/',
    'airtel': 'https://airtelxstream.pbx1bots.workers.dev/',
    'zee5': 'https://zee5.pbx1bots.workers.dev/',
    'stage': 'https://stage.pbx1bots.workers.dev/',
    'bms': 'https://bms.pbx1.workers.dev/',
    'sun': 'https://sunnxt.pbx1.workers.dev/',
}

# Command Descriptions
COMMAND_DESCRIPTIONS = {
    'cdn': 'HubCDN',
    'eflix': 'ExtraFlix',
    'elink': 'ExtraLink',
    'gd': 'DriveLeech',
    'gdr': 'GDRex',
    'ged': 'GDFlix',
    'hb': 'HBLinks',
    'hub': 'HubCloud',
    'lux': 'LuxDrive',
    'neo': 'Neo',
    'nex': 'NexDrive',
    'pcdn': 'PixelCDN',
    'seed': 'HubDrive',
    'vcl': 'VCloud',
    'vega': 'Vega',
    'atv': 'AppleTV Posters',
    'prime': 'PrimeVideo Posters',
    'airtel': 'AirtelXstream Posters',
    'zee5': 'Zee5 Posters',
    'stage': 'Stage Posters',
    'bms': 'BookMyShow Posters',
    'sun': 'SunNXT Posters',
}

def format_response(data):
    """Formats the JSON response into a human-readable message."""
    if not isinstance(data, dict):
        return str(data)

    # Check for specific structure: file_name, links (common in file hosters)
    if 'file_name' in data and 'links' in data:
        lines = []
        if 'file_name' in data:
            lines.append(f"<b>File Name:</b> <code>{html.escape(str(data['file_name']))}</code>")
        if 'file_size' in data:
             lines.append(f"<b>File Size:</b> <code>{html.escape(str(data['file_size']))}</code>")

        lines.append("") # Spacer

        if isinstance(data['links'], list):
            lines.append("<b>Links:</b>")
            for idx, link_item in enumerate(data['links'], 1):
                if isinstance(link_item, dict):
                    link_type = link_item.get('type', 'Link')
                    link_url = link_item.get('url', 'No URL')
                    lines.append(f"{idx}. <b>{html.escape(str(link_type))}:</b> {html.escape(str(link_url))}")
                else:
                    lines.append(f"{idx}. {html.escape(str(link_item))}")

        if 'used_domain' in data:
             lines.append("")
             lines.append(f"<b>Used Domain:</b> {html.escape(str(data['used_domain']))}")

        return "\n".join(lines)

    # Generic Fallback for other APIs
    lines = []
    for key, value in data.items():
        formatted_key = key.replace('_', ' ').title()
        formatted_key = html.escape(formatted_key)
        if isinstance(value, list):
             lines.append(f"<b>{formatted_key}:</b>")
             for item in value:
                 lines.append(f"- {html.escape(str(item))}")
        elif isinstance(value, dict):
             lines.append(f"<b>{formatted_key}:</b>")
             for k, v in value.items():
                 lines.append(f"  - {html.escape(str(k))}: {html.escape(str(v))}")
        else:
             lines.append(f"<b>{formatted_key}:</b> {html.escape(str(value))}")

    return "\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message with available commands."""
    commands_text = ""
    sorted_cmds = sorted(API_MAP.keys())

    # Group commands? No, just list them with descriptions as requested.
    for cmd in sorted_cmds:
        description = COMMAND_DESCRIPTIONS.get(cmd, "Bypass Link")
        commands_text += f"/{cmd} - {description}\n"

    welcome_text = (
        "Welcome to the Link Bypass Bot!\n\n"
        "I can extract links and details from various supported sites and send them in a readable format.\n\n"
        "Available commands:\n"
        f"{commands_text}\n"
        "Usage: /command <url>"
    )
    await update.message.reply_text(welcome_text)

async def handle_bypass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the bypass command by calling the corresponding API."""
    if not context.args:
        await update.message.reply_text("Please provide a URL after the command. Usage: /command <url>")
        return

    url = context.args[0]
    cmd = update.message.text.split()[0][1:]
    if '@' in cmd:
        cmd = cmd.split('@')[0]

    api_url = API_MAP.get(cmd)

    if not api_url:
        await update.message.reply_text("Unknown command.")
        return

    try:
        full_url = f"{api_url}?url={url}"
        response = requests.get(full_url)

        try:
            data = response.json()
            formatted_text = format_response(data)

            if len(formatted_text) > 4000:
                formatted_text = formatted_text[:4000] + "..."
                # If truncated, disable HTML parsing to avoid broken tags
                await update.message.reply_text(formatted_text, disable_web_page_preview=True)
            else:
                await update.message.reply_text(formatted_text, parse_mode='HTML', disable_web_page_preview=True)
        except ValueError:
            await update.message.reply_text(response.text)

    except Exception as e:
        logging.error(f"Error processing {cmd}: {e}")
        await update.message.reply_text(f"Error occurred: {str(e)}")

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    for cmd in API_MAP.keys():
        application.add_handler(CommandHandler(cmd, handle_bypass))

    print("Bot is polling...")
    application.run_polling()
