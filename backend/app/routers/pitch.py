from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Problem, PitchSession, Message, TokenBalance, TokenTransaction, ValidationFailure, Proposal
from app.schemas import PitchStartRequest, PitchStartResponse, ChatRequest, ChatResponse, ScoreResponse
from app.auth import get_current_user, require_role, ensure_token_balance
from app.config import get_settings
from engine import process_answer, score_pitch, gate_decision, generate_suggestions, generate_outline, parse_pitch_lines

router = APIRouter(prefix="/pitch", tags=["pitch"])
settings = get_settings()

@router.post("/problems/{problem_id}/start", response_model=PitchStartResponse)
def start_pitch(problem_id: int, db: Session = Depends(get_db), user = Depends(require_role(["solver"]))):
    problem = db.query(Problem).filter(Problem.id == problem_id, Problem.status == "open").first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found or not open")
    
    existing = db.query(PitchSession).filter(PitchSession.user_id == user.id, PitchSession.problem_id == problem_id).first()
    if existing:
        session = existing
    else:
        balance = ensure_token_balance(db, user.id)
        session = PitchSession(user_id=user.id, problem_id=problem_id, current_step=1, attempt_no=1)
        db.add(session)
        db.commit()
        db.refresh(session)
    
    reply = "Welcome to the guided pitch. The pass mark is 6/10 across six dimensions: Problem Clarity, Customer Specificity, Cost & Value, Alternatives Awareness, Solver Capability, Delivery Readiness. Step 1: In one sentence, what does your solution do for this problem? Be specific enough that a stranger could explain it back."
    
    if not session.messages:
        msg = Message(session_id=session.id, role="assistant", content=reply)
        db.add(msg)
        db.commit()
    
    balance = ensure_token_balance(db, user.id)
    return PitchStartResponse(session_id=session.id, current_step=session.current_step, reply=reply, remaining_tokens=balance.balance)

@router.post("/{session_id}/chat", response_model=ChatResponse)
def chat_pitch(session_id: int, request: ChatRequest, db: Session = Depends(get_db), user = Depends(require_role(["solver"]))):
    session = db.query(PitchSession).filter(PitchSession.id == session_id, PitchSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Pitch session not found")
    
    if session.completed:
        raise HTTPException(status_code=400, detail="Pitch already completed")
    
    balance = ensure_token_balance(db, user.id)
    if balance.balance < settings.TOKENS_PER_ACCEPTED_ANSWER:
        raise HTTPException(status_code=400, detail=f"Insufficient tokens. Need {settings.TOKENS_PER_ACCEPTED_ANSWER}, have {balance.balance}")
    
    user_msg = Message(session_id=session.id, role="user", content=request.content)
    db.add(user_msg)
    db.commit()
    
    result = process_answer(session.current_step, request.content)
    
    if result.passed:
        balance.balance -= settings.TOKENS_PER_ACCEPTED_ANSWER
        txn = TokenTransaction(user_id=user.id, amount=-settings.TOKENS_PER_ACCEPTED_ANSWER, type="debit", reason=f"pitch_step_{session.current_step}", idempotency_key=f"pitch_{session.id}_step_{session.current_step}")
        db.add(txn)
        db.commit()
        
        session.pitch_text += f"[{session.current_step}] {request.content}\n"
        session.current_step = result.next_step
        if session.current_step > 5:
            session.completed = True
            session.current_step = 5
        db.commit()
    
    else:
        failure = ValidationFailure(user_id=user.id, session_id=session.id, problem_id=session.problem_id, step=session.current_step, raw_answer=request.content, pushback_message=result.reply)
        db.add(failure)
        db.commit()
    
    assistant_msg = Message(session_id=session.id, role="assistant", content=result.reply)
    db.add(assistant_msg)
    db.commit()
    
    balance = ensure_token_balance(db, user.id)
    return ChatResponse(reply=result.reply, current_step=session.current_step, pitch_complete=session.completed, remaining_tokens=balance.balance)

@router.get("/{session_id}")
def get_pitch_session(session_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    session = db.query(PitchSession).filter(PitchSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user.id and user.role != "poster":
        raise HTTPException(status_code=403, detail="Forbidden")
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()
    return {
        "id": session.id,
        "problem_id": session.problem_id,
        "current_step": session.current_step,
        "completed": session.completed,
        "pitch_text": session.pitch_text,
        "messages": [{"role": m.role, "content": m.content} for m in messages]
    }

@router.post("/{session_id}/score", response_model=ScoreResponse)
def score_pitch_session(session_id: int, db: Session = Depends(get_db), user = Depends(require_role(["solver"]))):
    session = db.query(PitchSession).filter(PitchSession.id == session_id, PitchSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.completed:
        raise HTTPException(status_code=400, detail="Pitch not complete")
    
    parsed = parse_pitch_lines(session.pitch_text)
    scores, feedback = score_pitch(session.pitch_text, parsed)
    passed, avg = gate_decision(scores)
    
    dimension_scores = [{"name": s.name, "score": s.score, "feedback": s.feedback} for s in scores]
    suggestions = generate_suggestions(scores)
    
    existing_proposal = db.query(Proposal).filter(Proposal.pitch_session_id == session_id).first()
    attempt_no = existing_proposal.attempts + 1 if existing_proposal else 1
    
    if passed:
        status = "submitted"
    else:
        status = "needs_work"
    
    if existing_proposal:
        existing_proposal.gate_score = round(avg * 10)
        existing_proposal.dimension_scores = dimension_scores
        existing_proposal.feedback = feedback
        existing_proposal.status = status
        existing_proposal.attempts = attempt_no
        proposal = existing_proposal
    else:
        proposal = Proposal(
            problem_id=session.problem_id,
            solver_id=user.id,
            pitch_session_id=session_id,
            gate_score=round(avg * 10),
            dimension_scores=dimension_scores,
            feedback=feedback,
            status=status,
            attempts=attempt_no
        )
        db.add(proposal)
    
    db.commit()
    db.refresh(proposal)
    
    return ScoreResponse(
        passed=passed,
        gate_score=avg,
        dimension_scores=dimension_scores,
        feedback=feedback,
        proposal_id=proposal.id
    )