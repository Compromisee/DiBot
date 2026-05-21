import discord
from discord.ext import commands
from utils.embeds import success_embed, error_embed, info_embed, warning_embed
import config

# ─────────────────────────────────────────
#  Music Cog
#  NOTE: Requires yt-dlp + PyNaCl + FFmpeg
# ─────────────────────────────────────────

import asyncio
import yt_dlp

YDL_OPTIONS = {
    "format"         : "bestaudio/best",
    "noplaylist"     : True,
    "quiet"          : True,
    "no_warnings"    : True,
    "default_search" : "auto",
    "source_address" : "0.0.0.0",
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options"       : "-vn",
}


class MusicQueue:
    def __init__(self):
        self.queue    : list  = []
        self.current  : dict  = None
        self.volume   : float = 0.5
        self.loop     : bool  = False
        self.skip_flag: bool  = False


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot    = bot
        self.queues : dict[int, MusicQueue] = {}

    def get_queue(self, guild_id: int) -> MusicQueue:
        if guild_id not in self.queues:
            self.queues[guild_id] = MusicQueue()
        return self.queues[guild_id]

    # ── Join ─────────────────────────────
    @commands.command(name="join", aliases=["connect", "j"], help="Join your voice channel")
    async def join(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(embed=error_embed("Error", "You must be in a voice channel!"))
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(embed=success_embed("Connected!", f"Joined **{channel.name}** 🎵"))

    # ── Leave ────────────────────────────
    @commands.command(name="leave", aliases=["disconnect", "dc", "stop"], help="Leave the voice channel")
    async def leave(self, ctx):
        if not ctx.voice_client:
            return await ctx.send(embed=error_embed("Error", "I'm not in a voice channel!"))
        guild_id = ctx.guild.id
        self.queues.pop(guild_id, None)
        await ctx.voice_client.disconnect()
        await ctx.send(embed=success_embed("Disconnected", "Left the voice channel."))

    # ── Play ─────────────────────────────
    @commands.command(name="play", aliases=["p"], help="Play a song (search or URL)")
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            return await ctx.send(embed=error_embed("Error", "Join a voice channel first!"))

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        queue = self.get_queue(ctx.guild.id)

        async with ctx.typing():
            try:
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(f"ytsearch:{query}" if not query.startswith("http") else query, download=False)
                    if "entries" in info:
                        info = info["entries"][0]

                song = {
                    "url"      : info["url"],
                    "title"    : info.get("title", "Unknown"),
                    "duration" : info.get("duration", 0),
                    "uploader" : info.get("uploader", "Unknown"),
                    "thumbnail": info.get("thumbnail", ""),
                    "webpage_url": info.get("webpage_url", ""),
                }
            except Exception as e:
                return await ctx.send(embed=error_embed("Error", f"Could not find: `{query}`\n{e}"))

        queue.queue.append(song)

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            embed = info_embed(
                "Added to Queue",
                f"**[{song['title']}]({song['webpage_url']})**\n"
                f"Position: #{len(queue.queue)}"
            )
            await ctx.send(embed=embed)
        else:
            await self._play_next(ctx)

    # ── Play Next ─────────────────────────
    async def _play_next(self, ctx):
        queue = self.get_queue(ctx.guild.id)

        if not queue.queue:
            queue.current = None
            return

        if queue.loop and queue.current:
            song = queue.current
        else:
            song = queue.queue.pop(0)
            queue.current = song

        def after_play(error):
            if error:
                print(f"Player error: {error}")
            if not queue.skip_flag:
                asyncio.run_coroutine_threadsafe(self._play_next(ctx), self.bot.loop)
            queue.skip_flag = False

        try:
            source = discord.FFmpegPCMAudio(song["url"], **FFMPEG_OPTIONS)
            source = discord.PCMVolumeTransformer(source, volume=queue.volume)
            ctx.voice_client.play(source, after=after_play)

            embed = discord.Embed(
                title       = "🎵 Now Playing",
                description = f"**[{song['title']}]({song['webpage_url']})**",
                color       = config.COLORS["cyan"]
            )
            embed.add_field(name="⏱️ Duration", value=self._fmt(song["duration"]), inline=True)
            embed.add_field(name="👤 Artist",   value=song["uploader"],           inline=True)
            if song["thumbnail"]:
                embed.set_thumbnail(url=song["thumbnail"])
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(embed=error_embed("Play Error", str(e)))

    # ── Skip ─────────────────────────────
    @commands.command(name="skip", aliases=["s", "next"], help="Skip the current song")
    async def skip(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            return await ctx.send(embed=error_embed("Error", "Nothing is playing!"))

        queue = self.get_queue(ctx.guild.id)
        queue.skip_flag = True
        ctx.voice_client.stop()
        await ctx.send(embed=success_embed("Skipped!", "Moving to next song..."))
        await self._play_next(ctx)

    # ── Pause ────────────────────────────
    @commands.command(name="pause", help="Pause the music")
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send(embed=success_embed("Paused", "Music paused. Use `!resume` to continue."))
        else:
            await ctx.send(embed=error_embed("Error", "Nothing is playing!"))

    # ── Resume ───────────────────────────
    @commands.command(name="resume", aliases=["unpause"], help="Resume the music")
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send(embed=success_embed("Resumed", "Music resumed! 🎵"))
        else:
            await ctx.send(embed=error_embed("Error", "Music is not paused!"))

    # ── Queue ────────────────────────────
    @commands.command(name="queue", aliases=["q", "nowplaying", "np"], help="View the music queue")
    async def queue(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        embed = discord.Embed(title="🎵 Music Queue", color=config.COLORS["cyan"])

        if queue.current:
            embed.add_field(
                name  = "🎵 Now Playing",
                value = f"**{queue.current['title']}** ({self._fmt(queue.current['duration'])})",
                inline= False
            )

        if queue.queue:
            tracks = "\n".join(
                f"`{i+1}.` **{s['title']}** ({self._fmt(s['duration'])})"
                for i, s in enumerate(queue.queue[:10])
            )
            embed.add_field(name=f"📋 Up Next ({len(queue.queue)} songs)", value=tracks, inline=False)
        else:
            embed.add_field(name="📋 Up Next", value="Queue is empty!", inline=False)

        embed.set_footer(text=f"Volume: {int(queue.volume*100)}% | Loop: {'✅' if queue.loop else '❌'}")
        await ctx.send(embed=embed)

    # ── Volume ───────────────────────────
    @commands.command(name="volume", aliases=["vol"], help="Set volume (0-100)")
    async def volume(self, ctx, vol: int):
        if vol < 0 or vol > 100:
            return await ctx.send(embed=error_embed("Error", "Volume must be 0–100"))

        queue         = self.get_queue(ctx.guild.id)
        queue.volume  = vol / 100

        if ctx.voice_client and ctx.voice_client.source:
            ctx.voice_client.source.volume = queue.volume

        await ctx.send(embed=success_embed("Volume Set", f"Volume set to **{vol}%**"))

    # ── Loop ─────────────────────────────
    @commands.command(name="loop", help="Toggle loop for current song")
    async def loop(self, ctx):
        queue      = self.get_queue(ctx.guild.id)
        queue.loop = not queue.loop
        state      = "✅ Enabled" if queue.loop else "❌ Disabled"
        await ctx.send(embed=success_embed("Loop", f"Loop is now **{state}**"))

    # ── Clear Queue ───────────────────────
    @commands.command(name="clearqueue", aliases=["cq"], help="Clear the music queue")
    async def clearqueue(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        count = len(queue.queue)
        queue.queue.clear()
        await ctx.send(embed=success_embed("Queue Cleared", f"Removed **{count}** songs from the queue."))

    # ── Format Duration ───────────────────
    def _fmt(self, seconds: int) -> str:
        if not seconds:
            return "?:??"
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"


async def setup(bot):
    await bot.add_cog(Music(bot))