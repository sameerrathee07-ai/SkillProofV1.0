import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth_router, problems, pitch, proposals, solver, admin

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SkillProof API",
    description="Backend API for SkillProof — Verified Problem-Solving Marketplace with Pitch Quality Gate",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: specify Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router.router)
app.include_router(problems.router)
app.include_router(pitch.router)
app.include_router(proposals.router)
app.include_router(solver.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "app": "SkillProof API",
        "version": "1.0.0",
        "quality_gate_threshold": 6.0
    }
