from quart import Blueprint, render_template, redirect, session, url_for
import config

# ─────────────────────────────────────────
#  Page / View Routes
# ─────────────────────────────────────────

views_bp = Blueprint("views", __name__)
bot_ref  = None


def set_bot(bot):
    global bot_ref
    bot_ref = bot


def _mutual_guilds(guilds: list) -> list:
    """Return guilds the user manages AND the bot is in."""
    if not bot_ref or not guilds:
        return []
    bot_guild_ids = {g.id for g in bot_ref.guilds}
    return [
        g for g in guilds
        if int(g["id"]) in bot_guild_ids and (int(g.get("permissions", 0)) & 0x20) == 0x20
    ]


# ── Home ─────────────────────────────────
@views_bp.route("/")
async def index():
    user = session.get("user")
    return await render_template(
        "index.html",
        user    = user,
        bot     = bot_ref,
        title   = f"{config.BOT_NAME} — Dashboard"
    )


# ── Dashboard ────────────────────────────
@views_bp.route("/dashboard")
async def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    guilds = _mutual_guilds(session.get("guilds", []))
    return await render_template(
        "dashboard.html",
        user   = user,
        guilds = guilds,
        title  = "Your Servers"
    )


# ── Guild Overview ────────────────────────
@views_bp.route("/guild/<int:guild_id>")
async def guild(guild_id: int):
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    if not bot_ref:
        return redirect(url_for("views.dashboard"))

    guild_obj = bot_ref.get_guild(guild_id)
    if not guild_obj:
        return redirect(url_for("views.dashboard"))

    settings    = await bot_ref.db.get_guild_settings(guild_id)
    stats       = await bot_ref.db.get_guild_stats(guild_id)
    leaderboard = await bot_ref.db.get_leaderboard(guild_id, "xp", 10)

    members = []
    for row in leaderboard:
        member = guild_obj.get_member(row["user_id"])
        if member:
            row["name"]   = member.display_name
            row["avatar"] = str(member.display_avatar.url)
            members.append(row)

    return await render_template(
        "guild.html",
        user        = user,
        guild       = guild_obj,
        settings    = settings,
        stats       = stats,
        leaderboard = members,
        title       = guild_obj.name
    )


# ── Leaderboard ──────────────────────────
@views_bp.route("/leaderboard/<int:guild_id>")
async def leaderboard(guild_id: int):
    user      = session.get("user")
    guild_obj = bot_ref.get_guild(guild_id) if bot_ref else None

    if not guild_obj:
        return redirect(url_for("views.dashboard"))

    lb      = await bot_ref.db.get_leaderboard(guild_id, "xp", 100)
    members = []
    for row in lb:
        member = guild_obj.get_member(row["user_id"])
        if member:
            row["name"]   = member.display_name
            row["avatar"] = str(member.display_avatar.url)
            members.append(row)

    return await render_template(
        "leaderboard.html",
        user        = user,
        guild       = guild_obj,
        leaderboard = members,
        title       = f"{guild_obj.name} Leaderboard"
    )


# ── Settings ─────────────────────────────
@views_bp.route("/settings/<int:guild_id>")
async def settings(guild_id: int):
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    guild_obj = bot_ref.get_guild(guild_id) if bot_ref else None
    if not guild_obj:
        return redirect(url_for("views.dashboard"))

    settings_data = await bot_ref.db.get_guild_settings(guild_id)

    return await render_template(
        "settings.html",
        user     = user,
        guild    = guild_obj,
        settings = settings_data,
        title    = f"{guild_obj.name} Settings"
    )