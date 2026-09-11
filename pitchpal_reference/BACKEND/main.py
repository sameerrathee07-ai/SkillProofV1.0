import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from migrations import ensure_schema
from routers import auth as auth_router
from routers import sessions as sessions_router
from routers import pdf as pdf_router
from routers import tokens as tokens_router

load_dotenv()

Base.metadata.create_all(bind=engine)
# create_all() adds missing tables but not missing columns, so a database
# created before a model gained a field would 500 on every query touching it.
ensure_schema(engine)

app = FastAPI(
    title="PitchPal API",
    description="Rule-based pitch coach: 5-step validation flow, heuristic scoring, PDF export.",
    version="1.0.0",
)

# Commit 12: CORS — Vercel frontend hits the Render backend cross-origin.
# SECURITY: an explicit allowlist, never "*". Wildcard origins combined with
# allow_credentials=True lets any site on the internet make authenticated calls
# on a logged-in user's behalf. Set CORS_ORIGINS in .env as a comma-separated list.
_default_origins = "http://localhost:5173,http://127.0.0.1:5173"
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", _default_origins).split(",")
    if origin.strip() and origin.strip() != "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Route registration. New routers (sessions, chat, scores, pdf, tokens) get included here as they land.
app.include_router(auth_router.router, prefix="/api", tags=["auth"])
app.include_router(sessions_router.router, prefix="/api", tags=["session"])
app.include_router(pdf_router.router, prefix="/api", tags=["pdf"])
app.include_router(tokens_router.router, prefix="/api", tags=["tokens"])


@app.get("/health", tags=["meta"])
def health():
    """Used by Render to verify the app is alive. Cheap, no DB hit."""
    return {"status": "ok"}
