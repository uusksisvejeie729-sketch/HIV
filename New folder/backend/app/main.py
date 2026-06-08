from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models.user import User
from app.middleware.security import SecurityHeadersMiddleware
from app.routers import admin, analytics, auth, predict, reports
from app.schemas.user import TokenResponse, UserLogin, UserRegister
from app.services.auth import hash_password
from app.services.ml_engine import load_model


def seed_admin():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@hivcare.ai").first():
            db.add(
                User(
                    name="System Admin",
                    email="admin@hivcare.ai",
                    password_hash=hash_password("Admin@12345"),
                    role="admin",
                )
            )
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_admin()
    try:
        load_model()
    except FileNotFoundError:
        pass
    yield


app = FastAPI(
    title=settings.app_name,
    description="Intelligent HIV/AIDS Risk Prediction and Support System",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(analytics.router)
app.include_router(admin.router)
app.include_router(reports.router)

# SRS §9 API aliases
app.post("/register", response_model=TokenResponse, status_code=201, tags=["Authentication"])(auth.register)
app.post("/login", response_model=TokenResponse, tags=["Authentication"])(auth.login)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "disclaimer": "Not a substitute for professional medical diagnosis.",
    }


@app.get("/health")
def health():
    from app.services.ml_engine import _resolve_path

    model_ok = _resolve_path(settings.model_path).exists()
    return {"status": "ok", "model_loaded": model_ok}
