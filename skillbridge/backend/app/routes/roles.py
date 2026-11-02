from fastapi import APIRouter

from app.services import data_service

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get("")
def list_roles():
    df = data_service.load_roles()
    return df.to_dict(orient="records")


@router.get("/trending")
def trending_roles(limit: int = 10):
    df = data_service.load_emerging_roles().sort_values("growth_pct", ascending=False)
    return df.head(limit).to_dict(orient="records")
