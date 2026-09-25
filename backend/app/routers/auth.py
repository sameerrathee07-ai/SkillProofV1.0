from fastapi import APIRouter, Response, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, TokenBalance
from app.schemas import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.auth import hash_password, verify_password, create_access_token, set_auth_cookie, clear_auth_cookie, get_current_user, ensure_token_balance

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=TokenResponse)
def signup(request: SignupRequest, response: Response, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        name=request.name,
        role=request.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    ensure_token_balance(db, user.id)
    
    token = create_access_token({"sub": user.id})
    set_auth_cookie(response, token)
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    ensure_token_balance(db, user.id)
    
    token = create_access_token({"sub": user.id})
    set_auth_cookie(response, token)
    return TokenResponse(access_token=token)

@router.post("/logout")
def logout(response: Response):
    clear_auth_cookie(response)
    return {"message": "Logged out"}

@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user