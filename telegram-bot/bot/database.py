"""
Async SQLite database layer.
Stores users, welcome text, pending captcha sessions.
"""

import aiosqlite
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bot_data.db")


async def init_db(path: str = DB_PATH) -> None:
    """Create tables if they don't exist."""
    async with aiosqlite.connect(path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                first_name  TEXT,
                joined_at   TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS captcha_sessions (
                user_id     INTEGER PRIMARY KEY,
                code        TEXT NOT NULL,
                attempts    INTEGER DEFAULT 0,
                created_at  TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.commit()


# ── Users ────────────────────────────────────────────────────────────

async def add_user(user_id: int, username: str = "", first_name: str = "",
                   path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username or "", first_name or ""),
        )
        await db.commit()


async def get_all_user_ids(path: str = DB_PATH) -> list[int]:
    async with aiosqlite.connect(path) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        return [r[0] for r in rows]


async def get_user_count(path: str = DB_PATH) -> int:
    async with aiosqlite.connect(path) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0] if row else 0


async def remove_user(user_id: int, path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.commit()


# ── Settings (welcome message, etc.) ────────────────────────────────

async def get_setting(key: str, default: str = "", path: str = DB_PATH) -> str:
    async with aiosqlite.connect(path) as db:
        cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row[0] if row else default


async def set_setting(key: str, value: str, path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
        await db.commit()


# ── Captcha Sessions ────────────────────────────────────────────────

async def save_captcha(user_id: int, code: str, path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await db.execute(
            "INSERT OR REPLACE INTO captcha_sessions (user_id, code, attempts) "
            "VALUES (?, ?, 0)",
            (user_id, code),
        )
        await db.commit()


async def get_captcha(user_id: int, path: str = DB_PATH) -> Optional[dict]:
    async with aiosqlite.connect(path) as db:
        cursor = await db.execute(
            "SELECT code, attempts FROM captcha_sessions WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        if row:
            return {"code": row[0], "attempts": row[1]}
        return None


async def increment_captcha_attempts(user_id: int, path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await db.execute(
            "UPDATE captcha_sessions SET attempts = attempts + 1 WHERE user_id = ?",
            (user_id,),
        )
        await db.commit()


async def delete_captcha(user_id: int, path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await db.execute("DELETE FROM captcha_sessions WHERE user_id = ?", (user_id,))
        await db.commit()
