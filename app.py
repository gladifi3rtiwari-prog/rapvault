from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, render_template, request, jsonify, session, url_for
import json
import os
import uuid
from datetime import datetime


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "rapvault-secret-key-2026")

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "gladifi3rtiwari@gmail.com").lower()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "kartik2009")

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

oauth = OAuth(app)
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

DATA_DIR = "data"
RAPS_FILE = os.path.join(DATA_DIR, "raps.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SUBS_FILE = os.path.join(DATA_DIR, "subscribers.json")
LIKES_FILE = os.path.join(DATA_DIR, "likes.json")
COMMENTS_FILE = os.path.join(DATA_DIR, "comments.json")
BIO_FILE = os.path.join(DATA_DIR, "bio.json")
VIEWS_FILE = os.path.join(DATA_DIR, "views.json")
PINNED_COMMENTS_FILE = os.path.join(DATA_DIR, "pinned_comments.json")

os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_BIO = {
    "name": "Kartikeya",
    "bio": "I don't just write rap - I write my identity.\nEvery line carries hunger, every verse brings fire.\nThis platform is my voice, where nothing is filtered and everything is real.\nIf you feel it, you already know - this is more than music, it's a legacy in the making",
    "photo": "",
}


def load_json(filepath, default=None):
    if default is None:
        default = []
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return default
    except Exception:
        return default


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
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
    user = session.get("user")
    return bool(user and user.get("email", "").lower() == ADMIN_EMAIL)


def now_label():
    return datetime.now().strftime("%Y-%m-%d")


def ensure_files():
    defaults = [
        (RAPS_FILE, []),
        (USERS_FILE, []),
        (SUBS_FILE, []),
        (LIKES_FILE, {}),
        (COMMENTS_FILE, {}),
        (BIO_FILE, DEFAULT_BIO),
        (VIEWS_FILE, {}),
        (PINNED_COMMENTS_FILE, []),
    ]
    for filepath, default in defaults:
        if not os.path.exists(filepath):
            save_json(filepath, default)


def enrich_rap(rap):
    likes = get_likes()
    comments = get_comments()
    views = get_views()
    rap_id = rap.get("id")
    rap_likes = likes.get(rap_id, {})
    rap_comments = comments.get(rap_id, [])
    copy = dict(rap)
    copy["likes_users"] = rap_likes.get("users", [])
    copy["likes_count"] = len(copy["likes_users"])
    copy["comments_count"] = len(rap_comments)
    copy["views"] = views.get(rap_id, 0)
    return copy


def find_rap(rap_id):
    return next((rap for rap in get_raps() if rap.get("id") == rap_id), None)


def google_login_markup():
    return """
                <a class="btn btn-outline" href="/auth/google" style="width:100%;justify-content:center;margin-bottom:12px;background:#fff;color:#1f2937;border-color:#fff;">
                    <i class="fab fa-google"></i> Continue with Google
                </a>
                <div style="text-align:center;color:var(--text-muted);font-size:.8rem;margin-bottom:1rem;">or use email</div>
"""


def cinematic_animation_markup():
    return """
    <div class="cinematic-intro" id="cinematicIntro">
        <div class="intro-grid"></div>
        <div class="intro-orbit orbit-one"></div>
        <div class="intro-orbit orbit-two"></div>
        <div class="intro-logo-wrap">
            <img src="https://raw.githubusercontent.com/gladifi3rtiwari-prog/rapvault/main/ChatGPTImageMay1202610_29_31A.jpeg" alt="RapVault" class="intro-logo">
            <div class="intro-ring"></div>
        </div>
        <div class="intro-copy">
            <span>Entering</span>
            <strong>RapVault</strong>
            <em>bars loading...</em>
        </div>
        <div class="intro-bars">
            <span></span><span></span><span></span><span></span><span></span>
        </div>
    </div>
"""


def cinematic_animation_css():
    return """

        /* ========== CINEMATIC MOTION UPGRADE ========== */
        .cinematic-intro{
            position:fixed;inset:0;z-index:12000;display:flex;align-items:center;justify-content:center;
            background:#020712;overflow:hidden;animation:cinematicExit .9s ease forwards 4.9s;
        }
        .intro-grid{
            position:absolute;inset:-20%;opacity:.35;
            background:
                linear-gradient(rgba(96,165,250,.12) 1px,transparent 1px),
                linear-gradient(90deg,rgba(96,165,250,.12) 1px,transparent 1px);
            background-size:58px 58px;transform:perspective(650px) rotateX(58deg) translateY(18%);
            animation:gridRush 4.8s cubic-bezier(.2,.8,.2,1) forwards;
        }
        .cinematic-intro::before,.cinematic-intro::after{
            content:"";position:absolute;width:90vmax;height:90vmax;border-radius:50%;filter:blur(34px);opacity:.5;
            background:conic-gradient(from 90deg,transparent,#2563eb,transparent,#f0b429,transparent);
            animation:spinGlow 5.2s linear infinite;
        }
        .cinematic-intro::after{width:60vmax;height:60vmax;animation-direction:reverse;opacity:.28}
        .intro-orbit{position:absolute;border:1px solid rgba(96,165,250,.28);border-radius:50%;animation:orbitPulse 2.4s ease-in-out infinite}
        .orbit-one{width:420px;height:420px}.orbit-two{width:610px;height:610px;animation-delay:.35s}
        .intro-logo-wrap{position:relative;width:176px;height:176px;display:grid;place-items:center;animation:logoLaunch 4.7s cubic-bezier(.15,.85,.25,1) forwards}
        .intro-logo{width:138px;height:138px;border-radius:28px;object-fit:cover;box-shadow:0 0 55px rgba(96,165,250,.72);animation:logoBeat .82s ease-in-out infinite}
        .intro-ring{position:absolute;inset:0;border-radius:34px;border:2px solid rgba(240,180,41,.7);animation:ringSnap 1.15s ease-in-out infinite}
        .intro-copy{position:absolute;bottom:17%;text-align:center;text-transform:uppercase;letter-spacing:0;font-family:'Poppins',sans-serif}
        .intro-copy span,.intro-copy em{display:block;color:var(--text-secondary);font-style:normal;font-size:.85rem;opacity:0;animation:copyRise .7s ease forwards .55s}
        .intro-copy strong{display:block;font-size:clamp(3rem,9vw,8rem);font-weight:900;line-height:.95;background:var(--gradient-2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;opacity:0;animation:titleSlam 1s cubic-bezier(.2,.9,.15,1) forwards .95s}
        .intro-copy em{animation-delay:1.55s;color:var(--gold)}
        .intro-bars{position:absolute;bottom:9%;display:flex;gap:9px;align-items:end;height:54px}
        .intro-bars span{display:block;width:9px;border-radius:9px;background:var(--blue-bright);animation:barBounce .58s ease-in-out infinite}
        .intro-bars span:nth-child(2){animation-delay:.08s;background:#fff}.intro-bars span:nth-child(3){animation-delay:.16s;background:var(--gold)}.intro-bars span:nth-child(4){animation-delay:.24s;background:#fff}.intro-bars span:nth-child(5){animation-delay:.32s;background:var(--blue-bright)}
        .main-site{animation:siteIn .6s ease forwards 5.15s}
        .splash{display:none}
        .logo img{animation:floatLogo 3.8s ease-in-out infinite}
        .hero-badge{animation:badgePulse 2.2s ease-in-out infinite}
        .hero h1{animation:heroLift .9s ease both 5.25s}
        .hero p,.hero-stats,.search-section,.bio-section{animation:softReveal .9s ease both 5.45s}
        .rap-card,.pinned-comments,.admin-panel{opacity:0;transform:translateY(22px) scale(.98)}
        .rap-card.revealed,.pinned-comments.revealed,.admin-panel.revealed{animation:cardReveal .72s ease forwards}
        .rap-card::after{
            content:"";position:absolute;inset:0;border-radius:var(--radius-lg);pointer-events:none;opacity:0;
            background:linear-gradient(120deg,transparent,rgba(255,255,255,.1),transparent);
            transform:translateX(-120%);transition:opacity .3s ease;
        }
        .rap-card:hover::after{opacity:1;animation:shineSweep .8s ease}
        .btn{position:relative;overflow:hidden}.btn::after{content:"";position:absolute;inset:0;background:rgba(255,255,255,.18);transform:translateX(-105%) skewX(-18deg);transition:transform .45s ease}.btn:hover::after{transform:translateX(105%) skewX(-18deg)}
        @keyframes cinematicExit{to{opacity:0;visibility:hidden;pointer-events:none;transform:scale(1.08)}}
        @keyframes gridRush{from{background-position:0 0;transform:perspective(650px) rotateX(58deg) translateY(25%) scale(1.25)}to{background-position:0 640px;transform:perspective(650px) rotateX(58deg) translateY(8%) scale(.9)}}
        @keyframes spinGlow{to{transform:rotate(360deg)}}
        @keyframes orbitPulse{50%{transform:scale(1.08);opacity:.35}100%{transform:scale(1);opacity:1}}
        @keyframes logoLaunch{0%{transform:scale(.25) rotate(-18deg);opacity:0}18%{transform:scale(1.12) rotate(4deg);opacity:1}70%{transform:scale(1) rotate(0)}100%{transform:translateY(-42px) scale(.82)}}
        @keyframes logoBeat{50%{transform:scale(1.05);box-shadow:0 0 80px rgba(96,165,250,.95)}}
        @keyframes ringSnap{50%{transform:scale(1.12) rotate(8deg);opacity:.55}}
        @keyframes copyRise{to{opacity:1;transform:translateY(-10px)}}
        @keyframes titleSlam{0%{opacity:0;transform:translateY(36px) scale(.86)}60%{opacity:1;transform:translateY(-5px) scale(1.04)}100%{opacity:1;transform:translateY(0) scale(1)}}
        @keyframes barBounce{0%,100%{height:16px}50%{height:54px}}
        @keyframes floatLogo{50%{transform:translateY(-4px) rotate(2deg)}}
        @keyframes badgePulse{50%{box-shadow:0 0 24px rgba(96,165,250,.3);transform:translateY(-2px)}}
        @keyframes heroLift{from{opacity:0;transform:translateY(28px)}to{opacity:1;transform:translateY(0)}}
        @keyframes softReveal{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
        @keyframes cardReveal{to{opacity:1;transform:translateY(0) scale(1)}}
        @keyframes shineSweep{to{transform:translateX(120%)}}
        @media (prefers-reduced-motion:reduce){
            .cinematic-intro{display:none}.main-site{animation:none;opacity:1}
            *{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}
        }
        @media(max-width:768px){
            .orbit-one{width:270px;height:270px}.orbit-two{width:390px;height:390px}
            .intro-logo-wrap{width:132px;height:132px}.intro-logo{width:104px;height:104px}
            .intro-copy{bottom:18%}
        }
"""


def cinematic_animation_js():
    return """
        function revealAnimatedElements(){
            const items=document.querySelectorAll('.rap-card,.pinned-comments,.admin-panel');
            if(!('IntersectionObserver' in window)){
                items.forEach(i=>i.classList.add('revealed'));
                return;
            }
            const observer=new IntersectionObserver(entries=>{
                entries.forEach(entry=>{
                    if(entry.isIntersecting){
                        entry.target.classList.add('revealed');
                        observer.unobserve(entry.target);
                    }
                });
            },{threshold:.12});
            items.forEach((item,index)=>{
                item.style.animationDelay=(Math.min(index,8)*70)+'ms';
                observer.observe(item);
            });
        }
        const originalRenderRaps=renderRaps;
        renderRaps=function(raps){
            originalRenderRaps(raps);
            requestAnimationFrame(revealAnimatedElements);
        };
        setTimeout(()=>document.getElementById('cinematicIntro')?.remove(),6200);
        document.addEventListener('DOMContentLoaded',revealAnimatedElements);
"""


def inject_google_login(html):
    login_anchor = '<p class="subtitle">Login to like, comment, and get notified.</p>'
    register_anchor = '<p class="subtitle">Create an account to stay connected.</p>'
    html = html.replace(login_anchor, login_anchor + google_login_markup(), 1)
    html = html.replace(register_anchor, register_anchor + google_login_markup(), 1)
    html = html.replace("</style>", cinematic_animation_css() + "\n    </style>", 1)
    html = html.replace("<body>", "<body>" + cinematic_animation_markup(), 1)
    html = html.replace("        init();", cinematic_animation_js() + "\n        init();", 1)
    return html


ensure_files()


@app.route("/")
def home():
    return inject_google_login(render_template("index.html"))


@app.route("/googlea57b609f2753a8e2.html")
def google_verify():
    return "google-site-verification: googlea57b609f2753a8e2.html", 200


@app.route("/auth/google")
def auth_google():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return (
            "Google login is not configured yet. Add GOOGLE_CLIENT_ID and "
            "GOOGLE_CLIENT_SECRET in Render environment variables.",
            503,
        )
    redirect_uri = "https://rapvault.onrender.com/auth/google/callback"
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/auth/google/callback")
def auth_google_callback():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return redirect("/")

    token = oauth.google.authorize_access_token()
    info = token.get("userinfo") or oauth.google.userinfo()
    email = (info.get("email") or "").strip().lower()
    name = (info.get("name") or info.get("given_name") or email.split("@")[0]).strip()

    if not email:
        return redirect("/")

    role = "admin" if email == ADMIN_EMAIL else "user"
    users = get_users()
    user = next((u for u in users if u.get("email", "").lower() == email), None)

    if user:
        user["name"] = name or user.get("name", "User")
        user["role"] = role
        user["auth_provider"] = "google"
    elif email != ADMIN_EMAIL:
        users.append(
            {
                "name": name,
                "email": email,
                "password": "",
                "subscribed": True,
                "role": role,
                "auth_provider": "google",
            }
        )
    save_json(USERS_FILE, users)

    subs = get_subscribers()
    if email not in subs:
        subs.append(email)
        save_json(SUBS_FILE, subs)

    session["user"] = {"name": name or "User", "email": email, "role": role}
    return redirect("/")


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    subscribe = data.get("subscribe", True)

    if not name or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    if email == ADMIN_EMAIL:
        return jsonify({"error": "This email is reserved for admin!"}), 403

    users = get_users()
    if any(u.get("email") == email for u in users):
        return jsonify({"error": "Email already registered"}), 400

    users.append(
        {
            "name": name,
            "email": email,
            "password": password,
            "subscribed": subscribe,
            "role": "user",
            "auth_provider": "password",
        }
    )
    save_json(USERS_FILE, users)

    if subscribe:
        subs = get_subscribers()
        if email not in subs:
            subs.append(email)
            save_json(SUBS_FILE, subs)

    session["user"] = {"name": name, "email": email, "role": "user"}
    return jsonify({"success": True, "user": session["user"]})


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    subscribe = data.get("subscribe", True)

    if not email or not password:
        return jsonify({"error": "Please fill in both email and password"}), 400

    if email == ADMIN_EMAIL:
        if password != ADMIN_PASSWORD:
            return jsonify({"error": "Invalid password for admin account"}), 401
        session["user"] = {"name": "Kartikeya", "email": ADMIN_EMAIL, "role": "admin"}
        return jsonify({"success": True, "user": session["user"]})

    users = get_users()
    user = next(
        (u for u in users if u.get("email") == email and u.get("password") == password),
        None,
    )

    if not user:
        return jsonify({"error": "Email or password is incorrect. Please try again or register."}), 401

    subs = get_subscribers()
    if subscribe and email not in subs:
        subs.append(email)
        save_json(SUBS_FILE, subs)
    elif not subscribe and email in subs:
        subs.remove(email)
        save_json(SUBS_FILE, subs)

    session["user"] = {
        "name": user.get("name", "User"),
        "email": user.get("email"),
        "role": user.get("role", "user"),
    }
    return jsonify({"success": True, "user": session["user"]})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("user", None)
    return jsonify({"success": True})


@app.route("/api/user")
def api_user():
    user = session.get("user")
    return jsonify(user) if user else jsonify(None)


@app.route("/api/subscribe", methods=["POST"])
def api_subscribe():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get("email", "").strip().lower()
    if not email or "@" not in email:
        return jsonify({"error": "Please enter a valid email"}), 400

    subs = get_subscribers()
    if email in subs:
        return jsonify({"success": True, "message": "Already subscribed!"})
    subs.append(email)
    save_json(SUBS_FILE, subs)
    return jsonify({"success": True, "message": "Subscribed!"})


@app.route("/api/bio")
def api_bio():
    return jsonify(get_bio())


@app.route("/api/bio", methods=["POST"])
def api_save_bio():
    if not is_admin():
        return jsonify({"error": "Admin only"}), 403
    data = request.get_json(force=True, silent=True) or {}
    bio = {
        "name": data.get("name", "").strip() or "Kartikeya",
        "bio": data.get("bio", "").strip(),
        "photo": data.get("photo", "").strip(),
    }
    save_json(BIO_FILE, bio)
    return jsonify({"success": True, "bio": bio})


@app.route("/api/raps")
def api_raps():
    tag = request.args.get("tag", "all").lower()
    search = request.args.get("search", "").strip().lower()
    raps = [enrich_rap(rap) for rap in get_raps()]

    if not is_admin():
        raps = [rap for rap in raps if not rap.get("is_draft")]
    if tag and tag != "all":
        raps = [rap for rap in raps if rap.get("tag", "").lower() == tag]
    if search:
        raps = [
            rap
            for rap in raps
            if search in rap.get("title", "").lower()
            or search in rap.get("preview", "").lower()
            or search in rap.get("lyrics", "").lower()
            or search in rap.get("tag", "").lower()
        ]

    raps.sort(key=lambda rap: rap.get("date", ""), reverse=True)
    return jsonify(raps)


@app.route("/api/rap/<rap_id>")
def api_rap_detail(rap_id):
    rap = find_rap(rap_id)
    if not rap:
        return jsonify({"error": "Rap not found"}), 404
    if rap.get("is_draft") and not is_admin():
        return jsonify({"error": "This rap is coming soon"}), 403

    views = get_views()
    views[rap_id] = views.get(rap_id, 0) + 1
    save_json(VIEWS_FILE, views)

    enriched = enrich_rap(rap)
    enriched["views"] = views[rap_id]
    enriched["comments"] = get_comments().get(rap_id, [])
    return jsonify(enriched)


@app.route("/api/like/<rap_id>", methods=["POST"])
def api_like(rap_id):
    user = session.get("user")
    if not user:
        return jsonify({"error": "Login required"}), 401
    if not find_rap(rap_id):
        return jsonify({"error": "Rap not found"}), 404

    likes = get_likes()
    likes.setdefault(rap_id, {"users": []})
    email = user["email"]
    if email in likes[rap_id]["users"]:
        likes[rap_id]["users"].remove(email)
        liked = False
    else:
        likes[rap_id]["users"].append(email)
        liked = True
    save_json(LIKES_FILE, likes)
    return jsonify({"success": True, "liked": liked, "likes_count": len(likes[rap_id]["users"])})


@app.route("/api/comment/<rap_id>", methods=["POST"])
def api_comment(rap_id):
    user = session.get("user")
    if not user:
        return jsonify({"error": "Login required"}), 401
    if not find_rap(rap_id):
        return jsonify({"error": "Rap not found"}), 404

    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Comment is required"}), 400

    comments = get_comments()
    comments.setdefault(rap_id, [])
    comment = {
        "id": str(uuid.uuid4()),
        "user": user.get("name", "User"),
        "email": user.get("email"),
        "text": text,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    comments[rap_id].append(comment)
    save_json(COMMENTS_FILE, comments)
    return jsonify({"success": True, "comment": comment})


@app.route("/api/stats")
def api_stats():
    raps = get_raps()
    likes = get_likes()
    views = get_views()
    total_likes = sum(len(item.get("users", [])) for item in likes.values())
    return jsonify(
        {
            "raps_count": len([rap for rap in raps if not rap.get("is_draft")]),
            "subscribers_count": len(get_subscribers()),
            "total_likes": total_likes,
            "total_views": sum(views.values()),
        }
    )


@app.route("/api/pinned-comments")
def api_pinned_comments():
    return jsonify(get_pinned_comments())


@app.route("/api/admin/post", methods=["POST"])
def api_admin_post():
    if not is_admin():
        return jsonify({"error": "Admin only"}), 403

    data = request.get_json(force=True, silent=True) or {}
    title = data.get("title", "").strip()
    tag = data.get("tag", "").strip().lower()
    preview = data.get("preview", "").strip()
    lyrics = data.get("lyrics", "").strip()
    if not title or not tag or not preview or not lyrics:
        return jsonify({"error": "All fields required"}), 400

    raps = get_raps()
    rap = {
        "id": str(uuid.uuid4()),
        "title": title,
        "tag": tag,
        "preview": preview,
        "lyrics": lyrics,
        "date": data.get("release_date") or now_label(),
        "is_draft": bool(data.get("is_draft", False)),
        "release_date": data.get("release_date"),
        "featured": False,
    }
    raps.append(rap)
    save_json(RAPS_FILE, raps)
    return jsonify({"success": True, "rap": rap})


@app.route("/api/admin/delete/<rap_id>", methods=["DELETE"])
def api_admin_delete(rap_id):
    if not is_admin():
        return jsonify({"error": "Admin only"}), 403
    raps = [rap for rap in get_raps() if rap.get("id") != rap_id]
    save_json(RAPS_FILE, raps)
    return jsonify({"success": True})


@app.route("/api/admin/feature/<rap_id>", methods=["POST"])
def api_admin_feature(rap_id):
    if not is_admin():
        return jsonify({"error": "Admin only"}), 403
    raps = get_raps()
    found = False
    for rap in raps:
        if rap.get("id") == rap_id:
            rap["featured"] = not rap.get("featured", False)
            found = True
            break
    if not found:
        return jsonify({"error": "Rap not found"}), 404
    save_json(RAPS_FILE, raps)
    return jsonify({"success": True})


@app.route("/api/admin/pin-comment", methods=["POST"])
def api_admin_pin_comment():
    if not is_admin():
        return jsonify({"error": "Admin only"}), 403
    data = request.get_json(force=True, silent=True) or {}
    comment_id = data.get("comment_id")
    rap_id = data.get("rap_id")
    comment = next(
        (c for c in get_comments().get(rap_id, []) if c.get("id") == comment_id),
        None,
    )
    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    pinned = get_pinned_comments()
    if not any(c.get("id") == comment_id for c in pinned):
        pinned.append({**comment, "rap_id": rap_id})
        save_json(PINNED_COMMENTS_FILE, pinned)
    return jsonify({"success": True})


@app.route("/admin/stats")
def admin_stats():
    if not is_admin():
        return redirect("/")
    likes = get_likes()
    comments = get_comments()
    views = get_views()
    total_likes = sum(len(item.get("users", [])) for item in likes.values())
    total_views = sum(views.values())
    return render_template(
        "admin_stats.html",
        raps=get_raps(),
        subs=get_subscribers(),
        likes=likes,
        comments=comments,
        views=views,
        total_likes=total_likes,
        total_views=total_views,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
