from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database_sql import get_db
from app.ml.matching_engine import compute_match
from app.models.db_models import Application, Company, JobPosting, StudentProfile, User
from app.services import data_service
from app.utils.security import require_role

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("")
def browse_jobs(
    location: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Public job browsing (platform postings from employers using
    SkillBridge, distinct from the bulk labour-market analytics dataset
    used for trend detection)."""
    try:
        query = db.query(JobPosting).filter_by(is_active=True)
        if location:
            query = query.filter(JobPosting.location == location)
        total = query.count()
        jobs = query.order_by(JobPosting.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return {
            "results": [
                {
                    "job_id": j.id,
                    "title": j.title,
                    "company": j.company.name,
                    "location": j.location,
                    "required_skills": j.required_skills,
                    "experience_required": j.experience_required,
                }
                for j in jobs
            ],
            "page": page,
            "page_size": page_size,
            "total": total,
        }
    except Exception:
        df = data_service.load_jobs_with_skills()
        if location:
            df = df[df["location"] == location]

        total = len(df)
        page_df = df.iloc[(page - 1) * page_size:page * page_size]
        results = [
            {
                "job_id": row["job_id"],
                "title": row["job_title"],
                "company": row.get("company"),
                "location": row.get("location"),
                "required_skills": row.get("extracted_skills") or row.get("skills"),
                "experience_required": row.get("experience_required"),
            }
            for _, row in page_df.iterrows()
        ]
        return {
            "results": results,
            "page": page,
            "page_size": page_size,
            "total": total,
        }


@router.post("/{job_id}/apply")
def apply_to_job(job_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    job = db.query(JobPosting).filter_by(id=job_id, is_active=True).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found or no longer active")

    existing = db.query(Application).filter_by(job_id=job_id, student_id=current_user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="You have already applied to this job")

    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if profile is None:
        raise HTTPException(status_code=400, detail="Complete your profile before applying")

    student_text = f"{profile.course} {profile.branch} {profile.career_interest} {' '.join(profile.known_skills or [])}"
    match = compute_match(profile.known_skills or [], student_text, job.required_skills, job.description)

    application = Application(job_id=job_id, student_id=current_user.id, match_score=match["overall_match_score"])
    db.add(application)
    db.commit()

    return {"message": "Applied successfully", "match_score": match["overall_match_score"], "evidence": match["evidence"]}


# --- Labour-market analytics endpoints (bulk CSV pipeline, unchanged) ---

@router.get("/market/stats")
def job_market_stats():
    df = data_service.load_jobs_with_skills()
    return {
        "total_jobs": int(df["job_id"].nunique()),
        "roles_covered": int(df["normalized_role"].nunique()),
        "cities_covered": int(df["location"].nunique()),
        "jobs_by_industry": df["industry"].value_counts().to_dict(),
        "jobs_by_city": df["location"].value_counts().to_dict(),
    }
