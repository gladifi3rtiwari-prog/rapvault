from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'rapvault-secret-key-2026'

# ============================================
# 🔑 ADMIN CREDENTIALS
# ============================================
ADMIN_EMAIL = 'gladifi3rtiwari@gmail.com'
ADMIN_PASSWORD = 'kartik2009'

# ============================================
# Google OAuth Configuration
# ============================================
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'your-client-id-here')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'your-client-secret-here')

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

# ============================================
# Data Storage (unchanged)
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

# ============================================
# Google OAuth Routes
# ============================================
@app.route('/login/google')
def login_google():
    redirect_uri = 'https://rapvault.onrender.com/login/google/callback'
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def authorize_google():
    try:
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        user_info = resp.json()
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')

        if not email:
            return redirect(url_for('home') + '?login=error')

        # Check if user exists, else create
        users = get_users()
        existing_user = next((u for u in users if u['email'] == email), None)
        if not existing_user:
            new_user = {
                "name": name,
                "email": email,
                "password": "google_oauth",  # placeholder
                "subscribed": True,
                "role": "admin" if email == ADMIN_EMAIL else "user",
                "picture": picture
            }
            users.append(new_user)
            save_json(USERS_FILE, users)

            # Add to subscribers if not already
            subs = get_subscribers()
            if email not in subs:
                subs.append(email)
                save_json(SUBS_FILE, subs)

        # Set session
        session['user'] = {
            "name": name,
            "email": email,
            "picture": picture,
            "role": "admin" if email == ADMIN_EMAIL else "user"
        }
        return redirect(url_for('home') + '?login=success')
    except Exception as e:
        print("Google login error:", e)
        return redirect(url_for('home') + '?login=error')

# ============================================
# All other routes (unchanged)
# ============================================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/googlea57b609f2753a8e2.html')
def google_verify():
    return 'google-site-verification: googlea57b609f2753a8e2.html', 200

@app.route('/api/bio', methods=['GET', 'POST'])
def api_bio():
    if request.method == 'GET':
        return jsonify(get_bio())
    if not is_admin():
        return jsonify({"error": "Admin only!"}), 403
    data = request.get_json(force=True, silent=True) or {}
    bio = get_bio()
    if 'name' in data: bio['name'] = data['name'].strip()
    if 'bio' in data: bio['bio'] = data['bio'].strip()
    if 'photo' in data: bio['photo'] = data['photo'].strip()
    save_json(BIO_FILE, bio)
    return jsonify({"success": True, "bio": bio})

@app.route('/api/raps')
def api_raps():
    tag = request.args.get('tag', 'all')
    search = request.args.get('search', '').lower()
    raps = get_raps()
    if tag != 'all':
        raps = [r for r in raps if r.get('tag', '').lower() == tag.lower()]
    if search:
        raps = [r for r in raps if
                search in r.get('title', '').lower() or
                search in r.get('preview', '').lower() or
                search in r.get('lyrics', '').lower()]
    raps.sort(key=lambda x: x.get('date', ''), reverse=True)
    likes = get_likes()
    views = get_views()
    for rap in raps:
        rid = rap['id']
        rap['likes_count'] = len(likes.get(rid, {}).get('users', []))
        rap['likes_users'] = likes.get(rid, {}).get('users', [])
        rap['comments_count'] = len(get_comments().get(rid, []))
        rap['views'] = views.get(rid, 0)
    return jsonify(raps)

@app.route('/api/rap/<rap_id>')
def api_rap_detail(rap_id):
    raps = get_raps()
    rap = next((r for r in raps if r['id'] == rap_id), None)
    if not rap:
        return jsonify({"error": "Rap not found"}), 404
    views = get_views()
    views[rap_id] = views.get(rap_id, 0) + 1
    save_json(VIEWS_FILE, views)
    likes = get_likes()
    comments = get_comments()
    rap['likes_count'] = len(likes.get(rap_id, {}).get('users', []))
    rap['likes_users'] = likes.get(rap_id, {}).get('users', [])
    rap['comments'] = comments.get(rap_id, [])
    rap['views'] = views.get(rap_id, 0)
    return jsonify(rap)

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
    if email == ADMIN_EMAIL:
        return jsonify({"error": "This email is reserved for admin!"}), 403
    users = get_users()
    if any(u['email'] == email for u in users):
        return jsonify({"error": "Email already registered"}), 400
    users.append({
        "name": name, "email": email, "password": password,
        "subscribed": subscribe, "role": "user"
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
        return jsonify({"error": "All fields required"}), 400
    if email == ADMIN_EMAIL:
        if password != ADMIN_PASSWORD:
            return jsonify({"error": "Invalid admin password!"}), 401
    users = get_users()
    user = next((u for u in users if u['email'] == email and u['password'] == password), None)
    if not user and email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        user = {
            "name": "Kartikeya", "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD, "subscribed": True, "role": "admin"
        }
        users.append(user)
        save_json(USERS_FILE, users)
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    subs = get_subscribers()
    if subscribe and email not in subs:
        subs.append(email)
        save_json(SUBS_FILE, subs)
    elif not subscribe and email in subs:
        subs.remove(email)
        save_json(SUBS_FILE, subs)
    session['user'] = {"name": user['name'], "email": user['email'], "role": "admin" if email == ADMIN_EMAIL else "user"}
    return jsonify({"success": True, "user": {"name": user['name'], "email": user['email'], "role": "admin" if email == ADMIN_EMAIL else "user"}})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True})

@app.route('/api/user')
def api_user():
    user = session.get('user')
    return jsonify(user) if user else jsonify(None)

@app.route('/api/like/<rap_id>', methods=['POST'])
def api_like(rap_id):
    user = session.get('user')
    if not user:
        return jsonify({"error": "Please login first"}), 401
    likes = get_likes()
    if rap_id not in likes:
        likes[rap_id] = {"users": []}
    if user['email'] in likes[rap_id]['users']:
        likes[rap_id]['users'].remove(user['email'])
    else:
        likes[rap_id]['users'].append(user['email'])
    save_json(LIKES_FILE, likes)
    return jsonify({"success": True, "likes_count": len(likes[rap_id]['users'])})

@app.route('/api/comment/<rap_id>', methods=['POST'])
def api_comment(rap_id):
    user = session.get('user')
    if not user:
        return jsonify({"error": "Please login first"}), 401
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    text = data.get('text', '').strip()
    if not text:
        return jsonify({"error": "Comment cannot be empty"}), 400
    comments = get_comments()
    if rap_id not in comments:
        comments[rap_id] = []
    comment = {
        "id": f"c_{len(comments[rap_id])+1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "user": user['name'], "email": user['email'],
        "text": text, "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "rap_id": rap_id
    }
    comments[rap_id].append(comment)
    save_json(COMMENTS_FILE, comments)
    return jsonify({"success": True, "comment": comment})

@app.route('/api/admin/pin-comment', methods=['POST'])
def api_pin_comment():
    if not is_admin():
        return jsonify({"error": "Admin only!"}), 403
    data = request.get_json(force=True, silent=True) or {}
    comment_id = data.get('comment_id')
    rap_id = data.get('rap_id')
    if not comment_id or not rap_id:
        return jsonify({"error": "Missing comment_id or rap_id"}), 400
    comments = get_comments().get(rap_id, [])
    comment = next((c for c in comments if c['id'] == comment_id), None)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    pinned = get_pinned_comments()
    if any(c['id'] == comment_id for c in pinned):
        return jsonify({"error": "Already pinned"}), 400
    pinned.append(comment)
    save_json(PINNED_COMMENTS_FILE, pinned)
    return jsonify({"success": True, "pinned": pinned})

@app.route('/api/pinned-comments')
def api_pinned_comments():
    return jsonify(get_pinned_comments())

@app.route('/api/admin/post', methods=['POST'])
def api_admin_post():
    if not is_admin():
        return jsonify({"error": "Admin only!"}), 403
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    title = data.get('title', '').strip()
    tag = data.get('tag', '').strip().lower()
    preview = data.get('preview', '').strip()
    lyrics = data.get('lyrics', '').strip()
    is_draft = data.get('is_draft', False)
    release_date = data.get('release_date')
    if not all([title, tag, preview, lyrics]):
        return jsonify({"error": "All fields required"}), 400
    raps = get_raps()
    new_rap = {
        "id": f"rap_{len(raps)+1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "title": title, "tag": tag, "preview": preview,
        "lyrics": lyrics, "date": datetime.now().strftime("%Y-%m-%d"),
        "featured": False, "posted_by": ADMIN_EMAIL,
        "is_draft": is_draft, "release_date": release_date if is_draft else None
    }
    raps.append(new_rap)
    save_json(RAPS_FILE, raps)
    subs = get_subscribers()
    return jsonify({"success": True, "rap": new_rap, "subscribers_notified": len(subs)})

@app.route('/api/admin/delete/<rap_id>', methods=['DELETE'])
def api_admin_delete(rap_id):
    if not is_admin():
        return jsonify({"error": "Admin only!"}), 403
    raps = get_raps()
    raps = [r for r in raps if r['id'] != rap_id]
    save_json(RAPS_FILE, raps)
    return jsonify({"success": True})

@app.route('/api/admin/feature/<rap_id>', methods=['POST'])
def api_admin_feature(rap_id):
    if not is_admin():
        return jsonify({"error": "Admin only!"}), 403
    raps = get_raps()
    for rap in raps:
        if rap['id'] == rap_id:
            rap['featured'] = not rap.get('featured', False)
    save_json(RAPS_FILE, raps)
    return jsonify({"success": True})

@app.route('/api/stats')
def api_stats():
    raps = get_raps()
    likes = get_likes()
    subs = get_subscribers()
    views = get_views()
    total_likes = sum(len(l.get('users', [])) for l in likes.values())
    total_views = sum(views.values())
    return jsonify({
        "raps_count": len(raps), "subscribers_count": len(subs),
        "total_likes": total_likes, "total_views": total_views
    })

@app.route('/admin/stats')
def admin_stats():
    if not is_admin():
        return "Access denied", 403
    raps = get_raps()
    likes = get_likes()
    views = get_views()
    subs = get_subscribers()
    comments = get_comments()
    total_likes = sum(len(l.get('users', [])) for l in likes.values())
    total_views = sum(views.values())
    return render_template('admin_stats.html',
                           raps=raps, likes=likes, views=views,
                           subs=subs, comments=comments,
                           total_likes=total_likes, total_views=total_views)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
