import discord
from discord.ext import commands
from datetime import datetime
import config

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) != config.STARBOARD_EMOJI:
            return

        # Check reaction roles
        rr = await self.db.get_reaction_role(payload.message_id, str(payload.emoji))
        if rr:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = guild.get_role(rr["role_id"])
            if member and role and not member.bot:
                await member.add_roles(role)
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        settings = await self.db.get_guild_settings(guild.id)
        if not settings["starboard_channel"]:
            return

        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        star_reaction = next((r for r in message.reactions if str(r.emoji) == config.STARBOARD_EMOJI), None)
        if not star_reaction:
            return

        star_count = star_reaction.count
        if star_count < settings["starboard_threshold"]:
            return

        starboard_channel = guild.get_channel(settings["starboard_channel"])
        if not starboard_channel:
            return

        entry = await self.db.get_starboard_entry(message.id)

        embed = discord.Embed(
            description=message.content or "*No text*",
            color=config.COLORS["starboard"],
            timestamp=message.created_at
        )
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.add_field(name="Source", value=f"[Jump to message]({message.jump_url})", inline=False)
        embed.set_footer(text=f"⭐ {star_count} | #{channel.name}")

        if message.attachments:
            embed.set_image(url=message.attachments[0].url)

        if entry:
            try:
                sb_msg = await starboard_channel.fetch_message(entry["starboard_msg_id"])
                await sb_msg.edit(content=f"⭐ **{star_count}** | {channel.mention}", embed=embed)
                await self.db.update_starboard_entry(message.id, star_count)
            except Exception:
                pass
        else:
            sb_msg = await starboard_channel.send(content=f"⭐ **{star_count}** | {channel.mention}", embed=embed)
            await self.db.create_starboard_entry(guild.id, message.id, sb_msg.id, channel.id, message.author.id, star_count)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # Handle reaction role removal
        rr = await self.db.get_reaction_role(payload.message_id, str(payload.emoji))
        if rr:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = guild.get_role(rr["role_id"])
            if member and role:
                await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(Starboard(bot))