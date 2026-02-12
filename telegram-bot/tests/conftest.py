"""
pytest configuration — shared fixtures.
"""

import os
import sys
import asyncio
import pytest
import pytest_asyncio

# Ensure the project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Override env vars before any module import
os.environ["BOT_TOKEN"] = "123456:ABC-DEF-test-token"
os.environ["CHANNEL_ID"] = "-1001234567890"
os.environ["ADMIN_IDS"] = "111111,222222"
os.environ["WELCOME_MESSAGE"] = "Test welcome!"
