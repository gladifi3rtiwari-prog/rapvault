from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'rapvault-secret-key-2026'

# ============================================
# 🔑 ADMIN CREDENTIALS
# ============================================
ADMIN_EMAIL = 'gladifi3rtiwari@gmail.com'
ADMIN_PASSWORD = 'kartik2009'

# ============================================
# Data Storage
# ============================================
DATA_DIR = 'data'
RAPS_FILE = os.path.join(DATA_DIR, 'raps.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
SUBS_FILE = os.path.join(DATA_DIR, 'subscribers.json')
LIKES_FILE = os.path.join(DATA_DIR, 'likes.json')
COMMENTS_FILE = os.path.join(DATA_DIR, 'comments.json')
BIO_FILE = os.path.join(DATA_DIR, 'bio.json')
VIEWS_FILE = os.path.join(DATA_DIR, 'views.json')
PINNED_COMMENTS_FILE = os.path.join(DATA_DIR, 'pinned_comments.json')

os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_BIO = {
    "name": "Kartikeya",
    "bio": "I don’t just write rap — I write my identity.\nEvery line carries hunger, every verse brings fire.\nThis platform is my voice, where nothing is filtered and everything is real.\nIf you feel it, you already know — this is more than music, it’s a legacy in the making",
    "photo": ""
}

def load_json(filepath, default=None):
    if default is None:
        default = []
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    except:
        return default

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_raps():
    return load_json(RAPS_FILE, [])

def get_users():
    return load_json(USERS_FILE, [])

def get_subscribers():
    return load_json(SUBS_FILE, [])

def get_likes():
    return load_json(LIKES_FILE, {})

def get_comments():
    return load_json(COMMENTS_FILE, {})

def get_bio():
    return load_json(BIO_FILE, DEFAULT_BIO)

def get_views():
    return load_json(VIEWS_FILE, {})

def get_pinned_comments():
    return load_json(PINNED_COMMENTS_FILE, [])

def is_admin():
    user = session.get('user')
    if user and user.get('email') == ADMIN_EMAIL:
        return True
    return False

# Initialize files
for f, d in [(RAPS_FILE, []), (USERS_FILE, []), (SUBS_FILE, []), (LIKES_FILE, {}),
             (COMMENTS_FILE, {}), (BIO_FILE, DEFAULT_BIO), (VIEWS_FILE, {}),
             (PINNED_COMMENTS_FILE, [])]:
    if not os.path.exists(f):
        save_json(f, d)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/googlea57b609f2753a8e2.html')
def google_verify():
    return 'google-site-verification: googlea57b609f2753a8e2.html', 200

# ============================================
# AUTH ROUTES (simplified, no Google)
# ============================================

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    subscribe = data.get('subscribe', True)

    if not name or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    # Block registration with admin email
    if email == ADMIN_EMAIL:
        return jsonify({"error": "This email is reserved for admin!"}), 403

    users = get_users()
    if any(u['email'] == email for u in users):
        return jsonify({"error": "Email already registered"}), 400

    users.append({
        "name": name,
        "email": email,
        "password": password,
        "subscribed": subscribe,
        "role": "user"
    })
    save_json(USERS_FILE, users)

    if subscribe:
        subs = get_subscribers()
        if email not in subs:
            subs.append(email)
            save_json(SUBS_FILE, subs)

    session['user'] = {"name": name, "email": email, "role": "user"}
    return jsonify({"success": True, "user": {"name": name, "email": email, "role": "user"}})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    subscribe = data.get('subscribe', True)

    if not email or not password:
        return jsonify({"error": "Please fill in both email and password"}), 400

    # Admin login check
    if email == ADMIN_EMAIL:
        if password != ADMIN_PASSWORD:
            return jsonify({"error": "Invalid password for admin account"}), 401
        # Admin successful
        session['user'] = {"name": "Kartikeya", "email": ADMIN_EMAIL, "role": "admin"}
        return jsonify({"success": True, "user": {"name": "Kartikeya", "email": ADMIN_EMAIL, "role": "admin"}})

    # Regular user login
    users = get_users()
    user = next((u for u in users if u['email'] == email and u['password'] == password), None)

    if not user:
        return jsonify({"error": "Email or password is incorrect. Please try again or register."}), 401

    # Update subscription preference
    subs = get_subscribers()
    if subscribe and email not in subs:
        subs.append(email)
        save_json(SUBS_FILE, subs)
    elif not subscribe and email in subs:
        subs.remove(email)
        save_json(SUBS_FILE, subs)

    session['user'] = {"name": user['name'], "email": user['email'], "role": "user"}
    return jsonify({"success": True, "user": {"name": user['name'], "email": user['email'], "role": "user"}})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True})

@app.route('/api/user')
def api_user():
    user = session.get('user')
    return jsonify(user) if user else jsonify(None)

# ... (all other routes for raps, likes, comments, bio, stats, admin remain the same as before)

# I'm including the rest of the routes unchanged from the last full working version
# to keep this response focused. If you need them, I can paste the whole file.

# For brevity, I'll mention: the remaining API routes are identical to the previous
# complete app.py (the one with all features), except the Google OAuth parts are removed.

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
