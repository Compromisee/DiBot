import discord
from discord.ext import commands
from datetime import datetime
import random
from database.db import Database
from utils.embeds import success_embed, error_embed, info_embed
from utils.helpers import parse_duration, format_time
from utils.views import GiveawayView
import config

# ─────────────────────────────────────────
#  Giveaways Cog
# ─────────────────────────────────────────

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    # ── Start Giveaway ───────────────────
    @commands.command(name="gstart", aliases=["gcreate", "giveaway"], help="Start a giveaway (!gstart 1h 2 Prize Name)")
    @commands.has_permissions(manage_guild=True)
    async def gstart(self, ctx, duration: str, winners: int, *, prize: str):
        try:
            td = parse_duration(duration)
        except ValueError:
            return await ctx.send(embed=error_embed("Invalid Duration", "Use: `1d`, `2h30m`, `30m`"))

        end_time = datetime.utcnow() + td

        embed = discord.Embed(
            title       = "🎉 GIVEAWAY! 🎉",
            description = (
                f"**Prize:** {prize}\n"
                f"**Winners:** {winners}\n"
                f"**Hosted by:** {ctx.author.mention}\n"
                f"**Ends:** <t:{int(end_time.timestamp())}:R>\n\n"
                f"Click the button below to enter!"
            ),
            color     = config.COLORS["pink"],
            timestamp = end_time
        )
        embed.set_footer(text="Ends at")

        await ctx.message.delete()
        msg = await ctx.send(embed=embed)

        giveaway_id = await self.db.create_giveaway(
            ctx.guild.id, ctx.channel.id, msg.id,
            ctx.author.id, prize, winners, end_time.isoformat()
        )

        view = GiveawayView(self.bot, giveaway_id)
        await msg.edit(view=view)

        await ctx.send(
            embed=success_embed("Giveaway Created!", f"Giveaway for **{prize}** has started!"),
            delete_after=5
        )

    # ── End Giveaway ─────────────────────
    @commands.command(name="gend", aliases=["endgiveaway"], help="End a giveaway early")
    @commands.has_permissions(manage_guild=True)
    async def gend(self, ctx, message_id: int):
        giveaways = await self.db.get_active_giveaways()
        giveaway  = next((g for g in giveaways if g["message_id"] == message_id), None)

        if not giveaway:
            return await ctx.send(embed=error_embed("Not Found", "Active giveaway not found!"))

        await self._end_giveaway(giveaway)
        await ctx.send(embed=success_embed("Giveaway Ended", "Winners have been selected."))

    # ── Reroll Giveaway ──────────────────
    @commands.command(name="greroll", aliases=["reroll"], help="Reroll a giveaway winner")
    @commands.has_permissions(manage_guild=True)
    async def greroll(self, ctx, message_id: int):
        entries = None
        import aiosqlite
        async with aiosqlite.connect(config.DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM giveaways WHERE message_id = ?", (message_id,)) as c:
                giveaway = await c.fetchone()
            if giveaway:
                async with db.execute("SELECT user_id FROM giveaway_entries WHERE giveaway_id = ?", (giveaway["id"],)) as c:
                    entries = [r[0] for r in await c.fetchall()]

        if not giveaway or not entries:
            return await ctx.send(embed=error_embed("Not Found", "Giveaway or entries not found!"))

        winner_id = random.choice(entries)
        await ctx.send(f"🎉 New winner: <@{winner_id}>! Congratulations on winning **{giveaway['prize']}**!")

    # ── List Giveaways ───────────────────
    @commands.command(name="glist", help="List all active giveaways")
    async def glist(self, ctx):
        giveaways = await self.db.get_active_giveaways()
        guild_g   = [g for g in giveaways if g["guild_id"] == ctx.guild.id]

        if not guild_g:
            return await ctx.send(embed=info_embed("No Giveaways", "No active giveaways in this server."))

        embed = discord.Embed(title="🎉 Active Giveaways", color=config.COLORS["pink"])
        for g in guild_g:
            end_ts = int(datetime.fromisoformat(g["end_time"]).timestamp())
            entries = await self.db.get_giveaway_entries(g["id"])
            embed.add_field(
                name  = f"#{g['id']} — {g['prize']}",
                value = (
                    f"Winners: **{g['winners']}** | Entries: **{len(entries)}**\n"
                    f"Ends: <t:{end_ts}:R>\n"
                    f"[Jump](<https://discord.com/channels/{g['guild_id']}/{g['channel_id']}/{g['message_id']}>)"
                ),
                inline=False
            )
        await ctx.send(embed=embed)

    # ── End Giveaway Helper ──────────────
    async def _end_giveaway(self, giveaway: dict):
        await self.db.end_giveaway(giveaway["id"])
        entries = await self.db.get_giveaway_entries(giveaway["id"])
        channel = self.bot.get_channel(giveaway["channel_id"])
        if not channel:
            return

        if not entries:
            embed = discord.Embed(
                title       = "🎉 Giveaway Ended",
                description = f"**Prize:** {giveaway['prize']}\nNo valid entries — no winner.",
                color       = config.COLORS["error"]
            )
        else:
            count       = min(giveaway["winners"], len(entries))
            winner_ids  = random.sample(entries, count)
            winners_str = ", ".join(f"<@{w}>" for w in winner_ids)
            embed = discord.Embed(
                title       = "🎉 Giveaway Ended!",
                description = f"**Prize:** {giveaway['prize']}\n🏆 **Winners:** {winners_str}",
                color       = config.COLORS["gold"]
            )
            await channel.send(
                f"🎉 Congrats {winners_str}! You won **{giveaway['prize']}**!"
            )

        try:
            msg = await channel.fetch_message(giveaway["message_id"])
            await msg.edit(embed=embed, view=None)
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(Giveaways(bot))