"""
tests/test_auth.py
──────────────────
Smoke tests for the Auth layer.
"""

import pytest
from src.green_jobs.db import Database
from src.green_jobs.auth import Auth, AuthError


@pytest.fixture
def auth(tmp_path):
    db = Database(path=str(tmp_path / "test.db"))
    return Auth(db)


def test_register_and_login(auth):
    auth.register("suraj", "securepass")
    ok, msg = auth.login("suraj", "securepass")
    assert ok is True
    assert msg == "OK"


def test_wrong_password(auth):
    auth.register("suraj", "securepass")
    ok, msg = auth.login("suraj", "wrongpass")
    assert ok is False
    assert "Invalid" in msg


def test_unknown_user(auth):
    ok, msg = auth.login("nobody", "password123")
    assert ok is False


def test_duplicate_username_raises(auth):
    auth.register("suraj", "password123")
    with pytest.raises(AuthError):
        auth.register("suraj", "password456")


def test_username_too_short_raises(auth):
    with pytest.raises(AuthError):
        auth.register("ab", "password123")


def test_password_too_short_raises(auth):
    with pytest.raises(AuthError):
        auth.register("validuser", "abc")


def test_get_user_strips_hash(auth):
    auth.register("suraj", "password123")
    user = auth.get_user("suraj")
    assert user is not None
    assert "password_hash" not in user
    assert user["username"] == "suraj"


def test_is_admin(auth):
    auth.register("adminuser", "password123", role="admin")
    assert auth.is_admin("adminuser") is True
    auth.register("normaluser", "password123")
    assert auth.is_admin("normaluser") is False


def test_ensure_admin_exists_idempotent(auth):
    """Calling ensure_admin_exists twice should not raise."""
    auth.ensure_admin_exists("admin", "adminpass123")
    auth.ensure_admin_exists("admin", "adminpass123")
    ok, _ = auth.login("admin", "adminpass123")
    assert ok is True