from quart import Quart, render_template, redirect, request, session, url_for, jsonify
from quart_cors import cors
import aiohttp
import config
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Quart(__name__, template_folder="templates", static_folder="static")
app.secret_key = config.DASHBOARD_SECRET
app = cors(app)

DISCORD_API = "https://discord.com/api/v10"
OAUTH_URL = (
    f"https://discord.com/api/oauth2/authorize?client_id={config.CLIENT_ID}"
    f"&redirect_uri={config.REDIRECT_URI}&response_type=code&scope=identify+guilds"
)

bot_instance = None

def set_bot(bot):
    global bot_instance
    bot_instance = bot

# ── Auth Helpers ─────────────────────
async def get_token(code):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{DISCORD_API}/oauth2/token", data={
            "client_id": config.CLIENT_ID,
            "client_secret": config.CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config.REDIRECT_URI,
        }) as resp:
            return await resp.json()

async def get_user(token):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{DISCORD_API}/users/@me", headers={
            "Authorization": f"Bearer {token}"
        }) as resp:
            return await resp.json()

async def get_user_guilds(token):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{DISCORD_API}/users/@me/guilds", headers={
            "Authorization": f"Bearer {token}"
        }) as resp:
            return await resp.json()

# ── Routes ────────────────────────────
@app.route("/")
async def index():
    user = session.get("user")
    return await render_template("index.html", user=user, bot=bot_instance)

@app.route("/login")
async def login():
    return redirect(OAUTH_URL)

@app.route("/callback")
async def callback():
    code = request.args.get("code")
    if not code:
        return redirect(url_for("index"))

    token_data = await get_token(code)
    access_token = token_data.get("access_token")
    if not access_token:
        return redirect(url_for("index"))

    user = await get_user(access_token)
    guilds = await get_user_guilds(access_token)

    session["user"] = user
    session["token"] = access_token
    session["guilds"] = guilds
    return redirect(url_for("dashboard"))

@app.route("/logout")
async def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
async def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    guilds = session.get("guilds", [])
    bot_guilds = [g.id for g in bot_instance.guilds] if bot_instance else []
    mutual = [g for g in guilds if int(g["id"]) in bot_guilds and (int(g["permissions"]) & 0x20) == 0x20]

    return await render_template("dashboard.html", user=user, guilds=mutual)

@app.route("/guild/<int:guild_id>")
async def guild_page(guild_id):
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    guild = bot_instance.get_guild(guild_id) if bot_instance else None
    if not guild:
        return redirect(url_for("dashboard"))

    settings = await bot_instance.db.get_guild_settings(guild_id)
    stats = await bot_instance.db.get_guild_stats(guild_id)
    leaderboard = await bot_instance.db.get_leaderboard(guild_id, "xp", 20)

    members = []
    for row in leaderboard:
        member = guild.get_member(row["user_id"])
        if member:
            row["name"] = member.display_name
            row["avatar"] = str(member.display_avatar.url)
            members.append(row)

    return await render_template("guild.html", user=user, guild=guild, settings=settings, stats=stats, leaderboard=members)

@app.route("/leaderboard/<int:guild_id>")
async def leaderboard_page(guild_id):
    user = session.get("user")
    guild = bot_instance.get_guild(guild_id) if bot_instance else None
    if not guild:
        return redirect(url_for("dashboard"))

    lb = await bot_instance.db.get_leaderboard(guild_id, "xp", 50)
    members = []
    for row in lb:
        member = guild.get_member(row["user_id"])
        if member:
            row["name"] = member.display_name
            row["avatar"] = str(member.display_avatar.url)
            members.append(row)

    return await render_template("leaderboard.html", user=user, guild=guild, leaderboard=members)

@app.route("/settings/<int:guild_id>")
async def settings_page(guild_id):
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    guild = bot_instance.get_guild(guild_id) if bot_instance else None
    if not guild:
        return redirect(url_for("dashboard"))
    settings = await bot_instance.db.get_guild_settings(guild_id)
    return await render_template("settings.html", user=user, guild=guild, settings=settings)

# ── API Routes ────────────────────────
@app.route("/api/settings/<int:guild_id>", methods=["POST"])
async def api_update_settings(guild_id):
    user = session.get("user")
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = await request.get_json()
    allowed = ["prefix", "welcome_channel", "log_channel", "automod_enabled", "antilink", "antispam", "max_warnings", "starboard_threshold"]
    updates = {k: v for k, v in data.items() if k in allowed}

    if updates:
        await bot_instance.db.update_guild_settings(guild_id, **updates)

    return jsonify({"success": True})

@app.route("/api/stats/<int:guild_id>")
async def api_stats(guild_id):
    stats = await bot_instance.db.get_guild_stats(guild_id)
    return jsonify(stats)

@app.route("/api/leaderboard/<int:guild_id>")
async def api_leaderboard(guild_id):
    lb = await bot_instance.db.get_leaderboard(guild_id, "xp", 50)
    guild = bot_instance.get_guild(guild_id)
    for row in lb:
        member = guild.get_member(row["user_id"]) if guild else None
        row["name"] = member.display_name if member else f"User {row['user_id']}"
    return jsonify(lb)

async def run_dashboard():
    await app.run_task(host="0.0.0.0", port=config.DASHBOARD_PORT)