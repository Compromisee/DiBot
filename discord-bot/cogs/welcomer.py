import discord
from discord.ext import commands
from datetime import datetime
from database.db import Database
from utils.embeds import success_embed, error_embed
import config

# ─────────────────────────────────────────
#  Advanced Welcomer Cog
# ─────────────────────────────────────────

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    def _format_message(self, template: str, member: discord.Member) -> str:
        return (
            template
            .replace("{user}",    member.mention)
            .replace("{name}",    member.display_name)
            .replace("{server}",  member.guild.name)
            .replace("{count}",   str(member.guild.member_count))
            .replace("{id}",      str(member.id))
        )

    # ── Welcome on Join ──────────────────
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        settings = await self.db.get_guild_settings(member.guild.id)

        if not settings["welcome_channel"]:
            return

        channel = self.bot.get_channel(settings["welcome_channel"])
        if not channel:
            return

        msg = self._format_message(settings["welcome_message"], member)

        embed = discord.Embed(
            title       = f"👋 Welcome to {member.guild.name}!",
            description = msg,
            color       = config.COLORS["success"],
            timestamp   = datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="📅 Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="👥 You are member",  value=f"**#{member.guild.member_count}**",            inline=True)

        if member.guild.icon:
            embed.set_author(name=member.guild.name, icon_url=member.guild.icon.url)

        await channel.send(embed=embed)

    # ── Leave on Remove ──────────────────
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        settings = await self.db.get_guild_settings(member.guild.id)
        ch_id    = settings.get("leave_channel") or settings.get("welcome_channel")

        if not ch_id:
            return

        channel = self.bot.get_channel(ch_id)
        if not channel:
            return

        msg = self._format_message(settings["leave_message"], member)

        embed = discord.Embed(
            title       = "👋 Member Left",
            description = msg,
            color       = config.COLORS["error"],
            timestamp   = datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👥 Members left", value=f"**{member.guild.member_count}**", inline=True)
        await channel.send(embed=embed)

    # ── Test Welcome ─────────────────────
    @commands.command(name="testwelcome", help="Test the welcome message")
    @commands.has_permissions(administrator=True)
    async def testwelcome(self, ctx):
        await self.on_member_join(ctx.author)
        await ctx.send(embed=success_embed("Test Sent", "Welcome message sent in the welcome channel."), delete_after=5)

    # ── Test Leave ───────────────────────
    @commands.command(name="testleave", help="Test the leave message")
    @commands.has_permissions(administrator=True)
    async def testleave(self, ctx):
        await self.on_member_remove(ctx.author)
        await ctx.send(embed=success_embed("Test Sent", "Leave message sent."), delete_after=5)

    # ── Preview Welcome Message ───────────
    @commands.command(name="previewwelcome", help="Preview the current welcome message")
    @commands.has_permissions(administrator=True)
    async def previewwelcome(self, ctx):
        settings = await self.db.get_guild_settings(ctx.guild.id)
        formatted = self._format_message(settings["welcome_message"], ctx.author)
        embed = discord.Embed(
            title       = "👁️ Welcome Message Preview",
            description = formatted,
            color       = config.COLORS["info"]
        )
        embed.add_field(
            name  = "📋 Template",
            value = f"`{settings['welcome_message']}`",
            inline= False
        )
        embed.add_field(
            name  = "📌 Variables",
            value = "`{user}` `{name}` `{server}` `{count}` `{id}`",
            inline= False
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Welcomer(bot))