"""
Tests for the database module.
"""

import os
import pytest
import pytest_asyncio
import asyncio

from bot.database import (
    init_db,
    add_user,
    get_all_user_ids,
    get_user_count,
    remove_user,
    get_setting,
    set_setting,
    save_captcha,
    get_captcha,
    delete_captcha,
    increment_captcha_attempts,
)

TEST_DB = os.path.join(os.path.dirname(__file__), "test_bot.db")


@pytest.fixture(autouse=True)
def clean_db():
    """Remove test DB before and after each test."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.mark.asyncio
async def test_init_db():
    """init_db should create the database file."""
    await init_db(TEST_DB)
    assert os.path.exists(TEST_DB)


@pytest.mark.asyncio
async def test_add_and_get_users():
    """Should add users and retrieve their IDs."""
    await init_db(TEST_DB)

    await add_user(100, "alice", "Alice", path=TEST_DB)
    await add_user(200, "bob", "Bob", path=TEST_DB)

    ids = await get_all_user_ids(path=TEST_DB)
    assert set(ids) == {100, 200}


@pytest.mark.asyncio
async def test_user_count():
    """get_user_count should return correct count."""
    await init_db(TEST_DB)

    assert await get_user_count(path=TEST_DB) == 0

    await add_user(100, "a", "A", path=TEST_DB)
    assert await get_user_count(path=TEST_DB) == 1

    await add_user(200, "b", "B", path=TEST_DB)
    assert await get_user_count(path=TEST_DB) == 2


@pytest.mark.asyncio
async def test_add_user_idempotent():
    """Adding the same user twice should not duplicate."""
    await init_db(TEST_DB)

    await add_user(100, "alice", "Alice", path=TEST_DB)
    await add_user(100, "alice", "Alice", path=TEST_DB)

    assert await get_user_count(path=TEST_DB) == 1


@pytest.mark.asyncio
async def test_remove_user():
    """remove_user should delete the user."""
    await init_db(TEST_DB)

    await add_user(100, "a", "A", path=TEST_DB)
    await add_user(200, "b", "B", path=TEST_DB)

    await remove_user(100, path=TEST_DB)
    ids = await get_all_user_ids(path=TEST_DB)
    assert ids == [200]


@pytest.mark.asyncio
async def test_remove_nonexistent_user():
    """Removing a non-existent user should not raise."""
    await init_db(TEST_DB)
    await remove_user(999, path=TEST_DB)  # Should not raise


# ── Settings ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_setting_default():
    """get_setting should return default when key doesn't exist."""
    await init_db(TEST_DB)
    val = await get_setting("nonexistent", "fallback", path=TEST_DB)
    assert val == "fallback"


@pytest.mark.asyncio
async def test_set_and_get_setting():
    """Should save and retrieve a setting."""
    await init_db(TEST_DB)

    await set_setting("welcome_message", "Hello!", path=TEST_DB)
    val = await get_setting("welcome_message", "", path=TEST_DB)
    assert val == "Hello!"


@pytest.mark.asyncio
async def test_set_setting_overwrite():
    """Setting the same key should overwrite."""
    await init_db(TEST_DB)

    await set_setting("key1", "value1", path=TEST_DB)
    await set_setting("key1", "value2", path=TEST_DB)

    val = await get_setting("key1", "", path=TEST_DB)
    assert val == "value2"


# ── Captcha Sessions ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_save_and_get_captcha():
    """Should save and retrieve a captcha session."""
    await init_db(TEST_DB)

    await save_captcha(100, "12345", path=TEST_DB)
    session = await get_captcha(100, path=TEST_DB)

    assert session is not None
    assert session["code"] == "12345"
    assert session["attempts"] == 0


@pytest.mark.asyncio
async def test_captcha_not_found():
    """get_captcha should return None for unknown user."""
    await init_db(TEST_DB)
    session = await get_captcha(999, path=TEST_DB)
    assert session is None


@pytest.mark.asyncio
async def test_increment_captcha_attempts():
    """Attempts should increment correctly."""
    await init_db(TEST_DB)

    await save_captcha(100, "12345", path=TEST_DB)
    await increment_captcha_attempts(100, path=TEST_DB)

    session = await get_captcha(100, path=TEST_DB)
    assert session["attempts"] == 1

    await increment_captcha_attempts(100, path=TEST_DB)
    session = await get_captcha(100, path=TEST_DB)
    assert session["attempts"] == 2


@pytest.mark.asyncio
async def test_delete_captcha():
    """delete_captcha should remove the session."""
    await init_db(TEST_DB)

    await save_captcha(100, "12345", path=TEST_DB)
    await delete_captcha(100, path=TEST_DB)

    session = await get_captcha(100, path=TEST_DB)
    assert session is None


@pytest.mark.asyncio
async def test_save_captcha_overwrites():
    """Saving a new captcha for the same user should overwrite."""
    await init_db(TEST_DB)

    await save_captcha(100, "11111", path=TEST_DB)
    await increment_captcha_attempts(100, path=TEST_DB)

    await save_captcha(100, "22222", path=TEST_DB)
    session = await get_captcha(100, path=TEST_DB)

    assert session["code"] == "22222"
    assert session["attempts"] == 0  # Reset on new captcha
