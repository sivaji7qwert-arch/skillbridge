"""
matching_engine.py
--------------------
TF-IDF + cosine similarity engine used to score how well a resume/skill
set matches a job description, a course, or a target role's requirements.

This is deliberately a classical, explainable ML technique (not a deep
model) so every match score can be decomposed: which terms drove the
similarity, what's the overlap vs. gap. That matters for the "explainable
match score" requirement on the Employer portal.

Two matching modes are provided:
  1. text_similarity() — raw TF-IDF cosine similarity between two free-text
     blobs (e.g. resume text vs. job description text). Captures phrasing/
     context, not just exact skill-name overlap.
  2. skill_set_match() — structured comparison between two skill lists
     (e.g. student's known_skills vs. job's required_skills). Simpler,
     more interpretable, and doesn't require a corpus to fit against.

In practice, we blend both (see compute_match()) so a candidate who
lists "ML" instead of "Machine Learning" verbatim still scores well via
skill-set matching, while still recognizing thematic
similarity for the free-text description.
"""
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def text_similarity(text_a: str, text_b: str) -> float:
    """Returns a 0-1 cosine similarity score between two text blobs."""
    if not text_a or not text_b:
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf = vectorizer.fit_transform([text_a, text_b])
    except ValueError:
        # happens if both texts are empty after stopword removal
        return 0.0
    sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(float(sim), 4)


def skill_set_match(candidate_skills: List[str], required_skills: List[str]) -> dict:
    """Structured overlap between two skill lists. Case-insensitive."""
    cand = {s.strip().lower() for s in candidate_skills if s.strip()}
    req = {s.strip().lower() for s in required_skills if s.strip()}

    if not req:
        return {"match_pct": 0.0, "matched_skills": [], "missing_skills": [], "extra_skills": sorted(cand)}

    matched = cand & req
    missing = req - cand
    extra = cand - req

    match_pct = round(len(matched) / len(req) * 100, 1)

    return {
        "match_pct": match_pct,
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "extra_skills": sorted(extra),
    }


def compute_match(candidate_skills: List[str], candidate_text: str,
                   required_skills: List[str], job_text: str,
                   skill_weight: float = 0.7) -> dict:
    """
    Blended match score for candidate-vs-job (or candidate-vs-course).

    skill_weight controls how much the structured skill-set overlap
    counts vs. free-text thematic similarity. Default weights skill
    overlap higher since it's the more interpretable, defensible
    signal for an "explainable match score" — text similarity is a
    secondary signal that catches related terms the skill dictionary
    might have missed.
    """
    skill_result = skill_set_match(candidate_skills, required_skills)
    text_sim = text_similarity(candidate_text, job_text)

    blended_score = round(
        skill_weight * skill_result["match_pct"] + (1 - skill_weight) * (text_sim * 100), 1
    )

    evidence = [
        f"{len(skill_result['matched_skills'])} of {len(required_skills)} required skills matched directly",
        f"Structured skill overlap: {skill_result['match_pct']}%",
        f"Free-text thematic similarity: {round(text_sim * 100, 1)}%",
    ]
    if skill_result["missing_skills"]:
        evidence.append(f"Missing: {', '.join(skill_result['missing_skills'][:6])}"
                         + (" …" if len(skill_result["missing_skills"]) > 6 else ""))

    return {
        "overall_match_score": blended_score,
        "skill_match_pct": skill_result["match_pct"],
        "text_similarity_pct": round(text_sim * 100, 1),
        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
        "extra_skills": skill_result["extra_skills"],
        "evidence": evidence,
    }
