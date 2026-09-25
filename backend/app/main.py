from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import Base, engine
from app.routers import auth, problems, pitch, proposals, solvers, pdf, tokens

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SkillProof API", version="1.0.0")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(problems.router)
app.include_router(pitch.router)
app.include_router(proposals.router)
app.include_router(solvers.router)
app.include_router(pdf.router)
app.include_router(tokens.router)

@app.get("/health")
def health():
    return {"status": "ok"}