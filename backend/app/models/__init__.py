from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    POSTER = "poster"
    SOLVER = "solver"


class ProblemStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class ProposalStatus(str, enum.Enum):
    NEEDS_WORK = "needs_work"
    SUBMITTED = "submitted"


class TransactionType(str, enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    problems = relationship("Problem", back_populates="poster", foreign_keys="Problem.poster_id")
    pitch_sessions = relationship("PitchSession", back_populates="solver")
    proposals = relationship("Proposal", back_populates="solver")
    token_balance = relationship("TokenBalance", back_populates="user", uselist=False)
    token_transactions = relationship("TokenTransaction", back_populates="user")
    validation_failures = relationship("ValidationFailure", back_populates="user")


class TokenBalance(Base):
    __tablename__ = "token_balance"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Integer, default=20, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="token_balance")


class TokenTransaction(Base):
    __tablename__ = "token_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    reason = Column(String(100), nullable=False)
    idempotency_key = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="token_transactions")


class Problem(Base):
    __tablename__ = "problems"
    
    id = Column(Integer, primary_key=True, index=True)
    poster_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    budget_range = Column(String(200), nullable=False)
    timeline = Column(String(200), nullable=False)
    status = Column(Enum(ProblemStatus), default=ProblemStatus.OPEN, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    poster = relationship("User", back_populates="problems", foreign_keys=[poster_id])
    proposals = relationship("Proposal", back_populates="problem")
    pitch_sessions = relationship("PitchSession", back_populates="problem")


class PitchSession(Base):
    __tablename__ = "pitch_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)
    pitch_text = Column(Text, default="")
    scores_json = Column(Text, nullable=True)
    current_step = Column(Integer, default=1)
    attempt_no = Column(Integer, default=1)
    
    solver = relationship("User", back_populates="pitch_sessions")
    problem = relationship("Problem", back_populates="pitch_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")
    proposals = relationship("Proposal", back_populates="pitch_session")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("pitch_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("PitchSession", back_populates="messages")


class Proposal(Base):
    __tablename__ = "proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    solver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    pitch_session_id = Column(Integer, ForeignKey("pitch_sessions.id"), nullable=False)
    gate_score = Column(Integer, nullable=True)
    dimension_scores = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    status = Column(Enum(ProposalStatus), default=ProposalStatus.NEEDS_WORK, nullable=False)
    attempts = Column(Integer, default=1)
    pdf_downloads = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    problem = relationship("Problem", back_populates="proposals")
    solver = relationship("User", back_populates="proposals")
    pitch_session = relationship("PitchSession", back_populates="proposals")


class ValidationFailure(Base):
    __tablename__ = "validation_failures"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("pitch_sessions.id"), nullable=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=True, index=True)
    step = Column(Integer, nullable=False)
    raw_answer = Column(Text, nullable=False)
    pushback_message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="validation_failures")