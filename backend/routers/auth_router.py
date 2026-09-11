from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import SignupRequest, LoginRequest, AuthResponse
from auth import hash_password, verify_password, create_access_token

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
