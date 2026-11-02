"""
gap_service.py
---------------
On-demand (request-time) skill-gap + recommendation computation, reusing
the same logic as scripts/calculate_skill_gaps.py and
scripts/generate_recommendations.py so the batch pipeline and the live
API never drift apart. Import the scripts directly rather than
duplicating logic.
"""
import json
import sys
from pathlib import Path

import pandas as pd

from app.services import data_service

SCRIPTS_DIR = str(Path(__file__).resolve().parents[3] / "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from calculate_skill_gaps import compute_gaps, load_role_core_skills, load_curriculum_skills  # noqa: E402
from generate_recommendations import build_recommendation, confidence_from_volume  # noqa: E402


def analyze_curriculum(role: str, curriculum_id: str) -> dict:
    demand_df = data_service.load_skill_demand()
    roles_path = data_service._path("roles.csv", raw=True)
    curricula_path = data_service._path("curricula.csv", raw=True)

    role_skills = load_role_core_skills(roles_path, role)
    curriculum_skills, modules = load_curriculum_skills(curricula_path, curriculum_id)

    gaps_df = compute_gaps(role_skills, curriculum_skills, demand_df)

    demand_indexed = demand_df.set_index("skill")
    max_job_count = demand_indexed["job_count"].max() if not demand_indexed.empty else 1

    recommendations = []
    for _, row in gaps_df.iterrows():
        row_dict = row.to_dict()
        row_dict["role"] = role
        demand_row = demand_indexed.loc[row["skill"]].to_dict() if row["skill"] in demand_indexed.index else None
        rec = build_recommendation(row_dict, demand_row)
        job_count = demand_row.get("job_count", 0) if demand_row else 0
        rec["confidence"] = confidence_from_volume(job_count, max_job_count)
        recommendations.append(rec)

    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    recommendations.sort(key=lambda r: priority_order.get(r["priority"], 3))

    total_score = gaps_df["industry_demand_score"].sum()
    covered_before = gaps_df[gaps_df["status"] == "Covered"]["industry_demand_score"].sum()
    would_cover = gaps_df[gaps_df["status"] != "Covered"]["industry_demand_score"].sum()
    alignment_before = round(covered_before / total_score * 100, 1) if total_score else 0
    alignment_after = round(min(100.0, (covered_before + would_cover * 0.9) / total_score * 100), 1) if total_score else 0

    return {
        "role": role,
        "curriculum_id": curriculum_id,
        "modules": modules,
        "gaps": gaps_df.to_dict(orient="records"),
        "alignment_before_pct": alignment_before,
        "alignment_after_estimate_pct": alignment_after,
        "note": "Alignment-after is a model-generated estimate assuming recommended additions are fully implemented. Not a guaranteed real-world outcome.",
        "recommendations": recommendations,
    }


def student_skill_gap(student_id: str) -> dict:
    students = data_service.load_students()
    row = students[students["student_id"] == student_id]
    if row.empty:
        raise ValueError(f"Student {student_id} not found")
    row = row.iloc[0]
    target_role = row["target_role"]
    known = set(s.strip() for s in row["known_skills"].split(","))

    roles_path = data_service._path("roles.csv", raw=True)
    role_skills = load_role_core_skills(roles_path, target_role)

    demand_df = data_service.load_skill_demand().set_index("skill")

    missing = []
    for skill in role_skills:
        if skill not in known:
            score = demand_df.loc[skill]["skill_demand_score"] if skill in demand_df.index else 50.0
            priority = "HIGH PRIORITY" if score >= 65 else ("MEDIUM PRIORITY" if score >= 40 else "LOW PRIORITY")
            missing.append({"skill": skill, "priority": priority, "demand_score": round(float(score), 1)})

    missing.sort(key=lambda m: -m["demand_score"])

    return {
        "student_id": student_id,
        "name": row["name"],
        "target_role": target_role,
        "known_skills": sorted(known),
        "missing_skills": missing,
    }
