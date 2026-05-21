import discord
from discord.ext import commands
from datetime import datetime, timedelta
from database.db import Database
from utils.embeds import success_embed, error_embed, warning_embed
from utils.helpers import can_moderate, format_time, parse_duration
import config

# ─────────────────────────────────────────
#  Moderation Cog  (Prefix Commands)
# ─────────────────────────────────────────

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    # ── Kick ─────────────────────────────
    @commands.command(name="kick", help="Kick a member")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        can_mod, msg = can_moderate(ctx, member)
        if not can_mod:
            return await ctx.send(embed=error_embed("Error", msg))

        await member.kick(reason=reason)
        await self.db.add_mod_log(ctx.guild.id, "Kick", member.id, ctx.author.id, reason)

        embed = success_embed("Member Kicked", f"**{member}** was kicked.\n**Reason:** {reason}")
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)
        await self._send_log(ctx, "Kick", member, reason)

    # ── Ban ──────────────────────────────
    @commands.command(name="ban", help="Ban a member")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        can_mod, msg = can_moderate(ctx, member)
        if not can_mod:
            return await ctx.send(embed=error_embed("Error", msg))

        await member.ban(reason=reason, delete_message_days=0)
        await self.db.add_mod_log(ctx.guild.id, "Ban", member.id, ctx.author.id, reason)

        embed = success_embed("Member Banned", f"**{member}** was banned.\n**Reason:** {reason}")
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)
        await self._send_log(ctx, "Ban", member, reason)

    # ── Temp Ban ─────────────────────────
    @commands.command(name="tempban", help="Temporarily ban a member (e.g. !tempban @user 1d reason)")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def tempban(self, ctx, member: discord.Member, duration: str, *, reason: str = "No reason"):
        can_mod, msg = can_moderate(ctx, member)
        if not can_mod:
            return await ctx.send(embed=error_embed("Error", msg))

        try:
            td = parse_duration(duration)
        except ValueError:
            return await ctx.send(embed=error_embed("Invalid Duration", "Use: `1d`, `2h30m`, `30m`"))

        unban_at = datetime.utcnow() + td
        await member.ban(reason=f"Temp ban | {reason}")
        await self.db.add_temp_ban(ctx.guild.id, member.id, ctx.author.id, reason, unban_at.isoformat())
        await self.db.add_mod_log(ctx.guild.id, "Temp Ban", member.id, ctx.author.id, reason, duration)

        embed = success_embed(
            "Temp Ban Applied",
            f"**{member}** banned until <t:{int(unban_at.timestamp())}:F>\n**Reason:** {reason}"
        )
        await ctx.send(embed=embed)
        await self._send_log(ctx, f"Temp Ban ({duration})", member, reason)

    # ── Unban ────────────────────────────
    @commands.command(name="unban", help="Unban a user by ID")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str = "No reason"):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=reason)
            await ctx.send(embed=success_embed("Unbanned", f"**{user}** was unbanned."))
        except discord.NotFound:
            await ctx.send(embed=error_embed("Not Found", "User not found or not banned."))

    # ── Mute ─────────────────────────────
    @commands.command(name="mute", help="Mute a member (e.g. !mute @user 10 reason)")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: int = 10, *, reason: str = "No reason"):
        can_mod, msg = can_moderate(ctx, member)
        if not can_mod:
            return await ctx.send(embed=error_embed("Error", msg))

        until = datetime.utcnow() + timedelta(minutes=duration)
        await member.timeout(until, reason=reason)
        await self.db.add_mod_log(ctx.guild.id, "Mute", member.id, ctx.author.id, reason, f"{duration}m")

        embed = success_embed("Muted", f"**{member}** muted for **{duration}m**.\n**Reason:** {reason}")
        await ctx.send(embed=embed)
        await self._send_log(ctx, f"Mute ({duration}m)", member, reason)

    # ── Unmute ───────────────────────────
    @commands.command(name="unmute", help="Unmute a member")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(embed=success_embed("Unmuted", f"**{member}** has been unmuted."))
        await self._send_log(ctx, "Unmute", member, "Manual unmute")

    # ── Warn ─────────────────────────────
    @commands.command(name="warn", help="Warn a member")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        can_mod, msg = can_moderate(ctx, member)
        if not can_mod:
            return await ctx.send(embed=error_embed("Error", msg))

        await self.db.get_user(member.id, ctx.guild.id)
        await self.db.add_warning(member.id, ctx.guild.id, reason, ctx.author.id)
        user_data = await self.db.get_user(member.id, ctx.guild.id)
        settings  = await self.db.get_guild_settings(ctx.guild.id)
        max_w     = settings["max_warnings"]
        warn_count = user_data["warnings"]

        embed = discord.Embed(
            title="⚠️ Warning Issued",
            description=(
                f"**{member}** has been warned.\n"
                f"**Reason:** {reason}\n"
                f"**Warnings:** {warn_count}/{max_w}"
            ),
            color=config.COLORS["warning"]
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

        if warn_count >= max_w:
            await member.ban(reason=f"Auto-ban: {max_w} warnings reached")
            await ctx.send(embed=error_embed(
                "Auto-Banned",
                f"**{member}** was auto-banned for reaching {max_w} warnings."
            ))
        await self._send_log(ctx, "Warn", member, reason)

    # ── Warnings ─────────────────────────
    @commands.command(name="warnings", help="View warnings for a member")
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        warns = await self.db.get_warnings(member.id, ctx.guild.id)
        embed = discord.Embed(
            title=f"⚠️ Warnings for {member}",
            color=config.COLORS["warning"]
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        if not warns:
            embed.description = "No warnings on record."
        else:
            for i, w in enumerate(warns, 1):
                mod = ctx.guild.get_member(w["moderator"])
                embed.add_field(
                    name=f"Warning #{i}",
                    value=(
                        f"**Reason:** {w['reason']}\n"
                        f"**By:** {mod or f'<@{w[\"moderator\"]}>'}\n"
                        f"**Date:** {w['created_at'][:10]}"
                    ),
                    inline=False
                )
        await ctx.send(embed=embed)

    # ── Clear Warnings ───────────────────
    @commands.command(name="clearwarnings", aliases=["clearwarns"], help="Clear all warnings for a member")
    @commands.has_permissions(administrator=True)
    async def clearwarnings(self, ctx, member: discord.Member):
        await self.db.clear_warnings(member.id, ctx.guild.id)
        await ctx.send(embed=success_embed("Warnings Cleared", f"All warnings for **{member}** have been cleared."))

    # ── Purge ────────────────────────────
    @commands.command(name="purge", aliases=["clear"], help="Delete messages (1-100)")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 10, member: discord.Member = None):
        if amount < 1 or amount > 100:
            return await ctx.send(embed=error_embed("Error", "Amount must be between 1 and 100."))

        await ctx.message.delete()

        if member:
            def check(m):
                return m.author == member
            deleted = await ctx.channel.purge(limit=amount * 5, check=check, bulk=True)
        else:
            deleted = await ctx.channel.purge(limit=amount)

        msg = await ctx.send(embed=success_embed("Purged", f"Deleted **{len(deleted)}** messages."))
        await msg.delete(delay=4)

    # ── Slowmode ─────────────────────────
    @commands.command(name="slowmode", help="Set slowmode delay (0 to disable)")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        if seconds < 0 or seconds > 21600:
            return await ctx.send(embed=error_embed("Error", "Slowmode must be 0–21600 seconds."))
        await ctx.channel.edit(slowmode_delay=seconds)
        msg = "Slowmode **disabled**." if seconds == 0 else f"Slowmode set to **{seconds}s**."
        await ctx.send(embed=success_embed("Slowmode", msg))

    # ── Lock ─────────────────────────────
    @commands.command(name="lock", help="Lock a channel")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(embed=success_embed("Channel Locked", f"🔒 {channel.mention} is now locked."))

    # ── Unlock ───────────────────────────
    @commands.command(name="unlock", help="Unlock a channel")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(embed=success_embed("Channel Unlocked", f"🔓 {channel.mention} is now unlocked."))

    # ── Lockdown ─────────────────────────
    @commands.command(name="lockdown", help="Lock ALL channels in the server")
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx):
        count = 0
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                count += 1
            except Exception:
                pass
        await ctx.send(embed=success_embed("🔒 Server Lockdown", f"Locked **{count}** channels."))

    # ── Unlockdown ───────────────────────
    @commands.command(name="unlockdown", help="Unlock ALL channels in the server")
    @commands.has_permissions(administrator=True)
    async def unlockdown(self, ctx):
        count = 0
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                count += 1
            except Exception:
                pass
        await ctx.send(embed=success_embed("🔓 Lockdown Lifted", f"Unlocked **{count}** channels."))

    # ── Nick ─────────────────────────────
    @commands.command(name="nick", help="Change a member's nickname")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, nickname: str = None):
        old_nick = member.display_name
        await member.edit(nick=nickname)
        if nickname:
            await ctx.send(embed=success_embed("Nickname Changed", f"**{old_nick}** → **{nickname}**"))
        else:
            await ctx.send(embed=success_embed("Nickname Removed", f"Reset nickname for **{old_nick}**."))

    # ── Role Add / Remove ─────────────────
    @commands.command(name="role", help="Add or remove a role from a member")
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member, *, role: discord.Role):
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(embed=success_embed("Role Removed", f"Removed {role.mention} from {member.mention}"))
        else:
            await member.add_roles(role)
            await ctx.send(embed=success_embed("Role Added", f"Added {role.mention} to {member.mention}"))

    # ── Mod Log Helper ───────────────────
    async def _send_log(self, ctx, action: str, target: discord.Member, reason: str):
        settings = await self.db.get_guild_settings(ctx.guild.id)
        if not settings["log_channel"]:
            return
        channel = ctx.guild.get_channel(settings["log_channel"])
        if not channel:
            return

        embed = discord.Embed(
            title=f"📋 {action}",
            color=config.COLORS["warning"],
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Target",    value=f"{target} ({target.id})",       inline=False)
        embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        embed.add_field(name="Channel",   value=ctx.channel.mention,             inline=False)
        embed.add_field(name="Reason",    value=reason,                          inline=False)
        await channel.send(embed=embed)

    # ── Error Handlers ───────────────────
    @kick.error
    @ban.error
    @mute.error
    async def mod_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send(embed=error_embed("Not Found", "Member not found!"))
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=error_embed("No Permission", "You lack the required permissions."))
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(embed=error_embed("Bot Error", "I don't have permission to do that."))


async def setup(bot):
    await bot.add_cog(Moderation(bot))