"""
extract_skills.py
------------------
Extracts and normalizes skills from free-text job descriptions using:
  1. A canonical skill dictionary (data/raw/skills.csv)
  2. An alias/normalization map (common variant spellings -> canonical name)
  3. Simple fuzzy matching (difflib) as a fallback for near-miss spellings

This intentionally avoids heavy transformer dependencies so it runs on
constrained hardware (8GB RAM). A sentence-transformers based fuzzy step
can be swapped in later (see `normalize_skills.py` docstring) without
changing the calling API.

Usage:
    python scripts/extract_skills.py --jobs ../data/raw/jobs.csv \
                                      --skills ../data/raw/skills.csv \
                                      --out ../data/processed/jobs_with_skills.csv
"""

import argparse
import difflib
import json
import re
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]


def resolve_repo_path(path):
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate

    # Prefer the current working directory when it already resolves.
    resolved = (Path.cwd() / candidate).resolve()
    if resolved.exists():
        return resolved

    # Common project convention: scripts/ and tests/ pass paths like ../data/raw/... .
    # When run from the repo root, those paths should still resolve inside the repo.
    if candidate.parts and candidate.parts[0] == "..":
        cleaned = Path(*candidate.parts[1:])
        return (REPO_ROOT / cleaned).resolve()

    # Fall back to repo root for all other relative inputs.
    return (REPO_ROOT / candidate).resolve()


# Common variant -> canonical skill name normalization
ALIASES = {
    "powerbi": "Power BI",
    "power-bi": "Power BI",
    "ms excel": "Excel",
    "microsoft excel": "Excel",
    "ml": "Machine Learning",
    "machine-learning": "Machine Learning",
    "amazon web services": "AWS",
    "aws cloud": "AWS",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "microsoft azure": "Azure",
    "js": "JavaScript",
    "reactjs": "React",
    "react.js": "React",
    "nodejs": "Node.js",
    "node": "Node.js",
    "postgres": "PostgreSQL",
    "mongo": "MongoDB",
    "k8s": "Kubernetes",
    "genai": "Generative AI",
    "gen ai": "Generative AI",
    "nlp processing": "NLP",
    "ui ux": "UI/UX Design",
    "ui/ux": "UI/UX Design",
    "html": "HTML/CSS",
    "css": "HTML/CSS",
}


def load_skill_dictionary(skills_csv):
    df = pd.read_csv(resolve_repo_path(skills_csv))
    canonical = df["name"].tolist()
    # build a lookup of lowercase -> canonical
    lookup = {s.lower(): s for s in canonical}
    lookup.update(ALIASES)
    return canonical, lookup


def normalize_token(token, lookup, canonical_list, cutoff=0.86):
    t = token.strip().lower()
    if not t:
        return None
    if t in lookup:
        return lookup[t]
    # fuzzy fallback against canonical list
    match = difflib.get_close_matches(token.strip(), canonical_list, n=1, cutoff=cutoff)
    if match:
        return match[0]
    return None


def extract_from_text(text, canonical_list, lookup):
    """
    Keyword-matching extraction: scans description text for any canonical
    skill name or known alias, using word-boundary regex so 'R' doesn't
    match inside 'Analytics', etc.
    """
    found = set()
    text_lower = text.lower()
    for skill in canonical_list:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.add(skill)
    for alias, canonical in ALIASES.items():
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(alias) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.add(canonical)
    return sorted(found)


def process_jobs(jobs_csv, skills_csv, out_csv):
    canonical_list, lookup = load_skill_dictionary(skills_csv)
    jobs = pd.read_csv(resolve_repo_path(jobs_csv))

    extracted_col = []
    for _, row in jobs.iterrows():
        # Prefer the structured `skills` column if present (comma-separated),
        # normalize each token; also mine the free-text description for
        # anything the structured list missed.
        skills_from_field = []
        if isinstance(row.get("skills"), str):
            for tok in row["skills"].split(","):
                norm = normalize_token(tok, lookup, canonical_list)
                if norm:
                    skills_from_field.append(norm)

        skills_from_text = []
        if isinstance(row.get("description"), str):
            skills_from_text = extract_from_text(row["description"], canonical_list, lookup)

        merged = sorted(set(skills_from_field) | set(skills_from_text))
        extracted_col.append(json.dumps(merged))

    jobs["extracted_skills"] = extracted_col
    output_path = resolve_repo_path(out_csv)
    jobs.to_csv(output_path, index=False)
    print(f"Wrote {len(jobs)} rows with extracted_skills -> {output_path}")

    # quick sanity sample
    sample = jobs.iloc[0]
    print("\nExample extraction:")
    print(json.dumps({
        "job_title": sample["job_title"],
        "role": sample.get("normalized_role"),
        "skills": json.loads(sample["extracted_skills"]),
    }, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", default=str(REPO_ROOT / "data" / "raw" / "jobs.csv"))
    parser.add_argument("--skills", default=str(REPO_ROOT / "data" / "raw" / "skills.csv"))
    parser.add_argument("--out", default=str(REPO_ROOT / "data" / "processed" / "jobs_with_skills.csv"))
    args = parser.parse_args()

    import os
    output_dir = resolve_repo_path(os.path.dirname(args.out))
    output_dir.mkdir(parents=True, exist_ok=True)
    process_jobs(args.jobs, args.skills, args.out)


if __name__ == "__main__":
    main()
