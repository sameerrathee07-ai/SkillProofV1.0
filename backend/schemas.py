from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class SignupRequest(BaseModel):
    fullName: str
    organization: Optional[str] = None
    email: EmailStr
    password: str
    role: str  # "poster" or "solver"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class GoogleLoginRequest(BaseModel):
    id_token: str
    role: Optional[str] = "solver"

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    fullName: str
    email: str

# --- Problem Schemas ---
class ProblemCreate(BaseModel):
    title: Optional[str] = None
    description: str
    category: str
    budgetRange: str
    timeline: str

class ProblemResponse(BaseModel):
    problem_id: str
    poster_id: str
    poster_name: Optional[str] = None
    title: str
    description: str
    category: str
    budgetRange: str
    timeline: str
    status: str
    created_at: datetime
    proposal_count: int = 0
    passed_gate_count: int = 0

class ProblemListResponse(BaseModel):
    items: List[ProblemResponse]
    total: int
    page: int

# --- Pitch Schemas ---
class PitchStepValidateRequest(BaseModel):
    step: int
    response: str

class PitchStepValidateResponse(BaseModel):
    valid: bool
    message: str
    next_step: int

class PitchSubmitRequest(BaseModel):
    problem_id: str
    responses: Dict[str, str]  # {"step1": "...", ..., "step5": "..."}

class DimensionScores(BaseModel):
    problem_clarity: float
    market_specificity: float
    revenue_viability: float
    competitive_awareness: float
    team_credibility: float
    investor_readiness: float

class PitchSubmitResponse(BaseModel):
    proposal_id: str
    problem_id: str
    dimension_scores: Dict[str, float]
    average_score: float
    status: str  # "submitted" | "needs_work"
    feedback: str

# --- Proposal Schemas ---
class ProposalResponse(BaseModel):
    proposal_id: str
    problem_id: str
    problem_title: str
    solver_id: str
    solver_name: str
    solver_credibility_score: float
    pitch_responses: Dict[str, str]
    dimension_scores: Dict[str, float]
    average_score: float
    status: str
    feedback: str
    created_at: datetime

class ProposalItem(BaseModel):
    proposal_id: str
    problem_id: str
    problem_title: str
    category: str
    status: str
    current_step: Optional[int] = None
    score: Optional[float] = None
    weakest_dimension: Optional[str] = None
    submitted_at: Optional[datetime] = None
    tokens_spent: int = 0

class ProposalListResponse(BaseModel):
    items: List[ProposalItem]
    total: int

# --- Solver Profile Schemas ---
class RecentSubmission(BaseModel):
    proposal_id: str
    problem_id: str
    problem_title: str
    category: str
    score: float
    status: str

class SolverProfileResponse(BaseModel):
    solver_id: str
    name: str
    credibility_score: float
    total_proposals: int
    passed_first_attempt: int
    average_score_across_all: float
    categories: List[str]
    member_since: datetime
    recent_submissions: List[RecentSubmission]
