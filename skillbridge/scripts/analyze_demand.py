"""
analyze_demand.py
------------------
Computes:
  - Skill frequency & demand percentage
  - Geographic demand by city
  - Growth rate (recent 6 months vs prior 6 months window)
  - Trend classification: Emerging / Growing / Stable / Declining
  - Composite Skill Demand Score (weights are configurable business
    weights, NOT claimed to be scientifically optimal — see section 9
    of the spec)

Usage:
    python scripts/analyze_demand.py \
        --jobs ../data/processed/jobs_with_skills.csv \
        --out ../data/processed/skill_demand.csv
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]


def resolve_repo_path(path):
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate

    resolved = (Path.cwd() / candidate).resolve()
    if resolved.exists():
        return resolved

    if candidate.parts and candidate.parts[0] == "..":
        cleaned = Path(*candidate.parts[1:])
        return (REPO_ROOT / cleaned).resolve()

    return (REPO_ROOT / candidate).resolve()


# Configurable business weights for the composite Skill Demand Score.
# NOTE: these are illustrative weights for the prototype, not derived
# from a validated statistical model.
WEIGHTS = {
    "frequency": 0.40,
    "growth": 0.25,
    "salary": 0.20,
    "geographic": 0.15,
}


def explode_skills(jobs):
    jobs = jobs.copy()
    jobs["extracted_skills"] = jobs["extracted_skills"].apply(json.loads)
    exploded = jobs.explode("extracted_skills").rename(columns={"extracted_skills": "skill"})
    exploded = exploded.dropna(subset=["skill"])
    return exploded


def compute_frequency(exploded, total_jobs):
    freq = exploded.groupby("skill")["job_id"].nunique().reset_index()
    freq.columns = ["skill", "job_count"]
    freq["demand_percentage"] = (freq["job_count"] / total_jobs * 100).round(2)
    return freq


def compute_growth(exploded):
    exploded = exploded.copy()
    exploded["posting_date"] = pd.to_datetime(exploded["posting_date"])
    cutoff_recent = exploded["posting_date"].max() - timedelta(days=180)
    cutoff_prior_start = cutoff_recent - timedelta(days=180)

    recent = exploded[exploded["posting_date"] >= cutoff_recent]
    prior = exploded[(exploded["posting_date"] >= cutoff_prior_start) & (exploded["posting_date"] < cutoff_recent)]

    recent_counts = recent.groupby("skill")["job_id"].nunique()
    prior_counts = prior.groupby("skill")["job_id"].nunique()

    growth_rows = []
    for skill in set(recent_counts.index) | set(prior_counts.index):
        r = recent_counts.get(skill, 0)
        p = prior_counts.get(skill, 0)
        if p == 0:
            growth = 100.0 if r > 0 else 0.0  # brand-new signal
        else:
            growth = round(((r - p) / p) * 100, 2)
        growth_rows.append({"skill": skill, "recent_count": r, "prior_count": p, "growth_pct": growth})
    return pd.DataFrame(growth_rows)


def classify_trend(growth_pct, recent_count):
    if recent_count < 5:
        return "Insufficient Data"
    if growth_pct >= 40:
        return "Emerging"
    if growth_pct >= 10:
        return "Growing"
    if growth_pct >= -10:
        return "Stable"
    return "Declining"


def compute_geographic(exploded):
    geo = exploded.groupby(["location", "skill"])["job_id"].nunique().reset_index()
    geo.columns = ["city", "skill", "job_count"]
    city_totals = exploded.groupby("location")["job_id"].nunique().to_dict()
    geo["demand_pct_in_city"] = geo.apply(
        lambda r: round(r["job_count"] / city_totals.get(r["city"], 1) * 100, 2), axis=1
    )
    return geo


def compute_salary_score(exploded):
    sal = exploded.groupby("skill")[["salary_min", "salary_max"]].mean().reset_index()
    sal["avg_salary"] = ((sal["salary_min"] + sal["salary_max"]) / 2).round(0)
    max_sal = sal["avg_salary"].max()
    sal["salary_score"] = (sal["avg_salary"] / max_sal * 100).round(2)
    return sal[["skill", "avg_salary", "salary_score"]]


def normalize_0_100(series):
    lo, hi = series.min(), series.max()
    if hi == lo:
        return series.apply(lambda x: 50.0)
    return ((series - lo) / (hi - lo) * 100).round(2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", default=str(REPO_ROOT / "data" / "processed" / "jobs_with_skills.csv"))
    parser.add_argument("--out", default=str(REPO_ROOT / "data" / "processed" / "skill_demand.csv"))
    parser.add_argument("--geo-out", default=str(REPO_ROOT / "data" / "processed" / "skill_demand_by_city.csv"))
    args = parser.parse_args()

    jobs = pd.read_csv(resolve_repo_path(args.jobs))
    total_jobs = jobs["job_id"].nunique()
    exploded = explode_skills(jobs)

    freq = compute_frequency(exploded, total_jobs)
    growth = compute_growth(exploded)
    salary = compute_salary_score(exploded)
    geo = compute_geographic(exploded)

    # geographic demand score per skill = avg demand pct across cities where it appears
    geo_score = geo.groupby("skill")["demand_pct_in_city"].mean().reset_index()
    geo_score.columns = ["skill", "geo_avg_demand_pct"]

    merged = freq.merge(growth, on="skill", how="left").merge(salary, on="skill", how="left").merge(geo_score, on="skill", how="left")
    merged = merged.fillna(0)

    merged["trend"] = merged.apply(lambda r: classify_trend(r["growth_pct"], r["recent_count"]), axis=1)

    merged["frequency_score"] = normalize_0_100(merged["demand_percentage"])
    merged["growth_score"] = normalize_0_100(merged["growth_pct"])
    merged["geo_score"] = normalize_0_100(merged["geo_avg_demand_pct"])

    merged["skill_demand_score"] = (
        WEIGHTS["frequency"] * merged["frequency_score"]
        + WEIGHTS["growth"] * merged["growth_score"]
        + WEIGHTS["salary"] * merged["salary_score"]
        + WEIGHTS["geographic"] * merged["geo_score"]
    ).round(2)

    merged = merged.sort_values("skill_demand_score", ascending=False)

    output_dir = resolve_repo_path(os.path.dirname(args.out))
    output_dir.mkdir(parents=True, exist_ok=True)
    merged.to_csv(resolve_repo_path(args.out), index=False)
    geo.to_csv(resolve_repo_path(args.geo_out), index=False)

    print(f"Wrote skill demand analysis ({len(merged)} skills) -> {resolve_repo_path(args.out)}")
    print(f"Wrote geographic breakdown -> {resolve_repo_path(args.geo_out)}")
    print("\nTop 10 skills by composite demand score:")
    print(merged[["skill", "demand_percentage", "growth_pct", "trend", "skill_demand_score"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
