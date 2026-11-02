import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database_sql import get_db
from app.models.db_models import Resume, StudentProfile, User
from app.services.resume_service import UnsupportedFileTypeError, parse_resume
from app.utils.security import require_role

router = APIRouter(prefix="/api/resumes", tags=["resumes"])
settings = get_settings()


@router.post("/upload")
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    file_bytes = file.file.read()
    skills_csv = os.path.join(settings.RAW_DATA_DIR, "skills.csv")

    try:
        raw_text, extracted_skills = parse_resume(file.filename, file_bytes, skills_csv)
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    upload_dir = os.path.join(settings.UPLOAD_DIR, "resumes")
    os.makedirs(upload_dir, exist_ok=True)
    stored_name = f"{current_user.id}_{uuid.uuid4().hex[:8]}_{file.filename}"
    stored_path = os.path.join(upload_dir, stored_name)
    with open(stored_path, "wb") as f:
        f.write(file_bytes)

    resume = Resume(
        student_id=current_user.id, file_path=stored_path,
        raw_text=raw_text, extracted_skills=extracted_skills,
    )
    db.add(resume)

    # merge resume-derived skills into the student's known_skills
    profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if profile:
        existing = set(profile.known_skills or [])
        profile.known_skills = sorted(existing | set(extracted_skills))

    db.commit()
    db.refresh(resume)

    return {
        "resume_id": resume.id,
        "extracted_skills": extracted_skills,
        "message": f"Resume parsed successfully. {len(extracted_skills)} skills detected and merged into your profile.",
    }


@router.get("/mine")
def my_resumes(db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    resumes = db.query(Resume).filter_by(student_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    return [
        {"resume_id": r.id, "extracted_skills": r.extracted_skills, "uploaded_at": r.uploaded_at}
        for r in resumes
    ]
