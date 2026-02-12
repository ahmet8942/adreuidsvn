"""
Welcome message editor — admins can view, edit, test,
and save a custom welcome message with optional media (photo/video/gif).
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.text_decorations import html_decoration

from bot.config import config
from bot.database import get_setting, set_setting
from bot.keyboards import welcome_confirm_kb, welcome_back_kb, main_menu_kb
from bot.states import WelcomeEditState

router = Router(name="welcome")


def _is_admin(user_id: int) -> bool:
    return user_id in config.admin_ids


async def _send_welcome_preview(bot: Bot, chat_id: int, text: str,
                                 photo_id: str = "", video_id: str = "",
                                 animation_id: str = "", prefix: str = "") -> None:
    """Send a welcome message preview with optional media."""
    if prefix:
        await bot.send_message(chat_id, prefix, parse_mode="HTML")

    if photo_id:
        await bot.send_photo(chat_id, photo=photo_id, caption=text or None, parse_mode="HTML")
    elif video_id:
        await bot.send_video(chat_id, video=video_id, caption=text or None, parse_mode="HTML")
    elif animation_id:
        await bot.send_animation(chat_id, animation=animation_id, caption=text or None, parse_mode="HTML")
    elif text:
        await bot.send_message(chat_id, text, parse_mode="HTML")
    else:
        await bot.send_message(chat_id, "<i>(пусто)</i>", parse_mode="HTML")


# ── Start welcome edit flow ─────────────────────────────────────────

@router.message(F.text == "✏️ Приветствие")
async def start_welcome_edit(message: Message, state: FSMContext, bot: Bot) -> None:
    """Show current welcome and ask for a new one."""
    if not _is_admin(message.from_user.id):
        return

    current_text = await get_setting("welcome_message", config.default_welcome)
    current_photo = await get_setting("welcome_photo_id", "")
    current_video = await get_setting("welcome_video_id", "")
    current_animation = await get_setting("welcome_animation_id", "")

    await _send_welcome_preview(
        bot, message.chat.id,
        text=current_text,
        photo_id=current_photo,
        video_id=current_video,
        animation_id=current_animation,
        prefix="📝 <b>Текущее приветствие:</b>",
    )

    await message.answer(
        "✏️ Отправь мне новое приветствие.\n\n"
        "💡 <b>Поддерживается:</b>\n"
        "• 📝 Текст (с HTML и эмодзи)\n"
        "• 🖼 Фото с подписью\n"
        "• 🎬 Видео с подписью\n"
        "• 🎞 GIF с подписью\n\n"
        "💡 <i>HTML-разметка:</i>\n"
        "<code>&lt;b&gt;жирный&lt;/b&gt;</code>\n"
        "<code>&lt;i&gt;курсив&lt;/i&gt;</code>\n"
        "<code>&lt;u&gt;подчёркнутый&lt;/u&gt;</code>\n"
        "<code>&lt;a href=\"url\"&gt;ссылка&lt;/a&gt;</code>\n\n"
        "Эмодзи тоже приветствуются! 🎉",
        parse_mode="HTML",
        reply_markup=welcome_back_kb(),
    )
    await state.set_state(WelcomeEditState.waiting_for_text)


# ── Receive new welcome content ─────────────────────────────────────

@router.message(WelcomeEditState.waiting_for_text)
async def receive_welcome_content(message: Message, state: FSMContext, bot: Bot) -> None:
    """Store whatever the admin sends (text/photo/video/gif) as the new welcome."""
    if not _is_admin(message.from_user.id):
        return

    new_text = ""
    photo_id = ""
    video_id = ""
    animation_id = ""

    if message.photo:
        photo_id = message.photo[-1].file_id  # best quality
        new_text = html_decoration.unparse(message.caption, message.caption_entities) if message.caption else ""
    elif message.video:
        video_id = message.video.file_id
        new_text = html_decoration.unparse(message.caption, message.caption_entities) if message.caption else ""
    elif message.animation:
        animation_id = message.animation.file_id
        new_text = html_decoration.unparse(message.caption, message.caption_entities) if message.caption else ""
    elif message.text:
        new_text = message.html_text
    else:
        await message.answer(
            "⚠️ Отправь текст, фото, видео или GIF. Другие типы не поддерживаются.",
        )
        return

    if not new_text and not photo_id and not video_id and not animation_id:
        await message.answer("⚠️ Сообщение пустое. Попробуй ещё раз.")
        return

    await state.update_data(
        new_welcome=new_text,
        new_photo_id=photo_id,
        new_video_id=video_id,
        new_animation_id=animation_id,
    )
    await state.set_state(WelcomeEditState.confirm)

    await _send_welcome_preview(
        bot, message.chat.id,
        text=new_text,
        photo_id=photo_id,
        video_id=video_id,
        animation_id=animation_id,
        prefix="👁 <b>Предпросмотр нового приветствия:</b>",
    )

    await message.answer(
        "Что делаем?",
        reply_markup=welcome_confirm_kb(),
    )


# ── Save welcome ────────────────────────────────────────────────────

@router.callback_query(F.data == "welcome_save")
async def save_welcome(callback: CallbackQuery, state: FSMContext) -> None:
    """Persist the new welcome message with media."""
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Недостаточно прав.", show_alert=True)
        return

    data = await state.get_data()
    new_text = data.get("new_welcome", "")
    photo_id = data.get("new_photo_id", "")
    video_id = data.get("new_video_id", "")
    animation_id = data.get("new_animation_id", "")

    if not new_text and not photo_id and not video_id and not animation_id:
        await callback.answer("⚠️ Нечего сохранять.", show_alert=True)
        await state.clear()
        return

    await set_setting("welcome_message", new_text)
    await set_setting("welcome_photo_id", photo_id)
    await set_setting("welcome_video_id", video_id)
    await set_setting("welcome_animation_id", animation_id)
    await state.clear()

    await callback.answer("✅ Сохранено!")
    await callback.message.edit_text("✅ <b>Приветствие обновлено!</b>", parse_mode="HTML")
    await callback.message.answer(
        "📋 Главное меню",
        reply_markup=main_menu_kb(is_admin=True),
    )


# ── Test welcome ────────────────────────────────────────────────────

@router.callback_query(F.data == "welcome_test")
async def test_welcome(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Send the new welcome back to the admin as a test."""
    data = await state.get_data()

    await callback.answer("👁 Тестовое сообщение отправлено!")
    await _send_welcome_preview(
        bot, callback.message.chat.id,
        text=data.get("new_welcome", ""),
        photo_id=data.get("new_photo_id", ""),
        video_id=data.get("new_video_id", ""),
        animation_id=data.get("new_animation_id", ""),
        prefix="🧪 <b>Тест приветствия (так увидят пользователи):</b>",
    )

    await callback.message.answer(
        "Что делаем?",
        reply_markup=welcome_confirm_kb(),
    )


# ── Cancel welcome edit ─────────────────────────────────────────────

@router.callback_query(F.data == "welcome_cancel")
async def cancel_welcome(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel welcome editing."""
    await state.clear()
    is_admin = _is_admin(callback.from_user.id)
    await callback.answer("❌ Отменено.")
    await callback.message.edit_text("❌ Редактирование приветствия отменено.")
    await callback.message.answer(
        "📋 Главное меню",
        reply_markup=main_menu_kb(is_admin=is_admin),
    )
