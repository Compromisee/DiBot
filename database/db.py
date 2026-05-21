import aiosqlite
import config
from datetime import datetime

# ─────────────────────────────────────────
#  Enhanced Database Manager
# ─────────────────────────────────────────

class Database:
    def __init__(self):
        self.db_path = config.DB_PATH

    async def setup(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript("""

                CREATE TABLE IF NOT EXISTS users (
                    user_id     INTEGER,
                    guild_id    INTEGER,
                    xp          INTEGER DEFAULT 0,
                    level       INTEGER DEFAULT 1,
                    coins       INTEGER DEFAULT 500,
                    bank        INTEGER DEFAULT 0,
                    warnings    INTEGER DEFAULT 0,
                    reputation  INTEGER DEFAULT 0,
                    messages    INTEGER DEFAULT 0,
                    last_daily  TEXT DEFAULT NULL,
                    last_work   TEXT DEFAULT NULL,
                    last_xp     TEXT DEFAULT NULL,
                    last_rob    TEXT DEFAULT NULL,
                    last_rep    TEXT DEFAULT NULL,
                    afk_message TEXT DEFAULT NULL,
                    afk_since   TEXT DEFAULT NULL,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                );

                CREATE TABLE IF NOT EXISTS warnings (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     INTEGER,
                    guild_id    INTEGER,
                    reason      TEXT,
                    moderator   INTEGER,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id            INTEGER PRIMARY KEY,
                    prefix              TEXT    DEFAULT '!',
                    welcome_channel     INTEGER DEFAULT NULL,
                    leave_channel       INTEGER DEFAULT NULL,
                    log_channel         INTEGER DEFAULT NULL,
                    starboard_channel   INTEGER DEFAULT NULL,
                    suggestion_channel  INTEGER DEFAULT NULL,
                    ticket_category     INTEGER DEFAULT NULL,
                    ticket_log          INTEGER DEFAULT NULL,
                    mute_role           INTEGER DEFAULT NULL,
                    auto_role           INTEGER DEFAULT NULL,
                    level_up_channel    INTEGER DEFAULT NULL,
                    welcome_message     TEXT    DEFAULT 'Welcome {user} to {server}!',
                    leave_message       TEXT    DEFAULT '{user} has left the server.',
                    automod_enabled     INTEGER DEFAULT 0,
                    antilink            INTEGER DEFAULT 0,
                    antispam            INTEGER DEFAULT 0,
                    max_warnings        INTEGER DEFAULT 3,
                    starboard_threshold INTEGER DEFAULT 3
                );

                CREATE TABLE IF NOT EXISTS giveaways (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id    INTEGER,
                    channel_id  INTEGER,
                    message_id  INTEGER,
                    host_id     INTEGER,
                    prize       TEXT,
                    winners     INTEGER DEFAULT 1,
                    end_time    TEXT,
                    ended       INTEGER DEFAULT 0,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS giveaway_entries (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    giveaway_id INTEGER,
                    user_id     INTEGER,
                    UNIQUE(giveaway_id, user_id)
                );

                CREATE TABLE IF NOT EXISTS tickets (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id    INTEGER,
                    channel_id  INTEGER,
                    user_id     INTEGER,
                    subject     TEXT DEFAULT 'No subject',
                    status      TEXT DEFAULT 'open',
                    claimed_by  INTEGER DEFAULT NULL,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
                    closed_at   TEXT DEFAULT NULL
                );

                CREATE TABLE IF NOT EXISTS shop (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id    INTEGER,
                    item_name   TEXT,
                    item_desc   TEXT DEFAULT '',
                    price       INTEGER,
                    role_id     INTEGER DEFAULT NULL,
                    stock       INTEGER DEFAULT -1,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS inventory (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     INTEGER,
                    guild_id    INTEGER,
                    item_name   TEXT,
                    quantity    INTEGER DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS starboard (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id        INTEGER,
                    original_msg_id INTEGER UNIQUE,
                    starboard_msg_id INTEGER,
                    channel_id      INTEGER,
                    author_id       INTEGER,
                    star_count      INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS reminders (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     INTEGER,
                    channel_id  INTEGER,
                    guild_id    INTEGER,
                    message     TEXT,
                    remind_at   TEXT,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
                    completed   INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS suggestions (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id    INTEGER,
                    user_id     INTEGER,
                    message_id  INTEGER,
                    content     TEXT,
                    status      TEXT DEFAULT 'pending',
                    response    TEXT DEFAULT NULL,
                    upvotes     INTEGER DEFAULT 0,
                    downvotes   INTEGER DEFAULT 0,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS reaction_roles (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id    INTEGER,
                    channel_id  INTEGER,
                    message_id  INTEGER,
                    emoji       TEXT,
                    role_id     INTEGER
                );

                CREATE TABLE IF NOT EXISTS mod_logs (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id    INTEGER,
                    action      TEXT,
                    target_id   INTEGER,
                    moderator_id INTEGER,
                    reason      TEXT,
                    duration    TEXT DEFAULT NULL,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS level_roles (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id    INTEGER,
                    level       INTEGER,
                    role_id     INTEGER,
                    UNIQUE(guild_id, level)
                );

                CREATE TABLE IF NOT EXISTS tags (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id    INTEGER,
                    name        TEXT,
                    content     TEXT,
                    author_id   INTEGER,
                    uses        INTEGER DEFAULT 0,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, name)
                );

                CREATE TABLE IF NOT EXISTS polls (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id    INTEGER,
                    channel_id  INTEGER,
                    message_id  INTEGER,
                    question    TEXT,
                    options     TEXT,
                    end_time    TEXT DEFAULT NULL,
                    ended       INTEGER DEFAULT 0,
                    author_id   INTEGER,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS temp_bans (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id    INTEGER,
                    user_id     INTEGER,
                    moderator   INTEGER,
                    reason      TEXT,
                    unban_at    TEXT,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
                );

            """)
            await db.commit()
        print("✅ Database initialized!")

    # ── User Operations ──────────────────
    async def get_user(self, user_id: int, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    await self.create_user(user_id, guild_id)
                    return await self.get_user(user_id, guild_id)
                return dict(row)

    async def create_user(self, user_id: int, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, guild_id, coins) VALUES (?, ?, ?)",
                (user_id, guild_id, config.STARTING_BALANCE)
            )
            await db.commit()

    async def update_user(self, user_id: int, guild_id: int, **kwargs):
        if not kwargs:
            return
        fields = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [user_id, guild_id]
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"UPDATE users SET {fields} WHERE user_id = ? AND guild_id = ?",
                values
            )
            await db.commit()

    async def get_leaderboard(self, guild_id: int, column: str = "xp", limit: int = 10):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                f"SELECT * FROM users WHERE guild_id = ? ORDER BY {column} DESC LIMIT ?",
                (guild_id, limit)
            ) as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    async def get_all_users(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE guild_id = ? ORDER BY xp DESC",
                (guild_id,)
            ) as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    # ── Warning Operations ────────────────
    async def add_warning(self, user_id: int, guild_id: int, reason: str, moderator_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO warnings (user_id, guild_id, reason, moderator) VALUES (?, ?, ?, ?)",
                (user_id, guild_id, reason, moderator_id)
            )
            await db.execute(
                "UPDATE users SET warnings = warnings + 1 WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            await db.commit()

    async def get_warnings(self, user_id: int, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM warnings WHERE user_id = ? AND guild_id = ? ORDER BY created_at DESC",
                (user_id, guild_id)
            ) as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    async def clear_warnings(self, user_id: int, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM warnings WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
            await db.execute("UPDATE users SET warnings = 0 WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
            await db.commit()

    # ── Guild Settings ────────────────────
    async def get_guild_settings(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM guild_settings WHERE guild_id = ?", (guild_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    await db.execute("INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)", (guild_id,))
                    await db.commit()
                    return await self.get_guild_settings(guild_id)
                return dict(row)

    async def update_guild_settings(self, guild_id: int, **kwargs):
        fields = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [guild_id]
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"UPDATE guild_settings SET {fields} WHERE guild_id = ?", values)
            await db.commit()

    # ── Giveaway Operations ───────────────
    async def create_giveaway(self, guild_id, channel_id, message_id, host_id, prize, winners, end_time):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO giveaways (guild_id, channel_id, message_id, host_id, prize, winners, end_time) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (guild_id, channel_id, message_id, host_id, prize, winners, end_time)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_active_giveaways(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM giveaways WHERE ended = 0") as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    async def end_giveaway(self, giveaway_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE giveaways SET ended = 1 WHERE id = ?", (giveaway_id,))
            await db.commit()

    async def enter_giveaway(self, giveaway_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "INSERT INTO giveaway_entries (giveaway_id, user_id) VALUES (?, ?)",
                    (giveaway_id, user_id)
                )
                await db.commit()
                return True
            except Exception:
                return False

    async def get_giveaway_entries(self, giveaway_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT user_id FROM giveaway_entries WHERE giveaway_id = ?",
                (giveaway_id,)
            ) as cursor:
                return [row[0] for row in await cursor.fetchall()]

    # ── Ticket Operations ─────────────────
    async def create_ticket(self, guild_id, channel_id, user_id, subject="No subject"):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO tickets (guild_id, channel_id, user_id, subject) VALUES (?, ?, ?, ?)",
                (guild_id, channel_id, user_id, subject)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_ticket(self, channel_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM tickets WHERE channel_id = ?", (channel_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def close_ticket(self, channel_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE tickets SET status = 'closed', closed_at = ? WHERE channel_id = ?",
                (datetime.utcnow().isoformat(), channel_id)
            )
            await db.commit()

    async def get_user_tickets(self, user_id: int, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM tickets WHERE user_id = ? AND guild_id = ? AND status = 'open'",
                (user_id, guild_id)
            ) as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    # ── Shop Operations ──────────────────
    async def get_shop_items(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM shop WHERE guild_id = ?", (guild_id,)) as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    async def add_shop_item(self, guild_id, name, desc, price, role_id=None, stock=-1):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO shop (guild_id, item_name, item_desc, price, role_id, stock) VALUES (?, ?, ?, ?, ?, ?)",
                (guild_id, name, desc, price, role_id, stock)
            )
            await db.commit()

    async def remove_shop_item(self, guild_id: int, item_name: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM shop WHERE guild_id = ? AND item_name = ?", (guild_id, item_name))
            await db.commit()

    async def get_inventory(self, user_id: int, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM inventory WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            ) as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    async def add_to_inventory(self, user_id, guild_id, item_name, quantity=1):
        async with aiosqlite.connect(self.db_path) as db:
            existing = await db.execute(
                "SELECT * FROM inventory WHERE user_id = ? AND guild_id = ? AND item_name = ?",
                (user_id, guild_id, item_name)
            )
            row = await existing.fetchone()
            if row:
                await db.execute(
                    "UPDATE inventory SET quantity = quantity + ? WHERE user_id = ? AND guild_id = ? AND item_name = ?",
                    (quantity, user_id, guild_id, item_name)
                )
            else:
                await db.execute(
                    "INSERT INTO inventory (user_id, guild_id, item_name, quantity) VALUES (?, ?, ?, ?)",
                    (user_id, guild_id, item_name, quantity)
                )
            await db.commit()

    # ── Reminder Operations ───────────────
    async def create_reminder(self, user_id, channel_id, guild_id, message, remind_at):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO reminders (user_id, channel_id, guild_id, message, remind_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, channel_id, guild_id, message, remind_at)
            )
            await db.commit()

    async def get_pending_reminders(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM reminders WHERE completed = 0 AND remind_at <= ?",
                (datetime.utcnow().isoformat(),)
            ) as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    async def complete_reminder(self, reminder_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE reminders SET completed = 1 WHERE id = ?", (reminder_id,))
            await db.commit()

    # ── Starboard Operations ──────────────
    async def get_starboard_entry(self, original_msg_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM starboard WHERE original_msg_id = ?",
                (original_msg_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def create_starboard_entry(self, guild_id, original_msg_id, starboard_msg_id, channel_id, author_id, star_count):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO starboard (guild_id, original_msg_id, starboard_msg_id, channel_id, author_id, star_count) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (guild_id, original_msg_id, starboard_msg_id, channel_id, author_id, star_count)
            )
            await db.commit()

    async def update_starboard_entry(self, original_msg_id: int, star_count: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE starboard SET star_count = ? WHERE original_msg_id = ?",
                (star_count, original_msg_id)
            )
            await db.commit()

    # ── Reaction Roles ────────────────────
    async def add_reaction_role(self, guild_id, channel_id, message_id, emoji, role_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO reaction_roles (guild_id, channel_id, message_id, emoji, role_id) VALUES (?, ?, ?, ?, ?)",
                (guild_id, channel_id, message_id, emoji, role_id)
            )
            await db.commit()

    async def get_reaction_role(self, message_id: int, emoji: str):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM reaction_roles WHERE message_id = ? AND emoji = ?",
                (message_id, emoji)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def remove_reaction_role(self, message_id: int, emoji: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM reaction_roles WHERE message_id = ? AND emoji = ?",
                (message_id, emoji)
            )
            await db.commit()

    # ── Tags ──────────────────────────────
    async def create_tag(self, guild_id, name, content, author_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO tags (guild_id, name, content, author_id) VALUES (?, ?, ?, ?)",
                (guild_id, name, content, author_id)
            )
            await db.commit()

    async def get_tag(self, guild_id: int, name: str):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM tags WHERE guild_id = ? AND name = ?",
                (guild_id, name)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    await db.execute(
                        "UPDATE tags SET uses = uses + 1 WHERE guild_id = ? AND name = ?",
                        (guild_id, name)
                    )
                    await db.commit()
                return dict(row) if row else None

    async def delete_tag(self, guild_id: int, name: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM tags WHERE guild_id = ? AND name = ?", (guild_id, name))
            await db.commit()

    async def get_all_tags(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM tags WHERE guild_id = ?", (guild_id,)) as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    # ── Mod Logs ──────────────────────────
    async def add_mod_log(self, guild_id, action, target_id, moderator_id, reason, duration=None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO mod_logs (guild_id, action, target_id, moderator_id, reason, duration) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (guild_id, action, target_id, moderator_id, reason, duration)
            )
            await db.commit()

    async def get_mod_logs(self, guild_id: int, target_id: int = None, limit: int = 20):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if target_id:
                query = "SELECT * FROM mod_logs WHERE guild_id = ? AND target_id = ? ORDER BY created_at DESC LIMIT ?"
                params = (guild_id, target_id, limit)
            else:
                query = "SELECT * FROM mod_logs WHERE guild_id = ? ORDER BY created_at DESC LIMIT ?"
                params = (guild_id, limit)
            async with db.execute(query, params) as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    # ── Suggestions ───────────────────────
    async def create_suggestion(self, guild_id, user_id, message_id, content):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO suggestions (guild_id, user_id, message_id, content) VALUES (?, ?, ?, ?)",
                (guild_id, user_id, message_id, content)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_suggestion(self, suggestion_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM suggestions WHERE id = ?", (suggestion_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_suggestion(self, suggestion_id: int, **kwargs):
        fields = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [suggestion_id]
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"UPDATE suggestions SET {fields} WHERE id = ?", values)
            await db.commit()

    # ── Temp Bans ─────────────────────────
    async def add_temp_ban(self, guild_id, user_id, moderator, reason, unban_at):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO temp_bans (guild_id, user_id, moderator, reason, unban_at) VALUES (?, ?, ?, ?, ?)",
                (guild_id, user_id, moderator, reason, unban_at)
            )
            await db.commit()

    async def get_expired_bans(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM temp_bans WHERE unban_at <= ?",
                (datetime.utcnow().isoformat(),)
            ) as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    async def remove_temp_ban(self, guild_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM temp_bans WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id)
            )
            await db.commit()

    # ── Level Roles ───────────────────────
    async def add_level_role(self, guild_id, level, role_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO level_roles (guild_id, level, role_id) VALUES (?, ?, ?)",
                (guild_id, level, role_id)
            )
            await db.commit()

    async def get_level_roles(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM level_roles WHERE guild_id = ? ORDER BY level ASC",
                (guild_id,)
            ) as cursor:
                return [dict(r) for r in await cursor.fetchall()]

    async def remove_level_role(self, guild_id: int, level: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM level_roles WHERE guild_id = ? AND level = ?", (guild_id, level))
            await db.commit()

    # ── Stats ─────────────────────────────
    async def get_guild_stats(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            stats = {}
            async with db.execute("SELECT COUNT(*) FROM users WHERE guild_id = ?", (guild_id,)) as c:
                stats["total_users"] = (await c.fetchone())[0]
            async with db.execute("SELECT SUM(messages) FROM users WHERE guild_id = ?", (guild_id,)) as c:
                stats["total_messages"] = (await c.fetchone())[0] or 0
            async with db.execute("SELECT SUM(coins + bank) FROM users WHERE guild_id = ?", (guild_id,)) as c:
                stats["total_economy"] = (await c.fetchone())[0] or 0
            async with db.execute("SELECT COUNT(*) FROM warnings WHERE guild_id = ?", (guild_id,)) as c:
                stats["total_warnings"] = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM tickets WHERE guild_id = ?", (guild_id,)) as c:
                stats["total_tickets"] = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM giveaways WHERE guild_id = ?", (guild_id,)) as c:
                stats["total_giveaways"] = (await c.fetchone())[0]
            return stats