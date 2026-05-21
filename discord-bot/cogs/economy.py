import discord
from discord.ext import commands
from datetime import datetime
import random
from database.db import Database
from utils.embeds import success_embed, error_embed, warning_embed, info_embed
from utils.helpers import is_on_cooldown, format_time
import config

# ─────────────────────────────────────────
#  Economy Cog
# ─────────────────────────────────────────

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    # ── Balance ──────────────────────────
    @commands.command(name="balance", aliases=["bal", "wallet", "money"], help="Check your balance")
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        data   = await self.db.get_user(member.id, ctx.guild.id)

        embed = discord.Embed(title=f"💰 {member.display_name}'s Wallet", color=config.COLORS["gold"])
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👛 Wallet", value=f"**{data['coins']:,}** coins",              inline=True)
        embed.add_field(name="🏦 Bank",   value=f"**{data['bank']:,}** coins",               inline=True)
        embed.add_field(name="💎 Total",  value=f"**{data['coins'] + data['bank']:,}** coins", inline=False)
        await ctx.send(embed=embed)

    # ── Daily ────────────────────────────
    @commands.command(name="daily", help=f"Claim your daily coins")
    async def daily(self, ctx):
        data     = await self.db.get_user(ctx.author.id, ctx.guild.id)
        on_cd, remaining = is_on_cooldown(data["last_daily"], 86400)

        if on_cd:
            return await ctx.send(embed=warning_embed(
                "Already Claimed",
                f"⏰ Come back in **{format_time(remaining)}**!"
            ))

        bonus = random.randint(0, 50)
        total = config.DAILY_COINS + bonus
        await self.db.update_user(
            ctx.author.id, ctx.guild.id,
            coins    = data["coins"] + total,
            last_daily = datetime.utcnow().isoformat()
        )
        embed = success_embed(
            "Daily Reward!",
            f"You received **{config.DAILY_COINS:,}** + **{bonus}** bonus = **{total:,}** coins! 🎉"
        )
        await ctx.send(embed=embed)

    # ── Work ─────────────────────────────
    @commands.command(name="work", help="Work to earn coins (1h cooldown)")
    async def work(self, ctx):
        data  = await self.db.get_user(ctx.author.id, ctx.guild.id)
        on_cd, remaining = is_on_cooldown(data["last_work"], 3600)

        if on_cd:
            return await ctx.send(embed=warning_embed(
                "Tired!",
                f"🛌 Rest for **{format_time(remaining)}** before working again."
            ))

        jobs = [
            ("👨‍💻 Software Developer", "wrote some amazing code"),
            ("🎨 Graphic Artist",       "designed a beautiful logo"),
            ("🍕 Pizza Delivery",       "delivered 20 hot pizzas"),
            ("📦 Warehouse Worker",     "packed boxes all day"),
            ("🎮 Game Tester",          "found 5 critical bugs"),
            ("✍️  Writer",             "wrote a compelling article"),
            ("🔧 Mechanic",             "fixed 3 broken cars"),
            ("🌮 Chef",                "cooked for 50 hungry people"),
            ("🎵 DJ",                  "played an epic set at the club"),
            ("📸 Photographer",        "shot a beautiful wedding"),
            ("🧑‍🏫 Teacher",           "taught an online coding class"),
            ("🚚 Truck Driver",         "delivered cargo across the country"),
        ]

        job, action = random.choice(jobs)
        earned      = random.randint(config.WORK_MIN_COINS, config.WORK_MAX_COINS)

        await self.db.update_user(
            ctx.author.id, ctx.guild.id,
            coins     = data["coins"] + earned,
            last_work = datetime.utcnow().isoformat()
        )
        await ctx.send(embed=success_embed(f"{job}", f"You {action} and earned **{earned:,}** coins!"))

    # ── Deposit ──────────────────────────
    @commands.command(name="deposit", aliases=["dep"], help="Deposit coins to your bank")
    async def deposit(self, ctx, amount: str):
        data   = await self.db.get_user(ctx.author.id, ctx.guild.id)
        wallet = data["coins"]

        amount = wallet if amount.lower() == "all" else int(amount)

        if amount <= 0:
            return await ctx.send(embed=error_embed("Error", "Amount must be positive!"))
        if amount > wallet:
            return await ctx.send(embed=error_embed("Error", f"You only have **{wallet:,}** coins in your wallet!"))

        await self.db.update_user(
            ctx.author.id, ctx.guild.id,
            coins = wallet - amount,
            bank  = data["bank"] + amount
        )
        await ctx.send(embed=success_embed("Deposited!", f"Moved **{amount:,}** coins to your bank 🏦"))

    # ── Withdraw ─────────────────────────
    @commands.command(name="withdraw", aliases=["with"], help="Withdraw coins from your bank")
    async def withdraw(self, ctx, amount: str):
        data = await self.db.get_user(ctx.author.id, ctx.guild.id)
        bank = data["bank"]

        amount = bank if amount.lower() == "all" else int(amount)

        if amount <= 0:
            return await ctx.send(embed=error_embed("Error", "Amount must be positive!"))
        if amount > bank:
            return await ctx.send(embed=error_embed("Error", f"You only have **{bank:,}** coins in your bank!"))

        await self.db.update_user(
            ctx.author.id, ctx.guild.id,
            coins = data["coins"] + amount,
            bank  = bank - amount
        )
        await ctx.send(embed=success_embed("Withdrawn!", f"Moved **{amount:,}** coins to your wallet 👛"))

    # ── Pay ──────────────────────────────
    @commands.command(name="pay", aliases=["give", "transfer"], help="Pay another member coins")
    async def pay(self, ctx, member: discord.Member, amount: int):
        if member == ctx.author:
            return await ctx.send(embed=error_embed("Error", "You can't pay yourself!"))
        if member.bot:
            return await ctx.send(embed=error_embed("Error", "You can't pay bots!"))
        if amount <= 0:
            return await ctx.send(embed=error_embed("Error", "Amount must be positive!"))

        data = await self.db.get_user(ctx.author.id, ctx.guild.id)
        if data["coins"] < amount:
            return await ctx.send(embed=error_embed("Error", f"You don't have enough coins! Balance: **{data['coins']:,}**"))

        target = await self.db.get_user(member.id, ctx.guild.id)
        await self.db.update_user(ctx.author.id, ctx.guild.id, coins=data["coins"] - amount)
        await self.db.update_user(member.id,      ctx.guild.id, coins=target["coins"] + amount)

        await ctx.send(embed=success_embed(
            "Payment Sent!",
            f"You sent **{amount:,}** coins to {member.mention} 💸"
        ))

    # ── Gamble ───────────────────────────
    @commands.command(name="gamble", aliases=["bet", "g"], help="Gamble your coins")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def gamble(self, ctx, amount: str):
        data   = await self.db.get_user(ctx.author.id, ctx.guild.id)
        wallet = data["coins"]

        try:
            amount = wallet if amount.lower() == "all" else int(amount)
        except ValueError:
            return await ctx.send(embed=error_embed("Error", "Enter a number or `all`"))

        if amount <= 0:
            return await ctx.send(embed=error_embed("Error", "Amount must be positive!"))
        if amount > wallet:
            return await ctx.send(embed=error_embed("Error", "Not enough coins!"))

        roll = random.randint(1, 100)

        if roll >= 55:
            mult     = 1.0 if roll < 80 else 1.5 if roll < 95 else 3.0
            winnings = int(amount * mult)
            new_bal  = wallet + winnings
            await self.db.update_user(ctx.author.id, ctx.guild.id, coins=new_bal)
            embed = success_embed(
                "🎰 You Won!",
                f"Rolled **{roll}** (×{mult}) → Won **{winnings:,}** coins!\nBalance: **{new_bal:,}**"
            )
        else:
            new_bal = wallet - amount
            await self.db.update_user(ctx.author.id, ctx.guild.id, coins=new_bal)
            embed = error_embed(
                "🎰 You Lost!",
                f"Rolled **{roll}** → Lost **{amount:,}** coins!\nBalance: **{new_bal:,}**"
            )
        await ctx.send(embed=embed)

    # ── Rob ──────────────────────────────
    @commands.command(name="rob", aliases=["steal"], help="Try to rob another member")
    async def rob(self, ctx, member: discord.Member):
        if member == ctx.author:
            return await ctx.send(embed=error_embed("Error", "You can't rob yourself!"))
        if member.bot:
            return await ctx.send(embed=error_embed("Error", "You can't rob bots!"))

        data  = await self.db.get_user(ctx.author.id, ctx.guild.id)
        on_cd, remaining = is_on_cooldown(data["last_rob"], 7200)

        if on_cd:
            return await ctx.send(embed=warning_embed("Cooldown", f"Wait **{format_time(remaining)}** before robbing again."))

        target = await self.db.get_user(member.id, ctx.guild.id)
        if target["coins"] < 100:
            return await ctx.send(embed=error_embed("Broke!", f"**{member.display_name}** is too poor to rob (< 100 coins)."))

        if random.randint(1, 100) <= config.ROB_SUCCESS_RATE:
            stolen  = random.randint(50, min(target["coins"], 500))
            await self.db.update_user(ctx.author.id, ctx.guild.id, coins=data["coins"] + stolen, last_rob=datetime.utcnow().isoformat())
            await self.db.update_user(member.id,      ctx.guild.id, coins=target["coins"] - stolen)
            embed = success_embed("Robbery Success! 🦹", f"You stole **{stolen:,}** coins from {member.mention}!")
        else:
            fine = int(data["coins"] * config.ROB_FINE_PERCENT / 100)
            await self.db.update_user(ctx.author.id, ctx.guild.id, coins=max(0, data["coins"] - fine), last_rob=datetime.utcnow().isoformat())
            embed = error_embed("Caught! 🚔", f"You were caught and fined **{fine:,}** coins!")

        await ctx.send(embed=embed)

    # ── Slots ────────────────────────────
    @commands.command(name="slots", help="Play the slot machine")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def slots(self, ctx, bet: int = 50):
        data = await self.db.get_user(ctx.author.id, ctx.guild.id)
        if bet <= 0 or bet > data["coins"]:
            return await ctx.send(embed=error_embed("Error", f"Invalid bet! You have **{data['coins']:,}** coins."))

        symbols  = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
        weights  = [30,   25,   20,   15,   7,    3]
        reels    = random.choices(symbols, weights=weights, k=3)

        if reels[0] == reels[1] == reels[2]:
            mults  = {"🍒": 3, "🍋": 4, "🍊": 5, "🍇": 8, "💎": 15, "7️⃣": 50}
            mult   = mults.get(reels[0], 3)
            win    = bet * mult
            result = f"🎉 JACKPOT! ×{mult} → +**{win:,}** coins!"
            color  = config.COLORS["gold"]
            await self.db.update_user(ctx.author.id, ctx.guild.id, coins=data["coins"] + win)
        elif reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
            result = f"✨ Two of a kind! +**{bet:,}** coins!"
            color  = config.COLORS["success"]
            await self.db.update_user(ctx.author.id, ctx.guild.id, coins=data["coins"] + bet)
        else:
            result = f"😔 No match. -**{bet:,}** coins."
            color  = config.COLORS["error"]
            await self.db.update_user(ctx.author.id, ctx.guild.id, coins=data["coins"] - bet)

        embed = discord.Embed(title="🎰 Slot Machine", color=color)
        embed.add_field(name="Reels",   value=f"**[ {reels[0]} | {reels[1]} | {reels[2]} ]**", inline=False)
        embed.add_field(name="Result",  value=result,                                           inline=False)
        await ctx.send(embed=embed)

    # ── Shop ─────────────────────────────
    @commands.command(name="shop", help="View the server shop")
    async def shop(self, ctx):
        items = await self.db.get_shop_items(ctx.guild.id)
        if not items:
            return await ctx.send(embed=info_embed("Empty Shop", "No items are available yet!"))

        embed = discord.Embed(title=f"🛒 {ctx.guild.name} Shop", color=config.COLORS["gold"])
        for item in items:
            stock     = "∞" if item["stock"] == -1 else str(item["stock"])
            role_text = f"\n🎭 Gives <@&{item['role_id']}>" if item["role_id"] else ""
            embed.add_field(
                name  = f"{item['item_name']} — {item['price']:,} coins",
                value = f"{item['item_desc']}\n📦 Stock: {stock}{role_text}",
                inline= False
            )
        embed.set_footer(text=f"Buy with: !buy <item name>")
        await ctx.send(embed=embed)

    # ── Buy ──────────────────────────────
    @commands.command(name="buy", help="Buy an item from the shop")
    async def buy(self, ctx, *, item_name: str):
        items = await self.db.get_shop_items(ctx.guild.id)
        item  = next((i for i in items if i["item_name"].lower() == item_name.lower()), None)

        if not item:
            return await ctx.send(embed=error_embed("Not Found", f"No item named `{item_name}`. Use `!shop` to browse."))

        data = await self.db.get_user(ctx.author.id, ctx.guild.id)
        if data["coins"] < item["price"]:
            short = item["price"] - data["coins"]
            return await ctx.send(embed=error_embed("Too Poor", f"You need **{short:,}** more coins!"))

        if item["stock"] == 0:
            return await ctx.send(embed=error_embed("Out of Stock", "This item is sold out!"))

        await self.db.update_user(ctx.author.id, ctx.guild.id, coins=data["coins"] - item["price"])
        await self.db.add_to_inventory(ctx.author.id, ctx.guild.id, item["item_name"])

        if item["role_id"]:
            role = ctx.guild.get_role(item["role_id"])
            if role:
                await ctx.author.add_roles(role)

        await ctx.send(embed=success_embed(
            "Purchased!",
            f"You bought **{item['item_name']}** for **{item['price']:,}** coins!"
        ))

    # ── Inventory ────────────────────────
    @commands.command(name="inventory", aliases=["inv", "bag"], help="View your inventory")
    async def inventory(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        inv    = await self.db.get_inventory(member.id, ctx.guild.id)

        if not inv:
            return await ctx.send(embed=info_embed("Empty Inventory", f"**{member.display_name}** doesn't own anything yet!"))

        embed = discord.Embed(title=f"🎒 {member.display_name}'s Inventory", color=config.COLORS["purple"])
        for item in inv:
            embed.add_field(name=item["item_name"], value=f"Qty: **{item['quantity']}**", inline=True)
        await ctx.send(embed=embed)

    # ── Richest ──────────────────────────
    @commands.command(name="richest", aliases=["rich", "topmoney"], help="Richest members leaderboard")
    async def richest(self, ctx):
        rows   = await self.db.get_leaderboard(ctx.guild.id, "coins")
        medals = ["🥇", "🥈", "🥉"]
        desc   = ""

        for i, row in enumerate(rows):
            member = ctx.guild.get_member(row["user_id"])
            name   = member.display_name if member else f"User {row['user_id']}"
            medal  = medals[i] if i < 3 else f"`{i+1}.`"
            total  = row["coins"] + row["bank"]
            desc  += f"{medal} **{name}** — {total:,} coins\n"

        embed = discord.Embed(
            title       = f"💰 Richest in {ctx.guild.name}",
            description = desc or "No data yet!",
            color       = config.COLORS["gold"]
        )
        await ctx.send(embed=embed)

    # ── Rep ──────────────────────────────
    @commands.command(name="rep", help="Give rep to a member (24h cooldown)")
    async def rep(self, ctx, member: discord.Member):
        if member == ctx.author:
            return await ctx.send(embed=error_embed("Error", "You can't rep yourself!"))

        data  = await self.db.get_user(ctx.author.id, ctx.guild.id)
        on_cd, remaining = is_on_cooldown(data["last_rep"], 86400)

        if on_cd:
            return await ctx.send(embed=warning_embed("Cooldown", f"Wait **{format_time(remaining)}** before repping again."))

        target = await self.db.get_user(member.id, ctx.guild.id)
        await self.db.update_user(member.id, ctx.guild.id, reputation=target["reputation"] + 1)
        await self.db.update_user(ctx.author.id, ctx.guild.id, last_rep=datetime.utcnow().isoformat())

        await ctx.send(embed=success_embed(
            "Rep Given! ⭐",
            f"You gave **{member.display_name}** a rep point!\nThey now have **{target['reputation'] + 1}** rep."
        ))


async def setup(bot):
    await bot.add_cog(Economy(bot))