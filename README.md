# 🌱 Green Jobs Career Advisor Agent

> *"What green skills do I need for the jobs of the future?"*

**Powered by:** Google Gemini Free API | DuckDuckGo Search | Skill India Knowledge Base
**Cost:** ₹0 — 100% Free Stack
**Type:** Autonomous AI Agent — Planning + Multi-Tool + Loop + PDF Report
**Session:** Edunet AI Training Program — Grand Finale Demo

---

## 📁 Project Structure

```
green_jobs_agent/
│
├── 📓 notebooks/
│   └── Green_Career_Agent.ipynb    ← START HERE (main demo notebook)
│
├── 🤖 agent/
│   ├── green_career_agent.py       ← Main orchestrator (one-line runner)
│   ├── planner.py                  ← Creates the 9-task plan
│   └── executor.py                 ← Runs the plan / agent loop
│
├── 🔧 tools/
│   ├── search_tool.py              ← Web search (DuckDuckGo/ddgs)
│   ├── knowledge_tool.py           ← India green jobs KB reader
│   └── report_tool.py              ← PDF report generator (fpdf2)
│
├── 📊 data/
│   └── green_jobs_india.json       ← Curated India green jobs data
│                                      (6 sectors, 15 roles, 8 platforms)
│
├── 📄 reports/                     ← PDF reports saved here (auto-created)
│
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

### Step 1 — Get Free Gemini API Key
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click **Create API Key**
4. Copy the key

### Step 2 — Install Requirements
```bash
pip install -r requirements.txt
```

### Step 3 — Open the Notebook
```bash
jupyter notebook notebooks/Green_Career_Agent.ipynb
```

### Step 4 — Paste API Key & Run
Paste your key in **Cell 2**, then run all cells top to bottom.

---

## 🤖 What the Agent Does — 9 Tasks Autonomously

| Task | Tool | What Happens |
|------|------|-------------|
| 1 | 🔍 Web Search | Fetches trending green jobs in India (live) |
| 2 | 📚 Knowledge Base | Loads curated Skill India green roles data |
| 3 | 🧠 Gemini LLM | Matches top 4 roles to YOUR background |
| 4 | 🧠 Gemini LLM | Identifies YOUR personal skill gaps |
| 5 | 🔍 Web Search | Finds free green courses available now |
| 6 | 📚 Knowledge Base | Loads free learning platforms |
| 7 | 🧠 Gemini LLM | Builds YOUR personalised 7-day roadmap |
| 8 | 🔍 Web Search | Searches current salary trends India |
| 9 | 📄 PDF Generator | Creates your complete career report |

---

## 🧩 All 6 Agent Components Demonstrated

| Component | Implementation |
|-----------|---------------|
| 🎯 Goal | Career transition to green jobs |
| 🧠 Reasoning | Gemini 1.5 Flash — 3 intelligent LLM calls |
| 📋 Planning | 9-task plan created before execution begins |
| 🔧 Tools | DuckDuckGo × 3 + Knowledge Base × 2 + PDF Generator |
| 💾 Memory | Results stored and reused across all 9 tasks |
| ⚡ Action | Personalised PDF career report delivered |

---

## 💰 Complete Cost Breakdown

| Tool | Provider | Cost |
|------|----------|------|
| Gemini 1.5 Flash LLM | Google AI Studio | Free (1500 req/day) |
| Web Search | DuckDuckGo (ddgs) | Free (no API key) |
| Knowledge Base | Local JSON | Free |
| PDF Generation | fpdf2 | Free (open source) |
| **TOTAL** | | **₹0** |

---

## 👤 Demo Profiles to Try Live

```python
# Software Engineer → EV
{"name": "Priya Sharma", "background": "Software/IT",
 "career_goal": "EV software and battery management"}

# Finance → ESG
{"name": "Rahul Mehta", "background": "Finance/Commerce",
 "career_goal": "ESG analysis and green finance"}

# Mechanical → Wind/EV
{"name": "Anita Patel", "background": "Mechanical Engineering",
 "career_goal": "wind energy and EV systems"}

# Civil → Green Buildings
{"name": "Sameer Khan", "background": "Civil Engineering",
 "career_goal": "LEED green buildings and energy audit"}
```

---

## 📊 Knowledge Base Contents

**Sectors covered (6):**
- Solar Energy
- Electric Vehicles (EV)
- Sustainability & ESG
- Green Building & Construction
- Wind Energy
- Green Finance

**Job roles (15):**
Solar PV Technician, Solar Energy Engineer, Solar Project Developer,
EV Battery Engineer, EV Charging Specialist, EV Software Engineer, EV Fleet Manager,
ESG Analyst, Carbon Credit Analyst, Sustainability Manager,
Green Building Consultant, Energy Auditor,
Wind Turbine Technician, Wind Resource Analyst,
Green Finance Analyst

**Free platforms (8):**
NPTEL, Coursera (Audit), Skill India/PMKVY, UNEP Finance Initiative,
edX (Audit), YouTube MNRE, GRI Academy, iGOT Karmayogi

---

## ⚠️ Trainer Notes

- **DuckDuckGo rate limits:** If 20+ students run simultaneously on the same WiFi,
  searches may briefly throttle. The `time.sleep(1.5)` between calls mitigates this.
  Run demos sequentially, not simultaneously.

- **Gemini free tier:** 15 requests/minute, 1500/day.
  For a class of 30, run the full agent for 2-3 profiles max as live demos,
  then let students run it individually after the session.

- **PDF location:** Reports are saved to the `reports/` folder automatically.
  Share the PDF with participants — it's a tangible takeaway.

---

> 🎓 **Edunet AI Training Program** | Introduction to AI Agents
> *From understanding to building — in one session.*
