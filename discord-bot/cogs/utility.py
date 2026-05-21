import discord
from discord.ext import commands
from datetime import datetime
from database.db import Database
from utils.embeds import success_embed, error_embed, info_embed, profile_embed
from utils.paginator import Paginator, build_pages
import config

# ─────────────────────────────────────────
#  Utility Cog
# ─────────────────────────────────────────

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    # ── Help ─────────────────────────────
    @commands.command(name="help", aliases=["h", "commands"], help="Show all commands")
    async def help(self, ctx, command_name: str = None):
        if command_name:
            cmd = self.bot.get_command(command_name)
            if not cmd:
                return await ctx.send(embed=error_embed("Not Found", f"No command named `{command_name}`"))
            embed = discord.Embed(
                title       = f"📖 !{cmd.name}",
                description = cmd.help or "No description.",
                color       = config.COLORS["blurple"]
            )
            if cmd.aliases:
                embed.add_field(name="Aliases", value=", ".join(f"`{a}`" for a in cmd.aliases))
            return await ctx.send(embed=embed)

        cog_emojis = {
            "Moderation" : "🛡️",
            "Economy"    : "💰",
            "Leveling"   : "⭐",
            "Fun"        : "🎉",
            "Utility"    : "🔧",
            "Admin"      : "⚙️",
            "Giveaways"  : "🎁",
            "Tickets"    : "🎫",
            "Reminders"  : "⏰",
            "Polls"      : "📊",
            "AFK"        : "💤",
            "Suggestions": "💡",
            "Logging"    : "📋",
            "Welcomer"   : "👋",
        }

        pages = []
        for cog_name, cog in self.bot.cogs.items():
            cmds = [c for c in cog.get_commands() if not c.hidden]
            if not cmds:
                continue
            emoji    = cog_emojis.get(cog_name, "📌")
            embed    = discord.Embed(
                title       = f"{emoji} {cog_name} Commands",
                color       = config.COLORS["blurple"],
                description = f"Prefix: `{config.PREFIX}`"
            )
            for cmd in cmds:
                embed.add_field(
                    name  = f"`{config.PREFIX}{cmd.name}`",
                    value = cmd.help or "No description",
                    inline= False
                )
            pages.append(embed)

        if not pages:
            return await ctx.send(embed=info_embed("No Commands", "No commands found."))

        view = Paginator(pages, ctx.author.id)
        await ctx.send(embed=pages[0], view=view)

    # ── Profile ──────────────────────────
    @commands.command(name="profile", aliases=["p", "me"], help="View your or another member's profile")
    async def profile(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        data   = await self.db.get_user(member.id, ctx.guild.id)
        await ctx.send(embed=profile_embed(member, data))

    # ── Server Info ──────────────────────
    @commands.command(name="serverinfo", aliases=["si", "server"], help="View server information")
    async def serverinfo(self, ctx):
        g     = ctx.guild
        bots  = sum(1 for m in g.members if m.bot)
        human = g.member_count - bots

        embed = discord.Embed(
            title     = f"📊 {g.name}",
            color     = config.COLORS["info"],
            timestamp = datetime.utcnow()
        )
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        if g.banner:
            embed.set_image(url=g.banner.url)

        embed.add_field(name="👑 Owner",      value=g.owner.mention,                    inline=True)
        embed.add_field(name="🆔 ID",          value=g.id,                               inline=True)
        embed.add_field(name="📅 Created",     value=f"<t:{int(g.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="👥 Members",     value=f"{g.member_count} total",          inline=True)
        embed.add_field(name="👤 Humans",      value=human,                              inline=True)
        embed.add_field(name="🤖 Bots",        value=bots,                               inline=True)
        embed.add_field(name="📺 Text Ch.",    value=len(g.text_channels),               inline=True)
        embed.add_field(name="🔊 Voice Ch.",   value=len(g.voice_channels),              inline=True)
        embed.add_field(name="🎭 Roles",       value=len(g.roles),                       inline=True)
        embed.add_field(name="😀 Emojis",      value=f"{len(g.emojis)}/{g.emoji_limit}", inline=True)
        embed.add_field(name="🔒 Verification",value=str(g.verification_level).title(),  inline=True)
        embed.add_field(name="🚀 Boosts",      value=g.premium_subscription_count,       inline=True)
        embed.set_footer(text=f"Locale: {g.preferred_locale}")
        await ctx.send(embed=embed)

    # ── User Info ────────────────────────
    @commands.command(name="userinfo", aliases=["ui", "whois", "user"], help="View user information")
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        roles  = [r.mention for r in reversed(member.roles) if r != ctx.guild.default_role]

        embed = discord.Embed(
            title     = f"👤 {member}",
            color     = member.color,
            timestamp = datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🆔 ID",          value=member.id,                                       inline=True)
        embed.add_field(name="🏷️ Nickname",   value=member.nick or "None",                           inline=True)
        embed.add_field(name="🤖 Bot",          value="✅" if member.bot else "❌",                    inline=True)
        embed.add_field(name="📅 Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="📅 Joined Server",   value=f"<t:{int(member.joined_at.timestamp())}:R>",  inline=True)
        embed.add_field(name="🎨 Top Role",    value=member.top_role.mention,                         inline=True)
        embed.add_field(
            name  = f"🎭 Roles ({len(roles)})",
            value = " ".join(roles[:15]) if roles else "None",
            inline= False
        )
        embed.set_footer(text=f"Status: {str(member.status).title()}")
        await ctx.send(embed=embed)

    # ── Avatar ───────────────────────────
    @commands.command(name="avatar", aliases=["av", "pfp", "icon"], help="View a member's avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed  = discord.Embed(
            title = f"🖼️ {member.display_name}'s Avatar",
            color = config.COLORS["info"]
        )
        embed.set_image(url=member.display_avatar.with_size(1024).url)
        embed.add_field(
            name  = "🔗 Links",
            value = (
                f"[PNG]({member.display_avatar.with_format('png').url}) | "
                f"[JPG]({member.display_avatar.with_format('jpg').url}) | "
                f"[WEBP]({member.display_avatar.with_format('webp').url})"
            )
        )
        await ctx.send(embed=embed)

    # ── Ping ─────────────────────────────
    @commands.command(name="ping", aliases=["latency"], help="Check bot latency")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        color   = (
            config.COLORS["success"] if latency < 100 else
            config.COLORS["warning"] if latency < 200 else
            config.COLORS["error"]
        )
        embed = discord.Embed(
            title       = "🏓 Pong!",
            description = f"**Latency:** {latency}ms",
            color       = color
        )
        await ctx.send(embed=embed)

    # ── Invite ───────────────────────────
    @commands.command(name="invite", help="Get the bot invite link")
    async def invite(self, ctx):
        link  = f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot+applications.commands"
        embed = discord.Embed(
            title       = "📨 Invite Me!",
            description = f"[Click here to invite {config.BOT_NAME}]({link})",
            color       = config.COLORS["blurple"]
        )
        await ctx.send(embed=embed)

    # ── Bot Info ─────────────────────────
    @commands.command(name="botinfo", aliases=["about", "info"], help="View bot information")
    async def botinfo(self, ctx):
        import platform
        import discord as dc

        embed = discord.Embed(
            title       = f"🤖 {config.BOT_NAME}",
            description = "A powerful multi-purpose Discord bot!",
            color       = config.COLORS["blurple"],
            timestamp   = datetime.utcnow()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="👥 Servers",   value=len(self.bot.guilds),        inline=True)
        embed.add_field(name="👤 Users",     value=len(self.bot.users),         inline=True)
        embed.add_field(name="📡 Latency",   value=f"{round(self.bot.latency*1000)}ms", inline=True)
        embed.add_field(name="🐍 Python",    value=platform.python_version(),   inline=True)
        embed.add_field(name="📦 discord.py",value=dc.__version__,              inline=True)
        embed.add_field(name="💻 OS",        value=platform.system(),           inline=True)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)

    # ── Uptime ───────────────────────────
    @commands.command(name="uptime", help="Check how long the bot has been online")
    async def uptime(self, ctx):
        if not hasattr(self.bot, "start_time"):
            return await ctx.send(embed=error_embed("Error", "Uptime not tracked."))
        delta   = datetime.utcnow() - self.bot.start_time
        hours, r = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(r, 60)
        days    = delta.days
        embed   = discord.Embed(
            title       = "⏱️ Uptime",
            description = f"**{days}d {hours%24}h {minutes}m {seconds}s**",
            color       = config.COLORS["success"]
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))