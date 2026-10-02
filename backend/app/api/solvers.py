from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.engine import compute_credibility
from app.schemas import CredibilityResponse
from app.models import User, Proposal

router = APIRouter(prefix="/solvers", tags=["solvers"])


@router.get("/{solver_id}/credibility", response_model=CredibilityResponse)
def get_credibility(
    solver_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    solver = db.query(User).filter(User.id == solver_id).first()
    if not solver:
        raise HTTPException(status_code=404, detail="Solver not found")
    
    proposals = db.query(Proposal).filter(Proposal.solver_id == solver_id).all()
    proposal_data = [
        {"status": p.status.value, "gate_score": p.gate_score, "attempts": p.attempts}
        for p in proposals
    ]
    
    credibility = compute_credibility(proposal_data)
    return CredibilityResponse(**credibility)