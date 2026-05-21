import discord
from discord.ext import commands
from collections import defaultdict
from datetime import datetime, timedelta
import re
import config

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.spam_tracker = defaultdict(list)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if message.author.guild_permissions.manage_messages:
            return

        settings = await self.db.get_guild_settings(message.guild.id)
        if not settings["automod_enabled"]:
            return

        violations = []

        # Anti-link
        if settings["antilink"]:
            url_pattern = re.compile(r'https?://\S+|discord\.gg/\S+')
            if url_pattern.search(message.content):
                violations.append("🔗 Links not allowed")

        # Anti-spam
        if settings["antispam"]:
            now = datetime.utcnow()
            key = f"{message.author.id}-{message.guild.id}"
            self.spam_tracker[key] = [
                t for t in self.spam_tracker[key]
                if (now - t).seconds < config.AUTOMOD_SPAM_INTERVAL
            ]
            self.spam_tracker[key].append(now)

            if len(self.spam_tracker[key]) >= config.AUTOMOD_SPAM_LIMIT:
                violations.append("🚫 Spam detected")
                self.spam_tracker[key] = []

        # Banned words
        for word in config.BANNED_WORDS:
            if word.lower() in message.content.lower():
                violations.append(f"🚫 Banned word: `{word}`")
                break

        # Excessive caps
        if len(message.content) > 10:
            caps_percent = sum(1 for c in message.content if c.isupper()) / len(message.content) * 100
            if caps_percent > config.CAPS_THRESHOLD:
                violations.append("🔠 Too many caps")

        # Excessive mentions
        if len(message.mentions) > config.MAX_MENTIONS:
            violations.append(f"📢 Too many mentions ({len(message.mentions)})")

        # Excessive emojis
        emoji_pattern = re.compile(r'<a?:\w+:\d+>|[\U0001F600-\U0001F9FF]')
        emoji_count = len(emoji_pattern.findall(message.content))
        if emoji_count > config.MAX_EMOJIS:
            violations.append(f"😀 Too many emojis ({emoji_count})")

        if violations:
            try:
                await message.delete()
            except Exception:
                pass

            embed = discord.Embed(
                title="🛡️ AutoMod",
                description=f"{message.author.mention}, your message was removed!\n\n" + "\n".join(violations),
                color=config.COLORS["error"]
            )
            await message.channel.send(embed=embed, delete_after=5)

            # Log
            settings = await self.db.get_guild_settings(message.guild.id)
            if settings["log_channel"]:
                log_ch = self.bot.get_channel(settings["log_channel"])
                if log_ch:
                    log_embed = discord.Embed(title="🛡️ AutoMod Action", color=config.COLORS["warning"], timestamp=datetime.utcnow())
                    log_embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=False)
                    log_embed.add_field(name="Channel", value=message.channel.mention, inline=False)
                    log_embed.add_field(name="Violations", value="\n".join(violations), inline=False)
                    log_embed.add_field(name="Content", value=message.content[:500], inline=False)
                    await log_ch.send(embed=log_embed)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))