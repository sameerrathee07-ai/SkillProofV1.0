import json
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import PitchSession, Message, Problem, User, TokenBalance, Proposal, ProposalStatus
from app.engine import (
    process_answer, score_pitch, gate_decision, generate_outline,
    compute_credibility, _parse_pitch_lines, Step, COMPLETE_MESSAGE
)
from app.services.tokens import debit_tokens
from app.core.config import settings


def start_pitch_session(db: Session, user_id: int, problem_id: int) -> Optional[PitchSession]:
    problem = db.query(Problem).filter(Problem.id == problem_id, Problem.status == "open").first()
    if not problem:
        return None
    
    existing = db.query(PitchSession).filter(
        PitchSession.user_id == user_id,
        PitchSession.problem_id == problem_id,
        PitchSession.completed == False
    ).first()
    if existing:
        return existing
    
    session = PitchSession(
        user_id=user_id,
        problem_id=problem_id,
        current_step=1,
        attempt_no=1,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    welcome_msg = Message(
        session_id=session.id,
        role="assistant",
        content=(
            "Welcome to the SkillProof pitch gate. You'll answer 5 questions. "
            "Each accepted answer costs 2 tokens. The pass mark is 6/10 average across 6 dimensions. "
            "Let's begin.\n\n"
            "Step 1 — Idea: In one sentence, what does your solution do for this problem? "
            "Specific enough that a stranger could explain it back."
        ),
    )
    db.add(welcome_msg)
    db.commit()
    
    return session


def get_pitch_session(db: Session, session_id: int, user_id: int) -> Optional[PitchSession]:
    return db.query(PitchSession).filter(
        PitchSession.id == session_id,
        PitchSession.user_id == user_id
    ).first()


def get_session_messages(db: Session, session_id: int) -> List[Message]:
    return db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()


def submit_answer(db: Session, session_id: int, user_id: int, answer: str) -> dict:
    session = get_pitch_session(db, session_id, user_id)
    if not session:
        return {"error": "Session not found"}
    
    if session.completed:
        return {"error": "Pitch already completed"}
    
    balance = db.query(TokenBalance).filter(TokenBalance.user_id == user_id).first()
    if not balance or balance.balance < settings.TOKENS_PER_ACCEPTED_ANSWER:
        return {"error": "Insufficient tokens"}
    
    result = process_answer(session.current_step, answer)
    
    user_msg = Message(session_id=session.id, role="user", content=answer)
    db.add(user_msg)
    
    if result.passed:
        idempotency_key = f"pitch_{session.id}_step_{session.current_step}_attempt_{session.attempt_no}"
        debit_tokens(db, user_id, settings.TOKENS_PER_ACCEPTED_ANSWER, f"pitch_step_{session.current_step}", idempotency_key)
        
        session.pitch_text += f"[{session.current_step}] {answer}\n"
        
        if session.current_step == 5:
            session.completed = True
            assistant_content = result.reply
        else:
            session.current_step = result.next_step
            assistant_content = result.reply
    else:
        from app.models import ValidationFailure
        failure = ValidationFailure(
            user_id=user_id,
            session_id=session.id,
            problem_id=session.problem_id,
            step=session.current_step,
            raw_answer=answer,
            pushback_message=result.reply,
        )
        db.add(failure)
        assistant_content = result.reply
    
    assistant_msg = Message(session_id=session.id, role="assistant", content=assistant_content)
    db.add(assistant_msg)
    db.commit()
    db.refresh(session)
    
    balance = db.query(TokenBalance).filter(TokenBalance.user_id == user_id).first()
    
    return {
        "reply": assistant_content,
        "current_step": session.current_step,
        "pitch_complete": session.completed,
        "remaining_tokens": balance.balance if balance else 0,
    }


def score_pitch_session(db: Session, session_id: int, user_id: int) -> dict:
    session = get_pitch_session(db, session_id, user_id)
    if not session:
        return {"error": "Session not found"}
    
    if not session.completed:
        return {"error": "Pitch not complete"}
    
    scores, feedback = score_pitch(session.pitch_text)
    passed, gate_score = gate_decision(scores, settings.GATE_THRESHOLD)
    
    dimension_scores_json = json.dumps({k: v for k, v in scores.items()})
    
    proposal = Proposal(
        problem_id=session.problem_id,
        solver_id=user_id,
        pitch_session_id=session.id,
        gate_score=round(gate_score * 10),
        dimension_scores=dimension_scores_json,
        feedback=feedback,
        status=ProposalStatus.SUBMITTED if passed else ProposalStatus.NEEDS_WORK,
        attempts=session.attempt_no,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    
    return {
        "gate_passed": passed,
        "gate_score": round(gate_score * 10),
        "dimension_scores": [{"dimension": k, "score": v} for k, v in scores.items()],
        "feedback": feedback,
        "proposal_id": proposal.id,
        "status": proposal.status.value,
    }


def revise_proposal(db: Session, proposal_id: int, user_id: int) -> Optional[PitchSession]:
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id, Proposal.solver_id == user_id).first()
    if not proposal:
        return None
    
    if proposal.status == ProposalStatus.SUBMITTED:
        return None
    
    session = db.query(PitchSession).filter(PitchSession.id == proposal.pitch_session_id).first()
    if not session:
        return None
    
    session.attempt_no += 1
    session.completed = False
    session.current_step = 1
    session.pitch_text = ""
    session.scores_json = None
    
    proposal.status = ProposalStatus.NEEDS_WORK
    proposal.attempts = session.attempt_no
    
    db.query(Message).filter(Message.session_id == session.id).delete()
    
    welcome_msg = Message(
        session_id=session.id,
        role="assistant",
        content=(
            f"Revision attempt {session.attempt_no}. Your previous scores and feedback are shown below. "
            "Edit any answers you want to improve — only changed steps will be re-validated and charged.\n\n"
            "Step 1 — Idea: In one sentence, what does your solution do for this problem? "
            "Specific enough that a stranger could explain it back."
        ),
    )
    db.add(welcome_msg)
    db.commit()
    db.refresh(session)
    
    return session


def get_solver_proposals(db: Session, user_id: int) -> List[Proposal]:
    return db.query(Proposal).filter(Proposal.solver_id == user_id).order_by(Proposal.created_at.desc()).all()


def get_problem_proposals(db: Session, problem_id: int, poster_id: int) -> List[Proposal]:
    problem = db.query(Problem).filter(Problem.id == problem_id, Problem.poster_id == poster_id).first()
    if not problem:
        return []
    return db.query(Proposal).filter(
        Proposal.problem_id == problem_id,
        Proposal.status == ProposalStatus.SUBMITTED
    ).order_by(Proposal.gate_score.desc().nullslast()).all()


def get_proposal_with_details(db: Session, proposal_id: int, user_id: int, user_role: str) -> Optional[dict]:
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        return None
    
    if user_role == "solver" and proposal.solver_id != user_id:
        if proposal.status == ProposalStatus.NEEDS_WORK:
            return None
    elif user_role == "poster":
        problem = db.query(Problem).filter(Problem.id == proposal.problem_id, Problem.poster_id == user_id).first()
        if not problem:
            return None
    
    solver = db.query(User).filter(User.id == proposal.solver_id).first()
    problem = db.query(Problem).filter(Problem.id == proposal.problem_id).first()
    
    dimension_scores = {}
    if proposal.dimension_scores:
        dimension_scores = json.loads(proposal.dimension_scores)
    
    answers = _parse_pitch_lines(proposal.pitch_session.pitch_text) if proposal.pitch_session else {}
    outline = generate_outline(answers, solver.name if solver else "Solver")
    
    credibility = compute_credibility([
        {"status": p.status.value, "gate_score": p.gate_score, "attempts": p.attempts}
        for p in db.query(Proposal).filter(Proposal.solver_id == proposal.solver_id).all()
    ])
    
    return {
        "proposal": proposal,
        "solver_name": solver.name if solver else "Solver",
        "problem_title": problem.description[:80] if problem else "Unknown Problem",
        "dimension_scores": dimension_scores,
        "outline": outline,
        "credibility": credibility,
    }


def increment_pdf_download(db: Session, proposal_id: int):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if proposal:
        proposal.pdf_downloads += 1
        db.commit()