from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Proposal, Problem
from schemas import SolverProfileResponse, RecentSubmission

router = APIRouter(prefix="/solver", tags=["Solver Profile"])

@router.get("/{solver_id}", response_model=SolverProfileResponse)
def get_solver_profile(solver_id: str, db: Session = Depends(get_db)):
    solver = db.query(User).filter(User.id == solver_id).first()
    if not solver:
        raise HTTPException(status_code=404, detail="Solver not found")

    proposals = db.query(Proposal).filter(Proposal.solver_id == solver_id).all()
    total_proposals = len(proposals)

    passed_first_attempt = sum(1 for p in proposals if p.status == "submitted")
    avg_score_10 = sum(p.average_score for p in proposals) / max(total_proposals, 1)
    credibility_5 = round(avg_score_10 / 2.0, 1)

    categories = list(set(p.problem.category for p in proposals if p.problem))

    recent = []
    for p in sorted(proposals, key=lambda x: x.created_at, reverse=True)[:5]:
        recent.append(RecentSubmission(
            proposal_id=p.id,
            problem_id=p.problem_id,
            problem_title=p.problem.title if p.problem else "Problem",
            category=p.problem.category if p.problem else "General",
            score=p.average_score,
            status=p.status
        ))

    return SolverProfileResponse(
        solver_id=solver.id,
        name=solver.full_name,
        credibility_score=credibility_5,
        total_proposals=total_proposals,
        passed_first_attempt=passed_first_attempt,
        average_score_across_all=round(avg_score_10, 1),
        categories=categories if categories else ["General"],
        member_since=solver.created_at,
        recent_submissions=recent
    )
