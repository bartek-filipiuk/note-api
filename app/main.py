from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import Base, engine
from app.models import Attachment, Note, NoteShare, User  # noqa: F401
from app.routers import admin, auth, export, notes, uploads
from app.routers.auth import limiter

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notes API", version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(uploads.router)
app.include_router(export.router)
app.include_router(admin.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
