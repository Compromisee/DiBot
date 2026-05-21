import discord
from discord.ext import commands
from discord import app_commands, ui
import random
import aiohttp
import config

class TicTacToeButton(ui.Button):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view
        if interaction.user != view.current_player:
            return await interaction.response.send_message("Not your turn!", ephemeral=True)

        self.disabled = True
        if view.current_player == view.player1:
            self.style = discord.ButtonStyle.danger
            self.label = "X"
            view.board[self.y][self.x] = "X"
            view.current_player = view.player2
        else:
            self.style = discord.ButtonStyle.success
            self.label = "O"
            view.board[self.y][self.x] = "O"
            view.current_player = view.player1

        winner = view.check_winner()
        if winner:
            for child in view.children:
                child.disabled = True
            content = f"🎉 **{winner}** wins!" if winner != "Tie" else "🤝 It's a tie!"
            await interaction.response.edit_message(content=content, view=view)
            view.stop()
        else:
            await interaction.response.edit_message(content=f"**{view.current_player.display_name}**'s turn", view=view)


class TicTacToeView(ui.View):
    def __init__(self, player1: discord.Member, player2: discord.Member):
        super().__init__(timeout=120)
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.board = [[None]*3 for _ in range(3)]
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_winner(self):
        b = self.board
        for row in b:
            if row[0] == row[1] == row[2] and row[0]:
                return self.player1.display_name if row[0] == "X" else self.player2.display_name

        for col in range(3):
            if b[0][col] == b[1][col] == b[2][col] and b[0][col]:
                return self.player1.display_name if b[0][col] == "X" else self.player2.display_name

        if b[0][0] == b[1][1] == b[2][2] and b[0][0]:
            return self.player1.display_name if b[0][0] == "X" else self.player2.display_name
        if b[0][2] == b[1][1] == b[2][0] and b[0][2]:
            return self.player1.display_name if b[0][2] == "X" else self.player2.display_name

        if all(b[y][x] for y in range(3) for x in range(3)):
            return "Tie"
        return None


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="tictactoe", description="Play Tic-Tac-Toe")
    @app_commands.describe(opponent="Who to play against")
    async def slash_tictactoe(self, interaction: discord.Interaction, opponent: discord.Member):
        if opponent == interaction.user:
            return await interaction.response.send_message("Can't play yourself!", ephemeral=True)
        if opponent.bot:
            return await interaction.response.send_message("Can't play against bots!", ephemeral=True)

        view = TicTacToeView(interaction.user, opponent)
        await interaction.response.send_message(
            f"🎮 **Tic-Tac-Toe**\n{interaction.user.mention} (X) vs {opponent.mention} (O)\n\n**{interaction.user.display_name}**'s turn",
            view=view
        )

    @app_commands.command(name="trivia", description="Answer a trivia question")
    async def slash_trivia(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://opentdb.com/api.php?amount=1&type=multiple") as resp:
                if resp.status != 200:
                    return await interaction.response.send_message("❌ Could not fetch trivia!", ephemeral=True)
                data = await resp.json()

        q = data["results"][0]
        import html
        question = html.unescape(q["question"])
        correct = html.unescape(q["correct_answer"])
        answers = [html.unescape(a) for a in q["incorrect_answers"]] + [correct]
        random.shuffle(answers)

        embed = discord.Embed(
            title=f"❓ Trivia — {q['category']}",
            description=f"**{question}**\n\nDifficulty: {q['difficulty'].title()}",
            color=config.COLORS["purple"]
        )

        class TriviaView(ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                for i, ans in enumerate(answers):
                    btn = ui.Button(label=ans[:80], style=discord.ButtonStyle.secondary, custom_id=f"trivia_{i}")
                    btn.callback = self.make_callback(ans)
                    self.add_item(btn)
                self.answered = False

            def make_callback(self, answer):
                async def callback(inter: discord.Interaction):
                    if inter.user != interaction.user:
                        return await inter.response.send_message("Not your trivia!", ephemeral=True)
                    if self.answered:
                        return
                    self.answered = True
                    for child in self.children:
                        child.disabled = True

                    if answer == correct:
                        coins = {"easy": 30, "medium": 60, "hard": 100}.get(q["difficulty"], 50)
                        user_data = await inter.client.db.get_user(inter.user.id, inter.guild.id)
                        await inter.client.db.update_user(inter.user.id, inter.guild.id, coins=user_data["coins"] + coins)
                        result = f"✅ Correct! +**{coins}** coins!"
                        color = config.COLORS["success"]
                    else:
                        result = f"❌ Wrong! Answer: **{correct}**"
                        color = config.COLORS["error"]

                    embed.color = color
                    embed.add_field(name="Result", value=result, inline=False)
                    await inter.response.edit_message(embed=embed, view=self)
                    self.stop()
                return callback

        await interaction.response.send_message(embed=embed, view=TriviaView())

    @app_commands.command(name="guess", description="Guess the number game")
    async def slash_guess(self, interaction: discord.Interaction):
        number = random.randint(1, 100)
        embed = discord.Embed(
            title="🔢 Guess the Number!",
            description="I picked a number between **1-100**.\nYou have **6 tries**! Type your guess.",
            color=config.COLORS["info"]
        )
        await interaction.response.send_message(embed=embed)

        attempts = 0
        max_attempts = 6

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel and m.content.isdigit()

        while attempts < max_attempts:
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30)
            except Exception:
                return await interaction.followup.send(f"⏰ Time's up! The number was **{number}**.")

            guess = int(msg.content)
            attempts += 1

            if guess == number:
                coins = (max_attempts - attempts + 1) * 20
                data = await self.db.get_user(interaction.user.id, interaction.guild.id)
                await self.db.update_user(interaction.user.id, interaction.guild.id, coins=data["coins"] + coins)
                return await interaction.followup.send(f"🎉 Correct! It was **{number}**! (+**{coins}** coins in {attempts} tries)")
            elif guess < number:
                await msg.reply(f"⬆️ Higher! ({max_attempts - attempts} tries left)", delete_after=5)
            else:
                await msg.reply(f"⬇️ Lower! ({max_attempts - attempts} tries left)", delete_after=5)

        await interaction.followup.send(f"😔 Game over! The number was **{number}**.")

async def setup(bot):
    await bot.add_cog(Games(bot))