"""Pydantic schemas for API request/response validation."""
from typing import List, Optional

from pydantic import BaseModel, Field


class JobOut(BaseModel):
    job_id: str
    job_title: str
    normalized_role: str
    company: str
    location: str
    industry: str
    experience_required: int
    salary_min: int
    salary_max: int
    skills: List[str]
    posting_date: str
    employment_type: str


class SkillDemandOut(BaseModel):
    skill: str
    demand_percentage: float
    growth_pct: float
    trend: str
    skill_demand_score: float
    avg_salary: Optional[float] = None


class EmergingRoleOut(BaseModel):
    role: str
    current_demand_postings: int
    growth_pct: float
    required_skills: List[str]
    top_locations: List[str]
    avg_salary: float
    trend: str


class SkillGapRow(BaseModel):
    skill: str
    industry_demand_pct: float
    industry_demand_score: float
    curriculum_coverage_score: float
    gap_score: float
    status: str


class CurriculumAnalyzeRequest(BaseModel):
    role: str = Field(..., description="Target role name, e.g. 'Data Analyst'")
    curriculum_id: str = Field(..., description="Curriculum identifier, e.g. 'CUR001'")


class RecommendationOut(BaseModel):
    skill: str
    action: str
    priority: str
    confidence: int
    evidence: List[str]
    industry_demand_pct: float
    curriculum_coverage_score: float
    gap_score: float


class RecommendationResponse(BaseModel):
    role: str
    alignment_before_pct: float
    alignment_after_estimate_pct: float
    note: str
    recommendations: List[RecommendationOut]


class StudentSkillGapOut(BaseModel):
    student_id: str
    target_role: str
    known_skills: List[str]
    missing_skills: List[dict]  # {skill, priority}


class EmployerFeedbackIn(BaseModel):
    employer_id: str
    recommendation_skill: str
    role: str
    decision: str = Field(..., pattern="^(Approve|Reject|Suggest Modification)$")
    comment: Optional[str] = None


class DashboardKPIs(BaseModel):
    total_jobs_analyzed: int
    total_skills_detected: int
    emerging_skills_count: int
    total_skill_gaps: int
    courses_analyzed: int
    avg_industry_alignment_pct: float
