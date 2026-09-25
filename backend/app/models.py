from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # poster / solver
    created_at = Column(DateTime, default=datetime.utcnow)
    
    problems = relationship("Problem", back_populates="poster")
    pitch_sessions = relationship("PitchSession", back_populates="solver")
    proposals = relationship("Proposal", back_populates="solver")
    token_transactions = relationship("TokenTransaction", back_populates="user")
    token_balance = relationship("TokenBalance", back_populates="user", uselist=False)
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
    type = Column(String(10), nullable=False)  # debit / credit
    reason = Column(String(100), nullable=False)
    idempotency_key = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="token_transactions")
    
    __table_args__ = (Index("ix_token_transactions_idempotency", "idempotency_key"),)

class Problem(Base):
    __tablename__ = "problems"
    id = Column(Integer, primary_key=True, index=True)
    poster_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    budget_range = Column(String(100), nullable=False)
    timeline = Column(String(100), nullable=False)
    status = Column(String(20), default="open", nullable=False)  # open / closed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    poster = relationship("User", back_populates="problems")
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
    scores_json = Column(JSON, nullable=True)
    current_step = Column(Integer, default=1)
    attempt_no = Column(Integer, default=1)
    
    solver = relationship("User", back_populates="pitch_sessions")
    problem = relationship("Problem", back_populates="pitch_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("pitch_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # assistant / user
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
    dimension_scores = Column(JSON, nullable=True)
    feedback = Column(Text, nullable=True)
    status = Column(String(20), default="needs_work", nullable=False)  # needs_work / submitted
    attempts = Column(Integer, default=1)
    pdf_downloads = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    problem = relationship("Problem", back_populates="proposals")
    solver = relationship("User", back_populates="proposals")

class ValidationFailure(Base):
    __tablename__ = "validation_failures"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("pitch_sessions.id"), nullable=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=True)
    step = Column(Integer, nullable=True)
    raw_answer = Column(Text, nullable=False)
    pushback_message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="validation_failures")