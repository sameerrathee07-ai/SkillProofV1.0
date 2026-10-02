from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    POSTER = "poster"
    SOLVER = "solver"


class ProblemStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class ProposalStatus(str, Enum):
    NEEDS_WORK = "needs_work"
    SUBMITTED = "submitted"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=100)
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProblemCreate(BaseModel):
    description: str = Field(min_length=1)
    category: str = Field(min_length=1)
    budget_range: str = Field(min_length=1)
    timeline: str = Field(min_length=1)


class ProblemResponse(BaseModel):
    id: int
    poster_id: int
    description: str
    category: str
    budget_range: str
    timeline: str
    status: ProblemStatus
    created_at: datetime

    class Config:
        from_attributes = True


class ProblemListResponse(BaseModel):
    id: int
    description: str
    category: str
    budget_range: str
    timeline: str
    status: ProblemStatus
    created_at: datetime
    poster_name: str

    class Config:
        from_attributes = True


class PitchStartResponse(BaseModel):
    session_id: int
    current_step: int
    message: str
    remaining_tokens: int


class PitchChatRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=5000)


class PitchChatResponse(BaseModel):
    reply: str
    current_step: int
    pitch_complete: bool
    remaining_tokens: int


class PitchSessionResponse(BaseModel):
    id: int
    user_id: int
    problem_id: int
    started_at: datetime
    completed: bool
    pitch_text: str
    scores_json: Optional[str]
    current_step: int
    attempt_no: int

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ScoreRequest(BaseModel):
    pass


class DimensionScore(BaseModel):
    dimension: str
    score: int


class ScoreResponse(BaseModel):
    gate_passed: bool
    gate_score: float
    dimension_scores: List[DimensionScore]
    feedback: str
    proposal_id: Optional[int] = None
    status: ProposalStatus


class ProposalResponse(BaseModel):
    id: int
    problem_id: int
    solver_id: int
    pitch_session_id: int
    gate_score: Optional[float]
    dimension_scores: Optional[str]
    feedback: Optional[str]
    status: ProposalStatus
    attempts: int
    pdf_downloads: int
    created_at: datetime
    solver_name: Optional[str] = None
    problem_title: Optional[str] = None

    class Config:
        from_attributes = True


class ProposalListResponse(BaseModel):
    id: int
    problem_id: int
    solver_id: int
    gate_score: Optional[float]
    dimension_scores: Optional[str]
    feedback: Optional[str]
    status: ProposalStatus
    attempts: int
    created_at: datetime
    solver_name: str
    solver_credibility: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class CredibilityResponse(BaseModel):
    avg_gate_score: float
    first_attempt_passes: int
    total_attempts: int
    total_passes: int


class TokenBalanceResponse(BaseModel):
    balance: int


class TokenPackage(BaseModel):
    id: str
    name: str
    price_rs: int
    tokens: int


class PurchaseRequest(BaseModel):
    package_id: str
    idempotency_key: str


class PurchaseResponse(BaseModel):
    success: bool
    new_balance: int
    tokens_added: int


class ValidationErrorResponse(BaseModel):
    field: str
    message: str


class ProblemValidationResponse(BaseModel):
    valid: bool
    errors: List[ValidationErrorResponse]