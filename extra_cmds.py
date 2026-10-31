# ═══════════════════════════════════════════════════════════════
# extra_cmds.py — HASIB CODEX extra command pack (offline, no API needed)
# Every command here is real & computed locally. Hooked into bot_core's
# dispatcher via  extra_cmds.handle(command_text)  and into /help via
# extra_cmds.build_help_pages(brand).
# ═══════════════════════════════════════════════════════════════
import ast, base64, binascii, hashlib, math, operator, random, re, string, time, uuid, urllib.parse
from datetime import datetime, timedelta, timezone, date

try:
    from zoneinfo import ZoneInfo
except Exception:                      # very old python
    ZoneInfo = None

START_TS = time.time()
REG = {}          # name -> dict(fn, usage, desc, cat)
ORDER = []        # registration order (for help)


class Usage(Exception):
    pass


def cmd(name, usage, desc, cat, aliases=()):
    def deco(fn):
        REG[name] = dict(fn=fn, usage=usage, desc=desc, cat=cat, name=name)
        ORDER.append(name)
        for a in aliases:
            REG[a] = REG[name]
        return fn
    return deco


def R(title, body, col="00FFFF"):
    return f"[B][C][{col}]{title}\n[B][C][FFFFFF]{body}"


def num(s):
    f = float(s)
    return int(f) if f.is_integer() and abs(f) < 1e15 else f


def fmt(x):
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return str(x)
        return f"{x:.6g}" if abs(x) < 1e15 else f"{x:.6e}"
    return str(x)


def need(args, n):
    if len(args) < n:
        raise Usage()


def txt(args, n=0):
    need(args, n + 1)
    return " ".join(args[n:])


# ─────────────────────────── TIME ───────────────────────────
# key -> (label, IANA tz, fallback UTC offset hours)
ZONES = {
    "bd": ("Bangladesh 🇧🇩", "Asia/Dhaka", 6), "in": ("India 🇮🇳", "Asia/Kolkata", 5.5),
    "pk": ("Pakistan 🇵🇰", "Asia/Karachi", 5), "np": ("Nepal 🇳🇵", "Asia/Kathmandu", 5.75),
    "lk": ("Sri Lanka 🇱🇰", "Asia/Colombo", 5.5), "bt": ("Bhutan 🇧🇹", "Asia/Thimphu", 6),
    "mv": ("Maldives 🇲🇻", "Indian/Maldives", 5), "af": ("Afghanistan 🇦🇫", "Asia/Kabul", 4.5),
    "us": ("USA East 🇺🇸", "America/New_York", -5), "usw": ("USA West 🇺🇸", "America/Los_Angeles", -8),
    "uk": ("UK 🇬🇧", "Europe/London", 0), "ie": ("Ireland 🇮🇪", "Europe/Dublin", 0),
    "uae": ("UAE 🇦🇪", "Asia/Dubai", 4), "sa": ("Saudi Arabia 🇸🇦", "Asia/Riyadh", 3),
    "qa": ("Qatar 🇶🇦", "Asia/Qatar", 3), "kw": ("Kuwait 🇰🇼", "Asia/Kuwait", 3),
    "om": ("Oman 🇴🇲", "Asia/Muscat", 4), "bh": ("Bahrain 🇧🇭", "Asia/Bahrain", 3),
    "iq": ("Iraq 🇮🇶", "Asia/Baghdad", 3), "ir": ("Iran 🇮🇷", "Asia/Tehran", 3.5),
    "tr": ("Turkey 🇹🇷", "Europe/Istanbul", 3), "eg": ("Egypt 🇪🇬", "Africa/Cairo", 2),
    "ng": ("Nigeria 🇳🇬", "Africa/Lagos", 1), "za": ("South Africa 🇿🇦", "Africa/Johannesburg", 2),
    "ke": ("Kenya 🇰🇪", "Africa/Nairobi", 3), "ma": ("Morocco 🇲🇦", "Africa/Casablanca", 1),
    "jp": ("Japan 🇯🇵", "Asia/Tokyo", 9), "cn": ("China 🇨🇳", "Asia/Shanghai", 8),
    "kr": ("South Korea 🇰🇷", "Asia/Seoul", 9), "hk": ("Hong Kong 🇭🇰", "Asia/Hong_Kong", 8),
    "sg": ("Singapore 🇸🇬", "Asia/Singapore", 8), "my": ("Malaysia 🇲🇾", "Asia/Kuala_Lumpur", 8),
    "id": ("Indonesia 🇮🇩", "Asia/Jakarta", 7), "th": ("Thailand 🇹🇭", "Asia/Bangkok", 7),
    "vn": ("Vietnam 🇻🇳", "Asia/Ho_Chi_Minh", 7), "ph": ("Philippines 🇵🇭", "Asia/Manila", 8),
    "au": ("Australia 🇦🇺", "Australia/Sydney", 11), "nz": ("New Zealand 🇳🇿", "Pacific/Auckland", 13),
    "ca": ("Canada 🇨🇦", "America/Toronto", -5), "mx": ("Mexico 🇲🇽", "America/Mexico_City", -6),
    "br": ("Brazil 🇧🇷", "America/Sao_Paulo", -3), "ar": ("Argentina 🇦🇷", "America/Argentina/Buenos_Aires", -3),
    "ru": ("Russia 🇷🇺", "Europe/Moscow", 3), "de": ("Germany 🇩🇪", "Europe/Berlin", 1),
    "fr": ("France 🇫🇷", "Europe/Paris", 1), "it": ("Italy 🇮🇹", "Europe/Rome", 1),
    "es": ("Spain 🇪🇸", "Europe/Madrid", 1), "nl": ("Netherlands 🇳🇱", "Europe/Amsterdam", 1),
    "se": ("Sweden 🇸🇪", "Europe/Stockholm", 1), "ch": ("Switzerland 🇨🇭", "Europe/Zurich", 1),
    "pt": ("Portugal 🇵🇹", "Europe/Lisbon", 0), "gr": ("Greece 🇬🇷", "Europe/Athens", 2),
    "ua": ("Ukraine 🇺🇦", "Europe/Kyiv", 2), "utc": ("UTC 🌍", "UTC", 0),
}
ZALIAS = {"bangladesh": "bd", "dhaka": "bd", "india": "in", "ind": "in", "delhi": "in", "pakistan": "pk",
          "nepal": "np", "srilanka": "lk", "usa": "us", "america": "us", "newyork": "us", "la": "usw",
          "england": "uk", "britain": "uk", "london": "uk", "dubai": "uae", "saudi": "sa", "ksa": "sa",
          "turkey": "tr", "egypt": "eg", "japan": "jp", "tokyo": "jp", "china": "cn", "korea": "kr",
          "singapore": "sg", "malaysia": "my", "indonesia": "id", "thailand": "th", "vietnam": "vn",
          "philippines": "ph", "australia": "au", "canada": "ca", "brazil": "br", "russia": "ru",
          "germany": "de", "france": "fr", "italy": "it", "spain": "es", "gmt": "utc", "bst": "bd"}


def _now_in(key):
    label, tz, off = ZONES[key]
    try:
        if ZoneInfo is None:
            raise RuntimeError
        return label, datetime.now(ZoneInfo(tz))
    except Exception:
        return label, datetime.now(timezone(timedelta(hours=off)))


def _fmt_dt(dt):
    return dt.strftime("%I:%M:%S %p") + dt.strftime(" • %a %d %b %Y")


@cmd("time", "/time [country]", "World Time (bd, ind, usa...)", "TIME")
def c_time(a, raw):
    k = (a[0].lower() if a else "bd")
    if k in ("all", "world"):
        return c_timeall([], raw)
    k = ZALIAS.get(k, k)
    if k not in ZONES:
        return R("❌ Unknown country", "Use /zones to see the list.\nExample: /time bd  /time ind  /time usa", "FF0000")
    label, dt = _now_in(k)
    off = dt.utcoffset().total_seconds() / 3600
    return R(f"🕒 {label}", f"[FFFF00]{_fmt_dt(dt)}\n[00FF00]UTC{off:+g}", "FFA500")


@cmd("timeall", "/timeall", "Main World Clocks", "TIME")
def c_timeall(a, raw):
    rows = []
    for k in ("bd", "in", "pk", "uae", "uk", "us", "jp", "au"):
        label, dt = _now_in(k)
        rows.append(f"[FFA500]{label.split(' ')[0]}[FFFFFF] {dt.strftime('%I:%M %p')}  [00FFFF]{dt.strftime('%a')}")
    return R("🌍 WORLD CLOCK", "\n".join(rows), "FFD700")


@cmd("zones", "/zones", "Country Code List", "TIME")
def c_zones(a, raw):
    return R("🌐 /time CODES", " ".join(sorted(ZONES)) + "\n[FFFF00]Also: bangladesh india usa uk dubai japan...", "00FFFF")


@cmd("date", "/date", "Today's Date", "TIME")
def c_date(a, raw):
    _, d = _now_in("bd")
    return R("📅 DATE (BD)", d.strftime("%A, %d %B %Y"), "00FF7F")


@cmd("day", "/day [YYYY-MM-DD]", "Weekday of a Date", "TIME", ("dayof",))
def c_day(a, raw):
    d = datetime.strptime(a[0], "%Y-%m-%d") if a else _now_in("bd")[1]
    return R("📆 DAY", d.strftime("%A, %d %B %Y"), "00FF7F")


@cmd("weekno", "/weekno", "Week Number of Year", "TIME")
def c_weekno(a, raw):
    d = _now_in("bd")[1]
    return R("🗓 WEEK", f"Week {d.isocalendar()[1]} of {d.year}\nDay {d.timetuple().tm_yday} of year", "00FF7F")


@cmd("yearprog", "/yearprog", "Year Progress Bar", "TIME")
def c_yearprog(a, raw):
    d = _now_in("bd")[1]
    tot = 366 if (d.year % 4 == 0 and (d.year % 100 or d.year % 400 == 0)) else 365
    p = d.timetuple().tm_yday / tot * 100
    bar = "█" * int(p // 10) + "░" * (10 - int(p // 10))
    return R(f"⏳ {d.year}", f"[FFA500]{bar} [FFFF00]{p:.1f}%", "FFD700")


@cmd("timestamp", "/timestamp", "Unix Timestamp Now", "TIME", ("unix",))
def c_timestamp(a, raw):
    return R("⌚ UNIX", str(int(time.time())), "00BFFF")


@cmd("fromunix", "/fromunix [ts]", "Unix to Date", "TIME")
def c_fromunix(a, raw):
    need(a, 1)
    dt = datetime.fromtimestamp(int(a[0]), timezone(timedelta(hours=6)))
    return R("⌚ UNIX → BD", _fmt_dt(dt), "00BFFF")


@cmd("countdown", "/countdown [YYYY-MM-DD]", "Days Until Date", "TIME", ("daysto",))
def c_countdown(a, raw):
    need(a, 1)
    t = datetime.strptime(a[0], "%Y-%m-%d").date()
    n = (t - _now_in("bd")[1].date()).days
    msg = f"{n} days left" if n > 0 else ("Today! 🎉" if n == 0 else f"{-n} days ago")
    return R("⏰ COUNTDOWN", f"{a[0]} → [FFFF00]{msg}", "FF69B4")


@cmd("leap", "/leap [year]", "Leap Year Check", "TIME")
def c_leap(a, raw):
    y = int(a[0]) if a else datetime.now().year
    ok = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
    return R("📅 LEAP", f"{y} is {'a leap year ✅' if ok else 'not a leap year ❌'}", "00FF7F")


@cmd("timediff", "/timediff [c1] [c2]", "Time Gap Between 2 Countries", "TIME")
def c_timediff(a, raw):
    need(a, 2)
    k1, k2 = ZALIAS.get(a[0].lower(), a[0].lower()), ZALIAS.get(a[1].lower(), a[1].lower())
    if k1 not in ZONES or k2 not in ZONES:
        raise Usage()
    l1, d1 = _now_in(k1); l2, d2 = _now_in(k2)
    h = (d2.utcoffset() - d1.utcoffset()).total_seconds() / 3600
    return R("⏱ TIME GAP", f"{l2} is [FFFF00]{h:+g}h[FFFFFF] from {l1}", "FFA500")


# ─────────────────────── UNIT CONVERTERS ───────────────────────
CONV = {
    "c2f": (lambda x: x * 9 / 5 + 32, "°C", "°F"), "f2c": (lambda x: (x - 32) * 5 / 9, "°F", "°C"),
    "c2k": (lambda x: x + 273.15, "°C", "K"), "k2c": (lambda x: x - 273.15, "K", "°C"),
    "km2mi": (lambda x: x * 0.621371, "km", "mi"), "mi2km": (lambda x: x / 0.621371, "mi", "km"),
    "kg2lb": (lambda x: x * 2.20462, "kg", "lb"), "lb2kg": (lambda x: x / 2.20462, "lb", "kg"),
    "m2ft": (lambda x: x * 3.28084, "m", "ft"), "ft2m": (lambda x: x / 3.28084, "ft", "m"),
    "cm2in": (lambda x: x / 2.54, "cm", "in"), "in2cm": (lambda x: x * 2.54, "in", "cm"),
    "l2gal": (lambda x: x * 0.264172, "L", "gal"), "gal2l": (lambda x: x / 0.264172, "gal", "L"),
    "kmh2mph": (lambda x: x * 0.621371, "km/h", "mph"), "mph2kmh": (lambda x: x / 0.621371, "mph", "km/h"),
    "g2oz": (lambda x: x / 28.3495, "g", "oz"), "oz2g": (lambda x: x * 28.3495, "oz", "g"), "cm2m": (lambda x: x / 100, "cm", "m"), "km2m": (lambda x: x * 1000, "km", "m"), "ft2in": (lambda x: x * 12, "ft", "in"), "m2yd": (lambda x: x / 0.9144, "m", "yd"),
    "kg2g": (lambda x: x * 1000, "kg", "g"), "g2kg": (lambda x: x / 1000, "g", "kg"),
    "l2ml": (lambda x: x * 1000, "L", "mL"), "ml2l": (lambda x: x / 1000, "mL", "L"), "min2hr": (lambda x: x / 60, "min", "hr"),
    "hr2min": (lambda x: x * 60, "hr", "min"), "hr2day": (lambda x: x / 24, "hr", "day"), "wk2day": (lambda x: x * 7, "week", "day"), "mb2gb": (lambda x: x / 1024, "MB", "GB"),
    "gb2mb": (lambda x: x * 1024, "GB", "MB"), "gb2tb": (lambda x: x / 1024, "GB", "TB"),
    "deg2rad": (lambda x: math.radians(x), "°", "rad"), "rad2deg": (lambda x: math.degrees(x), "rad", "°"),
    "sqft2sqm": (lambda x: x * 0.092903, "sqft", "sqm"), "sqm2sqft": (lambda x: x / 0.092903, "sqm", "sqft"),
}
CONV_HELP = {
    "c2f": "Celsius → Fahrenheit", "f2c": "Fahrenheit → Celsius", "c2k": "Celsius → Kelvin", "k2c": "Kelvin → Celsius",
    "km2mi": "Km → Miles", "mi2km": "Miles → Km", "kg2lb": "Kg → Pounds", "lb2kg": "Pounds → Kg",
    "m2ft": "Meter → Feet", "ft2m": "Feet → Meter", "cm2in": "Cm → Inch", "in2cm": "Inch → Cm",
    "l2gal": "Liter → Gallon", "gal2l": "Gallon → Liter", "kmh2mph": "Km/h → Mph", "mph2kmh": "Mph → Km/h",
    "g2oz": "Gram → Ounce", "oz2g": "Ounce → Gram", "mm2cm": "Mm → Cm", "cm2m": "Cm → Meter",
    "m2km": "Meter → Km", "km2m": "Km → Meter", "in2ft": "Inch → Feet", "ft2in": "Feet → Inch",
    "yd2m": "Yard → Meter", "m2yd": "Meter → Yard", "kg2g": "Kg → Gram", "g2kg": "Gram → Kg",
    "l2ml": "Liter → mL", "ml2l": "mL → Liter", "sec2min": "Sec → Min", "min2hr": "Min → Hour",
    "hr2min": "Hour → Min", "hr2day": "Hour → Day", "day2hr": "Day → Hour", "wk2day": "Week → Day",
    "kb2mb": "KB → MB", "mb2gb": "MB → GB", "gb2mb": "GB → MB", "gb2tb": "GB → TB",
    "deg2rad": "Degree → Radian", "rad2deg": "Radian → Degree", "sqft2sqm": "Sq.ft → Sq.m", "sqm2sqft": "Sq.m → Sq.ft",
}


# keep the menu at exactly 20 pages x 15 commands
for _d in ("mm2cm", "cm2m", "m2km", "km2m", "in2ft", "ft2in", "yd2m", "m2yd", "g2kg", "ml2l", "sec2min",
           "hr2day", "day2hr", "kb2mb", "gb2tb"):
    CONV.pop(_d, None)
    CONV_HELP.pop(_d, None)


def _mk_conv(name):
    f, u1, u2 = CONV[name]

    def fn(a, raw):
        need(a, 1)
        x = float(a[0])
        return R("🔁 CONVERT", f"[FFFF00]{fmt(x)} {u1} [FFFFFF]= [00FF00]{fmt(round(f(x), 4))} {u2}", "00BFFF")
    return fn


for _n in CONV:
    cmd(_n, f"/{_n} [n]", CONV_HELP[_n], "CONVERT")(_mk_conv(_n))


# ───────────────────────────── MATH ─────────────────────────────
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.Mod: operator.mod, ast.FloorDiv: operator.floordiv,
        ast.USub: operator.neg, ast.UAdd: operator.pos}


def safe_eval(expr):
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            l, r = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and abs(r) > 1000:
                raise ValueError("power too big")
            return _OPS[type(n.op)](l, r)
        if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.operand))
        raise ValueError("bad expression")
    return ev(ast.parse(expr.replace("^", "**").replace("x", "*").replace("×", "*").replace("÷", "/"), mode="eval"))


@cmd("calc", "/calc [expr]", "Calculator (2+3*4)", "MATH")
def c_calc(a, raw):
    e = txt(a)
    return R("🧮 CALC", f"[FFFF00]{e} [FFFFFF]= [00FF00]{fmt(safe_eval(e))}", "00FF7F")


def _bin(name, label, f, sym):
    def fn(a, raw):
        need(a, 2)
        x, y = float(a[0]), float(a[1])
        return R(f"🧮 {label}", f"[FFFF00]{fmt(x)} {sym} {fmt(y)} [FFFFFF]= [00FF00]{fmt(f(x, y))}", "00FF7F")
    cmd(name, f"/{name} [a] [b]", label, "MATH")(fn)


_bin("plus", "Add", operator.add, "+")
_bin("sub", "Subtract", operator.sub, "-")
_bin("mul", "Multiply", operator.mul, "×")
_bin("div", "Divide", lambda x, y: x / y, "÷")
_bin("mod", "Remainder", operator.mod, "%")
_bin("pow", "Power", lambda x, y: x ** y if abs(y) <= 1000 else 1 / 0, "^")


def _un(name, label, f, usage_extra="", cat="MATH"):
    def fn(a, raw):
        need(a, 1)
        x = float(a[0])
        return R(f"🧮 {label.upper()}", f"[FFFF00]{name}({fmt(x)}) [FFFFFF]= [00FF00]{fmt(f(x))}", "00FF7F")
    cmd(name, f"/{name} [n]", label, cat)(fn)


_un("sqrt", "Square Root", math.sqrt)
_un("cbrt", "Cube Root", lambda x: math.copysign(abs(x) ** (1 / 3), x))
_un("sq", "Square", lambda x: x * x)
_un("cube", "Cube", lambda x: x ** 3)
_un("sin", "Sine (deg)", lambda x: math.sin(math.radians(x)))
_un("cos", "Cosine (deg)", lambda x: math.cos(math.radians(x)))
_un("tan", "Tangent (deg)", lambda x: math.tan(math.radians(x)))
_un("log", "Log base 10", math.log10)
_un("ln", "Natural Log", math.log)
_un("exp", "e Power", math.exp)
_un("floor", "Floor", math.floor)
_un("ceil", "Ceiling", math.ceil)
_un("abs", "Absolute", abs)


@cmd("fact", "", "", "MATH")
def _dummy(a, raw): return None


# '/fact' already exists in bot_core (random fact) → keep ours as /factorial
del REG["fact"]; ORDER.remove("fact")


@cmd("factorial", "/factorial [n]", "Factorial (n!)", "MATH")
def c_factorial(a, raw):
    need(a, 1); n = int(a[0])
    if not 0 <= n <= 500:
        raise Usage()
    s = str(math.factorial(n))
    return R("🧮 FACTORIAL", f"{n}! = [00FF00]{s if len(s) < 60 else s[:20] + '… (' + str(len(s)) + ' digits)'}", "00FF7F")


@cmd("fib", "/fib [n]", "Fibonacci Number", "MATH")
def c_fib(a, raw):
    need(a, 1); n = int(a[0])
    if not 0 <= n <= 5000:
        raise Usage()
    x, y = 0, 1
    for _ in range(n):
        x, y = y, x + y
    s = str(x)
    return R("🧮 FIBONACCI", f"F({n}) = [00FF00]{s if len(s) < 60 else s[:20] + '… (' + str(len(s)) + ' digits)'}", "00FF7F")


def _is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


@cmd("isprime", "/isprime [n]", "Prime Check", "MATH")
def c_isprime(a, raw):
    need(a, 1); n = int(a[0])
    if n > 10 ** 12:
        raise Usage()
    return R("🧮 PRIME", f"{n} is {'[00FF00]PRIME ✅' if _is_prime(n) else '[FF0000]NOT prime ❌'}", "00FF7F")


@cmd("nextprime", "/nextprime [n]", "Next Prime Number", "MATH")
def c_nextprime(a, raw):
    need(a, 1); n = int(a[0]) + 1
    if n > 10 ** 12:
        raise Usage()
    while not _is_prime(n):
        n += 1
    return R("🧮 NEXT PRIME", f"[00FF00]{n}", "00FF7F")


@cmd("pfactors", "/pfactors [n]", "Prime Factors", "MATH")
def c_pfactors(a, raw):
    need(a, 1); n = int(a[0])
    if not 2 <= n <= 10 ** 12:
        raise Usage()
    out, d, m = [], 2, n
    while d * d <= m:
        while m % d == 0:
            out.append(d); m //= d
        d += 1
    if m > 1:
        out.append(m)
    return R("🧮 FACTORS", f"{n} = [00FF00]{' × '.join(map(str, out))}", "00FF7F")


@cmd("divisors", "/divisors [n]", "All Divisors", "MATH")
def c_divisors(a, raw):
    need(a, 1); n = int(a[0])
    if not 1 <= n <= 10 ** 7:
        raise Usage()
    ds = [i for i in range(1, n + 1) if n % i == 0]
    return R("🧮 DIVISORS", f"[00FF00]{' '.join(map(str, ds))}", "00FF7F")


@cmd("gcd", "/gcd [a] [b]", "Greatest Common Divisor", "MATH")
def c_gcd(a, raw):
    need(a, 2)
    return R("🧮 GCD", f"[00FF00]{math.gcd(int(a[0]), int(a[1]))}", "00FF7F")


@cmd("lcm", "/lcm [a] [b]", "Least Common Multiple", "MATH")
def c_lcm(a, raw):
    need(a, 2)
    return R("🧮 LCM", f"[00FF00]{math.lcm(int(a[0]), int(a[1]))}", "00FF7F")


def _lst(a):
    need(a, 1)
    return [float(x) for x in re.split(r"[ ,]+", " ".join(a).strip()) if x]


@cmd("avg", "/avg [n1 n2 ..]", "Average", "MATH")
def c_avg(a, raw):
    l = _lst(a); return R("🧮 AVERAGE", f"[00FF00]{fmt(sum(l) / len(l))}", "00FF7F")


@cmd("sum", "/sum [n1 n2 ..]", "Sum of Numbers", "MATH")
def c_sum(a, raw):
    return R("🧮 SUM", f"[00FF00]{fmt(sum(_lst(a)))}", "00FF7F")


@cmd("maxn", "/maxn [n1 n2 ..]", "Largest Number", "MATH")
def c_maxn(a, raw):
    return R("🧮 MAX", f"[00FF00]{fmt(max(_lst(a)))}", "00FF7F")


@cmd("minn", "/minn [n1 n2 ..]", "Smallest Number", "MATH")
def c_minn(a, raw):
    return R("🧮 MIN", f"[00FF00]{fmt(min(_lst(a)))}", "00FF7F")


@cmd("median", "/median [n1 n2 ..]", "Median", "MATH")
def c_median(a, raw):
    l = sorted(_lst(a)); n = len(l)
    m = l[n // 2] if n % 2 else (l[n // 2 - 1] + l[n // 2]) / 2
    return R("🧮 MEDIAN", f"[00FF00]{fmt(m)}", "00FF7F")


@cmd("sortn", "/sortn [n1 n2 ..]", "Sort Numbers", "MATH")
def c_sortn(a, raw):
    return R("🧮 SORTED", f"[00FF00]{' '.join(fmt(x) for x in sorted(_lst(a)))}", "00FF7F")


@cmd("tohex", "/tohex [n]", "Decimal → Hex", "MATH")
def c_tohex(a, raw):
    need(a, 1); return R("🔢 HEX", f"[00FF00]{hex(int(a[0]))[2:].upper()}", "00BFFF")


@cmd("tooct", "/tooct [n]", "Decimal → Octal", "MATH")
def c_tooct(a, raw):
    need(a, 1); return R("🔢 OCT", f"[00FF00]{oct(int(a[0]))[2:]}", "00BFFF")


@cmd("tobin", "/tobin [n]", "Decimal → Binary", "MATH")
def c_tobin(a, raw):
    need(a, 1); return R("🔢 BIN", f"[00FF00]{bin(int(a[0]))[2:]}", "00BFFF")


@cmd("frombin", "/frombin [bits]", "Binary → Decimal", "MATH")
def c_frombin(a, raw):
    need(a, 1); return R("🔢 DEC", f"[00FF00]{int(a[0], 2)}", "00BFFF")


@cmd("fromhex", "/fromhex [hex]", "Hex → Decimal", "MATH")
def c_fromhex(a, raw):
    need(a, 1); return R("🔢 DEC", f"[00FF00]{int(a[0], 16)}", "00BFFF")


@cmd("hasib", "/hasib [n]", "Number → HASIB", "MATH")
def c_hasib(a, raw):
    need(a, 1); n = int(a[0])
    if not 1 <= n <= 3999:
        raise Usage()
    out = ""
    for v, s in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"),
                 (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += s; n -= v
    return R("🏛 HASIB", f"[00FF00]{out}", "FFD700")


@cmd("ordinal", "/ordinal [n]", "1 → 1st, 2 → 2nd", "MATH")
def c_ordinal(a, raw):
    need(a, 1); n = int(a[0])
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return R("🔢 ORDINAL", f"[00FF00]{n}{suf}", "00BFFF")


@cmd("evenodd", "/evenodd [n]", "Even or Odd", "MATH")
def c_evenodd(a, raw):
    need(a, 1); n = int(a[0])
    return R("🔢 PARITY", f"{n} is [00FF00]{'EVEN' if n % 2 == 0 else 'ODD'}", "00BFFF")


@cmd("digitsum", "/digitsum [n]", "Sum of Digits", "MATH")
def c_digitsum(a, raw):
    need(a, 1)
    return R("🔢 DIGIT SUM", f"[00FF00]{sum(int(c) for c in a[0] if c.isdigit())}", "00BFFF")


@cmd("collatz", "/collatz [n]", "Collatz Steps", "MATH")
def c_collatz(a, raw):
    need(a, 1); n = int(a[0]); s = 0
    if not 1 <= n <= 10 ** 9:
        raise Usage()
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1; s += 1
    return R("🔢 COLLATZ", f"Reaches 1 in [00FF00]{s} steps", "00BFFF")


@cmd("tip", "/tip [bill] [%]", "Tip Calculator", "MATH")
def c_tip(a, raw):
    need(a, 1); b = float(a[0]); p = float(a[1]) if len(a) > 1 else 10
    return R("💵 TIP", f"Tip: [FFFF00]{b * p / 100:.2f}[FFFFFF]  Total: [00FF00]{b * (1 + p / 100):.2f}", "32CD32")


@cmd("discount", "/discount [price] [%]", "Discount Calculator", "MATH")
def c_discount(a, raw):
    need(a, 2); p, d = float(a[0]), float(a[1])
    return R("🏷 DISCOUNT", f"Save: [FFFF00]{p * d / 100:.2f}[FFFFFF]  Pay: [00FF00]{p * (1 - d / 100):.2f}", "32CD32")


@cmd("vat", "/vat [price] [%]", "Add VAT/Tax", "MATH")
def c_vat(a, raw):
    need(a, 2); p, d = float(a[0]), float(a[1])
    return R("🧾 VAT", f"Tax: [FFFF00]{p * d / 100:.2f}[FFFFFF]  Total: [00FF00]{p * (1 + d / 100):.2f}", "32CD32")


@cmd("pchange", "/pchange [old] [new]", "Percent Change", "MATH")
def c_pchange(a, raw):
    need(a, 2); o, n = float(a[0]), float(a[1])
    return R("📈 CHANGE", f"[00FF00]{(n - o) / o * 100:+.2f}%", "32CD32")


@cmd("si", "/si [P] [rate%] [years]", "Simple Interest", "MATH")
def c_si(a, raw):
    need(a, 3); p, r, t = map(float, a[:3])
    return R("🏦 SIMPLE INT", f"Interest: [FFFF00]{p * r * t / 100:.2f}[FFFFFF]  Total: [00FF00]{p + p * r * t / 100:.2f}", "32CD32")


@cmd("ci", "/ci [P] [rate%] [years]", "Compound Interest", "MATH")
def c_ci(a, raw):
    need(a, 3); p, r, t = map(float, a[:3])
    tot = p * (1 + r / 100) ** t
    return R("🏦 COMPOUND", f"Interest: [FFFF00]{tot - p:.2f}[FFFFFF]  Total: [00FF00]{tot:.2f}", "32CD32")


@cmd("emi", "/emi [loan] [rate%] [months]", "Loan EMI", "MATH")
def c_emi(a, raw):
    need(a, 3); p, r, n = float(a[0]), float(a[1]) / 1200, int(a[2])
    e = p / n if r == 0 else p * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return R("🏦 EMI", f"Monthly: [00FF00]{e:.2f}[FFFFFF]  Total: [FFFF00]{e * n:.2f}", "32CD32")


@cmd("circle", "/circle [radius]", "Circle Area & Perimeter", "MATH")
def c_circle(a, raw):
    need(a, 1); r = float(a[0])
    return R("⭕ CIRCLE", f"Area: [00FF00]{math.pi * r * r:.3f}[FFFFFF]  Perimeter: [FFFF00]{2 * math.pi * r:.3f}", "00BFFF")


@cmd("rect", "/rect [w] [h]", "Rectangle Area", "MATH")
def c_rect(a, raw):
    need(a, 2); w, h = float(a[0]), float(a[1])
    return R("▭ RECTANGLE", f"Area: [00FF00]{fmt(w * h)}[FFFFFF]  Perimeter: [FFFF00]{fmt(2 * (w + h))}", "00BFFF")


@cmd("triangle", "/triangle [a] [b] [c]", "Triangle (Heron)", "MATH")
def c_triangle(a, raw):
    need(a, 3); x, y, z = map(float, a[:3]); s = (x + y + z) / 2
    ar = math.sqrt(s * (s - x) * (s - y) * (s - z))
    return R("△ TRIANGLE", f"Area: [00FF00]{ar:.3f}[FFFFFF]  Perimeter: [FFFF00]{fmt(x + y + z)}", "00BFFF")


@cmd("speed", "/speed [km] [hours]", "Speed Calculator", "MATH")
def c_speed(a, raw):
    need(a, 2)
    return R("🚗 SPEED", f"[00FF00]{float(a[0]) / float(a[1]):.2f} km/h", "00BFFF")


@cmd("bmr", "/bmr [kg] [cm] [age] [m/f]", "Daily Calorie (BMR)", "MATH")
def c_bmr(a, raw):
    need(a, 4); w, h, ag = float(a[0]), float(a[1]), float(a[2])
    b = 10 * w + 6.25 * h - 5 * ag + (5 if a[3].lower().startswith("m") else -161)
    return R("🔥 BMR", f"[00FF00]{b:.0f} kcal/day [FFFFFF](at rest)", "FF8C00")


# ─────────────────────────── TEXT & CODE ───────────────────────────
def _tx(name, label, f, cat="TEXT"):
    def fn(a, raw):
        return R(f"✍ {label.upper()}", f"[00FF00]{f(txt(a))}", "FF69B4")
    cmd(name, f"/{name} [txt]", label, cat)(fn)


_tx("upper", "UPPERCASE", str.upper)
_tx("lower", "lowercase", str.lower)
_tx("titlec", "Title Case", str.title)
_tx("swapcase", "sWAP cASE", str.swapcase)
_tx("snake", "snake_case", lambda s: re.sub(r"\W+", "_", s.strip().lower()))
_tx("kebab", "kebab-case", lambda s: re.sub(r"\W+", "-", s.strip().lower()))
_tx("camel", "camelCase", lambda s: (lambda w: w[0].lower() + "".join(x.title() for x in w[1:]))(s.split()))
_tx("slug", "URL Slug", lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-"))
_tx("shout", "SHOUT!", lambda s: s.upper() + "!!!")
_tx("spaced", "S P A C E D", lambda s: " ".join(s))
_tx("novowels", "No Vowels", lambda s: re.sub(r"[aeiouAEIOU]", "", s))
_tx("onlyvowels", "Only Vowels", lambda s: "".join(c for c in s if c.lower() in "aeiou"))
_tx("sortw", "Sort Words A-Z", lambda s: " ".join(sorted(s.split(), key=str.lower)))
_tx("uniq", "Unique Words", lambda s: " ".join(dict.fromkeys(s.split())))
_tx("longest", "Longest Word", lambda s: max(s.split(), key=len))
_tx("initials", "Initials", lambda s: "".join(w[0].upper() for w in s.split()))
_tx("mirror", "Mirror Text", lambda s: s + " | " + s[::-1])
_tx("trim", "Trim Spaces", lambda s: re.sub(r"\s+", " ", s).strip())
_tx("repeatw", "Repeat x3", lambda s: " ".join([s] * 3))
_tx("atbash", "Atbash Cipher", lambda s: s.translate(str.maketrans(string.ascii_lowercase + string.ascii_uppercase,
                                                                    string.ascii_lowercase[::-1] + string.ascii_uppercase[::-1])))
_tx("palindrome", "Palindrome Check",
    lambda s: ("✅ Yes, palindrome" if (lambda t: t == t[::-1] and t)(re.sub(r"\W", "", s.lower())) else "❌ Not a palindrome"))
_tx("wordfreq", "Word Frequency",
    lambda s: ", ".join(f"{w}×{c}" for w, c in sorted(((w, s.lower().split().count(w)) for w in set(s.lower().split())), key=lambda x: -x[1])[:8]))
_tx("charfreq", "Letter Frequency",
    lambda s: ", ".join(f"{c}×{s.lower().count(c)}" for c in sorted(set(filter(str.isalpha, s.lower())), key=lambda c: -s.lower().count(c))[:8]))
_tx("len", "Text Length", lambda s: f"{len(s)} chars")
_tx("ascii", "Text → ASCII Codes", lambda s: " ".join(str(ord(c)) for c in s[:40]))
_tx("fromascii", "ASCII Codes → Text", lambda s: "".join(chr(int(x)) for x in s.split()))
_tx("hexenc", "Text → Hex", lambda s: s.encode().hex())
_tx("unhex", "Hex → Text", lambda s: bytes.fromhex(s.replace(" ", "")).decode())
_tx("b64", "Base64 Encode", lambda s: base64.b64encode(s.encode()).decode())
_tx("unb64", "Base64 Decode", lambda s: base64.b64decode(s.encode()).decode())
_tx("urlenc", "URL Encode", lambda s: urllib.parse.quote(s))
_tx("urldec", "URL Decode", lambda s: urllib.parse.unquote(s))
_tx("md5", "MD5 Hash", lambda s: hashlib.md5(s.encode()).hexdigest())
_tx("sha1", "SHA-1 Hash", lambda s: hashlib.sha1(s.encode()).hexdigest())
_tx("sha256", "SHA-256 Hash", lambda s: hashlib.sha256(s.encode()).hexdigest())


def _mapfont(src, dst_upper, dst_lower, dst_digit=None):
    def f(s):
        out = []
        for c in s:
            if "A" <= c <= "Z":
                out.append(chr(dst_upper + ord(c) - 65))
            elif "a" <= c <= "z":
                out.append(chr(dst_lower + ord(c) - 97))
            elif dst_digit and "0" <= c <= "9":
                out.append(chr(dst_digit + ord(c) - 48))
            else:
                out.append(c)
        return "".join(out)
    return f


_tx("bold", "𝐁𝐨𝐥𝐝 Font", _mapfont(0, 0x1D400, 0x1D41A, 0x1D7CE), "FONT")
_tx("italic", "𝘐𝘵𝘢𝘭𝘪𝘤 Font", _mapfont(0, 0x1D608, 0x1D622), "FONT")
_tx("script", "𝓢𝓬𝓻𝓲𝓹𝓽 Font", _mapfont(0, 0x1D4D0, 0x1D4EA), "FONT")
_tx("mono", "𝙼𝚘𝚗𝚘 Font", _mapfont(0, 0x1D670, 0x1D68A, 0x1D7F6), "FONT")
_tx("gothic", "𝔊𝔬𝔱𝔥𝔦𝔠 Font", _mapfont(0, 0x1D56C, 0x1D586), "FONT")
_tx("double", "𝔻𝕠𝕦𝕓𝕝𝕖 Font", _mapfont(0, 0x1D538, 0x1D552, 0x1D7D8), "FONT")
_tx("wide", "Ｆｕｌｌｗｉｄｔｈ", lambda s: "".join(chr(ord(c) + 0xFEE0) if 33 <= ord(c) <= 126 else c for c in s), "FONT")
_tx("bubble", "Ⓑⓤⓑⓑⓛⓔ Font", lambda s: "".join(
    chr(0x24B6 + ord(c) - 65) if "A" <= c <= "Z" else chr(0x24D0 + ord(c) - 97) if "a" <= c <= "z" else c for c in s), "FONT")
_tx("smallcaps", "Sᴍᴀʟʟ Cᴀᴘs", lambda s: s.lower().translate(str.maketrans(
    "abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")), "FONT")
_tx("flip", "uʍop ǝpısdn", lambda s: s.lower().translate(str.maketrans(
    "abcdefghijklmnopqrstuvwxyz", "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"))[::-1], "FONT")
_tx("bnum", "Bangla Digits ১২৩", lambda s: s.translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")), "FONT")
_tx("enum", "English Digits 123", lambda s: s.translate(str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")), "FONT")


@cmd("caesar", "/caesar [shift] [txt]", "Caesar Cipher", "TEXT")
def c_caesar(a, raw):
    need(a, 2); k = int(a[0]) % 26
    s = " ".join(a[1:])
    out = "".join(chr((ord(c) - 97 + k) % 26 + 97) if "a" <= c <= "z" else
                  chr((ord(c) - 65 + k) % 26 + 65) if "A" <= c <= "Z" else c for c in s)
    return R("🔐 CAESAR", f"[00FF00]{out}", "FF69B4")


@cmd("repeat", "/repeat [n] [txt]", "Repeat Text (max 10)", "TEXT")
def c_repeat(a, raw):
    need(a, 2); n = max(1, min(int(a[0]), 10))
    return R("🔁 REPEAT", " ".join([" ".join(a[1:])] * n), "FF69B4")


@cmd("uuid", "/uuid", "Random UUID", "TEXT")
def c_uuid(a, raw):
    return R("🆔 UUID", f"[00FF00]{uuid.uuid4()}", "00BFFF")


@cmd("random", "/random [min] [max]", "Random Number", "TEXT")
def c_random(a, raw):
    lo, hi = (int(a[0]), int(a[1])) if len(a) >= 2 else (1, int(a[0]) if a else 100)
    return R("🎲 RANDOM", f"[00FF00]{random.randint(min(lo, hi), max(lo, hi))}", "FFD700")


@cmd("pin", "/pin [digits]", "Random PIN", "TEXT")
def c_pin(a, raw):
    n = max(3, min(int(a[0]) if a else 4, 12))
    return R("🔢 PIN", f"[00FF00]{''.join(random.choice(string.digits) for _ in range(n))}", "FFD700")


@cmd("hex", "/hex", "Random Hex Code", "TEXT")
def c_hexrand(a, raw):
    return R("🎨 HEX", f"[00FF00]{random.randint(0, 0xFFFFFF):06X}", "FFD700")


# ───────────────────────────── FUN & ART ─────────────────────────────
def pick(l):
    return random.choice(l)


QUOTES = ["Success is the sum of small efforts repeated daily.", "Dream big, work hard, stay humble.",
          "Don't watch the clock; do what it does — keep going.", "Believe you can and you're halfway there.",
          "The harder you work, the luckier you get.", "Fall seven times, stand up eight.",
          "Great things never come from comfort zones.", "Your only limit is your mind.",
          "Discipline beats motivation.", "Small steps still move you forward.",
          "Be the reason someone smiles today.", "Winners never quit, quitters never win."]
BN_PROVERBS = ["অতি লোভে তাঁতি নষ্ট।", "সবুরে মেওয়া ফলে।", "যেমন কর্ম তেমন ফল।", "ঘরের শত্রু বিভীষণ।",
               "দশের লাঠি একের বোঝা।", "চোরের মায়ের বড় গলা।", "নাচতে না জানলে উঠান বাঁকা।",
               "যত গর্জে তত বর্ষে না।", "আপনি বাঁচলে বাপের নাম।", "অভাবে স্বভাব নষ্ট।",
               "রাম না জন্মাতেই রামায়ণ।", "লেখাপড়া করে যে, গাড়ি ঘোড়া চড়ে সে।"]
PICKUPS = ["Are you Wi-Fi? Because I'm feeling a connection.", "Do you play Free Fire? Because you're my headshot.",
           "Is your name Google? You have everything I'm searching for.",
           "Are you a booyah? Because you make my day.", "You must be a loot box — I want to open you every day.",
           "Are you my squad? Because I'd never leave you."]
DADJOKES = ["Why don't skeletons fight? They don't have the guts.", "I used to hate facial hair, but then it grew on me.",
            "Why did the scarecrow win an award? He was outstanding in his field.",
            "What do you call fake spaghetti? An impasta.", "I'm reading a book on anti-gravity. It's impossible to put down.",
            "Why can't you trust atoms? They make up everything."]
TWISTERS = ["She sells seashells by the seashore.", "Peter Piper picked a peck of pickled peppers.",
            "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
            "Red lorry, yellow lorry.", "Fresh fried fish, fish fresh fried.", "Unique New York, you know you need unique New York."]
TRIVIA = ["Honey never spoils.", "Octopuses have three hearts.", "Bananas are berries, strawberries are not.",
          "A day on Venus is longer than its year.", "Sharks are older than trees.", "Bangladesh has the world's longest natural sea beach — Cox's Bazar.",
          "Lightning is five times hotter than the Sun's surface.", "Wombat poop is cube-shaped.",
          "The Sundarbans is the largest mangrove forest on Earth.", "Sound can't travel through space."]
RIDDLES = [("What has keys but can't open locks?", "A keyboard"), ("What gets wetter the more it dries?", "A towel"),
           ("What has a head and tail but no body?", "A coin"), ("What can you catch but not throw?", "A cold"),
           ("The more you take, the more you leave behind. What am I?", "Footsteps"),
           ("What has hands but can't clap?", "A clock")]
VIBES = ["Chill 😎", "Energetic ⚡", "Mysterious 🌙", "Royal 👑", "Savage 🔥", "Peaceful 🕊", "Legendary 🏆", "Cute 🌸"]
AURAS = ["Red 🔴 (Powerful)", "Orange 🟠 (Creative)", "Yellow 🟡 (Happy)", "Green 🟢 (Healing)", "Blue 🔵 (Calm)",
         "Purple 🟣 (Wise)", "Gold 🌟 (Legendary)", "Pink 🌸 (Loving)"]
FORTUNES = ["A pleasant surprise is waiting for you.", "Big luck arrives this week.", "Someone is thinking about you.",
            "Your hard work will pay off soon.", "A new friend will change your life.", "Today is a great day to start.",
            "Money is coming your way 💰", "Stay patient, the best is near."]


@cmd("quote", "/quote", "Motivational Quote", "FUN")
def c_quote(a, raw):
    return R("💬 QUOTE", pick(QUOTES), "FFD700")


@cmd("motivate", "/motivate [name]", "Motivate Someone", "FUN")
def c_motivate(a, raw):
    n = " ".join(a) or "Champion"
    return R(f"🔥 {n.upper()}", pick(QUOTES), "FF4500")


@cmd("proverb", "/proverb", "Bangla Proverb", "FUN")
def c_proverb(a, raw):
    return R("📜 প্রবাদ", pick(BN_PROVERBS), "FFA500")


@cmd("pickup", "/pickup", "Pickup Line", "FUN")
def c_pickup(a, raw):
    return R("💘 PICKUP", pick(PICKUPS), "FF1493")


@cmd("dadjoke", "/dadjoke", "Dad Joke", "FUN")
def c_dadjoke(a, raw):
    return R("😂 DAD JOKE", pick(DADJOKES), "FFD700")


@cmd("tongue", "/tongue", "Tongue Twister", "FUN")
def c_tongue(a, raw):
    return R("👅 TWISTER", pick(TWISTERS), "00BFFF")


@cmd("trivia", "/trivia", "Random Trivia", "FUN")
def c_trivia(a, raw):
    return R("🧠 TRIVIA", pick(TRIVIA), "00FF7F")


@cmd("puzzle", "/puzzle", "Riddle + Answer", "FUN")
def c_puzzle(a, raw):
    q, ans = pick(RIDDLES)
    return R("🧩 PUZZLE", f"{q}\n[FFFF00]Answer: [00FF00]{ans}", "DA70D6")


@cmd("vibe", "/vibe [name]", "Vibe Check", "FUN")
def c_vibe(a, raw):
    return R(f"✨ {(' '.join(a) or 'YOU').upper()}", f"Vibe: [FFFF00]{pick(VIBES)}", "FF69B4")


@cmd("aura", "/aura [name]", "Aura Colour", "FUN")
def c_aura(a, raw):
    return R(f"🌈 {(' '.join(a) or 'YOU').upper()}", f"Aura: [FFFF00]{pick(AURAS)}", "DA70D6")


@cmd("fortune", "/fortune", "Fortune Cookie", "FUN")
def c_fortune(a, raw):
    return R("🥠 FORTUNE", pick(FORTUNES), "FFD700")


@cmd("iq", "/iq [name]", "IQ Test (fun)", "FUN")
def c_iq(a, raw):
    n = " ".join(a) or "You"
    return R("🧠 IQ", f"{n}: [00FF00]{random.randint(70, 200)} IQ", "00BFFF")


@cmd("lucky", "/lucky", "Lucky Number + Colour", "FUN")
def c_lucky(a, raw):
    return R("🍀 LUCKY", f"Number: [00FF00]{random.randint(1, 99)}[FFFFFF]  Colour: [FFFF00]{random.randint(0, 0xFFFFFF):06X}", "32CD32")


@cmd("lotto", "/lotto", "Lucky Lotto Numbers", "FUN")
def c_lotto(a, raw):
    return R("🎰 LOTTO", f"[00FF00]{' '.join(str(x) for x in sorted(random.sample(range(1, 50), 6)))}", "FFD700")


@cmd("slots", "/slots", "Slot Machine", "FUN")
def c_slots(a, raw):
    s = [pick("🍒🍋🍉⭐🔔7️⃣") for _ in range(3)]
    res = "🎉 JACKPOT!" if len(set(s)) == 1 else "Nice, 2 match!" if len(set(s)) == 2 else "Try again"
    return R("🎰 SLOTS", f"{' | '.join(s)}\n[FFFF00]{res}", "FFD700")


@cmd("guess", "/guess [1-10]", "Guess the Number", "FUN")
def c_guess(a, raw):
    need(a, 1); g = int(a[0]); n = random.randint(1, 10)
    return R("🎯 GUESS", f"You: {g}  Me: {n}\n" + ("[00FF00]Correct! 🎉" if g == n else "[FF0000]Wrong, try again"), "FFA500")


@cmd("rpsls", "/rpsls [pick]", "Rock Paper Scissors Lizard Spock", "FUN")
def c_rpsls(a, raw):
    need(a, 1)
    o = ["rock", "paper", "scissors", "lizard", "spock"]
    m = a[0].lower()
    if m not in o:
        raise Usage()
    b = pick(o)
    wins = {"rock": ("scissors", "lizard"), "paper": ("rock", "spock"), "scissors": ("paper", "lizard"),
            "lizard": ("paper", "spock"), "spock": ("rock", "scissors")}
    res = "Draw 🤝" if m == b else "You win 🏆" if b in wins[m] else "I win 😎"
    return R("✊ RPSLS", f"You: {m}  Bot: {b}\n[FFFF00]{res}", "FFA500")


@cmd("highfive", "/highfive [name]", "High Five", "FUN")
def c_highfive(a, raw):
    return R("🙌 HIGH FIVE", f"You ✋ {(' '.join(a) or 'Everyone')} !!", "FFD700")


@cmd("cheer", "/cheer [name]", "Cheer Someone", "FUN")
def c_cheer(a, raw):
    return R("🎉 CHEERS", f"Hip hip hooray for [FFFF00]{' '.join(a) or 'you'}[FFFFFF]! 🥳🎊", "FF69B4")


@cmd("shrug", "/shrug", "Shrug Art", "ART")
def c_shrug(a, raw):
    return R("🤷", "¯\\_(ツ)_/¯", "FFD700")


@cmd("tableflip", "/tableflip", "Table Flip Art", "ART")
def c_tableflip(a, raw):
    return R("😤", "(╯°□°）╯︵ ┻━┻", "FF4500")


@cmd("lenny", "/lenny", "Lenny Face", "ART")
def c_lenny(a, raw):
    return R("😏", "( ͡° ͜ʖ ͡°)", "FFD700")


@cmd("catart", "/catart", "Cat ASCII Art", "ART")
def c_cat(a, raw):
    return R("🐱 CAT", " /\\_/\\\n( o.o )\n > ^ <", "FFA500")


@cmd("heartart", "/heartart", "Heart Art", "ART")
def c_heart(a, raw):
    return R("💖 HEART", "  ♥♥   ♥♥\n♥♥♥♥ ♥♥♥♥\n ♥♥♥♥♥♥♥\n   ♥♥♥♥♥\n     ♥♥♥\n       ♥", "FF1493")


@cmd("pyramid", "/pyramid [n]", "Star Pyramid", "ART")
def c_pyramid(a, raw):
    n = max(2, min(int(a[0]) if a else 5, 8))
    return R("⭐ PYRAMID", "\n".join(" " * (n - i) + "★" * (2 * i - 1) for i in range(1, n + 1)), "FFD700")


@cmd("diamond", "/diamond [n]", "Diamond Art", "ART")
def c_diamond(a, raw):
    n = max(2, min(int(a[0]) if a else 4, 7))
    rows = [" " * (n - i) + "◆" * (2 * i - 1) for i in range(1, n + 1)]
    return R("💎 DIAMOND", "\n".join(rows + rows[-2::-1]), "00FFFF")


@cmd("box", "/box [txt]", "Text in a Box", "ART")
def c_box(a, raw):
    s = txt(a)[:30]
    return R("📦 BOX", f"╔{'═' * (len(s) + 2)}╗\n║ {s} ║\n╚{'═' * (len(s) + 2)}╝", "00FF7F")


@cmd("banner", "/banner [txt]", "Star Banner", "ART")
def c_banner(a, raw):
    s = txt(a)[:30]
    return R("🌟 BANNER", f"★━━━━━━━━━━━★\n   {s}\n★━━━━━━━━━━━★", "FFD700")


@cmd("progress", "/progress [percent]", "Progress Bar", "ART")
def c_progress(a, raw):
    need(a, 1); p = max(0, min(float(a[0]), 100))
    return R("📊 PROGRESS", f"{'█' * int(p // 10)}{'░' * (10 - int(p // 10))} [FFFF00]{p:g}%", "00FF7F")


# ─────────────────────────── BOT INFO ───────────────────────────
@cmd("ping", "/ping", "Bot Alive Check", "BOT")
def c_ping(a, raw):
    return R("🏓 PONG", "[00FF00]Bot is online & responding ✅", "00FF7F")


@cmd("uptime", "/uptime", "Bot Running Time", "BOT")
def c_uptime(a, raw):
    s = int(time.time() - START_TS)
    return R("⏱ UPTIME", f"[00FF00]{s // 3600}h {(s % 3600) // 60}m {s % 60}s", "00FF7F")


@cmd("botinfo", "/botinfo", "Bot Information", "BOT")
def c_botinfo(a, raw):
    return R("🤖 HASIB CODEX", f"Commands: [FFFF00]{total_commands()}[FFFFFF]\nHelp pages: [FFFF00]{len(PAGES_CACHE) or len(build_help_pages())}\n[00FFFF]Website control panel included", "FFA500")


@cmd("cmdcount", "/cmdcount", "Total Commands", "BOT")
def c_cmdcount(a, raw):
    return R("📊 COMMANDS", f"Total listed: [00FF00]{total_commands()}", "FFA500")


@cmd("search", "/search [word]", "Find a Command", "BOT", ("cmdfind",))
def c_search(a, raw):
    w = txt(a).lower()
    hits = [u for u, d, _ in ALL_ENTRIES() if w in u.lower() or w in d.lower()][:8]
    return R(f"🔎 '{w}'", "\n".join(f"[00FF00]{h}" for h in hits) or "[FF0000]No command found", "00BFFF")


@cmd("random_cmd", "/randcmd", "Random Command Hint", "BOT", ("randcmd",))
def c_randcmd(a, raw):
    u, d, _ = pick(ALL_ENTRIES())
    return R("💡 TRY THIS", f"[00FF00]{u}\n[FFFFFF]{d}", "FFD700")


@cmd("owner", "/owner", "Bot Owner", "BOT", ("credits",))
def c_owner(a, raw):
    return R("👑 OWNER", "[FFD700]HASIB CODEX\n[FFFFFF]Free Fire TCP Bot + Web Panel", "FFA500")


@cmd("version", "/version", "Bot Version", "BOT")
def c_version(a, raw):
    return R("🆚 VERSION", "HASIB CODEX [00FF00]v2.0 PREMIUM [FFFFFF]— OB55", "FFA500")


# ═══════════════════════ HELP BUILDER ═══════════════════════
# Commands that already live in bot_core.py (kept exactly as they were)
EXISTING = [
    ("/join [code]", "Join Squad", "MATCH"), ("/exit", "Leave Squad", "MATCH"), ("/3 /4 /5 /6", "Team Size", "MATCH"),
    ("/gh [tc] [name]", "Ghost Join", "MATCH"), ("[number]", "Self Emote", "EMOTE"), ("aa[num] [tc]", "Magic Emote", "EMOTE"),
    ("/menu[num]", "All Emotes Menu", "EMOTE"), ("/copy /copy off", "Emote Hijack", "EMOTE"),
    ("/dance [uids]", "Dance Sequence", "EMOTE"), ("/as", "Stop Dance", "EMOTE"), ("/e [uid] [emote]", "Emote Send", "EMOTE"),
    ("/p [uid] [em] [num]", "Custom Emote", "EMOTE"), ("/mg [txt] [rep]", "Wave Text", "EMOTE"), ("/stop msg", "Stop Wave Text", "EMOTE"),
    ("/animation [num]", "Animation", "EMOTE"), ("/ob55 /max", "Max Evo Self", "EVO"), ("/s", "Stop Evo Cycle", "EVO"),
    ("@max @evos", "Max Evo Bot", "EVO"), ("/o", "Stop Bot Evo", "EVO"), ("new", "Random Evo Self", "EVO"),
    ("/sm /sn", "Stop Random", "EVO"), ("@new", "Random Bot Evo", "EVO"), ("@bot", "Only Bot Random", "EVO"),
    ("@bt", "Stop Bot Cycle", "EVO"), ("/evo [uid] [1-21]", "Evo Emote", "EVO"), ("/evos /sevos", "Evo Cycle", "EVO"),
    ("/ice [uid]", "Freeze Emote", "EVO"), ("/s1 [uid]", "Badge 1", "BADGE"), ("/s2 [uid]", "Badge 2", "BADGE"),
    ("/s3 [uid]", "Badge 3", "BADGE"), ("/s4 [uid]", "Badge 4", "BADGE"), ("/s5 [uid]", "Badge 5", "BADGE"),
    ("/room [uid] [id]", "Room Invite", "BADGE"), ("/b [num]", "Equip Bundle", "BADGE"), ("/alltitles", "All Titles", "BADGE"),
    ("/title", "Title", "BADGE"), ("/info [uid]", "Player Info", "INFO"), ("/check [uid]", "Ban Status", "INFO"),
    ("/tt [user]", "TikTok Info", "INFO"), ("/yt [channel]", "YouTube Info", "INFO"), ("/weather", "Weather", "INFO"),
    ("/translet [lang] [txt]", "Translate", "INFO"), ("/admin", "Admin Info", "INFO"), ("/help [page]", "Show Help", "INFO"),
    ("/add [uid]", "Add Friend (Admin)", "ADMIN"), ("/remove [uid]", "Remove Friend (Admin)", "ADMIN"),
    ("/on /off", "Bot ON/OFF (Admin)", "ADMIN"), ("/restart", "Auto Reconnect (Admin)", "ADMIN"),
    ("/pc /phone", "Login Mode (Admin)", "ADMIN"), ("/display_msg", "Swap xC4 (Admin)", "ADMIN"),
    ("/stop", "Stop All", "ADMIN"), ("/ban [uid]", "Ban Spam (Admin)", "ADMIN"), ("/unban", "Stop Ban", "ADMIN"),
    ("/gali [name]", "Bangla Gali", "SOCIAL"), ("/praisa [name]", "Praise", "SOCIAL"), ("/later [name]", "Love Letter", "SOCIAL"),
    ("/sadlater [name]", "Sad Letter", "SOCIAL"), ("/love [name]", "Love Style", "SOCIAL"), ("/roast [name]", "Roast Someone", "SOCIAL"),
    ("/hug [name]", "Hug", "SOCIAL"), ("/kiss [name]", "Kiss", "SOCIAL"), ("/slap [name]", "Slap (fun)", "SOCIAL"),
    ("/propose [name]", "Propose", "SOCIAL"), ("/marry [name]", "Marry", "SOCIAL"), ("/crush [name]", "Crush Meter", "SOCIAL"),
    ("/flirt [name]", "Flirt", "SOCIAL"), ("/sing", "Sing", "SOCIAL"), ("/rate [name]", "Rate Someone", "SOCIAL"),
    ("/ship [a] [b]", "Ship Meter", "SOCIAL"), ("/name [txt]", "Big Banner Name", "SOCIAL"),
    ("/frt [n1]&[n2]", "Friend %", "GAME"), ("/grt [n1]&[n2]", "Soul %", "GAME"), ("/quiz", "Quiz", "GAME"),
    ("/dare", "Dare", "GAME"), ("/truth", "Truth", "GAME"), ("/wyr", "Would You Rather", "GAME"), ("/roll", "Roll", "GAME"),
    ("/rps", "Rock Paper Scissors", "GAME"), ("/8ball", "Magic 8 Ball", "GAME"), ("/dhadha", "Bangla Riddle", "GAME"),
    ("/riddle", "Riddle", "GAME"), ("/zodiac", "Zodiac", "GAME"), ("/rashi", "Rashi", "GAME"), ("/joke", "Joke", "GAME"),
    ("/spin", "Lucky Spin", "GAME"), ("/luck [name]", "Fortune", "GAME"), ("/coinflip", "Coin Toss", "GAME"),
    ("/meme", "Random Meme", "GAME"), ("/laugh", "Laugh Action", "ACTION"), ("/scream", "Scream Action", "ACTION"),
    ("/pray", "Pray Action", "ACTION"), ("/shower", "Shower Action", "ACTION"), ("/toilet", "Toilet Action", "ACTION"),
    ("/password [n]", "Generate Password", "TOOLS"), ("/bmi [kg] [m]", "BMI Calculator", "TOOLS"), ("/age [year]", "Age Calculator", "TOOLS"),
    ("/dice [NdM]", "Dice Roller", "TOOLS"), ("/reverse [txt]", "Reverse Text", "TOOLS"), ("/count [txt]", "Char/Word Count", "TOOLS"),
    ("/anagram [word]", "Shuffle Letters", "TOOLS"), ("/binary [txt]", "Text → Binary", "TOOLS"), ("/morse [txt]", "Text → Morse", "TOOLS"),
    ("/leet [txt]", "Leet Speak", "TOOLS"), ("/rot13 [txt]", "ROT13 Cipher", "TOOLS"), ("/percent [x] of [y]", "Percentage", "TOOLS"),
    ("/pick [a,b,c]", "Random Pick", "TOOLS"), ("/yesno", "Magic Answer", "TOOLS"), ("/compliment [name]", "Nice Message", "TOOLS"),
    ("/fact", "Fun Fact", "TOOLS"), ("/namegen", "Random Name", "TOOLS"), ("/color", "Random Hex Color", "TOOLS"),
    ("/define [word]", "Dictionary", "TOOLS"), ("/chucknorris", "Chuck Norris Joke", "TOOLS"),
]

EXISTING += [
    ("/leave", "Leave Squad", "MATCH"), ("/sticker", "Random Sticker", "EMOTE"), ("/mth [expr]", "Calculator", "INFO"),
    ("/rt [name]", "Roast Someone", "SOCIAL"), ("/bf [name]", "Boyfriend", "SOCIAL"), ("/gf [name]", "Girlfriend", "SOCIAL"),
    ("/breakup [name]", "Breakup", "SOCIAL"), ("/punch [name]", "Punch (fun)", "SOCIAL"), ("/kick [name]", "Kick (fun)", "SOCIAL"),
    ("/bite [name]", "Bite (fun)", "SOCIAL"), ("/lick [name]", "Lick (fun)", "SOCIAL"), ("/cry", "Cry Action", "ACTION"),
]

# Page order & colour (colour cycles through this palette)
PALETTE = [("FFA500", "FFD700"), ("00FFFF", "FFD700"), ("FF00FF", "FFD700"), ("8A2BE2", "9370DB"), ("FF0000", "FFD700"),
           ("FF1493", "FFD700"), ("4169E1", "FFD700"), ("00BFFF", "FFD700"), ("FF75EA", "FFD700"), ("DA70D6", "FFD700"),
           ("1690E8", "FFD700"), ("FF4500", "FFD700"), ("9370DB", "FFD700"), ("32CD32", "FFD700"), ("00FF7F", "FFD700")]
CAT_ORDER = ["MATCH", "EMOTE", "EVO", "BADGE", "INFO", "ADMIN", "SOCIAL", "GAME", "ACTION", "TOOLS", "TIME", "FUN", "ART",
             "FONT", "TEXT", "MATH", "CONVERT", "BOT"]
PAGES_CACHE = []


def ALL_ENTRIES():
    """[(usage, desc, category)] — existing + every registered extra command, in menu order."""
    items = list(EXISTING)
    seen = set()
    for n in ORDER:
        r = REG[n]
        if r["usage"] and r["name"] not in seen:
            seen.add(r["name"])
            items.append((r["usage"], r["desc"], r["cat"]))
    items.sort(key=lambda e: CAT_ORDER.index(e[2]) if e[2] in CAT_ORDER else 99)   # stable → keeps order inside a category
    return items


def total_commands():
    return len(ALL_ENTRIES())


CORE_CATS = {"MATCH", "EMOTE", "EVO", "BADGE", "INFO", "ADMIN"}
MAX_LINES = 11         # lines per menu (title + bars + category headers + rows)
NAMES_PER_ROW = 2      # compact categories: command names per row
_CAT_TITLE = {"MATCH": "MATCH & SQUAD", "EMOTE": "EMOTE CONTROL", "EVO": "EVO CONTROL", "BADGE": "BADGE & TITLE",
              "INFO": "INFO", "ADMIN": "ADMIN", "SOCIAL": "SOCIAL", "GAME": "GAMES", "ACTION": "ACTIONS",
              "TOOLS": "TOOLS", "TIME": "TIME", "FUN": "FUN", "ART": "ART", "FONT": "FONT", "TEXT": "TEXT",
              "MATH": "MATH", "CONVERT": "CONVERT", "BOT": "BOT"}
PER_PAGE = MAX_LINES
_PAGE_OF = {}


def _category_rows():
    """[(cat, [(row_text_without_colour, [usages])])] in menu order. Core = one command per row with description,
    others = NAMES_PER_ROW short names per row."""
    out = []
    cur_cat, rows, seen = None, [], set()
    for u, d, c in ALL_ENTRIES():
        if c != cur_cat:
            if rows:
                out.append((cur_cat, rows))
            cur_cat, rows = c, []
        if c in CORE_CATS:
            rows.append((f"[00FF00]{u} [FFFFFF]({d})", [u]))
        else:
            n = u.split()[0]
            if n in seen:
                continue
            seen.add(n)
            if rows and len(rows[-1][1]) < NAMES_PER_ROW and rows[-1][1][0].split()[0] not in CORE_CATS \
                    and not rows[-1][0].endswith(")"):
                rows[-1] = (rows[-1][0] + f" [FFFFFF]| [00FF00]{n}", rows[-1][1] + [n])
            else:
                rows.append((f"[00FF00]{n}", [n]))
    if rows:
        out.append((cur_cat, rows))
    return out


def build_help_pages(brand="HASIB"):
    """Short menus of <= MAX_LINES lines, tree style, category headers like the reference design."""
    cats = _category_rows()
    page_lines, pages_raw = [], []     # pages_raw: list of list of (kind, text, usages)
    cur = []

    def used():
        return len(cur) + 3            # title + top bar + closing bar

    for cat, rows in cats:
        title = _CAT_TITLE.get(cat, cat)
        idx = 0
        cont = False
        while idx < len(rows):
            sep = 1 if cur else 0
            free = MAX_LINES - used() - sep - 1          # minus header line
            if free < 2 and idx < len(rows) and not (len(rows) - idx == 1 and free >= 1):
                pages_raw.append(cur)
                cur = []
                continue
            take = min(free, len(rows) - idx)
            if cur:
                cur.append(("bar", "", []))
            cur.append(("head", title + (" (cont.)" if cont else ""), []))
            for j, (txt, us) in enumerate(rows[idx:idx + take]):
                last = (j == take - 1)
                cur.append(("row", ("└─" if last else "├─") + txt, us))
            idx += take
            cont = True
            if idx < len(rows):
                pages_raw.append(cur)
                cur = []
    if cur:
        pages_raw.append(cur)

    total = len(pages_raw)
    pages = []
    _PAGE_OF.clear()
    for p, items in enumerate(pages_raw):
        col, head = PALETTE[p % len(PALETTE)]
        bar = f"[B][{col}]──────────────────"
        lines = [f"[B][{col}]■ {brand}ㅤ MENU {p + 1:02d}/{total:02d} ■", bar]
        for kind, text, us in items:
            if kind == "bar":
                lines.append(bar)
            elif kind == "head":
                lines.append(f"[B][FFD700]{text}")
            else:
                br, rest = text[:2], text[2:]
                lines.append(f"[B][{col}]{br}{rest}")
                for u in us:
                    _PAGE_OF[u] = p + 1
        lines.append(bar)
        pages.append("\n".join(lines))
    PAGES_CACHE[:] = pages
    return pages


def catalog():
    """Used by the website: [{'cmd','desc','cat','page'}]"""
    if not PAGES_CACHE:
        build_help_pages()
    out = []
    for u, d, c in ALL_ENTRIES():
        out.append({"cmd": u, "desc": d, "cat": c, "page": _PAGE_OF.get(u) or _PAGE_OF.get(u.split()[0], 1)})
    return out


def handle(command_text):
    """Return a ready-to-send message string, or None if this isn't one of our commands."""
    parts = command_text.strip().split()
    if not parts or not parts[0].startswith("/"):
        return None
    name = parts[0][1:].split("@")[0].lower()
    r = REG.get(name)
    if not r:
        return None
    try:
        return r["fn"](parts[1:], command_text)
    except Usage:
        return f"[B][C][FF8C00]Usage: [FFFF00]{r['usage']}"
    except ZeroDivisionError:
        return "[B][C][FF0000]❌ Cannot divide by zero."
    except Exception:
        return f"[B][C][FF0000]❌ Invalid input.\n[B][C][FFFF00]Usage: {r['usage']}"
