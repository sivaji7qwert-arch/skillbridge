from fastapi import APIRouter, HTTPException

from app.schemas.schemas import CurriculumAnalyzeRequest
from app.services import data_service, gap_service

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])


@router.get("")
def list_curricula():
    df = data_service.load_curricula()
    return df.drop(columns=["modules_json"]).to_dict(orient="records")


@router.get("/{curriculum_id}")
def get_curriculum(curriculum_id: str):
    df = data_service.load_curricula()
    row = df[df["curriculum_id"] == curriculum_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    result = row.iloc[0].to_dict()
    import json
    result["modules"] = json.loads(result.pop("modules_json"))
    return result


@router.post("/analyze")
def analyze(req: CurriculumAnalyzeRequest):
    try:
        return gap_service.analyze_curriculum(req.role, req.curriculum_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
