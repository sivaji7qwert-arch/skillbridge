"""
db_models.py
-------------
SQLAlchemy models mirroring backend/app/models/schema.sql.
Uses PostgreSQL-specific ARRAY and ENUM types since the schema does too.
"""
import enum
import uuid

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UserRole(str, enum.Enum):
    student = "student"
    employer = "employer"
    institution = "institution"
    admin = "admin"


class VerificationStatus(str, enum.Enum):
    pending = "Pending"
    verified = "Verified"
    rejected = "Rejected"
    needs_review = "Needs Review"


class ApplicationStatus(str, enum.Enum):
    applied = "Applied"
    shortlisted = "Shortlisted"
    rejected = "Rejected"
    hired = "Hired"


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(ENUM(UserRole, name="user_role"), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    institution_profile = relationship("InstitutionProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    college_name = Column(String(255))
    course = Column(String(255))
    branch = Column(String(255))
    graduation_year = Column(Integer)
    career_interest = Column(String(255))
    known_skills = Column(ARRAY(String), default=list)
    programming_languages = Column(ARRAY(String), default=list)
    target_role = Column(String(255))
    onboarding_complete = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="student_profile")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    student_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    raw_text = Column(Text)
    extracted_skills = Column(ARRAY(String), default=list)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    student_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    certificate_type = Column(String(100))
    extracted_text = Column(Text)
    status = Column(ENUM(VerificationStatus, name="verification_status"), default=VerificationStatus.pending, nullable=False)
    reviewer_note = Column(Text)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))


class DSAProgress(Base):
    __tablename__ = "dsa_progress"
    __table_args__ = (UniqueConstraint("student_id", "problem_title", name="uq_student_problem"),)

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    student_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(100), nullable=False)
    problem_title = Column(String(255), nullable=False)
    difficulty = Column(String(20), nullable=False)
    platform = Column(String(50))
    solved = Column(Boolean, default=False, nullable=False)
    solved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Streak(Base):
    __tablename__ = "streaks"

    student_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_active_date = Column(DateTime)


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    employer_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    sector = Column(String(255))
    city = Column(String(255))
    website = Column(String(255))
    description = Column(Text)

    jobs = relationship("JobPosting", back_populates="company", cascade="all, delete-orphan")


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(ARRAY(String), nullable=False)
    preferred_qualifications = Column(Text)
    location = Column(String(255))
    experience_required = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("job_id", "student_id", name="uq_job_student"),)

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    job_id = Column(UUID(as_uuid=False), ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Float)
    status = Column(ENUM(ApplicationStatus, name="application_status"), default=ApplicationStatus.applied, nullable=False)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("JobPosting", back_populates="applications")


class InstitutionProfile(Base):
    __tablename__ = "institution_profiles"

    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    institution_name = Column(String(255), nullable=False)
    city = Column(String(255))
    state = Column(String(255))

    user = relationship("User", back_populates="institution_profile")
    courses = relationship("InstitutionCourse", back_populates="institution", cascade="all, delete-orphan")


class InstitutionCourse(Base):
    __tablename__ = "institution_courses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    institution_id = Column(UUID(as_uuid=False), ForeignKey("institution_profiles.user_id", ondelete="CASCADE"), nullable=False)
    department = Column(String(255), nullable=False)
    course_name = Column(String(255), nullable=False)
    taught_skills = Column(ARRAY(String), nullable=False)

    institution = relationship("InstitutionProfile", back_populates="courses")


class ExternalCourse(Base):
    __tablename__ = "external_courses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    provider = Column(String(100), nullable=False)  # Coursera, Infosys Springboard, Oracle University, IBM SkillsBuild
    title = Column(String(255), nullable=False)
    skills_taught = Column(ARRAY(String), nullable=False)
    url = Column(String(500))
