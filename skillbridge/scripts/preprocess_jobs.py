"""
preprocess_jobs.py
-------------------
Basic cleaning pass over raw job postings before skill extraction:
  - drops exact duplicates
  - strips whitespace on text fields
  - drops rows missing critical fields (job_title, normalized_role)
  - parses posting_date to a consistent format
  - clips unrealistic salary values

Usage:
    python scripts/preprocess_jobs.py --in ../data/raw/jobs.csv --out ../data/processed/jobs_clean.csv
"""
import argparse
import os
import pandas as pd


def clean(df):
    before = len(df)
    df = df.drop_duplicates()
    df = df.dropna(subset=["job_title", "normalized_role"])
    for col in ["job_title", "company", "location", "industry", "description"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    df["posting_date"] = pd.to_datetime(df["posting_date"], errors="coerce")
    df = df.dropna(subset=["posting_date"])
    df["posting_date"] = df["posting_date"].dt.strftime("%Y-%m-%d")
    # clip absurd salary outliers (basic sanity bound for a prototype)
    df["salary_min"] = df["salary_min"].clip(lower=100000, upper=10000000)
    df["salary_max"] = df["salary_max"].clip(lower=100000, upper=15000000)
    after = len(df)
    print(f"Cleaned {before} -> {after} rows ({before - after} dropped)")
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="inp", default="../data/raw/jobs.csv")
    parser.add_argument("--out", default="../data/processed/jobs_clean.csv")
    args = parser.parse_args()
    df = pd.read_csv(args.inp)
    df = clean(df)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
