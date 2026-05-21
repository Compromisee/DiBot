import discord
from discord.ext import commands
from discord import ui
from datetime import datetime
import json
from database.db import Database
from utils.embeds import success_embed, error_embed, info_embed
import config

# ─────────────────────────────────────────
#  Polls Cog
# ─────────────────────────────────────────

NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    # ── Quick Poll ───────────────────────
    @commands.command(name="poll", aliases=["vote"], help='Quick yes/no poll (!poll "Question")')
    async def poll(self, ctx, *, question: str):
        embed = discord.Embed(
            title       = f"📊 {question}",
            description = "👍 Yes  |  👎 No",
            color       = config.COLORS["info"],
            timestamp   = datetime.utcnow()
        )
        embed.set_footer(text=f"Poll by {ctx.author.display_name}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        await ctx.message.delete()

    # ── Multi Option Poll ────────────────
    @commands.command(name="multipoll", aliases=["mpoll"], help='Multi-option poll (!mpoll "Question" "Option 1" "Option 2" ...)')
    async def multipoll(self, ctx, question: str, *options: str):
        if len(options) < 2:
            return await ctx.send(embed=error_embed("Error", "Provide at least 2 options in quotes!"))
        if len(options) > 9:
            return await ctx.send(embed=error_embed("Error", "Maximum 9 options!"))

        desc  = "\n".join(f"{NUMBER_EMOJIS[i]} {opt}" for i, opt in enumerate(options))
        embed = discord.Embed(
            title       = f"📊 {question}",
            description = desc,
            color       = config.COLORS["info"],
            timestamp   = datetime.utcnow()
        )
        embed.set_footer(text=f"Poll by {ctx.author.display_name} | {len(options)} options")
        msg = await ctx.send(embed=embed)
        await ctx.message.delete()

        for i in range(len(options)):
            await msg.add_reaction(NUMBER_EMOJIS[i])

    # ── Straw Poll ───────────────────────
    @commands.command(name="strawpoll", help='Straw poll with results (!strawpoll "Q" "A" "B" "C")')
    async def strawpoll(self, ctx, question: str, *options: str):
        if len(options) < 2:
            return await ctx.send(embed=error_embed("Error", "Provide at least 2 options!"))
        if len(options) > 9:
            return await ctx.send(embed=error_embed("Error", "Maximum 9 options!"))

        desc  = "\n".join(f"{NUMBER_EMOJIS[i]} **{opt}** — 0 votes (0%)" for i, opt in enumerate(options))
        embed = discord.Embed(
            title       = f"📊 {question}",
            description = desc,
            color       = config.COLORS["purple"],
            timestamp   = datetime.utcnow()
        )
        embed.set_footer(text=f"0 total votes | Poll by {ctx.author.display_name}")
        msg = await ctx.send(embed=embed)
        await ctx.message.delete()

        for i in range(len(options)):
            await msg.add_reaction(NUMBER_EMOJIS[i])

        # Store poll data for live updates
        self.bot.polls = getattr(self.bot, "polls", {})
        self.bot.polls[msg.id] = {
            "question": question,
            "options" : list(options),
            "msg_id"  : msg.id,
            "ch_id"   : msg.channel.id
        }

    # ── End Poll ─────────────────────────
    @commands.command(name="endpoll", help="Manually end a poll and show results")
    @commands.has_permissions(manage_messages=True)
    async def endpoll(self, ctx, message_id: int):
        try:
            msg = await ctx.channel.fetch_message(message_id)
        except discord.NotFound:
            return await ctx.send(embed=error_embed("Not Found", "Message not found!"))

        if not msg.embeds:
            return await ctx.send(embed=error_embed("Error", "That message has no embed!"))

        total    = sum(r.count - 1 for r in msg.reactions if str(r.emoji) in NUMBER_EMOJIS)
        results  = []

        for r in msg.reactions:
            if str(r.emoji) in NUMBER_EMOJIS:
                idx   = NUMBER_EMOJIS.index(str(r.emoji))
                votes = r.count - 1
                pct   = int(votes / total * 100) if total > 0 else 0
                bar   = "█" * (pct // 10) + "░" * (10 - pct // 10)
                results.append((idx, str(r.emoji), votes, pct, bar))

        results.sort(key=lambda x: x[2], reverse=True)

        embed = discord.Embed(
            title       = f"📊 Poll Results: {msg.embeds[0].title}",
            color       = config.COLORS["gold"],
            timestamp   = datetime.utcnow()
        )
        embed.set_footer(text=f"Total votes: {total}")

        for idx, emoji, votes, pct, bar in results:
            embed.add_field(
                name  = f"{emoji} Option {idx + 1}",
                value = f"`[{bar}]` **{votes}** votes ({pct}%)",
                inline= False
            )

        await ctx.send(embed=embed)

    # ── Reaction Update ──────────────────
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self._update_strawpoll(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self._update_strawpoll(payload)

    async def _update_strawpoll(self, payload: discord.RawReactionActionEvent):
        polls = getattr(self.bot, "polls", {})
        if payload.message_id not in polls:
            return

        poll    = polls[payload.message_id]
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return

        try:
            msg   = await channel.fetch_message(payload.message_id)
            total = sum(r.count - 1 for r in msg.reactions if str(r.emoji) in NUMBER_EMOJIS)
            desc  = ""

            for i, option in enumerate(poll["options"]):
                emoji = NUMBER_EMOJIS[i]
                r     = next((r for r in msg.reactions if str(r.emoji) == emoji), None)
                votes = (r.count - 1) if r else 0
                pct   = int(votes / total * 100) if total > 0 else 0
                bar   = "█" * (pct // 10) + "░" * (10 - pct // 10)
                desc += f"{emoji} **{option}** — {votes} votes ({pct}%)\n`[{bar}]`\n\n"

            embed = msg.embeds[0].copy()
            embed.description = desc
            embed.set_footer(text=f"{total} total votes")
            await msg.edit(embed=embed)
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(Polls(bot))