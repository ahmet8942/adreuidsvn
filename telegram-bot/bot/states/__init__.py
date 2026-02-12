"""
FSM states for the bot.
"""

from aiogram.fsm.state import State, StatesGroup


class CaptchaState(StatesGroup):
    waiting_for_code = State()


class BroadcastState(StatesGroup):
    waiting_for_content = State()
    confirm = State()


class WelcomeEditState(StatesGroup):
    waiting_for_text = State()
    confirm = State()


class CaptchaTextEditState(StatesGroup):
    waiting_for_text = State()
    confirm = State()
