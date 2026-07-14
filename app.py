"""
app.py — Green Jobs Career Advisor
Premium AI Career Platform — Production UI
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

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv()

from agent.planner        import GreenCareerPlanner   # noqa: E402
from agent.executor       import GreenCareerExecutor  # noqa: E402
from tools.knowledge_tool import KnowledgeBaseTool    # noqa: E402
from src.green_jobs.db    import Database              # noqa: E402
from src.green_jobs.auth  import Auth, AuthError       # noqa: E402

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(),
              logging.FileHandler("green_jobs_app.log", encoding="utf-8")])
logger = logging.getLogger(__name__)

PAGE_TITLE = os.getenv("APP_TITLE",      "Green Jobs Career Advisor")
ACCENT     = os.getenv("ACCENT_COLOR",   "#059669")
ORG_NAME   = os.getenv("ORG_NAME",       "Edunet AI Training Program")
ADMIN_USER = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "changeme123")

_db   = Database()
_auth = Auth(_db)
_auth.ensure_admin_exists(ADMIN_USER, ADMIN_PASS)

DEFAULT_PROFILES = {
    "Priya Sharma — Software → EV": {
        "name": "Priya Sharma", "current_role": "Software Engineer",
        "background": "Software/IT — 4 years Python, cloud, and web development",
        "experience_years": 4, "city": "Bangalore",
        "career_goal": "transition to EV software and battery management systems",
    },
    "Rahul Mehta — Finance → ESG": {
        "name": "Rahul Mehta", "current_role": "Financial Analyst",
        "background": "Finance/Commerce — 5 years investment banking",
        "experience_years": 5, "city": "Mumbai",
        "career_goal": "ESG analysis, green bonds, and sustainable finance",
    },
    "Anita Patel — Mechanical → Wind/EV": {
        "name": "Anita Patel", "current_role": "Mechanical Engineer",
        "background": "Mechanical Engineering — 6 years manufacturing",
        "experience_years": 6, "city": "Pune",
        "career_goal": "wind turbine maintenance and EV powertrain systems",
    },
    "Sameer Khan — Civil → Green Buildings": {
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

st.set_page_config(
    page_title=PAGE_TITLE, page_icon="🌱",
    layout="wide", initial_sidebar_state="expanded",
)

DESIGN_SYSTEM = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ═══════════════════════════════════════════════
   DESIGN TOKENS
═══════════════════════════════════════════════ */
:root {
  /* Color Palette */
  --green-50:  #f0fdf4;
  --green-100: #dcfce7;
  --green-200: #bbf7d0;
  --green-500: #22c55e;
  --green-600: #16a34a;
  --green-700: #15803d;
  --green-800: #166534;
  --green-900: #14532d;
  --emerald-500: #10b981;
  --emerald-600: #059669;
  --teal-500: #14b8a6;
  --teal-600: #0d9488;
  --slate-50:  #f8fafc;
  --slate-100: #f1f5f9;
  --slate-200: #e2e8f0;
  --slate-300: #cbd5e1;
  --slate-400: #94a3b8;
  --slate-500: #64748b;
  --slate-600: #475569;
  --slate-700: #334155;
  --slate-800: #1e293b;
  --slate-900: #0f172a;
  --orange-400: #fb923c;
  --orange-500: #f97316;
  --blue-500: #3b82f6;
  --blue-600: #2563eb;
  --purple-500: #a855f7;
  --red-500: #ef4444;
  --yellow-400: #facc15;

  /* Semantic Tokens */
  --brand:         #059669;
  --brand-light:   #10b981;
  --brand-dark:    #047857;
  --brand-bg:      #ecfdf5;
  --brand-border:  #6ee7b7;

  /* Surface */
  --surface-0:  #ffffff;
  --surface-1:  #f8fafc;
  --surface-2:  #f1f5f9;
  --surface-3:  #e2e8f0;

  /* Text */
  --text-primary:   #0f172a;
  --text-secondary: #475569;
  --text-tertiary:  #94a3b8;
  --text-inverse:   #ffffff;
  --text-brand:     #059669;

  /* Border */
  --border-light:  #f1f5f9;
  --border-medium: #e2e8f0;
  --border-strong: #cbd5e1;
  --border-brand:  #a7f3d0;

  /* Shadow */
  --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --shadow-brand: 0 4px 14px 0 rgba(5, 150, 105, 0.25);

  /* Radius */
  --radius-sm:  6px;
  --radius-md:  10px;
  --radius-lg:  14px;
  --radius-xl:  20px;
  --radius-2xl: 28px;
  --radius-full: 9999px;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;

  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-size-xs:   11px;
  --font-size-sm:   13px;
  --font-size-base: 15px;
  --font-size-lg:   17px;
  --font-size-xl:   20px;
  --font-size-2xl:  24px;
  --font-size-3xl:  30px;
  --font-size-4xl:  36px;
  --font-size-5xl:  48px;

  /* Animation */
  --transition-fast:   120ms ease;
  --transition-base:   200ms ease;
  --transition-slow:   350ms ease;
}

/* ═══════════════════════════════════════════════
   GLOBAL RESET & BASE
═══════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: var(--font-family) !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Hide all Streamlit chrome */
#MainMenu, footer, header,
.stDeployButton,
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"] { display: none !important; }

/* App background */
.stApp {
  background: var(--surface-1) !important;
  min-height: 100vh;
}

/* ═══════════════════════════════════════════════
   SIDEBAR — Premium
═══════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
  background: var(--surface-0) !important;
  border-right: 1px solid var(--border-medium) !important;
  box-shadow: var(--shadow-sm) !important;
}
section[data-testid="stSidebar"] > div:first-child {
  padding: 0 !important;
}
section[data-testid="stSidebar"] .block-container {
  padding: var(--space-6) !important;
}

/* Sidebar labels */
section[data-testid="stSidebar"] label {
  font-size: var(--font-size-sm) !important;
  font-weight: 500 !important;
  color: var(--text-secondary) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
}

/* ═══════════════════════════════════════════════
   INPUTS — Premium
═══════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
  border: 1.5px solid var(--border-strong) !important;
  border-radius: var(--radius-md) !important;
  font-family: var(--font-family) !important;
  font-size: var(--font-size-base) !important;
  background: var(--surface-0) !important;
  color: var(--text-primary) !important;
  transition: border-color var(--transition-base),
              box-shadow var(--transition-base) !important;
  padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--brand) !important;
  box-shadow: 0 0 0 3px rgba(5,150,105,0.12) !important;
  outline: none !important;
}

/* ═══════════════════════════════════════════════
   BUTTONS — Premium
═══════════════════════════════════════════════ */
.stButton > button {
  font-family: var(--font-family) !important;
  font-size: var(--font-size-sm) !important;
  font-weight: 600 !important;
  letter-spacing: 0.2px !important;
  border-radius: var(--radius-md) !important;
  transition: all var(--transition-base) !important;
  border: none !important;
  cursor: pointer !important;
  padding: 10px 20px !important;
}
.stButton > button[kind="primary"],
.stButton > button:not([kind]) {
  background: linear-gradient(135deg, var(--emerald-600), var(--teal-600)) !important;
  color: white !important;
  box-shadow: var(--shadow-brand) !important;
}
.stButton > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px 0 rgba(5,150,105,0.35) !important;
  filter: brightness(1.05) !important;
}
.stButton > button:active {
  transform: translateY(0) !important;
}
.stDownloadButton > button {
  background: linear-gradient(135deg, var(--emerald-600), var(--teal-600)) !important;
  color: white !important;
  font-weight: 600 !important;
  border-radius: var(--radius-md) !important;
  border: none !important;
  box-shadow: var(--shadow-brand) !important;
  transition: all var(--transition-base) !important;
}
.stDownloadButton > button:hover {
  transform: translateY(-1px) !important;
  filter: brightness(1.05) !important;
}

/* ═══════════════════════════════════════════════
   SLIDER
═══════════════════════════════════════════════ */
.stSlider > div > div > div > div {
  background: var(--brand) !important;
}
.stSlider [data-baseweb="slider"] [role="slider"] {
  background: var(--brand) !important;
  border: 3px solid white !important;
  box-shadow: 0 0 0 2px var(--brand) !important;
  width: 20px !important;
  height: 20px !important;
}
.stSlider [data-baseweb="slider"] div[class*="Track"] {
  background: #e2e8f0 !important;
  height: 4px !important;
}
.stSlider [data-baseweb="slider"] div[class*="Track"]:first-child {
  background: var(--brand) !important;
}
/* Remove the red default thumb color */
.stSlider > div > div > div > div > div {
  background: var(--brand) !important;
  border-color: white !important;
}

/* ═══════════════════════════════════════════════
   TABS — Premium
═══════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  background: var(--surface-0) !important;
  border-bottom: 2px solid var(--border-medium) !important;
  gap: 4px !important;
  padding: 0 !important;
  position: sticky !important;
  top: 0 !important;
  z-index: 999 !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: var(--font-family) !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  color: var(--text-secondary) !important;
  padding: 14px 28px !important;
  border-radius: 0 !important;
  border-bottom: 2px solid transparent !important;
  margin-bottom: -2px !important;
  transition: all var(--transition-base) !important;
}
.stTabs [data-baseweb="tab"]:hover {
  color: var(--brand) !important;
  background: var(--brand-bg) !important;
}
.stTabs [aria-selected="true"] {
  color: var(--brand) !important;
  border-bottom-color: var(--brand) !important;
  font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-panel"] {
  padding: var(--space-6) 0 !important;
}

/* ═══════════════════════════════════════════════
   METRICS
═══════════════════════════════════════════════ */
[data-testid="stMetric"] {
  background: var(--surface-0) !important;
  border: 1px solid var(--border-medium) !important;
  border-radius: var(--radius-lg) !important;
  padding: var(--space-5) !important;
  box-shadow: var(--shadow-xs) !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--font-family) !important;
  font-size: 28px !important;
  font-weight: 700 !important;
  color: var(--text-primary) !important;
}
[data-testid="stMetricLabel"] {
  font-size: var(--font-size-xs) !important;
  font-weight: 500 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.6px !important;
  color: var(--text-tertiary) !important;
}

/* ═══════════════════════════════════════════════
   EXPANDER
═══════════════════════════════════════════════ */
[data-testid="stExpander"] {
  border: 1px solid var(--border-medium) !important;
  border-radius: var(--radius-lg) !important;
  background: var(--surface-0) !important;
  box-shadow: var(--shadow-xs) !important;
  overflow: hidden !important;
}
[data-testid="stExpander"] summary {
  font-weight: 500 !important;
  font-size: var(--font-size-sm) !important;
  color: var(--text-secondary) !important;
  padding: 14px 16px !important;
  background: var(--surface-0) !important;
}

/* ═══════════════════════════════════════════════
   ALERTS
═══════════════════════════════════════════════ */
[data-testid="stAlert"] {
  border-radius: var(--radius-lg) !important;
  border: 1px solid !important;
  font-size: var(--font-size-sm) !important;
}

/* ═══════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════ */
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--emerald-500), var(--teal-500)) !important;
  border-radius: var(--radius-full) !important;
}
.stProgress > div > div {
  background: var(--surface-2) !important;
  border-radius: var(--radius-full) !important;
  height: 6px !important;
}

/* ═══════════════════════════════════════════════
   PREMIUM COMPONENTS
═══════════════════════════════════════════════ */

/* Platform Hero */
.platform-hero {
  background: linear-gradient(135deg, #0f172a 0%, #134e4a 50%, #064e3b 100%);
  border-radius: var(--radius-2xl);
  padding: 48px 48px 40px;
  margin-bottom: 32px;
  position: relative;
  overflow: hidden;
}
.platform-hero::before {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(16,185,129,0.15) 0%, transparent 70%);
  border-radius: 50%;
}
.platform-hero::after {
  content: '';
  position: absolute;
  bottom: -40px; left: 20%;
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(20,184,166,0.1) 0%, transparent 70%);
  border-radius: 50%;
}
.hero-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(16,185,129,0.15);
  border: 1px solid rgba(110,231,183,0.3);
  border-radius: var(--radius-full);
  padding: 4px 14px;
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: #6ee7b7;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}
.hero-title {
  font-size: clamp(24px, 4vw, 42px);
  font-weight: 800;
  color: white;
  line-height: 1.15;
  margin: 0 0 12px;
  position: relative;
  z-index: 1;
  letter-spacing: -0.5px;
}
.hero-title span { color: #34d399; }
.hero-subtitle {
  font-size: var(--font-size-base);
  color: rgba(255,255,255,0.6);
  margin: 0 0 28px;
  position: relative;
  z-index: 1;
  max-width: 560px;
  line-height: 1.6;
}
.hero-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  position: relative;
  z-index: 1;
}
.hero-badge {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: var(--radius-full);
  padding: 5px 14px;
  font-size: var(--font-size-xs);
  color: rgba(255,255,255,0.75);
  font-weight: 500;
  backdrop-filter: blur(4px);
}

/* Stat Cards */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 14px;
  margin: 24px 0;
}
.stat-card {
  background: var(--surface-0);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
  padding: 20px 18px;
  box-shadow: var(--shadow-xs);
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}
.stat-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--emerald-500), var(--teal-500));
}
.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.stat-icon {
  width: 36px; height: 36px;
  border-radius: var(--radius-md);
  background: var(--brand-bg);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
  margin-bottom: 12px;
}
.stat-value {
  font-size: 26px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 4px;
}
.stat-label {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Workflow Steps */
.workflow-grid {
  display: grid;
  grid-template-columns: repeat(9, 1fr);
  gap: 8px;
  margin: 20px 0;
}
.workflow-step {
  background: var(--surface-0);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  padding: 14px 6px;
  text-align: center;
  transition: all var(--transition-base);
  cursor: default;
}
.workflow-step:hover {
  border-color: var(--brand-border);
  background: var(--brand-bg);
  box-shadow: var(--shadow-sm);
}
.workflow-step.active {
  border-color: var(--brand);
  background: var(--brand-bg);
  box-shadow: 0 0 0 3px rgba(5,150,105,0.1);
}
.workflow-step.done {
  border-color: var(--emerald-500);
  background: var(--green-50);
}
.ws-icon { font-size: 18px; margin-bottom: 4px; }
.ws-num  { font-size: 10px; font-weight: 700; color: var(--brand); }
.ws-label{ font-size: 9px; color: var(--text-tertiary); font-weight: 500; margin-top: 2px; }

/* Job Cards — Premium */
.role-card {
  background: var(--surface-0);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-xl);
  padding: 24px 24px 20px;
  margin-bottom: 16px;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}
.role-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 4px; height: 100%;
  background: linear-gradient(180deg, var(--emerald-500), var(--teal-500));
}
.role-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
  border-color: var(--brand-border);
}
.role-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
  padding-left: 4px;
}
.role-icon {
  width: 44px; height: 44px;
  background: linear-gradient(135deg, var(--emerald-600), var(--teal-600));
  border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px;
  margin-right: 14px;
  flex-shrink: 0;
}
.role-num {
  font-size: var(--font-size-xs);
  font-weight: 700;
  color: var(--brand);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 4px;
}
.role-title {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 2px;
  letter-spacing: -0.2px;
}
.role-sector {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  font-weight: 400;
}
.role-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 14px 0;
  padding: 14px;
  background: var(--surface-1);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
}
.meta-item { display: flex; flex-direction: column; gap: 2px; }
.meta-key  { font-size: 10px; color: var(--text-tertiary); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
.meta-val  { font-size: var(--font-size-sm); color: var(--text-primary); font-weight: 600; }
.role-why  {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  padding: 12px 14px;
  background: var(--green-50);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--emerald-500);
  margin-top: 10px;
}

/* Demand Badge */
.demand-vhigh {
  display: inline-flex; align-items: center; gap: 4px;
  background: #dcfce7; color: #15803d;
  border: 1px solid #86efac;
  padding: 3px 10px; border-radius: var(--radius-full);
  font-size: 11px; font-weight: 600;
}
.demand-high {
  display: inline-flex; align-items: center; gap: 4px;
  background: #fff7ed; color: #c2410c;
  border: 1px solid #fed7aa;
  padding: 3px 10px; border-radius: var(--radius-full);
  font-size: 11px; font-weight: 600;
}
.demand-med {
  display: inline-flex; align-items: center; gap: 4px;
  background: #eff6ff; color: #1d4ed8;
  border: 1px solid #bfdbfe;
  padding: 3px 10px; border-radius: var(--radius-full);
  font-size: 11px; font-weight: 600;
}

/* Skill Gap Cards */
.skill-card {
  background: var(--surface-0);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  margin-bottom: 12px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  box-shadow: var(--shadow-xs);
  transition: all var(--transition-base);
}
.skill-card:hover { box-shadow: var(--shadow-md); }
.skill-priority-bar {
  width: 4px; min-height: 60px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}
.priority-high   { background: linear-gradient(180deg, #ef4444, #f97316); }
.priority-medium { background: linear-gradient(180deg, #f97316, #facc15); }
.priority-low    { background: linear-gradient(180deg, #22c55e, #14b8a6); }
.skill-content { flex: 1; }
.skill-name { font-size: var(--font-size-base); font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.skill-desc { font-size: var(--font-size-sm); color: var(--text-secondary); line-height: 1.5; margin-bottom: 10px; }
.skill-chip {
  display: inline-flex; align-items: center;
  padding: 3px 10px; border-radius: var(--radius-full);
  font-size: 10px; font-weight: 700;
  letter-spacing: 0.5px; text-transform: uppercase;
}
.chip-high   { background: #fef2f2; color: #b91c1c; border: 1px solid #fca5a5; }
.chip-medium { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
.chip-low    { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }

/* Roadmap Timeline */
.timeline-container { padding: 8px 0; }
.timeline-item {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  position: relative;
}
.timeline-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 26px; top: 54px;
  width: 2px; height: calc(100% - 38px);
  background: linear-gradient(180deg, var(--brand-border), transparent);
}
.timeline-day {
  flex-shrink: 0;
  width: 52px; height: 52px;
  border-radius: var(--radius-lg);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  font-weight: 800; color: white;
  font-size: 10px;
  line-height: 1.1;
  box-shadow: var(--shadow-md);
}
.timeline-body {
  flex: 1;
  background: var(--surface-0);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  box-shadow: var(--shadow-xs);
  transition: all var(--transition-base);
}
.timeline-body:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--brand-border);
}
.timeline-focus {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.timeline-tasks {
  list-style: none;
  padding: 0; margin: 0;
}
.timeline-tasks li {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.5;
  padding: 4px 0;
  padding-left: 18px;
  position: relative;
}
.timeline-tasks li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: var(--brand);
  font-weight: 600;
}

/* Course Cards */
.course-card {
  background: var(--surface-0);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-xl);
  padding: 20px;
  margin-bottom: 12px;
  box-shadow: var(--shadow-xs);
  display: flex;
  gap: 16px;
  align-items: flex-start;
  transition: all var(--transition-base);
}
.course-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--brand-border);
  transform: translateY(-1px);
}
.course-icon {
  width: 48px; height: 48px;
  background: linear-gradient(135deg, var(--emerald-600), var(--teal-600));
  border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0;
}
.course-body { flex: 1; }
.course-name {
  font-size: var(--font-size-base);
  font-weight: 600; color: var(--text-primary);
  margin-bottom: 4px;
}
.course-platform {
  font-size: var(--font-size-xs);
  color: var(--brand);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}
.course-meta {
  display: flex; flex-wrap: wrap; gap: 10px;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}
.course-meta span { display: flex; align-items: center; gap: 4px; }

/* Step Cards */
.step-card {
  background: var(--surface-0);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  margin-bottom: 10px;
  display: flex;
  gap: 14px;
  align-items: flex-start;
  box-shadow: var(--shadow-xs);
  transition: all var(--transition-base);
}
.step-card:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--brand-border);
}
.step-number {
  width: 30px; height: 30px; min-width: 30px;
  background: linear-gradient(135deg, var(--emerald-600), var(--teal-600));
  border-radius: var(--radius-full);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: white;
  box-shadow: var(--shadow-brand);
}
.step-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  padding-top: 5px;
}

/* Salary Box */
.salary-insight {
  background: linear-gradient(135deg, #064e3b 0%, #0f766e 100%);
  border-radius: var(--radius-xl);
  padding: 24px 28px;
  margin-top: 20px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}
.salary-insight::before {
  content: '₹';
  position: absolute;
  right: 24px; top: 12px;
  font-size: 80px;
  font-weight: 900;
  color: rgba(255,255,255,0.06);
  line-height: 1;
}
.salary-title {
  font-size: var(--font-size-sm);
  color: rgba(255,255,255,0.6);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 8px;
}
.salary-value {
  font-size: clamp(20px, 3vw, 32px);
  font-weight: 800;
  color: white;
  margin-bottom: 6px;
  letter-spacing: -0.5px;
}
.salary-note {
  font-size: var(--font-size-sm);
  color: rgba(255,255,255,0.5);
  line-height: 1.5;
}

/* History Cards */
.history-card {
  background: var(--surface-0);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-xl);
  padding: 20px 22px;
  margin-bottom: 12px;
  box-shadow: var(--shadow-xs);
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}
.history-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 4px;
  border-radius: var(--radius-full) 0 0 var(--radius-full);
}
.history-card.status-completed::before { background: var(--emerald-500); }
.history-card.status-failed::before    { background: var(--red-500); }
.history-card.status-running::before   { background: var(--orange-500); }
.history-card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}
.history-name {
  font-size: var(--font-size-base);
  font-weight: 700; color: var(--text-primary);
}
.history-id {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary); font-weight: 500;
}
.history-goal {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
}
.history-footer {
  display: flex; flex-wrap: wrap; gap: 10px;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid var(--border-light);
}
.history-meta-item {
  display: flex; align-items: center; gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

/* Status Badges */
.status-badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 10px; border-radius: var(--radius-full);
  font-size: 11px; font-weight: 600;
}
.status-completed { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
.status-failed    { background: #fef2f2; color: #b91c1c; border: 1px solid #fca5a5; }
.status-running   { background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }

/* Section Headers */
.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 32px 0 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-medium);
}
.section-icon {
  width: 36px; height: 36px;
  background: var(--brand-bg);
  border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}
.section-title {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.3px;
}

/* Agent Log */
.agent-terminal {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: var(--radius-xl);
  overflow: hidden;
  margin: 16px 0;
}
.terminal-header {
  background: #161b22;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid #30363d;
}
.terminal-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
}
.terminal-title {
  font-size: var(--font-size-xs);
  color: #8b949e;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-weight: 500;
}
.terminal-body {
  padding: 16px;
  min-height: 120px;
}
.log-line {
  display: block;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 12px;
  color: #3fb950;
  padding: 2px 0;
  line-height: 1.6;
}
.log-line.warn { color: #d29922; }
.log-line.info { color: #58a6ff; }

/* Login — Premium Split */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-left {
  background: linear-gradient(135deg, #0f172a 0%, #064e3b 60%, #0f766e 100%);
  border-radius: var(--radius-2xl);
  padding: 48px 40px;
  position: relative;
  overflow: hidden;
  height: 100%;
  min-height: 520px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.login-left::before {
  content: '🌱';
  position: absolute;
  font-size: 200px;
  right: -20px; bottom: -20px;
  opacity: 0.04;
  line-height: 1;
}
.login-brand {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 32px;
}
.brand-icon {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
}
.brand-name {
  font-size: var(--font-size-base);
  font-weight: 700; color: white;
}
.login-tagline {
  font-size: clamp(22px, 3vw, 32px);
  font-weight: 800;
  color: white;
  line-height: 1.2;
  letter-spacing: -0.5px;
  margin-bottom: 12px;
}
.login-tagline span { color: #34d399; }
.login-desc {
  font-size: var(--font-size-sm);
  color: rgba(255,255,255,0.55);
  line-height: 1.7;
  margin-bottom: 28px;
}
.login-feature {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 10px;
}
.feature-check {
  width: 22px; height: 22px;
  background: #059669;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; flex-shrink: 0;
  color: white;
  font-weight: 700;
}
.feature-text {
  font-size: var(--font-size-sm);
  color: rgba(255,255,255,0.88);
  font-weight: 450;
}
.login-right {
  background: var(--surface-0);
  border-radius: var(--radius-2xl);
  padding: 44px 40px;
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-medium);
}
.login-title {
  font-size: var(--font-size-3xl);
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.5px;
  margin-bottom: 6px;
}
.login-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  margin-bottom: 28px;
}

/* Sidebar User Card */
.sidebar-user {
  background: var(--surface-1);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-lg);
  padding: 14px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-avatar {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, var(--emerald-600), var(--teal-600));
  border-radius: var(--radius-full);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 700; color: white;
  flex-shrink: 0;
}
.user-name {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
}
.user-role-label {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

/* Sidebar Nav Section */
.nav-section-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-tertiary);
  margin: 16px 0 8px;
}

/* PDF Download Area */
.pdf-download-area {
  background: linear-gradient(135deg, var(--surface-1), var(--green-50));
  border: 2px dashed var(--brand-border);
  border-radius: var(--radius-xl);
  padding: 32px;
  text-align: center;
  transition: all var(--transition-base);
}
.pdf-download-area:hover {
  border-color: var(--brand);
  background: var(--brand-bg);
}
.pdf-icon { font-size: 48px; margin-bottom: 12px; }
.pdf-title {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}
.pdf-meta {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  margin-bottom: 20px;
}

/* Divider */
.divider {
  height: 1px;
  background: var(--border-medium);
  margin: 24px 0;
}

/* Pills */
.pill-high   { display:inline-flex;align-items:center;gap:4px;background:#fef2f2;color:#b91c1c;border:1px solid #fca5a5;padding:3px 10px;border-radius:var(--radius-full);font-size:11px;font-weight:600;margin:3px; }
.pill-medium { display:inline-flex;align-items:center;gap:4px;background:#fffbeb;color:#b45309;border:1px solid #fde68a;padding:3px 10px;border-radius:var(--radius-full);font-size:11px;font-weight:600;margin:3px; }
.pill-low    { display:inline-flex;align-items:center;gap:4px;background:#f0fdf4;color:#15803d;border:1px solid #bbf7d0;padding:3px 10px;border-radius:var(--radius-full);font-size:11px;font-weight:600;margin:3px; }

/* Footer */
.app-footer {
  border-top: 1px solid var(--border-medium);
  padding: 20px 0;
  margin-top: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}
.footer-brand { font-size: var(--font-size-sm); font-weight: 600; color: var(--text-secondary); }
.footer-meta  { font-size: var(--font-size-xs); color: var(--text-tertiary); }

/* Radio override */
.stRadio > div {
  display: flex !important;
  gap: 8px !important;
  flex-direction: row !important;
}
.stRadio label {
  background: var(--surface-1) !important;
  border: 1.5px solid var(--border-strong) !important;
  border-radius: var(--radius-md) !important;
  padding: 8px 16px !important;
  cursor: pointer !important;
  transition: all var(--transition-base) !important;
  font-size: var(--font-size-sm) !important;
  font-weight: 500 !important;
}
.stRadio label:has(input:checked) {
  border-color: var(--brand) !important;
  background: var(--brand-bg) !important;
  color: var(--brand) !important;
}
</style>
"""

st.markdown(DESIGN_SYSTEM, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def demand_badge(demand: str) -> str:
    if demand == "Very High":
        return '<span class="demand-vhigh">🔥 Very High</span>'
    elif demand == "High":
        return '<span class="demand-high">⬆ High</span>'
    else:
        return '<span class="demand-med">→ Medium</span>'

def status_badge_html(status: str) -> str:
    icons = {"completed": "✓", "failed": "✗", "running": "○"}
    return f'<span class="status-badge status-{status}">{icons.get(status,"·")} {status.capitalize()}</span>'

def priority_pill(priority: str, skill: str) -> str:
    css = {"HIGH":"pill-high","MEDIUM":"pill-medium","LOW":"pill-low"}.get(priority,"pill-low")
    return f'<span class="{css}">{skill}</span>'

def pdf_download_button(pdf_path: str, label: str = "⬇ Download Report") -> None:
    try:
        with open(pdf_path, "rb") as f:
            data = f.read()
        st.download_button(label=label, data=data,
                           file_name=Path(pdf_path).name,
                           mime="application/pdf",
                           use_container_width=True)
    except FileNotFoundError:
        st.error(f"PDF not found: {pdf_path}")

ROLE_ICONS = ["⚡","🌱","💡","🏗","☀","🌬","💧","🔋","📊","🌍"]
DAY_COLORS = ["#064e3b","#065f46","#047857","#059669","#10b981","#34d399","#6ee7b7"]


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────────────────────────────────────

def show_login_page() -> None:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown(f"""
<div class="login-left">
  <div>
    <div class="login-brand">
      <div class="brand-icon">🌱</div>
      <span class="brand-name">Green Jobs AI</span>
    </div>
    <div class="login-tagline">
      Your AI-powered<br/><span>Green Career</span><br/>Advisor
    </div>
    <div class="login-desc">
      Discover green career opportunities tailored to your background.
      Get personalised skill gap analysis, a 7-day learning roadmap,
      and a professional PDF career report — all in under 2 minutes.
    </div>
    <div class="login-feature">
      <div class="feature-check">✓</div>
      <span class="feature-text">9-task autonomous AI agent</span>
    </div>
    <div class="login-feature">
      <div class="feature-check">✓</div>
      <span class="feature-text">Personalised skill gap analysis</span>
    </div>
    <div class="login-feature">
      <div class="feature-check">✓</div>
      <span class="feature-text">7-day learning roadmap</span>
    </div>
    <div class="login-feature">
      <div class="feature-check">✓</div>
      <span class="feature-text">Professional PDF career report</span>
    </div>
    <div class="login-feature">
      <div class="feature-check">✓</div>
      <span class="feature-text">Groq LLaMA 3.3 · 100% Free</span>
    </div>
  </div>
  <div style="font-size:11px;color:rgba(255,255,255,0.3);margin-top:24px">
    {ORG_NAME} · Powered by Groq + DuckDuckGo
  </div>
</div>
""", unsafe_allow_html=True)

    with col_right:
        # Style the right column as a card using CSS injection
        st.markdown("""
<style>
/* Target right login column */
[data-testid="column"]:nth-child(2) > div:first-child {
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 24px !important;
  padding: 44px 40px !important;
  box-shadow: 0 20px 60px rgba(0,0,0,0.10) !important;
  min-height: 520px;
}
/* Fix radio button tabs */
[data-testid="column"]:nth-child(2) .stRadio > div {
  background: #f1f5f9;
  border-radius: 10px;
  padding: 4px;
  gap: 4px !important;
  display: flex !important;
  flex-direction: row !important;
  margin-bottom: 20px;
}
[data-testid="column"]:nth-child(2) .stRadio label {
  flex: 1;
  text-align: center;
  border-radius: 8px !important;
  border: none !important;
  background: transparent !important;
  padding: 8px 16px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  color: #64748b !important;
  cursor: pointer !important;
  transition: all 0.15s ease !important;
}
[data-testid="column"]:nth-child(2) .stRadio label:has(input:checked) {
  background: #ffffff !important;
  color: #0f172a !important;
  font-weight: 600 !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important;
}
[data-testid="column"]:nth-child(2) .stRadio label span { display: none !important; }
[data-testid="column"]:nth-child(2) .stRadio label p {
  margin: 0 !important;
  font-size: 14px !important;
}
</style>
""", unsafe_allow_html=True)

        mode = st.radio("", ["Sign In", "Create Account"],
                        horizontal=True, label_visibility="collapsed",
                        key="login_mode")

        if mode == "Sign In":
            st.markdown("""
<div style="margin-bottom:24px">
  <div style="font-size:28px;font-weight:800;color:#0f172a;letter-spacing:-0.5px;margin-bottom:4px">Welcome back</div>
  <div style="font-size:14px;color:#94a3b8">Sign in to your account to continue</div>
</div>
""", unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;font-weight:500;color:#475569;margin-bottom:4px">Username</p>', unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter your username",
                                     key="li_user", label_visibility="collapsed")
            st.markdown('<p style="font-size:13px;font-weight:500;color:#475569;margin:12px 0 4px">Password</p>', unsafe_allow_html=True)
            password = st.text_input("Password", type="password",
                                     placeholder="Enter your password",
                                     key="li_pass", label_visibility="collapsed")
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("Sign In →", use_container_width=True, key="btn_login"):
                if not username or not password:
                    st.warning("Please enter your username and password.")
                else:
                    ok, msg = _auth.login(username, password)
                    if ok:
                        user = _auth.get_user(username)
                        st.session_state.update({
                            "logged_in": True,
                            "username":  username.strip().lower(),
                            "user_role": user.get("role", "user"),
                        })
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.markdown("""
<div style="margin-bottom:24px">
  <div style="font-size:28px;font-weight:800;color:#0f172a;letter-spacing:-0.5px;margin-bottom:4px">Get started</div>
  <div style="font-size:14px;color:#94a3b8">Create your free account today</div>
</div>
""", unsafe_allow_html=True)
            st.markdown('<p style="font-size:13px;font-weight:500;color:#475569;margin-bottom:4px">Username</p>', unsafe_allow_html=True)
            new_user  = st.text_input("Username", placeholder="Choose a username (min 3 chars)",
                                      key="reg_user", label_visibility="collapsed")
            st.markdown('<p style="font-size:13px;font-weight:500;color:#475569;margin:12px 0 4px">Password</p>', unsafe_allow_html=True)
            new_pass  = st.text_input("Password", type="password",
                                      placeholder="Choose a password (min 6 chars)",
                                      key="reg_pass", label_visibility="collapsed")
            st.markdown('<p style="font-size:13px;font-weight:500;color:#475569;margin:12px 0 4px">Confirm Password</p>', unsafe_allow_html=True)
            new_pass2 = st.text_input("Confirm Password", type="password",
                                      placeholder="Re-enter your password",
                                      key="reg_pass2", label_visibility="collapsed")
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("Create Account →", use_container_width=True, key="btn_reg"):
                if not new_user or not new_pass:
                    st.warning("Please fill in all fields.")
                elif new_pass != new_pass2:
                    st.error("Passwords do not match.")
                else:
                    try:
                        _auth.register(new_user, new_pass)
                        st.success(f"✓ Account created! Sign in as **{new_user.strip().lower()}**")
                    except AuthError as e:
                        st.error(str(e))

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
<div class="app-footer">
  <span class="footer-brand">🌱 {PAGE_TITLE}</span>
  <span class="footer-meta">Powered by Groq LLaMA 3.3 · DuckDuckGo · fpdf2 · Cost: ₹0</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HISTORY PAGE
# ─────────────────────────────────────────────────────────────────────────────

def show_history_page() -> None:
    username = st.session_state["username"]
    is_admin = st.session_state.get("user_role") == "admin"

    st.markdown("""
<div class="section-header">
  <div class="section-icon">📜</div>
  <span class="section-title">Run History</span>
</div>
""", unsafe_allow_html=True)

    runs = _db.get_all_runs() if is_admin else _db.get_runs_for_user(username)

    if is_admin:
        st.caption(f"Admin view — showing all {len(runs)} runs across all users")
    else:
        st.caption(f"Showing your {len(runs)} run(s)")

    if not runs:
        st.info("🌱 No runs yet. Go to the Agent tab and run the career advisor!")
        return

    total     = len(runs)
    completed = sum(1 for r in runs if r["status"] == "completed")
    failed    = total - completed
    avg_time  = (sum(r["elapsed_sec"] for r in runs if r["status"] == "completed")
                 / completed if completed else 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Runs",  total)
    c2.metric("Completed",   completed)
    c3.metric("Failed",      failed)
    c4.metric("Avg Time",    f"{avg_time:.0f}s")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    for run in runs:
        started  = run["started_at"][:16].replace("T", " ")
        elapsed  = f"{run['elapsed_sec']:.0f}s" if run["elapsed_sec"] else "—"
        status   = run["status"]
        badge    = status_badge_html(status)
        user_col = f'<span style="font-size:11px;color:var(--text-tertiary)"> · {run["username"]}</span>' if is_admin else ""

        st.markdown(f"""
<div class="history-card status-{status}">
  <div class="history-header">
    <div>
      <div class="history-id">RUN #{run['id']}{user_col}</div>
      <div class="history-name">{run['user_name']}</div>
    </div>
    {badge}
  </div>
  <div class="history-goal">🎯 {run['career_goal']}</div>
  <div class="history-footer">
    <span class="history-meta-item">🏙 {run['city']}</span>
    <span class="history-meta-item">🕐 {started}</span>
    <span class="history-meta-item">⏱ {elapsed}</span>
    <span class="history-meta-item">✓ {run.get('tasks_done',0)}/9 tasks</span>
  </div>
</div>
""", unsafe_allow_html=True)

        with st.expander(f"View details — Run #{run['id']}"):
            top_jobs   = json.loads(run["top_jobs"]   or "[]")
            skill_gaps = json.loads(run["skill_gaps"] or "[]")

            if top_jobs:
                st.markdown("**Top roles matched:**")
                for j in top_jobs:
                    st.markdown(f"- **{j.get('title','')}** — {j.get('sector','')} "
                                f"| ₹{j.get('salary','')} | {j.get('demand','')}")

            if skill_gaps:
                st.markdown("**Skill gaps:**")
                pills = "".join(priority_pill(g.get("priority","LOW"), g.get("skill",""))
                                for g in skill_gaps)
                st.markdown(pills, unsafe_allow_html=True)

            if run["salary_outlook"] and status == "completed":
                st.markdown(f"**Salary outlook:** {run['salary_outlook']}")

            if run["pdf_path"] and Path(run["pdf_path"]).exists():
                pdf_download_button(run["pdf_path"], "⬇ Download PDF from this run")

            logs = _db.get_run_logs(run["id"])
            if logs:
                st.markdown("**Agent log:**")
                lines = "".join(
                    f'<span class="log-line {"warn" if lg["level"]=="WARNING" else "info" if lg["level"]=="INFO" else ""}">'
                    f'[T{lg["task_id"]}] {lg["message"]}</span>'
                    for lg in logs
                )
                st.markdown(
                    f'<div class="agent-terminal">'
                    f'<div class="terminal-header">'
                    f'<div class="terminal-dot" style="background:#ff5f57"></div>'
                    f'<div class="terminal-dot" style="background:#ffbd2e"></div>'
                    f'<div class="terminal-dot" style="background:#28c840"></div>'
                    f'<span class="terminal-title">agent log · run #{run["id"]}</span>'
                    f'</div><div class="terminal-body">{lines}</div></div>',
                    unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

def show_main_app() -> None:
    username = st.session_state["username"]
    is_admin = st.session_state.get("user_role") == "admin"
    initials = username[0].upper()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        # User card
        role_label = "Administrator" if is_admin else "Member"
        st.markdown(f"""
<div class="sidebar-user">
  <div class="user-avatar">{initials}</div>
  <div>
    <div class="user-name">{username}</div>
    <div class="user-role-label">{role_label}</div>
  </div>
</div>
""", unsafe_allow_html=True)

        if st.button("Sign Out", key="btn_logout"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

        st.markdown('<div class="nav-section-label">Configuration</div>',
                    unsafe_allow_html=True)

        env_key = os.getenv("GROQ_API_KEY", "")
        if env_key:
            api_key = env_key
            st.success("✓ Groq API Key configured")
        else:
            api_key = st.text_input("Groq API Key", type="password",
                                    placeholder="gsk_...",
                                    help="Get free key: console.groq.com/keys")
            if api_key:
                st.success("✓ Key entered")
            else:
                st.warning("API key required")

        st.markdown('<div class="nav-section-label">User Profile</div>',
                    unsafe_allow_html=True)

        profile_choice = st.selectbox("Demo Profile",
                                      options=list(DEFAULT_PROFILES.keys()),
                                      index=0, label_visibility="collapsed")
        selected = DEFAULT_PROFILES[profile_choice].copy()

        name         = st.text_input("Full Name",         value=selected["name"])
        current_role = st.text_input("Current Role",      value=selected["current_role"])
        background   = st.text_area("Background",         value=selected["background"], height=80)
        exp_years    = st.slider("Experience (years)",    0, 25, int(selected["experience_years"]))
        city         = st.text_input("City",              value=selected["city"])
        career_goal  = st.text_area("Career Goal",        value=selected["career_goal"], height=70)

        st.markdown('<div class="nav-section-label">Knowledge Base</div>',
                    unsafe_allow_html=True)
        try:
            kb = KnowledgeBaseTool()
            kc1, kc2, kc3 = st.columns(3)
            kc1.metric("Sectors", len(kb.get_all_sectors()))
            kc2.metric("Roles",   len(kb.get_all_roles()))
            kc3.metric("Platforms", len(kb.get_learning_platforms()))
        except Exception:
            st.caption("KB loads on agent run")

        st.markdown("---")

        run_clicked = st.button(
            "🚀 Run Career Agent",
            disabled=not api_key or not name or not career_goal,
            use_container_width=True,
        )
        if not api_key:
            st.caption("⚠ Add API key to enable")
        elif not name or not career_goal:
            st.caption("⚠ Fill name and career goal")

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="platform-hero">
  <div class="hero-tag">✦ AI-Powered Career Platform</div>
  <div class="hero-title">
    Find Your Path in the<br/><span>Green Economy</span>
  </div>
  <div class="hero-subtitle">
    An autonomous AI agent that analyses your background, identifies skill gaps,
    builds a personalised learning roadmap, and generates a professional
    career transition report — in under 2 minutes.
  </div>
  <div class="hero-badges">
    <span class="hero-badge">₹0 Cost</span>
    <span class="hero-badge">Groq LLaMA 3.3</span>
    <span class="hero-badge">9-Task Agent</span>
    <span class="hero-badge">DuckDuckGo Search</span>
    <span class="hero-badge">Skill India KB</span>
    <span class="hero-badge">{ORG_NAME}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_agent, tab_history = st.tabs(["🤖 Career Agent", "📜 History"])

    # ════════════════════════════════════════════════════════════════════════
    # AGENT TAB
    # ════════════════════════════════════════════════════════════════════════
    with tab_agent:

        if not run_clicked and "results" not in st.session_state:
            # Stats grid
            st.markdown("""
<div class="stat-grid">
  <div class="stat-card">
    <div class="stat-icon">🤖</div>
    <div class="stat-value">9</div>
    <div class="stat-label">Autonomous Tasks</div>
  </div>
  <div class="stat-card">
    <div class="stat-icon">🔍</div>
    <div class="stat-value">3</div>
    <div class="stat-label">Live Web Searches</div>
  </div>
  <div class="stat-card">
    <div class="stat-icon">🧠</div>
    <div class="stat-value">3</div>
    <div class="stat-label">LLM Reasoning Calls</div>
  </div>
  <div class="stat-card">
    <div class="stat-icon">💼</div>
    <div class="stat-value">15</div>
    <div class="stat-label">Green Roles in KB</div>
  </div>
  <div class="stat-card">
    <div class="stat-icon">🎓</div>
    <div class="stat-value">8</div>
    <div class="stat-label">Free Platforms</div>
  </div>
  <div class="stat-card">
    <div class="stat-icon">💰</div>
    <div class="stat-value">₹0</div>
    <div class="stat-label">Total API Cost</div>
  </div>
</div>
""", unsafe_allow_html=True)

            # Workflow
            st.markdown("""
<div class="section-header">
  <div class="section-icon">🔄</div>
  <span class="section-title">Agent Workflow</span>
</div>
<div class="workflow-grid">
  <div class="workflow-step"><div class="ws-icon">🔍</div><div class="ws-num">1</div><div class="ws-label">Search Jobs</div></div>
  <div class="workflow-step"><div class="ws-icon">📚</div><div class="ws-num">2</div><div class="ws-label">Load KB</div></div>
  <div class="workflow-step"><div class="ws-icon">🧠</div><div class="ws-num">3</div><div class="ws-label">Match Roles</div></div>
  <div class="workflow-step"><div class="ws-icon">📊</div><div class="ws-num">4</div><div class="ws-label">Skill Gaps</div></div>
  <div class="workflow-step"><div class="ws-icon">🔍</div><div class="ws-num">5</div><div class="ws-label">Find Courses</div></div>
  <div class="workflow-step"><div class="ws-icon">📚</div><div class="ws-num">6</div><div class="ws-label">Platforms</div></div>
  <div class="workflow-step"><div class="ws-icon">🗓</div><div class="ws-num">7</div><div class="ws-label">Roadmap</div></div>
  <div class="workflow-step"><div class="ws-icon">💰</div><div class="ws-num">8</div><div class="ws-label">Salary Data</div></div>
  <div class="workflow-step"><div class="ws-icon">📄</div><div class="ws-num">9</div><div class="ws-label">PDF Report</div></div>
</div>
""", unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.info("👈 Fill in your profile in the sidebar, then click **Run Career Agent**.")

        # ── Run ───────────────────────────────────────────────────────────────
        if run_clicked:
            user_profile = {
                "name": name, "current_role": current_role,
                "background": background, "experience_years": exp_years,
                "city": city, "career_goal": career_goal,
            }

            st.markdown("""
<div class="section-header">
  <div class="section-icon">🤖</div>
  <span class="section-title">Agent Running</span>
</div>
""", unsafe_allow_html=True)

            prog_col, stat_col = st.columns([2, 1])
            with prog_col:
                prog_bar = st.progress(0)
                status_txt = st.empty()
            with stat_col:
                elapsed_txt = st.empty()

            log_box   = st.empty()
            log_lines: list[str] = []

            def log_ui(msg: str, level: str = "") -> None:
                log_lines.append((msg, level))
                html = "".join(f'<span class="log-line {c}">{m}</span>'
                               for m, c in log_lines[-14:])
                log_box.markdown(
                    f'<div class="agent-terminal">'
                    f'<div class="terminal-header">'
                    f'<div class="terminal-dot" style="background:#ff5f57"></div>'
                    f'<div class="terminal-dot" style="background:#ffbd2e"></div>'
                    f'<div class="terminal-dot" style="background:#28c840"></div>'
                    f'<span class="terminal-title">green-jobs-agent · running</span>'
                    f'</div><div class="terminal-body">{html}</div></div>',
                    unsafe_allow_html=True)

            run_id = _db.start_run(username, user_profile)
            try:
                log_ui(f"[{datetime.now().strftime('%H:%M:%S')}] Agent initialised")
                log_ui(f"[init] Profile: {name} · {career_goal[:50]}")
                _db.log_run_event(run_id, f"Agent started for {name}")

                planner = GreenCareerPlanner()
                tasks   = planner.create_plan(user_profile)
                log_ui(f"[plan] {len(tasks)} tasks scheduled")

                executor = GreenCareerExecutor(api_key=api_key)
                executor.memory["user"] = user_profile

                task_labels = {
                    1: "Fetching live green job market data...",
                    2: "Loading Skill India knowledge base...",
                    3: "AI matching top roles to your background...",
                    4: "AI analysing your skill gaps...",
                    5: "Searching free upskilling courses...",
                    6: "Loading learning platforms...",
                    7: "AI building your 7-day learning roadmap...",
                    8: "Researching salary trends...",
                    9: "Generating your PDF career report...",
                }

                start_time = time.time()
                for task in tasks:
                    pct = (task.id - 1) / 9
                    prog_bar.progress(pct)
                    status_txt.markdown(f"**Task {task.id}/9** — {task_labels.get(task.id, task.name)}")
                    elapsed_txt.metric("Elapsed", f"{round(time.time()-start_time,1)}s")
                    log_ui(f"[task {task.id}] {task.name}")
                    task.mark_running()

                    try:
                        if task.tool == "search":
                            executor._run_search(task)
                        elif task.tool == "knowledge":
                            executor._run_knowledge(task)
                        elif task.tool == "llm":
                            executor._run_llm(task)
                        elif task.tool == "report":
                            report_data = executor._compile_report_data(tasks)
                            executor.memory["report_data"] = report_data
                            executor._run_report(task)
                        log_ui(f"[task {task.id}] ✓ done", "info")
                        _db.log_run_event(run_id, f"Task {task.id} completed: {task.name}",
                                          task_id=task.id, level="INFO")
                    except Exception as e:
                        task.mark_failed(str(e))
                        log_ui(f"[task {task.id}] ⚠ {str(e)[:80]}", "warn")
                        _db.log_run_event(run_id, str(e), task_id=task.id, level="WARNING")

                elapsed = round(time.time() - start_time, 1)
                prog_bar.progress(1.0)
                status_txt.markdown("**✓ Agent complete!**")
                elapsed_txt.metric("Total Time", f"{elapsed}s")
                log_ui(f"[done] Completed in {elapsed}s · Cost: ₹0", "info")

                rd = executor.memory.get("report_data", {})
                _db.finish_run(run_id, {
                    "tasks_done":     sum(1 for t in tasks if t.status == "done"),
                    "pdf_path":       executor.memory.get("report_path", ""),
                    "top_jobs":       rd.get("top_jobs", []),
                    "skill_gaps":     rd.get("skill_gaps", []),
                    "salary_outlook": rd.get("salary_outlook", ""),
                }, elapsed)

                st.session_state.update({
                    "results":      rd,
                    "pdf_path":     executor.memory.get("report_path", ""),
                    "elapsed":      elapsed,
                    "tasks":        tasks,
                    "search_count": executor.search.stats()["total_searches"],
                })
                time.sleep(0.5)
                st.rerun()

            except Exception as e:
                _db.fail_run(run_id, str(e))
                st.error(f"Agent error: {e}")
                st.info("Check your API key and internet connection, then try again.")

        # ── Results ───────────────────────────────────────────────────────────
        if "results" in st.session_state:
            rd      = st.session_state["results"]
            pdf     = st.session_state.get("pdf_path", "")
            elapsed = st.session_state.get("elapsed", 0)
            s_count = st.session_state.get("search_count", 3)
            tasks   = st.session_state.get("tasks", [])
            done    = sum(1 for t in tasks if t.status == "done")

            # Results stats
            st.markdown(f"""
<div class="stat-grid" style="grid-template-columns:repeat(5,1fr)">
  <div class="stat-card"><div class="stat-icon">✓</div><div class="stat-value">{done}/9</div><div class="stat-label">Tasks Done</div></div>
  <div class="stat-card"><div class="stat-icon">🔍</div><div class="stat-value">{s_count}</div><div class="stat-label">Searches</div></div>
  <div class="stat-card"><div class="stat-icon">🧠</div><div class="stat-value">3</div><div class="stat-label">LLM Calls</div></div>
  <div class="stat-card"><div class="stat-icon">⏱</div><div class="stat-value">{elapsed}s</div><div class="stat-label">Time Taken</div></div>
  <div class="stat-card"><div class="stat-icon">💰</div><div class="stat-value">₹0</div><div class="stat-label">API Cost</div></div>
</div>
""", unsafe_allow_html=True)

            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "💼 Career Matches", "📊 Skill Gaps",
                "📅 Learning Roadmap", "🎓 Free Courses",
                "⚡ Next Steps", "📄 PDF Report",
            ])

            # ── Tab 1: Career Matches ─────────────────────────────────────────
            with tab1:
                st.markdown("""
<div class="section-header">
  <div class="section-icon">💼</div>
  <span class="section-title">Your Top Career Matches</span>
</div>
""", unsafe_allow_html=True)
                for i, job in enumerate(rd.get("top_jobs", []), 1):
                    icon  = ROLE_ICONS[(i - 1) % len(ROLE_ICONS)]
                    badge = demand_badge(job.get("demand", ""))
                    st.markdown(f"""
<div class="role-card">
  <div class="role-header">
    <div style="display:flex;align-items:flex-start;gap:14px">
      <div class="role-icon">{icon}</div>
      <div>
        <div class="role-num">Match #{i}</div>
        <div class="role-title">{job.get('title','')}</div>
        <div class="role-sector">{job.get('sector','')}</div>
      </div>
    </div>
    {badge}
  </div>
  <div class="role-meta">
    <div class="meta-item">
      <span class="meta-key">Salary</span>
      <span class="meta-val">₹{job.get('salary','')} p.a.</span>
    </div>
    <div class="meta-item">
      <span class="meta-key">Level</span>
      <span class="meta-val">{job.get('level','')}</span>
    </div>
    <div class="meta-item">
      <span class="meta-key">Demand</span>
      <span class="meta-val">{job.get('demand','')}</span>
    </div>
  </div>
  <div class="role-why">
    <strong>Why this matches you:</strong> {job.get('why_match','')}
  </div>
</div>
""", unsafe_allow_html=True)

            # ── Tab 2: Skill Gaps ─────────────────────────────────────────────
            with tab2:
                st.markdown("""
<div class="section-header">
  <div class="section-icon">📊</div>
  <span class="section-title">Skill Gap Analysis</span>
</div>
""", unsafe_allow_html=True)
                gaps = rd.get("skill_gaps", [])
                if gaps:
                    pills = "".join(priority_pill(g.get("priority","LOW"), g.get("skill",""))
                                    for g in gaps)
                    st.markdown(pills + "<br/><br/>", unsafe_allow_html=True)
                    for g in gaps:
                        p   = g.get("priority", "LOW")
                        bar = {"HIGH":"priority-high","MEDIUM":"priority-medium",
                               "LOW":"priority-low"}.get(p,"priority-low")
                        chip= {"HIGH":"chip-high","MEDIUM":"chip-medium",
                               "LOW":"chip-low"}.get(p,"chip-low")
                        st.markdown(f"""
<div class="skill-card">
  <div class="skill-priority-bar {bar}"></div>
  <div class="skill-content">
    <div class="skill-name">{g.get('skill','')}</div>
    <div class="skill-desc">{g.get('description','')}</div>
    <span class="skill-chip {chip}">{p} PRIORITY</span>
  </div>
</div>
""", unsafe_allow_html=True)

            # ── Tab 3: Roadmap ────────────────────────────────────────────────
            with tab3:
                st.markdown("""
<div class="section-header">
  <div class="section-icon">📅</div>
  <span class="section-title">Your 7-Day Learning Roadmap</span>
</div>
<div class="timeline-container">
""", unsafe_allow_html=True)
                for day in rd.get("roadmap_7day", []):
                    num   = day.get("day", "?")
                    shade = DAY_COLORS[(int(num) - 1) % len(DAY_COLORS)]
                    raw   = day.get("tasks", "")
                    items = [t.strip() for t in raw.split("|") if t.strip()]
                    if not items and raw:
                        items = [raw]
                    tasks_html = "".join(f"<li>{t}</li>" for t in items)
                    st.markdown(f"""
<div class="timeline-item">
  <div class="timeline-day" style="background:linear-gradient(135deg,{shade},{shade}99)">
    <span style="font-size:8px;opacity:0.8">DAY</span>
    <span style="font-size:18px">{num}</span>
  </div>
  <div class="timeline-body">
    <div class="timeline-focus">{day.get('focus','')}</div>
    <ul class="timeline-tasks">{tasks_html}</ul>
  </div>
</div>
""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Tab 4: Courses ────────────────────────────────────────────────
            with tab4:
                st.markdown("""
<div class="section-header">
  <div class="section-icon">🎓</div>
  <span class="section-title">Recommended Free Courses</span>
</div>
""", unsafe_allow_html=True)
                icons_map = ["📐","🔬","💡","🌍","📈","⚡","🏗"]
                for idx, c in enumerate(rd.get("recommended_courses", [])):
                    url  = c.get("url", "")
                    link = (f'<a href="{url}" target="_blank" '
                            f'style="color:var(--brand);font-size:12px;font-weight:600;'
                            f'text-decoration:none">Open Course →</a>') if url else ""
                    icon = icons_map[idx % len(icons_map)]
                    st.markdown(f"""
<div class="course-card">
  <div class="course-icon">{icon}</div>
  <div class="course-body">
    <div class="course-name">{c.get('name','')}</div>
    <div class="course-platform">{c.get('platform','')}</div>
    <div class="course-meta">
      <span>💰 {c.get('cost','Free')}</span>
      <span>⏱ {c.get('duration','Self-paced')}</span>
      <span>{link}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

                salary = rd.get("salary_outlook", "")
                if salary:
                    st.markdown(f"""
<div class="salary-insight">
  <div class="salary-title">Expected Salary After Transition</div>
  <div class="salary-value">{salary}</div>
  <div class="salary-note">Projected range after 6–12 months of green skilling,
  based on current market data and your experience level.</div>
</div>
""", unsafe_allow_html=True)

            # ── Tab 5: Next Steps ─────────────────────────────────────────────
            with tab5:
                st.markdown("""
<div class="section-header">
  <div class="section-icon">⚡</div>
  <span class="section-title">Recommended Next Steps</span>
</div>
""", unsafe_allow_html=True)
                for i, step in enumerate(rd.get("next_steps", []), 1):
                    st.markdown(f"""
<div class="step-card">
  <div class="step-number">{i}</div>
  <div class="step-text">{step}</div>
</div>
""", unsafe_allow_html=True)

            # ── Tab 6: PDF ────────────────────────────────────────────────────
            with tab6:
                st.markdown("""
<div class="section-header">
  <div class="section-icon">📄</div>
  <span class="section-title">Your Career Report</span>
</div>
""", unsafe_allow_html=True)
                if pdf and Path(pdf).exists():
                    size_kb = Path(pdf).stat().st_size // 1024
                    pages   = 5
                    st.markdown(f"""
<div class="pdf-download-area">
  <div class="pdf-icon">📄</div>
  <div class="pdf-title">Green Career Report Ready</div>
  <div class="pdf-meta">{Path(pdf).name} · {size_kb} KB · ~{pages} pages</div>
</div>
""", unsafe_allow_html=True)
                    pdf_download_button(pdf, "⬇ Download PDF Career Report")
                    st.markdown("---")
                    st.markdown("**Report includes:**")
                    contents = [
                        "🎨 Professional cover page with your details",
                        "📋 Executive summary with agent methodology",
                        "💼 Top 4 green career matches with salary data",
                        "📊 Skill gap analysis with priority ratings",
                        "📚 Free course recommendations with links",
                        "📅 Personalised 7-day learning roadmap",
                        "⚡ Concrete next steps for career transition",
                        "💰 Salary outlook after green skilling",
                    ]
                    for item in contents:
                        st.markdown(f"- {item}")
                else:
                    st.warning("PDF report was not generated. Try running the agent again.")

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            if st.button("↺ Run Again with Different Profile"):
                for key in ["results","pdf_path","elapsed","tasks","search_count"]:
                    st.session_state.pop(key, None)
                st.rerun()

    # ════════════════════════════════════════════════════════════════════════
    # HISTORY TAB
    # ════════════════════════════════════════════════════════════════════════
    with tab_history:
        show_history_page()

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="app-footer">
  <span class="footer-brand">🌱 {PAGE_TITLE}</span>
  <span class="footer-meta">
    Groq LLaMA 3.3 70B · DuckDuckGo · Skill India KB · fpdf2 · ₹0 Cost · {ORG_NAME}
  </span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    show_login_page()
else:
    show_main_app()