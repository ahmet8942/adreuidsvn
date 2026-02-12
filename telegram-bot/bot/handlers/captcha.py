"""
Captcha handler — intercepts channel join requests,
sends a CAPTCHA image, validates the answer.

NOTE: Does NOT use FSM states for captcha validation — the join request
comes from the channel context, but the user replies in their private chat,
which has a different FSM key.  Instead, we check the DB directly.
"""

import logging
from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    ChatJoinRequest,
    CallbackQuery,
    BufferedInputFile,
)
from aiogram.filters import BaseFilter

from bot.config import config
from bot.database import (
    save_captcha,
    get_captcha,
    delete_captcha,
    increment_captcha_attempts,
    add_user,
    get_setting,
)
from bot.captcha.generator import generate_captcha
from bot.keyboards import captcha_refresh_kb

router = Router(name="captcha")
logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5

DEFAULT_CAPTCHA_TEXT = (
    "🔐 <b>Проверка — Капча</b>\n\n"
    "Введи цифры, которые видишь на картинке, "
    "чтобы подтвердить, что ты не робот."
)


class HasPendingCaptcha(BaseFilter):
    """Filter that matches only if the user has an active captcha session in DB."""

    async def __call__(self, message: Message) -> bool:
        if message.chat.type != "private":
            return False
        session = await get_captcha(message.from_user.id)
        return session is not None


async def _send_captcha(bot: Bot, user_id: int) -> None:
    """Generate and send a new captcha to the user."""
    image_bytes, code = generate_captcha()
    await save_captcha(user_id, code)

    # Load custom captcha caption from DB
    custom_text = await get_setting("captcha_text", DEFAULT_CAPTCHA_TEXT)
    caption = f"{custom_text}\n\nℹ️ Попыток: <b>{MAX_ATTEMPTS}</b>"

    photo = BufferedInputFile(image_bytes.read(), filename="captcha.png")
    await bot.send_photo(
        chat_id=user_id,
        photo=photo,
        caption=caption,
        parse_mode="HTML",
        reply_markup=captcha_refresh_kb(),
    )


# ── Join request → send captcha ─────────────────────────────────────

@router.chat_join_request()
async def on_join_request(event: ChatJoinRequest, bot: Bot) -> None:
    """Intercept a channel/chat join request and send captcha to user."""
    user = event.from_user
    logger.info("Join request from %s (id=%d)", user.first_name, user.id)

    await add_user(user.id, user.username or "", user.first_name or "")

    try:
        await _send_captcha(bot, user.id)
    except Exception as e:
        logger.error("Failed to send captcha to %d: %s", user.id, e)


# ── Refresh captcha button ──────────────────────────────────────────

@router.callback_query(F.data == "captcha_refresh")
async def captcha_refresh(callback: CallbackQuery, bot: Bot) -> None:
    """Generate a new captcha image."""
    await callback.answer("🔄 Новая капча отправлена!")
    await _send_captcha(bot, callback.from_user.id)


# ── Validate captcha answer ─────────────────────────────────────────
# This handler catches ALL text messages in private chat and checks
# if the user has a pending captcha session in the DB.

@router.message(HasPendingCaptcha())
async def check_captcha_answer(message: Message, bot: Bot) -> None:
    """Check if the incoming message is a captcha answer."""
    user_id = message.from_user.id
    answer = message.text.strip() if message.text else ""

    session = await get_captcha(user_id)
    if not session:
        return

    if not answer:
        await message.answer(
            "✏️ Введи цифры с картинки, чтобы пройти проверку.",
            reply_markup=captcha_refresh_kb(),
        )
        return

    if answer == session["code"]:
        # ✅ Correct!
        await delete_captcha(user_id)

        # Approve the join request
        try:
            await bot.approve_chat_join_request(
                chat_id=config.channel_id,
                user_id=user_id,
            )
            await message.answer(
                "✅ <b>Капча пройдена!</b>\n\n"
                "Твоя заявка одобрена. Добро пожаловать в канал! 🎉",
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error("Failed to approve join for %d: %s", user_id, e)
            await message.answer(
                "✅ Капча верна, но не удалось одобрить заявку автоматически.\n"
                "Попробуй отправить заявку ещё раз или обратись к администратору.",
            )
    else:
        # ❌ Wrong answer
        await increment_captcha_attempts(user_id)
        new_session = await get_captcha(user_id)
        attempts = new_session["attempts"] if new_session else MAX_ATTEMPTS

        if attempts >= MAX_ATTEMPTS:
            await delete_captcha(user_id)
            try:
                await bot.decline_chat_join_request(
                    chat_id=config.channel_id,
                    user_id=user_id,
                )
            except Exception:
                pass
            await message.answer(
                "❌ <b>Слишком много попыток.</b>\n\n"
                "Твоя заявка отклонена. Попробуй снова позже.",
                parse_mode="HTML",
            )
        else:
            remaining = MAX_ATTEMPTS - attempts
            await message.answer(
                f"❌ Неверно! Осталось попыток: <b>{remaining}</b>\n"
                "Попробуй ещё раз или нажми кнопку 🔄 для новой капчи.",
                parse_mode="HTML",
                reply_markup=captcha_refresh_kb(),
            )
