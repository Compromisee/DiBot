import discord
from discord.ext import commands
from datetime import datetime
from database.db import Database
from utils.embeds import success_embed, error_embed, info_embed
from utils.helpers import parse_duration, format_time
import config

# ─────────────────────────────────────────
#  Reminders Cog
# ─────────────────────────────────────────

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    # ── Set Reminder ─────────────────────
    @commands.command(name="remind", aliases=["reminder", "remindme"], help="Set a reminder (e.g. !remind 30m Take a break)")
    async def remind(self, ctx, duration: str, *, message: str):
        try:
            td = parse_duration(duration)
        except ValueError:
            return await ctx.send(embed=error_embed(
                "Invalid Duration",
                "Examples: `30m`, `1h`, `2h30m`, `1d`"
            ))

        remind_at = datetime.utcnow() + td
        await self.db.create_reminder(
            ctx.author.id,
            ctx.channel.id,
            ctx.guild.id,
            message,
            remind_at.isoformat()
        )

        embed = success_embed(
            "⏰ Reminder Set!",
            f"I'll remind you <t:{int(remind_at.timestamp())}:R>\n**Message:** {message}"
        )
        embed.set_footer(text=f"Set by {ctx.author.display_name}")
        await ctx.send(embed=embed)

    # ── List Reminders ───────────────────
    @commands.command(name="reminders", aliases=["myreminders"], help="View your active reminders")
    async def reminders(self, ctx):
        import aiosqlite
        async with aiosqlite.connect(config.DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM reminders WHERE user_id = ? AND completed = 0 ORDER BY remind_at ASC",
                (ctx.author.id,)
            ) as cursor:
                rows = [dict(r) for r in await cursor.fetchall()]

        if not rows:
            return await ctx.send(embed=info_embed("No Reminders", "You have no active reminders!"))

        embed = discord.Embed(title="⏰ Your Reminders", color=config.COLORS["info"])
        for i, r in enumerate(rows[:10], 1):
            remind_ts = int(datetime.fromisoformat(r["remind_at"]).timestamp())
            embed.add_field(
                name  = f"Reminder #{i} (ID: {r['id']})",
                value = f"**Message:** {r['message']}\n**Fires:** <t:{remind_ts}:R>",
                inline= False
            )
        await ctx.send(embed=embed)

    # ── Cancel Reminder ──────────────────
    @commands.command(name="cancelreminder", aliases=["delreminder"], help="Cancel a reminder by ID")
    async def cancelreminder(self, ctx, reminder_id: int):
        import aiosqlite
        async with aiosqlite.connect(config.DB_PATH) as db:
            async with db.execute(
                "SELECT * FROM reminders WHERE id = ? AND user_id = ? AND completed = 0",
                (reminder_id, ctx.author.id)
            ) as cursor:
                row = await cursor.fetchone()

            if not row:
                return await ctx.send(embed=error_embed("Not Found", "Reminder not found or not yours!"))

            await db.execute("UPDATE reminders SET completed = 1 WHERE id = ?", (reminder_id,))
            await db.commit()

        await ctx.send(embed=success_embed("Reminder Cancelled", f"Reminder #{reminder_id} has been cancelled."))


async def setup(bot):
    await bot.add_cog(Reminders(bot))