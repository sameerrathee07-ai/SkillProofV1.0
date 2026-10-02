from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.auth import get_current_user
from app.services.pitch import (
    start_pitch_session, get_pitch_session, get_session_messages,
    submit_answer, score_pitch_session, revise_proposal,
    get_solver_proposals, get_problem_proposals
)
from app.schemas import (
    PitchStartResponse, PitchChatRequest, PitchChatResponse,
    PitchSessionResponse, MessageResponse, ScoreResponse,
    ProposalListResponse
)
from app.models import User, ProposalStatus

router = APIRouter(prefix="/pitch", tags=["pitch"])


@router.post("/problems/{problem_id}/start", response_model=PitchStartResponse)
def start_pitch(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "solver":
        raise HTTPException(status_code=403, detail="Only solvers can start pitches")
    
    session = start_pitch_session(db, current_user.id, problem_id)
    if not session:
        raise HTTPException(status_code=404, detail="Problem not found or not open")
    
    from app.services.tokens import get_balance
    balance = get_balance(db, current_user.id)
    
    messages = get_session_messages(db, session.id)
    first_msg = messages[0].content if messages else ""
    
    return PitchStartResponse(
        session_id=session.id,
        current_step=session.current_step,
        message=first_msg,
        remaining_tokens=balance.balance,
    )


@router.get("/{session_id}", response_model=PitchSessionResponse)
def get_pitch(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = get_pitch_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = get_pitch_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return get_session_messages(db, session_id)


@router.post("/{session_id}/chat", response_model=PitchChatResponse)
def chat(
    session_id: int,
    request: PitchChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = get_pitch_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = submit_answer(db, session_id, current_user.id, request.answer)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return PitchChatResponse(**result)


@router.post("/{session_id}/score", response_model=ScoreResponse)
def score(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = get_pitch_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = score_pitch_session(db, session_id, current_user.id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return ScoreResponse(**result)


@router.post("/proposals/{proposal_id}/revise", response_model=PitchStartResponse)
def revise(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "solver":
        raise HTTPException(status_code=403, detail="Only solvers can revise proposals")
    
    session = revise_proposal(db, proposal_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Proposal not found or cannot be revised")
    
    from app.services.tokens import get_balance
    balance = get_balance(db, current_user.id)
    
    messages = get_session_messages(db, session.id)
    first_msg = messages[0].content if messages else ""
    
    return PitchStartResponse(
        session_id=session.id,
        current_step=session.current_step,
        message=first_msg,
        remaining_tokens=balance.balance,
    )


@router.get("/proposals/mine", response_model=List[ProposalListResponse])
def my_proposals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "solver":
        raise HTTPException(status_code=403, detail="Only solvers can view their proposals")
    
    proposals = get_solver_proposals(db, current_user.id)
    result = []
    for p in proposals:
        solver = db.query(User).filter(User.id == p.solver_id).first()
        from app.engine import compute_credibility
        credibility = compute_credibility([
            {"status": prop.status.value, "gate_score": prop.gate_score, "attempts": prop.attempts}
            for prop in db.query(Proposal).filter(Proposal.solver_id == p.solver_id).all()
        ])
        result.append(ProposalListResponse(
            id=p.id,
            problem_id=p.problem_id,
            solver_id=p.solver_id,
            gate_score=p.gate_score,
            dimension_scores=p.dimension_scores,
            feedback=p.feedback,
            status=p.status,
            attempts=p.attempts,
            created_at=p.created_at,
            solver_name=solver.name if solver else "Unknown",
            solver_credibility=credibility,
        ))
    return result


@router.get("/problems/{problem_id}/proposals", response_model=List[ProposalListResponse])
def problem_proposals(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "poster":
        raise HTTPException(status_code=403, detail="Only problem posters can view proposals")
    
    proposals = get_problem_proposals(db, problem_id, current_user.id)
    result = []
    for p in proposals:
        solver = db.query(User).filter(User.id == p.solver_id).first()
        from app.engine import compute_credibility
        credibility = compute_credibility([
            {"status": prop.status.value, "gate_score": prop.gate_score, "attempts": prop.attempts}
            for prop in db.query(Proposal).filter(Proposal.solver_id == p.solver_id).all()
        ])
        result.append(ProposalListResponse(
            id=p.id,
            problem_id=p.problem_id,
            solver_id=p.solver_id,
            gate_score=p.gate_score,
            dimension_scores=p.dimension_scores,
            feedback=p.feedback,
            status=p.status,
            attempts=p.attempts,
            created_at=p.created_at,
            solver_name=solver.name if solver else "Unknown",
            solver_credibility=credibility,
        ))
    return result