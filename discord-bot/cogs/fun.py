import discord
from discord.ext import commands
import random
import aiohttp
from utils.embeds import error_embed
import config

# ─────────────────────────────────────────
#  Fun Cog
# ─────────────────────────────────────────

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── 8Ball ────────────────────────────
    @commands.command(name="8ball", aliases=["eightball"], help="Ask the magic 8-ball")
    async def eightball(self, ctx, *, question: str):
        responses = [
            "✅ It is certain.",         "✅ Without a doubt.",
            "✅ Yes, definitely!",       "✅ Most likely.",
            "✅ Outlook good.",          "🤔 Ask again later.",
            "🤔 Reply hazy, try again.", "🤔 Cannot predict now.",
            "🤔 Don't count on it yet.", "❌ My reply is no.",
            "❌ Very doubtful.",         "❌ Absolutely not.",
            "❌ Outlook not so good.",   "❌ My sources say no.",
        ]
        embed = discord.Embed(title="🎱 Magic 8-Ball", color=config.COLORS["purple"])
        embed.add_field(name="❓ Question", value=question,                inline=False)
        embed.add_field(name="🎱 Answer",   value=random.choice(responses), inline=False)
        embed.set_footer(text=f"Asked by {ctx.author.display_name}")
        await ctx.send(embed=embed)

    # ── Coinflip ─────────────────────────
    @commands.command(name="coinflip", aliases=["flip", "coin"], help="Flip a coin")
    async def coinflip(self, ctx):
        result = random.choice(["🪙 Heads!", "🪙 Tails!"])
        embed  = discord.Embed(title="Coin Flip", description=result, color=config.COLORS["gold"])
        await ctx.send(embed=embed)

    # ── Roll ─────────────────────────────
    @commands.command(name="roll", aliases=["dice"], help="Roll a dice (e.g. !roll 20)")
    async def roll(self, ctx, sides: int = 6):
        if sides < 2:
            return await ctx.send(embed=error_embed("Error", "Dice must have at least 2 sides!"))
        if sides > 1000000:
            return await ctx.send(embed=error_embed("Error", "Too many sides!"))

        result = random.randint(1, sides)
        embed  = discord.Embed(
            title=f"🎲 D{sides} Roll",
            description=f"You rolled a **{result}**!",
            color=config.COLORS["info"]
        )
        await ctx.send(embed=embed)

    # ── Joke ─────────────────────────────
    @commands.command(name="joke", help="Get a random joke")
    async def joke(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://official-joke-api.appspot.com/random_joke"
            ) as resp:
                if resp.status == 200:
                    data  = await resp.json()
                    embed = discord.Embed(title="😂 Random Joke", color=config.COLORS["info"])
                    embed.add_field(name="Setup",     value=data["setup"],                    inline=False)
                    embed.add_field(name="Punchline", value=f"||{data['punchline']}||",        inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(embed=error_embed("Error", "Could not fetch a joke."))

    # ── Meme ─────────────────────────────
    @commands.command(name="meme", help="Get a random meme")
    async def meme(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as resp:
                if resp.status == 200:
                    data  = await resp.json()
                    embed = discord.Embed(
                        title=data["title"],
                        url=data["postLink"],
                        color=config.COLORS["info"]
                    )
                    embed.set_image(url=data["url"])
                    embed.set_footer(text=f"👍 {data['ups']} | r/{data['subreddit']}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(embed=error_embed("Error", "Could not fetch a meme."))

    # ── Cat ──────────────────────────────
    @commands.command(name="cat", help="Random cat image")
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.thecatapi.com/v1/images/search") as resp:
                if resp.status == 200:
                    data  = await resp.json()
                    embed = discord.Embed(title="🐱 Random Cat", color=config.COLORS["info"])
                    embed.set_image(url=data[0]["url"])
                    await ctx.send(embed=embed)

    # ── Dog ──────────────────────────────
    @commands.command(name="dog", help="Random dog image")
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://dog.ceo/api/breeds/image/random") as resp:
                if resp.status == 200:
                    data  = await resp.json()
                    embed = discord.Embed(title="🐶 Random Dog", color=config.COLORS["info"])
                    embed.set_image(url=data["message"])
                    await ctx.send(embed=embed)

    # ── RPS ──────────────────────────────
    @commands.command(name="rps", help="Rock Paper Scissors")
    async def rps(self, ctx, choice: str):
        choices = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
        choice  = choice.lower()

        if choice not in choices:
            return await ctx.send(embed=error_embed("Error", "Choose: `rock`, `paper`, or `scissors`"))

        bot_choice = random.choice(list(choices.keys()))
        wins       = {"rock": "scissors", "paper": "rock", "scissors": "paper"}

        if choice == bot_choice:
            result, color = "🤝 It's a tie!", config.COLORS["warning"]
        elif wins[choice] == bot_choice:
            result, color = "🎉 You win!", config.COLORS["success"]
        else:
            result, color = "😔 You lose!", config.COLORS["error"]

        embed = discord.Embed(title="✂️ Rock Paper Scissors", color=color)
        embed.add_field(name="You",    value=f"{choices[choice]}    {choice.title()}",       inline=True)
        embed.add_field(name="Bot",    value=f"{choices[bot_choice]} {bot_choice.title()}", inline=True)
        embed.add_field(name="Result", value=result,                                          inline=False)
        await ctx.send(embed=embed)

    # ── Would You Rather ─────────────────
    @commands.command(name="wyr", help="Would you rather?")
    async def wyr(self, ctx):
        questions = [
            ("Be invisible",         "Be able to fly"),
            ("Have infinite money",  "Have infinite time"),
            ("Be a genius",          "Be the strongest person alive"),
            ("Travel to the past",   "Travel to the future"),
            ("Never eat pizza",      "Never eat burgers"),
            ("Know everything",      "Be loved by everyone"),
            ("Live in space",        "Live underwater"),
            ("Be super fast",        "Be super strong"),
            ("Always be too hot",    "Always be too cold"),
            ("Lose your memory",     "Lose your imagination"),
        ]
        a, b  = random.choice(questions)
        embed = discord.Embed(
            title="🤔 Would You Rather...",
            description=f"**🅰️  {a}**\n\nor\n\n**🅱️  {b}**",
            color=config.COLORS["purple"]
        )
        embed.set_footer(text="React to vote!")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🅰️")
        await msg.add_reaction("🅱️")

    # ── Roast ────────────────────────────
    @commands.command(name="roast", help="Roast a member")
    async def roast(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        roasts = [
            "You're like a cloud. When you disappear, it's a beautiful day.",
            "I'd roast you, but my mom said I'm not allowed to burn trash.",
            "You bring everyone so much joy when you leave.",
            "I'd explain it to you, but I don't have crayons.",
            "You're not stupid — you just have bad luck thinking.",
            "If I wanted to hear from someone like you, I'd go to the zoo.",
            "You're proof that evolution can go in reverse.",
            "Your brain is like a browser with 15 tabs open, 3 frozen, and you can't find the music.",
            "I've met some real characters in my time, but you're more like a rough draft.",
            "You're the reason the gene pool needs a lifeguard.",
        ]
        embed = discord.Embed(
            title=f"🔥 Roasting {member.display_name}",
            description=random.choice(roasts),
            color=config.COLORS["error"]
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    # ── Compliment ───────────────────────
    @commands.command(name="compliment", aliases=["praise"], help="Compliment a member")
    async def compliment(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        compliments = [
            "You light up every room you walk into!",
            "You have the best ideas — seriously impressive.",
            "You make the world a better place just by being in it.",
            "Your determination is truly inspiring.",
            "You're one of the most genuine people around.",
            "Your creativity knows no bounds!",
            "You have an incredible ability to make people feel seen.",
            "You're basically a walking, talking ray of sunshine.",
        ]
        embed = discord.Embed(
            title=f"💖 Complimenting {member.display_name}",
            description=random.choice(compliments),
            color=config.COLORS["pink"]
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    # ── Rate ──────────────────────────────
    @commands.command(name="rate", help="Rate anything out of 10")
    async def rate(self, ctx, *, thing: str):
        score = random.randint(0, 100) / 10
        bar   = "█" * int(score) + "░" * (10 - int(score))
        embed = discord.Embed(
            title=f"📊 Rating: {thing}",
            description=f"Score: **{score}/10**\n`[{bar}]`",
            color=config.COLORS["gold"]
        )
        await ctx.send(embed=embed)

    # ── Hug ──────────────────────────────
    @commands.command(name="hug", help="Hug someone")
    async def hug(self, ctx, member: discord.Member):
        embed = discord.Embed(
            title="🤗 Hug!",
            description=f"{ctx.author.mention} gave {member.mention} a big warm hug! 🤗",
            color=config.COLORS["pink"]
        )
        await ctx.send(embed=embed)

    # ── Slap ─────────────────────────────
    @commands.command(name="slap", help="Slap someone")
    async def slap(self, ctx, member: discord.Member):
        embed = discord.Embed(
            title="👋 Slap!",
            description=f"{ctx.author.mention} slapped {member.mention}! 💥",
            color=config.COLORS["error"]
        )
        await ctx.send(embed=embed)

    # ── Choose ───────────────────────────
    @commands.command(name="choose", help="Choose between options (separate with |)")
    async def choose(self, ctx, *, options: str):
        choices = [c.strip() for c in options.split("|") if c.strip()]
        if len(choices) < 2:
            return await ctx.send(embed=error_embed("Error", "Provide at least 2 options separated by `|`"))

        chosen = random.choice(choices)
        embed  = discord.Embed(
            title="🤔 I Choose...",
            description=f"**{chosen}**",
            color=config.COLORS["purple"]
        )
        embed.add_field(name="Options", value="\n".join(f"• {c}" for c in choices), inline=False)
        await ctx.send(embed=embed)

    # ── Reverse ──────────────────────────
    @commands.command(name="reverse", help="Reverse some text")
    async def reverse(self, ctx, *, text: str):
        embed = discord.Embed(
            title="🔄 Reversed",
            description=text[::-1],
            color=config.COLORS["info"]
        )
        await ctx.send(embed=embed)

    # ── Mock ─────────────────────────────
    @commands.command(name="mock", help="MoCk SoMeOnE's TeXt")
    async def mock(self, ctx, *, text: str):
        mocked = "".join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))
        embed  = discord.Embed(description=mocked, color=config.COLORS["warning"])
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))