"""
detect_trends.py
-----------------
Thin CLI wrapper around the trend-classification logic in
analyze_demand.py, plus emerging-role detection: roles whose posting
volume grew fastest in the most recent window, combined with the set
of skills that co-occur most with them (used by the "Emerging Job
Detection" feature, spec section 11).

Usage:
    python scripts/detect_trends.py --jobs ../data/processed/jobs_with_skills.csv \
                                     --out ../data/processed/emerging_roles.csv
"""
import argparse
import json
import os
from datetime import timedelta

import pandas as pd


def detect_emerging_roles(jobs, out_csv):
    jobs = jobs.copy()
    jobs["posting_date"] = pd.to_datetime(jobs["posting_date"])
    cutoff_recent = jobs["posting_date"].max() - timedelta(days=180)
    cutoff_prior_start = cutoff_recent - timedelta(days=180)

    recent = jobs[jobs["posting_date"] >= cutoff_recent]
    prior = jobs[(jobs["posting_date"] >= cutoff_prior_start) & (jobs["posting_date"] < cutoff_recent)]

    recent_counts = recent.groupby("normalized_role")["job_id"].nunique()
    prior_counts = prior.groupby("normalized_role")["job_id"].nunique()

    rows = []
    for role in set(recent_counts.index) | set(prior_counts.index):
        r = recent_counts.get(role, 0)
        p = prior_counts.get(role, 0)
        growth = 100.0 if p == 0 and r > 0 else (round((r - p) / p * 100, 2) if p else 0.0)
        role_jobs = recent[recent["normalized_role"] == role]
        avg_salary = round(((role_jobs["salary_min"] + role_jobs["salary_max"]) / 2).mean(), 0) if len(role_jobs) else 0
        top_cities = role_jobs["location"].value_counts().head(3).index.tolist()
        # aggregate top co-occurring skills
        skill_counts = {}
        for skills_json in role_jobs["extracted_skills"]:
            for s in json.loads(skills_json):
                skill_counts[s] = skill_counts.get(s, 0) + 1
        top_skills = sorted(skill_counts, key=skill_counts.get, reverse=True)[:6]

        rows.append({
            "role": role,
            "current_demand_postings": r,
            "growth_pct": growth,
            "required_skills": ", ".join(top_skills),
            "top_locations": ", ".join(top_cities),
            "avg_salary": avg_salary,
            "trend": "Emerging" if growth >= 40 and r >= 5 else ("Growing" if growth >= 10 else "Stable"),
        })

    df = pd.DataFrame(rows).sort_values("growth_pct", ascending=False)
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", default="../data/processed/jobs_with_skills.csv")
    parser.add_argument("--out", default="../data/processed/emerging_roles.csv")
    args = parser.parse_args()

    jobs = pd.read_csv(args.jobs)
    df = detect_emerging_roles(jobs, args.out)
    print(f"Wrote {len(df)} roles -> {args.out}\n")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
