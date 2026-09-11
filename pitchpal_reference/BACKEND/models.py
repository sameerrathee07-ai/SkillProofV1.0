from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


def utcnow():
    """Naive UTC, matching the rows already in the DB. datetime.utcnow() is
    deprecated in 3.12+, but switching to an aware default would make new rows
    incomparable with the existing naive ones."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    # Nullable: Google-only accounts have no local password. Login refuses any
    # account whose hash isn't a real bcrypt digest, so NULL can't be bypassed.
    password_hash = Column(String, nullable=True)
    # Google's stable subject id. Set only for accounts linked to Google.
    google_sub = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    # Incremented on each successful PDF export. A counter, not a derived value:
    # "decks generated" and "sessions completed" are different numbers, and the
    # dashboard should not report one as the other.
    pdf_downloads = Column(Integer, default=0, nullable=False, server_default="0")

    token_balance = relationship("TokenBalance", back_populates="user", uselist=False)
    transactions = relationship("TokenTransaction", back_populates="user")
    sessions = relationship("PitchSession", back_populates="user")

class TokenBalance(Base):
    __tablename__ = "token_balance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Integer, default=20, nullable=False)
    last_updated = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="token_balance")

class TokenTransaction(Base):
    __tablename__ = "token_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # "debit" | "credit"
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="transactions")

class PitchSession(Base):
    __tablename__ = "pitch_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=utcnow)
    completed = Column(Boolean, default=False)
    pitch_text = Column(Text, nullable=True)
    scores_json = Column(Text, nullable=True)
    current_step = Column(Integer, default=1)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", order_by="Message.created_at")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("pitch_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "assistant" | "user"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    session = relationship("PitchSession", back_populates="messages")
