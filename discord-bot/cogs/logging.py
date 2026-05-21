import discord
from discord.ext import commands
from datetime import datetime
from database.db import Database
import config

# ─────────────────────────────────────────
#  Advanced Logging Cog
# ─────────────────────────────────────────

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    async def get_log_channel(self, guild_id: int):
        settings = await self.db.get_guild_settings(guild_id)
        if not settings["log_channel"]:
            return None
        return self.bot.get_channel(settings["log_channel"])

    async def send_log(self, guild_id: int, embed: discord.Embed):
        ch = await self.get_log_channel(guild_id)
        if ch:
            try:
                await ch.send(embed=embed)
            except Exception:
                pass

    # ── Message Delete ───────────────────
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        embed = discord.Embed(
            title       = "🗑️ Message Deleted",
            color       = config.COLORS["error"],
            timestamp   = datetime.utcnow()
        )
        embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
        embed.add_field(name="Author",  value=message.author.mention, inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Content", value=message.content[:1024] or "*No text*", inline=False)
        embed.set_footer(text=f"User ID: {message.author.id}")
        await self.send_log(message.guild.id, embed)

    # ── Message Edit ─────────────────────
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild or before.author.bot:
            return
        if before.content == after.content:
            return

        embed = discord.Embed(
            title       = "✏️ Message Edited",
            color       = config.COLORS["warning"],
            timestamp   = datetime.utcnow()
        )
        embed.set_author(name=str(before.author), icon_url=before.author.display_avatar.url)
        embed.add_field(name="Author",  value=before.author.mention,        inline=True)
        embed.add_field(name="Channel", value=before.channel.mention,       inline=True)
        embed.add_field(name="[Jump]",  value=f"[Click]({after.jump_url})", inline=True)
        embed.add_field(name="Before",  value=before.content[:512] or "*Empty*", inline=False)
        embed.add_field(name="After",   value=after.content[:512]  or "*Empty*", inline=False)
        embed.set_footer(text=f"User ID: {before.author.id}")
        await self.send_log(before.guild.id, embed)

    # ── Member Join ──────────────────────
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed = discord.Embed(
            title       = "📥 Member Joined",
            description = f"{member.mention} joined the server",
            color       = config.COLORS["success"],
            timestamp   = datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Member #",        value=member.guild.member_count, inline=True)
        embed.set_footer(text=f"ID: {member.id}")
        await self.send_log(member.guild.id, embed)

    # ── Member Leave ─────────────────────
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        roles = [r.mention for r in member.roles if r != member.guild.default_role]
        embed = discord.Embed(
            title       = "📤 Member Left",
            description = f"{member.mention} left the server",
            color       = config.COLORS["error"],
            timestamp   = datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Joined At",   value=f"<t:{int(member.joined_at.timestamp())}:R>" if member.joined_at else "Unknown", inline=True)
        embed.add_field(name="Roles",       value=" ".join(roles[:10]) if roles else "None", inline=False)
        embed.set_footer(text=f"ID: {member.id}")
        await self.send_log(member.guild.id, embed)

    # ── Member Update (Roles, Nick) ───────
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        embed = None

        if before.nick != after.nick:
            embed = discord.Embed(title="✏️ Nickname Changed", color=config.COLORS["info"], timestamp=datetime.utcnow())
            embed.set_author(name=str(after), icon_url=after.display_avatar.url)
            embed.add_field(name="Before", value=before.nick or before.name, inline=True)
            embed.add_field(name="After",  value=after.nick  or after.name,  inline=True)

        elif before.roles != after.roles:
            added   = [r for r in after.roles  if r not in before.roles]
            removed = [r for r in before.roles if r not in after.roles]
            if added or removed:
                embed = discord.Embed(title="🎭 Roles Updated", color=config.COLORS["purple"], timestamp=datetime.utcnow())
                embed.set_author(name=str(after), icon_url=after.display_avatar.url)
                embed.add_field(name="Member", value=after.mention, inline=True)
                if added:
                    embed.add_field(name="✅ Added",   value=" ".join(r.mention for r in added),   inline=False)
                if removed:
                    embed.add_field(name="❌ Removed", value=" ".join(r.mention for r in removed), inline=False)

        if embed:
            embed.set_footer(text=f"ID: {after.id}")
            await self.send_log(after.guild.id, embed)

    # ── Role Create ──────────────────────
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        embed = discord.Embed(
            title     = "🎭 Role Created",
            color     = role.color or config.COLORS["success"],
            timestamp = datetime.utcnow()
        )
        embed.add_field(name="Name",  value=role.mention, inline=True)
        embed.add_field(name="Color", value=str(role.color), inline=True)
        embed.set_footer(text=f"Role ID: {role.id}")
        await self.send_log(role.guild.id, embed)

    # ── Role Delete ──────────────────────
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        embed = discord.Embed(
            title     = "🗑️ Role Deleted",
            color     = config.COLORS["error"],
            timestamp = datetime.utcnow()
        )
        embed.add_field(name="Name", value=role.name, inline=True)
        embed.set_footer(text=f"Role ID: {role.id}")
        await self.send_log(role.guild.id, embed)

    # ── Channel Create ───────────────────
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        embed = discord.Embed(
            title     = "📺 Channel Created",
            color     = config.COLORS["success"],
            timestamp = datetime.utcnow()
        )
        embed.add_field(name="Name",     value=channel.mention, inline=True)
        embed.add_field(name="Type",     value=str(channel.type).replace("_", " ").title(), inline=True)
        embed.add_field(name="Category", value=channel.category.name if channel.category else "None", inline=True)
        embed.set_footer(text=f"Channel ID: {channel.id}")
        await self.send_log(channel.guild.id, embed)

    # ── Channel Delete ───────────────────
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        embed = discord.Embed(
            title     = "🗑️ Channel Deleted",
            color     = config.COLORS["error"],
            timestamp = datetime.utcnow()
        )
        embed.add_field(name="Name", value=f"#{channel.name}", inline=True)
        embed.add_field(name="Type", value=str(channel.type).replace("_", " ").title(), inline=True)
        embed.set_footer(text=f"Channel ID: {channel.id}")
        await self.send_log(channel.guild.id, embed)

    # ── Voice State ──────────────────────
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel == after.channel:
            return

        embed = discord.Embed(color=config.COLORS["info"], timestamp=datetime.utcnow())
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)

        if not before.channel and after.channel:
            embed.title = "🔊 Joined Voice"
            embed.add_field(name="Channel", value=after.channel.mention)
        elif before.channel and not after.channel:
            embed.title = "🔇 Left Voice"
            embed.add_field(name="Channel", value=before.channel.name)
        elif before.channel and after.channel:
            embed.title = "🔀 Moved Voice"
            embed.add_field(name="From", value=before.channel.name,   inline=True)
            embed.add_field(name="To",   value=after.channel.mention, inline=True)

        embed.set_footer(text=f"ID: {member.id}")
        await self.send_log(member.guild.id, embed)

    # ── Ban / Unban ──────────────────────
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        embed = discord.Embed(
            title     = "🔨 Member Banned",
            color     = config.COLORS["error"],
            timestamp = datetime.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        await self.send_log(guild.id, embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        embed = discord.Embed(
            title     = "✅ Member Unbanned",
            color     = config.COLORS["success"],
            timestamp = datetime.utcnow()
        )
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
        await self.send_log(guild.id, embed)


async def setup(bot):
    await bot.add_cog(Logging(bot))