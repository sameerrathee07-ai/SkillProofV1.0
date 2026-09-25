from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str
    
    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
    
    @field_validator("role")
    @classmethod
    def role_valid(cls, v):
        if v not in ("poster", "solver"):
            raise ValueError("Role must be 'poster' or 'solver'")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProblemCreate(BaseModel):
    description: str
    category: str
    budget_range: str
    timeline: str
    
    @field_validator("category")
    @classmethod
    def category_valid(cls, v):
        allowed = ["Hospitality", "Financial Services", "Education", "Other"]
        if v not in allowed:
            raise ValueError(f"Category must be one of: {', '.join(allowed)}")
        return v

class ProblemResponse(BaseModel):
    id: int
    poster_id: int
    description: str
    category: str
    budget_range: str
    timeline: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PitchStartRequest(BaseModel):
    problem_id: int

class PitchStartResponse(BaseModel):
    session_id: int
    current_step: int
    reply: str
    remaining_tokens: int

class ChatRequest(BaseModel):
    content: str
    
    @field_validator("content")
    @classmethod
    def content_length(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        if len(v) > 5000:
            raise ValueError("Message too long (max 5000 characters)")
        return v

class ChatResponse(BaseModel):
    reply: str
    current_step: int
    pitch_complete: bool
    remaining_tokens: int

class ScoreResponse(BaseModel):
    passed: bool
    gate_score: float
    dimension_scores: List[dict]
    feedback: str
    proposal_id: Optional[int] = None

class ProposalResponse(BaseModel):
    id: int
    problem_id: int
    solver_id: int
    gate_score: float
    dimension_scores: List[dict]
    feedback: str
    status: str
    attempts: int
    created_at: datetime
    solver_name: str
    solver_credibility: Optional[dict] = None
    
    class Config:
        from_attributes = True

class CredibilityResponse(BaseModel):
    user_id: int
    avg_gate_score: float
    first_attempt_passes: int
    total_passes: int
    total_attempts: int

class TokenBalanceResponse(BaseModel):
    balance: int

class PackageResponse(BaseModel):
    id: str
    name: str
    price_rs: int
    tokens: int

class PurchaseRequest(BaseModel):
    package_id: str

class PurchaseResponse(BaseModel):
    balance: int
    transaction_id: int