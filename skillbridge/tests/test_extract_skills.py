"""
test_extract_skills.py
------------------------
Run:
    cd scripts && python -m pytest ../tests/test_extract_skills.py -v

(Requires scripts/ on the path — see conftest.py)
"""
import json

from extract_skills import extract_from_text, load_skill_dictionary, normalize_token


def test_normalize_alias_powerbi():
    canonical, lookup = load_skill_dictionary("../data/raw/skills.csv")
    assert normalize_token("PowerBI", lookup, canonical) == "Power BI"


def test_normalize_alias_ms_excel():
    canonical, lookup = load_skill_dictionary("../data/raw/skills.csv")
    assert normalize_token("MS Excel", lookup, canonical) == "Excel"


def test_normalize_unknown_returns_none():
    canonical, lookup = load_skill_dictionary("../data/raw/skills.csv")
    assert normalize_token("Underwater Basket Weaving", lookup, canonical) is None


def test_extract_from_text_finds_multiple_skills():
    canonical, lookup = load_skill_dictionary("../data/raw/skills.csv")
    text = "We need a Data Analyst with Python, SQL, Power BI and Excel experience."
    found = extract_from_text(text, canonical, lookup)
    assert "Python" in found
    assert "SQL" in found
    assert "Power BI" in found
    assert "Excel" in found


def test_extract_from_text_no_partial_word_match():
    """'R' as a skill (if present) should not match inside 'Analyst' etc."""
    canonical, lookup = load_skill_dictionary("../data/raw/skills.csv")
    text = "Looking for a Data Analyst."
    found = extract_from_text(text, canonical, lookup)
    # 'Data Cleaning' etc should NOT spuriously appear just because 'Data' is a substring
    assert "Data Cleaning" not in found
