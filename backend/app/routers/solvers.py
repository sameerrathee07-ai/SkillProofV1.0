from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Proposal, User
from app.schemas import CredibilityResponse
from app.auth import get_current_user

router = APIRouter(prefix="/solvers", tags=["solvers"])

@router.get("/{solver_id}/credibility", response_model=CredibilityResponse)
def get_solver_credibility(solver_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    solver = db.query(User).filter(User.id == solver_id).first()
    if not solver:
        raise HTTPException(status_code=404, detail="Solver not found")
    
    proposals = db.query(Proposal).filter(Proposal.solver_id == solver_id, Proposal.status == "submitted").all()
    if not proposals:
        return CredibilityResponse(
            user_id=solver_id, avg_gate_score=0.0, first_attempt_passes=0, total_passes=0, total_attempts=0
        )
    
    total_gate = sum(p.gate_score for p in proposals) / 10.0
    first_attempt = sum(1 for p in proposals if p.attempts == 1)
    total_passes = len(proposals)
    total_attempts = sum(p.attempts for p in proposals)
    
    return CredibilityResponse(
        user_id=solver_id,
        avg_gate_score=round(total_gate / len(proposals), 2),
        first_attempt_passes=first_attempt,
        total_passes=total_passes,
        total_attempts=total_attempts
    )