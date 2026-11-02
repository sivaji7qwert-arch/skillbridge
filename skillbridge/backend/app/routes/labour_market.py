from fastapi import APIRouter

from app.services import data_service

router = APIRouter(prefix="/api/labour-market", tags=["labour-market"])


@router.get("/overview")
def overview():
    jobs = data_service.load_jobs_with_skills()
    skills = data_service.load_skill_demand()
    emerging = data_service.load_emerging_roles()

    return {
        "total_jobs": int(jobs["job_id"].nunique()),
        "total_skills_tracked": int(skills["skill"].nunique()),
        "emerging_roles_count": int((emerging["trend"] == "Emerging").sum()),
        "top_cities": jobs["location"].value_counts().head(8).to_dict(),
        "top_sectors": jobs["industry"].value_counts().head(10).to_dict(),
        "top_skills": skills.sort_values("skill_demand_score", ascending=False).head(10)[["skill", "skill_demand_score"]].to_dict(orient="records"),
    }
