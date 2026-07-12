"""
agent/executor.py
-----------------
Executor - runs each task in the plan using the right tool.
This is the LOOP that makes the agent autonomous.

SDK: google-generativeai (stable, works on Windows/Mac/Linux)
Install: pip install google-generativeai
Model: gemini-2.5-flash
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# google-generativeai — stable package, works everywhere
from groq import Groq

from tools.search_tool    import WebSearchTool
from tools.knowledge_tool import KnowledgeBaseTool
from tools.report_tool    import ReportGeneratorTool
from agent.planner        import Task


class GreenCareerExecutor:
    """
    Executor: Runs the task plan produced by the Planner.
    Orchestrates all tools + Gemini LLM.
    """

    MODEL = "llama-3.3-70b-versatile"

    def __init__(self, api_key: str):
        # Configure the generativeai SDK
        self._client = Groq(api_key=api_key)
        self.search    = WebSearchTool(max_results=4, sleep_between=1.5)
        self.knowledge = KnowledgeBaseTool()
        self.reporter  = ReportGeneratorTool()
        self.memory    = {}
        print("   Executor ready (Gemini + Search + KB + Report tools loaded)")

    # ── Shared LLM call helper ────────────────────────────────────

    def _ask_llm(self, prompt: str) -> str:
        """Single wrapper for all Gemini calls."""
        resp = self._client.chat.completions.create(
        model=self.MODEL,
        messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()

    # ── Main execution loop ───────────────────────────────────────

    def run(self, tasks: list, user_profile: dict) -> dict:
        self.memory["user"]    = user_profile
        self.memory["started"] = datetime.now().strftime("%H:%M:%S")

        total = len(tasks)
        for task in tasks:
            print(f"\n   Task {task.id}/{total}: {task.name}")
            task.mark_running()
            try:
                if task.tool == "search":
                    self._run_search(task)
                elif task.tool == "knowledge":
                    self._run_knowledge(task)
                elif task.tool == "llm":
                    self._run_llm(task)
                elif task.tool == "report":
                    self._run_report(task)
                else:
                    task.mark_failed(f"Unknown tool: {task.tool}")
                    continue
            except Exception as e:
                print(f"      Task {task.id} failed: {e}")
                task.mark_failed(str(e))

        self.memory["finished"] = datetime.now().strftime("%H:%M:%S")
        return self._compile_report_data(tasks)

    # ── Tool runners ──────────────────────────────────────────────

    def _run_search(self, task: Task):
        results   = self.search.search(task.query)
        formatted = self.search.format_for_llm(results)
        task.mark_done({"raw": results, "formatted": formatted})
        self.memory[f"search_{task.id}"] = formatted
        print(f"      Stored: search_{task.id}")

    def _run_knowledge(self, task: Task):
        if task.query == "all_roles":
            roles = self.knowledge.find_roles_for_background(
                self.memory["user"].get("background", "")
            )
            formatted = "\n\n".join(
                self.knowledge.format_role_summary(r) for r in roles
            )
            task.mark_done({"roles": roles, "formatted": formatted})
            self.memory["kb_roles"]     = roles
            self.memory["kb_roles_txt"] = formatted

        elif task.query == "platforms":
            skill_keywords = self._extract_skill_keywords()
            platforms = self.knowledge.get_platforms_for_skills(skill_keywords)
            task.mark_done({"platforms": platforms})
            self.memory["kb_platforms"] = platforms

        print("      Stored KB result")

    def _run_llm(self, task: Task):
        if task.id == 3:
            result = self._llm_match_roles(task)
        elif task.id == 4:
            result = self._llm_skill_gaps(task)
        elif task.id == 7:
            result = self._llm_roadmap(task)
        else:
            text   = self._ask_llm(task.query)
            result = {"text": text}
        task.mark_done(result)
        self.memory[f"llm_{task.id}"] = result

    def _run_report(self, task: Task):
        report_data = self.memory.get("report_data", {})
        filepath    = self.reporter.generate(report_data)
        task.mark_done({"filepath": filepath})
        self.memory["report_path"] = filepath

    # ── LLM sub-tasks ─────────────────────────────────────────────

    def _llm_match_roles(self, task: Task) -> dict:
        user       = self.memory["user"]
        kb_txt     = self.memory.get("kb_roles_txt", "")
        search_txt = self.memory.get("search_1", "")

        prompt = f"""
You are a green career counsellor for India.

USER PROFILE:
- Name        : {user.get('name')}
- Current Role: {user.get('current_role')}
- Background  : {user.get('background')}
- Experience  : {user.get('experience_years')} years
- City        : {user.get('city')}
- Career Goal : {user.get('career_goal')}

KNOWLEDGE BASE ROLES:
{kb_txt}

LIVE MARKET DATA:
{search_txt}

TASK: Identify the TOP 4 green job roles best suited to this person.

Output ONLY valid JSON, no markdown fences:
{{
  "top_jobs": [
    {{
      "title": "Job Title",
      "sector": "Sector name",
      "salary": "X,XX,XXX - Y,YY,YYY",
      "demand": "Very High/High/Medium",
      "level": "Entry/Mid/Senior",
      "why_match": "One sentence why this fits their background"
    }}
  ]
}}
"""
        print("      [LLM] Matching roles...")
        text = self._ask_llm(prompt)
        text = text.replace("```json", "").replace("```", "").strip()
        try:
            parsed = json.loads(text)
            self.memory["top_jobs"] = parsed.get("top_jobs", [])
            return parsed
        except Exception:
            self.memory["top_jobs"] = []
            return {"raw": text}

    def _llm_skill_gaps(self, task: Task) -> dict:
        user     = self.memory["user"]
        top_jobs = self.memory.get("top_jobs", [])
        jobs_str = "\n".join(
            f"- {j.get('title')} ({j.get('sector')})" for j in top_jobs
        )

        prompt = f"""
You are a green skills expert.

USER: {user.get('name')}, {user.get('background')} background,
{user.get('experience_years')} years experience.

TARGET GREEN ROLES:
{jobs_str}

TASK: List the top 7 skill gaps this person needs to fill.

Output ONLY valid JSON, no markdown fences:
{{
  "skill_gaps": [
    {{
      "skill": "Skill name",
      "priority": "HIGH/MEDIUM/LOW",
      "description": "Why this skill is needed (one sentence)"
    }}
  ]
}}
"""
        print("      [LLM] Identifying skill gaps...")
        text = self._ask_llm(prompt)
        text = text.replace("```json", "").replace("```", "").strip()
        try:
            parsed = json.loads(text)
            self.memory["skill_gaps"] = parsed.get("skill_gaps", [])
            return parsed
        except Exception:
            self.memory["skill_gaps"] = []
            return {"raw": text}

    def _llm_roadmap(self, task: Task) -> dict:
        user       = self.memory["user"]
        skill_gaps = self.memory.get("skill_gaps", [])
        platforms  = self.memory.get("kb_platforms", [])
        top_jobs   = self.memory.get("top_jobs", [])

        gaps_str = "\n".join(
            f"- {g.get('skill')} ({g.get('priority')})" for g in skill_gaps[:5]
        )
        plat_str = "\n".join(
            f"- {p['platform']} ({p['cost']}): {', '.join(p['relevant_courses'][:3])}"
            for p in platforms[:4]
        )
        jobs_str = ", ".join(j.get("title", "") for j in top_jobs[:3])

        prompt = f"""
You are a green career coach.

USER: {user.get('name')}, {user.get('background')}, targeting: {jobs_str}

SKILL GAPS TO ADDRESS:
{gaps_str}

AVAILABLE FREE PLATFORMS:
{plat_str}

TASK: Create a 7-day intensive green skilling roadmap.
Each day should have a clear focus and 2-3 specific tasks.

Output ONLY valid JSON, no markdown fences:
{{
  "roadmap_7day": [
    {{
      "day": 1,
      "focus": "Short focus theme for the day",
      "tasks": "2-3 specific tasks separated by | character"
    }}
  ],
  "summary": "Two sentence overall summary of the roadmap",
  "salary_outlook": "Expected salary range after 6-12 months of green skilling (in INR)",
  "next_steps": [
    "Concrete next step 1",
    "Concrete next step 2",
    "Concrete next step 3",
    "Concrete next step 4",
    "Concrete next step 5"
  ],
  "recommended_courses": [
    {{
      "name": "Course name",
      "platform": "Platform name",
      "cost": "Free/Rs. X",
      "duration": "X weeks",
      "url": "URL if known"
    }}
  ]
}}
"""
        print("      [LLM] Building 7-day roadmap...")
        text = self._ask_llm(prompt)
        text = text.replace("```json", "").replace("```", "").strip()
        try:
            parsed = json.loads(text)
            self.memory["roadmap"]             = parsed.get("roadmap_7day", [])
            self.memory["roadmap_summary"]     = parsed.get("summary", "")
            self.memory["salary_outlook"]      = parsed.get("salary_outlook", "")
            self.memory["next_steps"]          = parsed.get("next_steps", [])
            self.memory["recommended_courses"] = parsed.get("recommended_courses", [])
            return parsed
        except Exception:
            return {"raw": text}

    # ── Helpers ───────────────────────────────────────────────────

    def _extract_skill_keywords(self) -> list:
        roles    = self.memory.get("kb_roles", [])
        keywords = []
        for item in roles[:2]:
            role = item.get("role", {})
            keywords.extend(role.get("skills_required", [])[:3])
        return keywords if keywords else ["solar", "sustainability", "EV"]

    def _compile_report_data(self, tasks: list) -> dict:
        user      = self.memory.get("user", {})
        completed = sum(1 for t in tasks if t.status == "done")
        searches  = self.search.stats()["total_searches"]

        agent_summary = (
            f"This report was autonomously generated by the Green Jobs Career Advisor Agent "
            f"for {user.get('name', 'the user')} in {datetime.now().strftime('%B %Y')}. "
            f"The agent completed {completed} tasks, performed {searches} live web searches, "
            f"and consulted a curated India-specific green jobs knowledge base. "
            f"All tools used are completely free (Gemini 2.5 Flash, DuckDuckGo, Skill India KB). "
            f"The roadmap and recommendations are personalised to a "
            f"{user.get('background', '')} professional targeting "
            f"{user.get('career_goal', 'the green sector')}."
        )

        report_data = {
            "user_name":           user.get("name", "Professional"),
            "current_role":        user.get("current_role", "N/A"),
            "experience_years":    user.get("experience_years", "N/A"),
            "background":          user.get("background", "N/A"),
            "career_goal":         user.get("career_goal", "Green sector"),
            "city":                user.get("city", "India"),
            "top_jobs":            self.memory.get("top_jobs", []),
            "skill_gaps":          self.memory.get("skill_gaps", []),
            "roadmap_7day":        self.memory.get("roadmap", []),
            "recommended_courses": self.memory.get("recommended_courses", []),
            "salary_outlook":      self.memory.get("salary_outlook", ""),
            "next_steps":          self.memory.get("next_steps", []),
            "agent_summary":       agent_summary,
        }

        self.memory["report_data"] = report_data
        return report_data
