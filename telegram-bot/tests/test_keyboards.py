"""
Tests for keyboard builders.
"""

import pytest
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from bot.keyboards import (
    main_menu_kb,
    captcha_refresh_kb,
    broadcast_confirm_kb,
    broadcast_cancel_kb,
    welcome_confirm_kb,
    welcome_back_kb,
    captcha_text_confirm_kb,
    captcha_text_back_kb,
)


class TestMainMenuKeyboard:
    def test_regular_user_menu(self):
        """Regular user should see no buttons (empty keyboard)."""
        kb = main_menu_kb(is_admin=False)
        assert isinstance(kb, ReplyKeyboardMarkup)
        all_text = [btn.text for row in kb.keyboard for btn in row]
        assert "📢 РАССЫЛКА" not in all_text
        assert "✏️ Приветствие" not in all_text

    def test_admin_menu(self):
        """Admin should see broadcast, welcome, captcha text and stats buttons."""
        kb = main_menu_kb(is_admin=True)
        all_text = [btn.text for row in kb.keyboard for btn in row]
        assert "📢 РАССЫЛКА" in all_text
        assert "✏️ Приветствие" in all_text
        # Check captcha text button exists (match by text suffix)
        assert any("Текст капчи" in t for t in all_text)
        assert "📊 Статистика" in all_text

    def test_resize_keyboard(self):
        """Keyboard should be resized."""
        kb = main_menu_kb()
        assert kb.resize_keyboard is True


class TestCaptchaKeyboard:
    def test_refresh_button(self):
        """Should have a refresh captcha button."""
        kb = captcha_refresh_kb()
        assert isinstance(kb, InlineKeyboardMarkup)
        btn = kb.inline_keyboard[0][0]
        assert btn.callback_data == "captcha_refresh"
        assert "🔄" in btn.text


class TestBroadcastKeyboards:
    def test_confirm_has_two_buttons(self):
        """Confirm keyboard should have confirm and cancel buttons."""
        kb = broadcast_confirm_kb()
        row = kb.inline_keyboard[0]
        callbacks = [b.callback_data for b in row]
        assert "broadcast_confirm" in callbacks
        assert "broadcast_cancel" in callbacks

    def test_cancel_keyboard(self):
        """Cancel keyboard should have one cancel button."""
        kb = broadcast_cancel_kb()
        btn = kb.inline_keyboard[0][0]
        assert btn.callback_data == "broadcast_cancel"


class TestWelcomeKeyboards:
    def test_confirm_has_three_buttons(self):
        """Welcome confirm should have save, test, cancel."""
        kb = welcome_confirm_kb()
        row = kb.inline_keyboard[0]
        callbacks = [b.callback_data for b in row]
        assert "welcome_save" in callbacks
        assert "welcome_test" in callbacks
        assert "welcome_cancel" in callbacks

    def test_back_keyboard(self):
        """Back keyboard should have one cancel button."""
        kb = welcome_back_kb()
        btn = kb.inline_keyboard[0][0]
        assert btn.callback_data == "welcome_cancel"


class TestCaptchaTextKeyboards:
    def test_confirm_has_three_buttons(self):
        """Captcha text confirm should have save, test, cancel."""
        kb = captcha_text_confirm_kb()
        row = kb.inline_keyboard[0]
        callbacks = [b.callback_data for b in row]
        assert "captext_save" in callbacks
        assert "captext_test" in callbacks
        assert "captext_cancel" in callbacks

    def test_back_keyboard(self):
        """Back keyboard should have cancel button."""
        kb = captcha_text_back_kb()
        btn = kb.inline_keyboard[0][0]
        assert btn.callback_data == "captext_cancel"
