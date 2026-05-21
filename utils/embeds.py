import discord
from datetime import datetime
import config

def success_embed(title: str, description: str = "") -> discord.Embed:
    return discord.Embed(title=f"✅ {title}", description=description, color=config.COLORS["success"], timestamp=datetime.utcnow())

def error_embed(title: str, description: str = "") -> discord.Embed:
    return discord.Embed(title=f"❌ {title}", description=description, color=config.COLORS["error"], timestamp=datetime.utcnow())

def warning_embed(title: str, description: str = "") -> discord.Embed:
    return discord.Embed(title=f"⚠️ {title}", description=description, color=config.COLORS["warning"], timestamp=datetime.utcnow())

def info_embed(title: str, description: str = "") -> discord.Embed:
    return discord.Embed(title=f"ℹ️ {title}", description=description, color=config.COLORS["info"], timestamp=datetime.utcnow())

def profile_embed(user: discord.Member, data: dict) -> discord.Embed:
    embed = discord.Embed(title=f"👤 {user.display_name}'s Profile", color=config.COLORS["purple"], timestamp=datetime.utcnow())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="⭐ Level", value=data["level"], inline=True)
    embed.add_field(name="✨ XP", value=f"{data['xp']:,}", inline=True)
    embed.add_field(name="💰 Coins", value=f"{data['coins']:,}", inline=True)
    embed.add_field(name="🏦 Bank", value=f"{data['bank']:,}", inline=True)
    embed.add_field(name="⚠️ Warnings", value=data["warnings"], inline=True)
    embed.add_field(name="💬 Messages", value=f"{data['messages']:,}", inline=True)
    embed.add_field(name="⭐ Rep", value=data["reputation"], inline=True)
    embed.set_footer(text=f"ID: {user.id}")
    return embed