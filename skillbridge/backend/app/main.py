"""
SkillBridge API — main FastAPI application.

Run locally:
    cd backend
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    createdb skillbridge          # one-time, requires local PostgreSQL
    uvicorn app.main:app --reload

Docs available at http://localhost:8000/docs
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database_sql import init_db
from app.routes import (
    admin, auth, certificates, curriculum, dashboard, employers, institutions,
    jobs, labour_market, ml, resumes, roles, skills, students,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("skillbridge")

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Role-based career intelligence platform: Student / Employer / Institution / Government portals (SIH26134)",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(resumes.router)
app.include_router(certificates.router)
app.include_router(employers.router)
app.include_router(institutions.router)
app.include_router(admin.router)
app.include_router(jobs.router)
app.include_router(skills.router)
app.include_router(roles.router)
app.include_router(curriculum.router)
app.include_router(labour_market.router)
app.include_router(dashboard.router)
app.include_router(ml.router)


@app.on_event("startup")
def on_startup():
    try:
        init_db()
        logger.info("Database tables verified/created.")
    except Exception as e:
        logger.error(
            f"Could not connect to PostgreSQL ({e}). Platform features (auth, "
            "portals) will not work until DATABASE_URL is reachable. Labour-market "
            "analytics endpoints (dashboard, skills, roles) will still work since "
            "they read directly from the CSV pipeline."
        )


@app.get("/")
def root():
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.exception_handler(FileNotFoundError)
def handle_missing_pipeline_output(request, exc):
    from fastapi.responses import JSONResponse
    logger.error(f"Pipeline output missing: {exc}")
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Required data file not found. Run the data pipeline first: "
                       "python scripts/generate_dataset.py && python scripts/extract_skills.py && "
                       "python scripts/analyze_demand.py && python scripts/detect_trends.py"
        },
    )
