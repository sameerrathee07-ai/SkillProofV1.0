from app.engine import generate_pdf_bytes
from app.services.pitch import get_proposal_with_details, increment_pdf_download
from sqlalchemy.orm import Session


def generate_proposal_pdf(db: Session, proposal_id: int, user_id: int, user_role: str) -> Optional[bytes]:
    details = get_proposal_with_details(db, proposal_id, user_id, user_role)
    if not details:
        return None
    
    proposal = details["proposal"]
    if proposal.status.value != "submitted":
        return None
    
    pdf_bytes = generate_pdf_bytes(
        proposal_id=str(proposal.id),
        solver_name=details["solver_name"],
        problem_title=details["problem_title"],
        problem_ref=str(proposal.problem_id),
        overall_score=proposal.gate_score or 0,
        dimension_scores=details["dimension_scores"],
        feedback=proposal.feedback or "",
        outline=details["outline"],
    )
    
    increment_pdf_download(db, proposal_id)
    
    return pdf_bytes