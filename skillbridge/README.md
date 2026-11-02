# SkillBridge — Role-Based Career Intelligence Platform

A four-portal platform (Student / Employer / Institution / Government) connecting
real job-market demand to skill development, resume matching, and interview prep.
Built for **SIH26134** (Government of Maharashtra), extended into a general-purpose
career intelligence system.

## Architecture

```
PostgreSQL (accounts, profiles, jobs, applications, resumes, certificates, DSA progress)
        +
CSV/pandas pipeline (bulk labour-market analytics: skill demand, trends, emerging roles)
        ↓
FastAPI backend (role-based JWT auth, TF-IDF/cosine matching engine, OCR)
        ↓
React + Tailwind frontend (4 role-specific portals)
```

Two data stores serve two different needs:
- **PostgreSQL** — transactional, per-user data: accounts, job postings, applications,
  uploaded resumes/certificates, DSA progress. This is the platform's system of record.
- **CSV pipeline** (`scripts/*.py` → `data/processed/*.csv`) — bulk labour-market
  analytics recomputed from job posting data. Read-heavy, not transactional, so it
  stays outside Postgres by design.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, React Router, Axios, Recharts |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL |
| ML | scikit-learn (TF-IDF, cosine similarity, RandomForest), pandas, NumPy |
| Document processing | pdfplumber (PDF), python-docx (DOCX), pytesseract + Tesseract (OCR) |
| Auth | JWT (python-jose), bcrypt password hashing (passlib) |

## The Four Portals

### Student Portal
- Onboarding (college, course, branch, graduation year, skills, target role)
- Resume upload → automatic skill extraction (merged into profile)
- Skill-gap analysis vs. target role, with priority-ranked missing skills
- Course recommendations (Coursera / Infosys Springboard / Oracle University / IBM SkillsBuild)
- DSA prep: topic roadmap, daily streak, weakest-topic-first problem recommendations,
  link-outs to LeetCode/HackerRank/CodeChef (no scraped/reproduced problem content)
- Certificate upload with OCR text extraction (status: Pending → Verified/Rejected/Needs
  Review — **only a human reviewer can mark Verified**, this platform never claims
  automatic authenticity verification)
- Job browsing and application (with an explainable match score shown at apply time)

### Employer/Recruiter Portal
- Company profile
- Job posting with required skills
- **AI-ranked candidates**: every onboarded student is scored against the job via a
  blended TF-IDF text-similarity + structured skill-overlap match, with the score
  breakdown and evidence shown (see `backend/app/ml/matching_engine.py`)
- Application status management (Applied/Shortlisted/Rejected/Hired)
- Certificate status viewing (not raw document content) for verification checks

### Institution/College Portal
- Course/department registration with taught skills
- Student skill statistics (aggregated by matching `college_name`)
- Common skill-gap detection: industry-high-demand skills with low coverage among
  the institution's own students
- Placement readiness estimate (heuristic based on known-skill count — explicitly
  labeled as a heuristic, not a certified assessment)
- Shared access to labour-market analytics and curriculum-vs-industry gap analysis

### Government/Admin Portal
- Platform-wide user/job/skill counts
- City-wise (proxy for district-wise) skill demand
- Institution-wise placement readiness comparison
- Emerging job roles ranked by growth

## Real Dataset Support

`scripts/ingest_linkedin_jobs.py` ingests the Kaggle **"LinkedIn Jobs Dataset for
India"** (michellemiranda/linkedin-jobs-dataset-for-india), matching its exact
published schema (`id, publishedAt, title, companyName, postedTime,
applicationsCount, description, contractType, experienceLevel, workType, sector,
companyId, city, state, recently_posted_jobs`), and converts it into the format the
rest of the pipeline expects.

```bash
# 1. Download the dataset (requires a free Kaggle account)
pip install kaggle
kaggle datasets download -d michellemiranda/linkedin-jobs-dataset-for-india
unzip linkedin-jobs-dataset-for-india.zip -d data/raw/

# 2. Ingest it
cd scripts
python ingest_linkedin_jobs.py --in ../data/raw/<the-downloaded-csv>.csv --out ../data/raw/jobs.csv

# 3. Run the rest of the pipeline as usual
python extract_skills.py --jobs ../data/raw/jobs.csv --out ../data/processed/jobs_with_skills.csv
python analyze_demand.py --jobs ../data/processed/jobs_with_skills.csv
python detect_trends.py --jobs ../data/processed/jobs_with_skills.csv
```

If no real file is supplied, `ingest_linkedin_jobs.py` falls back to a small,
explicitly-labeled sample (`is_sample_data=True` in the output) so development
isn't blocked — this is never presented as real data anywhere in the UI/API.

**Note on salary data:** the published Kaggle dataset does not include salary
fields. Rather than fabricating numbers, `salary_min`/`salary_max` are left null
for LinkedIn-sourced rows, and salary-based scoring degrades gracefully (treated
as a zero contribution) rather than showing invented figures.

## Installation

### 1. PostgreSQL

```bash
createdb skillbridge
psql skillbridge -f backend/app/models/schema.sql   # or let init_db() auto-create on first run
```

### 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL if not using the default local Postgres
uvicorn app.main:app --reload
```

Tesseract must also be installed system-wide for certificate OCR:
- macOS: `brew install tesseract`
- Ubuntu/Debian: `apt-get install tesseract-ocr`
- Windows: install from the [Tesseract project releases](https://github.com/UB-Mannheim/tesseract/wiki)

### 3. Seed external course catalog (for course recommendations)

```bash
cd scripts
python seed_external_courses.py --database-url postgresql://postgres:postgres@localhost:5432/skillbridge
```

### 4. Run the labour-market data pipeline

```bash
cd scripts
python generate_dataset.py --out ../data/raw     # or ingest_linkedin_jobs.py for real data
python extract_skills.py --jobs ../data/raw/jobs.csv --out ../data/processed/jobs_with_skills.csv
python analyze_demand.py --jobs ../data/processed/jobs_with_skills.csv
python detect_trends.py --jobs ../data/processed/jobs_with_skills.csv
python train_model.py --demand ../data/processed/skill_demand.csv --out-dir ../models
```

### 5. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Demo Flow

1. **Register** at `/register` — pick a role (Student/Employer/Institution/Admin)
2. **Student**: complete onboarding → upload a resume (skills auto-merge into
   profile) → check Skill Gap on the dashboard → browse DSA problems and mark some
   solved (watch the streak increment) → browse and apply to jobs
3. **Employer**: register as employer → set up company profile → post a job → view
   AI-ranked candidates with explainable match scores
4. **Institution**: register as institution → add courses → view aggregated student
   skill statistics and common gaps
5. **Admin**: register as admin → view platform-wide overview, district skill
   demand, and institution readiness comparison

## Explainability & Honesty Commitments

- Every AI match score (candidate↔job, student↔role) decomposes into its
  contributing signals (skill overlap %, text similarity %, matched/missing
  skills) — never a bare unexplained number
- Certificate OCR extracts text for a human reviewer; it **never** auto-sets
  status to "Verified" — that requires a manual `institution`/`admin` action
- DSA problem references are well-known public problem titles with link-outs to
  the actual platforms — no scraped problem statements or test cases
- Sample/synthetic data is explicitly flagged (`is_sample_data`) and never
  presented as real data
- Alignment/readiness percentages are labeled as estimates/heuristics, not
  certified assessments

## Project Structure

```
skillbridge/
├── backend/
│   └── app/
│       ├── models/          # db_models.py (SQLAlchemy), schema.sql (DDL)
│       ├── routes/          # auth, students, employers, institutions, admin,
│       │                      resumes, certificates, jobs, skills, roles,
│       │                      curriculum, labour_market, dashboard, ml
│       ├── services/        # data_service, gap_service, resume_service,
│       │                      certificate_service, dsa_service
│       ├── ml/               # matching_engine.py, predictor.py
│       └── utils/            # security.py (auth/JWT)
├── frontend/
│   └── src/
│       ├── pages/student/    # onboarding, dashboard, resume, certificates, dsa, jobs
│       ├── pages/employer/   # dashboard, post-job, candidate ranking
│       ├── pages/institution/# dashboard, courses
│       ├── pages/admin/      # dashboard
│       └── layouts/          # PortalLayout.jsx (shared, role-aware nav)
├── scripts/                  # data pipeline: generate/ingest, extract, analyze,
│                                detect trends, calculate gaps, recommend, train model
├── data/
│   ├── raw/, processed/      # CSV pipeline data
│   └── uploads/               # resumes/, certificates/ (uploaded files)
└── models/                    # trained ML model artifacts
```
