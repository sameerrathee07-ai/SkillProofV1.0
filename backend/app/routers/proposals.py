from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Proposal, Problem, User, PitchSession
from app.schemas import ProposalResponse, ScoreResponse
from app.auth import get_current_user, require_role
from engine import score_pitch, gate_decision, generate_suggestions, parse_pitch_lines

router = APIRouter(prefix="/proposals", tags=["proposals"])

@router.get("/mine", response_model=list[ProposalResponse])
def list_my_proposals(db: Session = Depends(get_db), user = Depends(require_role(["solver"]))):
    proposals = db.query(Proposal).filter(Proposal.solver_id == user.id).order_by(Proposal.created_at.desc()).all()
    result = []
    for p in proposals:
        solver = db.query(User).filter(User.id == p.solver_id).first()
        result.append(ProposalResponse(
            id=p.id, problem_id=p.problem_id, solver_id=p.solver_id,
            gate_score=p.gate_score / 10.0, dimension_scores=p.dimension_scores or [],
            feedback=p.feedback or "", status=p.status, attempts=p.attempts,
            created_at=p.created_at, solver_name=solver.name if solver else "Unknown"
        ))
    return result

@router.get("/problems/{problem_id}", response_model=list[ProposalResponse])
def list_problem_proposals(problem_id: int, db: Session = Depends(get_db), user = Depends(require_role(["poster"]))):
    problem = db.query(Problem).filter(Problem.id == problem_id, Problem.poster_id == user.id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    proposals = db.query(Proposal).filter(Proposal.problem_id == problem_id, Proposal.status == "submitted").all()
    result = []
    for p in proposals:
        solver = db.query(User).filter(User.id == p.solver_id).first()
        credibility = compute_credibility(db, p.solver_id)
        result.append(ProposalResponse(
            id=p.id, problem_id=p.problem_id, solver_id=p.solver_id,
            gate_score=p.gate_score / 10.0, dimension_scores=p.dimension_scores or [],
            feedback=p.feedback or "", status=p.status, attempts=p.attempts,
            created_at=p.created_at, solver_name=solver.name if solver else "Unknown",
            solver_credibility=credibility
        ))
    result.sort(key=lambda x: (-x.gate_score, -(x.solver_credibility.get("avg_gate_score", 0) if x.solver_credibility else 0)))
    return result

@router.post("/{proposal_id}/revise", response_model=ScoreResponse)
def revise_proposal(proposal_id: int, db: Session = Depends(get_db), user = Depends(require_role(["solver"]))):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id, Proposal.solver_id == user.id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.status != "needs_work":
        raise HTTPException(status_code=400, detail="Only needs_work proposals can be revised")
    
    session = db.query(PitchSession).filter(PitchSession.id == proposal.pitch_session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Pitch session not found")
    
    session.completed = False
    session.current_step = 1
    session.attempt_no += 1
    session.pitch_text = ""
    db.commit()
    
    proposal.status = "needs_work"
    db.commit()
    
    return ScoreResponse(passed=False, gate_score=0, dimension_scores=[], feedback="Pitch reset. Start from Step 1.", proposal_id=proposal.id)

def compute_credibility(db: Session, user_id: int) -> dict:
    proposals = db.query(Proposal).filter(Proposal.solver_id == user_id, Proposal.status == "submitted").all()
    if not proposals:
        return {"avg_gate_score": 0.0, "first_attempt_passes": 0, "total_passes": 0, "total_attempts": 0}
    
    total_gate = sum(p.gate_score for p in proposals) / 10.0
    first_attempt = sum(1 for p in proposals if p.attempts == 1)
    total_passes = len(proposals)
    total_attempts = sum(p.attempts for p in proposals)
    
    return {
        "avg_gate_score": round(total_gate / len(proposals), 2),
        "first_attempt_passes": first_attempt,
        "total_passes": total_passes,
        "total_attempts": total_attempts
    }