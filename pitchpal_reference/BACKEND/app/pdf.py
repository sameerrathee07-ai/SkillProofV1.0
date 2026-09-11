"""PDF generation with ReportLab — dark theme, radar chart, 7 sections.

Pure function: generate_pdf_bytes(outline, scores, session_id) -> bytes.
"""

import io
import json
from datetime import datetime

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# Color palette matching the design system
CANVAS = HexColor("#181715")          # --color-navy
CANVAS_ELEVATED = HexColor("#252320") # --color-navy-elevated
INK = HexColor("#FAF9F5")             # --color-canvas (used as text on dark)
MUTED = HexColor("#8E8B82")           # --color-muted-soft
HAIRLINE = HexColor("#E6DFD8")        # --color-hairline (borders)
CORAL = HexColor("#CC785C")           # --color-coral
CORAL_DIM = HexColor("#F5E8DF")       # --color-coral-dim
GOLD = HexColor("#F0C040")            # --color-gold


PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
CONTENT_W = PAGE_W - 2 * MARGIN


def generate_pdf_bytes(
    outline: dict,
    scores: dict,
    session_id: int,
    founder_name: str = "Founder",
) -> bytes:
    """Generate a dark-theme PDF pitch deck and return bytes."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Register fonts (fallback to built-in if not available)
    try:
        pdfmetrics.registerFont(TTFont("Cormorant", "CormorantGaramond-Regular.ttf"))
        pdfmetrics.registerFont(TTFont("Cormorant-Bold", "CormorantGaramond-Bold.ttf"))
        pdfmetrics.registerFont(TTFont("Inter", "Inter-Regular.ttf"))
        pdfmetrics.registerFont(TTFont("Inter-Bold", "Inter-Bold.ttf"))
        pdfmetrics.registerFont(TTFont("JetBrainsMono", "JetBrainsMono-Regular.ttf"))
        DISPLAY_FONT = "Cormorant"
        DISPLAY_BOLD = "Cormorant-Bold"
        BODY_FONT = "Inter"
        BODY_BOLD = "Inter-Bold"
        MONO_FONT = "JetBrainsMono"
    except Exception:
        # Fallback to built-in fonts
        DISPLAY_FONT = "Helvetica"
        DISPLAY_BOLD = "Helvetica-Bold"
        BODY_FONT = "Helvetica"
        BODY_BOLD = "Helvetica-Bold"
        MONO_FONT = "Courier"

    def draw_radar_chart(cx: float, cy: float, radius: float, values: dict) -> None:
        """Draw a 6-axis radar chart centered at (cx, cy)."""
        dims = [
            ("problem_clarity", "Problem\nClarity"),
            ("market_specificity", "Market\nSpecificity"),
            ("revenue_viability", "Revenue\nViability"),
            ("competitive_awareness", "Competitive\nAwareness"),
            ("team_credibility", "Team\nCredibility"),
            ("investor_readiness", "Investor\nReadiness"),
        ]
        n = len(dims)
        angles = [2 * 3.14159 * i / n - 3.14159 / 2 for i in range(n)]

        # Background circles
        for ring in [0.2, 0.4, 0.6, 0.8, 1.0]:
            r = radius * ring
            c.setStrokeColor(HAIRLINE)
            c.setLineWidth(0.5)
            c.circle(cx, cy, r, stroke=1, fill=0)

        # Axes
        c.setStrokeColor(MUTED)
        c.setLineWidth(0.5)
        for angle in angles:
            x = cx + radius * 1.05 * (angle > 0 and 1 or -1) * 0.01  # tiny offset
            y = cy + radius * 1.05
            c.line(cx, cy, cx + radius * 1.1 * (angle if angle < 3.14 else angle), cy)

        # Data polygon
        points = []
        for i, (key, _) in enumerate(dims):
            val = values.get(key, 5) / 10.0
            r = radius * val
            x = cx + r * (1 if angles[i] < 3.14 else 1) * (angles[i] % 3.14) / 1.57
            # Simplified: use cos/sin
            import math
            x = cx + r * math.cos(angles[i])
            y = cy + r * math.sin(angles[i])
            points.append((x, y))

        # Fill
        c.setFillColor(GOLD)
        c.setFillAlpha(0.25)
        if len(points) >= 3:
            path = c.beginPath()
            path.moveTo(points[0][0], points[0][1])
            for px, py in points[1:]:
                path.lineTo(px, py)
            path.close()
            c.drawPath(path, fill=1, stroke=0)

        # Stroke
        c.setFillAlpha(1.0)
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        if len(points) >= 3:
            path = c.beginPath()
            path.moveTo(points[0][0], points[0][1])
            for px, py in points[1:]:
                path.lineTo(px, py)
            path.close()
            c.drawPath(path, fill=0, stroke=1)

        # Labels
        c.setFont(BODY_FONT, 8)
        c.setFillColor(MUTED)
        for i, (_, label) in enumerate(dims):
            angle = angles[i]
            label_r = radius * 1.18
            import math
            lx = cx + label_r * math.cos(angle)
            ly = cy + label_r * math.sin(angle)
            c.drawCentredString(lx, ly, label.split("\n")[0])

    def draw_section_header(y: float, title: str) -> float:
        """Draw a section header and return new y position."""
        c.setFont(DISPLAY_BOLD, 16)
        c.setFillColor(CORAL)
        c.drawString(MARGIN, y, title.upper())
        y -= 8 * mm
        # Hairline
        c.setStrokeColor(HAIRLINE)
        c.setLineWidth(0.5)
        c.line(MARGIN, y, PAGE_W - MARGIN, y)
        y -= 6 * mm
        return y

    def draw_body_text(y: float, text: str, font_size: int = 10, leading: int = 14, color=INK) -> float:
        """Draw wrapped body text and return new y position."""
        c.setFont(BODY_FONT, font_size)
        c.setFillColor(color)
        text_obj = c.beginText(MARGIN, y)
        text_obj.setLeading(leading)
        for line in text.split("\n"):
            # Simple word wrap
            words = line.split(" ")
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if c.stringWidth(test_line, BODY_FONT, font_size) > CONTENT_W:
                    text_obj.textLine(current_line)
                    current_line = word
                else:
                    current_line = test_line
            if current_line:
                text_obj.textLine(current_line)
        c.drawText(text_obj)
        return text_obj.getY() - 4 * mm

    # ===== PAGE 1: COVER =====
    c.setFillColor(CANVAS)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Title
    y = PAGE_H - 60 * mm
    c.setFont(DISPLAY_BOLD, 42)
    c.setFillColor(INK)
    c.drawCentredString(PAGE_W / 2, y, "PITCH DECK")
    y -= 12 * mm

    c.setFont(DISPLAY_FONT, 28)
    c.setFillColor(CORAL)
    c.drawCentredString(PAGE_W / 2, y, outline.get("solution", "Untitled Pitch"))
    y -= 10 * mm

    c.setFont(BODY_FONT, 12)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, y, f"Prepared by {founder_name}")
    y -= 6 * mm
    c.drawCentredString(PAGE_W / 2, y, f"Session #{session_id} · {datetime.now().strftime('%B %d, %Y')}")

    # Divider
    y -= 10 * mm
    c.setStrokeColor(CORAL)
    c.setLineWidth(2)
    c.line(PAGE_W / 2 - 40 * mm, y, PAGE_W / 2 + 40 * mm, y)

    # Score summary
    y -= 10 * mm
    c.setFont(DISPLAY_BOLD, 18)
    c.setFillColor(GOLD)
    overall = sum(scores.get(k, 5) for k in [
        "problem_clarity", "market_specificity", "revenue_viability",
        "competitive_awareness", "team_credibility", "investor_readiness"
    ]) / 6
    c.drawCentredString(PAGE_W / 2, y, f"Overall Score: {overall * 10:.0f} / 100")

    c.showPage()

    # ===== PAGE 2: RADAR + SCORES =====
    c.setFillColor(CANVAS)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    y = PAGE_H - MARGIN
    c.setFont(DISPLAY_BOLD, 24)
    c.setFillColor(INK)
    c.drawString(MARGIN, y, "Six-Dimension Assessment")
    y -= 10 * mm

    # Radar chart centered
    radar_cx = PAGE_W / 2
    radar_cy = y - 55 * mm
    draw_radar_chart(radar_cx, radar_cy, 50 * mm, scores)
    y = radar_cy - 55 * mm

    # Score breakdown
    y -= 5 * mm
    c.setFont(DISPLAY_BOLD, 16)
    c.setFillColor(CORAL)
    c.drawString(MARGIN, y, "Score Breakdown")
    y -= 8 * mm

    dim_labels = {
        "problem_clarity": "Problem Clarity",
        "market_specificity": "Market Specificity",
        "revenue_viability": "Revenue Viability",
        "competitive_awareness": "Competitive Awareness",
        "team_credibility": "Team Credibility",
        "investor_readiness": "Investor Readiness",
    }

    for key, label in dim_labels.items():
        val = scores.get(key, 5)
        c.setFont(BODY_BOLD, 11)
        c.setFillColor(INK)
        c.drawString(MARGIN + 10 * mm, y, f"{label}")
        c.setFont(MONO_FONT, 24)
        c.setFillColor(GOLD if val >= 7 else CORAL if val >= 5 else MUTED)
        c.drawRightString(PAGE_W - MARGIN - 10 * mm, y, f"{val}/10")
        y -= 7 * mm

    # Feedback callout
    y -= 4 * mm
    c.setFillColor(CORAL_DIM)
    c.setStrokeColor(CORAL)
    c.setLineWidth(1)
    c.roundRect(MARGIN, y - 14 * mm, CONTENT_W, 16 * mm, 4 * mm, fill=1, stroke=1)
    c.setFont(BODY_BOLD, 10)
    c.setFillColor(CORAL)
    c.drawString(MARGIN + 6 * mm, y - 4 * mm, "Where to focus next:")
    c.setFont(BODY_FONT, 10)
    c.setFillColor(INK)
    c.drawString(MARGIN + 6 * mm, y - 10 * mm, scores.get("feedback", ""))
    y -= 20 * mm

    c.showPage()

    # ===== PAGES 3+: OUTLINE SECTIONS =====
    sections = [
        ("Problem", "problem"),
        ("Solution", "solution"),
        ("Target Customer", "customer"),
        ("Business Model", "business_model"),
        ("Competition & Edge", "competition"),
        ("Team & Advantage", "team"),
        ("The Ask", "ask"),
    ]

    for title, key in sections:
        c.setFillColor(CANVAS)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

        y = PAGE_H - MARGIN
        y = draw_section_header(y, title)
        y = draw_body_text(y, outline.get(key, "Not specified."), font_size=11, leading=16)
        c.showPage()

    # ===== FINAL PAGE: FOOTER / DISCLOSURE =====
    c.setFillColor(CANVAS)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    y = PAGE_H / 2
    c.setFont(BODY_FONT, 9)
    c.setFillColor(MUTED)
    c.drawCentredString(PAGE_W / 2, y, "Generated by PitchPal AI Coach")
    y -= 6 * mm
    c.drawCentredString(PAGE_W / 2, y, f"Session #{session_id} · {datetime.now().isoformat()}")
    y -= 6 * mm
    c.drawCentredString(PAGE_W / 2, y, "This document was generated by a rule-based validation engine.")
    y -= 4 * mm
    c.drawCentredString(PAGE_W / 2, y, "No external AI models were used in its creation.")

    c.save()
    buffer.seek(0)
    return buffer.getvalue()


if __name__ == "__main__":
    # Smoke test
    outline = {
        "problem": "Founders waste hours crafting vague pitches.",
        "solution": "PitchPal automatically validates startup pitch answers.",
        "customer": "Students aged 18-24 who struggle with pitch prep.",
        "business_model": "49 rupees monthly for students, 99 rupees yearly for teams.",
        "competition": "Unlike ChatGPT and Grammarly, PitchPal validates structure step by step.",
        "team": "Five years building fintech products. Unfair advantage: direct bank data access.",
        "ask": "Seeking investment to accelerate growth and capture market share.",
        "founder_name": "Test Founder",
    }
    scores = {
        "problem_clarity": 8, "market_specificity": 7, "revenue_viability": 6,
        "competitive_awareness": 8, "team_credibility": 7, "investor_readiness": 6,
        "feedback": "The money model needs a price and a recurring frequency.",
    }
    pdf_bytes = generate_pdf_bytes(outline, scores, 123, "Test Founder")
    assert len(pdf_bytes) > 1000
    assert pdf_bytes[:4] == b"%PDF"
    print(f"OK - PDF generated: {len(pdf_bytes)} bytes")