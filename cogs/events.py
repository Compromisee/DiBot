import discord
from discord.ext import commands, tasks
from datetime import datetime
from database.db import Database
from utils.helpers import is_on_cooldown, get_level_from_xp, xp_for_level
import config
import random

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db
        self.check_reminders.start()
        self.check_giveaways.start()
        self.check_temp_bans.start()

    def cog_unload(self):
        self.check_reminders.cancel()
        self.check_giveaways.cancel()
        self.check_temp_bans.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.bot.guilds)} servers | /help"
            )
        )
        print(f"""
╔══════════════════════════════════════╗
║  🤖 {self.bot.user} is ONLINE!
║  📡 Guilds: {len(self.bot.guilds)}
║  👥 Users: {len(self.bot.users)}
║  🔧 Commands: {len(self.bot.commands)}
║  ⚡ Slash Commands: {len(self.bot.tree.get_commands())}
╚══════════════════════════════════════╝
        """)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.db.create_user(member.id, member.guild.id)
        settings = await self.db.get_guild_settings(member.guild.id)

        if settings["welcome_channel"]:
            channel = self.bot.get_channel(settings["welcome_channel"])
            if channel:
                msg = settings["welcome_message"].replace("{user}", member.mention).replace("{server}", member.guild.name).replace("{count}", str(member.guild.member_count))
                embed = discord.Embed(title="👋 Welcome!", description=msg, color=config.COLORS["success"], timestamp=datetime.utcnow())
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_image(url=member.guild.banner.url if member.guild.banner else discord.Embed.Empty)
                await channel.send(embed=embed)

        if settings["auto_role"]:
            role = member.guild.get_role(settings["auto_role"])
            if role:
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        settings = await self.db.get_guild_settings(member.guild.id)
        ch_id = settings.get("leave_channel") or settings.get("welcome_channel")
        if ch_id:
            channel = self.bot.get_channel(ch_id)
            if channel:
                msg = settings["leave_message"].replace("{user}", str(member)).replace("{server}", member.guild.name)
                embed = discord.Embed(title="👋 Goodbye!", description=msg, color=config.COLORS["error"], timestamp=datetime.utcnow())
                embed.set_thumbnail(url=member.display_avatar.url)
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Track messages
        user = await self.db.get_user(message.author.id, message.guild.id)
        await self.db.update_user(message.author.id, message.guild.id, messages=user["messages"] + 1)

        # AFK check
        if user["afk_message"]:
            await self.db.update_user(message.author.id, message.guild.id, afk_message=None, afk_since=None)
            await message.reply(f"Welcome back {message.author.mention}! Your AFK has been removed.", delete_after=5)

        # Check mentions for AFK users
        for mentioned in message.mentions:
            m_data = await self.db.get_user(mentioned.id, message.guild.id)
            if m_data["afk_message"]:
                await message.reply(
                    f"💤 **{mentioned.display_name}** is AFK: {m_data['afk_message']} "
                    f"(since <t:{int(datetime.fromisoformat(m_data['afk_since']).timestamp())}:R>)",
                    delete_after=10
                )

        # XP system
        on_cd, _ = is_on_cooldown(user["last_xp"], config.XP_COOLDOWN)
        if not on_cd:
            xp_gain = random.randint(config.XP_PER_MESSAGE - 5, config.XP_PER_MESSAGE + 10)
            new_xp = user["xp"] + xp_gain
            old_level = user["level"]
            new_level = get_level_from_xp(new_xp)

            await self.db.update_user(
                message.author.id, message.guild.id,
                xp=new_xp, level=new_level,
                last_xp=datetime.utcnow().isoformat()
            )

            if new_level > old_level:
                settings = await self.db.get_guild_settings(message.guild.id)
                ch = self.bot.get_channel(settings["level_up_channel"]) if settings["level_up_channel"] else message.channel

                embed = discord.Embed(
                    title="🎉 Level Up!",
                    description=f"Congrats {message.author.mention}! You reached **Level {new_level}**! 🚀",
                    color=config.COLORS["gold"]
                )
                await ch.send(embed=embed, delete_after=15)

                # Check level roles
                level_roles = await self.db.get_level_roles(message.guild.id)
                for lr in level_roles:
                    if lr["level"] <= new_level:
                        role = message.guild.get_role(lr["role_id"])
                        if role and role not in message.author.roles:
                            await message.author.add_roles(role)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You lack permissions!", delete_after=5)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found!", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing: `{error.param.name}`", delete_after=5)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Cooldown: **{error.retry_after:.1f}s**", delete_after=5)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I lack permissions!", delete_after=5)
        else:
            print(f"Error: {error}")

    # ── Background Tasks ─────────────────
    @tasks.loop(seconds=30)
    async def check_reminders(self):
        reminders = await self.db.get_pending_reminders()
        for r in reminders:
            channel = self.bot.get_channel(r["channel_id"])
            if channel:
                user = self.bot.get_user(r["user_id"])
                embed = discord.Embed(
                    title="⏰ Reminder!",
                    description=r["message"],
                    color=config.COLORS["info"]
                )
                await channel.send(content=f"{user.mention}" if user else "", embed=embed)
            await self.db.complete_reminder(r["id"])

    @tasks.loop(seconds=15)
    async def check_giveaways(self):
        giveaways = await self.db.get_active_giveaways()
        for g in giveaways:
            end_time = datetime.fromisoformat(g["end_time"])
            if datetime.utcnow() >= end_time:
                await self._end_giveaway(g)

    @tasks.loop(minutes=1)
    async def check_temp_bans(self):
        bans = await self.db.get_expired_bans()
        for b in bans:
            guild = self.bot.get_guild(b["guild_id"])
            if guild:
                try:
                    user = await self.bot.fetch_user(b["user_id"])
                    await guild.unban(user, reason="Temp ban expired")
                except Exception:
                    pass
            await self.db.remove_temp_ban(b["guild_id"], b["user_id"])

    async def _end_giveaway(self, giveaway):
        await self.db.end_giveaway(giveaway["id"])
        entries = await self.db.get_giveaway_entries(giveaway["id"])
        channel = self.bot.get_channel(giveaway["channel_id"])
        if not channel:
            return

        import random as rng
        if not entries:
            embed = discord.Embed(
                title="🎉 Giveaway Ended!",
                description=f"**Prize:** {giveaway['prize']}\nNo valid entries!",
                color=config.COLORS["error"]
            )
        else:
            winner_count = min(giveaway["winners"], len(entries))
            winner_ids = rng.sample(entries, winner_count)
            winners = [f"<@{w}>" for w in winner_ids]
            embed = discord.Embed(
                title="🎉 Giveaway Ended!",
                description=f"**Prize:** {giveaway['prize']}\n**Winners:** {', '.join(winners)}",
                color=config.COLORS["gold"]
            )
            await channel.send(f"🎉 Congrats {', '.join(winners)}! You won **{giveaway['prize']}**!")

        try:
            msg = await channel.fetch_message(giveaway["message_id"])
            await msg.edit(embed=embed, view=None)
        except Exception:
            pass

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()

    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()

    @check_temp_bans.before_loop
    async def before_check_temp_bans(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Events(bot))