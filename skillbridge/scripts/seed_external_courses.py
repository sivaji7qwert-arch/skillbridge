"""
seed_external_courses.py
---------------------------
Seeds the external_courses table with a curated set of real, publicly
listed courses from Coursera, Infosys Springboard, Oracle University,
and IBM SkillsBuild, tagged with the skills they teach — used to power
course recommendations when a student has a skill gap.

These are real course titles/providers (not fabricated), but URLs
should be re-verified periodically since course catalogs change.

Usage:
    python scripts/seed_external_courses.py --database-url postgresql://postgres:postgres@localhost:5432/skillbridge
"""
import argparse
import sys
from pathlib import Path

BACKEND_DIR = str(Path(__file__).resolve().parents[1] / "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.db_models import Base, ExternalCourse

COURSES = [
    {"provider": "Coursera", "title": "Google Data Analytics Professional Certificate",
     "skills_taught": ["Excel", "SQL", "Tableau", "Statistics", "Data Cleaning"],
     "url": "https://www.coursera.org/professional-certificates/google-data-analytics"},
    {"provider": "Coursera", "title": "IBM Data Science Professional Certificate",
     "skills_taught": ["Python", "SQL", "Machine Learning", "Statistics"],
     "url": "https://www.coursera.org/professional-certificates/ibm-data-science"},
    {"provider": "Coursera", "title": "AWS Fundamentals Specialization",
     "skills_taught": ["AWS", "Cloud", "Linux"],
     "url": "https://www.coursera.org/specializations/aws-fundamentals"},
    {"provider": "Coursera", "title": "Deep Learning Specialization (deeplearning.ai)",
     "skills_taught": ["Deep Learning", "TensorFlow", "Machine Learning", "Python"],
     "url": "https://www.coursera.org/specializations/deep-learning"},
    {"provider": "Infosys Springboard", "title": "Python for Data Science",
     "skills_taught": ["Python", "Data Cleaning", "Statistics"],
     "url": "https://infyspringboard.onwingspan.com/"},
    {"provider": "Infosys Springboard", "title": "Full Stack Web Development",
     "skills_taught": ["JavaScript", "React", "Node.js", "HTML/CSS"],
     "url": "https://infyspringboard.onwingspan.com/"},
    {"provider": "Infosys Springboard", "title": "Cloud Computing Fundamentals",
     "skills_taught": ["AWS", "Azure", "Docker"],
     "url": "https://infyspringboard.onwingspan.com/"},
    {"provider": "Oracle University", "title": "Oracle Cloud Infrastructure Foundations",
     "skills_taught": ["Cloud", "Linux", "Networking"],
     "url": "https://education.oracle.com/oracle-cloud-infrastructure-foundations"},
    {"provider": "Oracle University", "title": "Oracle Database SQL Certified Associate",
     "skills_taught": ["SQL", "PostgreSQL", "Database"],
     "url": "https://education.oracle.com/database-sql"},
    {"provider": "IBM SkillsBuild", "title": "Introduction to Cybersecurity Tools & Cyberattacks",
     "skills_taught": ["Cybersecurity", "Network Security"],
     "url": "https://skillsbuild.org/"},
    {"provider": "IBM SkillsBuild", "title": "Machine Learning with Python",
     "skills_taught": ["Python", "Machine Learning", "Scikit-learn"],
     "url": "https://skillsbuild.org/"},
    {"provider": "IBM SkillsBuild", "title": "DevOps and Software Engineering",
     "skills_taught": ["Docker", "Kubernetes", "CI/CD", "Git"],
     "url": "https://skillsbuild.org/"},
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default="postgresql://postgres:postgres@localhost:5432/skillbridge")
    args = parser.parse_args()

    engine = create_engine(args.database_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    existing_titles = {c.title for c in db.query(ExternalCourse).all()}
    added = 0
    for course in COURSES:
        if course["title"] in existing_titles:
            continue
        db.add(ExternalCourse(**course))
        added += 1

    db.commit()
    print(f"Seeded {added} new courses ({len(COURSES) - added} already present).")


if __name__ == "__main__":
    main()
