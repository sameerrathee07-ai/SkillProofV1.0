from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from database import get_db
import models

load_dotenv()

# SECURITY: no fallback secret. A hardcoded default means anyone who has read the
# source can forge a JWT for any user, so refuse to boot without a real key.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError(
        "SECRET_KEY is missing or too short (need >=32 chars). "
        "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(48))\" "
        "and put it in BACKEND/.env"
    )

# Pinned, not read from env: a misconfigured algorithm is an auth bypass, and we
# only ever issue HS256.
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# auto_error=False so a missing or malformed Authorization header reaches our own
# check below. HTTPBearer's built-in error is a 403, which reads as "you are
# signed in but not allowed" — the opposite of the truth, and the frontend only
# clears a dead session on a 401.
security = HTTPBearer(auto_error=False)


# Commit 8: JWT utility functions
# WHY: Auth requires 4 functions:
#   1. hash_password: Store password securely (bcrypt)
#   2. verify_password: Check if plain password matches hash
#   3. create_access_token: Generate JWT for authenticated users
#   4. decode_token: Validate JWT from Authorization header
#   5. get_current_user: Dependency that protects routes

def hash_password(password: str) -> str:
    """Hash password with bcrypt. Called on signup."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify plain password against bcrypt hash. Called on login."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT token.
    TRICKY: Token expires in 1440 minutes (24 hours) by default.
    Payload contains: user_id (sub), exp (expiration), iat (issued at)
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """
    Validate JWT and extract payload.
    Returns None if token is expired or tampered with.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """
    FastAPI dependency that validates JWT and returns authenticated user.
    HTTPBearer extracts "Bearer <token>" from the Authorization header; a
    missing, non-Bearer or invalid token is always a 401 (never a 403), so the
    client can tell "sign in again" apart from "you may not do this".
    Used as: @app.get("/protected") def route(user: models.User = Depends(get_current_user))
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or not credentials.credentials:
        raise unauthorized

    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise unauthorized
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise unauthorized

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise unauthorized
    return user