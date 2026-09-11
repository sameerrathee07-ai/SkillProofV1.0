import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from auth import hash_password, verify_password, create_access_token, get_current_user
from database import get_db

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()

SIGNUP_BONUS = 20


def _grant_signup_bonus(db: Session, user_id: int) -> None:
    """20 free tokens + an audit row. Shared by password and Google signup."""
    db.add(models.TokenBalance(user_id=user_id, balance=SIGNUP_BONUS))
    db.add(models.TokenTransaction(
        user_id=user_id, amount=SIGNUP_BONUS, type="credit", reason="signup_bonus"
    ))


def _has_usable_password(user: models.User) -> bool:
    """A Google-only account has no local password. Guard before verify_password
    so a NULL or sentinel hash can never be coerced into a match, and so passlib
    never sees a malformed digest (which would raise a 500)."""
    return bool(user.password_hash) and user.password_hash.startswith("$2")


# Commit 9: Signup endpoint
# WHY: The whole token economy starts here.
#   1. Normalize + validate the email
#   2. Reject duplicates (409)
#   3. Hash the password with bcrypt (never store plaintext)
#   4. Create the user, grant 20 free tokens, log the credit transaction
#   5. Return a JWT so they're logged in immediately

@router.post("/signup", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: schemas.SignupRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()

    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    if len(payload.password) < 8:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password must be at least 8 characters")

    user = models.User(email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()  # assign user.id before creating dependent rows

    # Grant 20 free tokens on signup + record the credit for auditability.
    _grant_signup_bonus(db, user.id)
    db.commit()

    token = create_access_token({"sub": str(user.id)})
    return schemas.TokenResponse(access_token=token)


# Commit 10: Login endpoint
# WHY: Return the same JWT shape as signup so the frontend treats both identically.
# Same message for "no such user" and "wrong password" — don't leak which one failed.

@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email.lower().strip()).first()
    if not user or not _has_usable_password(user) or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})
    return schemas.TokenResponse(access_token=token)


# Google sign-in.
# The browser gets an ID token from Google Identity Services and posts it here.
# We verify the signature and audience server-side — a client-supplied email or
# subject is never trusted on its own, since anyone can POST arbitrary JSON.
# Then create-or-link the account and return our own JWT, same shape as /login.

@router.post("/google", response_model=schemas.TokenResponse)
def google_auth(payload: schemas.GoogleAuthRequest, db: Session = Depends(get_db)):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured on this server",
        )

    # Imported lazily so the app still boots if the optional dep is absent.
    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token as google_id_token
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server missing google-auth; run: pip install -r requirements.txt",
        )

    try:
        claims = google_id_token.verify_oauth2_token(
            payload.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,  # audience check: rejects tokens minted for another app
        )
    except ValueError:
        # Bad signature, wrong audience, or expired. Don't echo the reason back.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google credential")

    if claims.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google credential")

    # Unverified Google addresses could be used to hijack a password account
    # that owns the same address, so require the verified flag.
    if not claims.get("email_verified"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Google email is not verified")

    google_sub = claims.get("sub")
    email = (claims.get("email") or "").lower().strip()
    if not google_sub or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google credential")

    user = db.query(models.User).filter(models.User.google_sub == google_sub).first()

    if not user:
        # Same person arriving via Google for the first time: link by verified email.
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            user.google_sub = google_sub
        else:
            user = models.User(email=email, password_hash=None, google_sub=google_sub)
            db.add(user)
            db.flush()
            _grant_signup_bonus(db, user.id)

    # Refresh the profile fields on every sign-in; they can change upstream.
    user.name = claims.get("name") or user.name
    user.picture = claims.get("picture") or user.picture
    db.commit()

    token = create_access_token({"sub": str(user.id)})
    return schemas.TokenResponse(access_token=token)


# Commit 11: /user/me route
# WHY: Dashboard needs user info + token balance. Protected by get_current_user (JWT bearer).
# UserOut expects a plain int for token_balance, but the ORM exposes a relationship — resolve it here.

@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return schemas.UserOut(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        token_balance=user.token_balance.balance if user.token_balance else 0,
        name=user.name,
        picture=user.picture,
        pdf_downloads=user.pdf_downloads or 0,
    )