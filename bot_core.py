# ═══════════════════════════════════════════════════════════════
# bot_core.py — HASIB COMMUNITY TCP BOT (100% FULL & FIXED)
# Dev: ALPHA | TG: 03008891580
# ═══════════════════════════════════════════════════════════════

import asyncio, random, json, os, time, re
import extra_cmds
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from xC4 import *
from xP import JoinSq, OpenCh, MsqSq, ExitSq
from byte import Encrypt_ID, encrypt_api
from Pb2 import DEcwHisPErMsG_pb2, sQ_pb2

import urllib3
import login_engine
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════════════════════════════════════════════
# CREDIT
# ═══════════════════════════════════════════════════════════════
CREDIT_NAME = "TEAM NEXUS"
CREDIT_DEV  = "ALPHA"
CREDIT_TG   = "03008891580

# ═══════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMOTES_PATH       = os.path.join(BASE_DIR, "emotes.json")
EMOTE_MENU_PATH   = os.path.join(BASE_DIR, "emote_menu.json")
SINGLE_EMOTE_PATH = os.path.join(BASE_DIR, "singele_emote.json")
SPAM_TARGETS_FILE = os.path.join(BASE_DIR, "spam_targets.json")

# ═══════════════════════════════════════════════════════════════
# GLOBALS
# ═══════════════════════════════════════════════════════════════
online_writer = None
whisper_writer = None
FULL_RESTART_REQUESTED = False  # set True to force a fresh login (picks up new /pc /phone mode etc.)
spam_running = False
bot_uid = None
ToKen = None
region = None
admin_uid = "2799233875"

pending_ghost_future = None
ghost_team_id = None
ghost_squad_code = None

spm_tasks = {}
ban_task = None
lw_running = False
lw_task = None
ban_running = False
ban_targets = set()
evo_cycle_running = False
evo_cycle_task = None
v_dance_task = None
freeze_running = False
freeze_task = None
fast_spam_running = False
fast_spam_task = None
custom_spam_running = False
custom_spam_task = None
msg_spam_running = False
msg_spam_task = None
mg_spam_task = None
reject_spam_running = False
reject_spam_task = None
emote_hijack = False
bot_enabled = True

EVO_IDS = [
    909000063, 909000075, 909040010, 909000081, 909039011,
    909045001, 909038012, 909042008, 909051003, 909035012,
    909000098, 909033002, 909037011, 909049010, 909041005,
    909038010, 909033001, 909035007, 909000090, 909000085,
    909000068
]

SINGLE_EMOTES_FALLBACK = {
    1: 909052010, 2: 909055012, 3: 909055011, 4: 909055010, 5: 909055009,
    6: 909055008, 7: 909055007, 8: 909055006, 9: 909055005, 10: 909055004,
    11: 909055003, 12: 909055002, 13: 909054020, 14: 909051011, 15: 909051015,
    16: 909051017, 17: 909051022, 18: 909054013, 19: 909054012, 20: 909054009,
    21: 909054020, 22: 909054017, 23: 909054002, 24: 909054003, 25: 909053011,
    26: 909053001, 27: 909052001, 28: 909052002, 29: 909052003, 30: 909052008,
    31: 909052005, 32: 909052004, 33: 909051015, 34: 909051011, 35: 909051010,
    36: 909000002, 37: 909000008, 38: 909000010, 39: 909000011, 40: 909000012,
    41: 909000014, 42: 909000014, 43: 909000015, 44: 909000020, 45: 909000070,
    46: 909000048, 47: 909034008, 48: 909033005, 49: 909042007, 50: 909051009,
    51: 909051007, 52: 909051006, 53: 909000130, 54: 909045005, 55: 909046004,
    56: 909042003, 57: 909042012, 58: 909046006, 59: 909046005, 60: 909045010,
    61: 909037006, 62: 909037001, 63: 909036010, 64: 909043010, 65: 909041013,
    66: 909042002, 67: 909041001, 68: 909042006, 69: 909053009, 70: 909051017,
    71: 909047003, 72: 909047009, 73: 909000101, 74: 909049013
}

# ═══════════════════════════════════════════════════════════════
# LOAD JSON FILES
# ═══════════════════════════════════════════════════════════════
GENERAL_EMOTES_MAP = {}
EMOTE_MAP = {}
EMOTE_MENU = {}
SINGLE_EMOTES_MAP = SINGLE_EMOTES_FALLBACK.copy()

try:
    with open(EMOTES_PATH, "r", encoding="utf-8") as _f:
        _emote_list = json.load(_f)
    GENERAL_EMOTES_MAP = {str(item["Number"]): int(item["Id"]) for item in _emote_list}
    EMOTE_MAP = {int(item["Number"]): int(item["Id"]) for item in _emote_list}
    print(f"✅ Loaded {len(GENERAL_EMOTES_MAP)} emotes from emotes.json")
except Exception as _e:
    print(f"❌ emotes.json load error: {_e}")

try:
    with open(SINGLE_EMOTE_PATH, "r", encoding="utf-8") as _f:
        _single_list = json.load(_f)
    for item in _single_list:
        SINGLE_EMOTES_MAP[int(item["Number"])] = int(item["Id"])
    print(f"✅ Loaded {len(SINGLE_EMOTES_MAP)} single emotes from singele_emote.json")
except Exception as _e:
    print(f"⚠️ singele_emote.json not loaded, using fallback: {_e}")

try:
    with open(EMOTE_MENU_PATH, "r", encoding="utf-8") as _f:
        EMOTE_MENU = json.load(_f)
    print(f"✅ Loaded emote_menu.json")
except Exception as _e:
    print(f"⚠️ emote_menu.json not loaded: {_e}")

NAME_EMOTES = {
    "ak": 909000063, "scar": 909000068, "mp40": 909000075,
    "m1014": 909000081, "xm8": 909000085, "famas": 909000090,
    "ump": 909000098, "m1887": 909035007, "woodpecker": 909042008,
    "groza": 909041005, "m4a1": 909033001, "thompson": 909038010,
    "g18": 909038012, "parafal": 909045001, "p90": 909049010,
    "m60": 909051003, "fist": 909037011, "ring": 909050009,
    "heart": 909038004, "love": 909000010, "dance": 909000027,
    "hello": 909000001, "hi": 909000001, "money": 909000129,
    "lol": 909000002, "sad": 909038005, "angry": 909000014,
    "chicken": 909000006, "dab": 909000005, "selfie": 909000040,
    "shower": 909051004, "flower": 909051002, "petals": 909051013,
}

# ── all named emotes = emote_menu.json (number->name) joined with emotes.json (number->id) ──
for _n, _name in EMOTE_MENU.items():
    _eid = GENERAL_EMOTES_MAP.get(str(_n))
    if _eid and str(_name).strip():
        NAME_EMOTES.setdefault(str(_name).strip().lower().replace(" ", ""), int(_eid))

# ── extra named emotes merged from alia_emotes.json (real Free Fire emote-ID catalogue) ──
try:
    with open("alia_emotes.json", "r", encoding="utf-8") as _f:
        _alia = json.load(_f)
    _added = 0
    for _name, _eid in _alia.items():
        key = str(_name).strip().lower().replace(" ", "")
        if key and key not in NAME_EMOTES:
            NAME_EMOTES[key] = int(_eid)
            _added += 1
    print(f"✅ Loaded {_added} extra named emotes from alia_emotes.json")
except FileNotFoundError:
    print("⚠️ alia_emotes.json not found, skipping extra named emotes")
except Exception as e:
    print(f"❌ alia_emotes.json load error: {e}")

print(f"✅ Named emotes available: {len(NAME_EMOTES)}")

def get_menu_page(page, per_page=25):
    import math
    items = sorted(EMOTE_MENU.items(), key=lambda x: int(x[0]))
    total = max(1, math.ceil(len(items) / per_page))
    page = max(1, min(page, total))
    s = (page - 1) * per_page
    text = f"[B][C][00FFFF]🎭 EMOTE MENU  [FFD700]{page}/{total}\n[B][C][FFFFFF]──────────────────\n"
    for num, name in items[s:s + per_page]:
        text += f"[B][C][00FF00]{num} [FFFFFF]➤ [FFFF00]{name}\n"
    text += f"[B][C][FFFFFF]──────────────────\n[B][C][FF69B4]/menu{min(page + 1, total)} → next page"
    return text

async def emote_to_user_once(team_code, emote_number, target_uid, key, iv, region):
    """aa[num] TEAMCODE : join team, emote on target, leave  (ported from Personal)"""
    emote_id = GENERAL_EMOTES_MAP.get(str(emote_number))
    if not emote_id:
        return False
    try:
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await JoinSq_original(team_code, key, iv))
        await asyncio.sleep(0.5)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await Emote_k(int(target_uid), int(emote_id), key, iv, region))
        await asyncio.sleep(0.5)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
        return True
    except Exception as e:
        print("aa emote error:", e)
        return False

# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def load_spam_targets():
    if os.path.exists(SPAM_TARGETS_FILE):
        with open(SPAM_TARGETS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_spam_targets():
    with open(SPAM_TARGETS_FILE, "w") as f:
        json.dump(list(spam_targets), f)

spam_targets = load_spam_targets()

# ═══════════════════════════════════════════════════════════════
# SHARE CARDS  (.s1 .. .s8, .s11, .t1) — legitimate in-game "share"
# messages (group recruit, craftland map, HUD tip, title, clan,
# workshop map, discount code, room recruit) sent to the current
# chat only. No targeting of a third party, no spam loop.
# ═══════════════════════════════════════════════════════════════
SHARE_CARDS = {
    "s1": '{"GroupID":6654519138,"Group":3,"Map":[1],"Game":1,"Match":1,"MemberNum":1,"RequireRankMin":0,"RequireRankMax":0,"CSSpecialModeEventId":0,"GroupTag":"0;0","SecretCode":null,"RecruitCode":"0","showGameBuf":0,"hasLuckyBuf":false,"hasMapBonus":false,"type":"group"}',
    "s2": '{"GroupID":888888,"Group":1,"Map":[1,22,29],"Game":1,"Match":2,"MemberNum":1,"RequireRankMin":0,"RequireRankMax":0,"CSSpecialModeEventId":0,"GroupTag":"0;0","SecretCode":null,"RecruitCode":"0","showGameBuf":0,"hasLuckyBuf":false,"hasMapBonus":false,"type":"group"}',
    "s3": '{"RoomId":0,"gameMode":15,"groupMode":3,"currentRoomNum":1,"MaxRoomNum":1,"RecruitCode":"0","OwnerNickname":"TEAM NEXUS","type":"RoomRecruit"}',
    "s4": '{"GroupID":6654519138,"Group":3,"Map":[100],"Game":100,"Match":1,"MemberNum":1,"RequireRankMin":0,"RequireRankMax":0,"CSSpecialModeEventId":10,"GroupTag":"10;100","SecretCode":null,"RecruitCode":"0","showGameBuf":0,"hasLuckyBuf":true,"hasMapBonus":true,"type":"group"}',
    "s5": '{"id":0,"Name":"TEAM NEXUS","Level":1,"MemberNum":"(1/50)","Apply":1,"Declaration":"","m_LimitLevel":1,"m_LimitRank":0,"m_LimitCSRank":0,"m_ClanBadgeID":1,"m_EntryType":1,"type":"clan"}',
    "s6": '{"ShareCode":"HASIBSHARECODE","type":"HUDShare"}',
    "s7": '{"WorkshopCode":"HASIBFFCRFLANDCODE","type":"UGCMapShare"}',
    "s8": '{"BufLoc":"T_36_YY_SOCIALBUFF_TEAM_TIPS","type":"Buf"}',
    "s11": '{"ShareDiscountCode":"TEAM NEXUS","SharerAccountID":0,"DiscountValue":10,"type":"RelayMartDiscountCodeShare"}',
    "t1": '{"TitleID":904590059,"type":"Title"}',
}

async def send_share_card(key_name, uid, chat_id, chat_type, key, iv):
    hud_json = SHARE_CARDS.get(key_name)
    if not hud_json: return False
    hud_json = hud_json.replace("__BRAND__", BOT_BRAND)
    try:
        if chat_type == 2: target_id = uid
        else: target_id = chat_id
        fields = {
            1: 1,
            2: {
                1: int(bot_uid) if bot_uid else 0,
                2: target_id,
                3: chat_type,
                5: int(time.time()),
                7: 1,
                8: hud_json,
                9: {
                    1: BOT_BRAND,
                    2: int(await xBunnEr()),
                    4: 330,
                    5: 102000015,
                    8: "TEAM NEXUS",
                    10: 1, 11: 1,
                    13: {1: 2},
                    14: {1: 1158053040, 2: 8,
                         3: b"\x10\x15\x08\x0a\x0b\x15\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}
                },
                10: "en",
                13: {2: 2, 3: 1}
            }
        }
        proto_hex = (await CrEaTe_ProTo(fields)).hex()
        packet = await GeneRaTePk(proto_hex, '1215', key, iv)
        if packet and whisper_writer:
            whisper_writer.write(packet)
            await whisper_writer.drain()
            return True
    except Exception as e:
        print(f"Share card ({key_name}) error: {e}")
    return False

# ═══════════════════════════════════════════════════════════════
# 20 NEW UTILITY/FUN COMMANDS (batch 1) — pure-python where possible,
# small free public APIs only where it genuinely needs live data.
# ═══════════════════════════════════════════════════════════════
import string as _string

MORSE_MAP = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.',
    'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.',
    'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-',
    'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', ' ': '/'
}
LEET_MAP = str.maketrans("aeiostAEIOST", "4310574310574"[:12])
COMPLIMENTS = [
    "তুমি আজ দারুণ পারফর্ম করেছ! 🔥", "তোমার হাসিটা সবার দিন ভালো করে দেয়! 😊",
    "তুমি একজন অসাধারণ টিমমেট! 👏", "তোমার ধৈর্য সত্যিই প্রশংসনীয়! 💪",
    "তুমি যা করো তাতেই সেরা! ⭐", "তোমার সাথে খেলা মানেই মজা! 🎮",
    "তুমি অনেক স্মার্ট আর সাহসী! 🧠", "তোমার জন্য আজকের দিনটা শুভ হোক! 🌟",
]
FUN_FACTS = [
    "মধু কখনো নষ্ট হয় না — হাজার বছর পুরনো মধুও খাওয়ার উপযোগী থাকতে পারে!",
    "অক্টোপাসের ৩টা হৃদপিণ্ড আছে!",
    "একটা দিনে মানুষ গড়ে প্রায় ৭০০০ শব্দ বলে।",
    "কলা আসলে বেরি (berry), কিন্তু স্ট্রবেরি বেরি না!",
    "পৃথিবীর সবচেয়ে ছোট হাড় কানে থাকে।",
    "প্রজাপতি তার পা দিয়ে স্বাদ নিতে পারে!",
    "একটা মেঘের ওজন প্রায় ১০ লক্ষ কেজির মতো হতে পারে।",
]
RANDOM_NAMES = ["Rafiq", "Arman", "Nusrat", "Tanvir", "Mim", "Sabbir", "Rakib", "Lamia", "Fahim", "Jannat"]

async def fetch_word_definition(word):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200: return None
                data = await resp.json()
        meaning = data[0]["meanings"][0]
        pos = meaning.get("partOfSpeech", "")
        definition = meaning["definitions"][0]["definition"]
        return pos, definition
    except Exception:
        return None

async def fetch_chuck_joke():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.chucknorris.io/jokes/random", timeout=10) as resp:
                if resp.status != 200: return None
                data = await resp.json()
        return data.get("value")
    except Exception:
        return None

LANG_NAMES = {"bn": "Bangla", "en": "English", "hi": "Hindi", "ar": "Arabic", "zh-CN": "Chinese"}

def detect_lang(text):
    for ch in text:
        o = ord(ch)
        if 0x0980 <= o <= 0x09FF: return "bn"          # Bengali script
        if 0x0600 <= o <= 0x06FF: return "ar"           # Arabic script
        if 0x0900 <= o <= 0x097F: return "hi"           # Devanagari (Hindi)
        if 0x4E00 <= o <= 0x9FFF: return "zh-CN"        # CJK (Chinese)
    return "en"

async def fetch_translation(text, target_lang):
    source_lang = detect_lang(text)
    if source_lang == target_lang:
        source_lang = "en" if target_lang != "en" else "bn"
    try:
        import urllib.parse as _urlp
        q = _urlp.quote(text, safe="")
        async with aiohttp.ClientSession() as session:
            url = f"https://api.mymemory.translated.net/get?q={q}&langpair={source_lang}|{target_lang}"
            async with session.get(url, timeout=15) as resp:
                if resp.status != 200:
                    return None, None, f"API Error! Status Code: {resp.status}"
                data = await resp.json()
        translated = data.get("responseData", {}).get("translatedText")
        if not translated:
            return None, None, "No translation returned."
        return source_lang, translated, None
    except Exception as e:
        return None, None, str(e)[:120]

async def fetch_tiktok_info(username):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://kawsar-tikto-info.vercel.app/tiktok?username={username}", timeout=15) as resp:
                if resp.status != 200:
                    return f"[B][C][FF8C00]❌ TikTok API Error! Status Code: {resp.status}"
                user = await resp.json()
        identity = user.get("identity", {})
        statistics = user.get("statistics", {})
        status = user.get("status", {})
        full_name = identity.get("full_name", "Unknown")
        username_ = identity.get("username", "")
        followers = statistics.get("followers", 0)
        following = statistics.get("following", 0)
        likes = statistics.get("likes", 0)
        videos = statistics.get("videos", 0)
        private_status = status.get("private_account", False)
        signature = user.get("bio", "")
        return f"""[B][C][1E90FF]◉[FFFF00]━[FF69B4]◉[FFFFFF]
[C][B][00BFFF]║[00BFFF]TIKTOK INFO[FFFFFF]║
[C][B][FF00FF]━━━━━━━━━━━
[C][B][FFFFFF]Fullname   : [FFFF00]{full_name}
[C][B][FFFFFF]Username   : [FFFF00]{username_}
[C][B][FFFFFF]Signature  : [00BFFF]{signature}
[C][B][FFFFFF]Followers  : [00BFFF]{followers}
[C][B][FFFFFF]Following  : [00BFFF]{following}
[C][B][FFFFFF]Likes      : [00BFFF]{likes}
[C][B][FFFFFF]Videos     : [00BFFF]{videos}
[C][B][FFFFFF]Private    : [FFFF00]{private_status}
[C][B][00FFFF]━━━━━━━━━━━"""
    except Exception as e:
        return f"[B][C][FF8C00]❌ TikTok lookup failed: {str(e)[:80]}"

async def fetch_youtube_info(channel_name):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://youtube-api.vercel.app/yt?channel={channel_name.lstrip('@')}", timeout=15) as resp:
                if resp.status != 200:
                    return f"[B][C][FF8C00]❌ YouTube API Error! Status Code: {resp.status}", None
                data = await resp.json()
        stats = data.get("statistics", {})
        subscribers = xMsGFixinG(stats.get("subscribers", "0"))
        views = xMsGFixinG(stats.get("views", "0"))
        videos = xMsGFixinG(stats.get("videos", "0"))
        description = data.get("description", "")
        main_info = f"""[B][C][FF8C00]◉[FF4500]━[FFD700]◉[FFFFFF]
[C][B][FF8C00]║[00BFFF]YOUTUBE INFO[FFFFFF]║
[C][B][FF00FF]━━━━━━━━━━━
[C][B][FFFFFF]Channel Name : [FFFF00]{data.get('channel_title', 'Unknown')}
[C][B][FFFFFF]Channel ID   : [FFFF00]{data.get('channel_id', 'Unknown')}
[C][B][FFFFFF]Handle       : [00BFFF]{data.get('handle', 'Unknown')}
[C][B][FFFFFF]Subscribers  : [00BFFF]{subscribers}
[C][B][FFFFFF]Views        : [00BFFF]{views}
[C][B][FFFFFF]Videos       : [00BFFF]{videos}
[C][B][FFFFFF]Published At : [00BFFF]{xMsGFixinG(data.get('published_at', ''))}
[C][B][00FFFF]━━━━━━━━━━━
[C][B][FFFFFF]Developer    : {BOT_BRAND}"""
        return main_info, (description or None)
    except Exception as e:
        return f"[B][C][FF8C00]❌ YouTube lookup failed: {str(e)[:80]}", None

def get_random_color():
    colors = [
        "[FF0000]", "[00FF00]", "[0000FF]", "[FFFF00]", "[FF00FF]", "[00FFFF]", "[FFFFFF]", "[FFA500]",
        "[A52A2A]", "[800080]", "[000000]", "[808080]", "[C0C0C0]", "[FFC0CB]", "[FFD700]", "[ADD8E6]",
        "[90EE90]", "[D2691E]", "[DC143C]", "[00CED1]", "[9400D3]", "[F08080]", "[20B2AA]", "[FF1493]",
        "[7CFC00]", "[B22222]", "[FF4500]", "[DAA520]", "[00BFFF]", "[00FF7F]", "[4682B4]", "[6495ED]",
        "[5F9EA0]", "[DDA0DD]", "[E6E6FA]", "[B0C4DE]", "[556B2F]", "[8FBC8F]", "[2E8B57]", "[3CB371]",
        "[6B8E23]", "[808000]", "[B8860B]", "[CD5C5C]", "[8B0000]", "[FF6347]", "[FF8C00]", "[BDB76B]"
    ]
    return random.choice(colors)

def get_random_avatar():
    return random.choice([902050001, 902050002, 902050003, 902039016, 902050004, 902047011, 902047010, 902049015, 902050006, 902049020])

def get_random_sticker():
    pack_id, start, end = random.choice([("1200000001", 1, 24), ("1200000004", 1, 15), ("1200000002", 1, 13)])
    return f"[1={pack_id}-{random.randint(start, end)}]"

def xMsGFixinG(n):
    return '🗿'.join(str(n)[i:i + 3] for i in range(0, len(str(n)), 3))

async def encrypt_packet(packet_hex, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(bytes.fromhex(packet_hex), AES.block_size)).hex()

# ═══════════════════════════════════════════════════════════════
# AUTH & DECODE
# ═══════════════════════════════════════════════════════════════
def build_ob55_online_auth(account_uid, token, kts, key, iv):
    token_bytes = token.encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc_token = cipher.encrypt(pad(token_bytes, 16))
    opcode = bytes.fromhex("830c")
    uid_bytes = int(account_uid).to_bytes(8, byteorder="big")
    kts_bytes = int(kts).to_bytes(4, byteorder="big")
    len_bytes = len(enc_token).to_bytes(8, byteorder="big")
    return opcode + uid_bytes + kts_bytes + len_bytes + enc_token, enc_token

def create_auth_token_chat(account_id, jwt_token, timestamp, key, iv):
    try:
        K = bytes.fromhex(key) if isinstance(key, str) else key
        V = bytes.fromhex(iv) if isinstance(iv, str) else iv
        ct = AES.new(K, AES.MODE_CBC, V).encrypt(pad(jwt_token.encode('utf-8'), AES.block_size))
        return (bytes.fromhex('6d19') + int(account_id).to_bytes(8, 'big') + int(timestamp).to_bytes(4, 'big') + len(ct).to_bytes(4, 'big') + ct).hex()
    except: return None

async def cHTypE(H):
    return 'Squid' if not H else 'CLan' if H == 1 else 'PrivaTe'

async def DecodeWhisperMessage(hex_packet):
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(bytes.fromhex(hex_packet))
    return proto

async def get_colorful_message(message_text, message_number):
    color_palette = ["FF0000", "FFFF00", "0000FF", "FF00FF", "00FFFF", "FFA500", "FF1493", "00FF7F", "7B68EE", "FF66CC", "00CED1", "FF69B4"]
    return f"[C][B][{color_palette[(message_number - 1) % len(color_palette)]}]{message_text}"

# ═══════════════════════════════════════════════════════════════
# PACKET BUILDERS
# ═══════════════════════════════════════════════════════════════
async def NewClanChatPacket(message_text, key, iv, clan_id=3102281341):
    # BUGFIX: this previously hardcoded a fake sender UID (16801068917) instead of the
    # bot's own authenticated account UID, so the server had no reason to accept the
    # message as coming from a real member of the clan -> guild chat send silently failed.
    my_uid = int(bot_uid) if bot_uid else 0
    fields = {1: my_uid, 2: 18, 4: 1, 5: {1: my_uid, 2: clan_id, 3: 1, 4: BOT_BRAND, 5: 1785944381, 7: 6, 9: {1: message_text, 4: 301, 8: BOT_BRAND, 13: '', 14: {1: my_uid}, 18: {1: my_uid, 3: 1, 4: ''}}, 10: 'ar', 13: {2: 1, 3: 1}, 14: '', 16: int(time.time() * 1000)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)

async def SEndMsG(H, message, Uid, chat_id, key, iv):
    TypE = await cHTypE(H)
    if TypE == 'Squid': return await xSEndMsgsQ(message, chat_id, key, iv)
    elif TypE == 'CLan': return await NewClanChatPacket(message, key, iv, chat_id)
    elif TypE == 'PrivaTe': return await xSEndMsg(message, 2, Uid, Uid, key, iv)

async def SEndPacKeT(OnLinE, ChaT, TypE, PacKeT):
    if TypE == 'ChaT' and ChaT: whisper_writer.write(PacKeT); await whisper_writer.drain()
    elif TypE == 'OnLine': online_writer.write(PacKeT); await online_writer.drain()

async def safe_send_message(chat_type, message, uid, chat_id, key, iv, max_retries=3):
    for attempt in range(max_retries):
        try:
            packet = await SEndMsG(chat_type, message, uid, chat_id, key, iv)
            if packet: await SEndPacKeT(whisper_writer, online_writer, 'ChaT', packet); return True
        except Exception: pass
        await asyncio.sleep(0.5)
    return False

async def JoinSq_original(code, K, V):
    skinz = {1: 4, 2: {4: "\u0001\u0007\t\n\u000b\u0012\u0019 '", 5: str(code), 6: 6, 8: 1,
        9: {1: "08FFF3BE903F27DF0203110111110000006B0003006800169194106F13CF106E4676251411010404dfe9e8b5ca3ca4f96a3119c00000004f03060301cacfa16d",
            2: 130, 3: "tY_S\u0013\b\u0001M\u0002\u0000T\u0000\u0005\u000e\b\t\u0002\u0000\u0003U\u0003\u0001V\u000fR\u000e\tRQ\u0002\u0004\u0005US\u0003XS\u0005\u0001\u0002\u0011\u0001\u0002JuTAEN\u001e\u0002\u001c\u0002\u001f\u0013\b\u0003M\u001cDbz_Q@}p_QOgsC\u001dYVI\u0004UAAj_ga\u0004\u0012\u0000K\u001d\u0007_t\u0019b\bCx\u0002UeGat\u001fTTCBLER`\u0006\u0001\r\f\u0012\u0006\u0005N^^\u0002acH~r\u0004_\u0003RO|\u000bcd_@~`Rnqrgh\n\u0015\nL\\Nh\u0000~G\u000et\u0000eb]VQ\u0006t^F[ZIGxCdZD\u000b\u0011\u0002OA~LP@\u000fcSDyATQApaT^{|wa]\\\u0001E\u000f\u0013\nJfxve}\u0004J\u0003c{YL\u0007^^yDYQf\bhe\u0005_wg\r\u0010\u0007\bEHpX@||\u0002Z\\uTGyA\u0001JP\u0005t~VkTE\u0000J\\\u000b\u0013\nMr\u0018zTzK}qE]vnvwROuheYvwduvQ\r\u001a\u0005M\u0006z\u001dfXfzvHFc~dXUz}O\u001aB\u0005t\u0002i\u001co_\u0004\u0012\u0003\u0007J\u0006b\u0003\u000eqlfvbEstgu~wB\u0001v@`yI\u0002ZPx\f\u0014\u0003NR\u0002yBZvuD_cd\u0004q]lH]\u0007bD}pCe\t\u0004t\n",
            4: "w^_R", 6: 11, 7: "\u0014\u0004aqrg\u0015\u0013", 8: "1.132.1", 9: 3, 10: 2,
            11: "\u0003bbSQ6wxegh9qAdV2KyoVleA17yPmYF+yTnOrl+JMknmppeUBe5ZsiHueP2mZZ4KOs6b2Ail1S9z3qIeU9hGFZ2M6PP39/zjIc/RFVPAkgDagySswMVmYaPhkzU5IqNPow2843fyQUz9xI10NdMhl1WiI4Y6wCXBotiUS9wSgujQ4j0fWXUyklCxBWo8r27hyoGSVrPdTPXFMnJJpPRRFFmWqc3fWvMg+BNfxSRJOZRSrkzG0nNvSIJ4uZB2pqAlHIPEYx7bI6zsgwUVDiLZJKTUTyuCGbOd1DegDUFfazFesTG1LJknT5WhgzCsrBIy+f2l+LeJe5DW7wEwNaHambM7ECXcJcLIhB9kJJsW0tFvXkk3HSdcQ8N1K6wjSKWhpkW0kV8Zrjj0jkhS/7AZ6T9GJRIA827YDtTorBvbx1UkXjYrqYI1nSa2GaMexGnqlurc5DE3v1R+mUBI9GqmjEPgTSYVBxyeCdQMHaMXGtspAhvkiO84ToU87sP45pylDEfFOVoc/rcmdzWeqlYPsv6txKRtIHcb0cO+MoVShoU8ZUVRDF3znbqzVrscPIfplBaa79lwvQqzRubLl9XY="},
        11: {1: "IDC4", 2: 281, 3: "ME"}, 13: "fr", 16: "7OR\u0019", 20: "\b\u0015", 27: "\bH\u0010\u0003"}}
    return await GeneRaTePk((await CrEaTe_ProTo(skinz)).hex(), '0515', K, V)

async def MahirAccepted(uid, code, K, V, region):
    fields = {1: 4, 2: {1: int(uid), 3: int(uid), 4: "rYUW\u0017\t\u0007NR\u000f\u0005\u0004\\W\u0002\u000fV\u0004TPQ\u0003\u000f\u0005\u0004]\u0005\u000b\u0000\u0002W\u0005\r\nVY\u0004\u0007\u0007\u0007\u0017\u0001\bNQ\fS\u0005\u000e\u0006\f\u0005\rT\u0002\r\u0000TS\u0007U\u0004X\u0006RY\u0005\u0003\u0003SW\u0000\u000eQ\u0000^\u0014\u0003\u0004JXS\u000f\u0000g{gqfePblEZJp{_xU\bmQW\f\u0007\u000f\u0015\u0007H\\U^CHXh@Ax`\u000f~\rPN~Nz\\\u001fr_ckPU\u000b\u0015\u0005\u0003Ekfp\u007fcY\u0001nWV\u0002\u0005azE~N\u0007HTg\u0007w}@\u0002{\t\u0013\u0001NeNP]DUf|]ugINs{\u0001\\rAgB_\u0004fA]\u0004\r\u001a\u0000HpOv\\\u0005|gS\u0019\\A\u007fWW\u0003\u007fTqFGi\u0004Qr\u0019dW\u0004\u0011\rD\u0002yeZ]A\u0016a\u0007Ungeg\u0007E\\P\u001b\u000b\u0004\u0005dd\ff\r\u000f\u0017\t\u000fNRyZd\u0012tZ\fe\u0007AGv\u007fw]{P\u001c\u007ff\u0005ZJK\u0004\u0005\u0014\u0001Jgq\u001frymsB\u0001\u000fd`\u001bj~[}\u0004SDZ|IxKB\u0000\n\u0011\u0002J^`tjYN\u0007WQdE[PQ\u0002_{VP`S\t\u007f\u001dP\n\u000f\u000f\u0015\u0004\u0004L{V\u0003@yP[rgJ{Hpk\u0001\u000bw\u0001Agt_\u0003HxPc\u000b\u0017\u0005E`y\ngWoy\u0006S{A\u001b``Y\u0002Xzw}dDWOKsg\t\u0013\u000eNf\u000e\\`\u0005AwJc\u0003BM\u0001^\u0000R\u0002Qoh]tbS~`G\r\u001a\u0004HibAQ\u000f^XNt~kDUWaeaNqcLQ]Py[G\u0004",
            8: 1, 9: {1: "08FBA33CFF105FDD02030A01111100000003000100020000B687046B0D6D2083467625141101030175a63c900e748c3f6a311e04000000ff00040202cacfa16d",
            2: 197, 3: "735154531406054a035305025a0e50560f5100040250020f5e0401520653000303505e0d520302501500064d705548424e1f051a001e12040a441d45677f5a56477574565e4f6274451d585849005a4f456d5b64670c1400496d017842740c670100040069536e72586c02016e657e566b524403081500044d0d515b637f757c19095c7c510b00417f565e5e066f5b584d6e02400a160e4d58496d0177400e750763605c575d0f7d5f475e5f4c407f4b60534b0b140549751e66407a4860726e44400e6103557e515c646f43577106077b60051b0f4b4e474e58457e4f615c01406000051e0361516e7b67614e040102540c1609004a0e40730f62517f446a135179507e706850547f7e7a67795553597c0a1206445b456640046265725c4d505d446d50737b7c42035970486370645e0b12034d506f5c7a1c554f574b0e765a0f0a7364505203477569456c6c420f0a1604014b647149136c186f795f5d78755e550e7842545e53747b08705f7f5d0a14004a08666b5a5b5f00045c7f5e584d72584262705f56055c61475564790515004b76514178587f52797a0f077a070953507d7f4d784f794f667b4256081b0e4a75627d4778417a06717574747c4c78557b4b7a0a697f0e714573600a",
            4: "{Y_R", 6: 13, 7: "1c6f017306741513", 8: "2.126.22", 9: 2, 10: 1,
            11: "036262535136784d584e38742b416456324b796f566c6537392f763672324d4773683377706379634f6b6b6f7447397934523930517432797246474c464c624c777a7747344d4d5257623146756d2b6556777a62597736743973492b787059612f55596e43465a59485235713348705830306c485a6f3632565145574e7145705866414c38734a754646575247386d376f5444566a4c484c576e714c52576f4e653236437a734c346a4144482b71694b55384d71476c5936546669544863716c487a345568463869396a365233366d49774b71746c36714f797568513854367945714b69742f45466d2b3636634b787649304f384d6c41385166454b6253467366477a2f30684e6a543873305369722f3962635a2f4679376c752f61632f366765704d415734566b442b36374f535756473665377a775a79312b797a42334b70632b7571782b577437414d39727761644439575765704570567849526d66654f5847627775787a68574b5664344c49586f415a364b387063647450627953575857455135706a542b653669365a2f6177444a3179356f774d5a534f64487262392b7877424a4d444f7848565a7a483372547a30314a316738517675466b656c3042433746473630683456427041494457487956684e794b4f5145507139467a4a6272686b316146306768766578512f6a2f484767426a5268675134645243372b477a5a687a2b77505967376454746f2b494d56363774642b54435653314234346b4148395a6d415872763758615941626477644e664f533170484875736b7336346f72463452534d3772656345417661484e61484854314c5545686e786a5a616d4d4f303d"},
            10: str(code), 11: {1: "IDC3", 2: 84, 3: "BD"}, 13: "en", 16: "374f5219",
            20: {1: 21}, 23: "a_1477547277882450725", 27: {1: 2, 2: 8}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def leave_channel_req(channel_id, channel_type, key, iv):
    fields = {1: 4, 2: {1: int(channel_id), 2: int(channel_type), 3: "en"}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '1215', key, iv)

async def SPamSqForSpm(Uid, K, V):
    same_value = random.choice([4096, 16384, 8192])
    fields = {1: 33, 2: {1: int(Uid), 2: "ME", 3: 1, 4: 1,
        5: bytes([1, 7, 9, 10, 11, 18, 25, 26, 32]), 6: "Tg:[C][B][FF0000] @team_xypphon",
        7: 330, 8: 1000, 10: "ME",
        11: bytes([49,97,99,52,98,56,48,101,99,102,48,52,55,56,97,52,52,50,48,51,98,102,56,102,97,99,54,49,50,48,102,53]),
        12: 1, 13: int(Uid),
        14: {1: 2203434355, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"},
        16: 1, 17: 1, 18: 312, 19: 46, 23: bytes([16, 1, 24, 1]),
        24: await xBunnEr(), 26: "", 28: "",
        31: {1: 1, 2: same_value}, 32: same_value,
        34: {1: int(Uid), 2: 8, 3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])}},
        10: "en", 13: {2: 1, 3: 1}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', K, V)

async def GhostPakcet(player_id, nm, secret_code, key, iv):
    fields = {1: 61, 2: {1: int(player_id), 2: {1: int(player_id), 2: 1159,
        3: f"[b][c]{get_random_color()}{nm}", 5: 12, 6: 999, 7: 1,
        8: {2: 1, 3: 1}, 9: 3}, 3: secret_code}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)

async def xBaNchaTxSkInZ(uidd, K, V):
    return await GeneRaTePk((await CrEaTe_ProTo({1: 3, 2: {1: int(uidd), 3: "fr", 4: "1750728024661459697_3qind8eeqs"}})).hex(), '1215', K, V)

async def send_sticker_packet(target_uid, chat_id, key, iv, nickname="TEAM NEXUS"):
    try:
        sticker_value = get_random_sticker()
        fields = {1: 1, 2: {1: int(target_uid), 2: int(chat_id),
            5: int(time.time()), 8: f'{{"StickerStr" : "{sticker_value}", "type":"Sticker"}}',
            9: {1: f"[C][B][FF0000]{nickname}", 2: get_random_avatar(), 4: 330, 5: 827001007,
                8: "TEAM NEXUS", 10: 1, 11: 66, 12: 66, 13: {1: 2},
                14: {1: 1158053040, 2: 8, 3: b"\x10\x15\x08\x0a\x0b\x15\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}},
            10: "en", 13: {2: 2, 3: 1}, 14: {}}}
        packet_hex = (await CrEaTe_ProTo(fields)).hex()
        encrypted = await encrypt_packet(packet_hex, key, iv)
        pl = len(encrypted) // 2
        hl = f"{pl:04x}"
        prefix = "121500" + ("0" * (6 - len(hl)))
        return bytes.fromhex(prefix + hl + encrypted)
    except Exception as e:
        print(f"❌ Sticker error: {e}")
        return None

async def animation_packet(animation_id, key, iv):
    fields = {1: 88, 2: {1: {1: int(animation_id)}}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    pl = len(encrypted) // 2
    hl = format(pl, 'x')
    final = "051500" + "0" * (6 - len(hl)) + hl + encrypted
    return bytes.fromhex(final)

async def Look_Changer(bundle_id, key, iv, look_type=1, region="bd"):
    fields = {1: 88, 2: {1: {1: bundle_id, 2: look_type}, 2: 2}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if region.lower() == "ind": pt = "0514"
    elif region.lower() == "bd": pt = "0519"
    else: pt = "0515"
    if len(hl) == 2: h = f"{pt}000000"
    elif len(hl) == 3: h = f"{pt}00000"
    elif len(hl) == 4: h = f"{pt}0000"
    elif len(hl) == 5: h = f"{pt}000"
    else: h = f"{pt}000000"
    return bytes.fromhex(h + hl + encrypted)

async def Room_Spam(Uid, Rm, Nm, K, V):
    fields = {1: 78, 2: {1: int(Rm), 2: "iG:[C][B][FF0000]TEAM NEXUS", 3: {2: 1, 3: 1},
        4: 330, 5: 6000, 6: 201, 10: get_random_avatar(), 11: int(Uid), 12: 1,
        15: {1: 1, 2: 32768}, 16: 32768,
        18: {1: 11481904755, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"},
        31: {1: 1, 2: 32768}, 32: 32768,
        34: {1: int(Uid), 2: 8, 3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])}}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0e15', K, V)

async def banecipher(target_uid, key, iv):
    banner_text = ".\n.\n.\n[b][FF0000]TEAM NEXUS[00FF00] ⚡\n.\n.\n."
    fields = {1: 5, 2: {1: int(target_uid), 2: 1, 3: int(target_uid), 4: banner_text}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if len(hl) == 2: f = "0515000000"
    elif len(hl) == 3: f = "051500000"
    elif len(hl) == 4: f = "05150000"
    elif len(hl) == 5: f = "0515000"
    else: f = "0515000000"
    return bytes.fromhex(f + hl + encrypted)

async def banecipher1(target_uid, key, iv):
    gay_text = ".\n.\n.\n[b][FF0000]TEAM NEXUS ⚡[00FF00]\n.\n.\n."
    fields = {1: int(target_uid), 2: 5, 4: 50, 5: {1: int(target_uid), 2: gay_text}}
    packet_hex = (await CrEaTe_ProTo(fields)).hex()
    encrypted = await encrypt_packet(packet_hex, key, iv)
    hl = await DecodE_HeX(len(encrypted) // 2)
    if len(hl) == 2: f = "0515000000"
    elif len(hl) == 3: f = "051500000"
    elif len(hl) == 4: f = "05150000"
    elif len(hl) == 5: f = "0515000"
    else: f = "0515000000"
    return bytes.fromhex(f + hl + encrypted)

async def convert_kyro_to_your_system(target_uid, chat_id, key, iv, nickname="TEAM NEXUS", title_id=None):
    try:
        if title_id is None:
            available_titles = [905090075, 904990072, 904990069, 905190079, 904090014, 904090015, 904090024, 904090025, 904090026, 904090027, 904990070, 904990071]
            title_id = random.choice(available_titles)
        fields = {1: 1, 2: {1: int(target_uid), 2: int(chat_id),
            5: int(time.time()),
            8: f'{{"TitleID":{title_id},"type":"Title"}}',
            9: {1: f"[C][B][FF0000]{nickname}", 2: get_random_avatar(), 4: 330, 5: 827001007, 8: "TEAM NEXUS", 10: 1, 11: 1, 13: {1: 2},
                14: {1: 1158053040, 2: 8, 3: b"\x10\x15\x08\x0a\x0b\x15\x0c\x0f\x11\x04\x07\x02\x03\x0d\x0e\x12\x01\x05\x06"}},
            10: "en", 13: {2: 2, 3: 1}, 14: {}}}
        packet_hex = (await CrEaTe_ProTo(fields)).hex()
        encrypted = await encrypt_packet(packet_hex, key, iv)
        pl = len(encrypted) // 2
        hl = f"{pl:04x}"
        prefix = "121500" + ("0" * (6 - len(hl)))
        return bytes.fromhex(prefix + hl + encrypted)
    except Exception as e:
        print(f"❌ Title error: {e}")
        return None

async def xSEndMsgsQQ(Msg, id, K, V):
    fields = {1: id, 2: id, 4: Msg, 5: 1756580149, 7: 2, 8: 904990072,
        9: {1: "TEAM NEXUS", 2: get_random_avatar(), 4: 330, 5: 1001000001, 8: "TEAM NEXUS", 10: 1, 11: 1, 13: {1: 2},
            14: {1: 1158053040, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}},
        10: "en", 13: {2: 2, 3: 1}}
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)

# ═══════════════════════════════════════════════════════════════
# LOOPS
# ═══════════════════════════════════════════════════════════════
async def spm_loop(uid, key, iv, interval=0.5):
    while True:
        try:
            if online_writer is not None:
                packet = await SPamSqForSpm(uid, key, iv)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', packet)
            else: await asyncio.sleep(1)
        except asyncio.CancelledError: break
        except Exception: pass
        await asyncio.sleep(interval)

async def ban_loop(key, iv, interval=0.5):
    global ban_running, ban_targets
    ban_running = True
    try:
        while ban_running:
            if online_writer is not None and ban_targets:
                for uid in list(ban_targets):
                    try:
                        ban_pkt = await xBaNchaTxSkInZ(uid, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', ban_pkt)
                    except Exception: pass
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass
    finally:
        ban_running = False

async def evo_gun_cycle(uids, evo_ids_list, key, iv, region):
    global evo_cycle_running
    cc = 0
    while evo_cycle_running:
        cc += 1
        for emote_id in evo_ids_list:
            if not evo_cycle_running: break
            for uid_str in uids:
                try:
                    H = await Emote_k(int(uid_str), int(emote_id), key, iv, region)
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                except Exception: pass
            if evo_cycle_running:
                for i in range(5):
                    if not evo_cycle_running: break
                    await asyncio.sleep(1)
        if evo_cycle_running: await asyncio.sleep(2)

async def fast_emote_spam(uids, emote_id, key, iv, region):
    global fast_spam_running
    count = 0
    while fast_spam_running and count < 25:
        for uid in uids:
            try:
                H = await Emote_k(int(uid), int(emote_id), key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except Exception: pass
        count += 1
        await asyncio.sleep(0.1)

async def custom_emote_spam(uid, emote_id, times, key, iv, region):
    global custom_spam_running
    count = 0
    while custom_spam_running and count < times:
        try:
            H = await Emote_k(int(uid), int(emote_id), key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            count += 1
            await asyncio.sleep(0.1)
        except Exception: break

async def reject_spam_loop(target_uid, key, iv):
    global reject_spam_running
    count = 0
    while reject_spam_running and count < 150:
        try:
            p1 = await banecipher1(target_uid, key, iv)
            p2 = await banecipher(target_uid, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', p1)
            await asyncio.sleep(0.1)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', p2)
            count += 1
            await asyncio.sleep(0.2)
        except Exception: break
    return count

async def msg_spam_loop(message_text, times, chat_id, key, iv, region):
    global msg_spam_running
    count = 0
    while msg_spam_running and count < times:
        try:
            colorful = await get_colorful_message(message_text, count + 1)
            msg_packet = await xSEndMsgsQQ(colorful, int(chat_id), key, iv)
            if msg_packet and whisper_writer:
                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                count += 1
                await asyncio.sleep(0.1)
        except Exception: break
    return count

async def send_wave_messages(message_text, repeats, chat_id, key, iv, region):
    global msg_spam_running
    count = 0
    total_cycles = 0
    while msg_spam_running and total_cycles < repeats:
        try:
            for i in range(1, len(message_text) + 1):
                if not msg_spam_running: break
                partial = message_text[:i]
                colorful = await get_colorful_message(partial, i)
                msg_packet = await xSEndMsgsQ(colorful, int(chat_id), key, iv)
                if msg_packet and whisper_writer:
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                    count += 1
                    await asyncio.sleep(0.1)
            for i in range(len(message_text) - 1, 0, -1):
                if not msg_spam_running: break
                partial = message_text[:i]
                colorful = await get_colorful_message(partial, i)
                msg_packet = await xSEndMsgsQQ(colorful, int(chat_id), key, iv)
                if msg_packet and whisper_writer:
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', msg_packet)
                    count += 1
                    await asyncio.sleep(0.1)
            total_cycles += 1
        except Exception: break
    return count, total_cycles

async def freeze_emote_spam(uid, key, iv, region, chat_type, chat_id, sender_uid):
    global freeze_running
    FREEZE_EMOTES = [909052010, 909052010, 909052010]
    cycles = 0
    while freeze_running and cycles < 10:
        for emote_id in FREEZE_EMOTES:
            if not freeze_running: break
            try:
                emote_packet = await Emote_k(int(uid), emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', emote_packet)
                await asyncio.sleep(0.1)
            except Exception: pass
        cycles += 1
        await asyncio.sleep(1)
    return cycles

# ═══════════════════════════════════════════════════════════════
# API CALLS (SMT INFO API FIXED)
# ═══════════════════════════════════════════════════════════════
async def send_friend_request(target_uid, token, region):
    try:
        encrypted_id = Encrypt_ID(target_uid)
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        kb = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        ib = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        cipher = AES.new(kb, AES.MODE_CBC, ib)
        ep = cipher.encrypt(pad(bytes.fromhex(payload), AES.block_size)).hex()
        url = "https://clientbp.ggpolarbear.com/RequestAddingFriend"
        headers = {"Authorization": f"Bearer {token}", "X-Unity-Version": "2018.4.11f1", "X-GA": "v1 1", "ReleaseVersion": "OB55", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=bytes.fromhex(ep), ssl=False) as r:
                return (True, "✅ Friend request sent") if r.status == 200 else (False, f"❌ Status: {r.status}")
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

async def remove_friend(target_uid, token, region):
    try:
        import RemoveFriend_Req_pb2
        msg = RemoveFriend_Req_pb2.RemoveFriend()
        msg.AuthorUid = int(admin_uid); msg.TargetUid = int(target_uid)
        kb = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
        ib = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
        cipher = AES.new(kb, AES.MODE_CBC, ib)
        eb = cipher.encrypt(pad(msg.SerializeToString(), AES.block_size))
        url = "https://clientbp.ggpolarbear.com/RemoveFriend"
        headers = {'Authorization': f"Bearer {token}", 'User-Agent': "Dalvik/2.1.0 (Linux; Android 9)", 'Content-Type': "application/x-www-form-urlencoded", 'X-Unity-Version': "2018.4.11f1", 'X-GA': "v1 1", 'ReleaseVersion': "OB55"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=eb, headers=headers, ssl=False) as r:
                return (True, "✅ Friend removed") if r.status == 200 else (False, f"❌ Status: {r.status}")
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

async def check_banned(player_id):
    try:
        url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
        headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10)", "Accept": "application/json", "referer": "https://ff.garena.com/en/support/", "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, ssl=False) as r:
                if r.status == 200: return True, await r.json()
                return False, f"Failed: {r.status}"
    except Exception as e: return False, f"Error: {str(e)}"

async def get_player_info(player_id):
    try:
        url = f"https://smt-info-api.vercel.app/info?uid={player_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200: return True, await r.json()
                return False, f"HTTP {r.status}"
    except Exception as e: return False, str(e)

def format_player_info(data):
    if data.get("status") != "success":
        return [f"[B][C][FF0000]❌ API Error: {data.get('message', 'Unknown')}"]
    b = data.get("BasicInformation", {})
    a = data.get("ActivityInformation", {})
    g = data.get("GuildInformation", {})
    l = data.get("LeaderInformation", {})
    p = data.get("PetDetails", {})
    ban = data.get("BanStatus", "Unknown")

    p1 = f"""[B][C][{get_random_color()}] ═══ PLAYER INFO (1/3) ═══
[B][C][FFFFFF]👤 Name: [00FF00]{b.get('Name', 'N/A')}
[B][C][FFFFFF]🆔 UID: [FFFF00]{b.get('UID', 'N/A')}
[B][C][FFFFFF]🌍 Region: [FF69B4]{b.get('Region', 'N/A')}
[B][C][FFFFFF]📊 Level: [FFA500]{b.get('Level', 'N/A')}
[B][C][FFFFFF]❤️ Likes: [FF1493]{b.get('Likes', 'N/A')}
[B][C][FFFFFF]⚔️ BR Rank: [00FFFF]{a.get('BRRank', 'N/A')} ({a.get('BRPoints', 0)} pts)
[B][C][FFFFFF]🛡️ Ban Status: {ban}
[B][C][FFFFFF]📝 Bio: [D3D3D3]{b.get('Signature', 'N/A')}
[B][C][{get_random_color()}] ═════════════════════════"""

    p2 = f"""[B][00FFFF]■ {B}ㅤMENU 02 ■
[B][00FFFF]──────────────────
[B][FFD700]EMOTE CONTROL
[B][00FFFF]├─[00FFFF][number] [FFFFFF](Self Emote)
[B][00FFFF]├─[00FFFF]aa[num] [tc] [FFFFFF](Magic Emote)
[B][00FFFF]├─[00FFFF]/menu[num] [FFFFFF](All Emotes Menu)
[B][00FFFF]├─[00FFFF]/copy , /copy off [FFFFFF](Emote Copy)
[B][00FFFF]├─[00FFFF]/e [uid] [num/name] [FFFFFF](Emote Send)
[B][00FFFF]└─[00FFFF]/sticker [FFFFFF](Random Sticker)
[B][00FFFF]──────────────────
[B][FFD700]EVO CONTROL
[B][00FFFF]├─[00FFFF]max / new [FFFFFF](Evo Self / Random)
[B][00FFFF]├─[00FFFF]@max / @new [FFFFFF](Evo Bot / Random)
[B][00FFFF]├─[00FFFF]@evos [FFFFFF](Evo Bot + You)
[B][00FFFF]├─[00FFFF]/evo [uid] [1-21] [FFFFFF](Evo Emote)
[B][00FFFF]├─[00FFFF]/evos [FFFFFF](Start Evo Cycle)
[B][00FFFF]├─[00FFFF]/ob55 /ob54 [FFFFFF](OB55 Special)
[B][00FFFF]└─[00FFFF]/s /o /sm @bt /sevos [FFFFFF](Stop)
[B][00FFFF]──────────────────"""
    p3 = f"""[B][C][{get_random_color()}] ═══ ACTIVITY & EXTRA (3/3) ═══
[B][C][FFFFFF]🐾 Pet: [FF69B4]{p.get('PetNick', 'N/A')} (Lv {p.get('PetLevel', 0)})
[B][C][FFFFFF]🌟 Celebrity: [FFFF00]{b.get('CelebrityStatus', 'No')}
[B][C][FFFFFF]🏅 Honor Score: [00FF00]{b.get('HonorScore', 0)}
[B][C][FFFFFF]📅 Created: [D3D3D3]{a.get('CreatedAt', 'N/A')}
[B][C][FFFFFF]⏰ Last Login: [D3D3D3]{a.get('LastLogin', 'N/A')}
[B][C][FFFFFF]🎖️ BP Badges: [FFA500]{a.get('CurrentBpBadges', 0)}
[B][C][FFFFFF]🆕 Recent OB: [00FFFF]{a.get('MostRecentOB', 'N/A')}

[B][C][{get_random_color()}] ✨ Powered by TEAM NEXUS"""
    return [p1, p2, p3]

def format_check_result(data):
    try: return f"[b][c]{get_random_color()} 🔍 BAN CHECK\n[b][c][FFFFFF]Type: {data.get('ban_type', 'Unknown')}\n[b][c][FFFFFF]Duration: {data.get('ban_duration', 'Unknown')}"
    except Exception as e: return f"[b][c]Error: {str(e)}"

# ═══════════════════════════════════════════════════════════════
# AUTO BOT SQUAD JOIN EVENT (DRESS + EVO + ANIMATION + WELCOME)
# ═══════════════════════════════════════════════════════════════
async def bot_squad_join_event(leader_uid, key, iv, region, chat_id):
    try:
        # 1. Random Bundle Change
        bundles = [914000002, 914000003, 914038001, 914039001, 914042001, 914044001, 914047001, 914047002, 914048001, 914050001, 914051001, 914053001]
        chosen_bundle = random.choice(bundles)
        b_pkt = await Look_Changer(chosen_bundle, key, iv, look_type=1, region=region)
        if b_pkt and online_writer:
            online_writer.write(b_pkt)
            await online_writer.drain()
        await asyncio.sleep(1)
        
        # 2. Random Evo Emote to Leader
        random_evo = random.choice(EVO_IDS)
        H = await Emote_k(int(leader_uid), int(random_evo), key, iv, region)
        if H and online_writer:
            online_writer.write(H)
            await online_writer.drain()
        await asyncio.sleep(1)
        
        # 3. Random Animation
        anims = [914000002, 914000003, 914038001, 914039001, 914042001, 914044001, 914047001, 914047002, 914048001, 914050001, 914051001, 914053001]
        chosen_anim = random.choice(anims)
        anim_pkt = await animation_packet(chosen_anim, key, iv)
        if anim_pkt and online_writer:
            online_writer.write(anim_pkt)
            await online_writer.drain()
        await asyncio.sleep(1)
        
        # 4. Welcome Message in Team Chat
        welcome_msg = get_welcome_header() + f"\n[B][C][00FF7F]Thanks for inviting me! 🎮\n[B][C][FFFFFF]Dev: {CREDIT_DEV}\n[B][C][FFFFFF]TG: {CREDIT_TG}\n[B][C][FFD700]Type [00FF00]/help [FFD700]to see all commands ❤️"
        pkt = await SEndMsG(2, welcome_msg, leader_uid, chat_id, key, iv)
        if pkt and whisper_writer:
            whisper_writer.write(pkt)
            await whisper_writer.drain()
            
    except Exception as e:
        print(f"Bot squad join event error: {e}")

# ═══════════════════════════════════════════════════════════════
# TCP ONLINE HANDLER
# ═══════════════════════════════════════════════════════════════
async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer, whisper_writer, region, pending_ghost_future, ghost_team_id, ghost_squad_code, emote_hijack, bot_uid
    while True:
        if FULL_RESTART_REQUESTED:
            print("🔄 Full restart requested -> leaving TcPOnLine so a fresh login can happen.")
            return
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            token_bytes = bytes.fromhex(AutHToKen) if isinstance(AutHToKen, str) else AutHToKen
            writer.write(token_bytes); await writer.drain()
            print(f"✅ ONLINE connected to {ip}:{port}")
            while not FULL_RESTART_REQUESTED:
                try:
                    data = await asyncio.wait_for(reader.read(9999), timeout=5)
                except asyncio.TimeoutError:
                    continue  # just re-checks FULL_RESTART_REQUESTED / loops again
                if not data: break
                hex_data = data.hex()
                if not hex_data.startswith("0500"): continue
                if emote_hijack and bot_uid:
                    asyncio.create_task(detect_and_hijack_emote(hex_data, key, iv, int(bot_uid), region))
                try: packet_json = json.loads(await DeCode_PackEt(hex_data[10:]))
                except Exception: continue
                try:
                    if ('5' in packet_json and 'data' in packet_json['5'] and '1' in packet_json['5']['data'] and '8' in packet_json['5']['data']):
                        owner = packet_json['5']['data']['1']['data']
                        code = packet_json['5']['data']['8']['data']
                        chat_code = None
                        try: chat_code = packet_json['5']['data']['17']['data']
                        except: pass
                        
                        join_pkt = await MahirAccepted(owner, code, key, iv, region)
                        if join_pkt and online_writer: await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_pkt)
                        
                        # Wait a moment for team chat to initialize
                        await asyncio.sleep(2)
                        
                        # Auto trigger bot event if we have chat code
                        if chat_code:
                            asyncio.create_task(bot_squad_join_event(owner, key, iv, region, chat_code))
                except Exception: pass
                try:
                    uid_g = packet_json['5']['data']['1']['data']
                    chat_code = packet_json['5']['data']['17']['data']
                    squad_code = packet_json['5']['data']['31']['data']
                    if uid_g is not None:
                        INV_JOIN = await AutH_Chat(3, uid_g, chat_code, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', INV_JOIN)
                except Exception: pass
                try:
                    if pending_ghost_future and not pending_ghost_future.done():
                        f5 = packet_json.get('5', {}).get('data', {})
                        if '31' in f5: ghost_squad_code = f5['31'].get('data')
                        if '1' in f5: ghost_team_id = f5['1'].get('data')
                        if ghost_team_id and ghost_squad_code: pending_ghost_future.set_result(True)
                except Exception: pass
                try:
                    if packet_json.get('4', {}).get('data') == 8:
                        f5 = packet_json.get('5', {}).get('data', {})
                        if f5.get('2', {}).get('data') == 5:
                            chat_code = f5.get('17', {}).get('data')
                            if chat_code is not None:
                                LeAvE = await leave_channel_req(chat_code, 3, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', LeAvE)
                except Exception: pass
            writer.close(); await writer.wait_closed(); online_writer = None
        except Exception as e:
            print(f"Online error: {ip}:{port} - {e}")
            online_writer = None
        await asyncio.sleep(reconnect_delay)

# ═══════════════════════════════════════════════════════════════
# HELP MENU (9 PAGES)
# ═══════════════════════════════════════════════════════════════
BOT_BRAND = "Ꮋꫝsɪʙ"
HELP_PAGE_DELAY = 1.0   # seconds between menu pages (raise if messages get dropped)

def get_welcome_header():
    return "[b][c][00FFFF] Hey User [FF0000] Welcome [FF00FF] To Hᴀsɪʙ [FFFF00] Cᴏᴅᴇx [fc0f94] ˣ BOT"

# ═══════════════════════════════════════════════════════════════
# BADGE COMMANDS  /s1 .. /s5   (ported from TEAM NEXUS PERSONAL)
# ═══════════════════════════════════════════════════════════════
BADGE_VALUES = {"s1": 1048576, "s2": 32768, "s3": 2048, "s4": 64, "s5": 262144}
BADGE_PACKETS = 5          # packets per command
BADGE_COOLDOWN = 30        # seconds per target uid
_badge_last = {}

async def request_join_with_badge(target_uid, badge_value, key, iv, region):
    """Send join request with specific badge - converted from your old TCP"""
    fields = {
        1: 33,
        2: {
            1: int(target_uid),
            2: region.upper(),
            3: 1,
            4: 1,
            5: bytes([1, 7, 9, 10, 11, 18, 25, 26, 32]),
            6: f"[C][B][FF0000]{BOT_BRAND}",
            7: 330,
            8: 1000,
            10: region.upper(),
            11: bytes([49, 97, 99, 52, 98, 56, 48, 101, 99, 102, 48, 52, 55, 56,
                       97, 52, 52, 50, 48, 51, 98, 102, 56, 102, 97, 99, 54, 49, 50, 48, 102, 53]),
            12: 1,
            13: int(target_uid),
            14: {
                1: 2203434355,
                2: 8,
                3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"
            },
            16: 1,
            17: 1,
            18: 312,
            19: 46,
            23: bytes([16, 1, 24, 1]),
            24: int(get_random_avatar()),
            26: "",
            28: "",
            31: {
                1: 1,
                2: badge_value  # Dynamic badge value
            },
            32: badge_value,    # Dynamic badge value
            34: {
                1: int(target_uid),
                2: 8,
                3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])
            }
        },
        10: "en",
        13: {
            2: 1,
            3: 1
        }
    }

    packet = (await CrEaTe_ProTo(fields)).hex()

    if region.lower() == "ind":
        packet_type = '0514'
    elif region.lower() == "bd":
        packet_type = "0519"
    else:
        packet_type = "0515"
    
    return await GeneRaTePk(packet, packet_type, key, iv)

async def handle_badge_command(cmd, text, uid, chat_id, key, iv, region, chat_type):
    parts = text.strip().split()
    if len(parts) < 2 or not parts[1].isdigit():
        await safe_send_message(chat_type, f"[B][C][FF0000]❌ Usage: /{cmd} [uid]\nExample: /{cmd} 123456789\n", uid, chat_id, key, iv)
        return
    target_uid = parts[1]
    now = time.time()
    if now - _badge_last.get(target_uid, 0) < BADGE_COOLDOWN:
        await safe_send_message(chat_type, f"[B][C][FF8C00]⏳ Please wait {BADGE_COOLDOWN}s before using /{cmd} on this uid again.\n", uid, chat_id, key, iv)
        return
    _badge_last[target_uid] = now
    badge_value = BADGE_VALUES.get(cmd, 1048576)
    await safe_send_message(chat_type, f"[B][C][1E90FF]🌀 Request received! Preparing to send {cmd} ({badge_value}) to {target_uid}...\n", uid, chat_id, key, iv)
    try:
        pkt = await request_join_with_badge(target_uid, badge_value, key, iv, region)
        if not pkt:
            await safe_send_message(chat_type, "[B][C][FF0000]❌ Failed to create badge packet!\n", uid, chat_id, key, iv)
            return
        for i in range(BADGE_PACKETS):
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', pkt)
            await asyncio.sleep(0.5)
        await safe_send_message(chat_type, f"[B][C][FFFF00]✅ Successfully Sent {cmd} Badge!\n🎯 Target: {target_uid}\n🏷️ Badge Value: {badge_value}\n📤 Packets Sent: {BADGE_PACKETS}\n", uid, chat_id, key, iv)
    except Exception as e:
        await safe_send_message(chat_type, f"[B][C][FF0000]❌ Error in /{cmd}: {e}\n", uid, chat_id, key, iv)

# ═══════════════════════════════════════════════════════════════
# /dhadha  (Bangla riddles)
# ═══════════════════════════════════════════════════════════════
DHADHA_LIST = [
    ("যত কাটো তত বড় হয়, বলো তো কী?", "গর্ত"),
    ("দাঁত আছে কিন্তু কামড়ায় না, কী সে?", "চিরুনি"),
    ("হাত নেই পা নেই, তবু সারাদিন চলে। মুখ নেই, তবু সময় বলে। কী সে?", "ঘড়ি"),
    ("যত ধোও তত নোংরা হয়, কী সে?", "পানি"),
    ("ডানা নেই তবু ভেসে বেড়ায়, চোখ নেই তবু কাঁদে। কী সে?", "মেঘ"),
    ("এমন কী জিনিস যা তোমার, কিন্তু অন্যরা তোমার চেয়ে বেশি ব্যবহার করে?", "তোমার নাম"),
    ("কোন জিনিস ভাঙলে আর জোড়া লাগে না এবং ভাঙার আগে হাতে নেওয়া যায় না?", "প্রতিজ্ঞা / ওয়াদা"),
    ("কোন মাসে ২৮ দিন থাকে?", "সব মাসেই!"),
    ("মুখ আছে কিন্তু কথা বলে না, বিছানা আছে কিন্তু ঘুমায় না। কী সে?", "নদী"),
    ("যত বেশি নাও, তত বেশি পেছনে পড়ে থাকে। কী সে?", "পায়ের ছাপ"),
    ("ভাগ করলে বাড়ে, কমে না। কী সে?", "আনন্দ"),
    ("রাতে আসে, দিনে হারিয়ে যায়, চুরিও হয় না। কী সে?", "তারা"),
    ("ছোট্ট এক কাঠি, মাথায় তার আগুন। একবার জ্বললে আর জ্বলে না। কী সে?", "দেশলাইয়ের কাঠি"),
    ("আমি উঠলে সবাই জাগে, আমি ডুবলে সবাই ঘুমায়। কে আমি?", "সূর্য"),
    ("চোখ আছে কিন্তু দেখতে পায় না, কী সে?", "সুই / আলু"),
]

# ═══════════════════════════════════════════════════════════════
# HELP MENU (12 PAGES, Personal tree style)
# ═══════════════════════════════════════════════════════════════
def get_help_pages():
    """/help -> 20 pages x 15 commands (built from extra_cmds registry + existing commands)."""
    return extra_cmds.build_help_pages(BOT_BRAND)

def _legacy_help_pages():
    """/help -> 13 pages, fixed per-page colours matching the Personal reference design exactly
    (no random colour rotation). Only real, working OB55 commands are listed — no fake/attack/spam entries."""
    B = BOT_BRAND
    BAR = "──────────────────"

    def page(col, title, *rows):
        body = "\n".join(rows)
        return f"""[B][{col}]■ {B}ㅤ MENU {title} ■
[B][{col}]{BAR}
{body}
[B][{col}]{BAR}"""

    h1 = page("FFA500", "01",
        "[B][FFD700]MATCH & SQUAD",
        "[B][FFA500]├─[00FF00]/join [code] [FFFFFF](Join Squad)",
        "[B][FFA500]└─[00FF00]/exit [FFFFFF](Leave Squad)",
        "[B][FFA500]──────────────────",
        "[B][FFD700]TEAM CREATION",
        "[B][FFA500]├─[00FF00]/3 /4 /5 /6 [FFFFFF](Team Size)",
        "[B][FFA500]└─[00FF00]/gh [tc] [name] [FFFFFF](Ghost Join)")

    h2 = page("00FFFF", "02",
        "[B][FFD700]EMOTE CONTROL",
        "[B][00FFFF]├─[00FFFF][number] [FFFFFF](Self Emote)",
        "[B][00FFFF]├─[00FFFF]aa[num] [tc] [FFFFFF](Magic Emote)",
        "[B][00FFFF]├─[00FFFF]/menu[num] [FFFFFF](All Emotes Menu)",
        "[B][00FFFF]├─[00FFFF]/copy /copy off [FFFFFF](Emote Hijack)",
        "[B][00FFFF]└─[00FFFF]/dance [uids] /dance stop [FFFFFF](Dance)",
        "[B][00FFFF]──────────────────",
        "[B][FFD700]EVO CONTROL",
        "[B][00FFFF]├─[00FFFF]/ob55 /max [FFFFFF](Max Evo Self)",
        "[B][00FFFF]├─[00FFFF]/s [FFFFFF](Stop Evo Cycle)",
        "[B][00FFFF]└─[00FFFF]@max @evos [FFFFFF](Max Evo Bot)")

    h3 = page("FF00FF", "03",
        "[B][FFD700]EVO CYCLE",
        "[B][DA70D6]├─[00FF00]/o [FFFFFF](Stop Bot Evo)",
        "[B][DA70D6]├─[00FF00]new [FFFFFF](Random Evo Self)",
        "[B][DA70D6]├─[00FF00]/sm /sn [FFFFFF](Stop Random)",
        "[B][DA70D6]├─[00FF00]@new [FFFFFF](Random Bot)",
        "[B][DA70D6]├─[00FF00]@bot [FFFFFF](Only Bot Random)",
        "[B][DA70D6]└─[00FF00]@bt [FFFFFF](Stop Bot Cycle)",
        "[B][DA70D6]──────────────────",
        "[B][FFD700]EVO EXTRA",
        "[B][DA70D6]├─[00FF00]/evo [uid] [1-21] [FFFFFF](Evo Emote)",
        "[B][DA70D6]└─[00FF00]/evos /sevos [FFFFFF](Evo Cycle)")

    h4 = page("8A2BE2", "04",
        "[B][FFD700]CUSTOM EMOTE",
        "[B][8A2BE2]├─[9370DB]/p [uid] [em] [num] [FFFFFF](Custom Emote)",
        "[B][8A2BE2]└─[9370DB]/mg [txt] [rep] [FFFFFF](Wave Text)",
        "[B][8A2BE2]──────────────────",
        "[B][FFD700]SYSTEM",
        "[B][8A2BE2]├─[9370DB]/check [uid] [FFFFFF](Ban Check)",
        "[B][8A2BE2]└─[9370DB]/stop msg [FFFFFF](Stop Wave Text)")

    h5 = page("FF0000", "05",
        "[B][FFD700]BADGE SHOW",
        "[B][FF0000]├─[1690E8]/s1 [uid] [FFFFFF](Badge 1)",
        "[B][FF0000]├─[1690E8]/s2 [uid] [FFFFFF](Badge 2)",
        "[B][FF0000]├─[1690E8]/s3 [uid] [FFFFFF](Badge 3)",
        "[B][FF0000]├─[1690E8]/s4 [uid] [FFFFFF](Badge 4)",
        "[B][FF0000]└─[1690E8]/s5 [uid] [FFFFFF](Badge 5)",
        "[B][FF0000]──────────────────",
        "[B][FFD700]ROOM TOOLS",
        "[B][FF0000]├─[1690E8]/room [uid] [room_id] [FFFFFF](Room Invite)",
        "[B][FF0000]└─[1690E8]/ice [uid] [FFFFFF](Freeze Emote)")

    h6 = page("FF1493", "06",
        "[B][FFD700]ATTACK & INFO",
        "[B][00FF7F]├─[1AF7B6]/info [uid] [FFFFFF](Player Info)",
        "[B][00FF7F]└─[1AF7B6]/check [uid] [FFFFFF](Ban Status)",
        "[B][00FF7F]──────────────────",
        "[B][FFD700]FUN & ENTERTAINMENT",
        "[B][00FF7F]├─[1AF7B6]/gali [name] [FFFFFF](Bangla Gali)",
        "[B][00FF7F]└─[1AF7B6]/praisa [name] [FFFFFF](Praise)")

    h7 = page("4169E1", "07",
        "[B][FFD700]TOOLS",
        "[B][4169E1]├─[F3FE83]/help [FFFFFF](Show Help)",
        "[B][4169E1]├─[F3FE83]/admin [FFFFFF](Admin Info)",
        "[B][4169E1]├─[F3FE83]/tt [username] [FFFFFF](TikTok Info)",
        "[B][4169E1]├─[F3FE83]/yt [channel] [FFFFFF](YouTube Info)",
        "[B][4169E1]└─[F3FE83]/translet [lang] [txt] [FFFFFF](Translate)",
        "[B][4169E1]──────────────────",
        "[B][FFD700]CUSTOM & LETTERS",
        "[B][4169E1]├─[F3FE83]/b [num] [FFFFFF](Equip Bundle)",
        "[B][4169E1]└─[F3FE83]/later [name] [FFFFFF](Love Letter)")

    h8 = page("00BFFF", "08",
        "[B][FFD700]FUN",
        "[B][00BFFF]├─[5BEBBB]/sadlater [name] [FFFFFF](Sad Letter)",
        "[B][00BFFF]├─[5BEBBB]/love [name] [FFFFFF](Love Spam)",
        "[B][00BFFF]└─[5BEBBB]/roast [name] [FFFFFF](Roast Someone)",
        "[B][00BFFF]──────────────────",
        "[B][FFD700]FRIEND TOOLS (Admin)",
        "[B][00BFFF]├─[5BEBBB]/add [uid] [FFFFFF](Add Friend)",
        "[B][00BFFF]└─[5BEBBB]/remove [uid] [FFFFFF](Remove Friend)")

    h9 = page("FF75EA", "09",
        "[B][FFD700]CUSTOMS",
        "[B][FF75EA]├─[66EA13]/animation [num] [FFFFFF](Animation)",
        "[B][FF75EA]├─[66EA13]/e [uid] [emote] [FFFFFF](Emote Send)",
        "[B][FF75EA]├─[66EA13]/frt [n1]&[n2] [FFFFFF](Friend %)",
        "[B][FF75EA]├─[66EA13]/grt [n1]&[n2] [FFFFFF](Soul %)",
        "[B][FF75EA]└─[66EA13]/alltitles [FFFFFF](All Titles)")

    h10 = page("DA70D6", "10",
        "[B][FFD700]FUN GAMES",
        "[B][DA70D6]├─[00FF00]/quiz [FFFFFF](Quiz)",
        "[B][DA70D6]├─[00FF00]/dare /truth /wyr [FFFFFF](Party Games)",
        "[B][DA70D6]├─[00FF00]/roll /rps /8ball [FFFFFF](Luck Games)",
        "[B][DA70D6]├─[00FF00]/dhadha [FFFFFF](Bangla Riddle)",
        "[B][DA70D6]├─[00FF00]/zodiac [FFFFFF](Zodiac)",
        "[B][DA70D6]├─[00FF00]/joke [FFFFFF](Joke)",
        "[B][DA70D6]└─[00FF00]/spin [FFFFFF](Lucky Spin)")

    h11 = page("1690E8", "11",
        "[B][FFD700]EXTRA TOOLS",
        "[B][1690E8]├─[5BEBBB]/weather [FFFFFF](Weather)",
        "[B][1690E8]├─[5BEBBB]/title [FFFFFF](Title)",
        "[B][1690E8]├─[5BEBBB]/luck [name] [FFFFFF](Fortune)",
        "[B][1690E8]├─[5BEBBB]/coinflip [FFFFFF](Coin Toss)",
        "[B][1690E8]└─[5BEBBB]/meme [FFFFFF](Random Meme)",
        "[B][1690E8]──────────────────",
        "[B][FFD700]MORE ACTIONS",
        "[B][1690E8]├─[5BEBBB]/laugh /scream /pray [FFFFFF](Actions)",
        "[B][1690E8]└─[5BEBBB]/shower /toilet [FFFFFF](Actions)")

    h12 = page("FF4500", "12",
        "[B][FFD700]CONTROL (Admin)",
        "[B][00FF7F]├─[FFFFFF]/on /off [FFFFFF](Bot ON/OFF)",
        "[B][00FF7F]├─[FFFFFF]/ban [uid] [FFFFFF](Ban Spam)",
        "[B][00FF7F]├─[FFFFFF]/ban stop /unban [FFFFFF](Stop Ban)",
        "[B][00FF7F]├─[FFFFFF]/restart [FFFFFF](Offline -> Auto Online)",
        "[B][00FF7F]├─[FFFFFF]/pc /phone [FFFFFF](Login Mode)",
        "[B][00FF7F]├─[FFFFFF]/display_msg [_off] [FFFFFF](Swap xC4 + Restart)",
        "[B][00FF7F]└─[FFFFFF]/stop [FFFFFF](Stop All)")

    h13 = page("9370DB", "13 — NEW TOOLS",
        "[B][9370DB]├─[00FF00]/password [n] [FFFFFF](Generate Password)",
        "[B][9370DB]├─[00FF00]/bmi [kg] [m] [FFFFFF](BMI Calculator)",
        "[B][9370DB]├─[00FF00]/age [year] [FFFFFF](Age Calculator)",
        "[B][9370DB]├─[00FF00]/dice [NdM] [FFFFFF](Dice Roller)",
        "[B][9370DB]├─[00FF00]/reverse [txt] [FFFFFF](Reverse Text)",
        "[B][9370DB]├─[00FF00]/count [txt] [FFFFFF](Char/Word Count)",
        "[B][9370DB]├─[00FF00]/anagram [word] [FFFFFF](Shuffle Letters)")

    h14 = page("9370DB", "14 — NEW TOOLS",
        "[B][9370DB]├─[00FF00]/binary /morse [txt] [FFFFFF](Encode Text)",
        "[B][9370DB]├─[00FF00]/leet /rot13 [txt] [FFFFFF](Cipher Text)",
        "[B][9370DB]├─[00FF00]/percent [x] of [y] [FFFFFF](Percentage)",
        "[B][9370DB]├─[00FF00]/pick [a,b,c] [FFFFFF](Random Pick)",
        "[B][9370DB]├─[00FF00]/yesno [FFFFFF](Magic Answer)",
        "[B][9370DB]├─[00FF00]/compliment [name] [FFFFFF](Nice Message)")

    h15 = page("9370DB", "15 — NEW TOOLS",
        "[B][9370DB]├─[00FF00]/fact /namegen [FFFFFF](Fun Fact/Name)",
        "[B][9370DB]├─[00FF00]/color [FFFFFF](Random Hex Color)",
        "[B][9370DB]├─[00FF00]/define [word] [FFFFFF](Dictionary)",
        "[B][9370DB]├─[00FF00]/chucknorris [FFFFFF](Random Joke)",
        "[B][9370DB]└─[00FF00]/name [text] [FFFFFF](Big Banner Name)")

    guild = f"""[B][4169E1]■ BOT SYSTEM ■
[B][4169E1]──────────────────
[B][FFD700]DEVELOPER INFO
[B][4169E1]├─[FFFFFF]Owner: [FFD700]{B}
[B][4169E1]└─[FFFFFF]Powered By: [FFFF00]ᎻꫝsɪʙㅤCᴏᴅᴇx
[B][4169E1]──────────────────
[B][FF0000]NOTE
[B][4169E1]├─[FFFFFF]Stop Any Task: [FF0000]/stop
[B][4169E1]└─[FFFFFF]Status: [00FF00]Online"""

    return (h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, guild)

# ═══════════════════════════════════════════════════════════════
# PERSONAL COLOURS / MESSAGES  (/love, /roast, evo start+stop texts)
# ═══════════════════════════════════════════════════════════════
LOVE_PREFIX  = "[B][C][FFFFFF][B][C][32CD32][FFFFFF][FFA500][FFFFFF][FF00FF][FFD700][FFFFFF][00FFFF][FF1493][00FF00][FFFFFF][FF0000] "
ROAST_PREFIX = "[B][C][FFFFFF][B][C][32CD32][FFFFFF][FFA500][FFFFFF][FF00FF][FFD700][FFFFFF][00FFFF] "
BANGLA_JOKES = ['এক লোক ডাক্তার কাছে গেল।\nলোক: ডাক্তার সাহেব, আমার সবকিছু ভুলে যাওয়ার রোগ হয়েছে।\nডাক্তার: কবে থেকে হয়েছে?\nলোক: কী কবে থেকে হয়েছে?\nডাক্তার: এই যে ভুলে যাওয়ার রোগ!\nলোক: ওহ! আমি তো ভুলেই গিয়েছিলাম কেন এসেছি!', 'এক ছাত্র পরীক্ষায় কিছুই লিখতে পারছে না।\nশিক্ষক: কেন কিছু লিখছ না?\nছাত্র: স্যার, প্রশ্নগুলো খুব কঠিন।\nশিক্ষক: তাহলে সহজটা লেখো।\nছাত্র: স্যার, সহজ প্রশ্নটা তো আপনি করেননি!', 'এক বন্ধু আরেক বন্ধুকে বলল,\nআমি কাল থেকে ডায়েট শুরু করব।\nবন্ধু: কাল কেন?\nসে: আজকে ফ্রিজে যত খাবার আছে শেষ করতে হবে।\nবন্ধু: তাহলে তোর ডায়েট কখনোই শুরু হবে না!', 'এক লোক দোকানে গিয়ে বলল,\nভাই, এমন একটা ঘড়ি দেখান যেটা পানিতে নষ্ট হবে না।\nদোকানদার একটা ঘড়ি দেখালেন।\nলোক: এটা কি সত্যি পানিতে নষ্ট হবে না?\nদোকানদার: না, কারণ এটা আমি কাউকে পানিতে ফেলতে দিই না!', 'শিক্ষক ক্লাসে জিজ্ঞেস করলেন,\nবল তো, পৃথিবী গোল কেন?\nএক ছাত্র: স্যার, যদি পৃথিবী চৌকো হতো…\nশিক্ষক: তাহলে?\nছাত্র: তাহলে কোণায় বসে আমরা পড়াশোনা এড়িয়ে যেতাম!', 'এক লোক বন্ধুকে বলল,\nআমি গতকাল জিমে ভর্তি হয়েছি।\nবন্ধু: সত্যি?\nলোক: হ্যাঁ, আজকে জিমের সামনে দিয়ে হেঁটে এসেছি।\nবন্ধু: ভিতরে ঢুকলি না?\nলোক: না, এত তাড়াহুড়ো কেন!', 'এক ছাত্র বাবাকে বলল,\nবাবা, পরীক্ষায় আমি পাশ করেছি।\nবাবা: কত নম্বর পেয়েছ?\nছাত্র: শিক্ষক দয়া করে পাশ করিয়েছেন।\nবাবা: তাহলে পড়াশোনা কর।\nছাত্র: বাবা, দয়া থাকলে পড়াশোনা লাগে?', 'এক লোক রেস্টুরেন্টে গিয়ে বলল,\nভাই, খাবার এত দেরি হচ্ছে কেন?\nওয়েটার: স্যার, আমরা তাজা খাবার বানাই।\nলোক: তাজা মানে?\nওয়েটার: মুরগিটা ধরতে একটু সময় লাগে!', 'এক ছেলে মাকে বলল,\nমা, আমার মাথা খুব ব্যথা করছে।\nমা: তাহলে পড়তে বসো না।\nছেলে: তাহলে তো মাথা আরও ব্যথা করবে!\nমা: কেন?\nছেলে: কারণ পড়া দেখলেই মাথা ধরে!', 'এক বন্ধু বলল,\nতুই এত দেরি করে কেন এলি?\nঅন্য বন্ধু: রাস্তা ভুলে গিয়েছিলাম।\nসে: তুই তো এই এলাকায় থাকিস!\nবন্ধু: হ্যাঁ, কিন্তু মোবাইলে গেম খেলতে খেলতে রাস্তা ভুলে গেছি!', 'এক ছাত্র বলল,\nস্যার, আমি সব বুঝেছি।\nস্যার: তাহলে বোর্ডে এসে বুঝিয়ে দাও।\nছাত্র: স্যার, আমি বুঝেছি কিন্তু বোঝাতে পারব না।\nস্যার: কেন?\nছাত্র: কারণ বোঝাতে গেলে আবার বুঝতে হবে!', 'এক লোক বলল,\nআমার ঘড়ি সব সময় এগিয়ে যায়।\nবন্ধু: তাহলে ভালোই তো!\nলোক: ভালো কোথায়?\nবন্ধু: সব কাজে আগে পৌঁছাবে।\nলোক: না, সবাই ভাবে আমি দেরি করেছি!', 'এক ছেলে বাবাকে বলল,\nবাবা, আমি বড় হয়ে বড়লোক হব।\nবাবা: কীভাবে?\nছেলে: আমি ইউটিউবার হব।\nবাবা: ভিডিও বানাতে পারো?\nছেলে: না, কিন্তু কমেন্ট করতে পারি!', 'এক ছাত্র বলল,\nস্যার, আমার পেট ব্যথা।\nস্যার: তাহলে বাড়ি যাও।\nছাত্র: তাহলে তো কাল আবার স্কুলে আসতে হবে।\nস্যার: তাতে সমস্যা কী?\nছাত্র: আজই যদি না আসতাম!', 'এক বন্ধু বলল,\nআমি খুব পরিশ্রম করি।\nঅন্য বন্ধু: কী কাজ করিস?\nসে: ঘুমানোর আগে ভাবি কাল কী করব।\nবন্ধু: তারপর?\nসে: সকালে উঠে ভুলে যাই!', 'এক ছেলে বলল,\nমা, আমি ডায়েট করছি।\nমা: তাহলে এত খাচ্ছ কেন?\nছেলে: ডায়েট কাল থেকে শুরু হবে।\nমা: আজ?\nছেলে: আজ বিদায় পার্টি!', 'এক ছাত্র বলল,\nস্যার, আমি আজ পড়া পারিনি।\nস্যার: কেন?\nছাত্র: কারেন্ট ছিল না।\nস্যার: দিনে তো কারেন্ট লাগে না।\nছাত্র: স্যার, দিনে তো ঘুমাই!', 'এক লোক বলল,\nআমার ফোন খুব স্মার্ট।\nবন্ধু: কেন?\nলোক: আমি পড়তে বসলে নিজেই গেম খুলে যায়।\nবন্ধু: তাহলে ফোন না তুই স্মার্ট?\nলোক: ফোনই!', 'এক ছাত্র বলল,\nস্যার, আমার কলম কাজ করছে না।\nস্যার: তাহলে অন্য কলম নাও।\nছাত্র: তাও কাজ করছে না।\nস্যার: কেন?\nছাত্র: কারণ আমি পড়িনি!', 'এক বন্ধু বলল,\nতুই এত মোটা কেন?\nঅন্যজন: আমি সুখে আছি।\nবন্ধু: সুখে থাকলে মোটা হয়?\nসে: খেতে খেতে সুখ পাই!', 'এক ছেলে বলল,\nবাবা, আমি পড়াশোনা করব না।\nবাবা: তাহলে কী করবি?\nছেলে: বিজনেস করব।\nবাবা: কী বিজনেস?\nছেলে: ঘুমানোর!', 'এক বন্ধু বলল,\nতোর প্রেম কেমন চলছে?\nঅন্য বন্ধু: WiFi এর মতো।\nবন্ধু: মানে?\nসে: কখনো কানেক্ট হয়, কখনো যায়!', 'এক ছাত্র বলল,\nস্যার, আমি পড়া ভুলে গেছি।\nস্যার: কেন?\nছাত্র: মনে রাখতে জায়গা ছিল না।\nস্যার: কেন?\nছাত্র: সব জায়গা গেমে ভর্তি!', 'এক লোক বলল,\nআমি আজ খুব কাজ করেছি।\nবন্ধু: কী কাজ?\nলোক: ঘুম থেকে উঠেছি।\nবন্ধু: আর?\nলোক: আবার ঘুমিয়েছি!', 'এক ছাত্র বলল,\nস্যার, আমি বই খুলেছি।\nস্যার: তাহলে পড়ো।\nছাত্র: স্যার, খুলতেই তো কষ্ট হয়েছে!', 'এক বন্ধু বলল,\nতুই এত অলস কেন?\nঅন্যজন: আমি শক্তি সঞ্চয় করি।\nবন্ধু: কিসের জন্য?\nসে: ঘুমানোর জন্য!', 'এক ছেলে বলল,\nমা, আমি ক্ষুধার্ত।\nমা: ফ্রিজে খাবার আছে।\nছেলে: ফ্রিজ খুলতে আলসেমি লাগছে!', 'এক ছাত্র বলল,\nস্যার, আমার মাথা কাজ করছে না।\nস্যার: কেন?\nছাত্র: আমি ছুটি দিয়েছি!', 'এক লোক বলল,\nআমি দৌড়াতে পারি না।\nবন্ধু: কেন?\nলোক: দৌড়ালেই হাঁপিয়ে যাই।', 'এক ছেলে বলল,\nবাবা, আমি বড় হয়ে পাইলট হব।\nবাবা: কেন?\nছেলে: স্কুলে না যাওয়ার জন্য!', 'এক ছাত্র বলল,\nস্যার, আমার পেট ব্যথা।\nস্যার: ডাক্তারের কাছে যাও।\nছাত্র: তাহলে তো স্কুলে আসতে হবে না!', 'এক বন্ধু বলল,\nতুই কি পড়াশোনা করিস?\nঅন্যজন: হ্যাঁ।\nবন্ধু: কখন?\nসে: পরীক্ষার আগের রাত!', 'এক ছেলে বলল,\nমা, আমি আজ পড়ব।\nমা: খুব ভালো।\nছেলে: কিন্তু কাল থেকে!', 'এক ছাত্র বলল,\nস্যার, আমি বই পড়েছি।\nস্যার: কী বুঝেছ?\nছাত্র: বইটা ভারী!', 'এক লোক বলল,\nআমি আজ খুব ব্যস্ত।\nবন্ধু: কী কাজ?\nলোক: কিছু না করার কাজ!', 'এক বন্ধু বলল,\nতুই এত ঘুমাস কেন?\nঅন্যজন: স্বপ্নে কাজ করি!', 'এক ছেলে বলল,\nমা, আমার খুব ক্ষুধা।\nমা: খাবার খাও।\nছেলে: তুমি খাইয়ে দাও!', 'এক ছাত্র বলল,\nস্যার, প্রশ্নটা বুঝিনি।\nস্যার: আবার পড়ো।\nছাত্র: তবুও বুঝব না!', 'এক বন্ধু বলল,\nতুই এত মোবাইল ব্যবহার করিস কেন?\nঅন্যজন: মোবাইল আমাকে ব্যবহার করে!', 'এক ছেলে বলল,\nবাবা, আমি পড়তে বসেছি।\nবাবা: তাহলে পড়ো।\nছেলে: ঘুম পাচ্ছে!', 'এক ছাত্র বলল,\nস্যার, আমার খাতা হারিয়ে গেছে।\nস্যার: কোথায়?\nছাত্র: যেখানে পড়িনি!', 'এক বন্ধু বলল,\nতুই এত হাসছ কেন?\nঅন্যজন: কারণ কাঁদতে ইচ্ছে করছে!', 'এক ছেলে বলল,\nমা, আমি বড় হয়ে ধনী হব।\nমা: কীভাবে?\nছেলে: স্বপ্নে!', 'এক ছাত্র বলল,\nস্যার, আমি পড়িনি।\nস্যার: কেন?\nছাত্র: বই আমাকে ডাকেনি!', 'এক বন্ধু বলল,\nতুই এত কথা বলিস কেন?\nঅন্যজন: চুপ থাকতে পারি না!', 'এক ছেলে বলল,\nমা, আমি আজ স্কুলে যাব না।\nমা: কেন?\nছেলে: ঘুম ভালো লাগছে!', 'এক ছাত্র বলল,\nস্যার, আমার কলম শেষ।\nস্যার: তাহলে লিখবে কী দিয়ে?\nছাত্র: মনে!', 'এক বন্ধু বলল,\nতুই কি কাজ করিস?\nঅন্যজন: ভাবি!', 'এক ছেলে বলল,\nমা, আমার মাথা ঘুরছে।\nমা: কম মোবাইল ব্যবহার কর।', 'এক ছাত্র বলল,\nস্যার, আমি আজ পড়ব না।\nস্যার: কেন?\nছাত্র: আজ রবিবার!', 'এক লোক ট্রেনে উঠে বলল,\nভাই, এই ট্রেন কোথায় যায়?\nযাত্রী: এটা কুমিল্লা যায়।\nলোক: আমি তো ঢাকা যাব!\nযাত্রী: তাহলে নামুন!\nলোক: ট্রেনটা ঘুরিয়ে দেন না!', 'এক ছেলে বলল,\nবাবা, আমার পকেটমানি বাড়াও।\nবাবা: কেন?\nছেলে: বন্ধুরা বেশি পায়।\nবাবা: তাহলে ওদের বাবা হও!', 'এক লোক হাসপাতালে গিয়ে বলল,\nডাক্তার, আমি কি বাঁচব?\nডাক্তার: আপনার কি হয়েছে?\nলোক: কিছু হয়নি, শুধু জানতে চাই!\nডাক্তার: তাহলে বিল দিন!', 'এক ছাত্র বলল,\nস্যার, বাংলাদেশ কোন মহাদেশে?\nস্যার: এশিয়া।\nছাত্র: তাহলে আমরা এশিয়ান?\nস্যার: হ্যাঁ।\nছাত্র: তাহলে আমিও জাপানি!', 'এক বন্ধু বলল,\nতুই কি রান্না পারিস?\nঅন্যজন: হ্যাঁ, পানি গরম করতে পারি!\nবন্ধু: সেটা তো রান্না না!\nসে: পানি ছাড়া রান্না হয়?', 'এক ছেলে বলল,\nমা, আমি প্রেসিডেন্ট হতে চাই।\nমা: আগে ঘর গুছাও।\nছেলে: প্রেসিডেন্ট কি ঘর গোছায়?\nমা: না, কিন্তু তুইও প্রেসিডেন্ট হবি না!', 'এক লোক বলল,\nআমি একজন মাল্টিটাস্কার।\nবন্ধু: কীভাবে?\nলোক: একসাথে খাই, ঘুমাই আর স্বপ্ন দেখি!', 'এক ছাত্র বলল,\nস্যার, ইংরেজি কেন শিখব?\nস্যার: চাকরি পাবে।\nছাত্র: আমি তো ইউটিউবার হব!\nস্যার: তাহলে thumbnail বানাতে শেখ!', 'এক বন্ধু বলল,\nতোর জীবনের লক্ষ্য কি?\nঅন্যজন: শুক্রবার!\nবন্ধু: সেটা তো দিন!\nসে: আমার জীবনের সেরা দিন!', 'এক ছেলে বলল,\nমা, WiFi পাসওয়ার্ড কি?\nমা: আগে পড়ো।\nছেলে: সেটাই পাসওয়ার্ড?\nমা: না, আমি বলছি পড়াশোনা করো!', 'এক লোক বলল,\nআমি ভবিষ্যৎ দেখতে পাই।\nবন্ধু: সত্যি?\nলোক: হ্যাঁ, আমি দেখতে পাচ্ছি তুই এখন হাসবি!', 'এক ছাত্র বলল,\nস্যার, আমি তো জিনিয়াস!\nস্যার: প্রমাণ?\nছাত্র: আমার মা বলেছে!\nস্যার: মায়ের কথা সবসময় ঠিক হয় না!', 'এক বন্ধু বলল,\nতুই ফেসবুকে কি করিস সারাদিন?\nঅন্যজন: রিসার্চ!\nবন্ধু: কিসের?\nসে: মিম এর!', 'এক ছেলে বলল,\nবাবা, আমাকে একটা নতুন ফোন কিনে দাও।\nবাবা: পুরানোটা কি হয়েছে?\nছেলে: ভালো আছে, কিন্তু বন্ধুদের সামনে লজ্জা লাগে!\nবাবা: তাহলে বন্ধু বদলাও!', 'এক লোক রাস্তায় হেঁটে যাচ্ছিল।\nহঠাৎ একজন বলল, ভাই সময় কত?\nলোক: আমার কাছে ঘড়ি নেই।\nসে: তাহলে ফোন দেখুন।\nলোক: ফোনও নেই।\nসে: তাহলে আপনি কীভাবে সময় জানেন?\nলোক: জানি না তো!', 'এক ছাত্র পরীক্ষার হলে বসে ফ্যানের দিকে তাকাচ্ছে।\nশিক্ষক: ফ্যানের দিকে তাকাচ্ছ কেন?\nছাত্র: স্যার, ভাবছি ফ্যান ঘুরতে পারলে আমিও পারব!', 'এক বন্ধু বলল,\nতুই কি চশমা পরিস?\nঅন্যজন: হ্যাঁ।\nবন্ধু: দৃষ্টি কত কম?\nসে: এত কম যে চশমা ছাড়া চশমা খুঁজে পাই না!', 'এক ছেলে বলল,\nমা, আমি আজ ফার্স্ট হয়েছি!\nমা: সত্যি?\nছেলে: হ্যাঁ, ক্লাসে প্রথম ঢুকেছি!', 'এক লোক বলল,\nআমি সাঁতার জানি না।\nবন্ধু: তাহলে শেখ।\nলোক: পানিতে নামলেই ডুবি!\nবন্ধু: তাই তো শিখতে হবে!\nলোক: ডুবে গেলে শিখব কীভাবে?']
JOKE_COLORS = ['FF4500', '00CED1', 'FFD700', 'FF69B4', '7CFC00', 'FF6347', '00BFFF', 'FF1493', '32CD32', 'FFA500',
               '9370DB', '1E90FF', 'DC143C', '20B2AA', '7B68EE', 'DA70D6', '00FF7F', 'FF8C00', 'ADFF2F', 'FF6EC7']
LOVE_COLORS = ['FF1493', '00FFFF', 'FFD700', 'FF00FF', '32CD32', 'FFA500', 'FF69B4', 'FF0000',
               '9370DB', '1E90FF', 'DC143C', '00FF7F', 'DA70D6', '7B68EE']

BLACKLIST_NAMES = ["hasib", "hasibvai", "sami", "mostakim", "rifat", "rifa"]   # ei nam gula /gali /rt /roast e target kora jabe na (nijer o bondhur nam ekhane boshao)

def is_blacklisted(name):
    return name.strip().lower().replace(" ", "") in [n.strip().lower().replace(" ", "") for n in BLACKLIST_NAMES]

BLACKLIST_WARN_MSG = "[B][C][FF0000]⚠️ WARNING!\n[FFFFFF]এই নামটা টার্গেট করা যাবে না ⛔"
ROAST_LINES = [
    "আরে {Name} তো একটা আস্ত বট! 😂",
    "{Name} গেম খেলা বাদ দিয়ে লুডু খেল যা! 🤣",
    "{Name} এর হেডশট রেট মাইনাসে চলে গেছে! 📉",
    "{Name} ল্যান্ড করার আগেই লবিতে চলে যায়! 🪂💨",
    "সবাই সাবধানে থেকো, {Name} নামের বট গেমে ঢুকেছে! 🤖",
    "আরে {Name}, তুই তো প্রো... প্রো-ম্যাক্স লেভেলের বট! 🤡",
    "{Name} এর থেকে তো ট্রেনিং গ্রাউন্ডের পুতুলও ভালো খেলে! 🗿",
    "বুইয়া তো দূরের কথা, {Name} তো জোন সারভাইভ করতেই মরে যায়! ☠️",
    "ভাই {Name}, তুই কি বন্দুকের বদলে লাঠি নিয়ে খেলিস? 🦯",
    "ও ভাই! {Name} তো এনিমি দেখলে উল্টা দৌড় দেয়! 🏃‍♂️💨",
    "এনিমি দেখলে {Name} এর হাত-পা কাঁপে! 🥶",
    "{Name} এর মতো বট আমি জীবনেও দেখি নাই! 🤦‍♂️",
    "গেমের সবচেয়ে বড় বট অ্যাওয়ার্ড {Name} কে দেওয়া হোক! 🏆",
    "{Name} ভাই, তুই ফ্রি ফায়ার ডিলিট করে দে! 🗑️",
    "{Name} এর গেমপ্লে দেখলে এনিমিও হাসতে হাসতে মরে যাবে! 😆",
    "{Name} এর কিল চুরি করার ট্যালেন্ট অস্কার পাওয়ার মতো! 🎭",
    "টিমমেট নক হলে {Name} সবার আগে পালায়! 🏃‍♂️",
    "গান স্কিন দিয়ে কী হবে, {Name} তো গুলি করতেই ভুলে যায়! 🔫",
    "{Name} তো গেম খেলে না, গেম {Name} কে নিয়ে খেলে! 🎮",
    "{Name} হলো ফ্রি ফায়ারের জীবন্ত লেজেন্ডারি বট! 👑",
]

# start / stop messages per evo mode (Personal texts)
EVO_START_MSG = {
    "user": "[B][C][00FFFF]🔥 OB55 SPECIAL EMOTE STARTED STOP[00FF00] COMMAND /s 🔥",
    "sm":   "[B][C][FFFF00]✅ SUCCESS! [00FFFF]Evolution emote[b][c][ffffff] cycle started!\n🎯 Target: [00FFFF]সঠিক ভাবে চালু [b][c][ffffff]হয়েছে\n🔄 Cycle: বন্ধ করতে /o\n",
    "new":  "[B][C][FFFF00]✅ SUCCESS! [00FFFF] emote[b][c][00ff00] cycle started!\n🎯 Target: [00FFFF]সঠিক ভাবে চালু [b][c][ffffff]হয়েছে\n🔄 Cycle: বন্ধ করতে /sm\n",
    "sam":  "[B][C][FFFF00]✅ SUCCESS! [00FFFF]Evolution emote[b][c][FFFFFF] cycle started!\n🎯 Target: [00FFFF]সঠিক ভাবে চালু [b][c][00FF00]হয়েছে\n🔄 Cycle: বন্ধ করতে /sn\n",
    "bot":  "[B][C][FFFF00]✅ SUCCESS! [00FFFF]Evolution emote[b][c][00ff00] cycle started!\n🎯 Target: [00FFFF]সঠিক ভাবে চালু [b][c][00ff00]হয়েছে\n🔄 Cycle: বন্ধ করতে @bt\n",
}

# ═══════════════════════════════════════════════════════════════
# EVO ENGINE (ported from PERSONAL: evo_cycle_spam / _sm / _sam / _bot / emotes_cycle_spam)
# ═══════════════════════════════════════════════════════════════
EVO_P_EMOTES = {'1': '909054005', '2': '909054001', '3': '909054003', '4': '909054004', '5': '909054010', '6': '909054008', '7': '909054013', '8': '909054014', '9': '909054016', '10': '909054015', '11': '909054017', '12': '909034014', '13': '909034003', '14': '909034001', '15': '909036009', '16': '909047001', '17': '909038005', '18': '909038011'}
MY_P_EMOTES  = {'1': '909052002', '2': '909052011', '3': '909052012', '4': '909052004', '5': '909052007', '6': '909052009', '7': '909052003', '8': '909051001', '9': '909052005', '10': '909052001', '11': '909042008', '12': '909041005', '13': '909033001', '14': '909038010', '15': '909038012', '16': '909045001', '17': '909049010', '18': '909051003', '19': '909000063', '20': '909037011', '21': '909049012', '22': '909000002', '23': '909051014', '24': '909050009', '25': '909051013', '26': '909051010', '27': '909051004', '28': '909051002', '29': '909048015', '30': '909051001', '31': '909044015', '32': '909041008', '33': '909049003', '34': '909050008', '35': '909049001', '36': '909041013', '37': '909050014', '38': '909050015', '39': '909050002', '40': '909000034', '41': '909000012', '42': '909000020', '43': '909000014', '44': '909000010', '45': '909038004', '46': '909040004', '47': '909041012', '48': '909041003', '49': '909000084', '50': '909000142', '51': '909000086', '52': '909000087', '53': '909000088', '54': '909000095', '55': '909000125', '56': '909000129', '57': '909000130', '58': '909000135', '59': '909000143', '60': '909034003', '61': '909033005', '62': '909000034', '63': '909000039', '64': '909000055', '65': '909000064', '66': '909000071', '67': '909000074', '68': '909000080', '69': '909034009', '70': '909035006', '71': '909034014', '72': '909035001', '73': '909035002', '74': '909035003', '75': '909035010', '76': '909036001', '77': '909036002', '78': '909036004', '79': '909036008', '80': '909036010', '81': '909037003', '82': '909037004', '83': '909037009', '84': '909038001', '85': '909037002', '86': '909037006', '87': '909037008', '88': '909037010', '89': '909037011', '90': '909038003', '91': '909038006', '92': '909038008', '93': '909038011', '94': '909039004', '95': '909039006', '96': '909040001', '97': '909052012', '98': '909040004', '99': '909040005', '100': '909052002'}
BAL_P_EMOTES = {'1': '909050010', '2': '909048005', '3': '909048016', '4': '909052005', '5': '909047007', '6': '909047015', '7': '909047009', '8': '909046015', '9': '909044005', '10': '909042006', '11': '909042002', '12': '909040009', '13': '909039001', '14': '909035009', '15': '909035014', '16': '909036002', '17': '909000087', '18': '909000089', '19': '909000096', '20': '909000077', '21': '909000064', '22': '909000054'}

# mode -> (table, user does emote?, bot does emote?)
#   user = /ob55 /ob54 /max      : sender only         (evo emotes)
#   sm   = @max @maxx @evos      : sender + bot mirror (evo emotes)
#   new  = new                   : sender only         (gun emotes)
#   sam  = @new                  : sender + bot mirror (gun emotes)
#   bot  = @bot                  : bot only            (bal emotes)
EVO_MODES = {
    "user": (EVO_P_EMOTES, True,  False),
    "sm":   (EVO_P_EMOTES, True,  True),
    "new":  (MY_P_EMOTES,  True,  False),
    "sam":  (MY_P_EMOTES,  True,  True),
    "bot":  (BAL_P_EMOTES, False, True),
}

async def evo_cycle_p(mode, uids, key, iv, region):
    global evo_cycle_running
    table, user_does, bot_does = EVO_MODES[mode]
    items = list(table.values())
    total = len(items)
    try:
        while evo_cycle_running:
            for idx, eid in enumerate(items):
                if not evo_cycle_running: break
                if user_does:
                    for u in uids:
                        try:
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await Emote_k(int(u), int(eid), key, iv, region))
                        except Exception as e: print(f"evo user error: {e}")
                if bot_does and bot_uid:
                    try:
                        if not user_does:   # bot-only mode: bot does its own emote first
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await Emote_k(int(bot_uid), int(eid), key, iv, region))
                        await asyncio.sleep(0.5)
                        opp = items[total - 1 - idx]
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await Emote_k(int(bot_uid), int(opp), key, iv, region))
                    except Exception as e: print(f"evo bot error: {e}")
                else:
                    await asyncio.sleep(0.5)
                for _ in range(5):
                    if not evo_cycle_running: break
                    await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass

async def start_evo_cycle(mode, uid, text, XX, chat_id, key, iv, region, label):
    """stop old cycle, start new one. extra uids may follow the command (e.g. '@max 123456789')"""
    global evo_cycle_task, evo_cycle_running
    uids = [str(uid)]
    for part in text.strip().split()[1:]:
        if part.isdigit() and len(part) >= 7 and part not in uids: uids.append(part)
    if evo_cycle_task and not evo_cycle_task.done():
        evo_cycle_running = False; evo_cycle_task.cancel(); await asyncio.sleep(0.4)
    evo_cycle_running = True
    evo_cycle_task = asyncio.create_task(evo_cycle_p(mode, uids, key, iv, region))
    await safe_send_message(XX, EVO_START_MSG.get(mode, "[B][C][FFFF00]✅ SUCCESS! Evo cycle started!  Stop: /s"), uid, chat_id, key, iv)

async def stop_evo_cycle(uid, XX, chat_id, key, iv):
    global evo_cycle_task, evo_cycle_running
    if evo_cycle_task and not evo_cycle_task.done():
        evo_cycle_running = False; evo_cycle_task.cancel()
        await safe_send_message(XX, "[B][C][00FFFF]🔥 OB55 SPECIAL EMOTE STOPPED! 🔥\n[B][C][FFFF00]✅ SUCCESS! Evolution emote cycle stopped!", uid, chat_id, key, iv)
    else:
        await safe_send_message(XX, "[B][C][FF0000]❌ ERROR! No active evolution emote cycle to stop!\n", uid, chat_id, key, iv)

# ═══════════════════════════════════════════════════════════════
# /copy  (emote hijack - bot copies every emote it sees)  ported from PERSONAL
# ═══════════════════════════════════════════════════════════════
def _ex5(pj):
    if pj.get('1') == 5:
        try:
            d = pj['2']['data']; s = d.get('1', {}).get('data'); e = d.get('4', {}).get('data')
            if s: return {'sender_uid': s, 'emote_id': e or 909054004}
        except Exception: pass
    return None

def _ex21(pj):
    if pj.get('1') == 21:
        try:
            n = pj['2']['data']['5']['data']; s = n.get('1', {}).get('data'); e = n.get('3', {}).get('data')
            if s and e: return {'sender_uid': s, 'emote_id': e}
        except Exception: pass
    return None

def _ex26(pj):
    if pj.get('1') == 26:
        try:
            d = pj['2']['data']; s = d.get('1', {}).get('data'); e = d.get('2', {}).get('data')
            if s and e: return {'sender_uid': s, 'emote_id': e}
        except Exception: pass
    return None

def _exgeneric(pj):
    found = {'uid': None, 'emote': None}
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == 'data' and isinstance(v, (int, str)) and str(v).isdigit():
                    n = int(v)
                    if 1000000 < n < 99999999999:
                        if not found['uid']: found['uid'] = n
                        elif str(v).startswith('909') and len(str(v)) >= 9: found['emote'] = n
                elif isinstance(v, (dict, list)): walk(v)
        elif isinstance(o, list):
            for i in o: walk(i)
    walk(pj)
    if found['uid']: return {'sender_uid': found['uid'], 'emote_id': found['emote'] or 909054004}
    return None

async def detect_and_hijack_emote(hex_data, key, iv, my_uid, region):
    try:
        pj = json.loads(await DeCode_PackEt(hex_data[10:]))
        info = None
        for fn in (_ex21, _ex26, _ex5, _exgeneric):
            info = fn(pj)
            if info and info.get('sender_uid'): break
        if not info or not info.get('sender_uid'): return
        if int(info['sender_uid']) == int(my_uid): return
        # only copy when it really looks like an emote id
        if not str(info['emote_id']).startswith('909'): return
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await Emote_k(int(my_uid), int(info['emote_id']), key, iv, region))
    except Exception as e:
        print(f"copy error: {e}")

# ═══════════════════════════════════════════════════════════════
# TCP CHAT HANDLER
# ═══════════════════════════════════════════════════════════════
async def TcPChaT(ip, port, AutHToKen, key, iv, ready_event, region, reconnect_delay=0.5):
    global whisper_writer, online_writer, spm_tasks, ToKen, bot_uid, bot_enabled, emote_hijack, v_dance_task
    global spam_targets, evo_cycle_running, evo_cycle_task, ban_task, ban_running, ban_targets
    global fast_spam_running, fast_spam_task, custom_spam_running, custom_spam_task
    global msg_spam_running, msg_spam_task, mg_spam_task
    global reject_spam_running, reject_spam_task, freeze_running, freeze_task
    global FULL_RESTART_REQUESTED

    print(f"📡 {region} → TCP CHAT connecting...")
    while True:
        if FULL_RESTART_REQUESTED:
            print("🔄 Full restart requested -> leaving TcPChaT so a fresh login can happen.")
            return
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen) if isinstance(AutHToKen, str) else AutHToKen
            whisper_writer.write(bytes_payload); await whisper_writer.drain()
            ready_event.set()
            print(f"✅ CHAT connected to {ip}:{port}")

            for tgt in spam_targets:
                if tgt not in spm_tasks or spm_tasks[tgt].done():
                    spm_tasks[tgt] = asyncio.create_task(spm_loop(tgt, key, iv))

            while not FULL_RESTART_REQUESTED:
                try:
                    data = await asyncio.wait_for(reader.read(9999), timeout=5)
                except asyncio.TimeoutError:
                    continue  # just re-checks FULL_RESTART_REQUESTED / loops again
                if not data: break
                if not data.hex().startswith("120000"): continue
                try:
                    response = await DecodeWhisperMessage(data.hex()[10:])
                    uid = response.Data.uid
                    chat_id = response.Data.Chat_ID
                    XX = response.Data.chat_type
                    inPuTMsG = response.Data.msg.lower()
                except Exception: continue

                command_text = inPuTMsG.strip()
                command = command_text.split()[0].split("@")[0].lower() if command_text else ""

                if not bot_enabled and command not in ("/on", "/admin", "/help", "TEAM NEXUS", "help"): continue

                # ═══════════════════════════════════════════════
                # /help & 1 (FIXED TIMING)
                # ═══════════════════════════════════════════════
                if command in ("/help", "help", "/hasib", "hasib") or command_text == "bot help":
                    # Personal-style tree menu: welcome header first, then menu pages
                    try: await safe_send_message(XX, get_welcome_header(), uid, chat_id, key, iv)
                    except Exception as e: print(f"Help header err: {e}")
                    try:
                        greet_emote = await Emote_k(int(uid), 909000010, key, iv, region)  # friendly wave/heart emote
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', greet_emote)
                    except Exception as e:
                        print(f"Help emote error: {e}")
                    await asyncio.sleep(0.3)
                    _pages = get_help_pages()
                    _arg = command_text.split()[1] if len(command_text.split()) > 1 else ""
                    if _arg.isdigit() and 1 <= int(_arg) <= len(_pages): _pages = [_pages[int(_arg) - 1]]
                    for i, page_text in enumerate(_pages):
                        try: await safe_send_message(XX, page_text, uid, chat_id, key, iv)
                        except Exception as e: print(f"Help err: {e}")
                        await asyncio.sleep(HELP_PAGE_DELAY)

                # ═══════════════════════════════════════════════
                # /admin
                # ═══════════════════════════════════════════════
                elif (_xmsg := extra_cmds.handle(command_text)) is not None:
                    await safe_send_message(XX, _xmsg, uid, chat_id, key, iv)

                elif command in ("/admin", "admin"):
                    msg = f"""[b][c]{get_random_color()} ═══ TEAM NEXUS ═══

[b][c][00FFFF]👤 Name: TEAM NEXUS
[b][c][FFFFFF]👑 Dev: {CREDIT_DEV}
[b][c][FFFFFF]✈ Telegram: {CREDIT_TG}

[b][c][FFFF00]🎮 Free Fire Mini SRC Developer
[b][c][FFFFFF]⚡ TEAM NEXUS TCP BOT

[b][c]{get_random_color()} Powered by TEAM NEXUS"""
                    await safe_send_message(XX, msg, uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # /on /off
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == '/on':
                    if str(uid) != admin_uid: await safe_send_message(XX, f"[B][C][FF0000]❌ Only admin can use /on", uid, chat_id, key, iv)
                    else: bot_enabled = True; await safe_send_message(XX, f"[B][C][00FF00]✅ Bot is now ON", uid, chat_id, key, iv)
                elif inPuTMsG.strip() == '/off':
                    if str(uid) != admin_uid: await safe_send_message(XX, f"[B][C][FF0000]❌ Only admin can use /off", uid, chat_id, key, iv)
                    else: bot_enabled = False; await safe_send_message(XX, f"[B][C][FF0000]⛔ Bot is now OFF", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # /evos & /sevos (FIXED)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/evos'):
                    if evo_cycle_task and not evo_cycle_task.done():
                        evo_cycle_running = False; evo_cycle_task.cancel(); await asyncio.sleep(0.3)
                    evo_cycle_running = True
                    evo_cycle_task = asyncio.create_task(evo_gun_cycle([str(uid)], EVO_IDS, key, iv, region))
                    await safe_send_message(XX, f"[B][C][00FF00]✅ Evo cycle started", uid, chat_id, key, iv)
                elif inPuTMsG.strip() == '/sevos':
                    if evo_cycle_task and not evo_cycle_task.done():
                        evo_cycle_running = False; evo_cycle_task.cancel()
                        await safe_send_message(XX, f"[B][C][00FF00]✅ Evo cycle stopped", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # /e EMOTE (FIXED to use singele_emote.json)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/e '):
                    parts = inPuTMsG.strip().split()
                    try:
                        if len(parts) < 2: continue
                        last = parts[-1].lower()
                        is_num = last.isdigit() and (int(last) in SINGLE_EMOTES_MAP or last in GENERAL_EMOTES_MAP)
                        is_name = last in NAME_EMOTES
                        if not (is_num or is_name):
                            await safe_send_message(XX, f"[B][C][FF0000]❌ Emote '{last}' not found", uid, chat_id, key, iv)
                            continue
                        tgt_uids = []
                        if len(parts) == 2: tgt_uids.append(int(uid))
                        else:
                            for p in parts[1:-1]:
                                if p.isdigit(): tgt_uids.append(int(p))
                        emote_id = (SINGLE_EMOTES_MAP.get(int(last)) or GENERAL_EMOTES_MAP.get(last)) if is_num else NAME_EMOTES.get(last)
                        sc = 0
                        for t in tgt_uids:
                            try:
                                H = await Emote_k(t, int(emote_id), key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                sc += 1
                                await asyncio.sleep(0.1)
                            except Exception: pass
                        if sc > 0:
                            await safe_send_message(XX, f"[B][C][00FF00]✅ Emote sent to {sc} player(s)", uid, chat_id, key, iv)
                    except Exception as e: print(f"E cmd error: {e}")

                # ═══════════════════════════════════════════════
                # /evo
                # ═══════════════════════════════════════════════
                elif inPuTMsG.startswith('/evo ') and not inPuTMsG.startswith('/evos'):
                    parts = inPuTMsG.strip().split()
                    try:
                        num = None; uids_l = []
                        for p in parts[1:]:
                            if p.isdigit():
                                if len(p) <= 2 and num is None: num = p
                                else: uids_l.append(p)
                        if not num or not uids_l:
                            await safe_send_message(XX, f"[B][C][FF0000]Usage: /evo <uid> <1-21>", uid, chat_id, key, iv)
                            continue
                        num_i = int(num)
                        if num_i not in EMOTE_MAP:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ Number must be 1-21", uid, chat_id, key, iv)
                            continue
                        emote_id = EMOTE_MAP[num_i]
                        for t in uids_l:
                            try:
                                H = await Emote_k(int(t), int(emote_id), key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                await asyncio.sleep(0.1)
                            except Exception: pass
                        await safe_send_message(XX, f"[B][C][00FF00]✅ Evo emote {num_i} sent", uid, chat_id, key, iv)
                    except Exception as e: print(f"Evo error: {e}")

                # ═══════════════════════════════════════════════
                # SHARE CARDS: .s1-.s8, .s11 (group/room/clan/HUD/
                # title/discount share), .t1 (title share)
                # ═══════════════════════════════════════════════
                elif command_text in (".s1", ".s2", ".s3", ".s4", ".s5", ".s6", ".s7", ".s8", ".s11", ".t1"):
                    key_name = command_text[1:]
                    ok = await send_share_card(key_name, uid, chat_id, XX, key, iv)
                    if not ok:
                        await safe_send_message(XX, "[B][C][FF0000]❌ Share card failed to send.", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # .r / /restart — owner-only: go offline, then the
                # existing reconnect loop brings the bot back online
                # automatically (reconnect_delay seconds later).
                # ═══════════════════════════════════════════════
                # ═══════════════════════════════════════════════
                # /pc, /phone — owner-only: switch the login device
                # profile (cosmetic only: PC/phone icon next to the
                # account), then restart so it takes effect.
                # ═══════════════════════════════════════════════
                elif command_text in ("/pc", "/phone"):
                    if str(uid) != admin_uid:
                        await safe_send_message(XX, "[B][C][FF0000]❌ Only admin can use /pc or /phone", uid, chat_id, key, iv)
                    else:
                        mode = "pc" if command_text == "/pc" else "phone"
                        login_engine.set_platform_mode(mode)
                        await safe_send_message(
                            XX,
                            f"[B][C][FFFF00]✅ Login mode saved as {mode.upper()}! Doing a FULL relogin now "
                            f"(not just a reconnect) — going offline briefly, then back online with the {mode.upper()} icon.",
                            uid, chat_id, key, iv)
                        FULL_RESTART_REQUESTED = True
                        try:
                            if whisper_writer: whisper_writer.close()
                        except Exception: pass
                        try:
                            if online_writer: online_writer.close()
                        except Exception: pass

                elif command_text in (".r", "/restart"):
                    if str(uid) != admin_uid:
                        await safe_send_message(XX, "[B][C][FF0000]❌ Only admin can use /restart", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, "[B][C][FFFF00]✅ Restarting bot... going offline, full relogin, then back online shortly.", uid, chat_id, key, iv)
                        FULL_RESTART_REQUESTED = True
                        try:
                            if whisper_writer: whisper_writer.close()
                        except Exception: pass
                        try:
                            if online_writer: online_writer.close()
                        except Exception: pass

                # ═══════════════════════════════════════════════
                # /display_msg, /display_msg_off — owner-only: swap
                # the active xC4.py for xC4_1.py / xC4_2.py and do a
                # FULL restart so the swapped code is actually loaded
                # (Python caches imports, so only a process-level
                # relogin picks up a changed xC4.py). Both files start
                # as plain copies of the current xC4.py — edit either
                # one yourself to make the swap do something different.
                # ═══════════════════════════════════════════════
                elif command_text in ("/display_msg", "/display_msg_off"):
                    if str(uid) != admin_uid:
                        await safe_send_message(XX, "[B][C][FF0000]❌ Only admin can use /display_msg", uid, chat_id, key, iv)
                    else:
                        src = "xC4_1.py" if command_text == "/display_msg" else "xC4_2.py"
                        label = "xC4_1.py (new)" if command_text == "/display_msg" else "xC4_2.py (old)"
                        try:
                            import shutil
                            if not os.path.exists(src):
                                shutil.copyfile("xC4.py", src)  # first-time safety copy
                            shutil.copyfile(src, "xC4.py")
                            await safe_send_message(
                                XX,
                                f"[B][C][FFFF00]✅ Switched active code to {label}.\n"
                                f"[FFFFFF]Going offline for a full restart so the new xC4.py actually loads...",
                                uid, chat_id, key, iv)
                            FULL_RESTART_REQUESTED = True
                            try:
                                if whisper_writer: whisper_writer.close()
                            except Exception: pass
                            try:
                                if online_writer: online_writer.close()
                            except Exception: pass
                        except Exception as e:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ Swap failed: {str(e)[:120]}", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # /name [text] — 3 big bordered name banners
                # (green, red, multi-colour), fullwidth stylised text
                # ═══════════════════════════════════════════════
                elif command_text.startswith('/name '):
                    raw_name = inPuTMsG.strip().split(maxsplit=1)[1][:20]
                    def _fullwidth(s):
                        out = []
                        for ch in s.upper():
                            if ch == ' ':
                                out.append('　')
                            elif 0x21 <= ord(ch) <= 0x7E:
                                out.append(chr(ord(ch) + 0xFEE0))
                            else:
                                out.append(ch)
                        return ''.join(out)
                    big = _fullwidth(raw_name)
                    bar = "═" * (len(raw_name) + 6)
                    green_banner = f"[B][C][00FF00]╔{bar}╗\n[00FF00]║   {big}   ║\n[00FF00]╚{bar}╝"
                    red_banner = f"[B][C][FF0000]╔{bar}╗\n[FF0000]║   {big}   ║\n[FF0000]╚{bar}╝"
                    multi_colors = ["FF0000", "FFA500", "FFFF00", "00FF00", "00FFFF", "FF00FF"]
                    multi_name = ''.join(f"[{multi_colors[i % len(multi_colors)]}]{c}" for i, c in enumerate(big))
                    multi_banner = f"[B][C][FFD700]╔{bar}╗\n[FFD700]║   {multi_name}[FFD700]   ║\n[FFD700]╚{bar}╝"
                    await safe_send_message(XX, green_banner, uid, chat_id, key, iv)
                    await asyncio.sleep(1)
                    await safe_send_message(XX, red_banner, uid, chat_id, key, iv)
                    await asyncio.sleep(1)
                    await safe_send_message(XX, multi_banner, uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # /dance [uid2] [uid3] [uid4] — 8-emote dance sequence,
                # 8s apart, for sender (+ optional extra consenting
                # teammates whose UIDs are given). /dance stop cancels.
                # ═══════════════════════════════════════════════
                elif command_text == '/dance stop':
                    if v_dance_task and not v_dance_task.done():
                        v_dance_task.cancel()
                        await safe_send_message(XX, "[B][C][FF0000]🛑 Dance stopped!", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, "[B][C][FF0000]❌ No active dance to stop!", uid, chat_id, key, iv)

                elif command_text.startswith('/dance'):
                    parts = command_text.split()
                    target_uids = [str(uid)]
                    for p in parts[1:5]:
                        if p.isdigit():
                            target_uids.append(p)
                    if v_dance_task and not v_dance_task.done():
                        v_dance_task.cancel()
                    init_msg = f"[B][C][00FFFF]🔥 ＶＩＰ ＤＡＮＣＥ ＳＴＡＲＴＥＤ 🔥\n[FFFFFF]প্লেয়ার: {len(target_uids)} জন\nইমোট: ৮টি (৮ সেকেন্ড পর পর)\n[FF0000]থামাতে লিখুন: /as"
                    await safe_send_message(XX, init_msg, uid, chat_id, key, iv)

                    async def _v_dance_sequence(uids_list, sender_uid, c_id, c_type, k, v, rgn):
                        try:
                            emotes = [909000137, 909041014, 909038004, 909037009, 909035006, 909000135, 909042001, 909040005]
                            for i in range(8):
                                for t_uid in uids_list:
                                    try:
                                        ep = await Emote_k(int(t_uid), int(emotes[i]), k, v, rgn)
                                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', ep)
                                    except Exception as e:
                                        print(f"Dance emote error for {t_uid}: {e}")
                                if i < 7:
                                    await asyncio.sleep(8.0)
                            await safe_send_message(c_type, "[B][C][00FF00]✅ VIP DANCE COMPLETED! 🕺", sender_uid, c_id, k, v)
                        except asyncio.CancelledError:
                            await safe_send_message(c_type, "[B][C][FF0000]🛑 VIP DANCE মাঝপথে থামানো হয়েছে!", sender_uid, c_id, k, v)

                    v_dance_task = asyncio.create_task(_v_dance_sequence(target_uids, uid, chat_id, XX, key, iv, region))

                elif command_text in ('/as', '/dance stop'):
                    if v_dance_task and not v_dance_task.done():
                        v_dance_task.cancel()
                    else:
                        await safe_send_message(XX, "[B][C][FF0000]❌ কোনো V-Dance চালু নেই!", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # /spin — lucky spin, random fun outcome text
                # ═══════════════════════════════════════════════
                elif command_text == '/spin':
                    await safe_send_message(XX, "[B][C][00FFFF]🎰 Spinning the wheel of luck... 🌪️", uid, chat_id, key, iv)

                    async def _send_spin_result(c_type, t_uid, c_id, k, v):
                        await asyncio.sleep(2)
                        outcomes = [
                            "[00FF00]🎁 10,000 Diamonds! [FFFFFF](in your dreams — gone when you wake up!) 🤣",
                            "[FF0000]💩 1 Gold Coin! [FFFFFF]That's the poor man's luck for you! 🪙",
                            "[00FFFF]🔥 Max Evo Gun! [FFFFFF](Today you're hacker-level pro!) 🔫",
                            "[FFFF00]🤡 Default Character! [FFFFFF](Your true form, accept it!) 🧍",
                            "[FFD700]👑 V-Badge! [FFFFFF](Garena thinks you're a YouTuber now!) ✅",
                            "[32CD32]🛡️ Unlimited Gloo Walls! [FFFFFF](Today you camp, not rush!) 🧱",
                            "[FFA500]🍗 Free Chicken Dinner! [FFFFFF](Today is YOUR day!) 🏆",
                        ]
                        result = random.choice(outcomes)
                        msg = f"[B][C][FFD700]🎰 LUCKY SPIN 🎰\n[FFFFFF]──────────────────────\n{result}\n[FFFFFF]──────────────────────"
                        await safe_send_message(c_type, msg, t_uid, c_id, k, v)

                    asyncio.create_task(_send_spin_result(XX, uid, chat_id, key, iv))

                # ═══════════════════════════════════════════════
                # 20 NEW UTILITY/FUN COMMANDS (batch 1)
                # ═══════════════════════════════════════════════
                elif command_text.startswith('/password'):
                    parts = command_text.split()
                    length = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 12
                    length = max(6, min(length, 64))
                    chars = _string.ascii_letters + _string.digits + "!@#$%&*"
                    pw = ''.join(random.choice(chars) for _ in range(length))
                    await safe_send_message(XX, f"[B][C][00FF00]🔐 Generated Password ({length} chars):\n[FFFF00]{pw}", uid, chat_id, key, iv)

                elif command_text.startswith('/bmi '):
                    p = command_text.split()
                    if len(p) < 3:
                        await safe_send_message(XX, "[B][C][FF8C00]Usage: /bmi <kg> <meters>\nExample: /bmi 70 1.75", uid, chat_id, key, iv)
                    else:
                        try:
                            w, h = float(p[1]), float(p[2])
                            bmi = w / (h * h)
                            cat = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
                            await safe_send_message(XX, f"[B][C][00BFFF]⚖️ BMI: [FFFF00]{bmi:.1f}[FFFFFF] — {cat}", uid, chat_id, key, iv)
                        except Exception:
                            await safe_send_message(XX, "[B][C][FF0000]❌ Invalid numbers.", uid, chat_id, key, iv)

                elif command_text.startswith('/age '):
                    p = command_text.split()
                    if len(p) < 2 or not p[1].isdigit():
                        await safe_send_message(XX, "[B][C][FF8C00]Usage: /age <birth_year>", uid, chat_id, key, iv)
                    else:
                        from datetime import datetime as _dt
                        yr = int(p[1])
                        age = _dt.now().year - yr
                        await safe_send_message(XX, f"[B][C][00FF00]🎂 You are approximately {age} years old!", uid, chat_id, key, iv)

                elif command_text.startswith('/dice'):
                    p = command_text.split()
                    spec = p[1] if len(p) > 1 else "1d6"
                    try:
                        n, sides = spec.lower().split('d')
                        n, sides = max(1, min(int(n), 20)), max(2, min(int(sides), 1000))
                        rolls = [random.randint(1, sides) for _ in range(n)]
                        await safe_send_message(XX, f"[B][C][FFD700]🎲 Rolled {spec}: {rolls} = {sum(rolls)}", uid, chat_id, key, iv)
                    except Exception:
                        await safe_send_message(XX, "[B][C][FF8C00]Usage: /dice 2d6", uid, chat_id, key, iv)

                elif command_text.startswith('/reverse '):
                    txt = inPuTMsG.strip().split(maxsplit=1)[1]
                    await safe_send_message(XX, f"[B][C][00FFFF]🔁 {txt[::-1]}", uid, chat_id, key, iv)

                elif command_text.startswith('/count '):
                    txt = inPuTMsG.strip().split(maxsplit=1)[1]
                    await safe_send_message(XX, f"[B][C][00BFFF]📊 Chars: {len(txt)} | Words: {len(txt.split())}", uid, chat_id, key, iv)

                elif command_text.startswith('/anagram '):
                    word = inPuTMsG.strip().split(maxsplit=1)[1]
                    letters = list(word)
                    random.shuffle(letters)
                    await safe_send_message(XX, f"[B][C][FF69B4]🔀 {''.join(letters)}", uid, chat_id, key, iv)

                elif command_text.startswith('/binary '):
                    txt = inPuTMsG.strip().split(maxsplit=1)[1]
                    b_out = ' '.join(format(ord(c), '08b') for c in txt)
                    await safe_send_message(XX, f"[B][C][00FF00]💻 {b_out}", uid, chat_id, key, iv)

                elif command_text.startswith('/morse '):
                    txt = inPuTMsG.strip().split(maxsplit=1)[1].upper()
                    m_out = ' '.join(MORSE_MAP.get(c, '?') for c in txt)
                    await safe_send_message(XX, f"[B][C][FFD700]📡 {m_out}", uid, chat_id, key, iv)

                elif command_text.startswith('/leet '):
                    txt = inPuTMsG.strip().split(maxsplit=1)[1]
                    await safe_send_message(XX, f"[B][C][32CD32]🅻 {txt.translate(LEET_MAP)}", uid, chat_id, key, iv)

                elif command_text.startswith('/rot13 '):
                    txt = inPuTMsG.strip().split(maxsplit=1)[1]
                    rot = _string.ascii_lowercase[13:] + _string.ascii_lowercase[:13]
                    ROT = _string.ascii_uppercase[13:] + _string.ascii_uppercase[:13]
                    table = str.maketrans(_string.ascii_lowercase + _string.ascii_uppercase, rot + ROT)
                    await safe_send_message(XX, f"[B][C][FF00FF]🔐 {txt.translate(table)}", uid, chat_id, key, iv)

                elif command_text.startswith('/percent '):
                    p = command_text.split()
                    if len(p) < 4 or p[2] != "of":
                        await safe_send_message(XX, "[B][C][FF8C00]Usage: /percent <x> of <y>\nExample: /percent 20 of 150", uid, chat_id, key, iv)
                    else:
                        try:
                            x, y = float(p[1]), float(p[3])
                            await safe_send_message(XX, f"[B][C][00BFFF]📐 {x}% of {y} = {x/100*y:.2f}", uid, chat_id, key, iv)
                        except Exception:
                            await safe_send_message(XX, "[B][C][FF0000]❌ Invalid numbers.", uid, chat_id, key, iv)

                elif command_text.startswith('/pick '):
                    opts = inPuTMsG.strip().split(maxsplit=1)[1].split(',')
                    opts = [o.strip() for o in opts if o.strip()]
                    if len(opts) < 2:
                        await safe_send_message(XX, "[B][C][FF8C00]Usage: /pick option1, option2, option3", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, f"[B][C][FFD700]🎯 I pick: {random.choice(opts)}", uid, chat_id, key, iv)

                elif command_text == '/yesno':
                    await safe_send_message(XX, f"[B][C][00FFFF]🔮 {random.choice(['Yes ✅', 'No ❌', 'Maybe 🤔', 'Ask again later 🔁'])}", uid, chat_id, key, iv)

                elif command_text.startswith('/compliment'):
                    p = command_text.split(maxsplit=1)
                    name = p[1] if len(p) > 1 else "তুমি"
                    await safe_send_message(XX, f"[B][C][FF69B4]{name}, {random.choice(COMPLIMENTS)}", uid, chat_id, key, iv)

                elif command_text == '/fact':
                    await safe_send_message(XX, f"[B][C][00FF00]💡 {random.choice(FUN_FACTS)}", uid, chat_id, key, iv)

                elif command_text == '/namegen':
                    await safe_send_message(XX, f"[B][C][FFD700]🎲 Random Name: {random.choice(RANDOM_NAMES)}", uid, chat_id, key, iv)

                elif command_text.startswith('/color'):
                    hexcol = f"{random.randint(0,255):02X}{random.randint(0,255):02X}{random.randint(0,255):02X}"
                    await safe_send_message(XX, f"[B][C][{hexcol}]🎨 Random Color: #{hexcol}", uid, chat_id, key, iv)

                elif command_text.startswith('/define '):
                    word = inPuTMsG.strip().split(maxsplit=1)[1]
                    result = await fetch_word_definition(word)
                    if result:
                        pos, definition = result
                        await safe_send_message(XX, f"[B][C][00BFFF]📖 {word} [FFFFFF]({pos})\n[FFD700]{definition}", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, "[B][C][FF0000]❌ No definition found.", uid, chat_id, key, iv)

                elif command_text == '/chucknorris':
                    joke = await fetch_chuck_joke()
                    await safe_send_message(XX, f"[B][C][FF4500]😂 {joke}" if joke else "[B][C][FF0000]❌ Could not fetch joke.", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # /translet <lang> <text>  -> en/bn/hi/ar/zh-CN
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/translet '):
                    tparts = inPuTMsG.strip().split(maxsplit=2)
                    if len(tparts) < 3 or tparts[1].lower() not in ("bn", "en", "hi", "ar", "zh", "zh-cn"):
                        usage = ("[B][C][FF8C00]❌ Usage: /translet <lang> <text>\n"
                                 "[FFFFFF]lang: [FFD700]bn[FFFFFF]=Bangla  [FFD700]en[FFFFFF]=English  "
                                 "[FFD700]hi[FFFFFF]=Hindi  [FFD700]ar[FFFFFF]=Arabic  [FFD700]zh[FFFFFF]=Chinese\n"
                                 "Example: /translet bn how are you")
                        await safe_send_message(XX, usage, uid, chat_id, key, iv)
                    else:
                        target = tparts[1].lower()
                        target = "zh-CN" if target in ("zh", "zh-cn") else target
                        text_in = tparts[2]
                        src, translated, err = await fetch_translation(text_in, target)
                        if err:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ Translate failed: {err}", uid, chat_id, key, iv)
                        else:
                            src_name = LANG_NAMES.get(src, src)
                            dst_name = LANG_NAMES.get(target, target)
                            out = f"""[B][C][00BFFF]◉[FFD700]━[FF69B4]◉
[C][B][00FFFF]{src_name} ➤ {dst_name}
[C][B][FF00FF]━━━━━━━━━━━
[C][B][FFFFFF]{translated}
[C][B][00FFFF]━━━━━━━━━━━"""
                            await safe_send_message(XX, out, uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # SOCIAL LOOKUP: /tt (TikTok), /yt (YouTube)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/tt '):
                    uname = inPuTMsG.strip().split(maxsplit=1)[1].strip() if len(inPuTMsG.strip().split()) > 1 else ""
                    if not uname:
                        await safe_send_message(XX, "[B][C][FF8C00]❌ ERROR! Usage: /tt <username>\nExample: /tt virat.kohli\n", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, f"[B][C]{get_random_color()}\nFetching TikTok info for {uname}...\n", uid, chat_id, key, iv)
                        result = await fetch_tiktok_info(uname)
                        await safe_send_message(XX, result, uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/yt '):
                    channel = inPuTMsG.strip().split(maxsplit=1)[1].strip() if len(inPuTMsG.strip().split()) > 1 else ""
                    if not channel:
                        await safe_send_message(XX, "[B][C][FF8C00]❌ ERROR! Usage: /yt <channel>\nExample: /yt HasibCodex\n", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, f"[B][C]{get_random_color()}\nFetching YouTube info for {channel}...\n", uid, chat_id, key, iv)
                        main_info, description = await fetch_youtube_info(channel)
                        await safe_send_message(XX, main_info, uid, chat_id, key, iv)
                        if description:
                            await asyncio.sleep(0.2)
                            await safe_send_message(XX, f"[B][C][00BFFF]Description: {description}", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # INFO (smt-info-api fixed)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/info '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        await safe_send_message(XX, f"[B][C][FFFF00]🔍 Fetching info for {parts[1]}...", uid, chat_id, key, iv)
                        ok, data = await get_player_info(parts[1])
                        if ok:
                            msgs = format_player_info(data)
                            for m in msgs:
                                P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                await asyncio.sleep(2)
                        else:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ {data}", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, f"[B][C][FF0000]Usage: /info <uid>", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # OTHER COMMANDS
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/check '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        ok, result = await check_banned(parts[1])
                        reply = format_check_result(result) if ok else f"[B][C][FF0000]❌ {result}"
                        P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    else: await safe_send_message(XX, f"[B][C][FF0000]Usage: /check <uid>", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/mth'):
                    parts = inPuTMsG.strip().split(maxsplit=1)
                    if len(parts) < 2: await safe_send_message(XX, f"[B][C][FFFF00]Usage: /mth 2+2", uid, chat_id, key, iv)
                    else:
                        expr = parts[1].strip().replace("×", "*").replace("÷", "/").replace("x", "*")
                        try:
                            import re as _re
                            if not _re.match(r'^[\d\s\+\-\*\/\.\(\)\%]+$', expr): raise ValueError("Invalid expression")
                            result = eval(expr)
                            if isinstance(result, float) and result == int(result): result = int(result)
                            P = await SEndMsG(XX, f"[B][C][00FFFF]🧮 Calculator\n\n[FFFF00]Expression: [FFFFFF]{expr}\n[00FF00]Result: [FFFFFF]{result}", uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                        except ZeroDivisionError: await safe_send_message(XX, f"[B][C][FF0000]❌ Division by zero", uid, chat_id, key, iv)
                        except Exception: await safe_send_message(XX, f"[B][C][FF0000]❌ Invalid expression", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith("/add ") and str(uid) == admin_uid:
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            ok, msg = await send_friend_request(parts[1], ToKen, region)
                            reply = f"[B][C]{get_random_color()} {msg}"
                        except Exception as e: reply = f"[B][C][FF0000]Error: {e}"
                    else: reply = f"[B][C][FF0000]Usage: /add <uid>"
                    P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith("/remove ") and str(uid) == admin_uid:
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        try:
                            ok, msg = await remove_friend(parts[1], ToKen, region)
                            reply = f"[B][C]{get_random_color()} {msg}"
                        except Exception as e: reply = f"[B][C][FF0000]Error: {e}"
                    else: reply = f"[B][C][FF0000]Usage: /remove <uid>"
                    P = await SEndMsG(XX, reply, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/join '):
                    try:
                        code = inPuTMsG.split('/join ')[1].strip()
                        EM = await JoinSq_original(code, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                        await safe_send_message(XX, f"[B][C]{get_random_color()}\n✅ Joined squad: {code}", uid, chat_id, key, iv)
                    except Exception as e: print(f"Join error: {e}")

                elif inPuTMsG.startswith('/exit') or inPuTMsG.startswith('/leave'):
                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(uid, key, iv))
                    await safe_send_message(XX, f"[B][C]{get_random_color()}\n✅ Left squad", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/5') and not inPuTMsG.startswith('/50'):
                    try:
                        # ported from TEAM NEXUS PERSONAL (old OB55 /5 was not working)
                        await safe_send_message(XX, f"[B][C]{get_random_color()}\n\nSending Group Invitation...\n\n", uid, chat_id, key, iv)
                        PAc = await OpEnSq_P(key, iv, region)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
                        C = await cHSq_P(5, uid, key, iv, region)
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', C)
                        V = await SEnd_InV_P(5, uid, key, iv, region)
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
                        E = await ExiT(None, key, iv)
                        await asyncio.sleep(3.5)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                        await safe_send_message(XX, f"[B][C][FFFF00]✅ SUCCESS! Group invitation sent successfully to {uid}!\n", uid, chat_id, key, iv)
                    except Exception as e: print(f"Team5 error: {e}")

                elif inPuTMsG.startswith('/6'):
                    try:
                        await safe_send_message(XX, f"[B][C]{get_random_color()}\n\nCreating 6-man team...\n", uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await OpEnSq_P(key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await cHSq_P(6, uid, key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await SEnd_InV_P(6, uid, key, iv, region))
                        await asyncio.sleep(3.5)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
                        await safe_send_message(XX, f"[B][C][00FF00]✅ 6-man team invitation sent!", uid, chat_id, key, iv)
                    except Exception as e: print(f"Team6 error: {e}")

                elif inPuTMsG.startswith('/3') and not inPuTMsG.startswith('/30'):
                    try:
                        await safe_send_message(XX, f"[B][C]{get_random_color()}\n\nCreating 3-man team...\n", uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await OpEnSq_P(key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await cHSq_P(3, uid, key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await SEnd_InV_P(3, uid, key, iv, region))
                        await asyncio.sleep(3.5)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
                        await safe_send_message(XX, f"[B][C][00FF00]✅ 3-man team invitation sent!", uid, chat_id, key, iv)
                    except Exception as e: print(f"Team3 error: {e}")

                elif inPuTMsG.startswith('/4'):
                    try:
                        await safe_send_message(XX, f"[B][C]{get_random_color()}\n\nCreating 4-man team...\n", uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await OpEnSq_P(key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await cHSq_P(4, uid, key, iv, region))
                        await asyncio.sleep(0.3)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await SEnd_InV_P(4, uid, key, iv, region))
                        await asyncio.sleep(3.5)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
                        await safe_send_message(XX, f"[B][C][00FF00]✅ 4-man team invitation sent!", uid, chat_id, key, iv)
                    except Exception as e: print(f"Team4 error: {e}")

                elif inPuTMsG.startswith('/spm '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        tgt = parts[1]
                        if tgt in spm_tasks: spm_tasks[tgt].cancel()
                        spam_targets.add(tgt); save_spam_targets()
                        spm_tasks[tgt] = asyncio.create_task(spm_loop(tgt, key, iv))
                        await safe_send_message(XX, f"[B][C][00FF00]✅ Spam started for {tgt}", uid, chat_id, key, iv)
                    else: await safe_send_message(XX, f"[B][C][FF0000]Usage: /spm <uid>", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/stp '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1] in spm_tasks:
                        spm_tasks[parts[1]].cancel(); del spm_tasks[parts[1]]
                        if parts[1] in spam_targets: spam_targets.remove(parts[1]); save_spam_targets()
                        await safe_send_message(XX, f"[B][C][00FF00]✅ Spam stopped", uid, chat_id, key, iv)
                    else: await safe_send_message(XX, f"[B][C][FF0000]❌ No active spam", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/gh '):
                    parts = inPuTMsG.split(' ', 2)
                    if len(parts) >= 3 and bot_uid is not None:
                        teamcode = parts[1].strip(); name = parts[2].strip()
                        try:
                            pending_ghost_future = asyncio.Future()
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await JoinSq_original(teamcode, key, iv))
                            try: await asyncio.wait_for(pending_ghost_future, timeout=8.0)
                            except asyncio.TimeoutError:
                                await safe_send_message(XX, f"[B][C][FF0000]❌ No response", uid, chat_id, key, iv)
                                pending_ghost_future = None; continue
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await ExiT(None, key, iv))
                            await asyncio.sleep(0.2)
                            for _ in range(4):
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', await GhostPakcet(ghost_team_id, name, ghost_squad_code, key, iv))
                                await asyncio.sleep(0.1)
                            await safe_send_message(XX, f"[B][C][00FF00]✅ Ghost joined as {name}", uid, chat_id, key, iv)
                            pending_ghost_future = None
                        except Exception as e:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ {e}", uid, chat_id, key, iv)
                            pending_ghost_future = None

                elif inPuTMsG.startswith('/msg '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) < 3: await safe_send_message(XX, f"[B][C][FF0000]Usage: /msg <text> <times>", uid, chat_id, key, iv)
                    else:
                        try:
                            times = int(parts[-1]); message = ' '.join(parts[1:-1])
                            if msg_spam_task and not msg_spam_task.done():
                                msg_spam_running = False; msg_spam_task.cancel(); await asyncio.sleep(0.1)
                            msg_spam_running = True
                            msg_spam_task = asyncio.create_task(msg_spam_loop(message, times, chat_id, key, iv, region))
                            await safe_send_message(XX, f"[B][C][00FF00]✅ Sending {times}x: {message}", uid, chat_id, key, iv)
                        except ValueError: await safe_send_message(XX, f"[B][C][FF0000]Usage: /msg <text> <times>", uid, chat_id, key, iv)

                elif inPuTMsG.strip() == '/stop msg':
                    if msg_spam_task and not msg_spam_task.done():
                        msg_spam_running = False; msg_spam_task.cancel()
                        await safe_send_message(XX, f"[B][C][00FF00]✅ Msg spam stopped", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/mg '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) < 2: await safe_send_message(XX, f"[B][C][FF0000]Usage: /mg <text> [repeats]", uid, chat_id, key, iv)
                    else:
                        try:
                            message = parts[1]; repeats = int(parts[2]) if len(parts) > 2 else 5
                            if repeats > 10: repeats = 10
                            if mg_spam_task and not mg_spam_task.done():
                                msg_spam_running = False; mg_spam_task.cancel(); await asyncio.sleep(0.1)
                            msg_spam_running = True
                            mg_spam_task = asyncio.create_task(send_wave_messages(message, repeats, chat_id, key, iv, region))
                            await safe_send_message(XX, f"[B][C][00FF00]✅ Wave started: {message} x{repeats}", uid, chat_id, key, iv)
                        except ValueError: await safe_send_message(XX, f"[B][C][FF0000]Usage: /mg <text> [repeats]", uid, chat_id, key, iv)

                elif inPuTMsG.strip() in ('/ban stop', '/unban'):
                    if ban_task and not ban_task.done():
                        ban_running = False; ban_task.cancel(); ban_targets.clear()
                        await safe_send_message(XX, "[B][C][00FF00]✅ Ban spam stopped", uid, chat_id, key, iv)
                    else:
                        await safe_send_message(XX, "[B][C][FF0000]❌ No active ban spam to stop!", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/ban '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        if parts[1] in ban_targets:
                            await safe_send_message(XX, f"[B][C][FF8C00]⏳ {parts[1]} is already being ban-spammed!\nStop: /ban stop", uid, chat_id, key, iv)
                        else:
                            if len(ban_targets) >= 3:
                                await safe_send_message(XX, "[B][C][FF0000]❌ Max 3 targets at once! Use /ban stop first.", uid, chat_id, key, iv)
                            else:
                                ban_targets.add(parts[1])
                                if not (ban_task and not ban_task.done()):
                                    ban_task = asyncio.create_task(ban_loop(key, iv))
                                await safe_send_message(XX, f"[B][C][00FF00]✅ Ban spam started on {parts[1]}\n[FFFFFF]Targets: {len(ban_targets)}  Stop: [FFD700]/ban stop", uid, chat_id, key, iv)
                    else: await safe_send_message(XX, "[B][C][FF0000]Usage: /ban <uid>\n[FFFFFF]Stop: /ban stop", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/reject '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        if reject_spam_task and not reject_spam_task.done():
                            reject_spam_running = False; reject_spam_task.cancel(); await asyncio.sleep(0.3)
                        await safe_send_message(XX, f"[B][C][FFFF00]🌀 Reject spam started on {parts[1]}", uid, chat_id, key, iv)
                        reject_spam_running = True
                        reject_spam_task = asyncio.create_task(reject_spam_loop(parts[1], key, iv))
                    else: await safe_send_message(XX, f"[B][C][FF0000]Usage: /reject <uid>", uid, chat_id, key, iv)

                elif inPuTMsG.strip() == '/reject_stop':
                    if reject_spam_task and not reject_spam_task.done():
                        reject_spam_running = False; reject_spam_task.cancel()
                        await safe_send_message(XX, f"[B][C][00FF00]✅ Reject spam stopped", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/fast '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 3:
                        uids = []; emote_id = None
                        for p in parts[1:]:
                            if p.isdigit():
                                if len(p) > 3: uids.append(p)
                                else: emote_id = p
                        if uids and emote_id:
                            if fast_spam_task and not fast_spam_task.done():
                                fast_spam_running = False; fast_spam_task.cancel()
                            fast_spam_running = True
                            fast_spam_task = asyncio.create_task(fast_emote_spam(uids, emote_id, key, iv, region))
                            await safe_send_message(XX, f"[B][C][00FF00]✅ Fast spam started", uid, chat_id, key, iv)

                elif inPuTMsG.startswith('/p '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 4:
                        try:
                            tgt = parts[1]; emote_id = parts[2]; times = int(parts[3])
                            if times > 100: times = 100
                            if custom_spam_task and not custom_spam_task.done():
                                custom_spam_running = False; custom_spam_task.cancel(); await asyncio.sleep(0.2)
                            custom_spam_running = True
                            custom_spam_task = asyncio.create_task(custom_emote_spam(tgt, emote_id, times, key, iv, region))
                            await safe_send_message(XX, f"[B][C][00FF00]✅ Custom spam started: {emote_id} x{times}", uid, chat_id, key, iv)
                        except ValueError: await safe_send_message(XX, f"[B][C][FF0000]Usage: /p <uid> <emote> <times>", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/title') or inPuTMsG.strip().startswith('/alltitles'):
                    titles_list = [905090075, 904990072, 904990069, 905190079, 904090014, 904090015, 904090024, 904090025, 904090026, 904090027, 904990070, 904990071]
                    await safe_send_message(XX, f"[B][C][FFFF00]🎖️ Sending {len(titles_list)} titles...", uid, chat_id, key, iv)
                    for tid in titles_list:
                        try:
                            pkt = await convert_kyro_to_your_system(int(uid), chat_id, key, iv, nickname="TEAM NEXUS", title_id=tid)
                            if pkt and whisper_writer:
                                whisper_writer.write(pkt); await whisper_writer.drain()
                            await asyncio.sleep(2)
                        except Exception as e: print(f"Title error: {e}")
                    await safe_send_message(XX, f"[B][C][00FF00]✅ All titles sent!", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/animation'):
                    parts = inPuTMsG.strip().split()
                    anim_ids = {"1": 914000002, "2": 914000003, "3": 914038001, "4": 914039001, "5": 914042001, "6": 914044001, "7": 914047001, "8": 914047002, "9": 914048001, "10": 914050001, "11": 914051001, "12": 914053001}
                    if len(parts) < 2:
                        lst = "1-rampage\n2-cannibal\n3-devil\n4-scorpio\n5-frostfire\n6-paradox\n7-naruto\n8-aurora\n9-midnight\n10-itachi\n11-dreamspace\n12-eclipse"
                        await safe_send_message(XX, f"[B][C][FFFF00]Animations:\n{lst}", uid, chat_id, key, iv)
                    elif parts[1] in anim_ids:
                        try:
                            pkt = await animation_packet(anim_ids[parts[1]], key, iv)
                            if pkt and online_writer:
                                online_writer.write(pkt); await online_writer.drain()
                            await safe_send_message(XX, f"[B][C][00FF00]✅ Animation {parts[1]} sent!", uid, chat_id, key, iv)
                        except Exception as e: print(f"Anim error: {e}")
                    else: await safe_send_message(XX, f"[B][C][FF0000]❌ Animation not found", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/b '):
                    parts = inPuTMsG.strip().split()
                    bundle_ids = {"1": 914000002, "2": 914000003, "3": 914038001, "4": 914039001, "5": 914042001, "6": 914044001, "7": 914047001, "8": 914047002, "9": 914048001, "10": 914050001, "11": 914051001, "12": 914053001}
                    if len(parts) < 2: await safe_send_message(XX, f"[B][C][FFFF00]Usage: /b <1-12>", uid, chat_id, key, iv)
                    elif parts[1] in bundle_ids:
                        bid = bundle_ids[parts[1]]
                        try:
                            anim_pkt = await animation_packet(bid, key, iv)
                            if anim_pkt and online_writer:
                                online_writer.write(anim_pkt); await online_writer.drain()
                            await asyncio.sleep(3)
                            b_pkt = await Look_Changer(bid, key, iv, look_type=1, region=region)
                            if b_pkt and online_writer:
                                online_writer.write(b_pkt); await online_writer.drain()
                            await safe_send_message(XX, f"[B][C][00FF00]✅ Bundle {parts[1]} sent!", uid, chat_id, key, iv)
                        except Exception as e: print(f"Bundle error: {e}")
                    else: await safe_send_message(XX, f"[B][C][FF0000]❌ Bundle not found", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/sticker'):
                    try:
                        pkt = await send_sticker_packet(uid, chat_id, key, iv)
                        if pkt and whisper_writer:
                            whisper_writer.write(pkt); await whisper_writer.drain()
                    except Exception as e: print(f"Sticker error: {e}")

                elif inPuTMsG.strip() == '/love':
                    await safe_send_message(XX, "[B][C][FF0000]❌ ERROR! Usage:\n/love <name>\nExample: /love hater", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/love '):
                    try:
                        name = inPuTMsG.strip()[6:].strip()
                        if is_blacklisted(name):
                            await safe_send_message(XX, BLACKLIST_WARN_MSG, uid, chat_id, key, iv)
                            continue
                        await safe_send_message(XX, "[B][C][00FFFF]দোস্ত তুই শরমে পারছিস না, [FFFFFF]তোর হয়ে [FFFF00]আমিই বলে দিচ্ছি! ♡", uid, chat_id, key, iv)
                        await asyncio.sleep(2.0)
                        love_msgs = [
                            "[B][C][FFFFFF]♡ [FF1493]{Name} [FFFFFF]তুই আমার [00FFFF]সেফ জোন [FFFFFF]♡",
                            "[B][C][FFFFFF]♡ [00FF00]লবিতে [FFFFFF]শুধু [FFD700]{Name} তোকেই খুঁজি [FFFFFF]♡",
                            "[B][C][FFFFFF]♡ [00FFFF]এয়ারড্রপের [FFFFFF]চেয়েও [FF1493]তুই দামি [FFFFFF]♡",
                            "[B][C][FFFFFF]♡ [FFD700]{Name} তোর হাসিতে [FFFFFF]আমার [00FF00]HP বাড়ে [FFFFFF]♡",
                            "[B][C][FFFFFF]♡ [FF00FF]{Name} তুই ছাড়া [FFFFFF]গেম খেলা [00FFFF]পুরোই বৃথা [FFFFFF]♡",
                            "[B][C][FFFFFF]♡ [FFA500]স্নাইপারের [FFFFFF]একমাত্র [FF1493]লক্ষ্য {Name} তুই [FFFFFF]♡",
                            "[B][C][FFFFFF]♡ [32CD32]{Name} তুই আমার [FFFFFF]গ্লু-ওয়ালের [FFD700]কভার [FFFFFF]♡",
                            "[B][C][FFFFFF]♡ [FF0000]{Name} চল দুজনে [FFFFFF]মিলে [00FFFF]বুইয়া নিই [FFFFFF]♡",
                        ]
                        love_emotes = [909000010, 909000045, 909038004, 909047007]  # heart/propose-style emotes
                        # keep the ORIGINAL design exactly (per request: don't change colours, just fix errors)
                        for i, m in enumerate(love_msgs):
                            await safe_send_message(XX, m.replace('{Name}', name.upper()), uid, chat_id, key, iv)
                            try:
                                em_packet = await Emote_k(int(uid), love_emotes[i % len(love_emotes)], key, iv, region)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', em_packet)
                            except Exception as e:
                                print(f"Love emote error: {e}")
                            await asyncio.sleep(3.0)
                    except Exception as e: print(f"Love error: {e}")

                elif inPuTMsG.strip().startswith('/propose '):
                    name = inPuTMsG.strip()[9:].strip()
                    msg = f"[B][C][FF1493]💍 {name} 💍\n\nতুই আমার জীবন, তুই আমার সব।\nআমার হয়ে যাবি? 💕\n\n[FF69B4]❤️ প্রেমের প্রস্তাব ❤️"
                    P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/flirt '):
                    name = inPuTMsG.strip()[7:].strip()
                    flirts = [
                        f"[B][C][FF69B4]{name} তোর চোখে ডুবে গেলাম! 😍",
                        f"[B][C][FF1493]{name} তুই কি চাঁদ থেকে এসেছিস? 🌙",
                        f"[B][C][FF66CC]{name} তোর হাসি আমার হার্টবিট বাড়ায়! 💓",
                        f"[B][C][FF00FF]{name} তুই আমার স্বপ্নের রাজকুমারী! 👑",
                    ]
                    for m in flirts:
                        P = await SEndMsG(XX, m, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                        await asyncio.sleep(1.2)

                elif inPuTMsG.strip().startswith('/kiss '):
                    name = inPuTMsG.strip()[6:].strip()
                    msg = f"[B][C][FF1493]💋 {name} কে চুমু দিলাম! 😘\n[FF69B4]❤️❤️❤️"
                    P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/hug '):
                    name = inPuTMsG.strip()[5:].strip()
                    msg = f"[B][C][FF69B4]🤗 {name} কে জড়িয়ে ধরলাম! 💕"
                    P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/marry '):
                    name = inPuTMsG.strip()[7:].strip()
                    msg = f"[B][C][FF1493]💍 {name} তুই আমার হয়ে যাবি? 💍\n[FF69B4]❤️ বিয়ে করবো ❤️"
                    P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/bf '):
                    name = inPuTMsG.strip()[4:].strip()
                    msg = f"[B][C][FF69B4]💕 {name} তুই আমার বয়ফ্রেন্ড! 💕"
                    P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/gf '):
                    name = inPuTMsG.strip()[4:].strip()
                    msg = f"[B][C][FF69B4]💕 {name} তুই আমার গার্লফ্রেন্ড! 💕"
                    P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/ship '):
                    parts = inPuTMsG.strip()[6:].split()
                    if len(parts) >= 2:
                        pct = random.randint(1, 100)
                        msg = f"[B][C][FF1493]💘 {parts[0]} + {parts[1]} = {pct}% 💘"
                    else: msg = f"[B][C][FF0000]Usage: /ship <name1> <name2>"
                    P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/crush '):
                    name = inPuTMsG.strip()[7:].strip()
                    pct = random.randint(50, 100)
                    msg = f"[B][C][FF69B4]💗 {name} তোর প্রতি আমার ক্রাশ {pct}% 💗"
                    P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/breakup '):
                    name = inPuTMsG.strip()[9:].strip()
                    msg = f"[B][C][FF0000]💔 {name} আমাদের সম্পর্ক শেষ! 😭"
                    P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/later '):
                    try:
                        name = inPuTMsG.strip()[7:].strip()
                        msg = f"[B][C][FF1493]💌 প্রিয় {name} 💌\n\nতোর یادেতে দিন কাটে,\nতোর ছাড়া মন কাঁদে,\nতুই ছাড়া এই দুনিয়ায়,\nকিছুই যেন ভালো লাগে না।\n\n💕 তোর সবসময় 💕"
                        P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    except Exception as e: print(f"Later error: {e}")

                elif inPuTMsG.strip().startswith('/sadlater '):
                    try:
                        name = inPuTMsG.strip()[10:].strip()
                        msg = f"[B][C][808080]💔 {name} 💔\n\nভাঙা মনের কথা শোনো,\nপ্রতি রাতে তোর কথা আসে,\nতুই দূরে তবুও,\nতোর স্মৃতি প্রতি পলে কাঁদায়।\n\n💔 একা 💔"
                        P = await SEndMsG(XX, msg, uid, chat_id, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    except Exception as e: print(f"Sad error: {e}")

                elif inPuTMsG.strip() == '/joke':
                    try:
                        joke = random.choice(BANGLA_JOKES)
                        c1 = random.choice(JOKE_COLORS)
                        c2 = random.choice(JOKE_COLORS)
                        while c2 == c1: c2 = random.choice(JOKE_COLORS)
                        num = BANGLA_JOKES.index(joke) + 1
                        joke_msg = f"""[B][C][{c1}]━━━━━━━━━━━━━━━━━━
[{c1}]┃  [FFFFFF]😂 JOKE #{num}  [{c1}]┃
[{c1}]━━━━━━━━━━━━━━━━━━

[{c2}]{joke}

[{c1}]━━━━━━━━━━━━━━━━━━
[FFD700]🔮 Powered By [FFFF00]ᎻꫝsɪʙㅤCᴏᴅᴇx [FF69B4]➤ /joke
[{c1}]━━━━━━━━━━━━━━━━━━"""
                        await safe_send_message(XX, joke_msg, uid, chat_id, key, iv)
                    except Exception as e: print(f"Joke error: {e}")

                elif inPuTMsG.strip().startswith('/gali '):
                    try:
                        name = inPuTMsG.strip()[6:].strip()
                        if is_blacklisted(name):
                            await safe_send_message(XX, BLACKLIST_WARN_MSG, uid, chat_id, key, iv)
                            continue
                        gali_list = [
                            "তুই একটা খানকির বাচ্চা! 🤬", "তুই গন্দি নালার কীট! 🐛", "তুই ভসড়ির! 💢",
                            "তুই মাদারচোদ! 😡", "তুই ভাড়ভা! 🤬", "তুই রেন্ডির বাচ্চা! 😤",
                            "তুই নালায়েক কুত্তা! 🐕", "তুই হারামী! 💀", "তুই কুত্তার পিল্লা! 🐶",
                            "তুই চুতিয়া! 🤡", "তুই বেইজ্জত! 😈", "তুই শুয়োরের বাচ্চা! 🐷",
                        ]
                        for g in gali_list:
                            P = await SEndMsG(XX, f"[B][C][FF0000]{name} {g}", uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            await asyncio.sleep(1.5)
                        try:
                            taunt_emote = await Emote_k(int(uid), 909041014, key, iv, region)  # laugh/taunt emote
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', taunt_emote)
                        except Exception as e:
                            print(f"Gali emote error: {e}")
                    except Exception as e: print(f"Gali error: {e}")

                elif inPuTMsG.strip().startswith('/rt '):
                    try:
                        name = inPuTMsG.strip()[4:].strip()
                        if is_blacklisted(name):
                            await safe_send_message(XX, BLACKLIST_WARN_MSG, uid, chat_id, key, iv)
                            continue
                        roast_list = [
                            "তুই তো বট, রোবট! 🤖", "তুই ট্রেনিং গ্রাউন্ডের পুতুল! 🗿",
                            "তোর হেডশট রেট মাইনাসে! 📉", "তুই এনিমি দেখলেই পালাস! 🏃",
                            "তুই ফ্রি ফায়ারের সবচেয়ে বড় নуб! 🎯", "তোর গেমপ্লে দেখে বটরাও হাসে! 😂",
                            "তুই বন্দুকের বদলে লাঠি আনিস! 🦯", "তোর K/D রেশিও শূন্য! 0️⃣",
                            "তুই পুরা জোকার! 🤡", "তুই গেমে ভুত! 👻",
                        ]
                        for r in roast_list:
                            P = await SEndMsG(XX, f"[B][C][FF0000]{name} {r}", uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            await asyncio.sleep(1.5)
                    except Exception as e: print(f"RT error: {e}")

                elif inPuTMsG.strip().startswith('/praisa '):
                    try:
                        name = inPuTMsG.strip()[8:].strip()
                        praise_list = [
                            "তুই অসাধারণ মানুষ! 🌟", "তোর মেহনত একদিন রঙ দেবে! 🔥", "তুই ইউনিক! 💎",
                            "তোর ভবিষ্যৎ উজ্জ্বল! 🚀", "তুই লিডার হওয়ার যোগ্য! 👑", "তোর হাসি সবার দিন বানায়! 🌈",
                            "তুই সবসময় পজিটিভ থাক! 💖", "তুই যা চাস তা পাবি! 🏆", "তুই প্রেরণার উৎস! ✨",
                            "তোর ফোকাসই তোর শক্তি! 🎯",
                        ]
                        for p in praise_list:
                            P = await SEndMsG(XX, f"[B][C][00FF00]{name} {p}", uid, chat_id, key, iv)
                            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            await asyncio.sleep(0.8)
                    except Exception as e: print(f"Praisa error: {e}")

                elif inPuTMsG.strip().startswith('/slap '):
                    name = inPuTMsG.strip()[6:].strip()
                    P = await SEndMsG(XX, f"[B][C][FF0000]👋 {name} কে চড় দিলাম! 💥", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/punch '):
                    name = inPuTMsG.strip()[7:].strip()
                    P = await SEndMsG(XX, f"[B][C][FF0000]👊 {name} কে ঘুষি দিলাম! 💥", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/kick '):
                    name = inPuTMsG.strip()[6:].strip()
                    P = await SEndMsG(XX, f"[B][C][FF0000]🦵 {name} কে লাথি দিলাম! 💥", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/bite '):
                    name = inPuTMsG.strip()[6:].strip()
                    P = await SEndMsG(XX, f"[B][C][FF0000]🦷 {name} কে কামড় দিলাম! 😬", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/lick '):
                    name = inPuTMsG.strip()[6:].strip()
                    P = await SEndMsG(XX, f"[B][C][FF69B4]👅 {name} কে চাট দিলাম! 😋", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/dance':
                    P = await SEndMsG(XX, "[B][C][FF00FF]💃 আমি নাচছি! 🕺🎶", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/sing':
                    P = await SEndMsG(XX, "[B][C][00FFFF]🎤 লা লা লা... 🎶🎵", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/cry':
                    P = await SEndMsG(XX, "[B][C][808080]😭 আমি কাঁদছি... 😢", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/laugh':
                    P = await SEndMsG(XX, "[B][C][FFFF00]😂 হা হা হা! 🤣", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/scream':
                    P = await SEndMsG(XX, "[B][C][FF0000]😱 আআআআআ!!! 🤯", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/pray':
                    P = await SEndMsG(XX, "[B][C][00FF00]🤲 দোয়া করছি... 🙏", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/shower':
                    P = await SEndMsG(XX, "[B][C][00FFFF]🚿 গোসল করছি... 💦", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/toilet':
                    P = await SEndMsG(XX, "[B][C][808080]🚽 টয়লেটে গেলাম... 💩", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/meme':
                    memes = [
                        "[B][C][FFFF00]😂 মিম: আমি যখন পরীক্ষায় পাস করি — সবাই অবাক! 🤯",
                        "[B][C][FF69B4]😆 মিম: আমি ঘুমাতে যাই — চোখ খোলে সকাল! 🌅",
                        "[B][C][FF0000]🤣 মিম: ফ্রি ফায়ারে ১vs৪ — আমি জিতি! 🏆",
                        "[B][C][00FFFF]😹 মিম: খাবার দেখলে আমার অবস্থা — 🐷",
                    ]
                    P = await SEndMsG(XX, random.choice(memes), uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/quiz':
                    q, a = random.choice([
                        ("বাংলাদেশের রাজধানী?", "ঢাকা"), ("পৃথিবীর সবচেয়ে বড় মহাসাগর?", "প্রশান্ত মহাসাগর"),
                        ("বাংলাদেশের জাতীয় পাখি?", "দোয়েল"), ("১ কিলোমিটার = কত মিটার?", "১০০০"),
                        ("সূর্য কোন দিক থেকে ওঠে?", "পূর্ব"), ("পানির রাসায়নিক সূত্র?", "H2O"),
                        ("বাংলাদেশের জাতীয় ফল?", "কাঁঠাল"), ("মানব শরীরে কত হাড়?", "২০৬"),
                        ("ফ্রি ফায়ারে কত প্লেয়ার?", "৫০"), ("সবচেয়ে বড় গ্রহ?", "বৃহস্পতি"),
                    ])
                    P = await SEndMsG(XX, f"[B][C][FF4500]🧠 QUIZ 🧠\n\n[00FFFF]❓ {q}\n\n[FF4500]────────\n[00FF00]✅ উত্তর: {a}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/truth':
                    t = random.choice([
                        "তুই কাকে সবচেয়ে বেশি ভালোবাসিস?", "তোর সবচেয়ে বড় সিক্রেট কী?",
                        "শেষবার কবে কেঁদেছিলি?", "তোর ক্রাশ কে?", "শেষবার কবে মিথ্যা বলেছিলি?",
                        "তোর সবচেয়ে বড় ভয় কী?", "তোর সবচেয়ে লজ্জার মুহূর্ত?",
                        "তুই কখনো চুরি করেছিস?", "তোর ফোনে লুকানো অ্যাপ আছে?", "কাকে সবচেয়ে বেশি ঘৃণা করিস?",
                    ])
                    P = await SEndMsG(XX, f"[B][C][00FFFF]🤔 TRUTH 🤔\n\n{t}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/dare':
                    d = random.choice([
                        "🔥 ৫ মিনিট চোখ বন্ধ রাখ!", "😂 পরের ১০ মিনিট শুধু হাসতে থাক!",
                        "🐔 মুরগির মতো ডাক দে!", "🎤 একটা গান গা!", "💃 ৩০ সেকেন্ড নাচ!",
                        "🤪 বানরের আওয়াজ বের কর!", "😜 তোর ক্রাশকে মেসেজ দে!",
                        "🤡 ৫ মিনিট জোকার হ!", "📱 তোর ফোনের শেষ চ্যাট দেখাও!", "🍋 একটা কাঁচা লেবু খা!",
                    ])
                    P = await SEndMsG(XX, f"[B][C][FF4500]🎲 DARE 🎲\n\n{d}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/wyr':
                    a, b = random.choice([
                        ("অদৃশ্য হওয়ার শক্তি", "উড়ার শক্তি"), ("সবসময় পিজ্জা খাওয়া", "সবসময় বিরিয়ানি খাওয়া"),
                        ("অতীতে যাওয়া", "ভবিষ্যতে যাওয়া"), ("সুপারম্যান হওয়া", "ব্যাটম্যান হওয়া"),
                        ("ইন্টারনেট ছাড়া থাকা", "ফোন ছাড়া থাকা"), ("১০০ বিড়াল", "১০০ কুকুর"),
                        ("চিরকাল বাচ্চা থাকা", "চিরকাল বুড়ো থাকা"), ("সব ভাষা জানা", "সব যন্ত্র চালানো"),
                        ("ধনী কিন্তু একা", "গরিব কিন্তু বন্ধুদের সাথে"), ("চাঁদে বাড়ি", "সমুদ্রের নিচে বাড়ি"),
                    ])
                    P = await SEndMsG(XX, f"[B][C][DC143C]🤔 WOULD YOU RATHER?\n\n[00FF7F]A) {a}\n\n[DC143C]───── অথবা ─────\n\n[00FFFF]B) {b}\n\n[FF69B4]তোর উত্তর: A নাকি B?", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/roll':
                    d1 = random.randint(1, 6); d2 = random.randint(1, 6)
                    P = await SEndMsG(XX, f"[B][C][FF8C00]🎲 DICE ROLL 🎲\n\n[00FFFF]🎯 ডাইস ১: {d1}\n[FF69B4]🎯 ডাইস ২: {d2}\n\n[FF8C00]────────\n[FFFF00]📊 মোট: {d1+d2}/12", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/zodiac' or inPuTMsG.strip() == '/rashi':
                    s, d = random.choice(list({
                        "মেষ ♈": ("লাল", "৯", "মঙ্গলবার"), "বৃষ ♉": ("সবুজ", "৬", "শুক্রবার"),
                        "মিথুন ♊": ("হলুদ", "৫", "বুধবার"), "কর্কট ♋": ("সাদা", "২", "সোমবার"),
                        "সিংহ ♌": ("সোনালি", "১", "রবিবার"), "কন্যা ♍": ("সবুজ", "৫", "বুধবার"),
                        "তুলা ♎": ("নীল", "৬", "শুক্রবার"), "বৃশ্চিক ♏": ("লাল", "৯", "মঙ্গলবার"),
                        "ধনু ♐": ("বেগুনি", "৩", "বৃহস্পতিবার"), "মকর ♑": ("কালো", "৮", "শনিবার"),
                        "কুম্ভ ♒": ("নীল", "৪", "শনিবার"), "মীন ♓": ("সমুদ্রি", "৭", "বৃহস্পতিবার"),
                    }).items())
                    h = random.choice(["আজ তোর দিন শानदার যাবে!", "প্রেমে আজ ভালো খবর আসতে পারে!", "আর্থিক বিষয়ে সতর্ক থাক।", "আজ কিছু নতুন শিখবি!", "স্বাস্থ্যের যত্ন নে।"])
                    P = await SEndMsG(XX, f"[B][C][9370DB]🌟 রাশিফল 🌟\n\n[00FFFF]🔮 রাশি: [FF69B4]{s}\n[FFFF00]🎨 রঙ: [FFFFFF]{d[0]}\n[00FF7F]🔢 নাম্বার: [FFFFFF]{d[1]}\n[FF4500]📅 দিন: [FFFFFF]{d[2]}\n\n[DA70D6]📜 {h}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/weather' or inPuTMsG.strip() == '/abohawa':
                    city = random.choice(["ঢাকা", "চট্টগ্রাম", "খুলনা", "রাজশাহী", "সিলেট", "বরিশাল", "রংপুর", "ময়মনসিংহ", "কুমিল্লা", "নারায়ণগঞ্জ", "গাজীপুর", "বগুড়া"])
                    temp = f"{random.randint(20, 40)}°C"
                    w = random.choice(["☀️ রোদ", "🌤️ আংশিক মেঘ", "⛅ মেঘ", "🌧️ বৃষ্টি", "🌦️ হালকা বৃষ্টি", "⛈️ ভারী বৃষ্টি", "🌬️ ঠান্ডা বাতাস", "🌫️ কুয়াশা"])
                    hum = f"{random.randint(40, 95)}%"; wind = f"{random.randint(5, 40)} km/h"
                    P = await SEndMsG(XX, f"[B][C][1E90FF]🌤️ আবহাওয়া 🌤️\n\n[FF66CC]📍 শহর: [FFFFFF]{city}\n[FF69B4]🌡️ তাপমাত্রা: [FFFFFF]{temp}\n[00FF7F]☁️ আবহাওয়া: [FFFFFF]{w}\n[DA70D6]💧 আর্দ্রতা: [FFFFFF]{hum}\n[FF8C00]💨 বাতাস: [FFFFFF]{wind}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/luck '):
                    try:
                        name = inPuTMsG.strip()[6:].strip().title()
                        if not name:
                            await safe_send_message(XX, "[B][C][FF8C00]❌ ERROR! নাম লিখুন!\n[FFFFFF]Example: /luck hasib\n", uid, chat_id, key, iv)
                        else:
                            good_predictions = [
                                f"🌟 {name} তুমি খুব শীঘ্রই একটি বড় সাফল্য অর্জন করবে!",
                                f"💰 {name} তোমার জীবনে অনেক টাকা আসবে ইনশাআল্লাহ!",
                                f"❤️ {name} তোমার সত্যিকারের ভালোবাসা খুব কাছেই!",
                                f"🏆 {name} তুমি একদিন চ্যাম্পিয়ন হবে!",
                                f"📚 {name} তোমার পরীক্ষায় অনেক ভালো রেজাল্ট হবে!",
                                f"🌈 {name} তোমার কঠিন সময় শেষ হয়ে যাচ্ছে!",
                                f"🎯 {name} তোমার স্বপ্ন পূরণ হবে খুব শীঘ্রই!",
                                f"💎 {name} তুমি একটি মূল্যবান উপহার পাবে!",
                                f"🚀 {name} তোমার ক্যারিয়ার রকেটের মতো উঠবে!",
                                f"🏠 {name} তুমি একটি সুন্দর বাড়ি পাবে!",
                                f"✈️ {name} তুমি বিদেশ ভ্রমণ করবে!",
                                f"👑 {name} তুমি নেতা হবে একদিন!",
                                f"💪 {name} তোমার স্বাস্থ্য খুব ভালো থাকবে!",
                                f"🌺 {name} তোমার পরিবার সুখী হবে!",
                                f"🎓 {name} তুমি উচ্চ শিক্ষায় সফল হবে!",
                                f"🌟 {name} তোমার নাম সবাই জানবে!",
                                f"💝 {name} তোমার জীবনসঙ্গী অনেক সুন্দর হবে!",
                                f"🎶 {name} তুমি একটি প্রতিভা আবিষ্কার করবে!",
                                f"🏅 {name} তুমি গেমে গ্র্যান্ডমাস্টার হবে!",
                                f"🌻 {name} তোমার বন্ধুরা তোমাকে অনেক ভালোবাসে!",
                                f"💫 {name} তোমার ভাগ্য এখন খুব ভালো চলছে!",
                                f"🎁 {name} তুমি একটি চমক পাবে আজকে!",
                                f"🔥 {name} তোমার ভিতরে লুকানো শক্তি আছে!",
                                f"🌙 {name} তোমার রাতের দোয়া কবুল হবে!",
                                f"⭐ {name} তুমি তারকা হবে একদিন!",
                                f"🎪 {name} তোমার জীবনে আনন্দের ঝড় আসবে!",
                                f"💐 {name} তুমি অনেক সম্মান পাবে!",
                                f"🏰 {name} তোমার ভবিষ্যৎ রাজার মতো হবে!",
                                f"🌞 {name} তোমার জীবন আলোয় ভরে যাবে!",
                                f"💖 {name} তোমাকে অনেকে গোপনে পছন্দ করে!",
                                f"🎯 {name} তোমার লক্ষ্য পূরণ হবে ১০০%!",
                                f"🦁 {name} তুমি সিংহের মতো সাহসী!",
                                f"🌍 {name} তুমি বিশ্ব জয় করবে!",
                                f"💡 {name} তোমার বুদ্ধি অনেক তীক্ষ্ণ!",
                                f"🎭 {name} তুমি একটি বিশেষ প্রতিভার অধিকারী!",
                                f"🌸 {name} তোমার চারপাশে সুখ ছড়িয়ে আছে!",
                                f"💰 {name} তুমি কোটিপতি হবে ইনশাআল্লাহ!",
                                f"🎨 {name} তোমার সৃজনশীলতা অসাধারণ!",
                                f"🏋️ {name} তুমি যেকোনো কঠিন কাজ পারবে!",
                                f"🌟 {name} আল্লাহ তোমাকে অনেক ভালোবাসে!",
                                f"🦋 {name} তোমার জীবনে সুন্দর পরিবর্তন আসছে!",
                                f"🎗️ {name} তোমার কষ্টের দিন শেষ হচ্ছে!",
                                f"💎 {name} তুমি হীরার মতো মূল্যবান!",
                                f"🌺 {name} তোমার হাসি সবাইকে খুশি করে!",
                                f"🚗 {name} তুমি একটি দামি গাড়ি কিনবে!",
                                f"📱 {name} তোমার হাতে নতুন ফোন আসবে!",
                                f"🎮 {name} তুমি গেমিংয়ে লেজেন্ড হবে!",
                                f"💪 {name} তোমার শত্রুরা তোমাকে ভয় পায়!",
                                f"🌈 {name} তোমার পরে রংধনু আছে!",
                                f"🏆 {name} তুমি ১ নম্বর হবে সবকিছুতে!"
                            ]

                            bad_predictions = [
                                f"💀 {name} তোমার আজকের দিনটা খারাপ যাবে!",
                                f"😭 {name} তুমি আজ কাঁদবে!",
                                f"🐍 {name} তোমার কাছের মানুষ তোমাকে ধোঁকা দেবে!",
                                f"💔 {name} তোমার প্রেম ভেঙে যাবে!",
                                f"📉 {name} তোমার পরীক্ষায় ফেল হবে!",
                                f"🦷 {name} তোমার দাঁতে ব্যথা হবে!",
                                f"🤒 {name} তুমি অসুস্থ হয়ে পড়বে!",
                                f"👻 {name} রাতে তুমি ভয় পাবে!",
                                f"🐛 {name} তোমার খাবারে পোকা পাওয়া যাবে!",
                                f"📵 {name} তোমার ফোন নষ্ট হয়ে যাবে!",
                                f"🌧️ {name} তোমার উপর বৃষ্টি পড়বে বাইরে গেলে!",
                                f"😤 {name} তোমার সাথে কেউ ঝগড়া করবে!",
                                f"🐜 {name} তোমার ঘরে পিঁপড়া ভরে যাবে!",
                                f"💸 {name} তোমার টাকা হারিয়ে যাবে!",
                                f"🦟 {name} মশা তোমাকে অনেক কামড়াবে!",
                                f"😴 {name} তোমার আজ ঘুম হবে না!",
                                f"🤡 {name} মানুষ তোমাকে নিয়ে হাসবে!",
                                f"🧊 {name} তোমার ঠান্ডা লাগবে!",
                                f"🤯 {name} তোমার মাথা ব্যথা হবে!",
                                f"😱 {name} তুমি একটি ভয়ংকর স্বপ্ন দেখবে!",
                                f"🐸 {name} তোমার সামনে ব্যাঙ লাফ দেবে!",
                                f"💩 {name} তোমার জুতায় কিছু লাগবে!",
                                f"🦎 {name} তোমার ঘরে টিকটিকি পড়বে!",
                                f"🌪️ {name} তোমার ছাতা হারিয়ে যাবে!",
                                f"😡 {name} তোমার বন্ধু তোমার সাথে কথা বলবে না!",
                                f"🐕 {name} কুকুর তোমাকে তাড়া করবে!",
                                f"🧅 {name} তোমার চোখে পেঁয়াজের জ্বালা হবে!",
                                f"📝 {name} তোমার হোমওয়ার্ক হারিয়ে যাবে!",
                                f"🎮 {name} তুমি গেমে হেরে যাবে আজ!",
                                f"🔋 {name} তোমার ফোনের চার্জ শেষ হবে!",
                                f"🧦 {name} তোমার মোজা হারিয়ে যাবে!",
                                f"🦷 {name} তুমি চুইংগাম চুলে লাগাবে!",
                                f"🍕 {name} তোমার পছন্দের খাবার শেষ হয়ে যাবে!",
                                f"📶 {name} তোমার ইন্টারনেট স্লো হবে!",
                                f"🚌 {name} তুমি বাস মিস করবে!",
                                f"☔ {name} তুমি বৃষ্টিতে ভিজবে!",
                                f"😪 {name} তোমার ক্লাসে ঘুম পাবে!",
                                f"🧻 {name} বাথরুমে টিস্যু শেষ থাকবে!",
                                f"🦗 {name} তোমার কানের পাশে ঝিঁঝিঁ ডাকবে!",
                                f"💤 {name} তুমি অ্যালার্ম শুনতে পাবে না!",
                                f"🐦 {name} পাখি তোমার মাথায় হাগবে!",
                                f"🧹 {name} তোমাকে আজ ঘর পরিষ্কার করতে হবে!",
                                f"🤧 {name} তোমার হাঁচি থামবে না!",
                                f"🦠 {name} তোমার পেটে সমস্যা হবে!",
                                f"🔑 {name} তোমার চাবি হারিয়ে যাবে!",
                                f"👟 {name} তোমার জুতার ফিতা ছিঁড়ে যাবে!",
                                f"🧊 {name} তুমি পানিতে পিছলে পড়বে!",
                                f"🪳 {name} তোমার বিছানায় তেলাপোকা উঠবে!",
                                f"🍋 {name} তোমার মুখে টক লাগবে!",
                                f"😵 {name} তুমি মাথা ঘুরে পড়ে যাবে!"
                            ]
                            all_predictions = good_predictions + bad_predictions
                            prediction = random.choice(all_predictions)
                            if prediction in good_predictions:
                                pred_type = "[00FF00]✅ শুভ ভবিষ্যৎবাণী"
                                border_color = "00FF7F"
                            else:
                                pred_type = "[FF4500]⚠️ সতর্কতা ভবিষ্যৎবাণী"
                                border_color = "FF6347"
                            emoji = "🔮"
                            colors = ["FF69B4", "FFD700", "00FFFF", "FF4500", "7B68EE", "00FF7F", "FF1493", "1E90FF", "DA70D6", "DC143C", "20B2AA", "FF8C00", "9370DB", "4169E1", "00CED1"]
                            c1, c2, c3 = random.choice(colors), random.choice(colors), random.choice(colors)
                            luke_msg = f"""[B][C][{border_color}]━━━━━━━━━━━━━
[{c1}]★ [{c2}]{emoji} ভ বি ষ্য ৎ বা ণী {emoji} [{c1}]★
[{border_color}]━━━━━━━━━━━━━━━━━
[FFD700]👤 নাম: [{c3}]{name}
[{border_color}]━━━━━━━━━━━━━━━━
{pred_type}
[{border_color}]━━━━━━━━━━━━━━━━
[{c1}]{prediction}
[{border_color}]━━━━━━━━━━━━━━━━
[FF69B4]🔮 Powered By [FFFF00]ᎻꫝsɪʙㅤCᴏᴅᴇx
[{border_color}]━━━━━━━━━━━━━━━━━"""
                            await safe_send_message(XX, luke_msg, uid, chat_id, key, iv)
                    except Exception as e: print(f"Luck error: {e}")

                elif inPuTMsG.strip().startswith('/8ball '):
                    q = inPuTMsG.strip()[7:].strip()
                    answers = ["হ্যাঁ, নিশ্চিত! ✅", "না, একদমই না! ❌", "হতে পারে... 🤔", "ভাগ্য ভালো থাকলে হবে! 🍀", "আমার মনে হয় না! 😕", "অবশ্যই হবে! 💯", "ধৈর্য ধর, সময় লাগবে! ⏳"]
                    P = await SEndMsG(XX, f"[B][C][9370DB]🎱 MAGIC 8BALL 🎱\n\n[00FFFF]❓ {q}\n\n[FFFF00]{random.choice(answers)}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/coinflip':
                    P = await SEndMsG(XX, f"[B][C][FFD700]🪙 COIN FLIP 🪙\n\n[FFFF00]ফলাফল: {random.choice(['হেডস 🪙', 'টেইলস 🪙'])}", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip() == '/rps':
                    bot = random.choice(["পাথর 🪨", "কাগজ 📄", "কাঁচি ✂️"])
                    P = await SEndMsG(XX, f"[B][C][FF4500]✊ ROCK-PAPER-SCISSORS ✋\n\n[00FFFF]বট: {bot}\n[FFFF00]তুই কী বাছলি? লিখ!", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/rate '):
                    name = inPuTMsG.strip()[6:].strip()
                    pct = random.randint(1, 100)
                    P = await SEndMsG(XX, f"[B][C][FF69B4]⭐ RATING ⭐\n\n[00FFFF]👤 {name}\n[FFFF00]রেটিং: {pct}/100", uid, chat_id, key, iv)
                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                elif inPuTMsG.strip().startswith('/ice '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 2:
                        tgt = parts[1] if parts[1].lower() not in ('me', 'self') else str(uid)
                        if freeze_task and not freeze_task.done():
                            freeze_running = False; freeze_task.cancel(); await asyncio.sleep(0.3)
                        freeze_running = True
                        freeze_task = asyncio.create_task(freeze_emote_spam(tgt, key, iv, region, XX, chat_id, uid))
                        await safe_send_message(XX, f"[B][C][00FFFF]❄️ Freeze started {tgt}", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/room '):
                    parts = inPuTMsG.strip().split()
                    if len(parts) >= 3:
                        tgt = parts[1]; rid = parts[2]
                        try:
                            for i in range(3000):
                                spam_p = await Room_Spam(tgt, rid, "TEAM NEXUS", key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', spam_p)
                                if (i + 1) % 50 == 0: print(f"Room spam progress: {i+1}/3000")
                                await asyncio.sleep(0.05)
                            await safe_send_message(XX, f"[B][C][00FF00]✅ Room spam completed", uid, chat_id, key, iv)
                        except Exception as e: print(f"Room spam error: {e}")

                # ═══════════════════════════════════════════════
                # EMOTE EXTRAS (from Personal): [number] self emote, /menuN, aa[num] TEAMCODE
                # ═══════════════════════════════════════════════
                elif re.fullmatch(r'\d{1,3}', inPuTMsG.strip()) and inPuTMsG.strip() in GENERAL_EMOTES_MAP:
                    try:
                        H = await Emote_k(int(uid), int(GENERAL_EMOTES_MAP[inPuTMsG.strip()]), key, iv, region)
                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                    except Exception as e: print(f"Self emote error: {e}")

                elif re.fullmatch(r'/menu\d*', inPuTMsG.strip()):
                    try:
                        pg = int(inPuTMsG.strip()[5:] or 1)
                        await safe_send_message(XX, get_menu_page(pg), uid, chat_id, key, iv)
                    except Exception as e: print(f"Menu error: {e}")

                elif re.match(r'^aa\d+\s+\S+', inPuTMsG.strip()):
                    try:
                        cmd_, team_code = inPuTMsG.strip().split(maxsplit=1)
                        num_ = cmd_[2:]
                        if num_ not in GENERAL_EMOTES_MAP:
                            await safe_send_message(XX, f"[B][C][FF0000]❌ Emote {num_} not found", uid, chat_id, key, iv)
                        else:
                            await safe_send_message(XX, f"[B][C][00FF00]✅ Emote sending...\nEmote: {num_}", uid, chat_id, key, iv)
                            asyncio.create_task(emote_to_user_once(team_code.strip(), num_, uid, key, iv, region))
                    except Exception as e:
                        await safe_send_message(XX, "[B][C][FF0000]❌ Usage: aa[number] TEAMCODE\nExample: aa1 ABC123", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # EVO COMMANDS (Personal): /ob55 /ob54 /max | @max @maxx @evos | new | @new | @bot
                # ═══════════════════════════════════════════════
                elif re.match(r'^(/ob55|/ob54|/max|max)(\s|$)', inPuTMsG.strip()):
                    await start_evo_cycle("user", uid, inPuTMsG, XX, chat_id, key, iv, region, "OB55 SPECIAL EVO EMOTE")
                elif re.match(r'^(@max|@maxx|@evos)(\s|$)', inPuTMsG.strip()):
                    await start_evo_cycle("sm", uid, inPuTMsG, XX, chat_id, key, iv, region, "MAX EVO (You + Bot)")
                elif re.match(r'^new(\s|$)', inPuTMsG.strip()):
                    await start_evo_cycle("new", uid, inPuTMsG, XX, chat_id, key, iv, region, "NEW EMOTE CYCLE")
                elif re.match(r'^@new(\s|$)', inPuTMsG.strip()):
                    await start_evo_cycle("sam", uid, inPuTMsG, XX, chat_id, key, iv, region, "NEW EMOTE (You + Bot)")
                elif re.match(r'^@bot(\s|$)', inPuTMsG.strip()):
                    await start_evo_cycle("bot", uid, inPuTMsG, XX, chat_id, key, iv, region, "BOT EMOTE CYCLE")
                elif inPuTMsG.strip() in ('/s', '/o', '/sm', '/sn', '@bt'):
                    await stop_evo_cycle(uid, XX, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # /copy  /copy off   (emote hijack, from Personal)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == '/copy off':
                    emote_hijack = False
                    await safe_send_message(XX, "[B][C][00FFFF]The hijack Is Now OFF\n", uid, chat_id, key, iv)
                elif inPuTMsG.strip() == '/copy':
                    emote_hijack = True
                    await safe_send_message(XX, "[B][C][00FF00]The hijack Is Now ON\n[B][C][FFFFFF]Type [FFD700]/copy off [00FFFF]to turn it off", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # /roast <name>  (Personal, 20 gaming jokes)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() == '/roast':
                    await safe_send_message(XX, "[B][C][FF0000]❌ ERROR! Usage:\n/roast <name>\nExample: /roast hater", uid, chat_id, key, iv)

                elif inPuTMsG.strip().startswith('/roast '):
                    try:
                        name = inPuTMsG.strip()[7:].strip()
                        if is_blacklisted(name):
                            await safe_send_message(XX, BLACKLIST_WARN_MSG, uid, chat_id, key, iv)
                        else:
                            for line in ROAST_LINES:
                                await safe_send_message(XX, ROAST_PREFIX + line.replace('{Name}', name.upper()), uid, chat_id, key, iv)
                                await asyncio.sleep(1.5)
                    except Exception as e:
                        await safe_send_message(XX, f"[B][C][FF0000]❌ ERROR! Something went wrong:\n{e}", uid, chat_id, key, iv)

                # ═══════════════════════════════════════════════
                # /s1 .. /s5  BADGE (from Personal)
                # ═══════════════════════════════════════════════
                elif re.match(r'^/s[1-5](\s|$)', inPuTMsG.strip()):
                    try: await handle_badge_command(inPuTMsG.strip()[1:3], inPuTMsG, uid, chat_id, key, iv, region, XX)
                    except Exception as e: print(f"Badge cmd error: {e}")

                # ═══════════════════════════════════════════════
                # /dhadha  (Bangla riddle, answer after 20s)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip() in ('/dhadha', '/dhada', '/riddle'):
                    try:
                        q, ans = random.choice(DHADHA_LIST)
                        await safe_send_message(XX, f"[B][C][FFA500]🧩 ধাঁধা 🧩\n[B][C][FFFFFF]{q}\n[B][C][00FFFF]⏳ উত্তর ২০ সেকেন্ড পরে...", uid, chat_id, key, iv)
                        async def _dhadha_answer(_XX=XX, _uid=uid, _cid=chat_id, _ans=ans):
                            await asyncio.sleep(20)
                            await safe_send_message(_XX, f"[B][C][00FF00]✅ উত্তর: [FFFF00]{_ans}", _uid, _cid, key, iv)
                        asyncio.create_task(_dhadha_answer())
                    except Exception as e: print(f"Dhadha error: {e}")

                # ═══════════════════════════════════════════════
                # /frt  /grt  (friend % / soul %)
                # ═══════════════════════════════════════════════
                elif inPuTMsG.strip().startswith('/frt ') or inPuTMsG.strip().startswith('/grt '):
                    try:
                        is_frt = inPuTMsG.strip().startswith('/frt ')
                        raw = inPuTMsG.strip()[5:].strip()
                        if '&' not in raw:
                            await safe_send_message(XX, f"[B][C][FF8C00]❌ Usage: {'/frt' if is_frt else '/grt'} name1&name2\n", uid, chat_id, key, iv)
                        else:
                            n1, n2 = [x.strip().upper() for x in raw.split('&', 1)]
                            pct = random.randint(1, 100)
                            if pct >= 90: emo, stat, col = "💖💖💖", "BEST FOREVER!", "FF1493"
                            elif pct >= 70: emo, stat, col = "💕💕", "Amazing Bond!", "FF69B4"
                            elif pct >= 50: emo, stat, col = "💗", "Good Match!", "FFB6C1"
                            elif pct >= 30: emo, stat, col = "🤝", "Growing Bond", "FFA500"
                            else: emo, stat, col = "😅", "Need More Bonding!", "FFFF00"
                            title = "💕 FRIENDSHIP FOREVER TEST 💕" if is_frt else "💞 SOUL CONNECTION TEST 💞"
                            card = (f"[B][C][{col}]◎━━━━━━━━━━━━━━━━━━◎\n[FF69B4]◉ {title} ◉\n[{col}]◎━━━━━━━━━━━━━━━━━━◎\n"
                                    f"[FFFFFF]Name 1: [{col}]{n1}\n[FFFFFF]Name 2: [{col}]{n2}\n[{col}]◎━━━━━━━━━━━━━━━━━━◎\n"
                                    f"[FFFFFF]{emo} Result: [{col}]{pct}%\n[FFFFFF]{stat}\n[FFD700]◉ ᎻꫝsɪʙㅤCᴏᴅᴇx BOT ◉")
                            await safe_send_message(XX, card, uid, chat_id, key, iv)
                    except Exception as e: print(f"frt/grt error: {e}")

                else:
                    pass

            writer.close(); await writer.wait_closed(); whisper_writer = None
        except Exception as e:
            print(f"Chat error: {ip}:{port} - {e}")
            whisper_writer = None
        await asyncio.sleep(reconnect_delay)