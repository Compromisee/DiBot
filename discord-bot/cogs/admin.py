import discord
from discord.ext import commands
from utils.embeds import success_embed, error_embed, info_embed
from utils.helpers import get_level_from_xp
import config

# ─────────────────────────────────────────
#  Admin Cog
# ─────────────────────────────────────────

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db  = bot.db

    def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    # ── Set Welcome Channel ───────────────
    @commands.command(name="setwelcome", help="Set welcome channel")
    async def setwelcome(self, ctx, channel: discord.TextChannel):
        await self.db.update_guild_settings(ctx.guild.id, welcome_channel=channel.id)
        await ctx.send(embed=success_embed("Welcome Channel Set", f"Welcome messages → {channel.mention}"))

    # ── Set Leave Channel ─────────────────
    @commands.command(name="setleave", help="Set leave/goodbye channel")
    async def setleave(self, ctx, channel: discord.TextChannel):
        await self.db.update_guild_settings(ctx.guild.id, leave_channel=channel.id)
        await ctx.send(embed=success_embed("Leave Channel Set", f"Leave messages → {channel.mention}"))

    # ── Set Log Channel ───────────────────
    @commands.command(name="setlog", aliases=["setlogs"], help="Set mod log channel")
    async def setlog(self, ctx, channel: discord.TextChannel):
        await self.db.update_guild_settings(ctx.guild.id, log_channel=channel.id)
        await ctx.send(embed=success_embed("Log Channel Set", f"Mod logs → {channel.mention}"))

    # ── Set Starboard ─────────────────────
    @commands.command(name="setstarboard", help="Set starboard channel")
    async def setstarboard(self, ctx, channel: discord.TextChannel, threshold: int = 3):
        await self.db.update_guild_settings(ctx.guild.id, starboard_channel=channel.id, starboard_threshold=threshold)
        await ctx.send(embed=success_embed("Starboard Set", f"Starboard → {channel.mention} (threshold: {threshold} ⭐)"))

    # ── Set Suggestion Channel ────────────
    @commands.command(name="setsuggestions", help="Set suggestions channel")
    async def setsuggestions(self, ctx, channel: discord.TextChannel):
        await self.db.update_guild_settings(ctx.guild.id, suggestion_channel=channel.id)
        await ctx.send(embed=success_embed("Suggestions Channel Set", f"Suggestions → {channel.mention}"))

    # ── Set Level Up Channel ──────────────
    @commands.command(name="setlevelup", help="Set level up notification channel")
    async def setlevelup(self, ctx, channel: discord.TextChannel = None):
        await self.db.update_guild_settings(ctx.guild.id, level_up_channel=channel.id if channel else None)
        msg = f"Level ups → {channel.mention}" if channel else "Level ups in same channel"
        await ctx.send(embed=success_embed("Level Up Channel Set", msg))

    # ── Set Auto Role ─────────────────────
    @commands.command(name="setautorole", aliases=["autorole"], help="Set auto role for new members")
    async def setautorole(self, ctx, role: discord.Role = None):
        await self.db.update_guild_settings(ctx.guild.id, auto_role=role.id if role else None)
        if role:
            await ctx.send(embed=success_embed("Auto Role Set", f"New members get → {role.mention}"))
        else:
            await ctx.send(embed=success_embed("Auto Role Removed", "Auto role has been cleared."))

    # ── Set Welcome Message ───────────────
    @commands.command(name="setwelcomemsg", help="Set welcome message ({user}, {server}, {count})")
    async def setwelcomemsg(self, ctx, *, message: str):
        await self.db.update_guild_settings(ctx.guild.id, welcome_message=message)
        await ctx.send(embed=success_embed("Welcome Message Set", f"Message: {message}"))

    # ── Set Max Warnings ──────────────────
    @commands.command(name="setmaxwarnings", help="Set max warnings before auto-ban")
    async def setmaxwarnings(self, ctx, amount: int):
        if amount < 1 or amount > 20:
            return await ctx.send(embed=error_embed("Error", "Amount must be 1–20"))
        await self.db.update_guild_settings(ctx.guild.id, max_warnings=amount)
        await ctx.send(embed=success_embed("Max Warnings Set", f"Auto-ban after **{amount}** warnings."))

    # ── Add Shop Item ─────────────────────
    @commands.command(name="additem", help="Add an item to the shop")
    async def additem(self, ctx, name: str, price: int, stock: int = -1, role: discord.Role = None, *, desc: str = ""):
        await self.db.add_shop_item(ctx.guild.id, name, desc, price, role.id if role else None, stock)
        await ctx.send(embed=success_embed("Item Added", f"Added **{name}** to the shop for **{price:,}** coins."))

    # ── Remove Shop Item ──────────────────
    @commands.command(name="removeitem", help="Remove an item from the shop")
    async def removeitem(self, ctx, *, name: str):
        await self.db.remove_shop_item(ctx.guild.id, name)
        await ctx.send(embed=success_embed("Item Removed", f"Removed **{name}** from the shop."))

    # ── Add Coins ─────────────────────────
    @commands.command(name="addcoins", aliases=["givecoins"], help="Add coins to a member")
    async def addcoins(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send(embed=error_embed("Error", "Amount must be positive!"))
        data = await self.db.get_user(member.id, ctx.guild.id)
        await self.db.update_user(member.id, ctx.guild.id, coins=data["coins"] + amount)
        await ctx.send(embed=success_embed("Coins Added", f"Added **{amount:,}** coins to {member.mention}"))

    # ── Remove Coins ──────────────────────
    @commands.command(name="removecoins", aliases=["takecoins"], help="Remove coins from a member")
    async def removecoins(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            return await ctx.send(embed=error_embed("Error", "Amount must be positive!"))
        data = await self.db.get_user(member.id, ctx.guild.id)
        new  = max(0, data["coins"] - amount)
        await self.db.update_user(member.id, ctx.guild.id, coins=new)
        await ctx.send(embed=success_embed("Coins Removed", f"Removed **{amount:,}** coins from {member.mention}"))

    # ── Set XP ───────────────────────────
    @commands.command(name="setxp", help="Set XP for a member")
    async def setxp(self, ctx, member: discord.Member, amount: int):
        new_level = get_level_from_xp(amount)
        await self.db.update_user(member.id, ctx.guild.id, xp=amount, level=new_level)
        await ctx.send(embed=success_embed("XP Set", f"Set {member.mention} to **{amount:,}** XP (Level {new_level})"))

    # ── Reset User ───────────────────────
    @commands.command(name="resetuser", help="Reset a member's economy and XP")
    async def resetuser(self, ctx, member: discord.Member):
        await self.db.update_user(
            member.id, ctx.guild.id,
            xp=0, level=1, coins=config.STARTING_BALANCE, bank=0, warnings=0, reputation=0, messages=0
        )
        await ctx.send(embed=success_embed("User Reset", f"{member.mention}'s data has been reset."))

    # ── Announce ─────────────────────────
    @commands.command(name="announce", aliases=["announcement"], help="Send an announcement")
    async def announce(self, ctx, channel: discord.TextChannel, *, message: str):
        embed = discord.Embed(
            description = f"📢 {message}",
            color       = config.COLORS["blurple"],
            timestamp   = __import__("datetime").datetime.utcnow()
        )
        embed.set_footer(
            text     = f"By {ctx.author.display_name}",
            icon_url = ctx.author.display_avatar.url
        )
        await channel.send(embed=embed)
        await ctx.send(embed=success_embed("Announced!", f"Message sent to {channel.mention}"))
        await ctx.message.delete()

    # ── Set Bot Status ───────────────────
    @commands.command(name="setstatus", help="Change bot status (owner only)")
    async def setstatus(self, ctx, *, status: str):
        if ctx.author.id != config.OWNER_ID:
            return await ctx.send(embed=error_embed("Access Denied", "This is an owner-only command!"))
        await self.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name=status)
        )
        await ctx.send(embed=success_embed("Status Updated", f"Now showing: **{status}**"))

    # ── Server Settings ──────────────────
    @commands.command(name="settings", help="View current server settings")
    async def settings(self, ctx):
        s = await self.db.get_guild_settings(ctx.guild.id)

        def ch(id_):
            ch_ = ctx.guild.get_channel(id_) if id_ else None
            return ch_.mention if ch_ else "Not set"

        def role(id_):
            r = ctx.guild.get_role(id_) if id_ else None
            return r.mention if r else "Not set"

        embed = discord.Embed(title=f"⚙️ {ctx.guild.name} Settings", color=config.COLORS["info"])
        embed.add_field(name="Prefix",          value=f"`{s['prefix']}`",          inline=True)
        embed.add_field(name="Welcome Channel",  value=ch(s["welcome_channel"]),    inline=True)
        embed.add_field(name="Leave Channel",    value=ch(s["leave_channel"]),      inline=True)
        embed.add_field(name="Log Channel",      value=ch(s["log_channel"]),        inline=True)
        embed.add_field(name="Starboard Channel",value=ch(s["starboard_channel"]),  inline=True)
        embed.add_field(name="⭐ Threshold",     value=s["starboard_threshold"],     inline=True)
        embed.add_field(name="Suggestion Ch.",   value=ch(s["suggestion_channel"]), inline=True)
        embed.add_field(name="Level Up Ch.",     value=ch(s["level_up_channel"]),   inline=True)
        embed.add_field(name="Auto Role",        value=role(s["auto_role"]),        inline=True)
        embed.add_field(name="AutoMod",          value="✅" if s["automod_enabled"] else "❌", inline=True)
        embed.add_field(name="Anti-Link",        value="✅" if s["antilink"]        else "❌", inline=True)
        embed.add_field(name="Anti-Spam",        value="✅" if s["antispam"]        else "❌", inline=True)
        embed.add_field(name="Max Warnings",     value=s["max_warnings"],           inline=True)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))