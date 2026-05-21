import discord
from discord.ext import commands
from database.db import Database
from utils.embeds import success_embed, error_embed, info_embed
from utils.views import TicketView
import config

# ─────────────────────────────────────────
#  Tickets Cog
# ─────────────────────────────────────────

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    # ── Setup Panel ──────────────────────
    @commands.command(name="ticketsetup", aliases=["setuptickets"], help="Setup the ticket panel")
    @commands.has_permissions(administrator=True)
    async def ticketsetup(self, ctx, category: discord.CategoryChannel = None, log: discord.TextChannel = None):
        await self.db.update_guild_settings(
            ctx.guild.id,
            ticket_category = category.id if category else None,
            ticket_log      = log.id if log else None
        )

        embed = discord.Embed(
            title       = "🎫 Support Tickets",
            description = (
                "Need help? Click the button below to open a support ticket.\n"
                "A staff member will assist you as soon as possible!"
            ),
            color = config.COLORS["blurple"]
        )
        embed.set_footer(text="One ticket per issue, please.")
        view = TicketView(self.bot)
        await ctx.channel.send(embed=embed, view=view)
        await ctx.send(embed=success_embed("Ticket Panel Created!", "The panel has been sent."), delete_after=5)
        await ctx.message.delete()

    # ── Close ────────────────────────────
    @commands.command(name="close", help="Close the current ticket")
    async def close(self, ctx):
        ticket = await self.db.get_ticket(ctx.channel.id)
        if not ticket:
            return await ctx.send(embed=error_embed("Error", "This is not a ticket channel!"))

        if ticket["status"] == "closed":
            return await ctx.send(embed=error_embed("Error", "This ticket is already closed."))

        await self.db.close_ticket(ctx.channel.id)

        embed = success_embed("Ticket Closed", f"Closed by {ctx.author.mention}. Deleting in 5s...")
        await ctx.send(embed=embed)

        import asyncio
        await asyncio.sleep(5)
        await ctx.channel.delete()

    # ── Add Member ───────────────────────
    @commands.command(name="tadd", aliases=["ticketadd"], help="Add a member to the ticket")
    @commands.has_permissions(manage_messages=True)
    async def tadd(self, ctx, member: discord.Member):
        ticket = await self.db.get_ticket(ctx.channel.id)
        if not ticket:
            return await ctx.send(embed=error_embed("Error", "Not a ticket channel!"))

        await ctx.channel.set_permissions(member, view_channel=True, send_messages=True)
        await ctx.send(embed=success_embed("Member Added", f"{member.mention} has been added to this ticket."))

    # ── Remove Member ─────────────────────
    @commands.command(name="tremove", aliases=["ticketremove"], help="Remove a member from the ticket")
    @commands.has_permissions(manage_messages=True)
    async def tremove(self, ctx, member: discord.Member):
        ticket = await self.db.get_ticket(ctx.channel.id)
        if not ticket:
            return await ctx.send(embed=error_embed("Error", "Not a ticket channel!"))

        await ctx.channel.set_permissions(member, overwrite=None)
        await ctx.send(embed=success_embed("Member Removed", f"{member.mention} has been removed from this ticket."))

    # ── Claim ────────────────────────────
    @commands.command(name="claim", help="Claim a ticket (staff only)")
    @commands.has_permissions(manage_messages=True)
    async def claim(self, ctx):
        ticket = await self.db.get_ticket(ctx.channel.id)
        if not ticket:
            return await ctx.send(embed=error_embed("Error", "Not a ticket channel!"))

        embed = success_embed("Ticket Claimed", f"This ticket is now being handled by {ctx.author.mention}")
        await ctx.send(embed=embed)

    # ── Rename ───────────────────────────
    @commands.command(name="trename", help="Rename the ticket channel")
    @commands.has_permissions(manage_channels=True)
    async def trename(self, ctx, *, name: str):
        ticket = await self.db.get_ticket(ctx.channel.id)
        if not ticket:
            return await ctx.send(embed=error_embed("Error", "Not a ticket channel!"))

        await ctx.channel.edit(name=name)
        await ctx.send(embed=success_embed("Renamed", f"Channel renamed to **{name}**."))

    # ── Ticket Info ──────────────────────
    @commands.command(name="tinfo", aliases=["ticketinfo"], help="View info about this ticket")
    async def tinfo(self, ctx):
        ticket = await self.db.get_ticket(ctx.channel.id)
        if not ticket:
            return await ctx.send(embed=error_embed("Error", "Not a ticket channel!"))

        user = ctx.guild.get_member(ticket["user_id"])
        embed = discord.Embed(title="🎫 Ticket Info", color=config.COLORS["info"])
        embed.add_field(name="🆔 ID",        value=ticket["id"],       inline=True)
        embed.add_field(name="👤 Opened by", value=user.mention if user else f"<@{ticket['user_id']}>", inline=True)
        embed.add_field(name="📋 Status",    value=ticket["status"].title(), inline=True)
        embed.add_field(name="📝 Subject",   value=ticket["subject"],  inline=False)
        embed.add_field(name="📅 Created",   value=ticket["created_at"][:10], inline=True)
        if ticket["closed_at"]:
            embed.add_field(name="🔒 Closed", value=ticket["closed_at"][:10], inline=True)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Tickets(bot))