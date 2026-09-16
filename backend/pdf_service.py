from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

try:
    # Register Unicode fonts for currency symbol support
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    bold_font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans-Bold.ttf")
    oblique_font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans-Oblique.ttf")
    
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    if os.path.exists(bold_font_path):
        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold_font_path))
    if os.path.exists(oblique_font_path):
        pdfmetrics.registerFont(TTFont("DejaVuSans-Oblique", oblique_font_path))
    
    FONT_REGULAR = "DejaVuSans"
    FONT_BOLD = "DejaVuSans-Bold"
    FONT_OBLIQUE = "DejaVuSans-Oblique"
except Exception:
    FONT_REGULAR = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
    FONT_OBLIQUE = "Helvetica-Oblique"

BG_IVORY = HexColor("#F7F3EA")
INK_DARK = HexColor("#1C1B19")
BRASS_GOLD = HexColor("#C08A2E")
FOREST_GREEN = HexColor("#2F5233")
GRAY_MUTED = HexColor("#5A5854")
CARD_BG = HexColor("#E8E4DA")

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm

def _editorial_canvas(canvas_obj: canvas.Canvas, doc):
    canvas_obj.saveState()
    canvas_obj.setFillColor(BG_IVORY)
    canvas_obj.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    canvas_obj.setStrokeColor(BRASS_GOLD)
    canvas_obj.setLineWidth(0.75)
    canvas_obj.line(MARGIN, MARGIN, PAGE_W - MARGIN, MARGIN)
    canvas_obj.line(MARGIN, PAGE_H - MARGIN, PAGE_W - MARGIN, PAGE_H - MARGIN)

    canvas_obj.setFont(FONT_BOLD, 8)
    canvas_obj.setFillColor(GRAY_MUTED)
    canvas_obj.drawString(MARGIN, MARGIN - 10, f"SkillProof Proposal — Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC")
    canvas_obj.drawRightString(PAGE_W - MARGIN, MARGIN - 10, f"Page {doc.page}")
    canvas_obj.restoreState()

def _get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="HeaderTitle",
        fontName=FONT_BOLD,
        fontSize=28,
        leading=34,
        textColor=INK_DARK,
        alignment=TA_CENTER,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="HeaderSubtitle",
        fontName=FONT_REGULAR,
        fontSize=12,
        leading=16,
        textColor=BRASS_GOLD,
        alignment=TA_CENTER,
        spaceAfter=20,
    ))
    styles.add(ParagraphStyle(
        name="ProblemTitle",
        fontName=FONT_BOLD,
        fontSize=16,
        leading=20,
        textColor=INK_DARK,
        spaceBefore=12,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName=FONT_BOLD,
        fontSize=13,
        leading=17,
        textColor=BRASS_GOLD,
        spaceBefore=14,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="BodyContent",
        fontName=FONT_REGULAR,
        fontSize=10,
        leading=15,
        textColor=INK_DARK,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="ScoreBoxLabel",
        fontName=FONT_BOLD,
        fontSize=8,
        leading=10,
        textColor=BRASS_GOLD,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="ScoreBoxValue",
        fontName=FONT_BOLD,
        fontSize=20,
        leading=24,
        textColor=FOREST_GREEN,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="FeedbackBox",
        fontName=FONT_OBLIQUE,
        fontSize=9.5,
        leading=14,
        textColor=INK_DARK,
        backColor=CARD_BG,
        borderColor=BRASS_GOLD,
        borderWidth=0.5,
        borderPadding=8,
        spaceBefore=8,
        spaceAfter=8,
    ))
    return styles

def generate_proposal_pdf(
    solver_name: str,
    problem_title: str,
    category: str,
    budget: str,
    timeline: str,
    pitch_responses: dict,
    scores: dict,
    average_score: float,
    status: str,
    feedback: str,
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )

    styles = _get_styles()
    story = []

    # Title & Metadata Header
    story.append(Paragraph("SKILLPROOF VETTED PROPOSAL", styles["HeaderTitle"]))
    story.append(Paragraph(f"Quality Gate Score: {average_score}/10 • Status: {status.upper()}", styles["HeaderSubtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BRASS_GOLD, spaceAfter=14))

    # Problem & Solver Overview Table
    overview_data = [
        [Paragraph("<b>Problem:</b>", styles["BodyContent"]), Paragraph(problem_title, styles["BodyContent"])],
        [Paragraph("<b>Category:</b>", styles["BodyContent"]), Paragraph(f"{category} | Budget: {budget} | Timeline: {timeline}", styles["BodyContent"])],
        [Paragraph("<b>Solver:</b>", styles["BodyContent"]), Paragraph(solver_name, styles["BodyContent"])],
        [Paragraph("<b>Submitted:</b>", styles["BodyContent"]), Paragraph(datetime.utcnow().strftime('%B %d, %Y'), styles["BodyContent"])],
    ]
    t_overview = Table(overview_data, colWidths=[3 * cm, 13 * cm])
    t_overview.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, BRASS_GOLD),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, CARD_BG),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 14))

    # Score Grid
    story.append(Paragraph("GATE SCORING BREAKDOWN", styles["SectionHeader"]))
    score_items = [
        ("PROBLEM CLARITY", scores.get("problem_clarity", 0)),
        ("MARKET SPECIFICITY", scores.get("market_specificity", 0)),
        ("REVENUE VIABILITY", scores.get("revenue_viability", 0)),
        ("COMPETITIVE AWARENESS", scores.get("competitive_awareness", 0)),
        ("TEAM CREDIBILITY", scores.get("team_credibility", 0)),
        ("INVESTOR READINESS", scores.get("investor_readiness", 0)),
    ]

    grid_data = []
    for i in range(0, 6, 3):
        row_labels = [Paragraph(item[0], styles["ScoreBoxLabel"]) for item in score_items[i:i+3]]
        row_vals = [Paragraph(f"{item[1]}/10", styles["ScoreBoxValue"]) for item in score_items[i:i+3]]
        grid_data.append(row_labels)
        grid_data.append(row_vals)

    t_grid = Table(grid_data, colWidths=[5.33 * cm] * 3)
    t_grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, BRASS_GOLD),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BRASS_GOLD),
    ]))
    story.append(t_grid)
    story.append(Spacer(1, 10))

    if feedback:
        story.append(Paragraph(f"<b>Quality Gate Recommendation:</b> {feedback}", styles["FeedbackBox"]))

    story.append(Spacer(1, 10))

    # 5-Step Pitch Content
    story.append(Paragraph("DETAILED 5-STEP PITCH SUBMISSION", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BRASS_GOLD, spaceAfter=10))

    steps = [
        ("Step 1: Solution Approach & Mechanics", pitch_responses.get("step1", "N/A")),
        ("Step 2: Target User / Impact & Pain Point", pitch_responses.get("step2", "N/A")),
        ("Step 3: Cost Justification & Value Model", pitch_responses.get("step3", "N/A")),
        ("Step 4: Alternative Approaches & Edge", pitch_responses.get("step4", "N/A")),
        ("Step 5: Solver Background & Advantage", pitch_responses.get("step5", "N/A")),
    ]

    for title, content in steps:
        story.append(Paragraph(title, styles["SectionHeader"]))
        story.append(Paragraph(content, styles["BodyContent"]))
        story.append(Spacer(1, 4))

    doc.build(story, onFirstPage=_editorial_canvas, onLaterPages=_editorial_canvas)
    return buffer.getvalue()
