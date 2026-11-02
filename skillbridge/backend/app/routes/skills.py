from typing import Optional

from fastapi import APIRouter

from app.services import data_service

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("")
def list_skills():
    df = data_service.load_skill_demand()
    return df.to_dict(orient="records")


@router.get("/trending")
def trending_skills(limit: int = 10):
    df = data_service.load_skill_demand().sort_values("skill_demand_score", ascending=False)
    return df.head(limit).to_dict(orient="records")


@router.get("/by-city")
def skills_by_city(city: Optional[str] = None):
    df = data_service.load_skill_demand_by_city()
    if city:
        df = df[df["city"] == city]
    return df.to_dict(orient="records")
