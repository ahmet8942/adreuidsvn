"""
Captcha text editor — admins can customise the caption that appears
alongside the CAPTCHA image.  Supports emoji and HTML.
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from bot.config import config
from bot.database import get_setting, set_setting
from bot.keyboards import captcha_text_confirm_kb, captcha_text_back_kb, main_menu_kb
from bot.states import CaptchaTextEditState
from bot.captcha.generator import generate_captcha

router = Router(name="captcha_text")

DEFAULT_CAPTCHA_TEXT = (
    "🔐 <b>Проверка — Капча</b>\n\n"
    "Введи цифры, которые видишь на картинке, "
    "чтобы подтвердить, что ты не робот.\n\n"
    "У тебя <b>5</b> попыток."
)


def _is_admin(user_id: int) -> bool:
    return user_id in config.admin_ids


# ── Start captcha text edit flow ────────────────────────────────────

CAPTCHA_TEXT_BUTTON = "\U0001f510 Текст капчи"


@router.message(F.text == CAPTCHA_TEXT_BUTTON)
async def start_captcha_text_edit(message: Message, state: FSMContext, bot: Bot) -> None:
    """Show current captcha text and ask for a new one."""
    if not _is_admin(message.from_user.id):
        return

    current = await get_setting("captcha_text", DEFAULT_CAPTCHA_TEXT)

    # Show a sample captcha with current text
    image_bytes, _ = generate_captcha()
    photo = BufferedInputFile(image_bytes.read(), filename="captcha_preview.png")
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo,
        caption=f"📝 <b>Текущий текст капчи:</b>\n\n{current}",
        parse_mode="HTML",
    )

    await message.answer(
        "✏️ Отправь мне новый текст для капчи.\n\n"
        "💡 <b>Поддерживается:</b>\n"
        "• HTML-разметка (<code>&lt;b&gt;</code>, <code>&lt;i&gt;</code>, <code>&lt;u&gt;</code>)\n"
        "• Эмодзи 🎉🔐✅\n\n"
        "⚠️ Количество попыток подставляется автоматически, "
        "его писать не нужно.",
        parse_mode="HTML",
        reply_markup=captcha_text_back_kb(),
    )
    await state.set_state(CaptchaTextEditState.waiting_for_text)


# ── Receive new captcha text ────────────────────────────────────────

@router.message(CaptchaTextEditState.waiting_for_text)
async def receive_captcha_text(message: Message, state: FSMContext, bot: Bot) -> None:
    """Store the new captcha text and ask for confirmation."""
    if not _is_admin(message.from_user.id):
        return

    new_text = message.html_text if message.text else ""
    if not new_text.strip():
        await message.answer("⚠️ Текст не может быть пустым. Попробуй ещё раз.")
        return

    await state.update_data(new_captcha_text=new_text)
    await state.set_state(CaptchaTextEditState.confirm)

    # Show preview with sample captcha
    image_bytes, _ = generate_captcha()
    photo = BufferedInputFile(image_bytes.read(), filename="captcha_preview.png")
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo,
        caption=f"👁 <b>Предпросмотр:</b>\n\n{new_text}",
        parse_mode="HTML",
    )

    await message.answer(
        "Что делаем?",
        reply_markup=captcha_text_confirm_kb(),
    )


# ── Save captcha text ───────────────────────────────────────────────

@router.callback_query(F.data == "captext_save")
async def save_captcha_text(callback: CallbackQuery, state: FSMContext) -> None:
    """Persist the new captcha text."""
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Недостаточно прав.", show_alert=True)
        return

    data = await state.get_data()
    new_text = data.get("new_captcha_text", "")
    if not new_text:
        await callback.answer("⚠️ Текст не найден.", show_alert=True)
        await state.clear()
        return

    await set_setting("captcha_text", new_text)
    await state.clear()

    await callback.answer("✅ Сохранено!")
    await callback.message.edit_text("✅ <b>Текст капчи обновлён!</b>", parse_mode="HTML")
    await callback.message.answer(
        "📋 Главное меню",
        reply_markup=main_menu_kb(is_admin=True),
    )


# ── Test captcha text ───────────────────────────────────────────────

@router.callback_query(F.data == "captext_test")
async def test_captcha_text(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Send a test captcha with the new text."""
    data = await state.get_data()
    new_text = data.get("new_captcha_text", "")

    await callback.answer("👁 Тест отправлен!")

    image_bytes, _ = generate_captcha()
    photo = BufferedInputFile(image_bytes.read(), filename="captcha_test.png")
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        photo=photo,
        caption=f"🧪 <b>Тест (так увидят пользователи):</b>\n\n{new_text}",
        parse_mode="HTML",
    )

    await callback.message.answer(
        "Что делаем?",
        reply_markup=captcha_text_confirm_kb(),
    )


# ── Cancel captcha text edit ────────────────────────────────────────

@router.callback_query(F.data == "captext_cancel")
async def cancel_captcha_text(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel captcha text editing."""
    await state.clear()
    is_admin = _is_admin(callback.from_user.id)
    await callback.answer("❌ Отменено.")
    await callback.message.edit_text("❌ Редактирование текста капчи отменено.")
    await callback.message.answer(
        "📋 Главное меню",
        reply_markup=main_menu_kb(is_admin=is_admin),
    )
