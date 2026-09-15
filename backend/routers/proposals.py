from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import User, Problem, Pitch, Proposal
from schemas import ProposalResponse, ProposalListResponse, ProposalItem
from auth import get_current_user
from pdf_service import generate_proposal_pdf

router = APIRouter(prefix="", tags=["Proposals"])

@router.get("/proposals/{proposal_id}", response_model=ProposalResponse)
def get_proposal(
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    problem = proposal.problem
    # Ownership guard: user must be solver or problem poster
    if current_user.id != proposal.solver_id and current_user.id != problem.poster_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this proposal.")

    pitch = proposal.pitch
    solver = proposal.solver

    # Compute solver credibility score
    solver_proposals = db.query(Proposal).filter(Proposal.solver_id == solver.id).all()
    avg_credibility = round(sum(p.average_score for p in solver_proposals) / max(len(solver_proposals), 1) / 2.0, 1)  # 0-5 scale

    return ProposalResponse(
        proposal_id=proposal.id,
        problem_id=problem.id,
        problem_title=problem.title,
        solver_id=solver.id,
        solver_name=solver.full_name,
        solver_credibility_score=avg_credibility,
        pitch_responses={
            "step1": pitch.step1_response or "",
            "step2": pitch.step2_response or "",
            "step3": pitch.step3_response or "",
            "step4": pitch.step4_response or "",
            "step5": pitch.step5_response or "",
        },
        dimension_scores=proposal.dimension_scores,
        average_score=proposal.average_score,
        status=proposal.status,
        feedback=proposal.feedback,
        created_at=proposal.created_at
    )

# In-memory PDF byte cache keyed by proposal_id
_pdf_cache = {}

@router.get("/proposals/{proposal_id}/pdf")
def download_proposal_pdf(
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    problem = proposal.problem
    if current_user.id != proposal.solver_id and current_user.id != problem.poster_id:
        raise HTTPException(status_code=403, detail="Not authorized to download this PDF.")

    pitch = proposal.pitch
    solver = proposal.solver

    if proposal_id in _pdf_cache:
        pdf_bytes = _pdf_cache[proposal_id]
    else:
        pdf_bytes = generate_proposal_pdf(
            solver_name=solver.full_name,
            problem_title=problem.title,
            category=problem.category,
            budget=problem.budget_range,
            timeline=problem.timeline,
            pitch_responses={
                "step1": pitch.step1_response or "",
                "step2": pitch.step2_response or "",
                "step3": pitch.step3_response or "",
                "step4": pitch.step4_response or "",
                "step5": pitch.step5_response or "",
            },
            scores=proposal.dimension_scores,
            average_score=proposal.average_score,
            status=proposal.status,
            feedback=proposal.feedback
        )
        _pdf_cache[proposal_id] = pdf_bytes

    filename = f"proposal_{solver.full_name.replace(' ', '_')}_{proposal.id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Cache-Control": "private, max-age=86400, immutable"
        }
    )

@router.get("/my-proposals", response_model=ProposalListResponse)
def get_my_proposals(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "solver":
        raise HTTPException(status_code=403, detail="Only solvers can view my-proposals dashboard.")

    query = db.query(Proposal).filter(Proposal.solver_id == current_user.id)
    if status and status != "all":
        query = query.filter(Proposal.status == status)

    proposals = query.order_by(Proposal.created_at.desc()).all()
    items = []

    for p in proposals:
        pitch = p.pitch
        problem = p.problem
        weakest = min(p.dimension_scores, key=p.dimension_scores.get) if p.dimension_scores else None

        items.append(ProposalItem(
            proposal_id=p.id,
            problem_id=problem.id,
            problem_title=problem.title,
            category=problem.category,
            status=p.status,
            current_step=pitch.current_step if pitch else 5,
            score=p.average_score,
            weakest_dimension=weakest,
            submitted_at=p.created_at,
            tokens_spent=pitch.tokens_spent if pitch else 0
        ))

    return ProposalListResponse(items=items, total=len(items))

@router.get("/problems/{problem_id}/proposals")
def get_problem_proposals(
    problem_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    if current_user.id != problem.poster_id:
        raise HTTPException(status_code=403, detail="Only the problem poster can view submitted proposals.")

    proposals = db.query(Proposal).filter(Proposal.problem_id == problem_id).all()
    results = []
    for p in proposals:
        solver = p.solver
        results.append({
            "proposal_id": p.id,
            "problem_id": p.problem_id,
            "solver_id": solver.id,
            "solver_name": solver.full_name,
            "average_score": p.average_score,
            "status": p.status,
            "created_at": p.created_at
        })
    return {"items": results, "total": len(results)}
