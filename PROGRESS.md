# PROGRESS.md

## Project: Green Jobs Career Advisor — Industry Standards Upgrade
## Started: 2026-07-10

---

## ✅ Completed Steps

### Step 1 — pyproject.toml + uv setup (DONE)
- uv created .venv with Python 3.12.12 (uv chose 3.12 over 3.14 — correct)
- google-genai==2.11.0 installed (replaces deprecated google-generativeai)
- sqlite-utils==4.0 installed
- bcrypt==5.0.0 installed
- All dev tools: pytest, ruff, mypy, pre-commit
- requirements.txt can now be deleted after Step 3 restructure

### Step 2 — Secrets + Git (DONE)
- .gitignore, .env.example created
- Git initialised, remote set to https://github.com/codewithleo1/Green-Job-Agent.git
- LESSON LEARNED: notebook had real API key hardcoded (G-001 triggered)
- GitHub push protection blocked the push — caught it before it went public
- Used git filter-repo to scrub notebook from all commits
- Force pushed clean history
- Notebook will be re-added later with key removed (replaced with os.environ call)
- Real API key was invalidated at aistudio.google.com — generate a new one

---

## 🐛 Known Gotchas (never re-introduce these)

### G-001: API Key in source code
- **File**: Green_Career_Agent.ipynb, Cell 2
- **Problem**: `GEMINI_API_KEY = "AQ.Ab8RN6L..."` — real key committed to repo
- **Fix**: Always load from `.env` via `python-dotenv`; `.env` must be in `.gitignore`

### G-002: google-generativeai vs google-genai conflict
- **File**: executor.py line 20
- **Problem**: executor.py imports `google.generativeai` (deprecated) while notebook uses `google.genai` (new). They configure differently and can't be mixed.
- **Fix**: Standardise on `google-genai` (`google.genai`) everywhere. The old package shows FutureWarning and will break.

### G-003: PowerShell does not support &&
- **Problem**: `cd project && uv run python` fails in PowerShell
- **Fix**: Always split into separate commands

### G-004: Hardcoded file paths in KnowledgeBaseTool
- **File**: knowledge_tool.py
- **Problem**: `Path(__file__).resolve().parent.parent / "data"` — breaks when `src/` layout is introduced
- **Fix**: Use `importlib.resources` or pass the path via config

### G-005: ReportGeneratorTool output_dir defaults to relative path
- **File**: report_tool.py
- **Problem**: `reports/` folder created relative to wherever Python runs, not relative to project root
- **Fix**: Resolve output path from config/env variable

### G-006: executor.py uses google-generativeai (deprecated)
- **File**: executor.py, line 20: `import google.generativeai as genai`
- **Problem**: This package is end-of-life. The notebook already migrated to `google-genai`.
- **Fix**: Replace with `from google import genai` and update all SDK calls

### G-007: Python version mismatch
- uv selected Python 3.12.12, not 3.14.5
- All code and tests must target 3.12, not 3.14
- pyproject.toml says requires-python = ">=3.11" — keep it that way

### G-008: sqlite-utils 4.0 API change
- sqlite-utils 4.0 removed the .insert() shorthand in some contexts
- Always use db["table"].insert(row) pattern, not db.insert()
- Docs: https://sqlite-utils.datasette.io/en/stable/

### G-009: Space in folder name breaks git filter-branch
- "green_jobs_agent V3" path with space caused filter-branch to fail
- Fix: use git filter-repo instead (pip install git-filter-repo)

---

## 📋 Upgrade Steps

- [ ] Step 0: PROGRESS.md (this file)
- [ ] Step 1: pyproject.toml + uv setup
- [ ] Step 2: .env + secrets handling
- [ ] Step 3: src/ layout restructure
- [ ] Step 4: Logging module
- [ ] Step 5: Type hints
- [ ] Step 6: Error handling
- [ ] Step 7: CLI entry point
- [ ] Step 8: pytest tests
- [ ] Step 9: pre-commit hooks