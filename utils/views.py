import discord
from discord import ui
import config

# ─────────────────────────────────────────
#  Button Views for Interactive Commands
# ─────────────────────────────────────────

class ConfirmView(ui.View):
    def __init__(self, author_id: int, timeout: int = 30):
        super().__init__(timeout=timeout)
        self.value = None
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This isn't for you!", ephemeral=True)
            return False
        return True

    @ui.button(label="Confirm", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        self.value = True
        self.stop()
        await interaction.response.defer()

    @ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        self.value = False
        self.stop()
        await interaction.response.defer()


class GiveawayView(ui.View):
    def __init__(self, bot, giveaway_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.giveaway_id = giveaway_id

    @ui.button(label="🎉 Enter Giveaway", style=discord.ButtonStyle.blurple, custom_id="giveaway_enter")
    async def enter(self, interaction: discord.Interaction, button: ui.Button):
        success = await self.bot.db.enter_giveaway(self.giveaway_id, interaction.user.id)
        if success:
            entries = await self.bot.db.get_giveaway_entries(self.giveaway_id)
            button.label = f"🎉 Enter Giveaway ({len(entries)} entries)"
            await interaction.message.edit(view=self)
            await interaction.response.send_message("✅ You entered the giveaway!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ You already entered!", ephemeral=True)


class TicketView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.blurple, custom_id="ticket_create")
    async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
        # Check existing tickets
        existing = await self.bot.db.get_user_tickets(interaction.user.id, interaction.guild.id)
        if len(existing) >= 3:
            return await interaction.response.send_message("❌ Max 3 open tickets!", ephemeral=True)

        # Get settings
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        category = interaction.guild.get_channel(settings["ticket_category"]) if settings["ticket_category"] else None

        # Create channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }

        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        ticket_id = await self.bot.db.create_ticket(interaction.guild.id, channel.id, interaction.user.id)

        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket_id}",
            description=(
                f"Welcome {interaction.user.mention}!\n\n"
                "Describe your issue and a staff member will assist you.\n"
                "Click the button below to close this ticket."
            ),
            color=config.COLORS["info"]
        )
        await channel.send(embed=embed, view=TicketControlView(self.bot))
        await interaction.response.send_message(f"✅ Ticket created: {channel.mention}", ephemeral=True)


class TicketControlView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger, custom_id="ticket_close")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        ticket = await self.bot.db.get_ticket(interaction.channel.id)
        if not ticket:
            return await interaction.response.send_message("❌ Not a ticket channel!", ephemeral=True)

        await self.bot.db.close_ticket(interaction.channel.id)

        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"Closed by {interaction.user.mention}\nThis channel will be deleted in 5 seconds.",
            color=config.COLORS["error"]
        )
        await interaction.response.send_message(embed=embed)

        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @ui.button(label="👤 Claim", style=discord.ButtonStyle.success, custom_id="ticket_claim")
    async def claim_ticket(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("❌ Staff only!", ephemeral=True)

        embed = discord.Embed(
            title="👤 Ticket Claimed",
            description=f"This ticket is now being handled by {interaction.user.mention}",
            color=config.COLORS["success"]
        )
        await interaction.response.send_message(embed=embed)


class RoleSelectView(ui.View):
    def __init__(self, roles: list[discord.Role]):
        super().__init__(timeout=None)
        options = [
            discord.SelectOption(label=role.name, value=str(role.id), emoji="🎭")
            for role in roles[:25]
        ]
        self.add_item(RoleSelect(options))


class RoleSelect(ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Select a role...", options=options, custom_id="role_select")

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values[0])
        role = interaction.guild.get_role(role_id)
        if not role:
            return await interaction.response.send_message("❌ Role not found!", ephemeral=True)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"✅ Removed **{role.name}**", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Added **{role.name}**", ephemeral=True)


class PaginatorView(ui.View):
    def __init__(self, pages: list[discord.Embed], author_id: int):
        super().__init__(timeout=120)
        self.pages = pages
        self.current = 0
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.author_id

    @ui.button(label="◀◀", style=discord.ButtonStyle.secondary)
    async def first(self, interaction: discord.Interaction, button: ui.Button):
        self.current = 0
        await interaction.response.edit_message(embed=self.pages[self.current])

    @ui.button(label="◀", style=discord.ButtonStyle.primary)
    async def prev(self, interaction: discord.Interaction, button: ui.Button):
        self.current = max(0, self.current - 1)
        await interaction.response.edit_message(embed=self.pages[self.current])

    @ui.button(label="▶", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: ui.Button):
        self.current = min(len(self.pages) - 1, self.current + 1)
        await interaction.response.edit_message(embed=self.pages[self.current])

    @ui.button(label="▶▶", style=discord.ButtonStyle.secondary)
    async def last(self, interaction: discord.Interaction, button: ui.Button):
        self.current = len(self.pages) - 1
        await interaction.response.edit_message(embed=self.pages[self.current])

    @ui.button(label="✖", style=discord.ButtonStyle.danger)
    async def stop_pages(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.message.delete()
        self.stop()