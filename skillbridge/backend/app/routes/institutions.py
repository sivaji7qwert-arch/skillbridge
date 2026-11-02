from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database_sql import get_db
from app.models.db_models import InstitutionCourse, InstitutionProfile, StudentProfile, User
from app.services import data_service
from app.utils.security import require_role

router = APIRouter(prefix="/api/institution", tags=["institutions"])


class CourseRequest(BaseModel):
    department: str
    course_name: str
    taught_skills: List[str]


@router.post("/courses")
def add_course(req: CourseRequest, db: Session = Depends(get_db), current_user: User = Depends(require_role("institution"))):
    course = InstitutionCourse(institution_id=current_user.id, **req.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return {"course_id": course.id, "course_name": course.course_name}


@router.get("/courses")
def list_courses(db: Session = Depends(get_db), current_user: User = Depends(require_role("institution"))):
    courses = db.query(InstitutionCourse).filter_by(institution_id=current_user.id).all()
    return [{"course_id": c.id, "department": c.department, "course_name": c.course_name, "taught_skills": c.taught_skills} for c in courses]


@router.get("/student-skill-stats")
def student_skill_stats(db: Session = Depends(get_db), current_user: User = Depends(require_role("institution"))):
    """Aggregates known-skill data across this institution's students
    (matched by college_name) to show common skill gaps."""
    profile = db.query(InstitutionProfile).filter_by(user_id=current_user.id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Institution profile not found")

    students = db.query(StudentProfile).filter_by(college_name=profile.institution_name).all()
    if not students:
        return {"total_students": 0, "message": "No students registered under this institution name yet."}

    skill_counts = {}
    for s in students:
        for skill in (s.known_skills or []):
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

    total = len(students)
    demand_df = data_service.load_skill_demand().set_index("skill")

    # skills that are highly in demand but rare among this institution's students -> common gap
    common_gaps = []
    for skill, row in demand_df.iterrows():
        student_coverage_pct = round(skill_counts.get(skill, 0) / total * 100, 1)
        if row["skill_demand_score"] >= 50 and student_coverage_pct < 30:
            common_gaps.append({
                "skill": skill, "industry_demand_score": round(float(row["skill_demand_score"]), 1),
                "student_coverage_pct": student_coverage_pct,
            })
    common_gaps.sort(key=lambda g: -g["industry_demand_score"])

    return {
        "total_students": total,
        "top_known_skills": sorted(skill_counts.items(), key=lambda kv: -kv[1])[:10],
        "common_skill_gaps": common_gaps[:10],
    }


@router.get("/placement-readiness")
def placement_readiness(db: Session = Depends(get_db), current_user: User = Depends(require_role("institution"))):
    profile = db.query(InstitutionProfile).filter_by(user_id=current_user.id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Institution profile not found")

    students = db.query(StudentProfile).filter_by(college_name=profile.institution_name).all()
    ready, developing, early = 0, 0, 0
    for s in students:
        skill_count = len(s.known_skills or [])
        if skill_count >= 6:
            ready += 1
        elif skill_count >= 3:
            developing += 1
        else:
            early += 1

    return {
        "total_students": len(students),
        "readiness_breakdown": {"Placement Ready": ready, "Developing": developing, "Early Stage": early},
        "note": "Readiness is estimated from known-skill count relative to target-role requirements — a simple heuristic, not a certified assessment.",
    }
