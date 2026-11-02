"""
predictor.py
-------------
Loads the trained model bundle (models/skill_trend_model.joblib,
produced by scripts/train_model.py) and exposes prediction functions
for the API layer.

If the model file doesn't exist yet (train_model.py hasn't been run),
functions raise a clear error rather than failing with a confusing
stack trace deep in joblib.
"""
import os
from functools import lru_cache

import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "skill_trend_model.joblib")


class ModelNotTrainedError(Exception):
    pass


@lru_cache
def load_bundle():
    if not os.path.exists(MODEL_PATH):
        raise ModelNotTrainedError(
            f"No trained model found at {os.path.abspath(MODEL_PATH)}. "
            "Run: python scripts/train_model.py"
        )
    return joblib.load(MODEL_PATH)


def predict_trend(features: dict) -> dict:
    """features must contain all keys in bundle['feature_cols_classifier']."""
    bundle = load_bundle()
    clf = bundle["trend_classifier"]
    le = bundle["label_encoder"]
    cols = bundle["feature_cols_classifier"]

    if clf is None:
        raise ModelNotTrainedError("Trend classifier was not trained (insufficient data at training time).")

    x = np.array([[features.get(c, 0.0) for c in cols]])
    pred_idx = clf.predict(x)[0]
    pred_label = le.inverse_transform([pred_idx])[0]
    proba = clf.predict_proba(x)[0]
    proba_by_class = {le.inverse_transform([i])[0]: round(float(p), 4) for i, p in enumerate(proba)}

    return {"predicted_trend": pred_label, "class_probabilities": proba_by_class}


def predict_demand_score(features: dict) -> dict:
    bundle = load_bundle()
    reg = bundle["demand_regressor"]
    cols = bundle["feature_cols_regressor"]

    if reg is None:
        raise ModelNotTrainedError("Demand regressor was not trained (insufficient data at training time).")

    x = np.array([[features.get(c, 0.0) for c in cols]])
    score = float(reg.predict(x)[0])
    return {"predicted_demand_score": round(score, 2)}


def get_model_metrics() -> dict:
    bundle = load_bundle()
    return bundle.get("metrics", {})
