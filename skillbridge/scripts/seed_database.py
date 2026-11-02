"""
seed_database.py
------------------
Loads pipeline outputs (data/raw + data/processed) into MongoDB
collections, matching the schema in backend/app/database.py.

This is optional for local demos (the FastAPI backend reads directly
from the processed CSV/JSON files via app/services/data_service.py),
but is what you'd run to back the app with real persistence.

Usage:
    python scripts/seed_database.py --mongo-uri mongodb://localhost:27017 --db skillbridge
"""
import argparse
import json

import pandas as pd
from pymongo import MongoClient


def seed(mongo_uri, db_name):
    client = MongoClient(mongo_uri)
    db = client[db_name]

    print("Seeding companies...")
    db.companies.delete_many({})
    db.companies.insert_many(pd.read_csv("../data/raw/companies.csv").to_dict(orient="records"))

    print("Seeding skills...")
    db.skills.delete_many({})
    db.skills.insert_many(pd.read_csv("../data/raw/skills.csv").to_dict(orient="records"))

    print("Seeding roles...")
    db.roles.delete_many({})
    db.roles.insert_many(pd.read_csv("../data/raw/roles.csv").to_dict(orient="records"))

    print("Seeding jobs (with extracted skills)...")
    jobs_df = pd.read_csv("../data/processed/jobs_with_skills.csv")
    jobs_df["extracted_skills"] = jobs_df["extracted_skills"].apply(json.loads)
    db.jobs.delete_many({})
    db.jobs.insert_many(jobs_df.to_dict(orient="records"))

    print("Seeding curricula...")
    curricula_df = pd.read_csv("../data/raw/curricula.csv")
    curricula_df["modules"] = curricula_df["modules_json"].apply(json.loads)
    curricula_df = curricula_df.drop(columns=["modules_json"])
    db.curricula.delete_many({})
    db.curricula.insert_many(curricula_df.to_dict(orient="records"))

    print("Seeding courses...")
    db.courses.delete_many({})
    db.courses.insert_many(pd.read_csv("../data/raw/courses.csv").to_dict(orient="records"))

    print("Seeding students...")
    db.students.delete_many({})
    db.students.insert_many(pd.read_csv("../data/raw/students.csv").to_dict(orient="records"))

    print("Seeding employers...")
    db.employers.delete_many({})
    db.employers.insert_many(pd.read_csv("../data/raw/employers.csv").to_dict(orient="records"))

    print("Seeding skill demand analytics...")
    db.analytics.delete_many({"type": "skill_demand"})
    demand_df = pd.read_csv("../data/processed/skill_demand.csv")
    db.analytics.insert_one({"type": "skill_demand", "computed_at": pd.Timestamp.now().isoformat(),
                               "data": demand_df.to_dict(orient="records")})

    print("Done seeding database:", db_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mongo-uri", default="mongodb://localhost:27017")
    parser.add_argument("--db", default="skillbridge")
    args = parser.parse_args()
    seed(args.mongo_uri, args.db)


if __name__ == "__main__":
    main()
