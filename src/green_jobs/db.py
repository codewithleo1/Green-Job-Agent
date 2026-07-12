"""
src/green_jobs/db.py
────────────────────
Database layer — SQLite via sqlite-utils 4.0.

Tables:
  users     — registered accounts (hashed passwords, roles)
  runs      — one row per agent execution
  run_logs  — one row per task log line within a run

Usage:
    from src.green_jobs.db import Database
    db = Database()                        # uses DB_PATH from .env
    db = Database(path="custom.db")        # explicit path
"""

import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import sqlite_utils
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Database:
    """
    Thin wrapper around sqlite-utils.
    All methods are explicit — no magic, easy to test.
    """

    def __init__(self, path: str | None = None) -> None:
        db_path = path or os.getenv("DB_PATH", "green_jobs.db")
        self._path = Path(db_path)
        self._db = sqlite_utils.Database(self._path)
        self._ensure_schema()
        logger.info("Database ready at %s", self._path.resolve())

    # ── Schema ────────────────────────────────────────────────────

    def _ensure_schema(self) -> None:
        """Create tables if they don't exist yet."""

        if "users" not in self._db.table_names():
            self._db["users"].create({
                "id":           int,
                "username":     str,
                "password_hash": str,
                "role":         str,   # "admin" | "user"
                "created_at":   str,
            }, pk="id", not_null={"username", "password_hash", "role"})
            self._db["users"].create_index(["username"], unique=True)
            logger.info("Created table: users")

        if "runs" not in self._db.table_names():
            self._db["runs"].create({
                "id":            int,
                "username":      str,
                "user_name":     str,   # profile name (e.g. "Priya Sharma")
                "career_goal":   str,
                "background":    str,
                "city":          str,
                "experience_years": int,
                "status":        str,   # "running" | "completed" | "failed"
                "tasks_done":    int,
                "elapsed_sec":   float,
                "pdf_path":      str,
                "top_jobs":      str,   # JSON
                "skill_gaps":    str,   # JSON
                "salary_outlook": str,
                "started_at":    str,
                "finished_at":   str,
            }, pk="id")
            self._db["runs"].create_index(["username"])
            self._db["runs"].create_index(["started_at"])
            logger.info("Created table: runs")

        if "run_logs" not in self._db.table_names():
            self._db["run_logs"].create({
                "id":       int,
                "run_id":   int,
                "task_id":  int,
                "level":    str,   # "INFO" | "WARNING" | "ERROR"
                "message":  str,
                "logged_at": str,
            }, pk="id", foreign_keys=[("run_id", "runs", "id")])
            self._db["run_logs"].create_index(["run_id"])
            logger.info("Created table: run_logs")

    # ── Users ─────────────────────────────────────────────────────

    def create_user(
        self,
        username: str,
        password_hash: str,
        role: str = "user",
    ) -> int:
        """Insert a new user. Returns the new row id."""
        row = {
            "username":      username,
            "password_hash": password_hash,
            "role":          role,
            "created_at":    _now(),
        }
        self._db["users"].insert(row)  # sqlite-utils 4.0 pattern
        result = self._db.execute(
            "SELECT id FROM users WHERE username = ?", [username]
        ).fetchone()
        return result[0]

    def get_user(self, username: str) -> dict | None:
        """Return user row as dict, or None if not found."""
        result = self._db.execute(
            "SELECT * FROM users WHERE username = ?", [username]
        ).fetchone()
        if result is None:
            return None
        cols = [c[1] for c in self._db.execute(
            "PRAGMA table_info(users)"
        ).fetchall()]
        return dict(zip(cols, result))

    def user_exists(self, username: str) -> bool:
        return self.get_user(username) is not None

    def list_users(self) -> list[dict]:
        return list(self._db["users"].rows)

    # ── Runs ──────────────────────────────────────────────────────

    def start_run(self, username: str, user_profile: dict) -> int:
        """
        Insert a run row at the moment the agent starts.
        Returns the run_id to pass around during execution.
        """
        row = {
            "username":        username,
            "user_name":       user_profile.get("name", ""),
            "career_goal":     user_profile.get("career_goal", ""),
            "background":      user_profile.get("background", ""),
            "city":            user_profile.get("city", ""),
            "experience_years": int(user_profile.get("experience_years", 0)),
            "status":          "running",
            "tasks_done":      0,
            "elapsed_sec":     0.0,
            "pdf_path":        "",
            "top_jobs":        "[]",
            "skill_gaps":      "[]",
            "salary_outlook":  "",
            "started_at":      _now(),
            "finished_at":     "",
        }
        self._db["runs"].insert(row)
        run_id = self._db.execute("SELECT last_insert_rowid()").fetchone()[0]
        logger.info("Run %d started for user '%s'", run_id, username)
        return run_id

    def finish_run(self, run_id: int, result: dict, elapsed: float) -> None:
        """Update the run row when the agent finishes."""
        self._db["runs"].update(run_id, {
            "status":        "completed",
            "tasks_done":    result.get("tasks_done", 0),
            "elapsed_sec":   elapsed,
            "pdf_path":      result.get("pdf_path", ""),
            "top_jobs":      json.dumps(result.get("top_jobs", [])),
            "skill_gaps":    json.dumps(result.get("skill_gaps", [])),
            "salary_outlook": result.get("salary_outlook", ""),
            "finished_at":   _now(),
        })
        logger.info("Run %d completed in %.1fs", run_id, elapsed)

    def fail_run(self, run_id: int, error: str) -> None:
        """Mark a run as failed."""
        self._db["runs"].update(run_id, {
            "status":      "failed",
            "finished_at": _now(),
            "salary_outlook": error,  # reuse field for error message
        })
        logger.warning("Run %d failed: %s", run_id, error)

    def get_runs_for_user(self, username: str) -> list[dict]:
        """All runs for one user, newest first."""
        rows = self._db.execute(
            "SELECT * FROM runs WHERE username = ? ORDER BY started_at DESC",
            [username],
        ).fetchall()
        cols = [c[1] for c in self._db.execute(
            "PRAGMA table_info(runs)"
        ).fetchall()]
        return [dict(zip(cols, r)) for r in rows]

    def get_all_runs(self) -> list[dict]:
        """All runs across all users — for admin history view."""
        rows = self._db.execute(
            "SELECT * FROM runs ORDER BY started_at DESC"
        ).fetchall()
        cols = [c[1] for c in self._db.execute(
            "PRAGMA table_info(runs)"
        ).fetchall()]
        return [dict(zip(cols, r)) for r in rows]

    def get_run(self, run_id: int) -> dict | None:
        """Single run by id."""
        result = self._db.execute(
            "SELECT * FROM runs WHERE id = ?", [run_id]
        ).fetchone()
        if result is None:
            return None
        cols = [c[1] for c in self._db.execute(
            "PRAGMA table_info(runs)"
        ).fetchall()]
        return dict(zip(cols, result))

    # ── Run logs ──────────────────────────────────────────────────

    def log_run_event(
        self,
        run_id: int,
        message: str,
        task_id: int = 0,
        level: str = "INFO",
    ) -> None:
        """Append one log line to a run."""
        self._db["run_logs"].insert({
            "run_id":    run_id,
            "task_id":   task_id,
            "level":     level,
            "message":   message,
            "logged_at": _now(),
        })

    def get_run_logs(self, run_id: int) -> list[dict]:
        """All log lines for one run, in order."""
        rows = self._db.execute(
            "SELECT * FROM run_logs WHERE run_id = ? ORDER BY id",
            [run_id],
        ).fetchall()
        # REPLACE WITH:
        cols = [c[1] for c in self._db.execute(
            "PRAGMA table_info(run_logs)"
        ).fetchall()]
        return [dict(zip(cols, r)) for r in rows]

    # ── Stats ─────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Quick summary stats for the admin dashboard."""
        total_runs = self._db.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        completed  = self._db.execute(
            "SELECT COUNT(*) FROM runs WHERE status='completed'"
        ).fetchone()[0]
        total_users = self._db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        avg_elapsed = self._db.execute(
            "SELECT AVG(elapsed_sec) FROM runs WHERE status='completed'"
        ).fetchone()[0] or 0.0
        return {
            "total_runs":   total_runs,
            "completed":    completed,
            "failed":       total_runs - completed,
            "total_users":  total_users,
            "avg_elapsed":  round(avg_elapsed, 1),
        }


# ── Helpers ───────────────────────────────────────────────────────

def _now() -> str:
    """UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat()