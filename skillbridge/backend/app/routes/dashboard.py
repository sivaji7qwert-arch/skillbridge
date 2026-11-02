from fastapi import APIRouter

from app.services import data_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def dashboard_kpis():
    jobs = data_service.load_jobs_with_skills()
    skills = data_service.load_skill_demand()
    emerging = data_service.load_emerging_roles()
    curricula = data_service.load_curricula()

    return {
        "total_jobs_analyzed": int(jobs["job_id"].nunique()),
        "total_skills_detected": int(skills["skill"].nunique()),
        "emerging_skills_count": int((skills["trend"] == "Emerging").sum()),
        "emerging_roles_count": int((emerging["trend"] == "Emerging").sum()),
        "curricula_tracked": int(curricula["curriculum_id"].nunique()),
        "top_5_skills": skills.sort_values("skill_demand_score", ascending=False).head(5)["skill"].tolist(),
    }
