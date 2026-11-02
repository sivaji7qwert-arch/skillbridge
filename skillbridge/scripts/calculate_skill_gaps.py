"""
calculate_skill_gaps.py
------------------------
Compares curriculum skill coverage against industry demand for a given
target role, producing a weighted Skill Gap Score per skill:

    Skill Gap Score = Industry Demand Score - Curriculum Coverage Score

Curriculum coverage is estimated as: does this skill appear in any
module of the curriculum? (100 if yes, 0 if no) — a simple, explainable
proxy suitable for a hackathon prototype. This can be refined later
(e.g. weighting by module depth/assessment rigor) without changing the
downstream recommendation engine's interface.

Usage:
    python scripts/calculate_skill_gaps.py \
        --demand ../data/processed/skill_demand.csv \
        --curricula ../data/raw/curricula.csv \
        --role "Data Analyst" \
        --curriculum-id CUR001 \
        --out ../data/processed/skill_gaps.csv
"""

import argparse
import json
import os

import pandas as pd

ROLE_SKILL_MAP_PATH_HINT = "../data/raw/roles.csv"


def load_role_core_skills(roles_csv, role_name):
    roles = pd.read_csv(roles_csv)
    row = roles[roles["name"] == role_name]
    if row.empty:
        raise ValueError(f"Role '{role_name}' not found in {roles_csv}")
    skills = [s.strip() for s in row.iloc[0]["core_skills"].split(",")]
    return skills


def load_curriculum_skills(curricula_csv, curriculum_id):
    curricula = pd.read_csv(curricula_csv)
    row = curricula[curricula["curriculum_id"] == curriculum_id]
    if row.empty:
        raise ValueError(f"Curriculum '{curriculum_id}' not found in {curricula_csv}")
    modules = json.loads(row.iloc[0]["modules_json"])
    skills = set()
    for m in modules:
        skills.update(m["skills"])
    return skills, modules


def compute_gaps(role_skills, curriculum_skills, demand_df):
    demand_lookup = demand_df.set_index("skill")["skill_demand_score"].to_dict()
    demand_pct_lookup = demand_df.set_index("skill")["demand_percentage"].to_dict()

    rows = []
    for skill in role_skills:
        industry_score = demand_lookup.get(skill, 50.0)  # neutral default if unseen
        industry_pct = demand_pct_lookup.get(skill, 0.0)
        curriculum_score = 90.0 if skill in curriculum_skills else 0.0
        gap = round(industry_score - curriculum_score, 2)
        rows.append({
            "skill": skill,
            "industry_demand_pct": industry_pct,
            "industry_demand_score": industry_score,
            "curriculum_coverage_score": curriculum_score,
            "gap_score": gap,
            "status": "Covered" if gap <= 10 else ("Low Priority Gap" if gap <= 35 else "Critical Gap"),
        })

    df = pd.DataFrame(rows).sort_values("gap_score", ascending=False)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demand", default="../data/processed/skill_demand.csv")
    parser.add_argument("--roles", default="../data/raw/roles.csv")
    parser.add_argument("--curricula", default="../data/raw/curricula.csv")
    parser.add_argument("--role", required=True, help="Target role, e.g. 'Data Analyst'")
    parser.add_argument("--curriculum-id", required=True, help="e.g. CUR001")
    parser.add_argument("--out", default="../data/processed/skill_gaps.csv")
    args = parser.parse_args()

    demand_df = pd.read_csv(args.demand)
    role_skills = load_role_core_skills(args.roles, args.role)
    curriculum_skills, modules = load_curriculum_skills(args.curricula, args.curriculum_id)

    gaps = compute_gaps(role_skills, curriculum_skills, demand_df)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    gaps.to_csv(args.out, index=False)

    covered = gaps[gaps["status"] == "Covered"]["industry_demand_score"].sum()
    total = gaps["industry_demand_score"].sum()
    alignment_pct = round(covered / total * 100, 1) if total else 0.0

    print(f"Role: {args.role} | Curriculum: {args.curriculum_id}")
    print(f"Current alignment: {alignment_pct}%")
    print(f"\nWrote skill gap table ({len(gaps)} skills) -> {args.out}\n")
    print(gaps.to_string(index=False))


if __name__ == "__main__":
    main()
