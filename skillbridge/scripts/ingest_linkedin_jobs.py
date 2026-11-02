"""
ingest_linkedin_jobs.py
-------------------------
Ingests the Kaggle "LinkedIn Jobs Dataset for India" (michellemiranda/
linkedin-jobs-dataset-for-india) and converts it into the schema the
rest of the SkillBridge pipeline expects (same shape as jobs.csv from
generate_dataset.py), so extract_skills.py / analyze_demand.py /
detect_trends.py all work unmodified against real data.

Source columns (as published on Kaggle):
    id, publishedAt, title, companyName, postedTime, applicationsCount,
    description, contractType, experienceLevel, workType, sector,
    companyId, city, state, recently_posted_jobs

Get the file:
    1. Download from https://www.kaggle.com/datasets/michellemiranda/linkedin-jobs-dataset-for-india
       (requires a free Kaggle account) OR via the Kaggle CLI:
           pip install kaggle
           kaggle datasets download -d michellemiranda/linkedin-jobs-dataset-for-india
           unzip linkedin-jobs-dataset-for-india.zip -d data/raw/
    2. Point --in at the resulting CSV.

Usage:
    python scripts/ingest_linkedin_jobs.py \
        --in ../data/raw/linkedin_jobs_india.csv \
        --out ../data/raw/jobs.csv

If --in is missing, this script generates a small SAMPLE file matching
the exact published schema so the rest of the pipeline stays runnable
for development/demo purposes — it is clearly labeled as sample data,
never presented as real LinkedIn data (see the `is_sample_data` flag
written into the output and the console warning).
"""
import argparse
import os
import re

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Sample-data fallback (clearly labeled, used only if no real file is given)
# ---------------------------------------------------------------------------
SAMPLE_ROWS = [
    {
        "id": 1, "publishedAt": "2026-06-01", "title": "Data Analyst",
        "companyName": "Bharat Technologies", "postedTime": "3 days ago",
        "applicationsCount": 42.0,
        "description": "Looking for a Data Analyst with Python, SQL, Power BI and Excel experience. 2+ years experience preferred.",
        "contractType": "Full-time", "experienceLevel": "Mid-Senior level",
        "workType": "On-site", "sector": "Information Technology",
        "companyId": 101, "city": "Pune", "state": "Maharashtra", "recently_posted_jobs": "Yes",
    },
    {
        "id": 2, "publishedAt": "2026-05-20", "title": "Machine Learning Engineer",
        "companyName": "Deccan Analytics", "postedTime": "2 weeks ago",
        "applicationsCount": 87.0,
        "description": "Machine Learning Engineer role requiring Python, TensorFlow, PyTorch, Docker, AWS and strong DSA fundamentals.",
        "contractType": "Full-time", "experienceLevel": "Associate",
        "workType": "Hybrid", "sector": "Information Technology",
        "companyId": 102, "city": "Mumbai", "state": "Maharashtra", "recently_posted_jobs": "No",
    },
]


def load_source(in_path):
    if in_path and os.path.exists(in_path):
        df = pd.read_csv(in_path)
        is_sample = False
        print(f"Loaded {len(df)} real rows from {in_path}")
    else:
        df = pd.DataFrame(SAMPLE_ROWS)
        is_sample = True
        print(f"WARNING: '{in_path}' not found. Using {len(df)} labeled SAMPLE rows "
              "for development only — this is NOT real LinkedIn data. "
              "Download the real dataset per the docstring instructions to replace this.")
    return df, is_sample


def parse_experience_years(level):
    """Maps LinkedIn's categorical experienceLevel to an approximate numeric
    years value, since the rest of the pipeline expects experience_required
    as an integer."""
    mapping = {
        "Internship": 0, "Entry level": 0, "Associate": 1,
        "Mid-Senior level": 4, "Director": 8, "Executive": 12,
    }
    if pd.isna(level):
        return 1
    return mapping.get(str(level).strip(), 1)


def parse_salary_stub(row):
    """The Kaggle dataset does not publish salary fields. Rather than
    inventing numbers, we leave salary as NaN and flag it so downstream
    salary-based scoring (analyze_demand.py's salary_score) degrades
    gracefully (treated as 0 contribution) instead of being fabricated."""
    return np.nan, np.nan


def normalize_location(city, state):
    city = str(city).strip().title() if pd.notna(city) else "Unknown"
    state = str(state).strip().title() if pd.notna(state) else "Unknown"
    return city, state


def clean(df, is_sample):
    df = df.drop_duplicates(subset=["id"]).copy()
    df = df.dropna(subset=["title", "description"])

    df["job_id"] = "LI" + df["id"].astype(str).str.zfill(7)
    df["job_title"] = df["title"].astype(str).str.strip()
    df["normalized_role"] = df["job_title"]  # role normalization happens in extract_skills/analyze_demand
    df["company"] = df["companyName"].astype(str).str.strip()

    city_state = df.apply(lambda r: normalize_location(r.get("city"), r.get("state")), axis=1)
    df["location"] = [c for c, s in city_state]
    df["state"] = [s for c, s in city_state]

    df["industry"] = df["sector"].fillna("Unspecified")
    df["experience_required"] = df["experienceLevel"].apply(parse_experience_years)
    df["education"] = "Not specified"  # not published by this dataset

    salaries = df.apply(parse_salary_stub, axis=1, result_type="expand")
    df["salary_min"], df["salary_max"] = salaries[0], salaries[1]

    df["skills"] = ""  # populated downstream by extract_skills.py from `description`
    df["description"] = df["description"].astype(str)
    df["posting_date"] = pd.to_datetime(df["publishedAt"], errors="coerce")
    df = df.dropna(subset=["posting_date"])
    df["posting_date"] = df["posting_date"].dt.strftime("%Y-%m-%d")
    df["employment_type"] = df["contractType"].fillna("Not specified")
    df["work_type"] = df["workType"].fillna("Not specified")
    df["applications_count"] = df["applicationsCount"].fillna(0).astype(int)
    df["is_sample_data"] = is_sample

    out_cols = [
        "job_id", "job_title", "normalized_role", "company", "location", "state",
        "industry", "experience_required", "education", "salary_min", "salary_max",
        "skills", "description", "posting_date", "employment_type", "work_type",
        "applications_count", "is_sample_data",
    ]
    return df[out_cols]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", default="../data/raw/linkedin_jobs_india.csv")
    parser.add_argument("--out", default="../data/raw/jobs.csv")
    args = parser.parse_args()

    df, is_sample = load_source(args.inp)
    cleaned = clean(df, is_sample)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    cleaned.to_csv(args.out, index=False)

    print(f"\nWrote {len(cleaned)} cleaned job rows -> {args.out}")
    print(f"is_sample_data = {is_sample} (downstream UI must show a 'sample data' badge when True)")
    print("\nNext: run extract_skills.py, analyze_demand.py, detect_trends.py as usual — "
          "they read the `description` field the same way regardless of source.")


if __name__ == "__main__":
    main()
