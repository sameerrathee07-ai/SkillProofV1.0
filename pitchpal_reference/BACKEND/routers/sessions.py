import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from auth import get_current_user
from ai_service import OPENING_MESSAGE, PASS_COST, TOTAL_STEPS, generate_outline, process_answer, score_pitch
from database import get_db

router = APIRouter(prefix="/session", tags=["session"])


# Commit 15: /session/start — create a new session and return the opening message.
# WHY: The frontend calls this when the user hits "Start New Pitch".
# The opening assistant message is stored so session history/replay is complete.

@router.post("/start", response_model=schemas.SessionStartResponse, status_code=status.HTTP_201_CREATED)
def start_session(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = models.PitchSession(user_id=user.id, current_step=1, completed=False)
    db.add(session)
    db.commit()
    db.refresh(session)

    db.add(models.Message(session_id=session.id, role="assistant", content=OPENING_MESSAGE))
    db.commit()

    return schemas.SessionStartResponse(
        session_id=session.id,
        message=OPENING_MESSAGE,
        current_step=1,
    )


# Shared helper: fetch a session owned by the current user. Used by /chat and history.
def _get_owned_session(db: Session, session_id: int, user: models.User) -> models.PitchSession:
    """Fetch a session and verify it belongs to the current user."""
    session = db.query(models.PitchSession).filter(models.PitchSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")
    return session


# Commit 16: /chat — the heart of the app.
# WHY: Every user message goes through here. The backend:
#   1. verifies ownership + session still open
#   2. deducts 2 tokens SERVER-SIDE (frontend never touches the balance)
#   3. stores the user answer (even failed ones — history is honest)
#   4. runs the state machine, stores the reply
#   5. marks the session complete when step 5 passes
# Passed answers accumulate in pitch_text so the outline/scoring/PDF can read them later.

@router.post("/chat", response_model=schemas.ChatResponse)
def chat(
    payload: schemas.ChatRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_owned_session(db, payload.session_id, user)
    if session.completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This pitch session is already complete")

    balance = user.token_balance
    if not balance or balance.balance < PASS_COST:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Out of tokens — top up to keep pitching",
        )

    # Deduct tokens first — fail fast, and the charge can never be skipped.
    balance.balance -= PASS_COST
    db.add(models.TokenTransaction(
        user_id=user.id, amount=PASS_COST, type="debit", reason="chat_message"
    ))
    db.commit()

    db.add(models.Message(session_id=session.id, role="user", content=payload.content))
    result = process_answer(session.current_step, payload.content)

    pitch_complete = False
    if result.passed:
        # Keep every validated answer so the outline generator has the raw material.
        session.pitch_text = (session.pitch_text or "") + f"[{session.current_step}] {payload.content.strip()}\n"
        if session.current_step >= TOTAL_STEPS:
            session.completed = True
            pitch_complete = True
        session.current_step = result.next_step

    db.add(models.Message(session_id=session.id, role="assistant", content=result.reply))
    db.commit()

    return schemas.ChatResponse(
        reply=result.reply,
        current_step=session.current_step,
        pitch_complete=pitch_complete,
        remaining_tokens=balance.balance,
    )


# Commit 19: /score — run the heuristic engine on a completed pitch.
# WHY: Frontend calls this after pitch_complete=true to show radar chart + scores.
# The scores are stored on the session so the PDF generator can reuse them.

@router.post("/score", response_model=schemas.ScoreResponse)
def score_session(
    payload: schemas.ScoreRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_owned_session(db, payload.session_id, user)
    if not session.completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pitch not complete — finish all 5 steps first")

    if not session.pitch_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pitch content to score")

    scores = score_pitch(session.pitch_text)
    session.scores_json = json.dumps(scores)
    db.commit()

    return schemas.ScoreResponse(**scores)


# Commit 22: /history — list user's sessions for dashboard
@router.get("/history", response_model=List[schemas.SessionSummary])
def session_history(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = db.query(models.PitchSession).filter(
        models.PitchSession.user_id == user.id
    ).order_by(models.PitchSession.started_at.desc()).all()
    return sessions


# The 7-section outline, same generator the PDF uses. Exposed as JSON so the
# results page can show the outline on screen instead of only inside a download.
@router.get("/{session_id}/outline", response_model=schemas.OutlineOut)
def session_outline(
    session_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_owned_session(db, session_id, user)
    if not session.completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pitch not complete — finish all 5 steps first",
        )
    if not session.pitch_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pitch content")

    outline = generate_outline(session.pitch_text, founder_name=user.email.split("@")[0])
    return schemas.OutlineOut(**outline)


# Commit 23: /session/{id} — get single session with messages for chat replay
@router.get("/{session_id}", response_model=schemas.SessionOut)
def get_session(
    session_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_owned_session(db, session_id, user)
    return session
