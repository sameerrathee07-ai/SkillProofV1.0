from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.auth import get_current_user
from app.services.problems import (
    validate_problem, create_problem, get_problems, get_problem, close_problem
)
from app.schemas import (
    ProblemCreate, ProblemResponse, ProblemListResponse, ProblemValidationResponse
)
from app.models import User, ProblemStatus

router = APIRouter(prefix="/problems", tags=["problems"])


@router.post("/validate", response_model=ProblemValidationResponse)
def validate_problem_endpoint(problem: ProblemCreate):
    return validate_problem(problem)


@router.post("", response_model=ProblemResponse)
def create_problem_endpoint(
    problem: ProblemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "poster":
        raise HTTPException(status_code=403, detail="Only problem posters can create problems")
    
    validation = validate_problem(problem)
    if not validation.valid:
        raise HTTPException(status_code=400, detail=validation.errors)
    
    return create_problem(db, problem, current_user.id)


@router.get("", response_model=List[ProblemListResponse])
def list_problems(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_problems(db)


@router.get("/{problem_id}", response_model=ProblemResponse)
def get_problem_endpoint(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    problem = get_problem(db, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.patch("/{problem_id}/close")
def close_problem_endpoint(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "poster":
        raise HTTPException(status_code=403, detail="Only problem posters can close problems")
    
    success = close_problem(db, problem_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Problem not found or not authorized")
    
    return {"message": "Problem closed"}