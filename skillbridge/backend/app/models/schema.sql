-- SkillBridge PostgreSQL schema
-- Covers: authentication, role-based profiles, job postings & applications,
-- resumes, certificates, DSA progress/streaks.
--
-- Job-market ANALYTICS (skill demand, trends) intentionally stays in the
-- existing CSV/pandas pipeline (scripts/*.py -> data/processed/*.csv) since
-- it's bulk, read-heavy, recomputed-from-scratch data — not a good fit for
-- transactional storage. This schema is for the platform's own write-heavy,
-- per-user data: accounts, applications, uploaded documents, progress.
--
-- Run:
--   createdb skillbridge
--   psql skillbridge -f backend/app/models/schema.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE user_role AS ENUM ('student', 'employer', 'institution', 'admin');
CREATE TYPE verification_status AS ENUM ('Pending', 'Verified', 'Rejected', 'Needs Review');
CREATE TYPE application_status AS ENUM ('Applied', 'Shortlisted', 'Rejected', 'Hired');

-- ---------------------------------------------------------------------------
-- Core accounts
-- ---------------------------------------------------------------------------
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            user_role NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_active       BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX idx_users_role ON users(role);

-- ---------------------------------------------------------------------------
-- Student profile
-- ---------------------------------------------------------------------------
CREATE TABLE student_profiles (
    user_id             UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    college_name        VARCHAR(255),
    course              VARCHAR(255),
    branch              VARCHAR(255),
    graduation_year     INTEGER,
    career_interest     VARCHAR(255),
    known_skills        TEXT[],            -- normalized skill names, self-reported + resume-derived
    programming_languages TEXT[],
    target_role         VARCHAR(255),
    onboarding_complete BOOLEAN NOT NULL DEFAULT false,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE resumes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_path       VARCHAR(500) NOT NULL,
    raw_text        TEXT,
    extracted_skills TEXT[],
    uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE certificates (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_path       VARCHAR(500) NOT NULL,
    certificate_type VARCHAR(100),          -- e.g. 'Degree', 'Course Completion'
    extracted_text  TEXT,
    status          verification_status NOT NULL DEFAULT 'Pending',
    reviewer_note    TEXT,
    uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at     TIMESTAMPTZ
);

-- ---------------------------------------------------------------------------
-- DSA prep / streak tracking
-- ---------------------------------------------------------------------------
CREATE TABLE dsa_progress (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic           VARCHAR(100) NOT NULL,     -- e.g. 'Arrays', 'Dynamic Programming'
    problem_title   VARCHAR(255) NOT NULL,
    difficulty      VARCHAR(20) NOT NULL,       -- Easy / Medium / Hard
    platform        VARCHAR(50),                -- LeetCode / HackerRank / CodeChef (link-out only)
    solved          BOOLEAN NOT NULL DEFAULT false,
    solved_at       TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(student_id, problem_title)
);

CREATE TABLE streaks (
    student_id      UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    current_streak  INTEGER NOT NULL DEFAULT 0,
    longest_streak  INTEGER NOT NULL DEFAULT 0,
    last_active_date DATE
);

-- ---------------------------------------------------------------------------
-- Employer / company / job postings
-- ---------------------------------------------------------------------------
CREATE TABLE companies (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employer_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    sector          VARCHAR(255),
    city            VARCHAR(255),
    website         VARCHAR(255),
    description     TEXT
);

CREATE TABLE job_postings (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    title               VARCHAR(255) NOT NULL,
    description         TEXT NOT NULL,
    required_skills     TEXT[] NOT NULL,
    preferred_qualifications TEXT,
    location            VARCHAR(255),
    experience_required INTEGER DEFAULT 0,
    is_active           BOOLEAN NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_job_postings_company ON job_postings(company_id);

CREATE TABLE applications (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id          UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    student_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    match_score     FLOAT,                      -- TF-IDF/cosine similarity score at time of application
    status          application_status NOT NULL DEFAULT 'Applied',
    applied_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(job_id, student_id)
);

-- ---------------------------------------------------------------------------
-- Institution
-- ---------------------------------------------------------------------------
CREATE TABLE institution_profiles (
    user_id         UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    institution_name VARCHAR(255) NOT NULL,
    city            VARCHAR(255),
    state           VARCHAR(255)
);

CREATE TABLE institution_courses (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    department      VARCHAR(255) NOT NULL,
    course_name     VARCHAR(255) NOT NULL,
    taught_skills   TEXT[] NOT NULL
);

-- ---------------------------------------------------------------------------
-- Course catalog (external providers) used for recommendations
-- ---------------------------------------------------------------------------
CREATE TABLE external_courses (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider        VARCHAR(100) NOT NULL,   -- 'Coursera', 'Infosys Springboard', 'Oracle University', 'IBM SkillsBuild'
    title           VARCHAR(255) NOT NULL,
    skills_taught   TEXT[] NOT NULL,
    url             VARCHAR(500)
);

CREATE INDEX idx_external_courses_provider ON external_courses(provider);
