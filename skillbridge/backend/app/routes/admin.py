from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database_sql import get_db
from app.models.db_models import InstitutionProfile, StudentProfile, User, UserRole
from app.services import data_service
from app.utils.security import require_role

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/overview")
def platform_overview(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    total_users = db.query(func.count(User.id)).scalar()
    total_students = db.query(func.count(User.id)).filter(User.role == UserRole.student).scalar()
    total_employers = db.query(func.count(User.id)).filter(User.role == UserRole.employer).scalar()
    total_institutions = db.query(func.count(User.id)).filter(User.role == UserRole.institution).scalar()

    jobs_df = data_service.load_jobs_with_skills()
    skills_df = data_service.load_skill_demand()
    emerging_df = data_service.load_emerging_roles()

    return {
        "total_users": total_users, "total_students": total_students,
        "total_employers": total_employers, "total_institutions": total_institutions,
        "jobs_analyzed": int(jobs_df["job_id"].nunique()),
        "skills_tracked": int(skills_df["skill"].nunique()),
        "emerging_roles": int((emerging_df["trend"] == "Emerging").sum()),
    }


@router.get("/district-skill-gaps")
def district_skill_gaps(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    """City-wise (used as a proxy for district) skill demand, sourced
    from the labour-market analytics pipeline."""
    geo_df = data_service.load_skill_demand_by_city()
    result = {}
    for city, group in geo_df.groupby("city"):
        top = group.sort_values("demand_pct_in_city", ascending=False).head(5)
        result[city] = top[["skill", "demand_pct_in_city"]].to_dict(orient="records")
    return result


@router.get("/institution-readiness")
def institution_readiness(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    institutions = db.query(InstitutionProfile).all()
    result = []
    for inst in institutions:
        students = db.query(StudentProfile).filter_by(college_name=inst.institution_name).all()
        ready = sum(1 for s in students if len(s.known_skills or []) >= 6)
        result.append({
            "institution_name": inst.institution_name, "city": inst.city,
            "total_students": len(students), "placement_ready_pct": round(ready / len(students) * 100, 1) if students else 0.0,
        })
    return result


@router.get("/emerging-roles")
def emerging_roles(current_user: User = Depends(require_role("admin"))):
    df = data_service.load_emerging_roles()
    return df.sort_values("growth_pct", ascending=False).head(15).to_dict(orient="records")
