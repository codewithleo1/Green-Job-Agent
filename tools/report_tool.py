"""
tools/report_tool.py
────────────────────
Report Generator Tool — creates a PDF career report.
Uses fpdf2 (free, no external services needed).
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
from pathlib import Path


def _clean(text: str) -> str:
    """Remove non-latin1 characters that fpdf cannot encode."""
    # Replace common unicode symbols with ASCII equivalents
    replacements = {
        "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u2022": "*", "\u25cf": "*",
        "\u2713": "✓", "\u20b9": "Rs.", "\u2192": "->", "\u2714": "✓",
        "\u00e9": "e", "\u00e8": "e", "\u00e0": "a",
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
    # Strip any remaining non-latin1 chars
    return text.encode("latin-1", errors="replace").decode("latin-1")


class ReportGeneratorTool:
    """
    Tool: PDF Report Generator
    Creates a professional green career transition report.
    """

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path(__file__).resolve().parent.parent / "reports"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ── Colour helpers ────────────────────────────────────────────
    GREEN_DARK  = (27,  94,  32)
    GREEN_MID   = (46, 125,  50)
    GREEN_LIGHT = (200, 230, 201)
    YELLOW      = (255, 193,   7)
    WHITE       = (255, 255, 255)
    DARK        = (30,  30,  30)
    GRAY        = (100, 100, 100)
    LIGHT_GRAY  = (245, 245, 245)

    def generate(self, report_data: dict) -> str:
        """
        Generates a PDF report and saves it.
        Returns the file path as a string.

        report_data keys:
          user_name, current_role, experience_years, background,
          top_jobs (list), skill_gaps (list), roadmap_7day (list),
          recommended_courses (list), salary_outlook (str),
          next_steps (list), agent_summary (str)
        """

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        self._cover(pdf, report_data)
        pdf.add_page()
        self._executive_summary(pdf, report_data)
        self._top_green_jobs(pdf, report_data)
        pdf.add_page()
        self._skill_gap(pdf, report_data)
        self._courses(pdf, report_data)
        pdf.add_page()
        self._roadmap(pdf, report_data)
        self._next_steps(pdf, report_data)
        self._footer_page(pdf, report_data)

        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"Green_Career_Report_{report_data.get('user_name','User').replace(' ','_')}_{timestamp}.pdf"
        filepath  = self.output_dir / filename
        pdf.output(str(filepath))

        print(f"      📄 [REPORT TOOL] Saved: {filepath}")
        return str(filepath)

    # ── Section renderers ────────────────────────────────────────

    def _cover(self, pdf: FPDF, d: dict):
        """Full-page cover."""
        # Dark green background
        pdf.set_fill_color(*self.GREEN_DARK)
        pdf.rect(0, 0, 210, 297, "F")

        # Decorative accent stripe
        pdf.set_fill_color(*self.YELLOW)
        pdf.rect(0, 0, 8, 297, "F")

        # Logo area
        pdf.set_xy(20, 30)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*self.YELLOW)
        pdf.cell(0, 8, _clean("EDUNET AI TRAINING PROGRAM"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Main title
        pdf.set_xy(20, 60)
        pdf.set_font("Helvetica", "B", 32)
        pdf.set_text_color(*self.WHITE)
        pdf.multi_cell(170, 14, _clean("Green Jobs\nCareer Advisor"), align="L")

        # Subtitle
        pdf.set_xy(20, 115)
        pdf.set_font("Helvetica", "", 14)
        pdf.set_text_color(200, 230, 201)
        pdf.cell(0, 8, _clean("Personalised Career Transition Report"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Divider
        pdf.set_xy(20, 132)
        pdf.set_fill_color(*self.YELLOW)
        pdf.rect(20, 132, 100, 1.5, "F")

        # User details box
        pdf.set_xy(20, 145)
        pdf.set_fill_color(46, 125, 50)
        pdf.rect(20, 143, 165, 55, "F")

        pdf.set_xy(26, 150)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*self.YELLOW)
        pdf.cell(0, 7, _clean("PREPARED FOR"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_xy(26, 159)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(*self.WHITE)
        pdf.cell(0, 10, _clean(d.get("user_name", "Professional")), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_xy(26, 171)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(200, 230, 201)
        pdf.cell(80, 7, _clean(f"Current Role : {d.get('current_role', 'N/A')}"))
        pdf.cell(80, 7, _clean(f"Experience   : {d.get('experience_years', 'N/A')} years"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(26, 180)
        pdf.cell(0, 7, _clean(f"Background   : {d.get('background', 'N/A')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Date
        pdf.set_xy(20, 250)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(160, 210, 160)
        pdf.cell(0, 7, _clean(f"Generated on: {datetime.now().strftime('%d %B %Y at %H:%M')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(20, 258)
        pdf.cell(0, 7, _clean("Powered by: Google Gemini Free API + DuckDuckGo + Skill India KB"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Badge
        pdf.set_fill_color(*self.YELLOW)
        pdf.rect(130, 245, 60, 22, "F")
        pdf.set_xy(130, 249)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*self.GREEN_DARK)
        pdf.cell(60, 6, _clean("COST: Rs. 0"), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(130, 255)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(60, 6, _clean("100% Free API Stack"), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def _section_header(self, pdf: FPDF, title: str, color=None):
        """Reusable coloured section header."""
        if color is None:
            color = self.GREEN_DARK
        pdf.set_fill_color(*color)
        pdf.set_text_color(*self.WHITE)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, _clean(f"  {title}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        pdf.ln(3)
        pdf.set_text_color(*self.DARK)

    def _executive_summary(self, pdf: FPDF, d: dict):
        self._section_header(pdf, "Executive Summary")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_fill_color(*self.LIGHT_GRAY)
        pdf.multi_cell(
            0, 6,
            _clean(d.get("agent_summary",
                          "This report was generated by the Green Jobs Career Advisor Agent.")),
            fill=True
        )
        pdf.ln(6)

        # Quick stats row
        stats = [
            ("Top Green Roles Identified", str(len(d.get("top_jobs", [])))),
            ("Skill Gaps Found",           str(len(d.get("skill_gaps", [])))),
            ("Courses Recommended",        str(len(d.get("recommended_courses", [])))),
            ("Roadmap Duration",           "7 Days"),
        ]
        col_w = 46
        for label, val in stats:
            pdf.set_fill_color(*self.GREEN_LIGHT)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(*self.GREEN_DARK)
            pdf.cell(col_w, 14, _clean(val), border=0, align="C", fill=True)
            pdf.set_text_color(*self.DARK)

        pdf.ln(14)
        for label, val in stats:
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*self.GRAY)
            pdf.cell(col_w, 5, _clean(label), align="C")
        pdf.ln(10)

    def _top_green_jobs(self, pdf: FPDF, d: dict):
        self._section_header(pdf, "Your Top Green Job Matches")
        jobs = d.get("top_jobs", [])
        for i, job in enumerate(jobs[:4], 1):
            # Job card
            pdf.set_fill_color(*self.GREEN_LIGHT)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(*self.GREEN_DARK)
            pdf.cell(0, 8, _clean(f"  {i}.  {job.get('title', '')}  —  {job.get('sector', '')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
            pdf.set_text_color(*self.DARK)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(45, 6, _clean(f"  Salary: Rs.{job.get('salary', '')} p.a."))
            pdf.cell(45, 6, _clean(f"Demand: {job.get('demand', '')}"))
            pdf.cell(90, 6, _clean(f"Level: {job.get('level', '')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            # Why match
            if job.get("why_match"):
                pdf.set_text_color(*self.GRAY)
                pdf.set_font("Helvetica", "I", 9)
                pdf.multi_cell(0, 5, _clean(f"  Why a match: {job['why_match']}"))
                pdf.set_text_color(*self.DARK)
            pdf.ln(3)

    def _skill_gap(self, pdf: FPDF, d: dict):
        self._section_header(pdf, "Skill Gap Analysis")
        gaps = d.get("skill_gaps", [])
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, _clean(
            "Based on your current background, the following skills are needed "
            "to transition into green jobs. Priority order: HIGH → MEDIUM → LOW."
        ))
        pdf.ln(3)

        for gap in gaps[:8]:
            priority = gap.get("priority", "MEDIUM")
            color = self.GREEN_DARK if priority == "HIGH" else (
                self.GREEN_MID if priority == "MEDIUM" else self.GRAY)
            pdf.set_fill_color(*color)
            pdf.set_text_color(*self.WHITE)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(22, 7, _clean(f" {priority}"), fill=True)
            pdf.set_text_color(*self.DARK)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 7, _clean(f"  {gap.get('skill', '')}  —  {gap.get('description', '')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)

    def _courses(self, pdf: FPDF, d: dict):
        self._section_header(pdf, "Recommended Free Courses")
        courses = d.get("recommended_courses", [])
        pdf.set_font("Helvetica", "", 9)
        for c in courses[:6]:
            pdf.set_fill_color(*self.LIGHT_GRAY)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, _clean(f"  {c.get('name', '')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(50, 5, _clean(f"  Platform: {c.get('platform', '')}"))
            pdf.cell(50, 5, _clean(f"Cost: {c.get('cost', 'Free')}"))
            pdf.cell(0, 5, _clean(f"Duration: {c.get('duration', 'Self-paced')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if c.get("url"):
                pdf.set_text_color(*self.GREEN_MID)
                pdf.set_font("Helvetica", "I", 8)
                pdf.cell(0, 5, _clean(f"  Link: {c.get('url', '')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_text_color(*self.DARK)
            pdf.ln(2)

    def _roadmap(self, pdf: FPDF, d: dict):
        self._section_header(pdf, "Your 7-Day Green Skilling Roadmap")
        roadmap = d.get("roadmap_7day", [])
        colors  = [self.GREEN_DARK, self.GREEN_MID, (56,142,60), (76,175,80),
                   (102,187,106), (129,199,132), (165,214,167)]
        for i, day in enumerate(roadmap[:7]):
            c = colors[i % len(colors)]
            pdf.set_fill_color(*c)
            pdf.set_text_color(*self.WHITE)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(22, 9, _clean(f" DAY {i+1}"), fill=True)
            pdf.set_text_color(*self.DARK)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 9, _clean(f"  {day.get('focus', '')}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*self.GRAY)
            pdf.multi_cell(0, 5, _clean(f"     {day.get('tasks', '')}"))
            pdf.set_text_color(*self.DARK)
            pdf.ln(1)
        pdf.ln(4)

    def _next_steps(self, pdf: FPDF, d: dict):
        self._section_header(pdf, "Recommended Next Steps")
        steps = d.get("next_steps", [])
        pdf.set_font("Helvetica", "", 10)
        for i, step in enumerate(steps, 1):
            pdf.set_fill_color(*self.GREEN_LIGHT)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(8, 7, _clean(str(i)), align="C", fill=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 7, _clean(f"  {step}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)

        # Salary outlook box
        pdf.ln(4)
        pdf.set_fill_color(*self.GREEN_DARK)
        pdf.set_text_color(*self.WHITE)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 9, _clean("  Salary Outlook After Green Transition"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        pdf.set_fill_color(*self.LIGHT_GRAY)
        pdf.set_text_color(*self.DARK)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, _clean(d.get("salary_outlook", "")), fill=True)

    def _footer_page(self, pdf: FPDF, d: dict):
        pdf.ln(10)
        pdf.set_fill_color(*self.GREEN_DARK)
        pdf.rect(0, pdf.get_y(), 210, 30, "F")
        pdf.set_xy(10, pdf.get_y() + 5)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*self.WHITE)
        pdf.cell(0, 6, _clean("Generated by Green Jobs Career Advisor Agent"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(10, pdf.get_y())
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(200, 230, 200)
        pdf.cell(0, 5, _clean(
            "Powered by: Gemini 1.5 Flash (Free) | DuckDuckGo Search | "
            "Skill India Knowledge Base | Cost: Rs. 0"
        ), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
