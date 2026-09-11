import json

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_current_user
from ai_service import generate_outline
from database import get_db
from pdf_generator import build_pdf

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.post("/generate")
def generate_pdf(
    payload: schemas.ScoreRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(models.PitchSession).filter(
        models.PitchSession.id == payload.session_id
    ).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")
    if not session.completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Pitch not complete")
    if not session.pitch_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pitch content")

    if not session.scores_json:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scores not generated — call /session/score first")

    try:
        scores = json.loads(session.scores_json)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid scores data")

    outline = generate_outline(session.pitch_text, founder_name=user.email.split("@")[0])
    feedback = scores.get("feedback", "")

    pdf_bytes = build_pdf(
        founder_name=user.email.split("@")[0],
        outline=outline,
        scores=scores,
        feedback=feedback,
        started_at=session.started_at,
    )

    filename = f"pitchpal-{session.id}-{session.started_at.strftime('%Y%m%d')}.pdf"

    # Count the export only once the bytes exist — build_pdf raising must not
    # inflate a counter for a deck the founder never received.
    user.pdf_downloads = (user.pdf_downloads or 0) + 1
    db.commit()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )