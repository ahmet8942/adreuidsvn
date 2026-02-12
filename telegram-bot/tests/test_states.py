"""
Tests for FSM states.
"""

from bot.states import CaptchaState, BroadcastState, WelcomeEditState, CaptchaTextEditState


class TestStates:
    def test_captcha_states(self):
        """CaptchaState should have waiting_for_code."""
        assert CaptchaState.waiting_for_code is not None

    def test_broadcast_states(self):
        """BroadcastState should have waiting_for_content and confirm."""
        assert BroadcastState.waiting_for_content is not None
        assert BroadcastState.confirm is not None

    def test_welcome_states(self):
        """WelcomeEditState should have waiting_for_text and confirm."""
        assert WelcomeEditState.waiting_for_text is not None
        assert WelcomeEditState.confirm is not None

    def test_captcha_text_states(self):
        """CaptchaTextEditState should have waiting_for_text and confirm."""
        assert CaptchaTextEditState.waiting_for_text is not None
        assert CaptchaTextEditState.confirm is not None

    def test_states_are_distinct(self):
        """All states should be distinct from each other."""
        all_states = [
            CaptchaState.waiting_for_code,
            BroadcastState.waiting_for_content,
            BroadcastState.confirm,
            WelcomeEditState.waiting_for_text,
            WelcomeEditState.confirm,
            CaptchaTextEditState.waiting_for_text,
            CaptchaTextEditState.confirm,
        ]
        state_values = [str(s) for s in all_states]
        assert len(state_values) == len(set(state_values))
