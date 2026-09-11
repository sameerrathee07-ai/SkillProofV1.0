from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Auth ──────────────────────────────────────────────
class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    """The ID token string that Google Identity Services hands the browser."""
    credential: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── User ──────────────────────────────────────────────
class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime
    token_balance: int
    name: Optional[str] = None
    picture: Optional[str] = None
    # Counted server-side on every successful /pdf/generate, so the dashboard
    # reports decks actually downloaded rather than decks that could be.
    pdf_downloads: int = 0

    class Config:
        from_attributes = True


# ── Sessions ──────────────────────────────────────────
class SessionStartResponse(BaseModel):
    session_id: int
    message: str
    current_step: int


class ChatRequest(BaseModel):
    session_id: int
    content: str


class ChatResponse(BaseModel):
    reply: str
    current_step: int
    pitch_complete: bool
    remaining_tokens: int


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class SessionOut(BaseModel):
    id: int
    started_at: datetime
    completed: bool
    current_step: int
    scores_json: Optional[str] = None
    # The accumulated step answers. The results page derives its heading from
    # the step-1 answer, so without this the title falls back to "Untitled".
    pitch_text: Optional[str] = None
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True


class SessionSummary(BaseModel):
    id: int
    started_at: datetime
    completed: bool
    current_step: int
    # Included so the dashboard can render a card (title + score) from the list
    # response alone, instead of firing one request per session.
    scores_json: Optional[str] = None
    pitch_text: Optional[str] = None

    class Config:
        from_attributes = True


# ── Scores ────────────────────────────────────────────
class ScoreRequest(BaseModel):
    session_id: int


class ScoreResponse(BaseModel):
    problem_clarity: float
    market_specificity: float
    revenue_viability: float
    competitive_awareness: float
    team_credibility: float
    investor_readiness: float
    feedback: str


# ── Outline ───────────────────────────────────────────
class OutlineOut(BaseModel):
    """The 7 outline sections, matching ai_service.generate_outline."""
    problem: str
    solution: str
    customer: str
    business_model: str
    competition: str
    team: str
    ask: str
    founder_name: str


# ── Tokens ────────────────────────────────────────────
class PurchaseRequest(BaseModel):
    package: str  # a one-time plan id: "starter" | "standard" | "pro" | "team"


class PurchaseResponse(BaseModel):
    success: bool
    tokens_added: int
    new_balance: int
    message: str


class PackageOut(BaseModel):
    id: str
    tokens: int
    price_inr: int
    popular: bool = False


# ── Payment catalogue ─────────────────────────────────
# Amounts travel as minor units (paise/cents) plus a server-rendered display
# string. The client shows `amount_display` and never does money arithmetic.

class PlanOut(BaseModel):
    id: str
    name: str
    kind: str                      # "one_time" | "subscription"
    tokens: int                    # granted per billing interval
    tokens_per_month: int
    interval: Optional[str] = None  # None | "month" | "year"
    description: str
    badge: str = ""
    popular: bool = False
    amount_minor: int
    amount_display: str
    pitches: int                   # full 5-step pitches this many tokens buys


class PaymentMethodOut(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    min_amount_inr: int = 0


class PromotionOut(BaseModel):
    code: str
    description: str
    active: bool = True
    note: str = ""
    expires_on: Optional[str] = None


class CurrencyOut(BaseModel):
    code: str
    symbol: str
    decimals: int


class CatalogOut(BaseModel):
    """Everything the top-up modal needs, in one public request."""
    currency: CurrencyOut
    currencies: List[CurrencyOut]
    one_time: List[PlanOut]
    subscriptions: List[PlanOut]
    payment_methods: List[PaymentMethodOut]
    promotions: List[PromotionOut]
    tokens_per_message: int
    tokens_per_pitch: int
    emi_tenures: List[int]


class QuoteRequest(BaseModel):
    plan: str
    currency: Optional[str] = None
    promo_code: Optional[str] = None


class QuoteOut(BaseModel):
    plan: str
    tokens: int
    currency: CurrencyOut
    list_minor: int
    list_display: str
    discount_minor: int
    discount_display: str
    total_minor: int
    total_display: str
    promo_code: Optional[str] = None
    promo_description: Optional[str] = None
    promo_error: Optional[str] = None
    eligible_methods: List[PaymentMethodOut]
    balance_after: int
    pitches_after: int


class UsageDay(BaseModel):
    """Tokens spent on a single day. Powers the dashboard usage chart."""
    day: str      # short weekday label, e.g. "Mon"
    date: str     # ISO date, for unambiguous ordering
    tokens: int

if __name__ == "__main__":
    test_signup = SignupRequest(email="test@example.com", password="securepass123")
    print("✅ Pydantic schemas validated successfully")
    print(f"📍 Test: {test_signup.email}")