"""
Inline and reply keyboards.
"""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


# ── Main menu (regular users) ───────────────────────────────────────

def main_menu_kb(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Build the main reply keyboard."""
    buttons: list[list[KeyboardButton]] = []
    if is_admin:
        buttons.append([KeyboardButton(text="📢 РАССЫЛКА")])
        buttons.append([KeyboardButton(text="✏️ Приветствие"), KeyboardButton(text="\U0001f510 Текст капчи")])
        buttons.append([KeyboardButton(text="📊 Статистика")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# ── Captcha ──────────────────────────────────────────────────────────

def captcha_refresh_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Новая капча", callback_data="captcha_refresh")]
    ])


# ── Broadcast ────────────────────────────────────────────────────────

def broadcast_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Отправить всем", callback_data="broadcast_confirm"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="broadcast_cancel"),
        ]
    ])


def broadcast_cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить рассылку", callback_data="broadcast_cancel")]
    ])


# ── Welcome edit ─────────────────────────────────────────────────────

def welcome_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Сохранить", callback_data="welcome_save"),
            InlineKeyboardButton(text="👁 Тест", callback_data="welcome_test"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="welcome_cancel"),
        ]
    ])


def welcome_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="welcome_cancel")]
    ])


# ── Captcha text edit ────────────────────────────────────────────────

def captcha_text_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Сохранить", callback_data="captext_save"),
            InlineKeyboardButton(text="👁 Тест", callback_data="captext_test"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="captext_cancel"),
        ]
    ])


def captcha_text_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="captext_cancel")]
    ])
