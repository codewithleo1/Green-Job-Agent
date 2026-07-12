"""
tests/test_db.py
────────────────
Smoke tests for the Database layer.
Uses a temporary in-memory database — never touches green_jobs.db.
"""

import json
import pytest
from src.green_jobs.db import Database


@pytest.fixture
def db(tmp_path):
    """Fresh database for each test — isolated, no side effects."""
    return Database(path=str(tmp_path / "test.db"))


def test_schema_creates_tables(db):
    """All three tables must exist after init."""
    tables = db._db.table_names()
    assert "users" in tables
    assert "runs" in tables
    assert "run_logs" in tables


def test_create_and_get_user(db):
    user_id = db.create_user("suraj", "hashed_pw", role="admin")
    assert isinstance(user_id, int)
    assert user_id > 0

    user = db.get_user("suraj")
    assert user is not None
    assert user["username"] == "suraj"
    assert user["role"] == "admin"
    assert user["password_hash"] == "hashed_pw"


def test_user_exists(db):
    assert not db.user_exists("nobody")
    db.create_user("somebody", "pw")
    assert db.user_exists("somebody")


def test_get_user_returns_none_for_missing(db):
    assert db.get_user("ghost") is None


def test_start_and_finish_run(db):
    db.create_user("testuser", "pw")
    profile = {
        "name": "Test User",
        "career_goal": "solar energy",
        "background": "Software",
        "city": "Mumbai",
        "experience_years": 3,
    }
    run_id = db.start_run("testuser", profile)
    assert isinstance(run_id, int)

    run = db.get_run(run_id)
    assert run["status"] == "running"
    assert run["username"] == "testuser"

    db.finish_run(run_id, {
        "tasks_done": 9,
        "pdf_path": "/tmp/report.pdf",
        "top_jobs": [{"title": "Solar Engineer"}],
        "skill_gaps": [{"skill": "Python"}],
        "salary_outlook": "8-15 LPA",
    }, elapsed=42.5)

    run = db.get_run(run_id)
    assert run["status"] == "completed"
    assert run["elapsed_sec"] == 42.5
    assert run["tasks_done"] == 9
    assert json.loads(run["top_jobs"])[0]["title"] == "Solar Engineer"


def test_fail_run(db):
    db.create_user("u", "pw")
    run_id = db.start_run("u", {"name": "U", "career_goal": "x",
                                 "background": "y", "city": "z",
                                 "experience_years": 1})
    db.fail_run(run_id, "Something went wrong")
    run = db.get_run(run_id)
    assert run["status"] == "failed"


def test_log_and_retrieve_run_events(db):
    db.create_user("u2", "pw")
    run_id = db.start_run("u2", {"name": "U2", "career_goal": "x",
                                  "background": "y", "city": "z",
                                  "experience_years": 1})
    db.log_run_event(run_id, "Task 1 started", task_id=1, level="INFO")
    db.log_run_event(run_id, "Task 1 failed", task_id=1, level="WARNING")

    logs = db.get_run_logs(run_id)
    assert len(logs) == 2
    assert logs[0]["message"] == "Task 1 started"
    assert logs[1]["level"] == "WARNING"


def test_get_runs_for_user(db):
    db.create_user("u3", "pw")
    profile = {"name": "U3", "career_goal": "x", "background": "y",
               "city": "z", "experience_years": 1}
    db.start_run("u3", profile)
    db.start_run("u3", profile)

    runs = db.get_runs_for_user("u3")
    assert len(runs) == 2


def test_get_stats(db):
    stats = db.get_stats()
    assert "total_runs" in stats
    assert "total_users" in stats
    assert stats["total_runs"] == 0