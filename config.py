import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
#  Bot Configuration
# ─────────────────────────────────────────

TOKEN           = os.getenv("DISCORD_TOKEN")
PREFIX          = os.getenv("PREFIX", "!")
BOT_NAME        = os.getenv("BOT_NAME", "UltimateBot")
OWNER_ID        = int(os.getenv("OWNER_ID", 0))

# Dashboard
DASHBOARD_SECRET = os.getenv("DASHBOARD_SECRET", "super-secret")
CLIENT_ID        = os.getenv("CLIENT_ID", "")
CLIENT_SECRET    = os.getenv("CLIENT_SECRET", "")
REDIRECT_URI     = os.getenv("REDIRECT_URI", "http://localhost:5000/callback")
DASHBOARD_PORT   = int(os.getenv("DASHBOARD_PORT", 5000))

# Colors
COLORS = {
    "success"   : 0x2ECC71,
    "error"     : 0xE74C3C,
    "warning"   : 0xF39C12,
    "info"      : 0x3498DB,
    "purple"    : 0x9B59B6,
    "gold"      : 0xF1C40F,
    "pink"      : 0xE91E63,
    "cyan"      : 0x00BCD4,
    "dark"      : 0x2C2F33,
    "blurple"   : 0x5865F2,
    "starboard" : 0xFFAC33,
}

# Economy
DAILY_COINS       = 100
WORK_MIN_COINS    = 50
WORK_MAX_COINS    = 200
STARTING_BALANCE  = 500
ROB_SUCCESS_RATE  = 40
ROB_FINE_PERCENT  = 20

# Leveling
XP_PER_MESSAGE    = 15
XP_COOLDOWN       = 60
LEVEL_UP_CHANNEL  = None

# Level role rewards {level: role_id}
LEVEL_ROLES = {}

# Moderation
MAX_WARNINGS      = 3

# Starboard
STARBOARD_THRESHOLD = 3
STARBOARD_EMOJI     = "⭐"

# AutoMod
AUTOMOD_SPAM_LIMIT    = 5
AUTOMOD_SPAM_INTERVAL = 5
BANNED_WORDS          = ["slur1", "slur2"]
CAPS_THRESHOLD        = 70
MAX_MENTIONS           = 5
MAX_EMOJIS             = 10

# Tickets
TICKET_CATEGORY       = None
TICKET_LOG_CHANNEL    = None

# Giveaways
GIVEAWAY_EMOJI = "🎉"

# Database
DB_PATH = "database/bot.db"