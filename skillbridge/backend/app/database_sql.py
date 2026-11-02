"""
database_sql.py
-----------------
PostgreSQL connection (SQLAlchemy) for platform data: accounts, profiles,
job postings, applications, resumes, certificates, DSA progress.

This is separate from app/services/data_service.py, which reads the
bulk job-market analytics (skill demand, trends) from the CSV pipeline
in data/processed/ — that data is recomputed wholesale by the pipeline
scripts and doesn't belong in transactional storage.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.db_models import Base

settings = get_settings()

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency — yields a session, closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Creates all tables if they don't exist yet. Prefer running
    schema.sql directly for production; this is a convenience for local
    dev so `uvicorn app.main:app` works right after `createdb skillbridge`
    without a manual psql step."""
    Base.metadata.create_all(bind=engine)
