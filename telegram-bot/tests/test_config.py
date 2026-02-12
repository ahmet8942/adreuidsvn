"""
Tests for configuration.
"""

import os
import pytest


class TestConfig:
    """Tests for Config dataclass."""

    def test_config_loads_env(self):
        """Config should load values from environment."""
        os.environ["BOT_TOKEN"] = "test-token-123"
        os.environ["CHANNEL_ID"] = "-100999"
        os.environ["ADMIN_IDS"] = "111,222,333"

        # Re-import to pick up new env
        from bot.config import Config
        cfg = Config()

        assert cfg.bot_token == "test-token-123"
        assert cfg.channel_id == -100999
        assert cfg.admin_ids == [111, 222, 333]

    def test_config_default_welcome(self):
        """Config should have a default welcome message."""
        from bot.config import Config
        os.environ.pop("WELCOME_MESSAGE", None)
        cfg = Config()
        assert "Добро пожаловать" in cfg.default_welcome

    def test_config_custom_welcome_from_env(self):
        """Config should use WELCOME_MESSAGE from env."""
        os.environ["WELCOME_MESSAGE"] = "Custom hello!"
        from bot.config import Config
        cfg = Config()
        assert cfg.default_welcome == "Custom hello!"

    def test_config_empty_admin_ids(self):
        """Empty ADMIN_IDS should result in empty list."""
        os.environ["ADMIN_IDS"] = ""
        from bot.config import Config
        cfg = Config()
        assert cfg.admin_ids == []

    def test_config_newline_in_welcome(self):
        """Escaped newlines in env should be converted."""
        os.environ["WELCOME_MESSAGE"] = "Line1\\nLine2"
        from bot.config import Config
        cfg = Config()
        assert "\n" in cfg.default_welcome
