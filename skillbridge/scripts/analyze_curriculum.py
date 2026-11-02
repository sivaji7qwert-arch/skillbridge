"""
analyze_curriculum.py
-----------------------
End-to-end convenience CLI: runs skill-gap calculation + recommendation
generation for a given role/curriculum in one command (chains
calculate_skill_gaps.py + generate_recommendations.py).

Usage:
    python scripts/analyze_curriculum.py --role "Data Analyst" --curriculum-id CUR001
"""
import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", required=True)
    parser.add_argument("--curriculum-id", required=True)
    parser.add_argument("--demand", default="../data/processed/skill_demand.csv")
    parser.add_argument("--roles", default="../data/raw/roles.csv")
    parser.add_argument("--curricula", default="../data/raw/curricula.csv")
    args = parser.parse_args()

    gaps_out = "../data/processed/skill_gaps.csv"
    rec_out = "../data/processed/recommendations.json"

    print("Step 1/2: Calculating skill gaps...")
    subprocess.run([
        sys.executable, "calculate_skill_gaps.py",
        "--demand", args.demand, "--roles", args.roles, "--curricula", args.curricula,
        "--role", args.role, "--curriculum-id", args.curriculum_id, "--out", gaps_out,
    ], check=True)

    print("\nStep 2/2: Generating recommendations...")
    subprocess.run([
        sys.executable, "generate_recommendations.py",
        "--gaps", gaps_out, "--demand", args.demand, "--role", args.role, "--out", rec_out,
    ], check=True)

    print(f"\nDone. See {gaps_out} and {rec_out}")


if __name__ == "__main__":
    main()
