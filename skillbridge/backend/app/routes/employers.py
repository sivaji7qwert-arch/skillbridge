from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database_sql import get_db
from app.ml.matching_engine import compute_match
from app.models.db_models import Application, Company, JobPosting, StudentProfile, User
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/employer", tags=["employers"])
LOCAL_COMPANIES = {}
LOCAL_JOBS = {}


class CompanyRequest(BaseModel):
    name: str
    sector: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None


@router.post("/company")
def create_or_update_company(req: CompanyRequest, db: Session = Depends(get_db), current_user: User = Depends(require_role("employer"))):
    if str(current_user.id).startswith(("demo-", "local-")):
        LOCAL_COMPANIES[current_user.id] = {"company_id": f"local-company-{uuid.uuid4()}", **req.model_dump()}
        return {"company_id": LOCAL_COMPANIES[current_user.id]["company_id"], "name": req.name}

    company = db.query(Company).filter_by(employer_id=current_user.id).first()
    if company is None:
        company = Company(employer_id=current_user.id, **req.model_dump())
        db.add(company)
    else:
        for k, v in req.model_dump().items():
            setattr(company, k, v)
    db.commit()
    db.refresh(company)
    return {"company_id": company.id, "name": company.name}


class JobPostRequest(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    preferred_qualifications: Optional[str] = None
    location: Optional[str] = None
    experience_required: int = 0


@router.post("/jobs")
def post_job(req: JobPostRequest, db: Session = Depends(get_db), current_user: User = Depends(require_role("employer"))):
    if str(current_user.id).startswith(("demo-", "local-")):
        if current_user.id not in LOCAL_COMPANIES:
            raise HTTPException(status_code=400, detail="Create a company profile before posting jobs")
        job_id = f"local-job-{uuid.uuid4()}"
        LOCAL_JOBS.setdefault(current_user.id, []).insert(0, {"job_id": job_id, **req.model_dump(), "application_count": 0})
        return {"job_id": job_id, "title": req.title}

    company = db.query(Company).filter_by(employer_id=current_user.id).first()
    if company is None:
        raise HTTPException(status_code=400, detail="Create a company profile before posting jobs")

    job = JobPosting(company_id=company.id, **req.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id, "title": job.title}


@router.get("/jobs")
def my_jobs(db: Session = Depends(get_db), current_user: User = Depends(require_role("employer"))):
    if str(current_user.id).startswith(("demo-", "local-")):
        return LOCAL_JOBS.get(current_user.id, [])

    company = db.query(Company).filter_by(employer_id=current_user.id).first()
    if company is None:
        return []
    jobs = db.query(JobPosting).filter_by(company_id=company.id).order_by(JobPosting.created_at.desc()).all()
    return [
        {
            "job_id": j.id, "title": j.title, "required_skills": j.required_skills,
            "location": j.location, "is_active": j.is_active,
            "application_count": len(j.applications),
        }
        for j in jobs
    ]


@router.get("/jobs/{job_id}/candidates")
def ranked_candidates(
    job_id: str,
    min_experience: Optional[int] = None,
    institution: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("employer")),
):
    """AI-ranked candidates for a job: every student with an onboarded
    profile is scored against this job's requirements via the TF-IDF +
    skill-overlap matching engine, with an explainable score breakdown."""
    job = db.query(JobPosting).filter_by(id=job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    company = db.query(Company).filter_by(employer_id=current_user.id).first()
    if company is None or job.company_id != company.id:
        raise HTTPException(status_code=403, detail="You can only view candidates for your own job postings")

    query = db.query(StudentProfile).filter(StudentProfile.onboarding_complete.is_(True))
    if institution:
        query = query.filter(StudentProfile.college_name == institution)
    if min_experience is not None:
        pass  # student profiles in this prototype don't track work experience years; reserved for future extension

    candidates = query.all()
    results = []
    for c in candidates:
        student_text = f"{c.course} {c.branch} {c.career_interest} {' '.join(c.known_skills or [])}"
        match = compute_match(
            candidate_skills=c.known_skills or [], candidate_text=student_text,
            required_skills=job.required_skills, job_text=job.description,
        )
        results.append({
            "student_id": c.user_id,
            "college_name": c.college_name, "course": c.course, "branch": c.branch,
            **match,
        })

    results.sort(key=lambda r: -r["overall_match_score"])
    return results


@router.get("/applications")
def list_applications(db: Session = Depends(get_db), current_user: User = Depends(require_role("employer"))):
    company = db.query(Company).filter_by(employer_id=current_user.id).first()
    if company is None:
        return []
    job_ids = [j.id for j in db.query(JobPosting).filter_by(company_id=company.id).all()]
    apps = db.query(Application).filter(Application.job_id.in_(job_ids)).all()
    return [
        {"application_id": a.id, "job_id": a.job_id, "student_id": a.student_id,
         "match_score": a.match_score, "status": a.status.value, "applied_at": a.applied_at}
        for a in apps
    ]


class ApplicationStatusUpdate(BaseModel):
    status: str  # Applied | Shortlisted | Rejected | Hired


@router.patch("/applications/{application_id}")
def update_application_status(application_id: str, req: ApplicationStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("employer"))):
    app_row = db.query(Application).filter_by(id=application_id).first()
    if app_row is None:
        raise HTTPException(status_code=404, detail="Application not found")
    from app.models.db_models import ApplicationStatus
    try:
        app_row.status = ApplicationStatus(req.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status '{req.status}'")
    db.commit()
    return {"message": "Status updated", "status": app_row.status.value}
