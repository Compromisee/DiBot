import discord
from discord.ext import commands
from datetime import datetime
from database.db import Database
from utils.embeds import success_embed, info_embed
import config

# ─────────────────────────────────────────
#  AFK Cog
# ─────────────────────────────────────────

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    # ── Set AFK ──────────────────────────
    @commands.command(name="afk", help="Set your AFK status")
    async def afk(self, ctx, *, message: str = "AFK"):
        if len(message) > 100:
            message = message[:100]

        await self.db.update_user(
            ctx.author.id, ctx.guild.id,
            afk_message = message,
            afk_since   = datetime.utcnow().isoformat()
        )

        # Add AFK to nickname
        try:
            if not ctx.author.display_name.startswith("[AFK]"):
                await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}"[:32])
        except discord.Forbidden:
            pass

        embed = success_embed(
            "AFK Set 💤",
            f"{ctx.author.mention} is now AFK: **{message}**"
        )
        await ctx.send(embed=embed)

    # ── Return from AFK ──────────────────
    # Handled via on_message in events.py

    # ── AFK Status ───────────────────────
    @commands.command(name="afkstatus", help="Check if a member is AFK")
    async def afkstatus(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        data   = await self.db.get_user(member.id, ctx.guild.id)

        if not data["afk_message"]:
            return await ctx.send(embed=info_embed("Not AFK", f"**{member.display_name}** is not AFK."))

        since_ts = int(datetime.fromisoformat(data["afk_since"]).timestamp())
        embed = discord.Embed(
            title       = f"💤 {member.display_name} is AFK",
            description = f"**Message:** {data['afk_message']}\n**Since:** <t:{since_ts}:R>",
            color       = config.COLORS["warning"]
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    # ── Clear AFK ────────────────────────
    @commands.command(name="afkclear", aliases=["removeafk"], help="Clear someone's AFK (Admin)")
    @commands.has_permissions(manage_messages=True)
    async def afkclear(self, ctx, member: discord.Member):
        data = await self.db.get_user(member.id, ctx.guild.id)
        if not data["afk_message"]:
            return await ctx.send(embed=info_embed("Not AFK", f"**{member.display_name}** is not AFK."))

        await self.db.update_user(member.id, ctx.guild.id, afk_message=None, afk_since=None)

        try:
            name = member.display_name.replace("[AFK] ", "")
            await member.edit(nick=name)
        except discord.Forbidden:
            pass

        await ctx.send(embed=success_embed("AFK Cleared", f"Cleared AFK for **{member.display_name}**."))

    # ── List AFK Members ─────────────────
    @commands.command(name="afklist", help="List all AFK members")
    async def afklist(self, ctx):
        import aiosqlite
        async with aiosqlite.connect(config.DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE guild_id = ? AND afk_message IS NOT NULL",
                (ctx.guild.id,)
            ) as cursor:
                rows = [dict(r) for r in await cursor.fetchall()]

        if not rows:
            return await ctx.send(embed=info_embed("No AFK Members", "Nobody is currently AFK."))

        embed = discord.Embed(title="💤 AFK Members", color=config.COLORS["warning"])
        for row in rows[:20]:
            member   = ctx.guild.get_member(row["user_id"])
            name     = member.display_name if member else f"User {row['user_id']}"
            since_ts = int(datetime.fromisoformat(row["afk_since"]).timestamp()) if row["afk_since"] else 0
            embed.add_field(
                name  = name,
                value = f"{row['afk_message']}\nSince: <t:{since_ts}:R>",
                inline= True
            )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AFK(bot))