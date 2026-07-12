"""
src/green_jobs/auth.py
──────────────────────
Authentication layer — register, login, session helpers.

Passwords are hashed with bcrypt (work factor 12).
Plain-text passwords are never stored or logged.

Usage:
    from src.green_jobs.auth import Auth
    from src.green_jobs.db import Database

    db   = Database()
    auth = Auth(db)

    auth.register("suraj", "mypassword")
    ok, msg = auth.login("suraj", "mypassword")
"""

import logging
import bcrypt

from src.green_jobs.db import Database

logger = logging.getLogger(__name__)

# bcrypt work factor — 12 is the industry standard (slow enough to resist
# brute force, fast enough that a real user doesn't notice ~0.3s delay)
_BCRYPT_ROUNDS = 12


class AuthError(Exception):
    """Raised for all authentication failures."""


class Auth:
    """
    Handles user registration and login against the Database.
    All password operations go through bcrypt — never store plain text.
    """

    def __init__(self, db: Database) -> None:
        self._db = db

    # ── Public API ────────────────────────────────────────────────

    def register(
        self,
        username: str,
        password: str,
        role: str = "user",
    ) -> int:
        """
        Register a new user.
        Returns the new user id.
        Raises AuthError if username already exists or inputs are invalid.
        """
        username = username.strip().lower()
        self._validate_username(username)
        self._validate_password(password)

        if self._db.user_exists(username):
            raise AuthError(f"Username '{username}' is already taken.")

        hashed = _hash_password(password)
        user_id = self._db.create_user(username, hashed, role)
        logger.info("Registered new user '%s' (id=%d, role=%s)", username, user_id, role)
        return user_id

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Verify credentials.
        Returns (True, "OK") on success.
        Returns (False, reason) on failure — reason is safe to show the user.
        Never reveals whether the username exists (prevents enumeration).
        """
        username = username.strip().lower()
        user = self._db.get_user(username)

        if user is None:
            logger.warning("Login attempt for unknown user '%s'", username)
            return False, "Invalid username or password."

        if not _verify_password(password, user["password_hash"]):
            logger.warning("Failed login for user '%s'", username)
            return False, "Invalid username or password."

        logger.info("User '%s' logged in successfully", username)
        return True, "OK"

    def get_user(self, username: str) -> dict | None:
        """Return user record (without password hash) or None."""
        user = self._db.get_user(username.strip().lower())
        if user is None:
            return None
        # Strip the hash before returning to the app layer
        return {k: v for k, v in user.items() if k != "password_hash"}

    def is_admin(self, username: str) -> bool:
        """Check if user has admin role."""
        user = self._db.get_user(username.strip().lower())
        return user is not None and user.get("role") == "admin"

    def ensure_admin_exists(self, admin_username: str, admin_password: str) -> None:
        """
        Create the admin account on first run if it doesn't exist.
        Called once at app startup from .env values.
        """
        admin_username = admin_username.strip().lower()
        if not self._db.user_exists(admin_username):
            self.register(admin_username, admin_password, role="admin")
            logger.info("Admin account '%s' created", admin_username)
        else:
            logger.debug("Admin account '%s' already exists", admin_username)

    # ── Validation ────────────────────────────────────────────────

    @staticmethod
    def _validate_username(username: str) -> None:
        if len(username) < 3:
            raise AuthError("Username must be at least 3 characters.")
        if len(username) > 30:
            raise AuthError("Username must be 30 characters or fewer.")
        if not username.replace("_", "").replace("-", "").isalnum():
            raise AuthError("Username may only contain letters, numbers, - and _.")

    @staticmethod
    def _validate_password(password: str) -> None:
        if len(password) < 6:
            raise AuthError("Password must be at least 6 characters.")


# ── bcrypt helpers ────────────────────────────────────────────────

def _hash_password(plain: str) -> str:
    """Hash a plain-text password. Returns a utf-8 string."""
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=_BCRYPT_ROUNDS))
    return hashed.decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False