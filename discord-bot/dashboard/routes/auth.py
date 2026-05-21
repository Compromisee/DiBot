from quart import Blueprint, redirect, request, session, url_for
import aiohttp
import config

# ─────────────────────────────────────────
#  Auth Routes (Discord OAuth2)
# ─────────────────────────────────────────

auth_bp = Blueprint("auth", __name__)

DISCORD_API  = "https://discord.com/api/v10"
OAUTH_URL    = (
    f"https://discord.com/api/oauth2/authorize"
    f"?client_id={config.CLIENT_ID}"
    f"&redirect_uri={config.REDIRECT_URI}"
    f"&response_type=code"
    f"&scope=identify+guilds"
)


async def _exchange_code(code: str) -> dict:
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{DISCORD_API}/oauth2/token", data={
            "client_id"    : config.CLIENT_ID,
            "client_secret": config.CLIENT_SECRET,
            "grant_type"   : "authorization_code",
            "code"         : code,
            "redirect_uri" : config.REDIRECT_URI,
        }) as resp:
            return await resp.json()


async def _get_user(token: str) -> dict:
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{DISCORD_API}/users/@me", headers={
            "Authorization": f"Bearer {token}"
        }) as resp:
            return await resp.json()


async def _get_guilds(token: str) -> list:
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{DISCORD_API}/users/@me/guilds", headers={
            "Authorization": f"Bearer {token}"
        }) as resp:
            return await resp.json()


@auth_bp.route("/login")
async def login():
    return redirect(OAUTH_URL)


@auth_bp.route("/callback")
async def callback():
    code = request.args.get("code")
    if not code:
        return redirect(url_for("views.index"))

    token_data   = await _exchange_code(code)
    access_token = token_data.get("access_token")

    if not access_token:
        return redirect(url_for("views.index"))

    user   = await _get_user(access_token)
    guilds = await _get_guilds(access_token)

    session["user"]   = user
    session["token"]  = access_token
    session["guilds"] = guilds

    return redirect(url_for("views.dashboard"))


@auth_bp.route("/logout")
async def logout():
    session.clear()
    return redirect(url_for("views.index"))