import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
import enum

class UserRole(str, enum.Enum):
    POSTER = "poster"
    SOLVER = "solver"

class ProblemCategory(str, enum.Enum):
    HOSPITALITY = "Hospitality"
    FINANCIAL_SERVICES = "Financial Services"
    OTHER = "Other"

class ProblemStatus(str, enum.Enum):
    PUBLISHED = "published"
    CLOSED = "closed"

class PitchStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    NEEDS_WORK = "needs_work"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    organization = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "poster" or "solver"
    tokens_balance = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)

    problems = relationship("Problem", back_populates="poster", cascade="all, delete-orphan")
    pitches = relationship("Pitch", back_populates="solver", cascade="all, delete-orphan")
    proposals = relationship("Proposal", back_populates="solver", cascade="all, delete-orphan")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    poster_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, index=True, nullable=False)  # "Hospitality", "Financial Services", "Other"
    budget_range = Column(String, nullable=False)
    timeline = Column(String, nullable=False)
    status = Column(String, index=True, default="published")  # "published", "closed"
    created_at = Column(DateTime, default=datetime.utcnow)

    poster = relationship("User", back_populates="problems")
    pitches = relationship("Pitch", back_populates="problem", cascade="all, delete-orphan")
    proposals = relationship("Proposal", back_populates="problem", cascade="all, delete-orphan")


class Pitch(Base):
    __tablename__ = "pitches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    solver_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    problem_id = Column(String, ForeignKey("problems.id"), index=True, nullable=False)
    current_step = Column(Integer, default=1)
    step1_response = Column(Text, nullable=True)
    step2_response = Column(Text, nullable=True)
    step3_response = Column(Text, nullable=True)
    step4_response = Column(Text, nullable=True)
    step5_response = Column(Text, nullable=True)
    status = Column(String, index=True, default="in_progress")  # "in_progress", "submitted", "needs_work"
    tokens_spent = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    solver = relationship("User", back_populates="pitches")
    problem = relationship("Problem", back_populates="pitches")
    proposals = relationship("Proposal", back_populates="pitch", cascade="all, delete-orphan")


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pitch_id = Column(String, ForeignKey("pitches.id"), index=True, nullable=False)
    problem_id = Column(String, ForeignKey("problems.id"), index=True, nullable=False)
    solver_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    dimension_scores = Column(JSON, nullable=False)  # dict with 6 dimension scores
    average_score = Column(Float, nullable=False)
    feedback = Column(Text, nullable=False)
    status = Column(String, index=True, nullable=False)  # "submitted" or "needs_work"
    created_at = Column(DateTime, default=datetime.utcnow)

    pitch = relationship("Pitch", back_populates="proposals")
    problem = relationship("Problem", back_populates="proposals")
    solver = relationship("User", back_populates="proposals")
