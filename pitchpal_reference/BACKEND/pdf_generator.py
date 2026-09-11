from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Line
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.graphics import renderPDF

DARK_BG = HexColor("#0a0a0f")
GOLD = HexColor("#f0c040")
GOLD_DIM = HexColor("#c49632")
WHITE = HexColor("#ffffff")
GRAY = HexColor("#6b6b6b")
LIGHT_GRAY = HexColor("#2a2a2f")
CARD_BG = HexColor("#14141a")

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm


def _register_fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os

    font_dir = os.path.join(os.path.dirname(__file__), "fonts")
    if os.path.exists(font_dir):
        for fname in os.listdir(font_dir):
            if fname.endswith(".ttf"):
                try:
                    pdfmetrics.registerFont(TTFont(fname[:-4], os.path.join(font_dir, fname)))
                except Exception:
                    pass


_register_fonts()


def _get_font(name: str) -> str:
    return name


HEADING_FONT = "Helvetica-Bold"
MONO_FONT = "Courier"
BODY_FONT = "Helvetica"


def _dark_canvas(canvas: canvas.Canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, MARGIN, PAGE_W - MARGIN, MARGIN)
    canvas.line(MARGIN, PAGE_H - MARGIN, PAGE_W - MARGIN, PAGE_H - MARGIN)

    canvas.setFont(MONO_FONT, 7)
    canvas.setFillColor(GRAY)
    canvas.drawString(MARGIN, MARGIN - 8, f"PitchPal — Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC")
    canvas.drawRightString(PAGE_W - MARGIN, MARGIN - 8, f"Page {doc.page}")
    canvas.restoreState()


def _styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CoverTitle",
        fontName=HEADING_FONT,
        fontSize=36,
        leading=44,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        fontName=MONO_FONT,
        fontSize=14,
        leading=18,
        textColor=GOLD,
        alignment=TA_CENTER,
        spaceAfter=24,
    ))
    styles.add(ParagraphStyle(
        name="CoverMeta",
        fontName=BODY_FONT,
        fontSize=11,
        leading=16,
        textColor=GRAY,
        alignment=TA_CENTER,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontName=HEADING_FONT,
        fontSize=16,
        leading=22,
        textColor=GOLD,
        spaceBefore=18,
        spaceAfter=10,
        borderWidth=0,
        borderPadding=0,
    ))
    styles.add(ParagraphStyle(
        name="SectionBody",
        fontName=BODY_FONT,
        fontSize=10.5,
        leading=16,
        textColor=WHITE,
        spaceAfter=8,
        leftIndent=4,
    ))
    styles.add(ParagraphStyle(
        name="ScoreLabel",
        fontName=MONO_FONT,
        fontSize=9,
        leading=12,
        textColor=GOLD,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="ScoreValue",
        fontName=HEADING_FONT,
        fontSize=28,
        leading=32,
        textColor=WHITE,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="FeedbackStyle",
        fontName=BODY_FONT,
        fontSize=10,
        leading=15,
        textColor=GOLD,
        leftIndent=8,
        rightIndent=8,
        spaceBefore=6,
        spaceAfter=6,
        backColor=LIGHT_GRAY,
        borderWidth=0.5,
        borderColor=GOLD_DIM,
        borderPadding=8,
    ))
    return styles


def _draw_radar_chart(drawing: Drawing, scores: dict, width: float, height: float):
    chart = SpiderChart()
    chart.x = 20
    chart.y = 10
    chart.width = width - 40
    chart.height = height - 40

    labels = [
        "Problem\nClarity",
        "Market\nSpecificity",
        "Revenue\nViability",
        "Competitive\nAwareness",
        "Team\nCredibility",
        "Investor\nReadiness",
    ]
    data = [[
        scores.get("problem_clarity", 5),
        scores.get("market_specificity", 5),
        scores.get("revenue_viability", 5),
        scores.get("competitive_awareness", 5),
        scores.get("team_credibility", 5),
        scores.get("investor_readiness", 5),
    ]]

    chart.data = data
    chart.labels = labels

    chart.strokeWidth = 2
    chart.strokeColor = GOLD
    chart.fillColor = HexColor("#f0c04033")

    chart.spokes[0].strokeColor = HexColor("#33333a")
    chart.spokes[0].strokeWidth = 0.5
    chart.strands[0].strokeColor = HexColor("#33333a")
    chart.strands[0].strokeWidth = 0.5

    drawing.add(chart)


def build_pdf(
    founder_name: str,
    outline: dict,
    scores: dict,
    feedback: str,
    started_at: datetime,
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

    styles = _styles()
    story = []

    story.append(Spacer(1, 6 * cm))
    story.append(Paragraph("PitchPal", styles["CoverTitle"]))
    story.append(Paragraph("INVESTOR PITCH DECK", styles["CoverSubtitle"]))
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(founder_name, styles["CoverMeta"]))
    story.append(Paragraph(started_at.strftime("%B %d, %Y"), styles["CoverMeta"]))
    story.append(Spacer(1, 2 * cm))

    t = Table([["CONFIDENTIAL — FOR INVESTOR REVIEW ONLY"]], colWidths=[14 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), MONO_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), GRAY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, GOLD_DIM),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
    ]))
    story.append(t)

    story.append(PageBreak())

    story.append(Paragraph("SCORED DIMENSIONS", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD_DIM, spaceAfter=16))

    drawing = Drawing(16 * cm, 9 * cm)
    _draw_radar_chart(drawing, scores, 16 * cm, 9 * cm)
    story.append(drawing)
    story.append(Spacer(1, 12))

    score_items = [
        ("PROBLEM CLARITY", scores.get("problem_clarity", 5)),
        ("MARKET SPECIFICITY", scores.get("market_specificity", 5)),
        ("REVENUE VIABILITY", scores.get("revenue_viability", 5)),
        ("COMPETITIVE AWARENESS", scores.get("competitive_awareness", 5)),
        ("TEAM CREDIBILITY", scores.get("team_credibility", 5)),
        ("INVESTOR READINESS", scores.get("investor_readiness", 5)),
    ]

    score_table_data = []
    for i in range(0, 6, 3):
        row_labels = []
        row_values = []
        for label, val in score_items[i:i+3]:
            row_labels.append(Paragraph(label, styles["ScoreLabel"]))
            row_values.append(Paragraph(str(val), styles["ScoreValue"]))
        while len(row_labels) < 3:
            row_labels.append(Paragraph("", styles["ScoreLabel"]))
            row_values.append(Paragraph("", styles["ScoreValue"]))
        score_table_data.append(row_labels)
        score_table_data.append(row_values)

    score_table = Table(score_table_data, colWidths=[5.33 * cm] * 3)
    score_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, GOLD_DIM),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, GOLD_DIM),
    ]))
    story.append(score_table)

    story.append(Spacer(1, 16))
    story.append(Paragraph(f"KEY FEEDBACK: {feedback}", styles["FeedbackStyle"]))

    story.append(PageBreak())

    story.append(Paragraph("PITCH OUTLINE", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD_DIM, spaceAfter=16))

    sections = [
        ("PROBLEM", outline.get("problem", "")),
        ("SOLUTION", outline.get("solution", "")),
        ("CUSTOMER", outline.get("customer", "")),
        ("BUSINESS MODEL", outline.get("business_model", "")),
        ("COMPETITION", outline.get("competition", "")),
        ("TEAM", outline.get("team", "")),
        ("THE ASK", outline.get("ask", "")),
    ]

    for title, body in sections:
        story.append(Paragraph(title, styles["SectionTitle"]))
        story.append(Paragraph(body or "Not specified.", styles["SectionBody"]))

    doc.build(story, onFirstPage=_dark_canvas, onLaterPages=_dark_canvas)
    return buffer.getvalue()


if __name__ == "__main__":
    test_outline = {
        "problem": "Founders waste hours crafting vague pitches that investors reject instantly.",
        "solution": "PitchPal automatically validates startup pitch answers and pushes back with targeted coaching to sharpen them.",
        "customer": "Students aged 18 to 24 hate wasting hours preparing vague pitches and feel stuck without expert feedback.",
        "business_model": "We charge 49 rupees monthly for students and 99 rupees yearly for teams who pay per subscription.",
        "competition": "ChatGPT, Claude and Grammarly give generic advice, but PitchPal uniquely validates structure step by step.",
        "team": "I have five years of experience building fintech products and my unfair advantage is direct access to bank data.",
        "ask": "Seeking investment to accelerate growth and capture market share.",
    }
    test_scores = {
        "problem_clarity": 8,
        "market_specificity": 7,
        "revenue_viability": 6,
        "competitive_awareness": 8,
        "team_credibility": 7,
        "investor_readiness": 6,
    }
    test_feedback = "The money model needs a price and a recurring frequency."
    pdf_bytes = build_pdf("Test Founder", test_outline, test_scores, test_feedback, datetime.utcnow())
    with open("test_pitchpal.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("Generated test_pitchpal.pdf")