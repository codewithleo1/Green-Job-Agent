"""
agent/green_career_agent.py
────────────────────────────
Main orchestrator — the single entry point for the agent.

Usage:
    from agent.green_career_agent import GreenCareerAgent

    agent = GreenCareerAgent(api_key="YOUR_GEMINI_KEY")
    result = agent.run(user_profile={...})
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.planner  import GreenCareerPlanner
from agent.executor import GreenCareerExecutor


BANNER = """
╔══════════════════════════════════════════════════════════════╗
║       🌱  GREEN JOBS CAREER ADVISOR AGENT  🌱               ║
║       "What green skills do I need for the future?"          ║
╠══════════════════════════════════════════════════════════════╣
║  Tools  : Gemini 1.5 Flash | DuckDuckGo | KB | PDF Report   ║
║  Cost   : Rs. 0 — 100% Free API Stack                        ║
║  Powered: Edunet AI Training Program                         ║
╚══════════════════════════════════════════════════════════════╝
"""


class GreenCareerAgent:
    """
    Top-level agent that:
      1. Validates the user profile
      2. Creates a task plan (Planner)
      3. Executes the plan (Executor / Loop)
      4. Returns the report data + PDF path
    """

    def __init__(self, api_key: str):
        self.api_key  = api_key
        self.planner  = GreenCareerPlanner()
        self.executor = None  # initialised in run() so we can show the banner first

    def run(self, user_profile: dict) -> dict:
        """
        Main entry point.
        Returns dict with all results + PDF path.
        """
        start = time.time()
        print(BANNER)

        # ── Step 0: Validate input ─────────────────────────────────
        user_profile = self._validate_profile(user_profile)
        self._print_user_summary(user_profile)

        # ── Step 1: Create plan ────────────────────────────────────
        print("\n" + "=" * 64)
        print("  PHASE 1 — PLANNING")
        print("=" * 64)
        print("  Agent is analysing your profile and creating a task plan...")
        tasks = self.planner.create_plan(user_profile)
        self.planner.display_plan(tasks)

        # ── Step 2: Initialise executor ────────────────────────────
        print("=" * 64)
        print("  PHASE 2 — EXECUTION LOOP")
        print("=" * 64)
        print("  Agent is executing each task autonomously...")
        self.executor = GreenCareerExecutor(api_key=self.api_key)

        # ── Step 3: Execute all tasks ──────────────────────────────
        report_data = self.executor.run(tasks, user_profile)

        # ── Step 4: Summary ────────────────────────────────────────
        elapsed   = round(time.time() - start, 1)
        completed = sum(1 for t in tasks if t.status == "done")
        failed    = sum(1 for t in tasks if t.status == "failed")

        print()
        print("=" * 64)
        print("  PHASE 3 — COMPLETE")
        print("=" * 64)
        self._print_final_summary(report_data, tasks, elapsed, completed, failed)

        return {
            "report_data": report_data,
            "pdf_path":    self.executor.memory.get("report_path", ""),
            "tasks":       tasks,
            "elapsed_sec": elapsed,
        }

    # ── Helpers ───────────────────────────────────────────────────

    def _validate_profile(self, profile: dict) -> dict:
        defaults = {
            "name":            "Professional",
            "current_role":    "Software Engineer",
            "background":      "Software/IT",
            "experience_years": 3,
            "city":            "Bangalore",
            "career_goal":     "solar energy and sustainability",
        }
        for key, val in defaults.items():
            if key not in profile or not profile[key]:
                profile[key] = val
        return profile

    def _print_user_summary(self, user: dict):
        print(f"  👤  Name          : {user['name']}")
        print(f"  💼  Current Role  : {user['current_role']}")
        print(f"  🎓  Background    : {user['background']}")
        print(f"  📅  Experience    : {user['experience_years']} years")
        print(f"  📍  City          : {user['city']}")
        print(f"  🎯  Career Goal   : {user['career_goal']}")
        print(f"  🕒  Started at    : {datetime.now().strftime('%H:%M:%S on %d %b %Y')}")

    def _print_final_summary(self, data: dict, tasks, elapsed, completed, failed):
        print()
        print(f"  ✅  Tasks completed   : {completed}/{len(tasks)}")
        if failed:
            print(f"  ⚠️   Tasks failed      : {failed}")
        print(f"  ⏱   Total time        : {elapsed} seconds")
        print(f"  🔍  Web searches      : {self.executor.search.stats()['total_searches']}")
        print("  🧠  LLM calls         : 3  (role match + skill gap + roadmap)")
        print(f"  💼  Green roles found : {len(data.get('top_jobs', []))}")
        print(f"  📊  Skill gaps found  : {len(data.get('skill_gaps', []))}")
        print(f"  📚  Courses found     : {len(data.get('recommended_courses', []))}")
        pdf = self.executor.memory.get("report_path", "")
        if pdf:
            print(f"  📄  PDF Report        : {pdf}")
        print()
        print("  🎉  Career Advisor Agent mission complete!")
        print("=" * 64)
