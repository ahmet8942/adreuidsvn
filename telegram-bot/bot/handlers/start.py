"""
/start command and welcome message handler.
"""

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaAnimation

from bot.config import config
from bot.database import add_user, get_setting
from bot.keyboards import main_menu_kb

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Handle /start — register user, show welcome, show menu."""
    await state.clear()

    user = message.from_user
    await add_user(user.id, user.username or "", user.first_name or "")

    is_admin = user.id in config.admin_ids

    # Get custom welcome — try media first, then text
    welcome_photo = await get_setting("welcome_photo_id", "")
    welcome_video = await get_setting("welcome_video_id", "")
    welcome_animation = await get_setting("welcome_animation_id", "")
    welcome_text = await get_setting("welcome_message", config.default_welcome)

    if welcome_photo:
        await message.answer_photo(
            photo=welcome_photo,
            caption=welcome_text or None,
            parse_mode="HTML",
            reply_markup=main_menu_kb(is_admin),
        )
    elif welcome_video:
        await message.answer_video(
            video=welcome_video,
            caption=welcome_text or None,
            parse_mode="HTML",
            reply_markup=main_menu_kb(is_admin),
        )
    elif welcome_animation:
        await message.answer_animation(
            animation=welcome_animation,
            caption=welcome_text or None,
            parse_mode="HTML",
            reply_markup=main_menu_kb(is_admin),
        )
    else:
        await message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=main_menu_kb(is_admin),
        )


@router.message(F.text == " Статистика")
async def admin_stats(message: Message) -> None:
    """Show bot stats (admin only)."""
    if message.from_user.id not in config.admin_ids:
        return

    from bot.database import get_user_count
    count = await get_user_count()

    await message.answer(
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего пользователей: <b>{count}</b>",
        parse_mode="HTML",
    )
