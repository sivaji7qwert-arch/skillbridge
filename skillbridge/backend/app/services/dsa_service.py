"""
dsa_service.py
-----------------
Generates a DSA (Data Structures & Algorithms) preparation roadmap for
a student targeting a software role, tracks their solved-problem
progress, and maintains a daily streak.

IMPORTANT — content sourcing:
This module references well-known, publicly-documented problem TITLES
(e.g. "Two Sum", "Merge Intervals") that are standard interview prep
vocabulary — it does not scrape, copy, or reproduce any platform's
problem statements, test cases, or editorial content. For solving,
students are linked out to a SEARCH URL on LeetCode/HackerRank/CodeChef
(e.g. leetcode.com/problems/<slug>) rather than embedding content, per
each platform's terms of use.
"""
from datetime import date, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.models.db_models import DSAProgress, Streak

LOCAL_DSA_PROGRESS = {}

# Topic -> ordered curriculum (progressive difficulty), each with a small
# curated set of canonical/well-known problem titles. Slugs are simple
# lowercase-hyphenated guesses at the platform's actual URL slug — these
# are link-outs, not scraped content, and may occasionally not resolve
# if a platform's slug differs; the student is taken to the platform's
# site either way to search from there.
DSA_ROADMAP = {
    "Software Engineer": [
        {"topic": "Arrays", "problems": [
            ("Two Sum", "Easy"), ("Best Time to Buy and Sell Stock", "Easy"),
            ("Product of Array Except Self", "Medium"), ("Maximum Subarray", "Medium"),
        ]},
        {"topic": "Strings", "problems": [
            ("Valid Anagram", "Easy"), ("Longest Substring Without Repeating Characters", "Medium"),
            ("Group Anagrams", "Medium"),
        ]},
        {"topic": "Linked Lists", "problems": [
            ("Reverse Linked List", "Easy"), ("Merge Two Sorted Lists", "Easy"),
            ("Linked List Cycle", "Easy"), ("Merge K Sorted Lists", "Hard"),
        ]},
        {"topic": "Trees", "problems": [
            ("Maximum Depth of Binary Tree", "Easy"), ("Validate Binary Search Tree", "Medium"),
            ("Binary Tree Level Order Traversal", "Medium"), ("Lowest Common Ancestor of a Binary Tree", "Medium"),
        ]},
        {"topic": "Graphs", "problems": [
            ("Number of Islands", "Medium"), ("Course Schedule", "Medium"),
            ("Clone Graph", "Medium"), ("Word Ladder", "Hard"),
        ]},
        {"topic": "Dynamic Programming", "problems": [
            ("Climbing Stairs", "Easy"), ("Coin Change", "Medium"),
            ("Longest Common Subsequence", "Medium"), ("Edit Distance", "Hard"),
        ]},
        {"topic": "Sliding Window", "problems": [
            ("Minimum Window Substring", "Hard"), ("Sliding Window Maximum", "Hard"),
        ]},
    ],
}

PLATFORM_SEARCH_URLS = {
    "LeetCode": "https://leetcode.com/problems/{slug}/",
    "HackerRank": "https://www.hackerrank.com/domains/algorithms",
    "CodeChef": "https://www.codechef.com/practice",
}


def slugify(title: str) -> str:
    return title.lower().replace(" ", "-").replace(",", "")


def get_roadmap(target_role: str = "Software Engineer") -> List[dict]:
    roadmap = DSA_ROADMAP.get(target_role, DSA_ROADMAP["Software Engineer"])
    out = []
    for section in roadmap:
        problems = []
        for title, difficulty in section["problems"]:
            problems.append({
                "title": title,
                "difficulty": difficulty,
                "leetcode_url": PLATFORM_SEARCH_URLS["LeetCode"].format(slug=slugify(title)),
                "hackerrank_url": PLATFORM_SEARCH_URLS["HackerRank"],
                "codechef_url": PLATFORM_SEARCH_URLS["CodeChef"],
            })
        out.append({"topic": section["topic"], "problems": problems})
    return out


def mark_problem_solved(db: Session, student_id: str, topic: str, title: str, difficulty: str, platform: str = "LeetCode"):
    if str(student_id).startswith(("demo-", "local-")):
        entries = LOCAL_DSA_PROGRESS.setdefault(student_id, [])
        entry = next((item for item in entries if item["title"] == title), None)
        if entry is None:
            entry = {"topic": topic, "title": title, "difficulty": difficulty, "platform": platform, "solved": True}
            entries.append(entry)
        else:
            entry["solved"] = True
        return entry

    entry = db.query(DSAProgress).filter_by(student_id=student_id, problem_title=title).first()
    if entry is None:
        entry = DSAProgress(
            student_id=student_id, topic=topic, problem_title=title,
            difficulty=difficulty, platform=platform,
        )
        db.add(entry)

    entry.solved = True
    entry.solved_at = date.today()
    _update_streak(db, student_id)
    db.commit()
    return entry


def _update_streak(db: Session, student_id: str):
    streak = db.query(Streak).filter_by(student_id=student_id).first()
    today = date.today()

    if streak is None:
        streak = Streak(student_id=student_id, current_streak=1, longest_streak=1, last_active_date=today)
        db.add(streak)
        return streak

    if streak.last_active_date == today:
        return streak  # already counted today

    if streak.last_active_date == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1  # streak broken, restart

    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.last_active_date = today
    return streak


def get_progress_summary(db: Session, student_id: str) -> dict:
    if str(student_id).startswith(("demo-", "local-")):
        entries = LOCAL_DSA_PROGRESS.get(student_id, [])
        solved = [entry for entry in entries if entry["solved"]]
        by_topic = {}
        by_difficulty = {"Easy": 0, "Medium": 0, "Hard": 0}
        for entry in solved:
            by_topic[entry["topic"]] = by_topic.get(entry["topic"], 0) + 1
            if entry["difficulty"] in by_difficulty:
                by_difficulty[entry["difficulty"]] += 1
        return {
            "total_solved": len(solved), "by_topic": by_topic,
            "by_difficulty": by_difficulty, "current_streak": 0, "longest_streak": 0,
        }

    entries = db.query(DSAProgress).filter_by(student_id=student_id).all()
    streak = db.query(Streak).filter_by(student_id=student_id).first()

    solved = [e for e in entries if e.solved]
    by_topic = {}
    for e in solved:
        by_topic[e.topic] = by_topic.get(e.topic, 0) + 1

    by_difficulty = {"Easy": 0, "Medium": 0, "Hard": 0}
    for e in solved:
        if e.difficulty in by_difficulty:
            by_difficulty[e.difficulty] += 1

    return {
        "total_solved": len(solved),
        "by_topic": by_topic,
        "by_difficulty": by_difficulty,
        "current_streak": streak.current_streak if streak else 0,
        "longest_streak": streak.longest_streak if streak else 0,
    }


def recommend_next_problems(db: Session, student_id: str, target_role: str = "Software Engineer", limit: int = 3) -> List[dict]:
    """Recommends the next unsolved problems, prioritizing topics with
    the fewest solved problems so far (i.e. the student's weakest area),
    then easiest-first within that topic."""
    roadmap = get_roadmap(target_role)
    if str(student_id).startswith(("demo-", "local-")):
        solved_entries = [entry for entry in LOCAL_DSA_PROGRESS.get(student_id, []) if entry["solved"]]
        solved_titles = {entry["title"] for entry in solved_entries}
        solved_by_topic = {}
        for entry in solved_entries:
            solved_by_topic[entry["topic"]] = solved_by_topic.get(entry["topic"], 0) + 1
        topics_sorted = sorted(roadmap, key=lambda sec: solved_by_topic.get(sec["topic"], 0))
        difficulty_rank = {"Easy": 0, "Medium": 1, "Hard": 2}
        recommendations = []
        for section in topics_sorted:
            unsolved = [p for p in section["problems"] if p["title"] not in solved_titles]
            unsolved.sort(key=lambda p: difficulty_rank.get(p["difficulty"], 1))
            for problem in unsolved:
                recommendations.append({**problem, "topic": section["topic"]})
                if len(recommendations) >= limit:
                    return recommendations
        return recommendations

    solved_titles = {
        e.problem_title for e in db.query(DSAProgress).filter_by(student_id=student_id, solved=True).all()
    }
    solved_by_topic = {}
    for e in db.query(DSAProgress).filter_by(student_id=student_id, solved=True).all():
        solved_by_topic[e.topic] = solved_by_topic.get(e.topic, 0) + 1

    # sort topics by least progress first (weakest area gets prioritized)
    topics_sorted = sorted(roadmap, key=lambda sec: solved_by_topic.get(sec["topic"], 0))

    difficulty_rank = {"Easy": 0, "Medium": 1, "Hard": 2}
    recommendations = []
    for section in topics_sorted:
        unsolved = [p for p in section["problems"] if p["title"] not in solved_titles]
        unsolved.sort(key=lambda p: difficulty_rank.get(p["difficulty"], 1))
        for p in unsolved:
            recommendations.append({**p, "topic": section["topic"]})
            if len(recommendations) >= limit:
                return recommendations
    return recommendations
