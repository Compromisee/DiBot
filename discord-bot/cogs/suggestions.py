import discord
from discord.ext import commands
from datetime import datetime
from database.db import Database
from utils.embeds import success_embed, error_embed, info_embed
import config

# ─────────────────────────────────────────
#  Suggestions Cog
# ─────────────────────────────────────────

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    # ── Suggest ──────────────────────────
    @commands.command(name="suggest", aliases=["suggestion"], help="Submit a suggestion")
    async def suggest(self, ctx, *, suggestion: str):
        if len(suggestion) < 10:
            return await ctx.send(embed=error_embed("Too Short", "Suggestion must be at least 10 characters."))
        if len(suggestion) > 1000:
            return await ctx.send(embed=error_embed("Too Long", "Suggestion must be under 1000 characters."))

        settings = await self.db.get_guild_settings(ctx.guild.id)
        channel  = (
            self.bot.get_channel(settings["suggestion_channel"])
            if settings["suggestion_channel"] else ctx.channel
        )

        embed = discord.Embed(
            title       = "💡 New Suggestion",
            description = suggestion,
            color       = config.COLORS["info"],
            timestamp   = datetime.utcnow()
        )
        embed.set_author(
            name     = ctx.author.display_name,
            icon_url = ctx.author.display_avatar.url
        )
        embed.set_footer(text="Status: ⏳ Pending")

        msg            = await channel.send(embed=embed)
        suggestion_id  = await self.db.create_suggestion(ctx.guild.id, ctx.author.id, msg.id, suggestion)

        embed.set_footer(text=f"ID: #{suggestion_id} | Status: ⏳ Pending")
        await msg.edit(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

        if ctx.channel != channel:
            await ctx.send(embed=success_embed("Suggestion Submitted!", f"ID: **#{suggestion_id}**"), delete_after=5)
        await ctx.message.delete()

    # ── Approve ──────────────────────────
    @commands.command(name="approve", help="Approve a suggestion")
    @commands.has_permissions(manage_guild=True)
    async def approve(self, ctx, suggestion_id: int, *, response: str = ""):
        await self._update_suggestion(ctx, suggestion_id, "approved", response, config.COLORS["success"], "✅ Approved")

    # ── Deny ─────────────────────────────
    @commands.command(name="deny", help="Deny a suggestion")
    @commands.has_permissions(manage_guild=True)
    async def deny(self, ctx, suggestion_id: int, *, response: str = ""):
        await self._update_suggestion(ctx, suggestion_id, "denied", response, config.COLORS["error"], "❌ Denied")

    # ── Consider ─────────────────────────
    @commands.command(name="consider", help="Mark a suggestion as under consideration")
    @commands.has_permissions(manage_guild=True)
    async def consider(self, ctx, suggestion_id: int, *, response: str = ""):
        await self._update_suggestion(ctx, suggestion_id, "considering", response, config.COLORS["warning"], "🤔 Considering")

    # ── Implement ────────────────────────
    @commands.command(name="implement", help="Mark a suggestion as implemented")
    @commands.has_permissions(manage_guild=True)
    async def implement(self, ctx, suggestion_id: int, *, response: str = ""):
        await self._update_suggestion(ctx, suggestion_id, "implemented", response, config.COLORS["cyan"], "🚀 Implemented")

    # ── Helper ───────────────────────────
    async def _update_suggestion(self, ctx, suggestion_id, status, response, color, label):
        sug = await self.db.get_suggestion(suggestion_id)
        if not sug:
            return await ctx.send(embed=error_embed("Not Found", f"Suggestion #{suggestion_id} not found!"))

        await self.db.update_suggestion(suggestion_id, status=status, response=response or None)

        settings = await self.db.get_guild_settings(ctx.guild.id)
        channel  = (
            self.bot.get_channel(settings["suggestion_channel"])
            if settings["suggestion_channel"] else ctx.channel
        )

        try:
            msg  = await channel.fetch_message(sug["message_id"])
            embed = msg.embeds[0]
            embed.color = color
            embed.set_footer(text=f"ID: #{suggestion_id} | Status: {label}")
            if response:
                # Remove old response field if exists
                embed.clear_fields()
                embed.add_field(name="📝 Staff Response", value=response, inline=False)
            await msg.edit(embed=embed)
        except Exception:
            pass

        await ctx.send(embed=success_embed(f"Suggestion {label}", f"#{suggestion_id} updated."), delete_after=5)
        await ctx.message.delete()

    # ── View Suggestion ──────────────────
    @commands.command(name="viewsuggestion", aliases=["sug"], help="View a suggestion by ID")
    async def viewsuggestion(self, ctx, suggestion_id: int):
        sug = await self.db.get_suggestion(suggestion_id)
        if not sug:
            return await ctx.send(embed=error_embed("Not Found", f"Suggestion #{suggestion_id} not found!"))

        author = ctx.guild.get_member(sug["user_id"])
        embed  = discord.Embed(
            title       = f"💡 Suggestion #{suggestion_id}",
            description = sug["content"],
            color       = config.COLORS["info"],
            timestamp   = datetime.fromisoformat(sug["created_at"])
        )
        embed.add_field(name="👤 Submitted by",  value=author.mention if author else f"<@{sug['user_id']}>", inline=True)
        embed.add_field(name="📋 Status",        value=sug["status"].title(),  inline=True)
        if sug["response"]:
            embed.add_field(name="📝 Response",  value=sug["response"], inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Suggestions(bot))