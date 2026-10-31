#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#  app.py — HASIB CODEX  •  ONE-FILE LAUNCHER + WEB PANEL
#
#  Run:   python app.py
#  Then open the link it prints (on a host like Render/Railway/VPS it is
#  your public site URL).  The bot does NOT start by itself — you log in
#  to the website, enter UID / Password / Nick and press "Save & Start".
#  (Set  autostart=1  in bot.txt or tick the switch in the panel if you
#  want it to come online automatically when the site boots.)
#
#  Logins (change them any time in the Admin page):
#     user : teamnexus1  / teamnexus1
#     admin: teamnexusadmin   / teamnexusadmin
# ═══════════════════════════════════════════════════════════════
import collections
import hmac
import hashlib
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
from datetime import timedelta
from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, HERE)

# DATA_DIR = where users.json, bot.txt, bot1.txt, bot2.txt ... are saved.
# On Render / Railway the normal disk is wiped on every deploy, so attach a volume/disk and set DATA_DIR to its path.
DATA_DIR = os.environ.get("DATA_DIR") or HERE
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
KEY_FILE = os.path.join(DATA_DIR, ".secret_key")
PORT = int(os.environ.get("PORT", "8080"))
MAX_KEY_USERS = int(os.environ.get("MAX_KEY_USERS", "200"))   # how many password-only accounts may be created
MAX_RUNNING_BOTS = int(os.environ.get("MAX_RUNNING_BOTS", "50"))

# ───────────────────────── users ─────────────────────────
DEFAULT_USERS = {"alphathefucker": (os.environ.get("USER_PASS", "alphathefucker"), "user"),
                 "alphatheadmin": (os.environ.get("ADMIN_PASS", "alphatheadmin"), "admin")}
_users_lock = threading.Lock()


def _seed_users():
    return {n: {"role": r, "hash": generate_password_hash(p), "bot": "bot.txt"} for n, (p, r) in DEFAULT_USERS.items()}


def load_users():
    with _users_lock:
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                u = json.load(f)
            if isinstance(u, dict) and u and all(isinstance(v, dict) and "hash" in v for v in u.values()):
                return u
        except Exception:
            pass
        u = _seed_users()                     # first run, or an old-format file → fresh seed
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(u, f, indent=2)
        return u


def save_users(u):
    with _users_lock:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(u, f, indent=2)


# ───────────────────────── bot files  (bot.txt, bot1.txt, bot2.txt ...) ─────────────────────────
# One file per bot "slot". slot = file name without .txt  ("bot", "bot1", "bot2" ...)
SLOT_RE = re.compile(r"^bot\d*$")


def valid_slot(slot):
    return bool(SLOT_RE.match(str(slot)))


def slot_path(slot):
    p = os.path.join(DATA_DIR, f"{slot}.txt")
    if slot == "bot" and not os.path.exists(p) and os.path.exists(os.path.join(HERE, "bot.txt")):
        try:
            shutil.copy(os.path.join(HERE, "bot.txt"), p)       # first run with a separate DATA_DIR
        except Exception:
            pass
    return p


def mode_path(slot):
    return os.path.join(DATA_DIR, "platform_mode.txt" if slot == "bot" else f"platform_mode_{slot}.txt")


def read_bot_txt(slot="bot"):
    d = {"uid": "", "password": "", "nick": "ALPHA", "region": "PK", "autostart": "0"}
    try:
        with open(slot_path(slot), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                d[k.strip().lower()] = v.strip()
    except FileNotFoundError:
        pass
    return d


def write_bot_txt(d, slot="bot"):
    with open(slot_path(slot), "w", encoding="utf-8") as f:
        f.write(f"# {slot}.txt — written by the website (app.py). You can also edit it by hand.\n")
        for k in ("uid", "password", "nick", "region", "autostart"):
            f.write(f"{k}={d.get(k, '')}\n")


def creds_ready(d=None, slot="bot"):
    d = d or read_bot_txt(slot)
    uid, pw = d.get("uid", ""), d.get("password", "")
    return uid.isdigit() and set(uid) != {"0"} and bool(pw) and not pw.startswith("PASTE_")


def all_slots():
    slots = {"bot"}
    for n in os.listdir(DATA_DIR):
        m = re.match(r"^(bot\d*)\.txt$", n)
        if m:
            slots.add(m.group(1))
    return sorted(slots, key=lambda x: int(x[3:] or 0))


def new_slot():
    used = set(all_slots())
    for u in load_users().values():
        used.add(str(u.get("bot", "bot.txt"))[:-4])
    n = 1
    while f"bot{n}" in used:
        n += 1
    return f"bot{n}"


# ───────────────────────── bot processes (one per slot) ─────────────────────────
BOTS = {}                       # slot -> state
_bot_lock = threading.RLock()
_log_lock = threading.Lock()


def st(slot):
    with _bot_lock:
        if slot not in BOTS:
            BOTS[slot] = {"proc": None, "started": None, "want": False, "restarts": 0,
                          "logs": collections.deque(maxlen=1500), "log_id": 0}
        return BOTS[slot]


def log(line, src="web", slot="bot"):
    s_ = st(slot)
    with _log_lock:
        s_["log_id"] += 1
        s_["logs"].append({"id": s_["log_id"], "t": time.strftime("%H:%M:%S"), "src": src, "msg": str(line).rstrip()})


def _pump(proc, slot):
    for line in iter(proc.stdout.readline, ""):
        if line.strip():
            log(line, "bot", slot)
    proc.stdout.close()


def bot_running(slot="bot"):
    p = st(slot)["proc"]
    return p is not None and p.poll() is None


def start_bot(slot="bot"):
    s_ = st(slot)
    with _bot_lock:
        if bot_running(slot):
            return False, "Bot is already running."
        if not creds_ready(slot=slot):
            return False, "Save a valid UID and password first."
        if sum(1 for k in list(BOTS) if bot_running(k)) >= MAX_RUNNING_BOTS:
            return False, "Server is full right now. Try again later."
        env = dict(os.environ, HASIB_WEB="1", PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8",
                   BOT_FILE=slot_path(slot), BOT_MODE_FILE=mode_path(slot), BOT_SLOT=slot)
        env.pop("PORT", None)
        try:
            proc = subprocess.Popen([sys.executable, "-u", os.path.join(HERE, "bot_runner.py")], cwd=HERE, env=env,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                    encoding="utf-8", errors="replace", bufsize=1)
        except Exception as e:
            return False, f"Could not start: {e}"
        s_.update(proc=proc, started=time.time(), want=True)
    threading.Thread(target=_pump, args=(proc, slot), daemon=True).start()
    log("Bot process started.", slot=slot)
    return True, "Bot starting…"


def stop_bot(slot="bot"):
    s_ = st(slot)
    with _bot_lock:
        s_["want"] = False
        p = s_["proc"]
        if p is None or p.poll() is not None:
            return False, "Bot is not running."
        p.terminate()
        try:
            p.wait(timeout=8)
        except subprocess.TimeoutExpired:
            p.kill()
        s_["started"] = None
    log("Bot stopped.", slot=slot)
    return True, "Bot stopped."


def _watchdog():
    """If a bot dies on its own while we want it running, bring it back."""
    while True:
        time.sleep(5)
        try:
            for slot in list(BOTS):
                s_ = BOTS[slot]
                if s_["want"] and not bot_running(slot):
                    s_["restarts"] += 1
                    log("Bot exited unexpectedly — restarting in 5s…", slot=slot)
                    time.sleep(5)
                    if s_["want"] and not bot_running(slot):
                        start_bot(slot)
        except Exception as e:  # never let the watchdog die
            print(f"watchdog: {e}")


# ───────────────────────── flask app ─────────────────────────
app = Flask(__name__, static_folder="static", template_folder="templates")


def _secret():
    try:
        with open(KEY_FILE, "r") as f:
            k = f.read().strip()
            if len(k) >= 32:
                return k
    except FileNotFoundError:
        pass
    k = secrets.token_hex(32)
    with open(KEY_FILE, "w") as f:
        f.write(k)
    return k


app.secret_key = os.environ.get("SECRET_KEY") or _secret()
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  PERMANENT_SESSION_LIFETIME=timedelta(days=7), TEMPLATES_AUTO_RELOAD=True)

_fails = collections.defaultdict(list)   # ip -> [timestamps]


def client_ip():
    return (request.headers.get("X-Forwarded-For", request.remote_addr or "?").split(",")[0]).strip()


def login_required(admin=False):
    def deco(fn):
        @wraps(fn)
        def wrap(*a, **k):
            if "user" not in session:
                if request.path.startswith("/api/"):
                    return jsonify(ok=False, error="Not logged in"), 401
                return redirect(url_for("login_page"))
            if admin and session.get("role") != "admin":
                return jsonify(ok=False, error="Admin only"), 403
            return fn(*a, **k)
        return wrap
    return deco


def cur_slot():
    """The bot file this logged-in person controls. Admins may pass ?slot=botN to control any bot."""
    users = load_users()
    me = users.get(session.get("user"), {})
    slot = str(me.get("bot", "bot.txt"))[:-4] or "bot"
    if session.get("role") == "admin":
        want = request.args.get("slot") or (request.get_json(silent=True) or {}).get("slot") if request.method != "GET" \
            else request.args.get("slot")
        if want and valid_slot(want) and (want in all_slots()):
            slot = want
    return slot if valid_slot(slot) else "bot"


@app.after_request
def _headers(r):
    r.headers["X-Content-Type-Options"] = "nosniff"
    r.headers["X-Frame-Options"] = "SAMEORIGIN"
    r.headers["Cache-Control"] = "no-store" if request.path.startswith("/api/") else "no-cache"
    return r


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("panel"))
    return render_template("landing.html")


@app.route("/signup")
def signup_page():
    # Public sign-up is intentionally closed: anyone who signed up could control the bot account.
    # The owner creates logins from  Pro Dashboard -> Admin Panel.
    return redirect(url_for("login_page"))


@app.route("/healthz")
def healthz():
    return jsonify(status="ok")


@app.route("/login")
def login_page():
    if "user" in session:
        return redirect(url_for("panel"))
    return render_template("login.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    ip = client_ip()
    now = time.time()
    _fails[ip] = [t for t in _fails[ip] if now - t < 300]
    if len(_fails[ip]) >= 6:
        return jsonify(ok=False, status="error", message="TOO MANY TRIES - WAIT 5 MIN", error="Too many attempts. Wait 5 minutes."), 429
    data = request.get_json(silent=True) or {}
    name = str(data.get("username", "")).strip().lower()
    pw = str(data.get("password", ""))
    u = load_users().get(name)
    if u and check_password_hash(u["hash"], pw):
        session.clear()
        session.permanent = True
        session["user"], session["role"] = name, u.get("role", "user")
        _fails.pop(ip, None)
        log(f"Login: {name} ({u.get('role')}) from {ip}", slot=str(u.get("bot", "bot.txt"))[:-4])
        return jsonify(ok=True, status="success", message="Login OK", redirect=url_for("panel"))
    _fails[ip].append(now)
    return jsonify(ok=False, status="error", message="WRONG USERNAME OR PASSWORD", error="Wrong username or password."), 401


def _finish_login(name, u, ip):
    session.clear()
    session.permanent = True
    session["user"], session["role"] = name, u.get("role", "user")
    _fails.pop(ip, None)
    log(f"Login: {name} ({u.get('role')}) from {ip}", slot=str(u.get("bot", "bot.txt"))[:-4])


@app.route("/api/quick", methods=["POST"])
def api_quick():
    """Password-only access: type any password (6+ chars). New password = your own account + your own bot file
    (bot1.txt, bot2.txt ...). Same password again = back into the same account."""
    ip = client_ip()
    now = time.time()
    _fails[ip] = [t for t in _fails[ip] if now - t < 300]
    if len(_fails[ip]) >= 6:
        return jsonify(ok=False, status="error", message="TOO MANY TRIES - WAIT 5 MIN", error="Too many attempts. Wait 5 minutes."), 429
    pw = str((request.get_json(silent=True) or {}).get("password", ""))
    if len(pw) < 6 or len(pw) > 64:
        return jsonify(ok=False, status="error", message="PASSWORD: 6-64 CHARACTERS", error="Password must be 6-64 characters."), 400
    name = "u" + hmac.new(app.secret_key.encode(), pw.encode(), hashlib.sha256).hexdigest()[:12]
    users = load_users()
    u = users.get(name)
    created = False
    if u is None:
        if sum(1 for v in users.values() if v.get("key")) >= MAX_KEY_USERS:
            return jsonify(ok=False, status="error", message="SERVER FULL", error="No more free accounts right now."), 503
        slot = new_slot()
        write_bot_txt({"uid": "", "password": "", "nick": "TEAM NEXUS", "region": "PK", "autostart": "0"}, slot)
        u = {"role": "user", "hash": generate_password_hash(pw), "bot": slot + ".txt", "key": True}
        users[name] = u
        save_users(users)
        created = True
    elif not check_password_hash(u["hash"], pw):
        _fails[ip].append(now)
        return jsonify(ok=False, status="error", message="WRONG PASSWORD", error="Wrong password."), 401
    _finish_login(name, u, ip)
    return jsonify(ok=True, status="success", message="NEW BOT CREATED" if created else "Login OK",
                   created=created, redirect=url_for("panel"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


@app.route("/panel")
@login_required()
def panel():
    return render_template("panel.html", user=session["user"], role=session["role"])


@app.route("/pro")
@login_required()
def pro_dashboard():
    return render_template("pro.html", user=session["user"], role=session["role"])


# ───────────────────────── API ─────────────────────────
def _catalog():
    try:
        import extra_cmds
        extra_cmds.build_help_pages()
        return extra_cmds.catalog()
    except Exception as e:
        log(f"catalog error: {e}")
        return []


@app.route("/api/status")
@login_required()
def api_status():
    slot = cur_slot()
    d = read_bot_txt(slot)
    s_ = st(slot)
    mf = mode_path(slot)
    up = int(time.time() - s_["started"]) if bot_running(slot) and s_["started"] else 0
    return jsonify(ok=True, running=bot_running(slot), uptime=up, restarts=s_["restarts"],
                   uid=d["uid"][:3] + "•••" + d["uid"][-2:] if len(d["uid"]) > 5 else d["uid"],
                   nick=d["nick"], region=d["region"], autostart=d["autostart"] == "1",
                   has_password=creds_ready(d), commands=len(_catalog()),
                   mode=(open(mf).read().strip() if os.path.exists(mf) else "phone"),
                   user=session["user"], role=session["role"], slot=slot + ".txt")


@app.route("/api/config", methods=["GET", "POST"])
@login_required()
def api_config():
    slot = cur_slot()
    d = read_bot_txt(slot)
    if request.method == "GET":
        return jsonify(ok=True, uid=d["uid"], nick=d["nick"], region=d["region"], slot=slot + ".txt",
                       autostart=d["autostart"] == "1", has_password=bool(d["password"]) and not d["password"].startswith("PASTE_"))
    j = request.get_json(silent=True) or {}
    uid = str(j.get("uid", d["uid"])).strip()
    if uid and not uid.isdigit():
        return jsonify(ok=False, error="UID must be numbers only."), 400
    pw = str(j.get("password", "")).strip()          # blank = keep the saved one
    nick = str(j.get("nick", d["nick"])).strip()[:20] or "TEAM NEXUS"
    region = str(j.get("region", d["region"])).strip().upper()[:4] or "PK"
    if any(c in nick + region + pw + uid for c in "\r\n"):
        return jsonify(ok=False, error="Invalid characters."), 400
    d.update(uid=uid, nick=nick, region=region)
    if pw:
        d["password"] = pw
    if "autostart" in j:
        d["autostart"] = "1" if j["autostart"] else "0"
    write_bot_txt(d, slot)
    log(f"{slot}.txt updated by {session['user']} (uid={uid}, nick={nick}, region={region})", slot=slot)
    msg = "Saved."
    if j.get("start"):
        if bot_running(slot):
            stop_bot(slot)
            time.sleep(1)
        ok, m = start_bot(slot)
        msg = "Saved. " + m
        return jsonify(ok=ok, message=msg, error=None if ok else m)
    return jsonify(ok=True, message=msg)


@app.route("/api/bot/<action>", methods=["POST"])
@login_required()
def api_bot(action):
    slot = cur_slot()
    if action == "start":
        ok, m = start_bot(slot)
    elif action == "stop":
        ok, m = stop_bot(slot)
    elif action == "restart":
        stop_bot(slot)
        time.sleep(1)
        ok, m = start_bot(slot)
    else:
        return jsonify(ok=False, error="Unknown action"), 404
    log(f"{action} pressed by {session['user']}", slot=slot)
    return jsonify(ok=ok, message=m, error=None if ok else m)


@app.route("/api/mode", methods=["POST"])
@login_required()
def api_mode():
    slot = cur_slot()
    m = str((request.get_json(silent=True) or {}).get("mode", "")).lower()
    if m not in ("pc", "phone"):
        return jsonify(ok=False, error="mode must be pc or phone"), 400
    with open(mode_path(slot), "w") as f:
        f.write(m)
    return jsonify(ok=True, message=f"Login mode: {m.upper()} (applies on next Start / Restart)")


@app.route("/api/logs")
@login_required()
def api_logs():
    slot = cur_slot()
    since = int(request.args.get("since", 0) or 0)
    with _log_lock:
        rows = [r for r in st(slot)["logs"] if r["id"] > since]
    return jsonify(ok=True, logs=rows[-400:], last=rows[-1]["id"] if rows else since)


@app.route("/api/logs/clear", methods=["POST"])
@login_required()
def api_logs_clear():
    with _log_lock:
        st(cur_slot())["logs"].clear()
    return jsonify(ok=True)


@app.route("/api/bots")
@login_required(admin=True)
def api_bots():
    """Admin: every bot file on the server, who owns it, and whether it is running."""
    owners = {}
    for n, v in load_users().items():
        owners.setdefault(str(v.get("bot", "bot.txt"))[:-4], []).append(n)
    out = []
    for slot in all_slots():
        d = read_bot_txt(slot)
        out.append({"slot": slot + ".txt", "owners": owners.get(slot, []), "running": bot_running(slot),
                    "uid": d["uid"], "nick": d["nick"], "has_password": creds_ready(d)})
    return jsonify(ok=True, bots=out)


@app.route("/api/commands")
@login_required()
def api_commands():
    return jsonify(ok=True, commands=_catalog())


@app.route("/api/zones")
@login_required()
def api_zones():
    import extra_cmds
    return jsonify(ok=True, zones=[{"code": k, "label": v[0], "tz": v[1]} for k, v in extra_cmds.ZONES.items()])


@app.route("/api/password", methods=["POST"])
@login_required()
def api_password():
    j = request.get_json(silent=True) or {}
    users = load_users()
    me = users[session["user"]]
    if me.get("key"):
        return jsonify(ok=False, error="Password-only accounts cannot change password. Log in with a new password to get a new bot."), 400
    if not check_password_hash(me["hash"], str(j.get("old", ""))):
        return jsonify(ok=False, error="Current password is wrong."), 400
    new = str(j.get("new", ""))
    if len(new) < 4:
        return jsonify(ok=False, error="New password must be at least 4 characters."), 400
    me["hash"] = generate_password_hash(new)
    save_users(users)
    return jsonify(ok=True, message="Password changed.")


@app.route("/api/users", methods=["GET", "POST", "DELETE"])
@login_required(admin=True)
def api_users():
    users = load_users()
    if request.method == "GET":
        return jsonify(ok=True, users=[{"name": n, "role": v.get("role", "user"), "bot": v.get("bot", "bot.txt")} for n, v in users.items()])
    j = request.get_json(silent=True) or {}
    name = str(j.get("name", "")).strip().lower()
    if not name or not name.replace("_", "").isalnum() or len(name) > 24:
        return jsonify(ok=False, error="Username: letters/numbers/_ only (max 24)."), 400
    if request.method == "DELETE":
        if name == session["user"]:
            return jsonify(ok=False, error="You can't delete yourself."), 400
        if users.pop(name, None) is None:
            return jsonify(ok=False, error="No such user."), 404
        save_users(users)
        return jsonify(ok=True, message=f"Deleted {name}.")
    pw = str(j.get("password", ""))
    role = "admin" if j.get("role") == "admin" else "user"
    if len(pw) < 4:
        return jsonify(ok=False, error="Password must be at least 4 characters."), 400
    prev = users.get(name, {})
    users[name] = {"role": role, "hash": generate_password_hash(pw), "bot": prev.get("bot", "bot.txt")}
    save_users(users)
    return jsonify(ok=True, message=f"Saved {name} ({role}).")


# ───────────────────────── main ─────────────────────────
def _lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    load_users()
    threading.Thread(target=_watchdog, daemon=True).start()
    for slot in all_slots():
        d = read_bot_txt(slot)
        if d.get("autostart") == "1" and creds_ready(d):
            log("autostart=1 → starting bot", slot=slot)
            start_bot(slot)
    pub = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("PUBLIC_URL") or \
        (("https://" + os.environ["RAILWAY_PUBLIC_DOMAIN"]) if os.environ.get("RAILWAY_PUBLIC_DOMAIN") else "")
    print("\n" + "═" * 56)
    print("  TEAM NEXUS • Web Panel is LIVE")
    print(f"  Local : http://127.0.0.1:{PORT}")
    print(f"  LAN   : http://{_lan_ip()}:{PORT}")
    if pub:
        print(f"  Public: {pub}")
    if os.environ.get("ADMIN_PASS") and os.environ.get("USER_PASS"):
        print("  Logins: set from ADMIN_PASS / USER_PASS environment variables")
    else:
        print("  Logins: teamnexus1 / teamnexus1   |   admin: teamnexusadmin / teamnexusadmin   (set USER_PASS / ADMIN_PASS to change!)")
    print("═" * 56 + "\n")
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        [stop_bot(k) for k in list(BOTS)]
        print("\nBye.")
