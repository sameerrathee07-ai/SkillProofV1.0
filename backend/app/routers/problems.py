import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Problem, ValidationFailure
from app.schemas import ProblemCreate, ProblemResponse
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/problems", tags=["problems"])

ACTION_VERBS = {"build", "create", "design", "develop", "implement", "automate", "optimize", "streamline", "reduce", "eliminate", "improve", "solve", "fix", "address", "tackle", "deliver", "provide", "enable", "allow", "connect", "integrate", "schedule", "assign", "track", "monitor", "alert", "notify", "generate", "calculate", "analyze", "report", "manage", "organize", "coordinate", "simplify", "standardize", "digitize", "modernize", "replace", "upgrade", "enhance"}
CURRENCY_PATTERNS = [
    r"(?:rs|inr|rupees?|₹)\s*\d+",
    r"\d+\s*(?:rs|inr|rupees?|₹)",
    r"\$\s*\d+",
    r"\d+\s*\$",
    r"\d+(?:,\d{3})*(?:\.\d{2})?",
]
DURATION_PATTERNS = [
    r"\d+\s*(?:day|week|month|year)s?",
    r"(?:day|week|month|year)s?",
    r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}",
]

def _has_action_verb(text: str) -> bool:
    text_lower = text.lower()
    for verb in ACTION_VERBS:
        if re.search(r"\b" + re.escape(verb) + r"\b", text_lower):
            return True
    return False

def _has_currency(text: str) -> bool:
    text_lower = text.lower()
    for pattern in CURRENCY_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def _has_duration(text: str) -> bool:
    text_lower = text.lower()
    for pattern in DURATION_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def log_validation_failure(db: Session, user_id: int, problem_id: int | None, step: int | None, answer: str, pushback: str):
    failure = ValidationFailure(
        user_id=user_id,
        problem_id=problem_id,
        step=step,
        raw_answer=answer,
        pushback_message=pushback
    )
    db.add(failure)
    db.commit()

@router.post("", response_model=ProblemResponse)
def create_problem(request: ProblemCreate, db: Session = Depends(get_db), user = Depends(require_role(["poster"]))):
    errors = []
    
    if len(request.description.split()) < 15:
        errors.append("Description must be at least 15 words")
    elif not _has_action_verb(request.description):
        errors.append("Description must contain at least one action verb (e.g., build, create, automate, reduce)")
    
    if not _has_currency(request.budget_range):
        errors.append("Budget must contain a currency reference and number (e.g., Rs 5000, $100, 5000 rupees)")
    
    if not _has_duration(request.timeline):
        errors.append("Timeline must contain a duration or date reference (e.g., 2 weeks, 30 days, 2024-12-31)")
    
    if errors:
        for err in errors:
            log_validation_failure(db, user.id, None, None, f"Problem creation: {request.description[:100]}", err)
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    problem = Problem(
        poster_id=user.id,
        description=request.description,
        category=request.category,
        budget_range=request.budget_range,
        timeline=request.timeline
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem

@router.get("", response_model=list[ProblemResponse])
def list_problems(db: Session = Depends(get_db), user = Depends(get_current_user)):
    problems = db.query(Problem).filter(Problem.status == "open").order_by(Problem.created_at.desc()).all()
    return problems

@router.get("/{problem_id}", response_model=ProblemResponse)
def get_problem(problem_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@router.patch("/{problem_id}/close")
def close_problem(problem_id: int, db: Session = Depends(get_db), user = Depends(require_role(["poster"]))):
    problem = db.query(Problem).filter(Problem.id == problem_id, Problem.poster_id == user.id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found or not yours")
    problem.status = "closed"
    db.commit()
    return {"message": "Problem closed"}