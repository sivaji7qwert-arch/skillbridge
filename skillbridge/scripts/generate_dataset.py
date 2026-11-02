"""
generate_dataset.py
--------------------
Synthetic dataset generator for SkillBridge (SIH26134).

Generates realistic, CORRELATED (not purely random) data representing
Maharashtra's labour market:
  - jobs.csv        (10,000+ postings)
  - companies.csv    (500+ companies)
  - skills.csv        (100+ skills)
  - roles.csv          (30+ normalized roles)
  - courses.csv         (20+ courses)
  - curricula.csv        (10+ curricula, each with modules -> skills)
  - students.csv           (500+ students)
  - employers.csv            (50+ employers)

Run:
    python scripts/generate_dataset.py --out ../data/raw --seed 42

Design notes:
  - Uses role -> skill_pool mappings so postings are realistic, not
    random noise (see ROLE_SKILL_MAP below).
  - Adds a time dimension (posting_date across ~24 months) so that
    growth-rate / trend-detection has something real to compute on.
  - Adds mild randomness per posting (drop 0-2 skills, add 0-1 "noise"
    skill) so the NLP/extraction step has non-trivial text to parse.
"""

import argparse
import json
import os
import random
from datetime import datetime, timedelta

import pandas as pd

# ---------------------------------------------------------------------------
# Lightweight local "faker" replacement (no external dependency / no network
# needed). Produces plausible Indian names and company names by combining
# word lists, seeded via `random` so --seed still makes runs reproducible.
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
    "Ishaan", "Rohan", "Ananya", "Diya", "Saanvi", "Aadhya", "Myra", "Pari",
    "Anika", "Kavya", "Riya", "Isha", "Rahul", "Priya", "Neha", "Sanjay",
    "Pooja", "Amit", "Sneha", "Vikram", "Kiran", "Meera", "Suresh", "Lakshmi",
    "Rajesh", "Anjali", "Manish", "Deepa", "Nikhil", "Swati", "Karan", "Divya",
]
LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Kulkarni", "Deshmukh", "Joshi",
    "Shah", "Mehta", "Iyer", "Nair", "Reddy", "Rao", "Pawar", "Jadhav",
    "Kale", "Kadam", "Bhosale", "Chavan", "More", "Gaikwad", "Salunkhe",
    "Naik", "Kamble", "Pillai", "Menon", "Agarwal", "Bansal", "Chopra",
]
COMPANY_PREFIXES = [
    "Bharat", "Sahyadri", "Konkan", "Deccan", "Maratha", "Sindhu", "Ratna",
    "Vidarbha", "Sahaj", "Uday", "Prime", "Apex", "NextGen", "Bluewave",
    "Skyline", "Novatech", "Quantum", "Vertex", "Zenith", "Orbit",
]
COMPANY_SUFFIXES = [
    "Technologies", "Industries", "Solutions", "Systems", "Enterprises",
    "Manufacturing", "Analytics", "Innovations", "Automation", "Dynamics",
    "Softworks", "Infra", "Digital", "Labs", "Group",
]


def fake_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def fake_company():
    return f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)}"

CITIES = [
    "Mumbai", "Pune", "Nagpur", "Nashik", "Thane",
    "Aurangabad", "Kolhapur", "Navi Mumbai",
]

SECTORS = [
    "IT", "Manufacturing", "Healthcare", "Banking", "Finance",
    "Automotive", "Electronics", "Construction", "Logistics",
    "Retail", "Agriculture Technology", "Renewable Energy",
]

# Canonical skill list with category, used for skills.csv
SKILLS = {
    "Python": "Programming", "SQL": "Data", "Excel": "Data",
    "Power BI": "Data Visualization", "Tableau": "Data Visualization",
    "AWS": "Cloud", "Azure": "Cloud", "GCP": "Cloud",
    "Docker": "DevOps", "Kubernetes": "DevOps", "Git": "DevOps",
    "CI/CD": "DevOps", "Machine Learning": "AI/ML",
    "Deep Learning": "AI/ML", "TensorFlow": "AI/ML", "PyTorch": "AI/ML",
    "NLP": "AI/ML", "Generative AI": "AI/ML", "Prompt Engineering": "AI/ML",
    "Java": "Programming", "JavaScript": "Programming",
    "React": "Frontend", "Node.js": "Backend", "FastAPI": "Backend",
    "MongoDB": "Database", "PostgreSQL": "Database",
    "Cybersecurity": "Security", "Network Security": "Security",
    "PLC": "Industrial", "CNC": "Industrial", "AutoCAD": "Industrial",
    "SCADA": "Industrial", "Industrial IoT": "Industrial",
    "Solar Panel Installation": "Renewable Energy",
    "EV Battery Systems": "Automotive",
    "Statistics": "Data", "Data Cleaning": "Data",
    "Business Analysis": "Business", "Financial Modeling": "Finance",
    "Risk Management": "Finance", "Digital Marketing": "Marketing",
    "SEO": "Marketing", "Content Writing": "Marketing",
    "Supply Chain Management": "Logistics", "Inventory Management": "Logistics",
    "HTML/CSS": "Frontend", "TypeScript": "Frontend",
    "Linux": "Systems", "Bash Scripting": "Systems",
    "Agile/Scrum": "Process", "Product Management": "Business",
    "UI/UX Design": "Design", "Figma": "Design",
    "Data Structures": "Programming", "Algorithms": "Programming",
    "Spring Boot": "Backend", "Django": "Backend",
    "Salesforce": "Business", "SAP": "Business",
    "Quality Assurance": "Testing", "Automation Testing": "Testing",
    "Robotics": "Industrial", "Renewable Energy Systems": "Renewable Energy",
    "Electric Vehicle Diagnostics": "Automotive",
    "Healthcare Informatics": "Healthcare", "Medical Coding": "Healthcare",
    "GIS": "Agriculture Technology", "Precision Farming": "Agriculture Technology",
    "Communication Skills": "Soft Skills", "Team Leadership": "Soft Skills",
}

ROLE_SKILL_MAP = {
    "Data Analyst": ["Python", "SQL", "Excel", "Power BI", "Statistics", "Tableau", "Data Cleaning"],
    "Data Scientist": ["Python", "SQL", "Machine Learning", "Statistics", "Deep Learning", "TensorFlow", "PyTorch"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Docker", "Git", "AWS"],
    "AI Engineer": ["Python", "Machine Learning", "Deep Learning", "NLP", "Generative AI", "Prompt Engineering", "Docker"],
    "Cloud Engineer": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Linux", "CI/CD"],
    "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD", "Linux", "AWS", "Bash Scripting", "Git"],
    "Full Stack Developer": ["JavaScript", "React", "Node.js", "HTML/CSS", "MongoDB", "Git", "TypeScript"],
    "Backend Developer": ["Java", "Spring Boot", "SQL", "PostgreSQL", "FastAPI", "Git", "Django"],
    "Frontend Developer": ["JavaScript", "React", "HTML/CSS", "TypeScript", "Figma", "UI/UX Design"],
    "Cybersecurity Analyst": ["Cybersecurity", "Network Security", "Linux", "Risk Management", "Python"],
    "Business Analyst": ["Excel", "SQL", "Business Analysis", "Power BI", "Communication Skills", "Statistics"],
    "Financial Analyst": ["Excel", "Financial Modeling", "Risk Management", "SQL", "Statistics"],
    "Digital Marketing Specialist": ["Digital Marketing", "SEO", "Content Writing", "Excel", "Communication Skills"],
    "Supply Chain Analyst": ["Supply Chain Management", "Inventory Management", "Excel", "SQL", "GIS"],
    "QA Engineer": ["Quality Assurance", "Automation Testing", "Python", "Git", "Agile/Scrum"],
    "Product Manager": ["Product Management", "Agile/Scrum", "Communication Skills", "Team Leadership", "SQL"],
    "UI/UX Designer": ["UI/UX Design", "Figma", "Communication Skills", "HTML/CSS"],
    "Electric Vehicle Technician": ["EV Battery Systems", "Electric Vehicle Diagnostics", "PLC", "AutoCAD"],
    "CNC Operator": ["CNC", "AutoCAD", "PLC", "Quality Assurance"],
    "Industrial Automation Technician": ["PLC", "SCADA", "Industrial IoT", "AutoCAD", "Robotics"],
    "Solar Technician": ["Solar Panel Installation", "Renewable Energy Systems", "PLC", "AutoCAD"],
    "Renewable Energy Engineer": ["Renewable Energy Systems", "Solar Panel Installation", "AutoCAD", "GIS"],
    "Healthcare Data Analyst": ["Healthcare Informatics", "SQL", "Excel", "Statistics", "Medical Coding"],
    "Precision Agriculture Specialist": ["GIS", "Precision Farming", "Python", "Statistics"],
    "AI Governance Analyst": ["Generative AI", "Risk Management", "Communication Skills", "Python"],
    "Prompt Engineer": ["Prompt Engineering", "Generative AI", "NLP", "Python", "Communication Skills"],
    "Generative AI Developer": ["Generative AI", "Python", "NLP", "Deep Learning", "Docker", "Git"],
    "Industrial IoT Engineer": ["Industrial IoT", "PLC", "SCADA", "Python", "AWS"],
    "Network Administrator": ["Network Security", "Linux", "Cybersecurity", "Bash Scripting"],
    "SAP Consultant": ["SAP", "Business Analysis", "Excel", "Communication Skills"],
}

ROLES = list(ROLE_SKILL_MAP.keys())
EMPLOYMENT_TYPES = ["Full-time", "Part-time", "Contract", "Internship"]
EDUCATION = ["Diploma", "Bachelor's", "Master's", "ITI Certificate"]

# Emerging roles get an upward growth bias over time (used to bias posting_date)
EMERGING_ROLES = {
    "AI Governance Analyst", "Prompt Engineer", "Generative AI Developer",
    "Electric Vehicle Technician", "Industrial IoT Engineer",
    "Renewable Energy Engineer", "AI Engineer",
}

DECLINING_SKILLS = {"Excel"}  # slowly declining in relative weight over time, kept realistic but modest


def weighted_date(start, end, role):
    """Bias posting dates later in the range for emerging roles."""
    total_days = (end - start).days
    if role in EMERGING_ROLES:
        # skew towards recent (higher random power -> closer to 1 -> later date)
        r = random.random() ** 0.4
    else:
        r = random.random()
    return start + timedelta(days=int(r * total_days))


def generate_companies(n, out_dir):
    rows = []
    for i in range(n):
        rows.append({
            "company_id": f"CMP{i+1:05d}",
            "company_name": fake_company(),
            "sector": random.choice(SECTORS),
            "city": random.choice(CITIES),
            "size": random.choice(["Small (1-50)", "Medium (51-500)", "Large (500+)"]),
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out_dir, "companies.csv"), index=False)
    return df


def generate_skills_csv(out_dir):
    rows = [{"skill_id": f"SK{i+1:04d}", "name": name, "category": cat}
            for i, (name, cat) in enumerate(SKILLS.items())]
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out_dir, "skills.csv"), index=False)
    return df


def generate_roles_csv(out_dir):
    rows = []
    for i, role in enumerate(ROLES):
        rows.append({
            "role_id": f"RL{i+1:03d}",
            "name": role,
            "sector_hint": random.choice(SECTORS),
            "core_skills": ", ".join(ROLE_SKILL_MAP[role]),
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out_dir, "roles.csv"), index=False)
    return df


TITLE_VARIANTS = {
    "Data Analyst": ["Data Analyst", "Data Analytics Specialist", "Business Data Analyst", "Junior Data Analyst"],
    "Full Stack Developer": ["Full Stack Developer", "Full-Stack Engineer", "MERN Stack Developer"],
    "Machine Learning Engineer": ["Machine Learning Engineer", "ML Engineer", "Applied ML Engineer"],
}


def sample_title(role):
    return random.choice(TITLE_VARIANTS.get(role, [role]))


def build_description(role, skills):
    return (
        f"We are looking for a {sample_title(role)} with experience in "
        f"{', '.join(skills)}. The candidate should be comfortable working "
        f"in a fast-paced {random.choice(SECTORS)} environment based in "
        f"{random.choice(CITIES)}, Maharashtra."
    )


def generate_jobs(n, companies_df, out_dir, start, end):
    rows = []
    for i in range(n):
        role = random.choice(ROLES)
        base_skills = ROLE_SKILL_MAP[role][:]
        random.shuffle(base_skills)
        # drop 0-2 skills, add 0-1 noise skill for realism
        keep = max(3, len(base_skills) - random.randint(0, 2))
        job_skills = base_skills[:keep]
        if random.random() < 0.25:
            noise = random.choice(list(SKILLS.keys()))
            if noise not in job_skills:
                job_skills.append(noise)

        company = companies_df.sample(1).iloc[0]
        exp_years = random.choice([0, 1, 2, 3, 5, 7, 10])
        salary_min = random.randint(3, 15) * 100000 + exp_years * 50000
        salary_max = salary_min + random.randint(1, 6) * 100000
        posting_date = weighted_date(start, end, role)

        rows.append({
            "job_id": f"JOB{i+1:06d}",
            "job_title": sample_title(role),
            "normalized_role": role,
            "company": company["company_name"],
            "location": company["city"],
            "industry": company["sector"],
            "experience_required": exp_years,
            "education": random.choice(EDUCATION),
            "salary_min": salary_min,
            "salary_max": salary_max,
            "skills": ", ".join(job_skills),
            "description": build_description(role, job_skills),
            "posting_date": posting_date.strftime("%Y-%m-%d"),
            "employment_type": random.choice(EMPLOYMENT_TYPES),
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out_dir, "jobs.csv"), index=False)
    return df


def generate_courses(out_dir):
    course_defs = [
        ("Advanced Data Analytics", ["Excel", "SQL", "Statistics", "Power BI", "Python", "Machine Learning"]),
        ("Full Stack Web Development", ["HTML/CSS", "JavaScript", "React", "Node.js", "MongoDB", "Git"]),
        ("Cloud & DevOps Fundamentals", ["AWS", "Docker", "Kubernetes", "Linux", "CI/CD"]),
        ("Applied Machine Learning", ["Python", "Machine Learning", "Statistics", "TensorFlow"]),
        ("Cybersecurity Essentials", ["Cybersecurity", "Network Security", "Linux", "Risk Management"]),
        ("Industrial Automation", ["PLC", "SCADA", "AutoCAD", "Industrial IoT"]),
        ("Electric Vehicle Technology", ["EV Battery Systems", "Electric Vehicle Diagnostics", "PLC"]),
        ("Renewable Energy Systems", ["Solar Panel Installation", "Renewable Energy Systems", "AutoCAD"]),
        ("Digital Marketing Bootcamp", ["Digital Marketing", "SEO", "Content Writing"]),
        ("Business Analytics Foundations", ["Excel", "SQL", "Business Analysis", "Power BI"]),
        ("Financial Modeling & Risk", ["Financial Modeling", "Risk Management", "Excel"]),
        ("Generative AI Foundations", ["Python", "NLP", "Generative AI", "Prompt Engineering"]),
        ("Supply Chain Analytics", ["Supply Chain Management", "Inventory Management", "Excel", "SQL"]),
        ("UI/UX Design Essentials", ["UI/UX Design", "Figma", "HTML/CSS"]),
        ("Quality Assurance & Testing", ["Quality Assurance", "Automation Testing", "Git"]),
        ("SAP Fundamentals", ["SAP", "Business Analysis", "Excel"]),
        ("Healthcare Informatics", ["Healthcare Informatics", "SQL", "Medical Coding"]),
        ("Precision Agriculture Tech", ["GIS", "Precision Farming", "Python"]),
        ("Network Administration", ["Network Security", "Linux", "Bash Scripting"]),
        ("Product Management Basics", ["Product Management", "Agile/Scrum", "Communication Skills"]),
    ]
    rows = []
    for i, (title, skills) in enumerate(course_defs):
        rows.append({
            "course_id": f"CRS{i+1:03d}",
            "title": title,
            "skills": ", ".join(skills),
            "difficulty": random.choice(["Beginner", "Intermediate", "Advanced"]),
            "duration_weeks": random.choice([4, 6, 8, 12]),
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out_dir, "courses.csv"), index=False)
    return df, course_defs


def generate_curricula(out_dir, course_defs):
    institute_names = [
        "Pune Institute of Technical Education", "Mumbai Skill Development Centre",
        "Nagpur Vocational Training Institute", "Nashik Polytechnic",
        "Thane Industrial Training Institute", "Aurangabad Skills Academy",
        "Kolhapur College of Applied Sciences", "Navi Mumbai Technical Institute",
        "Maharashtra State Skill University", "Pune Data Science Academy",
    ]
    rows = []
    for i, institute in enumerate(institute_names):
        # each curriculum bundles 3-5 courses (intentionally incomplete vs industry)
        chosen = random.sample(course_defs, k=random.randint(3, 5))
        modules = [{"name": c[0], "skills": c[1]} for c in chosen]
        rows.append({
            "curriculum_id": f"CUR{i+1:03d}",
            "institute_name": institute,
            "city": random.choice(CITIES),
            "modules_json": json.dumps(modules),
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out_dir, "curricula.csv"), index=False)
    return df


def generate_students(n, out_dir):
    rows = []
    for i in range(n):
        role = random.choice(ROLES)
        full_skill_set = ROLE_SKILL_MAP[role]
        # student knows a partial subset (simulating skill gap)
        known = random.sample(full_skill_set, k=max(1, int(len(full_skill_set) * random.uniform(0.3, 0.7))))
        rows.append({
            "student_id": f"STU{i+1:05d}",
            "name": fake_name(),
            "city": random.choice(CITIES),
            "target_role": role,
            "known_skills": ", ".join(known),
            "education": random.choice(EDUCATION),
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out_dir, "students.csv"), index=False)
    return df


def generate_employers(n, companies_df, out_dir):
    rows = []
    sampled = companies_df.sample(n=min(n, len(companies_df)))
    for i, (_, comp) in enumerate(sampled.iterrows()):
        role = random.choice(ROLES)
        rows.append({
            "employer_id": f"EMP{i+1:04d}",
            "company": comp["company_name"],
            "sector": comp["sector"],
            "city": comp["city"],
            "typical_role_hired": role,
            "required_skills": ", ".join(ROLE_SKILL_MAP[role]),
        })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out_dir, "employers.csv"), index=False)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="../data/raw")
    parser.add_argument("--jobs", type=int, default=10000)
    parser.add_argument("--companies", type=int, default=500)
    parser.add_argument("--students", type=int, default=500)
    parser.add_argument("--employers", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    
    os.makedirs(args.out, exist_ok=True)

    print("Generating companies...")
    companies_df = generate_companies(args.companies, args.out)

    print("Generating skills...")
    generate_skills_csv(args.out)

    print("Generating roles...")
    generate_roles_csv(args.out)

    print("Generating jobs (this may take a moment)...")
    start = datetime.today() - timedelta(days=730)
    end = datetime.today()
    generate_jobs(args.jobs, companies_df, args.out, start, end)

    print("Generating courses...")
    _, course_defs = generate_courses(args.out)

    print("Generating curricula...")
    generate_curricula(args.out, course_defs)

    print("Generating students...")
    generate_students(args.students, args.out)

    print("Generating employers...")
    generate_employers(args.employers, companies_df, args.out)

    print(f"\nDone. Files written to: {os.path.abspath(args.out)}")


if __name__ == "__main__":
    main()
