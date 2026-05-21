import discord
from datetime import datetime, timedelta
import re
import config

def xp_for_level(level: int) -> int:
    return 5 * (level ** 2) + 50 * level + 100

def get_level_from_xp(xp: int) -> int:
    level = 1
    remaining = xp
    while remaining >= xp_for_level(level):
        remaining -= xp_for_level(level)
        level += 1
    return level

def format_time(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"

def is_on_cooldown(last_used: str, cooldown_seconds: int) -> tuple:
    if not last_used:
        return False, 0
    last = datetime.fromisoformat(last_used)
    diff = (datetime.utcnow() - last).total_seconds()
    if diff < cooldown_seconds:
        return True, int(cooldown_seconds - diff)
    return False, 0

def can_moderate(ctx, target: discord.Member) -> tuple:
    if target == ctx.author:
        return False, "You cannot moderate yourself!"
    if target == ctx.guild.owner:
        return False, "You cannot moderate the server owner!"
    if target.top_role >= ctx.author.top_role:
        return False, "Target has equal or higher role!"
    if target.top_role >= ctx.guild.me.top_role:
        return False, "Target has higher role than me!"
    return True, ""

def parse_duration(duration_str: str) -> timedelta:
    """Parse duration string like '1d2h30m' into timedelta"""
    pattern = re.compile(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?')
    match = pattern.match(duration_str)
    if not match or not any(match.groups()):
        raise ValueError("Invalid duration format")
    days = int(match.group(1) or 0)
    hours = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)
    seconds = int(match.group(4) or 0)
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

def progress_bar(current: int, maximum: int, length: int = 20) -> str:
    filled = min(int((current / maximum) * length), length)
    return "█" * filled + "░" * (length - filled)

def truncate(text: str, max_length: int = 1024) -> str:
    return text[:max_length - 3] + "..." if len(text) > max_length else text