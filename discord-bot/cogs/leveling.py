import discord
from discord.ext import commands
from database.db import Database
from utils.embeds import success_embed, error_embed, info_embed
from utils.helpers import xp_for_level, progress_bar
from utils.paginator import Paginator, build_pages
import config

# ─────────────────────────────────────────
#  Leveling Cog
# ─────────────────────────────────────────

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    # ── Rank ─────────────────────────────
    @commands.command(name="rank", aliases=["level", "xp", "lvl"], help="View your rank")
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        data   = await self.db.get_user(member.id, ctx.guild.id)
        level  = data["level"]
        xp     = data["xp"]
        needed = xp_for_level(level)
        bar    = progress_bar(xp, needed)

        all_users = await self.db.get_all_users(ctx.guild.id)
        rank_pos  = next((i+1 for i, u in enumerate(all_users) if u["user_id"] == member.id), "?")

        embed = discord.Embed(
            title = f"⭐ {member.display_name}'s Rank",
            color = config.COLORS["purple"]
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🏅 Rank",     value=f"**#{rank_pos}**",            inline=True)
        embed.add_field(name="⭐ Level",    value=f"**{level}**",               inline=True)
        embed.add_field(name="💬 Messages", value=f"**{data['messages']:,}**",   inline=True)
        embed.add_field(
            name  = "✨ XP Progress",
            value = f"`[{bar}]` **{xp:,}/{needed:,}** ({int(xp/needed*100)}%)",
            inline= False
        )
        embed.set_footer(text=f"Rep: {data['reputation']} | ID: {member.id}")
        await ctx.send(embed=embed)

    # ── Leaderboard ──────────────────────
    @commands.command(name="leaderboard", aliases=["lb", "top", "levels"], help="View XP leaderboard")
    async def leaderboard(self, ctx):
        rows   = await self.db.get_leaderboard(ctx.guild.id, "xp", 50)
        medals = ["🥇", "🥈", "🥉"]
        items  = []

        for i, row in enumerate(rows):
            member = ctx.guild.get_member(row["user_id"])
            name   = member.display_name if member else f"User {row['user_id']}"
            medal  = medals[i] if i < 3 else f"`{i+1}.`"
            items.append(f"{medal} **{name}** — Lv.{row['level']} | {row['xp']:,} XP")

        if not items:
            return await ctx.send(embed=info_embed("No Data", "No leaderboard data yet!"))

        pages = build_pages(
            items,
            title    = f"🏆 {ctx.guild.name} Leaderboard",
            per_page = 10,
            color    = config.COLORS["gold"],
            formatter= lambda x: x
        )
        view = Paginator(pages, ctx.author.id)
        await ctx.send(embed=pages[0], view=view)

    # ── Set Level Role ────────────────────
    @commands.command(name="addlevelrole", help="Add a role reward for reaching a level")
    @commands.has_permissions(administrator=True)
    async def addlevelrole(self, ctx, level: int, role: discord.Role):
        await self.db.add_level_role(ctx.guild.id, level, role.id)
        await ctx.send(embed=success_embed("Level Role Added", f"Reaching **Level {level}** grants {role.mention}"))

    # ── Remove Level Role ────────────────
    @commands.command(name="removelevelrole", help="Remove a level role reward")
    @commands.has_permissions(administrator=True)
    async def removelevelrole(self, ctx, level: int):
        await self.db.remove_level_role(ctx.guild.id, level)
        await ctx.send(embed=success_embed("Removed", f"Level role for **Level {level}** removed."))

    # ── List Level Roles ─────────────────
    @commands.command(name="levelroles", help="View all level role rewards")
    async def levelroles(self, ctx):
        roles = await self.db.get_level_roles(ctx.guild.id)
        if not roles:
            return await ctx.send(embed=info_embed("No Level Roles", "No level roles configured yet."))

        embed = discord.Embed(title="⭐ Level Role Rewards", color=config.COLORS["purple"])
        for lr in roles:
            role = ctx.guild.get_role(lr["role_id"])
            embed.add_field(
                name  = f"Level {lr['level']}",
                value = role.mention if role else "Role deleted",
                inline= True
            )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leveling(bot))