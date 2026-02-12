"""
Broadcast (рассылка) handler — allows admins to create and send
posts to all bot users.
"""

import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.config import config
from bot.database import get_all_user_ids, remove_user
from bot.keyboards import broadcast_confirm_kb, broadcast_cancel_kb, main_menu_kb
from bot.states import BroadcastState

router = Router(name="broadcast")
logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    return user_id in config.admin_ids


# ── Start broadcast flow ────────────────────────────────────────────

@router.message(F.text == "📢 РАССЫЛКА")
async def start_broadcast(message: Message, state: FSMContext) -> None:
    """Admin pressed the broadcast button."""
    if not _is_admin(message.from_user.id):
        return

    await state.set_state(BroadcastState.waiting_for_content)
    await message.answer(
        "📢 <b>Создание рассылки</b>\n\n"
        "Отправь мне сообщение, которое хочешь разослать всем пользователям.\n\n"
        "Поддерживается:\n"
        "• 📝 Текст (с форматированием и эмодзи)\n"
        "• 🖼 Фото с подписью\n"
        "• 🎬 Видео с подписью\n"
        "• 📄 Документы\n"
        "• 🎵 Аудио\n"
        "• 📍 Стикеры\n\n"
        "Или нажми кнопку отмены ⬇️",
        parse_mode="HTML",
        reply_markup=broadcast_cancel_kb(),
    )


# ── Receive broadcast content ───────────────────────────────────────

@router.message(BroadcastState.waiting_for_content)
async def receive_broadcast_content(message: Message, state: FSMContext) -> None:
    """Save whatever the admin sends as the broadcast content."""
    if not _is_admin(message.from_user.id):
        return

    # Store the message_id so we can forward/copy it later
    await state.update_data(
        broadcast_chat_id=message.chat.id,
        broadcast_message_id=message.message_id,
    )
    await state.set_state(BroadcastState.confirm)

    await message.answer(
        "👆 <b>Предпросмотр выше.</b>\n\n"
        "Это сообщение будет отправлено всем пользователям бота.\n"
        "Подтвердить отправку?",
        parse_mode="HTML",
        reply_markup=broadcast_confirm_kb(),
    )


# ── Confirm broadcast ───────────────────────────────────────────────

@router.callback_query(F.data == "broadcast_confirm")
async def confirm_broadcast(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    """Send the broadcast to all users."""
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Недостаточно прав.", show_alert=True)
        return

    data = await state.get_data()
    source_chat = data.get("broadcast_chat_id")
    source_msg = data.get("broadcast_message_id")

    if not source_chat or not source_msg:
        await callback.answer("⚠️ Сообщение не найдено.", show_alert=True)
        await state.clear()
        return

    await callback.answer("🚀 Рассылка запущена!")
    await callback.message.edit_text("⏳ <b>Рассылка в процессе...</b>", parse_mode="HTML")

    user_ids = await get_all_user_ids()
    total = len(user_ids)
    success = 0
    failed = 0
    blocked = 0

    for i, uid in enumerate(user_ids):
        try:
            await bot.copy_message(
                chat_id=uid,
                from_chat_id=source_chat,
                message_id=source_msg,
            )
            success += 1
        except Exception as e:
            err_text = str(e).lower()
            if "blocked" in err_text or "deactivated" in err_text:
                blocked += 1
                await remove_user(uid)
            else:
                failed += 1
                logger.warning("Broadcast to %d failed: %s", uid, e)

        # Rate limiting: ~25 messages/sec to stay within Telegram limits
        if (i + 1) % 25 == 0:
            await asyncio.sleep(1)

    await state.clear()

    await callback.message.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"📊 Всего пользователей: <b>{total}</b>\n"
        f"✅ Доставлено: <b>{success}</b>\n"
        f"🚫 Заблокировали бота: <b>{blocked}</b>\n"
        f"❌ Ошибки: <b>{failed}</b>",
        parse_mode="HTML",
    )

    # Re-show admin menu
    await callback.message.answer(
        "📋 Главное меню",
        reply_markup=main_menu_kb(is_admin=True),
    )


# ── Cancel broadcast ────────────────────────────────────────────────

@router.callback_query(F.data == "broadcast_cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel the broadcast flow."""
    await state.clear()
    is_admin = _is_admin(callback.from_user.id)
    await callback.answer("❌ Рассылка отменена.")
    await callback.message.edit_text("❌ Рассылка отменена.")
    await callback.message.answer(
        "📋 Главное меню",
        reply_markup=main_menu_kb(is_admin=is_admin),
    )
