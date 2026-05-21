
<div align="center">

<img src="https://cdn.discordapp.com/emojis/1234567890.png" width="120" alt="Bot Logo"/>

# 🤖 UltimateBot

### The most powerful open-source Discord bot — built with Python

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![discord.py](https://img.shields.io/badge/discord.py-2.3.2-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discordpy.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/https://github.com/Compromisee/DiBot?style=for-the-badge&color=yellow)](https://github.com/https://github.com/Compromisee/DiBot/stargazers)
[![Forks](https://img.shields.io/github/forks/https://github.com/Compromisee/DiBot?style=for-the-badge&color=blue)](https://github.com/https://github.com/Compromisee/DiBot/network/members)
[![Issues](https://img.shields.io/github/issues/https://github.com/Compromisee/DiBot?style=for-the-badge&color=red)](https://github.com/https://github.com/Compromisee/DiBot/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge)](https://github.com/https://github.com/Compromisee/DiBot/pulls)
[![Last Commit](https://img.shields.io/github/last-commit/https://github.com/Compromisee/DiBot?style=for-the-badge)](https://github.com/https://github.com/Compromisee/DiBot/commits)
[![Code Size](https://img.shields.io/github/languages/code-size/https://github.com/Compromisee/DiBot?style=for-the-badge)](https://github.com/https://github.com/Compromisee/DiBot)
[![Top Language](https://img.shields.io/github/languages/top/https://github.com/Compromisee/DiBot?style=for-the-badge&color=blue)](https://github.com/https://github.com/Compromisee/DiBot)

---

**94+ Features • Slash Commands • Web Dashboard • Economy • Music • AutoMod • Tickets • Giveaways**

[🚀 Quick Start](#-quick-start) •
[📋 Features](#-features) •
[📖 Commands](#-commands) •
[🌐 Dashboard](#-web-dashboard) •
[⚙️ Config](#️-configuration) •
[🤝 Contributing](#-contributing)

---

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Configuration & API Keys](#️-configuration--api-keys)
- [Features](#-features)
  - [Moderation](#️-moderation)
  - [Economy](#-economy)
  - [Leveling & XP](#-leveling--xp)
  - [Fun & Games](#-fun--games)
  - [Giveaways](#-giveaways)
  - [Tickets](#-tickets)
  - [Music](#-music)
  - [AutoMod](#️-automod)
  - [Starboard](#-starboard)
  - [Polls](#-polls)
  - [Reaction Roles](#-reaction-roles)
  - [AFK System](#-afk-system)
  - [Suggestions](#-suggestions)
  - [Reminders](#-reminders)
  - [Advanced Logging](#-advanced-logging)
  - [Welcome System](#-welcome-system)
  - [Tags](#-tags)
  - [Utility](#-utility)
  - [Admin](#️-admin)
  - [Web Dashboard](#-web-dashboard)
- [Commands Reference](#-commands-reference)
- [Slash Commands](#-slash-commands)
- [Database Schema](#-database-schema)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**UltimateBot** is a fully-featured, production-ready Discord bot built with
`discord.py 2.3.2`. It supports both **prefix commands** (`!`) and **slash
commands** (`/`), comes with a **web dashboard** powered by Quart (async Flask),
and stores all data in **SQLite** via `aiosqlite`.

### ✨ Why UltimateBot?

| Feature | Details |
|---|---|
| 🔧 **94+ commands** | Prefix + Slash, covering every use case |
| 🌐 **Web Dashboard** | Manage servers, view leaderboards, change settings |
| 💾 **Persistent DB** | SQLite — no external database required |
| 🤖 **AutoMod** | Anti-spam, anti-link, caps filter, mention flood |
| 🎵 **Music** | YouTube playback, queue, loop, volume |
| 💰 **Economy** | Coins, bank, shop, gambling, rob system |
| ⭐ **Leveling** | XP per message, role rewards, rank cards |
| 🎉 **Giveaways** | Button-based entry, auto-end, reroll |
| 🎫 **Tickets** | Panel + buttons, claim, log, multi-ticket |
| 📋 **Logging** | Message edits/deletes, joins/leaves, voice, roles |
| 🚀 **Slash Commands** | Full `/` support with choices, autocomplete |
| 🔒 **Permission System** | Per-command Discord permission checks |

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version |
|---|---|
| Python | `3.11+` |
| FFmpeg | Latest (for music) |
| Git | Any |

### 1. Clone the Repository

```bash
git clone https://github.com/https://github.com/Compromisee/DiBot.git
cd discord-bot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Then edit .env with your tokens
```

### 5. Run the Bot

```bash
python bot.py
```

> 🌐 **Dashboard** will automatically start at `http://localhost:5000`

---

## 📁 Project Structure

```
discord-bot/
│
├── 📄 bot.py                     # Main entry point — starts bot + dashboard
├── 📄 config.py                  # All configuration values loaded from .env
├── 📄 .env                       # Secret tokens & API keys (never commit!)
├── 📄 .env.example               # Safe template for .env
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                  # You are here
│
├── 📂 cogs/                      # Feature modules (Cogs)
│   ├── 📄 __init__.py
│   ├── 📄 events.py              # on_ready, on_message, XP, background tasks
│   ├── 📄 slash_commands.py      # All slash (/) commands
│   ├── 📄 moderation.py          # Kick, ban, mute, warn, purge, lockdown
│   ├── 📄 economy.py             # Coins, work, daily, gamble, rob, shop
│   ├── 📄 leveling.py            # XP, rank, leaderboard, level roles
│   ├── 📄 fun.py                 # 8ball, meme, roast, rps, slots, etc.
│   ├── 📄 utility.py             # Help, profile, serverinfo, ping, botinfo
│   ├── 📄 admin.py               # Server setup, shop items, coin control
│   ├── 📄 giveaways.py           # Create, end, reroll giveaways
│   ├── 📄 tickets.py             # Ticket panel, close, add, claim
│   ├── 📄 music.py               # YouTube music player + queue
│   ├── 📄 automod.py             # Anti-spam, anti-link, caps, banned words
│   ├── 📄 starboard.py           # Auto-post starred messages
│   ├── 📄 polls.py               # Quick, multi-option, and straw polls
│   ├── 📄 reactionroles.py       # Add/remove roles via reactions
│   ├── 📄 afk.py                 # AFK status + auto-notify on mention
│   ├── 📄 suggestions.py         # Submit, approve, deny suggestions
│   ├── 📄 logging.py             # Full Discord event logging
│   └── 📄 welcomer.py            # Welcome/leave messages with templates
│
├── 📂 database/
│   ├── 📄 __init__.py
│   └── 📄 db.py                  # Full async SQLite database manager
│
├── 📂 utils/
│   ├── 📄 __init__.py
│   ├── 📄 embeds.py              # Reusable embed templates
│   ├── 📄 helpers.py             # XP math, cooldown checks, duration parser
│   ├── 📄 views.py               # Discord UI Views & Buttons
│   └── 📄 paginator.py           # Interactive paginator with nav buttons
│
└── 📂 dashboard/                 # Web dashboard (Quart)
    ├── 📄 app.py                 # App factory + route registration
    ├── 📂 routes/
    │   ├── 📄 __init__.py
    │   ├── 📄 auth.py            # Discord OAuth2 login/logout/callback
    │   ├── 📄 api.py             # REST API endpoints (JSON)
    │   └── 📄 views.py           # HTML page routes
    ├── 📂 templates/
    │   ├── 📄 base.html          # Base layout with navbar + footer
    │   ├── 📄 index.html         # Landing page with feature showcase
    │   ├── 📄 login.html         # Discord OAuth login page
    │   ├── 📄 dashboard.html     # Server selection grid
    │   ├── 📄 guild.html         # Server overview + stats
    │   ├── 📄 leaderboard.html   # Full XP leaderboard table
    │   └── 📄 settings.html      # Live server settings editor
    └── 📂 static/
        ├── 📂 css/
        │   └── 📄 style.css      # Full dark theme CSS
        └── 📂 js/
            └── 📄 main.js        # Counter animations + settings save
```

---

## ⚙️ Configuration & API Keys

All configuration is done through the `.env` file.
**Never commit your `.env` to GitHub.**

```env
# ════════════════════════════════════════
#  REQUIRED — Bot will NOT start without these
# ════════════════════════════════════════

DISCORD_TOKEN=          # Your bot token from discord.com/developers
PREFIX=!                # Default command prefix
BOT_NAME=UltimateBot    # Display name used in embeds
OWNER_ID=               # Your Discord user ID (right-click → Copy ID)

# ════════════════════════════════════════
#  REQUIRED FOR DASHBOARD
# ════════════════════════════════════════

DASHBOARD_SECRET=       # Any random string (used to sign sessions)
CLIENT_ID=              # Bot's Application ID
CLIENT_SECRET=          # OAuth2 Client Secret (Developers Portal)
REDIRECT_URI=http://localhost:5000/callback
DASHBOARD_PORT=5000

# ════════════════════════════════════════
#  OPTIONAL — Bot works without these
# ════════════════════════════════════════

OPENAI_API_KEY=         # Only needed if you add AI features
SPOTIFY_CLIENT_ID=      # Future Spotify integration
SPOTIFY_CLIENT_SECRET=  # Future Spotify integration
```

### 🔑 Where to Get Each Key

<details>
<summary><b>🤖 Discord Bot Token</b></summary>

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Click **New Application** → give it a name
3. Go to **Bot** tab → click **Add Bot**
4. Under **Token** → click **Reset Token** → copy it
5. Paste into `DISCORD_TOKEN=` in your `.env`

**Required Intents to enable:**
- ✅ Presence Intent
- ✅ Server Members Intent
- ✅ Message Content Intent

</details>

<details>
<summary><b>🆔 Client ID & Owner ID</b></summary>

- **CLIENT_ID**: Found on the **General Information** tab of your app → Application ID
- **OWNER_ID**: In Discord → right-click your username → **Copy User ID**
  - *(Enable Developer Mode: Settings → Advanced → Developer Mode)*

</details>

<details>
<summary><b>🔐 OAuth2 Client Secret (Dashboard)</b></summary>

1. In Developer Portal → go to **OAuth2** tab
2. Click **Reset Secret** → copy it → paste into `CLIENT_SECRET=`
3. Under **Redirects** → add: `http://localhost:5000/callback`
4. Set `REDIRECT_URI=http://localhost:5000/callback` in `.env`

</details>

<details>
<summary><b>🎵 FFmpeg (for Music)</b></summary>

Music playback requires **FFmpeg** installed on your system:

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
# Add to PATH environment variable
```

**Linux:**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

**Mac:**
```bash
brew install ffmpeg
```

</details>

<details>
<summary><b>🤖 OpenAI API Key (Optional)</b></summary>

Only needed if you extend the bot with AI features:
1. Go to [platform.openai.com](https://platform.openai.com)
2. API Keys → Create new secret key
3. Paste into `OPENAI_API_KEY=`

</details>

---

## 📋 Features

### 🛡️ Moderation

> **File:** `cogs/moderation.py`
> **Permissions required:** Varies per command

<details>
<summary><b>View all moderation features</b></summary>

| Feature | Description |
|---|---|
| **Kick** | Remove a member from the server with optional reason |
| **Ban** | Permanently ban a member with reason logging |
| **Temp Ban** | Ban for a specific duration — auto-unbans via background task |
| **Unban** | Unban a user by their Discord ID |
| **Mute** | Timeout a member using Discord's native timeout system |
| **Unmute** | Remove timeout from a member instantly |
| **Warn** | Issue a warning — stored in database with timestamp |
| **Warnings** | View all warnings for a specific member with full history |
| **Clear Warnings** | Remove all warnings for a member |
| **Purge** | Bulk delete 1–100 messages, optionally filter by member |
| **Slowmode** | Set channel slowmode delay (0 to disable) |
| **Lock** | Prevent `@everyone` from sending in a channel |
| **Unlock** | Re-enable sending in a locked channel |
| **Lockdown** | Lock ALL text channels simultaneously |
| **Unlockdown** | Unlock ALL text channels simultaneously |
| **Nick** | Change a member's nickname |
| **Role Toggle** | Add or remove a role from a member |
| **Auto-ban** | Automatically ban on reaching max warnings |
| **Mod Log** | Every action is logged to the configured log channel |
| **Mod History** | View full moderation history via `/modlogs` |

**Cooldowns & Safeguards:**
- Cannot moderate members with equal or higher role
- Cannot moderate the server owner
- Cannot moderate yourself
- Bot checks its own permissions before acting
- All actions logged to database + log channel

</details>

---

### 💰 Economy

> **File:** `cogs/economy.py` + `cogs/slash_commands.py`
> **Database tables:** `users`, `shop`, `inventory`

<details>
<summary><b>View all economy features</b></summary>

| Feature | Description |
|---|---|
| **Balance** | View wallet + bank + total coins |
| **Daily** | Claim 100 coins every 24h with a random bonus (0–50) |
| **Work** | Earn 50–200 coins every hour — 12 different jobs |
| **Deposit** | Move coins from wallet to bank (safe from robbery) |
| **Withdraw** | Move coins from bank to wallet |
| **Pay** | Transfer coins directly to another member |
| **Gamble** | Bet coins — 45% house edge, 3× and 50× rare multipliers |
| **Rob** | Attempt to steal coins (40% success, 20% fine on fail) |
| **Slots** | 🍒🍋🍊🍇💎7️⃣ — weighted symbol pulls with jackpots |
| **Shop** | View server item shop with stock and role rewards |
| **Buy** | Purchase items — auto-grants role if configured |
| **Inventory** | View all owned items with quantities |
| **Richest** | Top 10 wealthiest members leaderboard |
| **Rep** | Give a reputation point (24h cooldown) |

**Economy Rates (configurable in `config.py`):**

```python
DAILY_COINS      = 100       # Base daily reward
WORK_MIN_COINS   = 50        # Minimum work reward
WORK_MAX_COINS   = 200       # Maximum work reward
STARTING_BALANCE = 500       # Coins given to new users
ROB_SUCCESS_RATE = 40        # % chance rob succeeds
ROB_FINE_PERCENT = 20        # % of wallet lost on failed rob
```

**Gamble Multipliers:**
- Roll 55–79 → ×1.0 (break even)
- Roll 80–94 → ×1.5
- Roll 95–100 → ×3.0

**Slots Payouts:**
| Symbol | Jackpot Multiplier |
|---|---|
| 🍒 Cherry | ×3 |
| 🍋 Lemon | ×4 |
| 🍊 Orange | ×5 |
| 🍇 Grape | ×8 |
| 💎 Diamond | ×15 |
| 7️⃣ Seven | ×50 |

</details>

---

### ⭐ Leveling & XP

> **File:** `cogs/leveling.py`, `cogs/events.py`
> **Database tables:** `users`, `level_roles`

<details>
<summary><b>View all leveling features</b></summary>

| Feature | Description |
|---|---|
| **XP per Message** | Earn 10–25 XP per message (60s cooldown) |
| **Level Up Notification** | Auto-announced in configured channel |
| **Rank Card** | Visual rank card with XP progress bar and position |
| **Leaderboard** | Paginated top-100 XP leaderboard |
| **Level Roles** | Automatically grant roles at specific levels |
| **Message Counter** | Total messages tracked per user |
| **Rank Position** | Your exact position vs all tracked users |

**XP Formula:**

```python
# XP required to reach next level
def xp_for_level(level: int) -> int:
    return 5 * (level ** 2) + 50 * level + 100
```

| Level | XP Required |
|---|---|
| 1 → 2 | 155 XP |
| 5 → 6 | 475 XP |
| 10 → 11 | 1,100 XP |
| 25 → 26 | 4,475 XP |
| 50 → 51 | 15,100 XP |

**Configurable values in `config.py`:**
```python
XP_PER_MESSAGE  = 15    # Base XP per message
XP_COOLDOWN     = 60    # Seconds between XP gains
```

</details>

---

### 🎉 Fun & Games

> **File:** `cogs/fun.py`, `cogs/games.py`

<details>
<summary><b>View all fun & game features</b></summary>

**Fun Commands:**

| Command | Description |
|---|---|
| `!8ball` | Ask a question, get one of 14 responses |
| `!coinflip` | Heads or tails |
| `!roll [sides]` | Roll any-sided dice (default D6) |
| `!joke` | Fetch a random joke from joke API |
| `!meme` | Random meme from Reddit via meme-api |
| `!cat` | Random cat image from The Cat API |
| `!dog` | Random dog image from Dog CEO API |
| `!rps` | Rock Paper Scissors vs the bot |
| `!wyr` | Would You Rather with reaction voting |
| `!roast @user` | Roast someone with one of 10 roasts |
| `!compliment @user` | Compliment someone |
| `!rate <thing>` | Rate anything out of 10 |
| `!hug @user` | Hug someone |
| `!slap @user` | Slap someone |
| `!choose a\|b\|c` | Let the bot choose between options |
| `!reverse <text>` | Reverse any text |
| `!mock <text>` | mOcK tExT converter |

**Games:**

| Command | Description |
|---|---|
| `!tictactoe @user` | Interactive 3×3 Tic-Tac-Toe with buttons |
| `!trivia` | Fetch question from OpenTDB API — correct answer = coins |
| `!guess` | Guess a number 1–100 in 6 tries — earn coins |
| `!slots [bet]` | Slot machine with weighted symbols and jackpots |

**External APIs used:**
- `https://official-joke-api.appspot.com` — Jokes
- `https://meme-api.com/gimme` — Memes
- `https://api.thecatapi.com/v1/images/search` — Cat images
- `https://dog.ceo/api/breeds/image/random` — Dog images
- `https://opentdb.com/api.php` — Trivia questions

</details>

---

### 🎁 Giveaways

> **File:** `cogs/giveaways.py`
> **Database tables:** `giveaways`, `giveaway_entries`

<details>
<summary><b>View all giveaway features</b></summary>

| Feature | Description |
|---|---|
| **Start Giveaway** | Create with duration, winner count, and prize |
| **Button Entry** | Members click 🎉 button to enter — no reactions needed |
| **Entry Counter** | Button label updates live with entry count |
| **Auto End** | Background task checks every 15s and ends on time |
| **Winner Selection** | Random selection supporting multiple winners |
| **End Early** | Manually end any active giveaway |
| **Reroll** | Pick a new winner from existing entries |
| **List Giveaways** | View all active giveaways with entry counts |
| **Jump Links** | Direct link to the giveaway message |

**Duration Format:**
```
!gstart 1d     → 1 day
!gstart 2h30m  → 2 hours 30 minutes
!gstart 30m    → 30 minutes
!gstart 1d12h  → 1 day 12 hours
```

**Full Example:**
```bash
!gstart 24h 3 $25 Steam Gift Card
# Creates a 24-hour giveaway for 3 winners
```

</details>

---

### 🎫 Tickets

> **File:** `cogs/tickets.py`
> **Database tables:** `tickets`

<details>
<summary><b>View all ticket features</b></summary>

| Feature | Description |
|---|---|
| **Panel Setup** | Send an interactive button panel in any channel |
| **Create Ticket** | Members click button → private channel created instantly |
| **Multi-ticket** | Up to 3 open tickets per user |
| **Auto Naming** | Channel named `ticket-username` automatically |
| **Category Support** | Tickets created inside a configured category |
| **Close** | Staff or user can close — deletes channel after 5s |
| **Claim** | Staff members can claim ownership of a ticket |
| **Add Member** | Add extra members to a private ticket |
| **Remove Member** | Remove a member from the ticket |
| **Rename** | Rename the ticket channel |
| **Ticket Info** | View ticket ID, status, creator, dates |
| **Log Channel** | Log ticket creation/closure to a log channel |
| **Permission System** | Only ticket creator + staff can view |

</details>

---

### 🎵 Music

> **File:** `cogs/music.py`
> **Requires:** `yt-dlp`, `PyNaCl`, `FFmpeg`

<details>
<summary><b>View all music features</b></summary>

| Feature | Description |
|---|---|
| **Play** | Play from YouTube URL or search query |
| **Queue** | Add multiple songs — auto-plays next |
| **Now Playing** | Shows title, duration, artist, thumbnail |
| **Skip** | Skip current song and play next |
| **Pause / Resume** | Pause and resume playback |
| **Stop / Leave** | Stop music and disconnect bot |
| **Volume** | Adjust volume 0–100% |
| **Loop** | Toggle loop for current song |
| **Clear Queue** | Remove all queued songs |
| **View Queue** | See all queued tracks with positions |
| **Reconnect** | Auto-reconnects on stream drops |
| **Join** | Join your current voice channel |

**Supported Sources:**
- YouTube URLs
- YouTube search queries
- YouTube playlists (first track)

**FFmpeg Options (in `cogs/music.py`):**
```python
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options"       : "-vn",
}
```

</details>

---

### 🤖 AutoMod

> **File:** `cogs/automod.py`
> **Database tables:** `guild_settings`

<details>
<summary><b>View all AutoMod features</b></summary>

| Filter | Description | Config |
|---|---|---|
| **Anti-Link** | Delete messages containing URLs | `antilink = 1` |
| **Anti-Spam** | Delete if 5+ messages in 5 seconds | `antispam = 1` |
| **Banned Words** | Delete messages with configured words | `BANNED_WORDS` list |
| **Caps Filter** | Delete if >70% of message is caps | `CAPS_THRESHOLD = 70` |
| **Mass Mentions** | Delete if >5 user mentions | `MAX_MENTIONS = 5` |
| **Emoji Flood** | Delete if >10 emojis in one message | `MAX_EMOJIS = 10` |
| **Log Violations** | Log every violation to log channel | Auto |
| **Staff Bypass** | Members with `manage_messages` bypass all | Auto |
| **Delete & Notify** | Message deleted + user notified (5s) | Auto |

**Configurable in `config.py`:**
```python
AUTOMOD_SPAM_LIMIT    = 5    # Messages before spam trigger
AUTOMOD_SPAM_INTERVAL = 5    # Seconds window for spam check
BANNED_WORDS          = []   # Add your word list here
CAPS_THRESHOLD        = 70   # % caps to trigger filter
MAX_MENTIONS          = 5    # Max @mentions per message
MAX_EMOJIS            = 10   # Max emojis per message
```

</details>

---

### ⭐ Starboard

> **File:** `cogs/starboard.py`
> **Database tables:** `starboard`

<details>
<summary><b>View all starboard features</b></summary>

| Feature | Description |
|---|---|
| **Auto-detect** | Watches for ⭐ reactions automatically |
| **Threshold** | Configurable minimum stars (default: 3) |
| **Live Update** | Updates star count on existing starboard posts |
| **Attachments** | Images are preserved in the starboard embed |
| **Jump Link** | Direct link to the original message |
| **Deduplication** | Same message never posted twice |
| **Channel Config** | Set any channel as the starboard channel |

**Setup:**
```bash
!setstarboard #starboard 3
# Sets #starboard as destination, requires 3 ⭐ reactions
```

</details>

---

### 📊 Polls

> **File:** `cogs/polls.py`

<details>
<summary><b>View all poll features</b></summary>

| Feature | Description |
|---|---|
| **Quick Poll** | Yes/No poll with 👍👎 reactions |
| **Multi Poll** | Up to 9 options with numbered emoji reactions |
| **Straw Poll** | Live-updating vote percentages and progress bars |
| **End Poll** | Manually end any poll and display final results |
| **Live Updates** | Straw polls update in real time on each reaction |
| **Results Bar** | Visual `████░░░░` progress bars for each option |

**Poll Types:**
```bash
!poll "Is Python the best language?"
# Quick yes/no

!multipoll "Favourite colour?" "Red" "Green" "Blue"
# Multi-option with reactions

!strawpoll "Best pizza topping?" "Cheese" "Pepperoni" "Pineapple"
# Live updating results
```

</details>

---

### 🎭 Reaction Roles

> **File:** `cogs/reactionroles.py`
> **Database tables:** `reaction_roles`

<details>
<summary><b>View all reaction role features</b></summary>

| Feature | Description |
|---|---|
| **Add Reaction Role** | Attach a role to any emoji on any message |
| **Remove Reaction Role** | Remove by message ID + emoji |
| **List Reaction Roles** | View all configured reaction roles in server |
| **Create Panel** | Auto-generate a dedicated role panel message |
| **Toggle Roles** | React → get role, un-react → lose role |
| **Jump Links** | Direct links to configured messages |

**Setup:**
```bash
# 1. Create a panel or use any message
!rrpanel "Choose Your Roles"

# 2. Add roles to it
!rradd <message_id> 🎮 @Gamer
!rradd <message_id> 🎵 @Music
!rradd <message_id> 🎨 @Artist
```

</details>

---

### 💤 AFK System

> **File:** `cogs/afk.py`
> **Database tables:** `users` (afk_message, afk_since columns)

<details>
<summary><b>View all AFK features</b></summary>

| Feature | Description |
|---|---|
| **Set AFK** | Set a custom AFK message |
| **Auto Nickname** | Adds `[AFK]` prefix to nickname automatically |
| **Auto Remove** | AFK removed when user sends a message |
| **Mention Notify** | When someone @mentions an AFK user, bot replies with their message |
| **AFK Duration** | Shows how long the user has been AFK |
| **AFK Status** | Check if any member is AFK |
| **AFK List** | List all currently AFK members |
| **Admin Clear** | Staff can clear anyone's AFK |

**Usage:**
```bash
!afk studying for exams
# → Sets AFK with message "studying for exams"

# When someone mentions them:
# → "💤 Username is AFK: studying for exams (since 2h ago)"
```

</details>

---

### 💡 Suggestions

> **File:** `cogs/suggestions.py`
> **Database tables:** `suggestions`

<details>
<summary><b>View all suggestion features</b></summary>

| Feature | Description |
|---|---|
| **Submit** | Post a suggestion to the configured channel |
| **Auto Reactions** | 👍 and 👎 added automatically |
| **Suggestion ID** | Each suggestion gets a unique ID |
| **Approve** | Mark as ✅ Approved with optional staff response |
| **Deny** | Mark as ❌ Denied with optional reason |
| **Consider** | Mark as 🤔 Under Consideration |
| **Implement** | Mark as 🚀 Implemented |
| **Embed Update** | Original embed color and footer update on status change |
| **View by ID** | Look up any suggestion by ID |

**Status Flow:**
```
⏳ Pending → ✅ Approved
           → ❌ Denied
           → 🤔 Considering
           → 🚀 Implemented
```

</details>

---

### ⏰ Reminders

> **File:** `cogs/reminders.py`
> **Database tables:** `reminders`
> **Background task:** Checks every 30 seconds

<details>
<summary><b>View all reminder features</b></summary>

| Feature | Description |
|---|---|
| **Set Reminder** | Set a reminder with flexible duration format |
| **List Reminders** | View all your active reminders with countdown |
| **Cancel** | Cancel any reminder by ID |
| **Background Check** | Bot checks for due reminders every 30 seconds |
| **Channel Delivery** | Reminder fires in the channel it was set |
| **User Ping** | Pings the user when reminder fires |

**Duration Formats:**
```bash
!remind 30m Take a break
!remind 1h30m Call mom
!remind 2d Submit assignment
!remind 1d12h30m Complex reminder
```

</details>

---

### 📋 Advanced Logging

> **File:** `cogs/logging.py`
> **Requires:** Log channel configured via `!setlog #channel`

<details>
<summary><b>View all logged events</b></summary>

| Event | What's Logged |
|---|---|
| **Message Deleted** | Author, channel, full content |
| **Message Edited** | Before + after content, jump link |
| **Member Joined** | Account age, member count |
| **Member Left** | Time in server, roles held |
| **Nickname Changed** | Before and after nickname |
| **Roles Updated** | Added and removed roles |
| **Role Created** | Name, color, permissions |
| **Role Deleted** | Name and ID |
| **Channel Created** | Name, type, category |
| **Channel Deleted** | Name and ID |
| **Voice Join** | User + channel |
| **Voice Leave** | User + channel |
| **Voice Move** | From → to channel |
| **Member Banned** | User info |
| **Member Unbanned** | User info |
| **Mod Actions** | All moderation commands logged |

All log embeds include:
- ⏰ Timestamp
- 👤 User ID in footer
- 🖼️ User avatar thumbnail
- 🔗 Jump links where applicable

</details>

---

### 👋 Welcome System

> **File:** `cogs/welcomer.py`
> **Database tables:** `guild_settings`

<details>
<summary><b>View all welcome features</b></summary>

| Feature | Description |
|---|---|
| **Welcome Message** | Custom embed on member join |
| **Leave Message** | Custom embed on member leave |
| **Template Variables** | `{user}` `{name}` `{server}` `{count}` `{id}` |
| **Member Count** | Shows your member number (#2,341) |
| **Account Age** | Shows how old the Discord account is |
| **Server Icon** | Displayed in embed author |
| **Banner** | Server banner shown if available |
| **Auto Role** | Automatically assign a role on join |
| **Test Command** | Preview welcome/leave without waiting |
| **Preview** | See formatted message + available variables |

**Example welcome message:**
```
Welcome {user} to {server}! You are member #{count}! 🎉
```

</details>

---

### 🏷️ Tags

> **File:** `cogs/slash_commands.py` (`/tag` group)
> **Database tables:** `tags`

<details>
<summary><b>View all tag features</b></summary>

| Feature | Description |
|---|---|
| **Create** | Create a custom tag with name + content |
| **Get** | Retrieve and display a tag |
| **List** | List all server tags with use counts |
| **Delete** | Delete your own tag (or admin can delete any) |
| **Use Counter** | Tracks how many times each tag is used |
| **Ownership** | Only creator or admins can delete |

**Usage:**
```bash
/tag create name:rules content:Please read the rules in #rules!
/tag get name:rules
/tag list
/tag delete name:rules
```

</details>

---

### 🔧 Utility

> **File:** `cogs/utility.py`

<details>
<summary><b>View all utility features</b></summary>

| Command | Description |
|---|---|
| `!help [command]` | Paginated help menu — all cogs/commands |
| `!help <command>` | Detailed info on a specific command |
| `!profile [@user]` | Full profile card with XP, coins, rep, warnings |
| `!serverinfo` | Full server info — members, channels, boosts, etc. |
| `!userinfo [@user]` | Account age, join date, roles, status |
| `!avatar [@user]` | Full-size avatar with PNG/JPG/WEBP links |
| `!ping` | Bot latency with color-coded indicator |
| `!botinfo` | Bot stats — servers, users, Python/discord.py version |
| `!uptime` | How long the bot has been running |
| `!invite` | Bot invite link with admin permissions |

</details>

---

### ⚙️ Admin

> **File:** `cogs/admin.py`
> **Required permission:** `Administrator`

<details>
<summary><b>View all admin features</b></summary>

| Command | Description |
|---|---|
| `!setwelcome #ch` | Set welcome channel |
| `!setleave #ch` | Set leave/goodbye channel |
| `!setlog #ch` | Set mod log channel |
| `!setstarboard #ch [n]` | Set starboard channel + threshold |
| `!setsuggestions #ch` | Set suggestion submission channel |
| `!setlevelup #ch` | Set level-up notification channel |
| `!setautorole @role` | Set role given to new members |
| `!setwelcomemsg <text>` | Set welcome message template |
| `!setmaxwarnings <n>` | Set max warnings before auto-ban |
| `!additem` | Add an item to the economy shop |
| `!removeitem <name>` | Remove an item from the shop |
| `!addcoins @user <n>` | Give a member coins |
| `!removecoins @user <n>` | Take coins from a member |
| `!setxp @user <n>` | Set a member's XP and level |
| `!resetuser @user` | Reset all data for a member |
| `!announce #ch <msg>` | Send a branded announcement |
| `!settings` | View all current server settings |
| `!setstatus <text>` | Change bot's Discord status (owner only) |

</details>

---

### 🌐 Web Dashboard

> **Files:** `dashboard/app.py`, `dashboard/routes/`
> **URL:** `http://localhost:5000` (or your domain)

<details>
<summary><b>View all dashboard features</b></summary>

| Page | Features |
|---|---|
| **Landing Page** | Bot stats, feature showcase, login button |
| **Login** | Discord OAuth2 — secure, no password stored |
| **Server Select** | Shows only servers you manage AND bot is in |
| **Overview** | Members, messages, economy, warnings, tickets, giveaways |
| **Leaderboard** | Full paginated XP table with avatars |
| **Settings** | Live settings editor — saves via REST API |

**REST API Endpoints:**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/botstats` | Bot servers, users, latency |
| `GET` | `/api/stats/<guild_id>` | Guild statistics |
| `GET` | `/api/leaderboard/<guild_id>` | XP leaderboard JSON |
| `GET` | `/api/settings/<guild_id>` | Current guild settings |
| `POST` | `/api/settings/<guild_id>` | Update guild settings |
| `GET` | `/api/users/<guild_id>` | All tracked users |
| `POST` | `/api/coins/<guild_id>/<user_id>` | Add/remove coins |
| `GET` | `/api/giveaways/<guild_id>` | Active giveaways |

**OAuth2 Flow:**
```
User clicks Login
    → Redirected to Discord OAuth2
    → Authorizes bot
    → Redirected to /callback
    → Bot fetches user + guilds
    → Session stored securely
    → Redirected to /dashboard
```

</details>

---

## 📖 Commands Reference

### 🛡️ Moderation Commands

| Command | Aliases | Permission | Description |
|---|---|---|---|
| `!kick @user [reason]` | — | Kick Members | Kick a member |
| `!ban @user [reason]` | — | Ban Members | Ban a member |
| `!tempban @user <dur> [reason]` | — | Ban Members | Temp ban (e.g. `1d`) |
| `!unban <user_id>` | — | Ban Members | Unban by ID |
| `!mute @user [min] [reason]` | — | Manage Roles | Timeout a member |
| `!unmute @user` | — | Manage Roles | Remove timeout |
| `!warn @user [reason]` | — | Manage Messages | Issue a warning |
| `!warnings @user` | — | Manage Messages | View warnings |
| `!clearwarnings @user` | `clearwarns` | Administrator | Clear all warnings |
| `!purge [n] [@user]` | `clear` | Manage Messages | Delete messages |
| `!slowmode [seconds]` | — | Manage Channels | Set slowmode |
| `!lock [#channel]` | — | Manage Channels | Lock channel |
| `!unlock [#channel]` | — | Manage Channels | Unlock channel |
| `!lockdown` | — | Administrator | Lock all channels |
| `!unlockdown` | — | Administrator | Unlock all channels |
| `!nick @user [nickname]` | — | Manage Nicknames | Change nickname |
| `!role @user @role` | — | Manage Roles | Toggle a role |

---

### 💰 Economy Commands

| Command | Aliases | Description |
|---|---|---|
| `!balance [@user]` | `bal` `wallet` `money` | Check balance |
| `!daily` | — | Claim daily coins |
| `!work` | — | Work for coins (1h cooldown) |
| `!deposit <amount/all>` | `dep` | Deposit to bank |
| `!withdraw <amount/all>` | `with` | Withdraw from bank |
| `!pay @user <amount>` | `give` `transfer` | Send coins |
| `!gamble <amount/all>` | `bet` `g` | Gamble coins |
| `!rob @user` | `steal` | Rob a member |
| `!slots [bet]` | — | Slot machine |
| `!shop` | — | View server shop |
| `!buy <item>` | — | Buy a shop item |
| `!inventory [@user]` | `inv` `bag` | View inventory |
| `!richest` | `rich` `topmoney` | Rich leaderboard |
| `!rep @user` | — | Give reputation |

---

### ⭐ Leveling Commands

| Command | Aliases | Description |
|---|---|---|
| `!rank [@user]` | `level` `xp` `lvl` | View rank card |
| `!leaderboard` | `lb` `top` `levels` | XP leaderboard |
| `!addlevelrole <level> @role` | — | Add level role reward |
| `!removelevelrole <level>` | — | Remove level role |
| `!levelroles` | — | List all level roles |

---

### 🎉 Fun Commands

| Command | Aliases | Description |
|---|---|---|
| `!8ball <question>` | `eightball` | Magic 8-ball |
| `!coinflip` | `flip` `coin` | Heads or tails |
| `!roll [sides]` | `dice` | Roll a dice |
| `!joke` | — | Random joke |
| `!meme` | — | Random meme |
| `!cat` | — | Random cat |
| `!dog` | — | Random dog |
| `!rps <rock/paper/scissors>` | — | RPS vs bot |
| `!wyr` | — | Would You Rather |
| `!roast [@user]` | — | Roast someone |
| `!compliment [@user]` | `praise` | Compliment someone |
| `!rate <thing>` | — | Rate something |
| `!hug @user` | — | Hug someone |
| `!slap @user` | — | Slap someone |
| `!choose a\|b\|c` | — | Pick an option |
| `!reverse <text>` | — | Reverse text |
| `!mock <text>` | — | mOcK tExT |

---

### 🎮 Game Commands

| Command | Description |
|---|---|
| `!tictactoe @user` | Play Tic-Tac-Toe |
| `!trivia` | Answer a trivia question |
| `!guess` | Number guessing game |
| `!slots [bet]` | Slot machine game |

---

### 🎁 Giveaway Commands

| Command | Aliases | Permission | Description |
|---|---|---|---|
| `!gstart <dur> <winners> <prize>` | `gcreate` | Manage Guild | Start giveaway |
| `!gend <message_id>` | `endgiveaway` | Manage Guild | End early |
| `!greroll <message_id>` | `reroll` | Manage Guild | Reroll winner |
| `!glist` | — | Everyone | List active giveaways |

---

### 🎫 Ticket Commands

| Command | Aliases | Permission | Description |
|---|---|---|---|
| `!ticketsetup [category] [#log]` | `setuptickets` | Administrator | Create ticket panel |
| `!close` | — | Everyone (own ticket) | Close ticket |
| `!tadd @user` | `ticketadd` | Manage Messages | Add to ticket |
| `!tremove @user` | `ticketremove` | Manage Messages | Remove from ticket |
| `!claim` | — | Manage Messages | Claim ticket |
| `!trename <name>` | — | Manage Channels | Rename channel |
| `!tinfo` | `ticketinfo` | Everyone | View ticket info |

---

### 🎵 Music Commands

| Command | Aliases | Description |
|---|---|---|
| `!join` | `connect` `j` | Join voice channel |
| `!leave` | `disconnect` `dc` `stop` | Leave + clear queue |
| `!play <query/url>` | `p` | Play a song |
| `!skip` | `s` `next` | Skip current song |
| `!pause` | — | Pause playback |
| `!resume` | `unpause` | Resume playback |
| `!queue` | `q` `np` | View queue |
| `!volume <0-100>` | `vol` | Set volume |
| `!loop` | — | Toggle loop |
| `!clearqueue` | `cq` | Clear queue |

---

### 📊 Poll Commands

| Command | Aliases | Description |
|---|---|---|
| `!poll "Question"` | `vote` | Yes/No poll |
| `!multipoll "Q" "A" "B" "C"` | `mpoll` | Multi-option poll |
| `!strawpoll "Q" "A" "B" "C"` | — | Live-updating poll |
| `!endpoll <message_id>` | — | End poll + show results |

---

### 🎭 Reaction Role Commands

| Command | Aliases | Permission | Description |
|---|---|---|---|
| `!rradd <msg_id> <emoji> @role` | `addreactionrole` | Manage Roles | Add reaction role |
| `!rrremove <msg_id> <emoji>` | `removereactionrole` | Manage Roles | Remove reaction role |
| `!rrlist` | `reactionroles` | Everyone | List reaction roles |
| `!rrpanel [title]` | — | Manage Roles | Create role panel |

---

### 💤 AFK Commands

| Command | Aliases | Description |
|---|---|---|
| `!afk [message]` | — | Set AFK status |
| `!afkstatus [@user]` | — | Check AFK status |
| `!afklist` | — | List AFK members |
| `!afkclear @user` | `removeafk` | Clear AFK (staff) |

---

### 💡 Suggestion Commands

| Command | Aliases | Permission | Description |
|---|---|---|---|
| `!suggest <text>` | `suggestion` | Everyone | Submit suggestion |
| `!approve <id> [response]` | — | Manage Guild | Approve |
| `!deny <id> [response]` | — | Manage Guild | Deny |
| `!consider <id> [response]` | — | Manage Guild | Mark considering |
| `!implement <id> [response]` | — | Manage Guild | Mark implemented |
| `!viewsuggestion <id>` | `sug` | Everyone | View by ID |

---

### ⏰ Reminder Commands

| Command | Aliases | Description |
|---|---|---|
| `!remind <duration> <message>` | `reminder` `remindme` | Set a reminder |
| `!reminders` | `myreminders` | List your reminders |
| `!cancelreminder <id>` | `delreminder` | Cancel a reminder |

---

### 🔧 Utility Commands

| Command | Aliases | Description |
|---|---|---|
| `!help [command]` | `h` `commands` | Help menu |
| `!profile [@user]` | `p` `me` | Profile card |
| `!serverinfo` | `si` `server` | Server info |
| `!userinfo [@user]` | `ui` `whois` `user` | User info |
| `!avatar [@user]` | `av` `pfp` `icon` | View avatar |
| `!ping` | `latency` | Bot latency |
| `!botinfo` | `about` `info` | Bot information |
| `!uptime` | — | Bot uptime |
| `!invite` | — | Bot invite link |

---

### 👋 Welcome Commands

| Command | Permission | Description |
|---|---|---|
| `!testwelcome` | Administrator | Test welcome message |
| `!testleave` | Administrator | Test leave message |
| `!previewwelcome` | Administrator | Preview with variables |

---

### ⚙️ Admin Commands

| Command | Permission | Description |
|---|---|---|
| `!setwelcome #ch` | Administrator | Set welcome channel |
| `!setleave #ch` | Administrator | Set leave channel |
| `!setlog #ch` | Administrator | Set log channel |
| `!setstarboard #ch [n]` | Administrator | Set starboard |
| `!setsuggestions #ch` | Administrator | Set suggestions channel |
| `!setlevelup #ch` | Administrator | Set level up channel |
| `!setautorole @role` | Administrator | Set join role |
| `!setwelcomemsg <text>` | Administrator | Set welcome message |
| `!setmaxwarnings <n>` | Administrator | Set max warnings |
| `!additem <name> <price>` | Administrator | Add shop item |
| `!removeitem <name>` | Administrator | Remove shop item |
| `!addcoins @user <n>` | Administrator | Add coins |
| `!removecoins @user <n>` | Administrator | Remove coins |
| `!setxp @user <n>` | Administrator | Set XP |
| `!resetuser @user` | Administrator | Reset user data |
| `!announce #ch <msg>` | Administrator | Send announcement |
| `!settings` | Administrator | View server settings |
| `!setstatus <text>` | Bot Owner | Set bot status |

---

## ⚡ Slash Commands

All slash commands mirror prefix commands but with Discord's native UI.

<details>
<summary><b>View all slash commands</b></summary>

| Command | Description |
|---|---|
| `/ping` | Check latency |
| `/help` | Paginated help (4 pages with navigation) |
| `/profile [member]` | View profile |
| `/serverinfo` | Server information |
| `/userinfo [member]` | User information |
| `/avatar [member]` | View avatar |
| `/afk [message]` | Set AFK |
| `/remind <duration> <message>` | Set reminder |
| `/balance [member]` | Check balance |
| `/daily` | Daily coins |
| `/work` | Work for coins |
| `/deposit <amount>` | Deposit to bank |
| `/withdraw <amount>` | Withdraw from bank |
| `/pay <member> <amount>` | Pay someone |
| `/gamble <amount>` | Gamble coins |
| `/rob <member>` | Rob someone |
| `/shop` | View shop |
| `/buy <item>` | Buy item |
| `/inventory` | View inventory |
| `/richest` | Rich leaderboard |
| `/rep <member>` | Give reputation |
| `/rank [member]` | View rank |
| `/leaderboard` | XP leaderboard |
| `/kick <member> [reason]` | Kick |
| `/ban <member> [reason]` | Ban with confirmation |
| `/tempban <member> <dur> [reason]` | Temp ban |
| `/mute <member> [min] [reason]` | Mute |
| `/unmute <member>` | Unmute |
| `/warn <member> [reason]` | Warn |
| `/warnings <member>` | View warnings |
| `/purge <amount>` | Bulk delete |
| `/lock` | Lock channel |
| `/unlock` | Unlock channel |
| `/slowmode [seconds]` | Set slowmode |
| `/modlogs [member]` | Paginated mod logs |
| `/8ball <question>` | Magic 8-ball |
| `/coinflip` | Flip a coin |
| `/roll [sides]` | Roll dice |
| `/rps <choice>` | Rock Paper Scissors with choices menu |
| `/meme` | Random meme |
| `/joke` | Random joke |
| `/roast [member]` | Roast someone |
| `/wyr` | Would You Rather |
| `/slots [bet]` | Slot machine |
| `/tictactoe <opponent>` | Tic-Tac-Toe |
| `/trivia` | Trivia question |
| `/guess` | Guess the number |
| `/giveaway start` | Start giveaway |
| `/giveaway end` | End giveaway |
| `/giveaway reroll` | Reroll winner |
| `/ticket setup` | Setup ticket panel |
| `/ticket close` | Close ticket |
| `/ticket add <member>` | Add to ticket |
| `/suggest <suggestion>` | Submit suggestion |
| `/suggestion approve <id>` | Approve |
| `/suggestion deny <id>` | Deny |
| `/tag create <name> <content>` | Create tag |
| `/tag get <name>` | Get tag |
| `/tag list` | List tags |
| `/tag delete <name>` | Delete tag |
| `/poll <question> <opt1> <opt2> ...` | Create poll |
| `/stats` | Server statistics |
| `/setup welcome <channel> [msg]` | Setup welcome |
| `/setup logs <channel>` | Setup logs |
| `/setup autorole <role>` | Setup auto role |
| `/setup starboard <channel> [n]` | Setup starboard |
| `/setup suggestions <channel>` | Setup suggestions |
| `/setup levelup [channel]` | Setup level up |
| `/setup automod [enabled] [antilink] [antispam]` | Setup automod |
| `/addcoins <member> <amount>` | Add coins |
| `/setxp <member> <amount>` | Set XP |
| `/announce <channel> <message>` | Announce |
| `/levelrole <level> <role>` | Add level role |
| `/reactionrole <msg_id> <emoji> <role>` | Add reaction role |

</details>

---

## 🗄️ Database Schema

> **Engine:** SQLite via `aiosqlite`
> **File:** `database/bot.db` (auto-created on first run)

<details>
<summary><b>View full database schema</b></summary>

```sql
-- Users (economy + xp + afk)
users (user_id, guild_id, xp, level, coins, bank, warnings,
       reputation, messages, last_daily, last_work, last_xp,
       last_rob, last_rep, afk_message, afk_since, created_at)

-- Guild configuration
guild_settings (guild_id, prefix, welcome_channel, leave_channel,
                log_channel, starboard_channel, suggestion_channel,
                ticket_category, ticket_log, mute_role, auto_role,
                level_up_channel, welcome_message, leave_message,
                automod_enabled, antilink, antispam,
                max_warnings, starboard_threshold)

-- Moderation warnings
warnings (id, user_id, guild_id, reason, moderator, created_at)

-- Mod action history
mod_logs (id, guild_id, action, target_id, moderator_id,
          reason, duration, created_at)

-- Giveaways
giveaways (id, guild_id, channel_id, message_id, host_id,
           prize, winners, end_time, ended, created_at)

-- Giveaway entries
giveaway_entries (id, giveaway_id, user_id) UNIQUE

-- Support tickets
tickets (id, guild_id, channel_id, user_id, subject,
         status, claimed_by, created_at, closed_at)

-- Economy shop
shop (id, guild_id, item_name, item_desc, price,
      role_id, stock, created_at)

-- User inventory
inventory (id, user_id, guild_id, item_name, quantity)

-- Starboard
starboard (id, guild_id, original_msg_id, starboard_msg_id,
           channel_id, author_id, star_count)

-- Reminders
reminders (id, user_id, channel_id, guild_id, message,
           remind_at, created_at, completed)

-- Suggestions
suggestions (id, guild_id, user_id, message_id, content,
             status, response, upvotes, downvotes, created_at)

-- Reaction roles
reaction_roles (id, guild_id, channel_id, message_id, emoji, role_id)

-- Level role rewards
level_roles (id, guild_id, level, role_id) UNIQUE

-- Custom tags
tags (id, guild_id, name, content, author_id, uses, created_at)

-- Polls
polls (id, guild_id, channel_id, message_id, question,
       options, end_time, ended, author_id, created_at)

-- Temporary bans
temp_bans (id, guild_id, user_id, moderator, reason,
           unban_at, created_at)
```

</details>

---

## 🔧 Background Tasks

The bot runs the following background tasks automatically:

| Task | Interval | Description |
|---|---|---|
| `check_reminders` | Every 30s | Fire due reminders |
| `check_giveaways` | Every 15s | End expired giveaways |
| `check_temp_bans` | Every 60s | Unban expired temp bans |

---

## 📦 Dependencies

```txt
discord.py==2.3.2      # Core Discord library
python-dotenv==1.0.0   # Load .env file
aiosqlite==0.19.0      # Async SQLite database
yt-dlp==2023.11.16     # YouTube audio download (music)
PyNaCl==1.5.0          # Voice encryption (music)
aiohttp==3.9.1         # Async HTTP requests (APIs)
Pillow==10.1.0         # Image processing
quart==0.19.4          # Async web framework (dashboard)
quart-cors==0.7.0      # CORS for dashboard API
humanize==4.9.0        # Human-readable time/numbers
parsedatetime==2.6     # Parse natural time strings
python-dateutil==2.8.2 # Date utilities
jinja2==3.1.2          # HTML templating (dashboard)
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines

- Follow the existing cog structure
- Use `utils/embeds.py` for all embed responses
- Add prefix + slash version of new commands
- Test before submitting PR

---

## ❓ FAQ

<details>
<summary><b>The bot doesn't respond to commands</b></summary>

- Check `MESSAGE_CONTENT` intent is enabled in Developer Portal
- Ensure the bot has permissions in that channel
- Verify the prefix in `.env` matches what you're using

</details>

<details>
<summary><b>Music doesn't work</b></summary>

- Install FFmpeg and make sure it's in your system PATH
- Run `ffmpeg -version` to verify installation
- Make sure `yt-dlp` is installed: `pip install yt-dlp`

</details>

<details>
<summary><b>Dashboard OAuth2 not working</b></summary>

- In Developer Portal → OAuth2 → add `http://localhost:5000/callback` to redirects
- Make sure `CLIENT_ID`, `CLIENT_SECRET`, and `REDIRECT_URI` match exactly in `.env`

</details>

<details>
<summary><b>Slash commands not showing</b></summary>

- Wait up to 1 hour for global sync
- Or add guild-specific sync for instant testing
- Make sure `applications.commands` scope is in the invite URL

</details>

<details>
<summary><b>Bot can't mute members</b></summary>

- The bot's role must be HIGHER than the target's highest role
- Enable `Moderate Members` permission in server settings

</details>

---

## 📜 License

```
MIT License

Copyright (c) 2024 UltimateBot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

<div align="center">

**Made with ❤️ and Python**

[![Discord](https://img.shields.io/badge/Join_Support_Server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/)
[![GitHub](https://img.shields.io/badge/Star_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/compromisee/DiBot)


⭐ **Star this repo if it helped you!** ⭐

</div>
````
