import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
from database import get_db
from models import User
from schemas import SignupRequest, LoginRequest, GoogleLoginRequest, AuthResponse
from auth import hash_password, verify_password, create_access_token, get_current_user

def get_google_client_id() -> str | None:
    raw = os.getenv("GOOGLE_CLIENT_ID", "").strip().strip('"').strip("'")
    return raw if raw else None

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=AuthResponse)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    if req.role not in ["poster", "solver"]:
        raise HTTPException(status_code=400, detail="Invalid role specified")

    user = User(
        full_name=req.fullName,
        organization=req.organization,
        email=req.email,
        password_hash=hash_password(req.password),
        role=req.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"user_id": user.id, "role": user.role, "email": user.email})
    return AuthResponse(
        access_token=token,
        role=user.role,
        user_id=user.id,
        fullName=user.full_name,
        email=user.email
    )

@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"user_id": user.id, "role": user.role, "email": user.email})
    return AuthResponse(
        access_token=token,
        role=user.role,
        user_id=user.id,
        fullName=user.full_name,
        email=user.email
    )

@router.post("/google", response_model=AuthResponse)
def google_login(req: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        # If GOOGLE_CLIENT_ID is set in env, verify against it; otherwise verify token structure
        client_id_check = get_google_client_id()
        id_info = id_token.verify_oauth2_token(req.id_token, requests.Request(), audience=client_id_check)
        email = id_info.get("email")
        name = id_info.get("name", "Google User")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        role = req.role if req.role in ["poster", "solver"] else "solver"
        user = User(
            full_name=name,
            organization="Google Auth",
            email=email,
            password_hash=hash_password("oauth_google_login_protected"),
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"user_id": user.id, "role": user.role, "email": user.email})
    return AuthResponse(
        access_token=token,
        role=user.role,
        user_id=user.id,
        fullName=user.full_name,
        email=user.email
    )

@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """GDPR Article 17 - Right to be Forgotten user deletion endpoint."""
    db.delete(current_user)
    db.commit()
    return {"status": "success", "message": "Account and associated personal data deleted successfully."}

@router.get("/me/export")
def export_user_data(
    current_user: User = Depends(get_current_user)
):
    """GDPR Article 15 - Data Portability export endpoint."""
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "organization": current_user.organization,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }
