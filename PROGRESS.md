# PROGRESS.md

## Project: Green Jobs Career Advisor — Industry Standards Upgrade
## Started: 2026-07-10
## Completed: 2026-07-12

---

## ✅ Completed Steps

### Step 0 — PROGRESS.md + Codebase Audit (DONE)
- Full audit of existing codebase before writing any code
- Documented 9 gotchas (G-001 through G-009)
- Established rule: audit before coding, one file at a time

### Step 1 — pyproject.toml + uv setup (DONE)
- uv created .venv with Python 3.12.12 (uv chose 3.12 over 3.14 — correct)
- google-genai==2.11.0 installed (replaces deprecated google-generativeai)
- sqlite-utils==4.0 installed
- bcrypt==5.0.0 installed
- groq==1.5.0 installed (LLaMA 3.3 70B — replaces Gemini)
- All dev tools: pytest, ruff, mypy, pre-commit
- requirements.txt superseded by pyproject.toml

### Step 2 — Secrets + Git (DONE)
- .gitignore, .env.example created
- Git initialised correctly inside green_jobs_agent V3/ (not parent folder)
- LESSON LEARNED: notebook had real API key hardcoded (G-001 triggered)
- GitHub push protection blocked the push — caught before going public
- Used git filter-repo to scrub notebook from all commits
- Force pushed clean history
- Real API key invalidated — new Groq key used instead
- LESSON LEARNED: git init must run inside the project folder, not parent

### Step 3 — Database layer (DONE)
- src/green_jobs/db.py — SQLite via sqlite-utils 4.0
- Three tables: users, runs, run_logs
- Every agent run saved with inputs, outputs, timing, status, task logs
- Fixed G-008: used db["table"].insert(row) pattern throughout
- Fixed PRAGMA table_info bug: c[1] for column name, not c[0]

### Step 4 — Authentication (DONE)
- src/green_jobs/auth.py — bcrypt password hashing (work factor 12)
- register(), login(), get_user(), is_admin(), ensure_admin_exists()
- Safe error messages — never reveals whether username exists
- Username and password validation with clear AuthError messages
- Admin account auto-created on first startup from .env values

### Step 5 — Logging (DONE)
- Python logging module configured in app.py
- Dual output: StreamHandler (console) + FileHandler (green_jobs_app.log)
- All auth events, run starts/completions logged with structured format
- Per-task log lines saved to run_logs table in database

### Step 6 — app.py rewrite (DONE)
- Login / Register page as app entry point — no agent access without login
- Secrets loaded from .env — no hardcoded values anywhere
- Groq LLaMA 3.3 70B replaces Gemini (faster, generous free tier)
- History tab: users see own runs, admin sees all runs (RBAC)
- Every run saved to database automatically
- All existing tabs preserved: Green Roles, Skill Gaps, Roadmap, Courses, Next Steps, PDF
- Run again button clears session state cleanly

### Step 7 — Groq migration (DONE)
- executor.py migrated from google-generativeai to groq SDK
- Model: llama-3.3-70b-versatile
- Fixed G-002 and G-006: deprecated google.generativeai fully removed
- Ruff passing — 0 errors across agent/, tools/, src/, app.py

### Step 8 — pytest tests (DONE)
- tests/test_db.py — 9 tests covering schema, users, runs, logs, stats
- tests/test_auth.py — 9 tests covering register, login, validation, admin
- tests/test_tools.py — 7 tests covering KB sectors, roles, platforms
- 25/25 tests passing on Python 3.12.12
- Uses tmp_path fixture — tests never touch production database

### Step 9 — Git hygiene (DONE)
- .gitattributes added — normalised line endings (LF for all source files)
- Repo reinitialised in correct directory after parent-folder git incident
- All commits clean — no venvs, no other projects, no secrets
- GitHub repo: https://github.com/codewithleo1/Green-Job-Agent.git

---

## 🐛 Known Gotchas (never re-introduce these)

### G-001: API Key in source code
- **File**: Green_Career_Agent.ipynb, Cell 2
- **Problem**: `GEMINI_API_KEY = "AQ.Ab8RN6L..."` — real key committed to repo
- **Fix**: Always load from `.env` via `python-dotenv`; `.env` must be in `.gitignore`

### G-002: google-generativeai vs google-genai conflict
- **File**: executor.py line 20
- **Problem**: executor.py imports `google.generativeai` (deprecated)
- **Fix**: Replaced with groq SDK entirely — problem no longer exists

### G-003: PowerShell does not support &&
- **Problem**: `cd project && uv run python` fails in PowerShell
- **Fix**: Always split into separate commands

### G-004: Hardcoded file paths in KnowledgeBaseTool
- **File**: knowledge_tool.py
- **Problem**: Path resolves relative to __file__ — breaks on import from different locations
- **Status**: Works in current flat layout; revisit if src/ restructure is done

### G-005: ReportGeneratorTool output_dir defaults to relative path
- **File**: report_tool.py
- **Problem**: reports/ folder created relative to wherever Python runs
- **Status**: Works when run from project root via `uv run streamlit run app.py`

### G-006: executor.py uses google-generativeai (deprecated)
- **Fixed**: Replaced with groq SDK (llama-3.3-70b-versatile)

### G-007: Python version mismatch
- uv selected Python 3.12.12, not 3.14.5
- All code and tests target 3.12
- pyproject.toml: requires-python = ">=3.11" — keep it that way

### G-008: sqlite-utils 4.0 API change
- Always use db["table"].insert(row) pattern
- db["table"].update(id, changes) for updates

### G-009: Space in folder name breaks git filter-branch
- "green_jobs_agent V3" path with space caused filter-branch to fail
- Fix: use git filter-repo instead (pip install git-filter-repo)

### G-010: git init in wrong directory
- Running git init in parent "AI Agent/" swept in all sibling projects
- Fix: always cd into the specific project folder before git init
- Detection: git rev-parse --show-toplevel must return the project folder

### G-011: PRAGMA table_info returns (cid, name, type, ...) not (name, ...)
- c[0] returns the column id number, not the column name
- Always use c[1] to get the column name when building dicts from raw SQL

---

## 📋 Upgrade Steps

- [x] Step 0: PROGRESS.md + codebase audit
- [x] Step 1: pyproject.toml + uv setup
- [x] Step 2: .env + secrets handling + Git
- [x] Step 3: Database layer (db.py)
- [x] Step 4: Authentication (auth.py)
- [x] Step 5: Logging
- [x] Step 6: app.py rewrite (login + history + Groq)
- [x] Step 7: Groq migration (executor.py)
- [x] Step 8: pytest — 25/25 passing
- [x] Step 9: Git hygiene (.gitattributes, clean repo)

---

## 🚀 How to run

```powershell
uv run streamlit run app.py
```

## 🧪 How to test

```powershell
uv run pytest tests/ -v --basetemp="tmp_pytest" -p no:cacheprovider
```

## 📁 Final structure

```
green_jobs_agent V3/
├── app.py                  ← Streamlit UI (login + agent + history)
├── agent/
│   ├── executor.py         ← Groq LLaMA 3.3, tool orchestration
│   ├── planner.py          ← 9-task plan generator
│   └── green_career_agent.py
├── tools/
│   ├── search_tool.py      ← DuckDuckGo
│   ├── knowledge_tool.py   ← Skill India JSON KB
│   └── report_tool.py      ← PDF generator (fpdf2)
├── src/green_jobs/
│   ├── db.py               ← SQLite: users, runs, run_logs
│   └── auth.py             ← bcrypt login/register
├── tests/
│   ├── test_db.py          ← 9 tests
│   ├── test_auth.py        ← 9 tests
│   └── test_tools.py       ← 7 tests
├── data/
│   └── green_jobs_india.json
├── pyproject.toml
├── .env                    ← secrets (never committed)
├── .env.example
├── .gitignore
├── .gitattributes
└── PROGRESS.md
```