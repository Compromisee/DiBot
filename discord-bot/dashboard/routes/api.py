from quart import Blueprint, jsonify, request, session
import config

# ─────────────────────────────────────────
#  API Routes (REST)
# ─────────────────────────────────────────

api_bp  = Blueprint("api", __name__, url_prefix="/api")
bot_ref = None


def set_bot(bot):
    global bot_ref
    bot_ref = bot


def require_auth(f):
    from functools import wraps
    @wraps(f)
    async def decorated(*args, **kwargs):
        if not session.get("user"):
            return jsonify({"error": "Unauthorized"}), 401
        return await f(*args, **kwargs)
    return decorated


# ── Bot Stats ────────────────────────────
@api_bp.route("/botstats")
async def botstats():
    if not bot_ref:
        return jsonify({"error": "Bot not connected"}), 503
    return jsonify({
        "guilds"  : len(bot_ref.guilds),
        "users"   : len(bot_ref.users),
        "latency" : round(bot_ref.latency * 1000),
        "commands": len(bot_ref.commands),
    })


# ── Guild Stats ──────────────────────────
@api_bp.route("/stats/<int:guild_id>")
@require_auth
async def guild_stats(guild_id: int):
    if not bot_ref:
        return jsonify({"error": "Bot not connected"}), 503
    stats = await bot_ref.db.get_guild_stats(guild_id)
    return jsonify(stats)


# ── Leaderboard ──────────────────────────
@api_bp.route("/leaderboard/<int:guild_id>")
async def leaderboard(guild_id: int):
    if not bot_ref:
        return jsonify({"error": "Bot not connected"}), 503

    lb    = await bot_ref.db.get_leaderboard(guild_id, "xp", 50)
    guild = bot_ref.get_guild(guild_id)

    for row in lb:
        member   = guild.get_member(row["user_id"]) if guild else None
        row["name"]   = member.display_name if member else f"User {row['user_id']}"
        row["avatar"] = str(member.display_avatar.url) if member else ""

    return jsonify(lb)


# ── Guild Settings (GET) ──────────────────
@api_bp.route("/settings/<int:guild_id>", methods=["GET"])
@require_auth
async def get_settings(guild_id: int):
    if not bot_ref:
        return jsonify({"error": "Bot not connected"}), 503
    settings = await bot_ref.db.get_guild_settings(guild_id)
    return jsonify(settings)


# ── Guild Settings (POST / Update) ────────
@api_bp.route("/settings/<int:guild_id>", methods=["POST"])
@require_auth
async def update_settings(guild_id: int):
    if not bot_ref:
        return jsonify({"error": "Bot not connected"}), 503

    data    = await request.get_json()
    allowed = [
        "prefix", "welcome_channel", "log_channel",
        "automod_enabled", "antilink", "antispam",
        "max_warnings", "starboard_threshold",
        "welcome_message", "leave_message"
    ]
    updates = {k: v for k, v in data.items() if k in allowed}

    if updates:
        await bot_ref.db.update_guild_settings(guild_id, **updates)

    return jsonify({"success": True, "updated": list(updates.keys())})


# ── Users ─────────────────────────────────
@api_bp.route("/users/<int:guild_id>")
@require_auth
async def guild_users(guild_id: int):
    if not bot_ref:
        return jsonify({"error": "Bot not connected"}), 503

    users = await bot_ref.db.get_all_users(guild_id)
    guild = bot_ref.get_guild(guild_id)

    for u in users:
        member   = guild.get_member(u["user_id"]) if guild else None
        u["name"]   = member.display_name if member else f"User {u['user_id']}"
        u["avatar"] = str(member.display_avatar.url) if member else ""

    return jsonify(users)


# ── Economy: Add Coins ────────────────────
@api_bp.route("/coins/<int:guild_id>/<int:user_id>", methods=["POST"])
@require_auth
async def add_coins(guild_id: int, user_id: int):
    if not bot_ref:
        return jsonify({"error": "Bot not connected"}), 503

    data   = await request.get_json()
    amount = data.get("amount", 0)

    if not isinstance(amount, int) or amount == 0:
        return jsonify({"error": "Invalid amount"}), 400

    user_data = await bot_ref.db.get_user(user_id, guild_id)
    new_coins = max(0, user_data["coins"] + amount)
    await bot_ref.db.update_user(user_id, guild_id, coins=new_coins)

    return jsonify({"success": True, "new_balance": new_coins})


# ── Giveaways ─────────────────────────────
@api_bp.route("/giveaways/<int:guild_id>")
@require_auth
async def get_giveaways(guild_id: int):
    if not bot_ref:
        return jsonify({"error": "Bot not connected"}), 503
    giveaways = await bot_ref.db.get_active_giveaways()
    return jsonify([g for g in giveaways if g["guild_id"] == guild_id])