"""
train_model.py
----------------
Trains an actual ML model (not rule-based) on top of the pipeline's
skill demand output: a RandomForestClassifier that predicts a skill's
trend label (Emerging / Growing / Stable / Declining) from its
demand features (demand %, growth %, salary score, geographic spread).

This complements analyze_demand.py's threshold-based trend labels —
the rule-based labels in analyze_demand.py are the TRAINING TARGET,
and this model learns to generalize that labeling logic so it can
score skills that don't yet have enough posting volume for the
threshold rule to fire confidently (see MIN_POSTINGS in analyze_demand.py),
or so it can be re-used as a scoring function once live job-portal
data replaces the synthetic dataset.

Also trains a secondary regressor that predicts a skill's demand
score directly from its raw signals — used for a "what-if" style
estimate when new skills are added to the dictionary before enough
job postings exist for them.

Usage:
    python scripts/train_model.py \
        --demand ../data/processed/skill_demand.csv \
        --out ../models/trend_classifier.joblib
"""
import argparse
import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

FEATURE_COLS = [
    "demand_percentage", "growth_pct", "recent_count", "prior_count",
    "avg_salary", "salary_score", "geo_avg_demand_pct",
    "frequency_score", "growth_score", "geo_score",
]


def load_and_prepare(demand_csv):
    df = pd.read_csv(demand_csv)
    df = df.dropna(subset=FEATURE_COLS + ["trend", "skill_demand_score"])
    # Exclude the "Insufficient Data" bucket from classifier training —
    # it's a data-volume artifact, not a real trend signal, and including
    # it would just teach the model to memorize "low recent_count".
    df = df[df["trend"] != "Insufficient Data"].reset_index(drop=True)
    return df


def train_trend_classifier(df):
    X = df[FEATURE_COLS].values
    le = LabelEncoder()
    y = le.fit_transform(df["trend"].values)

    if len(df) < 10 or len(set(y)) < 2:
        print("Not enough labeled data / class diversity to train a classifier reliably. "
              "Skipping classifier training — run with a larger dataset (more skills / more history).")
        return None, le, None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y if min(np.bincount(y)) >= 2 else None
    )

    clf = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42, class_weight="balanced")
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0)

    print(f"\nTrend Classifier — test accuracy: {acc:.3f}\n")
    print(report)

    feature_importance = dict(zip(FEATURE_COLS, clf.feature_importances_.round(4)))
    print("Feature importances:", json.dumps(feature_importance, indent=2))

    return clf, le, {"accuracy": round(float(acc), 4), "feature_importance": feature_importance}


def train_demand_regressor(df):
    # predicts skill_demand_score from the underlying raw signals — useful
    # for scoring a brand-new skill (e.g. just added to the dictionary)
    # once you have even a handful of postings for it.
    feature_cols = ["demand_percentage", "growth_pct", "avg_salary", "geo_avg_demand_pct"]
    X = df[feature_cols].values
    y = df["skill_demand_score"].values

    if len(df) < 10:
        print("Not enough data to train the demand regressor. Skipping.")
        return None, None

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    reg = RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42)
    reg.fit(X_train, y_train)

    y_pred = reg.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"\nDemand Score Regressor — test MAE: {mae:.2f} (score scale is 0-100)")

    return reg, {"mae": round(float(mae), 2), "feature_cols": feature_cols}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demand", default="../data/processed/skill_demand.csv")
    parser.add_argument("--out-dir", default="../models")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    df = load_and_prepare(args.demand)
    print(f"Training on {len(df)} labeled skills (trend classes: {df['trend'].value_counts().to_dict()})")

    clf, label_encoder, clf_metrics = train_trend_classifier(df)
    reg, reg_metrics = train_demand_regressor(df)

    bundle = {
        "trend_classifier": clf,
        "label_encoder": label_encoder,
        "demand_regressor": reg,
        "feature_cols_classifier": FEATURE_COLS,
        "feature_cols_regressor": ["demand_percentage", "growth_pct", "avg_salary", "geo_avg_demand_pct"],
        "metrics": {"classifier": clf_metrics, "regressor": reg_metrics},
    }

    out_path = os.path.join(args.out_dir, "skill_trend_model.joblib")
    joblib.dump(bundle, out_path)
    print(f"\nSaved trained model bundle -> {out_path}")

    metrics_path = os.path.join(args.out_dir, "model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(bundle["metrics"], f, indent=2)
    print(f"Saved metrics -> {metrics_path}")


if __name__ == "__main__":
    main()
