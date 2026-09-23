#!/usr/bin/env python3
"""Generate Aaron Eltahan recruiting resume PDF."""

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

OUTPUT = "/workspace/Aaron_Eltahan_Resume_20260923.pdf"

styles = getSampleStyleSheet()
TITLE = ParagraphStyle(
    "Title",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=18,
    spaceAfter=4,
    textColor=colors.HexColor("#111827"),
)
SUBTITLE = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10,
    leading=13,
    spaceAfter=2,
)
SECTION = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=11,
    spaceBefore=10,
    spaceAfter=4,
    textColor=colors.HexColor("#111827"),
)
BODY = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10,
    leading=13,
    spaceAfter=4,
)
BULLET = ParagraphStyle(
    "Bullet",
    parent=BODY,
    leftIndent=12,
    bulletIndent=0,
    spaceAfter=2,
)
JOB_TITLE = ParagraphStyle(
    "JobTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10,
    spaceBefore=6,
    spaceAfter=2,
)
ORG = ParagraphStyle(
    "Org",
    parent=styles["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=10,
    spaceAfter=2,
)
DATE = ParagraphStyle(
    "Date",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10,
    spaceAfter=4,
)


def bullets(items):
    return ListFlowable(
        [ListItem(Paragraph(item, BULLET), leftIndent=12) for item in items],
        bulletType="bullet",
        start="bulletchar",
        bulletFontName="Helvetica",
        bulletFontSize=10,
        leftIndent=18,
        bulletOffsetY=0,
    )


def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )
    story = []

    story.append(Paragraph("Aaron Eltahan", TITLE))
    story.append(Paragraph("Austin, TX", SUBTITLE))
    story.append(
        Paragraph(
            'Phone: 512-775-0005 | Email: '
            '<link href="mailto:eltahanaaron@gmail.com">eltahanaaron@gmail.com</link>',
            SUBTITLE,
        )
    )
    story.append(
        Paragraph(
            'Soccer recruiting hub: '
            '<link href="https://aaron-eltahan-soccer.github.io/" color="#0c2d48">'
            "Profile, highlight film &amp; schedule</link>",
            SUBTITLE,
        )
    )
    story.append(
        Paragraph(
            "Attacking Midfielder / Winger &nbsp;|&nbsp; 6'1\" &nbsp;|&nbsp; 160 lbs &nbsp;|&nbsp; Class of 2028",
            SUBTITLE,
        )
    )

    story.append(Paragraph("Background", SECTION))
    story.append(
        Paragraph(
            "An Early College High School (ECHS) student in Round Rock ISD on track to earn both a "
            "high school diploma and an associate degree from Austin Community College (ACC). Builds "
            "strong college readiness through dual-credit coursework, STAAR Masters-level performance, "
            "and competitive PSAT results. Especially interested in sports medicine, athletic performance, "
            "injury prevention, and sports and event management, combining science, leadership, and teamwork. "
            "Applies that focus through competitive soccer and lifeguarding in high-traffic venues.",
            BODY,
        )
    )

    story.append(Paragraph("Education", SECTION))
    story.append(
        Paragraph(
            "Early College High School, Round Rock ISD (Expected Graduation: May 2028)",
            BODY,
        )
    )
    story.append(bullets([
        "High school diploma, and",
        "Associate degree from Austin Community College (ACC) (Expected Graduation: May 2028)",
    ]))
    story.append(Paragraph("Academic Performance:", BODY))
    story.append(bullets([
        "GPA: 3.9600 (Weighted: 5.5333), Rank: 23/102",
        "STAAR Mathematics: Masters (98th percentile), Science: Masters (91st percentile), "
        "Reading/Language Arts: Masters (90th percentile)",
        "PSAT/NMSQT (Grade 10): Total 1090 — 95th percentile (state), 90th percentile (national).",
    ]))

    story.append(Paragraph("Work &amp; Mentorship Experience", SECTION))
    story.append(Paragraph("Lifeguard", JOB_TITLE))
    story.append(Paragraph("Kalahari Resorts &amp; Conventions, Round Rock, TX", ORG))
    story.append(Paragraph("May 2025 – August 2025", DATE))
    story.append(bullets([
        "Worked in a safety-critical environment requiring constant situational awareness.",
        "Performed routine inspections of assigned areas and equipment.",
        "Identified hazards and responded quickly to prevent incidents.",
        "Followed established safety protocols and emergency procedures.",
        "Communicated clearly with supervisors and team members during peak operations.",
    ]))

    story.append(Paragraph("Junior Leader Mentorship Participant", JOB_TITLE))
    story.append(Paragraph("EP Sports Academy, Austin, TX", ORG))
    story.append(Paragraph("January 2026 – Present (ongoing)", DATE))
    story.append(bullets([
        "Selected for a structured mentorship program focused on leadership, responsibility, and skill development.",
        "Assigned a mentor to guide learning through real-world coaching, event operations, and youth program support.",
        "Assist with youth soccer activities including practice support, warm-ups, and small-sided games.",
        "Learn to follow operational procedures, manage time commitments, and receive formal feedback on performance.",
        "Program includes regular check-ins, written evaluations, and opportunities to progress to paid roles.",
    ]))

    story.append(PageBreak())

    story.append(Paragraph("Athletics &amp; Leadership Experience", SECTION))
    story.append(Paragraph("Elite Soccer Athlete — Lonestar SC", JOB_TITLE))
    story.append(
        Paragraph(
            "ATX STH ECNL RL STXCL B2009/10 Gold, Austin, TX (2026–present)",
            ORG,
        )
    )
    story.append(bullets([
        "Attacking midfielder and winger in ECNL Regional League STXCL competition.",
        "Previously: FC Westlake 2010 ECNL RL STXCL (2024–2026); Lonestar SC (2019–2024).",
        "2025–26 ECNL RL STXCL (FC Westlake): 21 games played, 20 starts, ~40 min avg.",
        "Trains 3–4× weekly S&amp;C; ongoing technical development with 1A Soccer Sports Club.",
        "Highlight films: youtube.com/channel/UCdoNA38vU1hO9fTR-QM_jcg",
    ]))

    story.append(Paragraph("Recruiting Profile &amp; Coach References", JOB_TITLE))
    story.append(bullets([
        "NCAA ID: 2511775039 &nbsp;|&nbsp; NAIA ID: 1025364",
        "NCSA Profile (verified) &nbsp;|&nbsp; FieldLevel: aaron.eltahan",
        "Club Coach: Oscar Garcia — 512-586-3930, ogarcia@lonestar-sc.com",
        "Club Director: Ross McGibney — 203-803-3039, rmcgibney@lonestar-sc.com",
        "Previous Club Coach (FC Westlake): Darrell Best — 512-925-4456, dbest@fcwestlakesoccer.com",
    ]))

    story.append(Paragraph("Recent Showcases &amp; Events", JOB_TITLE))
    story.append(bullets([
        "Trinity Univ Men's College Prep / ID — Aug 1–2, 2026, San Antonio TX",
        "Texas Elite Men's Combine — Jul 25–26, 2026, Round Rock TX",
        "Texas Lutheran Univ Men's College Prep / ID — Jul 10–12, 2026, Seguin TX",
        "Lonestar Boys College ID Camp — Jun 21, 2026, San Antonio TX",
        "St. Edwards College Prep ID Clinic — Dec 13–14, 2025, Austin TX",
    ]))

    story.append(Paragraph("Skills &amp; Strengths", SECTION))
    story.append(bullets([
        "Safety awareness and adherence to procedures",
        "Interest in sports medicine, human performance, and injury-prevention basics",
        "Interest in sports and event management, logistics, and guest-facing operations",
        "Ability to learn through mentorship and feedback",
        "Team communication in operational environments",
        "Reliable, punctual, and accountable",
    ]))

    story.append(Paragraph("Activities &amp; Community Involvement", SECTION))
    story.append(bullets([
        "Weightlifting Club: discipline, goal setting, and consistency",
        "Music Club: coordination, listening skills, and collaboration",
        "Volunteer youth soccer mentor supporting younger players",
    ]))

    doc.build(story)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build()
