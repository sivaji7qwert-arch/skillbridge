"""
generate_recommendations.py
----------------------------
Turns a skill-gap table into explainable curriculum recommendations.

Every recommendation includes: action, priority, confidence, and a
human-readable evidence list — deliberately rule-based (not a black-box
model) so it satisfies the "explainable AI" requirement for SIH judging
(spec sections 27-28). Confidence is a simple function of how much
signal (posting volume) backs the number, not a mysterious ML score.

Usage:
    python scripts/generate_recommendations.py \
        --gaps ../data/processed/skill_gaps.csv \
        --demand ../data/processed/skill_demand.csv \
        --role "Data Analyst" \
        --out ../data/processed/recommendations.json
"""

import argparse
import json

import pandas as pd


def confidence_from_volume(job_count, max_count):
    if max_count == 0:
        return 50
    return int(min(95, 40 + (job_count / max_count) * 55))


def build_recommendation(row, demand_row):
    skill = row["skill"]
    gap = row["gap_score"]
    industry_pct = row["industry_demand_pct"]
    trend = demand_row.get("trend", "Stable") if demand_row is not None else "Stable"
    growth_pct = demand_row.get("growth_pct", 0) if demand_row is not None else 0
    job_count = demand_row.get("job_count", 0) if demand_row is not None else 0

    if row["status"] == "Critical Gap":
        action = "ADD"
        priority = "HIGH"
    elif row["status"] == "Low Priority Gap":
        action = "ADD" if trend in ("Emerging", "Growing") else "MONITOR"
        priority = "MEDIUM"
    else:
        # covered - check if declining -> REDUCE, else RETAIN, or MODIFY if
        # curriculum coverage is nominal but industry demand is very high
        if trend == "Declining" and industry_pct < 5:
            action = "REDUCE"
            priority = "LOW"
        elif industry_pct > 25 and gap > -10:
            action = "MODIFY"  # covered but should go deeper given how central it is
            priority = "MEDIUM"
        else:
            action = "RETAIN"
            priority = "LOW"

    evidence = [
        f"Required by {industry_pct}% of {row.get('role', 'target role')} postings analyzed",
        f"Demand trend classified as '{trend}' ({growth_pct:+.1f}% growth vs prior period)" if demand_row is not None else "Demand trend data unavailable for this skill",
        f"Current curriculum coverage score: {row['curriculum_coverage_score']}/100",
        f"Skill gap score: {gap}",
    ]

    return {
        "skill": skill,
        "action": action,
        "priority": priority,
        "confidence": confidence_from_volume(job_count, 1),  # normalized below
        "raw_job_count": int(job_count),
        "evidence": evidence,
        "industry_demand_pct": industry_pct,
        "curriculum_coverage_score": row["curriculum_coverage_score"],
        "gap_score": gap,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gaps", default="../data/processed/skill_gaps.csv")
    parser.add_argument("--demand", default="../data/processed/skill_demand.csv")
    parser.add_argument("--role", required=True)
    parser.add_argument("--out", default="../data/processed/recommendations.json")
    args = parser.parse_args()

    gaps = pd.read_csv(args.gaps)
    demand = pd.read_csv(args.demand).set_index("skill")

    max_job_count = demand["job_count"].max() if not demand.empty else 1

    recommendations = []
    for _, row in gaps.iterrows():
        row_dict = row.to_dict()
        row_dict["role"] = args.role
        demand_row = demand.loc[row["skill"]].to_dict() if row["skill"] in demand.index else None
        rec = build_recommendation(row_dict, demand_row)
        # recompute confidence properly against max volume in this dataset
        job_count = demand_row.get("job_count", 0) if demand_row else 0
        rec["confidence"] = confidence_from_volume(job_count, max_job_count)
        recommendations.append(rec)

    # sort: HIGH priority ADD first, then MEDIUM, then others
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    recommendations.sort(key=lambda r: priority_order.get(r["priority"], 3))

    # alignment before/after estimate
    total_score = gaps["industry_demand_score"].sum()
    covered_before = gaps[gaps["status"] == "Covered"]["industry_demand_score"].sum()
    # "after" assumes all ADD/MODIFY recommendations get implemented
    would_cover = gaps[gaps["status"] != "Covered"]["industry_demand_score"].sum()
    alignment_before = round(covered_before / total_score * 100, 1) if total_score else 0
    alignment_after_est = round(min(100.0, (covered_before + would_cover * 0.9) / total_score * 100), 1) if total_score else 0

    output = {
        "role": args.role,
        "alignment_before_pct": alignment_before,
        "alignment_after_estimate_pct": alignment_after_est,
        "note": "Alignment-after is a model-generated estimate assuming recommended additions are fully implemented. Not a guaranteed real-world outcome.",
        "recommendations": recommendations,
    }

    with open(args.out, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Role: {args.role}")
    print(f"Alignment: {alignment_before}% -> estimated {alignment_after_est}% after recommendations")
    print(f"\nWrote {len(recommendations)} recommendations -> {args.out}\n")
    for r in recommendations:
        print(f"[{r['priority']:6s}] {r['action']:8s} {r['skill']:20s} confidence={r['confidence']}%")


if __name__ == "__main__":
    main()
