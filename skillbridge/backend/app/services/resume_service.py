"""
resume_service.py
--------------------
Extracts raw text from an uploaded resume (PDF or DOCX), then reuses the
same skill dictionary/matching logic from scripts/extract_skills.py to
derive a normalized skill list — so a resume and a job posting are
scored against the exact same skill vocabulary.

Supported formats: .pdf (via pdfplumber), .docx (via python-docx).
Anything else is rejected with a clear error rather than silently
returning an empty result.
"""
import io
import os
import sys
from pathlib import Path
from typing import List, Tuple

import docx
import pdfplumber

SCRIPTS_DIR = str(Path(__file__).resolve().parents[3] / "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from extract_skills import extract_from_text, load_skill_dictionary  # noqa: E402

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


class UnsupportedFileTypeError(Exception):
    pass


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    document = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


def extract_text(filename: str, file_bytes: bytes) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == ".docx":
        return extract_text_from_docx(file_bytes)
    else:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{ext}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )


def extract_skills_from_resume(raw_text: str, skills_csv: str) -> List[str]:
    """Reuses the exact same dictionary-matching logic used for job
    postings, so resume skills and job-required skills are directly
    comparable (same normalization, same canonical names)."""
    canonical_list, lookup = load_skill_dictionary(skills_csv)
    return extract_from_text(raw_text, canonical_list, lookup)


def parse_resume(filename: str, file_bytes: bytes, skills_csv: str) -> Tuple[str, List[str]]:
    """Returns (raw_text, extracted_skills)."""
    raw_text = extract_text(filename, file_bytes)
    if not raw_text.strip():
        raise ValueError(
            "No extractable text found in this file. If it's a scanned/image-based "
            "PDF, OCR would be required — not yet supported for resumes in this build."
        )
    skills = extract_skills_from_resume(raw_text, skills_csv)
    return raw_text, skills
