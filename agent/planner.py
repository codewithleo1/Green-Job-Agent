"""
agent/planner.py
────────────────
Planner module — takes the user profile and creates
an ordered list of research tasks for the agent to execute.

This is what makes it an AGENT, not just a chatbot.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """A single atomic task in the agent's plan."""
    id:          int
    name:        str
    description: str
    tool:        str          # "search" | "knowledge" | "llm" | "report"
    query:       str = ""
    status:      str = "pending"   # pending | running | done | failed
    result:      dict = field(default_factory=dict)
    started_at:  str = ""
    finished_at: str = ""

    def mark_running(self):
        self.status     = "running"
        self.started_at = datetime.now().strftime("%H:%M:%S")

    def mark_done(self, result: dict):
        self.status      = "done"
        self.result      = result
        self.finished_at = datetime.now().strftime("%H:%M:%S")

    def mark_failed(self, error: str):
        self.status      = "failed"
        self.result      = {"error": error}
        self.finished_at = datetime.now().strftime("%H:%M:%S")


class GreenCareerPlanner:
    """
    Planner: Breaks the user's career goal into concrete tasks.

    Given a user profile it creates a task list covering:
      T1 — Fetch trending green jobs (search)
      T2 — Match roles to user background (knowledge + LLM)
      T3 — Identify skill gaps (LLM)
      T4 — Find free courses (knowledge + search)
      T5 — Build 7-day roadmap (LLM)
      T6 — Research salary trends (search)
      T7 — Generate PDF report (report tool)
    """

    def create_plan(self, user_profile: dict) -> list[Task]:
        name    = user_profile.get("name", "User")
        role    = user_profile.get("current_role", "professional")
        bg      = user_profile.get("background", "general")
        goal    = user_profile.get("career_goal", "green energy sector")
        year    = datetime.now().year

        tasks = [
            Task(
                id=1,
                name="Fetch Trending Green Jobs",
                description=f"Search for top green jobs trending in India in {year}",
                tool="search",
                query=f"top green jobs India {year} solar EV sustainability hiring demand"
            ),
            Task(
                id=2,
                name="Load India Green Jobs Knowledge Base",
                description="Read curated India-specific green job roles and skills",
                tool="knowledge",
                query="all_roles"
            ),
            Task(
                id=3,
                name="Match Roles to User Background",
                description=f"Use LLM to match green roles to {name}'s {bg} background",
                tool="llm",
                query=(
                    f"User: {name}. Current role: {role}. Background: {bg}. "
                    f"Career goal: {goal}. Match top 4 green job roles."
                )
            ),
            Task(
                id=4,
                name="Identify Skill Gaps",
                description=f"Analyse what skills {name} needs to transition to green jobs",
                tool="llm",
                query=f"Skill gap analysis for {bg} professional moving to {goal}"
            ),
            Task(
                id=5,
                name="Search Free Green Skills Courses",
                description="Find free and low-cost courses for green upskilling",
                tool="search",
                query=f"free green skills courses India {goal} NPTEL Coursera {year}"
            ),
            Task(
                id=6,
                name="Load Free Platforms from Knowledge Base",
                description="Retrieve curated free learning platforms for green skills",
                tool="knowledge",
                query="platforms"
            ),
            Task(
                id=7,
                name="Build 7-Day Learning Roadmap",
                description=f"Create a personalised 7-day roadmap for {name}",
                tool="llm",
                query=f"7-day roadmap for {bg} professional to start green skilling in {goal}"
            ),
            Task(
                id=8,
                name="Research Salary Trends",
                description="Search for current salary ranges for green jobs in India",
                tool="search",
                query=f"green jobs salary India {goal} {year} CTC package"
            ),
            Task(
                id=9,
                name="Generate Career Transition Report",
                description=f"Compile all findings into a PDF report for {name}",
                tool="report",
                query="generate_pdf"
            ),
        ]
        return tasks

    @staticmethod
    def display_plan(tasks: list[Task]):
        """Pretty-print the plan before execution."""
        print()
        print("   📋 AGENT PLAN — 9 tasks to complete:")
        print()
        tool_icons = {
            "search":    "🔍",
            "knowledge": "📚",
            "llm":       "🧠",
            "report":    "📄",
        }
        for t in tasks:
            icon = tool_icons.get(t.tool, "▶")
            print(f"      {icon}  Task {t.id}: {t.name}")
            print(f"           └─ Tool: {t.tool.upper()}")
        print()
