"""
app.py  —  Green Jobs Career Advisor Agent
Streamlit Web UI — v3 Industry Standards Edition

Features:
  - Login / Register page (bcrypt passwords, SQLite users table)
  - Full agent UI (9-task autonomous agent)
  - History tab: users see own runs, admin sees all runs
  - Secrets loaded from .env (no hardcoded keys)
  - Run history saved to SQLite after every agent execution

Run with:
    uv run streamlit run app.py
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# ── Path setup — must happen before project imports ───────────────
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv()

from agent.planner        import GreenCareerPlanner   # noqa: E402
from agent.executor       import GreenCareerExecutor  # noqa: E402
from tools.knowledge_tool import KnowledgeBaseTool    # noqa: E402
from src.green_jobs.db    import Database              # noqa: E402
from src.green_jobs.auth  import Auth, AuthError       # noqa: E402

# ── Logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("green_jobs_app.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ── Config from .env ──────────────────────────────────────────────
PAGE_TITLE    = os.getenv("APP_TITLE",    "Green Jobs Career Advisor")
ACCENT_COLOR  = os.getenv("ACCENT_COLOR", "#2E7D32")
ORG_NAME      = os.getenv("ORG_NAME",     "Edunet AI Training Program")
ADMIN_USER    = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS    = os.getenv("ADMIN_PASSWORD", "changeme123")

# ── Database + Auth (initialised once per process) ────────────────
_db   = Database()
_auth = Auth(_db)
_auth.ensure_admin_exists(ADMIN_USER, ADMIN_PASS)

# ── Demo profiles ─────────────────────────────────────────────────
DEFAULT_PROFILES = {
    "Priya Sharma — Software Engineer → EV": {
        "name": "Priya Sharma", "current_role": "Software Engineer",
        "background": "Software/IT — 4 years Python, cloud, and web development",
        "experience_years": 4, "city": "Bangalore",
        "career_goal": "transition to EV software and battery management systems",
    },
    "Rahul Mehta — Finance Analyst → ESG": {
        "name": "Rahul Mehta", "current_role": "Financial Analyst",
        "background": "Finance/Commerce — 5 years investment banking",
        "experience_years": 5, "city": "Mumbai",
        "career_goal": "ESG analysis, green bonds, and sustainable finance",
    },
    "Anita Patel — Mechanical Eng → Wind/EV": {
        "name": "Anita Patel", "current_role": "Mechanical Engineer",
        "background": "Mechanical Engineering — 6 years manufacturing",
        "experience_years": 6, "city": "Pune",
        "career_goal": "wind turbine maintenance and EV powertrain systems",
    },
    "Sameer Khan — Civil Eng → Green Buildings": {
        "name": "Sameer Khan", "current_role": "Civil Engineer",
        "background": "Civil Engineering — 5 years construction projects",
        "experience_years": 5, "city": "Delhi",
        "career_goal": "LEED green buildings and energy auditing",
    },
    "Custom Profile": {
        "name": "", "current_role": "", "background": "",
        "experience_years": 3, "city": "", "career_goal": "",
    },
}

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{ background-color: #F1F8E9; }}
  h1, h2, h3 {{ color: {ACCENT_COLOR}; }}

  .header-banner {{
      background: linear-gradient(135deg, {ACCENT_COLOR} 0%, #1B5E20 100%);
      padding: 2rem 2.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;
  }}
  .header-banner h1 {{ color: white !important; font-size: 2.2rem; margin: 0; }}
  .header-banner p  {{ color: #C8E6C9; margin: 0.3rem 0 0 0; font-size: 1rem; }}
  .badge {{
      display: inline-block; background: #F9A825; color: #1B2A00;
      padding: 3px 12px; border-radius: 20px; font-size: 0.78rem;
      font-weight: 700; margin-right: 6px; margin-top: 8px;
  }}
  .metric-card {{
      background: white; border-left: 5px solid {ACCENT_COLOR};
      border-radius: 8px; padding: 1rem 1.2rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 0.8rem;
  }}
  .metric-card .value {{ font-size: 1.6rem; font-weight: 800; color: {ACCENT_COLOR}; }}
  .metric-card .label {{ font-size: 0.82rem; color: #666; margin-top: 2px; }}
  .job-card {{
      background: white; border-radius: 10px; padding: 1.1rem 1.3rem;
      margin-bottom: 0.9rem; border-top: 4px solid {ACCENT_COLOR};
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  }}
  .job-card h4 {{ margin: 0 0 6px 0; color: {ACCENT_COLOR}; font-size: 1.05rem; }}
  .pill-high   {{ background:#FFEBEE; color:#C62828; border:1px solid #EF9A9A;
                  padding:4px 12px; border-radius:20px; font-size:0.82rem;
                  display:inline-block; margin:3px; font-weight:600; }}
  .pill-medium {{ background:#FFF8E1; color:#E65100; border:1px solid #FFCC80;
                  padding:4px 12px; border-radius:20px; font-size:0.82rem;
                  display:inline-block; margin:3px; font-weight:600; }}
  .pill-low    {{ background:#E8F5E9; color:#2E7D32; border:1px solid #A5D6A7;
                  padding:4px 12px; border-radius:20px; font-size:0.82rem;
                  display:inline-block; margin:3px; font-weight:600; }}
  .day-card {{
      background: white; border-radius: 8px; padding: 0.9rem 1.1rem;
      margin-bottom: 0.6rem; display: flex; gap: 1rem;
      box-shadow: 0 1px 5px rgba(0,0,0,0.06);
  }}
  .day-num {{
      background: {ACCENT_COLOR}; color: white; border-radius: 6px;
      width: 52px; min-width: 52px; text-align: center;
      padding: 6px 0; font-weight: 800; font-size: 0.9rem;
  }}
  .step-box {{
      background: white; border-radius: 8px; padding: 0.8rem 1rem;
      margin-bottom: 0.5rem; display: flex; gap: 0.8rem;
      align-items: flex-start; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}
  .step-num {{
      background: #F9A825; color: #1B2A00; border-radius: 50%;
      width: 28px; min-width: 28px; height: 28px; text-align: center;
      line-height: 28px; font-weight: 800; font-size: 0.85rem;
  }}
  .course-card {{
      background: white; border-radius: 8px; padding: 0.9rem 1.1rem;
      margin-bottom: 0.6rem; border-left: 4px solid #43A047;
      box-shadow: 0 1px 5px rgba(0,0,0,0.06);
  }}
  .salary-box {{
      background: linear-gradient(135deg, {ACCENT_COLOR}, #1B5E20);
      color: white; padding: 1.2rem 1.5rem; border-radius: 10px; margin-top: 0.5rem;
  }}
  .log-line {{
      background: #263238; color: #A5D6A7; font-family: monospace;
      font-size: 0.82rem; padding: 3px 8px; border-radius: 4px; margin: 2px 0;
  }}
  .section-hdr {{
      background: {ACCENT_COLOR}; color: white; padding: 8px 16px;
      border-radius: 6px; font-weight: 700; font-size: 1rem;
      margin: 1.2rem 0 0.7rem 0;
  }}
  .history-row {{
      background: white; border-radius: 8px; padding: 0.8rem 1rem;
      margin-bottom: 0.5rem; border-left: 4px solid {ACCENT_COLOR};
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}
  .login-box {{
      max-width: 420px; margin: 3rem auto; background: white;
      border-radius: 14px; padding: 2.5rem 2rem;
      box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  }}
  .stDownloadButton > button {{
      background: {ACCENT_COLOR} !important; color: white !important;
      border-radius: 8px !important; font-weight: 700 !important;
      border: none !important; width: 100%;
  }}
  .stButton > button {{
      background: {ACCENT_COLOR}; color: white; border-radius: 8px;
      font-weight: 700; border: none; width: 100%;
  }}
  .stButton > button:hover {{ background: #1B5E20; }}
  .footer {{
      text-align: center; color: #888; font-size: 0.8rem;
      margin-top: 3rem; padding: 1rem; border-top: 1px solid #ddd;
  }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────

def pdf_download_button(pdf_path: str, label: str = "⬇️  Download PDF Report") -> None:
    try:
        with open(pdf_path, "rb") as f:
            data = f.read()
        st.download_button(
            label=label, data=data,
            file_name=Path(pdf_path).name,
            mime="application/pdf",
            use_container_width=True,
        )
    except FileNotFoundError:
        st.error(f"PDF not found: {pdf_path}")


def demand_badge(demand: str) -> str:
    colors = {
        "Very High": ("background:#E8F5E9;color:#2E7D32;border:1px solid #81C784", "🔥"),
        "High":      ("background:#FFF8E1;color:#E65100;border:1px solid #FFCC80", "⬆️"),
        "Medium":    ("background:#E3F2FD;color:#1565C0;border:1px solid #90CAF9", "→"),
    }
    style, icon = colors.get(demand, ("background:#EEE;color:#555", ""))
    return (
        f'<span style="{style};padding:3px 10px;border-radius:12px;'
        f'font-size:0.8rem;font-weight:600">{icon} {demand}</span>'
    )


def priority_pill(priority: str, skill: str) -> str:
    css = {"HIGH": "pill-high", "MEDIUM": "pill-medium", "LOW": "pill-low"}.get(priority, "pill-low")
    return f'<span class="{css}">{skill}</span>'


def status_badge(status: str) -> str:
    styles = {
        "completed": "background:#E8F5E9;color:#2E7D32;border:1px solid #81C784",
        "running":   "background:#FFF8E1;color:#E65100;border:1px solid #FFCC80",
        "failed":    "background:#FFEBEE;color:#C62828;border:1px solid #EF9A9A",
    }
    icons = {"completed": "✅", "running": "⏳", "failed": "❌"}
    style = styles.get(status, "background:#EEE;color:#555")
    icon  = icons.get(status, "")
    return (
        f'<span style="{style};padding:3px 10px;border-radius:12px;'
        f'font-size:0.8rem;font-weight:600">{icon} {status}</span>'
    )


# ─────────────────────────────────────────────────────────────────
# LOGIN / REGISTER PAGE
# ─────────────────────────────────────────────────────────────────

def show_login_page() -> None:
    """Shown when no user is logged in. Handles both login and register."""
    st.markdown(f"""
    <div class="header-banner">
      <h1>🌱 Green Jobs Career Advisor</h1>
      <p>Autonomous AI Agent — Powered by Groq LLaMA + DuckDuckGo + Skill India KB</p>
      <span class="badge">₹0 Cost</span>
      <span class="badge">Groq LLaMA 3.3</span>
      <span class="badge">{ORG_NAME}</span>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 1.4, 1])
    with col_m:
        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

        with tab_login:
            st.markdown("#### Welcome back")
            username = st.text_input("Username", key="login_user", placeholder="your username")
            password = st.text_input("Password", key="login_pass", type="password")

            if st.button("Login", key="btn_login"):
                if not username or not password:
                    st.warning("Please enter username and password.")
                else:
                    ok, msg = _auth.login(username, password)
                    if ok:
                        user = _auth.get_user(username)
                        st.session_state["logged_in"]  = True
                        st.session_state["username"]   = username.strip().lower()
                        st.session_state["user_role"]  = user.get("role", "user")
                        logger.info("Session started for '%s'", username)
                        st.rerun()
                    else:
                        st.error(msg)

        with tab_register:
            st.markdown("#### Create an account")
            new_user = st.text_input("Choose a username", key="reg_user",
                                     placeholder="letters, numbers, - or _")
            new_pass = st.text_input("Choose a password", key="reg_pass",
                                     type="password", help="Minimum 6 characters")
            new_pass2 = st.text_input("Confirm password", key="reg_pass2", type="password")

            if st.button("Register", key="btn_register"):
                if not new_user or not new_pass:
                    st.warning("Please fill in all fields.")
                elif new_pass != new_pass2:
                    st.error("Passwords do not match.")
                else:
                    try:
                        _auth.register(new_user, new_pass)
                        st.success(f"Account created! You can now log in as **{new_user.strip().lower()}**.")
                    except AuthError as e:
                        st.error(str(e))

    st.markdown(f"""
    <div class="footer">
      🌱 {PAGE_TITLE} &nbsp;|&nbsp; {ORG_NAME} &nbsp;|&nbsp; Total Cost: ₹0
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# HISTORY PAGE
# ─────────────────────────────────────────────────────────────────

def show_history_page() -> None:
    """Run history: users see own runs, admin sees all."""
    username  = st.session_state["username"]
    is_admin  = st.session_state.get("user_role") == "admin"

    st.markdown("<div class='section-hdr'>📜 Run History</div>", unsafe_allow_html=True)

    if is_admin:
        runs = _db.get_all_runs()
        st.caption(f"Admin view — showing all {len(runs)} runs across all users.")
    else:
        runs = _db.get_runs_for_user(username)
        st.caption(f"Showing your {len(runs)} run(s).")

    if not runs:
        st.info("No runs yet. Go to the Agent tab and run the career advisor!")
        return

    # Summary stats
    total     = len(runs)
    completed = sum(1 for r in runs if r["status"] == "completed")
    failed    = total - completed
    avg_time  = (
        sum(r["elapsed_sec"] for r in runs if r["status"] == "completed") / completed
        if completed else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, total,          "Total Runs"),
        (c2, completed,      "Completed"),
        (c3, failed,         "Failed"),
        (c4, f"{avg_time:.0f}s", "Avg Time"),
    ]:
        col.markdown(
            f"<div class='metric-card'><div class='value'>{val}</div>"
            f"<div class='label'>{label}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    for run in runs:
        started = run["started_at"][:16].replace("T", " ")
        elapsed = f"{run['elapsed_sec']:.0f}s" if run["elapsed_sec"] else "—"

        # Build header line
        user_col = f"&nbsp;·&nbsp; 👤 <b>{run['username']}</b>" if is_admin else ""
        badge = status_badge(run['status'])
        st.markdown(f"""
        <div class="history-row">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
            <b style="font-size:1rem;color:#1B5E20">#{run['id']} &nbsp; {run['user_name']}</b>
            {user_col} &nbsp; {badge}
            </div>
            <div style="font-size:0.8rem;color:#777">{started} &nbsp;·&nbsp; {elapsed}</div>
        </div>
        <div style="font-size:0.85rem;color:#444;margin-top:6px">
            🎯 <b>Goal:</b> {run['career_goal']}<br/>
            🏙️ {run['city']} &nbsp;·&nbsp; 🎓 {run['background'][:60]}{'…' if len(run['background']) > 60 else ''}
        </div>
        </div>
        """, unsafe_allow_html=True)

        # Expandable detail
        with st.expander(f"View details — Run #{run['id']}"):
            top_jobs   = json.loads(run["top_jobs"]  or "[]")
            skill_gaps = json.loads(run["skill_gaps"] or "[]")

            if top_jobs:
                st.markdown("**Top roles matched:**")
                for j in top_jobs:
                    st.markdown(f"- {j.get('title','')} — {j.get('sector','')} "
                                f"| ₹{j.get('salary','')} | {j.get('demand','')}")

            if skill_gaps:
                st.markdown("**Skill gaps:**")
                pills = "".join(priority_pill(g.get("priority","LOW"), g.get("skill",""))
                                for g in skill_gaps)
                st.markdown(pills, unsafe_allow_html=True)

            if run["salary_outlook"] and run["status"] == "completed":
                st.markdown(f"**Salary outlook:** {run['salary_outlook']}")

            if run["pdf_path"] and Path(run["pdf_path"]).exists():
                pdf_download_button(run["pdf_path"], "⬇️ Download PDF from this run")

            # Log lines
            logs = _db.get_run_logs(run["id"])
            if logs:
                st.markdown("**Task log:**")
                log_html = "".join(
                    f'<div class="log-line">[{entry["level"]}] T{entry["task_id"]} {entry["message"]}</div>'
                    for entry in logs
                )
                st.markdown(
                    f'<div style="background:#1E272E;padding:10px;border-radius:8px">{log_html}</div>',
                    unsafe_allow_html=True,
                )


# ─────────────────────────────────────────────────────────────────
# MAIN APP (after login)
# ─────────────────────────────────────────────────────────────────

def show_main_app() -> None:
    username = st.session_state["username"]
    is_admin = st.session_state.get("user_role") == "admin"

    # ── Header ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="header-banner">
      <h1>🌱 Green Jobs Career Advisor</h1>
      <p>Autonomous AI Agent — Powered by Gemini Free API + DuckDuckGo + Skill India KB</p>
      <span class="badge">₹0 Cost</span>
      <span class="badge">Groq LLaMA 3.3</span>
      <span class="badge">9-Task Agent</span>
      <span class="badge">{ORG_NAME}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"### 👤 {username}")
        if is_admin:
            st.markdown("🔑 **Admin**")
        if st.button("Logout", key="btn_logout"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

        st.markdown("---")
        st.markdown("## ⚙️ Configuration")

        # API Key
        st.markdown("### 🔑 Groq API Key")
        env_key = os.getenv("GROQ_API_KEY", "")
        if env_key:
            api_key = env_key
            st.success("✅ API Key loaded from .env")
        else:
            api_key = st.text_input(
                "Paste your free GROQ API key",
                type="password", placeholder="AIza...",
                help="Get your FREE key at https://console.groq.com/keys",
            )
            if api_key:
                st.success("✅ Key entered")
            else:
                st.warning("⚠️  Key required to run the agent")

        st.markdown("---")

        # Profile
        st.markdown("### 👤 User Profile")
        profile_choice = st.selectbox(
            "Choose a demo profile or enter custom:",
            options=list(DEFAULT_PROFILES.keys()), index=0,
        )
        selected = DEFAULT_PROFILES[profile_choice].copy()

        name         = st.text_input("Full Name",         value=selected["name"])
        current_role = st.text_input("Current Job Title", value=selected["current_role"])
        background   = st.text_area("Background & Skills", value=selected["background"],
                                    height=90)
        exp_years    = st.slider("Years of Experience", 0, 25, int(selected["experience_years"]))
        city         = st.text_input("City", value=selected["city"])
        career_goal  = st.text_area("Green Career Goal", value=selected["career_goal"],
                                    height=80)

        st.markdown("---")

        # KB preview
        st.markdown("### 📊 Knowledge Base")
        try:
            kb = KnowledgeBaseTool()
            st.metric("Green Sectors", len(kb.get_all_sectors()))
            st.metric("Job Roles",     len(kb.get_all_roles()))
            st.metric("Free Platforms", len(kb.get_learning_platforms()))
        except Exception:
            st.info("KB loads when agent runs")

        st.markdown("---")

        run_clicked = st.button(
            "🚀  Run Green Career Agent",
            disabled=not api_key or not name or not career_goal,
        )
        if not api_key:
            st.caption("⚠️  Enter API key to enable")
        elif not name or not career_goal:
            st.caption("⚠️  Fill name and career goal")

    # ── Page tabs ─────────────────────────────────────────────────
    page_tab_agent, page_tab_history = st.tabs(["🤖 Agent", "📜 History"])

    # ════════════════════════════════════════════════════════
    # AGENT TAB
    # ════════════════════════════════════════════════════════
    with page_tab_agent:

        # Landing state
        if not run_clicked and "results" not in st.session_state:
            c1, c2, c3 = st.columns(3)
            for col, val, label in [
                (c1, "9",   "Autonomous Tasks"),
                (c1, "3",   "Live Web Searches"),
                (c2, "3",   "Groq LLM Calls"),
                (c2, "15",  "Green Roles in KB"),
                (c3, "₹0",  "Total API Cost"),
                (c3, "PDF", "Report Generated"),
            ]:
                col.markdown(
                    f"<div class='metric-card'><div class='value'>{val}</div>"
                    f"<div class='label'>{label}</div></div>",
                    unsafe_allow_html=True,
                )
            st.markdown("---")
            st.markdown("### 🔄 Agent Workflow")
            flow_cols = st.columns(9)
            steps = [
                ("1","🔍","Search"), ("2","📚","Load KB"), ("3","🧠","Match Roles"),
                ("4","🧠","Skill Gaps"), ("5","🔍","Courses"), ("6","📚","Platforms"),
                ("7","🧠","Roadmap"), ("8","🔍","Salary"), ("9","📄","PDF"),
            ]
            for col, (num, icon, label) in zip(flow_cols, steps):
                with col:
                    st.markdown(
                        f"<div style='text-align:center;background:white;border-radius:8px;"
                        f"padding:10px 4px;box-shadow:0 1px 5px rgba(0,0,0,0.08)'>"
                        f"<div style='font-size:1.4rem'>{icon}</div>"
                        f"<div style='font-weight:700;font-size:0.8rem;color:#2E7D32'>{num}</div>"
                        f"<div style='font-size:0.7rem;color:#555'>{label}</div></div>",
                        unsafe_allow_html=True,
                    )
            st.markdown("---")
            st.info("👈  Fill in your profile in the sidebar and click **Run Green Career Agent**.")

        # ── Run the agent ─────────────────────────────────────────
        if run_clicked:
            user_profile = {
                "name": name, "current_role": current_role,
                "background": background, "experience_years": exp_years,
                "city": city, "career_goal": career_goal,
            }

            st.markdown("### 🤖 Agent Running — Live Progress")
            log_box    = st.empty()
            prog_bar   = st.progress(0)
            status_txt = st.empty()
            log_lines: list[str] = []

            def log_ui(msg: str) -> None:
                log_lines.append(msg)
                lines_html = "".join(
                    f'<div class="log-line">{line}</div>' for line in log_lines[-12:]
                )
                log_box.markdown(
                    f'<div style="background:#1E272E;padding:10px;border-radius:8px">'
                    f'{lines_html}</div>',
                    unsafe_allow_html=True,
                )

            # Start DB run record
            run_id = _db.start_run(username, user_profile)
            logger.info("Starting agent run %d for user '%s'", run_id, username)

            try:
                log_ui(f"🌱 Agent started {datetime.now().strftime('%H:%M:%S')}")
                log_ui(f"👤 {name} | Goal: {career_goal}")
                log_ui("─" * 50)
                _db.log_run_event(run_id, f"Agent started for {name}", level="INFO")

                planner = GreenCareerPlanner()
                tasks   = planner.create_plan(user_profile)
                log_ui(f"📋 Plan ready — {len(tasks)} tasks")

                executor = GreenCareerExecutor(api_key=api_key)
                executor.memory["user"] = user_profile

                task_labels = {
                    1: "Searching trending green jobs...",
                    2: "Loading Skill India knowledge base...",
                    3: "LLM matching roles to your background...",
                    4: "LLM identifying skill gaps...",
                    5: "Searching free green courses...",
                    6: "Loading free learning platforms...",
                    7: "LLM building 7-day roadmap...",
                    8: "Searching salary trends...",
                    9: "Generating PDF career report...",
                }

                start_time = time.time()

                for task in tasks:
                    label = task_labels.get(task.id, task.name)
                    log_ui(f"▶ Task {task.id}/9: {task.name}")
                    prog_bar.progress((task.id - 1) / 9)
                    status_txt.markdown(f"**Task {task.id}/9: {label}**")
                    task.mark_running()

                    try:
                        if task.tool == "search":
                            executor._run_search(task)
                        elif task.tool == "knowledge":
                            executor._run_knowledge(task)
                        elif task.tool == "llm":
                            executor._run_llm(task)
                            report_data = executor._compile_report_data(tasks)
                            executor.memory["report_data"] = report_data
                            executor._run_report(task)
                        log_ui(f"   ✅ Task {task.id} done")
                        _db.log_run_event(run_id, f"Task {task.id} completed: {task.name}",
                                          task_id=task.id, level="INFO")
                    except Exception as e:
                        task.mark_failed(str(e))
                        log_ui(f"   ⚠️ Task {task.id} warning: {e}")
                        _db.log_run_event(run_id, str(e), task_id=task.id, level="WARNING")

                elapsed = round(time.time() - start_time, 1)
                prog_bar.progress(1.0)
                status_txt.markdown("**✅ Agent complete!**")
                log_ui("─" * 50)
                log_ui(f"🎉 Done in {elapsed}s | Cost: ₹0")

                # Save to DB
                rd = executor.memory.get("report_data", {})
                _db.finish_run(run_id, {
                    "tasks_done":    sum(1 for t in tasks if t.status == "done"),
                    "pdf_path":      executor.memory.get("report_path", ""),
                    "top_jobs":      rd.get("top_jobs", []),
                    "skill_gaps":    rd.get("skill_gaps", []),
                    "salary_outlook": rd.get("salary_outlook", ""),
                }, elapsed)

                st.session_state["results"]      = rd
                st.session_state["pdf_path"]     = executor.memory.get("report_path", "")
                st.session_state["elapsed"]      = elapsed
                st.session_state["tasks"]        = tasks
                st.session_state["search_count"] = executor.search.stats()["total_searches"]

                time.sleep(0.8)
                st.rerun()

            except Exception as e:
                _db.fail_run(run_id, str(e))
                logger.error("Run %d failed: %s", run_id, e)
                st.error(f"❌ Agent error: {e}")
                st.info("Check your API key and internet connection, then try again.")

        # ── Results display ───────────────────────────────────────
        if "results" in st.session_state:
            rd      = st.session_state["results"]
            pdf     = st.session_state.get("pdf_path", "")
            elapsed = st.session_state.get("elapsed", 0)
            s_count = st.session_state.get("search_count", 3)
            tasks   = st.session_state.get("tasks", [])
            done    = sum(1 for t in tasks if t.status == "done")

            st.markdown("### 📊 Agent Results")
            m1, m2, m3, m4, m5 = st.columns(5)
            for col, val, label in [
                (m1, f"{done}/9",   "Tasks Completed"),
                (m2, str(s_count),  "Web Searches"),
                (m3, "3",           "LLM Calls"),
                (m4, f"{elapsed}s", "Time Taken"),
                (m5, "₹0",          "Total Cost"),
            ]:
                col.markdown(
                    f"<div class='metric-card'><div class='value'>{val}</div>"
                    f"<div class='label'>{label}</div></div>",
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "💼 Green Roles", "📊 Skill Gaps", "📅 7-Day Roadmap",
                "📚 Free Courses", "⚡ Next Steps", "📄 Download PDF",
            ])

            with tab1:
                st.markdown("<div class='section-hdr'>💼 Top Green Roles</div>",
                            unsafe_allow_html=True)
                for i, job in enumerate(rd.get("top_jobs", []), 1):
                    st.markdown(f"""
                    <div class="job-card">
                      <h4>{i}. {job.get('title','')} &nbsp; {demand_badge(job.get('demand',''))}</h4>
                      <table style="width:100%;font-size:0.88rem">
                        <tr>
                          <td><b>Sector</b></td><td>{job.get('sector','')}</td>
                          <td><b>Salary</b></td><td>₹{job.get('salary','')} p.a.</td>
                        </tr>
                      </table>
                      <p style="margin:8px 0 0;font-size:0.85rem;color:#555">
                        <b>Why a match:</b> {job.get('why_match','')}
                      </p>
                    </div>
                    """, unsafe_allow_html=True)

            with tab2:
                st.markdown("<div class='section-hdr'>📊 Skill Gap Analysis</div>",
                            unsafe_allow_html=True)
                gaps = rd.get("skill_gaps", [])
                pills_html = "".join(
                    priority_pill(g.get("priority","LOW"), g.get("skill","")) for g in gaps
                )
                st.markdown(pills_html, unsafe_allow_html=True)
                st.markdown("---")
                for g in gaps:
                    p = g.get("priority", "LOW")
                    color  = {"HIGH":"#FFEBEE","MEDIUM":"#FFF8E1","LOW":"#E8F5E9"}.get(p,"#F5F5F5")
                    border = {"HIGH":"#EF5350","MEDIUM":"#FFA726","LOW":"#66BB6A"}.get(p,"#ccc")
                    st.markdown(f"""
                    <div style="background:{color};border-left:5px solid {border};
                         border-radius:6px;padding:10px 14px;margin-bottom:8px">
                      <b>{g.get('skill','')}</b>
                      &nbsp;<span style="background:{border};color:white;padding:2px 8px;
                      border-radius:10px;font-size:0.75rem;font-weight:700">{p}</span><br/>
                      <span style="font-size:0.85rem;color:#444">{g.get('description','')}</span>
                    </div>
                    """, unsafe_allow_html=True)

            with tab3:
                st.markdown("<div class='section-hdr'>📅 7-Day Roadmap</div>",
                            unsafe_allow_html=True)
                shades = ["#1B5E20","#2E7D32","#388E3C","#43A047","#4CAF50","#66BB6A","#81C784"]
                for day in rd.get("roadmap_7day", []):
                    num   = day.get("day", "?")
                    shade = shades[(int(num) - 1) % len(shades)]
                    tasks_html = "".join(
                        f"<li style='margin:4px 0;font-size:0.85rem'>{t.strip()}</li>"
                        for t in day.get("tasks","").split("|") if t.strip()
                    )
                    st.markdown(f"""
                    <div class="day-card">
                      <div class="day-num" style="background:{shade}">DAY<br/>{num}</div>
                      <div>
                        <b style="color:#1B5E20">{day.get('focus','')}</b>
                        <ul style="margin:6px 0 0;padding-left:18px">{tasks_html}</ul>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            with tab4:
                st.markdown("<div class='section-hdr'>📚 Free Courses</div>",
                            unsafe_allow_html=True)
                for c in rd.get("recommended_courses", []):
                    url = c.get("url","")
                    link = f'&nbsp;<a href="{url}" target="_blank" style="color:#43A047">🔗 Open</a>' if url else ""
                    st.markdown(f"""
                    <div class="course-card">
                      <b>{c.get('name','')} {link}</b><br/>
                      <span style="font-size:0.83rem;color:#555">
                        📍 {c.get('platform','')} &nbsp;|&nbsp;
                        💰 {c.get('cost','Free')} &nbsp;|&nbsp;
                        ⏱ {c.get('duration','Self-paced')}
                      </span>
                    </div>
                    """, unsafe_allow_html=True)
                salary = rd.get("salary_outlook","")
                if salary:
                    st.markdown(
                        f"<div class='salary-box'><b>💰 Salary Outlook</b><br/>"
                        f"<span style='font-size:0.9rem'>{salary}</span></div>",
                        unsafe_allow_html=True,
                    )

            with tab5:
                st.markdown("<div class='section-hdr'>⚡ Next Steps</div>",
                            unsafe_allow_html=True)
                for i, step in enumerate(rd.get("next_steps", []), 1):
                    st.markdown(f"""
                    <div class="step-box">
                      <div class="step-num">{i}</div>
                      <div style="font-size:0.92rem;padding-top:4px">{step}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with tab6:
                st.markdown("<div class='section-hdr'>📄 Career Report PDF</div>",
                            unsafe_allow_html=True)
                if pdf and Path(pdf).exists():
                    size_kb = Path(pdf).stat().st_size // 1024
                    st.markdown(f"""
                    <div style="background:#E8F5E9;border-radius:10px;padding:1.5rem;
                         text-align:center;margin-bottom:1.2rem">
                      <div style="font-size:3rem">📄</div>
                      <div style="font-weight:700;color:#2E7D32">Green Career Report Ready!</div>
                      <div style="color:#555;font-size:0.85rem">{Path(pdf).name} | {size_kb} KB</div>
                    </div>
                    """, unsafe_allow_html=True)
                    pdf_download_button(pdf, "⬇️  Download Your PDF Career Report")
                else:
                    st.warning("PDF was not generated. Try running the agent again.")

            st.markdown("---")
            if st.button("🔄  Run Agent Again with Different Profile"):
                for key in ["results","pdf_path","elapsed","tasks","search_count"]:
                    st.session_state.pop(key, None)
                st.rerun()

    # ════════════════════════════════════════════════════════
    # HISTORY TAB
    # ════════════════════════════════════════════════════════
    with page_tab_history:
        show_history_page()

    # ── Footer ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="footer">
      🌱 {PAGE_TITLE} &nbsp;|&nbsp;
      Powered by Groq LLaMA 3.3 · DuckDuckGo · Skill India KB · fpdf2 &nbsp;|&nbsp;
      Total Cost: ₹0 &nbsp;|&nbsp; {ORG_NAME}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ROUTER — login gate
# ─────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    show_login_page()
else:
    show_main_app()
