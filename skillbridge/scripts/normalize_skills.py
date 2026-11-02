"""
normalize_skills.py
--------------------
Standalone normalization utility — exposes the alias/canonical mapping
used by extract_skills.py so other scripts (or the FastAPI backend) can
normalize a raw skill string without re-running full extraction.

Usage as a library:
    from normalize_skills import normalize
    normalize("powerbi")  -> "Power BI"

CLI usage (normalize a comma-separated list):
    python scripts/normalize_skills.py --skills "powerbi, ms excel, reactjs"
"""
import argparse
from extract_skills import load_skill_dictionary, normalize_token


def normalize(token, skills_csv="../data/raw/skills.csv"):
    canonical_list, lookup = load_skill_dictionary(skills_csv)
    return normalize_token(token, lookup, canonical_list)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skills", required=True, help="Comma-separated raw skill tokens")
    parser.add_argument("--dict", default="../data/raw/skills.csv")
    args = parser.parse_args()

    canonical_list, lookup = load_skill_dictionary(args.dict)
    for tok in args.skills.split(","):
        norm = normalize_token(tok, lookup, canonical_list)
        print(f"{tok.strip():25s} -> {norm}")


if __name__ == "__main__":
    main()
