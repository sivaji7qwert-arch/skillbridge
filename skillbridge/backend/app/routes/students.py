from typing import List, Optional
from types import SimpleNamespace

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database_sql import get_db
from app.ml.matching_engine import skill_set_match
from app.models.db_models import ExternalCourse, StudentProfile, User
from app.services import data_service, dsa_service
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/students", tags=["students"])
LOCAL_STUDENT_PROFILES = {}


class OnboardingRequest(BaseModel):
    college_name: str
    course: str
    branch: str
    graduation_year: int
    career_interest: str
    known_skills: List[str] = []
    programming_languages: List[str] = []
    target_role: str


def _local_profile(user_id: str):
    profile = LOCAL_STUDENT_PROFILES.get(user_id)
    return SimpleNamespace(**profile) if profile else None


@router.post("/onboarding")
def complete_onboarding(
    req: OnboardingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    if str(current_user.id).startswith(("demo-", "local-")):
        LOCAL_STUDENT_PROFILES[current_user.id] = {
            "user_id": current_user.id,
            "college_name": req.college_name,
            "course": req.course,
            "branch": req.branch,
            "graduation_year": req.graduation_year,
            "career_interest": req.career_interest,
            "known_skills": req.known_skills,
            "programming_languages": req.programming_languages,
            "target_role": req.target_role,
            "onboarding_complete": True,
        }
        return {"message": "Onboarding complete", "target_role": req.target_role}

    profile = None
    if not str(current_user.id).startswith(("demo-", "local-")):
        profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if profile is None:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    profile.college_name = req.college_name
    profile.course = req.course
    profile.branch = req.branch
    profile.graduation_year = req.graduation_year
    profile.career_interest = req.career_interest
    profile.known_skills = req.known_skills
    profile.programming_languages = req.programming_languages
    profile.target_role = req.target_role
    profile.onboarding_complete = True

    db.commit()
    return {"message": "Onboarding complete", "target_role": req.target_role}


@router.get("/me/profile")
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    local_profile = _local_profile(current_user.id)
    if local_profile:
        return {
            "email": current_user.email, "full_name": current_user.full_name,
            "college_name": local_profile.college_name, "course": local_profile.course,
            "branch": local_profile.branch, "graduation_year": local_profile.graduation_year,
            "career_interest": local_profile.career_interest,
            "known_skills": local_profile.known_skills or [],
            "programming_languages": local_profile.programming_languages or [],
            "target_role": local_profile.target_role,
            "onboarding_complete": local_profile.onboarding_complete,
        }
    profile = None
    if not str(current_user.id).startswith(("demo-", "local-")):
        profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found — complete onboarding first")
    return {
        "email": current_user.email, "full_name": current_user.full_name,
        "college_name": profile.college_name, "course": profile.course, "branch": profile.branch,
        "graduation_year": profile.graduation_year, "career_interest": profile.career_interest,
        "known_skills": profile.known_skills or [], "programming_languages": profile.programming_languages or [],
        "target_role": profile.target_role, "onboarding_complete": profile.onboarding_complete,
    }


@router.get("/me/skill-gap")
def my_skill_gap(db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    profile = _local_profile(current_user.id)
    if profile is None and not str(current_user.id).startswith(("demo-", "local-")):
        profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    if profile is None or not profile.target_role:
        raise HTTPException(status_code=404, detail="Complete onboarding first (need a target role)")

    roles_path = data_service._path("roles.csv", raw=True)
    import pandas as pd
    roles_df = pd.read_csv(roles_path)
    role_row = roles_df[roles_df["name"] == profile.target_role]
    if role_row.empty:
        raise HTTPException(status_code=404, detail=f"Target role '{profile.target_role}' not found in role catalog")

    required_skills = [s.strip() for s in role_row.iloc[0]["core_skills"].split(",")]
    match = skill_set_match(profile.known_skills or [], required_skills)

    demand_df = data_service.load_skill_demand().set_index("skill")
    missing_with_priority = []
    for skill in match["missing_skills"]:
        score = float(demand_df.loc[skill]["skill_demand_score"]) if skill in demand_df.index else 50.0
        priority = "HIGH" if score >= 65 else ("MEDIUM" if score >= 40 else "LOW")
        missing_with_priority.append({"skill": skill, "priority": priority, "demand_score": round(score, 1)})
    missing_with_priority.sort(key=lambda m: -m["demand_score"])

    return {
        "target_role": profile.target_role,
        "match_pct": match["match_pct"],
        "matched_skills": match["matched_skills"],
        "missing_skills": missing_with_priority,
    }


@router.get("/me/course-recommendations")
def course_recommendations(db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    gap = my_skill_gap(db, current_user)
    missing_skills = {m["skill"].lower() for m in gap["missing_skills"]}

    try:
        courses = db.query(ExternalCourse).all()
    except Exception:
        return [
            {"provider": provider, "title": title, "url": url, "covers_missing_skills": [skill]}
            for provider, title, skill, url in [
                ("Infosys Springboard", "Programming Fundamentals with Python", "python", "https://infyspringboard.onwingspan.com/"),
                ("IBM", "Data Analysis with Python", "python", "https://www.coursera.org/learn/data-analysis-with-python"),
                ("Coursera", "Google Data Analytics Professional Certificate", "data analytics", "https://www.coursera.org/professional-certificates/google-data-analytics"),
            ]
            if skill in missing_skills
        ]
    recommendations = []
    for course in courses:
        taught = {s.lower() for s in (course.skills_taught or [])}
        overlap = missing_skills & taught
        if overlap:
            recommendations.append({
                "provider": course.provider, "title": course.title,
                "url": course.url, "covers_missing_skills": sorted(overlap),
            })
    recommendations.sort(key=lambda r: -len(r["covers_missing_skills"]))
    return recommendations[:10]


@router.get("/me/dsa-roadmap")
def dsa_roadmap(current_user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    profile = _local_profile(current_user.id)
    if profile is None and not str(current_user.id).startswith(("demo-", "local-")):
        profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    target_role = profile.target_role if profile and profile.target_role else "Software Engineer"
    return dsa_service.get_roadmap(target_role)


@router.get("/me/dsa-progress")
def dsa_progress(current_user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    return dsa_service.get_progress_summary(db, current_user.id)


@router.get("/me/dsa-next")
def dsa_next(current_user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    profile = _local_profile(current_user.id)
    if profile is None and not str(current_user.id).startswith(("demo-", "local-")):
        profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
    target_role = profile.target_role if profile and profile.target_role else "Software Engineer"
    return dsa_service.recommend_next_problems(db, current_user.id, target_role)


class SolveRequest(BaseModel):
    topic: str
    title: str
    difficulty: str
    platform: str = "LeetCode"


@router.post("/me/dsa-solve")
def dsa_mark_solved(req: SolveRequest, current_user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    entry = dsa_service.mark_problem_solved(db, current_user.id, req.topic, req.title, req.difficulty, req.platform)
    return {"message": "Marked solved", "problem": req.title}
