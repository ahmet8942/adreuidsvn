"""
Bot application — assembles routers, sets up middleware, starts polling.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from bot.config import config
from bot.database import init_db
from bot.handlers import start, captcha, broadcast, welcome
from bot.handlers import captcha_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Entry point — initialize DB, build dispatcher, start polling."""
    logger.info("Initializing database...")
    await init_db()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher(storage=MemoryStorage())

    # Register routers (order matters!)
    # captcha.router FIRST — HasPendingCaptcha filter only matches users
    # with an active captcha session in DB, so it won't block other handlers.
    dp.include_routers(
        captcha.router,
        broadcast.router,
        welcome.router,
        captcha_text.router,
        start.router,
    )

    logger.info("Bot is starting...")
    logger.info("Admin IDs: %s", config.admin_ids)
    logger.info("Channel ID: %s", config.channel_id)

    # Drop pending updates and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
