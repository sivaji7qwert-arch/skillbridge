"""
data_service.py
----------------
Reads the outputs of the offline ML pipeline (scripts/*.py ->
data/processed/*.csv|json) and serves them to the API layer.

This keeps the hackathon prototype runnable WITHOUT requiring MongoDB
to be running: the pipeline artifacts are the source of truth, cached
in memory. `seed_database.py` can load the same artifacts into Mongo
for a "real" persistence layer; swapping this module's internals to
query Mongo instead of CSVs would not require changing any route.
"""
import json
from functools import lru_cache
from pathlib import Path

import pandas as pd

from app.config import get_settings

settings = get_settings()


def _path(filename: str, raw: bool = False) -> str:
    base = Path(settings.RAW_DATA_DIR if raw else settings.DATA_DIR)
    return str(base / filename)


@lru_cache
def load_jobs_with_skills() -> pd.DataFrame:
    df = pd.read_csv(_path("jobs_with_skills.csv"))
    df["extracted_skills"] = df["extracted_skills"].apply(json.loads)
    return df


@lru_cache
def load_skill_demand() -> pd.DataFrame:
    return pd.read_csv(_path("skill_demand.csv"))


@lru_cache
def load_skill_demand_by_city() -> pd.DataFrame:
    return pd.read_csv(_path("skill_demand_by_city.csv"))


@lru_cache
def load_emerging_roles() -> pd.DataFrame:
    return pd.read_csv(_path("emerging_roles.csv"))


@lru_cache
def load_roles() -> pd.DataFrame:
    return pd.read_csv(_path("roles.csv", raw=True))


@lru_cache
def load_curricula() -> pd.DataFrame:
    return pd.read_csv(_path("curricula.csv", raw=True))


@lru_cache
def load_courses() -> pd.DataFrame:
    return pd.read_csv(_path("courses.csv", raw=True))


@lru_cache
def load_students() -> pd.DataFrame:
    return pd.read_csv(_path("students.csv", raw=True))


@lru_cache
def load_employers() -> pd.DataFrame:
    return pd.read_csv(_path("employers.csv", raw=True))


def clear_cache():
    """Call after re-running the pipeline / uploading a new dataset."""
    for fn in (
        load_jobs_with_skills, load_skill_demand, load_skill_demand_by_city,
        load_emerging_roles, load_roles, load_curricula, load_courses,
        load_students, load_employers,
    ):
        fn.cache_clear()
