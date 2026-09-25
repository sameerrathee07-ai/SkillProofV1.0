import io
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from app.database import get_db
from app.models import Proposal, Problem, User, PitchSession
from app.auth import get_current_user
from engine import generate_outline, parse_pitch_lines

router = APIRouter(prefix="/pdf", tags=["pdf"])

DARK_BG = HexColor("#1a1a2e")
ACCENT = HexColor("#00d4aa")
TEXT_WHITE = HexColor("#ffffff")
TEXT_GRAY = HexColor("#cccccc")
RED = HexColor("#ff6b6b")
BLUE = HexColor("#4dabf7")
GREEN = HexColor("#51cf66")

def draw_radar_chart(c, center_x, center_y, radius, scores, labels):
    import math
    n = len(labels)
    angle_step = 360 / n
    
    for ring in range(1, 6):
        r = radius * ring / 5
        c.setStrokeColor(HexColor("#333333"))
        c.setLineWidth(0.5)
        points = []
        for i in range(n):
            angle = (i * angle_step - 90) * math.pi / 180
            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)
            points.append((x, y))
        for i in range(n):
            c.line(points[i][0], points[i][1], points[(i+1)%n][0], points[(i+1)%n][1])
    
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    points = []
    for i, score in enumerate(scores):
        angle = (i * angle_step - 90) * math.pi / 180
        r = radius * score / 10
        x = center_x + r * math.cos(angle)
        y = center_y + r * math.sin(angle)
        points.append((x, y))
    for i in range(n):
        c.line(points[i][0], points[i][1], points[(i+1)%n][0], points[(i+1)%n][1])
    
    c.setFillColor(ACCENT)
    c.setFont("Helvetica", 7)
    for i, (score, label) in enumerate(zip(scores, labels)):
        angle = (i * angle_step - 90) * math.pi / 180
        r = radius * 1.15
        x = center_x + r * math.cos(angle)
        y = center_y + r * math.sin(angle)
        c.drawCentredString(x, y - 4, label[:12])

def draw_score_bars(c, x, y, width, height, scores, labels):
    c.setFont("Helvetica", 9)
    bar_height = 18
    gap = 6
    for i, (score, label) in enumerate(zip(scores, labels)):
        bar_y = y - i * (bar_height + gap)
        c.setFillColor(HexColor("#333333"))
        c.rect(x, bar_y, width, bar_height, fill=1, stroke=0)
        
        if score >= 7:
            color = GREEN
        elif score >= 5:
            color = BLUE
        else:
            color = RED
        
        bar_width = width * score / 10
        c.setFillColor(color)
        c.rect(x, bar_y, bar_width, bar_height, fill=1, stroke=0)
        
        c.setFillColor(TEXT_WHITE)
        c.drawString(x + 5, bar_y + 4, label)
        c.drawRightString(x + width - 5, bar_y + 4, f"{score}/10")

@router.get("/proposals/{proposal_id}")
def download_proposal_pdf(proposal_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if proposal.status != "submitted":
        raise HTTPException(status_code=403, detail="Proposal not submitted")
    
    if user.role == "solver" and proposal.solver_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if user.role == "poster":
        problem = db.query(Problem).filter(Problem.id == proposal.problem_id, Problem.poster_id == user.id).first()
        if not problem:
            raise HTTPException(status_code=403, detail="Forbidden")
    
    solver = db.query(User).filter(User.id == proposal.solver_id).first()
    problem = db.query(Problem).filter(Problem.id == proposal.problem_id).first()
    session = db.query(PitchSession).filter(PitchSession.id == proposal.pitch_session_id).first()
    
    outline = generate_outline(session.pitch_text if session else "", solver.name if solver else "Solver")
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    c.setFillColor(DARK_BG)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height - 150, "PROPOSAL")
    
    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 200, outline["Solution"][:80])
    
    c.setFont("Helvetica", 11)
    c.drawCentredString(width/2, height - 230, f"Prepared by: {solver.name if solver else 'Solver'}")
    c.drawCentredString(width/2, height - 250, f"Problem: #{proposal.problem_id} — {problem.category if problem else 'Unknown'}")
    c.drawCentredString(width/2, height - 270, f"Date: {datetime.utcnow().strftime('%B %d, %Y')}")
    c.drawCentredString(width/2, height - 290, f"Overall Score: {proposal.gate_score}/100")
    
    c.showPage()
    
    c.setFillColor(DARK_BG)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, height - 72, "DIMENSION SCORES")
    
    scores = [d["score"] for d in proposal.dimension_scores]
    labels = [d["name"] for d in proposal.dimension_scores]
    draw_radar_chart(c, width/2, height - 280, 120, scores, labels)
    
    draw_score_bars(c, 72, height - 460, width - 144, 18, scores, labels)
    
    c.setFillColor(TEXT_GRAY)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(72, height - 620, f"Feedback: {proposal.feedback}")
    
    c.showPage()
    
    sections = [
        ("PROBLEM", outline["Problem"]),
        ("SOLUTION", outline["Solution"]),
        ("AFFECTED PEOPLE", outline["Affected People"]),
        ("COST AND VALUE", outline["Cost and Value"]),
        ("ALTERNATIVES AND EDGE", outline["Alternatives and Edge"]),
        ("SOLVER AND ADVANTAGE", outline["Solver and Advantage"]),
        ("PROPOSED NEXT STEP", outline["Proposed Next Step"]),
    ]
    
    for title, content in sections:
        c.setFillColor(DARK_BG)
        c.rect(0, 0, width, height, fill=1, stroke=0)
        
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, height - 72, title)
        
        c.setFillColor(TEXT_WHITE)
        c.setFont("Helvetica", 11)
        
        text = c.beginText(72, height - 120)
        text.setFont("Helvetica", 11)
        text.setFillColor(TEXT_WHITE)
        
        for line in content.split('\n'):
            if text.getY() < 72:
                c.drawText(text)
                c.showPage()
                c.setFillColor(DARK_BG)
                c.rect(0, 0, width, height, fill=1, stroke=0)
                text = c.beginText(72, height - 72)
                text.setFont("Helvetica", 11)
                text.setFillColor(TEXT_WHITE)
            text.textLine(line)
        
        c.drawText(text)
        c.showPage()
    
    c.setFillColor(DARK_BG)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(TEXT_GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(72, 72, f"Generated by SkillProof | Proposal #{proposal.id} | {datetime.utcnow().isoformat()}Z")
    c.drawString(72, 56, "No external AI models were used.")
    
    c.save()
    
    proposal.pdf_downloads += 1
    db.commit()
    
    buffer.seek(0)
    return Response(
        content=buffer.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="proposal_{proposal_id}.pdf"'}
    )