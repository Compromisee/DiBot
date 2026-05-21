import discord
from discord.ext import commands
from database.db import Database
from utils.embeds import success_embed, error_embed, info_embed
import config

# ─────────────────────────────────────────
#  Reaction Roles Cog
# ─────────────────────────────────────────

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db

    # ── Add Reaction Role ────────────────
    @commands.command(name="rradd", aliases=["addreactionrole"], help="Add a reaction role to a message")
    @commands.has_permissions(manage_roles=True)
    async def rradd(self, ctx, message_id: int, emoji: str, role: discord.Role):
        try:
            msg = await ctx.channel.fetch_message(message_id)
        except discord.NotFound:
            return await ctx.send(embed=error_embed("Not Found", "Message not found in this channel!"))

        await msg.add_reaction(emoji)
        await self.db.add_reaction_role(ctx.guild.id, ctx.channel.id, message_id, emoji, role.id)
        await ctx.send(embed=success_embed(
            "Reaction Role Added!",
            f"React with {emoji} on [that message](https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{message_id}) to get {role.mention}"
        ))

    # ── Remove Reaction Role ─────────────
    @commands.command(name="rrremove", aliases=["removereactionrole"], help="Remove a reaction role")
    @commands.has_permissions(manage_roles=True)
    async def rrremove(self, ctx, message_id: int, emoji: str):
        await self.db.remove_reaction_role(message_id, emoji)
        await ctx.send(embed=success_embed("Reaction Role Removed", f"Removed {emoji} reaction role."))

    # ── List Reaction Roles ──────────────
    @commands.command(name="rrlist", aliases=["reactionroles"], help="List all reaction roles in this server")
    async def rrlist(self, ctx):
        import aiosqlite
        async with aiosqlite.connect(config.DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM reaction_roles WHERE guild_id = ?",
                (ctx.guild.id,)
            ) as cursor:
                rows = [dict(r) for r in await cursor.fetchall()]

        if not rows:
            return await ctx.send(embed=info_embed("No Reaction Roles", "No reaction roles set up!"))

        embed = discord.Embed(title="🎭 Reaction Roles", color=config.COLORS["info"])
        for rr in rows:
            role    = ctx.guild.get_role(rr["role_id"])
            channel = ctx.guild.get_channel(rr["channel_id"])
            embed.add_field(
                name  = f"{rr['emoji']} → {role.name if role else 'Deleted Role'}",
                value = (
                    f"Channel: {channel.mention if channel else 'Deleted'}\n"
                    f"[Jump to message](https://discord.com/channels/{ctx.guild.id}/{rr['channel_id']}/{rr['message_id']})"
                ),
                inline= False
            )
        await ctx.send(embed=embed)

    # ── Create Reaction Role Panel ────────
    @commands.command(name="rrpanel", help="Create a reaction role panel")
    @commands.has_permissions(manage_roles=True)
    async def rrpanel(self, ctx, title: str = "🎭 Role Selection"):
        embed = discord.Embed(
            title       = title,
            description = "React below to get your roles!\n\nReact again to remove the role.",
            color       = config.COLORS["purple"]
        )
        embed.set_footer(text=f"Powered by {config.BOT_NAME}")
        msg = await ctx.send(embed=embed)
        await ctx.send(
            embed=success_embed(
                "Panel Created!",
                f"Use `!rradd {msg.id} <emoji> <role>` to add roles to the panel."
            ),
            delete_after=10
        )
        await ctx.message.delete()

    # ── Reaction Add ─────────────────────
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        rr = await self.db.get_reaction_role(payload.message_id, str(payload.emoji))
        if not rr:
            return

        guild  = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role   = guild.get_role(rr["role_id"])

        if member and role:
            try:
                await member.add_roles(role, reason="Reaction Role")
            except discord.Forbidden:
                pass

    # ── Reaction Remove ──────────────────
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        rr = await self.db.get_reaction_role(payload.message_id, str(payload.emoji))
        if not rr:
            return

        guild  = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role   = guild.get_role(rr["role_id"])

        if member and role:
            try:
                await member.remove_roles(role, reason="Reaction Role removed")
            except discord.Forbidden:
                pass


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))