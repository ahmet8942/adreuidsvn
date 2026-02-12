"""
Bot configuration — loads settings from .env
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str = ""
    channel_id: int = 0
    admin_ids: list[int] = field(default_factory=list)
    default_welcome: str = (
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Рад видеть тебя здесь! Я помогу тебе вступить в наш канал.\n\n"
        "Нажми кнопку ниже, чтобы начать."
    )

    def __post_init__(self):
        self.bot_token = os.getenv("BOT_TOKEN", self.bot_token)
        channel_raw = os.getenv("CHANNEL_ID", str(self.channel_id))
        self.channel_id = int(channel_raw) if channel_raw else 0

        admin_raw = os.getenv("ADMIN_IDS", "")
        if admin_raw:
            self.admin_ids = [int(x.strip()) for x in admin_raw.split(",") if x.strip()]

        env_welcome = os.getenv("WELCOME_MESSAGE", "")
        if env_welcome:
            self.default_welcome = env_welcome.replace("\\n", "\n")


config = Config()
