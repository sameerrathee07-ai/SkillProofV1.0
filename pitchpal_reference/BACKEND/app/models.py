"""SQLAlchemy 2.0 models for PitchPal."""

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def utcnow() -> datetime:
    """Naive UTC, matching the rows already in the DB. datetime.utcnow() is
    deprecated in 3.12+, but switching to an aware default would make new rows
    incomparable with the existing naive ones."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    # Nullable: Google-only accounts have no local password. Login refuses any
    # account whose hash isn't a real bcrypt digest, so NULL can't be bypassed.
    password_hash = Column(String(255), nullable=True)
    # Google's stable subject id. Set only for accounts linked to Google.
    google_sub = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=True)
    picture = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    # Incremented on each successful PDF export. A counter, not a derived value:
    # "decks generated" and "sessions completed" are different numbers.
    pdf_downloads = Column(Integer, default=0, nullable=False, server_default="0")
    # RLS-ready for future multi-tenancy
    tenant_id = Column(Integer, default=1, nullable=False, server_default="1")

    token_balance = relationship(
        "TokenBalance", back_populates="user", uselist=False
    )
    transactions = relationship("TokenTransaction", back_populates="user")
    sessions = relationship("PitchSession", back_populates="user")
    validation_failures = relationship("ValidationFailure", back_populates="user")
    waitlist_signups = relationship("WaitlistSignup", back_populates="user")


class TokenBalance(Base):
    __tablename__ = "token_balance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False
    )
    balance = Column(Integer, default=20, nullable=False)
    last_updated = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="token_balance")


class TokenTransaction(Base):
    __tablename__ = "token_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    type = Column(String(10), nullable=False)  # "debit" | "credit"
    reason = Column(String(100), nullable=False)
    idempotency_key = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=utcnow)
    tenant_id = Column(Integer, default=1, nullable=False, server_default="1")

    user = relationship("User", back_populates="transactions")

    __table_args__ = (
        Index("ix_token_transactions_user_created", "user_id", "created_at"),
    )


class PitchSession(Base):
    __tablename__ = "pitch_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=utcnow)
    completed = Column(Boolean, default=False)
    pitch_text = Column(Text, nullable=True)
    scores_json = Column(Text, nullable=True)
    current_step = Column(Integer, default=1)
    tenant_id = Column(Integer, default=1, nullable=False, server_default="1")

    user = relationship("User", back_populates="sessions")
    messages = relationship(
        "Message", back_populates="session", order_by="Message.created_at"
    )
    validation_failures = relationship("ValidationFailure", back_populates="session")

    __table_args__ = (
        Index("ix_pitch_sessions_user_started", "user_id", "started_at"),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer, ForeignKey("pitch_sessions.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(String(10), nullable=False)  # "assistant" | "user"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    session = relationship("PitchSession", back_populates="messages")


class ValidationFailure(Base):
    """Logged validation failures for false-reject analysis (PRD §3.2)."""

    __tablename__ = "validation_failures"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(
        Integer, ForeignKey("pitch_sessions.id"), nullable=False
    )
    step = Column(Integer, nullable=False)
    raw_answer = Column(Text, nullable=False)
    pushback_message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    tenant_id = Column(Integer, default=1, nullable=False, server_default="1")

    user = relationship("User", back_populates="validation_failures")
    session = relationship("PitchSession", back_populates="validation_failures")

    __table_args__ = (
        Index("ix_validation_failures_user_step", "user_id", "step"),
        Index("ix_validation_failures_session", "session_id"),
    )


class WaitlistSignup(Base):
    """Landing page waitlist signups."""

    __tablename__ = "waitlist_signups"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    source = Column(String(100), nullable=True)  # 'hero', 'footer', 'pricing'
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    # Optional: link to user if they later sign up
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="waitlist_signups")

    __table_args__ = (
        Index("ix_waitlist_signups_created", "created_at"),
        UniqueConstraint("email", name="uq_waitlist_email"),
    )