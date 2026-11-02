from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ml.predictor import ModelNotTrainedError, get_model_metrics, predict_demand_score, predict_trend

router = APIRouter(prefix="/api/ml", tags=["ml"])


class TrendPredictRequest(BaseModel):
    demand_percentage: float = 0.0
    growth_pct: float = 0.0
    recent_count: float = 0.0
    prior_count: float = 0.0
    avg_salary: float = 0.0
    salary_score: float = 0.0
    geo_avg_demand_pct: float = 0.0
    frequency_score: float = 0.0
    growth_score: float = 0.0
    geo_score: float = 0.0


class DemandPredictRequest(BaseModel):
    demand_percentage: float = 0.0
    growth_pct: float = 0.0
    avg_salary: float = 0.0
    geo_avg_demand_pct: float = 0.0


@router.get("/metrics")
def model_metrics():
    """Reports the trained model's held-out test accuracy/MAE, so the
    frontend can show these aren't hand-picked numbers."""
    try:
        return get_model_metrics()
    except ModelNotTrainedError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/predict-trend")
def predict_skill_trend(req: TrendPredictRequest):
    try:
        return predict_trend(req.model_dump())
    except ModelNotTrainedError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/predict-demand-score")
def predict_skill_demand_score(req: DemandPredictRequest):
    try:
        return predict_demand_score(req.model_dump())
    except ModelNotTrainedError as e:
        raise HTTPException(status_code=503, detail=str(e))
