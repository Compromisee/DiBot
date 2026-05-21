import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import random
from database.db import Database
from utils.embeds import success_embed, error_embed, info_embed, profile_embed
from utils.helpers import xp_for_level, progress_bar, is_on_cooldown, format_time, parse_duration
from utils.views import ConfirmView, GiveawayView, TicketView, PaginatorView
import config

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    # ═══════════════════════════════════
    #  UTILITY SLASH COMMANDS
    # ═══════════════════════════════════

    @app_commands.command(name="ping", description="Check bot latency")
    async def slash_ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**Latency:** {latency}ms\n**API:** {round(self.bot.latency * 1000)}ms",
            color=config.COLORS["success"] if latency < 100 else config.COLORS["warning"]
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Show all bot commands")
    async def slash_help(self, interaction: discord.Interaction):
        pages = []

        # Page 1 - Overview
        embed1 = discord.Embed(title=f"📖 {config.BOT_NAME} Help", description="Navigate using buttons below!", color=config.COLORS["blurple"])
        embed1.add_field(name="🛡️ Moderation", value="`/kick` `/ban` `/mute` `/warn` `/purge` `/lock` `/tempban`", inline=False)
        embed1.add_field(name="💰 Economy", value="`/balance` `/daily` `/work` `/deposit` `/withdraw` `/pay` `/gamble` `/rob` `/shop` `/buy`", inline=False)
        embed1.add_field(name="⭐ Leveling", value="`/rank` `/leaderboard` `/levelrole`", inline=False)
        embed1.set_footer(text="Page 1/4")
        pages.append(embed1)

        # Page 2
        embed2 = discord.Embed(title=f"📖 {config.BOT_NAME} Help", color=config.COLORS["blurple"])
        embed2.add_field(name="🎉 Fun", value="`/8ball` `/coinflip` `/roll` `/joke` `/meme` `/rps` `/roast` `/wyr`", inline=False)
        embed2.add_field(name="🎮 Games", value="`/trivia` `/guess` `/slots` `/tictactoe` `/connect4`", inline=False)
        embed2.add_field(name="🔧 Utility", value="`/profile` `/serverinfo` `/userinfo` `/avatar` `/poll` `/remind` `/afk`", inline=False)
        embed2.set_footer(text="Page 2/4")
        pages.append(embed2)

        # Page 3
        embed3 = discord.Embed(title=f"📖 {config.BOT_NAME} Help", color=config.COLORS["blurple"])
        embed3.add_field(name="🎉 Giveaways", value="`/giveaway` `/giveaway reroll` `/giveaway end`", inline=False)
        embed3.add_field(name="🎫 Tickets", value="`/ticket setup` `/ticket close` `/ticket add`", inline=False)
        embed3.add_field(name="⭐ Starboard", value="`/starboard setup` Auto-detects ⭐ reactions", inline=False)
        embed3.add_field(name="💡 Suggestions", value="`/suggest` `/suggestion approve` `/suggestion deny`", inline=False)
        embed3.set_footer(text="Page 3/4")
        pages.append(embed3)

        # Page 4
        embed4 = discord.Embed(title=f"📖 {config.BOT_NAME} Help", color=config.COLORS["blurple"])
        embed4.add_field(name="⚙️ Admin", value="`/setup` `/setwelcome` `/setlog` `/autorole` `/addcoins` `/setxp` `/announce`", inline=False)
        embed4.add_field(name="🏷️ Tags", value="`/tag create` `/tag get` `/tag list` `/tag delete`", inline=False)
        embed4.add_field(name="🎭 Reaction Roles", value="`/reactionrole add` `/reactionrole remove`", inline=False)
        embed4.add_field(name="🌐 Dashboard", value=f"[Open Dashboard](http://localhost:{config.DASHBOARD_PORT})", inline=False)
        embed4.set_footer(text="Page 4/4")
        pages.append(embed4)

        view = PaginatorView(pages, interaction.user.id)
        await interaction.response.send_message(embed=pages[0], view=view)

    @app_commands.command(name="profile", description="View your or another member's profile")
    @app_commands.describe(member="The member to view")
    async def slash_profile(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        data = await self.db.get_user(member.id, interaction.guild.id)
        embed = profile_embed(member, data)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="View server information")
    async def slash_serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        bots = sum(1 for m in g.members if m.bot)
        embed = discord.Embed(title=f"📊 {g.name}", color=config.COLORS["info"], timestamp=datetime.utcnow())
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="👑 Owner", value=g.owner.mention, inline=True)
        embed.add_field(name="👥 Members", value=f"{g.member_count} ({g.member_count - bots} humans)", inline=True)
        embed.add_field(name="📺 Channels", value=f"{len(g.text_channels)} text / {len(g.voice_channels)} voice", inline=True)
        embed.add_field(name="🎭 Roles", value=len(g.roles), inline=True)
        embed.add_field(name="😀 Emojis", value=len(g.emojis), inline=True)
        embed.add_field(name="🔒 Verification", value=str(g.verification_level), inline=True)
        embed.add_field(name="📅 Created", value=f"<t:{int(g.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="🆔 ID", value=g.id, inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="View user information")
    @app_commands.describe(member="The member to view")
    async def slash_userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        roles = [r.mention for r in reversed(member.roles) if r != interaction.guild.default_role]
        embed = discord.Embed(title=f"👤 {member}", color=member.color, timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🆔 ID", value=member.id, inline=True)
        embed.add_field(name="🏷️ Nick", value=member.nick or "None", inline=True)
        embed.add_field(name="🤖 Bot", value="Yes" if member.bot else "No", inline=True)
        embed.add_field(name="📅 Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="📅 Joined Server", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
        embed.add_field(name=f"🎭 Roles ({len(roles)})", value=" ".join(roles[:15]) or "None", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="View a member's avatar")
    @app_commands.describe(member="The member whose avatar to view")
    async def slash_avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"🖼️ {member.display_name}'s Avatar", color=config.COLORS["info"])
        embed.set_image(url=member.display_avatar.with_size(1024).url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="afk", description="Set your AFK status")
    @app_commands.describe(message="Your AFK message")
    async def slash_afk(self, interaction: discord.Interaction, message: str = "AFK"):
        await self.db.update_user(
            interaction.user.id, interaction.guild.id,
            afk_message=message,
            afk_since=datetime.utcnow().isoformat()
        )
        embed = success_embed("AFK Set", f"💤 {interaction.user.mention} is now AFK: **{message}**")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remind", description="Set a reminder")
    @app_commands.describe(duration="Duration (e.g. 1h30m, 2d, 30m)", message="What to remind you about")
    async def slash_remind(self, interaction: discord.Interaction, duration: str, message: str):
        try:
            td = parse_duration(duration)
        except ValueError:
            return await interaction.response.send_message(embed=error_embed("Invalid Duration", "Use format: `1d2h30m`"), ephemeral=True)

        remind_at = datetime.utcnow() + td
        await self.db.create_reminder(interaction.user.id, interaction.channel.id, interaction.guild.id, message, remind_at.isoformat())
        embed = success_embed("Reminder Set!", f"I'll remind you <t:{int(remind_at.timestamp())}:R>\n**Message:** {message}")
        await interaction.response.send_message(embed=embed)

    # ═══════════════════════════════════
    #  ECONOMY SLASH COMMANDS
    # ═══════════════════════════════════

    @app_commands.command(name="balance", description="Check your balance")
    @app_commands.describe(member="Member to check")
    async def slash_balance(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        data = await self.db.get_user(member.id, interaction.guild.id)
        embed = discord.Embed(title=f"💰 {member.display_name}'s Wallet", color=config.COLORS["gold"])
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="👛 Wallet", value=f"**{data['coins']:,}**", inline=True)
        embed.add_field(name="🏦 Bank", value=f"**{data['bank']:,}**", inline=True)
        embed.add_field(name="💎 Total", value=f"**{data['coins']+data['bank']:,}**", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="daily", description="Collect your daily coins")
    async def slash_daily(self, interaction: discord.Interaction):
        data = await self.db.get_user(interaction.user.id, interaction.guild.id)
        on_cd, remaining = is_on_cooldown(data["last_daily"], 86400)
        if on_cd:
            return await interaction.response.send_message(embed=warning_embed("Already Claimed", f"Come back in **{format_time(remaining)}**!"), ephemeral=True)

        streak_bonus = random.randint(0, 50)
        total = config.DAILY_COINS + streak_bonus
        await self.db.update_user(interaction.user.id, interaction.guild.id, coins=data["coins"] + total, last_daily=datetime.utcnow().isoformat())
        embed = success_embed("Daily Claimed!", f"You received **{config.DAILY_COINS:,}** + **{streak_bonus}** bonus = **{total:,}** coins! 🎉")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="Work to earn coins")
    async def slash_work(self, interaction: discord.Interaction):
        data = await self.db.get_user(interaction.user.id, interaction.guild.id)
        on_cd, remaining = is_on_cooldown(data["last_work"], 3600)
        if on_cd:
            return await interaction.response.send_message(embed=warning_embed("Tired!", f"Rest for **{format_time(remaining)}**"), ephemeral=True)

        jobs = [
            ("👨‍💻 Developer", "wrote clean code"), ("🎨 Artist", "painted a masterpiece"),
            ("🍕 Pizza Chef", "made 30 pizzas"), ("📦 Delivery Driver", "delivered packages"),
            ("🎮 Game Tester", "found 5 bugs"), ("✍️ Writer", "wrote an article"),
            ("🔧 Mechanic", "fixed 3 cars"), ("🌮 Chef", "cooked for 50 people"),
            ("🎵 DJ", "played a sick set"), ("📸 Photographer", "took wedding photos"),
            ("🏗️ Builder", "built a house"), ("🧑‍🔬 Scientist", "discovered a formula"),
        ]
        job, action = random.choice(jobs)
        earned = random.randint(config.WORK_MIN_COINS, config.WORK_MAX_COINS)
        await self.db.update_user(interaction.user.id, interaction.guild.id, coins=data["coins"] + earned, last_work=datetime.utcnow().isoformat())
        embed = success_embed(f"{job}", f"You {action} and earned **{earned:,}** coins!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deposit", description="Deposit coins to bank")
    @app_commands.describe(amount="Amount to deposit (or 'all')")
    async def slash_deposit(self, interaction: discord.Interaction, amount: str):
        data = await self.db.get_user(interaction.user.id, interaction.guild.id)
        amt = data["coins"] if amount.lower() == "all" else int(amount)
        if amt <= 0 or amt > data["coins"]:
            return await interaction.response.send_message(embed=error_embed("Error", "Invalid amount!"), ephemeral=True)
        await self.db.update_user(interaction.user.id, interaction.guild.id, coins=data["coins"] - amt, bank=data["bank"] + amt)
        await interaction.response.send_message(embed=success_embed("Deposited!", f"Moved **{amt:,}** coins to bank 🏦"))

    @app_commands.command(name="withdraw", description="Withdraw coins from bank")
    @app_commands.describe(amount="Amount to withdraw (or 'all')")
    async def slash_withdraw(self, interaction: discord.Interaction, amount: str):
        data = await self.db.get_user(interaction.user.id, interaction.guild.id)
        amt = data["bank"] if amount.lower() == "all" else int(amount)
        if amt <= 0 or amt > data["bank"]:
            return await interaction.response.send_message(embed=error_embed("Error", "Invalid amount!"), ephemeral=True)
        await self.db.update_user(interaction.user.id, interaction.guild.id, coins=data["coins"] + amt, bank=data["bank"] - amt)
        await interaction.response.send_message(embed=success_embed("Withdrawn!", f"Moved **{amt:,}** coins to wallet 👛"))

    @app_commands.command(name="pay", description="Pay another member")
    @app_commands.describe(member="Who to pay", amount="How much to pay")
    async def slash_pay(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if member == interaction.user:
            return await interaction.response.send_message(embed=error_embed("Error", "Can't pay yourself!"), ephemeral=True)
        data = await self.db.get_user(interaction.user.id, interaction.guild.id)
        if amount <= 0 or amount > data["coins"]:
            return await interaction.response.send_message(embed=error_embed("Error", "Invalid amount!"), ephemeral=True)
        target = await self.db.get_user(member.id, interaction.guild.id)
        await self.db.update_user(interaction.user.id, interaction.guild.id, coins=data["coins"] - amount)
        await self.db.update_user(member.id, interaction.guild.id, coins=target["coins"] + amount)
        await interaction.response.send_message(embed=success_embed("Payment Sent!", f"Sent **{amount:,}** coins to {member.mention} 💸"))

    @app_commands.command(name="gamble", description="Gamble your coins")
    @app_commands.describe(amount="Amount to gamble (or 'all')")
    async def slash_gamble(self, interaction: discord.Interaction, amount: str):
        data = await self.db.get_user(interaction.user.id, interaction.guild.id)
        amt = data["coins"] if amount.lower() == "all" else int(amount)
        if amt <= 0 or amt > data["coins"]:
            return await interaction.response.send_message(embed=error_embed("Error", "Invalid amount!"), ephemeral=True)

        roll = random.randint(1, 100)
        if roll >= 55:
            multiplier = 1.0 if roll < 80 else 1.5 if roll < 95 else 3.0
            winnings = int(amt * multiplier)
            new_bal = data["coins"] + winnings
            await self.db.update_user(interaction.user.id, interaction.guild.id, coins=new_bal)
            embed = success_embed("🎰 You Won!", f"Rolled **{roll}** (x{multiplier}) — Won **{winnings:,}**!\nBalance: **{new_bal:,}**")
        else:
            new_bal = data["coins"] - amt
            await self.db.update_user(interaction.user.id, interaction.guild.id, coins=new_bal)
            embed = error_embed("🎰 You Lost!", f"Rolled **{roll}** — Lost **{amt:,}**!\nBalance: **{new_bal:,}**")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rob", description="Rob another member")
    @app_commands.describe(member="Who to rob")
    async def slash_rob(self, interaction: discord.Interaction, member: discord.Member):
        if member == interaction.user:
            return await interaction.response.send_message(embed=error_embed("Error", "Can't rob yourself!"), ephemeral=True)

        data = await self.db.get_user(interaction.user.id, interaction.guild.id)
        on_cd, remaining = is_on_cooldown(data["last_rob"], 7200)
        if on_cd:
            return await interaction.response.send_message(embed=warning_embed("Cooldown", f"Wait **{format_time(remaining)}**"), ephemeral=True)

        target = await self.db.get_user(member.id, interaction.guild.id)
        if target["coins"] < 100:
            return await interaction.response.send_message(embed=error_embed("Error", "They're too poor to rob!"), ephemeral=True)

        if random.randint(1, 100) <= config.ROB_SUCCESS_RATE:
            stolen = random.randint(1, min(target["coins"], 500))
            await self.db.update_user(interaction.user.id, interaction.guild.id, coins=data["coins"] + stolen, last_rob=datetime.utcnow().isoformat())
            await self.db.update_user(member.id, interaction.guild.id, coins=target["coins"] - stolen)
            embed = success_embed("Robbery Successful! 🦹", f"You stole **{stolen:,}** coins from {member.mention}!")
        else:
            fine = int(data["coins"] * config.ROB_FINE_PERCENT / 100)
            await self.db.update_user(interaction.user.id, interaction.guild.id, coins=data["coins"] - fine, last_rob=datetime.utcnow().isoformat())
            embed = error_embed("Caught! 🚔", f"You got caught and fined **{fine:,}** coins!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shop", description="View the server shop")
    async def slash_shop(self, interaction: discord.Interaction):
        items = await self.db.get_shop_items(interaction.guild.id)
        if not items:
            return await interaction.response.send_message(embed=info_embed("Shop Empty", "No items in shop! Admins can add items."))

        embed = discord.Embed(title=f"🛒 {interaction.guild.name}'s Shop", color=config.COLORS["gold"])
        for item in items:
            stock = "∞" if item["stock"] == -1 else str(item["stock"])
            role_text = f" | Gives <@&{item['role_id']}>" if item["role_id"] else ""
            embed.add_field(
                name=f"{item['item_name']} — {item['price']:,} coins",
                value=f"{item['item_desc']}\nStock: {stock}{role_text}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Buy an item from the shop")
    @app_commands.describe(item_name="Name of the item to buy")
    async def slash_buy(self, interaction: discord.Interaction, item_name: str):
        items = await self.db.get_shop_items(interaction.guild.id)
        item = next((i for i in items if i["item_name"].lower() == item_name.lower()), None)
        if not item:
            return await interaction.response.send_message(embed=error_embed("Not Found", "Item doesn't exist!"), ephemeral=True)

        data = await self.db.get_user(interaction.user.id, interaction.guild.id)
        if data["coins"] < item["price"]:
            return await interaction.response.send_message(embed=error_embed("Too Poor", f"You need **{item['price'] - data['coins']:,}** more coins!"), ephemeral=True)

        if item["stock"] == 0:
            return await interaction.response.send_message(embed=error_embed("Out of Stock", "This item is sold out!"), ephemeral=True)

        await self.db.update_user(interaction.user.id, interaction.guild.id, coins=data["coins"] - item["price"])
        await self.db.add_to_inventory(interaction.user.id, interaction.guild.id, item["item_name"])

        if item["role_id"]:
            role = interaction.guild.get_role(item["role_id"])
            if role:
                await interaction.user.add_roles(role)

        await interaction.response.send_message(embed=success_embed("Purchased!", f"You bought **{item['item_name']}** for **{item['price']:,}** coins!"))

    @app_commands.command(name="inventory", description="View your inventory")
    async def slash_inventory(self, interaction: discord.Interaction):
        inv = await self.db.get_inventory(interaction.user.id, interaction.guild.id)
        if not inv:
            return await interaction.response.send_message(embed=info_embed("Empty Inventory", "You don't own anything!"))

        embed = discord.Embed(title=f"🎒 {interaction.user.display_name}'s Inventory", color=config.COLORS["purple"])
        for item in inv:
            embed.add_field(name=item["item_name"], value=f"Quantity: **{item['quantity']}**", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="richest", description="View the richest members")
    async def slash_richest(self, interaction: discord.Interaction):
        rows = await self.db.get_leaderboard(interaction.guild.id, "coins")
        medals = ["🥇", "🥈", "🥉"]
        desc = ""
        for i, row in enumerate(rows):
            member = interaction.guild.get_member(row["user_id"])
            name = member.display_name if member else f"User {row['user_id']}"
            medal = medals[i] if i < 3 else f"`{i+1}.`"
            desc += f"{medal} **{name}** — {row['coins'] + row['bank']:,} coins\n"
        embed = discord.Embed(title=f"💰 Richest in {interaction.guild.name}", description=desc or "No data!", color=config.COLORS["gold"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rep", description="Give reputation to a member")
    @app_commands.describe(member="Who to give rep to")
    async def slash_rep(self, interaction: discord.Interaction, member: discord.Member):
        if member == interaction.user:
            return await interaction.response.send_message(embed=error_embed("Error", "Can't rep yourself!"), ephemeral=True)
        data = await self.db.get_user(interaction.user.id, interaction.guild.id)
        on_cd, remaining = is_on_cooldown(data["last_rep"], 86400)
        if on_cd:
            return await interaction.response.send_message(embed=warning_embed("Cooldown", f"Wait **{format_time(remaining)}**"), ephemeral=True)

        target = await self.db.get_user(member.id, interaction.guild.id)
        await self.db.update_user(member.id, interaction.guild.id, reputation=target["reputation"] + 1)
        await self.db.update_user(interaction.user.id, interaction.guild.id, last_rep=datetime.utcnow().isoformat())
        await interaction.response.send_message(embed=success_embed("Rep Given!", f"You gave a rep point to {member.mention}! They now have **{target['reputation'] + 1}** rep ⭐"))

    # ═══════════════════════════════════
    #  LEVELING SLASH COMMANDS
    # ═══════════════════════════════════

    @app_commands.command(name="rank", description="View your rank")
    @app_commands.describe(member="Member to check")
    async def slash_rank(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        data = await self.db.get_user(member.id, interaction.guild.id)
        level = data["level"]
        xp = data["xp"]
        needed = xp_for_level(level)
        bar = progress_bar(xp, needed)

        # Calculate rank position
        all_users = await self.db.get_all_users(interaction.guild.id)
        rank_pos = next((i+1 for i, u in enumerate(all_users) if u["user_id"] == member.id), "?")

        embed = discord.Embed(title=f"⭐ {member.display_name}'s Rank", color=config.COLORS["purple"])
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🏅 Rank", value=f"#{rank_pos}", inline=True)
        embed.add_field(name="⭐ Level", value=f"**{level}**", inline=True)
        embed.add_field(name="✨ XP", value=f"**{xp:,}/{needed:,}**", inline=True)
        embed.add_field(name="📊 Progress", value=f"`[{bar}]` {int(xp/needed*100)}%", inline=False)
        embed.add_field(name="💬 Messages", value=f"**{data['messages']:,}**", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View XP leaderboard")
    async def slash_leaderboard(self, interaction: discord.Interaction):
        rows = await self.db.get_leaderboard(interaction.guild.id, "xp")
        medals = ["🥇", "🥈", "🥉"]
        desc = ""
        for i, row in enumerate(rows):
            member = interaction.guild.get_member(row["user_id"])
            name = member.display_name if member else f"User {row['user_id']}"
            medal = medals[i] if i < 3 else f"`{i+1}.`"
            desc += f"{medal} **{name}** — Level {row['level']} | {row['xp']:,} XP\n"
        embed = discord.Embed(title=f"🏆 {interaction.guild.name} Leaderboard", description=desc or "No data!", color=config.COLORS["gold"])
        await interaction.response.send_message(embed=embed)

    # ═══════════════════════════════════
    #  MODERATION SLASH COMMANDS
    # ═══════════════════════════════════

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.describe(member="Member to kick", reason="Reason for kick")
    @app_commands.default_permissions(kick_members=True)
    async def slash_kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(embed=error_embed("Error", "Can't kick this member!"), ephemeral=True)
        await member.kick(reason=reason)
        await self.db.add_mod_log(interaction.guild.id, "Kick", member.id, interaction.user.id, reason)
        embed = success_embed("Member Kicked", f"**{member}** kicked.\n**Reason:** {reason}")
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.describe(member="Member to ban", reason="Reason for ban")
    @app_commands.default_permissions(ban_members=True)
    async def slash_ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message(embed=error_embed("Error", "Can't ban this member!"), ephemeral=True)

        view = ConfirmView(interaction.user.id)
        await interaction.response.send_message(embed=warning_embed("Confirm Ban", f"Ban **{member}** for: {reason}?"), view=view)
        await view.wait()

        if view.value:
            await member.ban(reason=reason)
            await self.db.add_mod_log(interaction.guild.id, "Ban", member.id, interaction.user.id, reason)
            await interaction.edit_original_response(embed=success_embed("Banned!", f"**{member}** has been banned."), view=None)
        else:
            await interaction.edit_original_response(embed=info_embed("Cancelled", "Ban was cancelled."), view=None)

    @app_commands.command(name="tempban", description="Temporarily ban a member")
    @app_commands.describe(member="Member to ban", duration="Duration (e.g. 1d, 2h30m)", reason="Reason")
    @app_commands.default_permissions(ban_members=True)
    async def slash_tempban(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason"):
        try:
            td = parse_duration(duration)
        except ValueError:
            return await interaction.response.send_message(embed=error_embed("Invalid Duration", "Use format: 1d2h30m"), ephemeral=True)

        unban_at = datetime.utcnow() + td
        await member.ban(reason=f"Temp ban: {reason} (until {unban_at})")
        await self.db.add_temp_ban(interaction.guild.id, member.id, interaction.user.id, reason, unban_at.isoformat())
        await self.db.add_mod_log(interaction.guild.id, "Temp Ban", member.id, interaction.user.id, reason, duration)
        embed = success_embed("Temp Banned!", f"**{member}** banned until <t:{int(unban_at.timestamp())}:F>\n**Reason:** {reason}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="mute", description="Mute a member")
    @app_commands.describe(member="Member to mute", duration="Duration in minutes", reason="Reason")
    @app_commands.default_permissions(manage_roles=True)
    async def slash_mute(self, interaction: discord.Interaction, member: discord.Member, duration: int = 10, reason: str = "No reason"):
        from datetime import timedelta
        until = datetime.utcnow() + timedelta(minutes=duration)
        await member.timeout(until, reason=reason)
        await self.db.add_mod_log(interaction.guild.id, "Mute", member.id, interaction.user.id, reason, f"{duration}m")
        embed = success_embed("Muted!", f"**{member}** muted for **{duration}m**.\n**Reason:** {reason}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unmute", description="Unmute a member")
    @app_commands.describe(member="Member to unmute")
    @app_commands.default_permissions(manage_roles=True)
    async def slash_unmute(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        await interaction.response.send_message(embed=success_embed("Unmuted!", f"**{member}** has been unmuted."))

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member to warn", reason="Reason")
    @app_commands.default_permissions(manage_messages=True)
    async def slash_warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        await self.db.get_user(member.id, interaction.guild.id)
        await self.db.add_warning(member.id, interaction.guild.id, reason, interaction.user.id)
        user_data = await self.db.get_user(member.id, interaction.guild.id)
        settings = await self.db.get_guild_settings(interaction.guild.id)
        max_w = settings["max_warnings"]

        embed = discord.Embed(
            title="⚠️ Warning Issued",
            description=f"**{member}** warned.\n**Reason:** {reason}\n**Warnings:** {user_data['warnings']}/{max_w}",
            color=config.COLORS["warning"]
        )
        await interaction.response.send_message(embed=embed)

        if user_data["warnings"] >= max_w:
            await member.ban(reason=f"Auto-ban: {max_w} warnings")
            await interaction.followup.send(embed=error_embed("Auto-Banned", f"**{member}** reached max warnings!"))

    @app_commands.command(name="warnings", description="View member's warnings")
    @app_commands.describe(member="Member to check")
    @app_commands.default_permissions(manage_messages=True)
    async def slash_warnings(self, interaction: discord.Interaction, member: discord.Member):
        warns = await self.db.get_warnings(member.id, interaction.guild.id)
        embed = discord.Embed(title=f"⚠️ Warnings for {member}", color=config.COLORS["warning"])
        embed.set_thumbnail(url=member.display_avatar.url)
        if not warns:
            embed.description = "No warnings!"
        else:
            for i, w in enumerate(warns, 1):
                embed.add_field(name=f"#{i}", value=f"**Reason:** {w['reason']}\n**By:** <@{w['moderator']}>\n**Date:** {w['created_at'][:10]}", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="purge", description="Delete messages")
    @app_commands.describe(amount="Number of messages (1-100)")
    @app_commands.default_permissions(manage_messages=True)
    async def slash_purge(self, interaction: discord.Interaction, amount: int = 10):
        if amount < 1 or amount > 100:
            return await interaction.response.send_message(embed=error_embed("Error", "1-100 only!"), ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(embed=success_embed("Purged!", f"Deleted **{len(deleted)}** messages."), ephemeral=True)

    @app_commands.command(name="lock", description="Lock a channel")
    @app_commands.default_permissions(manage_channels=True)
    async def slash_lock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message(embed=success_embed("Locked!", f"🔒 {interaction.channel.mention} is now locked."))

    @app_commands.command(name="unlock", description="Unlock a channel")
    @app_commands.default_permissions(manage_channels=True)
    async def slash_unlock(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message(embed=success_embed("Unlocked!", f"🔓 {interaction.channel.mention} is now unlocked."))

    @app_commands.command(name="slowmode", description="Set channel slowmode")
    @app_commands.describe(seconds="Slowmode delay in seconds (0 to disable)")
    @app_commands.default_permissions(manage_channels=True)
    async def slash_slowmode(self, interaction: discord.Interaction, seconds: int = 0):
        await interaction.channel.edit(slowmode_delay=seconds)
        msg = "Slowmode disabled." if seconds == 0 else f"Slowmode set to **{seconds}s**."
        await interaction.response.send_message(embed=success_embed("Slowmode", msg))

    @app_commands.command(name="modlogs", description="View moderation logs")
    @app_commands.describe(member="Filter by member")
    @app_commands.default_permissions(manage_messages=True)
    async def slash_modlogs(self, interaction: discord.Interaction, member: discord.Member = None):
        logs = await self.db.get_mod_logs(interaction.guild.id, member.id if member else None)
        if not logs:
            return await interaction.response.send_message(embed=info_embed("No Logs", "No moderation logs found."))

        pages = []
        for i in range(0, len(logs), 5):
            embed = discord.Embed(title="📋 Mod Logs", color=config.COLORS["warning"])
            for log in logs[i:i+5]:
                embed.add_field(
                    name=f"{log['action']} — {log['created_at'][:10]}",
                    value=f"**Target:** <@{log['target_id']}>\n**Mod:** <@{log['moderator_id']}>\n**Reason:** {log['reason']}",
                    inline=False
                )
            embed.set_footer(text=f"Page {i//5 + 1}/{(len(logs)-1)//5 + 1}")
            pages.append(embed)

        if len(pages) == 1:
            await interaction.response.send_message(embed=pages[0])
        else:
            view = PaginatorView(pages, interaction.user.id)
            await interaction.response.send_message(embed=pages[0], view=view)

    # ═══════════════════════════════════
    #  FUN SLASH COMMANDS
    # ═══════════════════════════════════

    @app_commands.command(name="8ball", description="Ask the magic 8-ball")
    @app_commands.describe(question="Your question")
    async def slash_8ball(self, interaction: discord.Interaction, question: str):
        responses = [
            "✅ Definitely yes!", "✅ Without a doubt.", "✅ Most likely.",
            "✅ Yes!", "🤔 Ask again later.", "🤔 Cannot predict now.",
            "❌ Don't count on it.", "❌ My reply is no.", "❌ Very doubtful."
        ]
        embed = discord.Embed(title="🎱 Magic 8-Ball", color=config.COLORS["purple"])
        embed.add_field(name="❓ Question", value=question, inline=False)
        embed.add_field(name="🎱 Answer", value=random.choice(responses), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def slash_coinflip(self, interaction: discord.Interaction):
        result = random.choice(["🪙 Heads!", "🪙 Tails!"])
        embed = discord.Embed(title="Coin Flip", description=result, color=config.COLORS["gold"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roll", description="Roll a dice")
    @app_commands.describe(sides="Number of sides")
    async def slash_roll(self, interaction: discord.Interaction, sides: int = 6):
        result = random.randint(1, max(2, sides))
        embed = discord.Embed(title=f"🎲 D{sides}", description=f"You rolled **{result}**!", color=config.COLORS["info"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rps", description="Rock Paper Scissors")
    @app_commands.describe(choice="rock, paper, or scissors")
    @app_commands.choices(choice=[
        app_commands.Choice(name="🪨 Rock", value="rock"),
        app_commands.Choice(name="📄 Paper", value="paper"),
        app_commands.Choice(name="✂️ Scissors", value="scissors"),
    ])
    async def slash_rps(self, interaction: discord.Interaction, choice: app_commands.Choice[str]):
        choices = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
        bot_choice = random.choice(list(choices.keys()))
        wins = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        user_choice = choice.value

        if user_choice == bot_choice:
            result, color = "🤝 Tie!", config.COLORS["warning"]
        elif wins[user_choice] == bot_choice:
            result, color = "🎉 You win!", config.COLORS["success"]
        else:
            result, color = "😔 You lose!", config.COLORS["error"]

        embed = discord.Embed(title="✂️ Rock Paper Scissors", color=color)
        embed.add_field(name="You", value=f"{choices[user_choice]} {user_choice.title()}", inline=True)
        embed.add_field(name="Bot", value=f"{choices[bot_choice]} {bot_choice.title()}", inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="meme", description="Get a random meme")
    async def slash_meme(self, interaction: discord.Interaction):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(title=data["title"], url=data["postLink"], color=config.COLORS["info"])
                    embed.set_image(url=data["url"])
                    embed.set_footer(text=f"👍 {data['ups']} | r/{data['subreddit']}")
                    await interaction.response.send_message(embed=embed)

    @app_commands.command(name="joke", description="Get a random joke")
    async def slash_joke(self, interaction: discord.Interaction):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("https://official-joke-api.appspot.com/random_joke") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(title="😂 Joke", color=config.COLORS["info"])
                    embed.add_field(name="Setup", value=data["setup"], inline=False)
                    embed.add_field(name="Punchline", value=f"||{data['punchline']}||", inline=False)
                    await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roast", description="Roast a member")
    @app_commands.describe(member="Who to roast")
    async def slash_roast(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        roasts = [
            "You're like a cloud. When you disappear, it's a beautiful day.",
            "I'd roast you, but my mom said I'm not allowed to burn trash.",
            "You bring everyone so much joy... when you leave.",
            "I'd explain it to you, but I don't have crayons with me.",
            "You're not stupid, you just have bad luck thinking.",
            "If I wanted to hear from someone like you, I'd go to the zoo.",
            "You're proof that evolution CAN go in reverse.",
            "Your brain is like a browser — 15 tabs open, 3 frozen, and you have no idea where the music is coming from.",
        ]
        embed = discord.Embed(title=f"🔥 Roasting {member.display_name}", description=random.choice(roasts), color=config.COLORS["error"])
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="wyr", description="Would You Rather")
    async def slash_wyr(self, interaction: discord.Interaction):
        questions = [
            ("Be invisible", "Be able to fly"),
            ("Have infinite money", "Have infinite time"),
            ("Be a genius", "Be the strongest alive"),
            ("Travel to the past", "Travel to the future"),
            ("Never sleep", "Never eat"),
            ("Know everything", "Be loved by everyone"),
            ("Live in space", "Live underwater"),
            ("Be famous", "Be the richest person nobody knows"),
        ]
        a, b = random.choice(questions)
        embed = discord.Embed(title="🤔 Would You Rather...", description=f"**🅰️ {a}**\n\nor\n\n**🅱️ {b}**", color=config.COLORS["purple"])
        msg = await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("🅰️")
        await msg.add_reaction("🅱️")

    @app_commands.command(name="slots", description="Play the slot machine")
    @app_commands.describe(bet="Amount to bet")
    async def slash_slots(self, interaction: discord.Interaction, bet: int = 50):
        data = await self.db.get_user(interaction.user.id, interaction.guild.id)
        if bet <= 0 or bet > data["coins"]:
            return await interaction.response.send_message(embed=error_embed("Error", "Invalid bet!"), ephemeral=True)

        symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
        weights = [30, 25, 20, 15, 7, 3]
        reels = random.choices(symbols, weights=weights, k=3)

        if reels[0] == reels[1] == reels[2]:
            multipliers = {"🍒": 3, "🍋": 4, "🍊": 5, "🍇": 8, "💎": 15, "7️⃣": 50}
            mult = multipliers.get(reels[0], 3)
            winnings = bet * mult
            result = f"🎉 JACKPOT! x{mult}! You won **{winnings:,}** coins!"
            color = config.COLORS["gold"]
            await self.db.update_user(interaction.user.id, interaction.guild.id, coins=data["coins"] + winnings)
        elif reels[0] == reels[1] or reels[1] == reels[2]:
            winnings = bet
            result = f"✨ Two match! You won **{winnings:,}** coins!"
            color = config.COLORS["success"]
            await self.db.update_user(interaction.user.id, interaction.guild.id, coins=data["coins"] + winnings)
        else:
            result = f"😔 No match. Lost **{bet:,}** coins."
            color = config.COLORS["error"]
            await self.db.update_user(interaction.user.id, interaction.guild.id, coins=data["coins"] - bet)

        embed = discord.Embed(title="🎰 Slot Machine", color=color)
        embed.add_field(name="Result", value=f"[ {reels[0]} | {reels[1]} | {reels[2]} ]", inline=False)
        embed.add_field(name="Outcome", value=result, inline=False)
        await interaction.response.send_message(embed=embed)

    # ═══════════════════════════════════
    #  GIVEAWAY SLASH COMMANDS
    # ═══════════════════════════════════

    giveaway_group = app_commands.Group(name="giveaway", description="Giveaway commands")

    @giveaway_group.command(name="start", description="Start a giveaway")
    @app_commands.describe(prize="What's the prize", duration="Duration (e.g. 1h, 1d)", winners="Number of winners", channel="Channel for giveaway")
    @app_commands.default_permissions(manage_guild=True)
    async def giveaway_start(self, interaction: discord.Interaction, prize: str, duration: str, winners: int = 1, channel: discord.TextChannel = None):
        channel = channel or interaction.channel
        try:
            td = parse_duration(duration)
        except ValueError:
            return await interaction.response.send_message(embed=error_embed("Invalid Duration", "Use format: 1d2h30m"), ephemeral=True)

        end_time = datetime.utcnow() + td

        embed = discord.Embed(
            title="🎉 GIVEAWAY! 🎉",
            description=(
                f"**Prize:** {prize}\n"
                f"**Winners:** {winners}\n"
                f"**Hosted by:** {interaction.user.mention}\n"
                f"**Ends:** <t:{int(end_time.timestamp())}:R>\n\n"
                f"Click the button below to enter!"
            ),
            color=config.COLORS["pink"],
            timestamp=end_time
        )
        embed.set_footer(text="Ends at")

        await interaction.response.send_message("✅ Giveaway created!", ephemeral=True)
        msg = await channel.send(embed=embed)

        giveaway_id = await self.db.create_giveaway(
            interaction.guild.id, channel.id, msg.id,
            interaction.user.id, prize, winners, end_time.isoformat()
        )
        view = GiveawayView(self.bot, giveaway_id)
        await msg.edit(view=view)

    @giveaway_group.command(name="end", description="End a giveaway early")
    @app_commands.describe(message_id="Message ID of the giveaway")
    @app_commands.default_permissions(manage_guild=True)
    async def giveaway_end(self, interaction: discord.Interaction, message_id: str):
        giveaways = await self.db.get_active_giveaways()
        giveaway = next((g for g in giveaways if g["message_id"] == int(message_id)), None)
        if not giveaway:
            return await interaction.response.send_message(embed=error_embed("Not Found", "Giveaway not found!"), ephemeral=True)

        from cogs.events import Events
        events_cog = self.bot.get_cog("Events")
        if events_cog:
            await events_cog._end_giveaway(giveaway)
        await interaction.response.send_message(embed=success_embed("Giveaway Ended!", "Winners have been selected."), ephemeral=True)

    @giveaway_group.command(name="reroll", description="Reroll giveaway winners")
    @app_commands.describe(message_id="Message ID of the giveaway")
    @app_commands.default_permissions(manage_guild=True)
    async def giveaway_reroll(self, interaction: discord.Interaction, message_id: str):
        async with aiosqlite.connect(config.DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM giveaways WHERE message_id = ?", (int(message_id),)) as cursor:
                giveaway = await cursor.fetchone()

        if not giveaway:
            return await interaction.response.send_message(embed=error_embed("Not Found", "Giveaway not found!"), ephemeral=True)

        import aiosqlite
        entries = await self.db.get_giveaway_entries(giveaway["id"])
        if not entries:
            return await interaction.response.send_message(embed=error_embed("Error", "No entries!"), ephemeral=True)

        winner_id = random.choice(entries)
        await interaction.response.send_message(f"🎉 New winner: <@{winner_id}>! Congratulations!")

    # ═══════════════════════════════════
    #  TICKET SLASH COMMANDS
    # ═══════════════════════════════════

    ticket_group = app_commands.Group(name="ticket", description="Ticket commands")

    @ticket_group.command(name="setup", description="Setup the ticket system")
    @app_commands.describe(category="Category for tickets", log_channel="Log channel for tickets")
    @app_commands.default_permissions(administrator=True)
    async def ticket_setup(self, interaction: discord.Interaction, category: discord.CategoryChannel = None, log_channel: discord.TextChannel = None):
        await self.db.update_guild_settings(
            interaction.guild.id,
            ticket_category=category.id if category else None,
            ticket_log=log_channel.id if log_channel else None
        )

        embed = discord.Embed(
            title="🎫 Support Tickets",
            description="Click the button below to create a support ticket!",
            color=config.COLORS["blurple"]
        )
        view = TicketView(self.bot)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message(embed=success_embed("Ticket System Setup!", "Panel created."), ephemeral=True)

    @ticket_group.command(name="close", description="Close the current ticket")
    async def ticket_close(self, interaction: discord.Interaction):
        ticket = await self.db.get_ticket(interaction.channel.id)
        if not ticket:
            return await interaction.response.send_message(embed=error_embed("Error", "Not a ticket channel!"), ephemeral=True)

        await self.db.close_ticket(interaction.channel.id)
        await interaction.response.send_message(embed=success_embed("Ticket Closing", "Channel deleted in 5 seconds..."))

        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @ticket_group.command(name="add", description="Add a member to ticket")
    @app_commands.describe(member="Member to add")
    async def ticket_add(self, interaction: discord.Interaction, member: discord.Member):
        ticket = await self.db.get_ticket(interaction.channel.id)
        if not ticket:
            return await interaction.response.send_message(embed=error_embed("Error", "Not a ticket!"), ephemeral=True)

        await interaction.channel.set_permissions(member, view_channel=True, send_messages=True)
        await interaction.response.send_message(embed=success_embed("Member Added", f"{member.mention} added to ticket."))

    # ═══════════════════════════════════
    #  SUGGESTION SLASH COMMANDS
    # ═══════════════════════════════════

    @app_commands.command(name="suggest", description="Make a suggestion")
    @app_commands.describe(suggestion="Your suggestion")
    async def slash_suggest(self, interaction: discord.Interaction, suggestion: str):
        settings = await self.db.get_guild_settings(interaction.guild.id)
        channel = self.bot.get_channel(settings["suggestion_channel"]) if settings["suggestion_channel"] else interaction.channel

        embed = discord.Embed(
            title="💡 New Suggestion",
            description=suggestion,
            color=config.COLORS["info"],
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="Status: ⏳ Pending")

        msg = await channel.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

        suggestion_id = await self.db.create_suggestion(interaction.guild.id, interaction.user.id, msg.id, suggestion)
        embed.set_footer(text=f"ID: {suggestion_id} | Status: ⏳ Pending")
        await msg.edit(embed=embed)
        await interaction.response.send_message(embed=success_embed("Suggestion Submitted!", f"ID: #{suggestion_id}"), ephemeral=True)

    suggestion_group = app_commands.Group(name="suggestion", description="Manage suggestions")

    @suggestion_group.command(name="approve", description="Approve a suggestion")
    @app_commands.describe(suggestion_id="Suggestion ID", response="Your response")
    @app_commands.default_permissions(manage_guild=True)
    async def suggestion_approve(self, interaction: discord.Interaction, suggestion_id: int, response: str = ""):
        sug = await self.db.get_suggestion(suggestion_id)
        if not sug:
            return await interaction.response.send_message(embed=error_embed("Not Found"), ephemeral=True)

        await self.db.update_suggestion(suggestion_id, status="approved", response=response)
        settings = await self.db.get_guild_settings(interaction.guild.id)
        channel = self.bot.get_channel(settings["suggestion_channel"]) if settings["suggestion_channel"] else interaction.channel

        try:
            msg = await channel.fetch_message(sug["message_id"])
            embed = msg.embeds[0]
            embed.color = config.COLORS["success"]
            embed.set_footer(text=f"ID: {suggestion_id} | Status: ✅ Approved")
            if response:
                embed.add_field(name="📝 Response", value=response, inline=False)
            await msg.edit(embed=embed)
        except Exception:
            pass

        await interaction.response.send_message(embed=success_embed("Suggestion Approved!"), ephemeral=True)

    @suggestion_group.command(name="deny", description="Deny a suggestion")
    @app_commands.describe(suggestion_id="Suggestion ID", response="Reason for denial")
    @app_commands.default_permissions(manage_guild=True)
    async def suggestion_deny(self, interaction: discord.Interaction, suggestion_id: int, response: str = ""):
        sug = await self.db.get_suggestion(suggestion_id)
        if not sug:
            return await interaction.response.send_message(embed=error_embed("Not Found"), ephemeral=True)

        await self.db.update_suggestion(suggestion_id, status="denied", response=response)
        settings = await self.db.get_guild_settings(interaction.guild.id)
        channel = self.bot.get_channel(settings["suggestion_channel"]) if settings["suggestion_channel"] else interaction.channel

        try:
            msg = await channel.fetch_message(sug["message_id"])
            embed = msg.embeds[0]
            embed.color = config.COLORS["error"]
            embed.set_footer(text=f"ID: {suggestion_id} | Status: ❌ Denied")
            if response:
                embed.add_field(name="📝 Response", value=response, inline=False)
            await msg.edit(embed=embed)
        except Exception:
            pass

        await interaction.response.send_message(embed=success_embed("Suggestion Denied!"), ephemeral=True)

    # ═══════════════════════════════════
    #  TAG SLASH COMMANDS
    # ═══════════════════════════════════

    tag_group = app_commands.Group(name="tag", description="Tag commands")

    @tag_group.command(name="create", description="Create a tag")
    @app_commands.describe(name="Tag name", content="Tag content")
    async def tag_create(self, interaction: discord.Interaction, name: str, content: str):
        existing = await self.db.get_tag(interaction.guild.id, name)
        if existing:
            return await interaction.response.send_message(embed=error_embed("Exists", "Tag already exists!"), ephemeral=True)
        await self.db.create_tag(interaction.guild.id, name, content, interaction.user.id)
        await interaction.response.send_message(embed=success_embed("Tag Created!", f"Tag `{name}` created."))

    @tag_group.command(name="get", description="Get a tag")
    @app_commands.describe(name="Tag name")
    async def tag_get(self, interaction: discord.Interaction, name: str):
        tag = await self.db.get_tag(interaction.guild.id, name)
        if not tag:
            return await interaction.response.send_message(embed=error_embed("Not Found", "Tag doesn't exist!"), ephemeral=True)
        embed = discord.Embed(title=f"🏷️ {tag['name']}", description=tag["content"], color=config.COLORS["info"])
        embed.set_footer(text=f"Uses: {tag['uses']} | Created by ID: {tag['author_id']}")
        await interaction.response.send_message(embed=embed)

    @tag_group.command(name="list", description="List all tags")
    async def tag_list(self, interaction: discord.Interaction):
        tags = await self.db.get_all_tags(interaction.guild.id)
        if not tags:
            return await interaction.response.send_message(embed=info_embed("No Tags", "No tags created yet!"))
        desc = "\n".join(f"`{t['name']}` — {t['uses']} uses" for t in tags)
        embed = discord.Embed(title="🏷️ Server Tags", description=desc, color=config.COLORS["info"])
        await interaction.response.send_message(embed=embed)

    @tag_group.command(name="delete", description="Delete a tag")
    @app_commands.describe(name="Tag name")
    async def tag_delete(self, interaction: discord.Interaction, name: str):
        tag = await self.db.get_tag(interaction.guild.id, name)
        if not tag:
            return await interaction.response.send_message(embed=error_embed("Not Found"), ephemeral=True)
        if tag["author_id"] != interaction.user.id and not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(embed=error_embed("Error", "Not your tag!"), ephemeral=True)
        await self.db.delete_tag(interaction.guild.id, name)
        await interaction.response.send_message(embed=success_embed("Tag Deleted!", f"Deleted `{name}`."))

    # ═══════════════════════════════════
    #  ADMIN SLASH COMMANDS
    # ═══════════════════════════════════

    setup_group = app_commands.Group(name="setup", description="Server setup commands")

    @setup_group.command(name="welcome", description="Set welcome channel & message")
    @app_commands.describe(channel="Welcome channel", message="Welcome message ({user}, {server}, {count})")
    @app_commands.default_permissions(administrator=True)
    async def setup_welcome(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = "Welcome {user} to {server}!"):
        await self.db.update_guild_settings(interaction.guild.id, welcome_channel=channel.id, welcome_message=message)
        await interaction.response.send_message(embed=success_embed("Welcome Setup!", f"Channel: {channel.mention}\nMessage: {message}"))

    @setup_group.command(name="logs", description="Set mod log channel")
    @app_commands.describe(channel="Log channel")
    @app_commands.default_permissions(administrator=True)
    async def setup_logs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self.db.update_guild_settings(interaction.guild.id, log_channel=channel.id)
        await interaction.response.send_message(embed=success_embed("Log Channel Set!", f"Logs → {channel.mention}"))

    @setup_group.command(name="autorole", description="Set auto role for new members")
    @app_commands.describe(role="Role to give new members")
    @app_commands.default_permissions(administrator=True)
    async def setup_autorole(self, interaction: discord.Interaction, role: discord.Role):
        await self.db.update_guild_settings(interaction.guild.id, auto_role=role.id)
        await interaction.response.send_message(embed=success_embed("Auto Role Set!", f"New members get {role.mention}"))

    @setup_group.command(name="starboard", description="Setup starboard channel")
    @app_commands.describe(channel="Starboard channel", threshold="Stars needed")
    @app_commands.default_permissions(administrator=True)
    async def setup_starboard(self, interaction: discord.Interaction, channel: discord.TextChannel, threshold: int = 3):
        await self.db.update_guild_settings(interaction.guild.id, starboard_channel=channel.id, starboard_threshold=threshold)
        await interaction.response.send_message(embed=success_embed("Starboard Setup!", f"Channel: {channel.mention}\nThreshold: {threshold} ⭐"))

    @setup_group.command(name="suggestions", description="Setup suggestions channel")
    @app_commands.describe(channel="Suggestions channel")
    @app_commands.default_permissions(administrator=True)
    async def setup_suggestions(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self.db.update_guild_settings(interaction.guild.id, suggestion_channel=channel.id)
        await interaction.response.send_message(embed=success_embed("Suggestions Setup!", f"Channel: {channel.mention}"))

    @setup_group.command(name="levelup", description="Set level up notification channel")
    @app_commands.describe(channel="Level up channel (leave empty for same channel)")
    @app_commands.default_permissions(administrator=True)
    async def setup_levelup(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        await self.db.update_guild_settings(interaction.guild.id, level_up_channel=channel.id if channel else None)
        msg = f"Level ups → {channel.mention}" if channel else "Level ups in same channel"
        await interaction.response.send_message(embed=success_embed("Level Up Channel!", msg))

    @setup_group.command(name="automod", description="Toggle auto-moderation")
    @app_commands.describe(enabled="Enable or disable", antilink="Block links", antispam="Block spam")
    @app_commands.default_permissions(administrator=True)
    async def setup_automod(self, interaction: discord.Interaction, enabled: bool = True, antilink: bool = False, antispam: bool = False):
        await self.db.update_guild_settings(
            interaction.guild.id,
            automod_enabled=int(enabled),
            antilink=int(antilink),
            antispam=int(antispam)
        )
        embed = success_embed("AutoMod Updated!", f"AutoMod: {'✅' if enabled else '❌'}\nAnti-Link: {'✅' if antilink else '❌'}\nAnti-Spam: {'✅' if antispam else '❌'}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addcoins", description="Add coins to a member")
    @app_commands.describe(member="Who", amount="How much")
    @app_commands.default_permissions(administrator=True)
    async def slash_addcoins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        data = await self.db.get_user(member.id, interaction.guild.id)
        await self.db.update_user(member.id, interaction.guild.id, coins=data["coins"] + amount)
        await interaction.response.send_message(embed=success_embed("Coins Added!", f"Added **{amount:,}** to {member.mention}"))

    @app_commands.command(name="setxp", description="Set XP for a member")
    @app_commands.describe(member="Who", amount="XP amount")
    @app_commands.default_permissions(administrator=True)
    async def slash_setxp(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        from utils.helpers import get_level_from_xp
        new_level = get_level_from_xp(amount)
        await self.db.update_user(member.id, interaction.guild.id, xp=amount, level=new_level)
        await interaction.response.send_message(embed=success_embed("XP Set!", f"Set {member.mention} to **{amount:,}** XP (Level {new_level})"))

    @app_commands.command(name="announce", description="Make an announcement")
    @app_commands.describe(channel="Channel", title="Title", message="Message", ping="Role to ping")
    @app_commands.default_permissions(administrator=True)
    async def slash_announce(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str, title: str = "📢 Announcement", ping: discord.Role = None):
        embed = discord.Embed(title=title, description=message, color=config.COLORS["blurple"], timestamp=datetime.utcnow())
        embed.set_footer(text=f"By {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        content = ping.mention if ping else None
        await channel.send(content=content, embed=embed)
        await interaction.response.send_message(embed=success_embed("Announced!", f"Sent to {channel.mention}"), ephemeral=True)

    @app_commands.command(name="levelrole", description="Add a level role reward")
    @app_commands.describe(level="Level to grant role at", role="Role to grant")
    @app_commands.default_permissions(administrator=True)
    async def slash_levelrole(self, interaction: discord.Interaction, level: int, role: discord.Role):
        await self.db.add_level_role(interaction.guild.id, level, role.id)
        await interaction.response.send_message(embed=success_embed("Level Role Added!", f"Level {level} → {role.mention}"))

    @app_commands.command(name="reactionrole", description="Create a reaction role")
    @app_commands.describe(message_id="Message ID", emoji="Emoji", role="Role")
    @app_commands.default_permissions(administrator=True)
    async def slash_reactionrole(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role):
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
            await msg.add_reaction(emoji)
        except Exception:
            return await interaction.response.send_message(embed=error_embed("Error", "Message not found!"), ephemeral=True)

        await self.db.add_reaction_role(interaction.guild.id, interaction.channel.id, int(message_id), emoji, role.id)
        await interaction.response.send_message(embed=success_embed("Reaction Role Added!", f"{emoji} → {role.mention}"), ephemeral=True)

    @app_commands.command(name="poll", description="Create an advanced poll")
    @app_commands.describe(question="Poll question", option1="Option 1", option2="Option 2", option3="Option 3", option4="Option 4", option5="Option 5")
    async def slash_poll(self, interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str = None, option4: str = None, option5: str = None):
        options = [o for o in [option1, option2, option3, option4, option5] if o]
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        desc = "\n".join(f"{emojis[i]} {opt}" for i, opt in enumerate(options))

        embed = discord.Embed(title=f"📊 {question}", description=desc, color=config.COLORS["info"], timestamp=datetime.utcnow())
        embed.set_footer(text=f"Poll by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        for i in range(len(options)):
            await msg.add_reaction(emojis[i])

    @app_commands.command(name="stats", description="View server stats")
    async def slash_stats(self, interaction: discord.Interaction):
        stats = await self.db.get_guild_stats(interaction.guild.id)
        embed = discord.Embed(title=f"📊 {interaction.guild.name} Stats", color=config.COLORS["blurple"])
        embed.add_field(name="👥 Tracked Users", value=f"{stats['total_users']:,}", inline=True)
        embed.add_field(name="💬 Total Messages", value=f"{stats['total_messages']:,}", inline=True)
        embed.add_field(name="💰 Total Economy", value=f"{stats['total_economy']:,} coins", inline=True)
        embed.add_field(name="⚠️ Total Warnings", value=f"{stats['total_warnings']:,}", inline=True)
        embed.add_field(name="🎫 Total Tickets", value=f"{stats['total_tickets']:,}", inline=True)
        embed.add_field(name="🎉 Total Giveaways", value=f"{stats['total_giveaways']:,}", inline=True)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))