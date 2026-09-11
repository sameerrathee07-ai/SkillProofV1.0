from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Problem, Pitch, Proposal
from auth import hash_password
from scoring import score_pitch_responses

router = APIRouter(prefix="/admin", tags=["Admin & Seed"])

@router.post("/seed/problems")
def seed_problems(db: Session = Depends(get_db)):
    # Ensure poster exists
    poster = db.query(User).filter(User.email == "poster@demo.com").first()
    if not poster:
        poster = User(
            full_name="Grand Hyatt Operations",
            organization="Grand Hyatt Hotels",
            email="poster@demo.com",
            password_hash=hash_password("password123"),
            role="poster"
        )
        db.add(poster)
        db.commit()
        db.refresh(poster)

    demo_problems = [
        {
            "title": "Automate Guest Check-In & Digital Room Key Dispatch",
            "description": "Our 120-room boutique hotel handles 50+ manual check-ins daily, causing 20-minute front desk bottlenecks during peak 3 PM arrival hours. We need an automated mobile or kiosk system with QR check-in and digital key generation.",
            "category": "Hospitality",
            "budget_range": "₹25,000 - ₹50,000",
            "timeline": "3 weeks"
        },
        {
            "title": "Real-time Room Service Ordering & Kitchen KDS Sync",
            "description": "Room service orders are currently taken over phone and handwritten on tickets, leading to 15% order errors and delayed billing. We require a QR-based room ordering Web App syncing directly with kitchen display monitors.",
            "category": "Hospitality",
            "budget_range": "₹15,000 - ₹35,000",
            "timeline": "2 weeks"
        },
        {
            "title": "Automated Reconciliation Engine for UPI & Card POS",
            "description": "Our retail chain processes 500+ daily transactions across 4 stores. End-of-day bank statement reconciliation takes 3 hours manually and misses chargeback discrepancies. We need a Python automated reconciliation script with ledger export.",
            "category": "Financial Services",
            "budget_range": "₹40,000 - ₹80,000",
            "timeline": "4 weeks"
        },
        {
            "title": "Micro-Invoicing & Automated GST Compliance Tool",
            "description": "Freelance consultants struggle to generate GST-compliant B2B invoices and calculate GSTR-1 liability breakdown automatically. Need a clean dashboard tool for auto-generating PDF tax invoices.",
            "category": "Financial Services",
            "budget_range": "₹20,000 - ₹30,000",
            "timeline": "2 weeks"
        },
        {
            "title": "Student Attendance Tracking via Smart QR Scanner",
            "description": "University professors spend 10 minutes per lecture calling roll across 80-student lecture halls. We want a time-expiring dynamic QR code system for student attendance validation on smartphones.",
            "category": "Other",
            "budget_range": "₹10,000 - ₹20,000",
            "timeline": "1 week"
        }
    ]

    created = []
    for dp in demo_problems:
        p = Problem(
            poster_id=poster.id,
            title=dp["title"],
            description=dp["description"],
            category=dp["category"],
            budget_range=dp["budget_range"],
            timeline=dp["timeline"],
            status="published"
        )
        db.add(p)
        created.append(p)

    db.commit()
    return {"message": f"Successfully seeded {len(created)} demo problems", "poster_id": poster.id}

@router.post("/seed/solvers")
def seed_solvers(db: Session = Depends(get_db)):
    solvers_data = [
        {"name": "Sarah Chen", "email": "sarah.chen@solver.com", "org": "IIT Bombay"},
        {"name": "Raj Patel", "email": "raj.patel@solver.com", "org": "BITS Pilani"},
        {"name": "Maya Sharma", "email": "maya.sharma@solver.com", "org": "Delhi Tech Univ"}
    ]

    created_ids = []
    for s in solvers_data:
        u = db.query(User).filter(User.email == s["email"]).first()
        if not u:
            u = User(
                full_name=s["name"],
                email=s["email"],
                organization=s["org"],
                password_hash=hash_password("password123"),
                role="solver"
            )
            db.add(u)
            db.commit()
            db.refresh(u)
        created_ids.append(u.id)

    return {"message": "Successfully seeded demo solver accounts", "solver_ids": created_ids}

@router.post("/seed/full-demo-loop")
def seed_full_demo_loop(db: Session = Depends(get_db)):
    # Run seed problems & solvers first
    seed_problems(db)
    seed_solvers(db)

    poster = db.query(User).filter(User.email == "poster@demo.com").first()
    solver = db.query(User).filter(User.email == "sarah.chen@solver.com").first()
    problem = db.query(Problem).filter(Problem.category == "Hospitality").first()

    # Create active pitch & proposal
    responses = {
        "step1": "We build a web-based mobile check-in portal that allows hotel guests to scan a QR code at arrival, verify identity, and instantly receive a digital web key.",
        "step2": "Front desk managers at 120-room boutique hotels who face severe 20-minute arrival bottlenecks and manual registration paperwork daily.",
        "step3": "We charge a ₹3,000 monthly subscription per hotel location, saving the hotel ₹15,000 monthly in front desk staff overtime.",
        "step4": "Compared to generic physical keycard encoders and manual paper forms, our solution requires zero app download and connects directly via Web Bluetooth.",
        "step5": "I have 3 years of web app development experience and built the guest Wi-Fi portal at Marriott during my internship."
    }

    pitch = Pitch(
        solver_id=solver.id,
        problem_id=problem.id,
        current_step=5,
        step1_response=responses["step1"],
        step2_response=responses["step2"],
        step3_response=responses["step3"],
        step4_response=responses["step4"],
        step5_response=responses["step5"],
        status="submitted"
    )
    db.add(pitch)
    db.commit()
    db.refresh(pitch)

    scoring = score_pitch_responses(responses)
    proposal = Proposal(
        pitch_id=pitch.id,
        problem_id=problem.id,
        solver_id=solver.id,
        dimension_scores=scoring["dimension_scores"],
        average_score=scoring["average_score"],
        feedback=scoring["feedback"],
        status="submitted"
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    return {
        "message": "Full demo loop created successfully!",
        "problem_id": problem.id,
        "solver_id": solver.id,
        "proposal_id": proposal.id,
        "score": scoring["average_score"],
        "status": proposal.status
    }

@router.delete("/clear")
def clear_all_data(db: Session = Depends(get_db)):
    db.query(Proposal).delete()
    db.query(Pitch).delete()
    db.query(Problem).delete()
    db.query(User).delete()
    db.commit()
    return {"message": "All database tables cleared!"}
