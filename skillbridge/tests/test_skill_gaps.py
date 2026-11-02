"""
test_skill_gaps.py
--------------------
Unit tests for the gap-scoring logic in calculate_skill_gaps.py using a
small synthetic demand table (no dependency on the generated dataset).
"""
import pandas as pd

from calculate_skill_gaps import compute_gaps


def make_demand_df():
    return pd.DataFrame([
        {"skill": "Python", "skill_demand_score": 90.0, "demand_percentage": 30.0},
        {"skill": "AWS", "skill_demand_score": 70.0, "demand_percentage": 12.0},
        {"skill": "Excel", "skill_demand_score": 40.0, "demand_percentage": 20.0},
    ])


def test_covered_skill_has_low_gap():
    demand_df = make_demand_df()
    role_skills = ["Python", "Excel"]
    curriculum_skills = {"Python", "Excel"}
    gaps = compute_gaps(role_skills, curriculum_skills, demand_df)
    python_row = gaps[gaps["skill"] == "Python"].iloc[0]
    assert python_row["status"] == "Covered"
    assert python_row["curriculum_coverage_score"] == 90.0


def test_missing_high_demand_skill_is_critical_gap():
    demand_df = make_demand_df()
    role_skills = ["Python", "AWS"]
    curriculum_skills = {"Python"}  # AWS missing entirely
    gaps = compute_gaps(role_skills, curriculum_skills, demand_df)
    aws_row = gaps[gaps["skill"] == "AWS"].iloc[0]
    assert aws_row["curriculum_coverage_score"] == 0.0
    assert aws_row["status"] == "Critical Gap"
    assert aws_row["gap_score"] > 35


def test_unknown_skill_gets_neutral_default_score():
    demand_df = make_demand_df()
    role_skills = ["SomeNewSkillNotInDemandTable"]
    curriculum_skills = set()
    gaps = compute_gaps(role_skills, curriculum_skills, demand_df)
    row = gaps.iloc[0]
    assert row["industry_demand_score"] == 50.0  # neutral default
