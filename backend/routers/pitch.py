from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Problem, Pitch, Proposal
from schemas import PitchStepValidateRequest, PitchStepValidateResponse, PitchSubmitRequest, PitchSubmitResponse
from auth import get_current_user
from validators import validate_pitch_step
from scoring import score_pitch_responses

router = APIRouter(prefix="/pitch", tags=["Pitch Gate"])

@router.get("/{problem_id}/session")
def get_pitch_session(
    problem_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "solver":
        raise HTTPException(status_code=403, detail="Only solvers can participate in pitch gates.")

    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    pitch = db.query(Pitch).filter(Pitch.solver_id == current_user.id, Pitch.problem_id == problem_id).first()
    if not pitch:
        pitch = Pitch(
            solver_id=current_user.id,
            problem_id=problem_id,
            current_step=1
        )
        db.add(pitch)
        db.commit()
        db.refresh(pitch)

    return {
        "pitch_id": pitch.id,
        "problem_id": problem.id,
        "problem_title": problem.title,
        "category": problem.category,
        "current_step": pitch.current_step,
        "status": pitch.status,
        "responses": {
            "step1": pitch.step1_response or "",
            "step2": pitch.step2_response or "",
            "step3": pitch.step3_response or "",
            "step4": pitch.step4_response or "",
            "step5": pitch.step5_response or "",
        }
    }

@router.post("/{problem_id}/step/{step_number}/validate", response_model=PitchStepValidateResponse)
def validate_step(
    problem_id: str,
    step_number: int,
    req: PitchStepValidateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "solver":
        raise HTTPException(status_code=403, detail="Only solvers can pitch.")

    if step_number < 1 or step_number > 5:
        raise HTTPException(status_code=400, detail="Step number must be between 1 and 5.")

    valid, msg = validate_pitch_step(step_number, req.response)

    # Save progress if valid
    pitch = db.query(Pitch).filter(Pitch.solver_id == current_user.id, Pitch.problem_id == problem_id).first()
    if not pitch:
        pitch = Pitch(solver_id=current_user.id, problem_id=problem_id, current_step=step_number)
        db.add(pitch)

    if valid:
        setattr(pitch, f"step{step_number}_response", req.response)
        pitch.current_step = min(5, step_number + 1)
        db.commit()

    return PitchStepValidateResponse(
        valid=valid,
        message=msg if not valid else f"Step {step_number} validated successfully!",
        next_step=pitch.current_step
    )

@router.post("/{problem_id}/submit", response_model=PitchSubmitResponse)
def submit_pitch(
    problem_id: str,
    req: PitchSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "solver":
        raise HTTPException(status_code=403, detail="Only solvers can submit pitches.")

    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    pitch = db.query(Pitch).filter(Pitch.solver_id == current_user.id, Pitch.problem_id == problem_id).first()
    if not pitch:
        raise HTTPException(status_code=400, detail="No active pitch session found.")

    # Save responses
    responses = req.responses
    pitch.step1_response = responses.get("step1", pitch.step1_response)
    pitch.step2_response = responses.get("step2", pitch.step2_response)
    pitch.step3_response = responses.get("step3", pitch.step3_response)
    pitch.step4_response = responses.get("step4", pitch.step4_response)
    pitch.step5_response = responses.get("step5", pitch.step5_response)

    # Run Scoring Engine
    score_result = score_pitch_responses(responses)

    status_str = score_result["status"]  # "submitted" | "needs_work"
    pitch.status = status_str
    db.commit()

    # Create/update Proposal entry
    proposal = db.query(Proposal).filter(Proposal.pitch_id == pitch.id).first()
    if not proposal:
        proposal = Proposal(
            pitch_id=pitch.id,
            problem_id=problem_id,
            solver_id=current_user.id,
            dimension_scores=score_result["dimension_scores"],
            average_score=score_result["average_score"],
            feedback=score_result["feedback"],
            status=status_str
        )
        db.add(proposal)
    else:
        proposal.dimension_scores = score_result["dimension_scores"]
        proposal.average_score = score_result["average_score"]
        proposal.feedback = score_result["feedback"]
        proposal.status = status_str

    db.commit()
    db.refresh(proposal)

    return PitchSubmitResponse(
        proposal_id=proposal.id,
        problem_id=problem_id,
        dimension_scores=score_result["dimension_scores"],
        average_score=score_result["average_score"],
        status=status_str,
        feedback=score_result["feedback"]
    )
