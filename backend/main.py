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

# Environment-driven trusted CORS origins
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Admin-Secret"],
)

from starlette.types import ASGIApp, Receive, Scope, Send

class SecurityHeadersMiddleware:
    """Injects standard HTTP Security Headers (OWASP recommendations)."""
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                headers[b"x-frame-options"] = b"DENY"
                headers[b"x-content-type-options"] = b"nosniff"
                headers[b"x-xss-protection"] = b"1; mode=block"
                headers[b"referrer-policy"] = b"strict-origin-when-cross-origin"
                headers[b"content-security-policy"] = b"default-src 'self'; frame-ancestors 'none';"
                headers[b"strict-transport-security"] = b"max-age=31536000; includeSubDomains"
                message["headers"] = list(headers.items())
            await send(message)

        await self.app(scope, receive, send_with_headers)

app.add_middleware(SecurityHeadersMiddleware)

class NormalizePathMiddleware:
    """Normalizes multiple consecutive slashes (e.g. //auth/google -> /auth/google)."""
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if "//" in path:
                scope["path"] = "/" + "/".join(filter(None, path.split("/")))
        await self.app(scope, receive, send)

app.add_middleware(NormalizePathMiddleware)

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
