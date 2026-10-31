# ═══════════════════════════════════════════════════════════════
# bot_runner.py — the bot process itself (started by app.py for every user bot; you normally never run this by hand)
# ═══════════════════════════════════════════════════════════════

import asyncio
import time
import os
import threading
from flask import Flask
from cfonts import render

# Auto-import दोनों modules (ये अपने आप load होंगे)
import login_engine
import bot_core

# Globals को share करने के लिए (bot_core में ही हैं, यहाँ reference)
from bot_core import (
    TcPOnLine, TcPChaT,
    build_ob55_online_auth, create_auth_token_chat,
    bot_uid, ToKen, region
)


PORT = 9181

app = Flask(__name__)


def load_credentials_from_file(path=None):
    path = path or os.environ.get("BOT_FILE", "bot.txt")
    """Read uid / password / region as key=value lines from a credentials file.
    This is the ONLY place real account credentials should live — never hardcode
    them in source. The web panel's "Save & Start" button writes this same file."""
    data = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line or line.startswith("#"):
                    continue
                k, v = line.split("=", 1)
                data[k.strip().lower()] = v.strip()
    except FileNotFoundError:
        return None
    if "uid" not in data or "password" not in data:
        return None
    return data


async def MaiiiinE():
    """Login + TCP start"""
    global bot_uid, ToKen, region

    bot_core.FULL_RESTART_REQUESTED = False  # clear so this fresh login cycle runs normally

    creds = load_credentials_from_file()
    if not creds:
        print(f"[-] {os.environ.get('BOT_FILE', 'bot.txt')} not found or incomplete (need uid= and password=).")
        print("[-] Set it via the web panel ('Save & Start') or edit bot.txt directly.")
        await asyncio.sleep(10)
        return

    # nick= in bot.txt (set from the website) becomes the brand name shown in menus
    if creds.get("nick"):
        bot_core.BOT_BRAND = creds["nick"]

    Uid = creds["uid"]
    Pw = creds["password"]
    REGION_PREF = creds.get("region", "BD")

    # ─── Login ───
    print("[*] Starting login...")
    result = await login_engine.do_login(Uid, Pw, REGION_PREF)
    if not result:
        print("[-] Login failed, retry in 10s...")
        await asyncio.sleep(10)
        return

    # ─── bot_core के globals set करें ───
    bot_core.bot_uid = result["bot_uid"]
    bot_core.ToKen   = result["token"]
    bot_core.region  = result["region"]

    key       = result["key"]
    iv        = result["iv"]
    timestamp = result["timestamp"]
    online_ip = result["online_ip"]
    online_port = result["online_port"]
    chat_ip   = result["chat_ip"]
    chat_port = result["chat_port"]
    acc_name  = result["account_name"]

    print(f"[+] UID: {result['bot_uid']} | Region: {result['region']} | Name: {acc_name}")

    # ─── Auth tokens ───
    ChatAutH = create_auth_token_chat(int(result["bot_uid"]), result["token"], int(timestamp), key, iv)
    OnlineAutH, _ = build_ob55_online_auth(int(result["bot_uid"]), result["token"], int(timestamp), key, iv)

    # ─── TCP tasks start ───
    ready_event = asyncio.Event()
    t1 = asyncio.create_task(
        TcPChaT(chat_ip, chat_port, ChatAutH, key, iv, ready_event, result["region"])
    )
    await ready_event.wait()
    await asyncio.sleep(1)
    t2 = asyncio.create_task(
        TcPOnLine(online_ip, online_port, key, iv, OnlineAutH)
    )

    # ─── Banner ───
    print(render('TEAM NEXUS', colors=['cyan', 'blue'], align='center'))
    print(f" - Region => {result['region']}")
    print(f" - Bot Online! UID: {result['bot_uid']} | Name: {acc_name}\n")

    # ─── Forever run ───
    await asyncio.gather(t1, t2)


async def StarTinG():
    """Auto-restart loop (हर 7 घंटे में token refresh)"""
    while True:
        try:
            await asyncio.wait_for(MaiiiinE(), timeout=7 * 60 * 60)
        except asyncio.TimeoutError:
            print("[!] Token expired, restarting...")
        except Exception as e:
            print(f"[!] Error: {e} -> Restarting in 5s...")
            await asyncio.sleep(5)


# ───────────────────────────────────────────────────────────────
# Flask (Render health-check এর জন্য)
# ───────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return "Bot is active and running successfully!"


@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


def run_web():
    print(f"[*] Flask listening on 0.0.0.0:{PORT}")
    app.run(
        host="0.0.0.0",
        port=PORT,
        use_reloader=False,   # duplicate process এড়াতে
        threaded=True,
    )


# ───────────────────────────────────────────────────────────────
# Entry
# ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 1) Flask কে daemon thread-এ চালাও → PORT bind হবে → Render happy
    # (skipped when hasib.py launched us: the website already owns the public port)
    if not os.environ.get("HASIB_WEB"):
        threading.Thread(target=run_web, daemon=True).start()

    # 2) asyncio bot loop main thread-এ (এটাই আসল কাজ)
    try:
        asyncio.run(StarTinG())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")