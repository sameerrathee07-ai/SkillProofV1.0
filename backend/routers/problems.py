from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, case
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from database import get_db
from models import User, Problem, Proposal
from schemas import ProblemCreate, ProblemResponse, ProblemListResponse
from auth import get_current_user
from validators import validate_problem_description, has_currency_reference, has_timeline_reference

router = APIRouter(prefix="", tags=["Problems"])

@router.post("/problems", response_model=ProblemResponse)
def create_problem(
    req: ProblemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "poster":
        raise HTTPException(status_code=403, detail="Only problem-posters can post problems.")

    # Server authoritative validation
    is_valid, msg = validate_problem_description(req.description)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    if not has_currency_reference(req.budgetRange):
        raise HTTPException(status_code=400, detail="Budget range must include a currency reference (₹, $, etc.) and numbers.")

    if not has_timeline_reference(req.timeline):
        raise HTTPException(status_code=400, detail="Timeline must specify duration or date reference (e.g. 2 weeks, Sept 30).")

    # Generate title if not provided
    title = req.title or (req.description.split(".")[0][:60] + "...")

    problem = Problem(
        poster_id=current_user.id,
        title=title,
        description=req.description,
        category=req.category,
        budget_range=req.budgetRange,
        timeline=req.timeline,
        status="published"
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)

    return ProblemResponse(
        problem_id=problem.id,
        poster_id=problem.poster_id,
        poster_name=current_user.full_name,
        title=problem.title,
        description=problem.description,
        category=problem.category,
        budgetRange=problem.budget_range,
        timeline=problem.timeline,
        status=problem.status,
        created_at=problem.created_at,
        proposal_count=0,
        passed_gate_count=0
    )

@router.get("/problems", response_model=ProblemListResponse)
def get_problems(
    category: Optional[str] = None,
    status: Optional[str] = "published",
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    base_query = db.query(Problem)
    if status:
        base_query = base_query.filter(Problem.status == status)
    if category and category != "All":
        base_query = base_query.filter(Problem.category == category)

    total = base_query.count()

    query = (
        db.query(
            Problem,
            func.count(Proposal.id).label("proposal_count"),
            func.count(case((Proposal.status == "submitted", 1))).label("passed_gate_count")
        )
        .options(joinedload(Problem.poster))
        .outerjoin(Proposal, Proposal.problem_id == Problem.id)
    )
    if status:
        query = query.filter(Problem.status == status)
    if category and category != "All":
        query = query.filter(Problem.category == category)

    items = (
        query.group_by(Problem.id)
        .order_by(Problem.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    results = []
    for p, p_count, passed_count in items:
        results.append(ProblemResponse(
            problem_id=p.id,
            poster_id=p.poster_id,
            poster_name=p.poster.full_name if p.poster else "Poster",
            title=p.title,
            description=p.description,
            category=p.category,
            budgetRange=p.budget_range,
            timeline=p.timeline,
            status=p.status,
            created_at=p.created_at,
            proposal_count=p_count,
            passed_gate_count=passed_count
        ))

    return ProblemListResponse(items=results, total=total, page=page)

@router.get("/my-listings")
def get_my_listings(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "poster":
        raise HTTPException(status_code=403, detail="Only problem posters can view listing dashboard.")

    base_query = db.query(Problem).filter(Problem.poster_id == current_user.id)
    if status and status != "all":
        base_query = base_query.filter(Problem.status == status)

    total_posted = base_query.count()

    query = (
        db.query(
            Problem,
            func.count(Proposal.id).label("proposal_count"),
            func.count(case((Proposal.status == "submitted", 1))).label("passed_gate_count")
        )
        .filter(Problem.poster_id == current_user.id)
        .outerjoin(Proposal, Proposal.problem_id == Problem.id)
    )
    if status and status != "all":
        query = query.filter(Problem.status == status)

    items = (
        query.group_by(Problem.id)
        .order_by(Problem.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    res_items = []
    total_proposals_all = 0
    total_solved = 0

    for p, p_count, passed_count in items:
        total_proposals_all += p_count
        if p.status == "closed":
            total_solved += 1

        res_items.append({
            "problem_id": p.id,
            "title": p.title,
            "description": p.description,
            "category": p.category,
            "budget_range": p.budget_range,
            "timeline": p.timeline,
            "status": p.status,
            "created_at": p.created_at,
            "proposal_count": p_count,
            "passed_gate_count": passed_count
        })

    avg_proposals = round(total_proposals_all / max(total_posted, 1), 1)

    return {
        "items": res_items,
        "total": total_posted,
        "metrics": {
            "total_posted": total_posted,
            "avg_proposals_per_problem": avg_proposals,
            "total_solved": total_solved
        }
    }
