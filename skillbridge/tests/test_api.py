"""
test_api.py
------------
Basic FastAPI endpoint tests using TestClient. Requires the data
pipeline to have been run first (jobs_with_skills.csv, skill_demand.csv,
etc. must exist in data/processed/).

Run:
    cd backend && python -m pytest ../tests/test_api.py -v
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_dashboard_kpis():
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "total_jobs_analyzed" in data
    assert data["total_jobs_analyzed"] > 0


def test_jobs_list_and_pagination():
    res = client.get("/api/jobs", params={"page": 1, "page_size": 5})
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) <= 5


def test_trending_skills():
    res = client.get("/api/skills/trending", params={"limit": 5})
    assert res.status_code == 200
    assert len(res.json()) <= 5


def test_curriculum_analyze():
    res = client.post("/api/curriculum/analyze", json={"role": "Data Analyst", "curriculum_id": "CUR001"})
    assert res.status_code == 200
    data = res.json()
    assert "recommendations" in data
    assert "alignment_before_pct" in data


def test_curriculum_analyze_invalid_role_returns_404():
    res = client.post("/api/curriculum/analyze", json={"role": "Nonexistent Role", "curriculum_id": "CUR001"})
    assert res.status_code == 404
