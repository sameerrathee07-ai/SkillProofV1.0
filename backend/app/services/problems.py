import re
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models import Problem, ProblemStatus, User
from app.schemas import ProblemCreate, ProblemResponse, ProblemListResponse, ProblemValidationResponse, ValidationErrorResponse


ACTION_VERBS = {
    "automate", "schedule", "alert", "optimize", "reduce", "eliminate", "streamline",
    "improve", "accelerate", "simplify", "integrate", "connect", "manage", "track",
    "monitor", "analyze", "predict", "generate", "create", "build", "design", "develop",
    "implement", "deploy", "launch", "scale", "enhance", "transform", "modernize",
    "digitize", "centralize", "standardize", "orchestrate", "coordinate"
}

VALID_CATEGORIES = {"Hospitality", "Financial Services", "Education", "Other"}

CURRENCY_PATTERN = re.compile(r"(rs|inr|rupees?|₹|\$)\s*\d+|\d+\s*(rs|inr|rupees?|₹|\$)", re.IGNORECASE)

DURATION_PATTERN = re.compile(r"\b(days?|weeks?|months?|years?|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", re.IGNORECASE)


def validate_problem(problem: ProblemCreate) -> ProblemValidationResponse:
    errors = []
    
    words = problem.description.strip().split()
    if len(words) < 15:
        errors.append(ValidationErrorResponse(field="description", message="Description must be at least 15 words."))
    else:
        has_verb = False
        desc_lower = problem.description.lower()
        for verb in ACTION_VERBS:
            if re.search(r'\b' + re.escape(verb) + r'\b', desc_lower):
                has_verb = True
                break
        if not has_verb:
            errors.append(ValidationErrorResponse(field="description", message="Description must contain at least one action verb (e.g., automate, schedule, optimize)."))
    
    if problem.category not in VALID_CATEGORIES:
        errors.append(ValidationErrorResponse(field="category", message=f"Category must be one of: {', '.join(VALID_CATEGORIES)}"))
    
    if not CURRENCY_PATTERN.search(problem.budget_range):
        errors.append(ValidationErrorResponse(field="budget_range", message="Budget must contain a currency reference and number (e.g., Rs 5000, $100, 5000 INR)."))
    
    if not DURATION_PATTERN.search(problem.timeline):
        errors.append(ValidationErrorResponse(field="timeline", message="Timeline must contain a duration or date reference (e.g., 2 weeks, 30 days, 2024-12-31)."))
    
    return ProblemValidationResponse(valid=len(errors) == 0, errors=errors)


def create_problem(db: Session, problem_in: ProblemCreate, poster_id: int) -> Problem:
    problem = Problem(
        poster_id=poster_id,
        description=problem_in.description,
        category=problem_in.category,
        budget_range=problem_in.budget_range,
        timeline=problem_in.timeline,
        status=ProblemStatus.OPEN,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


def get_problems(db: Session, status: ProblemStatus = ProblemStatus.OPEN) -> List[ProblemListResponse]:
    problems = db.query(Problem).filter(Problem.status == status).order_by(Problem.created_at.desc()).all()
    result = []
    for p in problems:
        poster = db.query(User).filter(User.id == p.poster_id).first()
        result.append(ProblemListResponse(
            id=p.id,
            description=p.description,
            category=p.category,
            budget_range=p.budget_range,
            timeline=p.timeline,
            status=p.status,
            created_at=p.created_at,
            poster_name=poster.name if poster else "Unknown",
        ))
    return result


def get_problem(db: Session, problem_id: int) -> Optional[Problem]:
    return db.query(Problem).filter(Problem.id == problem_id).first()


def close_problem(db: Session, problem_id: int, poster_id: int) -> bool:
    problem = db.query(Problem).filter(Problem.id == problem_id, Problem.poster_id == poster_id).first()
    if not problem:
        return False
    problem.status = ProblemStatus.CLOSED
    db.commit()
    return True