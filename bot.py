import discord
from discord.ext import commands
import asyncio
import config
from database.db import Database

# ─────────────────────────────────────────
#  Bot Setup
# ─────────────────────────────────────────

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=config.PREFIX,
    intents=intents,
    help_command=None,
    case_insensitive=True
)

bot.db = Database()

# ─────────────────────────────────────────
#  Load All Cogs
# ─────────────────────────────────────────

COGS = [
    "cogs.events",
    "cogs.slash_commands",
    "cogs.automod",
    "cogs.starboard",
    "cogs.games",
]

async def main():
    async with bot:
        # Setup database
        await bot.db.setup()

        # Load cogs
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"  ✅ Loaded: {cog}")
            except Exception as e:
                print(f"  ❌ Failed: {cog} — {e}")

        # Sync slash commands
        @bot.event
        async def on_ready():
            try:
                synced = await bot.tree.sync()
                print(f"  ⚡ Synced {len(synced)} slash commands")
            except Exception as e:
                print(f"  ❌ Sync failed: {e}")

        # Start dashboard in background
        async def start_dashboard():
            try:
                from dashboard.app import set_bot, app
                set_bot(bot)
                await app.run_task(host="0.0.0.0", port=config.DASHBOARD_PORT)
            except Exception as e:
                print(f"  ⚠️ Dashboard failed: {e}")

        bot.loop.create_task(start_dashboard())

        # Start bot
        print("\n🚀 Starting bot...")
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())