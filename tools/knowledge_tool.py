"""
tools/knowledge_tool.py
───────────────────────
Knowledge Base Tool — reads the local green_jobs_india.json file.
Gives the agent fast, structured, India-specific data without
burning search quota or waiting for the internet.
"""

import json
from pathlib import Path


class KnowledgeBaseTool:
    """
    Tool: Local Knowledge Base
    Reads curated green jobs data for India.
    No internet needed — instant results.
    """

    def __init__(self):
        base = Path(__file__).resolve().parent.parent
        kb_path = base / "data" / "green_jobs_india.json"
        with open(kb_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        print(f"      📚 [KB TOOL] Loaded: {kb_path.name}")

    # ── Public methods ────────────────────────────────────────────

    def get_all_sectors(self) -> list[str]:
        """Returns all green sector names."""
        return [s["sector"] for s in self.data["green_job_sectors"]]

    def get_sector(self, sector_name: str) -> dict | None:
        """Returns full sector data by name (fuzzy match)."""
        name = sector_name.lower()
        for sector in self.data["green_job_sectors"]:
            if name in sector["sector"].lower():
                return sector
        return None

    def get_all_roles(self) -> list[dict]:
        """Returns all job roles across all sectors."""
        roles = []
        for sector in self.data["green_job_sectors"]:
            for role in sector["top_roles"]:
                roles.append({
                    "sector": sector["sector"],
                    "role":   role
                })
        return roles

    def find_roles_for_background(self, background: str) -> list[dict]:
        """
        Returns job roles most relevant to the user's background.
        Simple keyword match — fast and explainable.
        """
        bg = background.lower()
        keyword_map = {
            "software":    ["Solar Energy Engineer", "EV Software Engineer", "Wind Resource Analyst", "ESG Analyst"],
            "it":          ["EV Software Engineer", "ESG Analyst", "Green Finance Analyst"],
            "electrical":  ["Solar PV Technician", "Solar Energy Engineer", "Wind Turbine Technician", "EV Charging Infrastructure Specialist"],
            "mechanical":  ["Wind Turbine Technician", "EV Battery Engineer", "Energy Auditor"],
            "civil":       ["Green Building Consultant", "Energy Auditor", "Solar Project Developer"],
            "finance":     ["Green Finance Analyst", "Carbon Credit Analyst", "ESG Analyst", "Solar Project Developer"],
            "mba":         ["Sustainability Manager", "Solar Project Developer", "EV Fleet Manager", "Green Finance Analyst"],
            "science":     ["ESG Analyst", "Carbon Credit Analyst", "Wind Resource Analyst"],
            "commerce":    ["ESG Analyst", "Green Finance Analyst", "Carbon Credit Analyst"],
            "hr":          ["Sustainability Manager", "ESG Analyst"],
            "marketing":   ["Sustainability Manager", "ESG Analyst"],
        }

        matched_titles = set()
        for keyword, titles in keyword_map.items():
            if keyword in bg:
                matched_titles.update(titles)

        # If no keyword match, return top roles from first 3 sectors
        if not matched_titles:
            matched_titles = {
                "Solar Energy Engineer", "ESG Analyst",
                "EV Charging Infrastructure Specialist"
            }

        results = []
        for item in self.get_all_roles():
            if item["role"]["title"] in matched_titles:
                results.append(item)
        return results

    def get_learning_platforms(self) -> list[dict]:
        """Returns all free/low-cost learning platforms."""
        return self.data["free_learning_platforms"]

    def get_platforms_for_skills(self, skills: list[str]) -> list[dict]:
        """Returns platforms relevant to a set of skills."""
        skill_text = " ".join(skills).lower()
        relevant   = []
        for platform in self.data["free_learning_platforms"]:
            courses_text = " ".join(platform["relevant_courses"]).lower()
            # Simple overlap check
            overlap = any(
                word in courses_text
                for word in skill_text.split()
                if len(word) > 3
            )
            if overlap:
                relevant.append(platform)
        return relevant if relevant else self.data["free_learning_platforms"][:4]

    def get_policy_context(self) -> dict:
        """Returns India green policy context."""
        return self.data["india_green_policy_context"]

    def format_role_summary(self, role_item: dict) -> str:
        """Returns a readable string summary of a role."""
        r = role_item["role"]
        return (
            f"Role    : {r['title']}\n"
            f"Sector  : {role_item['sector']}\n"
            f"Salary  : ₹{r['salary_range_inr']} per annum\n"
            f"Level   : {r['experience_level']}\n"
            f"Demand  : {r['demand']}\n"
            f"Skills  : {', '.join(r['skills_required'][:5])}\n"
            f"Certs   : {', '.join(r['certifications'][:3])}"
        )
