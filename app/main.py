import time

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import Base, db_ready, engine, get_db
from app.repository import create_profile, delete_profile, get_profile, list_profiles, update_profile
from app.schemas import ProfileCreate, ProfileRead, ProfileUpdate

settings = get_settings()

REQUEST_COUNT = Counter(
    "profile_service_http_requests_total",
    "Total HTTP requests handled by the profile service",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "profile_service_http_request_duration_seconds",
    "HTTP request latency for profile service",
    ["method", "path"],
)

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    # For assignment simplicity, create tables automatically.
    # In production, candidates should discuss proper migration strategy.
    Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time
    path = request.url.path
    REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(request.method, path).observe(duration)
    return response


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment}


@app.get("/readyz")
def readyz() -> dict[str, str]:
    if not db_ready():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="database not ready")
    return {"status": "ready"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/profiles", response_model=list[ProfileRead])
def profiles(db: Session = Depends(get_db)):
    return list_profiles(db)


@app.post("/profiles", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
def create(payload: ProfileCreate, db: Session = Depends(get_db)):
    try:
        return create_profile(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="profile already exists") from exc


@app.get("/profiles/{user_id}", response_model=ProfileRead)
def read(user_id: str, db: Session = Depends(get_db)):
    profile = get_profile(db, user_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="profile not found")
    return profile


@app.put("/profiles/{user_id}", response_model=ProfileRead)
def update(user_id: str, payload: ProfileUpdate, db: Session = Depends(get_db)):
    profile = update_profile(db, user_id, payload)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="profile not found")
    return profile


@app.delete("/profiles/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(user_id: str, db: Session = Depends(get_db)):
    deleted = delete_profile(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="profile not found")
    return None
