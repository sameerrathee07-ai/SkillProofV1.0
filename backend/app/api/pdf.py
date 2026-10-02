from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.services.pdf_service import generate_proposal_pdf
from app.models import User

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.get("/proposals/{proposal_id}")
def download_pdf(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pdf_bytes = generate_proposal_pdf(db, proposal_id, current_user.id, current_user.role.value)
    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="Proposal not found or not accessible")
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=proposal_{proposal_id}.pdf"}
    )